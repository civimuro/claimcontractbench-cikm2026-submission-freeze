# Data And Licenses

ClaimContractBench is a derived public-safe resource. It does not redistribute
raw third-party datasets.

## License Scope

- Code and executable scripts: Apache-2.0.
- Derived non-code resource materials: CC-BY-4.0.
- Raw third-party datasets: governed by their original providers, not by this
  repository.

See `LICENSE.md` and the full license texts in `LICENSES/`.

Short third-party source excerpts, source titles, URLs, and identifiers inside
public-safe audit rows are not relicensed by ClaimContractBench. They remain
governed by their original sources. See `docs/PUBLIC_EXCERPT_AND_LABEL_POLICY.md`.

## Raw Data Posture

The first-inspection path uses manifests, schemas, derived tables, and
public-safe reports. It does not require downloading ACS, WDC, Walmart-Amazon,
NAB, AI4I, or other raw data.

The dataset/source boundary is recorded in:

- `artifact/dataset_source_manifest_20260520.csv`
- `artifact/source_license_snapshot_20260520.csv`
- `artifact/split_scenario_manifest_examples_20260520.csv`

## Derived Materials

Derived release materials include:

- claim-passport rows;
- scenario summaries;
- WDC stability displays;
- template-admission cases;
- paper-claim benchmark rows;
- selected-excerpt reviewer-value rows;
- public-safe route and decision fixtures.

These files are intended to support inspection of the resource behavior without
bundling raw third-party records.

Some public-paper audit rows contain short public excerpts for source
traceability. These excerpts are minimized inspection anchors, not raw data
redistribution and not a ClaimContractBench-authored CC-BY grant over the
underlying third-party text.

## User Responsibility

Users who rerun experiments against raw third-party datasets must obtain the
data from the original providers and comply with the original terms. Passing
the ClaimContractBench release validator does not grant additional rights over
external data.
