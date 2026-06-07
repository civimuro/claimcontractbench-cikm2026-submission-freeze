# Template-Rule Stress Fresh Rerun Protocol

Status: `PUBLIC_SAFE_RERUN_PACKET`

This packet lets a reviewer or tool developer rerun the first validation-ladder
rung as a fresh LLM-proxy exercise. It is not an exact-reproducibility claim:
new LLM calls may differ from the frozen run. The point is to expose the same
inputs, prompt, output schema, and scoring target so a fresh run can be compared
against the frozen proxy adjudication.

## Files

- `template_rule_stress_blind_rows_20260605.csv`: 42 public-safe blind rows.
- `template_rule_stress_rerun_prompt_20260605.txt`: clean annotator prompt.
- `template_rule_stress_output_schema_20260605.md`: required output columns.
- `template_rule_stress_proxy_adjudication_20260605.csv`: frozen proxy
  adjudication used only for scoring after the fresh output is complete.

## Rerun Steps

1. Give the clean prompt to an LLM or annotator.
2. Do not show `template_rule_stress_channel_A_20260605.csv`,
   `template_rule_stress_channel_B_20260605.csv`,
   `template_rule_stress_proxy_adjudication_20260605.csv`, or
   `template_rule_stress_summary_20260605.json` before the output is produced.
3. Save the fresh output as CSV with the schema in
   `template_rule_stress_output_schema_20260605.md`.
4. Score the fresh output:

```bash
python3 src/claimcontractbench.py score-rerun \
  --rung template-stress \
  --input /path/to/fresh_template_stress_output.csv \
  --output /tmp/claimcontractbench_template_stress_rerun_score
```

## Interpretation

This rerun can support statements about LLM-proxy stability under a clean,
public-safe packet. It does not create human expert gold, human reviewer
utility evidence, or an automatic paper-review result.

