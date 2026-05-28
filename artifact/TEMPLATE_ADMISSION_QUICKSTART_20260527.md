# Template Admission Quickstart

Date: 2026-05-27
Status: `PUBLIC_SAFE_TEMPLATE_ADMISSION_GUIDE`

Use this guide when `claimcontractbench.py review` returns
`NEEDS_TEMPLATE_ADMISSION`. That result means the claim is relevant to
metric-to-claim governance, but the current release has no registered template
that can safely license or rewrite it.

## Short Version

Do not force the claim into a near-looking template. Create a candidate template
row and run admission:

```bash
python3 src/claimcontractbench.py init-template \
  --output claim_packets/my_template_admission.csv
python3 src/claimcontractbench.py admit-template \
  --input claim_packets/my_template_admission.csv \
  --output reports/my_template_admission
```

The row is admitted only if it supplies the typed contract needed by the
resource. Interesting domains, popular benchmarks, and plausible prose are not
enough.

## What The LLM Must Draft

Ask the LLM for one CSV row with this exact header:

```csv
template_id,domain_id,domain_family,template_role,evidence_unit,claim_template,G_binding,Q_binding,U_binding,action_mapping,preorder_relation,forbidden_claim,visual_or_case_anchor,expected_level,expected_verdict,boundary_note
```

The key fields are:

| Field | What It Must Say |
| --- | --- |
| `evidence_unit` | The auditable evidence object, such as a slice certificate, confidence interval, decision-region certificate, or stream/profile trace. |
| `claim_template` | The finite claim sentence family the tool may emit or rewrite toward. |
| `G_binding` | The information/comparison boundary: same-regime, upper-bound-only, declared profile, declared slice, etc. |
| `Q_binding` | The reportability rule: when this evidence is reportable, weakly reportable, support-only, or not reportable. |
| `U_binding` | The use context: no deployment claim, decision-local use, false-alarm-sensitive use, support-only context, etc. |
| `action_mapping` | One of `emit_as_written`, `relabel_as_upper_bound`, `weaken_to_diagnostic`, `rewrite_to_decision_local`, `suppress_fallback`, or `none`. |
| `preorder_relation` | What claim is weaker/stronger, or which claims are incomparable without a declared utility. |
| `forbidden_claim` | The stronger sentence the template must block. |
| `visual_or_case_anchor` | A casebook row or visual passport row anchoring the template. Leave blank only for a boundary probe. |
| `boundary_note` | A plain-language ceiling that says what the template does not license. |

## Copy-Paste Prompt For The User's LLM

```text
You are drafting a ClaimContractBench template-admission row.

Do not decide that the paper's claim is true. Do not invent evidence. Your job
is to turn a NEEDS_TEMPLATE_ADMISSION row into a candidate typed template that a
deterministic admission checker can accept, keep as a boundary probe, or reject.

Output only CSV with this exact header:
template_id,domain_id,domain_family,template_role,evidence_unit,claim_template,G_binding,Q_binding,U_binding,action_mapping,preorder_relation,forbidden_claim,visual_or_case_anchor,expected_level,expected_verdict,boundary_note

Rules:
- Use one candidate template per row.
- Fill evidence_unit, claim_template, G_binding, Q_binding, U_binding,
  action_mapping, preorder_relation, forbidden_claim, and boundary_note.
- Use visual_or_case_anchor only when there is an auditable casebook or visual
  passport row. If no anchor exists, leave it blank and mark the row as a
  boundary probe.
- Do not claim broad deployment, SOTA, legal, novelty, or proof validity.
- If the template is incomplete, set expected_level=L1_BOUNDARY_PROBE and
  expected_verdict=KEEP_BOUNDARY_PROBE.
- If the template is missing most typed fields, set expected_level=L0_REJECTED
  and expected_verdict=REJECT_PATCHWORK.
```

## How To Interpret Admission Results

- `ADMIT_MAINLINE_TEMPLATE`: the template is complete enough for the main
  resource path.
- `ADMIT_SUPPORT_ONLY_TEMPLATE`: the template can support context or boundary
  evidence, but should not become the paper's headline claim.
- `KEEP_BOUNDARY_PROBE`: the idea is useful, but missing at least one required
  contract field or anchor.
- `REJECT_PATCHWORK`: the row is mostly a topic label or benchmark idea, not a
  typed claim-governance template.

## Boundary

Template admission is still not automatic science. The checker verifies that a
typed contract exists. A human must still decide whether the evidence unit and
anchor are real, whether the template belongs in the paper, and whether adding
the new domain would improve the resource rather than making it sprawl.
