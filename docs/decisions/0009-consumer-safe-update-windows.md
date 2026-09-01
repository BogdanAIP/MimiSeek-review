# ADR 0009 — Consumer rollout requires a proven safe update window

## Context

A newly promoted MimiSeek reviewer may become available while a consumer project is in the middle of agent execution, exact-head review, acceptance, release, physical testing, migration, or another stage where changing reviewer/policy files would invalidate evidence or change semantics mid-operation.

Treating promotion as permission to update every consumer immediately would therefore be unsafe. Retrying a deferred rollout from the development/run conversation would also collapse the independent update boundary after promotion.

## Decision

Separate global MimiSeek promotion from per-consumer installation.

Every real consumer distribution decision is made by native update role `mimiseek-review-update` in a new independent ChatGPT chat under `.agents/skills/mimiseek-update/SKILL.md` and the consumer's own governing policy.

Before rollout, that fresh update invocation must prove from durable state that the exact target reviewer is the current authoritatively promoted stable. It then independently evaluates each registered consumer's live project state.

Only a proven `SAFE_TO_UPDATE` state permits a reviewer-version update change for that consumer.

If active work, project policy, compatibility, or the absence of a trustworthy safety signal prevents proof, leave that consumer pinned and record `PENDING_DISTRIBUTION` with the exact promoted-stable target and defer reason.

Already-running agent/reviewer/procedure runs remain bound to the reviewer version with which they started. A repository-level update applies only to future runs after the update becomes effective.

## Consequences

- MimiSeek can continue improving globally without forcing synchronized consumer updates.
- CAP, UV, and future projects may adopt the same stable reviewer at different safe times.
- Silence or lack of visible GitHub activity is never enough to infer safety.
- Consumer integration must eventually expose reliable machine-readable update-safety state or equivalent governed evidence.
- Deferred distributions are retried only by later fresh `mimiseek-review-update` invocations that revalidate the already-promoted stable and durable pending-distribution authority; they do not create or re-promote a candidate.
