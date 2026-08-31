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
