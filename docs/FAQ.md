# FAQ

## Do I need an LLM?

No. The human path is:

```bash
python3 src/claimcontractbench.py doctor
python3 src/claimcontractbench.py smoke
python3 src/claimcontractbench.py human-guide
```

An LLM can draft a packet, but the deterministic checker is the authority.

## Do I need raw data?

No for first inspection. The release uses public-safe manifests, schemas,
derived tables, and fixtures. It does not redistribute raw third-party datasets.

## What does `G/Q/U` mean?

`G` records the information or comparison boundary. `Q` records the
reportability policy. `U` records the decision-use context. Together they stop
a metric result from being silently reused as a stronger prose claim.

See `docs/CONCEPTS.md` for a plain-language example.

## Why are so many external paper rows unsupported or out of scope?

That is part of the resource boundary. The current catalog is small and
registered. Relevant claims without a typed template go to
`NEEDS_TEMPLATE_ADMISSION`; non-metric judgments stop at
`OUT_OF_SCOPE_DO_NOT_CALL`.

## Does a passing packet mean a paper is good?

No. It means the supplied rows were handled according to the registered
template contract. It is not an acceptance recommendation.

## Can this replace peer review?

No. It can help inspect whether specific empirical prose claims overreach their
evidence. Human reviewers still decide novelty, correctness, significance,
clarity, and venue fit.

## Can it audit proofs?

The metric-to-claim runner does not audit proofs.  The repository now includes
a separate Codex-only proof-audit guide and local scaffold for theorem and
rate-chain review:

```bash
python3 src/claimcontractbench.py proof-audit-guide
python3 src/claimcontractbench.py init-proof-audit --output proof_audits/my_proof_audit.md
```

That path can produce gap lists and LaTeX patches, but it is not formal
verification or a paper verdict.

## Why does the repo include an LLM-assisted path?

Because LLMs can be convenient for drafting candidate claim packets. The path is
separate so that the project remains usable by humans and so that LLM output is
never treated as licensing authority.

## Can another tool integrate only part of this repository?

Yes. Use:

```bash
python3 src/claimcontractbench.py integration-interface
```

The JSON interface marks the empirical claim-review checker as the core
capability and proof audit as optional. A collaborator can ignore proof audit
without changing the claim-review workflow.

## How should I ask a question or propose a template?

Use `SUPPORT.md`, `CONTRIBUTING.md`, and the GitHub issue templates. Keep the
question public-safe: paraphrase examples, cite public sources when possible,
and avoid confidential review material or raw data.

## What should I cite?

For now, cite the paper and the repository commit. The final public release
should add a version tag, GitHub release, archive DOI, and final citation
metadata.
