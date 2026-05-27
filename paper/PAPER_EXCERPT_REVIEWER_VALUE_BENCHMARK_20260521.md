# Paper Excerpt Reviewer-Value Benchmark (2026-05-21)

Status: `BOUNDED_SELECTED_EXCERPT_VALIDATION`.

Purpose: test whether the claim-audit component gives useful and safe
reviewer-facing decisions for selected, public-safe paper excerpt anchors
without claiming autonomous full-paper review.

## Why This Layer Exists

The prior 40-paper benchmark is a public-safe paraphrased claim benchmark. It
is useful for fail-closed action consistency, but it can be attacked as a
closed-form route/action table because the external rows mostly become
`UNSUPPORTED_TEMPLATE` or `OUT_OF_SCOPE`.

This layer adds a stricter reviewer-facing object:

- 80 external source-anchored excerpt units;
- 8 registered-template controls;
- 40 external source papers;
- 22 source families;
- explicit reviewer comments and overclaim hazards;
- a prediction packet for future LLM/human front-end scoring;
- a transparent keyword baseline reported separately.

The excerpt anchors are intentionally short public-safe micro-excerpts, mostly
title/metadata anchors in this release. Candidate claims and reviewer comments
are public-safe author paraphrases. This means the benchmark is stronger than a
free-floating paraphrase table, but still not a full body-text/PDF benchmark.

## Assets

- `artifact/paper_excerpt_reviewer_value_schema_20260521.json`
- `artifact/paper_excerpt_reviewer_value_cases_20260521.csv`
- `src/run_paper_excerpt_reviewer_value_benchmark.py`
- generated report: `reports/paper_excerpt_reviewer_value_benchmark_20260521/paper_excerpt_reviewer_value_report.md`
- optional baseline report: `reports/paper_excerpt_reviewer_value_benchmark_text_rules_20260521/paper_excerpt_reviewer_value_report.md`

Default command:

```bash
python3 src/run_paper_excerpt_reviewer_value_benchmark.py --output reports/paper_excerpt_reviewer_value_benchmark_20260521
```

Transparent baseline command:

```bash
python3 src/run_paper_excerpt_reviewer_value_benchmark.py --baseline text_rules --output reports/paper_excerpt_reviewer_value_benchmark_text_rules_20260521
```

## Default Result

```text
PASS paper excerpt reviewer-value benchmark
front_end_mode: human_gold_oracle
excerpt_rows: 88
source_papers: 40
source_families: 22
tool_decision_accuracy: 1.000
unsafe_release_rate: 0.000
autonomous_full_paper_review_supported: no
```

The default result uses human-gold routes as an oracle front end. It therefore
validates the deterministic claim-governance backend once a selected excerpt
and route are supplied. It does not prove autonomous extraction from full
papers.

## Transparent Baseline Result

The `text_rules` baseline is intentionally simple and is kept as a negative
control:

```text
PASS paper excerpt reviewer-value benchmark
front_end_mode: text_rules_baseline
excerpt_rows: 88
source_papers: 40
source_families: 22
tool_decision_accuracy: 0.943
unsafe_release_rate: 0.000
autonomous_full_paper_review_supported: no
```

The baseline records five route/action errors while maintaining zero unsafe
release. It falsely stops three relevant in-scope rows and falsely sends two
out-of-scope rows to admission rather than stopping them. This is useful
because it shows the benchmark is not just reporting a convenient 100% route
score: shallow keyword routing misses hard boundary cases.

## What This Supports

The benchmark supports a bounded application claim:

> For selected source-anchored empirical excerpts, the component can convert
> gold-routed registered controls into deterministic actions and can fail
> closed for unsupported or out-of-scope claims while producing reviewer-facing
> comments.

It also supports a practical engineering claim:

> The tool now has a measurable reviewer-facing benchmark surface with scale,
> source joins, public-safety checks, route/action metrics, unsafe-release
> tracking, and a prediction packet for future LLM or human front-end runs.

## What It Does Not Support

It does not support:

- autonomous full-paper review;
- direct PDF parsing;
- paper acceptance decisions;
- legal, deployment, proof, code, or ethics certification;
- human reviewer utility without a future user study;
- treating LLM route predictions as gold labels.

## Remaining Upgrade Path

The next true upgrade is an independently annotated front-end benchmark:

1. collect real body/abstract excerpt anchors under an explicit rights policy;
2. allow zero, one, or multiple candidate claims per excerpt;
3. run at least two independent annotators and report agreement;
4. score LLM front-end span/route/template predictions against frozen gold;
5. compare against LLM-only, keyword-only, and no-tool reviewer baselines;
6. keep negative results such as false stops and admission-vs-out-of-scope
   confusions in the report.
