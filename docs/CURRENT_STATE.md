# Current State

Last synchronized: 2026-09-01

## Repository state

- Project: MimiSeek Review
- Repository: `BogdanAIP/MimiSeek-review`
- Stable branch: `main`
- Development status: Stage 1 in progress — bootstrap data import + continuous evidence-intake foundation
- Stage 0 implementation foundation: accepted and merged
- Stable reviewer version: **not established yet**
- Bootstrap baseline seed: none
- Candidate reviewer version: none
- Registered initial consumers/evidence producers: `BogdanAIP/chat-agent-platform`, `BogdanAIP/uv-studio`
- Consumer MimiSeek installation: none yet; first installation is governed by Stage 8 safe distribution
- Native ChatGPT skill identities: `mimiseek-review-run` and `mimiseek-review-update`

Exact accepted-stage review/merge identities and chronology belong only in `docs/EVIDENCE_INDEX.md`. This file owns current position and next action.

## Stage 1 implementation reality

The Stage 1 implementation now has a proposed canonical bootstrap import and an early evidence-intake foundation:

- the pinned historical workbook was recovered and authenticated against `data/bootstrap-source.json`;
- `data/review-runs.jsonl`, `data/findings.jsonl`, and `data/regression-cases.jsonl` contain the proposed lossless bootstrap import;
- the import reconciles 92 review runs, 139 findings, and 84 unique regression cases internally, while complete commit-level provenance reconciliation remains unfinished;
- `tools/collect_github_evidence.py` provides deterministic read-only GitHub evidence polling for registered consumers;
- `.github/workflows/collect-review-evidence.yml` schedules hourly collection once the dedicated read-only GitHub App credentials are configured;
- source snapshots are written only to `evidence/github-intake`, which is **non-authoritative intake evidence** and is not the normalized outcome store;
- the intake backfill deliberately overlaps the bootstrap workbook so later normalization can deduplicate by immutable source identity rather than rely on an assumed perfect cutoff;
- `.github/workflows/ci.yml` provides the first repository unit-test workflow for collector/data contract code.

These changes do not create a baseline seed, candidate, stable reviewer, consumer installation, learning events, or promotion authority.

The full Stage 3 collector/outcome-store stage is **not** claimed complete. The early collector exists only to stop new evidence from being lost while Stage 1 and Stage 2 are implemented.

## Evidence gaps that remain

GitHub-native Codex reviews, PR comments, review comments, commits, and owner adjudication replies can be preserved automatically.

Fresh ordinary-ChatGPT terminal reviews that existed only inside ChatGPT and were never durably exported into the consumer PR cannot be reconstructed from GitHub alone. Stage 2 must define/implement structured consumer evidence export so future fresh terminal results are also captured automatically. Historical chat-only gaps must remain explicit rather than being inferred from absence.

## Next canonical action

Continue Stage 1, in this order:

1. accept and merge the bootstrap-data/evidence-intake foundation under the normal exact-head review policy;
2. run authenticated backfill for CAP/UV and verify the durable collector watermark/intake snapshots;
3. complete commit-level provenance reconciliation for imported BUGGY/FIXED/VERIFIED identities;
4. resolve exact accepted CAP/UV reviewer-policy refs;
5. classify generic versus project-specific rules;
6. only after the evidence set is current and reconciled, derive an immutable reusable **baseline seed** that is explicitly not stable and not distributable.

Stage 2 then adds structured consumer evidence export/binding, including durable fresh ordinary-ChatGPT result export. Stage 3 later completes the normalized operational collector/outcome-store contract.

All work uses normal post-bootstrap branch/PR acceptance. PR #1's bootstrap exception is no longer available.

## Open risks

- Loss of access to the exact pinned Library artifact must halt historical-source reconciliation until a governed replacement/provenance migration is accepted.
- Missing collector GitHub App credentials leave automatic intake unconfigured; do not pretend collection is active until a successful authenticated run records a watermark.
- Chat-only review evidence cannot be inferred from GitHub absence.
- A naive common baseline could silently lose CAP- or UV-specific obligations.
- Historical outcomes are selection-biased; they are learning/regression evidence, not a neutral leaderboard.
- First-promotion evaluation must later define fixed absolute requirements without fabricating a nonexistent stable comparison.
- Consumer safe-window detection must not infer safety from silence or absence of visible GitHub activity.
