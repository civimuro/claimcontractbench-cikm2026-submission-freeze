# Claim Identification

ClaimContractBench does not automatically find every claim in a paper.

It checks supplied candidate claims. A human or an LLM must first identify
candidate empirical claims and put them into a packet. This is the main
difference between the human path and the LLM-assisted path.

## What Counts As A Candidate Claim

A useful candidate claim usually says something empirical about:

- a benchmark or evaluation result;
- a metric comparison;
- a resource, dataset, schema, release, or metadata record;
- calibration, uncertainty, conformal, or probabilistic support;
- a bounded decision or reporting context.

Good candidate claims are sentences that could become too strong if the metric,
source excerpt, or context is read too broadly.

Do not send these to the claim runner as ordinary metric-to-claim rows:

- proof correctness;
- novelty priority;
- implementation bugs;
- ethics approval;
- legal clearance;
- deployment approval;
- paper acceptance or rejection;
- general scientific truth without a registered evidence template.

Those should be marked `OUT_OF_SCOPE_DO_NOT_CALL` or handled outside this
resource.

## Human Path

The human path is manual but transparent.

1. Choose a paper section, paragraph, table, or abstract.
2. Highlight candidate empirical claims.
3. Decide whether each claim fits a registered family exactly.
4. Fill a packet with one row per candidate claim.
5. Run the deterministic checker.

Useful commands:

```bash
python3 src/claimcontractbench.py templates
python3 src/claimcontractbench.py init-packet --output claim_packets/my_claim_packet.csv
python3 src/claimcontractbench.py review --input claim_packets/my_claim_packet.csv
```

Use this path when confidentiality matters, when you do not want an LLM to read
the paper, or when a reviewer wants to inspect a small number of important
claims directly.

Main limitation: the tool only checks the claims the human selected. It does not
prove full-paper coverage.

## LLM-Assisted Path

The LLM path reduces manual work but needs stricter boundaries.

1. Give the LLM the allowed paper text or excerpt only if policy allows it.
2. Give the LLM the registered template families and route labels.
3. Ask it to extract candidate empirical claims and route them into the packet.
4. Run the deterministic checker.
5. Review the output; the LLM is not the licensing authority.

Useful commands:

```bash
python3 src/claimcontractbench.py try-llm
python3 src/claimcontractbench.py init-packet --output claim_packets/my_claim_packet.csv
python3 src/claimcontractbench.py review --input claim_packets/my_claim_packet.csv
```

For the fixed public-paper demo, `try-llm` creates a clean packet with supplied
candidate claims. For a new paper, the LLM must perform the extraction step
from user-provided text.

Main limitation: LLM extraction can miss claims, over-select background text, or
force a nearby template. When uncertain, route to `NEEDS_TEMPLATE_ADMISSION` or
`OUT_OF_SCOPE_DO_NOT_CALL`.

## Current Supported Families

Current registered practical families:

- `llm_evaluation`
- `resource_documentation`
- `uncertainty_calibration`

For all other domains, do not force a match. Use template admission:

```bash
python3 src/claimcontractbench.py admission-guide
```

## Safe Claim About The Tool

Safe:

> Given selected candidate claims and registered templates, the tool exposes
> which rows are licensed, weakened, rewritten, support-only, suppressed,
> admission-needed, or out of scope.

Not safe:

> The tool automatically finds all claims in a paper or performs complete
> review by itself.
