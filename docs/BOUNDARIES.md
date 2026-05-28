# Boundaries

ClaimContractBench is a claim-licensing resource for registered empirical
metric-to-claim cases. It is designed to be useful because it fails closed.

## What It Does

- Checks whether a supplied claim packet matches registered finite templates.
- Rewrites, weakens, relabels, suppresses, or accepts claims under declared
  `G/Q/U` context.
- Opens template-admission work when a relevant claim has no registered
  contract.
- Stops out-of-scope rows before they are treated as claim-license problems.
- Regenerates public-safe derived reports and validation checks.

## What It Does Not Do

- It is not an autonomous reviewer or paper-acceptance engine.
- It is not an arbitrary natural-language fact checker.
- It does not prove proof correctness, novelty, legal compliance, ethics
  approval, deployment safety, fairness, or human reviewer utility.
- It does not certify full-paper coverage.
- It does not redistribute raw third-party datasets.
- It does not turn LLM output into authority. LLMs may draft or route packets;
  the deterministic checker enforces the registered boundary.

## Roles

Human role:

- choose the paper, excerpt, paragraph, or claim to inspect;
- decide whether the output matters for a review or rewrite;
- approve or reject new template admissions;
- handle scientific disputes outside the registered template catalog.

LLM role:

- optionally extract candidate empirical claims;
- optionally route claims into the public labels;
- optionally draft a typed template-admission row;
- never act as the licensing authority.

Deterministic tool role:

- validate the release surface;
- apply registered templates;
- reject unknown or malformed template calls;
- create reports that expose unsafe release rate, action decisions, and
  fail-closed behavior.

## Safe Interpretation

A passing check means the release surface or supplied packet satisfies the
documented contract. It does not mean the paper is accepted, the LLM found every
important claim, or the tool is useful to human reviewers without further study.

The safest strong claim is:

> Given the supplied packet and registered templates, ClaimContractBench exposes
> which rows are licensed, weakened, rewritten, suppressed, admitted for new
> template work, or stopped as out of scope.
