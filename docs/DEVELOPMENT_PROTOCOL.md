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

## Normal MimiSeek implementation cycle

```text
implement one roadmap slice
    ↓
development-chat verification
    ↓
tests / CI
    ↓
independent review according to MimiSeek repository policy
    ↓
adjudicate + fix confirmed findings
    ↓
CURRENT exact-head acceptance evidence
    ↓
merge
    ↓
update CURRENT_STATE / ROADMAP / EVIDENCE_INDEX as applicable
```

Consumer repositories may use different local review sequences. MimiSeek only consumes their accepted structured outcomes through the integration contract.

## Evolution pipeline versus development pipeline

The product's evolution pipeline is started by `.agents/skills/mimiseek-evolve/SKILL.md`:

`collect → normalize → learn → candidate → regression → fresh evaluation → promote/reject/abstain → distribute`.

Do not confuse that product pipeline with development of MimiSeek's own implementation.

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
