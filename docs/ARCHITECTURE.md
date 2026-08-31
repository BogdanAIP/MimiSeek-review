# Architecture

## System boundary

MimiSeek Review is a standalone system. CAP, UV, and future repositories are consumers, not owners of the generic reviewer implementation.

## Logical components

### Reviewer

Runs an independent semantic review against an immutable review identity and the consuming repository's governing policy.

Authority:

- may inspect allowed evidence;
- may emit structured review results/findings;
- may not adjudicate its own findings as ground truth;
- may not promote a reviewer candidate.

### Outcome store

Persists review runs, findings, dispositions, identities, and later fix/verification evidence.

Its purpose is reconstruction and learning, not rewriting project history.

### Learning event builder

Derives evidence-backed events from adjudicated outcomes, such as OUR_HIT or OUR_MISS_CODEX_HIT.

### Learner

Analyzes learning events and proposes transferable changes to reviewer behavior.

Authority:

- may produce a candidate reviewer and rationale;
- may not redefine the candidate's evaluation policy;
- may not make a candidate stable.

### Regression corpus

Contains real BUGGY→FIXED cases and protected-capability cases. It is development/regression evidence, not an external blind benchmark.

### Evaluator

Separately governed path that determines whether a candidate has sufficient evidence for `PROMOTE`, must `REJECT`, or must `ABSTAIN`.

The evaluator role is intended to run in a fresh independent ordinary-chat context for semantic promotion evaluation.

### Version registry

Identifies stable/candidate reviewer versions and their immutable implementation/policy refs.

### Consumer adapter/contract

Binds a consuming repository to an exact reviewer version while retaining project-specific policy locally.

## Authority separation

```text
real projects
    |
    v
stable reviewer ----> review outcomes ----> learning events
                                            |
                                            v
                                         learner
                                            |
                                            v
                                         candidate
                                            |
                           fixed evaluation policy + corpus
                                            |
                                            v
                                     fresh evaluator
                                  /        |        \
                           PROMOTE      REJECT     ABSTAIN
                              |
                              v
                         new stable
```

No single mutable reviewer candidate owns every arrow in this loop.

## Generic versus project-specific knowledge

A rule may enter the generic reviewer only when it is transferable beyond the originating project.

Example generic mechanic:

> For a modified durable object, enumerate all independent writers and prove they share the intended serialization/authority boundary.

Example project-specific rule:

> A particular CAP procedure must use a named receipt or a UV architecture document is the owner of a specific product state.

Project-specific rules stay in the consumer repository's policy/overlay.

## Durable state principle

Chat contexts are execution environments, not state stores. Canonical project state, reviewer versions, evidence, decisions, and accepted policy must be recoverable from repositories and structured persisted data.
