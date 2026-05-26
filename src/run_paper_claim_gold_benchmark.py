#!/usr/bin/env python3
"""Evaluate the paper-claim gold benchmark for claim-audit reliability.

This benchmark is deliberately stricter than the smaller gold probe. It samples
public-safe paraphrased claim fragments from 40 empirical ML or evaluation
papers, plus eight registered-template control rows. The current release is not
an autonomous PDF reader: external paper rows either require template admission
or are out of scope, while registered controls exercise the deterministic
claim-intake backend.
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
import html
import importlib.util
import json
from pathlib import Path
import re
import sys


FILES = {
    "schema": "artifact/paper_claim_gold_benchmark_schema_20260521.json",
    "sources": "artifact/paper_claim_gold_benchmark_sources_20260521.csv",
    "cases": "artifact/paper_claim_gold_benchmark_cases_20260521.csv",
    "template_cases": "artifact/claim_template_admission_cases_20260521.csv",
    "casebook": "data/claim_passport_casebook_20260519.csv",
    "nab_visual": "data/nab_adapter_visual_passport_rows_20260519.csv",
}

EXPECTED_SOURCE_COLUMNS = [
    "paper_id",
    "source_role",
    "source_family",
    "title",
    "primary_source",
    "year_or_version",
    "benchmark_role",
]

EXPECTED_CASE_COLUMNS = [
    "claim_id",
    "paper_id",
    "source_family",
    "case_role",
    "claim_index",
    "route_label",
    "template_id",
    "submitted_claim",
    "intended_use",
    "gold_action_after_admission",
    "current_expected_action",
    "evidence_anchor",
    "rationale",
]

ROUTE_LABELS = {
    "CALL_REGISTERED_TEMPLATE",
    "NEEDS_TEMPLATE_ADMISSION",
    "OUT_OF_SCOPE_DO_NOT_CALL",
}

GOLD_ACTIONS = {
    "ACCEPT",
    "REWRITE",
    "WEAKEN",
    "SUPPORT_ONLY",
    "SUPPRESS",
    "REJECT",
    "OUT_OF_SCOPE",
}

CURRENT_ACTIONS = {
    "ACCEPT",
    "REWRITE",
    "WEAKEN",
    "SUPPORT_ONLY",
    "SUPPRESS",
    "REJECT",
    "UNSUPPORTED_TEMPLATE",
    "OUT_OF_SCOPE",
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
        description="Evaluate public-safe paper-claim gold benchmark rows."
    )
    parser.add_argument("--root", default=".", help="Release root. Default: current directory.")
    parser.add_argument(
        "--output",
        default="reports/paper_claim_gold_benchmark_20260521",
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


def current_action_from_intake(
    decision: str, template_id: str, templates: dict[str, dict[str, str]]
) -> str:
    if decision == "ACCEPT_LICENSED":
        return "ACCEPT"
    if decision == "SUPPORT_ONLY_REWRITE":
        return "SUPPORT_ONLY"
    if decision == "SUPPRESS_BOTTOM":
        return "SUPPRESS"
    if decision in {"REJECT_PATCHWORK", "REJECT_UNKNOWN_TEMPLATE"}:
        return "REJECT"
    if decision == "REWRITE_TO_LICENSED":
        action = templates.get(template_id, {}).get("action_mapping", "")
        if action == "weaken_to_diagnostic":
            return "WEAKEN"
        if action == "suppress_fallback":
            return "SUPPRESS"
        return "REWRITE"
    return "REJECT"


def route_and_decide(
    row: dict[str, str],
    intake_runner,
    templates: dict[str, dict[str, str]],
    casebook_by_id: dict[str, dict[str, str]],
    nab_by_id: dict[str, dict[str, str]],
) -> dict[str, str]:
    route = row.get("route_label", "")
    template_id = row.get("template_id", "")
    if route == "CALL_REGISTERED_TEMPLATE":
        intake_row = {
            "intake_id": row.get("claim_id", ""),
            "template_id": template_id,
            "submitted_claim": row.get("submitted_claim", ""),
            "expected_decision": "",
        }
        decision = intake_runner.decide_intake(
            intake_row, templates, casebook_by_id, nab_by_id
        )
        backend_decision = decision["decision"]
        computed_action = current_action_from_intake(backend_decision, template_id, templates)
        output = decision["recommended_output"]
        explanation = decision["explanation"]
    elif route == "NEEDS_TEMPLATE_ADMISSION":
        backend_decision = "NEEDS_TEMPLATE_ADMISSION"
        computed_action = "UNSUPPORTED_TEMPLATE"
        output = "adapter_admission_required"
        explanation = (
            "Relevant empirical-claim text, but the current release has no "
            "registered claim template for this paper family."
        )
    elif route == "OUT_OF_SCOPE_DO_NOT_CALL":
        backend_decision = "OUT_OF_SCOPE_DO_NOT_CALL"
        computed_action = "OUT_OF_SCOPE"
        output = "not_a_current_tool_call"
        explanation = (
            "The text asks for legal, proof, novelty, safety, forensic, or "
            "acceptance judgment outside metric-to-claim licensing."
        )
    else:
        backend_decision = "INVALID_ROUTE"
        computed_action = "REJECT"
        output = "bottom_T"
        explanation = f"Unknown route_label: {route}"

    expected = row.get("current_expected_action", "")
    return {
        "claim_id": row.get("claim_id", ""),
        "paper_id": row.get("paper_id", ""),
        "source_family": row.get("source_family", ""),
        "case_role": row.get("case_role", ""),
        "route_label": route,
        "template_id": template_id,
        "gold_action_after_admission": row.get("gold_action_after_admission", ""),
        "current_expected_action": expected,
        "computed_current_action": computed_action,
        "backend_decision": backend_decision,
        "action_match": "PASS" if computed_action == expected else "FAIL",
        "recommended_output": output,
        "explanation": explanation,
        "submitted_claim": row.get("submitted_claim", ""),
    }


def build_by_paper_rows(
    sources: list[dict[str, str]], cases: list[dict[str, str]], decisions: list[dict[str, str]]
) -> list[dict[str, str]]:
    cases_by_paper: dict[str, list[dict[str, str]]] = defaultdict(list)
    decisions_by_paper: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in cases:
        cases_by_paper[row.get("paper_id", "")].append(row)
    for row in decisions:
        decisions_by_paper[row.get("paper_id", "")].append(row)

    rows = []
    for source in sources:
        paper_id = source.get("paper_id", "")
        action_counts = Counter(
            row.get("computed_current_action", "") for row in decisions_by_paper[paper_id]
        )
        gold_counts = Counter(
            row.get("gold_action_after_admission", "") for row in cases_by_paper[paper_id]
        )
        rows.append(
            {
                "paper_id": paper_id,
                "source_role": source.get("source_role", ""),
                "source_family": source.get("source_family", ""),
                "title": source.get("title", ""),
                "claim_rows": str(len(cases_by_paper[paper_id])),
                "current_action_counts": ";".join(
                    f"{key}:{value}" for key, value in sorted(action_counts.items())
                ),
                "gold_after_admission_counts": ";".join(
                    f"{key}:{value}" for key, value in sorted(gold_counts.items())
                ),
            }
        )
    return rows


def ratio(num: int, den: int) -> str:
    if den == 0:
        return "0.000"
    return f"{num / den:.3f}"


def build_markdown(
    summary: dict[str, object],
    checks: list[dict[str, str]],
    decisions: list[dict[str, str]],
    by_paper_rows: list[dict[str, str]],
) -> str:
    lines: list[str] = []
    lines.append("# Paper-Claim Gold Benchmark Report")
    lines.append("")
    lines.append("Status: generated from public-safe paraphrased paper-claim rows.")
    lines.append("")
    lines.append("## Purpose")
    lines.append("")
    lines.append(
        "This benchmark measures the current claim-audit backend on a larger "
        "paper-claim surface: 40 empirical ML or evaluation papers with three "
        "paraphrased claims each, plus eight registered-template controls. It "
        "does not claim autonomous PDF extraction or template discovery."
    )
    lines.append("")
    lines.append("## Reliability Summary")
    lines.append("")
    lines.append("| Item | Value |")
    lines.append("| --- | ---: |")
    for key in [
        "external_papers",
        "external_claim_rows",
        "registered_control_rows",
        "total_claim_rows",
        "current_action_matches",
        "current_action_mismatches",
        "registered_control_consistency_rate",
        "unsupported_template_rate_external_claims",
        "out_of_scope_rate_external_claims",
        "false_accept_rate_non_accept_rows",
        "false_release_rate_unsupported_or_out_of_scope",
        "false_kill_rate_supported_registered_controls",
        "checks_passed",
        "checks_failed",
    ]:
        lines.append(f"| {key} | {summary[key]} |")
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append(
        "A high unsupported-template rate is not a failure here; it is the "
        "measured boundary of the current release. The backend is conservative: "
        "registered controls are decided deterministically, while relevant but "
        "unregistered paper families fail closed into template admission instead "
        "of being silently accepted."
    )
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
    lines.append("## Per-Paper Coverage")
    lines.append("")
    lines.append("| Paper | Role | Family | Claims | Current actions | Post-admission gold |")
    lines.append("| --- | --- | --- | ---: | --- | --- |")
    for row in by_paper_rows:
        lines.append(
            f"| {row['paper_id']} | {row['source_role']} | {row['source_family']} | "
            f"{row['claim_rows']} | {row['current_action_counts'] or 'none'} | "
            f"{row['gold_after_admission_counts'] or 'none'} |"
        )
    lines.append("")
    lines.append("## Decision Rows")
    lines.append("")
    lines.append(
        "| Claim | Route | Template | Gold after admission | Current expected | "
        "Computed current | Match | Explanation |"
    )
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for row in decisions:
        lines.append(
            f"| {row['claim_id']} | {row['route_label']} | {row['template_id'] or 'none'} | "
            f"{row['gold_action_after_admission']} | {row['current_expected_action']} | "
            f"{row['computed_current_action']} | {row['action_match']} | "
            f"{short(row['explanation'], 160)} |"
        )
    lines.append("")
    lines.append("## Boundary")
    lines.append("")
    lines.append(
        "The benchmark supports a careful reliability claim for the deterministic "
        "registered-template backend and the fail-closed routing boundary. It "
        "does not yet support a claim that the system can read arbitrary papers, "
        "extract claims, or invent valid templates without a separate extractor "
        "and adapter-admission benchmark."
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


def build_html(
    summary: dict[str, object],
    checks: list[dict[str, str]],
    decisions: list[dict[str, str]],
    by_paper_rows: list[dict[str, str]],
) -> str:
    metrics = []
    for key in [
        "external_papers",
        "external_claim_rows",
        "registered_control_rows",
        "current_action_mismatches",
        "false_accept_rate_non_accept_rows",
        "unsupported_template_rate_external_claims",
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
    decision_rows = [
        {
            "claim": row["claim_id"],
            "route": row["route_label"],
            "gold": row["gold_action_after_admission"],
            "expected": row["current_expected_action"],
            "computed": row["computed_current_action"],
            "match": row["action_match"],
            "explanation": row["explanation"],
        }
        for row in decisions
    ]
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Paper-Claim Gold Benchmark Report</title>
  <style>
    :root {{
      --ink: #162024;
      --muted: #5d6968;
      --line: #d7dfdc;
      --wash: #f6faf8;
      --green: #145c5a;
      --amber: #a86916;
    }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--ink);
      background: var(--wash);
      line-height: 1.5;
    }}
    main {{
      max-width: 1220px;
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
      max-width: 930px;
      color: var(--muted);
    }}
    .metrics {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
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
      padding: 8px 10px;
      vertical-align: top;
      text-align: left;
      font-size: 13px;
    }}
    th {{
      background: #e8f2ee;
      color: var(--green);
      font-weight: 750;
    }}
    tr:last-child td {{
      border-bottom: 0;
    }}
    .note {{
      border-left: 5px solid var(--amber);
      background: white;
      padding: 14px 18px;
      border-radius: 4px;
    }}
  </style>
</head>
<body>
<main>
  <h1>Paper-Claim Gold Benchmark Report</h1>
  <p>Public-safe paraphrased claims from 40 empirical ML or evaluation papers,
  plus registered-template controls. The benchmark measures backend reliability
  and the explicit unsupported-template boundary.</p>
  <section class="metrics">{''.join(metrics)}</section>
  <h2>Checks</h2>
  {html_table(check_rows, ["check", "status", "evidence"])}
  <h2>Per-Paper Coverage</h2>
  {html_table(by_paper_rows, ["paper_id", "source_role", "source_family", "claim_rows", "current_action_counts", "gold_after_admission_counts"])}
  <h2>Decision Rows</h2>
  {html_table(decision_rows, ["claim", "route", "gold", "expected", "computed", "match", "explanation"])}
  <h2>Boundary</h2>
  <div class="note"><p>This is not an autonomous paper-reading benchmark. It is
  a reliability benchmark for registered-template decisions and fail-closed
  routing before adapter admission.</p></div>
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
        sources, source_header = read_csv(root / FILES["sources"])
    except (OSError, csv.Error) as exc:
        sources, source_header = [], []
        failures.append(f"{FILES['sources']}: could not read sources: {exc}")
    try:
        cases, case_header = read_csv(root / FILES["cases"])
    except (OSError, csv.Error) as exc:
        cases, case_header = [], []
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
    decisions = [
        route_and_decide(row, intake_runner, templates, casebook_by_id, nab_by_id)
        for row in cases
    ]
    by_paper_rows = build_by_paper_rows(sources, cases, decisions)

    source_ids = {row.get("paper_id", "") for row in sources}
    external_sources = [row for row in sources if row.get("source_role", "") == "external_paper"]
    registered_sources = [row for row in sources if row.get("source_role", "") == "registered_control"]
    external_source_ids = {row.get("paper_id", "") for row in external_sources}
    cases_by_paper: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in cases:
        cases_by_paper[row.get("paper_id", "")].append(row)

    route_counts = Counter(row.get("route_label", "") for row in cases)
    gold_counts = Counter(row.get("gold_action_after_admission", "") for row in cases)
    expected_counts = Counter(row.get("current_expected_action", "") for row in cases)
    computed_counts = Counter(row.get("computed_current_action", "") for row in decisions)
    mismatch_rows = [row["claim_id"] for row in decisions if row["action_match"] != "PASS"]
    private_source_rows = [row.get("paper_id", "") for row in sources if contains_private_marker(row)]
    private_case_rows = [row.get("claim_id", "") for row in cases if contains_private_marker(row)]
    invalid_routes = [
        row.get("claim_id", "")
        for row in cases
        if row.get("route_label", "") not in ROUTE_LABELS
    ]
    invalid_gold_actions = [
        row.get("claim_id", "")
        for row in cases
        if row.get("gold_action_after_admission", "") not in GOLD_ACTIONS
    ]
    invalid_current_actions = [
        row.get("claim_id", "")
        for row in cases
        if row.get("current_expected_action", "") not in CURRENT_ACTIONS
    ]
    missing_sources = [
        row.get("claim_id", "")
        for row in cases
        if row.get("paper_id", "") not in source_ids
    ]
    duplicate_claim_ids = [
        claim_id
        for claim_id, count in Counter(row.get("claim_id", "") for row in cases).items()
        if count > 1
    ]
    external_claim_counts = {
        paper_id: len(cases_by_paper[paper_id]) for paper_id in sorted(external_source_ids)
    }
    count_out_of_range = [
        f"{paper_id}:{count}"
        for paper_id, count in external_claim_counts.items()
        if count < 3 or count > 5
    ]
    registered_control_rows = [
        row for row in decisions if row.get("case_role", "") == "registered_control"
    ]
    registered_control_mismatches = [
        row["claim_id"] for row in registered_control_rows if row["action_match"] != "PASS"
    ]
    external_claim_rows = [
        row for row in decisions if row.get("case_role", "") == "external_claim"
    ]
    unsupported_external = [
        row for row in external_claim_rows if row.get("computed_current_action", "") == "UNSUPPORTED_TEMPLATE"
    ]
    out_of_scope_external = [
        row for row in external_claim_rows if row.get("computed_current_action", "") == "OUT_OF_SCOPE"
    ]
    non_accept_rows = [
        row for row in decisions if row.get("current_expected_action", "") != "ACCEPT"
    ]
    false_accepts = [
        row for row in non_accept_rows if row.get("computed_current_action", "") == "ACCEPT"
    ]
    protected_rows = [
        row
        for row in decisions
        if row.get("current_expected_action", "") in {"UNSUPPORTED_TEMPLATE", "OUT_OF_SCOPE"}
    ]
    false_release_rows = [
        row
        for row in protected_rows
        if row.get("computed_current_action", "")
        in {"ACCEPT", "REWRITE", "WEAKEN", "SUPPORT_ONLY"}
    ]
    supported_registered_controls = [
        row
        for row in registered_control_rows
        if row.get("current_expected_action", "") in {"ACCEPT", "REWRITE", "WEAKEN", "SUPPORT_ONLY"}
    ]
    false_kill_rows = [
        row
        for row in supported_registered_controls
        if row.get("computed_current_action", "")
        in {"SUPPRESS", "REJECT", "UNSUPPORTED_TEMPLATE", "OUT_OF_SCOPE"}
    ]

    checks: list[dict[str, str]] = []
    add_check(
        checks,
        "PB-01",
        "inputs present",
        not failures and bool(sources) and bool(cases),
        "schema, source manifest, cases, and supporting release inputs loaded",
        "; ".join(failures) if failures else "sources or cases are empty",
    )
    add_check(
        checks,
        "PB-02",
        "source header alignment",
        source_header == EXPECTED_SOURCE_COLUMNS,
        f"source header has {len(source_header)} expected columns",
        f"source header={source_header}; expected={EXPECTED_SOURCE_COLUMNS}",
    )
    add_check(
        checks,
        "PB-03",
        "case header alignment",
        case_header == EXPECTED_CASE_COLUMNS,
        f"case header has {len(case_header)} expected columns",
        f"case header={case_header}; expected={EXPECTED_CASE_COLUMNS}",
    )
    add_check(
        checks,
        "PB-04",
        "external paper count",
        30 <= len(external_sources) <= 50,
        f"{len(external_sources)} external papers in benchmark range [30, 50]",
        f"external paper count {len(external_sources)} outside [30, 50]",
    )
    add_check(
        checks,
        "PB-05",
        "claims per external paper",
        not count_out_of_range,
        "each external paper has 3-5 claim rows",
        f"out-of-range external counts: {count_out_of_range}",
    )
    add_check(
        checks,
        "PB-06",
        "source joins",
        not missing_sources,
        "every case row joins to a source row",
        f"case rows with missing source: {missing_sources}",
    )
    add_check(
        checks,
        "PB-07",
        "unique claim ids",
        not duplicate_claim_ids,
        "all claim ids are unique",
        f"duplicate claim ids: {duplicate_claim_ids}",
    )
    add_check(
        checks,
        "PB-08",
        "enum validity",
        not invalid_routes and not invalid_gold_actions and not invalid_current_actions,
        "route, gold-action, and current-action enums are valid",
        (
            f"invalid routes={invalid_routes}; invalid gold={invalid_gold_actions}; "
            f"invalid current={invalid_current_actions}"
        ),
    )
    add_check(
        checks,
        "PB-09",
        "registered control source exists",
        len(registered_sources) == 1 and len(registered_control_rows) == 8,
        "one registered-control source with eight control rows",
        (
            f"registered_sources={len(registered_sources)}; "
            f"registered_control_rows={len(registered_control_rows)}"
        ),
    )
    add_check(
        checks,
        "PB-10",
        "current action consistency",
        not mismatch_rows,
        f"{len(decisions)} / {len(decisions)} rows match current expected actions",
        f"current-action mismatches: {mismatch_rows}",
    )
    add_check(
        checks,
        "PB-11",
        "registered backend consistency",
        not registered_control_mismatches,
        "registered-template controls all match expected backend actions",
        f"registered-control mismatches: {registered_control_mismatches}",
    )
    add_check(
        checks,
        "PB-12",
        "no unsafe false accepts",
        not false_accepts,
        "no non-accept row is computed as ACCEPT",
        f"false accept rows: {[row['claim_id'] for row in false_accepts]}",
    )
    add_check(
        checks,
        "PB-13",
        "fail-closed unsupported boundary",
        not false_release_rows,
        "unsupported-template and out-of-scope rows are not released as licensed claims",
        f"false release rows: {[row['claim_id'] for row in false_release_rows]}",
    )
    add_check(
        checks,
        "PB-14",
        "no false kill on supported controls",
        not false_kill_rows,
        "supported registered controls are not suppressed, rejected, or marked unsupported",
        f"false kill rows: {[row['claim_id'] for row in false_kill_rows]}",
    )
    add_check(
        checks,
        "PB-15",
        "private marker scan",
        not private_source_rows and not private_case_rows,
        "no private coordination paths, local paths, or credential-like patterns in benchmark inputs",
        (
            f"private source rows={private_source_rows}; "
            f"private case rows={private_case_rows}"
        ),
    )

    checks_failed = sum(1 for row in checks if row["status"] == "FAIL")
    summary = {
        "external_papers": len(external_sources),
        "external_claim_rows": len(external_claim_rows),
        "registered_control_rows": len(registered_control_rows),
        "total_claim_rows": len(cases),
        "average_claims_per_external_paper": ratio(len(external_claim_rows), len(external_sources)),
        "current_action_matches": sum(1 for row in decisions if row["action_match"] == "PASS"),
        "current_action_mismatches": len(mismatch_rows),
        "registered_control_consistency_rate": ratio(
            len(registered_control_rows) - len(registered_control_mismatches),
            len(registered_control_rows),
        ),
        "unsupported_template_rows": len(unsupported_external),
        "out_of_scope_rows": len(out_of_scope_external),
        "unsupported_template_rate_external_claims": ratio(
            len(unsupported_external), len(external_claim_rows)
        ),
        "out_of_scope_rate_external_claims": ratio(
            len(out_of_scope_external), len(external_claim_rows)
        ),
        "false_accepts": len(false_accepts),
        "false_accept_rate_non_accept_rows": ratio(len(false_accepts), len(non_accept_rows)),
        "false_release_rows": len(false_release_rows),
        "false_release_rate_unsupported_or_out_of_scope": ratio(
            len(false_release_rows), len(protected_rows)
        ),
        "false_kill_rows": len(false_kill_rows),
        "false_kill_rate_supported_registered_controls": ratio(
            len(false_kill_rows), len(supported_registered_controls)
        ),
        "route_counts": dict(sorted(route_counts.items())),
        "gold_action_after_admission_counts": dict(sorted(gold_counts.items())),
        "current_expected_action_counts": dict(sorted(expected_counts.items())),
        "computed_current_action_counts": dict(sorted(computed_counts.items())),
        "autonomous_full_paper_routing_supported": "no",
        "checks_passed": len(checks) - checks_failed,
        "checks_failed": checks_failed,
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(
        output_dir / "paper_claim_gold_benchmark_decisions.csv",
        decisions,
        [
            "claim_id",
            "paper_id",
            "source_family",
            "case_role",
            "route_label",
            "template_id",
            "gold_action_after_admission",
            "current_expected_action",
            "computed_current_action",
            "backend_decision",
            "action_match",
            "recommended_output",
            "explanation",
            "submitted_claim",
        ],
    )
    write_csv(
        output_dir / "paper_claim_gold_benchmark_checks.csv",
        checks,
        ["check_id", "label", "status", "evidence"],
    )
    write_csv(
        output_dir / "paper_claim_gold_benchmark_by_paper.csv",
        by_paper_rows,
        [
            "paper_id",
            "source_role",
            "source_family",
            "title",
            "claim_rows",
            "current_action_counts",
            "gold_after_admission_counts",
        ],
    )
    write_json(output_dir / "paper_claim_gold_benchmark_summary.json", summary)
    (output_dir / "paper_claim_gold_benchmark_report.md").write_text(
        build_markdown(summary, checks, decisions, by_paper_rows), encoding="utf-8"
    )
    (output_dir / "paper_claim_gold_benchmark_report.html").write_text(
        build_html(summary, checks, decisions, by_paper_rows), encoding="utf-8"
    )

    if checks_failed:
        print("FAIL paper claim gold benchmark")
        print(f"checks_failed: {checks_failed}")
        return 1
    print("PASS paper claim gold benchmark")
    print(f"external_papers: {summary['external_papers']}")
    print(f"external_claim_rows: {summary['external_claim_rows']}")
    print(f"registered_control_rows: {summary['registered_control_rows']}")
    print(f"total_claim_rows: {summary['total_claim_rows']}")
    print(f"current_action_mismatches: {summary['current_action_mismatches']}")
    print(
        "unsupported_template_rate_external_claims: "
        f"{summary['unsupported_template_rate_external_claims']}"
    )
    print(
        "false_release_rate_unsupported_or_out_of_scope: "
        f"{summary['false_release_rate_unsupported_or_out_of_scope']}"
    )
    print("autonomous_full_paper_routing_supported: no")
    print("outputs:")
    for name in [
        "paper_claim_gold_benchmark_report.md",
        "paper_claim_gold_benchmark_report.html",
        "paper_claim_gold_benchmark_summary.json",
        "paper_claim_gold_benchmark_checks.csv",
        "paper_claim_gold_benchmark_decisions.csv",
        "paper_claim_gold_benchmark_by_paper.csv",
    ]:
        rel = output_dir.relative_to(root) / name if output_dir.is_relative_to(root) else output_dir / name
        print(f"- {rel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
