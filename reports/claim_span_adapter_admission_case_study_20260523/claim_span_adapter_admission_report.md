# Claim-Span Adapter Admission Case Study

Status: `PASS`.
Recommendation: `USE_AS_CONTROLLED_ADAPTER_ADMISSION_EVIDENCE`.

This case study admits selected families from the adjudicated claim-span gold through finite adapter templates. It is an extensibility demonstration, not an autonomous paper-review claim.

## Summary

| Metric | Value |
| --- | ---: |
| selected families | `conformal_prediction,dataset_documentation,llm_evaluation` |
| admitted rows | 22 |
| adapter spec rows | 6 |
| renderer | `deterministic_target_kind_span_renderer` |
| renderer inputs | `source_family,claim_level_target_kind,claim_level_span_found,span_match_type` |
| passport rows | 22 |
| action counts | `{'ACCEPT': 9, 'REWRITE': 6, 'SUPPORT_ONLY': 2, 'SUPPRESS': 1, 'WEAKEN': 4}` |
| evidence modes | `{'absence_boundary_rewrite': 2, 'direct_span_support': 8, 'localized_boundary_or_limitation': 9, 'partial_or_narrower_span_support': 3}` |
| protected false releases | 0 |
| no-span ACCEPT rows | 0 |
| checks passed | 10 |
| checks failed | 0 |

## Checks

| Check | Status | Evidence |
| --- | --- | --- |
| CSADAPT-01 spec fields complete | PASS | all adapter specs fill finite template, G/Q/U, action, preorder, forbidden, and passport fields |
| CSADAPT-02 selected families covered | PASS | family_counts={'conformal_prediction': 5, 'dataset_documentation': 8, 'llm_evaluation': 9} |
| CSADAPT-03 nontrivial action mix | PASS | action_counts={'ACCEPT': 9, 'REWRITE': 6, 'SUPPORT_ONLY': 2, 'SUPPRESS': 1, 'WEAKEN': 4} |
| CSADAPT-04 computed actions match post-admission gold | PASS | matched=22/22 |
| CSADAPT-05 protected false release is zero | PASS | no SUPPRESS/REJECT/OUT_OF_SCOPE gold rows released as positive claims |
| CSADAPT-06 no ACCEPT without localized support | PASS | no no-span/no-match row is admitted as ACCEPT |
| CSADAPT-07 passport rows emitted | PASS | passport_rows=22 |
| CSADAPT-08 upstream limitations carried | PASS | provenance=PASS_WITH_WARNINGS; wording=PASS |
| CSADAPT-09 private-marker hygiene | PASS | no private markers in adapter case-study rows |
| CSADAPT-10 structural boundary diversity | PASS | template_roles=broad_capability_boundary,conditional_or_instance_boundary,documentation_context_accept,documentation_to_deployment_boundary,marginal_or_declared_risk_accept,scenario_prompt_metric_accept |

## Interpretation

The result upgrades the application branch from a pure `NEEDS_TEMPLATE_ADMISSION` bottleneck to a bounded demonstration of how admission can work: new families supply templates, G/Q/U, action mappings, typed preorders, forbidden claims, and passport rows, then replay against adjudicated paper text without releasing protected claims.

The key remaining limitation is unchanged: the upstream claim-span gold is internal and cue-reduced, with provenance warnings. This case study strengthens controlled extensibility, not raw extraction reliability.
