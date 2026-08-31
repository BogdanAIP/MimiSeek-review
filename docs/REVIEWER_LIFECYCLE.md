# Reviewer Lifecycle

## Stable

The reviewer version released by MimiSeek for consumer use. Stable identity must be immutable and resolvable.

A global MimiSeek stable version and a consumer's currently installed reviewer version are not necessarily identical at every moment.

## Candidate

A proposed next version generated from evidence-backed learning. It is not consumer-authoritative merely because it exists or performs well on one case.

## PENDING_UPDATE

A frozen candidate package that passed the first chat's required pre-update checks and is ready for independent evaluation in a new chat through `mimiseek-update`.

Exactly one unresolved pending candidate is allowed unless future lifecycle policy explicitly defines otherwise.

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

MimiSeek uses a two-chat loop:

```text
stable reviewer
    ↓
consumer outcomes
    ↓
Chat A: mimiseek-run
collect + normalize → learning events → learner → candidate → regression
    ↓
PENDING_UPDATE
    ↓
NEW CHAT
    ↓
Chat B: mimiseek-update
independent evaluation
    ↓
PROMOTE / REJECT / ABSTAIN
    ↓
new MimiSeek stable only on PROMOTE
    ↓
per-consumer live update-safety evaluation
    ↓
SAFE_TO_UPDATE → update change
DEFER_*       → consumer remains pinned / PENDING_DISTRIBUTION
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

`mimiseek-run` proposes and freezes. `mimiseek-update` in a new independent chat judges under `EVALUATION_POLICY.md`.

Only authoritative `PROMOTE` can advance the global MimiSeek stable reviewer. `REJECT` and `ABSTAIN` leave stable unchanged.

## Consumer distribution lifecycle

Promotion and installation are separate.

For every registered consumer, MimiSeek tracks the globally desired stable version against the version actually installed in that repository.

A promoted stable may remain pending for a consumer while that project is in an unsafe update state.

Typical states:

- `INSTALLED` — consumer is on the target stable;
- `PENDING_DISTRIBUTION` — newer MimiSeek stable exists but update is deferred;
- `BLOCKED_COMPATIBILITY` — compatibility is not proven;
- `UPDATE_IN_PROGRESS` — a governed consumer update change exists and has not yet reached its terminal state.

A later `mimiseek-update` invocation may re-check deferred consumers without creating a new reviewer candidate.

## Running-run immutability

Every agent/reviewer/procedure run is bound to the reviewer version with which it started.

A later consumer repository update must not change the reviewer semantics of that already-running run. New reviewer versions become eligible only for new runs after the consumer update is effective.