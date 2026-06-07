# V3.4 Router Score Aggregate

Rows: `72`

| Condition | Action accuracy | Emit accuracy | Release-side accuracy | Dangerous false release | Release when gold non-release | False suppress | Protected when gold release | Macro-F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `R4_A` | `0.972` | `1.000` | `1.000` | 0 | 0 | 0 | 0 | `0.947` |
| `R4_B` | `0.958` | `1.000` | `1.000` | 0 | 0 | 0 | 0 | `0.925` |

## Family-Level Action Accuracy

| Condition | Family | Rows | Action accuracy | Release-side accuracy | Dangerous false release |
| --- | --- | ---: | ---: | ---: | ---: |
| `R4_A` | `llm_evaluation` | 24 | `0.958` | `1.000` | 0 |
| `R4_A` | `resource_documentation` | 24 | `1.000` | `1.000` | 0 |
| `R4_A` | `uncertainty_calibration` | 24 | `0.958` | `1.000` | 0 |
| `R4_B` | `llm_evaluation` | 24 | `0.917` | `1.000` | 0 |
| `R4_B` | `resource_documentation` | 24 | `1.000` | `1.000` | 0 |
| `R4_B` | `uncertainty_calibration` | 24 | `0.958` | `1.000` | 0 |
