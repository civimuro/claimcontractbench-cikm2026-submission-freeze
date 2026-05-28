# LLM-Assisted Path

This path is for users who want an LLM to draft a claim packet. It is optional.
The human reviewer path does not require it.

## Division Of Labor

- LLM: finds candidate empirical claims and routes them into the CSV format.
- ClaimContractBench: checks registered templates, template-admission needs,
  out-of-scope rows, malformed packets, and unsafe releases.
- Human: decides whether the output matters for a review, rewrite, or template
  addition.

## Minimal Workflow

```bash
python3 src/claimcontractbench.py templates
python3 src/claimcontractbench.py init-packet --output claim_packets/my_claim_packet.csv
```

Ask the LLM to fill the packet with one candidate claim per row. Then run:

```bash
python3 src/claimcontractbench.py review --input claim_packets/my_claim_packet.csv
```

## Route Labels

- `CALL_REGISTERED_TEMPLATE`: only for an exact registered template match.
- `NEEDS_TEMPLATE_ADMISSION`: relevant empirical metric-to-claim statement, but
  no registered template safely applies.
- `OUT_OF_SCOPE_DO_NOT_CALL`: proof, novelty, policy, ethics, legal,
  implementation, or acceptance judgment outside this resource.

When uncertain, prefer `NEEDS_TEMPLATE_ADMISSION` over a template call.

## Safety Rules

- Do not send confidential paper text to an external model unless allowed.
- Do not ask the LLM to decide whether a claim is scientifically true.
- Do not let the LLM invent evidence or table references.
- Do not treat a passing packet as paper acceptance.
- Do not force unknown claims into near-looking templates.

For a copy-paste prompt and CSV header, see
`artifact/LLM_ASSISTED_REVIEW_QUICKSTART_20260527.md`.
