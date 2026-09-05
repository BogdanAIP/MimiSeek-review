# Development Repeat Prevention

Status: explanatory reference only; non-authoritative.

## Purpose

This page explains the MimiSeek self-development repeat-prevention artifacts and why they exist. The **sole normative owner** of the cross-chat MimiSeek development process is `docs/DEVELOPMENT_PROTOCOL.md`. If this page ever conflicts with that protocol, the protocol governs and this page is stale documentation.

The design goal is simple: a confirmed material MimiSeek development defect should leave durable, preferably executable protection rather than relying on chat memory or a local one-off fix.

## Artifact map

The machine registry is:

`data/development-failure-patterns.jsonl`

Each non-empty line uses schema identity:

`DEVELOPMENT_FAILURE_PATTERN_V1`

Shape documentation:

`data/schemas/development-failure-pattern-v1.schema.json`

Executable registry validator:

`tools/validate_development_failure_patterns.py`

The validator checks machine shape and local repository references. Current path authority is intentionally Git-bound: prevention refs, discovered instances, and search-scope matches resolve only to tracked regular files from the Git index; `.git` metadata, untracked checkout files, and tracked symlinks do not count as repository artifacts.

## Scope boundary

This registry is limited to development of `BogdanAIP/MimiSeek-review` itself. It is separate from the future reviewer-evolution defect-pattern/counterexample architecture described in research documents.

It does not itself create:

- Stage 4 learning events;
- baseline/candidate/stable reviewer state;
- consumer-project adjudication authority;
- consumer installation/distribution state;
- `REVIEW_JOB_V1` or `REVIEW_RESULT_V1` semantics.

Any future use of these records as reviewer-learning input needs separately accepted authority.

## Current pattern inventory

The initial accepted target state of PR #21 contains three self-development failure classes:

- `DFP-0001` — `evidence.semantic_binding_missing`: claim-bearing free-form evidence can be identity-authenticated without binding the actual semantic body. Its repository search is currently `BOUNDED_FOLLOW_UP` because PR #21 found additional same-class commentary verifiers; durable closure is tracked in issue #22.
- `DFP-0002` — `repository.reference_not_git_bound`: checkout filesystem existence can be mistaken for durable tracked repository authority.
- `DFP-0003` — `governance.duplicate_canonical_owner`: one cross-chat process can accidentally be defined normatively in multiple mutable documents.

The registry itself, the exact origin evidence, and `docs/DEVELOPMENT_PROTOCOL.md` carry the authoritative machine/process details. This page only provides orientation.

## Why `DFP-0001` is not marked complete

The original PR #20 remediation hardened `tools/verify_bootstrap_commentary_authority_ci_reconciliation.py`, but the broader semantic search performed during PR #21 found additional same-class current instances in:

- `tools/verify_bootstrap_commentary_fix_baseline_reconciliation.py`;
- `tools/verify_bootstrap_commentary_fix_evidence_reconciliation.py`.

Issue #22 records the bounded follow-up. The registry therefore exposes that incomplete search state instead of claiming repository-wide closure prematurely.

## Relationship to ordinary acceptance

Repeat-prevention artifacts are additional self-development protection, not a substitute for the repository's existing exact-head independent acceptance workflow. The governing workflow and all consequences of a HEAD-changing remediation remain defined only in `docs/DEVELOPMENT_PROTOCOL.md`.
