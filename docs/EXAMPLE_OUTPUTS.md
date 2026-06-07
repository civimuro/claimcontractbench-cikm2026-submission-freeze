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
rows: 151
required_files: 151
public_safe_rows: 151
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
positive_checks: 15
negative_fail_closed_checks: 5
```

Meaning:

- positive public paths run;
- the three-family real-paper demo runs;
- the human guide and one-shot agent guide are reachable;
- bad packets fail closed rather than silently producing licensed claims.

## Real-Paper Template Review Demo

Command:

```bash
python3 src/claimcontractbench.py realpaper-demo \
  --output /tmp/claimcontractbench_realpaper_demo
```

Expected high-level output:

```text
PASS real-paper review demo
rows: 72
source_papers: 18
conservative_candidate_safety_accuracy: 0.958
conservative_display_action_accuracy: 0.806
conservative_unsafe_false_releases: 3
```

Meaning:

- three validated families are available for trial use;
- 18 public source papers and 72 supplied candidate claims are included;
- the conservative replay blocks most unsafe releases but still leaves three
  unsafe releases, concentrated in uncertainty-calibration background/support
  rows;
- this is a bounded claim-review demo, not automatic full-paper review.

## Validation Ladder

Command:

```bash
python3 src/claimcontractbench.py validation-ladder \
  --output /tmp/claimcontractbench_validation_ladder
```

Expected high-level output:

```text
PASS validation ladder
template_rule_stress_rows: 42
template_rule_stress_A_B_action_kappa: 1.000
positive_realpaper_use:
- R4_A: action_accuracy=70/72 release_side=72/72 dangerous_false_release=0
- R4_B: action_accuracy=69/72 release_side=72/72 dangerous_false_release=0
boundary_replay: safety=0.958 action=0.806 unsafe_false_releases=3
```

Meaning:

- the template-rule stress numbers are recomputed from public-safe blind rows
  and proxy outputs;
- the positive real-paper use numbers are recomputed from row-level score
  files;
- the boundary replay exposes remaining unsafe releases instead of hiding them;
- this is not a human-utility study or autonomous full-paper review.

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
