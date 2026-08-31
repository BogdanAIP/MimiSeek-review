# Development Protocol

## Purpose

Enable continuous development by ChatGPT across many disposable chats without depending on previous-chat memory.

## Starting a new development chat

Follow the bootstrap in `AGENTS.md`, then independently resolve live GitHub state. The new chat should be able to answer:

1. What are we building?
2. Where are we now?
3. What is the next canonical action?
4. Which accepted decisions and constraints must not be silently changed?

If those answers cannot be reconstructed from the repository, fix the repository state/document owners rather than creating a per-chat handoff note.

## Normal implementation cycle

```text
implement/change
    ↓
development-chat verification
    ↓
tests / CI
    ↓
Codex review when available and useful
    ↓
adjudicate + fix confirmed findings
    ↓
new exact HEAD
    ↓
fresh independent MimiSeek review
    ↓
FINDINGS? ─ yes → adjudicate + fix → new HEAD → new fresh review
    │
    no
    ↓
CURRENT PASS + required acceptance evidence
    ↓
merge/accept according to project policy
```

The exact ordering of optional Codex runs may evolve, but Codex is an evidence source, not the authority that defines MimiSeek quality.

## Review identity

Every semantic review run must bind to immutable review identity including at least repository, base SHA, and head SHA. A material change to HEAD invalidates older exact-head terminal evidence for the new HEAD.

## Finding disposition

A finding is an assertion until adjudicated.

Minimum dispositions:

- `CONFIRMED`: defect is accepted as real under governing semantics;
- `REJECTED`: evidence falsifies the finding;
- `SUPERSEDED`: later code/state makes the finding no longer the operative item without pretending the earlier assertion was evaluated on the new HEAD.

Additional states may be added only with clear semantics.

## Cross-chat continuity

Do not create `HANDOFF-<date>.md`, chat transcripts, daily logs, or duplicate current-state files.

At the end of significant work:

- commit code/tests;
- update the canonical owner whose truth changed;
- update `CURRENT_STATE` when project position changes;
- update `EVIDENCE_INDEX` when accepted evidence changes;
- record a decision only for durable architectural choices;
- ensure the PR body explains the proposed change and acceptance evidence.

Git history and PR discussion carry chronology. Canonical documents carry current truth.

## Safety of self-development

Changes to reviewer behavior use the same development discipline as other code. A learner-generated candidate is still just a proposed change until the evaluation path authoritatively accepts it.
