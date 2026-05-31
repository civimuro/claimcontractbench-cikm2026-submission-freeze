# Changelog

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
