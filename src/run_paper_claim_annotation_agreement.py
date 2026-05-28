#!/usr/bin/env python3
"""Check second-annotator agreement for the paper-claim benchmark.

The default input is the blind annotation packet, whose label columns are
intentionally blank. In that state the runner validates the packet and reports
PENDING_SECOND_ANNOTATOR. Once an annotator fills the three label columns, the
same runner computes exact agreement, Cohen's kappa, confusion rows, and
disagreement rows against the benchmark gold key.
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter
import html
import json
from pathlib import Path
import re


FILES = {
    "cases": "artifact/paper_claim_gold_benchmark_cases_20260521.csv",
    "packet": "artifact/paper_claim_gold_benchmark_blind_annotation_packet_20260521.csv",
    "map": "artifact/paper_claim_gold_benchmark_annotation_map_20260521.csv",
}

EXPECTED_PACKET_COLUMNS = [
    "annotation_id",
    "paper_id",
    "source_family",
    "source_title",
    "primary_source",
    "source_role",
    "case_role",
    "submitted_claim",
    "intended_use",
    "evidence_anchor",
    "annotator_route_label",
    "annotator_gold_action_after_admission",
    "annotator_current_action",
    "annotator_notes",
]

EXPECTED_MAP_COLUMNS = [
    "annotation_id",
    "claim_id",
    "paper_id",
    "case_role",
]

ROUTE_LABELS = {
    "CALL_REGISTERED_TEMPLATE",
    "NEEDS_TEMPLATE_ADMISSION",
    "OUT_OF_SCOPE_DO_NOT_CALL",
}

GOLD_ACTIONS = {
    "ACCEPT",
    "REWRITE",
    "WEAKEN",
    "SUPPORT_ONLY",
    "SUPPRESS",
    "REJECT",
    "OUT_OF_SCOPE",
}

CURRENT_ACTIONS = {
    "ACCEPT",
    "REWRITE",
    "WEAKEN",
    "SUPPORT_ONLY",
    "SUPPRESS",
    "REJECT",
    "UNSUPPORTED_TEMPLATE",
    "OUT_OF_SCOPE",
}

PACKET_LABEL_FIELDS = [
    "annotator_route_label",
    "annotator_gold_action_after_admission",
    "annotator_current_action",
]

PRIVATE_PATTERNS = (
    re.compile(r"/Users/[A-Za-z0-9._-]+"),
    re.compile(r"\bconnect\.[A-Za-z0-9.-]+\b"),
    re.compile(
        r"\b(?:"
        + "|".join(
            re.escape(prefix)
            for prefix in [
                "CODEX" + "_ONLY/",
                "CLAUDE" + "_ONLY/",
                "EX" + "CHANGE/",
            ]
        )
        + r")"
    ),
    re.compile(
        r"\b(?:password|passwd|token|secret|credential)\b\s*[:=]\s*"
        r"['\"]?[A-Za-z0-9_./+=-]{8,}",
        re.IGNORECASE,
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a blind paper-claim annotation packet and compute agreement once filled."
    )
    parser.add_argument("--root", default=".", help="Release root. Default: current directory.")
    parser.add_argument(
        "--annotations",
        default=FILES["packet"],
        help="Filled annotation CSV, relative to root unless absolute.",
    )
    parser.add_argument(
        "--annotation-map",
        default=FILES["map"],
        help="Annotation id to claim id map, relative to root unless absolute.",
    )
    parser.add_argument(
        "--output",
        default="reports/paper_claim_annotation_agreement_20260521",
        help="Report output directory. Relative paths are resolved under root.",
    )
    parser.add_argument(
        "--require-filled",
        action="store_true",
        help="Return failure unless every annotation row has all three label fields filled.",
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


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def resolve(root: Path, path_text: str) -> Path:
    path = Path(path_text)
    if not path.is_absolute():
        path = root / path
    return path.resolve()


def short(text: str, limit: int = 150) -> str:
    text = " ".join((text or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "..."


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


def ratio(num: int, den: int) -> str:
    if den == 0:
        return "0.000"
    return f"{num / den:.3f}"


def cohens_kappa(pairs: list[tuple[str, str]], categories: set[str]) -> str:
    if not pairs:
        return "NA"
    n = len(pairs)
    observed = sum(1 for left, right in pairs if left == right) / n
    left_counts = Counter(left for left, _ in pairs)
    right_counts = Counter(right for _, right in pairs)
    expected = sum(
        (left_counts[cat] / n) * (right_counts[cat] / n) for cat in categories
    )
    if expected == 1:
        return "1.000" if observed == 1 else "0.000"
    return f"{(observed - expected) / (1 - expected):.3f}"


def html_table(rows: list[dict[str, str]], columns: list[str]) -> str:
    header = "".join(f"<th>{html.escape(column)}</th>" for column in columns)
    body = []
    for row in rows:
        cells = "".join(
            f"<td>{html.escape(short(row.get(column, ''), 220))}</td>"
            for column in columns
        )
        body.append(f"<tr>{cells}</tr>")
    return f"<table><thead><tr>{header}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def build_agreement_rows(
    joined_rows: list[dict[str, str]]
) -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    field_specs = [
        (
            "route_label",
            "gold_route_label",
            "annotator_route_label",
            ROUTE_LABELS,
        ),
        (
            "gold_action_after_admission",
            "gold_gold_action_after_admission",
            "annotator_gold_action_after_admission",
            GOLD_ACTIONS,
        ),
        (
            "current_expected_action",
            "gold_current_expected_action",
            "annotator_current_action",
            CURRENT_ACTIONS,
        ),
    ]
    agreement_rows: list[dict[str, str]] = []
    confusion_rows: list[dict[str, str]] = []
    disagreement_rows: list[dict[str, str]] = []
    for field_name, gold_field, annotator_field, categories in field_specs:
        filled = [
            row
            for row in joined_rows
            if row.get(annotator_field, "").strip()
        ]
        pairs = [(row[gold_field], row[annotator_field]) for row in filled]
        matches = sum(1 for gold, annotator in pairs if gold == annotator)
        agreement_rows.append(
            {
                "field": field_name,
                "filled_rows": str(len(filled)),
                "exact_matches": str(matches),
                "agreement_rate": ratio(matches, len(filled)),
                "cohens_kappa": cohens_kappa(pairs, categories),
            }
        )
        for (gold, annotator), count in sorted(Counter(pairs).items()):
            confusion_rows.append(
                {
                    "field": field_name,
                    "gold_label": gold,
                    "annotator_label": annotator,
                    "count": str(count),
                }
            )
        for row in filled:
            if row[gold_field] != row[annotator_field]:
                disagreement_rows.append(
                    {
                        "field": field_name,
                        "annotation_id": row["annotation_id"],
                        "claim_id": row["claim_id"],
                        "gold_label": row[gold_field],
                        "annotator_label": row[annotator_field],
                        "submitted_claim": row["submitted_claim"],
                        "annotator_notes": row.get("annotator_notes", ""),
                    }
                )
    return agreement_rows, confusion_rows, disagreement_rows


def build_markdown(
    summary: dict[str, object],
    checks: list[dict[str, str]],
    agreement_rows: list[dict[str, str]],
    disagreement_rows: list[dict[str, str]],
) -> str:
    lines: list[str] = []
    lines.append("# Paper-Claim Annotation Agreement Report")
    lines.append("")
    lines.append(f"Status: `{summary['annotation_status']}`.")
    lines.append("")
    lines.append("## Purpose")
    lines.append("")
    lines.append(
        "This runner validates the blind annotation packet and computes "
        "second-annotator agreement once the label columns are filled. A pending "
        "status is intentional before an independent annotator supplies labels."
    )
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Item | Value |")
    lines.append("| --- | ---: |")
    for key in [
        "annotation_rows",
        "mapped_rows",
        "gold_rows",
        "fully_filled_rows",
        "agreement_computed",
        "checks_passed",
        "checks_failed",
    ]:
        lines.append(f"| {key} | {summary[key]} |")
    lines.append("")
    lines.append("## Agreement")
    lines.append("")
    lines.append("| Field | Filled rows | Exact matches | Agreement rate | Cohen's kappa |")
    lines.append("| --- | ---: | ---: | ---: | ---: |")
    for row in agreement_rows:
        lines.append(
            f"| {row['field']} | {row['filled_rows']} | {row['exact_matches']} | "
            f"{row['agreement_rate']} | {row['cohens_kappa']} |"
        )
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
    lines.append("## Disagreements")
    lines.append("")
    if disagreement_rows:
        lines.append(
            "| Field | Annotation | Claim | Gold | Annotator | Claim text |"
        )
        lines.append("| --- | --- | --- | --- | --- | --- |")
        for row in disagreement_rows[:60]:
            lines.append(
                f"| {row['field']} | {row['annotation_id']} | {row['claim_id']} | "
                f"{row['gold_label']} | {row['annotator_label']} | "
                f"{short(row['submitted_claim'], 160)} |"
            )
    else:
        lines.append("No disagreements are available yet.")
    lines.append("")
    lines.append("## Boundary")
    lines.append("")
    lines.append(
        "Before a second annotator fills the packet, this report supports only "
        "packet-readiness, not human agreement. After labels are supplied, the "
        "agreement rows become the reliability evidence."
    )
    lines.append("")
    return "\n".join(lines)


def build_html(
    summary: dict[str, object],
    checks: list[dict[str, str]],
    agreement_rows: list[dict[str, str]],
    disagreement_rows: list[dict[str, str]],
) -> str:
    metrics = []
    for key in [
        "annotation_rows",
        "fully_filled_rows",
        "agreement_computed",
        "checks_failed",
    ]:
        metrics.append(
            "<div class='metric'>"
            f"<span>{html.escape(key)}</span>"
            f"<strong>{html.escape(str(summary[key]))}</strong>"
            "</div>"
        )
    check_rows = [
        {
            "check": f"{row['check_id']} {row['label']}",
            "status": row["status"],
            "evidence": row["evidence"],
        }
        for row in checks
    ]
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Paper-Claim Annotation Agreement Report</title>
  <style>
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #f6faf8;
      color: #172124;
      line-height: 1.5;
    }}
    main {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 36px 28px 60px;
    }}
    h1 {{ margin: 0 0 8px; font-size: 34px; letter-spacing: 0; }}
    h2 {{
      margin-top: 34px;
      border-top: 2px solid #d7dfdc;
      padding-top: 20px;
      font-size: 22px;
      letter-spacing: 0;
    }}
    p {{ max-width: 900px; color: #5d6968; }}
    .metrics {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
      gap: 12px;
      margin: 24px 0;
    }}
    .metric {{
      background: white;
      border: 1px solid #d7dfdc;
      border-radius: 6px;
      padding: 14px 16px;
    }}
    .metric span {{ display: block; color: #5d6968; font-size: 13px; }}
    .metric strong {{ display: block; margin-top: 5px; color: #145c5a; font-size: 24px; }}
    table {{
      width: 100%;
      border-collapse: collapse;
      background: white;
      border: 1px solid #d7dfdc;
      border-radius: 6px;
      overflow: hidden;
      margin-top: 12px;
    }}
    th, td {{
      border-bottom: 1px solid #d7dfdc;
      padding: 8px 10px;
      vertical-align: top;
      text-align: left;
      font-size: 13px;
    }}
    th {{ background: #e8f2ee; color: #145c5a; font-weight: 750; }}
    tr:last-child td {{ border-bottom: 0; }}
  </style>
</head>
<body>
<main>
  <h1>Paper-Claim Annotation Agreement Report</h1>
  <p>Status: <strong>{html.escape(str(summary['annotation_status']))}</strong>.
  The report validates the blind packet now and computes agreement once an
  independent annotator fills the label columns.</p>
  <section class="metrics">{''.join(metrics)}</section>
  <h2>Agreement</h2>
  {html_table(agreement_rows, ["field", "filled_rows", "exact_matches", "agreement_rate", "cohens_kappa"])}
  <h2>Checks</h2>
  {html_table(check_rows, ["check", "status", "evidence"])}
  <h2>Disagreements</h2>
  {html_table(disagreement_rows[:80], ["field", "annotation_id", "claim_id", "gold_label", "annotator_label", "submitted_claim"])}
</main>
</body>
</html>
"""


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    output_dir = resolve(root, args.output)
    annotation_path = resolve(root, args.annotations)
    map_path = resolve(root, args.annotation_map)
    cases_path = root / FILES["cases"]

    failures: list[str] = []
    try:
        cases, _ = read_csv(cases_path)
    except (OSError, csv.Error) as exc:
        cases = []
        failures.append(f"{FILES['cases']}: could not read gold cases: {exc}")
    try:
        annotations, annotation_header = read_csv(annotation_path)
    except (OSError, csv.Error) as exc:
        annotations, annotation_header = [], []
        failures.append(f"{annotation_path}: could not read annotations: {exc}")
    try:
        map_rows, map_header = read_csv(map_path)
    except (OSError, csv.Error) as exc:
        map_rows, map_header = [], []
        failures.append(f"{map_path}: could not read annotation map: {exc}")

    cases_by_id = {row.get("claim_id", ""): row for row in cases}
    map_by_ann = {row.get("annotation_id", ""): row for row in map_rows}
    annotations_by_id = {row.get("annotation_id", ""): row for row in annotations}

    joined_rows: list[dict[str, str]] = []
    for ann in annotations:
        ann_id = ann.get("annotation_id", "")
        mapped = map_by_ann.get(ann_id, {})
        gold = cases_by_id.get(mapped.get("claim_id", ""), {})
        joined = dict(ann)
        joined.update(
            {
                "claim_id": mapped.get("claim_id", ""),
                "gold_route_label": gold.get("route_label", ""),
                "gold_gold_action_after_admission": gold.get("gold_action_after_admission", ""),
                "gold_current_expected_action": gold.get("current_expected_action", ""),
            }
        )
        joined_rows.append(joined)

    duplicate_annotation_ids = [
        ann_id
        for ann_id, count in Counter(row.get("annotation_id", "") for row in annotations).items()
        if count > 1
    ]
    missing_map = [
        row.get("annotation_id", "")
        for row in annotations
        if row.get("annotation_id", "") not in map_by_ann
    ]
    missing_case = [
        row.get("annotation_id", "")
        for row in map_rows
        if row.get("claim_id", "") not in cases_by_id
    ]
    unmapped_cases = sorted(
        set(cases_by_id) - {row.get("claim_id", "") for row in map_rows}
    )
    missing_annotations = sorted(
        set(map_by_ann) - set(annotations_by_id)
    )
    private_rows = [
        row.get("annotation_id", "")
        for row in annotations + map_rows
        if contains_private_marker(row)
    ]
    invalid_routes = [
        row.get("annotation_id", "")
        for row in annotations
        if row.get("annotator_route_label", "").strip()
        and row.get("annotator_route_label", "") not in ROUTE_LABELS
    ]
    invalid_gold_actions = [
        row.get("annotation_id", "")
        for row in annotations
        if row.get("annotator_gold_action_after_admission", "").strip()
        and row.get("annotator_gold_action_after_admission", "") not in GOLD_ACTIONS
    ]
    invalid_current_actions = [
        row.get("annotation_id", "")
        for row in annotations
        if row.get("annotator_current_action", "").strip()
        and row.get("annotator_current_action", "") not in CURRENT_ACTIONS
    ]
    blank_label_counts = {
        field: sum(1 for row in annotations if not row.get(field, "").strip())
        for field in PACKET_LABEL_FIELDS
    }
    fully_filled_rows = sum(
        1
        for row in annotations
        if all(row.get(field, "").strip() for field in PACKET_LABEL_FIELDS)
    )
    if fully_filled_rows == 0:
        annotation_status = "PENDING_SECOND_ANNOTATOR"
    elif fully_filled_rows < len(annotations):
        annotation_status = "PARTIAL_ANNOTATION"
    else:
        annotation_status = "FILLED"

    agreement_rows, confusion_rows, disagreement_rows = build_agreement_rows(joined_rows)

    checks: list[dict[str, str]] = []
    add_check(
        checks,
        "AA-01",
        "inputs present",
        not failures and bool(cases) and bool(annotations) and bool(map_rows),
        "gold cases, annotation packet, and annotation map loaded",
        "; ".join(failures) if failures else "one or more required inputs are empty",
    )
    add_check(
        checks,
        "AA-02",
        "packet header alignment",
        annotation_header == EXPECTED_PACKET_COLUMNS,
        f"annotation packet has {len(annotation_header)} expected columns",
        f"annotation header={annotation_header}; expected={EXPECTED_PACKET_COLUMNS}",
    )
    add_check(
        checks,
        "AA-03",
        "map header alignment",
        map_header == EXPECTED_MAP_COLUMNS,
        f"annotation map has {len(map_header)} expected columns",
        f"map header={map_header}; expected={EXPECTED_MAP_COLUMNS}",
    )
    hidden_gold_columns = [
        column
        for column in ["route_label", "gold_action_after_admission", "current_expected_action"]
        if column in annotation_header
    ]
    add_check(
        checks,
        "AA-04",
        "blind packet has no gold label columns",
        not hidden_gold_columns,
        "packet exposes only annotator label columns, not benchmark gold labels",
        f"hidden gold columns leaked into packet: {hidden_gold_columns}",
    )
    add_check(
        checks,
        "AA-05",
        "map and case joins",
        not missing_map and not missing_case and not unmapped_cases and not missing_annotations,
        "all annotation ids map to benchmark claim ids and all gold cases are covered",
        (
            f"missing_map={missing_map}; missing_case={missing_case}; "
            f"unmapped_cases={unmapped_cases}; missing_annotations={missing_annotations}"
        ),
    )
    add_check(
        checks,
        "AA-06",
        "row counts",
        len(annotations) == len(cases) == len(map_rows) == 128,
        "annotation packet, map, and gold key each contain 128 rows",
        (
            f"annotations={len(annotations)}; cases={len(cases)}; "
            f"map_rows={len(map_rows)}"
        ),
    )
    add_check(
        checks,
        "AA-07",
        "unique annotation ids",
        not duplicate_annotation_ids,
        "annotation ids are unique",
        f"duplicate annotation ids: {duplicate_annotation_ids}",
    )
    add_check(
        checks,
        "AA-08",
        "annotation enum validity",
        not invalid_routes and not invalid_gold_actions and not invalid_current_actions,
        "nonblank annotation labels obey route/action enums",
        (
            f"invalid_routes={invalid_routes}; invalid_gold={invalid_gold_actions}; "
            f"invalid_current={invalid_current_actions}"
        ),
    )
    add_check(
        checks,
        "AA-09",
        "private marker scan",
        not private_rows,
        "no private coordination paths, local paths, or credential-like patterns in packet or map",
        f"private marker rows: {private_rows}",
    )
    add_check(
        checks,
        "AA-10",
        "annotation state",
        annotation_status == "FILLED" or not args.require_filled,
        f"annotation_status={annotation_status}; blank_label_counts={blank_label_counts}",
        (
            "filled annotations are required but packet is not complete; "
            f"annotation_status={annotation_status}; blank_label_counts={blank_label_counts}"
        ),
    )

    checks_failed = sum(1 for row in checks if row["status"] == "FAIL")
    summary = {
        "annotation_status": annotation_status,
        "annotation_rows": len(annotations),
        "mapped_rows": len(map_rows),
        "gold_rows": len(cases),
        "fully_filled_rows": fully_filled_rows,
        "blank_label_counts": blank_label_counts,
        "agreement_computed": "yes" if annotation_status == "FILLED" else "no",
        "agreement_rows": agreement_rows,
        "disagreement_rows": len(disagreement_rows),
        "checks_passed": len(checks) - checks_failed,
        "checks_failed": checks_failed,
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(
        output_dir / "paper_claim_annotation_agreement_checks.csv",
        checks,
        ["check_id", "label", "status", "evidence"],
    )
    write_csv(
        output_dir / "paper_claim_annotation_agreement_metrics.csv",
        agreement_rows,
        ["field", "filled_rows", "exact_matches", "agreement_rate", "cohens_kappa"],
    )
    write_csv(
        output_dir / "paper_claim_annotation_agreement_confusion.csv",
        confusion_rows,
        ["field", "gold_label", "annotator_label", "count"],
    )
    write_csv(
        output_dir / "paper_claim_annotation_disagreements.csv",
        disagreement_rows,
        [
            "field",
            "annotation_id",
            "claim_id",
            "gold_label",
            "annotator_label",
            "submitted_claim",
            "annotator_notes",
        ],
    )
    write_json(output_dir / "paper_claim_annotation_agreement_summary.json", summary)
    (output_dir / "paper_claim_annotation_agreement_report.md").write_text(
        build_markdown(summary, checks, agreement_rows, disagreement_rows),
        encoding="utf-8",
    )
    (output_dir / "paper_claim_annotation_agreement_report.html").write_text(
        build_html(summary, checks, agreement_rows, disagreement_rows),
        encoding="utf-8",
    )

    if checks_failed:
        print("FAIL paper claim annotation agreement")
        print(f"checks_failed: {checks_failed}")
        return 1
    print("PASS paper claim annotation agreement scaffold")
    print(f"annotation_status: {annotation_status}")
    print(f"annotation_rows: {len(annotations)}")
    print(f"fully_filled_rows: {fully_filled_rows}")
    print(f"agreement_computed: {summary['agreement_computed']}")
    print(f"checks_passed: {summary['checks_passed']}")
    print("outputs:")
    for name in [
        "paper_claim_annotation_agreement_report.md",
        "paper_claim_annotation_agreement_report.html",
        "paper_claim_annotation_agreement_summary.json",
        "paper_claim_annotation_agreement_checks.csv",
        "paper_claim_annotation_agreement_metrics.csv",
        "paper_claim_annotation_agreement_confusion.csv",
        "paper_claim_annotation_disagreements.csv",
    ]:
        rel = output_dir.relative_to(root) / name if output_dir.is_relative_to(root) else output_dir / name
        print(f"- {rel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
