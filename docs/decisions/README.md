# Architectural Decisions

Use a decision record only for durable architectural choices that future chats might otherwise repeatedly reopen or accidentally reverse.

Each record contains:

- Context
- Decision
- Consequences
- Supersedes, when applicable

Chronology belongs in Git/PR history, not here.

Current records:

- `0001-standalone-multi-project-reviewer.md`
- `0002-repository-state-over-chat-handoff.md`
- `0003-stable-candidate-separation.md`
- `0004-fresh-independent-promotion-evaluator.md`
- `0005-evaluation-policy-separation.md`
- `0006-evolution-system-not-consumer-review-orchestrator.md`
- `0007-two-chat-two-skill-evolution.md`
- `0008-fresh-evaluator-replaces-routine-human-technical-promotion.md`
- `0009-consumer-safe-update-windows.md`
- `0010-base-policy-governs-pr-acceptance.md`
- `0011-no-bootstrap-bypass-for-first-stable-or-install.md`
- `0012-continuous-evidence-before-baseline.md`
