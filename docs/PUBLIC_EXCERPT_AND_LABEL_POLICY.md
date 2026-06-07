# Public Excerpt And Label Policy

This page records why the frozen release includes short public excerpts and
row-level labels, but does not include local raw caches, PDFs, or full extracted
paper text.

It is a transparency note, not legal advice.

## Why PDFs And Raw Caches Are Excluded

Public access does not automatically grant permission to repackage full papers
or extracted full text inside this repository. The release therefore excludes:

- downloaded PDFs;
- full paper text;
- local source caches;
- raw extraction logs that reproduce large portions of third-party works;
- private review notes or unpublished manuscripts.

The release keeps only the minimum public-safe anchors needed for row-level
inspection: source title, source URL, section locator, short excerpt, candidate
claim, template family, and label or replay outcome.

## What The Current Release Stores

The real-paper candidate packet stores 72 short source excerpts from 18 public
arXiv source pages:

- maximum excerpt length: 38 words;
- average excerpt length: 22.0 words;
- no excerpt is longer than 40 words;
- no PDF or full paper text is included.

The positive real-paper rerun packet follows the same public-safe style:

- maximum excerpt length: 38 words;
- average excerpt length: 22.2 words;
- no excerpt is longer than 40 words;
- no PDF or full paper text is included.

The template-rule stress packet stores 42 short source snippets:

- maximum snippet length: 19 words;
- average snippet length: 11.4 words;
- no snippet is longer than 40 words;
- annotators were instructed not to open source URLs.

These excerpts are not relicensed under ClaimContractBench's CC-BY-4.0 resource
license. They remain third-party text governed by the original source. The
ClaimContractBench license covers the authors' schemas, labels, runner code,
aggregate reports, documentation, and other original derived resource material.

## Why The Third Rung Is Lower Risk Than Raw Cache Release

The third rung, `realpaper-demo`, uses the public-safe candidate packet and
reference outcomes:

- source URLs and short excerpts instead of PDFs;
- 72 supplied candidate rows instead of full-paper extraction outputs;
- public-safe reference labels and conservative replay decisions;
- aggregate metrics and generated reports;
- no local PDF/text cache.

This is still not zero risk, because short excerpts are third-party text. The
release reduces that risk by keeping excerpts short, attributed, and necessary
for auditability, and by not claiming to relicense them.

## How Correctness Is Defined

The validation ladder has three different notions of "correct." They should
not be collapsed into one accuracy claim.

There is also a reproducibility distinction:

- exact frozen replay recomputes stored metrics from repository files;
- fresh LLM-proxy rerun repeats the task with public-safe inputs and may differ
  from the frozen labels because model calls are not deterministic scientific
  instruments.

Fresh reruns should be reported as stability probes against the locked
reference, not as exact replication.

### Rung 1: Template-Rule Stress

Input:

- 42 blind rows;
- two LLM-proxy annotator channels;
- one clean proxy-adjudication channel.

Correctness means agreement with the proxy-adjudicated action on a supplied
row. The metric is useful for checking whether the action taxonomy and rubric
behave consistently under blinded LLM-proxy use. It is not human-independent
gold and not a human-utility study.

Main reported signals:

- A/B action kappa;
- A/B span-found kappa;
- A/B accuracy against proxy adjudication;
- dangerous false release against proxy adjudication.

### Rung 2: Positive Real-Paper Use

Input:

- 18 public papers;
- 72 supplied candidate claims;
- three admitted template families;
- source-only locked reference actions created before the router scoring pass.

Correctness means the router action or release side matches the locked
source-only reference label for the supplied candidate row. A dangerous false
release means the reference label forbids releasing the candidate, but the
router releases it.

This rung mainly tests whether admitted templates can process positive
real-paper candidate rows. It is not a hard safety test because the reference
distribution is mostly `ACCEPT`/release-side rows.

Main reported signals:

- action accuracy for R4_A and R4_B;
- release-side accuracy;
- dangerous false release count;
- family-level action accuracy;
- baseline caveat against always-ACCEPT style interpretations.

### Rung 3: Reportability-Boundary Replay

Input:

- the current 72-row public real-paper packet;
- reference outcomes and conservative replay outcomes.

Correctness means the conservative replay matches the reference release side or
display action. Unsafe false release means the reference says a candidate should
not be released, but the conservative replay releases it.

This rung is intentionally more revealing than the positive-use rung: it leaves
three unsafe false releases visible and treats them as a boundary, not as a
success to hide.

## What Remains Subjective

The reference labels are judgments about source support, reporting force,
template fit, and safe release. They are therefore partly subjective. The
release makes this auditable by exposing:

- candidate rows;
- action labels;
- support/release labels;
- row-level matches and mismatches;
- baseline caveats;
- exact commands that recompute the aggregate metrics.

The release does not claim that these labels are final human expert truth.

## Why The First Two Rungs Now Have Rerun Packets

The first two rungs originally exposed frozen score files. The current release
also exposes public-safe rerun inputs:

- Stage 1: blind rows, clean annotator prompt, and output schema.
- Stage 2: source pool, source URLs, short excerpts, candidate claims, template
  cards, clean rerun protocol, and locked source-only reference labels for
  scoring after the fresh run.

This does not make LLM calls exactly reproducible. It makes the task auditable:
another reader can run a fresh model or human annotation pass on the same
public-safe rows, then score and compare the result.

## What To Do If More Transparency Is Needed

Future versions can strengthen the evidence by adding:

- human expert annotation;
- inter-annotator agreement over source-only packets;
- source-license metadata per public-paper row;
- a no-excerpt mode that stores only source URL, locator, and paraphrased
  candidate claim;
- larger held-out packets with harder nonrelease distributions.
