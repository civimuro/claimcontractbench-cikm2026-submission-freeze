# Reviewer Quickstart Release Snapshot (2026-05-20)

Status: `PUBLIC_FRIENDLY_SUBMISSION_SNAPSHOT_2026-06-01`.

This quickstart is written for the public/reviewer artifact root. It is not tied
to private coordination directories or local machine paths.

This archive is a manifest-controlled derived-asset release. Running these
commands creates reviewer reports under `reports/`; those reports are generated
inspection outputs, not raw-data reproductions and not a claim that raw
third-party datasets are redistributed.

License scope is defined in `LICENSE.md`: executable code is Apache-2.0,
derived non-code resource materials are CC-BY-4.0, and raw third-party data is
not redistributed.

Maintainer note: when creating a local submission snapshot from the full project
workspace, run the release builder from the `WORKSPACE` resource root. Once the
snapshot archive is created or unpacked, the commands below are run from that
release root.

## Requirements

- Python 3.9 or newer.
- No third-party Python packages for the first inspection path.
- No raw dataset download.
- No GPU training.

## First Inspection Commands

From the release root:

```bash
python3 src/validate_release_surface.py
python3 src/run_projection_smoke.py
python3 src/run_claim_audit_report.py --output reports/claim_audit_report_20260521
python3 src/run_claim_template_admission.py --output reports/claim_template_admission_20260521
python3 src/run_reviewer_claim_intake.py --output reports/reviewer_claim_intake_20260521
python3 src/run_claim_audit_gold_probe.py --output reports/claim_audit_gold_probe_20260521
python3 src/run_paper_claim_gold_benchmark.py --output reports/paper_claim_gold_benchmark_20260521
python3 src/run_paper_excerpt_reviewer_value_benchmark.py --output reports/paper_excerpt_reviewer_value_benchmark_20260521
python3 src/run_paper_claim_annotation_agreement.py --output reports/paper_claim_annotation_agreement_20260521
python3 src/run_reviewer_audit_demo.py --output reports/reviewer_facing_audit_demo_20260521
python3 src/run_reviewer_audit_demo_regression.py \
  --demo-dir reports/reviewer_facing_audit_demo_20260521 \
  --output reports/reviewer_facing_audit_demo_regression_20260521
```

Expected output for the surface validator:

```text
PASS release surface validation
root: /path/to/release/root
manifest: artifact/release_manifest_20260520.csv
rows: 110
required_files: 110
public_safe_rows: 110
raw_data_rows: 0
```

## Fast LLM-Assisted Path

For users who want to review a paper with an LLM front end, start here:

```bash
python3 src/run_llm_claim_review_packet.py \
  --input artifact/llm_claim_review_packet_template_20260527.csv \
  --output reports/llm_claim_review_packet_20260527
```

Expected output:

```text
PASS LLM claim review packet
packet_rows: 4
call_registered_template: 2
needs_template_admission: 1
out_of_scope: 1
unsafe_release_rate: 0.000
rejected_unknown_template: 0
invalid_route_rows: 0
checks_passed: 14
checks_failed: 0
```

Then follow `artifact/LLM_ASSISTED_REVIEW_QUICKSTART_20260527.md` to ask an LLM
to produce the same CSV format for a new paper. The LLM performs claim
extraction and routing only; it does not license claims.

Expected output for the projection smoke runner:

```text
PASS projection smoke runner
root: /path/to/release/root
smoke_rows: 5
emit_as_written: 1
relabel_as_upper_bound: 1
rewrite_to_decision_local: 1
suppress_fallback: 1
weaken_to_diagnostic: 1
```

Expected output for the claim audit report runner:

```text
PASS claim audit report
casebook_rows: 5
ablation_rows: 6
q_policy_rows: 8
nab_visual_rows: 5
checks_passed: 11
checks_failed: 0
```

Expected output for the reviewer claim-intake runner:

```text
PASS reviewer claim intake
intake_rows: 8
accepted: 1
rewritten: 3
suppressed: 1
support_only: 1
rejected: 2
checks_passed: 9
checks_failed: 0
```

Expected output for the claim-audit gold probe:

```text
PASS claim audit gold probe
gold_rows: 18
registered_template_rows: 8
adapter_needed_rows: 6
out_of_scope_rows: 4
decision_matches: 18
autonomous_routing_supported: no
```

Expected output for the paper-claim gold benchmark:

```text
PASS paper claim gold benchmark
external_papers: 40
external_claim_rows: 120
registered_control_rows: 8
total_claim_rows: 128
current_action_mismatches: 0
unsupported_template_rate_external_claims: 0.667
false_release_rate_unsupported_or_out_of_scope: 0.000
autonomous_full_paper_routing_supported: no
```

Expected output for the paper-excerpt decision-surface benchmark:

```text
PASS paper excerpt decision-surface benchmark
front_end_mode: human_gold_oracle
excerpt_rows: 88
source_papers: 40
source_families: 22
tool_decision_accuracy: 1.000
unsafe_release_rate: 0.000
autonomous_full_paper_review_supported: no
```

Here, `human_gold_oracle`, `gold benchmark`, and `tool_decision_accuracy` refer
to curated benchmark labels used for this release-check surface. They are not
independent reviewer-study evidence and do not support autonomous full-paper
review.

Expected output for the paper-claim annotation agreement scaffold:

```text
PASS paper claim annotation agreement scaffold
annotation_status: PENDING_SECOND_ANNOTATOR
annotation_rows: 128
fully_filled_rows: 0
agreement_computed: no
checks_passed: 10
```

Expected output for the reviewer-facing audit demo:

```text
PASS reviewer audit demo
audit_cards: 72
registered_template_cards: 8
admission_ticket_cards: 43
out_of_scope_cards: 21
```

Expected output for the reviewer-facing audit demo regression:

```text
PASS reviewer audit demo regression
audit_cards_checked: 72
checks_passed: 11
locked_registered_template_controls: 8
locked_fail_closed_boundary: yes
```

Expected output for the claim template admission runner:

```text
PASS claim template admission
templates: 9
admitted_mainline: 5
admitted_support_only: 3
boundary_probe: 0
rejected: 1
checks_passed: 10
checks_failed: 0
```

## What These Commands Check

The surface validator reads `artifact/release_manifest_20260520.csv` and checks that:

- every required release file exists;
- paths are release-root relative;
- no release row points into private coordination or `.git/` paths;
- required release files do not contain private coordination paths, local
  machine paths, or credential markers;
- no manifest row is marked as raw data;
- every manifest row is marked public-safe.
- required CSV and JSON files are structurally readable;
- the claim passport casebook header matches the public release schema;
- projection-action and claim-layer values respect the schema enums;
- casebook dataset/scenario ids join to the public manifests.

The projection smoke runner reads
`artifact/projection_smoke_cases_20260521.csv`, applies the public finite
projection rules for the five action families, and checks that the regenerated
rows exactly match `data/claim_passport_casebook_20260519.csv`. It also checks
dataset/scenario joins, action coverage, action/layer enum validity, and
`bottom_T` behavior for the suppression case.

The claim audit report runner reads the public claim passport, G/Q/U
intervention, Q-policy sensitivity, NAB support-only adapter, and
resource-boundary tables. It generates Markdown, HTML, CSV, and JSON reports
under `reports/claim_audit_report_20260521/`, checks 11 contribution-facing
conditions, and makes explicit whether the release behaves like a typed
claim-governance workflow rather than a loose table bundle.

The claim template admission runner reads
`artifact/claim_template_admission_cases_20260521.csv`, applies the adapter
admission contract, and writes Markdown, HTML, CSV, and JSON reports under
`reports/claim_template_admission_20260521/`. It admits five mainline templates
and three support-only NAB templates while rejecting the AI4I boundary probe
until the missing claim-template, G/Q/U, action, preorder, forbidden-claim, and
visual-row fields are supplied.

The reviewer claim-intake runner reads
`artifact/reviewer_claim_intake_examples_20260521.csv` and applies registered
templates to submitted author/reviewer claim sentences. It writes Markdown,
HTML, CSV, and JSON reports under `reports/reviewer_claim_intake_20260521/`,
returning application decisions such as accept, rewrite, suppress,
support-only rewrite, patchwork reject, and unknown-template reject.

The claim-audit gold probe reads
`artifact/claim_audit_gold_probe_cases_20260521.csv` and validates the current
routing boundary: registered-template calls are decided by the intake runner,
adapter-needed rows are not treated as already supported, and proof/novelty/code
or legal-safety text is marked out of scope for the current metric-to-claim
tool.

The paper-claim gold benchmark reads
`artifact/paper_claim_gold_benchmark_sources_20260521.csv` and
`artifact/paper_claim_gold_benchmark_cases_20260521.csv`. It evaluates 40
external empirical ML or evaluation paper sources with 120 public-safe
paraphrased claim rows plus 8 registered-template controls. It reports
current-action consistency, registered-control consistency, false-accept,
false-release, false-kill, unsupported-template, and out-of-scope rates. Its
unsupported-template rows are an explicit boundary measurement, not a claim
that the current release can autonomously register every field.

The paper-excerpt decision-surface benchmark reads
`artifact/paper_excerpt_reviewer_value_cases_20260521.csv`. It evaluates 80
public-safe source-anchored selected-excerpt units plus 8 registered controls.
Default mode uses human-gold routes as an oracle front end, so it checks the
deterministic reviewer-facing claim-audit decision layer after excerpt
selection. It also emits a prediction packet for future LLM/human front-end
scoring and supports a transparent `--baseline text_rules` run. These
gold/oracle labels are curated release benchmark labels, not independent
reviewer-study evidence.

The paper-claim annotation agreement runner reads the randomized blind
annotation packet and annotation map. Before a second annotator fills the label
columns, it reports `PENDING_SECOND_ANNOTATOR` while validating that the packet
is complete, blind to gold labels, joined to the gold key, and free of private
markers. After labels are supplied, the same runner computes exact agreement,
Cohen's kappa, confusion rows, and disagreement rows.

The reviewer-facing audit demo runner reads the selected and holdout paragraph
routing fixtures and joins them to registered template intake. It generates 72
audit cards: 8 registered-template decisions, 43 adapter-admission tickets, and
21 out-of-scope stops. The companion regression runner then locks this card
surface, the eight registered controls, the known selected residual, the
fail-closed boundary, and the filterable HTML card coverage.

## What This Does Not Check

These first inspection commands do not:

- download raw ACS, Bank, WDC, Walmart-Amazon, NAB, or AI4I data;
- rerun model training;
- reproduce official WDC/Ditto scores;
- regenerate the internal 375-event audit trace;
- certify deployment safety;
- validate arbitrary natural-language claims.
- infer missing adapter fields from domain names or prose.
- discover template ids from free text.
- extract claims from PDF/full-paper text without a separate extractor
  benchmark.
- turn LLM-generated routes into licensed claims unless the deterministic
  template/admission runner accepts the routed input.
- prove human reviewer utility without an independent reviewer study.

## Reviewer Reading Order

After the command passes, inspect:

1. `artifact/RESOURCE_SPEC.md` for the resource object and release boundary;
2. `artifact/ENVIRONMENT_NOTE_20260526.md` for the first-inspection runtime
   assumptions;
3. `artifact/dataset_source_manifest_20260520.csv`,
   `artifact/split_scenario_manifest_examples_20260520.csv`, and
   `artifact/claim_contract_schema_20260520.json` for machine-readable entry
   points;
4. `artifact/projection_smoke_cases_20260521.csv` and
   `data/claim_passport_casebook_20260519.csv` for the executable smoke
   projection surface;
5. `docs/REPORT_INDEX.md` for the commands that regenerate untracked inspection
   reports such as claim audit, template admission, reviewer intake, gold probe,
   paper-claim benchmark, selected-excerpt decision-surface benchmark,
   annotation scaffold, and reviewer demo outputs;
6. tracked report directories under `reports/` for public-safe fixtures that
   are included in this snapshot, especially fulltext-adjacent boundary
   readouts and controlled adapter-admission rows;
7. `paper/PAPER_EXCERPT_REVIEWER_VALUE_BENCHMARK_20260521.md`
   for the selected-excerpt decision-surface interpretation, transparent
   baseline, and limits;
8. `paper/REVIEWER_AUDIT_DEMO_USE_PROTOCOL_20260521.md` for the human/LLM/tool
   use boundary and non-goals;
9. `artifact/application_motivation_cases_20260521.csv` for external
   application cases that motivate the intake workflow;
10. `data/final_display_assets_20260520/claim_passport_compressed_table.csv`
   for the sentence-level claim passport display;
11. `data/support_resource_display_20260520/resource_component_rows.csv` for
   the resource components;
12. `data/wdc_unified_stability_display_20260519/model_seed_not_reportable_display.csv`
   for the WDC six-matrix depth witness;
13. `artifact/source_license_snapshot_20260520.csv` for source/license and
   redistribution posture;
14. `paper/APPENDIX_C_RESOURCE_RELEASE.md` for source and availability posture.

## Final Publication Metadata To Fill

The runnable release snapshot above is self-contained for first inspection.
Before a submitted paper can claim a final public archive, the authors still
need to fill publication metadata:

- public repository or archive URL;
- DOI or DOI plan;
- final confirmation that refreshed source/license access dates still match
  the archived release snapshot;
- clean-checkout rerun after the final public archive is created.
