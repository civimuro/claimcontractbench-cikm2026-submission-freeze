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

Shortest path:

```bash
python3 src/claimcontractbench.py doctor
python3 src/claimcontractbench.py agent-guide
python3 src/claimcontractbench.py init-packet --output claim_packets/my_claim_packet.csv
# ask an LLM to fill claim_packets/my_claim_packet.csv as plain CSV
python3 src/claimcontractbench.py review --input claim_packets/my_claim_packet.csv
```

If an AI coding assistant or LLM agent has local file and command access, the
user-facing one-sentence handoff is:

```text
Use the tools in this repository to assist a review of this paper.
```

The agent should follow `artifact/AGENT_ONE_SHOT_REVIEW_GUIDE_20260527.md`.
Without local command access, an LLM can draft the CSV packet but cannot run the
deterministic checks.

If the report says `NEEDS_TEMPLATE_ADMISSION`, switch to:

```bash
python3 src/claimcontractbench.py admission-guide
```

## Five-Minute Path

From the release root:

```bash
python3 src/claimcontractbench.py doctor
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

Open the generated report:

```text
reports/llm_claim_review_packet_20260527/llm_claim_review_packet_report.md
```

To test the happy path plus several bad packets that must fail closed:

```bash
python3 src/claimcontractbench.py smoke
```

## Use It On A New Paper

1. Give an LLM the prompt below and the paper text, abstract, or results
   section you are allowed to process.
2. Ask it to output only CSV rows with the exact header shown below.
3. Create a packet file:

```bash
python3 src/claimcontractbench.py init-packet --output claim_packets/my_claim_packet.csv
```

4. Replace the header-only file with the LLM's plain CSV output.
5. Run:

```bash
python3 src/claimcontractbench.py review \
  --input claim_packets/my_claim_packet.csv \
  --output reports/my_claim_packet
```

Do not ask the LLM to decide whether a claim is licensed. Ask it to route the
claim into one of three lanes.

## CSV Header

```csv
packet_id,source_title,source_section,submitted_claim,intended_use,route_label,template_id,evidence_pointer,llm_reason,human_check_required
```

CSV packet rules:

- use this exact header, in this exact order, with no extra columns;
- quote fields that contain commas, quotation marks, or line breaks;
- do not wrap the CSV in Markdown code fences when saving it to a file;
- use one claim per row;
- keep `packet_id` unique;
- set `human_check_required` to `yes` for every non-control row;
- for a new user-supplied paper, set `human_check_required` to `yes` for every
  row, including registered-template calls;
- keep `template_id` blank unless `route_label` is
  `CALL_REGISTERED_TEMPLATE`.

Allowed `route_label` values:

- `CALL_REGISTERED_TEMPLATE`
- `NEEDS_TEMPLATE_ADMISSION`
- `OUT_OF_SCOPE_DO_NOT_CALL`

Use `CALL_REGISTERED_TEMPLATE` only when the claim clearly matches one of the
registered template ids below. Otherwise use `NEEDS_TEMPLATE_ADMISSION` or
`OUT_OF_SCOPE_DO_NOT_CALL`.

If a row names an unknown template id, the row is reported as
`REJECT_UNKNOWN_TEMPLATE` and the whole packet fails check `LCP-07`. This is
intentional: an unknown id is not a safe adapter.

## Registered Template Shortlist

| Template | Use only for | Do not use for |
| --- | --- | --- |
| `CTA-CORE-01` | bounded ACS local slice support, as in `CP-01` | all-slice reliability |
| `CTA-CORE-02` | WDC stronger-information upper-bound reference, as in `CP-02` | same-regime model superiority |
| `CTA-CORE-03` | weak ACS local support that must be diagnostic, as in `CP-03` | decisive local result claims |
| `CTA-CORE-04` | WDC decision-local winner rewrite, as in `CP-04` | global metric winner transfer |
| `CTA-CORE-05` | unsupported WDC local slice suppression, as in `CP-05` | calibrated hard-negative slice claims |
| `CTA-NAB-01` | support-only clean-stream no-alert claim, as in `NAB-VIS-01` | overall detector effectiveness |
| `CTA-NAB-02` | support-only no-alert suppression, as in `NAB-VIS-02` | broad anomaly validation |
| `CTA-NAB-03` | support-only false-alarm-sensitive diagnostic claim, as in `NAB-VIS-04` | unqualified detector effectiveness |
| `CTA-AI4I-01` | boundary probe that must be rejected | admitted predictive-maintenance claim |

Exact registered examples are in:

- `data/claim_passport_casebook_20260519.csv`
- `data/nab_adapter_visual_passport_rows_20260519.csv`
- `artifact/claim_template_admission_cases_20260521.csv`

You can also print the current shortlist:

```bash
python3 src/claimcontractbench.py templates
```

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
- For a new paper supplied by the user, human_check_required should be yes for
  every row, including registered-template calls.
- Prefer NEEDS_TEMPLATE_ADMISSION over CALL_REGISTERED_TEMPLATE when uncertain.
- Prefer OUT_OF_SCOPE_DO_NOT_CALL over NEEDS_TEMPLATE_ADMISSION for non-metric
  review tasks.
- Return plain CSV only. Do not include explanations outside CSV fields.
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

`unsafe_release_rate` is an output-safety check over the packet decisions. It is
not a score for whether the LLM extracted every relevant claim from a paper.
The current release audits the supplied packet; it does not certify full
coverage of a full paper.

For paper review, the most useful rows are often not the accepted ones. The
high-value rows are usually rewrites, suppressions, support-only boundaries,
and admission tickets, because those show where a paper's prose outruns its
evidence.

## When No Template Matches

`NEEDS_TEMPLATE_ADMISSION` is not an error. It means the current release is
refusing to pretend that a nearby template applies. Use:

```bash
python3 src/claimcontractbench.py admission-guide
python3 src/claimcontractbench.py init-template --output claim_packets/my_template_admission.csv
python3 src/claimcontractbench.py admit-template --input claim_packets/my_template_admission.csv
```

The user's LLM should draft a candidate row following
`artifact/TEMPLATE_ADMISSION_QUICKSTART_20260527.md`. The required idea is:
new domains enter only by supplying a typed evidence unit, finite claim
template, `G/Q/U` bindings, action mapping, preorder/incomparability,
forbidden claim, anchor, and boundary note.

## Safety And Privacy

Only send paper text to an LLM if you are allowed to do so under the venue,
author, or institutional rules that apply to you. For confidential peer review,
use an approved private model or do not use the LLM front end. ClaimContractBench
can still run on manually prepared CSV packets without sending any text to an
external model.

## Optional Feedback Report

Feedback is optional and is not required to use the tool. An AI assistant must
not generate feedback by default. It should first show the user this exact
public-safe prompt and wait for explicit approval:

```text
With your approval, I can write a public-safe ClaimContractBench usability feedback note using only command names, aggregate routing counts, non-confidential summaries, and paraphrased template gaps, excluding confidential paper text, private review notes, author identities, unpublished results, raw data, credentials, private links, and local paths.
```

```bash
python3 src/claimcontractbench.py feedback-guide
python3 src/claimcontractbench.py init-feedback --output feedback/my_feedback_report.md
```

If the user approves, the feedback should focus only on usability: command
names, aggregate routing counts, confusing steps, and paraphrased template gaps.
It must not include confidential paper text, private reviewer notes, raw data,
local paths, author identities, unpublished results, credentials, or private
links. If the user is acting as a CIKM reviewer or is bound by
review-confidentiality rules, use official venue channels rather than contacting
the authors directly.

Use the prompt and minimal template in:

- `artifact/USER_EXPERIENCE_FEEDBACK_GUIDE_20260527.md`
- `artifact/user_experience_feedback_template_20260527.md`
