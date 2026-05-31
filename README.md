# ClaimContractBench

ClaimContractBench helps people check whether a supplied empirical ML claim
packet is licensed by registered metric evidence, templates, and declared
context.

It is a research-resource snapshot, not a chatbot demo. You can inspect it with
plain Python commands, read the evidence tables directly, or optionally use an
LLM to draft a claim packet that the deterministic checker then audits.

## Choose A Path

| I want to... | Start here | What you get |
| --- | --- | --- |
| Learn the idea in five minutes | `docs/CONCEPTS.md` | A plain-language explanation of metric-to-claim contracts, `G/Q/U`, templates, and fail-closed routing. |
| Verify the resource as a reviewer | `python3 src/claimcontractbench.py reviewer-checklist` | A one-page verification map, then the public-safe release check and fail-closed smoke suite. |
| Understand the outputs as a human | `python3 src/claimcontractbench.py human-guide` | A guided map to the reports, examples, limits, and FAQ. |
| Try it with an LLM-assisted packet | `python3 src/claimcontractbench.py templates` then `python3 src/claimcontractbench.py init-packet --output claim_packets/my_claim_packet.csv` | A conservative route for drafting candidate claims, followed by deterministic checks. |
| Add a new claim family | `python3 src/claimcontractbench.py admission-guide` | A typed template-admission workflow instead of loose template reuse. |

## Ten-Minute Human Check

From the repository root:

```bash
python3 src/claimcontractbench.py reviewer-checklist
python3 src/claimcontractbench.py doctor
python3 src/claimcontractbench.py smoke
```

Expected high-level result:

```text
PASS release surface validation
rows: 109
required_files: 109
public_safe_rows: 109
raw_data_rows: 0

PASS release smoke suite
positive_checks: 8
negative_fail_closed_checks: 4
```

The checklist shows what to inspect. The doctor command checks that the
repository is a manifest-controlled, public-safe release surface. The smoke
command runs positive examples and negative packets that must fail closed.

Then read:

- `docs/REVIEWER_CHECKLIST.md`
- `docs/CONCEPTS.md`
- `docs/HUMAN_REVIEWER_GUIDE.md`
- `docs/EXAMPLE_OUTPUTS.md`
- `docs/REPORT_INDEX.md`
- `docs/BOUNDARIES.md`
- `docs/FAQ.md`

## What The Resource Does

ClaimContractBench asks one narrow question:

> Given a metric/evidence bundle and a declared context, which emitted empirical
> claim is licensed, weakened, rewritten, relabeled, suppressed, or kept
> support-only?

The release includes:

- public-safe release, source/license, dataset, and scenario manifests;
- a machine-readable claim-contract schema;
- five claim-passport smoke rows spanning emit, relabel, weaken, rewrite, and
  suppress actions;
- WDC/ACS/NAB-derived evidence tables;
- template-admission and reviewer-intake examples;
- selected paper-claim and excerpt benchmarks that measure fail-closed behavior
  rather than autonomous full-paper reading;
- tracked fulltext-adjacent claim-span readouts and a controlled adapter
  admission case study for the paper's boundary evidence tier;
- standard-library runners that regenerate reports without raw data downloads,
  third-party Python packages, network access, or GPU training.

## What It Is Not

ClaimContractBench is not an autonomous reviewer, paper-acceptance engine,
arbitrary fact checker, model leaderboard, official benchmark reproduction,
deployment-safety certificate, or raw-data redistribution bundle.

An LLM can help draft a packet, but it is never the authority. The deterministic
checker is the release boundary.

## Optional LLM-Assisted Path

The LLM path is intentionally separate from the human reviewer path.

```bash
python3 src/claimcontractbench.py templates
python3 src/claimcontractbench.py init-packet --output claim_packets/my_claim_packet.csv
```

Ask an LLM to fill the CSV using the registered template menu, then run:

```bash
python3 src/claimcontractbench.py review --input claim_packets/my_claim_packet.csv
```

For a known example:

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
rejected_unknown_template: 0
invalid_route_rows: 0
checks_passed: 14
checks_failed: 0
```

Use `CALL_REGISTERED_TEMPLATE` only for exact registered template matches. Use
`NEEDS_TEMPLATE_ADMISSION` for relevant empirical metric-to-claim statements
without a registered template. Use `OUT_OF_SCOPE_DO_NOT_CALL` for proof
correctness, novelty, implementation bugs, legal/policy decisions, ethics
approval, or acceptance judgments.

Detailed LLM guides:

- `docs/LLM_ASSISTED_PATH.md`
- `artifact/LLM_ASSISTED_REVIEW_QUICKSTART_20260527.md`
- `artifact/AGENT_ONE_SHOT_REVIEW_GUIDE_20260527.md`

## Public Project Entry Points

The repository is organized for two audiences:

- humans who want to understand or verify the resource directly;
- LLM-assisted users who want a conservative packet-drafting route.

For public discussion and contribution, use:

- `CONTRIBUTING.md`
- `SUPPORT.md`
- `SECURITY.md`
- `.github/ISSUE_TEMPLATE/`
- `.github/pull_request_template.md`

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

See `docs/TEMPLATE_ADMISSION.md`.

## Repository Map

- `docs/`: concepts, human-facing guides, boundaries, examples, report index,
  reviewer checklist, reproducibility, data/license posture, FAQ, and
  LLM-assisted path.
- `artifact/`: schemas, manifests, quickstarts, packet templates, and release
  checklist.
- `data/`: public-safe derived tables and compact evidence displays.
- `src/`: standard-library runners and the `claimcontractbench.py` command hub.
- `reports/`: tracked public-safe fixtures for report regeneration; most
  generated reports are ignored by git.
- `paper/`: public-safe release protocol notes and paper-facing figures.
- `LICENSES/`: Apache-2.0 and CC-BY-4.0 license texts.

## Release And Citation Status

This snapshot is prepared for a CIKM 2026 Resource Paper submission. The
submission tag is `v0.1.0-cikm2026-submission`. A Zenodo archive may be
added for the public submission snapshot, but this repository does not claim a
public DOI until the Zenodo record resolves. After publication, cite the tagged
GitHub release and the Zenodo archive together.

Current license scope:

- Apache-2.0 for executable code and scripts;
- CC-BY-4.0 for derived non-code resource materials;
- no redistribution grant for raw third-party datasets.

See:

- `LICENSE.md`
- `docs/DATA_AND_LICENSES.md`
- `artifact/PUBLIC_RELEASE_CHECKLIST_20260527.md`
