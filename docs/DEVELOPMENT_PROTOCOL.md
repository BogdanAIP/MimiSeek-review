# Development Protocol

## Purpose

Enable MimiSeek Review itself to be developed by ChatGPT across many disposable chats without depending on previous-chat memory.

This document governs development of the MimiSeek improvement system. It does not own the ordinary review/fix loop of CAP, UV, or other consumer projects.

## Starting a new development chat

Follow `AGENTS.md`, then independently resolve live GitHub state. A new chat must be able to answer:

1. What is MimiSeek Review responsible for?
2. Where is development now?
3. What is the next canonical action?
4. Which accepted decisions and authority boundaries must not be silently changed?

If those answers cannot be reconstructed from the repository, fix the canonical owners rather than creating a per-chat handoff note.

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

Consumer repositories may use different local review sequences. MimiSeek only consumes their accepted structured outcomes through the integration contract.

## Repository development versus reviewer evolution

These are different workflows and must not be conflated.

### Developing MimiSeek Review itself

While `docs/CURRENT_STATE.md` says the product is still in bootstrap or implementation, the run entry point reconstructs the repository and continues the next canonical roadmap work. It must not pretend that collector, learner, regression, promotion, or distribution machinery already exists when the repository says it does not.

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

The same fail-closed principle applies to repository development: incomplete, stale, wrong-policy, non-durable, or ambiguously governed acceptance evidence leaves the PR unmerged.
