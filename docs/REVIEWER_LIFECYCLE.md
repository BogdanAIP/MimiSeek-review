# Reviewer Lifecycle

## Stable

The reviewer version released for real consumer use. Stable identity must be immutable and resolvable.

## Candidate

A proposed next version generated from evidence-backed learning. It is not consumer-authoritative merely because it exists or performs well on one case.

## Rejected candidate

A candidate that failed evaluation. Its evidence remains useful; rejection does not rewrite prior results.

## Source learning loop

Consumer projects naturally generate evidence during their own ordinary development/review work:

- MimiSeek findings are confirmed or rejected;
- Codex may find a defect MimiSeek missed;
- MimiSeek may find a defect Codex missed;
- development work may expose defects missed by reviewers;
- fixes produce BUGGY→FIXED pairs;
- later failures can reveal post-review escapes.

MimiSeek imports that evidence and runs:

```text
stable reviewer
    ↓
consumer outcomes
    ↓
collect + normalize
    ↓
learning events
    ↓
learner
    ↓
candidate
    ↓
regression / protected-capability evaluation
    ↓
fresh independent ChatGPT evaluator
    ↓
PROMOTE / REJECT / ABSTAIN
    ↓
new stable only on PROMOTE
    ↓
consumer update PRs
```

## Learning event principles

Events are derived from adjudicated evidence, not reviewer popularity.

Examples:

- `OUR_HIT`: MimiSeek finding was confirmed.
- `OUR_MISS_CODEX_HIT`: suitable MimiSeek evidence missed a defect that Codex reported and that was later confirmed.
- `OUR_HIT_CODEX_MISS`: MimiSeek confirmed a defect not reported by a suitable Codex run.
- `OUR_FALSE_POSITIVE`: MimiSeek finding was rejected after falsification.
- `BOTH_MISS_LATER_CONFIRMED`: suitable runs missed a later-confirmed defect.

Different-head review sequences are not automatically reviewer misses. Identity/timing/visibility conditions must support the inference.

## Learner output

The learner should extract transferable mechanics rather than historical answers.

Good:

> For a modified durable object, enumerate all independently reachable writers and prove the intended serialization boundary covers all of them.

Bad:

> On SHA abc123 inspect file X line 417.

Every candidate change must cite evidence for why the mechanic is proposed and identify capabilities it could affect.

## Protected capabilities

Demonstrated strengths may become protected evaluation coverage. A candidate must not be promoted if it loses protected capability beyond fixed policy tolerance.

## Promotion authority

The learner proposes. Regression evaluation measures. A fresh independent ChatGPT evaluator judges under `EVALUATION_POLICY.md`.

Only an authoritative `PROMOTE` result can update the stable reviewer identity. `REJECT` and `ABSTAIN` leave stable unchanged.
