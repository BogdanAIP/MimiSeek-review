# Integration Contract

## Goal

Allow CAP, UV, and future repositories to consume one standalone MimiSeek Review while preserving each repository's local governance.

## Responsibility split

### MimiSeek Review owns

- generic review engine/methodology;
- reviewer version identity;
- generic learning mechanics;
- learning history and regression infrastructure;
- candidate creation lifecycle;
- evaluation/promotion protocol.

### Consumer repository owns

- project architecture truth;
- project-specific `AGENTS.md`;
- project-specific acceptance/security constraints;
- applicable target skills and document owners;
- exact PR/BASE/HEAD identity;
- whether a reviewer version is permitted by that project's compatibility policy.

## Required consumer binding

A consumer must be able to identify the exact MimiSeek stable version it uses. The binding must eventually include at least:

- reviewer version;
- immutable MimiSeek commit/hash or equivalent content identity;
- compatibility/policy version where needed.

The concrete lock-file format is a Stage 1 deliverable and must be machine-readable.

## Project overlays

The common reviewer must read and obey project-local policy. Generic methodology must not overwrite local owners.

If a project requires stricter behavior than the generic reviewer, the stricter project policy governs that project unless the integration contract explicitly forbids the combination.

## Updates

A new MimiSeek stable version does not silently rewrite every consumer. Consumers must have an auditable update path.

The final policy may support controlled auto-update classes, but initial integration should prefer explicit exact-version pins until compatibility behavior is proven.

## Failure behavior

Fail closed on:

- unresolved/mismatched reviewer identity;
- missing required project policy;
- incompatible policy/reviewer versions;
- stale exact-head result being presented as current;
- ambiguous authority over which policy is governing.
