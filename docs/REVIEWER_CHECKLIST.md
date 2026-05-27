# Reviewer Verification Checklist

Use this page when you want to decide quickly whether the repository is a
checkable resource artifact, without treating it as a paper verdict machine.

## Ten-Minute Check

Run these from the repository root:

```bash
python3 src/claimcontractbench.py doctor
python3 src/claimcontractbench.py smoke
```

Expected high-level signal:

```text
PASS release surface validation
rows: 96
required_files: 96
public_safe_rows: 96
raw_data_rows: 0

PASS release smoke suite
positive_checks: 8
negative_fail_closed_checks: 4
```

If both commands pass, the checkout is a manifest-controlled, public-safe
release surface and the first-inspection runners still fail closed on bad
packets.

## What To Inspect Next

| Question | File or command | What counts as a good signal |
| --- | --- | --- |
| What is the core idea? | `docs/CONCEPTS.md` | You can explain metric-to-claim licensing, `G/Q/U`, and fail-closed routing in one paragraph. |
| What exactly is in the release? | `artifact/release_manifest_20260520.csv` | Every required row exists, is public-safe, and is not raw data. |
| What are the smallest examples? | `data/claim_passport_casebook_20260519.csv` | Five action families are present: emit, relabel, weaken, rewrite, suppress. |
| Which paper-facing claims are supported by which files? | `docs/REPORT_INDEX.md` | Each claim has a command, expected signal, and boundary. |
| What should not be claimed? | `docs/BOUNDARIES.md` | No autonomous review, peer-review replacement, raw-data redistribution, or human-utility proof is asserted. |
| How does the optional LLM path behave? | `python3 src/claimcontractbench.py review --input artifact/llm_claim_review_packet_template_20260527.csv` | The packet reports registered calls, admission-needed rows, out-of-scope rows, and zero unsafe release. |

## Thirty-Minute Deepening Path

1. Read `docs/CONCEPTS.md`.
2. Run `python3 src/claimcontractbench.py templates` and check the forbidden
   stronger-claim language.
3. Read `docs/REPORT_INDEX.md` beside the generated report commands.
4. Run one behavior report, for example:

   ```bash
   python3 src/run_claim_audit_report.py --output reports/claim_audit_report_20260521
   ```

5. Read `docs/DATA_AND_LICENSES.md` before making any claim about data
   redistribution or raw-data availability.
6. Check `artifact/PUBLIC_RELEASE_CHECKLIST_20260527.md` before citing this as
   a final archived public release.

## Red Flags

Treat any of these as a misuse or a documentation bug:

- a result is described as a paper accept/reject recommendation;
- a claim says the tool autonomously read a full paper;
- an unsupported external claim is silently treated as licensed;
- a new claim family is forced into a nearby registered template;
- raw third-party data is implied to be redistributed;
- reviewer utility or inter-annotator agreement is claimed beyond the stated
  boundary.

## Public Questions

Use `SUPPORT.md` and the GitHub issue templates for public-safe questions. If a
question requires confidential paper text, private review notes, raw data, or
author identity information, do not post it publicly.
