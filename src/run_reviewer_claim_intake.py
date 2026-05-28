#!/usr/bin/env python3
"""Run an application-facing reviewer claim-intake workflow.

The admission runner answers whether a template is allowed into the workflow.
This runner answers the next user-facing question: given a registered template
and a submitted claim sentence, what should an author or reviewer do with it?

The runner is intentionally conservative. It does not discover template ids,
parse arbitrary prose, or promote support-only rows into mainline claims.
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter
import html
import json
from pathlib import Path
import re


FILES = {
    "intake_schema": "artifact/reviewer_claim_intake_schema_20260521.json",
    "intake_examples": "artifact/reviewer_claim_intake_examples_20260521.csv",
    "template_schema": "artifact/claim_template_admission_schema_20260521.json",
    "template_cases": "artifact/claim_template_admission_cases_20260521.csv",
    "casebook": "data/claim_passport_casebook_20260519.csv",
    "nab_visual": "data/nab_adapter_visual_passport_rows_20260519.csv",
}

EXPECTED_INTAKE_COLUMNS = [
    "intake_id",
    "actor",
    "template_id",
    "submitted_claim",
    "intended_use",
    "expected_decision",
    "expected_output_hint",
]

DECISIONS = {
    "ACCEPT_LICENSED",
    "REWRITE_TO_LICENSED",
    "SUPPRESS_BOTTOM",
    "SUPPORT_ONLY_REWRITE",
    "REJECT_PATCHWORK",
    "REJECT_UNKNOWN_TEMPLATE",
}

ACTION_FAMILIES = {
    "emit_as_written",
    "relabel_as_upper_bound",
    "weaken_to_diagnostic",
    "rewrite_to_decision_local",
    "suppress_fallback",
}

PRIVATE_PATTERNS = (
    re.compile(r"/Users/[A-Za-z0-9._-]+"),
    re.compile(r"\bconnect\.[A-Za-z0-9.-]+\b"),
    re.compile(
        r"\b(?:"
        + "|".join(
            re.escape(prefix)
            for prefix in [
                "CODEX" + "_ONLY/",
                "CLAUDE" + "_ONLY/",
                "EX" + "CHANGE/",
            ]
        )
        + r")"
    ),
    re.compile(
        r"\b(?:password|passwd|token|secret|credential)\b\s*[:=]\s*"
        r"['\"]?[A-Za-z0-9_./+=-]{8,}",
        re.IGNORECASE,
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Apply admitted claim templates to reviewer claim-intake rows."
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Release root to audit. Default: current directory.",
    )
    parser.add_argument(
        "--output",
        default="reports/reviewer_claim_intake_20260521",
        help="Report output directory. Relative paths are resolved under root.",
    )
    return parser.parse_args()


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def resolve_output(root: Path, output: str) -> Path:
    out = Path(output)
    if not out.is_absolute():
        out = root / out
    return out.resolve()


def normalize(text: str) -> str:
    return " ".join((text or "").strip().lower().split())


def short(text: str, limit: int = 150) -> str:
    text = " ".join((text or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "..."


def contains_private_marker(row: dict[str, str]) -> bool:
    text = " ".join(str(value or "") for value in row.values())
    return any(pattern.search(text) for pattern in PRIVATE_PATTERNS)


def add_check(
    checks: list[dict[str, str]],
    check_id: str,
    label: str,
    ok: bool,
    evidence: str,
    fail_detail: str,
) -> None:
    checks.append(
        {
            "check_id": check_id,
            "label": label,
            "status": "PASS" if ok else "FAIL",
            "evidence": evidence if ok else fail_detail,
        }
    )


def is_filled(row: dict[str, str], field: str) -> bool:
    value = row.get(field, "").strip()
    if field == "action_mapping":
        return bool(value) and value != "none"
    return bool(value)


def compute_template_verdict(
    row: dict[str, str], critical_fields: list[str]
) -> tuple[str, str, list[str]]:
    missing = [field for field in critical_fields if not is_filled(row, field)]
    role = row.get("template_role", "")
    if missing:
        if len(missing) >= 5:
            return "L0_REJECTED", "REJECT_PATCHWORK", missing
        return "L1_BOUNDARY_PROBE", "KEEP_BOUNDARY_PROBE", missing
    if role == "mainline":
        return "L3_MAINLINE", "ADMIT_MAINLINE_TEMPLATE", []
    if role == "support_only":
        return "L2_SUPPORT_ONLY", "ADMIT_SUPPORT_ONLY_TEMPLATE", []
    return "L1_BOUNDARY_PROBE", "KEEP_BOUNDARY_PROBE", []


def build_template_rows(
    cases: list[dict[str, str]], critical_fields: list[str]
) -> dict[str, dict[str, str]]:
    templates: dict[str, dict[str, str]] = {}
    for row in cases:
        level, verdict, missing = compute_template_verdict(row, critical_fields)
        enriched = dict(row)
        enriched["computed_level"] = level
        enriched["computed_verdict"] = verdict
        enriched["missing_critical_fields"] = ";".join(missing)
        templates[row["template_id"]] = enriched
    return templates


def source_from_anchor(
    template: dict[str, str],
    casebook_by_id: dict[str, dict[str, str]],
    nab_by_id: dict[str, dict[str, str]],
) -> dict[str, str]:
    anchor = template.get("visual_or_case_anchor", "")
    if anchor.startswith("CP-") and anchor in casebook_by_id:
        row = casebook_by_id[anchor]
        return {
            "licensed": row.get("licensed_sentence", ""),
            "forbidden": row.get("forbidden_sentence", ""),
            "tempting": row.get("tempting_sentence", ""),
            "action": row.get("projection_action", template.get("action_mapping", "")),
            "boundary": row.get("boundary_note", template.get("boundary_note", "")),
            "source": anchor,
        }
    if anchor.startswith("NAB-VIS-") and anchor in nab_by_id:
        row = nab_by_id[anchor]
        return {
            "licensed": row.get("licensed_sentence", ""),
            "forbidden": row.get("forbidden_sentence", ""),
            "tempting": row.get("ordinary_sentence", ""),
            "action": row.get("adapter_action", template.get("action_mapping", "")),
            "boundary": row.get("visual_role", template.get("boundary_note", "")),
            "source": anchor,
        }
    return {
        "licensed": "",
        "forbidden": template.get("forbidden_claim", ""),
        "tempting": "",
        "action": template.get("action_mapping", ""),
        "boundary": template.get("boundary_note", ""),
        "source": anchor,
    }


def decide_intake(
    intake: dict[str, str],
    templates: dict[str, dict[str, str]],
    casebook_by_id: dict[str, dict[str, str]],
    nab_by_id: dict[str, dict[str, str]],
) -> dict[str, str]:
    template_id = intake.get("template_id", "")
    submitted = intake.get("submitted_claim", "")
    if template_id not in templates:
        return {
            "intake_id": intake.get("intake_id", ""),
            "template_id": template_id,
            "decision": "REJECT_UNKNOWN_TEMPLATE",
            "recommended_output": "bottom_T",
            "explanation": "Unknown template id; register a typed template before claim review.",
            "source_anchor": "",
            "expected_decision": intake.get("expected_decision", ""),
            "expected_match": "PASS"
            if intake.get("expected_decision") == "REJECT_UNKNOWN_TEMPLATE"
            else "FAIL",
        }

    template = templates[template_id]
    source = source_from_anchor(template, casebook_by_id, nab_by_id)
    verdict = template.get("computed_verdict", "")
    submitted_norm = normalize(submitted)
    licensed_norm = normalize(source["licensed"])
    forbidden_norm = normalize(source["forbidden"])
    tempting_norm = normalize(source["tempting"])
    action = source["action"] or template.get("action_mapping", "")
    registered_sentence_match = submitted_norm == licensed_norm or submitted_norm in {
        value for value in [forbidden_norm, tempting_norm] if value
    }

    if verdict == "REJECT_PATCHWORK":
        decision = "REJECT_PATCHWORK"
        output = "bottom_T"
        explanation = (
            "Template does not instantiate the adapter contract: "
            f"{template.get('missing_critical_fields', '')}."
        )
    elif not registered_sentence_match and action != "suppress_fallback":
        decision = "REJECT_PATCHWORK"
        output = "bottom_T"
        explanation = (
            "Submitted wording does not match this template's registered licensed, "
            "forbidden, or tempting claim sentences; reject as a template handoff mismatch."
        )
    elif verdict == "ADMIT_SUPPORT_ONLY_TEMPLATE":
        decision = "SUPPORT_ONLY_REWRITE"
        output = source["licensed"] or template.get("claim_template", "")
        explanation = (
            "Template is admitted only as support-only evidence; do not promote "
            "it to a headline or broad domain claim."
        )
    elif action == "suppress_fallback":
        decision = "SUPPRESS_BOTTOM"
        output = "bottom_T"
        explanation = "The registered action is fail-closed suppression."
    elif submitted_norm == licensed_norm:
        decision = "ACCEPT_LICENSED"
        output = source["licensed"]
        explanation = "Submitted claim already matches the licensed sentence."
    elif submitted_norm in {forbidden_norm, tempting_norm}:
        decision = "REWRITE_TO_LICENSED"
        output = source["licensed"]
        explanation = "Submitted claim matches a tempting or forbidden stronger claim."
    else:
        decision = "REWRITE_TO_LICENSED"
        output = source["licensed"]
        explanation = "Template is admitted, but the submitted wording is not the registered licensed sentence."

    return {
        "intake_id": intake.get("intake_id", ""),
        "template_id": template_id,
        "decision": decision,
        "recommended_output": output,
        "explanation": explanation,
        "source_anchor": source["source"],
        "expected_decision": intake.get("expected_decision", ""),
        "expected_match": "PASS"
        if decision == intake.get("expected_decision", "")
        else "FAIL",
    }


def build_markdown(
    summary: dict[str, object],
    checks: list[dict[str, str]],
    decisions: list[dict[str, str]],
) -> str:
    lines: list[str] = []
    lines.append("# Reviewer Claim Intake Report")
    lines.append("")
    lines.append("Status: generated from release-root public-safe assets.")
    lines.append("")
    lines.append("## Application Target")
    lines.append("")
    lines.append(
        "This report demonstrates the application-facing workflow: an author or "
        "reviewer submits a claim with a registered template id, and the tool "
        "returns whether to accept it, rewrite it, suppress it, keep it "
        "support-only, or reject it before review."
    )
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Item | Value |")
    lines.append("| --- | ---: |")
    for key in [
        "intake_rows",
        "accepted",
        "rewritten",
        "suppressed",
        "support_only",
        "rejected",
        "checks_passed",
        "checks_failed",
    ]:
        lines.append(f"| {key} | {summary[key]} |")
    lines.append("")
    lines.append("## Intake Checks")
    lines.append("")
    lines.append("| Check | Status | Evidence |")
    lines.append("| --- | --- | --- |")
    for row in checks:
        lines.append(
            f"| {row['check_id']} {row['label']} | {row['status']} | "
            f"{short(row['evidence'], 220)} |"
        )
    lines.append("")
    lines.append("## Application Decisions")
    lines.append("")
    lines.append("| Intake | Template | Decision | Recommended Output | Explanation |")
    lines.append("| --- | --- | --- | --- | --- |")
    for row in decisions:
        lines.append(
            f"| {row['intake_id']} | {row['template_id']} | {row['decision']} | "
            f"{short(row['recommended_output'], 180)} | {short(row['explanation'], 160)} |"
        )
    lines.append("")
    lines.append("## Current Limit")
    lines.append("")
    lines.append(
        "The runner is an intake workflow for registered templates. It does not "
        "discover template ids, infer G/Q/U from arbitrary prose, or certify "
        "deployment safety. Its value is application ergonomics: it turns the "
        "claim-contract machinery into concrete author/reviewer decisions."
    )
    lines.append("")
    return "\n".join(lines)


def html_table(rows: list[dict[str, str]], columns: list[str]) -> str:
    header = "".join(f"<th>{html.escape(column)}</th>" for column in columns)
    body = []
    for row in rows:
        cells = "".join(
            f"<td>{html.escape(short(row.get(column, ''), 240))}</td>"
            for column in columns
        )
        body.append(f"<tr>{cells}</tr>")
    return f"<table><thead><tr>{header}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def build_html(
    summary: dict[str, object],
    checks: list[dict[str, str]],
    decisions: list[dict[str, str]],
) -> str:
    metrics = []
    for key in [
        "intake_rows",
        "accepted",
        "rewritten",
        "suppressed",
        "support_only",
        "rejected",
        "checks_failed",
    ]:
        metrics.append(
            "<div class='metric'>"
            f"<span>{html.escape(key)}</span>"
            f"<strong>{html.escape(str(summary[key]))}</strong>"
            "</div>"
        )
    check_rows = [
        {
            "check": f"{row['check_id']} {row['label']}",
            "status": row["status"],
            "evidence": row["evidence"],
        }
        for row in checks
    ]
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Reviewer Claim Intake Report</title>
  <style>
    :root {{
      --ink: #172124;
      --muted: #5e6966;
      --line: #d8ded9;
      --wash: #f7faf7;
      --green: #145c5a;
      --gold: #ad741e;
    }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--wash);
      color: var(--ink);
      line-height: 1.5;
    }}
    main {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 36px 28px 60px;
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: 34px;
      letter-spacing: 0;
    }}
    h2 {{
      margin-top: 34px;
      border-top: 2px solid var(--line);
      padding-top: 20px;
      font-size: 22px;
      letter-spacing: 0;
    }}
    p {{
      max-width: 900px;
      color: var(--muted);
    }}
    .metrics {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 12px;
      margin: 24px 0;
    }}
    .metric {{
      background: white;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 14px 16px;
    }}
    .metric span {{
      display: block;
      color: var(--muted);
      font-size: 13px;
    }}
    .metric strong {{
      display: block;
      margin-top: 5px;
      color: var(--green);
      font-size: 24px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      background: white;
      border: 1px solid var(--line);
      border-radius: 6px;
      overflow: hidden;
      margin-top: 12px;
    }}
    th, td {{
      border-bottom: 1px solid var(--line);
      padding: 9px 10px;
      vertical-align: top;
      text-align: left;
      font-size: 13px;
    }}
    th {{
      background: #e8f3ee;
      color: var(--green);
      font-weight: 750;
    }}
    tr:last-child td {{
      border-bottom: 0;
    }}
    .note {{
      border-left: 5px solid var(--gold);
      background: white;
      padding: 14px 18px;
      border-radius: 4px;
    }}
  </style>
</head>
<body>
<main>
  <h1>Reviewer Claim Intake Report</h1>
  <p>Generated from public-safe release-root assets. The report shows how a
  registered claim template becomes an author/reviewer decision.</p>
  <section class="metrics">{''.join(metrics)}</section>
  <h2>Intake Checks</h2>
  {html_table(check_rows, ["check", "status", "evidence"])}
  <h2>Application Decisions</h2>
  {html_table(decisions, ["intake_id", "template_id", "decision", "recommended_output", "explanation"])}
  <h2>Current Limit</h2>
  <div class="note"><p>The runner is an intake workflow for registered
  templates. It does not infer missing template structure from arbitrary prose.</p></div>
</main>
</body>
</html>
"""


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    output_dir = resolve_output(root, args.output)

    failures: list[str] = []
    try:
        intake_schema = json.loads(
            (root / FILES["intake_schema"]).read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError) as exc:
        intake_schema = {}
        failures.append(f"{FILES['intake_schema']}: could not read schema: {exc}")

    try:
        template_schema = json.loads(
            (root / FILES["template_schema"]).read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError) as exc:
        template_schema = {}
        failures.append(f"{FILES['template_schema']}: could not read schema: {exc}")

    try:
        intake_rows, intake_header = read_csv(root / FILES["intake_examples"])
    except OSError as exc:
        intake_rows, intake_header = [], []
        failures.append(f"{FILES['intake_examples']}: could not read examples: {exc}")

    try:
        template_cases, _ = read_csv(root / FILES["template_cases"])
    except OSError as exc:
        template_cases = []
        failures.append(f"{FILES['template_cases']}: could not read template cases: {exc}")

    try:
        casebook_rows, _ = read_csv(root / FILES["casebook"])
    except OSError as exc:
        casebook_rows = []
        failures.append(f"{FILES['casebook']}: could not read casebook: {exc}")

    try:
        nab_rows, _ = read_csv(root / FILES["nab_visual"])
    except OSError as exc:
        nab_rows = []
        failures.append(f"{FILES['nab_visual']}: could not read NAB rows: {exc}")

    critical_fields = list(template_schema.get("critical_fields_for_admission", []))
    templates = build_template_rows(template_cases, critical_fields)
    casebook_by_id = {row.get("event_id", ""): row for row in casebook_rows}
    nab_by_id = {row.get("display_id", ""): row for row in nab_rows}
    decisions = [
        decide_intake(row, templates, casebook_by_id, nab_by_id)
        for row in intake_rows
    ]

    checks: list[dict[str, str]] = []
    add_check(
        checks,
        "RCI-01",
        "inputs present",
        not failures
        and bool(intake_rows)
        and bool(template_cases)
        and bool(intake_schema)
        and bool(template_schema),
        "intake schema, examples, template cases, casebook, and NAB rows loaded",
        "; ".join(failures) if failures else "one or more intake inputs are empty",
    )
    add_check(
        checks,
        "RCI-02",
        "intake header alignment",
        intake_header == EXPECTED_INTAKE_COLUMNS,
        f"intake header has {len(intake_header)} expected columns",
        f"intake header={intake_header}; expected={EXPECTED_INTAKE_COLUMNS}",
    )
    private_rows = [
        row.get("intake_id", "unknown")
        for row in intake_rows
        if contains_private_marker(row)
    ]
    add_check(
        checks,
        "RCI-03",
        "public-safe intake text",
        not private_rows,
        f"{len(intake_rows)} intake rows have no private path or credential markers",
        "private markers in: " + ", ".join(private_rows),
    )
    unknown_expected = [
        row.get("intake_id", "unknown")
        for row in intake_rows
        if row.get("template_id", "") not in templates
        and row.get("expected_decision") != "REJECT_UNKNOWN_TEMPLATE"
    ]
    add_check(
        checks,
        "RCI-04",
        "unknown-template fail-closed",
        not unknown_expected,
        "unknown template examples are expected to fail closed",
        "unexpected unknown templates in: " + ", ".join(unknown_expected),
    )
    expected_mismatches = [
        row.get("intake_id", "unknown")
        for row in decisions
        if row.get("expected_match") != "PASS"
    ]
    add_check(
        checks,
        "RCI-05",
        "expected decision agreement",
        not expected_mismatches,
        "computed application decisions match expected labels",
        "decision mismatches in: " + ", ".join(expected_mismatches),
    )
    decision_set = {row.get("decision", "") for row in decisions}
    add_check(
        checks,
        "RCI-06",
        "application decision coverage",
        DECISIONS.issubset(decision_set),
        "intake examples cover accept, rewrite, suppress, support-only, patchwork reject, and unknown-template reject",
        f"found decisions {sorted(decision_set)}; expected at least {sorted(DECISIONS)}",
    )
    emitted_forbidden = [
        row.get("intake_id", "unknown")
        for row in decisions
        if row.get("recommended_output") != "bottom_T"
        and any(
            normalize(row.get("recommended_output", "")) == normalize(t.get("forbidden_claim", ""))
            for t in templates.values()
        )
    ]
    add_check(
        checks,
        "RCI-07",
        "forbidden output firewall",
        not emitted_forbidden,
        "no recommended output equals a registered forbidden claim",
        "forbidden output emitted in: " + ", ".join(emitted_forbidden),
    )
    support_promotions = [
        row.get("intake_id", "unknown")
        for row in decisions
        if row.get("decision") == "ACCEPT_LICENSED"
        and templates.get(row.get("template_id", ""), {}).get("template_role") == "support_only"
    ]
    add_check(
        checks,
        "RCI-08",
        "support-only not accepted as headline",
        not support_promotions,
        "support-only intake rows are rewritten with support-only boundary",
        "support-only rows accepted as headline in: " + ", ".join(support_promotions),
    )
    action_coverage = {
        templates.get(row.get("template_id", ""), {}).get("action_mapping", "")
        for row in decisions
        if row.get("decision") in {"ACCEPT_LICENSED", "REWRITE_TO_LICENSED", "SUPPRESS_BOTTOM"}
    }
    add_check(
        checks,
        "RCI-09",
        "main application action coverage",
        ACTION_FAMILIES.issubset(action_coverage),
        "mainline intake rows exercise all five action families",
        f"found actions {sorted(action_coverage)}; expected {sorted(ACTION_FAMILIES)}",
    )

    decision_counts = Counter(row.get("decision", "") for row in decisions)
    checks_failed = sum(1 for row in checks if row["status"] != "PASS")
    checks_passed = len(checks) - checks_failed
    summary = {
        "status": "PASS" if checks_failed == 0 else "FAIL",
        "intake_rows": len(intake_rows),
        "accepted": decision_counts["ACCEPT_LICENSED"],
        "rewritten": decision_counts["REWRITE_TO_LICENSED"],
        "suppressed": decision_counts["SUPPRESS_BOTTOM"],
        "support_only": decision_counts["SUPPORT_ONLY_REWRITE"],
        "rejected": decision_counts["REJECT_PATCHWORK"]
        + decision_counts["REJECT_UNKNOWN_TEMPLATE"],
        "checks_passed": checks_passed,
        "checks_failed": checks_failed,
        "tool_boundary": (
            "registered-template reviewer intake workflow; no arbitrary prose "
            "parser and no support-only promotion"
        ),
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    write_json(output_dir / "reviewer_claim_intake_summary.json", summary)
    write_csv(
        output_dir / "reviewer_claim_intake_checks.csv",
        checks,
        ["check_id", "label", "status", "evidence"],
    )
    write_csv(
        output_dir / "reviewer_claim_intake_decisions.csv",
        decisions,
        [
            "intake_id",
            "template_id",
            "decision",
            "recommended_output",
            "explanation",
            "source_anchor",
            "expected_decision",
            "expected_match",
        ],
    )
    (output_dir / "reviewer_claim_intake_report.md").write_text(
        build_markdown(summary, checks, decisions),
        encoding="utf-8",
    )
    (output_dir / "reviewer_claim_intake_report.html").write_text(
        build_html(summary, checks, decisions),
        encoding="utf-8",
    )

    if checks_failed:
        print("FAIL reviewer claim intake")
    else:
        print("PASS reviewer claim intake")
    print(f"intake_rows: {summary['intake_rows']}")
    print(f"accepted: {summary['accepted']}")
    print(f"rewritten: {summary['rewritten']}")
    print(f"suppressed: {summary['suppressed']}")
    print(f"support_only: {summary['support_only']}")
    print(f"rejected: {summary['rejected']}")
    print(f"checks_passed: {checks_passed}")
    print(f"checks_failed: {checks_failed}")
    print("outputs:")
    for name in [
        "reviewer_claim_intake_report.md",
        "reviewer_claim_intake_report.html",
        "reviewer_claim_intake_summary.json",
        "reviewer_claim_intake_checks.csv",
        "reviewer_claim_intake_decisions.csv",
    ]:
        print(f"- {args.output.rstrip('/')}/{name}")
    return 0 if checks_failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
