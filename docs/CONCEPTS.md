# Concepts In Plain Language

ClaimContractBench is about one small but common failure mode in empirical ML
writing: a metric result is often true only inside a narrow context, but the
paper sentence can sound broader than the evidence allows.

The resource asks whether a claim sentence stays inside the boundary set by the
evidence, scenario, and intended use.

## The Basic Question

For each candidate claim, ask:

```text
Given this evidence bundle and context, what sentence is actually licensed?
```

The answer may be:

- keep the claim as written;
- relabel it as a comparison or upper-bound reference;
- weaken it to diagnostic support;
- rewrite it to a narrower decision-local statement;
- suppress it because the stronger sentence is not licensed;
- keep it as support-only background.

## A Small Example

| Evidence | Safe sentence | Too-strong sentence | Tool action |
| --- | --- | --- | --- |
| A method is best under one declared WDC scenario and policy. | The method is the same-scenario winner under the declared policy. | The method is the overall best entity matcher. | Rewrite or relabel. |
| A clean NAB stream has no thresholded alerts under one adapter. | The detector has no alerts on this clean stream. | The detector is effective on NAB overall. | Keep support-only. |
| A packet calls a template id that is not registered. | The claim needs template admission. | The claim is licensed by the nearest template. | Fail closed. |

The point is not to decide whether the paper is good. The point is to prevent a
narrow metric result from being silently reused as a broader prose claim.

## What `G/Q/U` Means

`G`, `Q`, and `U` are boundary fields.

- `G` records the evidence or comparison boundary.
- `Q` records the reportability policy.
- `U` records the intended decision-use context.

Together they make the claim sentence carry the same conditions as the metric
evidence. If any field changes, the licensed sentence may also change.

## Registered Templates

A registered template is a typed contract for one claim family. It names:

- the evidence unit;
- the safe claim template;
- the `G/Q/U` bindings;
- the action mapping;
- forbidden stronger claims;
- the anchor or case that makes the boundary checkable.

If a new paper has a relevant empirical claim but no exact registered template,
the safe route is `NEEDS_TEMPLATE_ADMISSION`, not a forced match to a nearby
template.

## Human And LLM Paths

Humans can inspect the resource with:

```bash
python3 src/claimcontractbench.py doctor
python3 src/claimcontractbench.py smoke
python3 src/claimcontractbench.py human-guide
```

An LLM can optionally help draft candidate rows, but the LLM is not the
authority. The deterministic runner decides whether a row calls a registered
template, needs admission, or is out of scope.

## What To Read Next

- `docs/QUICKSTART.md` for a ten-minute verification path.
- `docs/HUMAN_REVIEWER_GUIDE.md` for non-LLM inspection.
- `docs/EXAMPLE_OUTPUTS.md` for command output interpretation.
- `docs/BOUNDARIES.md` for what the resource must not be used to claim.
- `docs/TEMPLATE_ADMISSION.md` for adding a claim family.
