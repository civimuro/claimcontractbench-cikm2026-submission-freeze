# ClaimContractBench

This release contains the public-safe ClaimContractBench resource surface for a
CIKM 2026 Resource Paper submission.

Working title:

**ClaimContractBench: A Finite Claim-Licensing Resource for Metric-to-Claim Reporting**

## Reviewer First Step

The release is designed so that a reviewer can start without raw data, GPUs, or
third-party Python packages. From the release root:

```bash
python3 src/validate_release_surface.py
python3 src/run_projection_smoke.py
```

For the fuller reviewer path, follow:

- `artifact/REVIEWER_QUICKSTART_RELEASE_DRAFT_20260520.md`
- `artifact/LLM_ASSISTED_REVIEW_QUICKSTART_20260527.md`

The surface validator should report 65 required files, 65 public-safe rows, and
0 raw-data rows. The projection smoke runner should regenerate five public
claim-passport rows covering emit, relabel, rewrite, suppress, and weaken.

## Use With An LLM In Five Minutes

ClaimContractBench is easiest to try as an LLM-assisted workflow: let an LLM
extract and route candidate claims, then let the deterministic release scripts
accept, rewrite, suppress, or fail closed.

```bash
python3 src/run_llm_claim_review_packet.py \
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

For a new paper, copy the prompt in
`artifact/LLM_ASSISTED_REVIEW_QUICKSTART_20260527.md`, ask your LLM to output
the required CSV packet, and rerun the command with that CSV as `--input`.
The LLM is only the claim-extraction front end; ClaimContractBench remains the
fail-closed claim-governance layer.

For new-paper text, most rows should usually become `NEEDS_TEMPLATE_ADMISSION`
or `OUT_OF_SCOPE_DO_NOT_CALL` unless they exactly match a registered control or
template. Unknown templates, malformed CSV, private local paths, duplicate
packet ids, and missing human-check flags are treated as packet failures rather
than silently accepted rows.

This archive is a manifest-controlled derived-asset release. Running the
quickstart creates reviewer reports under `reports/`; those reports are
generated inspection outputs, not raw-data reproductions and not a claim that
raw third-party datasets are redistributed.

License scope is defined in `LICENSE.md`: executable code is Apache-2.0,
derived non-code resource materials are CC-BY-4.0, and raw third-party data is
not redistributed.

## What The Resource Is

ClaimContractBench is an executable claim-licensing audit resource. It helps a
reviewer, benchmark maintainer, or resource builder ask:

> Given a metric/evidence bundle and a declared context, which emitted
> empirical claim is actually licensed?

The resource includes manifests, claim schemas, reportability policies,
projection actions, validation scripts, source/provenance notes, and compact
derived evidence tables.

## What The Paper Is Not

It is not a generic calibration benchmark, a model leaderboard, an official WDC
reproduction, a deployment-safety validation, a raw-data redistribution bundle,
an arbitrary free-form claim verifier, or an autonomous full-paper reviewer.

## Folder Map

- `paper/`: CIKM paper outlines and manuscript drafts
- `artifact/`: resource specification and release checklist
- `data/`: dataset inventory, split metadata, and external-data notes
- `src/`: code for resource tooling
- `experiments/`: validation runs and compact benchmark evidence
- `reports/`: generated reports, plots, and screenshots
- `notes/`: working notes and decision log
- `admin/`: venue facts, policies, and source/license notes

## Immediate Milestone

Submit a CIKM Resource package whose paper and public snapshot agree on:

1. ClaimContractBench as the resource object;
2. the finite operator and `G/Q/U` schema as executable design;
3. action certificates and validators as resource behavior;
4. compact WDC and claim-benchmark evidence;
5. honest availability, license, and limitation boundaries.
