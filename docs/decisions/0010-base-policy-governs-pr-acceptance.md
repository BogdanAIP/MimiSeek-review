# ADR 0010 — Accepted BASE policy governs PR acceptance

## Context

MimiSeek Review develops its own governance through pull requests. If a PR that changes `AGENTS.md`, `docs/DEVELOPMENT_PROTOCOL.md`, CI requirements, review requirements, or acceptance authority could use those proposed HEAD rules to judge the same PR, it could weaken its own exam and create circular acceptance.

Exact BASE/HEAD binding and fresh-chat review are necessary but do not by themselves select which version of repository-development policy governs a governance-changing PR.

## Decision

For every ordinary MimiSeek repository-development PR after Stage 0, terminal acceptance is governed by policy already accepted at the PR's immutable `BASE_SHA`.

- Default `review_policy_ref` is the immutable `BASE_SHA`.
- If the accepted BASE policy explicitly delegates repository-development acceptance to another immutable policy ref, that already-accepted delegation may select the delegated ref.
- Proposed governance/acceptance changes in `HEAD_SHA` are reviewed only as target semantics for that PR and cannot govern, weaken, or replace the requirements used to accept themselves.
- Terminal semantic review evidence is identity-bound to repository + base + head + reviewer + `review_policy_ref`.
- If accepted BASE authority cannot determine the governing policy ref unambiguously, acceptance fails closed.

PR #1 is the one-time bootstrap exception because its BASE `09492f1ec8aeb1dfbfc152505d14574016a72870` contains only the original bootstrap README and no repository-development acceptance policy. For PR #1, `review_policy_ref` remains that immutable BASE SHA; authority is resolved from BASE bootstrap intent, exact live PR evidence, complete proposed HEAD governance treated only as target semantics, and a fresh independent read-only review. HEAD does not self-certify.

After Stage 0 is merged, the bootstrap exception is not available to ordinary future PRs.

## Consequences

- A governance-changing PR cannot create a weaker acceptance rule and use it immediately for its own merge.
- Review evidence remains reproducible against an immutable governing policy identity.
- HEAD policy changes can still be accepted, but only under previously accepted authority; they become governing rules for later PRs after merge.
- Ambiguous policy authority blocks merge rather than allowing an optimistic interpretation.
- The first bootstrap PR remains reviewable without pretending that its BASE already contained governance that did not exist.
