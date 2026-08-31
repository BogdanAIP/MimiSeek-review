# ChatGPT Entry Points

## Principle

The repository is the durable source of truth. Installed ChatGPT skills are stable entry points into the current repository-owned process; they must not duplicate a frozen copy of the whole implementation lifecycle.

MimiSeek Review exposes two user-facing workflows.

## 1. «Запусти Мимисик» — `mimiseek-review-run`

Target repository: `BogdanAIP/MimiSeek-review`.

A fresh chat invokes this skill to reconstruct the live project from GitHub and continue the **next canonical work from the repository's actual current state**.

That means:

- while MimiSeek Review is still being built, continue the current development/bootstrap stage according to `CURRENT_STATE`, `ROADMAP`, governance and acceptance evidence;
- once the reviewer-learning pipeline is operational, execute the governed collect/learn/candidate/regression side of that pipeline;
- never pretend a later lifecycle phase exists when the repository says prerequisites are still incomplete.

The run skill does not self-promote a reviewer candidate when the lifecycle requires independent evaluation, and it does not bypass consumer-project governance.

## 2. «Обнови Мимисик» — `mimiseek-review-update`

This workflow is invoked in a **new independent ChatGPT chat** when repository state contains an eligible candidate/update package or a previously promoted stable has deferred consumer distributions to reconcile.

The update chat:

1. independently reconstructs the exact MimiSeek state from GitHub;
2. evaluates candidate promotion under the fixed governing evaluation policy when a candidate is pending;
3. returns `PROMOTE`, `REJECT`, or `ABSTAIN` as governed;
4. only after valid promotion, evaluates each registered consumer's live safe-update window independently;
5. changes only consumers proven safe to update now;
6. leaves unsafe/unproven consumers pinned and records their deferred distribution state.

## Why two chats

The split preserves independent promotion judgment without requiring the run chat to create another ChatGPT context automatically.

```text
Chat A: «Запусти Мимисик»
        ↓
recover live repository state
        ↓
continue current canonical MimiSeek work
        ↓
when operational: collect → learn → candidate → regression
        ↓
freeze independent-update state when eligible

NEW CHAT

Chat B: «Обнови Мимисик»
        ↓
independent candidate evaluation / deferred rollout reconciliation
        ↓
PROMOTE / REJECT / ABSTAIN
        ↓
PROMOTE only: new MimiSeek stable
        ↓
per-consumer live safety check
        ↓
SAFE_TO_UPDATE → auditable update change
DEFER_*       → consumer unchanged
```

## Invocation and non-invocation

Installing, inspecting, or discussing a skill is not authorization for repository mutation.

The skills perform real work only when the user explicitly asks to run/continue MimiSeek Review or explicitly asks to update MimiSeek Review.

Do not invent demonstration tasks or fake project state. A requested simulation stays read-only unless the user separately requests a real run.

## Repository-first behavior

Every invocation must resolve the exact repository and current GitHub evidence rather than relying on previous-chat memory.

Changes in implementation details belong in repository-owned documents and code. The installed skills should remain stable launch contracts so reviewer evolution does not require reinstalling a ChatGPT skill after every project change.
