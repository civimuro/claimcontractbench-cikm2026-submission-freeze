# ClaimContractBench Trial Feedback

## Consent And Source Boundary

- Intended sharing target: public / private / local-only
- Materials inspected:
- Materials intentionally excluded:
- Public-safe confirmation: no confidential paper text, private review notes,
  author identities, unpublished results, raw data, credentials, private links,
  or local absolute paths are included.
- If any confidential material is needed for your own record, keep it in a
  separate private/local note and do not submit that note publicly.

## Trial Setup

- User role:
- AI assistant or model used, if shareable:
- Operating system:
- Commands attempted:
- Tool version or commit, if known:

## Task Type

- Paper or excerpt type:
- Main empirical claim type:
- Public-safe abstraction used instead of verbatim paper text:
- Was the task expected to match an existing template? yes / no / unsure

## Time To First Useful Report

- Under 5 minutes / under 15 minutes / longer:
- Main cause of delay:

## Packet Quality

- CSV valid on first try: yes / no
- Repair needed:
- Was `human_check_required` set correctly?

## Routing Behavior

- `CALL_REGISTERED_TEMPLATE` rows:
- `NEEDS_TEMPLATE_ADMISSION` rows:
- `OUT_OF_SCOPE_DO_NOT_CALL` rows:
- Possible overconfident template calls:
- Possible missed registered-template calls:

## Useful Tool Outputs

- Most useful action labels:
- Most useful report sections:
- Did the output suggest a concrete claim rewrite? yes / no
- If yes, describe the rewrite pattern abstractly; do not paste confidential
  manuscript text.

## Missing Template Families

- Missing domain or template family:
- Candidate evidence unit needed:
- Candidate forbidden claim:
- Public-safe example or paraphrase:
- Should this be mainline, support-only, boundary-probe, or rejected?

## Confusing Terms Or Steps

- Confusing command:
- Confusing CSV field:
- Confusing report label:
- Documentation gap:

## Reliability Concerns

- Too permissive case:
- Too suppressive case:
- LLM dependence issue:
- Privacy or review-policy issue:
- Did you use an external LLM on confidential material? no / yes, approved
  private workflow / yes, not approved and should not be repeated

## Suggested Improvements

- Documentation:
- CLI:
- Template coverage:
- Report format:
- Examples:

## Overall Utility

Choose one:

- useful now
- useful with minor fixes
- useful only for experts
- not useful for this task

Brief reason:

## Pre-Share Check

Before sharing this report publicly, run:

```bash
python3 src/claimcontractbench.py check-feedback --input feedback/my_feedback_report.md
```

Then manually re-read the report. The check is heuristic and cannot guarantee
that all confidential manuscript content has been removed.
