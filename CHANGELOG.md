# Changelog

## v0.1.7-cikm2026-reviewer-closure - GitHub Release And Template Entry Closure

- Promoted the current three V1.8-backed supported template families in the
  `templates` command before older admission-case examples, so first-time
  reviewers see the practical demo surface first.
- Aligned README, reviewer workflow, citation metadata, and release checklist
  with the current guided-trial tag.
- Kept `v0.1.0-cikm2026-submission` as the initial frozen submission snapshot
  while using this tag for the latest reviewer-facing GitHub workflow.

## v0.1.6-cikm2026-reviewer-workflow - Reviewer End-To-End Path

- Added `docs/REVIEWER_END_TO_END.md` as the first complete reviewer path
  from GitHub checkout to generated report and safe interpretation.
- Added a CLI `reviewer-flow` command that prints the clone, tag, trial,
  verification, interpretation, and human/LLM role split.
- Promoted the reviewer workflow in README, quickstart, checklist, and human
  reviewer guide so a first-time reviewer does not have to infer the path from
  a command menu.
- Expanded smoke coverage so the reviewer workflow entry point is checked
  alongside the existing human trial, LLM trial packet, claim-identification
  guide, and fail-closed packet checks.

## v0.1.5-cikm2026-claim-identification-boundary - Claim Selection Boundary

- Added an explicit claim-identification guide: ClaimContractBench checks
  supplied candidate claims and does not automatically find every claim in a
  paper.
- Clarified the human path: humans manually select candidate empirical claims,
  fill or inspect a packet, and run the deterministic checker.
- Clarified the LLM path: an LLM may help extract and route candidate claims
  from allowed text, but the deterministic checker remains the licensing
  boundary and no full-paper recall claim is made.
- Added a CLI `claim-id-guide` command and smoke coverage for this boundary.

## v0.1.4-cikm2026-guided-trial-paths - Human And LLM Trial UX

- Added a first-contact guide, LLM context file, and supported-template-family
  guide so human reviewers and AI assistants can understand the resource
  surface without reading the whole repository first.
- Added `try-human` for a no-LLM public-paper trial and `try-llm` for a
  gold-free LLM packet containing only candidate claims, template cards, prompt,
  and LLM context.
- Promoted the current practical capability statement: three V1.8-backed
  families (`llm_evaluation`, `resource_documentation`, and
  `uncertainty_calibration`) are supported for supplied candidate claims; other
  domains require template admission.
- Expanded the smoke suite so both no-threshold trial paths are checked in
  addition to the existing release and fail-closed checks.

## v0.1.3-cikm2026-public-surface-audit - Public-Surface Closure

- Closed the manifest surface after the real-paper template addendum: all 128
  tracked public-safe release files are now represented in the release
  manifest, including the tracked template-admission report fixtures.
- Synchronized public-facing validator and smoke-suite numbers across README,
  reviewer quickstarts, report index, resource specification, and paper-facing
  resource appendix.
- Kept the package boundary explicit: no credentials, private coordination
  files, raw third-party datasets, full paper PDFs, automatic full-paper review
  claim, human-utility claim, or zero-risk claim release is part of this
  snapshot.
- Refreshed citation metadata and checklist language for the current audited
  public-surface tag.

## v0.1.2-cikm2026-real-paper-template-addendum - Trial-Path UX Check

- Updated the human/reviewer quick trial path to prefer `/tmp` output, so
  first-time users can run the real-paper demo without writing generated files
  into their checkout.
- Kept the tracked generated report available for evidence inspection while
  making the read-only-style command the visible first-use route.

## v0.1.1-cikm2026-real-paper-template-addendum - Public Template Trial Addendum

- Added a real-paper template review demo over 18 public arXiv papers and 72
  supplied candidate claims across three V1.8-backed families:
  LLM evaluation, resource documentation, and uncertainty calibration.
- Added public-safe template cards, source manifest, candidate packet,
  reference outcomes, conservative replay summary, clean LLM prompt, and a
  reproducible demo runner.
- Added `python3 src/claimcontractbench.py realpaper-demo` as a reviewer-facing
  path that generates a readable report and can optionally score an LLM/user
  adjudication CSV.
- Updated the release smoke suite, quickstarts, report index, reviewer
  checklist, LLM-assisted path, and evaluation-source inventory so the new
  addendum is discoverable without changing the core non-goals.
- Kept the boundary explicit: this addendum demonstrates registered-template
  behavior on supplied real-paper candidate claims; it does not claim automatic
  full-paper extraction, broad coverage, zero-risk release, or human-utility
  improvement.

## v0.1.0-cikm2026-submission - CIKM 2026 Resource Submission Snapshot

- Reframed the repository as a reviewer-verifiable resource snapshot while
  preserving the LLM-assisted quick trial.
- Promoted the non-LLM human reviewer path to a first-class entry point through
  README path selection and `python3 src/claimcontractbench.py human-guide`.
- Added second-layer documentation under `docs/`:
  - plain-language concepts guide;
  - reviewer verification checklist;
  - human reviewer guide;
  - example output explanations;
  - FAQ;
  - optional LLM-assisted path;
  - reviewer quickstart;
  - scope boundaries;
  - report/evidence index;
  - template admission;
  - reproducibility;
  - data and license posture.
- Added a public release checklist for tag/archive/DOI readiness.
- Added public-facing community files: contributing guide, code of conduct,
  support and security notes, issue templates, and pull-request template.
- Kept the command hub and smoke suite as the primary first-inspection path.

## Initial Release Surface Assembly

- Created a manifest-controlled public-safe release surface.
- Added the command hub, LLM packet runner, template-admission path, one-shot
  agent guide, optional feedback scaffold, and GitHub Actions smoke workflow.
