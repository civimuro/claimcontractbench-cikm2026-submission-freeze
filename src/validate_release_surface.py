#!/usr/bin/env python3
"""Validate the public-safe ClaimContractBench release surface.

This script is intentionally standard-library only. It checks that a proposed
release manifest points to files inside the release root, that required files
exist, and that private coordination paths are not included.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import re
import sys


PRIVATE_DIR_PREFIXES = (
    "CODEX" + "_ONLY/",
    "CODEX" + "_AUDIT_TOWER/",
    "CLAUDE" + "_ONLY/",
    "EX" + "CHANGE/",
    ".co" + "dex/",
    ".cl" + "aude/",
)

FORBIDDEN_PREFIXES = PRIVATE_DIR_PREFIXES + (".git/",)

FORBIDDEN_CONTENT_MARKERS = PRIVATE_DIR_PREFIXES

FORBIDDEN_CONTENT_PATTERNS = (
    (
        "absolute local user path",
        re.compile(r"/Users/[A-Za-z0-9._-]+"),
    ),
    (
        "remote connector host",
        re.compile(r"\bconnect\.[A-Za-z0-9.-]+\b"),
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
        description="Validate ClaimContractBench release manifest paths."
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Release root to validate. Default: current directory.",
    )
    parser.add_argument(
        "--manifest",
        default="artifact/release_manifest_20260520.csv",
        help="Manifest CSV path relative to the release root.",
    )
    return parser.parse_args()


def is_truthy(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "y", "required"}


def validate_path(raw_path: str) -> list[str]:
    issues: list[str] = []
    if not raw_path or raw_path.strip() != raw_path:
        issues.append("path is empty or has surrounding whitespace")
    if raw_path.startswith("/"):
        issues.append("path must be release-root relative, not absolute")
    if ".." in Path(raw_path).parts:
        issues.append("path must not contain '..'")
    for prefix in FORBIDDEN_PREFIXES:
        if raw_path.startswith(prefix):
            issues.append("path must not include a private coordination prefix")
    return issues


def validate_content(path: Path, rel_path: str) -> list[str]:
    issues: list[str] = []
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError as exc:
        return [f"could not read file for content scan: {exc}"]
    for marker in FORBIDDEN_CONTENT_MARKERS:
        if marker in text:
            issues.append(
                f"{rel_path!r}: content contains a private path or credential marker"
            )
            break
    for label, pattern in FORBIDDEN_CONTENT_PATTERNS:
        if pattern.search(text):
            issues.append(f"{rel_path!r}: content matches forbidden pattern: {label}")
            break
    return issues


def validate_structured_file(path: Path, rel_path: str) -> list[str]:
    issues: list[str] = []
    if path.suffix == ".csv":
        try:
            with path.open(newline="", encoding="utf-8") as handle:
                reader = csv.DictReader(handle)
                rows = list(reader)
        except csv.Error as exc:
            return [f"{rel_path!r}: CSV parse failure: {exc}"]
        if not reader.fieldnames:
            issues.append(f"{rel_path!r}: CSV file has no header")
        if not rows:
            issues.append(f"{rel_path!r}: CSV file has no data rows")
    elif path.suffix == ".json":
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            issues.append(f"{rel_path!r}: JSON parse failure: {exc}")
    return issues


def read_csv_rows(path: Path, rel_path: str) -> tuple[list[dict[str, str]], list[str]]:
    issues: list[str] = []
    if not path.is_file():
        return [], [f"{rel_path!r}: required semantic file missing"]
    try:
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            rows = list(reader)
            fieldnames = list(reader.fieldnames or [])
    except csv.Error as exc:
        return [], [f"{rel_path!r}: CSV parse failure: {exc}"]
    if not fieldnames:
        issues.append(f"{rel_path!r}: CSV file has no header")
    if not rows:
        issues.append(f"{rel_path!r}: CSV file has no data rows")
    return rows, issues


def validate_claim_contract_semantics(root: Path) -> list[str]:
    """Check release-schema rows against dataset/scenario manifests.

    The surface validator stays lightweight, but it should catch the reuse
    failures that matter most for first inspection: schema/header drift,
    unknown dataset or scenario ids, and invalid action/layer enums.
    """

    issues: list[str] = []
    schema_rel = "artifact/claim_contract_schema_20260520.json"
    casebook_rel = "data/claim_passport_casebook_20260519.csv"
    dataset_rel = "artifact/dataset_source_manifest_20260520.csv"
    scenario_rel = "artifact/split_scenario_manifest_examples_20260520.csv"

    schema_path = root / schema_rel
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{schema_rel!r}: could not load claim-contract schema: {exc}"]

    fields = schema.get("fields", [])
    if not isinstance(fields, list) or not fields:
        return [f"{schema_rel!r}: schema has no fields list"]

    schema_field_names = [
        field.get("name") for field in fields if isinstance(field, dict)
    ]
    if any(not name for name in schema_field_names):
        issues.append(f"{schema_rel!r}: every schema field must have a name")

    required_fields = [
        field["name"]
        for field in fields
        if isinstance(field, dict) and field.get("required") and field.get("name")
    ]
    enum_values = {
        field.get("name"): set(field.get("values", []))
        for field in fields
        if isinstance(field, dict) and field.get("type") == "enum"
    }

    casebook_rows, casebook_issues = read_csv_rows(root / casebook_rel, casebook_rel)
    dataset_rows, dataset_issues = read_csv_rows(root / dataset_rel, dataset_rel)
    scenario_rows, scenario_issues = read_csv_rows(root / scenario_rel, scenario_rel)
    issues.extend(casebook_issues)
    issues.extend(dataset_issues)
    issues.extend(scenario_issues)
    if issues:
        return issues

    casebook_header = list(casebook_rows[0].keys()) if casebook_rows else []
    if casebook_header != schema_field_names:
        issues.append(
            f"{casebook_rel!r}: header must match schema fields; "
            f"got {casebook_header}, expected {schema_field_names}"
        )

    dataset_ids = {row.get("resource_dataset_id", "") for row in dataset_rows}
    scenarios = {row.get("scenario_id", ""): row for row in scenario_rows}

    for idx, row in enumerate(casebook_rows, start=2):
        event_id = row.get("event_id", f"row-{idx}")
        missing = [field for field in required_fields if not row.get(field, "").strip()]
        if missing:
            issues.append(f"{casebook_rel!r} row {idx} {event_id!r}: missing {missing}")

        dataset_id = row.get("dataset_id", "")
        scenario_id = row.get("scenario_id", "")
        if dataset_id not in dataset_ids:
            issues.append(
                f"{casebook_rel!r} row {idx} {event_id!r}: unknown dataset_id "
                f"{dataset_id!r}"
            )
        scenario = scenarios.get(scenario_id)
        if not scenario:
            issues.append(
                f"{casebook_rel!r} row {idx} {event_id!r}: unknown scenario_id "
                f"{scenario_id!r}"
            )
        elif scenario.get("dataset_id") != dataset_id:
            issues.append(
                f"{casebook_rel!r} row {idx} {event_id!r}: scenario "
                f"{scenario_id!r} belongs to {scenario.get('dataset_id')!r}, "
                f"not {dataset_id!r}"
            )

        for field_name, allowed in enum_values.items():
            value = row.get(field_name, "")
            if value not in allowed:
                issues.append(
                    f"{casebook_rel!r} row {idx} {event_id!r}: {field_name} "
                    f"{value!r} not in {sorted(allowed)}"
                )

        if (
            row.get("projection_action") == "suppress_fallback"
            and row.get("licensed_sentence") != "bottom_T"
        ):
            issues.append(
                f"{casebook_rel!r} row {idx} {event_id!r}: suppress_fallback "
                "must license bottom_T"
            )

    return issues


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    manifest = root / args.manifest

    if not manifest.is_file():
        print(f"FAIL missing manifest: {manifest}", file=sys.stderr)
        return 2

    rows = list(csv.DictReader(manifest.open(newline="", encoding="utf-8")))
    required_columns = {
        "path",
        "role",
        "required",
        "public_safe",
        "raw_data",
        "notes",
    }
    missing_columns = sorted(required_columns - set(rows[0].keys() if rows else []))
    if missing_columns:
        print(f"FAIL missing manifest columns: {missing_columns}", file=sys.stderr)
        return 2

    failures: list[str] = []
    required_count = 0
    public_safe_count = 0
    raw_data_count = 0

    for idx, row in enumerate(rows, start=2):
        rel_path = row["path"]
        for issue in validate_path(rel_path):
            failures.append(f"row {idx} {rel_path!r}: {issue}")

        required = is_truthy(row["required"])
        public_safe = is_truthy(row["public_safe"])
        raw_data = is_truthy(row["raw_data"])
        required_count += int(required)
        public_safe_count += int(public_safe)
        raw_data_count += int(raw_data)

        file_path = root / rel_path
        if required and not file_path.is_file():
            failures.append(f"row {idx} {rel_path!r}: required file missing")
        elif required:
            failures.extend(validate_content(file_path, rel_path))
            failures.extend(validate_structured_file(file_path, rel_path))
        if raw_data:
            failures.append(f"row {idx} {rel_path!r}: raw data flagged for release")
        if not public_safe:
            failures.append(f"row {idx} {rel_path!r}: not marked public safe")

    failures.extend(validate_claim_contract_semantics(root))

    if failures:
        print("FAIL release surface validation")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("PASS release surface validation")
    print(f"root: {root}")
    print(f"manifest: {manifest.relative_to(root)}")
    print(f"rows: {len(rows)}")
    print(f"required_files: {required_count}")
    print(f"public_safe_rows: {public_safe_count}")
    print(f"raw_data_rows: {raw_data_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
