# Reviewer Lifecycle

## Stable

The reviewer version released by MimiSeek for consumer use. Stable identity must be immutable and resolvable.

Before the first authoritative promotion, `stable = none` is a valid bootstrap state. No document, baseline seed, candidate, or consumer binding may pretend otherwise.

A global MimiSeek stable version and a consumer's currently installed reviewer version are not necessarily identical at every moment.

## Bootstrap baseline seed

Stage 1 may derive an evidence-backed reviewer baseline seed from the historical corpus and accepted CAP/UV policies.

The baseline seed:

- has immutable identity;
- is not stable;
- is not a candidate promotion result;
- is not consumer-authoritative;
- cannot be distributed;
- exists only as an input/comparison artifact for later governed candidate generation and evaluation.

There is no bootstrap shortcut from baseline seed to stable.

## Candidate

A proposed reviewer version generated from governed evidence. Before any stable exists, the first candidate may be derived from the Stage 1 baseline seed plus accumulated learning evidence. After a stable exists, later candidates evolve according to the accepted lifecycle.

A candidate is not consumer-authoritative merely because it exists or performs well on one case.

## Independent-update state

A frozen candidate package/state that passed the run chat's required pre-update checks and is ready for independent evaluation in a new chat through native role `mimiseek-review-update`.

The current implementation may call this state `PENDING_UPDATE`. Exactly one unresolved pending candidate is allowed unless future lifecycle policy explicitly defines otherwise.

## Rejected candidate

A candidate that failed evaluation. Its evidence remains useful; rejection does not rewrite prior results.

## Bootstrap boundary

The lifecycle below is operational product behavior. Until `docs/CURRENT_STATE.md` says the required collector/learner/regression machinery exists, `mimiseek-review-run` continues repository development rather than fabricating lifecycle state.

In particular, Stage 1 creates only the non-authoritative baseline seed. Stage 5 creates the first eligible candidate, Stage 6 freezes it after required regression/capability evaluation, and Stage 7 uses the same independent `PROMOTE / REJECT / ABSTAIN` authority path to create the first stable that is used for all later promotions.

## Source learning loop

Consumer projects naturally generate evidence during their own ordinary development/review work:

- MimiSeek findings are confirmed or rejected;
- Codex may find a defect MimiSeek missed;
- MimiSeek may find a defect Codex missed;
- development work may expose defects missed by reviewers;
- fixes produce BUGGY→FIXED pairs;
- later failures can reveal post-review escapes.

The operational two-chat loop is:

```text
stable reviewer (or bootstrap state before first stable)
    ↓
consumer outcomes
    ↓
Chat A: mimiseek-review-run
collect + normalize → learning events → learner → candidate → regression
    ↓
frozen independent-update state
    ↓
NEW CHAT
    ↓
Chat B: mimiseek-review-update
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

If no stable existed before the decision, authoritative `PROMOTE` establishes the first stable. `REJECT` or `ABSTAIN` leaves `stable = none`.

A later retry of `PENDING_DISTRIBUTION` is another **new independent update chat**. It starts from durable evidence that the target reviewer was already authoritatively promoted and is still the current stable; it does not create or re-promote a candidate.

Canonical repository workflow files are `.agents/skills/mimiseek-run/SKILL.md` and `.agents/skills/mimiseek-update/SKILL.md`.

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

`mimiseek-review-run` proposes and freezes once the operational pipeline exists. `mimiseek-review-update` in a new independent chat judges under `EVALUATION_POLICY.md`.

Only authoritative `PROMOTE` can advance the global MimiSeek stable reviewer. This rule also governs creation of the **first** stable. `REJECT` and `ABSTAIN` leave the previous stable unchanged; when no stable exists, they leave stable unset.

## Consumer distribution lifecycle

Promotion and installation are separate.

Before first installation, `consumer_installed = none` is a valid binding state. Merely registering a consumer or defining its binding schema does not install MimiSeek.

For every registered consumer, MimiSeek tracks the globally desired stable version against the version actually installed in that repository.

A promoted stable may remain pending for a consumer while that project is in an unsafe update state.

Typical states:

- `NOT_INSTALLED` — no MimiSeek reviewer is installed yet;
- `INSTALLED` — consumer is on the target stable;
- `PENDING_DISTRIBUTION` — current MimiSeek stable exists but installation/update is deferred;
- `BLOCKED_COMPATIBILITY` — compatibility is not proven;
- `UPDATE_IN_PROGRESS` — a governed consumer update change exists and has not yet reached its terminal state.

A later fresh `mimiseek-review-update` invocation may re-check deferred consumers without creating a new reviewer candidate, but only after durable state proves that the exact rollout target is the current authoritatively promoted stable and that its prior promotion evidence remains valid.

## Running-run immutability

Every agent/reviewer/procedure run is bound to the reviewer version/source with which it started.

A later consumer repository update must not change the reviewer semantics of that already-running run. New MimiSeek reviewer versions become eligible only for new runs after the consumer update is effective.
