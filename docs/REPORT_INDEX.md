# Report And Evidence Index

This index connects paper-facing resource claims to the release files and
runners that support them. Generated reports are inspection outputs; they are
not raw-data reproductions.

## Core Release Checks

| Claim to verify | Command | Expected signal |
| --- | --- | --- |
| The package is manifest-controlled and public-safe. | `python3 src/claimcontractbench.py doctor` | 96 rows, 96 required files, 96 public-safe rows, 0 raw-data rows. |
| The first-inspection paths run without raw data or GPU. | `python3 src/claimcontractbench.py smoke` | 8 positive checks and 4 fail-closed negative checks pass. |
| The projection operator regenerates five action-family examples. | `python3 src/run_projection_smoke.py` | 5 rows: emit, relabel, weaken, rewrite, suppress. |

## Resource Behavior Reports

| Resource surface | Command | What it supports | What it does not support |
| --- | --- | --- | --- |
| Claim audit report | `python3 src/run_claim_audit_report.py --output reports/claim_audit_report_20260521` | Casebook, `G/Q/U` intervention, Q-policy, NAB support-only rows, and 11 contribution-facing checks. | Arbitrary paper checking. |
| Template admission | `python3 src/run_claim_template_admission.py --output reports/claim_template_admission_20260521` | 9 template rows: 5 mainline, 3 support-only, 1 rejected; 10 checks. | Automatic admission of new domains. |
| Reviewer claim intake | `python3 src/run_reviewer_claim_intake.py --output reports/reviewer_claim_intake_20260521` | 8 author/reviewer submitted claim examples mapped to accept, rewrite, suppress, support-only, and reject decisions. | General reviewer utility. |
| LLM packet review | `python3 src/claimcontractbench.py review --input artifact/llm_claim_review_packet_template_20260527.csv` | 4-row packet: 2 registered calls, 1 admission-needed row, 1 out-of-scope row; fail-closed packet checks. | Full-paper extraction or acceptance advice. |

## Benchmark And Boundary Readouts

| Readout | Command | Key numbers | Boundary |
| --- | --- | --- | --- |
| Claim-audit gold probe | `python3 src/run_claim_audit_gold_probe.py --output reports/claim_audit_gold_probe_20260521` | 18 rows, 8 registered-template rows, 6 adapter-needed rows, 4 out-of-scope rows, 18 decision matches. | No autonomous routing claim. |
| Paper-claim gold benchmark | `python3 src/run_paper_claim_gold_benchmark.py --output reports/paper_claim_gold_benchmark_20260521` | 40 external papers, 120 external claim rows, 8 controls, 128 total rows, 0.000 false-release rate for unsupported/out-of-scope rows. | Measures fail-closed boundary, not autonomous paper reading. |
| Paper-excerpt reviewer-value benchmark | `python3 src/run_paper_excerpt_reviewer_value_benchmark.py --output reports/paper_excerpt_reviewer_value_benchmark_20260521` | 88 excerpt rows, 40 source papers, 22 source families, 1.000 tool-decision accuracy in human-gold-oracle mode, 0.000 unsafe-release rate. | Does not prove human-review utility or full-PDF extraction. |
| Annotation agreement scaffold | `python3 src/run_paper_claim_annotation_agreement.py --output reports/paper_claim_annotation_agreement_20260521` | 128 annotation rows, status `PENDING_SECOND_ANNOTATOR`, agreement not computed. | No independent annotation agreement is claimed. |
| Reviewer audit demo | `python3 src/run_reviewer_audit_demo.py --output reports/reviewer_facing_audit_demo_20260521` | 72 cards: 8 registered-template, 43 admission-ticket, 21 out-of-scope. | Demo cards are not a production reviewer study. |

For the reviewer-audit regression, first generate the demo at the default path,
then run:

```bash
python3 src/run_reviewer_audit_demo_regression.py \
  --output reports/reviewer_facing_audit_demo_regression_20260521
```

## Stable Evidence Files

- `artifact/release_manifest_20260520.csv`: public-safe release surface.
- `docs/REVIEWER_CHECKLIST.md`: one-page reviewer verification map.
- `artifact/source_license_snapshot_20260520.csv`: source and license posture.
- `artifact/dataset_source_manifest_20260520.csv`: dataset roles and raw-data
  redistribution boundaries.
- `artifact/claim_contract_schema_20260520.json`: claim-contract schema.
- `data/claim_passport_casebook_20260519.csv`: five public claim-passport rows.
- `artifact/llm_claim_review_packet_template_20260527.csv`: LLM trial packet.
- `artifact/template_admission_packet_template_20260527.csv`: admission packet.
