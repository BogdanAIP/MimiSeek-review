# ADR 0001 — Standalone multi-project reviewer

## Context

The reviewer is used across `chat-agent-platform` and `uv-studio` and should also be reusable by future repositories. Owning the generic reviewer inside either current project would couple its evolution to one consumer.

## Decision

MimiSeek Review is a standalone repository and product. Consumer repositories retain local project-specific policy and pin/use stable MimiSeek reviewer versions through an explicit integration contract.

## Consequences

- Learning from one project can improve review mechanics for other projects when the mechanic is genuinely generic.
- CAP/UV-specific rules must not leak into the generic reviewer without abstraction.
- Version distribution and compatibility become explicit responsibilities of MimiSeek Review.
