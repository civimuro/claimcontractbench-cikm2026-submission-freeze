# Real-Paper Template Review Demo

This is the most direct way to try ClaimContractBench as a claim-review
assistant.

It uses three validated template families, corresponding to three review
domains:

- `llm_evaluation`
- `resource_documentation`
- `uncertainty_calibration`

The packet contains 72 supplied candidate claims from 18 public arXiv papers:
6 papers per family, 4 candidate claims per paper. Each row includes a short
public excerpt and a source locator. The repository does not redistribute PDFs,
full paper text, raw datasets, confidential review material, or author-private
notes.

The file names retain `v18` and `v318b` provenance IDs so reviewers can trace
the release back to the internal validation ladder. The user-facing experiment
name is the real-paper template review demo, not the version ID.

## Quick Run

From the repository root:

```bash
python3 src/claimcontractbench.py realpaper-demo \
  --output /tmp/claimcontractbench_realpaper_demo
```

Expected high-level output:

```text
PASS real-paper review demo
rows: 72
source_papers: 18
families: {'llm_evaluation': 24, 'resource_documentation': 24, 'uncertainty_calibration': 24}
conservative_candidate_safety_accuracy: 0.958
conservative_display_action_accuracy: 0.806
conservative_unsafe_false_releases: 3
```

Open the generated report:

```text
/tmp/claimcontractbench_realpaper_demo/real_paper_review_demo_report.md
```

If you want the report written inside the checkout instead, omit `--output`:

```bash
python3 src/claimcontractbench.py realpaper-demo
```

The in-checkout report path is
`reports/real_paper_review_demo_20260606/real_paper_review_demo_report.md`.

## What The Actions Mean

| Action | Meaning |
| --- | --- |
| `ACCEPT` | The supplied candidate is within the visible source support and family template. |
| `WEAKEN` | The same object is supported, but the candidate is too strong and should be lowered. |
| `BLOCK_AND_SUGGEST` | The original candidate is unsafe, but a corrected claim can be suggested. |
| `SUPPORT_ONLY` | The sentence is useful background, method, or context, not a releaseable empirical claim. |
| `SUPPRESS` | No safe public claim should be emitted for this row. |
| `REJECT_OR_OUT_OF_SCOPE` | The row asks for something outside this resource, such as legal clearance, proof correctness, deployment approval, or paper acceptance. |

## Try It With An LLM

For a blind-style adjudication, give the LLM only these three files:

- `artifact/real_paper_review_candidate_claims_v318b_20260606.csv`
- `artifact/real_paper_review_template_cards_v18_20260606.csv`
- `artifact/real_paper_review_llm_prompt_20260606.md`

Do not provide the reference-outcome file, generated decision report, scoring
summary, or previous run output to the LLM during adjudication. Those files are
for after-the-fact scoring and human inspection only.

Ask the LLM to return exactly this CSV header:

```text
row_id,source_support_status,claim_role,reportability_gate,candidate_release_safe_yes_no,display_action,repair_suggestion_required_yes_no,suggested_rewrite,reason_code,rationale,confidence_1_to_5
```

Save the returned CSV to any local path, for example
`/tmp/realpaper_llm_output.csv`, then score it:

```bash
python3 src/claimcontractbench.py realpaper-demo \
  --adjudication path/to/llm_output.csv \
  --output /tmp/claimcontractbench_realpaper_llm_score
```

## Evidence Files

| File | Purpose |
| --- | --- |
| `artifact/real_paper_review_template_cards_v18_20260606.csv` | Three validated template cards. |
| `artifact/real_paper_review_source_manifest_v318b_20260606.csv` | 18 public source papers and URLs. |
| `artifact/real_paper_review_candidate_claims_v318b_20260606.csv` | 72 public-paper candidate rows for blind-style trial use. |
| `artifact/real_paper_review_reference_outcomes_v318b_20260606.csv` | Post-run reference labels plus conservative aggregate outcomes. Do not give this file to an LLM before adjudication. |
| `artifact/real_paper_review_evidence_summary_v318b_20260606.json` | Aggregate diagnostic numbers and limitations. |
| `artifact/real_paper_review_public_manifest_v318b_20260606.json` | Hashes for the public addendum files. |

## Boundary

This demo is valuable because it shows registered templates operating on
public-paper candidate claims. The candidate claims are supplied by the
artifact authors; they are not discovered automatically by the tool. It does
not show automatic full-paper claim discovery, human reviewer utility, broad
empirical-ML coverage, or zero-risk claim release.

The main residual failure mode is important: unsafe releases remain concentrated
in `uncertainty_calibration` background/support-only rows. Treat that as a
boundary signal, not a success to hide.
