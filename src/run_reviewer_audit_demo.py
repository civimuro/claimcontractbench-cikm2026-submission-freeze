#!/usr/bin/env python3
"""Build a reviewer-facing claim audit demo from paragraph-router outputs.

This runner connects the current application pieces without changing their
roles:

- paragraph front end: identify the actionable claim span and route;
- template catalog: decide whether an exact registered template can be called;
- reviewer claim intake: turn registered-template calls into concrete actions;
- route-boundary guide: keep unsupported-template and out-of-scope claims apart.

It is intentionally not a PDF parser or an autonomous reviewer.
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter
import html
import json
from pathlib import Path
import re

from run_reviewer_claim_intake import (
    build_template_rows,
    decide_intake,
    read_csv,
    short,
    write_csv,
    write_json,
)


FILES = {
    "template_schema": "artifact/claim_template_admission_schema_20260521.json",
    "template_cases": "artifact/claim_template_admission_cases_20260521.csv",
    "casebook": "data/claim_passport_casebook_20260519.csv",
    "nab_visual": "data/nab_adapter_visual_passport_rows_20260519.csv",
    "selected_eval": "reports/paragraph_claim_span_router_external_eval_guided_20260521",
    "holdout_eval": "reports/paragraph_claim_span_router_holdout_eval_guided_20260521",
}

ROUTE_LABELS = {
    "CALL_REGISTERED_TEMPLATE",
    "NEEDS_TEMPLATE_ADMISSION",
    "OUT_OF_SCOPE_DO_NOT_CALL",
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate reviewer-facing audit cards from paragraph router predictions."
    )
    parser.add_argument("--root", default=".", help="Workspace root. Default: current directory.")
    parser.add_argument(
        "--output",
        default="reports/reviewer_facing_audit_demo_20260521",
        help="Report output directory. Relative paths are resolved under root.",
    )
    parser.add_argument(
        "--selected-eval",
        default=FILES["selected_eval"],
        help="Selected paragraph evaluation directory.",
    )
    parser.add_argument(
        "--holdout-eval",
        default=FILES["holdout_eval"],
        help="Fresh holdout paragraph evaluation directory.",
    )
    return parser.parse_args()


def resolve(root: Path, value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = root / path
    return path.resolve()


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


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


def load_eval_bundle(eval_dir: Path, source_name: str) -> dict[str, object]:
    items, _ = read_csv(eval_dir / "noisy_claim_span_router_items.csv")
    decisions, _ = read_csv(eval_dir / "noisy_claim_span_router_decisions.csv")
    summary = load_json(eval_dir / "noisy_claim_span_router_summary.json")
    item_by_id = {row["noisy_id"]: row for row in items}
    decision_by_id = {row["noisy_id"]: row for row in decisions}
    rows = []
    for noisy_id, item in item_by_id.items():
        decision = decision_by_id.get(noisy_id, {})
        rows.append(
            {
                "source_name": source_name,
                "noisy_id": noisy_id,
                "source_title": item.get("source_title", ""),
                "source_family": item.get("source_family", ""),
                "snippet_text": item.get("snippet_text", ""),
                "gold_route_label": item.get("gold_route_label", ""),
                "predicted_route_label": decision.get("predicted_route_label", ""),
                "gold_template_id": item.get("gold_template_id", ""),
                "predicted_template_id": decision.get("predicted_template_id", ""),
                "gold_claim_span": item.get("gold_claim_span", ""),
                "predicted_claim_span": decision.get("predicted_claim_span", ""),
                "span_match": decision.get("span_match", ""),
                "route_match": decision.get("route_match", ""),
                "joint_match": decision.get("joint_match", ""),
            }
        )
    return {
        "rows": rows,
        "items": items,
        "decisions": decisions,
        "summary": summary,
    }


def load_templates(root: Path) -> tuple[dict[str, dict[str, str]], dict[str, dict[str, str]], dict[str, dict[str, str]]]:
    template_schema = load_json(root / FILES["template_schema"])
    template_cases, _ = read_csv(root / FILES["template_cases"])
    casebook, _ = read_csv(root / FILES["casebook"])
    nab_visual, _ = read_csv(root / FILES["nab_visual"])
    critical_fields = list(template_schema.get("critical_fields_for_admission", []))
    templates = build_template_rows(template_cases, critical_fields)
    return (
        templates,
        {row.get("event_id", ""): row for row in casebook},
        {row.get("display_id", ""): row for row in nab_visual},
    )


def final_action_for_row(
    row: dict[str, str],
    templates: dict[str, dict[str, str]],
    casebook_by_id: dict[str, dict[str, str]],
    nab_by_id: dict[str, dict[str, str]],
) -> dict[str, str]:
    route = row["predicted_route_label"]
    template_id = row["predicted_template_id"]
    claim = row["predicted_claim_span"]
    audit_id = f"{row['source_name']}-{row['noisy_id']}"

    if route == "CALL_REGISTERED_TEMPLATE":
        intake_row = {
            "intake_id": audit_id,
            "template_id": template_id,
            "submitted_claim": claim,
            "expected_decision": "",
        }
        decision = decide_intake(intake_row, templates, casebook_by_id, nab_by_id)
        return {
            "tool_decision": decision["decision"],
            "recommended_output": decision["recommended_output"],
            "reviewer_message": decision["explanation"],
            "source_anchor": decision["source_anchor"],
        }

    if route == "NEEDS_TEMPLATE_ADMISSION":
        return {
            "tool_decision": "OPEN_ADMISSION_TICKET",
            "recommended_output": "unsupported_template",
            "reviewer_message": (
                "The claim is in the empirical evaluation family, but no registered "
                "template licenses it yet. Admit a typed adapter before accepting, "
                "weakening, rewriting, supporting, or suppressing the claim."
            ),
            "source_anchor": "",
        }

    if route == "OUT_OF_SCOPE_DO_NOT_CALL":
        return {
            "tool_decision": "DO_NOT_CALL_CLAIM_RUNNER",
            "recommended_output": "bottom_T",
            "reviewer_message": (
                "This sentence asks for legal, policy, ethics, deployment, code, "
                "mechanistic, paper-acceptance, or other non-metric judgment outside "
                "the current claim-governance object."
            ),
            "source_anchor": "",
        }

    return {
        "tool_decision": "INVALID_ROUTE",
        "recommended_output": "bottom_T",
        "reviewer_message": "The front-end route label is invalid.",
        "source_anchor": "",
    }


def build_cards(
    rows: list[dict[str, str]],
    templates: dict[str, dict[str, str]],
    casebook_by_id: dict[str, dict[str, str]],
    nab_by_id: dict[str, dict[str, str]],
) -> list[dict[str, str]]:
    cards: list[dict[str, str]] = []
    for row in rows:
        final_action = final_action_for_row(row, templates, casebook_by_id, nab_by_id)
        cards.append(
            {
                "audit_id": f"{row['source_name']}-{row['noisy_id']}",
                "source_packet": row["source_name"],
                "source_family": row["source_family"],
                "source_title": row["source_title"],
                "claim_span": row["predicted_claim_span"],
                "route_label": row["predicted_route_label"],
                "template_id": row["predicted_template_id"],
                "tool_decision": final_action["tool_decision"],
                "recommended_output": final_action["recommended_output"],
                "reviewer_message": final_action["reviewer_message"],
                "source_anchor": final_action["source_anchor"],
                "span_match": row["span_match"],
                "route_match": row["route_match"],
                "joint_match": row["joint_match"],
                "snippet_excerpt": short(row["snippet_text"], 260),
            }
        )
    return cards


def summarize(cards: list[dict[str, str]], eval_summaries: dict[str, dict[str, object]]) -> dict[str, object]:
    decision_counts = Counter(row["tool_decision"] for row in cards)
    route_counts = Counter(row["route_label"] for row in cards)
    validation_counts = Counter(row["joint_match"] for row in cards)
    return {
        "status": "PASS",
        "audit_cards": len(cards),
        "source_packets": sorted(eval_summaries),
        "route_counts": dict(sorted(route_counts.items())),
        "decision_counts": dict(sorted(decision_counts.items())),
        "registered_template_cards": route_counts.get("CALL_REGISTERED_TEMPLATE", 0),
        "admission_ticket_cards": decision_counts.get("OPEN_ADMISSION_TICKET", 0),
        "out_of_scope_cards": decision_counts.get("DO_NOT_CALL_CLAIM_RUNNER", 0),
        "joint_validation_pass": validation_counts.get("PASS", 0),
        "joint_validation_fail": validation_counts.get("FAIL", 0),
        "selected_route_accuracy": eval_summaries["selected"].get("route_accuracy", ""),
        "selected_joint_accuracy": eval_summaries["selected"].get("joint_span_route_accuracy", ""),
        "holdout_route_accuracy": eval_summaries["holdout"].get("route_accuracy", ""),
        "holdout_joint_accuracy": eval_summaries["holdout"].get("joint_span_route_accuracy", ""),
    }


def build_markdown(
    summary: dict[str, object],
    checks: list[dict[str, str]],
    cards: list[dict[str, str]],
) -> str:
    lines: list[str] = []
    lines.append("# Reviewer-Facing Claim Audit Demo")
    lines.append("")
    lines.append("Status: generated from paragraph router outputs and registered template intake.")
    lines.append("")
    lines.append("## What This Demo Does")
    lines.append("")
    lines.append(
        "The demo shows the usable reviewer workflow: paragraph text is reduced to "
        "an actionable claim span, routed to a registered template, adapter "
        "admission ticket, or out-of-scope stop, and then rendered as a concrete "
        "reviewer-facing decision."
    )
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Item | Value |")
    lines.append("| --- | ---: |")
    for key in [
        "audit_cards",
        "registered_template_cards",
        "admission_ticket_cards",
        "out_of_scope_cards",
        "joint_validation_pass",
        "joint_validation_fail",
        "selected_route_accuracy",
        "selected_joint_accuracy",
        "holdout_route_accuracy",
        "holdout_joint_accuracy",
    ]:
        lines.append(f"| {key} | {summary[key]} |")
    lines.append("")
    lines.append("## Checks")
    lines.append("")
    lines.append("| Check | Status | Evidence |")
    lines.append("| --- | --- | --- |")
    for row in checks:
        lines.append(f"| {row['check_id']} {row['label']} | {row['status']} | {short(row['evidence'], 220)} |")
    lines.append("")
    lines.append("## Decision Mix")
    lines.append("")
    lines.append("| Decision | Count |")
    lines.append("| --- | ---: |")
    for decision, count in summary["decision_counts"].items():
        lines.append(f"| {decision} | {count} |")
    lines.append("")
    lines.append("## Audit Cards")
    lines.append("")
    lines.append("| ID | Route | Decision | Claim | Recommended Output |")
    lines.append("| --- | --- | --- | --- | --- |")
    for row in cards:
        lines.append(
            f"| {row['audit_id']} | {row['route_label']} | {row['tool_decision']} | "
            f"{short(row['claim_span'], 130)} | {short(row['recommended_output'], 130)} |"
        )
    lines.append("")
    lines.append("## Boundary")
    lines.append("")
    lines.append(
        "This is a reviewer-facing component for short excerpts or selected "
        "paragraphs. It does not parse full PDFs, decide paper acceptance, certify "
        "deployment safety, or create new domain templates without admission."
    )
    lines.append("")
    return "\n".join(lines)


def html_escape(value: object) -> str:
    return html.escape(str(value if value is not None else ""))


def html_table(rows: list[dict[str, str]], columns: list[str]) -> str:
    head = "".join(f"<th>{html_escape(column)}</th>" for column in columns)
    body = []
    for row in rows:
        cells = "".join(f"<td>{html_escape(short(row.get(column, ''), 260))}</td>" for column in columns)
        body.append(f"<tr>{cells}</tr>")
    return f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def build_html(summary: dict[str, object], checks: list[dict[str, str]], cards: list[dict[str, str]]) -> str:
    metrics = [
        ("Audit cards", summary["audit_cards"]),
        ("Template calls", summary["registered_template_cards"]),
        ("Admission tickets", summary["admission_ticket_cards"]),
        ("Out of scope", summary["out_of_scope_cards"]),
        ("Validation pass", summary["joint_validation_pass"]),
        ("Validation fail", summary["joint_validation_fail"]),
    ]
    metric_html = "".join(
        f"<section class='metric'><span>{html_escape(label)}</span><strong>{html_escape(value)}</strong></section>"
        for label, value in metrics
    )
    check_rows = [
        {
            "check": f"{row['check_id']} {row['label']}",
            "status": row["status"],
            "evidence": row["evidence"],
        }
        for row in checks
    ]
    decision_rows = [
        {"decision": decision, "count": str(count)}
        for decision, count in summary["decision_counts"].items()
    ]
    decision_options = "".join(
        f"<option value='{html_escape(decision)}'>{html_escape(decision)}</option>"
        for decision in summary["decision_counts"]
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Reviewer-Facing Claim Audit Demo</title>
  <style>
    :root {{
      --paper: #fbfaf6;
      --ink: #162322;
      --muted: #64706c;
      --line: #d9ddd2;
      --sage: #406357;
      --blue: #315f83;
      --amber: #a96f20;
      --red: #923c38;
      --white: #ffffff;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--paper);
      color: var(--ink);
      font-family: Aptos, "Segoe UI", sans-serif;
      line-height: 1.48;
    }}
    main {{
      max-width: 1240px;
      margin: 0 auto;
      padding: 34px 28px 58px;
    }}
    .topline {{
      display: grid;
      grid-template-columns: minmax(0, 1.25fr) minmax(280px, .75fr);
      gap: 28px;
      align-items: end;
      border-bottom: 2px solid var(--ink);
      padding-bottom: 22px;
    }}
    h1 {{
      margin: 0;
      font-family: Charter, Georgia, serif;
      font-size: 38px;
      line-height: 1.05;
      letter-spacing: 0;
    }}
    .lede {{
      margin: 12px 0 0;
      max-width: 780px;
      color: var(--muted);
      font-size: 16px;
    }}
    .stamp {{
      border-left: 5px solid var(--amber);
      padding: 12px 0 12px 16px;
      color: var(--muted);
      font-size: 13px;
    }}
    h2 {{
      margin: 34px 0 12px;
      font-size: 20px;
      letter-spacing: 0;
    }}
    .metrics {{
      display: grid;
      grid-template-columns: repeat(6, minmax(0, 1fr));
      gap: 10px;
      margin-top: 22px;
    }}
    .metric {{
      background: var(--white);
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 13px 14px;
      min-height: 82px;
    }}
    .metric span {{
      display: block;
      color: var(--muted);
      font-size: 12px;
    }}
    .metric strong {{
      display: block;
      margin-top: 7px;
      color: var(--sage);
      font-size: 26px;
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
      vertical-align: top;
      text-align: left;
      font-size: 12px;
    }}
    th {{
      color: var(--sage);
      background: #edf2eb;
      font-weight: 760;
    }}
    tr:last-child td {{ border-bottom: 0; }}
    .cards {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(330px, 1fr));
      gap: 12px;
    }}
    .toolbar {{
      display: grid;
      grid-template-columns: minmax(220px, 1fr) minmax(180px, 260px) minmax(180px, 260px);
      gap: 10px;
      margin: 12px 0;
    }}
    input, select {{
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--white);
      color: var(--ink);
      font: inherit;
      padding: 10px 11px;
    }}
    .card {{
      background: var(--white);
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 15px;
    }}
    .card h3 {{
      margin: 0 0 8px;
      font-size: 14px;
      letter-spacing: 0;
    }}
    .pillrow {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-bottom: 10px;
    }}
    .pill {{
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 3px 8px;
      font-size: 11px;
      color: var(--muted);
      background: #f6f7f3;
      white-space: nowrap;
    }}
    .pill.route {{ color: var(--blue); }}
    .pill.decision {{ color: var(--amber); }}
    .claim {{
      margin: 8px 0;
      font-family: Charter, Georgia, serif;
      font-size: 15px;
    }}
    .output {{
      border-left: 4px solid var(--sage);
      padding-left: 10px;
      color: var(--muted);
      font-size: 12px;
    }}
    .warn {{
      color: var(--red);
      font-weight: 700;
    }}
    .hidden {{ display: none; }}
    .countline {{
      margin: 8px 0 12px;
      color: var(--muted);
      font-size: 13px;
    }}
    @media (max-width: 840px) {{
      .topline {{ grid-template-columns: 1fr; }}
      .metrics {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .toolbar {{ grid-template-columns: 1fr; }}
      h1 {{ font-size: 31px; }}
    }}
  </style>
</head>
<body>
<main>
  <section class="topline">
    <div>
      <h1>Reviewer-Facing Claim Audit Demo</h1>
      <p class="lede">A compact demonstration of the complete claim-governance workflow:
      paragraph span routing, template lookup, admission boundary, and deterministic
      reviewer-facing action.</p>
    </div>
    <aside class="stamp">
      Selected route accuracy: {html_escape(summary["selected_route_accuracy"])}<br>
      Holdout route accuracy: {html_escape(summary["holdout_route_accuracy"])}<br>
      Scope: short excerpts, not full-PDF parsing
    </aside>
  </section>
  <section class="metrics">{metric_html}</section>
  <h2>Checks</h2>
  {html_table(check_rows, ["check", "status", "evidence"])}
  <h2>Decision Mix</h2>
  {html_table(decision_rows, ["decision", "count"])}
  <h2>Audit Cards</h2>
  <section class="toolbar" aria-label="Audit card filters">
    <input id="search" type="search" placeholder="Search claims, outputs, or source titles">
    <select id="routeFilter" aria-label="Route filter">
      <option value="">All routes</option>
      <option value="CALL_REGISTERED_TEMPLATE">CALL_REGISTERED_TEMPLATE</option>
      <option value="NEEDS_TEMPLATE_ADMISSION">NEEDS_TEMPLATE_ADMISSION</option>
      <option value="OUT_OF_SCOPE_DO_NOT_CALL">OUT_OF_SCOPE_DO_NOT_CALL</option>
    </select>
    <select id="decisionFilter" aria-label="Decision filter">
      <option value="">All decisions</option>
      {decision_options}
    </select>
  </section>
  <p id="countline" class="countline"></p>
  <section class="cards">
    {''.join(build_card_html(row) for row in cards)}
  </section>
  <h2>Boundary</h2>
  <p class="lede">This component helps reviewers and authors decide whether a
  claim is licensed, should be rewritten, requires template admission, or must
  stay outside the metric-to-claim runner. It does not decide paper acceptance,
  legal compliance, deployment safety, or mechanistic truth.</p>
</main>
<script>
  const cards = Array.from(document.querySelectorAll("[data-card]"));
  const search = document.querySelector("#search");
  const routeFilter = document.querySelector("#routeFilter");
  const decisionFilter = document.querySelector("#decisionFilter");
  const countline = document.querySelector("#countline");
  function applyFilters() {{
    const query = search.value.trim().toLowerCase();
    const route = routeFilter.value;
    const decision = decisionFilter.value;
    let visible = 0;
    for (const card of cards) {{
      const haystack = card.dataset.search;
      const okQuery = !query || haystack.includes(query);
      const okRoute = !route || card.dataset.route === route;
      const okDecision = !decision || card.dataset.decision === decision;
      const show = okQuery && okRoute && okDecision;
      card.classList.toggle("hidden", !show);
      if (show) visible += 1;
    }}
    countline.textContent = `${{visible}} of ${{cards.length}} cards visible`;
  }}
  search.addEventListener("input", applyFilters);
  routeFilter.addEventListener("change", applyFilters);
  decisionFilter.addEventListener("change", applyFilters);
  applyFilters();
</script>
</body>
</html>
"""


def build_card_html(row: dict[str, str]) -> str:
    failed = row.get("joint_match") == "FAIL"
    mismatch = '<span class="warn">validation mismatch</span>' if failed else ""
    searchable = " ".join(
        [
            row.get("audit_id", ""),
            row.get("source_packet", ""),
            row.get("source_family", ""),
            row.get("source_title", ""),
            row.get("claim_span", ""),
            row.get("tool_decision", ""),
            row.get("recommended_output", ""),
            row.get("reviewer_message", ""),
        ]
    ).lower()
    return (
        f'    <article class="card" data-card data-route="{html_escape(row["route_label"])}" '
        f'data-decision="{html_escape(row["tool_decision"])}" data-search="{html_escape(searchable)}">\n'
        f'      <h3>{html_escape(row["audit_id"])} {mismatch}</h3>\n'
        '      <div class="pillrow">\n'
        f'        <span class="pill">{html_escape(row["source_packet"])}</span>\n'
        f'        <span class="pill route">{html_escape(row["route_label"])}</span>\n'
        f'        <span class="pill decision">{html_escape(row["tool_decision"])}</span>\n'
        '      </div>\n'
        f'      <p class="claim">{html_escape(row["claim_span"])}</p>\n'
        f'      <p class="output">{html_escape(short(row["recommended_output"], 220))}</p>\n'
        f'      <p class="output">{html_escape(short(row["reviewer_message"], 220))}</p>\n'
        '    </article>\n'
    )


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    output_dir = resolve(root, args.output)

    selected_dir = resolve(root, args.selected_eval)
    holdout_dir = resolve(root, args.holdout_eval)
    selected = load_eval_bundle(selected_dir, "selected")
    holdout = load_eval_bundle(holdout_dir, "holdout")
    templates, casebook_by_id, nab_by_id = load_templates(root)

    rows = list(selected["rows"]) + list(holdout["rows"])
    cards = build_cards(rows, templates, casebook_by_id, nab_by_id)
    eval_summaries = {
        "selected": selected["summary"],
        "holdout": holdout["summary"],
    }
    summary = summarize(cards, eval_summaries)

    checks: list[dict[str, str]] = []
    add_check(
        checks,
        "RAD-01",
        "source coverage",
        len(selected["rows"]) == 36 and len(holdout["rows"]) == 36 and len(cards) == 72,
        "selected and holdout paragraph evaluations each contribute 36 audit cards",
        f"selected={len(selected['rows'])}; holdout={len(holdout['rows'])}; cards={len(cards)}",
    )
    invalid_routes = sorted({row["audit_id"] for row in cards if row["route_label"] not in ROUTE_LABELS})
    add_check(
        checks,
        "RAD-02",
        "valid route labels",
        not invalid_routes,
        "all cards use a valid route label",
        f"invalid route labels in {invalid_routes}",
    )
    template_call_errors = [
        row["audit_id"]
        for row in cards
        if row["route_label"] == "CALL_REGISTERED_TEMPLATE" and not row["template_id"]
    ]
    add_check(
        checks,
        "RAD-03",
        "template calls have template ids",
        not template_call_errors,
        "all registered-template calls carry a concrete template id",
        f"registered calls without template id: {template_call_errors}",
    )
    private_rows = [row["audit_id"] for row in cards if contains_private_marker(row)]
    add_check(
        checks,
        "RAD-04",
        "public-safe card text",
        not private_rows,
        "audit cards contain no private path, connector, or credential markers",
        f"private markers found in {private_rows}",
    )
    false_template_calls = [
        row["audit_id"]
        for row in cards
        if row["route_label"] == "CALL_REGISTERED_TEMPLATE"
        and row["tool_decision"] not in {
            "ACCEPT_LICENSED",
            "REWRITE_TO_LICENSED",
            "SUPPRESS_BOTTOM",
            "SUPPORT_ONLY_REWRITE",
            "REJECT_PATCHWORK",
            "REJECT_UNKNOWN_TEMPLATE",
        }
    ]
    add_check(
        checks,
        "RAD-05",
        "registered calls resolve to intake decisions",
        not false_template_calls,
        "all registered-template calls resolve through deterministic intake",
        f"unresolved registered calls: {false_template_calls}",
    )
    add_check(
        checks,
        "RAD-06",
        "holdout validation",
        holdout["summary"].get("joint_span_route_accuracy") == "1.000",
        "fresh holdout has perfect joint span-route validation under the locked guide",
        f"holdout joint accuracy={holdout['summary'].get('joint_span_route_accuracy')}",
    )
    selected_joint_fails = [
        row["audit_id"]
        for row in cards
        if row["source_packet"] == "selected" and row["joint_match"] == "FAIL"
    ]
    add_check(
        checks,
        "RAD-07",
        "selected residual boundary recorded",
        selected_joint_fails == ["selected-NSR-025"],
        "selected packet retains the known cognitive/construct-validity residual boundary",
        f"unexpected selected residuals: {selected_joint_fails}",
    )

    summary["checks_passed"] = sum(1 for row in checks if row["status"] == "PASS")
    summary["checks_failed"] = sum(1 for row in checks if row["status"] == "FAIL")
    if summary["checks_failed"]:
        summary["status"] = "FAIL"

    output_dir.mkdir(parents=True, exist_ok=True)
    card_fields = [
        "audit_id",
        "source_packet",
        "source_family",
        "source_title",
        "claim_span",
        "route_label",
        "template_id",
        "tool_decision",
        "recommended_output",
        "reviewer_message",
        "source_anchor",
        "span_match",
        "route_match",
        "joint_match",
        "snippet_excerpt",
    ]
    write_csv(output_dir / "reviewer_audit_cards.csv", cards, card_fields)
    write_csv(output_dir / "reviewer_audit_demo_checks.csv", checks, ["check_id", "label", "status", "evidence"])
    write_json(output_dir / "reviewer_audit_demo_summary.json", summary)
    (output_dir / "reviewer_audit_demo_report.md").write_text(
        build_markdown(summary, checks, cards), encoding="utf-8"
    )
    (output_dir / "reviewer_audit_demo_report.html").write_text(
        build_html(summary, checks, cards), encoding="utf-8"
    )

    if summary["checks_failed"]:
        print("FAIL reviewer audit demo")
        print(f"checks_failed: {summary['checks_failed']}")
        return 1
    print("PASS reviewer audit demo")
    print(f"audit_cards: {summary['audit_cards']}")
    print(f"registered_template_cards: {summary['registered_template_cards']}")
    print(f"admission_ticket_cards: {summary['admission_ticket_cards']}")
    print(f"out_of_scope_cards: {summary['out_of_scope_cards']}")
    print("outputs:")
    for name in [
        "reviewer_audit_demo_report.md",
        "reviewer_audit_demo_report.html",
        "reviewer_audit_demo_summary.json",
        "reviewer_audit_demo_checks.csv",
        "reviewer_audit_cards.csv",
    ]:
        rel = output_dir.relative_to(root) / name if output_dir.is_relative_to(root) else output_dir / name
        print(f"- {rel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
