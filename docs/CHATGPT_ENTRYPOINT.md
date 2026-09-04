# ChatGPT Entry Points

## Principle

The repository is the durable source of truth. Installed ChatGPT skills are stable entry points into the current repository-owned process; they must not duplicate a frozen copy of the whole implementation lifecycle.

MimiSeek Review exposes two user-facing workflows. Track R independent-review job coordination is a runtime/control-plane capability of MimiSeek, not a third promotion authority role.

## 1. «Запусти Мимисик» — `mimiseek-review-run`

Target repository: `BogdanAIP/MimiSeek-review`.

A fresh chat invokes this skill to reconstruct the live project from GitHub and continue the **next canonical work from the repository's actual current state**.

That means:

- while MimiSeek Review is still being built, continue the current development/bootstrap stage according to `CURRENT_STATE`, `ROADMAP`, governance and acceptance evidence;
- when Track R is accepted but incomplete, continue the next MimiSeek-side review-job implementation slice without pretending separately governed CAP/session capabilities are already accepted;
- once Track R is operational and an explicit governed review request exists, the run-side system may coordinate the bounded review job defined by `ARCHITECTURE.md` and `INTEGRATION_CONTRACT.md`, while consumer adjudication/fix/re-review/merge authority remains outside MimiSeek;
- once the reviewer-learning pipeline is operational, execute the governed collect/learn/candidate/regression side of that pipeline;
- never pretend a later lifecycle phase or external capability exists when the repository says prerequisites are still incomplete.

The run skill does not self-promote a reviewer candidate when the lifecycle requires independent evaluation, does not bypass consumer-project governance, and does not turn a Track R review `PASS` into consumer merge or MimiSeek promotion authority.

## Track R request boundary

Track R does not mean that every open PR is automatically review-authorized.

A real review job requires an explicit governed request/trigger bound to exact repository/PR/BASE/HEAD/`review_policy_ref` identity. Once the runtime exists, MimiSeek may coordinate that job through a generic session/execution substrate and persist the result durably, but the originating consumer workflow remains responsible for all project-specific consequences.

Private browser/ChatGPT/session authority is not repository-visible routing data. Public review-job records may carry only the safe durable identity/result state allowed by the integration contract.

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

Track R is not a substitute for this role. An ordinary independent review job does not evaluate/promote a reviewer candidate or authorize stable distribution.

## Why two chats

The split keeps all consequence-bearing reviewer-update authority out of the run/development conversation and preserves independent promotion judgment without requiring the run chat to create another ChatGPT context automatically.

```text
Chat A: «Запусти Мимисик»
        ↓
recover live repository state
        ↓
continue current canonical MimiSeek work
        ↓
when Track R operational: coordinate explicit review jobs within narrow boundary
        ↓
when evolution operational: collect → learn → candidate → regression
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

The skills perform real work only when the user explicitly asks to run/continue MimiSeek Review or explicitly asks to update MimiSeek Review. A Track R review job independently requires its governed explicit review request/trigger.

Do not invent demonstration tasks or fake project state. A requested simulation stays read-only unless the user separately requests a real run.

## Repository-first behavior

Every invocation must resolve the exact repository and current GitHub evidence rather than relying on previous-chat memory.

Changes in implementation details belong in repository-owned documents and code. The installed skills should remain stable launch contracts so reviewer evolution or Track R implementation does not require reinstalling a ChatGPT skill after every project change.
