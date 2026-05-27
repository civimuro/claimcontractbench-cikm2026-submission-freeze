# Contributing

ClaimContractBench is a public-safe research resource. Contributions are
welcome when they improve transparency, reproducibility, documentation, or
typed claim-template coverage without adding confidential material.

## Good Contribution Types

- documentation fixes that make the human path easier to follow;
- reproducibility reports for `doctor`, `smoke`, or a named runner;
- template-admission proposals for new metric-to-claim families;
- small code fixes that keep the standard-library command path working;
- report or manifest fixes that make public-safe files easier to verify;
- issue templates, examples, or terminology improvements for new readers.

## Material That Does Not Belong Here

Do not submit:

- confidential paper text, private peer-review notes, or author identities;
- raw third-party datasets or files whose redistribution rights are unclear;
- local absolute paths, credentials, private tokens, or institution-only links;
- claims that the tool replaces peer review or certifies scientific correctness;
- broad template reuse when a new typed admission row is needed.

## Template-Admission Contributions

If you propose a new claim family, open a template-admission issue or PR with:

- evidence unit;
- safe claim template;
- `G/Q/U` bindings;
- action mapping;
- preorder or incomparability relation;
- forbidden stronger claim;
- visual, table, or case anchor;
- boundary note.

If those fields cannot be supplied, keep the proposal as a boundary probe or
documentation question.

## Before Opening A Pull Request

Run these from the repository root:

```bash
python3 src/claimcontractbench.py doctor
python3 src/claimcontractbench.py smoke
```

If you changed a runner, also run the relevant command listed in
`docs/REPORT_INDEX.md`.

## Pull Request Checklist

- The change is public-safe.
- The manifest is updated when the release surface changes.
- No raw data or confidential review text is included.
- `doctor` and `smoke` pass, or the PR explains why they could not be run.
- Documentation is updated for any new user-facing command, output, or file.
- New templates use the typed admission path rather than loose analogy.
