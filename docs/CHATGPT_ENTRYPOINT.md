# ChatGPT Entry Points

## Current ChatGPT deployment model

The canonical workflow definitions live in this repository as `SKILL.md` files.

On ChatGPT surfaces where native Personal Skills can be installed, these repository skills may be installed/imported as native skills while preserving the repository as the source of truth.

On a personal ChatGPT plan/surface where native Personal Skills are unavailable, use a dedicated ChatGPT Project named `MimiSeek Review` with the routing instructions from `docs/CHATGPT_PROJECT_INSTRUCTIONS.md`. Those Project Instructions are only the launcher/router; they must always resolve and execute the live canonical `SKILL.md` from GitHub.

## User contract

MimiSeek Review exposes exactly two user-facing ChatGPT workflows.

### 1. Development / learning chat

User says:

> Запусти Мимисик.

This routes to `.agents/skills/mimiseek-run/SKILL.md`.

It collects new evidence, learns, builds and regression-checks a candidate, then either finishes with `NO_CHANGE` / `REJECTED_PRE_UPDATE` or freezes exactly one `PENDING_UPDATE` package.

It never promotes stable and never updates consumer repositories.

### 2. New independent update chat

The user opens a **new ChatGPT chat** in the same MimiSeek Project (or another proven native-skill context) and says:

> Обнови Мимисик.

This routes to `.agents/skills/mimiseek-update/SKILL.md`.

The second chat independently evaluates the frozen candidate. If it cannot prove promotion, stable remains unchanged.

If it does promote the candidate to MimiSeek stable, it then checks every registered consumer independently and updates only consumers whose **current live project state** proves a safe reviewer-update window. Unsafe/unproven consumers remain pinned and are recorded as `PENDING_DISTRIBUTION` for a later re-check.

## Why two skills

The two-chat split provides independence without requiring an automatic chat-creation capability.

```text
Chat A: «Запусти Мимисик»
        ↓
collect → learn → candidate → regression → freeze PENDING_UPDATE

NEW CHAT

Chat B: «Обнови Мимисик»
        ↓
independent candidate evaluation
        ↓
PROMOTE / REJECT / ABSTAIN
        ↓
PROMOTE only: new MimiSeek stable
        ↓
per-consumer live safety check
        ↓
SAFE_TO_UPDATE → auditable update change
DEFER_*       → leave consumer unchanged, persist PENDING_DISTRIBUTION
```

## Consumer update safety

A promoted reviewer is not automatically installed everywhere immediately.

The second skill must respect each consumer's own project state. Active agents, exact-head acceptance/release/physical gates, project stages that forbid unrelated changes, reviewer-policy migrations, or unresolved compatibility may make an update unsafe now.

Absence of visible activity is not proof of safety. If the safe window cannot be established, the consumer is deferred.

Already-running agent/reviewer/procedure runs keep the exact reviewer version with which they started. Repository-level updates affect only future runs after the update becomes effective.

## Repeated invocations

`Запусти Мимисик` with no new learning evidence should be a safe `NO_CHANGE`.

`Обнови Мимисик` with no `PENDING_UPDATE` but with deferred consumer distributions may re-check those consumers against live project state and install the already-promoted stable only where the safe window is now proven.

Interrupted runs must resume from durable repository state without duplicating imports, candidates, promotions, or consumer update changes.
