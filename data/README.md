# Data

This directory will contain MimiSeek Review's canonical machine-readable learning and regression data.

## Bootstrap source

The audited historical CAP/UV reviewer-statistics workbook used to bootstrap Stage 1 is durably pinned in this repository at:

`reports/bootstrap/reviewer_statistics_improvement_dataset.xlsx`

Its repository bootstrap identity is recorded in `data/bootstrap-source.json`. The pinned snapshot has SHA-256:

`6fe79a73a7f10e528a7323adce1fafcc1951955394a0dbece31a5eec73d6391a`

Stage 1 must resolve the workbook from the accepted Stage 0 Git commit, verify this digest before importing it, and independently reconcile the declared 84 BUGGY→FIXED cases and other counts against the workbook contents and underlying GitHub evidence. A count in documentation or the manifest is an expected reconciliation target, not a substitute for import verification.

The workbook is **not** intended to remain the canonical automation store because binary spreadsheets are difficult to diff, merge, validate, and consume safely from automation. Its purpose is an immutable bootstrap input/provenance snapshot.

## Planned canonical datasets

At minimum:

- `review-runs.jsonl` — normalized reviewer executions and immutable review identity;
- `findings.jsonl` — finding observations and adjudicated disposition/provenance;
- `regression-cases.jsonl` — BUGGY→FIXED target cases and evidence refs;
- `learning-events.jsonl` — derived OUR/Codex/development success/miss/false-positive events;
- versioned schemas for each dataset.

Exact schema is a Stage 1 deliverable.

## Rules

- Source evidence must remain traceable.
- Imports are idempotent.
- Unknown is preserved as unknown.
- Different HEADs are not silently collapsed into direct reviewer comparisons.
- Generated reports must not become competing truth owners.
- The bootstrap workbook digest must be verified before Stage 1 import/reconciliation.
