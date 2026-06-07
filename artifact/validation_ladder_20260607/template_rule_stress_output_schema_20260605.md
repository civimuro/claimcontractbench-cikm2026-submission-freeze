# Output Schemas

Status: `PUBLIC_DRAFT`

## 1. Annotator A/B Output

CSV header:

```csv
heldout_annotation_id,heldout_row_id,annotator_action,annotator_claim_level_span_found,annotator_span_match_type,annotator_real_section,annotator_real_span,annotator_span_word_count,annotator_confidence_1_to_5,annotator_not_found_reason,annotator_rationale,annotator_notes
```

Allowed `annotator_action`:

- `ACCEPT`
- `REWRITE`
- `WEAKEN`
- `SUPPORT_ONLY`
- `SUPPRESS`
- `REJECT_OR_OUT_OF_SCOPE`

Allowed `annotator_claim_level_span_found`:

- `yes`
- `partial`
- `no`

Allowed `annotator_span_match_type`:

- `exact_support`
- `narrower_support`
- `limitation_boundary`
- `no_match`
- `out_of_scope`

Rules:

- `annotator_confidence_1_to_5` is an integer from 1 to 5.
- If span is found, `annotator_real_span` must be filled.
- If span is not found, `annotator_real_span` is blank and `annotator_span_word_count` is 0.

## 2. Adjudicator Output

CSV header:

```csv
heldout_row_id,gold_action,gold_claim_level_span_found,gold_span_match_type,gold_real_section,gold_real_span,gold_reason,adjudication_status,adjudication_confidence_1_to_5,disagreement_type,target_drift_from_design,dangerous_boundary_flag,coordinator_notes
```

Allowed `adjudication_status`:

- `LOCKED_ADJUDICATED_DRAFT`

Allowed `disagreement_type`:

- `none`
- `action_disagreement`
- `span_presence_disagreement`
- `match_type_disagreement`
- `severity_disagreement`
- `rewrite_weaken_boundary`
- `weaken_suppress_boundary`
- `out_of_scope_boundary`
- `multiple`

Allowed `dangerous_boundary_flag`:

- `yes`
- `no`

## 3. Candidate Extraction Output

CSV header:

```csv
candidate_id,section_locator,claim_text,source_span,source_span_word_count,candidate_family,claim_strength,requires_template_admission,extraction_confidence_1_to_5,reason
```

Allowed `candidate_family`:

- `conformal_prediction`
- `dataset_documentation`
- `llm_evaluation`
- `calibration`
- `selective_prediction`
- `distribution_shift`
- `robustness_benchmark`
- `model_reporting`
- `benchmark_validity`
- `unknown_or_needs_admission`
- `out_of_scope`

Allowed `claim_strength`:

- `narrow`
- `moderate`
- `broad`
- `deployment_or_policy`
- `universal_or_replacement`
- `out_of_scope`

Allowed `requires_template_admission`:

- `yes`
- `no`
