# ChatGPT Two-Skill Entry Point

## User contract

MimiSeek Review exposes exactly two practical user workflows in ChatGPT.

### 1. Development / candidate creation

The user opens any normal development chat with access to MimiSeek and says:

> Запусти Мимисик.

This invokes `mimiseek-run`.

The skill collects new cross-project evidence, updates the learning dataset, learns from successes/misses/false positives, creates a candidate when justified, runs the required regression checks, and freezes a durable `PENDING_UPDATE` package.

It **cannot** promote stable or update consumer repositories.

### 2. Independent update

If the first skill finishes with `PENDING_UPDATE`, the user opens a **new ChatGPT chat** and says:

> Обнови Мимисик.

This invokes `mimiseek-update`.

The second skill independently reconstructs the pending package from GitHub, evaluates the candidate under the fixed policy, and returns `PROMOTE`, `REJECT`, or `ABSTAIN`.

Only `PROMOTE` may advance stable. On promotion, the same second skill records the new stable identity and creates reviewer-version update PRs for registered compatible consumers.

## Why two skills

Current ChatGPT does not need to programmatically create a new ordinary chat for the system to work. The user provides context isolation by opening the second chat. The repository is the complete handoff.

No technical prompt, candidate summary, or evidence package must be copied manually between chats.

## Pipeline

```text
CHAT 1
"Запусти Мимисик"
    ↓
mimiseek-run
    ↓
collect → normalize → learning events → learn → candidate → regression
    ↓
freeze PENDING_UPDATE in repository
    ↓

USER OPENS NEW CHAT
    ↓
"Обнови Мимисик"
    ↓
mimiseek-update
    ↓
independent reconstruction + evaluation
    ↓
PROMOTE / REJECT / ABSTAIN
    ↓
PROMOTE only: stable update + consumer update PRs
```

## Independence

`mimiseek-update` must not run promotion evaluation in the same conversation that created or materially modified the pending candidate/evaluation package.

If freshness/independence is not satisfied, stable remains unchanged.

## Durable handoff

The first skill must persist everything required by the second skill under immutable identities. Chat text is never the handoff authority.

The pending package must include stable/candidate/policy identities and exact evaluation evidence sufficient for independent reconstruction.

## Idempotence

Repeated `mimiseek-run` with no new evidence should be a safe no-op. It must not create competing candidates while an unresolved `PENDING_UPDATE` exists.

Repeated `mimiseek-update` must not promote or distribute the same candidate twice.

Interrupted runs must resume or fail closed from durable repository state.

## Future automation

A future executor may automatically create the second fresh ChatGPT context. That would remove the user's manual new-chat action but must preserve the same two-role boundary and independent evaluation semantics.