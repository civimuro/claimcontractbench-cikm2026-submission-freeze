# Environment Note For First Inspection

Status: `PUBLIC_SAFE_RELEASE_ENVIRONMENT_NOTE`.

This note describes the environment needed to inspect the ClaimContractBench
release candidate. It is intentionally narrow: the first inspection path checks
the manifest-controlled release surface and regenerates derived reports. It
does not download raw datasets, install machine-learning packages, rerun model
training, or require a GPU.

## Required Runtime

- Python 3.9 or newer.
- Python standard library only for the documented first-inspection commands.
- A normal POSIX-like shell is convenient for copying commands, but the Python
  scripts themselves are standard-library scripts.

No `pip install` step is required for the reviewer quickstart.

## First-Inspection Resource Checks

The reviewer-facing commands are listed in
`artifact/REVIEWER_QUICKSTART_RELEASE_DRAFT_20260520.md`. They validate:

- manifest paths are release-root relative;
- required files exist;
- every release row is marked public-safe;
- no manifest row is marked raw data;
- CSV and JSON files parse structurally;
- claim-passport rows match the public schema;
- dataset and scenario ids join to public manifests;
- projection smoke rows regenerate the five public action-family examples;
- generated reviewer reports remain derived inspection outputs.

## Non-Requirements

The first-inspection path does not require:

- raw ACS, Bank, WDC, Walmart-Amazon, NAB, or AI4I datasets;
- cloud credentials;
- external network access for the quickstart commands;
- GPU training;
- third-party Python packages;
- TeX or PDF-building tools.

## Boundary

Passing the first-inspection environment checks means that the release surface
is runnable and internally consistent as a manifest-controlled derived-asset
package. It does not prove human reviewer utility, deployment safety, arbitrary
natural-language claim verification, or public availability of a final archive.
