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
fresh independent exact-head review
    ↓
adjudicate + fix confirmed findings
    ↓
repeat review on the new exact head when fixes move HEAD
    ↓
CURRENT exact-head acceptance evidence
    ↓
merge
    ↓
update CURRENT_STATE / ROADMAP / EVIDENCE_INDEX as applicable
```

A review result is current only for the exact repository/base/head identity it evaluated. Any consequence-bearing fix that moves HEAD makes the earlier terminal review stale for merge acceptance.

Consumer repositories may use different local review sequences. MimiSeek only consumes their accepted structured outcomes through the integration contract.

## Repository development versus reviewer evolution

These are different workflows and must not be conflated.

### Developing MimiSeek Review itself

While `docs/CURRENT_STATE.md` says the product is still in bootstrap or implementation, the run entry point reconstructs the repository and continues the next canonical roadmap work. It must not pretend that collector, learner, regression, promotion, or distribution machinery already exists when the repository says it does not.

### Operating the reviewer-evolution product

Once the corresponding roadmap stages are implemented and accepted, the operational reviewer-evolution workflow is split across two chats:

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

Canonical repository workflow files are `.agents/skills/mimiseek-run/SKILL.md` and `.agents/skills/mimiseek-update/SKILL.md`. Their installed/native ChatGPT identities are documented in `docs/CHATGPT_ENTRYPOINT.md`.

The repository is the handoff between chats. Do not require the user to copy technical evaluator prompts or unpublished chat reasoning.

## Independent acceptance

The chat that materially changes a PR head is not the independent acceptance reviewer for that same head.

Before merge, use a new ordinary ChatGPT context that is read-only with respect to the PR and independently resolves:

- live PR identity;
- governing repository instructions from the applicable base/current policy;
- exact base and head under review;
- changed files and semantic effects;
- internal document/authority coherence;
- required tests/CI or the explicit fact that no such CI is configured for the stage.

The independent reviewer must report concrete actionable findings or an exact-head PASS. If it cannot establish identity, scope, or required evidence, acceptance fails closed rather than becoming an optimistic PASS.

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

The same fail-closed principle applies to repository development: incomplete or stale acceptance evidence leaves the PR unmerged.
