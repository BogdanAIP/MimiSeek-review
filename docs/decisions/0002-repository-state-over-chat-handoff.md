# ADR 0002 — Repository state over chat handoff

## Context

Development is performed by ChatGPT across many chats. Chats can end, stall, hit limits, or lose useful context.

## Decision

Chat contexts are disposable workers. Durable project state must be recoverable from Git/GitHub plus canonical repository documents. Per-chat handoff documents, daily logs, and duplicate current-state files are not canonical mechanisms.

## Consequences

- Every new chat follows the `AGENTS.md` bootstrap.
- `CURRENT_STATE.md` stays concise and current rather than becoming a historical log.
- Git and PR history provide chronology.
- Significant work is not complete until affected canonical document owners are synchronized.
