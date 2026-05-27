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
from pathlib import Path
import shutil
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
    result = subprocess.run(
        args,
        cwd=root,
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

    if (root / "src" / "__pycache__").exists():
        shutil.rmtree(root / "src" / "__pycache__")

    print("PASS release smoke suite")
    print("positive_checks: 8")
    print("negative_fail_closed_checks: 4")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
