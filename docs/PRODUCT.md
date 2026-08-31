# Product

## Purpose

MimiSeek Review is a standalone, multi-project **reviewer improvement and release system**.

Its job is not to run the normal review/fix loop inside CAP, UV, or another consumer repository. Those repositories continue to perform their own development and review workflows.

MimiSeek Review consumes verified outcomes from those workflows, learns from them, produces a better reviewer candidate, independently evaluates that candidate, and publishes a new stable reviewer when improvement is sufficiently proven.

The core product loop is:

```text
consumer review outcomes
    ↓
collect + normalize
    ↓
learning events
    ↓
learner
    ↓
candidate reviewer
    ↓
regression / protected-capability evaluation
    ↓
fresh independent ChatGPT evaluator
    ↓
PROMOTE / REJECT / ABSTAIN
    ↓
new stable reviewer when PROMOTE
    ↓
auditable update PRs to consumers
```

## Learning sources

MimiSeek should learn from:

- its own confirmed findings;
- its own misses;
- its own rejected/false-positive findings;
- confirmed Codex findings it missed;
- confirmed defects found by development work or other reviewers;
- Codex misses and rejected findings as negative or complementary evidence;
- historical BUGGY→FIXED regression cases;
- new real-world outcomes from CAP, UV, and future consumers;
- later external benchmarks and holdouts.

The goal is not to prove that one reviewer is universally better than another. Codex and other reviewers are evidence sources from which MimiSeek may acquire transferable review mechanics or falsification lessons.

## Consumers

Initial consumers:

- `BogdanAIP/chat-agent-platform`
- `BogdanAIP/uv-studio`

Future repositories must be attachable without embedding CAP- or UV-specific assumptions in the generic reviewer.

## User-facing entry point

The intended ChatGPT interface is one repository skill: `mimiseek-evolve`.

The user should be able to invoke that skill and let the system execute the full improvement pipeline. Internal roles may remain separate for authority and isolation, but they are not separate user workflows.

See `docs/CHATGPT_ENTRYPOINT.md` and `.agents/skills/mimiseek-evolve/SKILL.md`.

## Product principles

1. **Improve the reviewer, not the leaderboard.** Comparative reviewer data exist to teach MimiSeek.
2. **Repository state, not chat memory.** New chats recover state from Git/GitHub and canonical persisted data.
3. **Generic learning, project-local policy.** Transferable review mechanics live here; project-specific governance stays with the consumer.
4. **Ground truth is adjudicated evidence.** Reviewer agreement is not ground truth.
5. **Exact-head semantics.** Review outcomes used as evidence are bound to immutable repository identity.
6. **Self-improvement is gated.** Learning may create a candidate; it may not declare that candidate stable.
7. **No self-defined exam.** A candidate and learner cannot weaken or rewrite the policy used to evaluate that candidate.
8. **Preserve acquired strengths.** Improvements must not silently destroy previously demonstrated capabilities.
9. **False positives matter.** More findings alone are not improvement.
10. **Distribution is auditable.** A promoted stable reviewer is propagated to consumers by explicit versioned changes, normally update PRs.

## Non-goals

- Orchestrating the ordinary code-review/fix cycle inside every consumer repository.
- Training or fine-tuning model weights in the initial system.
- Replacing consumer `AGENTS.md`, architecture owners, or acceptance policy.
- Ranking Fresh ChatGPT versus Codex as the central objective.
- Majority voting between reviewers as a truth mechanism.
- Allowing a learner or candidate to certify itself.
