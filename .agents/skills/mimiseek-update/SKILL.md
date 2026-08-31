---
name: mimiseek-review-update
description: Use only in a new independent ChatGPT chat when the user asks "Обнови Мимисик", "обнови MimiSeek Review", explicitly invokes mimiseek-review-update, or asks to evaluate and safely roll out a pending reviewer candidate for the exact GitHub repository BogdanAIP/MimiSeek-review. Never route this skill to any other project named MimiSeek. First prove the exact repository identity, independently decide PROMOTE/REJECT/ABSTAIN, then update each consumer only if its live project state proves a safe update window.
---

# Skill: mimiseek-review-update

## Hard target identity

This skill is exclusively for the reviewer-development repository:

`BogdanAIP/MimiSeek-review`

Before any evaluation or mutation, independently resolve that exact GitHub repository and its durable `PENDING_UPDATE` / distribution state.

If the active target is any other repository, service, workspace, database-backed application, or unrelated product named MimiSeek, stop immediately and return:

`WRONG_MIMISEEK_TARGET`

Do not continue by analogy and do not infer that another MimiSeek project is the intended target.

The following are explicit wrong-target warning signs unless later introduced by the canonical `BogdanAIP/MimiSeek-review` repository itself:

- S3 configuration;
- PostgreSQL application configuration;
- `CONFIG_ENV` application setup;
- deployment/runtime setup for an unrelated MimiSeek service.

## User invocation

Primary natural-language trigger:

> Обнови Мимисик.

Equivalent explicit invocation:

> Используй навык `mimiseek-review-update`.

## Purpose

Run the **independent update half** of the MimiSeek Review reviewer-improvement loop in a new ChatGPT chat.

This skill has two separate responsibilities:

1. independently decide whether the frozen candidate may become the new MimiSeek Review stable reviewer;
2. if promoted, independently decide **for each consumer repository** whether installing that new stable version is safe **at the consumer's current live project state**.

Promotion of MimiSeek Review and installation into a consumer are different decisions. A candidate may become MimiSeek Review stable while one or more consumers safely remain pinned to the previous stable until an update window exists.

## Fresh-chat requirement

This skill must run in a ChatGPT conversation that did not create, modify, or advocate for the pending candidate.

If the current conversation participated in `mimiseek-review-run`, candidate construction, learner analysis, or mutation of the frozen evaluation package, do not perform promotion evaluation. Return `UPDATE_BLOCKED_NOT_FRESH` and leave stable unchanged.

The user satisfies this today by opening a new ChatGPT chat and invoking **«Обнови Мимисик»** or explicitly naming `mimiseek-review-update`. Durable repository state is the handoff; no technical prompt must be copied from the previous chat.

## Bootstrap

After the hard target-identity check and before mutations:

1. Resolve live `BogdanAIP/MimiSeek-review` state independently from GitHub.
2. Read the governing MimiSeek Review documents and exact frozen `PENDING_UPDATE` package.
3. Resolve current stable identity, candidate identity, evaluation-policy ref, evidence identities, consumer registry, and candidate diff.
4. Do not rely on claims or summaries from the chat that created the candidate.
5. Never import assumptions from another project merely because it is also called MimiSeek.

## Part A — Evaluate MimiSeek Review candidate

Independently verify at minimum:

- stable and candidate immutable identities;
- candidate is exactly covered by the frozen evaluation package;
- governing evaluation policy was fixed before candidate evaluation and was not weakened by candidate/learner;
- BUGGY target improvements are supported by confirmed defects;
- corresponding FIXED cases do not retain the old target finding;
- protected capabilities do not regress beyond policy tolerance;
- false-positive/rejected-finding behavior remains within policy tolerance;
- required shadow/new-real-world evidence, if any, is satisfied;
- evidence is current, complete, provenance-bound, and not based on invalid different-head comparisons.

Historical reviewer agreement is not ground truth. More findings alone is not improvement.

Return one semantic decision for the candidate:

- `PROMOTE`
- `REJECT`
- `ABSTAIN`

Any identity mismatch, stale package, unresolved provenance, wrong-target evidence, or inability to establish independence must not produce `PROMOTE`.

## Part B — Promote MimiSeek Review stable

### PROMOTE

Only after authoritative `PROMOTE` and successful mechanical identity checks:

1. atomically register the candidate as the new MimiSeek Review stable reviewer;
2. preserve previous stable identity and rollback evidence;
3. record immutable evaluation/promotion evidence;
4. terminally resolve the candidate's `PENDING_UPDATE` state.

Promotion does **not** by itself authorize changing every consumer repository immediately.

### REJECT

Keep current stable unchanged, mark the candidate rejected, preserve evidence, and terminally resolve the pending package.

### ABSTAIN

Keep current stable unchanged and preserve candidate/evidence for later re-evaluation if lifecycle permits.

## Part C — Consumer update-safety evaluation

Run this part only after MimiSeek Review itself has a newly promoted stable version or when reconciling an already-promoted stable with `PENDING_DISTRIBUTION` consumers.

For **each registered consumer independently**, resolve its live repository/project state and decide whether changing its pinned reviewer now is safe.

The consumer's own `AGENTS.md`, current-state/roadmap/acceptance owners, reviewer binding, active work state, and update policy govern this decision.

At minimum check whether any of the following is active or cannot be ruled out:

- an agent/procedure/review run whose semantics are bound to the currently pinned reviewer;
- a frozen exact HEAD or acceptance/release/physical gate that must not receive unrelated policy/tooling changes;
- an active development stage whose governing documents prohibit or defer infrastructure/reviewer updates;
- an open migration or compatibility transition involving reviewer/policy files;
- an unresolved review/merge operation that would become stale or semantically ambiguous if the reviewer binding changed;
- project-local policy requiring a specific safe update window;
- inability to prove that the new MimiSeek Review stable is compatible with the consumer's current project-local review policy.

**Absence of visible activity is not proof of safety.** If the consumer has no reliable way to establish whether an agent/run or protected stage is active, return `DEFER_UNPROVEN_SAFE_WINDOW` rather than modifying the consumer.

### Running-agent immutability

Any already-started agent/reviewer/procedure run must remain bound to the exact reviewer version with which that run started. A consumer update may affect only future runs after the safe update becomes effective.

Never silently switch reviewer semantics inside an in-progress run.

## Consumer distribution decisions

For each consumer return exactly one distribution state:

- `SAFE_TO_UPDATE` — compatibility and current project state prove the reviewer binding may be changed now;
- `DEFER_ACTIVE_WORK` — active work/run/gate makes update unsafe now;
- `DEFER_POLICY_WINDOW` — project stage/policy does not permit update now;
- `DEFER_COMPATIBILITY` — new stable compatibility is not proven;
- `DEFER_UNPROVEN_SAFE_WINDOW` — safety cannot be established reliably.

Only `SAFE_TO_UPDATE` permits creating the consumer update change.

## Applying a safe consumer update

For a `SAFE_TO_UPDATE` consumer:

1. create an auditable reviewer-version update PR/change according to that consumer's governing workflow;
2. bind the change to the exact old and new reviewer identities;
3. do not invalidate or rewrite already-running run identities;
4. do not push directly to a protected stable branch unless that consumer explicitly governs and proves such mutation safe;
5. record the resulting PR/change identity.

For any deferred consumer:

- leave its current reviewer pin unchanged;
- persist the desired target stable version plus defer reason;
- mark distribution `PENDING_DISTRIBUTION`;
- allow a later `mimiseek-review-update` invocation to re-check the live project state and apply the same already-promoted stable when a safe window appears.

A newer MimiSeek Review stable must not erase an older unresolved distribution state without explicit reconciliation.

## Final result

Return a concise `MIMISEEK_UPDATE_RESULT` containing:

- stable before;
- candidate identity;
- evaluation-policy ref;
- candidate decision (`PROMOTE`, `REJECT`, `ABSTAIN`, or blocked state);
- stable after;
- promotion evidence identity if promoted;
- per-consumer safety decision;
- update PR/change identities for safe consumers;
- pending/deferred consumers with exact reasons.

## Fail-closed rules

Never promote MimiSeek Review when candidate evaluation is incomplete, stale, non-independent, wrong-target, or violates a mandatory gate.

Never modify a consumer when:

- current project state cannot be resolved;
- active work safety cannot be established;
- project policy/stage forbids the update;
- compatibility is unresolved;
- the update would mutate semantics of an already-running run.

A failed or interrupted update must leave the previous MimiSeek Review stable usable and every consumer either unchanged or durably reconciled to an already-proven safe update.