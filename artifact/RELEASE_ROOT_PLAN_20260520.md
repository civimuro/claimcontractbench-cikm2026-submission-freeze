# Release Root Plan (2026-05-20)

Status: `ROUTE_A_RELEASE_READINESS_DRAFT`.

Purpose: define the public/reviewer-facing artifact root for
ClaimContractBench without leaking private coordination files, credentials, or
raw datasets.

## 1. Release Root

The future reviewer checkout should be organized as:

```text
ClaimContractBench/
├── README.md
├── LICENSE.md
├── LICENSES/
│   ├── Apache-2.0.txt
│   └── CC-BY-4.0.txt
├── artifact/
│   ├── RESOURCE_SPEC.md
│   ├── ENVIRONMENT_NOTE_20260526.md
│   ├── RELEASE_ROOT_PLAN_20260520.md
│   ├── REVIEWER_QUICKSTART_RELEASE_DRAFT_20260520.md
│   ├── LLM_ASSISTED_REVIEW_QUICKSTART_20260527.md
│   ├── release_manifest_20260520.csv
│   ├── source_license_snapshot_20260520.csv
│   ├── dataset_source_manifest_20260520.csv
│   ├── split_scenario_manifest_examples_20260520.csv
│   ├── claim_contract_schema_20260520.json
│   ├── projection_smoke_cases_20260521.csv
│   ├── claim_template_admission_schema_20260521.json
│   ├── claim_template_admission_cases_20260521.csv
│   ├── reviewer_claim_intake_schema_20260521.json
│   ├── reviewer_claim_intake_examples_20260521.csv
│   ├── llm_claim_review_packet_template_20260527.csv
│   ├── application_motivation_cases_20260521.csv
│   ├── claim_audit_gold_probe_schema_20260521.json
│   ├── claim_audit_gold_probe_cases_20260521.csv
│   ├── paper_claim_gold_benchmark_schema_20260521.json
│   ├── paper_claim_gold_benchmark_annotation_protocol_20260521.md
│   ├── paper_claim_gold_benchmark_blind_annotation_packet_20260521.csv
│   ├── paper_claim_gold_benchmark_annotation_map_20260521.csv
│   ├── paper_claim_gold_benchmark_sources_20260521.csv
│   ├── paper_claim_gold_benchmark_cases_20260521.csv
│   ├── paper_excerpt_reviewer_value_schema_20260521.json
│   └── paper_excerpt_reviewer_value_cases_20260521.csv
├── data/
│   ├── claim_passport_casebook_20260519.csv
│   ├── final_display_assets_20260520/
│   ├── gqu_ablation_display_20260520/
│   ├── q_policy_sensitivity_display_20260519/
│   ├── wdc_unified_stability_display_20260519/
│   ├── official_backup_full_matrix_readout_20260520/
│   ├── walmart_amazon_r2_scenario_summary.csv
│   └── nab_adapter_visual_passport_rows_20260519.csv
├── paper/
│   ├── figures/
│   ├── REVIEWER_AUDIT_DEMO_USE_PROTOCOL_20260521.md
│   ├── PAPER_EXCERPT_REVIEWER_VALUE_BENCHMARK_20260521.md
│   └── APPENDIX_C_RESOURCE_RELEASE.md
├── reports/
│   ├── paragraph_claim_span_router_external_eval_guided_20260521/
│   └── paragraph_claim_span_router_holdout_eval_guided_20260521/
└── src/
    ├── validate_release_surface.py
    ├── run_projection_smoke.py
    ├── run_claim_audit_report.py
    ├── run_claim_template_admission.py
    ├── run_reviewer_claim_intake.py
    ├── run_reviewer_audit_demo.py
    ├── run_reviewer_audit_demo_regression.py
    ├── run_llm_claim_review_packet.py
    ├── run_claim_audit_gold_probe.py
    ├── run_paper_claim_gold_benchmark.py
    ├── run_paper_excerpt_reviewer_value_benchmark.py
    └── run_paper_claim_annotation_agreement.py
```

This is a release-root plan, not the final archived artifact. The exact
repository URL, DOI, and final file snapshot remain author decisions.

## 2. Include / Exclude Rule

Include:

- explicit license-scope files for the mixed software/resource release;
- public-safe manifests and derived evidence tables;
- claim passport and resource component display sources;
- G/Q/U and Q-policy attack-control rows;
- WDC six-matrix depth display sources;
- official backup protocol-sensitivity summaries;
- Walmart-Amazon and NAB role-labeled support summaries;
- standard-library validation and projection smoke scripts;
- standard-library claim audit report generator;
- standard-library claim template admission generator;
- standard-library reviewer claim-intake decision generator;
- standard-library reviewer-facing audit demo generator;
- standard-library reviewer-facing audit demo regression generator;
- standard-library LLM claim-review packet generator;
- public-safe selected and holdout paragraph routing fixtures needed to
  regenerate the reviewer-facing audit demo;
- standard-library claim-audit gold-probe runner;
- standard-library paper-claim gold benchmark runner;
- standard-library paper-excerpt reviewer-value benchmark runner;
- application motivation cases for positioning the intake/admission workflow;
- public-safe paraphrased 40-paper claim benchmark sources and cases;
- public-safe source-anchored selected-excerpt benchmark cases;
- source/provenance and release posture docs;
- first-inspection environment note.

Exclude:

- raw ACS, Bank, WDC, Walmart-Amazon, NAB, or AI4I datasets unless provider
  terms clearly permit redistribution;
- GPU return archives and cloud credentials;
- private coordination directories or local machine paths;
- internal tower, handoff, or coordination logs;
- unpublished reviewer or agent notes.

## 3. First Reviewer Commands

From the release root:

```bash
python3 src/validate_release_surface.py
python3 src/run_projection_smoke.py
python3 src/run_claim_audit_report.py --output reports/claim_audit_report_20260521
python3 src/run_claim_template_admission.py --output reports/claim_template_admission_20260521
python3 src/run_reviewer_claim_intake.py --output reports/reviewer_claim_intake_20260521
python3 src/run_reviewer_audit_demo.py --output reports/reviewer_facing_audit_demo_20260521
python3 src/run_reviewer_audit_demo_regression.py --output reports/reviewer_facing_audit_demo_regression_20260521
python3 src/run_llm_claim_review_packet.py --output reports/llm_claim_review_packet_20260527
python3 src/run_claim_audit_gold_probe.py --output reports/claim_audit_gold_probe_20260521
python3 src/run_paper_claim_gold_benchmark.py --output reports/paper_claim_gold_benchmark_20260521
python3 src/run_paper_excerpt_reviewer_value_benchmark.py --output reports/paper_excerpt_reviewer_value_benchmark_20260521
python3 src/run_paper_claim_annotation_agreement.py --output reports/paper_claim_annotation_agreement_20260521
```

Expected result:

```text
PASS release surface validation
rows: 95
required_files: 95
public_safe_rows: 95
raw_data_rows: 0
PASS projection smoke runner
smoke_rows: 5
PASS claim audit report
checks_passed: 11
checks_failed: 0
PASS claim template admission
templates: 9
admitted_support_only: 3
rejected: 1
PASS reviewer claim intake
intake_rows: 8
support_only: 1
rejected: 2
PASS reviewer audit demo
audit_cards: 72
registered_template_cards: 8
admission_ticket_cards: 43
out_of_scope_cards: 21
PASS reviewer audit demo regression
audit_cards_checked: 72
checks_passed: 11
locked_registered_template_controls: 8
locked_fail_closed_boundary: yes
PASS LLM claim review packet
packet_rows: 4
call_registered_template: 2
needs_template_admission: 1
out_of_scope: 1
unsafe_release_rate: 0.000
PASS claim audit gold probe
gold_rows: 18
registered_template_rows: 8
adapter_needed_rows: 6
out_of_scope_rows: 4
autonomous_routing_supported: no
PASS paper claim gold benchmark
external_papers: 40
external_claim_rows: 120
registered_control_rows: 8
total_claim_rows: 128
current_action_mismatches: 0
false_release_rate_unsupported_or_out_of_scope: 0.000
autonomous_full_paper_routing_supported: no
PASS paper excerpt reviewer-value benchmark
front_end_mode: human_gold_oracle
excerpt_rows: 88
source_papers: 40
source_families: 22
tool_decision_accuracy: 1.000
unsafe_release_rate: 0.000
autonomous_full_paper_review_supported: no
PASS paper claim annotation agreement scaffold
annotation_status: PENDING_SECOND_ANNOTATOR
annotation_rows: 128
agreement_computed: no
```

These commands validate the release surface and regenerate the five public
claim-passport smoke rows from release-root inputs. They check required-file
presence, manifest path safety, raw-data exclusion, public-safe flags, content
privacy patterns, CSV/JSON structure, schema/casebook alignment,
dataset/scenario joins, action coverage, and `bottom_T` behavior. The claim
audit report runner additionally joins the public claim passport, G/Q/U
intervention, Q-policy, NAB support-only adapter, and resource-boundary assets
into Markdown/HTML/CSV/JSON reports. The template admission runner then checks
whether candidate claim templates instantiate the adapter contract before they
enter the workflow. The reviewer claim-intake runner demonstrates the
application step: registered templates plus submitted claim sentences are turned
into accept/rewrite/suppress/support-only/reject decisions. The reviewer audit
demo runner joins public paragraph-routing fixtures with that deterministic
intake layer, and the regression runner locks the card counts, registered
controls, selected residual, fail-closed boundary, and HTML surface. They do not download
raw datasets, rerun GPU training, regenerate the internal 375-event audit trace,
reproduce official benchmark scores, discover template ids from free text, or
infer missing adapter fields from prose.
The gold-probe runner makes this routing boundary testable by separating
registered calls, adapter-needed rows, and out-of-scope text.
The paper-claim gold benchmark runner expands the boundary check across 40
external empirical ML or evaluation paper sources with public-safe paraphrased
claims. It measures current action consistency, registered-control consistency,
false-accept, false-release, false-kill, unsupported-template, and out-of-scope
rates without claiming autonomous paper reading.
The paper-excerpt reviewer-value benchmark then evaluates 80 public-safe
source-anchored selected-excerpt units plus 8 registered controls. In default
mode it uses human-gold routes as an oracle front end, so it validates bounded
reviewer-facing claim-audit decisions after excerpt selection rather than
claiming autonomous full-paper review.
The annotation-agreement runner validates the randomized blind packet and
annotation map now, then computes exact agreement and Cohen's kappa once a
second annotator fills the route/action label columns.

## 3b. Local Candidate Builder

Before the final public repository or archive exists, authors can dry-run the
release surface with:

```bash
python3 src/build_release_candidate.py --output /tmp/claimcontractbench_release_candidate --force
```

The builder copies only required, public-safe manifest rows to the output
directory and then validates the copied candidate from inside that directory,
including the projection smoke runner and claim audit report runner when
present, plus the claim template admission runner when present. It is a
packaging guard, not a DOI/archive substitute. The reviewer claim-intake runner
is also executed when present, as are the reviewer audit demo, reviewer audit
demo regression, claim-audit gold probe, paper-claim gold benchmark, and
paper-excerpt reviewer-value benchmark, and annotation-agreement scaffold
runners.

If `--archive` is passed, the archive is built from a temporary manifest-only
mirror after the dry-run validation. This is intentional: validation runners
generate report directories inside the dry-run output, but the public archive
must not silently expand beyond the manifest surface unless the manifest is
explicitly updated and reviewed.

## 4. Artifact Claim Boundary

The release supports:

- inspection of the claim-contract schema and claim passport examples;
- validation that required public-safe derived files are present;
- regeneration of five public projection smoke rows covering the action grammar;
- generation of a joined claim audit report that exposes action cards,
  primitive stress rows, Q-policy sensitivity, adapter boundaries, and current
  limits;
- generation of a batch template-admission report that admits mainline and
  support-only templates while rejecting patchwork expansion probes with missing
  adapter fields;
- generation of an application-facing claim-intake report that turns registered
  templates and submitted claims into concrete author/reviewer decisions;
- generation of a reviewer-facing audit-card demo over selected paragraph
  routing fixtures;
- generation of a regression report that locks the reviewer audit demo's
  deterministic controls, fail-closed routing, known residual, and HTML card
  coverage;
- generation of a claim-audit gold-probe report that validates registered
  template decisions while explicitly counting adapter-needed and out-of-scope
  rows;
- generation of a paper-claim gold benchmark report that validates 128 current
  actions over 40 external sources and 8 registered controls while recording the
  unsupported-template boundary;
- generation of a source-anchored selected-excerpt reviewer-value benchmark
  report that validates 88 excerpt/control rows while recording the autonomy
  boundary and transparent baseline path;
- generation of an annotation-agreement scaffold that validates the blind
  second-annotation packet and computes agreement after labels are filled;
- an application motivation case map tying model reporting, dataset
  documentation, distribution-shift benchmarking, behavioral testing,
  robustness tooling, and selective prediction to the intake/admission workflow;
- review of WDC depth, G/Q/U, Q-policy, official support, Walmart-Amazon, and
  NAB support evidence in their assigned paper roles.

The release does not support:

- raw-data redistribution guarantees;
- official reproduction claims;
- SOTA or leaderboard claims;
- deployment safety;
- broad external validity or anomaly-detection validation;
- universal medium-train repair.

## 5. Remaining Release Work

Before final submission:

1. choose public repository or reviewer archive location;
2. decide DOI/archive plan;
3. keep source/license URLs and access dates synchronized with the final
   release snapshot;
4. normalize any final script paths after moving from work-use workspace to
   release root;
5. run the validator on a clean copied release directory;
6. update final paper availability statement with the repository/archive id.
