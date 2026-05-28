# Example Outputs

This file explains the shortest outputs a reviewer is likely to see.

## Release Surface

Command:

```bash
python3 src/claimcontractbench.py doctor
```

Expected high-level output:

```text
PASS release surface validation
rows: 102
required_files: 102
public_safe_rows: 102
raw_data_rows: 0
```

Meaning:

- every required release file exists;
- the manifest has only release-root-relative paths;
- no manifest row is raw data;
- all manifest rows are public-safe;
- CSV and JSON files parse;
- the claim-passport casebook matches the public schema and joins to dataset
  and scenario manifests.

## Smoke Suite

Command:

```bash
python3 src/claimcontractbench.py smoke
```

Expected high-level output:

```text
PASS release smoke suite
positive_checks: 11
negative_fail_closed_checks: 4
```

Meaning:

- positive public paths run;
- the human guide and one-shot agent guide are reachable;
- the integration interface is reachable;
- the Codex proof-audit guide and local scaffold are reachable;
- bad packets fail closed rather than silently producing licensed claims.

## Integration Interface

Command:

```bash
python3 src/claimcontractbench.py integration-interface
```

Expected high-level output:

```text
"interface_id": "claimcontractbench_public_integration_20260528"
"claim_review"
"proof_audit"
```

Meaning:

- external tools can discover the command surface without reading prose docs;
- `claim_review` is the required deterministic layer;
- `proof_audit` is optional and can be ignored by tools that only handle
  empirical metric-to-claim checks.

## Codex Proof Audit Scaffold

Command:

```bash
python3 src/claimcontractbench.py init-proof-audit --output proof_audits/my_proof_audit.md
```

Expected high-level output:

```text
PASS init proof audit
```

Meaning:

- the release can create a local Markdown draft for theorem or proof rigor
  review;
- the proof-audit path remains separate from metric-to-claim licensing;
- the generated `proof_audits/` directory is ignored by git.

## Registered Templates

Command:

```bash
python3 src/claimcontractbench.py templates
```

What to look for:

- 5 mainline template rows;
- 3 support-only rows;
- 1 rejected boundary probe;
- clear forbidden-claim language.

The template list is intentionally small. New papers should not be squeezed
into it unless the match is exact.

## LLM Packet Example

Command:

```bash
python3 src/claimcontractbench.py review \
  --input artifact/llm_claim_review_packet_template_20260527.csv
```

Expected high-level output:

```text
PASS LLM claim review packet
packet_rows: 4
call_registered_template: 2
needs_template_admission: 1
out_of_scope: 1
unsafe_release_rate: 0.000
checks_passed: 14
checks_failed: 0
```

Meaning:

- two rows safely call registered templates;
- one relevant row requires template admission;
- one row is out of scope;
- no unsafe release is produced.

## Template Admission Example

Command:

```bash
python3 src/run_claim_template_admission.py --output reports/claim_template_admission_20260521
```

Expected high-level output:

```text
PASS claim template admission
templates: 9
admitted_mainline: 5
admitted_support_only: 3
rejected: 1
checks_passed: 10
checks_failed: 0
```

Meaning:

- the current catalog admits only templates with a typed contract;
- support-only rows are separated from mainline claims;
- patchwork or incomplete claims are rejected.
