# LLM Prompt For The Real-Paper Template Review Demo

You are adjudicating candidate empirical claims against short source excerpts
and registered claim-template scopes.

Use only the candidate packet and template-card file provided by the user. Do
not browse. Do not use outside knowledge. Do not read reference, gold, scoring,
private, map, manuscript, prior-result, or audit files. Treat every row
independently.

Input files:

`artifact/real_paper_review_candidate_claims_v318b_20260606.csv`

`artifact/real_paper_review_template_cards_v18_20260606.csv`

Return exactly one CSV row for each input row, with this header:

`row_id,source_support_status,claim_role,reportability_gate,candidate_release_safe_yes_no,display_action,repair_suggestion_required_yes_no,suggested_rewrite,reason_code,rationale,confidence_1_to_5`

Allowed values:

`source_support_status`

- `directly_supported`
- `partially_supported`
- `background_only`
- `contradicted_by_source`
- `not_supported`
- `out_of_scope`

`claim_role`

- `bounded_method_or_design_claim`
- `primary_result_claim`
- `resource_or_dataset_description`
- `evaluation_or_protocol_scope`
- `calibration_or_uncertainty_claim`
- `background_or_motivation_context`
- `limitation_or_caveat`
- `deployment_or_policy_claim`
- `proof_or_theory_correctness`
- `paper_acceptance_or_review_judgment`

`reportability_gate`

- `reportable_as_claim`
- `reportable_after_weakening`
- `blocked_but_corrected_claim_available`
- `support_only_context`
- `suppress_no_safe_public_claim`
- `do_not_call_claim_runner`

`candidate_release_safe_yes_no`

- `yes`
- `no`

`display_action`

- `ACCEPT`
- `WEAKEN`
- `BLOCK_AND_SUGGEST`
- `SUPPORT_ONLY`
- `SUPPRESS`
- `REJECT_OR_OUT_OF_SCOPE`
- `NEEDS_TEMPLATE_ADMISSION`

`repair_suggestion_required_yes_no`

- `yes`
- `no`

`reason_code`

- `source_supports_candidate`
- `source_supports_weakened_candidate`
- `source_supports_corrected_claim_but_candidate_blocked`
- `source_background_only`
- `source_forbids_candidate_no_repair`
- `outside_registered_template_family`
- `out_of_scope_for_claim_contract`

Rules:

1. Use the row's `family` and `template_id`; do not invent a new family.
2. If the candidate is directly supported within the same scope, choose
   `ACCEPT` and `candidate_release_safe_yes_no=yes`.
3. If the candidate is too broad but the same object can be narrowed, choose
   `WEAKEN` or `BLOCK_AND_SUGGEST`, set `candidate_release_safe_yes_no=no`, and
   provide a safer `suggested_rewrite`.
4. If the source excerpt is background, motivation, definition, method context,
   or a limitation rather than a releaseable empirical claim, choose
   `SUPPORT_ONLY` or `SUPPRESS`; do not mark it safe just because the sentence is
   true.
5. If the row asks for legal clearance, deployment approval, proof correctness,
   clinical approval, paper acceptance, or broad trustworthiness outside the
   source excerpt, choose `REJECT_OR_OUT_OF_SCOPE`.
6. When uncertain, prefer `candidate_release_safe_yes_no=no`.
7. Do not add markdown, explanation paragraphs, or code fences. Return CSV only.
