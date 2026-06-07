# Supported Template Families

The current product-like surface is deliberately narrow. It is strongest when
used on supplied candidate claims that fit one of three validated template
families. Other empirical-ML claims should go through template admission.

## Current Families

| Family | Template id | What it can inspect | Main forbidden upgrade |
| --- | --- | --- | --- |
| `llm_evaluation` | `TPL-LLM-EVAL-V18` | Benchmark-scoped or evaluation-scoped claims about tasks, protocols, model versions, metrics, model-as-judge limits, evaluation datasets, or measured evaluation surfaces. | Turning an evaluation result into deployment readiness, broad general intelligence, human replacement, or paper-acceptance authority. |
| `resource_documentation` | `TPL-RESOURCE-DOC-V18` | Claims about what a resource, software package, metadata record, schema, release, annotation workflow, identifier, or documentation artifact records or makes available. | Turning documentation into correctness, legal clearance, security, deployment readiness, scientific validity, or complete reproducibility. |
| `uncertainty_calibration` | `TPL-UNCERTAINTY-CAL-V18` | Claims about calibration, probabilistic prediction, uncertainty quantification, diagnostics, calibration metrics, uncertainty libraries, probabilistic programming, or conformal/calibration support. | Turning calibration or uncertainty evidence into deployment safety, scientific truth, proof correctness, or universal uncertainty coverage. |

## Evidence In This Release

The practical trial is:

```bash
python3 src/claimcontractbench.py realpaper-demo \
  --output /tmp/claimcontractbench_realpaper_demo
```

It uses:

- 18 public arXiv papers;
- 72 supplied candidate claims;
- 3 template families;
- 6 papers and 24 candidate rows per family.

Expected aggregate signal:

```text
conservative_candidate_safety_accuracy: 0.958
conservative_display_action_accuracy: 0.806
conservative_unsafe_false_releases: 3
```

This result is useful, but not perfect. The residual unsafe releases are
disclosed and should be treated as a boundary, especially for
`uncertainty_calibration` background/support-only cases.

The `V18` suffix in template IDs is retained for provenance; users should read
the families by their domains and boundaries, not by the internal version
number.

## Template Mechanism

Each registered family supplies:

- a licensed object;
- `G/Q/U` bindings;
- a typed preorder;
- allowed actions;
- forbidden stronger claims;
- a boundary note.

The deterministic runner uses those fields to decide whether a supplied claim
can be accepted, weakened, blocked with a suggested repair, marked support-only,
suppressed, or rejected/out-of-scope.

## Expansion Rule

Do not use a nearby template just because a claim feels similar. For new
families, create a typed admission row:

```bash
python3 src/claimcontractbench.py init-template \
  --output claim_packets/my_template_admission.csv
python3 src/claimcontractbench.py admit-template \
  --input claim_packets/my_template_admission.csv
```

New families must supply evidence units, claim templates, `G/Q/U`, action
mapping, preorder or incomparability relation, forbidden claims, anchors, and
boundary notes before they should be treated as supported.
