# Public Release Checklist

Date: 2026-05-27
Updated: 2026-05-28
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
- Optional public-safe feedback scaffold with one-sentence LLM opt-in prompt
  and review-rule contact boundary.
- Mixed license scope: Apache-2.0 for code, CC-BY-4.0 for derived materials.
- GitHub Actions smoke workflow.
- Second-layer documentation under `docs/`.
- Reviewer verification checklist for first-pass artifact inspection.
- Plain-language concept guide for readers who are new to metric-to-claim
  contracts.
- Public contribution, support, security, issue, and pull-request templates.
- Current manifest validator result: 132 rows, 132 required files, 132
  public-safe rows, 0 raw-data rows.
- Current smoke result: 13 positive checks and 5 negative fail-closed checks.

## External Release Status To Verify

1. Final author metadata is confirmed locally: Yihui Guo, Wuhan University.
2. `CITATION.cff` contains the prepared release version and repository URL, but
   does not claim a public DOI before the Zenodo record resolves.
3. If a Zenodo draft is used, it should persist DOI, title, author, resource type, version,
   repository URL, Apache-2.0 and CC-BY-4.0 rights metadata, and the release
   Description.
4. The Zenodo draft should contain one uploaded archive file named
   `claimcontractbench-cikm2026.zip`; verify its checksum from the Zenodo
   record page for the exact published artifact.
5. If this file is being read from the final Zenodo record page, use Zenodo
   metadata as the authoritative publication status.
6. Verify the current guided-trial tag
   `v0.1.5-cikm2026-claim-identification-boundary` points to the intended audited
   snapshot commit. Older tags remain release-history checkpoints.
7. Create or verify a GitHub release from the tagged commit when ready.
8. Publish or verify the Zenodo record for the same snapshot if an archive DOI
   is used.
9. Rerun `python3 src/claimcontractbench.py doctor` and
   `python3 src/claimcontractbench.py smoke` on the exact archived snapshot.
10. Verify the repository URL, release-tag URL, and any DOI URL being cited
   from an unauthenticated browser.
11. Update the paper availability statement with URL, tag, DOI or DOI plan,
   access date, and validator output.

## Blinding / Track Boundary

This checklist assumes the CIKM Resource Papers track. CIKM 2026 Resource Paper
review is single-blind, and the Resource Paper instructions ask authors to
include names and affiliations in the paper. Under this track, the GitHub
repository may be named directly and should be public or otherwise
reviewer-accessible. If the work is moved to a double-blind Full Research or
Short Paper track, replace this public-owner repository route with an
anonymized review artifact route before submission.

## Do Not Claim Until Done

- final public DOI before the DOI resolves from an unauthenticated browser;
- final archival immutability;
- human reviewer utility;
- autonomous full-paper review;
- raw-data redistribution;
- full-paper claim coverage.
