# Development Protocol

## Purpose

Enable MimiSeek Review itself to be developed by ChatGPT across many disposable chats without depending on previous-chat memory.

Canonical owner for the MimiSeek cross-chat development process: this document.

This document governs development of the MimiSeek improvement system. It does not own the ordinary review/fix/merge loop of CAP, UV, or other consumer projects. Under the accepted narrow coordination boundary, MimiSeek may eventually coordinate an explicitly requested independent review job, but consumer project authority and consequences remain outside MimiSeek.

Supporting documents may explain or index this process, but they do not independently define normative cross-chat development rules. In particular, `docs/DEVELOPMENT_REPEAT_PREVENTION.md` is explanatory reference material only.

## Starting a new development chat

Follow `AGENTS.md`, then independently resolve live GitHub state. A new chat must be able to answer:

1. What is MimiSeek Review responsible for?
2. Where is development now?
3. What is the next canonical action?
4. Which accepted decisions and authority boundaries must not be silently changed?

If those answers cannot be reconstructed from the repository, fix the canonical owners rather than creating a per-chat handoff note.

Before material MimiSeek implementation, validate and inspect active self-development failure patterns:

```text
python tools/validate_development_failure_patterns.py --list-active
```

Compare their trigger conditions/applicable scope to the planned changed concepts. Known patterns are a risk scaffold, not an exhaustive checklist and not permission to skip open-ended engineering/review. A `BOUNDED_FOLLOW_UP` active pattern is unresolved process debt and its durable follow-up must remain visible; do not silently reinterpret it as complete.

## Normal repository implementation cycle

```text
implement one roadmap slice
    ↓
development-chat verification
    ↓
tests / CI when configured or required
    ↓
fresh independent exact-head review under immutable review_policy_ref
    ↓
adjudicate + fix confirmed findings
    ↓
close repeat-prevention loop for confirmed material defects
    ↓
repeat review on the new exact head when fixes move HEAD
    ↓
CURRENT exact-head + exact-policy terminal result
    ↓
persist terminal result through non-HEAD-mutating durable evidence channel
    ↓
merge
    ↓
index accepted evidence / update current state as applicable
```

A terminal review result is current only for the exact repository/base/head/reviewer/`review_policy_ref` identity it evaluated. Any consequence-bearing fix that moves HEAD makes the earlier terminal review stale for merge acceptance.

The terminal result itself must also be durable and independently resolvable. Persist it before merge through a channel that does **not** change the reviewed HEAD, for example a top-level PR comment containing or stably pointing to the exact result, or another immutable/stable evidence locator accepted by governing policy. Record enough identity to reconstruct repository, BASE, HEAD, reviewer identity/context, `review_policy_ref`, terminal status, validity and evidence location. Do not commit a result into the reviewed branch after PASS unless you intend to invalidate that PASS and run a new exact-head review.

After merge, `docs/EVIDENCE_INDEX.md` may index the accepted result, merge identity and other evidence without pretending that the post-merge index update retroactively created the independent review.

Consumer repositories may use different local review sequences. MimiSeek may consume their accepted structured outcomes and, once Track R is implemented, coordinate an explicitly requested bounded independent review job under `docs/INTEGRATION_CONTRACT.md`. It still does not own consumer finding adjudication, remediation, re-review policy, terminal acceptance, or merge consequences.

## Development repeat prevention

This section is the sole normative owner of MimiSeek self-development repeat prevention. Machine state lives in `data/development-failure-patterns.jsonl`; its schema identity is `DEVELOPMENT_FAILURE_PATTERN_V1`; the executable local validator is `tools/validate_development_failure_patterns.py`.

The registry is self-development state only. It does not instantiate future reviewer-learning `DEFECT_PATTERN_V1`, consumer adjudication authority, Stage 4 learning events, baseline/candidate/stable reviewer state, distribution state, or `REVIEW_JOB_V1` / `REVIEW_RESULT_V1` semantics.

### Eligible confirmed defects

After this control is accepted, a material MimiSeek development defect is eligible for durable repeat-prevention closure only when repository-governed evidence establishes it strongly enough to remediate, for example an actionable fresh independent review finding or a reproducible durable CI/runtime incident with established root cause.

Rejected or unresolved reviewer assertions are not automatically failure patterns. Non-material editorial corrections need no pattern unless they expose a broader guardable mechanism.

### Required closure

After an eligible material defect is confirmed and remediated, the remediation is not process-complete until the development workflow has:

1. identified the root cause below the immediate symptom;
2. mapped the defect to an existing `failure_class` or created a new governed class at mechanism level;
3. searched the applicable repository surface for other current instances of that same mechanism;
4. fixed discovered instances or recorded a durable bounded follow-up;
5. added or strengthened executable prevention plus regression/invariant coverage where feasible, otherwise recorded an explicit `MANUAL_ONLY` reason;
6. recorded the durable origin/repeat/related occurrence in the registry when the occurrence model applies.

Failure classes must generalize the mechanism rather than memorize one filename, SHA, comment ID, or exact old answer. Conversely, materially different mechanisms must not be collapsed solely to avoid creating a new class.

### Repository-wide search states

`repository_search.status=COMPLETED` means the declared applicable search scope has been searched at the failure-mechanism level and no unresolved same-class current instance remains.

`repository_search.status=BOUNDED_FOLLOW_UP` means closure is intentionally incomplete and `follow_up_refs` identify durable work that must finish it. A bounded follow-up must not be represented as complete merely because CI can validate the registry shape.

Search declarations, `discovered_instances`, executable `guard_refs`, and `regression_refs` are repository-authority claims. The executable validator must resolve local repository-file references only against tracked regular files in the exact checked-out Git `HEAD` tree. `.git` metadata, untracked or staged-only checkout files, tracked symlinks, submodules, or paths resolving outside repository authority do not satisfy these claims.

CI can prove that declared machine references satisfy this bounded contract; it cannot by itself prove that a semantic repository-wide search was complete or that the failure-class mapping is correct. Fresh semantic review remains responsible for those claims.

### Prevention

Prefer the strongest feasible executable prevention: schema/state invariant, safe shared abstraction, regression/invariant test, static repository guard, CI verifier, or fail-closed identity/authority check.

`prevention.kind=EXECUTABLE` requires at least one tracked regular-file guard reference and at least one tracked regular-file regression reference.

`prevention.kind=MANUAL_ONLY` is exceptional. It carries no executable guard/regression references and requires a concrete explanation of why automation is genuinely unavailable or disproportionate. It is not a shortcut for skipping a feasible protection.

### Repeat identity

One stable `failure_class` has one pattern identity. Do not create a second pattern merely because the same established mechanism appears in another file or PR.

The first occurrence is `ORIGIN`. A later established same-class defect is `REPEAT`; a materially connected but not-established-same-class occurrence may be `RELATED`.

A `REPEAT` must classify why prior prevention did not stop recurrence using one of:

- `NO_GUARD`;
- `GUARD_TOO_NARROW`;
- `GUARD_NOT_IN_CI`;
- `PATTERN_NOT_RETRIEVED`;
- `SCOPE_WRONG`;
- `NEW_VARIANT`;
- `UNKNOWN_PENDING_ANALYSIS`.

`UNKNOWN_PENDING_ANALYSIS` is a temporary fail-closed classification, not permission to finish remediation without determining whether the prevention loop itself needs strengthening.

A repeat is therefore both a new code/process defect and evidence that the prior prevention loop was insufficient.

### Review-time use

When a fresh reviewer finds a material MimiSeek defect, development adjudication must check whether an active `failure_class` already describes the mechanism. If yes, determine whether the occurrence is `REPEAT` or only `RELATED`, why prior prevention/retrieval/scope did not catch it, and whether the prevention needs strengthening repository-wide.

Known patterns supplement rather than replace open-ended semantic review. Absence of a matching pattern is never proof that a change is safe.

Any repeat-prevention remediation that moves the PR HEAD has the same freshness consequence as any other consequence-bearing fix: previous terminal exact-head review evidence becomes stale and a fresh independent review is required.

### Repository write hygiene

A repository Contents write is consequence-bearing because it can move the exact reviewed HEAD even when the intended task is only housekeeping.

Before a ChatGPT-driven MimiSeek repository file create/update:

1. classify whether the intended effect is a repository byte change or only PR metadata/comment/thread housekeeping;
2. use PR/comment/thread actions for non-file housekeeping rather than a repository Contents write;
3. for replacement writes, fetch the current blob and compare the complete intended bytes; if they are byte-identical, do not invoke the Contents update action;
4. when a repository content write is intentional, expect HEAD to move and treat previous exact-head CI/review evidence as stale.

A byte-identical Contents write that nevertheless moves HEAD is a development process incident under `workflow.noop_head_mutation`. If it occurs, preserve the incident evidence and apply the normal repeat-prevention closure. This tool-selection boundary is currently external to repository code/CI, so `MANUAL_ONLY` is acceptable only while the execution substrate provides no machine-enforceable write-intent/no-op fence.

## Track R review-job development versus consumer workflow

Track R implementation is MimiSeek repository development, not permission to take over a consumer repository's workflow.

The MimiSeek-side implementation may define and own:

- immutable `REVIEW_JOB_V1` schema/state/result identity;
- source identity validation before launch and after result capture;
- idempotent launch/result/publication/return coordination state;
- durable MimiSeek-owned GitHub result publication;
- public/private boundary for return-session authority;
- fail-closed stale/wrong-result/retry/concurrency handling.

It must not assume that CAP or another session substrate capability exists merely because architecture permits using one. Before live integration, resolve the exact separately accepted external capability/version and verify that its semantics satisfy the generic transport contract.

Consumer-side consequences remain consumer-owned:

- declaring a particular PR/HEAD ready for review;
- project-local policy selection/authority;
- adjudicating findings;
- modifying consumer code;
- deciding whether another review is required after HEAD moves;
- persisting consumer-local terminal evidence when required;
- merging or otherwise accepting the consumer change.

A Track R review job therefore ends by durably publishing the result and waking/returning control to the origin. It does not continue into consumer remediation/merge as MimiSeek authority.

## Repository development versus reviewer evolution

These are different workflows and must not be conflated.

### Developing MimiSeek Review itself

While `docs/CURRENT_STATE.md` says the product is still in bootstrap or implementation, the run entry point reconstructs the repository and continues the next canonical roadmap work. When the roadmap explicitly authorizes a parallel Track R slice, that slice may proceed without pretending the ordered reviewer-evolution stage sequence is complete.

The run chat must not pretend that collector, learner, regression, promotion, distribution, or review-job runtime machinery already exists when the repository says it does not.

### Operating the reviewer-evolution product

Once the corresponding roadmap stages are implemented and accepted, the operational reviewer-evolution workflow is split across two roles/chats:

```text
Chat A — mimiseek-review-run
collect → normalize → derive learning events → learn → candidate → regression
    ↓
freeze governed independent-update state

NEW INDEPENDENT CHAT

Chat B — mimiseek-review-update
independent candidate evaluation
    ↓
PROMOTE / REJECT / ABSTAIN
    ↓
PROMOTE only: global stable transition
    ↓
per-consumer live safe-update evaluation
    ↓
SAFE_TO_UPDATE → auditable update change
DEFER_*       → leave consumer pinned and persist distribution state
```

Every real `mimiseek-review-update` invocation uses a new independent ChatGPT chat. A later deferred-distribution reconciliation is a separate fresh update invocation that reconstructs the already-authoritatively-promoted current stable and durable `PENDING_DISTRIBUTION` state; it does not create or re-promote a candidate.

Track R is separate from this promotion/update flow. A review-job `PASS` is review evidence for one exact target; it is not `PROMOTE`, does not create a stable reviewer, and does not authorize consumer installation.

Canonical repository workflow files are `.agents/skills/mimiseek-run/SKILL.md` and `.agents/skills/mimiseek-update/SKILL.md`. Their installed/native ChatGPT identities are documented in `docs/CHATGPT_ENTRYPOINT.md`.

The repository is the handoff between chats. Do not require the user to copy technical evaluator prompts or unpublished chat reasoning.

## Repository-development review policy identity

Repository-development acceptance must not be judged by policy introduced by the same PR.

For an ordinary PR after Stage 0:

1. resolve the PR's immutable `BASE_SHA` and `HEAD_SHA`;
2. read the already-accepted repository-development acceptance policy from `BASE_SHA`;
3. set `review_policy_ref=BASE_SHA` unless that accepted BASE policy itself explicitly delegates acceptance to another immutable ref;
4. if such an accepted delegation exists, resolve and record that delegated immutable `review_policy_ref`;
5. treat any acceptance/review/governance changes in HEAD only as proposed target semantics for the PR under review;
6. fail closed if the governing policy ref cannot be determined from accepted BASE state.

A HEAD change cannot weaken fresh-review, CI, evidence, identity, or authority requirements for its own acceptance. It becomes governing policy only after that HEAD is accepted under prior authority and merged into the stable branch.

### One-time Stage 0 bootstrap exception

PR #1 has BASE `09492f1ec8aeb1dfbfc152505d14574016a72870`, whose tree contains only the original bootstrap README and no repository-development acceptance policy.

For this one foundation PR:

- `review_policy_ref` remains the immutable BASE SHA above;
- BASE bootstrap intent, exact live PR identity/evidence, and the complete proposed HEAD governance jointly define the bootstrap review scope;
- HEAD governance is evaluated only as proposed target semantics and does not certify itself;
- terminal acceptance still requires a fresh independent read-only exact-head semantic review and fail-closed handling of unresolved authority/evidence;
- once Stage 0 is merged, this bootstrap exception is unavailable to ordinary future PRs.

## Independent acceptance

The chat that materially changes a PR head is not the independent acceptance reviewer for that same head.

Before merge, use a new ordinary ChatGPT context that is read-only with respect to the PR and independently resolves:

- live PR identity;
- immutable `BASE_SHA` and `HEAD_SHA`;
- the governing `review_policy_ref` from already-accepted BASE authority using the rule above;
- governing repository instructions from that exact accepted policy ref;
- changed files and semantic effects, including proposed HEAD governance changes as target semantics;
- internal document/authority coherence;
- required tests/CI under the governing accepted policy, or the explicit fact that no such gate is configured for the stage.

The independent reviewer must bind its result to repository/base/head/reviewer/`review_policy_ref` and report concrete actionable findings or an exact-head PASS. If it cannot establish identity, policy authority, scope, or required evidence, acceptance fails closed rather than becoming an optimistic PASS.

After a terminal result is obtained and before merge, the development workflow must preserve that exact result durably without moving HEAD. The durable record may be created by the development workflow because it is evidence preservation, not semantic self-acceptance; however, it must preserve the independent result faithfully and must not manufacture reviewer identity, findings, PASS state, or independence claims absent from the result.

## Cross-chat continuity

Do not create `HANDOFF-<date>.md`, chat transcripts, daily logs, or duplicate current-state files.

At the end of significant work:

- commit code/tests;
- update the canonical owner whose truth changed;
- update `CURRENT_STATE` when project position changes;
- update `EVIDENCE_INDEX` when accepted evidence changes;
- record a decision only for durable architectural choices;
- keep PR body aligned with proposed change and acceptance evidence.

Git history and PR discussion carry chronology. Canonical documents carry current truth.

## Safety of self-development

A learner-generated reviewer candidate is a product artifact, not an accepted change merely because it exists.

The learner may create candidate changes, but evaluation-policy authority and promotion evidence remain separate. A failure to obtain required fresh independent evaluation leaves the current stable reviewer unchanged.

The same fail-closed principle applies to repository development and Track R coordination: incomplete, stale, wrong-policy, non-durable, ambiguously governed, wrong-job, or unresolved external-capability evidence leaves the transition unaccepted rather than guessed through.
