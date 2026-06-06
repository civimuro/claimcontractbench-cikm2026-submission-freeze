# ClaimContractBench

ClaimContractBench helps people check whether a supplied empirical ML claim
packet is licensed by registered metric evidence, templates, and declared
context.

It is a research-resource snapshot, not a chatbot demo. You can inspect it with
plain Python commands, read the evidence tables directly, or optionally use an
LLM to draft a claim packet that the deterministic checker then audits.

## Reviewer End-To-End Path

If you are opening this repository for the first time as a reviewer, start with
one complete path instead of the full menu:

```bash
git clone https://github.com/civimuro/claimcontractbench-cikm2026-submission-freeze.git
cd claimcontractbench-cikm2026-submission-freeze
git checkout v0.1.6-cikm2026-reviewer-workflow
python3 src/claimcontractbench.py reviewer-flow
python3 src/claimcontractbench.py try-human
```

Then open:

```text
/tmp/claimcontractbench_human_trial/real_paper_review_demo_report.md
```

This gives a no-LLM, end-to-end reviewer trial over the current three supported
template families. It validates the release surface, runs the public-paper
template demo, and writes the result outside the checkout.

Read `docs/REVIEWER_END_TO_END.md` for the same workflow with interpretation
rules and optional LLM-assisted steps.

## Fastest Trial

For a no-LLM human/reviewer trial:

```bash
python3 src/claimcontractbench.py try-human
```

For an LLM-assisted trial packet with no gold/reference files:

```bash
python3 src/claimcontractbench.py try-llm
```

The current practical surface supports three V1.8-backed template families:
`llm_evaluation`, `resource_documentation`, and `uncertainty_calibration`.
Other domains should go through template admission instead of being forced into
a nearby template.

Important: the tool checks supplied candidate claims. It does not automatically
find every claim in a paper. For custom papers, a human or an LLM first
identifies candidate claims; see `docs/CLAIM_IDENTIFICATION.md`.

Start with `docs/REVIEWER_END_TO_END.md` if you want the clearest reviewer
workflow, `docs/START_HERE.md` if you want the shortest guided path, or
`docs/LLM_CONTEXT.md` if you are giving the repository to an AI assistant.

## Choose A Path

| I want to... | Start here | What you get |
| --- | --- | --- |
| Get a full reviewer workflow | `docs/REVIEWER_END_TO_END.md` or `python3 src/claimcontractbench.py reviewer-flow` | Clone/tag/run/read/interpret steps from GitHub to result. |
| Try it as a human reviewer | `python3 src/claimcontractbench.py try-human` | A no-LLM public-paper trial and report under `/tmp`. |
| Prepare a clean LLM trial | `python3 src/claimcontractbench.py try-llm` | A gold-free packet containing only candidate claims, template cards, prompt, and LLM context. |
| Understand claim selection | `docs/CLAIM_IDENTIFICATION.md` or `python3 src/claimcontractbench.py claim-id-guide` | How humans or LLMs identify candidate claims before the checker runs. |
| Learn the idea in five minutes | `docs/CONCEPTS.md` | A plain-language explanation of metric-to-claim contracts, `G/Q/U`, templates, and fail-closed routing. |
| Verify the resource as a reviewer | `docs/REVIEWER_CHECKLIST.md` or `python3 src/claimcontractbench.py reviewer-checklist` | A one-page verification map, then the public-safe release check and fail-closed smoke suite. |
| Understand the outputs as a human | `python3 src/claimcontractbench.py human-guide` | A guided map to the reports, examples, limits, and FAQ. |
| Try the real-paper template demo | `python3 src/claimcontractbench.py realpaper-demo --output /tmp/claimcontractbench_realpaper_demo` | A 72-row public-paper claim review demo over three V1.8-backed template families. |
| Try it with an LLM-assisted packet | `python3 src/claimcontractbench.py templates` then `python3 src/claimcontractbench.py init-packet --output claim_packets/my_claim_packet.csv` | A conservative route for drafting candidate claims, followed by deterministic checks. |
| Add a new claim family | `python3 src/claimcontractbench.py admission-guide` | A typed template-admission workflow instead of loose template reuse. |

## Ten-Minute Human Check

Start here if you are reviewing the artifact for the first time. The checklist
is the canonical human entry point:

```bash
python3 src/claimcontractbench.py reviewer-checklist
```

From the repository root:

```bash
python3 src/claimcontractbench.py doctor
python3 src/claimcontractbench.py smoke
```

Expected high-level result:

```text
PASS release surface validation
rows: 133
required_files: 133
public_safe_rows: 133
raw_data_rows: 0

PASS release smoke suite
positive_checks: 14
negative_fail_closed_checks: 5
```

The checklist shows what to inspect. The doctor command checks that the
repository is a manifest-controlled, public-safe release surface. The smoke
command runs positive examples and negative packets that must fail closed. It
uses temporary working directories and should leave a clean git checkout.

If you need a strict no-generated-files path, run:

```bash
python3 src/claimcontractbench.py doctor
python3 src/run_projection_smoke.py
python3 src/claimcontractbench.py templates
```

Then read by depth:

| Time budget | Read |
| --- | --- |
| First contact | `docs/START_HERE.md`, `docs/CLAIM_IDENTIFICATION.md`, `docs/SUPPORTED_TEMPLATE_FAMILIES.md` |
| 10 minutes | `docs/REVIEWER_CHECKLIST.md`, `docs/CONCEPTS.md`, `docs/BOUNDARIES.md` |
| 30 minutes | `docs/HUMAN_REVIEWER_GUIDE.md`, `docs/REPORT_INDEX.md`, `docs/EXAMPLE_OUTPUTS.md` |
| Deep check | `docs/DATA_AND_LICENSES.md`, `docs/REPRODUCIBILITY.md`, `docs/EVALUATION_SOURCE_INVENTORY.md`, `artifact/PUBLIC_RELEASE_CHECKLIST_20260527.md` |

## Try The Real-Paper Template Demo

The most direct claim-review trial, without writing generated files into the
checkout, is:

```bash
python3 src/claimcontractbench.py realpaper-demo \
  --output /tmp/claimcontractbench_realpaper_demo
```

This runs a public-safe addendum built from three V1.8-backed template
families/domains:
`llm_evaluation`, `resource_documentation`, and `uncertainty_calibration`. The
packet contains 72 supplied candidate claims from 18 public arXiv papers. It
does not read full PDFs, discover all claims, or measure human reviewer utility.

Expected high-level result:

```text
PASS real-paper review demo
rows: 72
source_papers: 18
conservative_candidate_safety_accuracy: 0.958
conservative_display_action_accuracy: 0.806
conservative_unsafe_false_releases: 3
```

Read `docs/REAL_PAPER_REVIEW_DEMO.md` for the full workflow, including how to
score an independent LLM adjudication against the supplied reference outcomes.

For a clean LLM packet, run:

```bash
python3 src/claimcontractbench.py try-llm
```

This copies only the candidate claims, template cards, LLM prompt, and LLM
context into `/tmp/claimcontractbench_llm_trial`.

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
- a claim-identification guide separating human-selected claims from
  LLM-assisted extraction and routing;
- selected paper-claim and excerpt benchmarks that measure fail-closed behavior
  rather than autonomous full-paper reading;
- tracked fulltext-adjacent claim-span readouts and a controlled adapter
  admission case study for the paper's boundary evidence tier;
- a public-safe real-paper template-review addendum with 18 public source
  papers, 72 supplied candidate claims, three V1.8-backed template families,
  and a replay/scoring runner;
- a no-LLM human trial command and a gold-free LLM trial-packet command;
- an advanced evaluation-source inventory that keeps public-paper simulation
  data separate from the ordinary user path;
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
- `docs/REAL_PAPER_REVIEW_DEMO.md`
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
  reviewer workflow, reviewer checklist, reproducibility, data/license posture,
  FAQ, and LLM-assisted path.
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
current guided-trial tag is
`v0.1.6-cikm2026-reviewer-workflow`. Earlier tags remain part of the release
history: `v0.1.0-cikm2026-submission` is the initial frozen submission
snapshot, `v0.1.1-cikm2026-real-paper-template-addendum` adds the first public
real-paper template addendum, `v0.1.2-cikm2026-real-paper-template-addendum`
records the read-only-style `/tmp` trial path, and
`v0.1.3-cikm2026-public-surface-audit` closes the public-surface manifest
audit; `v0.1.4-cikm2026-guided-trial-paths` adds guided human and LLM trial
paths; `v0.1.5-cikm2026-claim-identification-boundary` clarifies that humans
or LLMs identify candidate claims before checking. A Zenodo archive may be
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
