#!/usr/bin/env python3
"""Run batch claim-template admission checks for ClaimContractBench.

This runner turns scope expansion into an interface test. A new claim template
is not admitted because a domain is interesting or metric-rich; it is admitted
only if it supplies the typed fields needed by the claim-contract workflow.

The script is standard-library only and uses public-safe release-root assets.
It does not parse arbitrary prose or promote support-only adapters to headline
claims.
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
    "schema": "artifact/claim_template_admission_schema_20260521.json",
    "cases": "artifact/claim_template_admission_cases_20260521.csv",
    "casebook": "data/claim_passport_casebook_20260519.csv",
    "nab_visual": "data/nab_adapter_visual_passport_rows_20260519.csv",
}

ACTION_FAMILIES = {
    "emit_as_written",
    "relabel_as_upper_bound",
    "weaken_to_diagnostic",
    "rewrite_to_decision_local",
    "suppress_fallback",
}

EXPECTED_CASE_COLUMNS = [
    "template_id",
    "domain_id",
    "domain_family",
    "template_role",
    "evidence_unit",
    "claim_template",
    "G_binding",
    "Q_binding",
    "U_binding",
    "action_mapping",
    "preorder_relation",
    "forbidden_claim",
    "visual_or_case_anchor",
    "expected_level",
    "expected_verdict",
    "boundary_note",
]

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
        description="Validate batch claim-template admission cases."
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Release root to audit. Default: current directory.",
    )
    parser.add_argument(
        "--output",
        default="reports/claim_template_admission_20260521",
        help="Report output directory. Relative paths are resolved under root.",
    )
    parser.add_argument(
        "--cases",
        default=FILES["cases"],
        help="Template-admission CSV to validate. Relative paths are resolved under root.",
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


def resolve_input(root: Path, value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = root / path
    return path.resolve()


def short(text: str, limit: int = 150) -> str:
    text = " ".join((text or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "..."


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


def compute_verdict(
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


def contains_private_marker(row: dict[str, str]) -> bool:
    text = " ".join(str(value or "") for value in row.values())
    return any(pattern.search(text) for pattern in PRIVATE_PATTERNS)


def anchor_status(
    row: dict[str, str], casebook_ids: set[str], nab_ids: set[str]
) -> tuple[bool, str]:
    anchor = row.get("visual_or_case_anchor", "").strip()
    verdict = row.get("computed_verdict", "")
    if not anchor:
        if verdict.startswith("ADMIT"):
            return False, "admitted template lacks an anchor"
        return True, "no anchor required for non-admitted template"
    if anchor.startswith("CP-"):
        return anchor in casebook_ids, f"casebook anchor {anchor}"
    if anchor.startswith("NAB-VIS-"):
        return anchor in nab_ids, f"NAB visual anchor {anchor}"
    return False, f"unknown anchor namespace {anchor}"


def build_verdict_rows(
    rows: list[dict[str, str]],
    critical_fields: list[str],
    casebook_ids: set[str],
    nab_ids: set[str],
) -> list[dict[str, str]]:
    verdict_rows: list[dict[str, str]] = []
    for row in rows:
        computed_level, computed_verdict, missing = compute_verdict(row, critical_fields)
        enriched = dict(row)
        enriched["computed_level"] = computed_level
        enriched["computed_verdict"] = computed_verdict
        enriched["missing_critical_fields"] = ";".join(missing)
        ok_anchor, anchor_note = anchor_status(enriched, casebook_ids, nab_ids)
        enriched["anchor_check"] = "PASS" if ok_anchor else "FAIL"
        enriched["anchor_note"] = anchor_note
        enriched["private_marker_check"] = "FAIL" if contains_private_marker(row) else "PASS"
        enriched["expected_match"] = (
            "PASS"
            if computed_level == row.get("expected_level")
            and computed_verdict == row.get("expected_verdict")
            else "FAIL"
        )
        verdict_rows.append(enriched)
    return verdict_rows


def build_markdown(
    summary: dict[str, object],
    checks: list[dict[str, str]],
    verdict_rows: list[dict[str, str]],
) -> str:
    lines: list[str] = []
    lines.append("# Claim Template Admission Report")
    lines.append("")
    lines.append("Status: generated from release-root public-safe assets.")
    lines.append("")
    lines.append("## Contribution Target")
    lines.append("")
    lines.append(
        "This report tests whether new claims and new domains can enter the "
        "typed claim-contract workflow by satisfying an explicit adapter "
        "admission interface. It is meant to distinguish real scope expansion "
        "from benchmark-table sprawl."
    )
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Item | Value |")
    lines.append("| --- | ---: |")
    for key in [
        "templates",
        "admitted_mainline",
        "admitted_support_only",
        "boundary_probe",
        "rejected",
        "checks_passed",
        "checks_failed",
    ]:
        lines.append(f"| {key} | {summary[key]} |")
    lines.append("")
    lines.append("## Admission Checks")
    lines.append("")
    lines.append("| Check | Status | Evidence |")
    lines.append("| --- | --- | --- |")
    for row in checks:
        lines.append(
            f"| {row['check_id']} {row['label']} | {row['status']} | "
            f"{short(row['evidence'], 220)} |"
        )
    lines.append("")
    lines.append("## Template Verdicts")
    lines.append("")
    lines.append(
        "| Template | Role | Action | Computed Verdict | Missing Fields | Boundary |"
    )
    lines.append("| --- | --- | --- | --- | --- | --- |")
    for row in verdict_rows:
        lines.append(
            f"| {row['template_id']} | {row['template_role']} | "
            f"{row['action_mapping']} | {row['computed_verdict']} | "
            f"{row['missing_critical_fields'] or 'none'} | "
            f"{short(row['boundary_note'], 160)} |"
        )
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append(
        "- The five core templates are admitted as mainline because they already "
        "instantiate the public claim passport."
    )
    lines.append(
        "- The three NAB templates are admitted only as support-only adapter "
        "templates: they show the interface can accept a distinct evidence unit, "
        "but they do not become anomaly-detection validation or a headline claim."
    )
    lines.append(
        "- The AI4I probe is rejected by design because it has an evidence family "
        "but lacks finite claim templates, G/Q/U bindings, action mapping, typed "
        "preorder, forbidden claim, and visual passport row."
    )
    lines.append("")
    lines.append("## Current Limit")
    lines.append("")
    lines.append(
        "The runner admits rows that are already expressed in the typed template "
        "schema. It does not infer G/Q/U or action mappings from arbitrary prose. "
        "The next high-value upgrade is to normalize the full 375-event operator "
        "trace into this release-root admission interface."
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
    verdict_rows: list[dict[str, str]],
) -> str:
    metrics = []
    for key in [
        "templates",
        "admitted_mainline",
        "admitted_support_only",
        "boundary_probe",
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
  <title>Claim Template Admission Report</title>
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
  <h1>Claim Template Admission Report</h1>
  <p>Generated from public-safe release-root assets. The report tests whether
  candidate claim templates instantiate the full adapter interface before they
  enter the audit workflow.</p>
  <section class="metrics">{''.join(metrics)}</section>
  <h2>Admission Checks</h2>
  {html_table(check_rows, ["check", "status", "evidence"])}
  <h2>Template Verdicts</h2>
  {html_table(verdict_rows, ["template_id", "domain_id", "template_role", "action_mapping", "computed_level", "computed_verdict", "missing_critical_fields", "boundary_note"])}
  <h2>Current Limit</h2>
  <div class="note"><p>The runner checks typed rows. It does not infer the
  template contract from arbitrary prose; that remains outside the present
  release boundary.</p></div>
</main>
</body>
</html>
"""


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    output_dir = resolve_output(root, args.output)
    cases_path = resolve_input(root, args.cases)
    default_cases_path = (root / FILES["cases"]).resolve()
    default_case_set = cases_path == default_cases_path

    failures: list[str] = []
    try:
        schema = json.loads((root / FILES["schema"]).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        schema = {}
        failures.append(f"{FILES['schema']}: could not read schema: {exc}")

    try:
        cases, case_header = read_csv(cases_path)
    except OSError as exc:
        cases, case_header = [], []
        failures.append(f"{cases_path}: could not read cases: {exc}")

    try:
        casebook_rows, _ = read_csv(root / FILES["casebook"])
    except OSError as exc:
        casebook_rows = []
        failures.append(f"{FILES['casebook']}: could not read casebook: {exc}")

    try:
        nab_rows, _ = read_csv(root / FILES["nab_visual"])
    except OSError as exc:
        nab_rows = []
        failures.append(f"{FILES['nab_visual']}: could not read NAB visual rows: {exc}")

    critical_fields = list(schema.get("critical_fields_for_admission", []))
    casebook_ids = {row.get("event_id", "") for row in casebook_rows}
    nab_ids = {row.get("display_id", "") for row in nab_rows}
    verdict_rows = build_verdict_rows(cases, critical_fields, casebook_ids, nab_ids)

    checks: list[dict[str, str]] = []
    add_check(
        checks,
        "ADM-01",
        "inputs present",
        not failures and bool(cases) and bool(critical_fields),
        "schema, cases, casebook, and NAB visual rows loaded",
        "; ".join(failures) if failures else "cases or critical fields are empty",
    )
    add_check(
        checks,
        "ADM-02",
        "case header alignment",
        case_header == EXPECTED_CASE_COLUMNS,
        f"case header has {len(case_header)} expected columns",
        f"case header={case_header}; expected={EXPECTED_CASE_COLUMNS}",
    )

    private_rows = [
        row.get("template_id", "unknown")
        for row in verdict_rows
        if row.get("private_marker_check") != "PASS"
    ]
    add_check(
        checks,
        "ADM-03",
        "public-safe template text",
        not private_rows,
        f"{len(verdict_rows)} templates have no private path or credential markers",
        "private markers in: " + ", ".join(private_rows),
    )

    match_failures = [
        row.get("template_id", "unknown")
        for row in verdict_rows
        if row.get("expected_match") != "PASS"
    ]
    add_check(
        checks,
        "ADM-04",
        "expected verdict agreement",
        not match_failures,
        "computed levels and verdicts match expected admission labels",
        "expected mismatch in: " + ", ".join(match_failures),
    )

    anchor_failures = [
        row.get("template_id", "unknown")
        for row in verdict_rows
        if row.get("anchor_check") != "PASS"
    ]
    add_check(
        checks,
        "ADM-05",
        "anchor resolution",
        not anchor_failures,
        "admitted templates resolve to CP or NAB visual anchors",
        "anchor failures in: " + ", ".join(anchor_failures),
    )

    admitted = [
        row for row in verdict_rows if row.get("computed_verdict", "").startswith("ADMIT")
    ]
    missing_in_admitted = [
        row.get("template_id", "unknown")
        for row in admitted
        if row.get("missing_critical_fields")
    ]
    add_check(
        checks,
        "ADM-06",
        "critical-field completeness for admitted templates",
        not missing_in_admitted,
        f"{len(admitted)} admitted templates provide all nine critical fields",
        "admitted rows missing fields: " + ", ".join(missing_in_admitted),
    )

    mainline_actions = {
        row.get("action_mapping", "")
        for row in verdict_rows
        if row.get("computed_verdict") == "ADMIT_MAINLINE_TEMPLATE"
    }
    add_check(
        checks,
        "ADM-07",
        "mainline action coverage",
        (not default_case_set) or mainline_actions == ACTION_FAMILIES,
        (
            "custom template packet: action-family coverage is not required"
            if not default_case_set
            else "mainline templates cover all five action families"
        ),
        f"found mainline actions {sorted(mainline_actions)}; expected {sorted(ACTION_FAMILIES)}",
    )

    support_promotions = [
        row.get("template_id", "unknown")
        for row in verdict_rows
        if row.get("template_role") == "support_only"
        and row.get("computed_verdict") == "ADMIT_MAINLINE_TEMPLATE"
    ]
    add_check(
        checks,
        "ADM-08",
        "support-only ceiling",
        not support_promotions,
        "support-only rows are not promoted to mainline or headline claims",
        "support rows promoted unexpectedly: " + ", ".join(support_promotions),
    )

    rejected_rows = [
        row for row in verdict_rows if row.get("computed_verdict") == "REJECT_PATCHWORK"
    ]
    add_check(
        checks,
        "ADM-09",
        "boundary rejection remains active",
        (not default_case_set)
        or any(row.get("domain_id") == "ai4i_predictive_maintenance" for row in rejected_rows),
        (
            "custom template packet: fixed AI4I boundary probe is not required"
            if not default_case_set
            else "AI4I boundary probe is rejected until it supplies the adapter contract"
        ),
        "no rejected AI4I boundary probe found",
    )

    forbidden_missing = [
        row.get("template_id", "unknown")
        for row in admitted
        if not row.get("forbidden_claim", "").strip()
        or not row.get("boundary_note", "").strip()
    ]
    add_check(
        checks,
        "ADM-10",
        "forbidden-claim and boundary discipline",
        not forbidden_missing,
        "all admitted templates include forbidden claims and boundary notes",
        "missing forbidden/boundary in: " + ", ".join(forbidden_missing),
    )

    verdict_counts = Counter(row.get("computed_verdict", "") for row in verdict_rows)
    checks_failed = sum(1 for row in checks if row["status"] != "PASS")
    checks_passed = len(checks) - checks_failed
    summary = {
        "status": "PASS" if checks_failed == 0 else "FAIL",
        "templates": len(verdict_rows),
        "admitted_mainline": verdict_counts["ADMIT_MAINLINE_TEMPLATE"],
        "admitted_support_only": verdict_counts["ADMIT_SUPPORT_ONLY_TEMPLATE"],
        "boundary_probe": verdict_counts["KEEP_BOUNDARY_PROBE"],
        "rejected": verdict_counts["REJECT_PATCHWORK"],
        "checks_passed": checks_passed,
        "checks_failed": checks_failed,
        "critical_fields": critical_fields,
        "tool_boundary": (
            "typed template admission over release rows; no arbitrary prose "
            "inference and no automatic support-only promotion"
        ),
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    write_json(output_dir / "claim_template_admission_summary.json", summary)
    write_csv(
        output_dir / "claim_template_admission_checks.csv",
        checks,
        ["check_id", "label", "status", "evidence"],
    )
    write_csv(
        output_dir / "claim_template_admission_verdicts.csv",
        verdict_rows,
        EXPECTED_CASE_COLUMNS
        + [
            "computed_level",
            "computed_verdict",
            "missing_critical_fields",
            "anchor_check",
            "anchor_note",
            "private_marker_check",
            "expected_match",
        ],
    )
    (output_dir / "claim_template_admission_report.md").write_text(
        build_markdown(summary, checks, verdict_rows),
        encoding="utf-8",
    )
    (output_dir / "claim_template_admission_report.html").write_text(
        build_html(summary, checks, verdict_rows),
        encoding="utf-8",
    )

    if checks_failed:
        print("FAIL claim template admission")
    else:
        print("PASS claim template admission")
    print(f"templates: {summary['templates']}")
    print(f"admitted_mainline: {summary['admitted_mainline']}")
    print(f"admitted_support_only: {summary['admitted_support_only']}")
    print(f"boundary_probe: {summary['boundary_probe']}")
    print(f"rejected: {summary['rejected']}")
    print(f"checks_passed: {checks_passed}")
    print(f"checks_failed: {checks_failed}")
    print("outputs:")
    for name in [
        "claim_template_admission_report.md",
        "claim_template_admission_report.html",
        "claim_template_admission_summary.json",
        "claim_template_admission_checks.csv",
        "claim_template_admission_verdicts.csv",
    ]:
        print(f"- {args.output.rstrip('/')}/{name}")
    return 0 if checks_failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
