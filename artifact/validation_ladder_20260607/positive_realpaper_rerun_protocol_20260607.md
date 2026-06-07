# Positive Real-Paper Fresh Rerun Protocol

Status: `PUBLIC_SAFE_RERUN_PACKET`

This packet makes the second validation-ladder rung inspectable as a fresh
source-only rerun. The frozen release already lets reviewers recompute the
stored R4_A/R4_B scores. This protocol adds the public-safe inputs needed to
rerun the adjudication task approximately: paper URLs, source locators, short
excerpts, candidate claims, template families, a clean prompt, and a locked
reference file for scoring after the fresh output is complete.

## Files

- `positive_realpaper_source_pool_20260605.csv`: 27 screened public sources,
  including the 18 selected sources and reserve/excluded candidates.
- `positive_realpaper_rerun_candidate_packet_20260605.csv`: 72 public-safe
  candidate rows from the selected public papers.
- `positive_realpaper_locked_reference_20260605.csv`: locked source-only
  reference labels. Do not show this file to an annotator before scoring.
- `artifact/real_paper_review_template_cards_v18_20260606.csv`: the three
  registered template-family cards used by the current public demo.

## Clean Annotator Prompt

Return CSV only with this exact header:

```csv
row_id,adjudicated_action,adjudicated_route_state,emit_worthy_yes_no,licensed_claim_or_note,forbidden_stronger_claim,adjudication_reason,confidence_1_to_5
```

Use only the candidate packet row, the linked template card for that row's
family, and the visible short source excerpt. The source URL may be opened only
to verify the public source and section locator; if you use it, say so in the
reason. Do not read prior router outputs, locked reference labels, aggregate
reports, paper text caches, manuscript drafts, or scoring files before writing
your output.

Allowed `adjudicated_action` values:

- `ACCEPT`
- `REWRITE`
- `WEAKEN`
- `SUPPORT_ONLY`
- `SUPPRESS`
- `REJECT_OR_OUT_OF_SCOPE`

Allowed `emit_worthy_yes_no` values:

- `yes`: the candidate, a rewrite, or a weakened version can be emitted as a
  reportable claim.
- `no`: the row should remain support-only, suppressed, or out of scope.

Treat each row as a supplied candidate claim, not as a request to review the
whole paper. The task is to decide whether this candidate row is licensed under
the registered template family and visible source support.

## Rerun Steps

1. Give the clean prompt plus
   `positive_realpaper_rerun_candidate_packet_20260605.csv` and
   `artifact/real_paper_review_template_cards_v18_20260606.csv` to the LLM or
   annotator.
2. Keep `positive_realpaper_locked_reference_20260605.csv` hidden until the
   fresh output is complete.
3. Save the fresh output as CSV.
4. Score the fresh output:

```bash
python3 src/claimcontractbench.py score-rerun \
  --rung positive-realpaper \
  --input /path/to/fresh_positive_realpaper_output.csv \
  --output /tmp/claimcontractbench_positive_realpaper_rerun_score
```

## Interpretation

This rerun can test whether the admitted templates process supplied candidate
rows from public papers in a transparent source-only setting. It remains an
LLM-proxy/source-only diagnostic. It is not human expert gold, broad robustness
evidence, full-paper claim discovery, or human reviewer utility.

