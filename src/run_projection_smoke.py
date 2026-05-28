#!/usr/bin/env python3
"""Regenerate the public claim-passport smoke cases from release-root inputs.

This is a deliberately small, standard-library-only runner. It is not a full
training or raw-data reproduction path; it checks that the public release has a
mechanical projection surface for the five reviewer-facing action families.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import sys


ACTION_COLUMNS = {
    "emit_as_written": "emit_sentence",
    "relabel_as_upper_bound": "relabel_sentence",
    "weaken_to_diagnostic": "weaken_sentence",
    "rewrite_to_decision_local": "rewrite_sentence",
}

REQUIRED_ACTIONS = {
    "emit_as_written",
    "relabel_as_upper_bound",
    "weaken_to_diagnostic",
    "rewrite_to_decision_local",
    "suppress_fallback",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Regenerate and validate ClaimContractBench projection smoke rows."
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Release root to validate. Default: current directory.",
    )
    parser.add_argument(
        "--schema",
        default="artifact/claim_contract_schema_20260520.json",
        help="Claim-contract schema path relative to root.",
    )
    parser.add_argument(
        "--cases",
        default="artifact/projection_smoke_cases_20260521.csv",
        help="Projection smoke input rows relative to root.",
    )
    parser.add_argument(
        "--expected",
        default="data/claim_passport_casebook_20260519.csv",
        help="Expected public casebook rows relative to root.",
    )
    parser.add_argument(
        "--dataset-manifest",
        default="artifact/dataset_source_manifest_20260520.csv",
        help="Dataset manifest path relative to root.",
    )
    parser.add_argument(
        "--scenario-manifest",
        default="artifact/split_scenario_manifest_examples_20260520.csv",
        help="Scenario manifest path relative to root.",
    )
    parser.add_argument(
        "--write-generated",
        help="Optional CSV path, relative to root, where regenerated rows are written.",
    )
    return parser.parse_args()


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


def schema_fields(schema_path: Path) -> tuple[list[str], dict[str, set[str]]]:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    fields = schema.get("fields", [])
    names = [field["name"] for field in fields]
    enums = {
        field["name"]: set(field.get("values", []))
        for field in fields
        if field.get("type") == "enum"
    }
    return names, enums


def project_action(row: dict[str, str]) -> str:
    g = row["G_information_boundary"]
    q = row["Q_reportability_policy"]
    u = row["U_decision_use"]
    if q == "not_reportable":
        return "suppress_fallback"
    if g == "upper_bound_only" and q in {"reportable", "weakly_reportable"}:
        return "relabel_as_upper_bound"
    if u.startswith("decision_winner_mismatch") and q in {
        "reportable",
        "weakly_reportable",
    }:
        return "rewrite_to_decision_local"
    if q == "weakly_reportable":
        return "weaken_to_diagnostic"
    if q == "reportable":
        return "emit_as_written"
    raise ValueError(
        f"{row['event_id']}: unsupported smoke projection state "
        f"G={g!r}, Q={q!r}, U={u!r}"
    )


def project_row(row: dict[str, str], fieldnames: list[str]) -> dict[str, str]:
    action = project_action(row)
    if action == "suppress_fallback":
        licensed_sentence = "bottom_T"
    else:
        source_column = ACTION_COLUMNS[action]
        licensed_sentence = row.get(source_column, "").strip()
        if not licensed_sentence:
            raise ValueError(
                f"{row['event_id']}: {action} requires nonempty {source_column}"
            )

    projected = {
        "event_id": row["event_id"],
        "dataset_id": row["dataset_id"],
        "scenario_id": row["scenario_id"],
        "model_or_scorer": row["model_or_scorer"],
        "seed_or_profile": row.get("seed_or_profile", ""),
        "claim_layer": row["claim_layer"],
        "G_information_boundary": row["G_information_boundary"],
        "Q_reportability_policy": row["Q_reportability_policy"],
        "U_decision_use": row["U_decision_use"],
        "preorder_relation": row["preorder_relation"],
        "tempting_sentence": row["tempting_sentence"],
        "licensed_sentence": licensed_sentence,
        "forbidden_sentence": row["forbidden_sentence"],
        "projection_action": action,
        "source_anchor_id": row["source_anchor_id"],
        "boundary_note": row["boundary_note"],
    }
    return {field: projected.get(field, "") for field in fieldnames}


def validate_joins(
    rows: list[dict[str, str]],
    dataset_rows: list[dict[str, str]],
    scenario_rows: list[dict[str, str]],
) -> list[str]:
    issues: list[str] = []
    dataset_ids = {row.get("resource_dataset_id", "") for row in dataset_rows}
    scenarios = {row.get("scenario_id", ""): row for row in scenario_rows}
    for row in rows:
        event_id = row["event_id"]
        dataset_id = row["dataset_id"]
        scenario_id = row["scenario_id"]
        if dataset_id not in dataset_ids:
            issues.append(f"{event_id}: unknown dataset_id {dataset_id!r}")
        scenario = scenarios.get(scenario_id)
        if not scenario:
            issues.append(f"{event_id}: unknown scenario_id {scenario_id!r}")
        elif scenario.get("dataset_id") != dataset_id:
            issues.append(
                f"{event_id}: scenario {scenario_id!r} belongs to "
                f"{scenario.get('dataset_id')!r}, not {dataset_id!r}"
            )
    return issues


def compare_rows(
    generated: list[dict[str, str]],
    expected: list[dict[str, str]],
    fieldnames: list[str],
) -> list[str]:
    issues: list[str] = []
    expected_by_id = {row["event_id"]: row for row in expected}
    generated_ids = {row["event_id"] for row in generated}
    if generated_ids != set(expected_by_id):
        issues.append(
            f"event_id set mismatch: generated={sorted(generated_ids)}, "
            f"expected={sorted(expected_by_id)}"
        )
        return issues

    for row in generated:
        event_id = row["event_id"]
        expected_row = expected_by_id[event_id]
        for field in fieldnames:
            if row.get(field, "") != expected_row.get(field, ""):
                issues.append(
                    f"{event_id}: {field} mismatch; generated={row.get(field, '')!r}; "
                    f"expected={expected_row.get(field, '')!r}"
                )
    return issues


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()

    fieldnames, enums = schema_fields(root / args.schema)
    cases, case_header = read_csv(root / args.cases)
    expected, expected_header = read_csv(root / args.expected)
    dataset_rows, _ = read_csv(root / args.dataset_manifest)
    scenario_rows, _ = read_csv(root / args.scenario_manifest)

    failures: list[str] = []
    if not cases:
        failures.append("projection smoke case file has no rows")
    if expected_header != fieldnames:
        failures.append(
            f"expected casebook header does not match schema: {expected_header}"
        )

    generated: list[dict[str, str]] = []
    seen_event_ids: set[str] = set()
    for row in cases:
        event_id = row.get("event_id", "")
        if event_id in seen_event_ids:
            failures.append(f"duplicate event_id {event_id!r}")
            continue
        seen_event_ids.add(event_id)
        try:
            projected = project_row(row, fieldnames)
        except (KeyError, ValueError) as exc:
            failures.append(str(exc))
            continue

        for field_name, allowed in enums.items():
            value = projected.get(field_name, "")
            if value not in allowed:
                failures.append(
                    f"{event_id}: {field_name}={value!r} not in {sorted(allowed)}"
                )
        if (
            projected["projection_action"] == "suppress_fallback"
            and projected["licensed_sentence"] != "bottom_T"
        ):
            failures.append(f"{event_id}: suppress_fallback must emit bottom_T")
        generated.append(projected)

    failures.extend(validate_joins(generated, dataset_rows, scenario_rows))
    failures.extend(compare_rows(generated, expected, fieldnames))

    action_counts = {
        action: sum(1 for row in generated if row["projection_action"] == action)
        for action in sorted(REQUIRED_ACTIONS)
    }
    if set(action for action, count in action_counts.items() if count) != REQUIRED_ACTIONS:
        failures.append(f"smoke cases must cover all action families: {action_counts}")

    if args.write_generated and not failures:
        write_csv(root / args.write_generated, generated, fieldnames)

    if failures:
        print("FAIL projection smoke runner")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("PASS projection smoke runner")
    print(f"root: {root}")
    print(f"smoke_rows: {len(generated)}")
    for action, count in action_counts.items():
        print(f"{action}: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
