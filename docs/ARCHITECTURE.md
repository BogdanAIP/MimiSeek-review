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
      FRESH CHATGPT EVALUATOR
        /           |          \
   PROMOTE        REJECT      ABSTAIN
      |
      v
 NEW STABLE REVIEWER
      |
      v
 DISTRIBUTOR → version-update PRs → consumers
```

## Logical components

### Stable reviewer artifact

The reviewer version currently released for consumer use. Its identity is immutable and resolvable by version plus content/commit identity.

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

### Fresh ChatGPT evaluator

A separately governed evaluator run in a **new isolated ChatGPT chat/context**. It independently checks candidate identity, evaluation evidence, governing policy, and regression/protected-capability results, then returns only an authoritative `PROMOTE`, `REJECT`, or `ABSTAIN` result under `docs/EVALUATION_POLICY.md`.

The learner and candidate do not control this context.

### Version registry

Identifies stable and candidate reviewer versions, immutable content identity, evaluation-policy identity, and promotion evidence.

### Distributor

After authoritative `PROMOTE`, prepares auditable reviewer-version update changes for every registered compatible consumer repository.

Default distribution mechanism is a separate update PR per consumer. Distribution must not silently push incompatible reviewer changes to consumer `main`.

### ChatGPT evolution orchestrator

The user-facing `mimiseek-evolve` skill starts the whole MimiSeek improvement pipeline from ChatGPT.

Internally it invokes collector, learner, regression, fresh evaluation, promotion, and distribution in order. It must stop fail-closed if required evidence, authority, or fresh-context capability is unavailable.

## Authority separation

- Consumer review processes create source evidence but do not promote MimiSeek versions.
- Collector imports evidence but does not decide learning changes.
- Learner proposes candidate changes but cannot promote them.
- Candidate cannot modify the policy or corpus result used to judge itself.
- Regression evaluator measures; it does not independently waive required fresh evaluation.
- Fresh evaluator judges under fixed policy but does not author candidate changes.
- Distributor acts only on an accepted immutable promotion result.

## Generic versus project-specific knowledge

A rule may enter the generic stable reviewer only when it is transferable beyond the originating project.

Generic example:

> For a modified durable object, enumerate all independent writers and prove they share the intended serialization/authority boundary.

Project-specific example:

> A named CAP receipt or UV document is authoritative for a specific local state.

Project-specific rules remain in the consumer repository's governing policy/overlay.

## Durable state principle

Chat contexts are workers, not state stores. Canonical project state, reviewer versions, normalized evidence, learning events, candidate rationale, evaluation results, and promotion history must be recoverable from Git/GitHub and structured persisted data.
