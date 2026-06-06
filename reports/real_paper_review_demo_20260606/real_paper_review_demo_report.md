# Real-Paper Template Review Demo

Status: generated from public-safe ClaimContractBench assets.

## What This Demonstrates

This demo applies three V1.8-backed claim-template families to supplied candidate claims from public arXiv papers: `llm_evaluation`, `resource_documentation`, and `uncertainty_calibration`. It checks a candidate claim against a short source excerpt and returns whether the claim can be released as written, weakened, rewritten, kept as support-only, blocked with a suggested correction, or suppressed.

It is not automatic full-paper review, full-paper claim discovery, or a human-utility study.

## Summary

| Item | Value |
| --- | ---: |
| rows | 72 |
| source_papers | 18 |
| conservative_candidate_safety_accuracy | 0.9583333333333334 |
| conservative_display_action_accuracy | 0.8055555555555556 |
| conservative_gate_accuracy | 0.8055555555555556 |
| conservative_unsafe_false_releases | 3 |

## Family Counts

| Family | Rows |
| --- | ---: |
| llm_evaluation | 24 |
| resource_documentation | 24 |
| uncertainty_calibration | 24 |

## Checks

| Check | Status | Evidence |
| --- | --- | --- |
| RP-001 candidate columns | PASS | 11 columns include required candidate fields |
| RP-002 template families | PASS | three V1.8-backed template families are present |
| RP-003 row alignment | PASS | 72 candidate rows join to reference outcomes |
| RP-004 family balance | PASS | 24 rows in each of three families |
| RP-005 source balance | PASS | 18 public-paper source ids |
| RP-006 public-safe content scan | PASS | no private path, private scoring marker, connector host, or credential-like text found |
| RP-006B reference outcome enum values | PASS | reference and conservative outcomes are inside the public prompt contract |

## Example Rows

| Row | Family | Reference | Conservative | Claim |
| --- | --- | --- | --- | --- |
| V317B-LLM-001 | llm_evaluation | ACCEPT / yes | ACCEPT / yes | The paper introduces Benchmark Agent as a fully autonomous agentic system for benchmark building. |
| V317B-LLM-002 | llm_evaluation | WEAKEN / no | WEAKEN / no | Benchmark Agent's generated benchmarks are broadly validated as high quality across benchmark types. |
| V317B-LLM-003 | llm_evaluation | WEAKEN / no | WEAKEN / no | The generated benchmarks show consistent scaling trends for all evaluated model families across every benchma... |
| V317B-LLM-004 | llm_evaluation | SUPPORT_ONLY / no | SUPPORT_ONLY / no | Rapid benchmark refresh for emerging models, new domains, and changing user needs is a design context for Ben... |
| V317B-LLM-005 | llm_evaluation | ACCEPT / yes | ACCEPT / yes | TeleSWEBench consists of 734 questions with executable unit tests. |
| V317B-LLM-006 | llm_evaluation | WEAKEN / no | WEAKEN / no | TeleSWEBench establishes a 25% success-rate ceiling for autonomous software engineering frameworks in telecom. |
| V317B-LLM-007 | llm_evaluation | BLOCK_AND_SUGGEST / no | BLOCK_AND_SUGGEST / no | TeleSWEBench evaluates only final functional correctness and does not separately test localization ability. |
| V317B-LLM-008 | llm_evaluation | SUPPRESS / no | SUPPRESS / no | TeleSWEBench proves telecom software agents are ready for production deployment. |
| V317B-LLM-009 | llm_evaluation | ACCEPT / yes | ACCEPT / yes | SenseJudge is reported to score 70.66 overall on LLM-as-a-Personalized-Judge and outperform compared baseline... |
| V317B-LLM-010 | llm_evaluation | WEAKEN / no | BLOCK_AND_SUGGEST / no | SenseJudge matches or surpasses reward models on RewardBench without training. |
| V317B-LLM-011 | llm_evaluation | BLOCK_AND_SUGGEST / no | BLOCK_AND_SUGGEST / no | SenseBench was built from single-turn synthetic prompts rather than real-world multi-turn interactions. |
| V317B-LLM-012 | llm_evaluation | SUPPORT_ONLY / no | SUPPORT_ONLY / no | SenseBench's coverage of eight common topics gives background context for interpreting SenseJudge evaluations. |

## Important Limit

The included reference outcomes are diagnostic labels for supplied candidate claims, not a claim that arbitrary papers can be reviewed automatically. The most important residual failure mode is unsafe release around uncertainty-calibration background/support-only rows.
