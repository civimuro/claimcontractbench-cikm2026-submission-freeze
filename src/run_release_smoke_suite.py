#!/usr/bin/env python3
"""Run the first-inspection ClaimContractBench release smoke suite.

This script is intentionally standard-library only. It is meant for local
reviewers and GitHub Actions: one command should prove that the public release
surface validates, the projection demo runs, the LLM packet happy path runs,
and critical bad packets fail closed.
"""

from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path
import subprocess
import sys
import tempfile


PACKET_HEADER = [
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run ClaimContractBench release smoke and fail-closed checks."
    )
    parser.add_argument("--root", default=".", help="Release root. Default: current directory.")
    return parser.parse_args()


def run_command(
    label: str,
    root: Path,
    args: list[str],
    expected_returncode: int = 0,
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(
        args,
        cwd=root,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if result.returncode != expected_returncode:
        print(f"FAIL {label}")
        print(f"expected_returncode: {expected_returncode}")
        print(f"actual_returncode: {result.returncode}")
        print(result.stdout)
        raise SystemExit(1)
    print(f"PASS {label}")
    return result


def write_packet(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=PACKET_HEADER)
        writer.writeheader()
        writer.writerows(rows)


def assert_contains(label: str, text: str, needle: str) -> None:
    if needle not in text:
        print(f"FAIL {label}")
        print(f"missing expected text: {needle}")
        print(text)
        raise SystemExit(1)


def assert_missing(path: Path, label: str) -> None:
    if path.exists():
        print(f"FAIL {label}")
        print(f"unexpected path exists: {path}")
        raise SystemExit(1)


def write_reference_realpaper_adjudication(root: Path, path: Path) -> None:
    reference = root / "artifact" / "real_paper_review_reference_outcomes_v318b_20260606.csv"
    header = [
        "row_id",
        "source_support_status",
        "claim_role",
        "reportability_gate",
        "candidate_release_safe_yes_no",
        "display_action",
        "repair_suggestion_required_yes_no",
        "suggested_rewrite",
        "reason_code",
        "rationale",
        "confidence_1_to_5",
    ]
    with reference.open(newline="", encoding="utf-8") as handle:
        reference_rows = list(csv.DictReader(handle))
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=header)
        writer.writeheader()
        for row in reference_rows:
            writer.writerow(
                {
                    "row_id": row["row_id"],
                    "source_support_status": "directly_supported"
                    if row["reference_candidate_release_safe"] == "yes"
                    else "partially_supported",
                    "claim_role": "primary_result_claim",
                    "reportability_gate": row["reference_reportability_gate"],
                    "candidate_release_safe_yes_no": row["reference_candidate_release_safe"],
                    "display_action": row["reference_display_action"],
                    "repair_suggestion_required_yes_no": "yes"
                    if row["reference_suggested_rewrite"]
                    else "no",
                    "suggested_rewrite": row["reference_suggested_rewrite"],
                    "reason_code": row["reference_reason_code"],
                    "rationale": "release smoke scoring fixture",
                    "confidence_1_to_5": "5",
                }
            )


def run_negative_packets(root: Path, temp_root: Path) -> None:
    cases = [
        (
            "unknown template fails packet",
            "unknown_template.csv",
            [
                {
                    "packet_id": "NEG-001",
                    "source_title": "Example",
                    "source_section": "Results",
                    "submitted_claim": "A bounded empirical claim.",
                    "intended_use": "paper result",
                    "route_label": "CALL_REGISTERED_TEMPLATE",
                    "template_id": "CTA-DOES-NOT-EXIST",
                    "evidence_pointer": "table 1",
                    "llm_reason": "unknown template should not be accepted",
                    "human_check_required": "yes",
                }
            ],
            1,
            "rejected_unknown_template: 1",
        ),
        (
            "non-call template id fails packet",
            "non_call_template.csv",
            [
                {
                    "packet_id": "NEG-002",
                    "source_title": "Example",
                    "source_section": "Results",
                    "submitted_claim": "A relevant but unsupported empirical claim.",
                    "intended_use": "paper result",
                    "route_label": "NEEDS_TEMPLATE_ADMISSION",
                    "template_id": "CTA-CORE-01",
                    "evidence_pointer": "table 1",
                    "llm_reason": "non-call rows must not name templates",
                    "human_check_required": "yes",
                }
            ],
            1,
            "checks_failed: 1",
        ),
        (
            "duplicate packet id fails packet",
            "duplicate_packet_id.csv",
            [
                {
                    "packet_id": "NEG-003",
                    "source_title": "Example",
                    "source_section": "Results",
                    "submitted_claim": "A relevant but unsupported empirical claim.",
                    "intended_use": "paper result",
                    "route_label": "NEEDS_TEMPLATE_ADMISSION",
                    "template_id": "",
                    "evidence_pointer": "table 1",
                    "llm_reason": "duplicate one",
                    "human_check_required": "yes",
                },
                {
                    "packet_id": "NEG-003",
                    "source_title": "Example",
                    "source_section": "Results",
                    "submitted_claim": "Another relevant but unsupported empirical claim.",
                    "intended_use": "paper result",
                    "route_label": "NEEDS_TEMPLATE_ADMISSION",
                    "template_id": "",
                    "evidence_pointer": "table 2",
                    "llm_reason": "duplicate two",
                    "human_check_required": "yes",
                },
            ],
            1,
            "checks_failed: 1",
        ),
    ]

    runner = root / "src" / "run_llm_claim_review_packet.py"
    for label, filename, rows, expected_returncode, expected_text in cases:
        packet = temp_root / filename
        output = temp_root / f"out_{packet.stem}"
        write_packet(packet, rows)
        result = run_command(
            label,
            root,
            [
                sys.executable,
                str(runner),
                "--root",
                str(root),
                "--input",
                str(packet),
                "--output",
                str(output),
            ],
            expected_returncode=expected_returncode,
        )
        assert_contains(label, result.stdout, expected_text)

    private_marker = "/" + "Users/example/private-note.md"
    private_packet = temp_root / "private_marker.csv"
    private_output = temp_root / "out_private_marker"
    write_packet(
        private_packet,
        [
            {
                "packet_id": "NEG-004",
                "source_title": "Example",
                "source_section": "Results",
                "submitted_claim": f"This claim came from {private_marker}.",
                "intended_use": "paper result",
                "route_label": "NEEDS_TEMPLATE_ADMISSION",
                "template_id": "",
                "evidence_pointer": private_marker,
                "llm_reason": "private marker should suppress reports",
                "human_check_required": "yes",
            }
        ],
    )
    result = run_command(
        "private marker suppresses reports",
        root,
        [
            sys.executable,
            str(runner),
            "--root",
            str(root),
            "--input",
            str(private_packet),
            "--output",
            str(private_output),
        ],
        expected_returncode=1,
    )
    assert_contains("private marker suppresses reports", result.stdout, "outputs: suppressed")
    assert_missing(private_output, "private marker suppresses reports")

    realpaper_reference = root / "artifact" / "real_paper_review_reference_outcomes_v318b_20260606.csv"
    realpaper_bad = temp_root / "realpaper_duplicate_adjudication.csv"
    with realpaper_reference.open(newline="", encoding="utf-8") as handle:
        reference_rows = list(csv.DictReader(handle))
    adjudication_header = [
        "row_id",
        "source_support_status",
        "claim_role",
        "reportability_gate",
        "candidate_release_safe_yes_no",
        "display_action",
        "repair_suggestion_required_yes_no",
        "suggested_rewrite",
        "reason_code",
        "rationale",
        "confidence_1_to_5",
    ]
    adjudication_rows: list[dict[str, str]] = []
    for row in reference_rows:
        adjudication_rows.append(
            {
                "row_id": row["row_id"],
                "source_support_status": "directly_supported",
                "claim_role": "primary_result_claim",
                "reportability_gate": row["reference_reportability_gate"],
                "candidate_release_safe_yes_no": row["reference_candidate_release_safe"],
                "display_action": row["reference_display_action"],
                "repair_suggestion_required_yes_no": "yes"
                if row["reference_suggested_rewrite"]
                else "no",
                "suggested_rewrite": row["reference_suggested_rewrite"],
                "reason_code": row["reference_reason_code"],
                "rationale": "smoke negative fixture",
                "confidence_1_to_5": "5",
            }
        )
    adjudication_rows[-1]["row_id"] = adjudication_rows[0]["row_id"]
    with realpaper_bad.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=adjudication_header)
        writer.writeheader()
        writer.writerows(adjudication_rows)
    result = run_command(
        "duplicate real-paper adjudication row fails packet",
        root,
        [
            sys.executable,
            "src/run_real_paper_review_demo.py",
            "--adjudication",
            str(realpaper_bad),
            "--output",
            str(temp_root / "out_realpaper_duplicate_adjudication"),
        ],
        expected_returncode=1,
    )
    assert_contains(
        "duplicate real-paper adjudication row fails packet",
        result.stdout,
        "RP-008 user row coverage",
    )


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"FAIL release smoke suite")
        print(f"root is not a directory: {root}")
        return 2

    with tempfile.TemporaryDirectory(prefix="claimcontractbench_release_smoke_") as tmp:
        temp_root = Path(tmp)
        run_command(
            "release surface validation",
            root,
            [sys.executable, "src/validate_release_surface.py"],
        )
        run_command(
            "projection smoke runner",
            root,
            [
                sys.executable,
                "src/run_projection_smoke.py",
                "--write-generated",
                str(temp_root / "projection_smoke_generated.csv"),
            ],
        )
        run_command(
            "LLM claim review happy path",
            root,
            [
                sys.executable,
                "src/run_llm_claim_review_packet.py",
                "--output",
                str(temp_root / "llm_happy_path"),
            ],
        )
        run_command(
            "template admission boundary-probe example",
            root,
            [
                sys.executable,
                "src/run_claim_template_admission.py",
                "--cases",
                "artifact/template_admission_packet_template_20260527.csv",
                "--output",
                str(temp_root / "template_admission_probe"),
            ],
        )
        realpaper_demo = run_command(
            "three-family real-paper review demo",
            root,
            [
                sys.executable,
                "src/run_real_paper_review_demo.py",
                "--output",
                str(temp_root / "real_paper_review_demo"),
            ],
        )
        assert_contains(
            "three-family real-paper review demo",
            realpaper_demo.stdout,
            "rows: 72",
        )
        assert_contains(
            "three-family real-paper review demo",
            realpaper_demo.stdout,
            "conservative_unsafe_false_releases: 3",
        )
        human_trial = run_command(
            "human trial path",
            root,
            [
                sys.executable,
                "src/claimcontractbench.py",
                "try-human",
                "--output",
                str(temp_root / "human_trial"),
            ],
        )
        assert_contains("human trial path", human_trial.stdout, "ClaimContractBench human trial")
        assert_contains("human trial path", human_trial.stdout, "Supported trial families:")
        if not (temp_root / "human_trial" / "real_paper_review_demo_report.md").exists():
            print("FAIL human trial path")
            print("missing human trial report")
            raise SystemExit(1)

        llm_trial_dir = temp_root / "llm_trial"
        llm_trial = run_command(
            "LLM trial packet path",
            root,
            [
                sys.executable,
                "src/claimcontractbench.py",
                "try-llm",
                "--output",
                str(llm_trial_dir),
            ],
        )
        assert_contains("LLM trial packet path", llm_trial.stdout, "PASS LLM trial packet")
        for filename in [
            "01_candidate_claims.csv",
            "02_template_cards.csv",
            "03_llm_prompt.md",
            "README_FOR_LLM.md",
        ]:
            if not (llm_trial_dir / filename).exists():
                print("FAIL LLM trial packet path")
                print(f"missing LLM trial file: {filename}")
                raise SystemExit(1)

        adjudication = temp_root / "valid_realpaper_adjudication.csv"
        write_reference_realpaper_adjudication(root, adjudication)
        scored_llm_trial = run_command(
            "LLM trial scoring path",
            root,
            [
                sys.executable,
                "src/claimcontractbench.py",
                "try-llm",
                "--output",
                str(temp_root / "llm_trial_scored"),
                "--adjudication",
                str(adjudication),
            ],
        )
        assert_contains("LLM trial scoring path", scored_llm_trial.stdout, "user_candidate_safety_accuracy: 1.000")
        assert_contains("LLM trial scoring path", scored_llm_trial.stdout, "user_unsafe_false_releases: 0")

        agent_guide = run_command(
            "one-shot agent guide",
            root,
            [
                sys.executable,
                "src/claimcontractbench.py",
                "agent-guide",
            ],
        )
        assert_contains("one-shot agent guide", agent_guide.stdout, "One-shot AI-agent review path")
        assert_contains(
            "one-shot agent guide",
            agent_guide.stdout,
            "AGENT_ONE_SHOT_REVIEW_GUIDE_20260527.md",
        )
        human_guide = run_command(
            "human reviewer guide",
            root,
            [
                sys.executable,
                "src/claimcontractbench.py",
                "human-guide",
            ],
        )
        assert_contains("human reviewer guide", human_guide.stdout, "Human reviewer path")
        assert_contains(
            "human reviewer guide",
            human_guide.stdout,
            "docs/HUMAN_REVIEWER_GUIDE.md",
        )
        reviewer_checklist = run_command(
            "reviewer verification checklist",
            root,
            [
                sys.executable,
                "src/claimcontractbench.py",
                "reviewer-checklist",
            ],
        )
        assert_contains(
            "reviewer verification checklist",
            reviewer_checklist.stdout,
            "Reviewer verification checklist",
        )
        assert_contains(
            "reviewer verification checklist",
            reviewer_checklist.stdout,
            "docs/REVIEWER_CHECKLIST.md",
        )
        claim_id_guide = run_command(
            "claim identification guide",
            root,
            [
                sys.executable,
                "src/claimcontractbench.py",
                "claim-id-guide",
            ],
        )
        assert_contains(
            "claim identification guide",
            claim_id_guide.stdout,
            "checks supplied candidate claims",
        )
        feedback_output = temp_root / "feedback" / "my_feedback_report.md"
        run_command(
            "optional feedback scaffold",
            root,
            [
                sys.executable,
                "src/claimcontractbench.py",
                "init-feedback",
                "--output",
                str(feedback_output),
            ],
        )
        if not feedback_output.exists():
            print("FAIL optional feedback scaffold")
            print(f"missing feedback output: {feedback_output}")
            raise SystemExit(1)
        run_negative_packets(root, temp_root)

    print("PASS release smoke suite")
    print("positive_checks: 13")
    print("negative_fail_closed_checks: 5")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
