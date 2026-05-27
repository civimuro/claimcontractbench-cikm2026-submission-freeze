# Template Admission

Use template admission when a paper claim is relevant to empirical
metric-to-claim governance but no registered template safely applies.

The key rule is simple:

> Do not force a new claim into a near-looking template.

## Command Path

```bash
python3 src/claimcontractbench.py admission-guide
python3 src/claimcontractbench.py init-template --output claim_packets/my_template_admission.csv
python3 src/claimcontractbench.py admit-template --input claim_packets/my_template_admission.csv
```

## Required Fields

A candidate template must supply:

- `evidence_unit`: the auditable evidence object;
- `claim_template`: the finite claim family;
- `G_binding`: information or comparison boundary;
- `Q_binding`: reportability policy;
- `U_binding`: use context;
- `action_mapping`: emit, relabel, weaken, rewrite, suppress, or none;
- `preorder_relation`: weaker/stronger relation or explicit incomparability;
- `forbidden_claim`: stronger sentence that must be blocked;
- `visual_or_case_anchor`: casebook or visual anchor, unless intentionally a
  boundary probe;
- `boundary_note`: plain-language ceiling.

## Admission Outcomes

- `ADMIT_MAINLINE_TEMPLATE`: complete enough for the main registered path.
- `ADMIT_SUPPORT_ONLY_TEMPLATE`: useful for context or boundary evidence, not a
  headline claim.
- `KEEP_BOUNDARY_PROBE`: relevant but incomplete.
- `REJECT_PATCHWORK`: topic label or benchmark idea without a typed contract.

## Current Catalog Shape

The current public catalog contains 9 admission rows:

- 5 mainline templates;
- 3 support-only templates;
- 1 rejected boundary probe.

The catalog is intentionally small. Breadth is handled through admission, not
through vague template reuse.

## LLM Use

An LLM may draft a candidate admission row. It must not decide that the template
is scientifically valid. The deterministic admission checker only verifies that
a typed contract exists; a human still decides whether the evidence and anchor
are real and whether the new domain belongs in the resource.

For a copy-paste drafting prompt, see
`artifact/TEMPLATE_ADMISSION_QUICKSTART_20260527.md`.
