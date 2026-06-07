# Reproducibility

The first-inspection path is designed for a clean reviewer checkout.

## Requirements

- Python 3.9 or newer.
- Standard library only for documented first-inspection commands.
- No raw dataset download.
- No GPU training.
- No external network access after checkout.

## Main Commands

```bash
python3 src/claimcontractbench.py doctor
python3 src/claimcontractbench.py smoke
```

These commands validate the release root and run the release smoke suite.

For the paper-facing validation evidence, also run:

```bash
python3 src/claimcontractbench.py validation-ladder \
  --output /tmp/claimcontractbench_validation_ladder
```

This recomputes the staged validation summaries from public-safe files. It is
not part of the shortest ordinary user trial.

## What The Validator Checks

`doctor` runs `src/validate_release_surface.py`. It checks:

- release-root-relative manifest paths;
- required files exist;
- no manifest path points into private coordination directories;
- required files do not contain local user paths, private coordination markers,
  connector host markers, or inline credential assignments;
- every manifest row is public-safe;
- no manifest row is raw data;
- required CSV and JSON files parse structurally;
- claim-passport rows match the public schema;
- dataset and scenario ids join to public manifests;
- projection actions and claim layers stay inside schema enums.

## What The Smoke Suite Checks

`smoke` runs:

- release-surface validation;
- projection smoke regeneration;
- LLM packet happy path;
- template-admission boundary-probe example;
- validation-ladder recomputation;
- human reviewer guide availability;
- reviewer checklist availability;
- one-shot agent guide availability;
- optional feedback scaffold creation;
- fail-closed negative packets for unknown template id, illegal template id on a
  non-call row, duplicate packet id, and private-marker report suppression.

## What The Validation Ladder Checks

`validation-ladder` checks:

- 42-row template-rule stress over cross-model LLM-proxy blind outputs;
- 72-row positive public-paper use over the three admitted template families;
- 72-row boundary replay using the current real-paper demo reference outcomes;
- public-safety scanning for the ladder files.

It supports a bounded resource-validity claim over supplied candidate rows. It
does not establish autonomous full-paper review, automatic claim discovery,
human reviewer utility, or broad empirical-ML coverage.

## Generated Outputs

Most generated outputs are intentionally ignored by git:

- `reports/claim_audit_report_*`;
- `reports/claim_template_admission_*`;
- `reports/reviewer_claim_intake_*`;
- `reports/llm_claim_review_packet_*`;
- `claim_packets/`;
- `feedback/`.

Tracked `reports/` files are public-safe fixtures used by the demo runners, not
raw data.

## Versioning Expectation

Before final public citation, create a tag, GitHub release, archive snapshot,
and DOI if available. Rerun `doctor` and `smoke` on the exact archived snapshot.
