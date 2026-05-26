#!/usr/bin/env python3
"""Small user-facing command hub for ClaimContractBench.

The release keeps individual scripts for auditability. This wrapper gives new
users one memorable entry point without adding third-party dependencies.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import shutil
import subprocess
import sys


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

TEMPLATE_ADMISSION_HEADER = [
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


def default_root() -> Path:
    return Path(__file__).resolve().parents[1]


def resolve(root: Path, value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = root / path
    return path.resolve()


def run(root: Path, args: list[str]) -> int:
    result = subprocess.run(args, cwd=root)
    return result.returncode


def script(root: Path, name: str) -> str:
    return str(root / "src" / name)


def command_doctor(args: argparse.Namespace) -> int:
    root = resolve(Path.cwd(), args.root)
    print("ClaimContractBench doctor")
    print(f"root: {root}")
    print("")
    sys.stdout.flush()
    code = run(root, [sys.executable, script(root, "validate_release_surface.py")])
    if code != 0:
        print("")
        print("Next step: run from the release root, or pass --root /path/to/release.")
        return code
    print("")
    print("Ready.")
    print("Next useful commands:")
    print("- python3 src/claimcontractbench.py smoke")
    print("- python3 src/claimcontractbench.py templates")
    print("- python3 src/claimcontractbench.py init-packet --output claim_packets/my_claim_packet.csv")
    print("- python3 src/claimcontractbench.py admission-guide")
    return 0


def command_smoke(args: argparse.Namespace) -> int:
    root = resolve(Path.cwd(), args.root)
    return run(root, [sys.executable, script(root, "run_release_smoke_suite.py"), "--root", str(root)])


def command_review(args: argparse.Namespace) -> int:
    root = resolve(Path.cwd(), args.root)
    command = [
        sys.executable,
        script(root, "run_llm_claim_review_packet.py"),
        "--root",
        str(root),
        "--input",
        args.input,
        "--output",
        args.output,
    ]
    return run(root, command)


def command_admit_template(args: argparse.Namespace) -> int:
    root = resolve(Path.cwd(), args.root)
    command = [
        sys.executable,
        script(root, "run_claim_template_admission.py"),
        "--root",
        str(root),
        "--cases",
        args.input,
        "--output",
        args.output,
    ]
    return run(root, command)


def command_init_packet(args: argparse.Namespace) -> int:
    root = resolve(Path.cwd(), args.root)
    output = resolve(root, args.output)
    if output.exists() and not args.force:
        print("FAIL init packet")
        print(f"output already exists: {output}")
        print("Use --force to overwrite.")
        return 1
    output.parent.mkdir(parents=True, exist_ok=True)
    if args.with_example:
        source = root / "artifact" / "llm_claim_review_packet_template_20260527.csv"
        shutil.copy2(source, output)
    else:
        with output.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(PACKET_HEADER)
    print("PASS init packet")
    print(f"output: {output}")
    print("")
    print("Send this CSV header to your LLM and ask it to return plain CSV only.")
    print("The default claim_packets/ folder is ignored by git.")
    print("Then run:")
    print(f"python3 src/claimcontractbench.py review --input {output}")
    return 0


def command_init_template(args: argparse.Namespace) -> int:
    root = resolve(Path.cwd(), args.root)
    output = resolve(root, args.output)
    if output.exists() and not args.force:
        print("FAIL init template")
        print(f"output already exists: {output}")
        print("Use --force to overwrite.")
        return 1
    output.parent.mkdir(parents=True, exist_ok=True)
    if args.blank:
        with output.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(TEMPLATE_ADMISSION_HEADER)
    else:
        source = root / "artifact" / "template_admission_packet_template_20260527.csv"
        shutil.copy2(source, output)
    print("PASS init template")
    print(f"output: {output}")
    print("")
    print("Ask your LLM to fill or revise this typed template-admission row.")
    print("Then run:")
    print(f"python3 src/claimcontractbench.py admit-template --input {output}")
    return 0


def command_admission_guide(args: argparse.Namespace) -> int:
    root = resolve(Path.cwd(), args.root)
    guide = root / "artifact" / "TEMPLATE_ADMISSION_QUICKSTART_20260527.md"
    print("Template admission path")
    print("")
    print("Use this when review returns NEEDS_TEMPLATE_ADMISSION.")
    print("")
    print("1. Create a draft template row:")
    print("   python3 src/claimcontractbench.py init-template --output claim_packets/my_template_admission.csv")
    print("2. Ask an LLM to fill the typed fields described in:")
    print(f"   {guide}")
    print("3. Check the row:")
    print("   python3 src/claimcontractbench.py admit-template --input claim_packets/my_template_admission.csv")
    print("")
    print("Required contract fields:")
    for field in [
        "evidence_unit",
        "claim_template",
        "G_binding",
        "Q_binding",
        "U_binding",
        "action_mapping",
        "preorder_relation",
        "forbidden_claim",
        "visual_or_case_anchor",
        "boundary_note",
    ]:
        print(f"- {field}")
    print("")
    print("If these fields cannot be supplied, keep the row as a boundary probe or reject it.")
    return 0


def command_templates(args: argparse.Namespace) -> int:
    root = resolve(Path.cwd(), args.root)
    path = root / "artifact" / "claim_template_admission_cases_20260521.csv"
    try:
        with path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
    except OSError as exc:
        print("FAIL templates")
        print(f"could not read template cases: {exc}")
        return 1
    print("Registered template shortlist")
    print("")
    print("| template_id | level | action | use boundary | forbidden claim |")
    print("| --- | --- | --- | --- | --- |")
    for row in rows:
        template_id = row.get("template_id", "")
        level = row.get("expected_level", "")
        action = row.get("action_mapping", "")
        boundary = row.get("boundary_note", "")
        forbidden = row.get("forbidden_claim", "")
        print(
            "| "
            + " | ".join(
                [
                    template_id,
                    level,
                    action,
                    boundary.replace("|", "/"),
                    forbidden.replace("|", "/"),
                ]
            )
            + " |"
        )
    print("")
    print("Rule of thumb: when uncertain, use NEEDS_TEMPLATE_ADMISSION instead of CALL_REGISTERED_TEMPLATE.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="One-entry ClaimContractBench command hub.",
        epilog=(
            "Typical path: doctor -> smoke -> init-packet -> ask an LLM to fill "
            "the packet -> review."
        ),
    )
    parser.add_argument("--root", default=str(default_root()), help="Release root.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_subcommand_root(subparser: argparse.ArgumentParser) -> None:
        subparser.add_argument(
            "--root",
            default=argparse.SUPPRESS,
            help="Release root. May be placed before or after the subcommand.",
        )

    doctor = subparsers.add_parser("doctor", help="Check that the release root is usable.")
    add_subcommand_root(doctor)
    doctor.set_defaults(func=command_doctor)

    smoke = subparsers.add_parser("smoke", help="Run positive and fail-closed smoke checks.")
    add_subcommand_root(smoke)
    smoke.set_defaults(func=command_smoke)

    templates = subparsers.add_parser("templates", help="Print registered template boundaries.")
    add_subcommand_root(templates)
    templates.set_defaults(func=command_templates)

    admission_guide = subparsers.add_parser(
        "admission-guide",
        help="Explain what to do when no registered template matches.",
    )
    add_subcommand_root(admission_guide)
    admission_guide.set_defaults(func=command_admission_guide)

    init_packet = subparsers.add_parser("init-packet", help="Create a CSV packet skeleton.")
    add_subcommand_root(init_packet)
    init_packet.add_argument("--output", required=True, help="CSV path to create.")
    init_packet.add_argument("--force", action="store_true", help="Overwrite the output if it exists.")
    init_packet.add_argument(
        "--with-example",
        action="store_true",
        help="Copy the release example packet instead of writing a blank header.",
    )
    init_packet.set_defaults(func=command_init_packet)

    init_template = subparsers.add_parser("init-template", help="Create a template-admission CSV.")
    add_subcommand_root(init_template)
    init_template.add_argument("--output", required=True, help="CSV path to create.")
    init_template.add_argument("--force", action="store_true", help="Overwrite the output if it exists.")
    init_template.add_argument(
        "--blank",
        action="store_true",
        help="Write only the header instead of copying the boundary-probe example.",
    )
    init_template.set_defaults(func=command_init_template)

    review = subparsers.add_parser("review", help="Review an LLM-produced claim packet.")
    add_subcommand_root(review)
    review.add_argument("--input", required=True, help="Input CSV packet.")
    review.add_argument("--output", default="reports/my_claim_packet", help="Report output directory.")
    review.set_defaults(func=command_review)

    admit_template = subparsers.add_parser("admit-template", help="Check a template-admission CSV.")
    add_subcommand_root(admit_template)
    admit_template.add_argument("--input", required=True, help="Input template-admission CSV.")
    admit_template.add_argument(
        "--output",
        default="reports/my_template_admission",
        help="Report output directory.",
    )
    admit_template.set_defaults(func=command_admit_template)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
