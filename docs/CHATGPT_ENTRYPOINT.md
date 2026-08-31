# ChatGPT Entry Point

## User contract

MimiSeek Review exposes one primary user workflow in ChatGPT: the `mimiseek-evolve` skill.

Intended user interaction:

> Запусти `mimiseek-evolve`.

or an equivalent explicit invocation naming the skill.

The user should not have to manually sequence collector, learner, regression, evaluator, promotion, or distribution steps.

## Full skill pipeline

```text
invoke mimiseek-evolve
    ↓
resolve MimiSeek live state
    ↓
collect new consumer evidence
    ↓
normalize + derive learning events
    ↓
create candidate when evidence supports a useful change
    ↓
run regression / protected-capability evaluation
    ↓
launch NEW isolated ChatGPT evaluator context
    ↓
PROMOTE / REJECT / ABSTAIN
    ↓
PROMOTE only: update stable registry
    ↓
create consumer reviewer-update PRs
    ↓
persist run/evidence/current state
```

## Fresh-context requirement

Promotion semantic evaluation must occur in a new isolated ChatGPT context. Reusing the learner/development chat is not equivalent.

The orchestration layer therefore needs a capability that can create a fresh ChatGPT chat/context, submit the evaluator request, and return the structured evaluator result.

MimiSeek must define this as an adapter/capability contract rather than hard-depend on CAP. CAP or another executor may implement the contract.

Until such an executor is available and proven, `mimiseek-evolve` must stop before promotion with stable unchanged. It must not silently substitute same-chat evaluation.

## Idempotence

Repeated invocation with no new evidence and no pending candidate should be a safe no-op.

Interrupted runs must resume from durable pipeline state rather than duplicating imported evidence, creating duplicate candidates, or distributing the same stable update twice.

## Authority

The orchestration skill coordinates the pipeline but does not gain the learner's or evaluator's semantic authority. It may only perform each transition when the corresponding role's durable result satisfies the governing contract.
