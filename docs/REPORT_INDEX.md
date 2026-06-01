# Report And Evidence Index

This index connects paper-facing resource claims to the release files and
runners that support them. Generated reports are inspection outputs; they are
not raw-data reproductions. For a strict local check, you may replace every
`reports/...` output path below with a temporary directory under `/tmp`.

## Core Release Checks

Use these first. They answer whether the checkout is a safe, runnable release
surface.

| Claim to verify | Command | Expected signal | Open after running |
| --- | --- | --- | --- |
| The package is manifest-controlled and public-safe. | `python3 src/claimcontractbench.py doctor` | 110 rows, 110 required files, 110 public-safe rows, 0 raw-data rows. | Console output. |
| The first-inspection paths run without raw data or GPU. | `python3 src/claimcontractbench.py smoke` | 8 positive checks and 4 fail-closed negative checks pass. | Console output. |
| The projection operator regenerates five action-family examples. | `python3 src/run_projection_smoke.py` | 5 rows: emit, relabel, weaken, rewrite, suppress. | Console output, or the path supplied with `--write-generated`. |

## Resource Behavior Reports

Use these after the core checks. They answer which paper-facing contribution a
specific generated report supports.

| Resource surface | Command | Open after running | What it supports | What it does not support |
| --- | --- | --- | --- | --- |
| Claim audit report | `python3 src/run_claim_audit_report.py --output reports/claim_audit_report_20260521` | `claim_audit_report.md` | Casebook, `G/Q/U` intervention, Q-policy, NAB support-only rows, and 11 contribution-facing checks. | Arbitrary paper checking. |
| Template admission | `python3 src/run_claim_template_admission.py --output reports/claim_template_admission_20260521` | `claim_template_admission_report.md` | 9 template rows: 5 mainline, 3 support-only, 1 rejected; 10 checks. | Automatic admission of new domains. |
| Reviewer claim intake | `python3 src/run_reviewer_claim_intake.py --output reports/reviewer_claim_intake_20260521` | `reviewer_claim_intake_report.md` | 8 author/reviewer submitted claim examples mapped to accept, rewrite, suppress, support-only, and reject decisions. | General reviewer utility. |
| LLM packet review | `python3 src/claimcontractbench.py review --input artifact/llm_claim_review_packet_template_20260527.csv` | `llm_claim_review_packet_report.md` | 4-row packet: 2 registered calls, 1 admission-needed row, 1 out-of-scope row; fail-closed packet checks. | Full-paper extraction or acceptance advice. |

## Benchmark And Boundary Readouts

| Readout | Command | Key numbers | Boundary |
| --- | --- | --- | --- |
| Claim-audit gold probe | `python3 src/run_claim_audit_gold_probe.py --output reports/claim_audit_gold_probe_20260521` | 18 rows, 8 registered-template rows, 6 adapter-needed rows, 4 out-of-scope rows, 18 decision matches. | No autonomous routing claim. |
| Paper-claim gold benchmark | `python3 src/run_paper_claim_gold_benchmark.py --output reports/paper_claim_gold_benchmark_20260521` | 40 external papers, 120 external claim rows, 8 controls, 128 total rows, 0.000 false-release rate for unsupported/out-of-scope rows. | Measures fail-closed boundary, not autonomous paper reading. |
| Paper-excerpt decision-surface benchmark | `python3 src/run_paper_excerpt_reviewer_value_benchmark.py --output reports/paper_excerpt_reviewer_value_benchmark_20260521` | 88 excerpt rows, 40 source papers, 22 source families, 1.000 tool-decision accuracy in human-gold-oracle mode, 0.000 unsafe-release rate. | Oracle-routed backend check only; does not prove human-review utility or full-PDF extraction. |
| Annotation agreement scaffold | `python3 src/run_paper_claim_annotation_agreement.py --output reports/paper_claim_annotation_agreement_20260521` | 128 annotation rows, status `PENDING_SECOND_ANNOTATOR`, agreement not computed. | No independent annotation agreement is claimed. |
| Reviewer audit demo | `python3 src/run_reviewer_audit_demo.py --output reports/reviewer_facing_audit_demo_20260521` | 72 cards: 8 registered-template, 43 admission-ticket, 21 out-of-scope. | Demo cards are not a production reviewer study. |
| Fulltext claim-span gold readout | tracked files under `reports/frontend_fulltext_phase1_claim_span_gold_readout_20260523/` | 80 adjudicated rows, 37 papers, 21 source families, 62 needs-adapter rows, 18 do-not-call rows, 60/62 adapter rows with localizable evidence. | Adapter/boundary evidence only; not automatic paper reading. |
| Fulltext claim-span strict agreement | tracked files under `reports/frontend_fulltext_phase1_claim_span_strict_agreement_20260523/` | 80 paired A/B rows, span-found agreement 0.850, kappa 0.749, match-type kappa 0.482, section exact 0.237, span exact 0.087, containment-at-0.8 rate 0.262. | Quality gates failed; these metrics do not license extraction reliability claims. |
| Controlled adapter admission case study | tracked files under `reports/claim_span_adapter_admission_case_study_20260523/` | 6 adapter specs, 22 passport rows, actions 9 accept / 6 rewrite / 4 weaken / 1 suppress / 2 support-only, 10 checks passed. | Controlled admission evidence, not cross-domain validation. |

These benchmark/readout files are advanced evidence for reviewers and tool
developers. Ordinary users do not need them to run the packet workflow. See
`docs/EVALUATION_SOURCE_INVENTORY.md` for the public-source policy, source mix,
and why the repository stores links, public-safe anchors, paraphrased claims,
and aggregate metrics instead of PDFs, long paper excerpts, or confidential
review material.

For the reviewer-audit regression, first generate the demo at the default path,
then run:

```bash
python3 src/run_reviewer_audit_demo_regression.py \
  --demo-dir reports/reviewer_facing_audit_demo_20260521 \
  --output reports/reviewer_facing_audit_demo_regression_20260521
```

## Stable Evidence Files

- `artifact/release_manifest_20260520.csv`: public-safe release surface.
- `docs/REVIEWER_CHECKLIST.md`: one-page reviewer verification map.
- `docs/EVALUATION_SOURCE_INVENTORY.md`: advanced public-paper source and
  benchmark inventory for reviewers and tool developers.
- `artifact/source_license_snapshot_20260520.csv`: source and license posture.
- `artifact/dataset_source_manifest_20260520.csv`: dataset roles and raw-data
  redistribution boundaries.
- `artifact/claim_contract_schema_20260520.json`: claim-contract schema.
- `data/claim_passport_casebook_20260519.csv`: five public claim-passport rows.
- `artifact/llm_claim_review_packet_template_20260527.csv`: LLM trial packet.
- `artifact/template_admission_packet_template_20260527.csv`: admission packet.
- `reports/frontend_fulltext_phase1_claim_span_gold_readout_20260523/`: fulltext-adjacent claim-span readout files.
- `reports/frontend_fulltext_phase1_claim_span_strict_agreement_20260523/`: A/B agreement and adjudication-candidate files.
- `reports/claim_span_adapter_admission_case_study_20260523/`: controlled adapter-admission case-study files.
