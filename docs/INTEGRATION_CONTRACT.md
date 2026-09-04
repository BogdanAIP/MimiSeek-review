# Integration Contract

## Goal

Allow CAP, UV, and future repositories to consume one standalone stable MimiSeek reviewer, contribute trustworthy review outcomes back to MimiSeek's learning system, and optionally request a bounded independent review job without surrendering project-local development authority.

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
- safety-gated distribution of stable-version updates;
- generic review-job identity/state/result coordination for explicitly requested independent reviews;
- post-result live source-identity validation before a job result is treated as current;
- durable review-job/result publication in MimiSeek-owned GitHub state without modifying the reviewed consumer HEAD;
- requesting one generic return/wake delivery through an external session transport when a valid origin route exists.

### Consumer repository owns

- its development and ordinary review/fix workflow;
- deciding when a PR/HEAD is ready to request independent review;
- project architecture truth;
- project-specific `AGENTS.md` and acceptance/security constraints;
- exact PR/BASE/HEAD identity and project-local acceptance policy;
- finding adjudication under its governing semantics;
- remediation and code changes;
- whether a changed HEAD requires another review;
- terminal acceptance and merge consequences;
- project-local policy overlay and document owners;
- authoritative signals for whether reviewer/infrastructure changes are permitted at the current project state.

A MimiSeek review-job `PASS` does not transfer any of those consumer authorities to MimiSeek.

## Review-job coordination contract

A consumer may explicitly request an independent review for one immutable target identity. The production trigger may be a structured consumer export, a durable PR marker, a MimiSeek request object, or another governed mechanism, but MimiSeek must re-resolve live source state rather than trusting the trigger alone.

A durable public job record must bind at least:

- `job_id` — immutable unique review-job identity;
- immutable repository identity, including repository ID when available and owner/name for readability;
- PR number;
- exact `base_sha`;
- exact `head_sha`;
- immutable `review_policy_ref`;
- request/source evidence locator;
- explicit reviewer profile/source identity used for this job;
- governed job state;
- durable result locator and content digest once available.

The job identity cannot be rewritten after launch. A new HEAD requires a new job identity rather than mutating an old one into currentness.

MimiSeek may ask a separately governed generic session/execution substrate to:

- launch one qualified fresh reviewer worker with a bounded neutral payload;
- return one correlated terminal worker result;
- retain/recover an opaque route to an existing originating ChatGPT conversation;
- deliver one bounded wake/resume message through that route with one-shot/recovery/no-blind-resend semantics.

The exact session transport API is not owned by MimiSeek. The transport must not need CAP/UV/MimiSeek project semantics, GitHub PR semantics, or `PASS`/`FINDINGS` semantics.

### Return-route privacy

A public GitHub review-job record must never contain a raw browser tab identifier, private ChatGPT conversation capability, authentication token, cookie, or equivalent usable session authority.

A return route may either:

- remain entirely in private transport state and be correlated to the immutable job ID; or
- be represented to MimiSeek by an opaque reference that is non-authorizing by itself and safe to persist only if the external transport contract explicitly guarantees that property.

If that boundary cannot be proven, the route remains private and only durable job/result state is stored in GitHub.

### Result validation and currentness

Receiving syntactically valid `REVIEW_RESULT_V1` is insufficient.

Before treating the result as current, MimiSeek must verify correlation to the exact job and re-resolve the live consumer repository/PR identity. A moved or mismatched HEAD produces an explicit stale state/result; it does not become optimistic `PASS`, generic failure, or silent retry.

Wrong-job, wrong-repository, wrong-PR, wrong-BASE, wrong-HEAD, wrong-policy, malformed/truncated, or conflicting repeated results fail closed.

A completed immutable job may be reconciled repeatedly, but reconciliation is a no-op and must not launch a second reviewer or produce a second wake merely because a caller retried after an ambiguous boundary.

### Durable result location

The initial production design keeps the existing CAP/UV source GitHub App read-only. MimiSeek must not widen source-repository permissions merely to publish review results.

The authoritative coordination copy of the review job/result is therefore stored in MimiSeek-owned GitHub state through a separately governed MimiSeek publication path that does not alter the reviewed consumer HEAD.

After wake, the consumer workflow reads that durable result and applies its own policy. If that consumer requires a terminal result to be copied into its own PR before merge, that write is a consumer-side consequence under the consumer's own authenticated authority.

## Consumer binding

The binding schema may exist before MimiSeek has a stable reviewer or before a consumer has installed one.

Before first installation, the binding must be able to represent `consumer_installed = none` / `NOT_INSTALLED` without inventing a reviewer identity. Defining or validating that schema is not itself a reviewer installation.

Once a consumer installs MimiSeek, it must identify the exact stable reviewer it uses. The machine-readable binding must include at least:

- reviewer version;
- immutable MimiSeek commit/content identity;
- compatibility/policy version where required.

Each individual agent/review/procedure run must also bind the reviewer version/source it started with. Updating the repository-level reviewer pin must never mutate reviewer semantics for a run already in progress.

A review job may exist before first MimiSeek stable/installation as long as the job explicitly records the actual reviewer profile/source used and the consumer's accepted project-local review authority. Review-job coordination does not fabricate a MimiSeek stable identity.

Stage 2 may establish the binding/evidence contract but must not create a CAP/UV MimiSeek pin merely to satisfy its acceptance criteria. The first real installation is governed by the same safe-distribution authority as all later updates.

## Evidence export

Consumers must eventually expose structured evidence sufficient for MimiSeek to reconstruct learning outcomes without chat history, including when available:

- review-run identity and reviewer version/source;
- exact repository/base/head identity;
- findings and severity/category;
- disposition (`CONFIRMED`, `REJECTED`, `SUPERSEDED`);
- discovery source (MimiSeek, Codex, development, other);
- fix and verified head;
- terminal PASS/currentness evidence.

A durable review-job result is source review evidence, not automatically adjudicated learning truth. Finding dispositions and remediation outcomes remain consumer-governed and enter the learning store only through the accepted evidence/outcome contract.

Evidence produced before first MimiSeek installation may still be imported when its actual reviewer source/version and provenance are explicit. Missing or ambiguous evidence must remain unknown; MimiSeek may not manufacture a HIT/MISS from absence alone.

## Project overlays

The common reviewer must read and obey project-local policy. Generic methodology must not overwrite project-specific owners.

A stricter project-local rule remains authoritative for that project unless the integration contract explicitly makes the combination incompatible.

The review-job control plane carries project identity as bounded data but must not encode project-specific remediation, merge, or acceptance decisions into generic coordination logic.

## Stable promotion versus consumer installation

MimiSeek promotion and consumer installation are separate transactions.

Before the first promotion, `mimiseek_stable = none` is valid. Before a consumer's first rollout, `consumer_installed = none` is valid.

A new MimiSeek stable may exist while a consumer remains intentionally uninstalled or pinned to a previous stable because the consumer is not in a safe update window.

This is normal, not an error.

Track at least:

- `mimiseek_stable` — current globally promoted reviewer or `none` before first promotion;
- `consumer_installed` — exact MimiSeek reviewer currently installed in each consumer, or `none` before first installation;
- `consumer_target` — promoted stable version MimiSeek wants the consumer to receive, or `none` when no promoted stable exists;
- `distribution_state` — not-installed, installed, pending, blocked, or incompatible with reason.

Review-job state is separate from these version/distribution states. A job `PASS` cannot advance `mimiseek_stable` or `consumer_installed`.

## Consumer safe-update gate

Every real consumer rollout or deferred-distribution reconciliation is performed by `mimiseek-review-update` in a new independent ChatGPT chat.

Before creating or applying a reviewer installation/update in a consumer repository, the update role must independently prove both:

1. the exact rollout target is the current authoritatively promoted MimiSeek stable, with durable valid promotion evidence; and
2. the consumer's current live project state permits that change.

Its canonical repository workflow is `.agents/skills/mimiseek-update/SKILL.md`.

A consumer is not safe to update merely because MimiSeek has promoted a new stable or because an independent review job returned PASS.

Potential blockers include:

- active agent/procedure/reviewer runs;
- frozen exact-head review, acceptance, release, or physical-test gates;
- project stages that forbid unrelated infrastructure/policy mutations;
- open migrations affecting reviewer/policy ownership;
- operations whose exact reviewer identity must remain stable until completion;
- unresolved compatibility with project-local review policy.

If no trustworthy project-local signal can prove the absence of such blockers, distribution is deferred fail-closed.

## Safe distribution

For a consumer proven `SAFE_TO_UPDATE`, MimiSeek prepares an auditable first-install or reviewer-version update according to that repository's governing workflow.

Default behavior is an update PR rather than a silent write to the stable branch.

For a consumer not safe to update:

- do not modify its reviewer pin;
- preserve its currently installed reviewer, including `none` before first installation;
- record the exact current promoted stable as target and the defer reason as `PENDING_DISTRIBUTION`;
- retry safety evaluation only in a later fresh `mimiseek-review-update` invocation that revalidates the target stable/promotion authority from durable state.

A later retry does not create or re-promote a candidate merely to resume distribution.

This allows different projects to adopt the same MimiSeek stable at different times without blocking global reviewer evolution.

## Failure behavior

Fail closed on:

- unresolved/mismatched review-job repository/PR/BASE/HEAD/`review_policy_ref` identity;
- attempted mutation of immutable job identity after launch;
- duplicate or ambiguous reviewer launch without reconciliation;
- wrong-job or conflicting repeated review result;
- stale source HEAD presented as current review evidence;
- malformed/truncated result content;
- ambiguous durable result publication;
- repeated wake after ambiguous delivery without reconciliation;
- leaking a private session/browser capability into public GitHub coordination state;
- unresolved/mismatched reviewer identity;
- missing required project policy;
- incompatible policy/reviewer versions;
- ambiguous finding disposition;
- attempted consumer installation/update without authoritative MimiSeek promotion/current-stable identity;
- attempted consumer installation/update without the required fresh independent update context;
- attempted consumer installation/update without a proven current safe-update window;
- any attempt to change reviewer semantics for an already-running run.
