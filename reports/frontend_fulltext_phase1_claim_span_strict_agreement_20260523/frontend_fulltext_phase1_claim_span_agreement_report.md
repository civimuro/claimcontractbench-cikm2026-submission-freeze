# Front-End Full-Text Phase 1 Claim-Span Agreement

Status: COMPLETE.

## Summary

| Metric | Value |
| --- | ---: |
| rows | 80 |
| annotator A filled rows | 80 |
| annotator B filled rows | 80 |
| paired completed rows | 80 |
| span-found agreement | 0.850 |
| match-type agreement | 0.600 |
| section exact agreement | 0.237 |
| span exact agreement | 0.087 |
| span overlap pairs | 61 |
| mean span-token Jaccard | 0.276 |
| span-token Jaccard >= 0.5 | 0.230 |
| mean span-token containment | 0.382 |
| span-token containment >= 0.8 | 0.262 |
| adjudication candidate rows | 76 |
| reliability metrics available | yes |

## Checks

| Check | Status | Evidence |
| --- | --- | --- |
| F1CSA-01 row joins | PASS | gold=80; a=80; b=80 |
| F1CSA-02 annotation completeness | PASS | filled_a=80; filled_b=80; required=True |
| F1CSA-03 valid annotation values | PASS | invalid_a=0; invalid_b=0 |
| F1CSA-04 private-marker hygiene | PASS | no private markers |
