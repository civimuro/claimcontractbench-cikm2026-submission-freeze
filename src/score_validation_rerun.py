#!/usr/bin/env python3
"""Score fresh public-safe validation-ladder reruns.

This scorer is intentionally small. It does not call an LLM; it compares a
fresh user/LLM CSV against the frozen public-safe reference labels for either
the template-rule stress packet or the positive real-paper packet.
"""

from __future__ import annotations

import argparse
from collections import Counter
import csv
import json
from pathlib import Path
import re


LADDER_DIR = "artifact/validation_ladder_20260607"

FILES = {
    "template_reference": f"{LADDER_DIR}/template_rule_stress_proxy_adjudication_20260605.csv",
    "positive_reference": f"{LADDER_DIR}/positive_realpaper_locked_reference_20260605.csv",
}

RELEASE_ACTIONS = {"ACCEPT", "REWRITE", "WEAKEN"}
PROTECTED_ACTIONS = {"SUPPORT_ONLY", "SUPPRESS", "REJECT_OR_OUT_OF_SCOPE"}

PRIVATE_PATTERNS = (
    re.compile(r"/Users/[A-Za-z0-9._-]+"),
    re.compile(r"\bconnect\.[A-Za-z0-9.-]+\b"),
    re.compile(
        r"\b(?:password|passwd|secret|credential|api[_-]?key)\b\s*[:=]\s*"
        r"['\"]?[A-Za-z0-9_./+=-]{8,}",
        re.IGNORECASE,
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Score a fresh validation-ladder rerun CSV.")
    parser.add_argument("--root", default=".", help="Release root. Default: current directory.")
    parser.add_argument(
        "--rung",
        choices=["template-stress", "positive-realpaper"],
        required=True,
        help="Which rerun packet to score.",
    )
    parser.add_argument("--input", required=True, help="Fresh rerun CSV to score.")
    parser.add_argument("--output", required=True, help="Output directory for report files.")
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


def ratio(num: int, den: int) -> str:
    return "NA" if den == 0 else f"{num / den:.3f}"


def release_side(action: str, explicit_emit: str = "") -> str:
    emit = (explicit_emit or "").strip().lower()
    if emit in {"yes", "no"}:
        return emit
    if action in RELEASE_ACTIONS:
        return "yes"
    if action in PROTECTED_ACTIONS:
        return "no"
    return "unknown"


def has_private_marker(row: dict[str, str]) -> bool:
    text = " ".join(str(value or "") for value in row.values())
    return any(pattern.search(text) for pattern in PRIVATE_PATTERNS)


def score_template(root: Path, fresh_path: Path) -> tuple[dict[str, object], list[dict[str, object]]]:
    fresh, fresh_fields = read_csv(fresh_path)
    reference, _ = read_csv(resolve(root, FILES["template_reference"]))
    required = {"heldout_row_id", "annotator_action"}
    missing = sorted(required - set(fresh_fields))
    if missing:
        raise SystemExit(f"FAIL scorer: missing columns for template-stress: {missing}")
    ref_by = {row["heldout_row_id"]: row for row in reference}
    fresh_by = {row["heldout_row_id"]: row for row in fresh}
    joined: list[dict[str, object]] = []
    for row_id, ref in ref_by.items():
        got = fresh_by.get(row_id, {})
        predicted = got.get("annotator_action", "")
        target = ref["gold_action"]
        false_release = target in PROTECTED_ACTIONS and predicted in RELEASE_ACTIONS
        joined.append(
            {
                "row_id": row_id,
                "predicted_action": predicted,
                "reference_action": target,
                "action_match": "yes" if predicted == target else "no",
                "dangerous_false_release": "yes" if false_release else "no",
            }
        )
    summary = {
        "rung": "template-stress",
        "rows_expected": len(reference),
        "rows_received": len(fresh),
        "missing_reference_rows": sorted(set(ref_by) - set(fresh_by)),
        "extra_rows": sorted(set(fresh_by) - set(ref_by)),
        "action_accuracy": ratio(sum(1 for row in joined if row["action_match"] == "yes"), len(joined)),
        "dangerous_false_releases": sum(
            1 for row in joined if row["dangerous_false_release"] == "yes"
        ),
        "private_marker_rows": sum(1 for row in fresh if has_private_marker(row)),
        "interpretation_limit": "Fresh LLM/human rerun against proxy adjudication; not human gold.",
    }
    return summary, joined


def score_positive(root: Path, fresh_path: Path) -> tuple[dict[str, object], list[dict[str, object]]]:
    fresh, fresh_fields = read_csv(fresh_path)
    reference, _ = read_csv(resolve(root, FILES["positive_reference"]))
    required = {"row_id", "adjudicated_action"}
    missing = sorted(required - set(fresh_fields))
    if missing:
        raise SystemExit(f"FAIL scorer: missing columns for positive-realpaper: {missing}")
    ref_by = {row["row_id"]: row for row in reference}
    fresh_by = {row["row_id"]: row for row in fresh}
    joined: list[dict[str, object]] = []
    for row_id, ref in ref_by.items():
        got = fresh_by.get(row_id, {})
        predicted = got.get("adjudicated_action", "")
        target = ref["adjudicated_action"]
        predicted_release = release_side(predicted, got.get("emit_worthy_yes_no", ""))
        target_release = ref["emit_worthy_yes_no"]
        false_release = target_release == "no" and predicted_release == "yes"
        joined.append(
            {
                "row_id": row_id,
                "family": ref["family"],
                "predicted_action": predicted,
                "reference_action": target,
                "predicted_release_side": predicted_release,
                "reference_release_side": target_release,
                "action_match": "yes" if predicted == target else "no",
                "release_side_match": "yes" if predicted_release == target_release else "no",
                "dangerous_false_release": "yes" if false_release else "no",
            }
        )
    by_family = Counter(row["family"] for row in joined)
    family_summary = {}
    for family in sorted(by_family):
        rows = [row for row in joined if row["family"] == family]
        family_summary[family] = {
            "rows": len(rows),
            "action_accuracy": ratio(sum(1 for row in rows if row["action_match"] == "yes"), len(rows)),
            "release_side_accuracy": ratio(
                sum(1 for row in rows if row["release_side_match"] == "yes"), len(rows)
            ),
            "dangerous_false_releases": sum(
                1 for row in rows if row["dangerous_false_release"] == "yes"
            ),
        }
    summary = {
        "rung": "positive-realpaper",
        "rows_expected": len(reference),
        "rows_received": len(fresh),
        "missing_reference_rows": sorted(set(ref_by) - set(fresh_by)),
        "extra_rows": sorted(set(fresh_by) - set(ref_by)),
        "action_accuracy": ratio(sum(1 for row in joined if row["action_match"] == "yes"), len(joined)),
        "release_side_accuracy": ratio(
            sum(1 for row in joined if row["release_side_match"] == "yes"), len(joined)
        ),
        "dangerous_false_releases": sum(
            1 for row in joined if row["dangerous_false_release"] == "yes"
        ),
        "family_summary": family_summary,
        "private_marker_rows": sum(1 for row in fresh if has_private_marker(row)),
        "interpretation_limit": "Fresh source-only rerun against locked source-only reference labels; not human gold or hard robustness.",
    }
    return summary, joined


def build_report(summary: dict[str, object]) -> str:
    lines = [
        "# Validation Rerun Score",
        "",
        f"Rung: `{summary['rung']}`",
        f"Rows expected: `{summary['rows_expected']}`",
        f"Rows received: `{summary['rows_received']}`",
        f"Action accuracy: `{summary['action_accuracy']}`",
    ]
    if "release_side_accuracy" in summary:
        lines.append(f"Release-side accuracy: `{summary['release_side_accuracy']}`")
    lines += [
        f"Dangerous false releases: `{summary['dangerous_false_releases']}`",
        f"Missing reference rows: `{len(summary['missing_reference_rows'])}`",
        f"Extra rows: `{len(summary['extra_rows'])}`",
        f"Private-marker rows: `{summary['private_marker_rows']}`",
        "",
        f"Limit: {summary['interpretation_limit']}",
        "",
    ]
    if "family_summary" in summary:
        lines += ["## Family Summary", "", "| Family | Rows | Action | Release Side | Dangerous False Releases |", "| --- | ---: | ---: | ---: | ---: |"]
        for family, row in summary["family_summary"].items():
            lines.append(
                f"| {family} | {row['rows']} | {row['action_accuracy']} | {row['release_side_accuracy']} | {row['dangerous_false_releases']} |"
            )
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    fresh_path = resolve(root, args.input)
    output = resolve(root, args.output)
    if args.rung == "template-stress":
        summary, rows = score_template(root, fresh_path)
    else:
        summary, rows = score_positive(root, fresh_path)
    output.mkdir(parents=True, exist_ok=True)
    write_json(output / "rerun_score_summary.json", summary)
    write_csv(output / "rerun_score_by_row.csv", rows, list(rows[0].keys()) if rows else [])
    (output / "rerun_score_report.md").write_text(build_report(summary), encoding="utf-8")
    print("PASS validation rerun score")
    print(f"rung: {summary['rung']}")
    print(f"rows_expected: {summary['rows_expected']}")
    print(f"rows_received: {summary['rows_received']}")
    print(f"action_accuracy: {summary['action_accuracy']}")
    if "release_side_accuracy" in summary:
        print(f"release_side_accuracy: {summary['release_side_accuracy']}")
    print(f"dangerous_false_releases: {summary['dangerous_false_releases']}")
    print(f"report: {output / 'rerun_score_report.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

