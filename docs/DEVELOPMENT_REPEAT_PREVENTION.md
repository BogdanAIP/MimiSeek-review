# Development Repeat Prevention

Status: explanatory reference only; non-authoritative.

## Purpose

This page explains why MimiSeek has self-development repeat-prevention artifacts and where to find their canonical owners. The **sole normative owner** of the cross-chat MimiSeek development process is `docs/DEVELOPMENT_PROTOCOL.md`. If this page ever conflicts with that protocol, the protocol governs and this page is stale documentation.

The design goal is simple: a confirmed material MimiSeek development defect should leave durable, preferably executable protection rather than relying on chat memory or a local one-off fix.

## Artifact map

Canonical machine state:

`data/development-failure-patterns.jsonl`

Schema identity and shape documentation:

`data/schemas/development-failure-pattern-v1.schema.json`

Exact-HEAD development finding adjudication records used to establish which reviewer findings are eligible to seed or extend the self-development registry:

`data/development-finding-adjudications.jsonl`

Adjudication record schema:

`data/schemas/development-finding-adjudication-v1.schema.json`

Executable registry validator:

`tools/validate_development_failure_patterns.py`

Normative process rules, including development-start retrieval, repository-search states, prevention requirements, repeat classification, retirement constraints, and repository write hygiene:

`docs/DEVELOPMENT_PROTOCOL.md`

The machine validator reads the canonical registry, its schema, and finding-adjudication state from the exact checked-out Git `HEAD`. Acceptance CI additionally binds the checkout to the immutable PR head and resolves issue-based bounded follow-ups. A review-comment locator by itself is not confirmation; eligible reviewer-finding records require a separate exact-HEAD `CONFIRMED` adjudication record.

This page intentionally does **not** copy the current pattern count, pattern identities, live search statuses, follow-up issue numbers, adjudication inventory, or occurrence inventory. Those are mutable machine facts owned by the JSONL records and should be inspected from their canonical sources rather than manually synchronized here.

## Scope boundary

The registry is limited to development of `BogdanAIP/MimiSeek-review` itself. It is separate from the future reviewer-evolution defect-pattern/counterexample architecture described in research documents.

It does not itself create:

- Stage 4 learning events;
- baseline/candidate/stable reviewer state;
- consumer-project adjudication authority;
- consumer installation/distribution state;
- `REVIEW_JOB_V1` or `REVIEW_RESULT_V1` semantics.

Any future use of these records as reviewer-learning input needs separately accepted authority.

## Relationship to ordinary acceptance

Repeat-prevention artifacts are additional self-development protection, not a substitute for the repository's existing exact-head independent acceptance workflow. The governing workflow and all consequences of a HEAD-changing remediation remain defined only in `docs/DEVELOPMENT_PROTOCOL.md`.
