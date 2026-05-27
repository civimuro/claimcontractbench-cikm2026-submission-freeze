# ClaimContractBench

ClaimContractBench is a manifest-controlled research resource for auditing the
step between metric evidence and prose claims in empirical ML papers.

Working title:

**ClaimContractBench: A Finite Claim-Licensing Resource for Metric-to-Claim Reporting**

The release is designed to serve two audiences without mixing their roles:

1. reviewers who need to verify that the resource is real, bounded, runnable,
   and internally consistent; and
2. authors or LLM users who want a quick, conservative way to try the
   claim-routing workflow on a paper excerpt.

The LLM path is a front end. The deterministic ClaimContractBench tools remain
the licensing boundary. This repository is not an autonomous reviewer,
paper-acceptance engine, arbitrary fact checker, model leaderboard, official
benchmark reproduction, or raw-data redistribution bundle.

## Ten-Minute Reviewer Path

From the release root:

```bash
python3 src/claimcontractbench.py doctor
python3 src/claimcontractbench.py smoke
```

Expected high-level result:

```text
PASS release surface validation
rows: 82
required_files: 82
public_safe_rows: 82
raw_data_rows: 0

PASS release smoke suite
positive_checks: 6
negative_fail_closed_checks: 4
```

`doctor` checks the manifest-controlled release surface. `smoke` checks the
positive public paths and four fail-closed packet failures: unknown template,
template id on a non-call row, duplicate packet id, and private-marker report
suppression.

For a guided explanation, read:

- `docs/QUICKSTART.md`
- `docs/REPRODUCIBILITY.md`
- `docs/REPORT_INDEX.md`
- `docs/BOUNDARIES.md`

## What This Resource Verifies

ClaimContractBench asks one narrow question:

> Given a metric/evidence bundle and a declared context, which emitted empirical
> claim is licensed, weakened, rewritten, relabeled, suppressed, or kept
> support-only?

The release contains:

- a public-safe release manifest;
- source/license and dataset/scenario manifests;
- a machine-readable claim-contract schema;
- five claim-passport smoke rows spanning emit, relabel, weaken, rewrite, and
  suppress actions;
- WDC/ACS/NAB-derived public-safe evidence tables;
- template-admission and reviewer-intake examples;
- selected paper-claim and excerpt benchmarks that measure fail-closed behavior
  rather than autonomous full-paper reading;
- standard-library runners that regenerate reports without raw data downloads,
  third-party Python packages, or GPU training.

## Quick LLM Trial

The repository still supports the original quick LLM-assisted trial. This path
is useful for fast exploration, but it should not be read as automatic paper
review.

```bash
python3 src/claimcontractbench.py templates
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
rejected_unknown_template: 0
invalid_route_rows: 0
checks_passed: 14
checks_failed: 0
```

For a new paper, create a packet and ask an LLM to fill only the CSV fields:

```bash
python3 src/claimcontractbench.py init-packet --output claim_packets/my_claim_packet.csv
```

Then run:

```bash
python3 src/claimcontractbench.py review --input claim_packets/my_claim_packet.csv
```

Use `CALL_REGISTERED_TEMPLATE` only for exact registered template matches. Use
`NEEDS_TEMPLATE_ADMISSION` for relevant empirical metric-to-claim statements
without a registered template. Use `OUT_OF_SCOPE_DO_NOT_CALL` for proof
correctness, novelty, implementation bugs, legal/policy decisions, ethics
approval, or acceptance judgments.

Details:

- `artifact/LLM_ASSISTED_REVIEW_QUICKSTART_20260527.md`
- `artifact/AGENT_ONE_SHOT_REVIEW_GUIDE_20260527.md`
- `docs/TEMPLATE_ADMISSION.md`

## Template Admission

If a relevant claim does not match a registered template, do not force a nearby
template. Start a typed admission row:

```bash
python3 src/claimcontractbench.py admission-guide
python3 src/claimcontractbench.py init-template --output claim_packets/my_template_admission.csv
python3 src/claimcontractbench.py admit-template --input claim_packets/my_template_admission.csv
```

A candidate template must supply an evidence unit, finite claim template,
`G/Q/U` bindings, action mapping, preorder or incomparability relation,
forbidden stronger claim, anchor, and boundary note.

## Repository Map

- `docs/`: reviewer-facing second-layer paper: quickstart, boundaries, report
  index, data/license posture, reproducibility, and template admission.
- `artifact/`: schemas, manifests, quickstarts, packet templates, and release
  checklist.
- `data/`: public-safe derived tables and compact evidence displays.
- `src/`: standard-library runners and the `claimcontractbench.py` command hub.
- `reports/`: tracked public-safe fixture inputs for report regeneration; most
  generated reports are ignored by git.
- `paper/`: public-safe release protocol notes and paper-facing figures.
- `LICENSES/`: Apache-2.0 and CC-BY-4.0 license texts.

## Release And Citation Status

This snapshot is prepared for a CIKM 2026 Resource Paper submission. If this
checkout has no release tag, GitHub release, or archive DOI, cite the paper and
the repository commit. The final public release should add a version tag,
release notes, archive DOI, and final citation metadata.

Current license scope:

- Apache-2.0 for executable code and scripts;
- CC-BY-4.0 for derived non-code resource materials;
- no redistribution grant for raw third-party datasets.

See:

- `LICENSE.md`
- `docs/DATA_AND_LICENSES.md`
- `artifact/PUBLIC_RELEASE_CHECKLIST_20260527.md`

## Immediate Milestone

The paper and public snapshot should agree on:

1. ClaimContractBench as the resource object;
2. the finite operator and `G/Q/U` schema as executable design;
3. action certificates and validators as resource behavior;
4. compact WDC and claim-benchmark evidence;
5. honest availability, license, and limitation boundaries.
