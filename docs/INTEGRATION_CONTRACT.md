# Integration Contract

## Goal

Allow CAP, UV, and future repositories to consume one standalone stable MimiSeek reviewer and to contribute trustworthy review outcomes back to MimiSeek's learning system.

## Responsibility split

### MimiSeek Review owns

- generic reviewer methodology/artifact;
- reviewer version identity;
- cross-project normalized learning data;
- historical regression corpus;
- learning-event derivation;
- learner and candidate lifecycle;
- candidate evaluation and promotion protocol;
- release of stable reviewer versions;
- distribution of stable-version update PRs to registered consumers.

### Consumer repository owns

- its development and ordinary review/fix workflow;
- project architecture truth;
- project-specific `AGENTS.md` and acceptance/security constraints;
- exact PR/BASE/HEAD identity;
- finding adjudication under its governing semantics;
- project-local policy overlay and document owners;
- production decision whether an update PR can merge under that project's own acceptance rules.

## Consumer binding

A consumer must identify the exact MimiSeek stable reviewer it uses. The machine-readable binding must include at least:

- reviewer version;
- immutable MimiSeek commit/content identity;
- compatibility/policy version where required.

## Evidence export

Consumers must eventually expose structured evidence sufficient for MimiSeek to reconstruct learning outcomes without chat history, including when available:

- review-run identity and reviewer version/source;
- exact repository/base/head identity;
- findings and severity/category;
- disposition (`CONFIRMED`, `REJECTED`, `SUPERSEDED`);
- discovery source (MimiSeek, Codex, development, other);
- fix and verified head;
- terminal PASS/currentness evidence.

Missing or ambiguous evidence must remain unknown; MimiSeek may not manufacture a HIT/MISS from absence alone.

## Project overlays

The common reviewer must read and obey project-local policy. Generic methodology must not overwrite project-specific owners.

A stricter project-local rule remains authoritative for that project unless the integration contract explicitly makes the combination incompatible.

## Stable update distribution

After `PROMOTE`, MimiSeek's distributor prepares a separate auditable version-update change for each registered compatible consumer.

Default behavior:

```text
MimiSeek stable vN → vN+1
    ↓
consumer A update PR
consumer B update PR
consumer C update PR
```

Do not silently push a reviewer update directly to a consumer's stable branch.

A consumer may remain pinned when compatibility cannot be established; that state must be explicit and visible to MimiSeek.

## Failure behavior

Fail closed on:

- unresolved/mismatched reviewer identity;
- missing required project policy;
- incompatible policy/reviewer versions;
- stale exact-head result presented as current evidence;
- ambiguous finding disposition;
- attempted automatic distribution without an authoritative promotion result.
