# Human Reviewer Guide

This guide is for people who want to inspect ClaimContractBench without using an
LLM. If you are doing a first-pass artifact review, start with
`docs/REVIEWER_CHECKLIST.md`; this guide is the deeper manual walkthrough.

## What To Do First

If you want the complete GitHub-to-result path first, run:

```bash
python3 src/claimcontractbench.py reviewer-flow
```

Then run the no-LLM trial. If you want the lowest-friction trial only, run:

```bash
python3 src/claimcontractbench.py try-human
```

This validates the release surface and runs the current three-family public
paper demo into `/tmp/claimcontractbench_human_trial`.

For a deeper verification pass, run:

```bash
python3 src/claimcontractbench.py doctor
python3 src/claimcontractbench.py smoke
```

If both pass, the release is runnable, public-safe, and internally consistent
for first inspection.

## What To Read Next

1. `docs/REVIEWER_END_TO_END.md`
2. `docs/REVIEWER_CHECKLIST.md`
3. `docs/START_HERE.md`
4. `docs/CLAIM_IDENTIFICATION.md`
5. `docs/SUPPORTED_TEMPLATE_FAMILIES.md`
6. `docs/CONCEPTS.md`
7. `docs/EXAMPLE_OUTPUTS.md`
8. `docs/REPORT_INDEX.md`
9. `docs/BOUNDARIES.md`
10. `docs/DATA_AND_LICENSES.md`
11. `docs/EVALUATION_SOURCE_INVENTORY.md` if you want the advanced public-paper
   benchmark/source inventory rather than the ordinary user path.

These files explain what the commands prove, where the generated reports go,
and which claims are intentionally out of scope.

## How To Inspect The Main Resource Object

The smallest concrete object is the five-row claim passport casebook:

```text
data/claim_passport_casebook_20260519.csv
```

It contains one example for each action family:

- emit as written;
- relabel as upper-bound reference;
- weaken to diagnostic support;
- rewrite to decision-local claim;
- suppress to `bottom_T`.

To regenerate and check those rows:

```bash
python3 src/run_projection_smoke.py
```

## How To Inspect The Evidence Surface

Use:

```bash
python3 src/run_claim_audit_report.py --output reports/claim_audit_report_20260521
```

The generated report summarizes the claim-passport rows, `G/Q/U` intervention
fields, Q-policy sensitivity rows, support-only adapter rows, and resource
boundary checks.

Use `docs/REPORT_INDEX.md` to connect each runner to the paper-facing claim it
supports.

## How To Interpret A Result

A result can support statements such as:

- the release files are present and public-safe;
- the registered examples regenerate;
- unknown or malformed template calls fail closed;
- unsupported external paper claims are not silently released as licensed
  claims;
- selected excerpt decisions are safe in human-gold-oracle mode.

A result does not support statements such as:

- the tool read an entire paper autonomously;
- the tool makes accept/reject recommendations;
- the tool proves scientific correctness;
- the tool proves human reviewer utility;
- the repository redistributes raw third-party datasets.

## If You Want To Try A Paper Manually

You can write your own CSV packet without an LLM:

```bash
python3 src/claimcontractbench.py init-packet --output claim_packets/my_claim_packet.csv
python3 src/claimcontractbench.py templates
```

Fill one row per candidate claim. Use:

- `CALL_REGISTERED_TEMPLATE` only for exact template matches;
- `NEEDS_TEMPLATE_ADMISSION` when the claim is relevant but no template fits;
- `OUT_OF_SCOPE_DO_NOT_CALL` when the claim is outside metric-to-claim review.

Then run:

```bash
python3 src/claimcontractbench.py review --input claim_packets/my_claim_packet.csv
```

The report is a claim-audit aid, not a review verdict.

The manual step is claim identification: you choose which empirical claims to
inspect. The tool does not prove that you found every relevant claim in the
paper. Use `docs/CLAIM_IDENTIFICATION.md` for selection rules.

## If You Want To Ask A Public Question

Use `SUPPORT.md` and the GitHub issue templates. Keep questions public-safe:
paraphrase examples, avoid confidential paper text, and do not upload raw data
or private review notes.
