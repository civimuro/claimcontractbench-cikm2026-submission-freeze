# ClaimContractBench Resource Specification

## Artifact MVP

The first CIKM-facing release should include:

- public-safe dataset manifest;
- split/scenario manifest examples;
- claim-contract schema;
- claim-template admission schema and cases;
- reviewer claim-intake schema and examples;
- application motivation cases;
- claim-audit gold-probe schema and cases;
- paper-claim gold benchmark schema, annotation protocol, sources, and cases;
- reportability-policy examples;
- projection/action-certificate examples and derived projection tables;
- validation scripts;
- reviewer-facing claim audit report generator;
- claim-template admission report generator;
- reviewer claim-intake decision generator;
- claim-audit gold-probe runner;
- paper-claim gold benchmark runner;
- compact derived evidence tables;
- source/provenance and license posture table;
- environment note;
- reviewer quickstart;
- one-shot AI-agent handoff guide;
- release or reviewer-accessible archive plan.

Raw datasets are excluded by default unless source terms clearly permit
redistribution with attribution. The initial artifact should release code,
manifests, derived outputs, validation tables, and source-provider instructions.

## Dataset Manifest Fields

For each dataset or benchmark family:

- resource dataset id;
- display name;
- task family;
- source/provider URL;
- license or terms URL;
- raw redistribution posture;
- derived-output posture;
- provenance caveat;
- resource role.

Current public-safe rows come from ACS/Folktables, UCI Bank Marketing, WDC
Products, Walmart-Amazon/DeepMatcher-style EM shakedown, and a support-only
NAB adapter-admission row. AI4I remains a future-expansion candidate only.

## Split And Scenario Metadata

Each scenario should specify:

- dataset id;
- scenario id;
- seed;
- model/scoring source;
- shift axis;
- train/calibration/evaluation sizes;
- source and target priors where applicable;
- source evidence file or public artifact id.

## Claim-Contract Schema

Each auditable event should include:

- event id;
- dataset and scenario ids;
- model or scorer and seed or profile;
- claim layer: scalar, score-region, slice, decision-region, or slice-decision;
- information-boundary, reportability, and decision-use primitives;
- preorder relation;
- tempting, licensed, and forbidden sentences;
- projection action;
- source anchor and boundary note.

The public release schema is the 16-field schema in
`artifact/claim_contract_schema_20260520.json`. Older 17-field work-use
operator traces remain internal theory/audit assets until they are normalized
to the release root.

## Projection Actions

The current action grammar is:

1. emit as written;
2. relabel as upper bound or reference;
3. weaken to diagnostic;
4. rewrite to decision-local claim;
5. suppress to `bottom_T`.

These actions license emitted claims over evidence traces. They do not replace
official metrics, scorers, or benchmark definitions.

## Reviewer Quickstart Target

The first reviewer quickstart validates the release surface and regenerates the
five public claim-passport smoke rows with Python 3.9+ standard-library scripts:

```bash
python3 src/validate_release_surface.py
python3 src/run_projection_smoke.py
python3 src/run_claim_audit_report.py --output reports/claim_audit_report_20260521
python3 src/run_claim_template_admission.py --output reports/claim_template_admission_20260521
python3 src/run_reviewer_claim_intake.py --output reports/reviewer_claim_intake_20260521
python3 src/run_claim_audit_gold_probe.py --output reports/claim_audit_gold_probe_20260521
python3 src/run_paper_claim_gold_benchmark.py --output reports/paper_claim_gold_benchmark_20260521
python3 src/run_paper_excerpt_reviewer_value_benchmark.py --output reports/paper_excerpt_reviewer_value_benchmark_20260521
python3 src/run_paper_claim_annotation_agreement.py --output reports/paper_claim_annotation_agreement_20260521
```

Current release-candidate status: the validator passes from the release root against
`artifact/release_manifest_20260520.csv`, with 82 required public-safe rows and
0 raw-data rows. The manifest includes `LICENSE.md` plus the Apache-2.0 and
CC-BY-4.0 license texts. The validator scans required release files for private
coordination paths, local machine paths, and credential-like patterns, and it
parses required CSV/JSON files for structural validity. It additionally checks
that the claim passport casebook header matches the public schema, that
projection-action and claim-layer values respect the schema enums, and that
dataset/scenario ids join to the public manifests. The projection smoke runner
then regenerates the five public action-family casebook rows from
`artifact/projection_smoke_cases_20260521.csv` and checks exact alignment with
`data/claim_passport_casebook_20260519.csv`. The claim audit report runner then
generates Markdown, HTML, CSV, and JSON reports from the public claim passport,
G/Q/U intervention, Q-policy, NAB support-only adapter, and resource-boundary
assets, with 11 contribution-facing checks passing. These commands do not require
raw-data downloads, third-party ML packages, or GPU training for the initial
review path. The claim template admission runner additionally checks nine
public-safe template-admission cases, admitting five mainline templates and
three NAB support-only templates while rejecting one AI4I patchwork-expansion
probe; it passes 10 admission checks.
The reviewer claim-intake runner then applies registered templates to eight
author/reviewer submitted claim sentences and returns accept, rewrite, suppress,
support-only, and reject decisions with 9 checks passing.
The application motivation case table maps six external evaluation/documentation
families to the tool's intake and admission decisions without claiming to
replace those frameworks.
The claim-audit gold probe then separates 18 rows into 8 registered-template
calls, 6 adapter-needed rows, and 4 out-of-scope rows; it passes 7 checks and
records that autonomous full-paper routing is not currently supported.
The paper-claim gold benchmark then expands this into a 40-paper, 120 external
claim-row reliability surface plus 8 registered-template controls. It passes 15
checks with 128/128 current action matches, 1.000 registered-control
consistency, 0.000 false-accept rate, 0.000 false-release rate for unsupported
or out-of-scope rows, and 0.000 false-kill rate on supported registered
controls. The benchmark intentionally records 80/120 external rows as
unsupported-template and 40/120 as out of scope, so it measures the current
fail-closed boundary rather than claiming autonomous paper reading.
The paper-excerpt reviewer-value benchmark then adds 80 public-safe
source-anchored selected-excerpt units plus 8 registered controls across 40
source papers and 22 source families. In default human-gold-oracle mode it
passes 13 checks with 1.000 tool-decision accuracy, 0.000 unsafe-release rate,
and an explicit `autonomous_full_paper_review_supported: no` boundary. A
transparent `text_rules` baseline is also supported and records imperfect
front-end routing while preserving the unsafe-release guard.
The paper-claim annotation-agreement runner validates a randomized 128-row
blind annotation packet and annotation map. Its current status is
`PENDING_SECOND_ANNOTATOR`: 10 packet-readiness checks pass, but no human
agreement is claimed until an independent annotator fills the route/action
label fields.

## Release Checklist

- [x] Release-root-relative quickstart commands
- [x] Public-safe dataset manifest
- [x] Split/scenario manifest examples
- [x] Claim-contract schema in machine-readable form
- [x] Claim-template admission schema and cases
- [x] Reviewer claim-intake schema and examples
- [x] Application motivation cases
- [x] Claim-audit gold-probe schema and cases
- [x] Paper-claim gold benchmark schema, annotation protocol, blind annotation packet, annotation map, sources, and cases
- [x] Paper-excerpt reviewer-value schema and cases
- [x] Projection/action-certificate examples
- [x] Standard-library projection smoke runner
- [x] Standard-library claim audit report runner
- [x] Standard-library claim template admission runner
- [x] Standard-library reviewer claim-intake runner
- [x] Standard-library claim-audit gold-probe runner
- [x] Standard-library paper-claim gold benchmark runner
- [x] Standard-library paper-excerpt reviewer-value benchmark runner
- [x] Standard-library paper-claim annotation agreement runner
- [x] Derived evidence tables
- [x] Source/license/provenance table
- [x] Environment note
- [x] Public-safe release surface manifest
- [x] Standard-library release surface validator
- [ ] Reviewer-accessible repository or archive
- [ ] DOI or DOI plan
