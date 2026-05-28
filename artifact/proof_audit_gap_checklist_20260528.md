# Proof-Audit Gap Checklist

This checklist supports the Codex proof-audit path.  It is public-safe and
domain-general; use it as a review aid rather than as a proof of correctness.

## Measurability And Conditioning

- Supremum over an uncountable index set is used without separability,
  continuity, or another measurability argument.
- Conditional expectation is written without naming the conditioning
  sigma-field.
- Stopping times, filtrations, or null-set modifications are used without the
  required event-level verification.

## Limit Exchange

- Limit and expectation are exchanged without domination or uniform
  integrability.
- Sum, integral, derivative, or supremum operations are exchanged without the
  needed theorem or uniform convergence condition.
- A double limit is treated like a joint limit without a stated coupling.

## Independence And Dependence

- Independent, iid, exchangeable, stationary, or mixing data are used before
  those conditions are declared.
- Sample splitting or cross-fitting is used, but the independence from the test
  fold is not stated.
- A martingale difference or bootstrap conditional-independence step is assumed
  without verification.

## Concentration And Tail Bounds

- A concentration inequality is invoked with missing bounded-difference,
  variance, Orlicz, or tail assumptions.
- Constants hide dimension, class count, worker count, or degree dependence that
  matters for the target rate.
- A polynomial tail is used as though it were exponential.

## Regularity

- Continuity, differentiability, compactness, boundedness, identifiability, or
  Lipschitz conditions are used but not stated.
- A Taylor expansion is made at a boundary point or with no neighborhood
  condition.
- A density argument is used in a setting where only a dominating measure has
  been defined.

## Asymptotic Regimes

- The proof switches between fixed and growing dimension without restating the
  regime.
- A rate condition is sufficient for one lemma but too weak for a later union
  bound.
- A theorem claims a sharp boundary while the proof establishes only a
  conservative sufficient condition.
- The theorem statement and proof use different quantifiers, such as "for all"
  in the statement and "for fixed" in the proof.
- A walked rate from upstream lemmas has a different exponent from the stated
  top-level rate.

## Notation And Scope

- The same symbol denotes two objects in overlapping scopes.
- A generic constant changes from line to line without declaration.
- Population and empirical objects are visually similar but not separated by
  notation.
- The theorem statement, proof body, and discussion use different quantifiers.

## Boundary Cases

- Empty sets, zero denominators, zero variance, missing communities, degenerate
  matrices, or non-positive probabilities are not handled.
- A result requires nondegeneracy but does not state it.
- A proof relies on labels, ranks, or class sizes that may vanish in the stated
  regime.

## Patch Pattern

Every accepted gap should have:

- a stable claim id;
- a severity score;
- an L/S/O triage label;
- a one-paragraph explanation;
- an insertion hint;
- a LaTeX patch carrying `\hypertarget{gap_<claim_id>}{}`.

## Patch Lint

Before a patch is promoted to the main audit report, check:

- the hypertarget anchor in the patch matches the finding id;
- every referenced label already exists in the manuscript;
- any new macro is either defined in the paper or explicitly introduced by the
  patch;
- the patch does not contradict a stated regime, such as fixed versus growing
  dimension;
- warnings are attached to the finding instead of silently ignored.

## Iteration Triage

- `L`: logical proof bug that is likely fixable by a bounded patch.
- `S`: style, citation, notation, exposition, or recurring concern that needs
  human review.
- `O`: open mathematical problem or scope issue requiring a new theorem,
  weaker statement, or future work.
