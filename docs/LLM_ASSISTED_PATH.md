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

If you want the cleanest fixed public-paper trial, start with:

```bash
python3 src/claimcontractbench.py try-llm
```

This copies only candidate claims, template cards, the LLM prompt, and
`docs/LLM_CONTEXT.md` into `/tmp/claimcontractbench_llm_trial`. It deliberately
does not copy gold/reference outcomes or generated reports.

For a custom paper packet, use:

```bash
python3 src/claimcontractbench.py templates
python3 src/claimcontractbench.py init-packet --output claim_packets/my_claim_packet.csv
```

Ask the LLM to fill the packet with one candidate claim per row. Then run:

```bash
python3 src/claimcontractbench.py review --input claim_packets/my_claim_packet.csv
```

## Real-Paper Demo Workflow

If you want to test an LLM on a fixed public-paper packet instead of drafting a
new packet, use:

```bash
python3 src/claimcontractbench.py realpaper-demo \
  --output /tmp/claimcontractbench_realpaper_demo
```

To score an LLM adjudication, give the LLM only:

- `artifact/real_paper_review_candidate_claims_v318b_20260606.csv`
- `artifact/real_paper_review_template_cards_v18_20260606.csv`
- `artifact/real_paper_review_llm_prompt_20260606.md`

Do not give the LLM the reference-outcome file, generated reports, or previous
run outputs during the run. Save the returned CSV and score it:

```bash
python3 src/claimcontractbench.py realpaper-demo \
  --adjudication path/to/llm_output.csv \
  --output /tmp/claimcontractbench_realpaper_llm_score
```

This evaluates supplied candidate claims in three registered families. It does
not test full-paper claim discovery.

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

For the fixed public-paper demo prompt, see
`artifact/real_paper_review_llm_prompt_20260606.md`.
