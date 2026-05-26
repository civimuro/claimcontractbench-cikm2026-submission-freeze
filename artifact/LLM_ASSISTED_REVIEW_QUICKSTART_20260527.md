# LLM-Assisted Review Quickstart

Date: 2026-05-27  
Status: `PUBLIC_SAFE_LLM_FRONTEND_GUIDE`

This guide shows how to use ClaimContractBench with an LLM quickly, without
turning the LLM into the authority. The intended division of labor is:

- the LLM finds and normalizes candidate empirical claims;
- ClaimContractBench applies registered claim templates and fails closed when a
  claim is unsupported, out of scope, or needs template admission;
- a human reviewer or author reads the report and decides what to do.

The current release does not provide autonomous full-paper reviewing. It
provides a conservative LLM-assisted front end for registered or explicitly
routed metric-to-claim audits.

## Five-Minute Path

From the release root:

```bash
python3 src/validate_release_surface.py
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
```

Open the generated report:

```text
reports/llm_claim_review_packet_20260527/llm_claim_review_packet_report.md
```

## Use It On A New Paper

1. Give an LLM the prompt below and the paper text, abstract, or results
   section you are allowed to process.
2. Ask it to output only CSV rows with the exact header shown below.
3. Save the CSV as, for example, `my_claim_packet.csv`.
4. Run:

```bash
python3 src/run_llm_claim_review_packet.py \
  --input my_claim_packet.csv \
  --output reports/my_claim_packet
```

Do not ask the LLM to decide whether a claim is licensed. Ask it to route the
claim into one of three lanes.

## CSV Header

```csv
packet_id,source_title,source_section,submitted_claim,intended_use,route_label,template_id,evidence_pointer,llm_reason,human_check_required
```

Allowed `route_label` values:

- `CALL_REGISTERED_TEMPLATE`
- `NEEDS_TEMPLATE_ADMISSION`
- `OUT_OF_SCOPE_DO_NOT_CALL`

Use `CALL_REGISTERED_TEMPLATE` only when the claim clearly matches one of the
registered template ids below. Otherwise use `NEEDS_TEMPLATE_ADMISSION` or
`OUT_OF_SCOPE_DO_NOT_CALL`.

## Registered Template Shortlist

| Template | Use only for | Do not use for |
| --- | --- | --- |
| `CTA-CORE-01` | bounded ACS local slice support | all-slice reliability |
| `CTA-CORE-02` | WDC stronger-information upper-bound reference | same-regime model superiority |
| `CTA-CORE-03` | weak ACS local support that must be diagnostic | decisive local result claims |
| `CTA-CORE-04` | WDC decision-local winner rewrite | global metric winner transfer |
| `CTA-CORE-05` | unsupported WDC local slice suppression | calibrated hard-negative slice claims |
| `CTA-NAB-01` | support-only clean-stream no-alert claim | overall detector effectiveness |
| `CTA-NAB-02` | support-only no-alert suppression | broad anomaly validation |
| `CTA-NAB-03` | support-only false-alarm-sensitive diagnostic claim | unqualified detector effectiveness |
| `CTA-AI4I-01` | boundary probe that must be rejected | admitted predictive-maintenance claim |

If a paper is about model cards, datasheets, robustness, distribution shift,
selective prediction, LLM evaluation, legal safety, novelty, proof correctness,
or implementation bugs, the current release usually should not call a
registered template. Use `NEEDS_TEMPLATE_ADMISSION` for relevant empirical
metric-to-claim cases, and `OUT_OF_SCOPE_DO_NOT_CALL` for legal, novelty,
proof, policy, or implementation-correctness claims.

## Copy-Paste LLM Prompt

```text
You are a conservative claim-routing assistant for ClaimContractBench.

Task:
Read the supplied paper text and extract candidate empirical claims that connect
metric evidence, benchmark evidence, calibration evidence, robustness evidence,
or resource evidence to a prose conclusion.

Do not decide that a claim is scientifically valid. Do not invent evidence. Do
not broaden a claim beyond the supplied text. Your job is only to produce a CSV
packet that a deterministic fail-closed tool can inspect.

Allowed route_label values:
1. CALL_REGISTERED_TEMPLATE
   Use only when the claim clearly matches one registered template id from the
   list below.
2. NEEDS_TEMPLATE_ADMISSION
   Use when the claim is relevant to empirical metric-to-claim review but no
   registered template safely applies.
3. OUT_OF_SCOPE_DO_NOT_CALL
   Use for proof correctness, novelty, implementation bugs, legal compliance,
   policy decisions, ethics approval, or other non-metric judgments.

Registered template ids and ceilings:
- CTA-CORE-01: bounded ACS local slice support; not all-slice reliability.
- CTA-CORE-02: WDC upper-bound reference; not same-regime superiority.
- CTA-CORE-03: weak ACS local support; diagnostic only.
- CTA-CORE-04: WDC decision-local winner rewrite; not global-to-decision transfer.
- CTA-CORE-05: unsupported WDC local slice; suppress to bottom_T.
- CTA-NAB-01: support-only clean-stream no-alert; not detector effectiveness.
- CTA-NAB-02: support-only no-alert suppression; not broad anomaly validation.
- CTA-NAB-03: support-only false-alarm diagnostic; not unqualified effectiveness.
- CTA-AI4I-01: rejected boundary probe; not an admitted maintenance template.

Output only CSV with this exact header:
packet_id,source_title,source_section,submitted_claim,intended_use,route_label,template_id,evidence_pointer,llm_reason,human_check_required

Rules:
- Use short stable packet ids such as LLM-001.
- Quote or paraphrase one claim per row.
- Keep template_id blank unless route_label is CALL_REGISTERED_TEMPLATE.
- evidence_pointer should name the section, table, figure, or sentence span.
- human_check_required must be yes for every row unless the source text is a
  release-provided registered control.
- Prefer NEEDS_TEMPLATE_ADMISSION over CALL_REGISTERED_TEMPLATE when uncertain.
- Prefer OUT_OF_SCOPE_DO_NOT_CALL over NEEDS_TEMPLATE_ADMISSION for non-metric
  review tasks.
```

## How To Read The Tool Output

The runner returns one action per row:

- `ACCEPT_LICENSED`: the submitted claim already matches a registered licensed
  sentence.
- `REWRITE_TO_LICENSED`: the claim is too strong but has a registered weaker
  output.
- `SUPPRESS_BOTTOM`: the claim must not be emitted under the registered
  template.
- `SUPPORT_ONLY_REWRITE`: the evidence may support context or motivation, but
  not a headline claim.
- `REJECT_PATCHWORK`: the template handoff is incomplete or mismatched.
- `REJECT_UNKNOWN_TEMPLATE`: the LLM supplied a template id that is not
  registered.
- `NEEDS_TEMPLATE_ADMISSION`: the row may be relevant, but a new typed adapter
  is needed first.
- `OUT_OF_SCOPE_DO_NOT_CALL`: the row is outside the metric-to-claim tool.

For paper review, the most useful rows are often not the accepted ones. The
high-value rows are usually rewrites, suppressions, support-only boundaries,
and admission tickets, because those show where a paper's prose outruns its
evidence.

## Safety And Privacy

Only send paper text to an LLM if you are allowed to do so under the venue,
author, or institutional rules that apply to you. For confidential peer review,
use an approved private model or do not use the LLM front end. ClaimContractBench
can still run on manually prepared CSV packets without sending any text to an
external model.
