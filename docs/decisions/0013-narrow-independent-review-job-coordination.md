# ADR 0013 — Narrow independent review-job coordination

## Context

Accepted ADR 0006 correctly separated MimiSeek's reviewer-evolution responsibilities from CAP/UV consumer development/review/fix workflows. That decision prevented MimiSeek from becoming a project-specific development orchestrator.

The desired operating model now also needs a reusable way to remove routine manual prompt/result shuttling when an exact consumer PR/HEAD is ready for independent review:

```text
originating project chat
    -> independent review request
    -> fresh Temporary Chat reviewer
    -> durable result
    -> originating project chat continues
```

Accepted research PR #14 (`docs/research/REVIEW_JOB_COORDINATION.md`) evaluated whether MimiSeek can coordinate that narrow review execution without taking ownership of consumer development consequences.

## Decision

Decision: **ACCEPT_NARROW**.

MimiSeek Review may own a project-neutral independent-review job control plane for an **explicitly requested immutable review target**.

For one review job MimiSeek may:

1. resolve and freeze exact repository/PR/BASE/HEAD/`review_policy_ref` identity;
2. create one immutable durable `REVIEW_JOB_V1` identity;
3. request one fresh qualified reviewer worker through a separately governed generic session/execution substrate;
4. receive only a result correlated to the exact job/execution identity;
5. re-resolve live source identity after result capture and classify movement/mismatch as stale;
6. persist the exact result durably in MimiSeek-owned GitHub state without modifying the reviewed consumer HEAD;
7. request one generic return/wake delivery to the originating project conversation through an opaque/private route contract;
8. stop at result handoff and return control to the consumer workflow.

The consumer repository remains authoritative for:

- when its PR/HEAD is ready to request review;
- project-local architecture and policy;
- finding adjudication;
- remediation/code changes;
- whether a new HEAD needs re-review;
- terminal acceptance evidence required by that repository;
- merge or other consequence-bearing acceptance actions.

A review-job `PASS` is therefore neither consumer merge authority nor MimiSeek reviewer-candidate promotion/distribution authority.

The external session/execution substrate remains generic. MimiSeek must not require it to know:

- UV Studio, MimiSeek Review, or chat-agent-platform project semantics;
- GitHub PR semantics;
- `PASS`/`FINDINGS` meaning;
- MimiSeek learning/promotion state;
- project-specific routing tables.

MimiSeek may rely only on separately accepted generic capabilities such as fresh qualified worker launch/result correlation and existing-session opaque return delivery with one-shot/recovery/no-blind-resend semantics.

Public GitHub review-job records must not expose raw browser/session identifiers, ChatGPT conversation capabilities, authentication secrets, or equivalent private authority. A return route stays private to the transport unless represented by an opaque reference proven non-authorizing by itself.

The existing CAP/UV source GitHub App remains read-only. Review-job/result publication must not widen source-repository permissions merely to write review results; the coordination copy belongs in MimiSeek-owned durable state.

Review-job coordination is a cross-cutting **Track R** and may be implemented in parallel with the remaining ordered reviewer-evolution stages once its own external prerequisites are independently verified. It does not mark Stage 1/2/3 complete and does not alter candidate → independent evaluation → promotion → safe distribution authority.

Track R may operate before a first MimiSeek stable exists, but each job must explicitly bind the actual reviewer profile/source and accepted project-local review authority rather than inventing a stable reviewer identity.

## Consequences

- MimiSeek can become the shared cross-project coordinator for independent review execution without becoming the owner of project development/fix/merge workflows.
- GitHub becomes the durable review-job/result handoff; chat delivery is a wake/resume mechanism rather than the only copy of the result.
- The same MimiSeek control plane can support UV, CAP, MimiSeek itself, and future projects without project-specific transport tables.
- CAP/session-runtime development remains independent and generic; MimiSeek must resolve exact accepted external capability identity before integration.
- Crash/retry/concurrency behavior must be idempotent: one immutable job may not produce duplicate reviewer launches, conflicting current results, or blind duplicate origin wakes.
- Source HEAD movement after launch yields explicit stale state rather than optimistic PASS or silent relaunch.
- Review-job evidence may later feed the normal evidence/outcome pipeline, but it is not automatically adjudicated learning truth.
- The ordered reviewer-evolution lifecycle and distribution safety rules remain unchanged.

## Supersedes

This decision **partially supersedes ADR 0006 only where ADR 0006's wording could be read as forbidding MimiSeek from coordinating independent review execution at all**.

ADR 0006 remains authoritative in its core principle: consumers own their development/review/fix/merge workflow and project-specific semantics. ADR 0013 adds only the narrow project-neutral review-job coordination authority defined above.
