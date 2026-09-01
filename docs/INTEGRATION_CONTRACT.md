# Integration Contract

## Goal

Allow CAP, UV, and future repositories to consume one standalone stable MimiSeek reviewer and to contribute trustworthy review outcomes back to MimiSeek's learning system.

## Responsibility split

### MimiSeek Review owns

- generic reviewer methodology/artifact;
- reviewer version identity;
- cross-project normalized learning data;
- historical regression corpus;
- learning-event derivation;
- learner and candidate lifecycle;
- candidate evaluation and promotion protocol;
- release of stable reviewer versions;
- tracking desired-versus-installed reviewer versions for consumers;
- safety-gated distribution of stable-version updates.

### Consumer repository owns

- its development and ordinary review/fix workflow;
- project architecture truth;
- project-specific `AGENTS.md` and acceptance/security constraints;
- exact PR/BASE/HEAD identity;
- finding adjudication under its governing semantics;
- project-local policy overlay and document owners;
- authoritative signals for whether reviewer/infrastructure changes are permitted at the current project state.

## Consumer binding

A consumer must identify the exact MimiSeek stable reviewer it uses. The machine-readable binding must include at least:

- reviewer version;
- immutable MimiSeek commit/content identity;
- compatibility/policy version where required.

Each individual agent/review/procedure run must also bind the reviewer version it started with. Updating the repository-level reviewer pin must never mutate reviewer semantics for a run already in progress.

## Evidence export

Consumers must eventually expose structured evidence sufficient for MimiSeek to reconstruct learning outcomes without chat history, including when available:

- review-run identity and reviewer version/source;
- exact repository/base/head identity;
- findings and severity/category;
- disposition (`CONFIRMED`, `REJECTED`, `SUPERSEDED`);
- discovery source (MimiSeek, Codex, development, other);
- fix and verified head;
- terminal PASS/currentness evidence.

Missing or ambiguous evidence must remain unknown; MimiSeek may not manufacture a HIT/MISS from absence alone.

## Project overlays

The common reviewer must read and obey project-local policy. Generic methodology must not overwrite project-specific owners.

A stricter project-local rule remains authoritative for that project unless the integration contract explicitly makes the combination incompatible.

## Stable promotion versus consumer installation

MimiSeek promotion and consumer installation are separate transactions.

A new MimiSeek stable may exist while a consumer remains intentionally pinned to the previous stable because the consumer is not in a safe update window.

This is normal, not an error.

Track at least:

- `mimiseek_stable` — current globally promoted reviewer;
- `consumer_installed` — exact reviewer currently installed in each consumer;
- `consumer_target` — stable version MimiSeek wants the consumer to receive;
- `distribution_state` — installed, pending, blocked, or incompatible with reason.

## Consumer safe-update gate

Before creating or applying a reviewer update in a consumer repository, native role `mimiseek-review-update` must independently resolve whether the current project state permits that change.

Its canonical repository workflow is `.agents/skills/mimiseek-update/SKILL.md`.

A consumer is not safe to update merely because MimiSeek has promoted a new stable.

Potential blockers include:

- active agent/procedure/reviewer runs;
- frozen exact-head review, acceptance, release, or physical-test gates;
- project stages that forbid unrelated infrastructure/policy mutations;
- open migrations affecting reviewer/policy ownership;
- operations whose exact reviewer identity must remain stable until completion;
- unresolved compatibility with project-local review policy.

If no trustworthy project-local signal can prove the absence of such blockers, distribution is deferred fail-closed.

## Safe distribution

For a consumer proven `SAFE_TO_UPDATE`, MimiSeek prepares an auditable reviewer-version update according to that repository's governing workflow.

Default behavior is an update PR rather than a silent write to the stable branch.

For a consumer not safe to update:

- do not modify its reviewer pin;
- preserve its currently installed reviewer;
- record the target new stable and defer reason as `PENDING_DISTRIBUTION`;
- retry safety evaluation on a later `mimiseek-review-update` invocation.

This allows different projects to adopt the same MimiSeek stable at different times without blocking global reviewer evolution.

## Failure behavior

Fail closed on:

- unresolved/mismatched reviewer identity;
- missing required project policy;
- incompatible policy/reviewer versions;
- stale exact-head result presented as current evidence;
- ambiguous finding disposition;
- attempted consumer update without authoritative MimiSeek promotion;
- attempted consumer update without a proven current safe-update window;
- any attempt to change reviewer semantics for an already-running run.
