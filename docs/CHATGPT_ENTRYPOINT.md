# ChatGPT Entry Points

## Current ChatGPT deployment model

The canonical workflow definitions live in this repository as `SKILL.md` files.

On ChatGPT surfaces where native Personal Skills can be installed, install them with the unique skill names:

- `mimiseek-review-run`
- `mimiseek-review-update`

Both are hard-bound to the exact GitHub repository `BogdanAIP/MimiSeek-review`.

A skill that routes to another product named MimiSeek is the wrong skill. S3/PostgreSQL/`CONFIG_ENV` application setup is an explicit wrong-target warning unless such infrastructure is later introduced by the canonical MimiSeek Review repository itself.

The repository remains the source of truth for workflow semantics.

## User contract

MimiSeek Review exposes exactly two user-facing ChatGPT workflows.

### 1. Development / learning chat

User says:

> Запусти Мимисик.

The installed skill must be `mimiseek-review-run` and its canonical repository workflow is stored at `.agents/skills/mimiseek-run/SKILL.md`.

Before any other action it must resolve `BogdanAIP/MimiSeek-review`. Failure to prove that target returns `WRONG_MIMISEEK_TARGET` and performs no mutation.

It collects new evidence, learns, builds and regression-checks a candidate, then either finishes with `NO_CHANGE` / `REJECTED_PRE_UPDATE` or freezes exactly one `PENDING_UPDATE` package.

It never promotes stable and never updates consumer repositories.

### 2. New independent update chat

The user opens a **new ChatGPT chat** and says:

> Обнови Мимисик.

The installed skill must be `mimiseek-review-update` and its canonical repository workflow is stored at `.agents/skills/mimiseek-update/SKILL.md`.

Before evaluation or mutation it must independently prove the same exact `BogdanAIP/MimiSeek-review` target. Wrong-target routing fails closed.

The second chat independently evaluates the frozen candidate. If it cannot prove promotion, stable remains unchanged.

If it does promote the candidate to MimiSeek Review stable, it then checks every registered consumer independently and updates only consumers whose **current live project state** proves a safe reviewer-update window. Unsafe/unproven consumers remain pinned and are recorded as `PENDING_DISTRIBUTION` for a later re-check.

## Why two skills

The two-chat split provides independence without requiring an automatic chat-creation capability.

```text
Chat A: «Запусти Мимисик»
        ↓
mimiseek-review-run
        ↓
collect → learn → candidate → regression → freeze PENDING_UPDATE

NEW CHAT

Chat B: «Обнови Мимисик»
        ↓
mimiseek-review-update
        ↓
independent candidate evaluation
        ↓
PROMOTE / REJECT / ABSTAIN
        ↓
PROMOTE only: new MimiSeek Review stable
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
