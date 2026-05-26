#!/usr/bin/env python3
"""Turn an LLM-produced claim-routing CSV into a fail-closed review report.

The LLM is treated as a front end only. It may find candidate claims and route
them, but registered template decisions still come from the deterministic
ClaimContractBench assets.
"""

from __future__ import annotations

import argparse
from collections import Counter
import csv
import html
import json
from pathlib import Path
import re
import sys

from run_reviewer_claim_intake import (
    build_template_rows,
    decide_intake,
    read_csv,
    short,
    write_csv,
    write_json,
)


FILES = {
    "template_schema": "artifact/claim_template_admission_schema_20260521.json",
    "template_cases": "artifact/claim_template_admission_cases_20260521.csv",
    "casebook": "data/claim_passport_casebook_20260519.csv",
    "nab_visual": "data/nab_adapter_visual_passport_rows_20260519.csv",
}

REQUIRED_COLUMNS = [
    "packet_id",
    "source_title",
    "source_section",
    "submitted_claim",
    "intended_use",
    "route_label",
    "template_id",
    "evidence_pointer",
    "llm_reason",
    "human_check_required",
]

ROUTE_LABELS = {
    "CALL_REGISTERED_TEMPLATE",
    "NEEDS_TEMPLATE_ADMISSION",
    "OUT_OF_SCOPE_DO_NOT_CALL",
}

PRIVATE_DIR_MARKERS = (
    "CODEX" + "_ONLY/",
    "CLAUDE" + "_ONLY/",
    "EX" + "CHANGE/",
)

PRIVATE_PATTERNS = (
    re.compile(r"/Users/[A-Za-z0-9._-]+"),
    re.compile(r"\bconnect\.[A-Za-z0-9.-]+\b"),
    re.compile("(?:" + "|".join(re.escape(marker) for marker in PRIVATE_DIR_MARKERS) + ")"),
    re.compile(
        r"\b(?:password|passwd|token|secret|credential)\b\s*[:=]\s*"
        r"['\"]?[A-Za-z0-9_./+=-]{8,}",
        re.IGNORECASE,
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Review an LLM-produced claim-routing packet fail-closed."
    )
    parser.add_argument("--root", default=".", help="Release root. Default: current directory.")
    parser.add_argument(
        "--input",
        default="artifact/llm_claim_review_packet_template_20260527.csv",
        help="LLM-produced claim packet CSV.",
    )
    parser.add_argument(
        "--output",
        default="reports/llm_claim_review_packet_20260527",
        help="Report output directory. Relative paths are resolved under root.",
    )
    return parser.parse_args()


def resolve(root: Path, value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = root / path
    return path.resolve()


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


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


def load_templates(
    root: Path,
) -> tuple[dict[str, dict[str, str]], dict[str, dict[str, str]], dict[str, dict[str, str]]]:
    template_schema = load_json(root / FILES["template_schema"])
    template_cases, _ = read_csv(root / FILES["template_cases"])
    casebook, _ = read_csv(root / FILES["casebook"])
    nab_visual, _ = read_csv(root / FILES["nab_visual"])
    critical_fields = list(template_schema.get("critical_fields_for_admission", []))
    templates = build_template_rows(template_cases, critical_fields)
    return (
        templates,
        {row.get("event_id", ""): row for row in casebook},
        {row.get("display_id", ""): row for row in nab_visual},
    )


def review_row(
    row: dict[str, str],
    templates: dict[str, dict[str, str]],
    casebook_by_id: dict[str, dict[str, str]],
    nab_by_id: dict[str, dict[str, str]],
) -> dict[str, str]:
    route = row.get("route_label", "").strip()
    template_id = row.get("template_id", "").strip()
    base = {
        "packet_id": row.get("packet_id", ""),
        "source_title": row.get("source_title", ""),
        "source_section": row.get("source_section", ""),
        "submitted_claim": row.get("submitted_claim", ""),
        "intended_use": row.get("intended_use", ""),
        "route_label": route,
        "template_id": template_id,
        "evidence_pointer": row.get("evidence_pointer", ""),
        "llm_reason": row.get("llm_reason", ""),
        "human_check_required": row.get("human_check_required", ""),
    }

    if route not in ROUTE_LABELS:
        return {
            **base,
            "tool_decision": "INVALID_ROUTE_LABEL",
            "recommended_output": "bottom_T",
            "explanation": "Route label is not one of the three supported LLM handoff lanes.",
            "source_anchor": "",
            "unsafe_release": "yes",
        }

    if route == "NEEDS_TEMPLATE_ADMISSION":
        return {
            **base,
            "tool_decision": "NEEDS_TEMPLATE_ADMISSION",
            "recommended_output": "Open a template-admission ticket before licensing this claim.",
            "explanation": "The LLM marked the row as relevant but unsupported by registered templates.",
            "source_anchor": "",
            "unsafe_release": "no",
        }

    if route == "OUT_OF_SCOPE_DO_NOT_CALL":
        return {
            **base,
            "tool_decision": "OUT_OF_SCOPE_DO_NOT_CALL",
            "recommended_output": "Do not call the metric-to-claim runner for this row.",
            "explanation": "The row is outside the current empirical metric-to-claim scope.",
            "source_anchor": "",
            "unsafe_release": "no",
        }

    intake = {
        "intake_id": row.get("packet_id", ""),
        "actor": "tool_demo",
        "template_id": template_id,
        "submitted_claim": row.get("submitted_claim", ""),
        "intended_use": row.get("intended_use", ""),
        "expected_decision": "",
        "expected_output_hint": "",
    }
    decision = decide_intake(intake, templates, casebook_by_id, nab_by_id)
    unsafe = "yes" if decision["decision"] in {"ACCEPT_LICENSED", "REWRITE_TO_LICENSED"} and not template_id else "no"
    return {
        **base,
        "tool_decision": decision["decision"],
        "recommended_output": decision["recommended_output"],
        "explanation": decision["explanation"],
        "source_anchor": decision["source_anchor"],
        "unsafe_release": unsafe if decision["decision"] == "REJECT_UNKNOWN_TEMPLATE" else "no",
    }


def build_markdown(
    input_path: Path,
    summary: dict[str, object],
    checks: list[dict[str, str]],
    decisions: list[dict[str, str]],
) -> str:
    lines: list[str] = []
    lines.append("# LLM Claim Review Packet Report")
    lines.append("")
    lines.append(f"Input: `{input_path}`")
    lines.append("")
    lines.append("## Role Split")
    lines.append("")
    lines.append(
        "The LLM is only a claim-extraction and routing front end. "
        "ClaimContractBench applies registered templates, rejects unknown or "
        "mismatched handoffs, and marks unsupported rows as admission tickets "
        "or out-of-scope rows."
    )
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Item | Value |")
    lines.append("| --- | ---: |")
    for key in [
        "packet_rows",
        "call_registered_template",
        "needs_template_admission",
        "out_of_scope",
        "registered_decision_rows",
        "accepted_or_rewritten",
        "suppressed_or_rejected",
        "unsafe_release_rate",
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
    lines.append("## Decisions")
    lines.append("")
    lines.append("| Packet | Route | Template | Tool Decision | Recommended Output |")
    lines.append("| --- | --- | --- | --- | --- |")
    for row in decisions:
        lines.append(
            f"| {row['packet_id']} | {row['route_label']} | {row['template_id']} | "
            f"{row['tool_decision']} | {short(row['recommended_output'], 220)} |"
        )
    lines.append("")
    lines.append("## Boundary")
    lines.append("")
    lines.append(
        "This report does not prove that the LLM extracted every relevant claim. "
        "It audits the packet that was supplied. For confidential review, use "
        "manual packets or an approved private LLM."
    )
    lines.append("")
    return "\n".join(lines)


def html_table(rows: list[dict[str, str]], columns: list[str]) -> str:
    header = "".join(f"<th>{html.escape(column)}</th>" for column in columns)
    body = []
    for row in rows:
        cells = "".join(
            f"<td>{html.escape(short(str(row.get(column, '')), 240))}</td>"
            for column in columns
        )
        body.append(f"<tr>{cells}</tr>")
    return f"<table><thead><tr>{header}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def build_html(summary: dict[str, object], checks: list[dict[str, str]], decisions: list[dict[str, str]]) -> str:
    metric_keys = [
        "packet_rows",
        "call_registered_template",
        "needs_template_admission",
        "out_of_scope",
        "unsafe_release_rate",
        "checks_failed",
    ]
    metrics = "".join(
        f"<div class='metric'><span>{html.escape(key)}</span><strong>{html.escape(str(summary[key]))}</strong></div>"
        for key in metric_keys
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
<title>LLM Claim Review Packet</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 32px; color: #172033; }}
.metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin: 20px 0; }}
.metric {{ border: 1px solid #d8dee9; padding: 14px; border-radius: 6px; background: #f8fafc; }}
.metric span {{ display: block; color: #5b6472; font-size: 13px; }}
.metric strong {{ display: block; font-size: 24px; margin-top: 6px; }}
table {{ border-collapse: collapse; width: 100%; margin: 16px 0 28px; }}
th, td {{ border: 1px solid #d8dee9; padding: 8px 10px; vertical-align: top; font-size: 13px; }}
th {{ background: #edf2f7; text-align: left; }}
</style>
</head>
<body>
<h1>LLM Claim Review Packet</h1>
<p>The LLM routes claims; ClaimContractBench applies registered templates and fails closed.</p>
<div class="metrics">{metrics}</div>
<h2>Checks</h2>
{html_table(check_rows, ["check", "status", "evidence"])}
<h2>Decisions</h2>
{html_table(decisions, ["packet_id", "route_label", "template_id", "tool_decision", "recommended_output", "explanation"])}
</body>
</html>
"""


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    input_path = resolve(root, args.input)
    output_dir = resolve(root, args.output)
    rows, columns = read_csv(input_path)
    templates, casebook_by_id, nab_by_id = load_templates(root)

    checks: list[dict[str, str]] = []
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in columns]
    add_check(
        checks,
        "LCP-01",
        "required columns",
        not missing_columns,
        "all required columns present",
        f"missing columns: {missing_columns}",
    )
    add_check(
        checks,
        "LCP-02",
        "packet is non-empty",
        bool(rows),
        f"{len(rows)} rows",
        "packet has no rows",
    )
    route_bad = [row.get("packet_id", "") for row in rows if row.get("route_label", "") not in ROUTE_LABELS]
    add_check(
        checks,
        "LCP-03",
        "route labels are valid",
        not route_bad,
        "all route labels use the three supported lanes",
        f"invalid route labels in: {route_bad}",
    )
    private_bad = [row.get("packet_id", "") for row in rows if contains_private_marker(row)]
    add_check(
        checks,
        "LCP-04",
        "no private markers in packet",
        not private_bad,
        "no private path or credential-like marker found",
        f"private markers in: {private_bad}",
    )
    missing_template = [
        row.get("packet_id", "")
        for row in rows
        if row.get("route_label", "") == "CALL_REGISTERED_TEMPLATE"
        and not row.get("template_id", "").strip()
    ]
    add_check(
        checks,
        "LCP-05",
        "registered calls name a template",
        not missing_template,
        "all CALL_REGISTERED_TEMPLATE rows include template_id",
        f"missing template_id in: {missing_template}",
    )
    blank_claims = [row.get("packet_id", "") for row in rows if not row.get("submitted_claim", "").strip()]
    add_check(
        checks,
        "LCP-06",
        "claims are non-empty",
        not blank_claims,
        "all submitted_claim fields are non-empty",
        f"blank claims in: {blank_claims}",
    )

    decisions = [review_row(row, templates, casebook_by_id, nab_by_id) for row in rows]
    counts = Counter(row["route_label"] for row in decisions)
    decision_counts = Counter(row["tool_decision"] for row in decisions)
    unsafe_rows = [row for row in decisions if row["unsafe_release"] == "yes"]
    unsafe_rate = len(unsafe_rows) / len(decisions) if decisions else 0.0
    add_check(
        checks,
        "LCP-07",
        "unsafe release rate is zero",
        unsafe_rate == 0.0,
        "unsafe_release_rate=0.000",
        f"unsafe rows: {[row['packet_id'] for row in unsafe_rows]}",
    )

    checks_passed = sum(1 for row in checks if row["status"] == "PASS")
    checks_failed = len(checks) - checks_passed
    summary: dict[str, object] = {
        "input": str(input_path),
        "packet_rows": len(rows),
        "call_registered_template": counts["CALL_REGISTERED_TEMPLATE"],
        "needs_template_admission": counts["NEEDS_TEMPLATE_ADMISSION"],
        "out_of_scope": counts["OUT_OF_SCOPE_DO_NOT_CALL"],
        "registered_decision_rows": counts["CALL_REGISTERED_TEMPLATE"],
        "accepted_or_rewritten": decision_counts["ACCEPT_LICENSED"] + decision_counts["REWRITE_TO_LICENSED"],
        "suppressed_or_rejected": decision_counts["SUPPRESS_BOTTOM"]
        + decision_counts["REJECT_PATCHWORK"]
        + decision_counts["REJECT_UNKNOWN_TEMPLATE"],
        "unsafe_release_rate": f"{unsafe_rate:.3f}",
        "checks_passed": checks_passed,
        "checks_failed": checks_failed,
        "decision_counts": dict(sorted(decision_counts.items())),
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(
        output_dir / "llm_claim_review_packet_decisions.csv",
        decisions,
        [
            "packet_id",
            "source_title",
            "source_section",
            "submitted_claim",
            "intended_use",
            "route_label",
            "template_id",
            "tool_decision",
            "recommended_output",
            "explanation",
            "source_anchor",
            "evidence_pointer",
            "llm_reason",
            "human_check_required",
            "unsafe_release",
        ],
    )
    write_csv(output_dir / "llm_claim_review_packet_checks.csv", checks, ["check_id", "label", "status", "evidence"])
    write_json(output_dir / "llm_claim_review_packet_summary.json", summary)
    (output_dir / "llm_claim_review_packet_report.md").write_text(
        build_markdown(input_path, summary, checks, decisions), encoding="utf-8"
    )
    (output_dir / "llm_claim_review_packet_report.html").write_text(
        build_html(summary, checks, decisions), encoding="utf-8"
    )

    print("PASS LLM claim review packet" if checks_failed == 0 else "FAIL LLM claim review packet")
    print(f"packet_rows: {summary['packet_rows']}")
    print(f"call_registered_template: {summary['call_registered_template']}")
    print(f"needs_template_admission: {summary['needs_template_admission']}")
    print(f"out_of_scope: {summary['out_of_scope']}")
    print(f"unsafe_release_rate: {summary['unsafe_release_rate']}")
    print(f"checks_passed: {checks_passed}")
    print(f"checks_failed: {checks_failed}")
    print("outputs:")
    for name in [
        "llm_claim_review_packet_report.md",
        "llm_claim_review_packet_report.html",
        "llm_claim_review_packet_summary.json",
        "llm_claim_review_packet_checks.csv",
        "llm_claim_review_packet_decisions.csv",
    ]:
        print(f"- {output_dir / name}")
    return 0 if checks_failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
