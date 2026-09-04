# Review-job coordination research

Status: research only; not yet product or architecture authority.

## Question

Can MimiSeek coordinate an explicitly requested independent review job for a consumer repository without taking ownership of that consumer's ordinary development/fix/merge workflow?

This question exists because accepted ADR 0006 and the current architecture deliberately keep consumer PR review/fix loops outside MimiSeek, while the desired automated workflow now needs one cross-project component to coordinate:

```text
consumer project chat
    -> durable review request
    -> MimiSeek review job
    -> generic CAP fresh worker
    -> fresh Temporary Chat reviewer
    -> REVIEW_RESULT_V1
    -> MimiSeek durable result
    -> generic CAP return delivery
    -> originating project chat continues
```

The proposal below is a narrow amendment candidate, not an authorization to implement it yet.

## Boundary to preserve

The consumer repository and its development chat continue to own:

- when its current PR/HEAD is ready to request independent review;
- exact repository/PR/BASE/HEAD and project-local acceptance policy;
- whether a finding is confirmed/rejected/superseded under project semantics;
- code changes and remediation;
- whether a new HEAD needs another review;
- terminal acceptance and merge consequences under that repository's own rules.

MimiSeek must not become a project-specific development coordinator, must not decide how UV/CAP code is fixed, and must not silently merge consumer PRs merely because a reviewer returned PASS.

## Proposed MimiSeek responsibility

MimiSeek would own a generic review-job control plane whose only review-loop responsibility is to coordinate independent review execution and durable result handoff.

For an explicitly requested job it would:

1. resolve and freeze the declared repository/PR/BASE/HEAD/review-policy identity;
2. reject stale or ambiguous request identity before launch;
3. create one durable `REVIEW_JOB_V1` identity;
4. ask a generic CAP/session executor to launch exactly one fresh independent reviewer worker for that job;
5. receive a correlated reviewer result;
6. independently validate result identity against the job and live consumer PR state;
7. persist the exact result durably in GitHub without modifying the reviewed consumer HEAD;
8. ask the generic session transport to deliver a short wake/resume notification to the originating project chat;
9. leave all finding adjudication, fixes, re-review decisions and merge consequences to the consumer workflow.

This is coordination of an independent review job, not ownership of the whole consumer development/review/fix loop.

## CAP boundary

CAP remains a general agent/session/execution substrate. MimiSeek must not require CAP to know about:

- UV Studio, MimiSeek Review, or chat-agent-platform as semantic project identities;
- GitHub PR semantics;
- `PASS` versus `FINDINGS` meaning;
- MimiSeek learning/promotion state;
- project-specific routing tables.

MimiSeek may depend only on generic capabilities such as:

- launch a fresh qualified worker with bounded payload and exact correlation;
- receive one correlated terminal worker result;
- retain/recover an opaque route to an existing ChatGPT conversation;
- deliver one bounded payload through that opaque route with one-shot/no-blind-resend/recovery semantics.

The exact CAP API is owned by CAP and is intentionally not specified here.

## Fresh reviewer boundary

The review worker must remain genuinely independent of the development chat whose HEAD it reviews.

The request carries object identity and bounded neutral focus, not expected findings or expected answers. The reviewer reconstructs governing repository evidence itself and returns an exact identity-bound result such as `REVIEW_RESULT_V1`.

MimiSeek must not turn a worker result into CURRENT merely because the payload parses. It must re-resolve live consumer identity after result capture.

## Proposed durable job identity

A public/durable job record should contain at least:

```text
schema=REVIEW_JOB_V1
job_id=<immutable unique id>
repository_id=<immutable GitHub repository id when available>
repository=<owner/name for readability>
pr_number=<number>
base_sha=<40-hex>
head_sha=<40-hex>
review_policy_ref=<immutable ref>
request_source=<durable GitHub evidence locator>
reviewer_profile=<qualified independent reviewer profile>
state=<governed state>
result_ref=<durable result locator or null>
result_sha256=<digest or null>
```

The record must not expose a private browser/session capability. A CAP return-route reference, if persistence is required, must be opaque and non-authorizing by itself or remain in private local state owned by the generic session transport. The public job record must be safe to preserve in GitHub.

## Proposed state machine

The exact names remain research-stage, but the semantics should distinguish at least:

```text
REQUESTED
  -> VALIDATED
  -> LAUNCH_CLAIMED
  -> REVIEWING
  -> RESULT_RECEIVED
  -> RESULT_VALIDATED
  -> RESULT_PERSISTED
  -> RETURN_PENDING
  -> RETURN_DELIVERED
  -> DONE
```

Terminal/non-success states must include explicit stale/abstain/failure semantics. A source HEAD move does not become an optimistic failure-to-notify; it produces an explicit stale result/state and wakes the origin so the consumer can decide whether to request a new review for the new HEAD.

A crash/retry must never create a second reviewer launch or a second wake merely because the caller cannot immediately prove what happened.

## GitHub as durable handoff

GitHub should be the durable, cross-chat review-job/result ledger. Chat messages are wake signals, not the only copy of the review result.

The first production design should avoid widening MimiSeek's source-App permissions. The existing CAP/UV source App remains read-only. MimiSeek may write review-job/result state only inside its own repository through a separately governed MimiSeek-owned publication path.

The originating consumer chat, after wake, reads the exact durable MimiSeek result and applies its own repository policy. If that consumer requires the terminal review to be copied into its PR before merge, that remains a consumer-side consequence under its existing authenticated GitHub authority.

This preserves the current useful split:

```text
consumer repositories: source truth + development consequences
MimiSeek GitHub: review-job/result coordination truth
CAP: generic ChatGPT session transport
fresh Temporary Chat: independent semantic reviewer
```

## Review request trigger

A production trigger must be durable and identity-bound. One candidate is a structured request marker attached to the consumer PR and visible through the existing read-only evidence path, for example:

```text
MIMISEEK_REVIEW_REQUEST_V1
job_id=<id>
repository=<owner/name>
pr_number=<number>
base_sha=<sha>
head_sha=<sha>
review_policy_ref=<ref>
```

MimiSeek must still re-resolve live PR identity rather than trusting the marker.

The return route must not be encoded as a browser tab id or a raw private ChatGPT conversation capability in that public marker. The originating chat/CAP runtime must establish the generic return route separately and correlate it to the same job identity.

Alternative triggers (consumer structured export, dedicated MimiSeek request object, webhook) remain candidates. The production choice should minimize source-repository write authority and preserve restart-safe correlation.

## Idempotence and concurrency requirements

The production job layer must fail closed on:

- two concurrent launch claims for one `job_id`;
- result for the wrong repository/PR/BASE/HEAD/policy/job;
- result received after consumer HEAD moved without being classified stale;
- repeated worker result capture that disagrees byte-for-byte or semantically for the same immutable result identity;
- ambiguous durable result publication;
- repeated wake after an ambiguous Send without reconciliation;
- reuse of an old return route for a different job;
- malformed/truncated result content;
- caller attempts to replace exact immutable job identity after launch.

A repeated read/reconcile of an already completed job should be a no-op, not a second review.

## Relationship to accepted ADR 0006

ADR 0006 correctly prevents MimiSeek from becoming the owner of CAP/UV-specific development/review/fix sequencing. That principle should remain.

The proposed amendment is narrower:

> Consumers own the development/review/fix/merge workflow and all project-specific consequences. MimiSeek may provide a reusable cross-project control plane for explicitly requested independent review jobs, provided the control plane is project-neutral and delegates ChatGPT session execution to a generic substrate.

If accepted, a new ADR must explicitly supersede only ADR 0006's blanket implication that MimiSeek cannot coordinate review execution at all. It must not supersede consumer ownership of project semantics.

## Relationship to the reviewer-evolution product

Review-job coordination and reviewer self-improvement are separate loops.

Fast operational loop:

```text
consumer HEAD -> review job -> fresh review -> durable result -> consumer continues
```

Slow reviewer-evolution loop:

```text
adjudicated review history -> learning events -> candidate -> regression -> independent promotion -> stable reviewer
```

The fast loop produces structured evidence that can later feed the slow loop, but a review job must work even before a MimiSeek stable reviewer exists. Before first stable, the worker profile may use the consumer's accepted current review policy/source exactly as it does today.

No review-job PASS is promotion authority for a MimiSeek reviewer candidate.

## Sequencing candidate

This coordination layer does not logically depend on deriving the Stage 1 baseline seed. It does depend on an accepted generic CAP fresh-worker/result path and an accepted generic existing-session return-delivery path.

A future canonical roadmap change may therefore allow bounded review-job-control-plane work to proceed in parallel with the remaining Stage 1 evidence reconciliation once this architectural boundary is independently accepted. Reviewer-learning/promotion sequencing remains unchanged.

## Minimum production acceptance experiment

Before treating this path as routine acceptance infrastructure, exercise one real end-to-end job for each development chat class without project-specific CAP routing:

1. consumer chat requests review for exact live HEAD;
2. request becomes durable and MimiSeek creates one exact job;
3. CAP launches one fresh Temporary Chat reviewer;
4. reviewer returns correlated `REVIEW_RESULT_V1`;
5. MimiSeek persists the exact result in GitHub;
6. source HEAD is rechecked;
7. CAP wakes the exact originating persistent chat through generic existing-session delivery;
8. the origin reads the durable result and continues;
9. repeating/recovering the same job does not launch or wake twice;
10. browser/runtime restart and ambiguous-Send cases are exercised separately.

Run the same architecture with UV, CAP and MimiSeek origins. The CAP runtime must not contain project-specific tables to pass.

## Decision gate

Before implementation, a separate governed architecture PR should decide `ACCEPT_NARROW | REJECT | DEFER` for this proposal and synchronize `PRODUCT.md`, `ARCHITECTURE.md`, `INTEGRATION_CONTRACT.md`, `ROADMAP.md`, `CURRENT_STATE.md`, applicable skill text, and a superseding ADR if `ACCEPT_NARROW` is chosen.

Until that decision is accepted, current ADR 0006 and current architecture remain authoritative and no MimiSeek review-job runtime should be implemented.