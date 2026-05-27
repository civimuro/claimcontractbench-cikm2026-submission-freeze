# Reviewer Quickstart

This is the reviewer-facing path for first inspection of ClaimContractBench.
It is intentionally short: no raw data download, no GPU, and no third-party
Python packages are required.

## 1. Check The Release Surface

From the repository root:

```bash
python3 src/claimcontractbench.py reviewer-checklist
python3 src/claimcontractbench.py doctor
```

Expected result:

```text
PASS release surface validation
rows: 96
required_files: 96
public_safe_rows: 96
raw_data_rows: 0
```

This validates the manifest-controlled package: required files exist, paths are
release-root relative, all rows are marked public-safe, no raw data rows are
included, CSV/JSON files parse, and the claim-passport casebook joins to the
public dataset/scenario manifests.

## 2. Run The Smoke Suite

```bash
python3 src/claimcontractbench.py smoke
```

Expected result:

```text
PASS release smoke suite
positive_checks: 8
negative_fail_closed_checks: 4
```

The positive checks cover release validation, projection smoke rows, the LLM
packet happy path, template admission, the one-shot agent guide, the reviewer
checklist, the human guide, and optional feedback scaffolding. The negative
checks verify that unsafe or malformed LLM packets fail closed rather than
producing a licensed claim report.

## 3. Inspect The Registered Templates

```bash
python3 src/claimcontractbench.py templates
```

This prints the current template catalog. It is deliberately small. For new
papers, most relevant empirical claims should become `NEEDS_TEMPLATE_ADMISSION`
unless they exactly match a registered template.

## 4. Try The Included LLM Packet

```bash
python3 src/claimcontractbench.py review \
  --input artifact/llm_claim_review_packet_template_20260527.csv \
  --output reports/llm_claim_review_packet_20260527
```

Expected result:

```text
PASS LLM claim review packet
packet_rows: 4
call_registered_template: 2
needs_template_admission: 1
out_of_scope: 1
unsafe_release_rate: 0.000
checks_passed: 14
checks_failed: 0
```

The LLM packet is a routing packet, not a paper review verdict. The deterministic
runner checks whether the supplied rows call a registered template, need a new
template, or should not call the claim runner at all.

## 5. Read The Evidence Map

Use `docs/REPORT_INDEX.md` to see which runner supports which paper-facing
claim. Use `docs/BOUNDARIES.md` before interpreting any result as a reviewer
utility claim, full-paper coverage claim, or autonomous-review claim.

If the terminology is unfamiliar, start with `docs/CONCEPTS.md`. If the artifact
boundary is what matters, start with `docs/REVIEWER_CHECKLIST.md`.
