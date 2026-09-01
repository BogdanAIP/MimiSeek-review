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

Every real invocation of this workflow occurs in a **new independent ChatGPT chat** when repository state contains an eligible candidate/update package or a previously promoted stable has deferred consumer distributions to reconcile.

The update chat:

1. independently reconstructs the exact MimiSeek state from GitHub;
2. evaluates candidate promotion under the fixed governing evaluation policy when a candidate is pending;
3. returns `PROMOTE`, `REJECT`, or `ABSTAIN` as governed for that candidate;
4. resolves a rollout target only when durable state proves that exact reviewer is the current authoritatively promoted stable — either promoted in this invocation or promoted earlier with persisted deferred-distribution state;
5. independently evaluates each target consumer's live safe-update window;
6. changes only consumers proven safe to update now;
7. leaves unsafe/unproven consumers pinned and records their deferred distribution state.

A distribution-only retry never invents or repeats promotion: it revalidates the already-promoted stable identity and durable pending-distribution authority before touching a consumer.

## Why two chats

The split keeps all consequence-bearing update authority out of the run/development conversation and preserves independent promotion judgment without requiring the run chat to create another ChatGPT context automatically.

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
independent candidate evaluation or deferred-rollout reconciliation
        ↓
if candidate exists: PROMOTE / REJECT / ABSTAIN
        ↓
authoritatively promoted stable only
        ↓
per-consumer live safety check
        ↓
SAFE_TO_UPDATE → auditable update change
DEFER_*       → consumer unchanged
```

A later deferred retry is another **NEW CHAT** invoking the same update role against durable pending-distribution state.

## Invocation and non-invocation

Installing, inspecting, or discussing a skill is not authorization for repository mutation.

The skills perform real work only when the user explicitly asks to run/continue MimiSeek Review or explicitly asks to update MimiSeek Review.

Do not invent demonstration tasks or fake project state. A requested simulation stays read-only unless the user separately requests a real run.

## Repository-first behavior

Every invocation must resolve the exact repository and current GitHub evidence rather than relying on previous-chat memory.

Changes in implementation details belong in repository-owned documents and code. The installed skills should remain stable launch contracts so reviewer evolution does not require reinstalling a ChatGPT skill after every project change.
