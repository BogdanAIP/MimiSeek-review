# Product

## Purpose

MimiSeek Review is a standalone, multi-project **reviewer improvement and release system**.

Its job is not to run the normal review/fix loop inside CAP, UV, or another consumer repository. Those repositories continue to perform their own development and review workflows.

MimiSeek Review consumes verified outcomes from those workflows, learns from them, produces a reviewer candidate, independently evaluates that candidate, and publishes a new stable reviewer only when the governed promotion policy authorizes it.

Before the first promotion, MimiSeek intentionally has **no stable reviewer**. Bootstrap may create historical data and a non-authoritative baseline seed, but the first stable must pass the same candidate → independent evaluation → `PROMOTE` authority path used for later versions. Likewise, the first CAP/UV installation must pass the same per-consumer safe-distribution gate used for later updates.

The operational product loop is:

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
frozen independent-update state
    ↓
NEW CHAT: independent evaluator
    ↓
PROMOTE / REJECT / ABSTAIN
    ↓
new stable reviewer when PROMOTE
    ↓
per-consumer live safe-update evaluation
    ↓
auditable first-install/update PR/change only where safe
```

Global reviewer promotion and installation into a consumer are separate transactions. A promoted stable reviewer may exist while one or more consumers intentionally remain uninstalled or pinned to an older stable until their current project state proves an update safe.

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

Registration as a consumer/evidence producer does not imply that MimiSeek is already installed. Before Stage 8, `consumer_installed = none` is a valid and expected state.

## User-facing ChatGPT workflows

MimiSeek Review exposes two separate user-facing ChatGPT roles.

### Run / development / learning

Native skill identity: `mimiseek-review-run`.

Canonical repository workflow: `.agents/skills/mimiseek-run/SKILL.md`.

The run chat reconstructs live repository state and continues the next canonical work. During bootstrap this means continuing MimiSeek Review implementation according to `CURRENT_STATE.md`, `ROADMAP.md`, and repository governance. Once the reviewer-learning machinery exists, the same entry point performs the governed collection/learning/candidate/regression half and freezes the state required for independent evaluation.

The run chat may not make its own candidate stable and may not treat a baseline seed or candidate as authority to update consumers.

### Independent update

Native skill identity: `mimiseek-review-update`.

Canonical repository workflow: `.agents/skills/mimiseek-update/SKILL.md`.

This workflow runs in a new independent chat when the repository contains an eligible candidate/update package or an already-promoted stable has deferred consumer distributions to reconcile. It independently evaluates promotion under the fixed governing policy and then evaluates each consumer's current live safe-update window before any rollout.

The same workflow establishes the first stable when `stable_before = none` and an authoritative `PROMOTE` is returned; there is no separate bootstrap admission path.

Repository state is the durable handoff between the two chats. The user must not need to copy a technical evaluation prompt from the run chat into the update chat.

See `docs/CHATGPT_ENTRYPOINT.md`, `docs/REVIEWER_LIFECYCLE.md`, and `docs/INTEGRATION_CONTRACT.md`.

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
10. **Distribution is auditable and safety-gated.** A promoted stable reviewer is propagated only through explicit versioned changes when each consumer's live state permits the update.
11. **Running work is immutable.** An already-started agent/reviewer/procedure run remains bound to the reviewer version/source with which it started.
12. **No bootstrap bypass.** The first stable and first consumer installation use the same promotion/distribution authorities as later versions.

## Non-goals

- Orchestrating the ordinary code-review/fix cycle inside every consumer repository.
- Training or fine-tuning model weights in the initial system.
- Replacing consumer `AGENTS.md`, architecture owners, or acceptance policy.
- Ranking Fresh ChatGPT versus Codex as the central objective.
- Majority voting between reviewers as a truth mechanism.
- Allowing a learner, candidate, or bootstrap baseline seed to certify itself.
- Forcing every consumer to adopt a newly promoted stable reviewer at the same time.
