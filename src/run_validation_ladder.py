#!/usr/bin/env python3
"""Check the public-safe validation ladder used by the resource paper.

The ladder is deliberately modest.  It verifies three bounded diagnostics:

1. template-rule stress over a 42-row LLM-proxy blind packet;
2. positive public-paper use over a 72-row admitted-template packet;
3. boundary replay over the current 72-row conservative real-paper demo.

None of these diagnostics is a human-utility study or autonomous full-paper
review.  The script exists so paper-facing numbers are not just listed in prose:
reviewers can inspect the files and recompute the core summaries.
"""

from __future__ import annotations

import argparse
from collections import Counter
import csv
import json
from pathlib import Path
import re
import sys


LADDER_DIR = "artifact/validation_ladder_20260607"

FILES = {
    "stress_blind": f"{LADDER_DIR}/template_rule_stress_blind_rows_20260605.csv",
    "stress_a": f"{LADDER_DIR}/template_rule_stress_channel_A_20260605.csv",
    "stress_b": f"{LADDER_DIR}/template_rule_stress_channel_B_20260605.csv",
    "stress_c": f"{LADDER_DIR}/template_rule_stress_proxy_adjudication_20260605.csv",
    "stress_summary": f"{LADDER_DIR}/template_rule_stress_summary_20260605.json",
    "positive_a": f"{LADDER_DIR}/positive_realpaper_router_R4_A_by_row_20260605.csv",
    "positive_b": f"{LADDER_DIR}/positive_realpaper_router_R4_B_by_row_20260605.csv",
    "positive_summary": f"{LADDER_DIR}/positive_realpaper_router_aggregate_summary_20260605.json",
    "positive_baseline": f"{LADDER_DIR}/positive_realpaper_failure_baseline_note_20260605.md",
    "positive_closeout": f"{LADDER_DIR}/positive_realpaper_validation_closeout_20260605.md",
    "boundary_candidates": "artifact/real_paper_review_candidate_claims_v318b_20260606.csv",
    "boundary_reference": "artifact/real_paper_review_reference_outcomes_v318b_20260606.csv",
}

LABELS = [
    "ACCEPT",
    "REWRITE",
    "WEAKEN",
    "SUPPORT_ONLY",
    "SUPPRESS",
    "REJECT_OR_OUT_OF_SCOPE",
]
RELEASE_ACTIONS = {"ACCEPT", "REWRITE", "WEAKEN"}
PROTECTED_ACTIONS = {"SUPPRESS", "REJECT_OR_OUT_OF_SCOPE"}
SPAN_FOUND_LABELS = {"yes", "partial", "no"}

PRIVATE_PATTERNS = (
    ("absolute local user path", re.compile(r"/Users/[A-Za-z0-9._-]+")),
    ("remote connector host", re.compile(r"\bconnect\.[A-Za-z0-9.-]+\b")),
    (
        "private coordination marker",
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
    ),
    (
        "credential-like assignment",
        re.compile(
            r"\b(?:password|passwd|secret|credential|api[_-]?key)\b\s*[:=]\s*"
            r"['\"]?[A-Za-z0-9_./+=-]{8,}",
            re.IGNORECASE,
        ),
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Recompute the public validation ladder summaries.")
    parser.add_argument("--root", default=".", help="Release root. Default: current directory.")
    parser.add_argument(
        "--output",
        default="reports/validation_ladder_20260607",
        help="Output directory for regenerated ladder report.",
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


def cohens_kappa(pairs: list[tuple[str, str]], labels: list[str]) -> str:
    if not pairs:
        return "NA"
    n = len(pairs)
    observed = sum(1 for left, right in pairs if left == right) / n
    left_counts = Counter(left for left, _ in pairs)
    right_counts = Counter(right for _, right in pairs)
    expected = sum((left_counts[label] / n) * (right_counts[label] / n) for label in labels)
    if expected == 1.0:
        return "1.000" if observed == 1.0 else "0.000"
    return f"{(observed - expected) / (1.0 - expected):.3f}"


def scan_public_safety(paths: list[Path]) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    for path in paths:
        text = path.read_text(encoding="utf-8", errors="ignore")
        for label, pattern in PRIVATE_PATTERNS:
            if pattern.search(text):
                issues.append({"path": str(path), "issue": label})
    return issues


def add_check(
    checks: list[dict[str, object]],
    check_id: str,
    label: str,
    ok: bool,
    evidence: str,
) -> None:
    checks.append(
        {
            "check_id": check_id,
            "label": label,
            "status": "PASS" if ok else "FAIL",
            "evidence": evidence,
        }
    )


def by_id(rows: list[dict[str, str]], key: str) -> dict[str, dict[str, str]]:
    return {row[key]: row for row in rows}


def summarize_template_rule_stress(root: Path, checks: list[dict[str, object]]) -> dict[str, object]:
    blind = read_csv(resolve(root, FILES["stress_blind"]))
    rows_a = read_csv(resolve(root, FILES["stress_a"]))
    rows_b = read_csv(resolve(root, FILES["stress_b"]))
    rows_c = read_csv(resolve(root, FILES["stress_c"]))
    stored = json.loads(resolve(root, FILES["stress_summary"]).read_text(encoding="utf-8"))

    a_by = by_id(rows_a, "heldout_row_id")
    b_by = by_id(rows_b, "heldout_row_id")
    c_by = by_id(rows_c, "heldout_row_id")
    ids = [row["heldout_row_id"] for row in blind]
    ids_ok = ids == [row["heldout_row_id"] for row in rows_a] == [
        row["heldout_row_id"] for row in rows_b
    ] == [row["heldout_row_id"] for row in rows_c]

    ab_pairs: list[tuple[str, str]] = []
    span_pairs: list[tuple[str, str]] = []
    a_vs_c = 0
    b_vs_c = 0
    dangerous_a = 0
    dangerous_b = 0
    scored_rows: list[dict[str, object]] = []
    for row_id in ids:
        a = a_by[row_id]
        b = b_by[row_id]
        c = c_by[row_id]
        action_a = a["annotator_action"]
        action_b = b["annotator_action"]
        action_c = c["gold_action"]
        ab_pairs.append((action_a, action_b))
        span_pairs.append((a["annotator_claim_level_span_found"], b["annotator_claim_level_span_found"]))
        if action_a == action_c:
            a_vs_c += 1
        if action_b == action_c:
            b_vs_c += 1
        false_release_a = action_c in PROTECTED_ACTIONS and action_a in RELEASE_ACTIONS
        false_release_b = action_c in PROTECTED_ACTIONS and action_b in RELEASE_ACTIONS
        dangerous_a += int(false_release_a)
        dangerous_b += int(false_release_b)
        scored_rows.append(
            {
                "row_id": row_id,
                "action_A": action_a,
                "action_B": action_b,
                "proxy_adjudicated_action": action_c,
                "A_equals_B": "yes" if action_a == action_b else "no",
                "A_equals_proxy": "yes" if action_a == action_c else "no",
                "B_equals_proxy": "yes" if action_b == action_c else "no",
                "dangerous_false_release_A": "yes" if false_release_a else "no",
                "dangerous_false_release_B": "yes" if false_release_b else "no",
            }
        )

    summary = {
        "name": "template_rule_stress",
        "evidence_class": "CROSS_MODEL_LLM_PROXY_DIAGNOSTIC_ONLY",
        "rows": len(ids),
        "A_B_action_agreement": ratio(sum(1 for a, b in ab_pairs if a == b), len(ab_pairs)),
        "A_B_action_kappa": cohens_kappa(ab_pairs, LABELS),
        "A_B_span_found_kappa": cohens_kappa(span_pairs, sorted(SPAN_FOUND_LABELS)),
        "A_vs_proxy_accuracy": ratio(a_vs_c, len(ids)),
        "B_vs_proxy_accuracy": ratio(b_vs_c, len(ids)),
        "dangerous_false_release_A_count": dangerous_a,
        "dangerous_false_release_B_count": dangerous_b,
        "action_counts_proxy": dict(sorted(Counter(c_by[row_id]["gold_action"] for row_id in ids).items())),
        "stored_summary_path": FILES["stress_summary"],
        "interpretation_limit": "LLM-proxy diagnostic only; not human-independent reliability or human utility.",
    }
    add_check(
        checks,
        "VL-01",
        "template stress row ids align",
        ids_ok,
        f"rows={len(ids)}",
    )
    add_check(
        checks,
        "VL-02",
        "template stress recomputed metrics match stored summary",
        summary["A_B_action_kappa"] == stored.get("A_B_action_kappa")
        and str(summary["dangerous_false_release_A_count"]) == str(stored.get("dangerous_false_release_A_count"))
        and str(summary["dangerous_false_release_B_count"]) == str(stored.get("dangerous_false_release_B_count")),
        f"recomputed_kappa={summary['A_B_action_kappa']}; stored_kappa={stored.get('A_B_action_kappa')}",
    )
    summary["scored_rows"] = scored_rows
    return summary


def summarize_positive_realpaper(root: Path, checks: list[dict[str, object]]) -> dict[str, object]:
    rows_by_label = {
        "R4_A": read_csv(resolve(root, FILES["positive_a"])),
        "R4_B": read_csv(resolve(root, FILES["positive_b"])),
    }
    stored = json.loads(resolve(root, FILES["positive_summary"]).read_text(encoding="utf-8"))
    stored_by_label = {row["label"]: row for row in stored.get("summaries", [])}
    summaries: list[dict[str, object]] = []
    family_rows: list[dict[str, object]] = []
    for label, rows in rows_by_label.items():
        action = sum(1 for row in rows if row["action_match"] == "yes")
        release = sum(1 for row in rows if row["release_side_match"] == "yes")
        dangerous = sum(1 for row in rows if row["dangerous_false_release"] == "yes")
        by_family = Counter(row["family"] for row in rows)
        summary = {
            "label": label,
            "rows": len(rows),
            "action_accuracy_count": action,
            "action_accuracy_rate": ratio(action, len(rows)),
            "release_side_accuracy_count": release,
            "release_side_accuracy_rate": ratio(release, len(rows)),
            "dangerous_false_release_count": dangerous,
            "gold_action_distribution": dict(sorted(Counter(row["gold_action"] for row in rows).items())),
            "interpretation_limit": "positive admitted-template use; gold is mostly release-side and not a robustness stress test.",
        }
        summaries.append(summary)
        for family in sorted(by_family):
            fam_rows = [row for row in rows if row["family"] == family]
            fam_action = sum(1 for row in fam_rows if row["action_match"] == "yes")
            fam_release = sum(1 for row in fam_rows if row["release_side_match"] == "yes")
            fam_danger = sum(1 for row in fam_rows if row["dangerous_false_release"] == "yes")
            family_rows.append(
                {
                    "label": label,
                    "family": family,
                    "rows": len(fam_rows),
                    "action_accuracy_rate": ratio(fam_action, len(fam_rows)),
                    "release_side_accuracy_rate": ratio(fam_release, len(fam_rows)),
                    "dangerous_false_release_count": fam_danger,
                }
            )
        stored_one = stored_by_label.get(label, {})
        add_check(
            checks,
            f"VL-03-{label}",
            f"positive real-paper {label} recomputes aggregate metrics",
            str(action) == str(stored_one.get("action_accuracy_count"))
            and str(release) == str(stored_one.get("release_side_accuracy_count"))
            and str(dangerous) == str(stored_one.get("dangerous_false_release_count")),
            f"action={action}/{len(rows)}; release={release}/{len(rows)}; dangerous={dangerous}",
        )
    return {
        "name": "positive_realpaper_use",
        "evidence_class": "PUBLIC_PAPER_POSITIVE_ADMITTED_TEMPLATE_DIAGNOSTIC",
        "conditions": summaries,
        "family_rows": family_rows,
        "stored_summary_path": FILES["positive_summary"],
        "baseline_note_path": FILES["positive_baseline"],
        "interpretation_limit": "bounded positive-use evidence; dominated by acceptable/release-side rows, so pair with the boundary replay.",
    }


def summarize_boundary_replay(root: Path, checks: list[dict[str, object]]) -> dict[str, object]:
    candidates = read_csv(resolve(root, FILES["boundary_candidates"]))
    references = read_csv(resolve(root, FILES["boundary_reference"]))
    cand_ids = [row["row_id"] for row in candidates]
    ref_ids = [row["row_id"] for row in references]
    rows = references
    safety = sum(
        1
        for row in rows
        if row["conservative_candidate_release_safe"] == row["reference_candidate_release_safe"]
    )
    action = sum(
        1 for row in rows if row["conservative_display_action"] == row["reference_display_action"]
    )
    unsafe = sum(
        1
        for row in rows
        if row["reference_candidate_release_safe"] == "no"
        and row["conservative_candidate_release_safe"] == "yes"
    )
    summary = {
        "name": "reportability_boundary_replay",
        "evidence_class": "PUBLIC_SAFE_BOUNDARY_REPLAY",
        "rows": len(rows),
        "source_papers": len({row["source_id"] for row in rows}),
        "family_distribution": dict(sorted(Counter(row["family"] for row in rows).items())),
        "candidate_release_safety_accuracy": ratio(safety, len(rows)),
        "display_action_accuracy": ratio(action, len(rows)),
        "unsafe_false_releases": unsafe,
        "candidate_packet": FILES["boundary_candidates"],
        "reference_outcomes": FILES["boundary_reference"],
        "direct_command": "python3 src/claimcontractbench.py realpaper-demo --output /tmp/claimcontractbench_realpaper_demo",
        "interpretation_limit": "boundary replay over supplied claims; not autonomous full-paper review or human utility.",
    }
    add_check(
        checks,
        "VL-04",
        "boundary replay candidate and reference row ids align",
        cand_ids == ref_ids,
        f"candidates={len(cand_ids)} reference={len(ref_ids)}",
    )
    add_check(
        checks,
        "VL-05",
        "boundary replay exposes remaining unsafe false releases",
        unsafe == 3,
        f"unsafe_false_releases={unsafe}",
    )
    return summary


def build_report(summary: dict[str, object], checks: list[dict[str, object]]) -> str:
    stress = summary["template_rule_stress"]
    positive = summary["positive_realpaper_use"]
    boundary = summary["reportability_boundary_replay"]
    lines = [
        "# Validation Ladder Report",
        "",
        f"Status: `{summary['status']}`",
        "",
        "This report connects paper-facing validation numbers to public-safe files in the frozen release. It is not a human-utility study and not an automatic peer-review claim.",
        "",
        "## Ladder Summary",
        "",
        "| Rung | What is checked | Main signal | Limit |",
        "| --- | --- | --- | --- |",
        (
            "| Template-rule stress | 42-row blind LLM-proxy packet | "
            f"A/B action kappa `{stress['A_B_action_kappa']}`, "
            f"dangerous false releases A/B `{stress['dangerous_false_release_A_count']}`/"
            f"`{stress['dangerous_false_release_B_count']}` | "
            "LLM-proxy only, not human-independent reliability. |"
        ),
        (
            "| Positive real-paper use | 18 public papers / 72 supplied claims under admitted templates | "
            f"R4_A action `{positive['conditions'][0]['action_accuracy_count']}/72`, "
            f"R4_B action `{positive['conditions'][1]['action_accuracy_count']}/72`, "
            "0 dangerous false releases | Positive packet, not hard robustness. |"
        ),
        (
            "| Boundary replay | Same 18-paper / 72-claim surface with harder reportability gates | "
            f"safety `{boundary['candidate_release_safety_accuracy']}`, "
            f"action/gate `{boundary['display_action_accuracy']}`, "
            f"unsafe false releases `{boundary['unsafe_false_releases']}` | "
            "Supplied claims only, not full-paper claim discovery. |"
        ),
        "",
        "## Checks",
        "",
        "| Check | Status | Evidence |",
        "| --- | --- | --- |",
    ]
    for check in checks:
        lines.append(f"| {check['check_id']} {check['label']} | {check['status']} | {check['evidence']} |")
    lines += [
        "",
        "## Files To Inspect",
        "",
        "- `artifact/validation_ladder_20260607/template_rule_stress_*.csv/json`: blind packet, A/B/C outputs, and stored template-rule-stress summary.",
        "- `artifact/validation_ladder_20260607/positive_realpaper_*.csv/json/md`: positive public-paper run rows, aggregate scores, and baseline caveat.",
        "- `artifact/real_paper_review_candidate_claims_v318b_20260606.csv` and `artifact/real_paper_review_reference_outcomes_v318b_20260606.csv`: current boundary replay packet and outcomes.",
        "",
        "## Safe Interpretation",
        "",
        "The release supports the narrow statement that admitted claim-template rules can be inspected and replayed on supplied candidate rows, including a positive public-paper packet and a harder boundary packet. It does not support claims of autonomous paper review, automatic claim discovery, human reviewer utility, broad empirical-ML coverage, or zero-risk release.",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    output = resolve(root, args.output)
    all_paths = [resolve(root, value) for value in FILES.values()]
    missing = [str(path) for path in all_paths if not path.is_file()]
    if missing:
        print("FAIL validation ladder")
        print("missing files:")
        for path in missing:
            print(f"- {path}")
        return 1

    checks: list[dict[str, object]] = []
    public_issues = scan_public_safety(all_paths)
    add_check(
        checks,
        "VL-00",
        "validation ladder files are public-safety scanned",
        not public_issues,
        f"issues={len(public_issues)}",
    )
    template_rule_stress = summarize_template_rule_stress(root, checks)
    positive_realpaper_use = summarize_positive_realpaper(root, checks)
    reportability_boundary_replay = summarize_boundary_replay(root, checks)

    if public_issues:
        for issue in public_issues:
            print(f"public-safety issue: {issue['path']} ({issue['issue']})")

    public_summary = {
        "status": "PASS" if all(check["status"] == "PASS" for check in checks) else "FAIL",
        "stage": "VALIDATION_LADDER_PUBLIC_SAFE_REPLAY",
        "template_rule_stress": {
            key: value for key, value in template_rule_stress.items() if key != "scored_rows"
        },
        "positive_realpaper_use": positive_realpaper_use,
        "reportability_boundary_replay": reportability_boundary_replay,
        "checks_passed": sum(1 for check in checks if check["status"] == "PASS"),
        "checks_failed": sum(1 for check in checks if check["status"] != "PASS"),
    }

    output.mkdir(parents=True, exist_ok=True)
    write_json(output / "validation_ladder_summary.json", public_summary)
    write_csv(
        output / "validation_ladder_checks.csv",
        checks,
        ["check_id", "label", "status", "evidence"],
    )
    write_csv(
        output / "template_rule_stress_scored_rows.csv",
        template_rule_stress["scored_rows"],
        [
            "row_id",
            "action_A",
            "action_B",
            "proxy_adjudicated_action",
            "A_equals_B",
            "A_equals_proxy",
            "B_equals_proxy",
            "dangerous_false_release_A",
            "dangerous_false_release_B",
        ],
    )
    (output / "validation_ladder_report.md").write_text(
        build_report(public_summary, checks), encoding="utf-8"
    )

    print(f"{public_summary['status']} validation ladder")
    print(f"template_rule_stress_rows: {template_rule_stress['rows']}")
    print(f"template_rule_stress_A_B_action_kappa: {template_rule_stress['A_B_action_kappa']}")
    print("positive_realpaper_use:")
    for row in positive_realpaper_use["conditions"]:
        print(
            f"- {row['label']}: action_accuracy={row['action_accuracy_count']}/{row['rows']} "
            f"release_side={row['release_side_accuracy_count']}/{row['rows']} "
            f"dangerous_false_release={row['dangerous_false_release_count']}"
        )
    print(
        "boundary_replay: "
        f"safety={reportability_boundary_replay['candidate_release_safety_accuracy']} "
        f"action={reportability_boundary_replay['display_action_accuracy']} "
        f"unsafe_false_releases={reportability_boundary_replay['unsafe_false_releases']}"
    )
    print(f"report: {output / 'validation_ladder_report.md'}")
    return 0 if public_summary["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
