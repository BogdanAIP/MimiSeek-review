# Architecture

## System boundary

MimiSeek Review is a standalone reviewer-improvement and release system.

CAP, UV, and future repositories are:

- consumers of the stable reviewer;
- producers of real review/outcome evidence;
- owners of their own development, review/fix loop, architecture truth, and project-specific policy.

MimiSeek Review does **not** own or orchestrate the ordinary PR review loop in those repositories.

## End-to-end architecture

```text
CAP / UV / future projects
  ordinary development + Codex + MimiSeek reviews
  adjudicated findings / PASS / fixes / exact identities
                    |
                    v
               CHAT A
        «Запусти Мимисик»
                    |
                    v
              COLLECTOR
                    |
                    v
          NORMALIZED OUTCOME STORE
                    |
                    v
          LEARNING EVENT BUILDER
                    |
                    v
                 LEARNER
                    |
                    v
          CANDIDATE REVIEWER
                    |
                    v
       REGRESSION / CAPABILITY GATE
                    |
                    v
          frozen PENDING_UPDATE
                    |
              NEW CHAT
                    |
                    v
               CHAT B
        «Обнови Мимисик»
                    |
                    v
      INDEPENDENT CANDIDATE EVALUATION
        /           |          \
   PROMOTE        REJECT      ABSTAIN
      |
      v
 NEW GLOBAL MIMISEEK STABLE
      |
      v
 PER-CONSUMER LIVE SAFETY CHECK
      |
  SAFE_TO_UPDATE ─────→ reviewer-update PR/change
  DEFER_*        ─────→ consumer remains pinned
```

## Logical components

### Stable reviewer artifact

The reviewer version currently released by MimiSeek for consumer use. Its identity is immutable and resolvable by version plus content/commit identity.

Global MimiSeek stable and a consumer's currently installed reviewer version may differ temporarily because consumer rollout can be deferred.

### Collector

Reads new structured review outcomes from registered consumer repositories and imports only evidence that satisfies identity and provenance requirements.

The collector must be idempotent and must not infer missing adjudication as truth.

### Outcome store

Persists normalized review runs, findings, dispositions, exact identities, discovery source, and fix/verification evidence.

Historical chronology remains in source repositories; this store is the canonical normalized learning input for MimiSeek.

### Learning event builder

Derives evidence-backed events such as:

- `OUR_HIT`;
- `OUR_MISS_CODEX_HIT`;
- `OUR_HIT_CODEX_MISS`;
- `OUR_FALSE_POSITIVE`;
- `BOTH_MISS_LATER_CONFIRMED`.

Different-head sequences must not be mislabeled as same-head misses.

### Learner

Analyzes accumulated events and proposes transferable changes to reviewer behavior.

Authority:

- may produce a candidate reviewer and rationale;
- may cite concrete learning evidence;
- may not modify the evaluation policy governing that candidate;
- may not make a candidate stable.

### Regression corpus

Contains real BUGGY→FIXED cases and protected-capability cases.

The existing historical reviewer workbook is the bootstrap source for this corpus and outcome history. Canonical machine data will live in text formats under `data/`; Excel remains a generated/reporting representation.

### Regression evaluator

Executes stable and candidate against appropriate historical cases and protected capabilities and records target detection, old-defect persistence on FIXED, regressions, and false positives.

A candidate that passes the required pre-update gate is frozen into a durable `PENDING_UPDATE` package. This package is the only handoff authority between Chat A and Chat B.

### `mimiseek-run`

User-facing skill invoked as **«Запусти Мимисик»** in Chat A.

It coordinates collection, normalization, learning-event derivation, learner execution, candidate creation, regression evaluation, and pending-package freeze.

It cannot promote stable and cannot update consumer reviewer pins.

### `mimiseek-update`

User-facing skill invoked as **«Обнови Мимисик»** in a new independent ChatGPT chat.

It has two separate authorities under fixed governing policy:

1. independently evaluate the frozen candidate and return `PROMOTE`, `REJECT`, or `ABSTAIN`;
2. after promotion, independently decide for each consumer whether the current live project state proves a safe update window.

It must not rely on learner advocacy from Chat A; all required evidence is reconstructed from repository-owned durable state.

### Version registry

Identifies stable and candidate reviewer versions, immutable content identity, evaluation-policy identity, pending-update state, promotion evidence, and consumer desired/installed reviewer identities.

### Consumer safe-update state

A promoted MimiSeek stable does not automatically authorize immediate installation everywhere.

For each consumer MimiSeek must be able to resolve states such as:

- `INSTALLED`;
- `PENDING_DISTRIBUTION`;
- `BLOCKED_COMPATIBILITY`;
- `UPDATE_IN_PROGRESS`.

If active work, exact-head gates, project policy, compatibility, or running-agent state makes an update unsafe or unprovable, the consumer remains pinned.

### Distributor

Distribution is performed only for a consumer that `mimiseek-update` has classified `SAFE_TO_UPDATE` under that consumer's live governing state.

Default mechanism is an auditable update PR/change. Running agent/reviewer/procedure runs remain bound to the reviewer version with which they started; repository-level updates affect only future runs after the consumer change becomes effective.

## Authority separation

- Consumer review processes create source evidence but do not promote MimiSeek versions.
- `mimiseek-run` may create/freeze a candidate but cannot promote or distribute it.
- Candidate cannot modify the policy or evaluation evidence used to judge itself.
- `mimiseek-update` must run in a fresh independent chat for promotion authority.
- Only `PROMOTE` advances global MimiSeek stable.
- Global promotion does not itself prove any consumer is currently safe to update.
- Consumer update safety is resolved per repository and fails closed when active-state safety or compatibility cannot be proven.

## Generic versus project-specific knowledge

A rule may enter the generic stable reviewer only when it is transferable beyond the originating project.

Generic example:

> For a modified durable object, enumerate all independent writers and prove they share the intended serialization/authority boundary.

Project-specific example:

> A named CAP receipt or UV document is authoritative for a specific local state.

Project-specific rules remain in the consumer repository's governing policy/overlay.

## Durable state principle

Chat contexts are workers, not state stores. Canonical project state, reviewer versions, normalized evidence, learning events, candidate rationale, frozen pending package, evaluation results, consumer distribution state, and promotion history must be recoverable from Git/GitHub and structured persisted data.
