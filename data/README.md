# Data

This directory will contain MimiSeek Review's canonical machine-readable learning and regression data.

## Bootstrap source

The existing audited reviewer-statistics workbook built from CAP and UV history is the initial import source. It currently contains the historical review runs/findings and 84 BUGGY→FIXED regression pairs assembled before this repository existed.

The workbook is **not** intended to remain the only canonical store because binary spreadsheets are difficult to diff, merge, validate, and consume safely from automation.

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
