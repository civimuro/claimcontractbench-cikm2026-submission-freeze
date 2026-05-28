#!/usr/bin/env python3
"""Generate a reviewer-facing claim audit report from release-root assets.

The projection smoke runner proves that the five public action families can be
regenerated. This runner asks a wider reviewer question: do the public release
assets jointly support a typed claim-governance workflow, or are they only a
set of disconnected tables?

The script remains standard-library only and uses public-safe derived assets.
It does not parse arbitrary natural-language claims, rerun training, or
regenerate the internal 375-event trace.
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
import html
import json
from pathlib import Path
import sys


FILES = {
    "schema": "artifact/claim_contract_schema_20260520.json",
    "casebook": "data/claim_passport_casebook_20260519.csv",
    "ablation": "data/gqu_ablation_display_20260520/ablation_display_rows.csv",
    "q_policy": "data/q_policy_sensitivity_display_20260519/q_policy_display_rows.csv",
    "resource": "data/support_resource_display_20260520/resource_component_rows.csv",
    "nab_visual": "data/nab_adapter_visual_passport_rows_20260519.csv",
}

ACTION_FAMILIES = {
    "emit_as_written",
    "relabel_as_upper_bound",
    "weaken_to_diagnostic",
    "rewrite_to_decision_local",
    "suppress_fallback",
}

EXPECTED_PRIMITIVES = {
    "G",
    "Q",
    "U",
    "layer",
    "support_anchor",
    "adapter_U_preorder",
}

EXPECTED_RESOURCE_COMPONENTS = {
    "dataset manifest",
    "scenario manifest",
    "claim schema",
    "projection specification",
    "action certificates",
    "validation scripts",
    "release notes",
}

ATTACK_MAP = [
    {
        "attack": "This is only a checklist or writing advice.",
        "asset": "claim schema + projection smoke + claim cards",
        "response": "The release has typed fields, finite action families, exact casebook rows, and fail-closed checks over emitted claims.",
    },
    {
        "attack": "Metric evidence should be enough; the operator adds bureaucracy.",
        "asset": "G/Q/U ablation rows",
        "response": "Removing G, Q, U, layer, or support anchors changes the licensed claim, overpromotes a claim, or makes the row unauditable.",
    },
    {
        "attack": "The method only suppresses claims.",
        "asset": "positive support case CP-01 and ABL-05",
        "response": "The operator can emit a bounded positive local claim when the declared support anchor is present.",
    },
    {
        "attack": "The Q policy is arbitrary and can strengthen claims after the fact.",
        "asset": "Q-policy sensitivity rows",
        "response": "The public Q rows expose threshold sensitivity and include a non-upgrading 1500/1500 PASS trace.",
    },
    {
        "attack": "NAB quietly expands the paper into anomaly detection.",
        "asset": "NAB visual passport rows",
        "response": "NAB is kept as a support-only adapter-admission witness with explicit forbidden broad anomaly-detection claims.",
    },
    {
        "attack": "Scope expansion is ad hoc and can admit any new benchmark.",
        "asset": "claim template admission runner",
        "response": "Batch admission admits mainline/support-only templates only when all critical fields instantiate, and rejects the AI4I probe until the missing contract fields exist.",
    },
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate reviewer-facing ClaimContractBench audit reports."
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Release root to audit. Default: current directory.",
    )
    parser.add_argument(
        "--output",
        default="reports/claim_audit_report_20260521",
        help="Report output directory. Relative paths are resolved under root.",
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


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_output(root: Path, output: str) -> Path:
    out = Path(output)
    if not out.is_absolute():
        out = root / out
    return out.resolve()


def short(text: str, limit: int = 150) -> str:
    text = " ".join((text or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "..."


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


def required_schema_fields(schema: dict[str, object]) -> tuple[list[str], list[str]]:
    fields = schema.get("fields", [])
    if not isinstance(fields, list):
        return [], []
    field_names = [
        field.get("name", "")
        for field in fields
        if isinstance(field, dict) and field.get("name")
    ]
    required = [
        field.get("name", "")
        for field in fields
        if isinstance(field, dict) and field.get("required") and field.get("name")
    ]
    return field_names, required


def action_semantic_issues(casebook_rows: list[dict[str, str]]) -> list[str]:
    issues: list[str] = []
    for row in casebook_rows:
        event_id = row.get("event_id", "")
        action = row.get("projection_action", "")
        licensed = row.get("licensed_sentence", "")
        g = row.get("G_information_boundary", "")
        q = row.get("Q_reportability_policy", "")
        u = row.get("U_decision_use", "")
        preorder = row.get("preorder_relation", "")

        if action == "suppress_fallback":
            if licensed != "bottom_T":
                issues.append(f"{event_id}: suppress_fallback must license bottom_T")
        elif not licensed or licensed == "bottom_T":
            issues.append(f"{event_id}: non-suppression action needs non-bottom license")

        if action == "relabel_as_upper_bound" and not (
            g == "upper_bound_only" or "upper_bound" in preorder
        ):
            issues.append(f"{event_id}: upper-bound relabel lacks G/preorder support")
        if action == "weaken_to_diagnostic" and q != "weakly_reportable":
            issues.append(f"{event_id}: diagnostic weaken should be weakly_reportable")
        if action == "rewrite_to_decision_local" and not u.startswith(
            "decision_winner_mismatch"
        ):
            issues.append(f"{event_id}: decision rewrite lacks decision-use mismatch")
        if action == "emit_as_written" and q != "reportable":
            issues.append(f"{event_id}: emit_as_written should be reportable")
        if action == "suppress_fallback" and q != "not_reportable":
            issues.append(f"{event_id}: suppress_fallback should be not_reportable")
    return issues


def build_claim_cards(
    casebook_rows: list[dict[str, str]],
    ablation_by_source: dict[str, list[dict[str, str]]],
) -> list[dict[str, str]]:
    cards: list[dict[str, str]] = []
    for row in casebook_rows:
        event_id = row["event_id"]
        linked = ablation_by_source.get(event_id, [])
        cards.append(
            {
                "event_id": event_id,
                "action": row["projection_action"],
                "layer": row["claim_layer"],
                "G": row["G_information_boundary"],
                "Q": row["Q_reportability_policy"],
                "U": row["U_decision_use"],
                "licensed_sentence": row["licensed_sentence"],
                "forbidden_sentence": row["forbidden_sentence"],
                "ablation_link": "; ".join(
                    f"{item['display_id']}:{item['primitive_or_field']}"
                    for item in linked
                ),
                "boundary": row["boundary_note"],
            }
        )
    return cards


def build_markdown(
    summary: dict[str, object],
    checks: list[dict[str, str]],
    claim_cards: list[dict[str, str]],
    ablation_rows: list[dict[str, str]],
    q_rows: list[dict[str, str]],
    nab_rows: list[dict[str, str]],
    resource_rows: list[dict[str, str]],
) -> str:
    lines: list[str] = []
    lines.append("# Claim Audit Report")
    lines.append("")
    lines.append("Status: generated from release-root public-safe assets.")
    lines.append("")
    lines.append("## Contribution Stress Target")
    lines.append("")
    lines.append(
        "This report tests whether the release behaves like a typed claim-governance "
        "workflow rather than a loose bundle of evidence tables. It audits the "
        "claim passport rows, G/Q/U field interventions, Q-policy sensitivity, "
        "support-only adapter rows, and resource boundaries in one reviewer-facing pass."
    )
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Item | Value |")
    lines.append("| --- | ---: |")
    for key in [
        "casebook_rows",
        "ablation_rows",
        "q_policy_rows",
        "nab_visual_rows",
        "resource_components",
        "checks_passed",
        "checks_failed",
    ]:
        lines.append(f"| {key} | {summary[key]} |")
    lines.append("")
    lines.append("## Audit Checks")
    lines.append("")
    lines.append("| Check | Status | Evidence |")
    lines.append("| --- | --- | --- |")
    for check in checks:
        lines.append(
            f"| {check['check_id']} {check['label']} | {check['status']} | "
            f"{short(check['evidence'], 220)} |"
        )
    lines.append("")
    lines.append("## Claim Cards")
    lines.append("")
    lines.append("| Event | Action | G/Q/U | Licensed Claim | Forbidden Claim | Linked Stress |")
    lines.append("| --- | --- | --- | --- | --- | --- |")
    for card in claim_cards:
        gqu = f"G={card['G']}; Q={card['Q']}; U={card['U']}"
        lines.append(
            f"| {card['event_id']} | {card['action']} | {short(gqu, 90)} | "
            f"{short(card['licensed_sentence'], 170)} | "
            f"{short(card['forbidden_sentence'], 140)} | "
            f"{card['ablation_link'] or 'none'} |"
        )
    lines.append("")
    lines.append("## Primitive Stress Map")
    lines.append("")
    lines.append("| Row | Field | What Breaks Without It | Licensed Effect | Boundary |")
    lines.append("| --- | --- | --- | --- | --- |")
    for row in ablation_rows:
        lines.append(
            f"| {row['display_id']} | {row['primitive_or_field']} | "
            f"{short(row['metric_only_failure'], 120)} | "
            f"{short(row['licensed_effect'], 120)} | {short(row['boundary'], 120)} |"
        )
    lines.append("")
    lines.append("## Q-Policy Sensitivity")
    lines.append("")
    lines.append("| Row | Group | Observed Result | Claim Effect | Boundary |")
    lines.append("| --- | --- | --- | --- | --- |")
    for row in q_rows:
        lines.append(
            f"| {row['row']} | {row['group']} | {short(row['observed result'], 120)} | "
            f"{short(row['claim effect'], 120)} | {short(row['boundary'], 120)} |"
        )
    lines.append("")
    lines.append("## Adapter Boundary Probe")
    lines.append("")
    lines.append("| Row | Action | Licensed Claim | Forbidden Claim | Role |")
    lines.append("| --- | --- | --- | --- | --- |")
    for row in nab_rows:
        lines.append(
            f"| {row['display_id']} | {row['adapter_action']} | "
            f"{short(row['licensed_sentence'], 160)} | "
            f"{short(row['forbidden_sentence'], 140)} | {row['visual_role']} |"
        )
    lines.append("")
    lines.append("## Resource Boundary")
    lines.append("")
    lines.append("| Component | Controls | Boundary |")
    lines.append("| --- | --- | --- |")
    for row in resource_rows:
        lines.append(
            f"| {row['component']} | {short(row['risk_controlled'], 120)} | "
            f"{short(row['boundary'], 120)} |"
        )
    lines.append("")
    lines.append("## Reviewer Attack Map")
    lines.append("")
    lines.append("| Attack | Asset | Response |")
    lines.append("| --- | --- | --- |")
    for item in ATTACK_MAP:
        lines.append(f"| {item['attack']} | {item['asset']} | {item['response']} |")
    lines.append("")
    lines.append("## Current Limits")
    lines.append("")
    lines.append(
        "- The report is a public-safe audit pass over derived release assets; it is "
        "not a raw-data or GPU reproduction path."
    )
    lines.append(
        "- It does not certify arbitrary natural-language reviewer claims. It audits "
        "rows that already enter the typed claim-contract schema."
    )
    lines.append(
        "- The companion claim-template admission runner now tests whether new "
        "claim templates have enough typed structure to enter the workflow. The "
        "strongest next contribution step is to normalize the full 375-event "
        "operator trace into the same release-root interface."
    )
    lines.append("")
    return "\n".join(lines)


def html_table(rows: list[dict[str, str]], columns: list[str]) -> str:
    head = "".join(f"<th>{html.escape(column)}</th>" for column in columns)
    body_rows = []
    for row in rows:
        cells = "".join(
            f"<td>{html.escape(short(row.get(column, ''), 240))}</td>"
            for column in columns
        )
        body_rows.append(f"<tr>{cells}</tr>")
    return f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(body_rows)}</tbody></table>"


def build_html(
    summary: dict[str, object],
    checks: list[dict[str, str]],
    claim_cards: list[dict[str, str]],
    ablation_rows: list[dict[str, str]],
    q_rows: list[dict[str, str]],
    nab_rows: list[dict[str, str]],
) -> str:
    cards = []
    for key in [
        "casebook_rows",
        "ablation_rows",
        "q_policy_rows",
        "nab_visual_rows",
        "checks_passed",
        "checks_failed",
    ]:
        cards.append(
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
    attack_rows = [
        {
            "attack": item["attack"],
            "asset": item["asset"],
            "response": item["response"],
        }
        for item in ATTACK_MAP
    ]
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Claim Audit Report</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #172124;
      --muted: #5e6966;
      --line: #d8ded9;
      --wash: #f7faf7;
      --green: #145c5a;
      --gold: #ad741e;
      --red: #9b4237;
    }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--wash);
      color: var(--ink);
      line-height: 1.5;
    }}
    main {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 36px 28px 60px;
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: 34px;
      letter-spacing: 0;
    }}
    h2 {{
      margin-top: 34px;
      border-top: 2px solid var(--line);
      padding-top: 20px;
      font-size: 22px;
      letter-spacing: 0;
    }}
    p {{
      max-width: 900px;
      color: var(--muted);
    }}
    .metrics {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 12px;
      margin: 24px 0;
    }}
    .metric {{
      background: white;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 14px 16px;
    }}
    .metric span {{
      display: block;
      color: var(--muted);
      font-size: 13px;
    }}
    .metric strong {{
      display: block;
      margin-top: 5px;
      color: var(--green);
      font-size: 24px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      background: white;
      border: 1px solid var(--line);
      border-radius: 6px;
      overflow: hidden;
      margin-top: 12px;
    }}
    th, td {{
      border-bottom: 1px solid var(--line);
      padding: 9px 10px;
      vertical-align: top;
      text-align: left;
      font-size: 13px;
    }}
    th {{
      background: #e8f3ee;
      color: var(--green);
      font-weight: 750;
    }}
    tr:last-child td {{
      border-bottom: 0;
    }}
    .limits {{
      background: white;
      border-left: 5px solid var(--gold);
      padding: 14px 18px;
      border-radius: 4px;
    }}
  </style>
</head>
<body>
<main>
  <h1>Claim Audit Report</h1>
  <p>Generated from public-safe release-root assets. The report checks whether
  typed claim licensing, field interventions, Q-policy sensitivity, adapter
  boundaries, and resource components form a coherent reviewer workflow.</p>
  <section class="metrics">{''.join(cards)}</section>
  <h2>Audit Checks</h2>
  {html_table(check_rows, ["check", "status", "evidence"])}
  <h2>Claim Cards</h2>
  {html_table(claim_cards, ["event_id", "action", "layer", "G", "Q", "U", "licensed_sentence", "forbidden_sentence", "ablation_link"])}
  <h2>Primitive Stress Map</h2>
  {html_table(ablation_rows, ["display_id", "primitive_or_field", "metric_only_failure", "licensed_effect", "boundary"])}
  <h2>Q-Policy Sensitivity</h2>
  {html_table(q_rows, ["row", "group", "observed result", "claim effect", "boundary"])}
  <h2>Adapter Boundary Probe</h2>
  {html_table(nab_rows, ["display_id", "adapter_action", "licensed_sentence", "forbidden_sentence", "visual_role"])}
  <h2>Reviewer Attack Map</h2>
  {html_table(attack_rows, ["attack", "asset", "response"])}
  <h2>Current Limits</h2>
  <div class="limits">
    <p>The report does not rerun training, redistribute raw data, certify
    deployment safety, or check arbitrary natural-language claims. Its strongest
    next contribution path is release-root normalization of the full operator
    trace; batch claim-template admission is now represented as a companion
    runner.</p>
  </div>
</main>
</body>
</html>
"""


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    output_dir = resolve_output(root, args.output)

    failures: list[str] = []
    loaded: dict[str, tuple[list[dict[str, str]], list[str]]] = {}
    for label, rel_path in FILES.items():
        path = root / rel_path
        try:
            if label == "schema":
                continue
            loaded[label] = read_csv(path)
        except OSError as exc:
            failures.append(f"{rel_path}: could not read CSV: {exc}")

    try:
        schema = read_json(root / FILES["schema"])
    except (OSError, json.JSONDecodeError) as exc:
        schema = {}
        failures.append(f"{FILES['schema']}: could not read schema: {exc}")

    casebook_rows, casebook_header = loaded.get("casebook", ([], []))
    ablation_rows, _ = loaded.get("ablation", ([], []))
    q_rows, _ = loaded.get("q_policy", ([], []))
    resource_rows, _ = loaded.get("resource", ([], []))
    nab_rows, _ = loaded.get("nab_visual", ([], []))

    checks: list[dict[str, str]] = []
    add_check(
        checks,
        "AUD-01",
        "inputs present",
        not failures and all(loaded.get(label, ([], []))[0] for label in loaded),
        "all configured public-safe inputs loaded",
        "; ".join(failures) if failures else "one or more public-safe inputs are empty",
    )

    schema_fields, required_fields = required_schema_fields(schema)
    add_check(
        checks,
        "AUD-02",
        "schema header alignment",
        bool(schema_fields) and casebook_header == schema_fields,
        f"casebook header matches {len(schema_fields)} schema fields",
        f"casebook header={casebook_header}; schema fields={schema_fields}",
    )

    missing_required = [
        f"{row.get('event_id', 'unknown')}:{field}"
        for row in casebook_rows
        for field in required_fields
        if not row.get(field, "").strip()
    ]
    add_check(
        checks,
        "AUD-03",
        "required claim fields",
        not missing_required,
        f"{len(casebook_rows)} claim rows have required fields",
        "missing required cells: " + ", ".join(missing_required[:12]),
    )

    action_counts = Counter(row.get("projection_action", "") for row in casebook_rows)
    add_check(
        checks,
        "AUD-04",
        "action-family coverage",
        set(action_counts) == ACTION_FAMILIES and all(action_counts[a] for a in ACTION_FAMILIES),
        "five action families are present: "
        + ", ".join(f"{key}={action_counts[key]}" for key in sorted(ACTION_FAMILIES)),
        f"found actions {dict(action_counts)}; expected {sorted(ACTION_FAMILIES)}",
    )

    action_issues = action_semantic_issues(casebook_rows)
    add_check(
        checks,
        "AUD-05",
        "action semantics",
        not action_issues,
        "action-specific G/Q/U and bottom_T constraints hold",
        "; ".join(action_issues[:12]),
    )

    forbidden_missing = [
        row.get("event_id", "unknown")
        for row in casebook_rows
        if not row.get("forbidden_sentence", "").strip()
    ]
    add_check(
        checks,
        "AUD-06",
        "forbidden-claim firewall",
        not forbidden_missing,
        f"{len(casebook_rows)} claim rows expose forbidden overclaims",
        "missing forbidden sentence for: " + ", ".join(forbidden_missing),
    )

    ablation_by_source: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in ablation_rows:
        ablation_by_source[row.get("source_passport_row", "")].append(row)
    observed_primitives = {
        row.get("primitive_or_field", "") for row in ablation_rows if row.get("primitive_or_field")
    }
    add_check(
        checks,
        "AUD-07",
        "primitive stress coverage",
        observed_primitives == EXPECTED_PRIMITIVES,
        "G, Q, U, layer, support_anchor, and adapter_U_preorder are stress-tested",
        f"found primitives {sorted(observed_primitives)}; expected {sorted(EXPECTED_PRIMITIVES)}",
    )

    casebook_ids = {row.get("event_id", "") for row in casebook_rows}
    unlinked_casebook = sorted(casebook_ids - set(ablation_by_source))
    external_sources = sorted(set(ablation_by_source) - casebook_ids)
    allowed_external = [source for source in external_sources if source.startswith("NAB-VIS-")]
    disallowed_external = sorted(set(external_sources) - set(allowed_external))
    add_check(
        checks,
        "AUD-08",
        "casebook-to-stress join",
        not unlinked_casebook and not disallowed_external,
        "every casebook row has a stress link; only NAB support rows are external links",
        f"unlinked={unlinked_casebook}; disallowed_external={disallowed_external}",
    )

    q_non_upgrade = any("1500_of_1500_PASS" in row.get("observed result", "") for row in q_rows)
    positive_threshold_rows = [
        row for row in q_rows if row.get("group") == "positive decision cells"
    ]
    add_check(
        checks,
        "AUD-09",
        "Q-policy non-upgrading evidence",
        q_non_upgrade and len(positive_threshold_rows) == 4,
        "Q rows include 1500/1500 non-upgrading trace and four positive threshold cells",
        "missing 1500/1500 non-upgrade row or expected positive threshold rows",
    )

    resource_components = {row.get("component", "") for row in resource_rows}
    add_check(
        checks,
        "AUD-10",
        "resource boundary components",
        resource_components == EXPECTED_RESOURCE_COMPONENTS,
        "seven resource components expose what the release supports and excludes",
        f"found components {sorted(resource_components)}; expected {sorted(EXPECTED_RESOURCE_COMPONENTS)}",
    )

    nab_missing_forbidden = [
        row.get("display_id", "unknown")
        for row in nab_rows
        if not row.get("forbidden_sentence", "").strip()
    ]
    nab_has_suppression = any(row.get("adapter_action") == "suppress_fallback" for row in nab_rows)
    nab_has_profile_row = any(
        "profile" in " ".join(
            [
                row.get("visual_role", ""),
                row.get("ordinary_sentence", ""),
                row.get("licensed_sentence", ""),
            ]
        )
        for row in nab_rows
    )
    nab_has_incomparability = any(
        "incomparable" in row.get("preorder_relation", "") for row in nab_rows
    )
    add_check(
        checks,
        "AUD-11",
        "adapter boundary discipline",
        bool(nab_rows)
        and not nab_missing_forbidden
        and nab_has_suppression
        and nab_has_profile_row
        and nab_has_incomparability,
        "NAB support rows include forbidden claims, suppression, profile sensitivity, and preorder incomparability",
        "NAB boundary rows are missing forbidden claims, suppression, profile sensitivity, or preorder incomparability",
    )

    checks_failed = sum(1 for row in checks if row["status"] != "PASS")
    checks_passed = len(checks) - checks_failed
    claim_cards = build_claim_cards(casebook_rows, ablation_by_source)
    summary = {
        "status": "PASS" if checks_failed == 0 else "FAIL",
        "casebook_rows": len(casebook_rows),
        "action_counts": dict(sorted(action_counts.items())),
        "ablation_rows": len(ablation_rows),
        "q_policy_rows": len(q_rows),
        "nab_visual_rows": len(nab_rows),
        "resource_components": len(resource_rows),
        "checks_passed": checks_passed,
        "checks_failed": checks_failed,
        "tool_boundary": (
            "public-safe typed claim audit report; no raw-data reproduction, "
            "no arbitrary natural-language claim parser, no deployment certification"
        ),
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    write_json(output_dir / "claim_audit_summary.json", summary)
    write_csv(
        output_dir / "claim_audit_checks.csv",
        checks,
        ["check_id", "label", "status", "evidence"],
    )
    write_csv(
        output_dir / "claim_audit_cards.csv",
        claim_cards,
        [
            "event_id",
            "action",
            "layer",
            "G",
            "Q",
            "U",
            "licensed_sentence",
            "forbidden_sentence",
            "ablation_link",
            "boundary",
        ],
    )
    (output_dir / "claim_audit_report.md").write_text(
        build_markdown(
            summary,
            checks,
            claim_cards,
            ablation_rows,
            q_rows,
            nab_rows,
            resource_rows,
        ),
        encoding="utf-8",
    )
    (output_dir / "claim_audit_report.html").write_text(
        build_html(summary, checks, claim_cards, ablation_rows, q_rows, nab_rows),
        encoding="utf-8",
    )

    if checks_failed:
        print("FAIL claim audit report")
    else:
        print("PASS claim audit report")
    print(f"casebook_rows: {summary['casebook_rows']}")
    print(f"ablation_rows: {summary['ablation_rows']}")
    print(f"q_policy_rows: {summary['q_policy_rows']}")
    print(f"nab_visual_rows: {summary['nab_visual_rows']}")
    print(f"checks_passed: {checks_passed}")
    print(f"checks_failed: {checks_failed}")
    print("outputs:")
    for name in [
        "claim_audit_report.md",
        "claim_audit_report.html",
        "claim_audit_summary.json",
        "claim_audit_checks.csv",
        "claim_audit_cards.csv",
    ]:
        print(f"- {args.output.rstrip('/')}/{name}")
    return 0 if checks_failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
