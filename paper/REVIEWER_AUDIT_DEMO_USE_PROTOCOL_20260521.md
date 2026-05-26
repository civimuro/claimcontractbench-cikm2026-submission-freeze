# Reviewer Audit Demo Use Protocol (2026-05-21)

Status: `BOUNDED_REVIEWER_COMPONENT_PROTOCOL`.

Purpose: define exactly how the reviewer-facing audit demo may be used, what
it proves, and where it must fail closed. This protocol is part of the tool
boundary, not a paper-polish document.

## 1. One-Sentence Use Boundary

For selected empirical-claim excerpts, the tool maps a routed claim span to one
of three safe paths: registered-template decision, adapter-admission ticket, or
out-of-scope stop.

It is not a paper-acceptance engine. It is not a full-paper parser. It does not
certify deployment safety, legal compliance, mechanistic truth, novelty, or
social impact.

## 2. Roles

Human role:

- choose the paper, section, paragraph, or claim sentence to inspect;
- decide whether the audit output is relevant to the review question;
- resolve substantive scientific disputes that are outside the registered
  metric-to-claim templates;
- approve any new adapter before it enters the registered template catalog.

LLM role:

- optionally help extract candidate claim spans from a selected paragraph;
- optionally choose among the public route labels and registered template menu;
- optionally draft reviewer-facing wording from the deterministic output;
- never act as the licensing authority for a claim.

Deterministic tool role:

- enforce the registered claim-template catalog;
- convert registered templates into accept, rewrite, suppress, support-only, or
  reject decisions;
- send unsupported-but-relevant claims to adapter admission;
- stop out-of-scope text at `bottom_T`;
- expose checks and regression outputs so later edits cannot hide drift.

## 3. Required Invocation Contract

The current demo is valid only when the caller supplies or derives:

| Field | Requirement |
| --- | --- |
| selected text | a short paragraph, snippet, or claim sentence, not an arbitrary full PDF |
| claim span | the candidate empirical claim to be audited |
| route label | one of `CALL_REGISTERED_TEMPLATE`, `NEEDS_TEMPLATE_ADMISSION`, or `OUT_OF_SCOPE_DO_NOT_CALL` |
| template id | required only for `CALL_REGISTERED_TEMPLATE` |
| source title/family | public-safe provenance label for the audit card |
| boundary guide | public route/admission guide used by the span router |

If a route label or template id is guessed without the public menu, the result
is an extractor experiment, not a licensed claim-audit result.

The companion paper-excerpt reviewer-value benchmark uses the same boundary:
its default run supplies human-gold routes as an oracle front end, while its
prediction packet and `text_rules` baseline are front-end experiments rather
than new licensing authority.

## 4. Output Semantics

The tool emits reviewer-facing actions with deliberately narrow meanings:

| Output family | Meaning |
| --- | --- |
| `ACCEPT_LICENSED` | the submitted claim already matches a registered licensed sentence |
| `REWRITE_TO_LICENSED` | the current wording overclaims, but a registered weaker sentence is available |
| `SUPPRESS_BOTTOM` | the claim must not be emitted under the registered context |
| `SUPPORT_ONLY_REWRITE` | the claim can support a boundary or diagnostic point but cannot headline the paper |
| `REJECT_PATCHWORK` | a proposed template lacks the adapter contract and must not enter the catalog |
| `REJECT_UNKNOWN_TEMPLATE` | no registered template exists for the supplied id |
| `OPEN_ADMISSION_TICKET` | the text is relevant but needs a template/admission process first |
| `DO_NOT_CALL_CLAIM_RUNNER` | the text belongs outside the current metric-to-claim object |

These outputs are claim-governance decisions, not paper-level accept/reject
decisions.

## 5. Evidence Currently Supporting This Boundary

The current reviewer-facing demo joins two paragraph-router packets:

- selected packet: 36 cards, route accuracy 0.972, joint span-route accuracy
  0.972, with the known residual `selected-NSR-025`;
- fresh holdout packet: 36 cards, route accuracy 1.000, joint span-route
  accuracy 1.000 under the locked public guide;
- registered-template controls: 8 rows covering accept, rewrite, suppress,
  support-only, patchwork reject, and unknown-template reject;
- boundary rows: 43 adapter-admission tickets and 21 out-of-scope stops.

This is evidence that the component is conservative and regression-testable for
selected excerpts. It is not evidence that arbitrary full papers can be parsed
without a separate extractor benchmark.

## 6. Correct Use Cases

Use the tool when a reviewer or author asks:

- is this metric-backed claim already licensed by a registered template?
- should this wording be weakened to a licensed sentence?
- is this claim relevant but unsupported because no adapter has been admitted?
- is this sentence outside the metric-to-claim object and therefore unsafe to
  run through the claim runner?
- which part of a review comment should become an admission ticket rather than
  an immediate rejection?

Do not use the tool when the question is:

- should the paper be accepted?
- is the theory novel?
- is the method mathematically correct?
- is deployment legally or ethically safe?
- does the code faithfully implement the algorithm?
- is an arbitrary domain already supported without adapter admission?

## 7. Failure and Escalation Policy

The component fails closed:

- missing or unknown template id -> `REJECT_UNKNOWN_TEMPLATE`;
- relevant but unregistered empirical claim -> `OPEN_ADMISSION_TICKET`;
- legal, ethics, novelty, proof, code, or paper-level judgment -> `DO_NOT_CALL_CLAIM_RUNNER`;
- registered suppression condition -> `SUPPRESS_BOTTOM`;
- support-only adapter row -> support-only wording, not headline wording.

If a user wants the tool to support a new domain, the domain must first pass
adapter admission: claim templates, G/Q/U fields, action mapping, typed
preorder, forbidden claims, and a visual passport row must be supplied and
reviewed.

## 8. What Would Be Needed For Stronger Autonomy

The next autonomy level would require a larger extractor benchmark over full
paper text, with measured span recall, route accuracy, false-call rate,
unsupported-template rate, and reviewer agreement. Until that exists, the
scientifically correct statement is:

> The tool supports bounded, auditable claim decisions for selected empirical
> excerpts with a registered template/admission boundary; it does not yet
> autonomously review whole papers.
