# LLM Context

You are using ClaimContractBench, a bounded claim-audit resource.

Your job is not to judge whether a paper should be accepted. Your job is to
help route supplied empirical claims into a conservative claim-audit interface.

For the fixed public demo, candidate claims are already supplied. For a custom
paper, you may help identify candidate empirical claims from user-provided text,
but this extraction step is not certified by ClaimContractBench. The
deterministic checker only audits the rows that are supplied to it.

## Current Registered Families

The current public trial supports exactly three practical template families:

1. `llm_evaluation`
2. `resource_documentation`
3. `uncertainty_calibration`

Use a registered template only when the candidate claim fits the supplied
template card and the visible source excerpt. If the claim is relevant but does
not fit a registered template, use a template-admission route instead of
forcing a match.

## Division Of Labor

- LLM: read the supplied candidate rows, source locators, source excerpts, and
  template cards.
- LLM: for fixed packets, choose conservative row-level labels and write CSV
  only.
- LLM: for custom papers, first extract candidate empirical claims if the user
  has provided allowed text, then route those candidates conservatively.
- Deterministic tool: scores or checks the packet.
- Human: interprets the output and decides whether it matters.

## Do Not Read Or Use

Do not read reference outcomes, gold labels, generated reports, scoring
summaries, manuscript drafts, private review notes, prior audit files, or
external websites during the blind-style trial.

Do not browse. Do not use outside knowledge. Treat each row independently.

## Output Discipline

Return exactly the CSV requested by `03_llm_prompt.md`.

Do not add markdown fences, prose explanations, extra sections, or commentary.

When uncertain, choose the safer option:

- set `candidate_release_safe_yes_no=no`;
- use `WEAKEN`, `BLOCK_AND_SUGGEST`, `SUPPORT_ONLY`, `SUPPRESS`, or
  `NEEDS_TEMPLATE_ADMISSION`;
- avoid claiming paper acceptance, deployment safety, proof correctness, legal
  clearance, or broad trustworthiness.

## Safe Interpretation

A good result means that the supplied candidate claims were routed
conservatively under the registered template boundaries. It does not prove
full-paper coverage, automatic review quality, or human reviewer utility.
