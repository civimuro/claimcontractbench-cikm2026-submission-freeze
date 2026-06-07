# V3.4 Prospective Real-Paper Adapter Validation Closeout

Date: 2026-06-05

Status: `CLOSED_POSITIVE_BOUNDED`

## What V3.4 Was Designed To Answer

Earlier template work left a serious concern:

> do the admitted templates only work on internally curated examples, or can
> they process fresh, public, real-paper claim rows in a source-traceable way?

V3.4 answers that concern with a prospective held-out run. The R4 two-step
taxonomy was frozen first, then new public-paper sources were selected, cached,
extracted, adjudicated, and routed.

## Evidence Chain

### 1. Fresh Source Selection

- 18 fresh public arXiv papers.
- 6 per admitted family:
  - `llm_evaluation`;
  - `resource_documentation`;
  - `uncertainty_calibration`.
- Prior V1/V2/V3/V3.1/V3.2/V3.3 arXiv IDs were excluded.
- 9 reserve sources were retained.

### 2. Source Cache

- PDF download and layout text extraction: 18/18 pass.
- Raw-order text extraction: 18/18 pass.
- Full PDFs/text remain local experiment cache only; public artifacts should
  use URLs, short spans, and hashes.

### 3. Claim Extraction

- Three family-specific source-only extraction channels.
- 72 candidate claims, exactly 4 per paper.
- Curated extraction guard: PASS, 0 hard issues.
- Repair log preserved four source-span traceability repairs.

### 4. Source-Only Proxy Gold

- A/B independent gold:
  - action agreement: 67/72 (`0.931`);
  - emit-worthiness agreement: 72/72 (`1.000`);
  - release-side agreement: 72/72 (`1.000`);
  - C-resolution rows: 9.
- Locked source-only gold guard: PASS, 0 issues.

Locked gold action distribution:

| Action | Count |
| --- | ---: |
| `ACCEPT` | 62 |
| `REWRITE` | 8 |
| `SUPPORT_ONLY` | 2 |
| `WEAKEN` | 0 |
| `SUPPRESS` | 0 |
| `REJECT_OR_OUT_OF_SCOPE` | 0 |
| `NEEDS_TEMPLATE_ADMISSION` | 0 |

This distribution matters: V3.4 is a **fresh-source positive usability
validation**, not a hard-boundary stress test.

## Router Results

Six router channels were run and guarded:

| Condition | Action accuracy | Emit accuracy | Release-side accuracy | Dangerous false release | Macro-F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| `R0_A` | `0.958` | `NA` | `1.000` | 0 | `0.925` |
| `R0_B` | `0.944` | `NA` | `1.000` | 0 | `0.894` |
| `R1_A` | `0.917` | `NA` | `0.972` | 1 | `0.851` |
| `R1_B` | `0.917` | `NA` | `1.000` | 0 | `0.873` |
| `R4_A` | `0.972` | `1.000` | `1.000` | 0 | `0.947` |
| `R4_B` | `0.958` | `1.000` | `1.000` | 0 | `0.925` |

Family-level R4 results:

| Condition | Family | Action accuracy | Release-side accuracy | Dangerous false release |
| --- | --- | ---: | ---: | ---: |
| `R4_A` | `llm_evaluation` | `0.958` | `1.000` | 0 |
| `R4_A` | `resource_documentation` | `1.000` | `1.000` | 0 |
| `R4_A` | `uncertainty_calibration` | `0.958` | `1.000` | 0 |
| `R4_B` | `llm_evaluation` | `0.917` | `1.000` | 0 |
| `R4_B` | `resource_documentation` | `1.000` | `1.000` | 0 |
| `R4_B` | `uncertainty_calibration` | `0.958` | `1.000` | 0 |

## What The Result Means

V3.4 is a positive result.

It supports:

- admitted template families can process fresh public-paper candidate claims;
- fresh real-paper claims can be extracted into source-traceable passport rows;
- source-only proxy-gold is stable at the release/nonrelease level;
- the R4 two-step taxonomy achieves strong action accuracy and perfect
  release-side accuracy on this fresh-source positive set;
- R4 gives an explicit emit-worthiness field, which directly addresses the
  V3.3 diagnosis that soft boundaries need a first-stage emit decision.

It is especially important because it closes the earlier gap where public-paper
probe evidence mostly showed template-admission failures. V3.4 shows a positive
counterpart: once a domain is admitted and a template exists, real public-paper
claim rows can be handled cleanly.

## What The Result Does Not Mean

V3.4 does not support:

- automatic full-paper claim discovery;
- broad coverage across all empirical ML papers;
- human expert gold quality;
- human reviewer efficiency improvement;
- zero-risk deployment as an automatic reviewer;
- hard forbidden-force robustness by itself.

The last point is crucial. V3.4 has no locked-gold `SUPPRESS` rows because fresh
natural claim extraction mostly yielded supportable author claims. Hard-boundary
stress claims must therefore continue to rely on V3.1/V3.2 rather than V3.4.

## Relation To The Full Evidence Program

The clean interpretation is layered:

1. **V1.8** checks whether admitted template families can be specified and
   independently applied.
2. **V3/V3.4** show real public-paper positive adapter usability.
3. **V3.1/V3.2** test hard-boundary overclaim suppression.
4. **V3.3** diagnoses soft action-boundary ambiguity.
5. **V3.4 R4** prospectively validates a frozen two-step taxonomy on fresh
   real-paper rows.

Together, these support this paper-safe claim:

> ClaimContractBench provides admitted template families and a claim-licensing
> router that can process source-traceable public-paper candidate claims under
> bounded templates, while preserving explicit admission and stress-test
> boundaries outside the supported scope.

## Paper-Integration Recommendation

Use V3.4 as the main answer to the earlier “no real positive use case” concern.
Do not replace the hard-boundary evidence with V3.4. Present it as a new
prospective positive adapter validation:

- 18 fresh public papers;
- 72 source-traceable candidate claims;
- A/B/C source-only proxy gold;
- R4 action accuracy 69-70/72;
- R4 release-side accuracy 72/72;
- R4 dangerous false release 0/72.

Then immediately state the limit:

> Because the fresh natural rows contain few hard-forbidden claims, hard
> overclaim suppression is evaluated separately in the boundary-stress suite.

