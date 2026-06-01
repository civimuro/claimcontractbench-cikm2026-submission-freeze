#!/usr/bin/env python3
"""Regression checks for the reviewer-facing audit demo.

The demo is a useful application artifact only if later edits preserve its
core promises: registered templates resolve deterministically, unsupported
templates fail into admission tickets, out-of-scope text is stopped, and the
known selected-packet residual remains visible instead of being hidden.
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter
import json
from pathlib import Path
import re


EXPECTED_SUMMARY = {
    "audit_cards": 72,
    "registered_template_cards": 8,
    "admission_ticket_cards": 43,
    "out_of_scope_cards": 21,
    "joint_validation_pass": 71,
    "joint_validation_fail": 1,
    "selected_route_accuracy": "0.972",
    "selected_joint_accuracy": "0.972",
    "holdout_route_accuracy": "1.000",
    "holdout_joint_accuracy": "1.000",
}

EXPECTED_ROUTES = {
    "CALL_REGISTERED_TEMPLATE": 8,
    "NEEDS_TEMPLATE_ADMISSION": 43,
    "OUT_OF_SCOPE_DO_NOT_CALL": 21,
}

EXPECTED_DECISIONS = {
    "ACCEPT_LICENSED": 1,
    "DO_NOT_CALL_CLAIM_RUNNER": 21,
    "OPEN_ADMISSION_TICKET": 43,
    "REJECT_PATCHWORK": 1,
    "REJECT_UNKNOWN_TEMPLATE": 1,
    "REWRITE_TO_LICENSED": 3,
    "SUPPORT_ONLY_REWRITE": 1,
    "SUPPRESS_BOTTOM": 1,
}

EXPECTED_REGISTERED_CALLS = {
    "selected-NSR-027": ("CTA-CORE-01", "ACCEPT_LICENSED"),
    "selected-NSR-028": ("CTA-CORE-02", "REWRITE_TO_LICENSED"),
    "selected-NSR-029": ("CTA-CORE-03", "REWRITE_TO_LICENSED"),
    "selected-NSR-030": ("CTA-CORE-04", "REWRITE_TO_LICENSED"),
    "selected-NSR-031": ("CTA-CORE-05", "SUPPRESS_BOTTOM"),
    "selected-NSR-032": ("CTA-NAB-01", "SUPPORT_ONLY_REWRITE"),
    "selected-NSR-033": ("CTA-AI4I-01", "REJECT_PATCHWORK"),
    "selected-NSR-034": ("CTA-UNKNOWN-01", "REJECT_UNKNOWN_TEMPLATE"),
}

EXPECTED_RESIDUALS = ["selected-NSR-025"]

PRIVATE_DIR_MARKERS = (
    "CODEX" + "_ONLY/",
    "CLAUDE" + "_ONLY/",
    "EX" + "CHANGE/",
)

PRIVATE_PATTERNS = (
    ("absolute local user path", re.compile(r"/Users/[A-Za-z0-9._-]+")),
    ("remote connector host", re.compile(r"\bconnect\.[A-Za-z0-9.-]+\b")),
    (
        "private coordination prefix",
        re.compile("(?:" + "|".join(re.escape(marker) for marker in PRIVATE_DIR_MARKERS) + ")"),
    ),
    (
        "inline credential assignment",
        re.compile(
            r"\b(?:password|passwd|token|secret|credential)\b\s*[:=]\s*"
            r"['\"]?[A-Za-z0-9_./+=-]{8,}",
            re.IGNORECASE,
        ),
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run regression checks for reviewer-facing audit demo outputs."
    )
    parser.add_argument("--root", default=".", help="Workspace root. Default: current directory.")
    parser.add_argument(
        "--demo-dir",
        default="reports/reviewer_facing_audit_demo_20260521",
        help="Reviewer audit demo output directory.",
    )
    parser.add_argument(
        "--output",
        default="reports/reviewer_facing_audit_demo_regression_20260521",
        help="Regression report output directory.",
    )
    return parser.parse_args()


def resolve(root: Path, value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = root / path
    return path.resolve()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


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


def private_hits(texts: dict[str, str]) -> list[str]:
    hits = []
    for name, text in texts.items():
        for label, pattern in PRIVATE_PATTERNS:
            if pattern.search(text):
                hits.append(f"{name}: {label}")
    return hits


def load_required_files(demo_dir: Path) -> tuple[dict[str, object], list[dict[str, str]], list[dict[str, str]], str, str]:
    summary = json.loads((demo_dir / "reviewer_audit_demo_summary.json").read_text(encoding="utf-8"))
    cards = read_csv(demo_dir / "reviewer_audit_cards.csv")
    checks = read_csv(demo_dir / "reviewer_audit_demo_checks.csv")
    html = (demo_dir / "reviewer_audit_demo_report.html").read_text(encoding="utf-8")
    markdown = (demo_dir / "reviewer_audit_demo_report.md").read_text(encoding="utf-8")
    return summary, cards, checks, html, markdown


def exact_dict(value: object) -> dict[str, int]:
    if not isinstance(value, dict):
        return {}
    return {str(key): int(count) for key, count in value.items()}


def build_report(summary: dict[str, object], checks: list[dict[str, str]]) -> str:
    lines = [
        "# Reviewer Audit Demo Regression",
        "",
        "Status: regression checks for the reviewer-facing audit demo outputs.",
        "",
        "## Summary",
        "",
        f"- status: `{summary['status']}`",
        f"- checks passed: {summary['checks_passed']}",
        f"- checks failed: {summary['checks_failed']}",
        f"- demo cards checked: {summary['audit_cards_checked']}",
        "",
        "## Checks",
        "",
        "| Check | Status | Evidence |",
        "| --- | --- | --- |",
    ]
    for row in checks:
        evidence = str(row["evidence"]).replace("|", "/")
        lines.append(f"| {row['check_id']} {row['label']} | {row['status']} | {evidence} |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "A passing result means the demo still behaves as a bounded reviewer aid: "
            "registered calls are deterministic, unsupported templates become "
            "admission work, out-of-scope text is not run through the claim "
            "contract, and the known selected-packet residual remains visible.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    demo_dir = resolve(root, args.demo_dir)
    output_dir = resolve(root, args.output)

    required = [
        demo_dir / "reviewer_audit_demo_summary.json",
        demo_dir / "reviewer_audit_cards.csv",
        demo_dir / "reviewer_audit_demo_checks.csv",
        demo_dir / "reviewer_audit_demo_report.html",
        demo_dir / "reviewer_audit_demo_report.md",
    ]
    checks: list[dict[str, str]] = []
    missing = [str(path) for path in required if not path.is_file()]
    add_check(
        checks,
        "RDR-01",
        "required demo outputs exist",
        not missing,
        "all reviewer audit demo outputs are present",
        f"missing required outputs: {missing}",
    )
    if missing:
        summary = {
            "status": "FAIL",
            "checks_passed": 0,
            "checks_failed": len(checks),
            "audit_cards_checked": 0,
        }
        output_dir.mkdir(parents=True, exist_ok=True)
        write_csv(output_dir / "reviewer_audit_demo_regression_checks.csv", checks, ["check_id", "label", "status", "evidence"])
        (output_dir / "reviewer_audit_demo_regression_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
        (output_dir / "reviewer_audit_demo_regression_report.md").write_text(
            build_report(summary, checks), encoding="utf-8"
        )
        print("FAIL reviewer audit demo regression")
        print("reason: missing required reviewer audit demo outputs")
        print(f"demo_dir: {demo_dir}")
        print("Run the demo first, or pass --demo-dir to the directory you already generated:")
        print("python3 src/run_reviewer_audit_demo.py --output <demo-dir>")
        print("python3 src/run_reviewer_audit_demo_regression.py --demo-dir <demo-dir> --output <regression-output-dir>")
        print("missing:")
        for path in missing:
            print(f"- {path}")
        print("diagnostic outputs:")
        print(f"- {output_dir / 'reviewer_audit_demo_regression_report.md'}")
        print(f"- {output_dir / 'reviewer_audit_demo_regression_summary.json'}")
        print(f"- {output_dir / 'reviewer_audit_demo_regression_checks.csv'}")
        return 1

    demo_summary, cards, demo_checks, html, markdown = load_required_files(demo_dir)
    card_by_id = {row["audit_id"]: row for row in cards}
    route_counts = Counter(row["route_label"] for row in cards)
    decision_counts = Counter(row["tool_decision"] for row in cards)
    source_counts = Counter(row["source_packet"] for row in cards)

    mismatched_summary = {
        key: (demo_summary.get(key), expected)
        for key, expected in EXPECTED_SUMMARY.items()
        if demo_summary.get(key) != expected
    }
    add_check(
        checks,
        "RDR-02",
        "summary counts remain locked",
        not mismatched_summary,
        "summary matches the locked 72-card selected-plus-holdout demo profile",
        f"summary mismatches: {mismatched_summary}",
    )

    add_check(
        checks,
        "RDR-03",
        "route and decision mix remain locked",
        dict(route_counts) == EXPECTED_ROUTES and dict(decision_counts) == EXPECTED_DECISIONS,
        f"routes={dict(route_counts)}; decisions={dict(decision_counts)}",
        f"routes={dict(route_counts)} expected={EXPECTED_ROUTES}; decisions={dict(decision_counts)} expected={EXPECTED_DECISIONS}",
    )

    duplicate_ids = sorted([audit_id for audit_id, count in Counter(row["audit_id"] for row in cards).items() if count > 1])
    add_check(
        checks,
        "RDR-04",
        "card identity and source partition",
        len(cards) == 72 and not duplicate_ids and dict(source_counts) == {"selected": 36, "holdout": 36},
        "72 unique cards, split evenly across selected and holdout packets",
        f"cards={len(cards)} duplicates={duplicate_ids} source_counts={dict(source_counts)}",
    )

    registered_errors = []
    for audit_id, (template_id, decision) in EXPECTED_REGISTERED_CALLS.items():
        row = card_by_id.get(audit_id)
        if not row:
            registered_errors.append(f"{audit_id}: missing")
            continue
        if row["template_id"] != template_id or row["tool_decision"] != decision:
            registered_errors.append(
                f"{audit_id}: got ({row['template_id']}, {row['tool_decision']}), expected ({template_id}, {decision})"
            )
        if not row.get("recommended_output", "").strip():
            registered_errors.append(f"{audit_id}: blank recommended output")
    add_check(
        checks,
        "RDR-05",
        "registered template controls resolve deterministically",
        not registered_errors,
        "all eight registered template controls preserve their locked template id and action",
        "; ".join(registered_errors),
    )

    fail_closed_errors = []
    for row in cards:
        if row["route_label"] == "NEEDS_TEMPLATE_ADMISSION":
            if row["tool_decision"] != "OPEN_ADMISSION_TICKET" or row["recommended_output"] != "unsupported_template":
                fail_closed_errors.append(row["audit_id"])
        if row["route_label"] == "OUT_OF_SCOPE_DO_NOT_CALL":
            if row["tool_decision"] != "DO_NOT_CALL_CLAIM_RUNNER" or row["recommended_output"] != "bottom_T":
                fail_closed_errors.append(row["audit_id"])
    add_check(
        checks,
        "RDR-06",
        "unsupported and out-of-scope rows fail closed",
        not fail_closed_errors,
        "adapter-needed rows open tickets and out-of-scope rows stop at bottom_T",
        f"non-fail-closed rows: {fail_closed_errors}",
    )

    residuals = sorted(row["audit_id"] for row in cards if row["joint_match"] == "FAIL")
    add_check(
        checks,
        "RDR-07",
        "known residual remains visible",
        residuals == EXPECTED_RESIDUALS,
        "the selected cognitive/construct-validity residual is still visible",
        f"residuals={residuals}; expected={EXPECTED_RESIDUALS}",
    )

    html_ok = (
        html.count("data-card data-route=") == 72
        and "routeFilter" in html
        and "decisionFilter" in html
        and "countline" in html
        and "selected-NSR-025" in html
    )
    add_check(
        checks,
        "RDR-08",
        "HTML report renders complete filterable card surface",
        html_ok,
        "HTML contains all 72 card articles, filters, count line, and residual marker",
        "HTML card/filter/residual surface is incomplete",
    )

    failed_demo_checks = [row["check_id"] for row in demo_checks if row.get("status") != "PASS"]
    add_check(
        checks,
        "RDR-09",
        "upstream demo checks pass",
        not failed_demo_checks,
        "all upstream reviewer audit demo checks are PASS",
        f"failed upstream demo checks: {failed_demo_checks}",
    )

    public_texts = {
        "cards": " ".join(" ".join(row.values()) for row in cards),
        "html": html,
        "markdown": markdown,
    }
    hits = private_hits(public_texts)
    add_check(
        checks,
        "RDR-10",
        "public-safe report text",
        not hits,
        "cards and reports contain no local path, connector host, or credential assignment markers",
        f"private/sensitive markers: {hits}",
    )

    protocol_path = root / "paper" / "REVIEWER_AUDIT_DEMO_USE_PROTOCOL_20260521.md"
    protocol_text = protocol_path.read_text(encoding="utf-8") if protocol_path.is_file() else ""
    protocol_needles = [
        "Human role",
        "LLM role",
        "Deterministic tool role",
        "It is not a paper-acceptance engine",
        "It is not a full-paper parser",
        "fails closed",
    ]
    missing_needles = [needle for needle in protocol_needles if needle not in protocol_text]
    add_check(
        checks,
        "RDR-11",
        "use protocol is explicit",
        protocol_path.is_file() and not missing_needles,
        "use protocol records human/LLM/tool roles and non-goals",
        f"missing protocol file or protocol phrases: {missing_needles}",
    )

    regression_summary = {
        "status": "PASS" if all(row["status"] == "PASS" for row in checks) else "FAIL",
        "audit_cards_checked": len(cards),
        "route_counts": dict(sorted(route_counts.items())),
        "decision_counts": dict(sorted(decision_counts.items())),
        "source_counts": dict(sorted(source_counts.items())),
        "checks_passed": sum(1 for row in checks if row["status"] == "PASS"),
        "checks_failed": sum(1 for row in checks if row["status"] == "FAIL"),
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(output_dir / "reviewer_audit_demo_regression_checks.csv", checks, ["check_id", "label", "status", "evidence"])
    (output_dir / "reviewer_audit_demo_regression_summary.json").write_text(
        json.dumps(regression_summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_dir / "reviewer_audit_demo_regression_report.md").write_text(
        build_report(regression_summary, checks),
        encoding="utf-8",
    )

    if regression_summary["status"] != "PASS":
        print("FAIL reviewer audit demo regression")
        print(f"checks_failed: {regression_summary['checks_failed']}")
        return 1

    print("PASS reviewer audit demo regression")
    print(f"audit_cards_checked: {regression_summary['audit_cards_checked']}")
    print(f"checks_passed: {regression_summary['checks_passed']}")
    print("locked_registered_template_controls: 8")
    print("locked_fail_closed_boundary: yes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
