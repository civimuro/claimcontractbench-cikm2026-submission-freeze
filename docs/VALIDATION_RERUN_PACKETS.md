# Validation Rerun Packets

The validation ladder has two different reproducibility levels.

## 1. Exact Frozen Replay

The command below recomputes the stored metrics from frozen public-safe files:

```bash
python3 src/claimcontractbench.py validation-ladder \
  --output /tmp/claimcontractbench_validation_ladder
```

This is exact in the ordinary artifact sense: the inputs, outputs, row IDs, and
scoring rules are fixed in the repository.

## 2. Fresh LLM-Proxy Rerun

Fresh LLM calls are not exact-reproducibility objects. A different model, date,
system prompt, or decoding stack may produce different row labels. The release
therefore treats fresh reruns as stability probes, not as guaranteed identical
reproduction.

For such probes, the repository now exposes public-safe rerun packets:

| Rung | Rerun packet | Scoring command |
| --- | --- | --- |
| Template-rule stress | `artifact/validation_ladder_20260607/template_rule_stress_rerun_protocol_20260607.md` | `python3 src/claimcontractbench.py score-rerun --rung template-stress --input fresh.csv --output /tmp/score` |
| Positive real-paper use | `artifact/validation_ladder_20260607/positive_realpaper_rerun_protocol_20260607.md` | `python3 src/claimcontractbench.py score-rerun --rung positive-realpaper --input fresh.csv --output /tmp/score` |
| Reportability-boundary replay | `docs/REAL_PAPER_REVIEW_DEMO.md` | `python3 src/claimcontractbench.py realpaper-demo --adjudication fresh.csv --output /tmp/demo` |

The first two packets add the missing transparency layer: they expose the same
kind of row-level material used by the diagnostics without releasing PDFs, full
text caches, private notes, local paths, or prior scoring outputs as annotator
inputs.

## What This Does And Does Not Prove

Supported:

- the frozen validation numbers can be recomputed from repository files;
- reviewers can inspect public source URLs, short excerpts, candidate claims,
  template cards, locked reference labels, and scoring code;
- independent LLM or human reruns can be compared against the frozen reference
  labels.

Not supported:

- exact reproduction of new LLM judgments;
- human expert ground truth;
- autonomous full-paper review;
- automatic claim discovery;
- broad empirical-ML coverage;
- human reviewer utility.

