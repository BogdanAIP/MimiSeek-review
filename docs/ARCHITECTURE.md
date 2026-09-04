# Architecture

## System boundary

MimiSeek Review is a standalone reviewer-improvement and release system with a bounded independent-review job control plane.

CAP, UV, and future repositories are:

- future/current consumers of the promoted stable reviewer;
- producers of real review/outcome evidence even before first MimiSeek installation when provenance is sufficient;
- owners of their own development, review/fix loop, architecture truth, project-specific policy, finding adjudication, remediation, acceptance, and merge consequences.

MimiSeek Review does **not** own those ordinary project workflows. It may, however, coordinate an explicitly requested independent review job for an immutable repository/PR/BASE/HEAD/policy identity and return the durable result to the originating project workflow.

This narrow coordination authority is project-neutral. It does not authorize MimiSeek to decide how consumer code is fixed or whether a consumer PR merges.

## Two separate operational loops

MimiSeek has two distinct loops that must not be conflated.

### Fast independent-review job loop

```text
originating project chat
      |
      | explicit review request for exact PR/HEAD
      v
MIMISEEK REVIEW-JOB CONTROL PLANE
      |
      | generic fresh-worker request
      v
GENERIC SESSION / EXECUTION SUBSTRATE (for example CAP)
      |
      v
FRESH TEMPORARY CHAT REVIEWER
      |
      | REVIEW_RESULT_V1
      v
MIMISEEK IDENTITY RECHECK + DURABLE RESULT
      |
      | generic return/wake delivery
      v
originating project chat
      |
      v
consumer adjudication / fix / re-review / merge
```

The generic session/execution substrate is not part of MimiSeek's semantic authority. It receives opaque session/worker references and bounded payloads. It must not require UV Studio, MimiSeek Review, chat-agent-platform, GitHub PR, `PASS`, or `FINDINGS` semantics.

### Slow reviewer-evolution loop

```text
CAP / UV / future projects
  development + reviews + adjudicated outcomes
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
  SAFE_TO_UPDATE ─────→ reviewer first-install/update PR/change
  DEFER_*        ─────→ consumer remains unchanged/pinned
```

A `PASS` from the fast review-job loop is not candidate-promotion authority in the slow loop.

## Bootstrap versus operational architecture

The architecture describes target operational components. `docs/CURRENT_STATE.md` and `docs/ROADMAP.md` determine which components actually exist now.

During bootstrap, native skill `mimiseek-review-run` is a repository-driven development entry point: it reconstructs live repository state and continues the next accepted implementation step. It must not simulate missing collector/learner/regression/distribution or review-job runtime components.

Stage 1 may create a non-authoritative baseline seed, but that seed is neither stable nor distributable. The first stable is created only through the same frozen-candidate + fresh independent `PROMOTE` path used for later versions; first consumer installation is performed only through the same safe-distribution gate used for later updates.

The review-job control plane is a cross-cutting capability and may be implemented independently of the baseline-seed lifecycle once its own architecture and external generic execution prerequisites are accepted. Its existence does not mark Stage 1, Stage 2, or later reviewer-evolution stages complete.

Canonical repository workflow files remain:

- `.agents/skills/mimiseek-run/SKILL.md` for native identity `mimiseek-review-run`;
- `.agents/skills/mimiseek-update/SKILL.md` for native identity `mimiseek-review-update`.

## Logical components

### Review-job control plane

Owns only the cross-project coordination state for an explicitly requested independent review.

Minimum authority:

- resolve and freeze immutable repository/PR/BASE/HEAD/`review_policy_ref` identity;
- create one durable immutable `REVIEW_JOB_V1` identity;
- claim at most one fresh reviewer launch for that job;
- send a bounded neutral review payload without expected-answer leakage through a generic execution substrate;
- accept only a result correlated to the exact job and reviewer execution identity;
- re-resolve live source PR identity after result capture;
- classify moved/mismatched source state as stale rather than current;
- persist the exact review result durably in MimiSeek-owned GitHub state without changing the reviewed consumer HEAD;
- request one generic return/wake delivery to the originating project session;
- leave consumer adjudication, fixes, re-review decisions, acceptance, and merge consequences outside MimiSeek authority.

A public durable job record must not expose a raw browser tab ID, ChatGPT conversation capability, authentication secret, or other private session authority. Any return route must remain private to the generic transport or be opaque and non-authorizing by itself.

The control plane must be idempotent across restart/retry and fail closed on ambiguous launch, result publication, stale source identity, wrong-job result, conflicting repeated result, or ambiguous return delivery. A repeated reconciliation of a completed immutable job is a no-op, not a second review.

### Generic session/execution substrate boundary

MimiSeek may depend on separately accepted generic capabilities such as:

- launch a fresh qualified worker with bounded payload and exact correlation;
- receive one correlated terminal worker result;
- retain/recover an opaque route to an existing ChatGPT conversation;
- deliver one bounded payload through that opaque route with one-shot/no-blind-resend/recovery semantics.

The exact external API and implementation belong to the session/execution provider, not to MimiSeek. MimiSeek must not require project-specific routing tables or teach the transport GitHub/reviewer semantics.

### Stable reviewer artifact

The reviewer version currently released by MimiSeek for consumer use. Its identity is immutable and resolvable by version plus content/commit identity.

`stable = none` is a valid state before the first authoritative promotion.

Global MimiSeek stable and a consumer's currently installed reviewer version may differ temporarily because consumer rollout can be deferred. A consumer may also remain `NOT_INSTALLED` until a first safe rollout succeeds.

### Bootstrap baseline seed

An immutable, non-authoritative Stage 1 reviewer artifact derived from reconciled historical evidence and accepted project policies.

It exists only to seed later candidate generation and to provide permitted comparison evidence. It cannot become stable directly and cannot be installed in a consumer.

### Collector

Reads new structured review outcomes from registered consumer/evidence-producing repositories and imports only evidence that satisfies identity and provenance requirements.

The collector must be idempotent and must not infer missing adjudication as truth. It may import pre-MimiSeek review evidence when the actual reviewer source/version is explicit.

The existing source GitHub App remains read-only. The review-job control plane must not widen source-repository permissions merely to publish results; durable coordination/result state belongs in MimiSeek-owned publication state unless a consumer independently persists a copy under its own authority.

### Outcome store

Persists normalized review runs, findings, dispositions, exact identities, discovery source, and fix/verification evidence.

Historical chronology remains in source repositories; this store is the canonical normalized learning input for MimiSeek.

A review-job ledger/result is operational coordination evidence, not automatically an adjudicated learning outcome. It enters the normalized learning path only through the governed evidence/outcome contract.

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

- may produce the first or next candidate reviewer and rationale;
- may cite concrete learning evidence;
- may use the Stage 1 baseline seed as governed bootstrap input before a first stable exists;
- may not modify the evaluation policy governing that candidate;
- may not make a candidate stable.

### Regression corpus

Contains real BUGGY→FIXED cases and protected-capability cases.

The existing historical reviewer workbook is the Stage 1 bootstrap input for this corpus and outcome history. Its exact access-controlled artifact identity and recovery contract are repository-owned in `data/bootstrap-source.json`. After verified import, canonical machine data live in text formats under `data/`; future Excel views are reports rather than competing automation truth.

### Regression evaluator

Executes an eligible candidate against appropriate historical cases and protected capabilities and records target detection, old-defect persistence on FIXED, regressions, and false positives.

When a stable exists, stable-versus-candidate comparison is included where governing policy requires it. Before the first stable, the evaluator must not fabricate a stable delta; it applies the fixed first-promotion corpus/protected-capability requirements and may use the non-authoritative baseline seed only as permitted comparison evidence.

A candidate that passes the required pre-update gate is frozen into durable independent-update state. That state, not previous-chat prose, is the handoff authority between Chat A and Chat B.

### Run role — `mimiseek-review-run`

During bootstrap, reconstructs live repository state and continues the next canonical repository-development action.

Once the operational evolution stages exist, it coordinates collection, normalization, learning-event derivation, learner execution, candidate creation, regression evaluation, and independent-update-state freeze.

When the review-job track is implemented and its dependencies are proven, the run-side system may also operate the bounded review-job control plane for explicit requests. This does not grant consumer development/fix/merge authority.

It cannot promote stable and cannot update consumer reviewer pins.

### Independent update role — `mimiseek-review-update`

Every real invocation runs in a new independent ChatGPT chat when an eligible candidate/update state or deferred consumer distribution exists.

It has two separate authorities under fixed governing policy:

1. when an eligible frozen candidate exists, independently evaluate it and return `PROMOTE`, `REJECT`, or `ABSTAIN`; only authoritative `PROMOTE` may make that candidate stable, including establishment of the first stable when `stable_before = none`;
2. for an exact reviewer version already proven to be the current authoritatively promoted stable, independently decide for each consumer whether the current live project state proves a safe update window. This may perform a first installation, immediate post-promotion update, or later fresh-chat reconciliation of durable deferred-distribution state.

It must not rely on learner advocacy from Chat A; all required promotion/distribution authority and project evidence are reconstructed from durable governed state.

### Version registry

Identifies baseline-seed, stable and candidate reviewer versions, immutable content identity, evaluation-policy identity, pending-update state, promotion evidence, and consumer desired/installed reviewer identities. It must represent `stable = none` and `consumer_installed = none` without ambiguity.

### Consumer safe-update state

A promoted MimiSeek stable does not automatically authorize immediate installation everywhere.

For each consumer MimiSeek must be able to resolve states such as:

- `NOT_INSTALLED`;
- `INSTALLED`;
- `PENDING_DISTRIBUTION`;
- `BLOCKED_COMPATIBILITY`;
- `UPDATE_IN_PROGRESS`.

If active work, exact-head gates, project policy, compatibility, or running-agent state makes an update unsafe or unprovable, the consumer remains unchanged/pinned.

### Distributor

Distribution is performed only for a consumer that the independent update role has classified `SAFE_TO_UPDATE` under that consumer's live governing state and only for an exact rollout target whose authoritative promotion/current-stable identity is proven.

Default mechanism is an auditable first-install/update PR/change. Running agent/reviewer/procedure runs remain bound to the reviewer version/source with which they started; repository-level updates affect only future runs after the consumer change becomes effective.

## Authority separation

- Consumer repositories own review readiness, project policy, finding adjudication, remediation, re-review policy, terminal acceptance, and merge consequences.
- MimiSeek review-job coordination may freeze identity, launch one independent reviewer through a generic substrate, validate/persist the result, and request a return wake; it may not decide the consumer consequence.
- A review-job `PASS` is not merge authority and is not reviewer-candidate promotion authority.
- Consumer review processes create source evidence but do not promote MimiSeek versions.
- Stage 1 baseline seed is non-authoritative and non-distributable.
- `mimiseek-review-run` may create/freeze a candidate once the operational pipeline exists, but cannot promote or distribute it.
- Candidate cannot modify the policy or evaluation evidence used to judge itself.
- Every real `mimiseek-review-update` invocation runs in a fresh independent ChatGPT chat, including distribution-only reconciliation.
- Only `PROMOTE` creates or advances global MimiSeek stable, including the first stable.
- A consumer rollout target must already be proven as the current authoritatively promoted stable; baseline seeds and pending/rejected/abstained candidates cannot be distributed.
- Global promotion does not itself prove any consumer is currently safe to update.
- Consumer update safety is resolved per repository and fails closed when active-state safety or compatibility cannot be proven.
- No bootstrap stage or review-job path may bypass promotion or distribution authority merely to establish an initial stable or initial consumer pin.

## Generic versus project-specific knowledge

A rule may enter the generic stable reviewer only when it is transferable beyond the originating project.

Generic example:

> For a modified durable object, enumerate all independent writers and prove they share the intended serialization/authority boundary.

Project-specific example:

> A named CAP receipt or UV document is authoritative for a specific local state.

Project-specific rules remain in the consumer repository's governing policy/overlay.

The review-job control plane may carry exact project identity as data, but must not encode project-specific semantic decisions into generic orchestration or transport logic.

## Durable state principle

Chat contexts are workers, not state stores. Canonical project state, review-job identities/results, reviewer baseline seed, reviewer versions, normalized evidence, learning events, candidate rationale, frozen independent-update state, evaluation results, consumer distribution state, and promotion history must be recoverable from Git/GitHub and structured persisted data.

Private session capabilities are an exception to public repository persistence: they must remain private transport state or opaque non-authorizing references. Public GitHub coordination records may identify a job/result but must not expose a usable private ChatGPT/browser authority.

When a bootstrap/source artifact itself is access-controlled external evidence rather than repository state, its exact locator, version identity, digest, recovery contract, and fail-closed behavior must be owned by the repository so a fresh authorized chat can recover and authenticate it without prior-chat memory.
