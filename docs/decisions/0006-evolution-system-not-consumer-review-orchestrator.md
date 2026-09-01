# ADR 0006 — MimiSeek evolves the reviewer; consumers run their own review workflows

## Context

Early bootstrap wording risked mixing two different responsibilities: running CAP/UV PR review/fix loops and improving the reusable reviewer itself.

## Decision

MimiSeek Review owns collection, learning, candidate generation, evaluation, stable release, and distribution of the generic reviewer.

CAP, UV, and future repositories own their ordinary development/review/fix workflows and contribute structured adjudicated outcomes to MimiSeek.

## Consequences

- MimiSeek remains reusable across projects.
- Consumer-specific sequencing does not become hard-coded into the reviewer-improvement system.
- The same reviewer can learn across multiple projects while retaining local project policy overlays.
