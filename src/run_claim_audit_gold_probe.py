#!/usr/bin/env python3
"""Run a small gold probe for claim-audit routing and decisions.

The reviewer claim-intake runner assumes an upstream user or extractor has
already supplied a template id. This probe makes that boundary explicit: some
rows should call a registered template, some need adapter admission first, and
some are outside the current empirical claim-audit scope.
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter
import html
import importlib.util
import json
from pathlib import Path
import re
import sys


FILES = {
    "schema": "artifact/claim_audit_gold_probe_schema_20260521.json",
    "cases": "artifact/claim_audit_gold_probe_cases_20260521.csv",
    "template_cases": "artifact/claim_template_admission_cases_20260521.csv",
    "casebook": "data/claim_passport_casebook_20260519.csv",
    "nab_visual": "data/nab_adapter_visual_passport_rows_20260519.csv",
}

EXPECTED_COLUMNS = [
    "gold_id",
    "source_family",
    "source_reference",
    "route_label",
    "template_id",
    "submitted_claim",
    "intended_use",
    "expected_decision",
    "expected_output_hint",
    "rationale",
]

ROUTE_LABELS = {
    "CALL_REGISTERED_TEMPLATE",
    "NEEDS_TEMPLATE_ADMISSION",
    "OUT_OF_SCOPE_DO_NOT_CALL",
}

INTAKE_DECISIONS = {
    "ACCEPT_LICENSED",
    "REWRITE_TO_LICENSED",
    "SUPPRESS_BOTTOM",
    "SUPPORT_ONLY_REWRITE",
    "REJECT_PATCHWORK",
    "REJECT_UNKNOWN_TEMPLATE",
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
        description="Evaluate the current claim-audit routing and decision gold probe."
    )
    parser.add_argument("--root", default=".", help="Release root. Default: current directory.")
    parser.add_argument(
        "--output",
        default="reports/claim_audit_gold_probe_20260521",
        help="Report output directory. Relative paths are resolved under root.",
    )
    return parser.parse_args()


def import_intake_runner(root: Path):
    module_path = root / "src" / "run_reviewer_claim_intake.py"
    spec = importlib.util.spec_from_file_location("run_reviewer_claim_intake", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"could not import {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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


def build_templates(intake_runner, template_cases: list[dict[str, str]]):
    critical = [
        "evidence_unit",
        "claim_template",
        "G_binding",
        "Q_binding",
        "U_binding",
        "action_mapping",
        "preorder_relation",
        "forbidden_claim",
        "visual_or_case_anchor",
    ]
    return intake_runner.build_template_rows(template_cases, critical)


def route_and_decide(
    row: dict[str, str],
    intake_runner,
    templates: dict[str, dict[str, str]],
    casebook_by_id: dict[str, dict[str, str]],
    nab_by_id: dict[str, dict[str, str]],
) -> dict[str, str]:
    route = row.get("route_label", "")
    expected = row.get("expected_decision", "")
    if route == "CALL_REGISTERED_TEMPLATE":
        intake_row = {
            "intake_id": row.get("gold_id", ""),
            "template_id": row.get("template_id", ""),
            "submitted_claim": row.get("submitted_claim", ""),
            "expected_decision": expected,
        }
        decision = intake_runner.decide_intake(
            intake_row, templates, casebook_by_id, nab_by_id
        )
        computed = decision["decision"]
        output = decision["recommended_output"]
        explanation = decision["explanation"]
    elif route == "NEEDS_TEMPLATE_ADMISSION":
        computed = "NEEDS_TEMPLATE_ADMISSION"
        output = "adapter_admission_required"
        explanation = (
            "The text is in a relevant application family, but the current "
            "release has no registered template id for this family."
        )
    elif route == "OUT_OF_SCOPE_DO_NOT_CALL":
        computed = "OUT_OF_SCOPE_DO_NOT_CALL"
        output = "not_a_current_tool_call"
        explanation = (
            "The text asks for proof, novelty, code, legal, or safety judgment "
            "outside the current empirical metric-to-claim audit scope."
        )
    else:
        computed = "INVALID_ROUTE"
        output = "bottom_T"
        explanation = f"Unknown route_label: {route}"

    return {
        "gold_id": row.get("gold_id", ""),
        "source_family": row.get("source_family", ""),
        "route_label": route,
        "template_id": row.get("template_id", ""),
        "expected_decision": expected,
        "computed_decision": computed,
        "decision_match": "PASS" if computed == expected else "FAIL",
        "recommended_output": output,
        "explanation": explanation,
        "submitted_claim": row.get("submitted_claim", ""),
    }


def build_markdown(summary: dict[str, object], checks: list[dict[str, str]], rows: list[dict[str, str]]) -> str:
    lines: list[str] = []
    lines.append("# Claim Audit Gold Probe Report")
    lines.append("")
    lines.append("Status: generated from public-safe release-root assets.")
    lines.append("")
    lines.append("## Purpose")
    lines.append("")
    lines.append(
        "This probe separates three questions: when a registered template can be "
        "called, when a relevant text needs adapter admission before the tool can "
        "act, and when the text is outside the current empirical claim-audit scope."
    )
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Item | Value |")
    lines.append("| --- | ---: |")
    for key in [
        "gold_rows",
        "registered_template_rows",
        "adapter_needed_rows",
        "out_of_scope_rows",
        "decision_matches",
        "decision_mismatches",
        "autonomous_routing_supported",
        "checks_passed",
        "checks_failed",
    ]:
        lines.append(f"| {key} | {summary[key]} |")
    lines.append("")
    lines.append("## Checks")
    lines.append("")
    lines.append("| Check | Status | Evidence |")
    lines.append("| --- | --- | --- |")
    for row in checks:
        lines.append(
            f"| {row['check_id']} {row['label']} | {row['status']} | "
            f"{short(row['evidence'], 220)} |"
        )
    lines.append("")
    lines.append("## Gold Rows")
    lines.append("")
    lines.append(
        "| Gold | Route | Template | Expected | Computed | Match | Explanation |"
    )
    lines.append("| --- | --- | --- | --- | --- | --- | --- |")
    for row in rows:
        lines.append(
            f"| {row['gold_id']} | {row['route_label']} | "
            f"{row['template_id'] or 'none'} | {row['expected_decision']} | "
            f"{row['computed_decision']} | {row['decision_match']} | "
            f"{short(row['explanation'], 180)} |"
        )
    lines.append("")
    lines.append("## Boundary")
    lines.append("")
    lines.append(
        "The current release does not include autonomous full-paper routing. A "
        "human reviewer, author, or upstream LLM extractor must propose candidate "
        "claims, template ids, and evidence anchors. This probe validates the "
        "deterministic back-end behavior once that routing information is supplied "
        "or explicitly marked as missing."
    )
    lines.append("")
    return "\n".join(lines)


def html_table(rows: list[dict[str, str]], columns: list[str]) -> str:
    header = "".join(f"<th>{html.escape(column)}</th>" for column in columns)
    body = []
    for row in rows:
        cells = "".join(
            f"<td>{html.escape(short(row.get(column, ''), 220))}</td>"
            for column in columns
        )
        body.append(f"<tr>{cells}</tr>")
    return f"<table><thead><tr>{header}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def build_html(summary: dict[str, object], checks: list[dict[str, str]], rows: list[dict[str, str]]) -> str:
    metrics = []
    for key in [
        "gold_rows",
        "registered_template_rows",
        "adapter_needed_rows",
        "out_of_scope_rows",
        "decision_mismatches",
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
  <title>Claim Audit Gold Probe Report</title>
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
  <h1>Claim Audit Gold Probe Report</h1>
  <p>Generated from public-safe release-root assets. The report distinguishes
  registered-template calls from adapter-needed and out-of-scope text.</p>
  <section class="metrics">{''.join(metrics)}</section>
  <h2>Checks</h2>
  {html_table(check_rows, ["check", "status", "evidence"])}
  <h2>Gold Rows</h2>
  {html_table(rows, ["gold_id", "route_label", "template_id", "expected_decision", "computed_decision", "decision_match", "explanation"])}
  <h2>Boundary</h2>
  <div class="note"><p>The current release does not include autonomous full-paper
  routing. It validates deterministic back-end decisions after a human or
  upstream extractor supplies routing information.</p></div>
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
        json.loads((root / FILES["schema"]).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        failures.append(f"{FILES['schema']}: could not read schema: {exc}")
    try:
        cases, header = read_csv(root / FILES["cases"])
    except (OSError, csv.Error) as exc:
        cases, header = [], []
        failures.append(f"{FILES['cases']}: could not read cases: {exc}")
    try:
        template_cases, _ = read_csv(root / FILES["template_cases"])
        casebook_rows, _ = read_csv(root / FILES["casebook"])
        nab_rows, _ = read_csv(root / FILES["nab_visual"])
    except (OSError, csv.Error) as exc:
        template_cases, casebook_rows, nab_rows = [], [], []
        failures.append(f"supporting release inputs could not be read: {exc}")

    intake_runner = import_intake_runner(root)
    templates = build_templates(intake_runner, template_cases)
    casebook_by_id = {row.get("event_id", ""): row for row in casebook_rows}
    nab_by_id = {row.get("display_id", ""): row for row in nab_rows}
    result_rows = [
        route_and_decide(row, intake_runner, templates, casebook_by_id, nab_by_id)
        for row in cases
    ]

    route_counts = Counter(row.get("route_label", "") for row in cases)
    decision_counts = Counter(row.get("computed_decision", "") for row in result_rows)
    mismatch_rows = [row["gold_id"] for row in result_rows if row["decision_match"] != "PASS"]
    private_rows = [row.get("gold_id", "") for row in cases if contains_private_marker(row)]
    invalid_routes = [
        row.get("gold_id", "")
        for row in cases
        if row.get("route_label", "") not in ROUTE_LABELS
    ]
    invalid_decisions = [
        row.get("gold_id", "")
        for row in cases
        if row.get("route_label", "") == "CALL_REGISTERED_TEMPLATE"
        and row.get("expected_decision", "") not in INTAKE_DECISIONS
    ]

    checks: list[dict[str, str]] = []
    add_check(
        checks,
        "GP-01",
        "inputs present",
        not failures and bool(cases),
        "schema, cases, template cases, casebook, and NAB visual rows loaded",
        "; ".join(failures) if failures else "gold cases are empty",
    )
    add_check(
        checks,
        "GP-02",
        "header alignment",
        header == EXPECTED_COLUMNS,
        f"gold header has {len(header)} expected columns",
        f"gold header={header}; expected={EXPECTED_COLUMNS}",
    )
    add_check(
        checks,
        "GP-03",
        "route labels valid",
        not invalid_routes,
        "all route labels are in the declared routing enum",
        f"invalid route rows: {invalid_routes}",
    )
    add_check(
        checks,
        "GP-04",
        "registered expectations valid",
        not invalid_decisions,
        "registered-template rows use reviewer-intake decisions",
        f"invalid registered expected decisions: {invalid_decisions}",
    )
    add_check(
        checks,
        "GP-05",
        "all gold decisions match",
        not mismatch_rows,
        f"{len(result_rows)} / {len(result_rows)} gold rows matched expected outcomes",
        f"decision mismatches: {mismatch_rows}",
    )
    add_check(
        checks,
        "GP-06",
        "private marker scan",
        not private_rows,
        "no private coordination markers or credential-like patterns in gold cases",
        f"private marker rows: {private_rows}",
    )
    add_check(
        checks,
        "GP-07",
        "routing boundary explicit",
        route_counts["NEEDS_TEMPLATE_ADMISSION"] > 0
        and route_counts["OUT_OF_SCOPE_DO_NOT_CALL"] > 0,
        (
            "gold probe includes adapter-needed and out-of-scope rows, so it "
            "does not overclaim autonomous routing"
        ),
        f"route counts: {dict(route_counts)}",
    )

    checks_failed = sum(1 for row in checks if row["status"] == "FAIL")
    summary = {
        "gold_rows": len(cases),
        "registered_template_rows": route_counts["CALL_REGISTERED_TEMPLATE"],
        "adapter_needed_rows": route_counts["NEEDS_TEMPLATE_ADMISSION"],
        "out_of_scope_rows": route_counts["OUT_OF_SCOPE_DO_NOT_CALL"],
        "decision_matches": sum(1 for row in result_rows if row["decision_match"] == "PASS"),
        "decision_mismatches": len(mismatch_rows),
        "autonomous_routing_supported": "no",
        "computed_decision_counts": dict(sorted(decision_counts.items())),
        "checks_passed": len(checks) - checks_failed,
        "checks_failed": checks_failed,
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(
        output_dir / "claim_audit_gold_probe_decisions.csv",
        result_rows,
        [
            "gold_id",
            "source_family",
            "route_label",
            "template_id",
            "expected_decision",
            "computed_decision",
            "decision_match",
            "recommended_output",
            "explanation",
            "submitted_claim",
        ],
    )
    write_csv(
        output_dir / "claim_audit_gold_probe_checks.csv",
        checks,
        ["check_id", "label", "status", "evidence"],
    )
    write_json(output_dir / "claim_audit_gold_probe_summary.json", summary)
    (output_dir / "claim_audit_gold_probe_report.md").write_text(
        build_markdown(summary, checks, result_rows), encoding="utf-8"
    )
    (output_dir / "claim_audit_gold_probe_report.html").write_text(
        build_html(summary, checks, result_rows), encoding="utf-8"
    )

    if checks_failed:
        print("FAIL claim audit gold probe")
        print(f"checks_failed: {checks_failed}")
        return 1
    print("PASS claim audit gold probe")
    print(f"gold_rows: {summary['gold_rows']}")
    print(f"registered_template_rows: {summary['registered_template_rows']}")
    print(f"adapter_needed_rows: {summary['adapter_needed_rows']}")
    print(f"out_of_scope_rows: {summary['out_of_scope_rows']}")
    print(f"decision_matches: {summary['decision_matches']}")
    print("autonomous_routing_supported: no")
    print("outputs:")
    for name in [
        "claim_audit_gold_probe_report.md",
        "claim_audit_gold_probe_report.html",
        "claim_audit_gold_probe_summary.json",
        "claim_audit_gold_probe_checks.csv",
        "claim_audit_gold_probe_decisions.csv",
    ]:
        print(f"- {output_dir.relative_to(root) / name if output_dir.is_relative_to(root) else output_dir / name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
