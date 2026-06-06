# Appendix C: Resource And Release Assets

Status: work-use appendix, 2026-05-16.  
Purpose: preserve the resource, quickstart, license, and release assets behind
the CIKM Resource paper.

Current status note: this appendix is a paper-facing release/provenance note,
not the canonical user quickstart. The current public checkout is governed by
`artifact/release_manifest_20260520.csv` and the README. The manifest-controlled
surface now contains 131 required public-safe rows and includes the later
real-paper template-review addendum.

## C1. Public-Safe Dataset Manifest

| Dataset id | Source | Raw data posture | Derived output posture | Role |
| --- | --- | --- | --- | --- |
| `acs_income_state_shift` | Folktables / ACS PUMS | do not bundle raw rows by default | include derived metadata/evidence | information-boundary and slice-reportability |
| `bank_marketing_shift` | UCI Bank Marketing | CC BY 4.0; raw optional after attribution, but not needed in first review package | include derived metadata/evidence | scalar-vs-score-region locality |
| `wdc_products_em_shift` | WDC Products | do not bundle raw product records without explicit terms | include scenario metadata, scores, contract evidence | decision-use and entity-matching depth |
| `walmart_amazon_em_shakedown` | DeepMatcher/Magellan-style source | do not bundle raw pairs until terms verified | include bounded derived summaries | held-out EM shakedown |

## C2. Split/Scenario Manifest Examples

| Dataset id | Scenario | Model/source | Shift axis | Source/target context |
| --- | --- | --- | --- | --- |
| `acs_income_state_shift` | `state_CA_to_TX` | logistic regression | state | source prior 0.405625; target prior 0.36275 |
| `bank_marketing_shift` | `contact_cellular_to_unknown` | logistic regression | contact method | source prior 0.152333; target prior 0.038143 |
| `wdc_products_em_shift` | `cc20_train_small_unseen000` | external RoBERTa/Ditto-style probe | corner case and unseen entity | source prior 0.2; target prior 0.111059 |
| `walmart_amazon_em_shakedown` | `random_split_baseline` | logistic similarity | entity-pair split | source prior 0.094192; target prior 0.094349 |

The held-out Walmart-Amazon shakedown now exposes the full five-scenario
derived prior table needed for the R2 audit. These are derived summaries, not
raw-pair redistribution.

| Dataset id | Scenario | Source cal n | Target eval n | Source prior | Target prior | Delta |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `walmart_amazon_em_shakedown` | `random_split_baseline` | 2049 | 1929 | 0.094192 | 0.094349 | +0.000157 |
| `walmart_amazon_em_shakedown` | `electronics_to_office_printers` | 831 | 296 | 0.052948 | 0.091216 | +0.038268 |
| `walmart_amazon_em_shakedown` | `peripherals_to_computers_networking` | 385 | 97 | 0.085714 | 0.195876 | +0.110162 |
| `walmart_amazon_em_shakedown` | `target_projection_screens_sparse` | 2049 | 316 | 0.094192 | 0.012658 | -0.081534 |
| `walmart_amazon_em_shakedown` | `prior_random_pi020` | 2049 | 845 | 0.094192 | 0.200000 | +0.105808 |

The matching reportability counts are promoted in
`data/walmart_amazon_r2_scenario_summary.csv` and Appendix B §B4.

## C3. Claim-Contract Schema

The public release schema is the 16-field machine-readable schema in
`artifact/claim_contract_schema_20260520.json`. Its fields are:

1. `event_id`
2. `dataset_id`
3. `scenario_id`
4. `model_or_scorer`
5. `seed_or_profile`
6. `claim_layer`
7. `G_information_boundary`
8. `Q_reportability_policy`
9. `U_decision_use`
10. `preorder_relation`
11. `tempting_sentence`
12. `licensed_sentence`
13. `forbidden_sentence`
14. `projection_action`
15. `source_anchor_id`
16. `boundary_note`

The five-row claim passport casebook now uses this public schema directly, so
the first inspection validator can check header alignment, action/layer enums,
and dataset/scenario joins against the public manifests. Appendix A §A6.1 keeps
the older 17-field operator-trace mapping as an internal work-use schema until
those richer candidate-check/action-certificate traces are normalized to the
release root.

## C4. Projection Examples

The public seed contains one example for each action family:

| Example | Action | Dataset | Reviewer reading |
| --- | --- | --- | --- |
| emit as written | `emit_as_written` | ACSIncome | local claim can pass when support is adequate |
| relabel as upper bound | `relabel_as_upper_bound` | WDC Products | stronger-information evidence is a reference, not same-regime winner |
| weaken to diagnostic | `weaken_to_diagnostic` | ACSIncome | weak support yields diagnostic wording |
| rewrite to decision-local | `rewrite_to_decision_local` | WDC Products | decision-local winner can differ from global metric winner |
| suppress fallback | `bottom_T` / suppress | WDC Products | unsupported claim is not silently strengthened |

## C5. Quickstart Plan

The historical quickstart had four commands:

1. build the public manifest seed;
2. run the operator report runner;
3. validate manuscript numbers;
4. dry-run the supplement packager.

After the workspace restructure, final release commands should be rewritten to
avoid private coordination paths. Work-use commands may still reference
internal audit scripts, but reviewer-facing commands should be release-root
relative.

Current environment posture:

- Python 3.9+;
- standard-library-only quickstart path;
- no NumPy/Pandas/Torch/sklearn needed for initial metadata/evidence
  validation;
- no raw dataset download or GPU training needed for first reviewer inspection.

Current release-root-relative first inspection commands:

```bash
python3 src/validate_release_surface.py
python3 src/run_projection_smoke.py
python3 src/run_claim_audit_report.py --output reports/claim_audit_report_20260521
python3 src/run_claim_template_admission.py --output reports/claim_template_admission_20260521
python3 src/run_reviewer_claim_intake.py --output reports/reviewer_claim_intake_20260521
python3 src/run_llm_claim_review_packet.py --output reports/llm_claim_review_packet_20260527
python3 src/run_claim_audit_gold_probe.py --output reports/claim_audit_gold_probe_20260521
python3 src/run_paper_claim_gold_benchmark.py --output reports/paper_claim_gold_benchmark_20260521
python3 src/run_paper_excerpt_reviewer_value_benchmark.py --output reports/paper_excerpt_reviewer_value_benchmark_20260521
python3 src/run_paper_claim_annotation_agreement.py --output reports/paper_claim_annotation_agreement_20260521
python3 src/run_reviewer_audit_demo.py --output reports/reviewer_facing_audit_demo_20260521
python3 src/run_reviewer_audit_demo_regression.py \
  --demo-dir reports/reviewer_facing_audit_demo_20260521 \
  --output reports/reviewer_facing_audit_demo_regression_20260521
python3 src/claimcontractbench.py realpaper-demo --output /tmp/claimcontractbench_realpaper_demo
```

The first command reads `artifact/release_manifest_20260520.csv` and checks that
the public-safe release surface exists, uses release-root-relative paths,
excludes private coordination directories, contains no raw-data rows, and does
not retain private coordination paths, local machine paths, or credential-like
patterns inside the required release files. It also parses required CSV/JSON
files for structural validity and verifies that the claim passport casebook
conforms to the public schema and joins to the dataset/scenario manifests.

The second command reads `artifact/projection_smoke_cases_20260521.csv` and
regenerates the five public claim-passport casebook rows covering emit, relabel,
weaken, rewrite, and suppress. It checks exact alignment with
`data/claim_passport_casebook_20260519.csv`, action/layer enum validity,
dataset/scenario joins, and `bottom_T` behavior. Current work-use result: the
validator and projection smoke runner PASS with 131 rows, 131 required files,
131 public-safe rows, 0 raw-data rows, and five regenerated smoke rows.

The third command generates a reviewer-facing audit report from the public claim
passport, G/Q/U intervention, Q-policy sensitivity, NAB support-only adapter,
and resource-boundary assets. It emits Markdown, HTML, CSV, and JSON files under
`reports/claim_audit_report_20260521/`, including claim cards, primitive stress
rows, Q-policy rows, adapter boundary rows, resource-boundary rows, and a
reviewer attack map. Current work-use result: PASS with 11 checks passing and
0 checks failing.

The fourth command generates a batch claim-template admission report from
`artifact/claim_template_admission_cases_20260521.csv`. It admits five mainline
templates and three NAB support-only templates while rejecting one AI4I
patchwork-expansion probe until the missing template, G/Q/U, action, preorder,
forbidden-claim, and visual-row fields exist. Current work-use result: PASS
with 10 checks passing and 0 checks failing.

The fifth command demonstrates an application-facing claim-intake workflow. It
reads `artifact/reviewer_claim_intake_examples_20260521.csv`, joins each
submitted claim to a registered template, and returns concrete author/reviewer
decisions: accept, rewrite, suppress, support-only rewrite, patchwork reject, or
unknown-template reject. Current work-use result: PASS with 8 intake rows, 9
checks passing, and 0 checks failing.

The application motivation table
`artifact/application_motivation_cases_20260521.csv` maps six external
evaluation/documentation families (model cards, datasheets, WILDS, CheckList,
Robustness Gym, and selective classification) to the claim-intake,
template-admission, and audit-report workflows. It is a motivation and boundary
map, not a claim that the resource replaces those frameworks.

The sixth command runs a claim-audit gold probe. It reads
`artifact/claim_audit_gold_probe_cases_20260521.csv` and separates candidate
text into registered-template calls, adapter-needed rows, and out-of-scope rows.
Current work-use result: PASS with 18 gold rows, 8 registered-template rows, 6
adapter-needed rows, 4 out-of-scope rows, 18 matching decisions, and
`autonomous_routing_supported: no`.

The seventh command runs the larger paper-claim gold benchmark. It reads
`artifact/paper_claim_gold_benchmark_sources_20260521.csv` and
`artifact/paper_claim_gold_benchmark_cases_20260521.csv`, covering 40 external
empirical ML/evaluation paper sources, 120 public-safe paraphrased external
claim rows, and 8 registered-template controls. Current work-use result: PASS
with 15 checks, 128/128 current action matches, 1.000 registered-control
consistency, 0.000 false-accept rate, 0.000 false-release rate for unsupported
or out-of-scope rows, 0.000 false-kill rate on supported registered controls,
80/120 external rows marked unsupported-template, and 40/120 marked out of
scope. The unsupported-template count is a boundary measurement: it shows the
current release fails closed rather than claiming autonomous paper reading or
template discovery.

The eighth command validates the annotation-reliability scaffold. It reads
`artifact/paper_claim_gold_benchmark_blind_annotation_packet_20260521.csv` and
`artifact/paper_claim_gold_benchmark_annotation_map_20260521.csv`. Current
work-use result: PASS with `annotation_status: PENDING_SECOND_ANNOTATOR`, 128
annotation rows, 0 filled rows, `agreement_computed: no`, and 10
packet-readiness checks passing. This is a readiness check, not a human
agreement claim.

Current release-root validation command:

```bash
python3 src/claimcontractbench.py doctor
python3 src/claimcontractbench.py smoke
```

These commands validate the manifest-controlled reviewer surface and run the
release smoke suite from the public checkout. Current work-use result: PASS with
131 rows, 131 required files, 131 public-safe rows, 0 raw-data rows, 12 positive
smoke checks, and 5 fail-closed negative checks. This is the executable
reviewer path for the current package; historical clean-copy builder drills are
not part of the public command surface.

The practical real-paper trial path is:

```bash
python3 src/claimcontractbench.py realpaper-demo --output /tmp/claimcontractbench_realpaper_demo
```

It replays 72 supplied candidate claims from 18 public arXiv papers across
three V1.8-backed template families. Current result: PASS with conservative
candidate-safety accuracy 0.958, display-action accuracy 0.806, and three
unsafe false releases under the conservative replay. This is a registered
template replay surface, not automatic full-paper extraction, human reviewer
utility evidence, broad empirical-ML coverage, or zero-risk release.

The five-row projection smoke runner is now release-root normalized. The deeper
375-event operator-regeneration commands remain internal work-use validation
paths until their richer traces are normalized to the public release root.

## C5b. Reference Operator Runtime

Local work-use measurement, 2026-05-18 05:34 Asia/Shanghai:

| Field | Value |
| --- | --- |
| Command | `/usr/bin/time -l python3 run_operator_report_runner.py` from the internal audit-script directory |
| Machine | Apple M5, arm64, 16 GB memory |
| OS / Python | macOS 26.3.1; Python 3.9.6 |
| Runner status | PASS |
| Scope | canonical 375-event operator denominator; E1 DistilBERT support-only directories excluded from this denominator |
| Output scale | 375 operator events; 1500 event checks; 1700 candidate rows; 2625 candidate checks; 1030 theory-property rows |
| Wall-clock | 0.07 s real; 0.05 s user; 0.01 s sys |
| Peak memory | 17,891,328-byte maximum resident set size (~17.1 MiB); 14,041,376-byte peak memory footprint (~13.4 MiB) |

This is a reference-machine usability measurement, not a performance benchmark
or scaling claim. The final public release should rerun the same measurement
from the release-root quickstart after private-path normalization.

## C6. License And Source Posture

| Source | Checked status | Remaining risk |
| --- | --- | --- |
| Folktables/ACS | 2026-05-20 snapshot: Folktables code posture and Census/ACS terms checked | cite Folktables and Census/ACS terms; do not bundle raw PUMS |
| UCI Bank Marketing | 2026-05-20 snapshot: DOI and CC BY 4.0 checked | attribution/change notice needed if raw/transformed rows released |
| WDC Products | 2026-05-20 snapshot: benchmark page checked, no explicit data-license text found | raw redistribution needs explicit terms/confirmation |
| Walmart-Amazon | 2026-05-20 snapshot: DeepMatcher dataset page checked, no license text found | keep derived only or verify/replace source |
| NAB adapter | 2026-05-20 snapshot: repository and MIT license checked | support-only adapter rows; no broad anomaly-detection validation |

The machine-readable source and redistribution posture snapshot is
`artifact/source_license_snapshot_20260520.csv`.

## C7. Release Checklist

| Item | Current state | Needed before final submission |
| --- | --- | --- |
| dataset manifest | `artifact/dataset_source_manifest_20260520.csv` | final public-archive sync |
| split/scenario manifest | `artifact/split_scenario_manifest_examples_20260520.csv` | final public-archive sync |
| claim-contract schema | `artifact/claim_contract_schema_20260520.json` | final public-archive sync |
| projection examples | action-covering examples seeded as public-schema casebook rows | final public-archive sync |
| release-surface quickstart | release-root validator and projection smoke runner passing in workspace and clean copied-release simulation | final public-archive rerun |
| release-candidate builder | the manifest-controlled GitHub snapshot contains 131 required public-safe rows and validates in place | final public-archive rerun after repository/archive choice |
| operator quickstart | five-row public smoke runner available; 375-event internal runner local reference runtime recorded | release-root normalization before claiming full public runner support |
| claim audit report | `src/run_claim_audit_report.py` generates reviewer-facing Markdown/HTML/CSV/JSON reports with 11 checks passing | final public-archive rerun and optional sample report inclusion |
| claim template admission | `src/run_claim_template_admission.py` admits 5 mainline and 3 support-only templates and rejects 1 patchwork probe with 10 checks passing | final public-archive rerun and optional sample report inclusion |
| reviewer claim intake | `src/run_reviewer_claim_intake.py` turns 8 submitted claim examples into accept/rewrite/suppress/support-only/reject decisions with 9 checks passing | final public-archive rerun and optional sample report inclusion |
| application motivation cases | six external evaluation/documentation families mapped to claim-audit, template-admission, and intake decisions | final source-link check before public archive |
| claim-audit gold probe | 18 routing/decision rows: 8 registered-template calls, 6 adapter-needed rows, 4 out-of-scope rows, and no autonomous routing claim | final public-archive rerun |
| paper-claim gold benchmark | annotation protocol, blind annotation packet, annotation map, 40 external paper sources, 120 paraphrased external claim rows, 8 registered controls, 15 passing checks, and 0 current-action mismatches | use as an internal fail-closed boundary benchmark; future work should add independent annotator, extractor, and template-admission benchmarks |
| paper-excerpt decision-surface benchmark | 80 public-safe source-anchored selected-excerpt units, 8 registered controls, 40 source papers, 22 source families, 13 passing checks, 0 unsafe-release rate, and transparent keyword baseline | future work should add independent body-excerpt annotation and reviewer utility study |
| fulltext claim-span gold readout | 80 adjudicated rows, 37 papers, 21 source families, 62 needs-adapter rows, 18 do-not-call rows, 60/62 adapter rows with localizable evidence, and 8 checks passing | adapter/boundary evidence only; not automatic paper reading |
| fulltext strict agreement | 80 paired A/B rows, span-found agreement 0.850, kappa 0.749, match-type kappa 0.482, section exact 0.237, real-span exact 0.087, containment-at-0.8 rate 0.262, and 4 checks passing | quality gates failed; no extraction-reliability claim |
| controlled adapter admission case study | 6 adapter specs, 22 passport rows, actions 9 accept / 6 rewrite / 4 weaken / 1 suppress / 2 support-only, and 10 checks passing | controlled admission evidence, not cross-domain validation |
| annotation agreement scaffold | `src/run_paper_claim_annotation_agreement.py` validates 128 blind annotation rows and reports `PENDING_SECOND_ANNOTATOR` until labels are filled | second annotator, adjudication, and agreement reporting |
| real-paper template addendum | 18 public arXiv papers, 72 supplied candidate claims, 3 V1.8-backed families, conservative safety 0.958, display-action accuracy 0.806, and 3 conservative unsafe false releases | registered-template replay evidence only; not automatic full-paper extraction or human utility |
| license table | 2026-05-20 source/license snapshot exists | recheck at final archive time |
| release manifest | 131 public-safe required rows, validator, projection smoke runner, claim audit report runner, claim template admission runner, reviewer claim-intake runner, claim-audit gold-probe runner, paper-claim gold benchmark runner, paper-excerpt decision-surface benchmark runner, fulltext claim-span readouts, controlled adapter case-study reports, annotation-agreement scaffold, environment note, and docs layer passing | final file snapshot after public archive |
| release path | `https://github.com/civimuro/claimcontractbench-cikm2026-submission-freeze` | frozen reviewer snapshot and DOI/archive plan |

## C8. Availability Statement Draft

ClaimContractBench releases code, manifest examples, derived claim-contract
tables, validation scripts, and source/provenance documentation at
`https://github.com/civimuro/claimcontractbench-cikm2026-submission-freeze`.
Raw datasets are not bundled in the initial artifact unless provider terms
clearly permit redistribution with required attribution. Reviewers can inspect
the claim-contract workflow using committed derived evidence and can follow
source-provider instructions for raw data access where needed.

## C8b. GenAI Usage Disclosure

CIKM 2026 requires every submission to include a GenAI Usage Disclosure
section placed immediately before the references. This section is excluded
from the page limit (per CIKM 2026 submission policy for full, short,
resource, and demo tracks) and disclosure is a hard requirement: omission can
result in desk rejection or other ACM-policy actions.

Current compact-manuscript wording:

> Generative AI tools, including OpenAI Codex/ChatGPT and Anthropic Claude, were
> used to assist with drafting, code and documentation review, reviewer-style
> critique, and language polishing. The authors reviewed and edited the
> generated material, verified the reported artifacts and analyses, and remain
> responsible for the paper's content.

The submitting authors should verify this wording before upload. Numeric
evidence in this resource is generated by the operator and validation scripts
under human review, not by AI free-form generation; source/license assessments
and dataset posture decisions remain author responsibility.

## C8c. CIKM 2026 Resource Submission Compliance Map

Current official-policy interpretation, checked 2026-05-20:

| Requirement | Current status | Required final action |
| --- | --- | --- |
| Resource paper length | ACM preview is 4 pages for main content; references and GenAI disclosure are outside the limited pages | keep the main-content budget at 4 pages after final metadata insertion |
| Review model | Resource Track is single-blind | replace temporary author/affiliation fields with real names and affiliations before submission |
| Reviewer nomination | CIKM requires at least one author to be nominated for reviewing papers | complete this in EasyChair; failure is a desk-rejection risk |
| Resource availability | code resources should be publicly available through reputable code-sharing platforms; datasets/benchmarks should provide metadata/DOI when relevant | GitHub repository selected; add final release tag and DOI/archive plan, then rerun the release validator on the final snapshot |
| Review rubric | novelty, availability, utility, and predicted impact are explicit Resource Track criteria | keep the claim passport, release manifest, quickstart, WDC depth witness, and limitations aligned with those criteria |
| GenAI disclosure | required immediately before references and outside the page limit | verify the candidate disclosure wording before submission |
| Accessibility | alt text is strongly encouraged for floats | preserve the current figure descriptions and verify final float descriptions |

## C9. Relation To Final 4-Page Paper

The final CIKM paper should include only a compact availability paragraph and
one resource-component table. This appendix preserves the full work-use
resource state for handoff and later artifact preparation.
