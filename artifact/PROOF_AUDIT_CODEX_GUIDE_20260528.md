# Codex Proof-Audit Guide

Use this guide when a theorem, proof, lower bound, or rate-chain claim needs
rigor review.  This path is separate from registered empirical metric-to-claim
templates.

## Boundary

The metric-to-claim checker may route proof claims to
`OUT_OF_SCOPE_DO_NOT_CALL`.  That is correct: proof audit is a different task.
Codex may audit proof rigor, but the deterministic claim-contract checker does
not become a proof verifier.

## Inputs

- Prefer LaTeX source for theorem and appendix audits.
- For digital PDFs, extract local text first and spot-check mathematical
  notation against the rendered paper.  Cap confidence for PDF-extracted
  findings because text extraction can corrupt math.
- For scanned or handwritten PDFs, report a blocker and request source or a
  reliable math OCR artifact.
- Read the main text when an appendix proof depends on definitions,
  assumptions, notation, or theorem statements there.

## Phase 0: Canary Preflight

Before a fresh audit, run a short local preflight.  Codex should correctly
classify these minimal cases:

| case | expected finding |
| --- | --- |
| limit and expectation exchanged without domination | `DCT-no-dominating-function` |
| Hoeffding used without bounded or sub-Gaussian inputs | concentration precondition gap |
| SLLN used after "sample" with no iid declaration | `iid-undeclared` |
| sample variance or denominator used at `n=1` | boundary-case gap |
| cross-fitting score uses nuisance estimates from the same fold | fold-independence gap |
| clean Chebyshev proof with stated finite variance | verified |

Abort the audit if Codex misses most buggy cases or invents a false positive on
the clean case.  Record the canary result in the report summary.

## Phase 1: Atomic Claim Decomposition

Create a stable list of atomic claims.  Include explicit theorem-like
environments and nontrivial proof steps such as concentration bounds,
conditioning arguments, limit exchanges, and rate substitutions.

Also collect global assumptions from setup and assumption blocks into
`proof_audit/global_assumptions.txt`.  This prevents false positives caused by
reading an appendix slice without the paper's declared assumptions.

Use this schema:

```json
{
  "claim_id": "C3",
  "claim_text": "verbatim or tightly paraphrased statement",
  "source_location": "section, theorem, lemma, or line hint",
  "depends_on": ["C1", "C2", "Davis-Kahan"],
  "preconditions": ["Assumption 2.1", "fixed K", "independent split"],
  "invoked_lemmas": ["Lemma A.1", "Davis-Kahan"],
  "status": "unreviewed",
  "gap_type": "",
  "severity": 0,
  "latex_patch": "",
  "confidence": 0.0
}
```

Severity uses 1 for cosmetic issues and 5 for proof-threatening issues.

Build claim packages when the manuscript is large:

```text
proof_audit/claim_packages/C3.json
```

Each package should contain statement text, proof text, local context,
dependency labels, known anchors, source line hints, and warnings.  Codex roles
should read packages first and open the full manuscript only when a package is
stale or incomplete.

## Phase 2: Codex Audit Passes

All audit passes are executed by Codex as part of this release path.  The roles
may be run sequentially or by Codex subagents; in both cases they use the same
claim packages and schema.

### Pedantic Pass

Check literal proof hygiene: undefined symbols, reused notation, missing
sigma-fields, measurability, regularity, dimension mismatch, constants that
change without declaration, and theorem statements that do not match proofs.

### Adversarial Pass

Try to break the claim through boundary cases: empty sets, zero variance,
vanishing class sizes, degenerate matrices, heavy tails, unclear joint limits,
dependence hidden by sample splitting, or constants that grow with dimension.

### Repair Pass

For each likely gap, propose the smallest sufficient assumption or proof step.
Prefer a patch that preserves the paper's intended theorem; if that is too
strong, propose a narrower theorem statement.

## Phase 3: Cross-Check And Consolidation

Codex should cross-check the union of role findings before synthesis:

- uphold findings with concrete support;
- refute findings only with a specific missed assumption, misread, or counter
  argument;
- partially uphold findings when the issue is real but the type or severity is
  wrong.

Deduplicate by `(claim_id, gap_type)`.  Keep a gap in the main report when it
is high severity, supported by multiple roles, or objectively checkable.  Keep
single-role or disputed findings in `RESIDUAL.md` unless human review promotes
them.

Rank by severity first and confidence second.

## Phase 4: Triage Classification

Classify each main finding:

- `L`: logical bug, bounded patch likely;
- `S`: style, citation, notation, or exposition issue;
- `O`: open problem, scope issue, or finding requiring new mathematics.

Recurring findings across multiple rounds should move to `S` or `O` rather
than staying in the auto-fix queue indefinitely.

## Phase 5: Patch Lint

Before publishing the local audit report, lint every patch:

- `hypertarget_anchor` matches the patch's first line;
- referenced labels exist in the manuscript;
- severity is a valid integer;
- non-verified findings have a nonempty gap type and insertion hint;
- new macros are either defined or flagged;
- patch assumptions do not obviously contradict stated regimes.

Findings that fail hard lint go to `RESIDUAL.md`; warnings remain in the main
report with the warning attached.

## Phase 6: Report

Write the local report in the draft created by:

```bash
python3 src/claimcontractbench.py init-proof-audit --output proof_audits/my_proof_audit.md
```

Each patch must include a traceable anchor:

```latex
\hypertarget{gap_C3}{}%
```

Use direct LaTeX snippets and insertion hints.  The report should be actionable
for an author revising a proof, not a general paper review.

## Rate-Chain Mode

Use rate-chain mode when the target claim is a composed big-O or asymptotic
rate that depends on several lemmas.  Codex should build:

- a dependency list from the target theorem or corollary back to upstream
  lemmas;
- a table of stated rates;
- a table of walked rates obtained from the proof chain;
- a walked-vs-stated diff;
- patch options such as weakening the top-level rate or tightening a specific
  upstream lemma.

Abort rate-chain mode if the chain is too short, the target is not a rate
statement, or the paper has already been formally verified.

## Iteration State

For multi-round repair, maintain:

```text
proof_audit/state.json
proof_audit/prior_round_state.json
proof_audit/round_metric.json
OPEN_PROBLEMS.md
```

Each round should record new findings, recurring findings, closed findings,
L/S/O counts, and a stop recommendation.  Stop when the logical Tier-L backlog
is drained, or pause for human judgment when findings recur without new
actionable changes.

## Public-Safe Reporting

Do not include confidential paper text in public issues.  For public discussion,
paraphrase the finding, cite public theorem labels when available, and omit raw
data, private review notes, and author identities unless sharing is explicitly
allowed.
