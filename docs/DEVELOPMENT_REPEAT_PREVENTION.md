# Development Repeat Prevention

## Purpose

MimiSeek Review must not rely on chat memory to avoid repeating confirmed defects in its own development.

This document defines a small cross-cutting **self-development** control:

```text
confirmed defect
  -> root cause
  -> failure class
  -> repository-wide search
  -> fix known instances / bound follow-up
  -> executable prevention where feasible
  -> regression/invariant coverage
  -> durable failure-pattern record
  -> active-pattern retrieval before later development
  -> repeat classification if the class appears again
```

The objective is not to create a generic bug database. A confirmed material error should leave behind a mechanism that makes the same failure class harder to reintroduce and easier to detect.

## Authority boundary

This control applies only to development of `BogdanAIP/MimiSeek-review`.

It is **not** the future reviewer-evolution `DEFECT_PATTERN_V1` / counterexample architecture described in semantic-review research. It does not:

- create Stage 4 learning events;
- create or modify a reviewer baseline seed;
- train, promote, or distribute a reviewer;
- turn MimiSeek self-development findings into consumer-project authority;
- classify CAP, UV, or another consumer's development findings on that consumer's behalf;
- change `REVIEW_JOB_V1` or `REVIEW_RESULT_V1` semantics.

A future accepted reviewer-learning pattern store may consume or reinterpret evidence from this self-development registry only through a separately governed migration/learning contract. The two namespaces must not silently alias.

## Canonical machine state

The registry is:

`data/development-failure-patterns.jsonl`

Each non-empty line is exactly one:

`DEVELOPMENT_FAILURE_PATTERN_V1`

Machine shape is documented by:

`data/schemas/development-failure-pattern-v1.schema.json`

The executable validator is:

`tools/validate_development_failure_patterns.py`

The validator is the current repository-level enforcement for registry shape, identity, occurrence rules, repository-search declarations, and executable prevention references. It does not make a historical finding true merely because a record is well formed; source evidence still requires ordinary repository acceptance review.

## When a pattern record is required

After this control is accepted, a **confirmed material defect in MimiSeek development** must be evaluated for repeat prevention before the remediation is considered process-complete.

A defect is eligible when durable evidence establishes the error, for example:

- a fresh independent repository-development review finding that is accepted as actionable and remediated;
- a reproducible CI/runtime defect with durable GitHub evidence;
- another repository-governed self-development incident whose root cause is established strongly enough to support a prevention rule.

Rejected or unresolved reviewer assertions are not automatically failure patterns.

Tiny spelling mistakes and other non-material editorial corrections do not need a failure-pattern record unless they reveal a broader mechanism worth guarding.

## Required closure loop

For every eligible confirmed defect, remediation must answer all of the following.

### 1. Root cause

What caused the failure, below the immediate symptom?

Bad:

> `foo.py` had the wrong value.

Better:

> A verifier authenticated the GitHub object identity but did not bind the claim-bearing free-form body, so unrelated text could satisfy the same evidence tokens.

### 2. Failure class

Assign one stable transferable mechanism in `failure_class`.

Do not create a second pattern merely because the same mechanism appears in another file. Repeated occurrences belong under the existing pattern.

### 3. Repository-wide search

Search the applicable MimiSeek repository surface for other current instances of the same mechanism.

`repository_search.status` is either:

- `COMPLETED` — the declared search scope is complete for the failure class and no unresolved same-class instance remains;
- `BOUNDED_FOLLOW_UP` — complete closure is intentionally deferred and `follow_up_refs` identify durable work that must finish it.

The search must operate on the **mechanism**, not only the exact original string.

### 4. Prevention

Prefer the strongest feasible executable prevention:

- schema constraint;
- shared safe abstraction/helper;
- regression test;
- invariant test;
- static repository guard;
- CI verifier;
- fail-closed state/identity check.

An `ACTIVE` pattern with `prevention.kind=EXECUTABLE` must identify both existing `guard_refs` and `regression_refs` in the MimiSeek repository.

`MANUAL_ONLY` is allowed only when automation is genuinely unavailable or disproportionate and must carry an explicit `manual_only_reason`. It is not a shortcut for skipping a feasible guard.

### 5. Durable occurrence identity

The first occurrence is `ORIGIN` and must exactly match the durable pattern origin.

Later same-class defects are added as `REPEAT` occurrences rather than new failure classes.

A repeat must record why the prior prevention did not stop it:

- `NO_GUARD`
- `GUARD_TOO_NARROW`
- `GUARD_NOT_IN_CI`
- `PATTERN_NOT_RETRIEVED`
- `SCOPE_WRONG`
- `NEW_VARIANT`
- `UNKNOWN_PENDING_ANALYSIS`

`RELATED` is for a materially connected occurrence that is not established as the same failure class; it does not require a prevention-failure reason.

## Development-start retrieval

Before material MimiSeek implementation, the development chat must validate and inspect active failure patterns:

```text
python tools/validate_development_failure_patterns.py --list-active
```

The compact output deliberately exposes:

- pattern identity;
- failure class/title;
- trigger conditions;
- applicable scope;
- executable guard/regression references.

It does not dump private reviewer reasoning or make the active pattern list an exhaustive checklist.

The development chat must compare the planned changed concepts/surfaces to active trigger conditions. Applicable patterns become explicit known-risk checks for that work.

Open-ended engineering and semantic review remain required: absence of an applicable known pattern is not evidence that a change is safe.

## Review-time repeat check

When a fresh reviewer finds a material defect in MimiSeek, the development workflow should first ask:

1. Does an existing active `failure_class` already describe this mechanism?
2. If yes, is this a `REPEAT` or only `RELATED` occurrence?
3. If it is a repeat, why did the existing guard/retrieval/scope fail?
4. Does the prevention need strengthening repository-wide before closure?

A repeated known defect is therefore two problems:

- the new code defect;
- a repeat-prevention failure that explains why prior protection was insufficient.

## CI role

CI runs the registry validator independently of unit-test discovery.

CI proves only that the registry and declared local prevention references satisfy the machine contract. It does not prove that:

- the recorded historical root cause is semantically correct;
- repository-wide search prose is truthful;
- a guard fully prevents every future variant;
- a fresh review is unnecessary.

Those remain ordinary semantic-review/acceptance questions.

## First seed

The first registry entry, `DFP-0001`, comes from the confirmed P1 in MimiSeek PR #20 on pre-remediation HEAD:

`a6a79485db9caac3cf68a6a9049a0a6ef9cd1c26`

Durable source review comment:

`review_comment:3940860016`

Failure class:

`evidence.semantic_binding_missing`

The accepted remediation on PR #20 replaced token-only commentary acceptance with distinct exact body/update bindings and negative regressions. The seed demonstrates the desired closed loop; it does not claim that all historical MimiSeek defects have already been backfilled.

## Historical backfill boundary

The registry starts prospectively with a bounded real seed. Historical backfill may add earlier confirmed MimiSeek development failure classes when their durable evidence and prevention semantics can be reconstructed without guesswork.

Do not fabricate patterns merely to make historical coverage look complete.

## Relationship to repository acceptance

This repeat-prevention layer does not replace the existing exact-head acceptance protocol.

Normal sequence remains:

```text
implementation
  -> development verification
  -> required CI
  -> fresh independent exact-head semantic review
  -> adjudicate/fix
  -> repeat prevention closure for confirmed material defects
  -> fresh re-review if HEAD moved
  -> terminal result persistence
  -> merge
```

If adding or strengthening repeat prevention moves the reviewed HEAD, the previous terminal review becomes stale exactly like any other consequence-bearing fix.
