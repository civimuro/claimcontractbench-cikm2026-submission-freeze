# Phase 1 Claim-Span Gold Readout

Status: `PASS`.
Recommendation: `USE_AS_ADAPTER_OPPORTUNITY_AND_BOUNDARY_EVIDENCE`.

This readout explains what the adjudicated gold supports after joining it back to the manifest. It is an interpretation layer, not a new annotation pass.

## Key Numbers

| Metric | Value |
| --- | ---: |
| rows | 80 |
| papers | 37 |
| source families | 21 |
| needs-adapter rows | 62 |
| adapter evidence present rows | 60 |
| adapter evidence present rate | 0.968 |
| do-not-call rows | 18 |
| do-not-call rows upgraded to yes | 0 |
| direct registered-template rows | 0 |
| raw A/B quality gate failed checks | 4 |
| raw adjudication candidate rows | 76 |
| non-consensus adjudication decision rows | 70 |

## Counts

- route counts: `{'NEEDS_TEMPLATE_ADMISSION': 62, 'OUT_OF_SCOPE_DO_NOT_CALL': 18}`
- post-admission action counts: `{'ACCEPT': 22, 'OUT_OF_SCOPE': 18, 'REWRITE': 18, 'SUPPORT_ONLY': 2, 'SUPPRESS': 8, 'WEAKEN': 12}`
- localization class counts: `{'adapter_claim_not_localized': 2, 'adapter_evidence_present': 60, 'do_not_call_boundary_cue_present': 7, 'do_not_call_boundary_not_localized': 11}`
- paper-facing role counts: `{'adapter_boundary_or_weakening_candidate': 38, 'adapter_gap_or_recheck_candidate': 2, 'boundary_stop_evidence': 7, 'boundary_stop_no_claim_span': 11, 'clean_adapter_accept_candidate': 17, 'partial_adapter_accept_candidate': 5}`

## Checks

| Check | Status | Evidence |
| --- | --- | --- |
| F1CSREAD-01 manifest and locked gold join exactly | PASS | manifest=80; locked=80; joined=80 |
| F1CSREAD-02 adjudicated closeout is locked | PASS | status=PASS; locked_rows=80 |
| F1CSREAD-03 adapter rows usually have localizable evidence | PASS | adapter_localized=60/62; rate=0.968 |
| F1CSREAD-04 direct registered-template coverage remains zero | PASS | direct_rows=0 |
| F1CSREAD-05 do-not-call rows are not upgraded to positive support | PASS | stop_rows=18; stop_yes=0 |
| F1CSREAD-06 source-family breadth preserved | PASS | source_families=21 |
| F1CSREAD-07 private-marker hygiene | PASS | no private markers in readout rows |
| F1CSREAD-08 raw A/B limitation carried into readout | PASS | raw_failed_checks=4; raw_candidates=76; non_consensus_decisions=70 |

## Interpretation

The result supports a narrow but valuable claim: in the selected public-safe paper-claim assets, many rows contain localizable claim-governance opportunities, but almost all relevant rows require adapter admission rather than direct execution by the current registered templates. Because the raw A/B quality gate failed and most candidate rows needed adjudication, the current tool should be presented as a claim-governance backend plus admission protocol, not as a universal full-paper reviewer or strong automatic extraction system.
