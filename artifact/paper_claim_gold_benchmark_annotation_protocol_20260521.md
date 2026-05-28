# Paper-Claim Gold Benchmark Annotation Protocol

Status: public-safe work-use protocol, 2026-05-21.

Purpose: define how labels in the paper-claim gold benchmark were assigned and
what reliability claims they can and cannot support.

Related files:

- `artifact/paper_claim_gold_benchmark_blind_annotation_packet_20260521.csv`
- `artifact/paper_claim_gold_benchmark_annotation_map_20260521.csv`
- `src/run_paper_claim_annotation_agreement.py`

## Unit

The annotation unit is a public-safe paraphrased claim sentence, not a copied
paper passage. Each external source contributes three claim rows:

1. a bounded claim that would be admissible after a valid adapter exists;
2. an over-broad or unsafe claim that would require rewrite, weakening,
   support-only treatment, suppression, or rejection after a valid adapter
   exists;
3. an out-of-scope claim that should not call the current metric-to-claim tool.

The registered control source contributes eight rows that exercise the current
template-intake backend.

## Route Labels

`CALL_REGISTERED_TEMPLATE`: a registered template id is present, so the current
backend should decide the claim now.

`NEEDS_TEMPLATE_ADMISSION`: the claim is relevant to empirical claim
governance, but the current release lacks the adapter fields required to decide
it now. This is a fail-closed state, not a negative judgment about the source
paper.

`OUT_OF_SCOPE_DO_NOT_CALL`: the claim asks for legal, policy, proof, novelty,
forensic, acceptance, code-correctness, or deployment-safety judgment outside
the current metric-to-claim operator.

## Post-Admission Gold Actions

`ACCEPT`: the claim is bounded to the stated evidence family and would be
licensed after a valid adapter exists.

`REWRITE`: the claim is directionally related to evidence but must be rewritten
to a narrower licensed sentence.

`WEAKEN`: the claim can survive only as diagnostic, local, conditional, or
construct-validity-limited wording.

`SUPPORT_ONLY`: the claim can be used as supporting context but not as a
headline contribution or mainline result.

`SUPPRESS`: the claim should not be emitted as a non-bottom claim under the
available evidence.

`REJECT`: the claim or template attempt fails the adapter contract.

`OUT_OF_SCOPE`: the claim belongs outside this tool family.

## Current Expected Actions

`current_expected_action` is the action the current release is allowed to emit.
For external rows without registered templates, this is `UNSUPPORTED_TEMPLATE`.
For out-of-scope rows, this is `OUT_OF_SCOPE`. For registered controls, it is
the deterministic action computed by the current reviewer claim-intake backend.

This split is essential. The benchmark should not count a future-admissible
claim as currently accepted unless the relevant adapter already exists.

## Quality Checks

The runner checks:

- source and case file readability;
- 30-50 external papers;
- 3-5 claim rows per external paper;
- source/case joins;
- unique claim ids;
- route/action enum validity;
- one registered-control source with eight controls;
- current action consistency;
- registered backend consistency;
- false accepts over non-accept rows;
- false releases for unsupported or out-of-scope rows;
- false kills on supported registered controls;
- private path, coordination-marker, and credential-like pattern absence.

## Reliability Status

The current file is a single-annotator internal gold benchmark with deterministic
consistency checks. It is suitable for release-surface reliability testing and
for demonstrating fail-closed behavior.

A randomized 128-row blind packet now exists for an independent second
annotator. The packet intentionally omits `route_label`,
`gold_action_after_admission`, and `current_expected_action`; it exposes only
claim text, source context, intended use, evidence anchor, and blank annotator
label columns. The companion annotation map lets the agreement runner join the
filled packet back to the gold key after annotation.

It is not yet a publication-grade human-annotation study. A publication-grade
extension should add at least one independent annotator, adjudicate
disagreements, report agreement such as Cohen's kappa or Krippendorff's alpha,
and preserve the same route/action definitions so new annotations remain
comparable with this benchmark.

## Allowed Claim

Allowed:

> On a 40-paper public-safe paraphrased paper-claim benchmark, the current
> release matches 128/128 current expected actions, keeps registered controls
> consistent, and fails closed for unsupported-template and out-of-scope rows.

Forbidden:

> The current release autonomously reads arbitrary papers, extracts their
> claims, and verifies all scientific conclusions.
