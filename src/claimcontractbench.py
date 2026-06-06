#!/usr/bin/env python3
"""Small user-facing command hub for ClaimContractBench.

The release keeps individual scripts for auditability. This wrapper gives new
users one memorable entry point without adding third-party dependencies.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import re
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

FEEDBACK_PRIVATE_PATTERNS = (
    ("absolute local user path", re.compile(r"/Users/[A-Za-z0-9._-]+")),
    ("remote connector host", re.compile(r"\bconnect\.[A-Za-z0-9.-]+\b")),
    (
        "credential-like text",
        re.compile(
            r"\b(?:password|passwd|token|secret|credential|api[_-]?key)\b\s*[:=]\s*"
            r"['\"]?[A-Za-z0-9_./+=-]{8,}",
            re.IGNORECASE,
        ),
    ),
    (
        "confidential inclusion flag",
        re.compile(r"confidential (?:text|material).*:\s*(?:yes|included)", re.IGNORECASE),
    ),
    (
        "private review note flag",
        re.compile(r"private review notes?.*:\s*(?:yes|included)", re.IGNORECASE),
    ),
    (
        "raw data inclusion flag",
        re.compile(r"raw data.*:\s*(?:yes|included)", re.IGNORECASE),
    ),
)


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
    print("- python3 src/claimcontractbench.py reviewer-checklist")
    print("- python3 src/claimcontractbench.py human-guide")
    print("- python3 src/claimcontractbench.py templates")
    print("- python3 src/claimcontractbench.py realpaper-demo --output /tmp/claimcontractbench_realpaper_demo")
    print("- python3 src/claimcontractbench.py agent-guide")
    print("- python3 src/claimcontractbench.py init-packet --output claim_packets/my_claim_packet.csv")
    print("- python3 src/claimcontractbench.py admission-guide")
    print("- python3 src/claimcontractbench.py feedback-guide")
    return 0


def command_smoke(args: argparse.Namespace) -> int:
    root = resolve(Path.cwd(), args.root)
    return run(root, [sys.executable, script(root, "run_release_smoke_suite.py"), "--root", str(root)])


def command_human_guide(args: argparse.Namespace) -> int:
    print("Human reviewer path")
    print("")
    print("Use this path when you want to inspect the resource without an LLM.")
    print("Start with docs/REVIEWER_CHECKLIST.md for the canonical first-pass map.")
    print("")
    print("1. Verify that the checkout is a public-safe release surface:")
    print("   python3 src/claimcontractbench.py doctor")
    print("2. Run the first-inspection smoke suite:")
    print("   python3 src/claimcontractbench.py smoke")
    print("3. Inspect the registered claim templates:")
    print("   python3 src/claimcontractbench.py templates")
    print("4. Read by depth:")
    print("   10 min: docs/REVIEWER_CHECKLIST.md, docs/CONCEPTS.md, docs/BOUNDARIES.md")
    print("   30 min: docs/HUMAN_REVIEWER_GUIDE.md, docs/REPORT_INDEX.md, docs/EXAMPLE_OUTPUTS.md")
    print("   deep:   docs/DATA_AND_LICENSES.md, docs/REPRODUCIBILITY.md,")
    print("           docs/EVALUATION_SOURCE_INVENTORY.md, artifact/PUBLIC_RELEASE_CHECKLIST_20260527.md")
    print("")
    print("LLM-assisted packet drafting is optional. The deterministic checks are the")
    print("release boundary whether a packet is written by a human or drafted by an LLM.")
    print("")
    print("For the current three-family public-paper demo, run:")
    print("   python3 src/claimcontractbench.py realpaper-demo \\")
    print("     --output /tmp/claimcontractbench_realpaper_demo")
    return 0


def command_reviewer_checklist(args: argparse.Namespace) -> int:
    print("Reviewer verification checklist")
    print("")
    print("Use this path when you want to verify the artifact without treating it")
    print("as a paper decision system.")
    print("")
    print("Ten-minute check:")
    print("  python3 src/claimcontractbench.py doctor")
    print("  python3 src/claimcontractbench.py smoke")
    print("")
    print("Then inspect by depth:")
    print("  10 min: docs/REVIEWER_CHECKLIST.md, docs/CONCEPTS.md, docs/BOUNDARIES.md")
    print("  30 min: docs/HUMAN_REVIEWER_GUIDE.md, docs/REPORT_INDEX.md, docs/EXAMPLE_OUTPUTS.md")
    print("  deep:   docs/DATA_AND_LICENSES.md, docs/REPRODUCIBILITY.md,")
    print("          docs/EVALUATION_SOURCE_INVENTORY.md, artifact/PUBLIC_RELEASE_CHECKLIST_20260527.md")
    print("")
    print("Good signals: public-safe manifest, fail-closed bad packets, exact")
    print("template boundaries, and explicit non-goals.")
    print("Red flags: accept/reject claims, autonomous full-paper review claims,")
    print("raw-data redistribution claims, or forced use of nearby templates.")
    print("")
    print("Three-family public-paper trial:")
    print("  python3 src/claimcontractbench.py realpaper-demo \\")
    print("    --output /tmp/claimcontractbench_realpaper_demo")
    return 0


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


def command_realpaper_demo(args: argparse.Namespace) -> int:
    root = resolve(Path.cwd(), args.root)
    command = [
        sys.executable,
        script(root, "run_real_paper_review_demo.py"),
        "--root",
        str(root),
        "--output",
        args.output,
    ]
    if args.adjudication:
        command.extend(["--adjudication", args.adjudication])
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
    print("For a new paper, set human_check_required=yes on every row, including")
    print("registered-template calls. Use no only for release-provided controls.")
    print("When uncertain, use NEEDS_TEMPLATE_ADMISSION instead of forcing a template.")
    print("Copy-paste prompt: artifact/LLM_ASSISTED_REVIEW_QUICKSTART_20260527.md")
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
    guide = "artifact/TEMPLATE_ADMISSION_QUICKSTART_20260527.md"
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


def command_agent_guide(args: argparse.Namespace) -> int:
    guide = "artifact/AGENT_ONE_SHOT_REVIEW_GUIDE_20260527.md"
    llm_guide = "artifact/LLM_ASSISTED_REVIEW_QUICKSTART_20260527.md"
    print("One-shot AI-agent review path")
    print("")
    print('User instruction this guide supports: "Use the tools in this repository to assist a review of this paper."')
    print("")
    print("Read:")
    print(f"  {guide}")
    print(f"  {llm_guide}")
    print("")
    print("Minimal local workflow:")
    print("  python3 src/claimcontractbench.py doctor")
    print("  python3 src/claimcontractbench.py smoke")
    print("  python3 src/claimcontractbench.py templates")
    print("  python3 src/claimcontractbench.py init-packet --output claim_packets/agent_claim_packet.csv")
    print("  # extract candidate empirical claims from the supplied paper into the packet")
    print("  python3 src/claimcontractbench.py review --input claim_packets/agent_claim_packet.csv --output reports/agent_claim_review")
    print("")
    print("For user-supplied papers, set human_check_required=yes for every extracted")
    print("row, including registered-template calls. Use no only for release controls.")
    print("Prefer NEEDS_TEMPLATE_ADMISSION over a near-but-not-exact template match.")
    print("")
    print("Stop or ask for input if no paper text/path is supplied, local commands cannot run,")
    print("or confidential text would need to be sent to an unapproved external model.")
    print("")
    print("Report claim-level actions, template gaps, out-of-scope rows, tool limits, and next actions.")
    return 0


def command_feedback_guide(args: argparse.Namespace) -> int:
    guide = "artifact/USER_EXPERIENCE_FEEDBACK_GUIDE_20260527.md"
    template = "artifact/user_experience_feedback_template_20260527.md"
    prompt = (
        "With your approval, I can write a public-safe ClaimContractBench "
        "usability feedback note using only command names, aggregate routing "
        "counts, non-confidential summaries, and paraphrased template gaps, "
        "excluding confidential paper text, private review notes, author "
        "identities, unpublished results, raw data, credentials, private links, "
        "and local paths."
    )
    print("Optional user-experience feedback path")
    print("")
    print("Human path:")
    print("  If you can share public-safe usage feedback, we would be grateful.")
    print("  Contact: civimuro@gmail.com")
    print("  Only do this when it does not violate CIKM, ACM, institutional,")
    print("  venue, or review-confidentiality rules. Active CIKM reviewers should")
    print("  use official review-system or program-committee channels instead.")
    print("")
    print("LLM/agent path:")
    print("  Show this exact prompt to the user first and generate feedback only")
    print("  after the user explicitly approves:")
    print(f"  {prompt}")
    print("")
    print("Create a local feedback draft:")
    print("  python3 src/claimcontractbench.py init-feedback --output feedback/my_feedback_report.md")
    print("Check a draft before sharing it publicly:")
    print("  python3 src/claimcontractbench.py check-feedback --input feedback/my_feedback_report.md")
    print("")
    print("Guide:")
    print(f"  {guide}")
    print("Minimal template:")
    print(f"  {template}")
    return 0


def command_init_feedback(args: argparse.Namespace) -> int:
    root = resolve(Path.cwd(), args.root)
    output = resolve(root, args.output)
    if output.exists() and not args.force:
        print("FAIL init feedback")
        print(f"output already exists: {output}")
        print("Use --force to overwrite.")
        return 1
    output.parent.mkdir(parents=True, exist_ok=True)
    source = root / "artifact" / "user_experience_feedback_template_20260527.md"
    shutil.copy2(source, output)
    print("PASS init feedback")
    print(f"output: {output}")
    print("")
    print("This report is optional and public-safe by default.")
    print("Do not put confidential paper text or private review notes in a public feedback report.")
    print("Before sharing publicly, run:")
    print(f"python3 src/claimcontractbench.py check-feedback --input {output}")
    return 0


def command_check_feedback(args: argparse.Namespace) -> int:
    root = resolve(Path.cwd(), args.root)
    path = resolve(root, args.input)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        print("FAIL feedback public-safety check")
        print(f"could not read feedback file: {exc}")
        return 1

    hits: list[str] = []
    for label, pattern in FEEDBACK_PRIVATE_PATTERNS:
        if pattern.search(text):
            hits.append(label)

    if hits:
        print("FAIL feedback public-safety check")
        print("Do not share this feedback publicly until the flagged material is removed.")
        print("hits:")
        for hit in hits:
            print(f"- {hit}")
        print("")
        print("Public feedback should use abstract task types, aggregate counts,")
        print("command names, and paraphrased template gaps rather than confidential")
        print("paper text, private review notes, raw data, local paths, or credentials.")
        return 1

    print("PASS feedback public-safety check")
    print("No obvious local paths, credential-like markers, or explicit confidential-material flags were found.")
    print("This is a heuristic check, not a guarantee. Re-read the report before public sharing.")
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
            "Typical human path: doctor -> smoke -> human-guide. "
            "Optional LLM path: templates -> init-packet -> review."
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

    human_guide = subparsers.add_parser(
        "human-guide",
        help="Explain the non-LLM reviewer inspection workflow.",
    )
    add_subcommand_root(human_guide)
    human_guide.set_defaults(func=command_human_guide)

    reviewer_checklist = subparsers.add_parser(
        "reviewer-checklist",
        help="Print the reviewer artifact verification checklist.",
    )
    add_subcommand_root(reviewer_checklist)
    reviewer_checklist.set_defaults(func=command_reviewer_checklist)

    templates = subparsers.add_parser("templates", help="Print registered template boundaries.")
    add_subcommand_root(templates)
    templates.set_defaults(func=command_templates)

    admission_guide = subparsers.add_parser(
        "admission-guide",
        help="Explain what to do when no registered template matches.",
    )
    add_subcommand_root(admission_guide)
    admission_guide.set_defaults(func=command_admission_guide)

    agent_guide = subparsers.add_parser(
        "agent-guide",
        help="Explain the one-shot AI-agent assisted review workflow.",
    )
    add_subcommand_root(agent_guide)
    agent_guide.set_defaults(func=command_agent_guide)

    feedback_guide = subparsers.add_parser(
        "feedback-guide",
        help="Explain the optional public-safe feedback path.",
    )
    add_subcommand_root(feedback_guide)
    feedback_guide.set_defaults(func=command_feedback_guide)

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

    init_feedback = subparsers.add_parser("init-feedback", help="Create a feedback Markdown template.")
    add_subcommand_root(init_feedback)
    init_feedback.add_argument("--output", required=True, help="Markdown path to create.")
    init_feedback.add_argument("--force", action="store_true", help="Overwrite the output if it exists.")
    init_feedback.set_defaults(func=command_init_feedback)

    check_feedback = subparsers.add_parser(
        "check-feedback",
        help="Heuristically check a feedback draft before public sharing.",
    )
    add_subcommand_root(check_feedback)
    check_feedback.add_argument("--input", required=True, help="Feedback Markdown path to check.")
    check_feedback.set_defaults(func=command_check_feedback)

    review = subparsers.add_parser("review", help="Review an LLM-produced claim packet.")
    add_subcommand_root(review)
    review.add_argument("--input", required=True, help="Input CSV packet.")
    review.add_argument("--output", default="reports/my_claim_packet", help="Report output directory.")
    review.set_defaults(func=command_review)

    realpaper_demo = subparsers.add_parser(
        "realpaper-demo",
        help="Run the three-family public-paper template review demo.",
    )
    add_subcommand_root(realpaper_demo)
    realpaper_demo.add_argument(
        "--adjudication",
        default="",
        help="Optional user/LLM adjudication CSV to score against the reference.",
    )
    realpaper_demo.add_argument(
        "--output",
        default="reports/real_paper_review_demo_20260606",
        help="Report output directory.",
    )
    realpaper_demo.set_defaults(func=command_realpaper_demo)

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
