# Reviewer Quickstart

This is the reviewer-facing path for first inspection of ClaimContractBench.
It is intentionally short: no raw data download, no GPU, and no third-party
Python packages are required.

## 1. Choose A Trial Path

For the complete reviewer path from repository checkout to result:

```bash
python3 src/claimcontractbench.py reviewer-flow
```

Then use the no-LLM trial below.

For a no-LLM human/reviewer trial:

```bash
python3 src/claimcontractbench.py try-human
```

For a clean LLM packet that excludes gold/reference files:

```bash
python3 src/claimcontractbench.py try-llm
```

The human path runs the current real-paper template demo and writes a report
under `/tmp/claimcontractbench_human_trial`. The LLM path copies only the
candidate claims, template cards, prompt, and LLM context into
`/tmp/claimcontractbench_llm_trial`.

## 2. Check The Release Surface

From the repository root:

```bash
python3 src/claimcontractbench.py reviewer-checklist
python3 src/claimcontractbench.py doctor
```

Expected result:

```text
PASS release surface validation
rows: 133
required_files: 133
public_safe_rows: 133
raw_data_rows: 0
```

This validates the manifest-controlled package: required files exist, paths are
release-root relative, all rows are marked public-safe, no raw data rows are
included, CSV/JSON files parse, and the claim-passport casebook joins to the
public dataset/scenario manifests.

## 3. Run The Smoke Suite

```bash
python3 src/claimcontractbench.py smoke
```

Expected result:

```text
PASS release smoke suite
positive_checks: 14
negative_fail_closed_checks: 5
```

The positive checks cover release validation, projection smoke rows, the LLM
packet happy path, template admission, the three-family real-paper demo, the
human trial path, the reviewer end-to-end workflow, the LLM trial-packet path,
the LLM adjudication scoring path, the one-shot agent guide, the reviewer
checklist, the human guide, the claim identification guide, and optional
feedback scaffolding. The negative checks
verify that unsafe or malformed LLM packets fail closed rather than producing a
licensed claim report. The smoke suite writes only temporary working files and
should leave a clean git checkout.

For a strict no-generated-files path, use:

```bash
python3 src/claimcontractbench.py doctor
python3 src/run_projection_smoke.py
python3 src/claimcontractbench.py templates
```

## 4. Try The Real-Paper Template Demo Directly

```bash
python3 src/claimcontractbench.py realpaper-demo \
  --output /tmp/claimcontractbench_realpaper_demo
```

Expected result:

```text
PASS real-paper review demo
rows: 72
source_papers: 18
conservative_candidate_safety_accuracy: 0.958
conservative_display_action_accuracy: 0.806
conservative_unsafe_false_releases: 3
```

This is the practical trial path for the current addendum. The `/tmp` output
keeps the checkout clean. It uses three V1.8-backed template families/domains
over supplied candidate claims from public papers. It does not perform
full-paper claim discovery or human review.

## 5. Inspect The Registered Templates

```bash
python3 src/claimcontractbench.py templates
```

This prints the current template catalog. It is deliberately small. For new
papers, most relevant empirical claims should become `NEEDS_TEMPLATE_ADMISSION`
unless they exactly match a registered template.

## 6. Optional: Try The Included LLM Packet

```bash
python3 src/claimcontractbench.py review \
  --input artifact/llm_claim_review_packet_template_20260527.csv \
  --output reports/llm_claim_review_packet_20260527
```

For a read-only-style local check, choose a temporary output directory instead:

```bash
python3 src/claimcontractbench.py review \
  --input artifact/llm_claim_review_packet_template_20260527.csv \
  --output /tmp/claimcontractbench_llm_claim_review_packet
```

Expected result:

```text
PASS LLM claim review packet
packet_rows: 4
call_registered_template: 2
needs_template_admission: 1
out_of_scope: 1
unsafe_release_rate: 0.000
rejected_unknown_template: 0
invalid_route_rows: 0
checks_passed: 14
checks_failed: 0
```

The LLM packet is a routing packet, not a paper review verdict. The deterministic
runner checks whether the supplied rows call a registered template, need a new
template, or should not call the claim runner at all.

## 7. Read The Evidence Map

Use `docs/REPORT_INDEX.md` to see which runner supports which paper-facing
claim. Use `docs/BOUNDARIES.md` before interpreting any result as a reviewer
utility claim, full-paper coverage claim, or autonomous-review claim.

If the terminology is unfamiliar, start with `docs/CONCEPTS.md`. If the artifact
boundary is what matters, start with `docs/REVIEWER_CHECKLIST.md`. If you want
the claim-review trial, read `docs/REAL_PAPER_REVIEW_DEMO.md`.
