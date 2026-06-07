# Validation Ladder

This page explains how the release supports the paper-facing claims about
template reliability and real-paper use.  It is for reviewers who want to check
the validation evidence rather than only run the shortest demo.

Run:

```bash
python3 src/claimcontractbench.py validation-ladder \
  --output /tmp/claimcontractbench_validation_ladder
```

Then open:

```text
/tmp/claimcontractbench_validation_ladder/validation_ladder_report.md
```

## What The Ladder Checks

| Rung | Files | Command support | What it supports | What it does not support |
| --- | --- | --- | --- | --- |
| Template-rule stress | `artifact/validation_ladder_20260607/template_rule_stress_*.csv/json`, plus a clean rerun prompt and protocol | Recomputed by `validation-ladder`; fresh reruns can be scored with `score-rerun --rung template-stress` | The admitted action taxonomy can separate accept, rewrite, weaken, support-only, suppress, and out-of-scope decisions in a 42-row cross-model LLM-proxy blind packet. | Human-independent reliability, human reviewer utility, exact reproduction of new LLM calls, or automatic paper review. |
| Positive real-paper use | `artifact/validation_ladder_20260607/positive_realpaper_*.csv/json/md`, plus a public-safe rerun candidate packet, source pool, and locked reference | Recomputed by `validation-ladder`; fresh reruns can be scored with `score-rerun --rung positive-realpaper` | Three admitted template families can process supplied candidate rows from 18 public papers with 70/72 and 69/72 action accuracy across two proxy channels and zero dangerous false releases in that positive packet. | Strong robustness: this packet is mostly release-side/acceptable rows, so it must not be used alone as a safety claim. It is also not human expert gold. |
| Reportability-boundary replay | `artifact/real_paper_review_candidate_claims_v318b_20260606.csv`, `artifact/real_paper_review_reference_outcomes_v318b_20260606.csv` | Recomputed by `validation-ladder`; directly runnable by `realpaper-demo` | The same three-family public-paper surface exposes the remaining boundary: conservative release safety `0.958`, action/gate accuracy `0.806`, and 3 unsafe false releases. | Full-paper claim discovery, autonomous review, human utility, or zero-risk use. |

## Why This Exists

The paper should not cite validation numbers that cannot be checked from the
frozen release.  This ladder therefore makes the result trail explicit:

- the first rung is a template-rule diagnostic;
- the second rung is a positive admitted-template use diagnostic;
- the third rung is the harder boundary replay that ordinary users can also
  try through `realpaper-demo`.

The first two rungs are not ordinary end-user workflows. They are evidence
assets for reviewers and tool developers. The ordinary no-LLM trial remains:

```bash
python3 src/claimcontractbench.py try-human
```

## Frozen Replay Versus Fresh Rerun

The frozen validation numbers are exactly recomputable from repository files.
Fresh LLM reruns are different: a new model call may not reproduce the same row
labels. The release therefore exposes rerun packets so reviewers can repeat the
task approximately and then score the new output against the locked reference:

```bash
python3 src/claimcontractbench.py score-rerun \
  --rung template-stress \
  --input /path/to/fresh_template_output.csv \
  --output /tmp/template_rerun_score

python3 src/claimcontractbench.py score-rerun \
  --rung positive-realpaper \
  --input /path/to/fresh_positive_output.csv \
  --output /tmp/positive_rerun_score
```

See `docs/VALIDATION_RERUN_PACKETS.md` for the exact rerun files and
interpretation boundary.

## Public-Safety Policy

The ladder stores public-safe rows, short claim text, source URLs where already
present in the source packet, row-level action labels, and aggregate metrics.
It does not store PDFs, full paper text, private review notes, local experiment
caches, credentials, or private coordination paths.

The `validation-ladder` command performs a public-safety scan over the ladder
files before reporting success.

For the license boundary on short excerpts and for the exact meaning of
"correct" in each rung, read `docs/PUBLIC_EXCERPT_AND_LABEL_POLICY.md`.

## Safe Wording

Supported:

> The release provides a public-safe validation ladder showing that admitted
> claim-template rules can be inspected and replayed on supplied candidate
> rows, including a positive public-paper packet and a harder boundary replay.

Not supported:

> The system automatically reviews papers, discovers all claims, improves human
> reviewer decisions, covers all empirical ML domains, or releases claims with
> zero risk.
