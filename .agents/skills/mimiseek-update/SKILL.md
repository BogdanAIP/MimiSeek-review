# Skill: mimiseek-update

## User invocation

Primary natural-language trigger:

> Обнови Мимисик.

Equivalent explicit invocations such as `mimiseek-update` are acceptable.

## Purpose

Run the **independent update half** of the MimiSeek reviewer-improvement loop in a new ChatGPT chat.

This skill independently evaluates the frozen `PENDING_UPDATE` candidate left by `mimiseek-run`. Only if the governing evaluation policy yields authoritative `PROMOTE` may this skill make the candidate the new stable reviewer and create update PRs for registered consumer repositories.

## Fresh-chat requirement

This skill must run in a ChatGPT conversation that did not create, modify, or advocate for the pending candidate.

If the current conversation participated in `mimiseek-run`, candidate construction, learner analysis, or mutation of the frozen evaluation package, do not perform promotion evaluation. Return `UPDATE_BLOCKED_NOT_FRESH` and leave stable unchanged.

The user is expected to satisfy this today by opening a new ChatGPT chat and invoking **«Обнови Мимисик»**. No technical evaluation prompt needs to be copied between chats; durable repository state is the handoff.

## Bootstrap

Before mutations:

1. Resolve live `BogdanAIP/MimiSeek-review` state independently from GitHub.
2. Read `AGENTS.md`, `docs/PRODUCT.md`, `docs/CURRENT_STATE.md`, `docs/REVIEWER_LIFECYCLE.md`, `docs/EVALUATION_POLICY.md`, `docs/INTEGRATION_CONTRACT.md`, and `docs/CHATGPT_ENTRYPOINT.md`.
3. Resolve exactly one eligible frozen `PENDING_UPDATE` package from durable state.
4. Independently resolve the current stable identity, candidate identity, evaluation-policy ref, evidence identities, consumer registry, and candidate diff.
5. Do not rely on claims or summaries from the chat that created the candidate.

## Evaluation

Evaluate the candidate under the fixed governing policy.

At minimum independently verify:

- stable and candidate immutable identities;
- candidate is exactly the one covered by the frozen regression/evidence package;
- governing evaluation policy was fixed before candidate evaluation and was not weakened by the candidate/learner;
- BUGGY target improvements are supported by real confirmed defects;
- corresponding FIXED cases do not retain the old target finding;
- protected capabilities do not regress beyond policy tolerance;
- false-positive/rejected-finding behavior remains within policy tolerance;
- required shadow/new-real-world evidence, if any, is satisfied;
- evidence is current, complete, provenance-bound, and not based on invalid different-head comparisons.

Historical reviewer agreement is not ground truth. More findings alone is not improvement.

## Decision

Return exactly one semantic decision:

- `PROMOTE` — the candidate satisfies every mandatory promotion condition;
- `REJECT` — a mandatory rule is violated or an unacceptable regression is proven;
- `ABSTAIN` — evidence is insufficient or ambiguous.

Any identity mismatch, stale package, unresolved provenance, or inability to establish independence must not result in `PROMOTE`.

## Apply decision

### PROMOTE

Only after authoritative `PROMOTE` and successful mechanical identity checks:

1. atomically register the candidate as the new stable reviewer;
2. preserve previous stable identity and rollback evidence;
3. record the immutable evaluation/promotion result;
4. clear/terminally resolve the corresponding `PENDING_UPDATE` state;
5. for each registered compatible consumer, create an auditable reviewer-version update PR;
6. never push the reviewer update directly to a consumer stable branch;
7. if compatibility cannot be proven for a consumer, leave it pinned and record the blocked distribution state.

### REJECT

Keep current stable unchanged, mark the candidate rejected, preserve all evidence for future learning, and resolve the pending package terminally.

### ABSTAIN

Keep current stable unchanged. Preserve the candidate and evidence for later re-evaluation if governing lifecycle permits. Do not distribute anything.

## Final result

Return a concise `MIMISEEK_UPDATE_RESULT` containing:

- stable before;
- candidate identity;
- evaluation-policy ref;
- decision (`PROMOTE`, `REJECT`, `ABSTAIN`, or update-blocked state);
- stable after;
- promotion evidence identity if promoted;
- consumer update PRs / blocked consumers.

## Fail-closed rules

Never promote when:

- this is not a fresh independent chat;
- no unique eligible `PENDING_UPDATE` exists;
- the candidate/evidence/policy identity is ambiguous or stale;
- the candidate altered its governing evaluation policy;
- a mandatory regression is unresolved or failed;
- evidence is insufficient for the fixed promotion gate.

A failed or interrupted update must leave the previous stable reviewer usable.