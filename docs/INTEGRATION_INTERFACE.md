# Integration Interface

This page defines the stable public interface for collaborators who want to
call ClaimContractBench from another review tool.

The interface has two independent layers:

- core claim review, which is always available;
- optional Codex proof audit, which can be ignored by integrations that only
  need empirical metric-to-claim checking.

The machine-readable version is:

```bash
python3 src/claimcontractbench.py integration-interface
```

or directly:

```text
artifact/integration_interface_20260528.json
```

## Core Claim Review

Use this layer for empirical paper claims, metric evidence, benchmark
interpretation, and template routing.

Recommended integration flow:

```bash
python3 src/claimcontractbench.py doctor
python3 src/claimcontractbench.py smoke
python3 src/claimcontractbench.py templates
python3 src/claimcontractbench.py init-packet --output claim_packets/my_claim_packet.csv
python3 src/claimcontractbench.py review \
  --input claim_packets/my_claim_packet.csv \
  --output reports/my_claim_packet
```

The packet schema is:

```text
artifact/llm_claim_review_packet_template_20260527.csv
```

The accepted route labels are:

- `CALL_REGISTERED_TEMPLATE`;
- `NEEDS_TEMPLATE_ADMISSION`;
- `OUT_OF_SCOPE_DO_NOT_CALL`.

Integrations should treat the deterministic report as a routing and boundary
check, not as an autonomous review verdict.

## Optional Proof Audit

Use this layer only when the upstream tool explicitly wants theorem, proof,
lower-bound, or rate-chain rigor review.

```bash
python3 src/claimcontractbench.py proof-audit-guide
python3 src/claimcontractbench.py init-proof-audit --output proof_audits/my_proof_audit.md
```

The proof-audit path is Codex-only in this repository. It provides a local
workflow guide, a gap checklist, and a Markdown scaffold. It does not extend the
metric-to-claim license and it does not produce paper acceptance decisions.

An integration can safely ignore the `proof_audit` capability in the JSON
interface. Core claim review remains valid without it.

## Contract For Tool Builders

Minimal consumer pattern:

```python
import json
import subprocess

interface = json.loads(
    subprocess.check_output(
        ["python3", "src/claimcontractbench.py", "integration-interface"],
        text=True,
    )
)

claim_review = interface["capabilities"]["claim_review"]
proof_audit = interface["capabilities"]["proof_audit"]

if proof_audit["available"] and user_requested_proof_audit:
    subprocess.run(proof_audit["commands"]["guide"].split(), check=True)
else:
    subprocess.run(claim_review["commands"]["smoke"].split(), check=True)
```

Callers should:

- run `doctor` before trusting a checkout;
- run `smoke` in continuous integration or before a release handoff;
- generate claim packets under ignored local folders such as `claim_packets/`;
- write generated reports under ignored local folders such as `reports/`;
- keep confidential manuscript text out of public issues, commits, and release
  artifacts;
- route theorem and proof claims to `OUT_OF_SCOPE_DO_NOT_CALL` unless the
  optional proof-audit layer is intentionally invoked.

Callers should not:

- force a near-match claim into `CALL_REGISTERED_TEMPLATE`;
- treat proof-audit notes as formal verification;
- publish private paper text or local reviewer notes through generated reports;
- require proof audit when their product only needs empirical claim review.
