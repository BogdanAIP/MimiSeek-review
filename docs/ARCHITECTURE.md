# Architecture

## System boundary

MimiSeek Review is a standalone reviewer-improvement and release system.

CAP, UV, and future repositories are:

- consumers of the stable reviewer;
- producers of real review/outcome evidence;
- owners of their own development, review/fix loop, architecture truth, and project-specific policy.

MimiSeek Review does **not** own or orchestrate the ordinary PR review loop in those repositories.

## Bootstrap versus operational architecture

The architecture below describes the target operational reviewer-evolution system. `docs/CURRENT_STATE.md` and `docs/ROADMAP.md` determine which components actually exist now.

During bootstrap, native skill `mimiseek-review-run` is a repository-driven development entry point: it reconstructs live repository state and continues the next accepted implementation step. It must not simulate missing collector/learner/regression/distribution components.

Once those components are implemented and accepted, the same run role enters the operational flow below.

## End-to-end operational architecture

```text
CAP / UV / future projects
  ordinary development + external/our reviews
  adjudicated findings / PASS / fixes / exact identities
                    |
                    v
               CHAT A
        mimiseek-review-run
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
       frozen independent-update state
                    |
              NEW CHAT
                    |
                    v
               CHAT B
       mimiseek-review-update
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

A later deferred-distribution retry is another fresh `mimiseek-review-update` chat that starts from the already-authoritatively-promoted stable and durable `PENDING_DISTRIBUTION` state; it does not repeat or invent candidate promotion.

Canonical repository workflow files remain:

- `.agents/skills/mimiseek-run/SKILL.md` for native identity `mimiseek-review-run`;
- `.agents/skills/mimiseek-update/SKILL.md` for native identity `mimiseek-review-update`.

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

The existing historical reviewer workbook is the Stage 1 bootstrap input for this corpus and outcome history. Its exact access-controlled artifact identity and recovery contract are repository-owned in `data/bootstrap-source.json`. After verified import, canonical machine data live in text formats under `data/`; future Excel views are reports rather than competing automation truth.

### Regression evaluator

Executes stable and candidate against appropriate historical cases and protected capabilities and records target detection, old-defect persistence on FIXED, regressions, and false positives.

A candidate that passes the required pre-update gate is frozen into durable independent-update state. That state, not previous-chat prose, is the handoff authority between Chat A and Chat B.

### Run role — `mimiseek-review-run`

During bootstrap, reconstructs live repository state and continues the next canonical repository-development action.

Once the operational evolution stages exist, it coordinates collection, normalization, learning-event derivation, learner execution, candidate creation, regression evaluation, and independent-update-state freeze.

It cannot promote stable and cannot update consumer reviewer pins.

### Independent update role — `mimiseek-review-update`

Every real invocation runs in a new independent ChatGPT chat when an eligible candidate/update state or deferred consumer distribution exists.

It has two separate authorities under fixed governing policy:

1. when an eligible frozen candidate exists, independently evaluate it and return `PROMOTE`, `REJECT`, or `ABSTAIN`; only authoritative `PROMOTE` may make that candidate stable;
2. for an exact reviewer version already proven to be the current authoritatively promoted stable, independently decide for each consumer whether the current live project state proves a safe update window. This may occur immediately after promotion or during a later fresh-chat reconciliation of durable deferred-distribution state.

It must not rely on learner advocacy from Chat A; all required promotion/distribution authority and project evidence are reconstructed from durable governed state.

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

Distribution is performed only for a consumer that the independent update role has classified `SAFE_TO_UPDATE` under that consumer's live governing state and only for an exact rollout target whose authoritative promotion/current-stable identity is proven.

Default mechanism is an auditable update PR/change. Running agent/reviewer/procedure runs remain bound to the reviewer version with which they started; repository-level updates affect only future runs after the consumer change becomes effective.

## Authority separation

- Consumer review processes create source evidence but do not promote MimiSeek versions.
- `mimiseek-review-run` may create/freeze a candidate once the operational pipeline exists, but cannot promote or distribute it.
- Candidate cannot modify the policy or evaluation evidence used to judge itself.
- Every real `mimiseek-review-update` invocation runs in a fresh independent ChatGPT chat, including distribution-only reconciliation.
- Only `PROMOTE` advances global MimiSeek stable.
- A consumer rollout target must already be proven as the current authoritatively promoted stable; pending/rejected/abstained candidates cannot be distributed.
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

Chat contexts are workers, not state stores. Canonical project state, reviewer versions, normalized evidence, learning events, candidate rationale, frozen independent-update state, evaluation results, consumer distribution state, and promotion history must be recoverable from Git/GitHub and structured persisted data.

When a bootstrap/source artifact itself is access-controlled external evidence rather than repository state, its exact locator, version identity, digest, recovery contract, and fail-closed behavior must be owned by the repository so a fresh authorized chat can recover and authenticate it without prior-chat memory.
