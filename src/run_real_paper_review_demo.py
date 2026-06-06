#!/usr/bin/env python3
"""Run the public-safe real-paper template review demo.

The demo uses three V1.8-backed template families and a 72-row public-paper
candidate packet.  It is not a full-paper reviewer: candidate claims are already
supplied, and the runner either replays the public reference/conservative
outcome or scores an optional user/LLM adjudication CSV against that reference.
"""

from __future__ import annotations

import argparse
from collections import Counter
import csv
import json
from pathlib import Path
import re
import sys


FILES = {
    "templates": "artifact/real_paper_review_template_cards_v18_20260606.csv",
    "candidates": "artifact/real_paper_review_candidate_claims_v318b_20260606.csv",
    "reference": "artifact/real_paper_review_reference_outcomes_v318b_20260606.csv",
    "summary": "artifact/real_paper_review_evidence_summary_v318b_20260606.json",
}

REQUIRED_CANDIDATE_COLUMNS = [
    "row_id",
    "source_id",
    "family",
    "template_id",
    "title",
    "source_url",
    "section_locator",
    "source_span_excerpt",
    "candidate_claim",
]

REQUIRED_ADJUDICATION_COLUMNS = [
    "row_id",
    "candidate_release_safe_yes_no",
    "display_action",
    "reportability_gate",
    "reason_code",
]

ALLOWED_SAFE_VALUES = {"yes", "no"}
ALLOWED_DISPLAY_ACTIONS = {
    "ACCEPT",
    "WEAKEN",
    "BLOCK_AND_SUGGEST",
    "SUPPORT_ONLY",
    "SUPPRESS",
    "REJECT_OR_OUT_OF_SCOPE",
    "NEEDS_TEMPLATE_ADMISSION",
}
ALLOWED_REPORTABILITY_GATES = {
    "reportable_as_claim",
    "reportable_after_weakening",
    "blocked_but_corrected_claim_available",
    "support_only_context",
    "suppress_no_safe_public_claim",
    "do_not_call_claim_runner",
}
ALLOWED_REASON_CODES = {
    "source_supports_candidate",
    "source_supports_weakened_candidate",
    "source_supports_corrected_claim_but_candidate_blocked",
    "source_background_only",
    "source_forbids_candidate_no_repair",
    "outside_registered_template_family",
    "out_of_scope_for_claim_contract",
}

PRIVATE_PATTERNS = (
    re.compile(r"/Users/[A-Za-z0-9._-]+"),
    re.compile(r"\bconnect\.[A-Za-z0-9.-]+\b"),
    re.compile(
        r"\b(?:"
        + "|".join(
            [
                "CODEX" + "_ONLY",
                "CLAUDE" + "_ONLY",
                "EX" + "CHANGE",
                "private" + "_scoring",
                "do" + "_not" + "_share",
            ]
        )
        + r")\b"
    ),
    re.compile(
        r"\b(?:password|passwd|secret|credential|api[_-]?key)\b\s*[:=]\s*"
        r"['\"]?[A-Za-z0-9_./+=-]{8,}",
        re.IGNORECASE,
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a public-safe three-family real-paper claim review report."
    )
    parser.add_argument("--root", default=".", help="Release root. Default: current directory.")
    parser.add_argument("--templates", default=FILES["templates"], help="Template card CSV.")
    parser.add_argument("--candidates", default=FILES["candidates"], help="Candidate claim CSV.")
    parser.add_argument("--reference", default=FILES["reference"], help="Reference outcome CSV.")
    parser.add_argument("--summary", default=FILES["summary"], help="Evidence summary JSON.")
    parser.add_argument(
        "--adjudication",
        default="",
        help="Optional user/LLM adjudication CSV to score against the reference.",
    )
    parser.add_argument(
        "--output",
        default="reports/real_paper_review_demo_20260606",
        help="Output directory. Relative paths are resolved under root.",
    )
    return parser.parse_args()


def resolve(root: Path, value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = root / path
    return path.resolve()


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def short(text: str, limit: int = 150) -> str:
    text = " ".join((text or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "..."


def has_private_marker(row: dict[str, str]) -> bool:
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


def accuracy(rows: list[dict[str, object]], pred: str, target: str) -> float:
    if not rows:
        return 0.0
    return sum(1 for row in rows if row[pred] == row[target]) / len(rows)


def duplicate_values(rows: list[dict[str, str]], column: str) -> list[str]:
    counts = Counter(row.get(column, "") for row in rows)
    return sorted(value for value, count in counts.items() if value and count > 1)


def invalid_values(
    rows: list[dict[str, str]], column: str, allowed: set[str]
) -> list[str]:
    return sorted({row.get(column, "") for row in rows if row.get(column, "") not in allowed})


def build_joined_rows(
    candidates: list[dict[str, str]],
    references: list[dict[str, str]],
    user_rows: list[dict[str, str]] | None,
) -> list[dict[str, object]]:
    ref_by_id = {row["row_id"]: row for row in references}
    user_by_id = {row["row_id"]: row for row in user_rows or []}
    joined: list[dict[str, object]] = []
    for row in candidates:
        ref = ref_by_id[row["row_id"]]
        user = user_by_id.get(row["row_id"], {})
        item: dict[str, object] = {
            "row_id": row["row_id"],
            "source_id": row["source_id"],
            "family": row["family"],
            "template_id": row["template_id"],
            "title": row["title"],
            "source_url": row["source_url"],
            "section_locator": row["section_locator"],
            "candidate_claim": row["candidate_claim"],
            "reference_safe": ref["reference_candidate_release_safe"],
            "reference_action": ref["reference_display_action"],
            "reference_gate": ref["reference_reportability_gate"],
            "reference_reason": ref["reference_reason_code"],
            "reference_rewrite": ref["reference_suggested_rewrite"],
            "conservative_safe": ref["conservative_candidate_release_safe"],
            "conservative_action": ref["conservative_display_action"],
            "conservative_gate": ref["conservative_reportability_gate"],
            "conservative_reason": ref["conservative_reason_code"],
        }
        if user_rows is not None:
            item.update(
                {
                    "user_safe": user.get("candidate_release_safe_yes_no", ""),
                    "user_action": user.get("display_action", ""),
                    "user_gate": user.get("reportability_gate", ""),
                    "user_reason": user.get("reason_code", ""),
                    "user_suggested_rewrite": user.get("suggested_rewrite", ""),
                    "user_safe_correct": user.get("candidate_release_safe_yes_no", "")
                    == ref["reference_candidate_release_safe"],
                    "user_action_correct": user.get("display_action", "")
                    == ref["reference_display_action"],
                    "user_gate_correct": user.get("reportability_gate", "")
                    == ref["reference_reportability_gate"],
                    "user_reason_correct": user.get("reason_code", "")
                    == ref["reference_reason_code"],
                    "user_unsafe_false_release": (
                        ref["reference_candidate_release_safe"] == "no"
                        and user.get("candidate_release_safe_yes_no", "") == "yes"
                    ),
                }
            )
        item.update(
            {
                "conservative_safe_correct": ref["conservative_candidate_release_safe"]
                == ref["reference_candidate_release_safe"],
                "conservative_action_correct": ref["conservative_display_action"]
                == ref["reference_display_action"],
                "conservative_gate_correct": ref["conservative_reportability_gate"]
                == ref["reference_reportability_gate"],
                "conservative_unsafe_false_release": (
                    ref["reference_candidate_release_safe"] == "no"
                    and ref["conservative_candidate_release_safe"] == "yes"
                ),
            }
        )
        joined.append(item)
    return joined


def summarize(joined: list[dict[str, object]], user_rows_present: bool) -> dict[str, object]:
    summary: dict[str, object] = {
        "rows": len(joined),
        "source_papers": len({row["source_id"] for row in joined}),
        "family_counts": dict(Counter(str(row["family"]) for row in joined)),
        "reference_action_counts": dict(Counter(str(row["reference_action"]) for row in joined)),
        "reference_safe_counts": dict(Counter(str(row["reference_safe"]) for row in joined)),
        "conservative_candidate_safety_accuracy": accuracy(
            joined, "conservative_safe", "reference_safe"
        ),
        "conservative_display_action_accuracy": accuracy(
            joined, "conservative_action", "reference_action"
        ),
        "conservative_gate_accuracy": accuracy(joined, "conservative_gate", "reference_gate"),
        "conservative_unsafe_false_releases": sum(
            1 for row in joined if row["conservative_unsafe_false_release"]
        ),
    }
    if user_rows_present:
        summary.update(
            {
                "user_candidate_safety_accuracy": accuracy(joined, "user_safe", "reference_safe"),
                "user_display_action_accuracy": accuracy(joined, "user_action", "reference_action"),
                "user_gate_accuracy": accuracy(joined, "user_gate", "reference_gate"),
                "user_reason_accuracy": accuracy(joined, "user_reason", "reference_reason"),
                "user_unsafe_false_releases": sum(
                    1 for row in joined if row["user_unsafe_false_release"]
                ),
            }
        )
    return summary


def build_markdown(
    summary: dict[str, object],
    checks: list[dict[str, str]],
    joined: list[dict[str, object]],
    user_rows_present: bool,
) -> str:
    lines: list[str] = []
    lines.append("# Real-Paper Template Review Demo")
    lines.append("")
    lines.append("Status: generated from public-safe ClaimContractBench assets.")
    lines.append("")
    lines.append("## What This Demonstrates")
    lines.append("")
    lines.append(
        "This demo applies three V1.8-backed claim-template families to supplied "
        "candidate claims from public arXiv papers: `llm_evaluation`, "
        "`resource_documentation`, and `uncertainty_calibration`. It checks a "
        "candidate claim against a short source excerpt and returns whether the "
        "claim can be released as written, weakened, rewritten, kept as "
        "support-only, blocked with a suggested correction, or suppressed."
    )
    lines.append("")
    lines.append("It is not automatic full-paper review, full-paper claim discovery, or a human-utility study.")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Item | Value |")
    lines.append("| --- | ---: |")
    for key in [
        "rows",
        "source_papers",
        "conservative_candidate_safety_accuracy",
        "conservative_display_action_accuracy",
        "conservative_gate_accuracy",
        "conservative_unsafe_false_releases",
    ]:
        lines.append(f"| {key} | {summary[key]} |")
    if user_rows_present:
        for key in [
            "user_candidate_safety_accuracy",
            "user_display_action_accuracy",
            "user_gate_accuracy",
            "user_reason_accuracy",
            "user_unsafe_false_releases",
        ]:
            lines.append(f"| {key} | {summary[key]} |")
    lines.append("")
    lines.append("## Family Counts")
    lines.append("")
    lines.append("| Family | Rows |")
    lines.append("| --- | ---: |")
    for family, count in sorted(summary["family_counts"].items()):  # type: ignore[union-attr]
        lines.append(f"| {family} | {count} |")
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
    lines.append("## Example Rows")
    lines.append("")
    lines.append("| Row | Family | Reference | Conservative | Claim |")
    lines.append("| --- | --- | --- | --- | --- |")
    for row in joined[:12]:
        lines.append(
            f"| {row['row_id']} | {row['family']} | {row['reference_action']} / "
            f"{row['reference_safe']} | {row['conservative_action']} / "
            f"{row['conservative_safe']} | {short(str(row['candidate_claim']), 110)} |"
        )
    lines.append("")
    lines.append("## Important Limit")
    lines.append("")
    lines.append(
        "The included reference outcomes are diagnostic labels for supplied "
        "candidate claims, not a claim that arbitrary papers can be reviewed "
        "automatically. The most important residual failure mode is unsafe release "
        "around uncertainty-calibration background/support-only rows."
    )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    output = resolve(root, args.output)

    try:
        templates, template_columns = read_csv(resolve(root, args.templates))
        candidates, candidate_columns = read_csv(resolve(root, args.candidates))
        references, reference_columns = read_csv(resolve(root, args.reference))
        evidence_summary = json.loads(resolve(root, args.summary).read_text(encoding="utf-8"))
        user_rows = None
        user_columns: list[str] = []
        if args.adjudication:
            user_rows, user_columns = read_csv(resolve(root, args.adjudication))
    except (OSError, UnicodeDecodeError, csv.Error, json.JSONDecodeError) as exc:
        print("FAIL real-paper review demo")
        print(f"could not load input assets: {exc}")
        return 1

    checks: list[dict[str, str]] = []
    add_check(
        checks,
        "RP-001",
        "candidate columns",
        all(column in candidate_columns for column in REQUIRED_CANDIDATE_COLUMNS),
        f"{len(candidate_columns)} columns include required candidate fields",
        "candidate packet is missing required columns",
    )
    add_check(
        checks,
        "RP-002",
        "template families",
        {row["family"] for row in templates}
        == {"llm_evaluation", "resource_documentation", "uncertainty_calibration"},
        "three V1.8-backed template families are present",
        "template family set does not match the V1.8-backed public demo",
    )
    add_check(
        checks,
        "RP-003",
        "row alignment",
        len(candidates) == len(references)
        and not duplicate_values(candidates, "row_id")
        and not duplicate_values(references, "row_id")
        and {row["row_id"] for row in candidates} == {row["row_id"] for row in references},
        f"{len(candidates)} candidate rows join to reference outcomes",
        "candidate and reference row ids do not align or contain duplicates",
    )
    add_check(
        checks,
        "RP-004",
        "family balance",
        Counter(row["family"] for row in candidates)
        == {"llm_evaluation": 24, "resource_documentation": 24, "uncertainty_calibration": 24},
        "24 rows in each of three families",
        "candidate packet is not balanced at 24/24/24 rows",
    )
    add_check(
        checks,
        "RP-005",
        "source balance",
        len({row["source_id"] for row in candidates}) == 18,
        "18 public-paper source ids",
        "candidate packet does not contain 18 public-paper source ids",
    )
    add_check(
        checks,
        "RP-006",
        "public-safe content scan",
        not any(has_private_marker(row) for row in candidates + references + templates),
        "no private path, private scoring marker, connector host, or credential-like text found",
        "public demo contains a private marker",
    )
    invalid_reference_safe = invalid_values(
        references, "reference_candidate_release_safe", ALLOWED_SAFE_VALUES
    ) + invalid_values(references, "conservative_candidate_release_safe", ALLOWED_SAFE_VALUES)
    invalid_reference_actions = invalid_values(
        references, "reference_display_action", ALLOWED_DISPLAY_ACTIONS
    ) + invalid_values(references, "conservative_display_action", ALLOWED_DISPLAY_ACTIONS)
    invalid_reference_gates = invalid_values(
        references, "reference_reportability_gate", ALLOWED_REPORTABILITY_GATES
    ) + invalid_values(references, "conservative_reportability_gate", ALLOWED_REPORTABILITY_GATES)
    invalid_reference_reasons = invalid_values(
        references, "reference_reason_code", ALLOWED_REASON_CODES
    ) + invalid_values(references, "conservative_reason_code", ALLOWED_REASON_CODES)
    add_check(
        checks,
        "RP-006B",
        "reference outcome enum values",
        not (
            invalid_reference_safe
            or invalid_reference_actions
            or invalid_reference_gates
            or invalid_reference_reasons
        ),
        "reference and conservative outcomes are inside the public prompt contract",
        (
            f"invalid safe={invalid_reference_safe}, actions={invalid_reference_actions}, "
            f"gates={invalid_reference_gates}, reasons={invalid_reference_reasons}"
        ),
    )
    if user_rows is not None:
        add_check(
            checks,
            "RP-007",
            "user adjudication columns",
            all(column in user_columns for column in REQUIRED_ADJUDICATION_COLUMNS),
            f"{len(user_columns)} user columns include required adjudication fields",
            "user adjudication CSV is missing required columns",
        )
        add_check(
            checks,
            "RP-008",
            "user row coverage",
            len(user_rows) == len(candidates)
            and not duplicate_values(user_rows, "row_id")
            and {row["row_id"] for row in user_rows} == {row["row_id"] for row in candidates},
            f"{len(user_rows)} user rows align with candidate packet",
            "user adjudication rows do not align with candidate packet or contain duplicates",
        )
        invalid_safe = invalid_values(
            user_rows, "candidate_release_safe_yes_no", ALLOWED_SAFE_VALUES
        )
        invalid_actions = invalid_values(user_rows, "display_action", ALLOWED_DISPLAY_ACTIONS)
        invalid_gates = invalid_values(
            user_rows, "reportability_gate", ALLOWED_REPORTABILITY_GATES
        )
        invalid_reasons = invalid_values(user_rows, "reason_code", ALLOWED_REASON_CODES)
        add_check(
            checks,
            "RP-009",
            "user adjudication enum values",
            not (invalid_safe or invalid_actions or invalid_gates or invalid_reasons),
            "user adjudication values are inside the public prompt contract",
            (
                f"invalid safe={invalid_safe}, actions={invalid_actions}, "
                f"gates={invalid_gates}, reasons={invalid_reasons}"
            ),
        )

    failed = [row for row in checks if row["status"] == "FAIL"]
    if failed:
        print("FAIL real-paper review demo")
        for row in failed:
            print(f"- {row['check_id']} {row['label']}: {row['evidence']}")
        return 1

    joined = build_joined_rows(candidates, references, user_rows)
    summary = summarize(joined, user_rows is not None)
    summary["evidence_summary_limits"] = evidence_summary.get("limitations", [])
    summary["checks_passed"] = len(checks)
    summary["checks_failed"] = 0

    output.mkdir(parents=True, exist_ok=True)
    decision_columns = list(joined[0].keys())
    write_csv(output / "real_paper_review_demo_decisions.csv", joined, decision_columns)
    write_csv(output / "real_paper_review_demo_checks.csv", checks, list(checks[0].keys()))
    write_json(output / "real_paper_review_demo_summary.json", summary)
    (output / "real_paper_review_demo_report.md").write_text(
        build_markdown(summary, checks, joined, user_rows is not None),
        encoding="utf-8",
    )

    print("PASS real-paper review demo")
    print(f"rows: {summary['rows']}")
    print(f"source_papers: {summary['source_papers']}")
    print(f"families: {summary['family_counts']}")
    print(f"conservative_candidate_safety_accuracy: {summary['conservative_candidate_safety_accuracy']:.3f}")
    print(f"conservative_display_action_accuracy: {summary['conservative_display_action_accuracy']:.3f}")
    print(f"conservative_unsafe_false_releases: {summary['conservative_unsafe_false_releases']}")
    if user_rows is not None:
        print(f"user_candidate_safety_accuracy: {summary['user_candidate_safety_accuracy']:.3f}")
        print(f"user_display_action_accuracy: {summary['user_display_action_accuracy']:.3f}")
        print(f"user_unsafe_false_releases: {summary['user_unsafe_false_releases']}")
    print("outputs:")
    print(f"- {output / 'real_paper_review_demo_report.md'}")
    print(f"- {output / 'real_paper_review_demo_decisions.csv'}")
    print(f"- {output / 'real_paper_review_demo_summary.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
