#!/usr/bin/env python3
"""Evaluate reviewer value on public-safe paper excerpt audit cases.

This benchmark is stricter than the paper-claim paraphrase benchmark because
each row is anchored to a short source excerpt and a reviewer-facing claim
decision. The default run uses the human gold route as an oracle front end; it
therefore tests the deterministic claim-governance layer, not autonomous paper
reading. A separate prediction packet is emitted for LLM or human front-end
evaluation.
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter
import html
import importlib.util
import json
from pathlib import Path
import re


FILES = {
    "schema": "artifact/paper_excerpt_reviewer_value_schema_20260521.json",
    "cases": "artifact/paper_excerpt_reviewer_value_cases_20260521.csv",
    "sources": "artifact/paper_claim_gold_benchmark_sources_20260521.csv",
    "template_schema": "artifact/claim_template_admission_schema_20260521.json",
    "template_cases": "artifact/claim_template_admission_cases_20260521.csv",
    "casebook": "data/claim_passport_casebook_20260519.csv",
    "nab_visual": "data/nab_adapter_visual_passport_rows_20260519.csv",
}

EXPECTED_CASE_COLUMNS = [
    "excerpt_id",
    "paper_id",
    "source_family",
    "case_role",
    "excerpt_index",
    "source_title",
    "primary_source",
    "excerpt_kind",
    "source_micro_excerpt",
    "micro_excerpt_word_count",
    "candidate_claim",
    "human_gold_route_label",
    "human_gold_template_id",
    "post_admission_gold_action",
    "current_expected_tool_decision",
    "current_expected_reviewer_action",
    "overclaim_hazard",
    "reviewer_comment_gold",
    "selection_rationale",
    "gold_label_basis",
]

ROUTE_LABELS = {
    "CALL_REGISTERED_TEMPLATE",
    "NEEDS_TEMPLATE_ADMISSION",
    "OUT_OF_SCOPE_DO_NOT_CALL",
}

TOOL_DECISIONS = {
    "ACCEPT_LICENSED",
    "REWRITE_TO_LICENSED",
    "SUPPRESS_BOTTOM",
    "SUPPORT_ONLY_REWRITE",
    "REJECT_PATCHWORK",
    "REJECT_UNKNOWN_TEMPLATE",
    "OPEN_ADMISSION_TICKET",
    "DO_NOT_CALL_CLAIM_RUNNER",
}

REVIEWER_ACTIONS = {
    "ACCEPT",
    "REWRITE",
    "WEAKEN",
    "SUPPORT_ONLY",
    "SUPPRESS",
    "REJECT",
    "ADMISSION_REQUIRED",
    "OUT_OF_SCOPE_STOP",
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

REGISTERED_TEMPLATE_PATTERNS = [
    ("CTA-CORE-01", "source-isotonic supports the RAC1P=1 slice claim"),
    ("CTA-CORE-02", "Oracle target isotonic is the same-regime winner"),
    ("CTA-CORE-03", "RAC1P=6 slice is fully reportable"),
    ("CTA-CORE-04", "global ECE winner transfers unchanged"),
    ("CTA-CORE-05", "raw method is calibrated on the hard-negative slice"),
    ("CTA-NAB-01", "null detector is effective on NAB overall"),
    ("CTA-AI4I-01", "AI4I predictive maintenance results support"),
    ("CTA-UNKNOWN-01", "unregistered benchmark claim should be accepted"),
]

OUT_OF_SCOPE_PATTERNS = [
    "legally compliant",
    "commercial downstream use",
    "hidden privacy violation",
    "clinical or operational deployment",
    "deployment readiness",
    "training or selection bug",
    "future adaptive attacks",
    "human-like reasoning",
    "human-like internal representation",
    "public deployment",
    "high-risk applications",
    "clinical triage",
    "ethically acceptable",
    "downstream decision",
    "biologically plausible",
    "venue should",
    "unrestricted ai reviewing",
    "paper should be accepted",
    "safe for every",
    "legal compliance",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate paper-excerpt reviewer-value claim audit cases."
    )
    parser.add_argument("--root", default=".", help="Workspace root. Default: current directory.")
    parser.add_argument(
        "--output",
        default="reports/paper_excerpt_reviewer_value_benchmark_20260521",
        help="Report output directory. Relative paths are resolved under root.",
    )
    parser.add_argument(
        "--predictions",
        default="",
        help="Optional front-end prediction CSV to score against human gold routes.",
    )
    parser.add_argument(
        "--baseline",
        choices=["none", "text_rules"],
        default="none",
        help="Optional transparent route baseline. Ignored when --predictions is supplied.",
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


def resolve(root: Path, value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = root / path
    return path.resolve()


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


def short(text: str, limit: int = 150) -> str:
    text = " ".join((text or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "..."


def normalize(text: str) -> str:
    return " ".join((text or "").lower().split())


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


def load_templates(root: Path, intake_runner):
    schema = json.loads((root / FILES["template_schema"]).read_text(encoding="utf-8"))
    template_cases, _ = read_csv(root / FILES["template_cases"])
    casebook, _ = read_csv(root / FILES["casebook"])
    nab_visual, _ = read_csv(root / FILES["nab_visual"])
    templates = intake_runner.build_template_rows(
        template_cases,
        list(schema.get("critical_fields_for_admission", [])),
    )
    return (
        templates,
        {row.get("event_id", ""): row for row in casebook},
        {row.get("display_id", ""): row for row in nab_visual},
    )


def reviewer_action_from_intake(decision: str, template_id: str, templates: dict[str, dict[str, str]]) -> str:
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


def decide_tool(
    row: dict[str, str],
    route_label: str,
    template_id: str,
    intake_runner,
    templates: dict[str, dict[str, str]],
    casebook_by_id: dict[str, dict[str, str]],
    nab_by_id: dict[str, dict[str, str]],
) -> dict[str, str]:
    if route_label == "CALL_REGISTERED_TEMPLATE":
        decision = intake_runner.decide_intake(
            {
                "intake_id": row["excerpt_id"],
                "template_id": template_id,
                "submitted_claim": row["candidate_claim"],
                "expected_decision": "",
            },
            templates,
            casebook_by_id,
            nab_by_id,
        )
        tool_decision = decision["decision"]
        return {
            "tool_decision": tool_decision,
            "reviewer_action": reviewer_action_from_intake(tool_decision, template_id, templates),
            "recommended_output": decision["recommended_output"],
            "reviewer_message": decision["explanation"],
            "source_anchor": decision["source_anchor"],
        }

    if route_label == "NEEDS_TEMPLATE_ADMISSION":
        return {
            "tool_decision": "OPEN_ADMISSION_TICKET",
            "reviewer_action": "ADMISSION_REQUIRED",
            "recommended_output": "unsupported_template",
            "reviewer_message": (
                "This excerpt contains a relevant empirical claim, but the current "
                "registry has no admitted template for this paper family. Open an "
                "adapter-admission ticket before accepting or weakening the claim."
            ),
            "source_anchor": "",
        }

    if route_label == "OUT_OF_SCOPE_DO_NOT_CALL":
        return {
            "tool_decision": "DO_NOT_CALL_CLAIM_RUNNER",
            "reviewer_action": "OUT_OF_SCOPE_STOP",
            "recommended_output": "bottom_T",
            "reviewer_message": (
                "Do not call the metric-to-claim runner. The excerpt asks for legal, "
                "policy, ethics, deployment, code, mechanistic, or paper-level judgment."
            ),
            "source_anchor": "",
        }

    return {
        "tool_decision": "DO_NOT_CALL_CLAIM_RUNNER",
        "reviewer_action": "OUT_OF_SCOPE_STOP",
        "recommended_output": "bottom_T",
        "reviewer_message": "Invalid route label; fail closed.",
        "source_anchor": "",
    }


def text_rule_predict(row: dict[str, str]) -> tuple[str, str, str]:
    text = normalize(row["candidate_claim"] + " " + row["source_micro_excerpt"])
    for template_id, pattern in REGISTERED_TEMPLATE_PATTERNS:
        if normalize(pattern) in text:
            return "CALL_REGISTERED_TEMPLATE", template_id, "registered phrase match"
    for pattern in OUT_OF_SCOPE_PATTERNS:
        if normalize(pattern) in text:
            return "OUT_OF_SCOPE_DO_NOT_CALL", "", f"out-of-scope phrase: {pattern}"
    return "NEEDS_TEMPLATE_ADMISSION", "", "empirical excerpt without registered template phrase"


def build_prediction_packet(cases: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        {
            "excerpt_id": row["excerpt_id"],
            "paper_id": row["paper_id"],
            "source_family": row["source_family"],
            "source_title": row["source_title"],
            "source_micro_excerpt": row["source_micro_excerpt"],
            "candidate_claim": row["candidate_claim"],
            "predicted_claim_span": "",
            "predicted_route_label": "",
            "predicted_template_id": "",
            "prediction_notes": "",
        }
        for row in cases
    ]


def load_predictions(
    root: Path,
    cases: list[dict[str, str]],
    prediction_path: str,
    baseline: str,
) -> tuple[str, list[dict[str, str]]]:
    if prediction_path:
        rows, _ = read_csv(resolve(root, prediction_path))
        return "external_predictions", rows
    predictions = []
    if baseline == "text_rules":
        for row in cases:
            route, template_id, note = text_rule_predict(row)
            predictions.append(
                {
                    "excerpt_id": row["excerpt_id"],
                    "predicted_claim_span": row["candidate_claim"],
                    "predicted_route_label": route,
                    "predicted_template_id": template_id,
                    "prediction_notes": note,
                }
            )
        return "text_rules_baseline", predictions
    for row in cases:
        predictions.append(
            {
                "excerpt_id": row["excerpt_id"],
                "predicted_claim_span": row["candidate_claim"],
                "predicted_route_label": row["human_gold_route_label"],
                "predicted_template_id": row["human_gold_template_id"],
                "prediction_notes": "human gold oracle front end; not autonomous extraction evidence",
            }
        )
    return "human_gold_oracle", predictions


def safe_rate(numerator: int, denominator: int) -> str:
    if denominator == 0:
        return "0.000"
    return f"{numerator / denominator:.3f}"


def evaluate(
    cases: list[dict[str, str]],
    predictions: list[dict[str, str]],
    front_end_mode: str,
    intake_runner,
    templates: dict[str, dict[str, str]],
    casebook_by_id: dict[str, dict[str, str]],
    nab_by_id: dict[str, dict[str, str]],
) -> tuple[dict[str, object], list[dict[str, str]], list[dict[str, str]]]:
    case_by_id = {row["excerpt_id"]: row for row in cases}
    prediction_ids = [row.get("excerpt_id", "") for row in predictions]
    prediction_by_id = {row.get("excerpt_id", ""): row for row in predictions}
    duplicate_predictions = sorted(
        excerpt_id for excerpt_id, count in Counter(prediction_ids).items() if count > 1
    )
    missing_predictions = sorted(set(case_by_id) - set(prediction_by_id))
    extra_predictions = sorted(set(prediction_by_id) - set(case_by_id))

    decision_rows: list[dict[str, str]] = []
    route_match_count = 0
    template_match_count = 0
    registered_count = 0
    tool_decision_match_count = 0
    reviewer_action_match_count = 0
    unsafe_release = []
    false_call_out_of_scope = []
    false_stop_relevant = []
    false_admission_out_of_scope = []
    comment_ready = 0
    route_confusion: Counter[tuple[str, str]] = Counter()

    for excerpt_id, row in case_by_id.items():
        prediction = prediction_by_id.get(excerpt_id, {})
        predicted_route = prediction.get("predicted_route_label", "")
        predicted_template = prediction.get("predicted_template_id", "")
        gold_route = row["human_gold_route_label"]
        gold_template = row["human_gold_template_id"]
        route_match = predicted_route == gold_route
        if route_match:
            route_match_count += 1
        if gold_route == "CALL_REGISTERED_TEMPLATE":
            registered_count += 1
            if predicted_template == gold_template:
                template_match_count += 1
        route_confusion[(gold_route, predicted_route)] += 1

        decision = decide_tool(
            row,
            predicted_route,
            predicted_template,
            intake_runner,
            templates,
            casebook_by_id,
            nab_by_id,
        )
        tool_match = decision["tool_decision"] == row["current_expected_tool_decision"]
        action_match = decision["reviewer_action"] == row["current_expected_reviewer_action"]
        if tool_match:
            tool_decision_match_count += 1
        if action_match:
            reviewer_action_match_count += 1

        if (
            gold_route in {"NEEDS_TEMPLATE_ADMISSION", "OUT_OF_SCOPE_DO_NOT_CALL"}
            and decision["tool_decision"] in {"ACCEPT_LICENSED", "REWRITE_TO_LICENSED", "SUPPORT_ONLY_REWRITE"}
        ):
            unsafe_release.append(excerpt_id)
        if gold_route == "OUT_OF_SCOPE_DO_NOT_CALL" and predicted_route == "CALL_REGISTERED_TEMPLATE":
            false_call_out_of_scope.append(excerpt_id)
        if gold_route == "OUT_OF_SCOPE_DO_NOT_CALL" and predicted_route == "NEEDS_TEMPLATE_ADMISSION":
            false_admission_out_of_scope.append(excerpt_id)
        if gold_route in {"CALL_REGISTERED_TEMPLATE", "NEEDS_TEMPLATE_ADMISSION"} and predicted_route == "OUT_OF_SCOPE_DO_NOT_CALL":
            false_stop_relevant.append(excerpt_id)
        if len(decision["reviewer_message"].strip()) >= 40 and len(row["reviewer_comment_gold"].strip()) >= 40:
            comment_ready += 1

        decision_rows.append(
            {
                "excerpt_id": excerpt_id,
                "paper_id": row["paper_id"],
                "source_family": row["source_family"],
                "case_role": row["case_role"],
                "source_title": row["source_title"],
                "source_micro_excerpt": row["source_micro_excerpt"],
                "candidate_claim": row["candidate_claim"],
                "gold_route_label": gold_route,
                "predicted_route_label": predicted_route,
                "route_match": "PASS" if route_match else "FAIL",
                "gold_template_id": gold_template,
                "predicted_template_id": predicted_template,
                "template_match_for_registered": "PASS"
                if gold_route != "CALL_REGISTERED_TEMPLATE" or predicted_template == gold_template
                else "FAIL",
                "tool_decision": decision["tool_decision"],
                "expected_tool_decision": row["current_expected_tool_decision"],
                "tool_decision_match": "PASS" if tool_match else "FAIL",
                "reviewer_action": decision["reviewer_action"],
                "expected_reviewer_action": row["current_expected_reviewer_action"],
                "reviewer_action_match": "PASS" if action_match else "FAIL",
                "recommended_output": decision["recommended_output"],
                "reviewer_message": decision["reviewer_message"],
                "gold_reviewer_comment": row["reviewer_comment_gold"],
                "overclaim_hazard": row["overclaim_hazard"],
                "prediction_notes": prediction.get("prediction_notes", ""),
            }
        )

    total = len(cases)
    summary = {
        "status": "PASS",
        "front_end_mode": front_end_mode,
        "excerpt_rows": total,
        "external_excerpt_rows": sum(1 for row in cases if row["case_role"] == "external_excerpt"),
        "registered_control_rows": registered_count,
        "source_papers": len({row["paper_id"] for row in cases if row["case_role"] == "external_excerpt"}),
        "source_families": len({row["source_family"] for row in cases}),
        "route_accuracy": safe_rate(route_match_count, total),
        "template_accuracy_on_registered": safe_rate(template_match_count, registered_count),
        "tool_decision_accuracy": safe_rate(tool_decision_match_count, total),
        "reviewer_action_accuracy": safe_rate(reviewer_action_match_count, total),
        "unsafe_release_rate": safe_rate(len(unsafe_release), total),
        "false_call_out_of_scope_count": len(false_call_out_of_scope),
        "false_admission_out_of_scope_count": len(false_admission_out_of_scope),
        "false_stop_relevant_count": len(false_stop_relevant),
        "comment_readiness_rate": safe_rate(comment_ready, total),
        "route_counts": dict(sorted(Counter(row["human_gold_route_label"] for row in cases).items())),
        "tool_decision_counts": dict(sorted(Counter(row["tool_decision"] for row in decision_rows).items())),
        "reviewer_action_counts": dict(sorted(Counter(row["reviewer_action"] for row in decision_rows).items())),
        "unsafe_release_ids": unsafe_release,
        "false_call_out_of_scope_ids": false_call_out_of_scope,
        "false_admission_out_of_scope_ids": false_admission_out_of_scope,
        "false_stop_relevant_ids": false_stop_relevant,
        "prediction_coverage_errors": {
            "duplicates": duplicate_predictions,
            "missing": missing_predictions,
            "extra": extra_predictions,
        },
        "autonomous_full_paper_review_supported": "no",
    }

    confusion_rows = [
        {
            "gold_route_label": gold,
            "predicted_route_label": predicted,
            "count": str(count),
        }
        for (gold, predicted), count in sorted(route_confusion.items())
    ]
    return summary, decision_rows, confusion_rows


def build_checks(
    cases: list[dict[str, str]],
    case_header: list[str],
    sources: list[dict[str, str]],
    summary: dict[str, object],
    decision_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    checks: list[dict[str, str]] = []
    source_ids = {row["paper_id"] for row in sources}
    duplicate_ids = sorted(
        excerpt_id for excerpt_id, count in Counter(row["excerpt_id"] for row in cases).items() if count > 1
    )
    add_check(
        checks,
        "PEV-01",
        "case schema and identity",
        case_header == EXPECTED_CASE_COLUMNS and not duplicate_ids,
        f"{len(cases)} rows with expected schema and unique ids",
        f"header={case_header}; expected={EXPECTED_CASE_COLUMNS}; duplicate_ids={duplicate_ids}",
    )
    add_check(
        checks,
        "PEV-02",
        "benchmark scale",
        len(cases) >= 80
        and summary["source_papers"] >= 24
        and summary["source_families"] >= 12
        and summary["registered_control_rows"] == 8,
        (
            f"rows={len(cases)}; source_papers={summary['source_papers']}; "
            f"families={summary['source_families']}; controls={summary['registered_control_rows']}"
        ),
        (
            f"insufficient scale: rows={len(cases)}; papers={summary['source_papers']}; "
            f"families={summary['source_families']}; controls={summary['registered_control_rows']}"
        ),
    )
    missing_sources = sorted({row["paper_id"] for row in cases} - source_ids)
    add_check(
        checks,
        "PEV-03",
        "source manifest join",
        not missing_sources,
        "all excerpt rows join to the source manifest",
        f"missing paper ids: {missing_sources}",
    )
    long_excerpts = [
        row["excerpt_id"]
        for row in cases
        if int(row.get("micro_excerpt_word_count") or 999) > 25
        or len(row["source_micro_excerpt"].split()) > 25
    ]
    add_check(
        checks,
        "PEV-04",
        "public-safe micro excerpts",
        not long_excerpts,
        "all source micro-excerpts stay within the short-quote boundary",
        f"overlong micro-excerpts: {long_excerpts}",
    )
    invalid_routes = sorted(
        row["excerpt_id"] for row in cases if row["human_gold_route_label"] not in ROUTE_LABELS
    )
    invalid_expected = sorted(
        row["excerpt_id"]
        for row in cases
        if row["current_expected_tool_decision"] not in TOOL_DECISIONS
        or row["current_expected_reviewer_action"] not in REVIEWER_ACTIONS
    )
    add_check(
        checks,
        "PEV-05",
        "valid route and action labels",
        not invalid_routes and not invalid_expected,
        "all gold route labels and expected current actions are valid",
        f"invalid_routes={invalid_routes}; invalid_expected={invalid_expected}",
    )
    private_rows = [row["excerpt_id"] for row in cases if contains_private_marker(row)]
    private_outputs = [row["excerpt_id"] for row in decision_rows if contains_private_marker(row)]
    add_check(
        checks,
        "PEV-06",
        "public-safe benchmark text",
        not private_rows and not private_outputs,
        "cases and decisions contain no private path, connector, or credential markers",
        f"case markers={private_rows}; output markers={private_outputs}",
    )
    coverage_errors = summary["prediction_coverage_errors"]
    add_check(
        checks,
        "PEV-07",
        "front-end prediction coverage",
        not coverage_errors["duplicates"] and not coverage_errors["missing"] and not coverage_errors["extra"],
        "every excerpt row has exactly one route prediction",
        f"prediction coverage errors: {coverage_errors}",
    )
    oracle_mode = summary["front_end_mode"] == "human_gold_oracle"
    decision_match = (
        summary["tool_decision_accuracy"] == "1.000"
        and summary["reviewer_action_accuracy"] == "1.000"
    )
    add_check(
        checks,
        "PEV-08",
        "backend consistency or prediction accuracy recorded",
        (decision_match if oracle_mode else True),
        (
            "all current tool decisions and reviewer actions match the gold boundary"
            if oracle_mode
            else (
                f"prediction mode records tool_decision_accuracy={summary['tool_decision_accuracy']} "
                f"and reviewer_action_accuracy={summary['reviewer_action_accuracy']}"
            )
        ),
        (
            f"tool_decision_accuracy={summary['tool_decision_accuracy']}; "
            f"reviewer_action_accuracy={summary['reviewer_action_accuracy']}"
        ),
    )
    add_check(
        checks,
        "PEV-09",
        "unsafe release guard",
        summary["unsafe_release_rate"] == "0.000"
        and summary["false_call_out_of_scope_count"] == 0,
        "no unsupported or out-of-scope excerpt is licensed as a claim",
        (
            f"unsafe_release_rate={summary['unsafe_release_rate']}; "
            f"false_call_out_of_scope={summary['false_call_out_of_scope_ids']}"
        ),
    )
    add_check(
        checks,
        "PEV-10",
        "registered control coverage",
        summary["template_accuracy_on_registered"] == "1.000",
        "all registered template controls preserve template identity",
        f"template_accuracy_on_registered={summary['template_accuracy_on_registered']}",
    )
    add_check(
        checks,
        "PEV-11",
        "reviewer comment readiness",
        summary["comment_readiness_rate"] == "1.000",
        "every row has a gold comment and generated reviewer-facing message",
        f"comment_readiness_rate={summary['comment_readiness_rate']}",
    )
    add_check(
        checks,
        "PEV-12",
        "autonomy boundary stated",
        summary["autonomous_full_paper_review_supported"] == "no",
        "benchmark explicitly denies autonomous full-paper review support",
        "autonomy boundary missing",
    )
    post_actions = Counter(row["post_admission_gold_action"] for row in cases)
    unique_claims = len({row["candidate_claim"] for row in cases})
    add_check(
        checks,
        "PEV-13",
        "claim diversity and hard-case balance",
        unique_claims >= 80
        and post_actions.get("OUT_OF_SCOPE", 0) >= 16
        and post_actions.get("SUPPRESS", 0) >= 8
        and {"ACCEPT", "REWRITE", "WEAKEN", "SUPPORT_ONLY", "SUPPRESS", "OUT_OF_SCOPE"}.issubset(post_actions),
        (
            f"unique_claims={unique_claims}; post_admission_actions={dict(sorted(post_actions.items()))}"
        ),
        (
            f"insufficient claim diversity or action balance: unique_claims={unique_claims}; "
            f"post_admission_actions={dict(sorted(post_actions.items()))}"
        ),
    )
    return checks


def html_escape(value: object) -> str:
    return html.escape(str(value if value is not None else ""))


def build_markdown(summary: dict[str, object], checks: list[dict[str, str]], decisions: list[dict[str, str]]) -> str:
    lines = [
        "# Paper Excerpt Reviewer-Value Benchmark",
        "",
        "Status: public-safe benchmark over short paper-excerpt anchors and reviewer-facing claim decisions.",
        "",
        "## Scope",
        "",
        "The default result uses a human-gold route as an oracle front end. It evaluates whether the deterministic claim-governance layer behaves safely once a selected excerpt and route are supplied. It does not prove autonomous full-paper review.",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
    ]
    for key in [
        "front_end_mode",
        "excerpt_rows",
        "external_excerpt_rows",
        "registered_control_rows",
        "source_papers",
        "source_families",
        "route_accuracy",
        "template_accuracy_on_registered",
        "tool_decision_accuracy",
        "reviewer_action_accuracy",
        "unsafe_release_rate",
        "false_call_out_of_scope_count",
        "false_admission_out_of_scope_count",
        "false_stop_relevant_count",
        "comment_readiness_rate",
        "autonomous_full_paper_review_supported",
    ]:
        lines.append(f"| {key} | {summary[key]} |")
    lines.extend(["", "## Checks", "", "| Check | Status | Evidence |", "| --- | --- | --- |"])
    for row in checks:
        lines.append(f"| {row['check_id']} {row['label']} | {row['status']} | {short(row['evidence'], 220)} |")
    lines.extend(["", "## Decision Sample", "", "| ID | Route | Tool Decision | Claim | Message |", "| --- | --- | --- | --- | --- |"])
    for row in decisions[:24]:
        lines.append(
            f"| {row['excerpt_id']} | {row['predicted_route_label']} | {row['tool_decision']} | "
            f"{short(row['candidate_claim'], 120)} | {short(row['reviewer_message'], 140)} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "A passing run supports a bounded claim: the tool is useful as a reviewer-facing claim audit component for selected empirical excerpts, because it converts registered controls into deterministic actions and fails closed for unsupported or out-of-scope claims. It does not support the stronger claim that the system can autonomously read and judge whole papers.",
            "",
        ]
    )
    return "\n".join(lines)


def build_html(summary: dict[str, object], checks: list[dict[str, str]], decisions: list[dict[str, str]]) -> str:
    metric_keys = [
        "excerpt_rows",
        "source_papers",
        "source_families",
        "tool_decision_accuracy",
        "unsafe_release_rate",
        "comment_readiness_rate",
    ]
    metrics = "".join(
        f"<section class='metric'><span>{html_escape(key)}</span><strong>{html_escape(summary[key])}</strong></section>"
        for key in metric_keys
    )
    check_rows = "".join(
        f"<tr><td>{html_escape(row['check_id'])}</td><td>{html_escape(row['label'])}</td><td>{html_escape(row['status'])}</td><td>{html_escape(short(row['evidence'], 220))}</td></tr>"
        for row in checks
    )
    card_rows = "".join(
        "<article class='card'>"
        f"<h3>{html_escape(row['excerpt_id'])}</h3>"
        f"<p class='meta'>{html_escape(row['source_family'])} · {html_escape(row['predicted_route_label'])} · {html_escape(row['tool_decision'])}</p>"
        f"<p class='quote'>{html_escape(row['source_micro_excerpt'])}</p>"
        f"<p>{html_escape(row['candidate_claim'])}</p>"
        f"<p class='message'>{html_escape(row['reviewer_message'])}</p>"
        "</article>"
        for row in decisions[:48]
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Paper Excerpt Reviewer-Value Benchmark</title>
  <style>
    :root {{
      --paper: #fbfaf6;
      --ink: #17211f;
      --muted: #62706b;
      --line: #d7dccf;
      --green: #3d6556;
      --blue: #2f5c86;
      --amber: #9b6b24;
      --white: #fffefb;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--paper);
      color: var(--ink);
      font-family: Aptos, "Segoe UI", sans-serif;
      line-height: 1.5;
    }}
    main {{
      max-width: 1220px;
      margin: 0 auto;
      padding: 34px 28px 56px;
    }}
    h1 {{
      margin: 0;
      font-family: Charter, Georgia, serif;
      font-size: 38px;
      line-height: 1.08;
      letter-spacing: 0;
    }}
    .lede {{
      margin: 12px 0 0;
      max-width: 850px;
      color: var(--muted);
    }}
    .metrics {{
      display: grid;
      grid-template-columns: repeat(6, minmax(0, 1fr));
      gap: 10px;
      margin: 24px 0;
    }}
    .metric {{
      background: var(--white);
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 13px;
      min-height: 84px;
    }}
    .metric span {{
      display: block;
      color: var(--muted);
      font-size: 12px;
    }}
    .metric strong {{
      display: block;
      margin-top: 7px;
      color: var(--green);
      font-size: 25px;
      line-height: 1;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      background: var(--white);
      border: 1px solid var(--line);
      border-radius: 6px;
      overflow: hidden;
    }}
    th, td {{
      border-bottom: 1px solid var(--line);
      padding: 8px 9px;
      text-align: left;
      vertical-align: top;
      font-size: 12px;
    }}
    th {{ background: #edf2eb; color: var(--green); }}
    .cards {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(330px, 1fr));
      gap: 12px;
    }}
    .card {{
      background: var(--white);
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 14px;
    }}
    .card h3 {{ margin: 0 0 6px; font-size: 14px; }}
    .meta {{ color: var(--blue); font-size: 12px; }}
    .quote {{
      border-left: 4px solid var(--amber);
      padding-left: 10px;
      color: var(--muted);
      font-family: Charter, Georgia, serif;
    }}
    .message {{ color: var(--muted); font-size: 12px; }}
    @media (max-width: 820px) {{
      .metrics {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      h1 {{ font-size: 31px; }}
    }}
  </style>
</head>
<body>
<main>
  <h1>Paper Excerpt Reviewer-Value Benchmark</h1>
  <p class="lede">A public-safe, excerpt-anchored benchmark for whether the claim-audit component gives useful reviewer-facing decisions without pretending to be an autonomous full-paper reviewer.</p>
  <section class="metrics">{metrics}</section>
  <h2>Checks</h2>
  <table><thead><tr><th>ID</th><th>Check</th><th>Status</th><th>Evidence</th></tr></thead><tbody>{check_rows}</tbody></table>
  <h2>Decision Cards</h2>
  <section class="cards">{card_rows}</section>
</main>
</body>
</html>
"""


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    output_dir = resolve(root, args.output)
    intake_runner = import_intake_runner(root)

    schema_path = root / FILES["schema"]
    if not schema_path.is_file():
        raise FileNotFoundError(f"missing schema: {schema_path}")
    cases, case_header = read_csv(root / FILES["cases"])
    sources, _ = read_csv(root / FILES["sources"])
    templates, casebook_by_id, nab_by_id = load_templates(root, intake_runner)
    front_end_mode, predictions = load_predictions(root, cases, args.predictions, args.baseline)
    summary, decision_rows, confusion_rows = evaluate(
        cases,
        predictions,
        front_end_mode,
        intake_runner,
        templates,
        casebook_by_id,
        nab_by_id,
    )
    checks = build_checks(cases, case_header, sources, summary, decision_rows)
    summary["checks_passed"] = sum(1 for row in checks if row["status"] == "PASS")
    summary["checks_failed"] = sum(1 for row in checks if row["status"] == "FAIL")
    if summary["checks_failed"]:
        summary["status"] = "FAIL"

    output_dir.mkdir(parents=True, exist_ok=True)
    decision_fields = [
        "excerpt_id",
        "paper_id",
        "source_family",
        "case_role",
        "source_title",
        "source_micro_excerpt",
        "candidate_claim",
        "gold_route_label",
        "predicted_route_label",
        "route_match",
        "gold_template_id",
        "predicted_template_id",
        "template_match_for_registered",
        "tool_decision",
        "expected_tool_decision",
        "tool_decision_match",
        "reviewer_action",
        "expected_reviewer_action",
        "reviewer_action_match",
        "recommended_output",
        "reviewer_message",
        "gold_reviewer_comment",
        "overclaim_hazard",
        "prediction_notes",
    ]
    write_csv(output_dir / "paper_excerpt_reviewer_value_decisions.csv", decision_rows, decision_fields)
    write_csv(output_dir / "paper_excerpt_reviewer_value_checks.csv", checks, ["check_id", "label", "status", "evidence"])
    write_csv(output_dir / "paper_excerpt_reviewer_value_confusion.csv", confusion_rows, ["gold_route_label", "predicted_route_label", "count"])
    write_csv(
        output_dir / "paper_excerpt_reviewer_value_prediction_packet.csv",
        build_prediction_packet(cases),
        [
            "excerpt_id",
            "paper_id",
            "source_family",
            "source_title",
            "source_micro_excerpt",
            "candidate_claim",
            "predicted_claim_span",
            "predicted_route_label",
            "predicted_template_id",
            "prediction_notes",
        ],
    )
    write_json(output_dir / "paper_excerpt_reviewer_value_summary.json", summary)
    (output_dir / "paper_excerpt_reviewer_value_report.md").write_text(
        build_markdown(summary, checks, decision_rows),
        encoding="utf-8",
    )
    (output_dir / "paper_excerpt_reviewer_value_report.html").write_text(
        build_html(summary, checks, decision_rows),
        encoding="utf-8",
    )

    if summary["status"] != "PASS":
        print("FAIL paper excerpt reviewer-value benchmark")
        print(f"checks_failed: {summary['checks_failed']}")
        return 1
    print("PASS paper excerpt reviewer-value benchmark")
    print(f"front_end_mode: {summary['front_end_mode']}")
    print(f"excerpt_rows: {summary['excerpt_rows']}")
    print(f"source_papers: {summary['source_papers']}")
    print(f"source_families: {summary['source_families']}")
    print(f"tool_decision_accuracy: {summary['tool_decision_accuracy']}")
    print(f"unsafe_release_rate: {summary['unsafe_release_rate']}")
    print(f"autonomous_full_paper_review_supported: {summary['autonomous_full_paper_review_supported']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
