# Start Here

ClaimContractBench is easiest to try in two separate paths.

If you are a reviewer opening the GitHub repository for the first time, the
most complete path is `docs/REVIEWER_END_TO_END.md` or:

```bash
python3 src/claimcontractbench.py reviewer-flow
```

Use the human path if you want to inspect the resource yourself. Use the LLM
path if you want an AI assistant to help adjudicate supplied candidate claims
inside the current registered templates.

The tool does not find every claim in a paper by itself. It audits supplied
candidate claims. For a custom paper, a human or an LLM must first identify
candidate empirical claims. See `docs/CLAIM_IDENTIFICATION.md`.

## Path A: Human / Reviewer Trial

Run one command:

```bash
python3 src/claimcontractbench.py try-human
```

This checks the public release surface and runs the three-family real-paper
demo into `/tmp/claimcontractbench_human_trial`.

Open:

```text
/tmp/claimcontractbench_human_trial/real_paper_review_demo_report.md
```

This path needs no LLM, no raw data, no GPU, no network access, and no third
party Python packages.

## Path B: LLM-Assisted Trial

Run one command:

```bash
python3 src/claimcontractbench.py try-llm
```

This creates a clean LLM packet in `/tmp/claimcontractbench_llm_trial`:

- `01_candidate_claims.csv`
- `02_template_cards.csv`
- `03_llm_prompt.md`
- `README_FOR_LLM.md`

Give the LLM only those copied files. Do not give it reference outcomes,
generated reports, scoring summaries, manuscript text, private review notes, or
prior audit files.

After the LLM returns a CSV, score it with:

```bash
python3 src/claimcontractbench.py realpaper-demo \
  --adjudication /path/to/llm_output.csv \
  --output /tmp/claimcontractbench_realpaper_llm_score
```

## Current Working Capability

The current practical template surface covers three registered families:

| Family | Template | Current use |
| --- | --- | --- |
| `llm_evaluation` | `TPL-LLM-EVAL-V18` | Benchmark, evaluation protocol, model-as-judge, metric-scope claims. |
| `resource_documentation` | `TPL-RESOURCE-DOC-V18` | Resource, dataset, metadata, schema, provenance, and release-documentation claims. |
| `uncertainty_calibration` | `TPL-UNCERTAINTY-CAL-V18` | Calibration, uncertainty, conformal, diagnostic, and probabilistic-support claims. |

The real-paper trial uses 18 public arXiv papers and 72 supplied candidate
claims: 6 papers and 24 candidate rows per family.

## Claim Identification Boundary

The fixed demo already includes candidate claims. A new paper does not.

- Human path: the reviewer selects candidate empirical claims manually, then
  fills or checks a packet.
- LLM path: the LLM may extract candidate empirical claims and route them into
  a packet, but the deterministic checker still decides whether a registered
  template was called safely.

Neither path proves full-paper coverage.

## What To Conclude

Safe conclusion:

> For supplied candidate claims in the three registered families,
> ClaimContractBench can replay a deterministic claim-audit surface that
> accepts, weakens, blocks-and-suggests, marks support-only, suppresses, or
> rejects/out-of-scope rows under explicit template boundaries.

Do not conclude:

- automatic full-paper review;
- human reviewer utility;
- broad empirical-ML coverage;
- zero-risk claim release;
- paper acceptance or rejection advice.

For unsupported domains, use template admission instead of forcing a nearby
template:

```bash
python3 src/claimcontractbench.py admission-guide
```
