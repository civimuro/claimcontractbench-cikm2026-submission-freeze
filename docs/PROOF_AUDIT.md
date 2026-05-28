# Codex Proof Audit Path

ClaimContractBench's metric-to-claim checker intentionally stops proof
correctness, theorem novelty, and rate-chain validity as out of scope.  This
page adds a separate Codex-run proof-audit path for those rows.

For external integrations, this path is optional.  The machine-readable
interface in `docs/INTEGRATION_INTERFACE.md` marks proof audit as a capability
that can be ignored when a tool only needs empirical claim review.

## What This Path Does

- Decomposes theorem, lemma, proposition, corollary, and nontrivial proof steps
  into atomic proof claims.
- Checks those claims for assumptions, edge cases, independence, measurability,
  tail bounds, notation collisions, and rate-chain drift.
- Produces concrete LaTeX patch suggestions with stable anchors such as
  `\hypertarget{gap_C7}{}`.
- Keeps proof audit separate from empirical metric-to-claim licensing.

## What It Does Not Do

- It does not accept or reject a paper.
- It does not verify a theorem formally in Lean, Coq, or another proof
  assistant.
- It does not certify novelty, venue fit, legal compliance, deployment safety,
  or human reviewer utility.
- It is executed by Codex only in this release path.

## Codex-Only Workflow

Use this path after a proof or rate claim is routed to
`OUT_OF_SCOPE_DO_NOT_CALL` by the metric-to-claim packet checker, or when a
reviewer directly wants proof rigor.

1. Verify the release first:

   ```bash
   python3 src/claimcontractbench.py doctor
   python3 src/claimcontractbench.py smoke
   ```

2. Read the proof-audit guide:

   ```bash
   python3 src/claimcontractbench.py proof-audit-guide
   ```

3. Create a local audit draft:

   ```bash
   python3 src/claimcontractbench.py init-proof-audit --output proof_audits/my_proof_audit.md
   ```

4. Run a small canary preflight before auditing a new manuscript.  Codex should
   be able to identify at least the following known issues from short snippets:
   missing DCT domination, Hoeffding misuse, undeclared iid sampling, an
   `n=1` boundary failure, and cross-fitting fold-dependence.

5. Give Codex the paper source and ask it to fill the draft.  Keep
   confidential paper text, private review notes, and raw data local unless
   sharing is explicitly allowed.

## Local Artifacts

A full audit should keep its local working files under a `proof_audit/`
directory next to the draft report:

```text
proof_audit/
  claims.json
  global_assumptions.txt
  claim_packages/
  prior_round_state.json
  findings_codex_pedantic.json
  findings_codex_adversarial.json
  findings_codex_generous.json
  synthesized.json
  classified.json
  lint_report.json
  round_metric.json
  RESIDUAL.md
THESIS_AUDIT.md or proof_audits/<name>.md
OPEN_PROBLEMS.md
```

These are local work products.  They should not be treated as release data or
uploaded publicly without review.

## Audit Roles

Codex performs all audit roles.  If Codex subagents are available, they may be
used for independent passes; otherwise run the passes sequentially in one
thread.

- Pedantic pass: notation, definitions, measurability, regularity, and
  dimension checks.
- Adversarial pass: counterexamples, degenerate regimes, asymptotic order, and
  edge cases.
- Repair pass: smallest sufficient assumptions and patch wording that would
  make a claim true.

The roles are review lenses, not separate authorities.  The final report should
deduplicate issues, mark low-confidence items, and keep human judgment in the
loop.

## Cross-Round State And Triage

For iterative proof repair, keep durable state across rounds.  Each new round
should receive prior findings and fix attempts, so it cannot simply rediscover
the same concern under a new phrasing.

Classify findings into three handling tiers:

- `L`: logical proof issue, plausibly fixable by a bounded LaTeX patch;
- `S`: style, citation, notation, or exposition issue for human review;
- `O`: open mathematical problem or scope issue requiring a new theorem,
  weaker statement, or future work.

Recurring findings should be promoted out of the auto-fix loop once repeated
patch attempts stop changing the mathematical issue.

## Rate-Chain Mode

For a top-level rate corollary that depends on a long lemma chain, Codex should
build an explicit dependency table and compare the walked rate against the
stated rate.  This is useful for exponent-level mismatches that are invisible
when each lemma is read locally.

Use claim packages and a walked-vs-stated table:

- discover the dependency chain from the target label;
- extract each statement rate and proof-walked rate;
- compose rates deterministically;
- report any mismatch with two patch options: weaken the top-level claim or
  tighten the specific upstream lemma.

The release includes a public-safe template and checklist, not an autonomous
rate-chain proof engine.  A reviewer can audit the resulting report because
every gap should carry a claim id, source location, and LaTeX patch.

## Validation And Patch Lint

Before a finding enters the main report, Codex should check:

- structured fields are present and use stable claim ids;
- severity is an integer from 0 to 5;
- each non-verified finding has a `gap_type`;
- every patch starts with a matching `\hypertarget{gap_<claim_id>...}{}`;
- labels referenced by a patch already exist in the manuscript;
- invented macros or semantic conflicts are flagged for human review.

Findings that fail lint should move to `RESIDUAL.md`, not disappear.

## Output Standard

The local report should include:

- total atomic claims;
- canary result and PDF-extraction warning if applicable;
- verified, gap, missing-assumption, unjustified-step, and notation counts;
- L/S/O triage counts;
- top fixes ranked by severity;
- prioritized gap list with patch snippets;
- residual low-confidence items;
- open-problem items;
- round metric and convergence recommendation when iterative repair is used;
- a limits section stating what the audit did not check.

Use `artifact/PROOF_AUDIT_CODEX_GUIDE_20260528.md` for the detailed
agent-facing instructions and `artifact/proof_audit_plan_template_20260528.md`
for the local draft structure.
