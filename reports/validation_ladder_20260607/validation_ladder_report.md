# Validation Ladder Report

Status: `PASS`

This report connects paper-facing validation numbers to public-safe files in the frozen release. It is not a human-utility study and not an automatic peer-review claim.

## Ladder Summary

| Rung | What is checked | Main signal | Limit |
| --- | --- | --- | --- |
| Template-rule stress | 42-row blind LLM-proxy packet | A/B action kappa `1.000`, dangerous false releases A/B `0`/`0` | LLM-proxy only, not human-independent reliability. |
| Positive real-paper use | 18 public papers / 72 supplied claims under admitted templates | R4_A action `70/72`, R4_B action `69/72`, 0 dangerous false releases | Positive packet, not hard robustness. |
| Boundary replay | Same 18-paper / 72-claim surface with harder reportability gates | safety `0.958`, action/gate `0.806`, unsafe false releases `3` | Supplied claims only, not full-paper claim discovery. |

## Checks

| Check | Status | Evidence |
| --- | --- | --- |
| VL-00 validation ladder files are public-safety scanned | PASS | issues=0 |
| VL-01 template stress row ids align | PASS | rows=42 |
| VL-02 template stress recomputed metrics match stored summary | PASS | recomputed_kappa=1.000; stored_kappa=1.000 |
| VL-03-R4_A positive real-paper R4_A recomputes aggregate metrics | PASS | action=70/72; release=72/72; dangerous=0 |
| VL-03-R4_B positive real-paper R4_B recomputes aggregate metrics | PASS | action=69/72; release=72/72; dangerous=0 |
| VL-03-RERUN-IDS positive real-paper rerun packet aligns with locked reference | PASS | candidates=72 reference=72 |
| VL-03-RERUN-SOURCES positive real-paper source pool covers rerun packet sources | PASS | selected_sources=18 source_pool=27 |
| VL-04 boundary replay candidate and reference row ids align | PASS | candidates=72 reference=72 |
| VL-05 boundary replay exposes remaining unsafe false releases | PASS | unsafe_false_releases=3 |

## Files To Inspect

- `artifact/validation_ladder_20260607/template_rule_stress_*.csv/json`: blind packet, A/B/C outputs, and stored template-rule-stress summary.
- `artifact/validation_ladder_20260607/positive_realpaper_*.csv/json/md`: positive public-paper run rows, aggregate scores, and baseline caveat.
- `artifact/real_paper_review_candidate_claims_v318b_20260606.csv` and `artifact/real_paper_review_reference_outcomes_v318b_20260606.csv`: current boundary replay packet and outcomes.
- `docs/VALIDATION_RERUN_PACKETS.md`: fresh-rerun protocols for rerunning the first two rungs without seeing reference labels first.

## Replay Versus Rerun

This command performs exact frozen replay: it recomputes metrics from repository files. Fresh LLM reruns are different. They should use the rerun protocols and are scored afterward with `score-rerun`; new LLM outputs are stability probes, not guaranteed identical reproductions.

## Safe Interpretation

The release supports the narrow statement that admitted claim-template rules can be inspected and replayed on supplied candidate rows, including a positive public-paper packet and a harder boundary packet. It does not support claims of autonomous paper review, automatic claim discovery, human reviewer utility, broad empirical-ML coverage, or zero-risk release.
