# Advanced Evaluation Source Inventory

This document is for reviewers and advanced users who want to inspect the
public-paper evaluation surfaces behind the release. It is not part of the
ten-minute first-use path. Most users can run `doctor`, `smoke`, and the packet
review commands without reading this file.

## What This Inventory Is For

ClaimContractBench is tested on public, public-safe evaluation surfaces that
exercise fail-closed routing, template-admission boundaries, selected-excerpt
decisions, and claim-span localization limits. These materials help reviewers
check that the tool is more than a README convention.

The inventory does not create an official peer-review dataset, does not claim
human reviewer utility, and does not prove autonomous full-paper review.

## Public Source Policy

The release keeps public-source simulations low risk:

- it records source identifiers, titles, public URLs, source families, short
  public-safe anchors, paraphrased candidate claims, labels, and aggregate
  metrics;
- it does not redistribute PDFs, source files, raw third-party datasets, long
  full-text excerpts, private manuscripts, or confidential review material;
- source-provider terms and each paper's license remain authoritative outside
  this repository;
- arXiv or other public-preprint sources should be cited by URL or identifier,
  and any future expansion should record license/version metadata before
  adding rows;
- outputs should be described as public-preprint or public-paper
  claim-audit simulations, not as official peer review.

## Advanced Evidence Surfaces

| Surface | Where to inspect | Scale | What it supports | What it does not support |
| --- | --- | ---: | --- | --- |
| Paper-claim gold benchmark | `artifact/paper_claim_gold_benchmark_sources_20260521.csv`, `artifact/paper_claim_gold_benchmark_cases_20260521.csv`, `src/run_paper_claim_gold_benchmark.py`, `reports/paper_claim_gold_benchmark_20260521/` | 40 public source papers, 120 paraphrased external claim rows, 8 controls, 128 total rows | fail-closed routing and unsupported-template boundary over public-paper claim rows | full-paper extraction, template discovery, or autonomous review |
| Paper-excerpt decision surface | `artifact/paper_excerpt_reviewer_value_cases_20260521.csv`, `src/run_paper_excerpt_reviewer_value_benchmark.py`, `reports/paper_excerpt_reviewer_value_benchmark_20260521/` | 80 selected external excerpt rows, 8 controls, 40 source papers, 22 source families | source-anchored selected-excerpt decisions once a route is supplied | human-review utility, full-PDF parsing, or acceptance advice |
| Fulltext-adjacent claim-span readout | `reports/frontend_fulltext_phase1_claim_span_gold_readout_20260523/`, `reports/frontend_fulltext_phase1_claim_span_strict_agreement_20260523/` | 80 adjudicated rows, 37 papers, 21 source families | adapter/boundary opportunities and localization limitations | reliable automatic extraction or full-paper recall |
| Controlled adapter admission case study | `reports/claim_span_adapter_admission_case_study_20260523/` | 6 adapter specs and 22 passport rows across three selected families | structural admission behavior and protected false-release checks | cross-domain validation |
| Annotation agreement scaffold | `artifact/paper_claim_gold_benchmark_blind_annotation_packet_20260521.csv`, `src/run_paper_claim_annotation_agreement.py` | 128 blind annotation rows, currently pending second annotator | readiness for future independent agreement measurement | existing inter-annotator agreement |
| Reviewer-demo regression | `src/run_reviewer_audit_demo.py`, `src/run_reviewer_audit_demo_regression.py`, `reports/reviewer_facing_audit_demo_20260521/` | 72 public-safe cards | fail-closed reviewer-facing route/card generation after supplied candidate rows | production reviewer study |
| Real-paper template review addendum | `docs/REAL_PAPER_REVIEW_DEMO.md`, `artifact/real_paper_review_candidate_claims_v318b_20260606.csv`, `artifact/real_paper_review_reference_outcomes_v318b_20260606.csv`, `src/run_real_paper_review_demo.py`, `reports/real_paper_review_demo_20260606/` | 18 public arXiv papers, 72 supplied candidate claims, 3 validated template families | reviewer-reproducible trial of registered templates on supplied real-paper candidate claims, with residual unsafe-release boundaries exposed | automatic full-paper extraction, broad template coverage, zero-risk release, or human-utility measurement |

## Source Mix

The current public-paper surfaces include model-reporting,
dataset-documentation, distribution-shift, benchmark-validity, calibration,
uncertainty, selective-prediction, conformal-prediction, LLM-evaluation,
behavioral-testing, LLM peer-review/security, resource-documentation, and
uncertainty-calibration families.

The larger paper-claim and excerpt surfaces use 40 external public source
papers. Their source manifest includes arXiv pages, ACL Anthology pages, PMLR,
NeurIPS/papers pages, GitHub project pages, and one JAMA Network page. The
repository stores links and public-safe derived rows rather than the papers
themselves.

The real-paper template review addendum uses 18 public arXiv papers: 6
LLM-evaluation papers, 6 resource-documentation papers, and 6
uncertainty-calibration papers. It stores source URLs, section locators, short
source-span excerpts, candidate claims, template cards, reference outcomes, and
public-safe replay summaries. It does not store PDFs or full-paper text.

## How Reviewers Should Read These Files

Use the surfaces as advanced evidence for these bounded questions:

1. Does the release fail closed when a public-paper claim family is not yet
   admitted?
2. Does the tool separate registered-template controls, adapter-needed claims,
   and out-of-scope claims?
3. Do selected public-paper rows reveal adapter opportunities without silently
   expanding the current template registry?
4. Do the claim-span agreement/readout files honestly expose localization
   difficulty rather than hiding it?
5. Can three validated templates process supplied real-paper candidate claims
   while exposing residual unsafe-release boundaries?

Do not use these files to claim:

- the tool can autonomously review arbitrary papers;
- the tool improves human reviewer speed or quality;
- every empirical ML paper is covered by the current templates;
- arXiv or any source provider endorses the tool;
- the repository redistributes complete third-party papers.

## Future Expansion Rule

A future public-preprint evaluation pack should add rows only when it can record
source URL or identifier, version date, source family, license/posture, public-
safe claim text or paraphrase, route label, and boundary rationale. Full papers
or long excerpts should stay outside the repository unless the individual
license clearly permits redistribution.
