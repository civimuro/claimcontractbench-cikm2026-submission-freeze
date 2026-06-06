# Reviewer Verification Checklist

Start here when you want to decide quickly whether the repository is a
checkable resource artifact, without treating it as a paper verdict machine.
This page is the canonical human-reviewer entry point.

## Ten-Minute Check

For a no-LLM trial over the current real-paper template surface:

```bash
python3 src/claimcontractbench.py try-human
```

Run these from the repository root:

```bash
python3 src/claimcontractbench.py doctor
python3 src/claimcontractbench.py smoke
```

Expected high-level signal:

```text
PASS release surface validation
rows: 132
required_files: 132
public_safe_rows: 132
raw_data_rows: 0

PASS release smoke suite
positive_checks: 13
negative_fail_closed_checks: 5
```

If both commands pass, the checkout is a manifest-controlled, public-safe
release surface and the first-inspection runners still fail closed on bad
packets. The smoke suite uses temporary working directories and should leave a
clean git checkout.

For a strict no-generated-files check, use:

```bash
python3 src/claimcontractbench.py doctor
python3 src/run_projection_smoke.py
python3 src/claimcontractbench.py templates
```

## What A Reviewer Can Safely Conclude

If the ten-minute check passes, a safe reviewer-facing conclusion is:

> The artifact is a public-safe, manifest-controlled resource snapshot with
> standard-library runners that regenerate its core claim-licensing examples
> and fail-closed checks.

Do not upgrade that conclusion into a claim that the tool autonomously reviews
papers, proves human-review utility, reproduces all raw-data experiments, or
judges paper acceptance.

## What To Inspect Next

| Question | File or command | What counts as a good signal |
| --- | --- | --- |
| What is the core idea? | `docs/CONCEPTS.md` | You can explain metric-to-claim licensing, `G/Q/U`, and fail-closed routing in one paragraph. |
| What exactly is in the release? | `artifact/release_manifest_20260520.csv` | Every required row exists, is public-safe, and is not raw data. |
| What are the smallest examples? | `data/claim_passport_casebook_20260519.csv` | Five action families are present: emit, relabel, weaken, rewrite, suppress. |
| Which paper-facing claims are supported by which files? | `docs/REPORT_INDEX.md` | Each claim has a command, expected signal, and boundary. |
| What should not be claimed? | `docs/BOUNDARIES.md` | No autonomous review, peer-review replacement, raw-data redistribution, or human-utility proof is asserted. |
| How does the optional LLM path behave? | `python3 src/claimcontractbench.py review --input artifact/llm_claim_review_packet_template_20260527.csv` | The packet reports registered calls, admission-needed rows, out-of-scope rows, and zero unsafe release. |
| Can an LLM try the current real-paper packet without gold leakage? | `python3 src/claimcontractbench.py try-llm` | A clean `/tmp` packet is created with candidate claims, template cards, prompt, and LLM context only. |
| Can the current real-paper templates be tried directly? | `python3 src/claimcontractbench.py realpaper-demo --output /tmp/claimcontractbench_realpaper_demo` | The 72-row public-paper demo reports three families, conservative safety 0.958, display-action accuracy 0.806, and three residual unsafe releases. |

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
6. Read `docs/EVALUATION_SOURCE_INVENTORY.md` only if you want the advanced
   public-paper benchmark/source inventory; ordinary users can skip it.
7. Check `artifact/PUBLIC_RELEASE_CHECKLIST_20260527.md` before citing this as
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
