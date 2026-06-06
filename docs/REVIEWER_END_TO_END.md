# Reviewer End-To-End Workflow

This page is the shortest complete path from opening the GitHub repository to
getting an interpretable ClaimContractBench result.

Use it if you are a reviewer, artifact evaluator, or first-time user who wants
to check whether the resource can be run and what its output means.

## What You Can Test

ClaimContractBench audits supplied candidate empirical claims against registered
claim templates and evidence boundaries. In this snapshot, the practical
review surface covers three template families:

| Family | What it is for |
| --- | --- |
| `llm_evaluation` | Benchmark, evaluation protocol, metric-scope, and model-as-judge claims. |
| `resource_documentation` | Dataset, resource, schema, provenance, and release-documentation claims. |
| `uncertainty_calibration` | Calibration, uncertainty, conformal, diagnostic, and probabilistic-support claims. |

The tool does not automatically find every claim in a paper. For a new paper,
a human reviewer or an approved LLM front end must first identify candidate
claims. The deterministic checker then audits the supplied packet.

## Step 1: Get The Frozen Snapshot

Open:

```text
https://github.com/civimuro/claimcontractbench-cikm2026-submission-freeze
```

Then either download the repository ZIP from GitHub or clone it:

```bash
git clone https://github.com/civimuro/claimcontractbench-cikm2026-submission-freeze.git
cd claimcontractbench-cikm2026-submission-freeze
git checkout v0.1.7-cikm2026-reviewer-closure
```

If you use the ZIP button instead of git, unzip the file and open a terminal in
the unzipped folder.

## Step 2: Run The No-LLM Reviewer Trial

Run one command:

```bash
python3 src/claimcontractbench.py try-human
```

This command:

1. checks that the public release surface is present and manifest-controlled;
2. runs the 72-row public-paper real-paper demo over the three registered
   template families;
3. writes the result outside the checkout so the repository stays clean.

Open the generated report:

```text
/tmp/claimcontractbench_human_trial/real_paper_review_demo_report.md
```

Expected high-level result:

```text
PASS release surface validation
rows: 133
required_files: 133
public_safe_rows: 133
raw_data_rows: 0

PASS real-paper review demo
rows: 72
source_papers: 18
conservative_candidate_safety_accuracy: 0.958
conservative_display_action_accuracy: 0.806
conservative_unsafe_false_releases: 3
```

## Step 3: Verify The Package

Run:

```bash
python3 src/claimcontractbench.py doctor
python3 src/claimcontractbench.py smoke
```

Expected smoke result:

```text
PASS release smoke suite
positive_checks: 14
negative_fail_closed_checks: 5
```

The smoke suite checks the visible user paths, including the human trial, LLM
trial packet, claim-identification guide, reviewer workflow guide, and
fail-closed negative packets.

## Step 4: Interpret The Result

Safe conclusion:

> For supplied candidate claims in the three registered template families,
> ClaimContractBench can replay a deterministic claim-audit surface that
> accepts, weakens, blocks-and-suggests, marks support-only, suppresses, or
> rejects/out-of-scope rows under explicit template boundaries.

Do not conclude:

- automatic full-paper review;
- paper accept/reject recommendation;
- proof of human reviewer utility;
- broad empirical-ML coverage;
- zero-risk claim release;
- raw-data or full-PDF redistribution.

## If You Want An LLM-Assisted Trial

Run:

```bash
python3 src/claimcontractbench.py try-llm
```

This creates:

```text
/tmp/claimcontractbench_llm_trial/
```

Give the LLM only the files copied into that folder. They contain candidate
claims, template cards, a prompt, and LLM context. They do not include gold
reference outcomes.

After the LLM returns a CSV, score it with:

```bash
python3 src/claimcontractbench.py realpaper-demo \
  --adjudication /path/to/llm_output.csv \
  --output /tmp/claimcontractbench_realpaper_llm_score
```

## If You Want To Try A New Paper

There are two roles:

1. The human or LLM front end identifies candidate empirical claims.
2. ClaimContractBench audits the supplied claim packet.

For humans:

```bash
python3 src/claimcontractbench.py templates
python3 src/claimcontractbench.py init-packet --output claim_packets/my_claim_packet.csv
```

Fill one row per candidate claim, then run:

```bash
python3 src/claimcontractbench.py review --input claim_packets/my_claim_packet.csv
```

For LLM-assisted use, read:

```bash
python3 src/claimcontractbench.py agent-guide
```

Important rule: use `CALL_REGISTERED_TEMPLATE` only for exact registered
template matches. Use `NEEDS_TEMPLATE_ADMISSION` when a claim is relevant but
does not have a matching template. Use `OUT_OF_SCOPE_DO_NOT_CALL` for claims
outside metric-to-claim review.

## If No Template Fits

Do not force the claim into a nearby template. Run:

```bash
python3 src/claimcontractbench.py admission-guide
```

A new template must specify an evidence unit, claim template, `G/Q/U` bindings,
action mapping, preorder or incomparability relation, forbidden stronger claim,
visual or case anchor, and boundary note.

## Where To Read More

| Need | File or command |
| --- | --- |
| First contact | `docs/START_HERE.md` |
| Claim identification boundary | `docs/CLAIM_IDENTIFICATION.md` |
| Current three supported families | `docs/SUPPORTED_TEMPLATE_FAMILIES.md` |
| Human-only inspection | `docs/HUMAN_REVIEWER_GUIDE.md` |
| LLM-assisted path | `docs/LLM_CONTEXT.md` and `docs/LLM_ASSISTED_PATH.md` |
| Evidence and report map | `docs/REPORT_INDEX.md` |
| Boundaries and non-goals | `docs/BOUNDARIES.md` |
