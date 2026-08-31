# Product

## Purpose

MimiSeek Review is a standalone, multi-project reviewer that improves over time from verified outcomes of real development work.

Its primary optimization target is the quality of MimiSeek Review itself. It should learn from:

- its own confirmed findings;
- its own misses;
- its own rejected/false-positive findings;
- confirmed Codex findings it missed;
- confirmed defects found by development work or other reviewers;
- Codex misses and rejected findings as negative or complementary evidence;
- historical BUGGY→FIXED regression cases;
- later external benchmarks and holdouts.

The goal is not to prove that one reviewer is universally better than another. Codex and other reviewers are sources of useful evidence from which MimiSeek Review can acquire transferable review mechanics.

## Consumers

Initial consumers:

- `BogdanAIP/chat-agent-platform`
- `BogdanAIP/uv-studio`

The design must support future repositories without embedding CAP- or UV-specific assumptions in the generic reviewer.

## Product principles

1. **Repository state, not chat memory.** New chats must recover project state from Git/GitHub and canonical documents.
2. **Generic learning, project-local policy.** Generic review mechanics may transfer across projects; project-specific architecture and acceptance policy stay with the project.
3. **Ground truth is adjudicated evidence.** Reviewer agreement is not ground truth.
4. **Exact-head semantics.** Review results are bound to immutable repository identity.
5. **Self-improvement is gated.** Learning may create a candidate; an independent evaluation path decides whether it becomes stable.
6. **No self-defined exam.** A candidate cannot weaken or rewrite the policy used to evaluate itself.
7. **Preserve acquired strengths.** Improvements must not silently destroy previously demonstrated review capabilities.
8. **False positives matter.** More findings alone are not improvement.

## Non-goals for the initial implementation

- Training or fine-tuning model weights.
- Replacing project-specific `AGENTS.md` or acceptance policy.
- Ranking Fresh ChatGPT versus Codex as the central product objective.
- Majority voting between reviewers as a truth mechanism.
- Automatic production promotion before the evaluation path itself is implemented and proven.
- Building a large service before the minimal cross-project reviewer contract works end to end.
