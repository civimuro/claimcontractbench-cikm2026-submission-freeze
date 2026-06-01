# User Experience Feedback Guide

Date: 2026-05-27
Status: `PUBLIC_SAFE_OPTIONAL_FEEDBACK_GUIDE`

This guide defines an optional feedback report for people who try
ClaimContractBench, especially when they use an LLM to prepare the claim packet
or template-admission row.

Feedback is useful only when it helps improve the resource. A general note such
as "the tool is good" is much less useful than a short report that identifies
where the path became unclear, where the LLM misrouted a claim, or where a new
template would be needed.

## Consent And Public-Safety First

The feedback report is optional and public-safe by default. For public GitHub
issues, public pull requests, public examples, or reports intended for the
project maintainers, do not include confidential paper text, private review
notes, author identities, unpublished results, raw data, private links,
credentials, or local file paths.

If you are using the tool on a confidential manuscript, keep the detailed
manuscript-specific notes locally or in an approved private channel. The public
feedback report should describe only abstract task types, aggregate counts,
command names, redacted error messages, and paraphrased template gaps.

A good default is to share only:

- the commands you ran;
- whether the command succeeded;
- the generated ClaimContractBench report summaries;
- short paraphrases of claim types rather than verbatim confidential claims;
- your LLM's routing difficulties or confusion points;
- suggested documentation or template-admission improvements.

Before sharing a feedback report publicly, run:

```bash
python3 src/claimcontractbench.py check-feedback --input feedback/my_feedback_report.md
```

This heuristic check can catch obvious local paths, credential-like strings, and
explicit confidential-material flags. It cannot prove that a report is safe; the
user must still review the text before posting or sending it.

## What Feedback Helps Most

The most useful report answers these questions:

1. Could the user find the shortest path?
2. Could their LLM produce a valid CSV packet without repeated repair?
3. Did the LLM overuse registered templates when it should have used
   `NEEDS_TEMPLATE_ADMISSION`?
4. Did the tool fail closed when the packet was incomplete, private, or
   overconfident?
5. Which report rows were actually useful for review or author revision?
6. Which claims were relevant but unsupported by current templates?
7. What new template family would be needed, and what evidence unit would make
   it auditable?
8. Which terms, commands, or output labels slowed the user down?
9. Did the report change the user's claim wording or reviewer concern?
10. Did privacy constraints prevent LLM use, and was manual CSV use still
    feasible?

## Optional LLM Feedback Workflow

If the user agrees, their AI assistant can read:

- this guide;
- `artifact/LLM_ASSISTED_REVIEW_QUICKSTART_20260527.md`;
- the generated ClaimContractBench report summary;
- optionally, a redacted claim packet.

The AI assistant should then write a separate feedback report using the template
in `artifact/user_experience_feedback_template_20260527.md`.

If the paper or review is confidential, do not send the paper text, private
review notes, or unredacted claim packet to an external LLM unless the user has
an approved private model/workflow. A safe default is to give the assistant only
aggregate routing counts, command output summaries, and paraphrased missing
template families.

From the release root:

```bash
python3 src/claimcontractbench.py feedback-guide
python3 src/claimcontractbench.py init-feedback --output feedback/my_feedback_report.md
```

The `feedback/` folder is ignored by git so trial reports do not accidentally
enter the release.

## Copy-Paste Prompt For The User's LLM

```text
You are writing an optional user-experience feedback report for
ClaimContractBench.

Consent and privacy:
- Public feedback must not include confidential paper text, private review
  notes, author names, local file paths, unpublished tables, raw datasets,
  credentials, or institution-only links.
- Prefer paraphrased claim types over verbatim claims.
- If the source is confidential, say so and keep examples abstract. Keep any
  detailed manuscript-specific notes in a private/local file, not in the public
  feedback report.

Read:
1. the ClaimContractBench quickstart or README;
2. the generated tool report the user provides;
3. optionally, a redacted claim packet.

Your job is not to review the paper. Your job is to report whether the tool was
usable, where the LLM-assisted path was reliable or confusing, and what would
make the resource more useful.

Write Markdown with these exact headings:

# ClaimContractBench Trial Feedback

## Consent And Source Boundary
State what material you were allowed to inspect and what you intentionally did
not include. Confirm that the public feedback report contains no confidential
paper text, private review notes, author identities, raw data, credentials, or
local paths.

## Trial Setup
Name the model or assistant used if the user permits, the operating system, and
the commands attempted.

## Task Type
Describe the paper or excerpt type at a high level, such as benchmark paper,
resource paper, robustness paper, calibration paper, or out-of-scope paper.

## Time To First Useful Report
Estimate whether the user reached a report in under 5 minutes, 15 minutes, or
longer, and why.

## Packet Quality
Report whether the CSV was valid on the first try. If not, describe the repair
needed without exposing private paper text.

## Routing Behavior
Count or describe CALL_REGISTERED_TEMPLATE, NEEDS_TEMPLATE_ADMISSION, and
OUT_OF_SCOPE_DO_NOT_CALL behavior. Note any overconfident template calls.

## Useful Tool Outputs
Identify the rows or output labels that were most useful for review, author
revision, or template design.

## Missing Template Families
Describe relevant empirical claims that could not be handled by current
templates. For each, propose the evidence unit that a future template would
need.

## Confusing Terms Or Steps
List command names, labels, fields, or explanations that slowed the user down.

## Reliability Concerns
State any case where the tool seemed too permissive, too suppressive, or too
dependent on the LLM.

## Suggested Improvements
Give concrete changes to docs, command names, templates, output reports, or
examples.

## Overall Utility
Choose one: useful now / useful with minor fixes / useful only for experts /
not useful for this task. Explain briefly.
```

## How This Helps The Project

These reports are evidence for the usability layer, not proof that the core
claim-licensing theory is correct. They help identify:

- documentation friction;
- LLM routing errors;
- missing template families;
- over-broad claims about applicability;
- privacy blockers;
- whether generated reports are actually useful to reviewers and authors.

They should not be presented as a human-utility study unless a separate
controlled protocol is run.
