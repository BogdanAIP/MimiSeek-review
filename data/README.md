# Data

This directory contains MimiSeek Review's canonical machine-readable bootstrap/learning/regression data. Non-authoritative live GitHub intake is stored separately on branch `evidence/github-intake`; it is source evidence, not canonical adjudicated truth.

## Bootstrap source

The audited historical CAP/UV reviewer-statistics workbook used to bootstrap Stage 1 is durably identified by `data/bootstrap-source.json`.

That manifest is the sole owner of the exact access-controlled Library path/version, byte size, SHA-256, recovery contract, and declared BUGGY→FIXED reconciliation target. A fresh authorized chat must recover that exact artifact and verify the manifest before trusting a bootstrap import. Failure to recover/authenticate it is fail-closed.

The workbook remains a bootstrap/provenance artifact, not the ongoing automation store.

## Canonical bootstrap datasets

Stage 1 imports the authenticated workbook into deterministic JSON Lines datasets:

- `review-runs.jsonl` — normalized historical reviewer executions and exact review identity;
- `findings.jsonl` — historical finding observations, disposition/provenance fields, and source identity;
- `regression-cases.jsonl` — historical BUGGY→FIXED target cases and evidence refs.

Their positional field contracts are versioned under `data/schemas/`. `data/bootstrap-import-report.json` records source authentication, counts, hashes, internal reconciliation, and explicitly unfinished provenance work. It is derived verification evidence, not a competing source-identity owner.

`learning-events.jsonl` does not exist yet. Learning events belong to Stage 4 and must not be fabricated during bootstrap.

## Continuous GitHub evidence intake

The bounded Stage 1 intake foundation polls repositories registered in `config/consumers.json` and stores deterministic per-PR source snapshots on branch:

`evidence/github-intake`

Typical paths:

- `evidence/github/<owner>/<repo>/pulls/<pr-number>.json` — PR metadata, comments, reviews, review comments and commits;
- `evidence/github/<owner>/<repo>/pull-reactions/<pr-number>.json` — PR-level reactions captured separately so late reactions and reaction-only clean-review signals are not lost.

Collector state/watermarks live alongside those snapshots on the intake branch.

The intake branch is deliberately **non-authoritative**:

- it preserves source GitHub facts/comments/reviews/commits/reactions;
- it does not decide that a finding is confirmed merely because text says so;
- it does not interpret a `+1` reaction as a clean review unless later governed normalization proves reviewer identity and timing;
- it does not convert absence into a reviewer miss;
- it does not create learning events, candidate state, stable state, or promotion authority;
- it may overlap the bootstrap workbook and later normalization must deduplicate by immutable GitHub/source identity.

The collectors are implemented by `tools/collect_github_evidence.py` and `tools/collect_github_pr_reactions.py` and scheduled by `.github/workflows/collect-review-evidence.yml`. Reliable scheduled operation requires the dedicated read-only GitHub App credentials described by ADR 0012.

Stage 2 will add the structured consumer evidence-export contract required to make fresh ordinary-ChatGPT terminal results automatically recoverable from consumer GitHub state. Stage 3 will complete normalized operational collector/outcome-store semantics.

## Rules

- Source evidence remains traceable to exact repository/PR/comment/review/commit/reaction identities.
- Imports and collection are idempotent.
- Unknown stays unknown.
- Different HEADs are not silently collapsed into direct reviewer comparisons.
- Generated reports and raw intake snapshots do not become competing truth owners.
- Incomplete/truncated API evidence fails closed.
- A baseline seed may not be derived merely because files exist; Stage 1 provenance/policy/classification requirements must also be satisfied.
