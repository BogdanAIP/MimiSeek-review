# 0013 — Preserve PR-level reactions as separate source evidence

## Context

GitHub-native review evidence is not always expressed as a review body or inline finding. In particular, an automated reviewer may signal a clean result only through a pull-request reaction. If MimiSeek collected only comments/reviews, the resulting corpus would over-represent FINDINGS-shaped runs and silently lose reaction-only clean-review evidence.

Reactions can also arrive after the PR metadata snapshot was last refreshed, so tying reaction collection only to the PR `updated_at` watermark is insufficient.

## Decision

During the Stage 1 intake foundation, preserve pull-request-level reactions in a separate deterministic raw snapshot:

`evidence/github/<owner>/<repo>/pull-reactions/<pr-number>.json`

The reaction collector rechecks every already-known PR snapshot on each scheduled intake run. It is read-only against consumers and uses the same bounded GitHub App token as the main source collector.

Reaction snapshots are non-authoritative source evidence. A `+1` is not itself a PASS. Later governed normalization must prove reviewer identity, timing, exact review head where possible, and the relevant source semantics before interpreting a reaction as a clean review result. Absence of a reaction is never a miss/finding signal.

## Consequences

- Reaction-only clean-review signals are no longer silently dropped.
- Late reactions are recoverable even when PR `updated_at` is unchanged.
- Raw PR source snapshots remain deterministic and independently refreshable; reaction churn does not force them into a different watermark model.
- The initial implementation intentionally captures PR-level reactions only. Comment-level reactions may be added later as an additional evidence source without changing the authority rule above.
