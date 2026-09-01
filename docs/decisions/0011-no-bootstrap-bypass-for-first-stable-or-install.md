# ADR 0011 — First stable and first installation use normal governed paths

## Context

The initial roadmap attempted to establish a first stable reviewer in Stage 1 and require CAP/UV reviewer pins in Stage 2, while the general candidate-promotion and safe-distribution mechanisms were scheduled for later stages.

That ordering created ambiguous bootstrap authority: either early stages would stall under fail-closed rules or they would need special shortcuts that bypassed the same promotion/distribution boundaries MimiSeek is intended to protect.

## Decision

Do not create bootstrap shortcuts for either first stable admission or first consumer installation.

- Stage 1 may derive an immutable **baseline seed**, but it is non-authoritative, non-stable, and non-distributable.
- Stage 5 creates the first eligible candidate through the normal candidate-generation path.
- Stage 6 evaluates/freezes that candidate under the normal regression/protected-capability gate. When no stable exists, evaluation uses fixed first-promotion requirements and must not fabricate a stable comparison.
- Stage 7 uses the normal fresh independent `PROMOTE / REJECT / ABSTAIN` workflow. If `stable_before = none`, authoritative `PROMOTE` establishes the first stable; otherwise stable remains unset on `REJECT`/`ABSTAIN`.
- Stage 2 establishes consumer binding/evidence schemas only and may represent `consumer_installed = none`.
- Stage 8 is the first point where a consumer reviewer pin may be changed solely to install MimiSeek, and that first installation uses the same fresh-update-chat + authoritative-promotion + `SAFE_TO_UPDATE` requirements as later updates.

## Consequences

- The first stable cannot bypass independent promotion authority.
- The first CAP/UV installation cannot bypass consumer safe-update authority.
- `stable = none` and `consumer_installed = none` are explicit valid bootstrap states rather than implicit errors.
- Historical/pre-installation CAP/UV review evidence can still be collected when reviewer source/version and provenance are explicit.
- Later self-improvement uses the same authority model established for the first real release and rollout.
