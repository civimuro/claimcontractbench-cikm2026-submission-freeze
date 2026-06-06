# Claim Template Admission Report

Status: generated from release-root public-safe assets.

## Contribution Target

This report tests whether new claims and new domains can enter the typed claim-contract workflow by satisfying an explicit adapter admission interface. It is meant to distinguish real scope expansion from benchmark-table sprawl.

## Summary

| Item | Value |
| --- | ---: |
| templates | 9 |
| admitted_mainline | 5 |
| admitted_support_only | 3 |
| boundary_probe | 0 |
| rejected | 1 |
| checks_passed | 10 |
| checks_failed | 0 |

## Admission Checks

| Check | Status | Evidence |
| --- | --- | --- |
| ADM-01 inputs present | PASS | schema, cases, casebook, and NAB visual rows loaded |
| ADM-02 case header alignment | PASS | case header has 16 expected columns |
| ADM-03 public-safe template text | PASS | 9 templates have no private path or credential markers |
| ADM-04 expected verdict agreement | PASS | computed levels and verdicts match expected admission labels |
| ADM-05 anchor resolution | PASS | admitted templates resolve to CP or NAB visual anchors |
| ADM-06 critical-field completeness for admitted templates | PASS | 8 admitted templates provide all nine critical fields |
| ADM-07 mainline action coverage | PASS | mainline templates cover all five action families |
| ADM-08 support-only ceiling | PASS | support-only rows are not promoted to mainline or headline claims |
| ADM-09 boundary rejection remains active | PASS | AI4I boundary probe is rejected until it supplies the adapter contract |
| ADM-10 forbidden-claim and boundary discipline | PASS | all admitted templates include forbidden claims and boundary notes |

## Template Verdicts

| Template | Role | Action | Computed Verdict | Missing Fields | Boundary |
| --- | --- | --- | --- | --- | --- |
| CTA-CORE-01 | mainline | emit_as_written | ADMIT_MAINLINE_TEMPLATE | none | local ACS slice claim only |
| CTA-CORE-02 | mainline | relabel_as_upper_bound | ADMIT_MAINLINE_TEMPLATE | none | upper-bound reference not same-regime model superiority |
| CTA-CORE-03 | mainline | weaken_to_diagnostic | ADMIT_MAINLINE_TEMPLATE | none | diagnostic local support only |
| CTA-CORE-04 | mainline | rewrite_to_decision_local | ADMIT_MAINLINE_TEMPLATE | none | decision-local claim only |
| CTA-CORE-05 | mainline | suppress_fallback | ADMIT_MAINLINE_TEMPLATE | none | unsupported local slice claim must suppress |
| CTA-NAB-01 | support_only | emit_as_written | ADMIT_SUPPORT_ONLY_TEMPLATE | none | support-only adapter row not detector ranking |
| CTA-NAB-02 | support_only | suppress_fallback | ADMIT_SUPPORT_ONLY_TEMPLATE | none | support-only adapter row not broad anomaly validation |
| CTA-NAB-03 | support_only | weaken_to_diagnostic | ADMIT_SUPPORT_ONLY_TEMPLATE | none | support-only adapter row with explicit profile utility boundary |
| CTA-AI4I-01 | boundary_probe | none | REJECT_PATCHWORK | claim_template;G_binding;Q_binding;U_binding;action_mapping;preorder_relation;forbidden_claim;visual_or_case_anchor | not admitted until templates G/Q/U action preorder forbidden claim and visual row are supplied |

## Interpretation

- The five core templates are admitted as mainline because they already instantiate the public claim passport.
- The three NAB templates are admitted only as support-only adapter templates: they show the interface can accept a distinct evidence unit, but they do not become anomaly-detection validation or a headline claim.
- The AI4I probe is rejected by design because it has an evidence family but lacks finite claim templates, G/Q/U bindings, action mapping, typed preorder, forbidden claim, and visual passport row.

## Current Limit

The runner admits rows that are already expressed in the typed template schema. It does not infer G/Q/U or action mappings from arbitrary prose. The next high-value upgrade is to normalize the full 375-event operator trace into this release-root admission interface.
