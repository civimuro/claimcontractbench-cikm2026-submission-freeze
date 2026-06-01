# Agent One-Shot Review Guide

Date: 2026-05-27
Status: `PUBLIC_SAFE_AGENT_HANDOFF_GUIDE`

This guide is for AI coding assistants or LLM agents that have access to this
repository and are asked to use ClaimContractBench in one instruction.

Typical user instruction:

> Use the tools in this repository to assist a review of the supplied paper.

The goal is a bounded claim-audit report, not an autonomous accept/reject
review. The agent extracts candidate empirical metric-to-claim statements,
ClaimContractBench checks the supplied packet against registered templates and
admission boundaries, and a human reads the final report.

## Preconditions

Proceed only when these inputs are available:

- a paper, excerpt, or results section that the user is allowed to process;
- a local checkout of this repository;
- permission to run local Python commands.

If no paper text or paper path is supplied, ask for it. If the current assistant
cannot run local commands, explain that it can draft a packet but cannot run the
deterministic checks. If the paper is confidential, do not send it to an
external model unless the user explicitly confirms that this is allowed.

## One-Shot Workflow

From the repository root:

```bash
python3 src/claimcontractbench.py doctor
python3 src/claimcontractbench.py smoke
python3 src/claimcontractbench.py templates
python3 src/claimcontractbench.py init-packet --output claim_packets/agent_claim_packet.csv
```

Then read:

- `README.md`
- `artifact/LLM_ASSISTED_REVIEW_QUICKSTART_20260527.md`

Extract candidate empirical claims from the supplied paper into
`claim_packets/agent_claim_packet.csv` with this exact header:

```csv
packet_id,source_title,source_section,submitted_claim,intended_use,route_label,template_id,evidence_pointer,llm_reason,human_check_required
```

Use only these `route_label` values:

- `CALL_REGISTERED_TEMPLATE`
- `NEEDS_TEMPLATE_ADMISSION`
- `OUT_OF_SCOPE_DO_NOT_CALL`

Use `CALL_REGISTERED_TEMPLATE` only when the paper claim clearly matches a
registered template printed by `templates`. When uncertain, prefer
`NEEDS_TEMPLATE_ADMISSION`. Use `OUT_OF_SCOPE_DO_NOT_CALL` for novelty,
proof-correctness, implementation-bug, ethics, policy, legal, or acceptance
judgments that are not metric-to-claim audits.
For user-supplied papers, set `human_check_required=yes` for every extracted
row, including registered-template calls. Use `human_check_required=no` only for
release-provided registered controls.

Run the packet:

```bash
python3 src/claimcontractbench.py review \
  --input claim_packets/agent_claim_packet.csv \
  --output reports/agent_claim_review
```

Read:

```text
reports/agent_claim_review/llm_claim_review_packet_report.md
reports/agent_claim_review/llm_claim_review_packet_decisions.csv
reports/agent_claim_review/llm_claim_review_packet_summary.json
```

If the report contains `NEEDS_TEMPLATE_ADMISSION`, do not force a nearby
registered template. Summarize the missing adapter need. If the user asks to
draft a new template, use:

```bash
python3 src/claimcontractbench.py admission-guide
python3 src/claimcontractbench.py init-template --output claim_packets/agent_template_admission.csv
python3 src/claimcontractbench.py admit-template \
  --input claim_packets/agent_template_admission.csv \
  --output reports/agent_template_admission
```

## Final Response Template

Write a concise report with these sections:

1. What I ran
2. Packet coverage
3. Claim-level findings
4. Paper-level review implications
5. Template gaps and out-of-scope items
6. Tool limitations
7. Next actions

For claim-level findings, report the important rows by action:

- accepted licensed claims;
- claims rewritten or weakened by the tool;
- suppressed claims;
- support-only claims;
- claims that need template admission;
- out-of-scope claims.

## Fail-Closed Rules

Do not:

- invent metric evidence or tables that are not in the supplied paper;
- claim full-paper coverage unless the packet truly covers the full paper;
- treat a passing packet as a paper acceptance recommendation;
- treat `NEEDS_TEMPLATE_ADMISSION` as failure or success;
- force an unknown field into a registered template;
- include confidential paper text, private reviewer notes, raw data, local
  paths, or author identities in shareable reports unless the user explicitly
  allows it.

The safest useful outcome is often a report that says which claims should be
rewritten, weakened, suppressed, or admitted through a new template before the
paper can make them responsibly.

## Optional Feedback

Do not generate a user-experience feedback report by default. If feedback would
be useful, first show the user this exact public-safe prompt and wait for
explicit approval:

```text
With your approval, I can write a public-safe ClaimContractBench usability feedback note using only command names, aggregate routing counts, non-confidential summaries, and paraphrased template gaps, excluding confidential paper text, private review notes, author identities, unpublished results, raw data, credentials, private links, and local paths.
```

If the user approves, follow
`artifact/USER_EXPERIENCE_FEEDBACK_GUIDE_20260527.md`. If the user is acting as
a CIKM reviewer or is bound by review-confidentiality rules, do not route
feedback through the authors; use official venue channels.
