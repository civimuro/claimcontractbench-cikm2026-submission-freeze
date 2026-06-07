# V3.4 Failure And Baseline Audit

Date: 2026-06-05

Status: `COMPLETED_WITH_ACTIONABLE_SHORTFALLS`

## Bottom Line

V3.4 is a positive real-paper usability validation, but it is not a strong robustness experiment. The locked gold is dominated by `ACCEPT` and release-side rows, so micro accuracy and release-side accuracy are easy to inflate. The right paper claim is bounded admitted-template use, not robust automatic review.

## Gold Distribution

| Quantity | Value |
| --- | --- |
| rows | `72` |
| action distribution | `{'ACCEPT': 62, 'REWRITE': 8, 'SUPPORT_ONLY': 2}` |
| release-side distribution | `{'nonrelease': 2, 'release': 70}` |
| danger flag distribution | `{'no': 70, 'review': 2}` |

## Baselines

| Condition | Action accuracy | Release-side accuracy | Macro-F1 |
| --- | ---: | ---: | ---: |
| `always_ACCEPT` | `62/72 (0.861)` | `70/72 (0.972)` | `0.308` |
| `always_REWRITE` | `8/72 (0.111)` | `70/72 (0.972)` | `0.067` |
| `always_SUPPORT_ONLY` | `2/72 (0.028)` | `2/72 (0.028)` | `0.018` |
| `family_majority_action` | `62/72 (0.861)` | `70/72 (0.972)` | `0.308` |

## Router Scores Against Baselines

| Router | Action accuracy | Wilson 95% | Release-side accuracy | Macro-F1 |
| --- | ---: | --- | ---: | ---: |
| `R0_A` | `69/72 (0.958)` | `0.885`--`0.986` | `72/72 (1.000)` | `0.925` |
| `R0_B` | `68/72 (0.944)` | `0.866`--`0.978` | `72/72 (1.000)` | `0.894` |
| `R1_A` | `66/72 (0.917)` | `0.830`--`0.961` | `70/72 (0.972)` | `0.567` |
| `R1_B` | `66/72 (0.917)` | `0.830`--`0.961` | `72/72 (1.000)` | `0.873` |
| `R4_A` | `70/72 (0.972)` | `0.904`--`0.992` | `72/72 (1.000)` | `0.947` |
| `R4_B` | `69/72 (0.958)` | `0.885`--`0.986` | `72/72 (1.000)` | `0.925` |

## Failure Pattern

- Always-`ACCEPT` already reaches 62/72 action accuracy and 70/72 release-side accuracy.
- Always-release reaches 70/72 release-side accuracy, so V3.4 release-side accuracy is weak as a headline metric.
- `SUPPORT_ONLY` has only two gold rows; any 2/2 result has a wide uncertainty interval.
- The recurring failure mode is `REWRITE -> ACCEPT`, meaning the router can release a claim without the required repair.

Most recurring mismatches:

| Row | Mismatch count across routers | Family | Gold |
| --- | ---: | --- | --- |
| `V34X-V34H-LLM-002-03` | 6 | `llm_evaluation` | `REWRITE` |
| `V34X-V34H-UNC-003-01` | 6 | `uncertainty_calibration` | `REWRITE` |
| `V34X-V34H-LLM-002-01` | 5 | `llm_evaluation` | `ACCEPT` |
| `V34X-V34H-LLM-003-04` | 1 | `llm_evaluation` | `ACCEPT` |
| `V34X-V34H-RES-001-02` | 1 | `resource_documentation` | `ACCEPT` |
| `V34X-V34H-RES-001-03` | 1 | `resource_documentation` | `REWRITE` |
| `V34X-V34H-RES-003-02` | 1 | `resource_documentation` | `ACCEPT` |
| `V34X-V34H-RES-006-04` | 1 | `resource_documentation` | `ACCEPT` |
| `V34X-V34H-UNC-004-02` | 1 | `uncertainty_calibration` | `SUPPORT_ONLY` |
| `V34X-V34H-UNC-005-01` | 1 | `uncertainty_calibration` | `SUPPORT_ONLY` |

## Required Follow-Up

V3.5 should not be another positive-only rerun. It should be a balanced challenge using public-paper source anchors, with explicit `ACCEPT`, `REWRITE`, `WEAKEN`, `SUPPORT_ONLY`, `SUPPRESS`, and `NEEDS_TEMPLATE_ADMISSION` targets, plus majority/action/release baselines and per-class recall.
