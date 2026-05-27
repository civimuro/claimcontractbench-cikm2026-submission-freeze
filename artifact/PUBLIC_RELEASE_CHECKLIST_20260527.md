# Public Release Checklist

Date: 2026-05-27
Status: `RELEASE_CANDIDATE_CHECKLIST`

This checklist records what remains before the repository can be cited as the
final public resource snapshot for the paper.

## Already Present

- Manifest-controlled public-safe release surface.
- Standard-library command hub: `src/claimcontractbench.py`.
- First-inspection checks: `doctor` and `smoke`.
- LLM-assisted packet trial.
- One-shot AI-agent handoff guide.
- Template-admission path.
- Optional consent-based feedback scaffold.
- Mixed license scope: Apache-2.0 for code, CC-BY-4.0 for derived materials.
- GitHub Actions smoke workflow.
- Second-layer documentation under `docs/`.
- Reviewer verification checklist for first-pass artifact inspection.
- Plain-language concept guide for readers who are new to metric-to-claim
  contracts.
- Public contribution, support, security, issue, and pull-request templates.

## Still Needed For Final Public Citation

1. Confirm final author metadata.
2. Create or update final citation metadata.
3. Create a version tag, for example `v0.1.0-cikm2026-resource-snapshot`.
4. Create a GitHub release from the tagged commit.
5. Archive the release on Zenodo or another stable archive if a DOI is needed.
6. Rerun `python3 src/claimcontractbench.py doctor` and
   `python3 src/claimcontractbench.py smoke` on the exact archived snapshot.
7. Update the paper availability statement with URL, tag, DOI or DOI plan,
   access date, and validator output.

## Do Not Claim Until Done

- final public DOI;
- final archival immutability;
- human reviewer utility;
- autonomous full-paper review;
- raw-data redistribution;
- full-paper claim coverage.
