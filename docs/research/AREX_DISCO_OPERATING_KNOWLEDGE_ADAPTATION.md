# AREX/DisCo operating-knowledge adaptation for MimiSeek

Status: **research only / non-authoritative / no production architecture selected**

Research baseline: 2026-09-06.

Primary upstream inspected for this research:

- repository: `VectorSpaceLab/AREX-Skill`
- branch: `main`
- exact upstream commit: `ac3fe1afa80fb9a09775ecfb2b6cc3ba850a2db6`
- license at that commit: Apache License 2.0

This document records which ideas and implementation patterns from AREX-Skill / DisCo are promising for MimiSeek, how they should be adapted, what should explicitly **not** be copied, and what evidence should be required before any operating-knowledge layer becomes production architecture.

It does **not** modify current MimiSeek product/runtime/acceptance authority. It does not change `REVIEW_JOB_V1`, `REVIEW_RESULT_V1`, consumer authority, reviewer promotion/distribution authority, merge semantics, the accepted Track R boundary, or the future reviewer-evolution architecture described in `docs/research/SEMANTIC_REVIEWER_ARCHITECTURE_PLAN.md`.

The central research idea is to add a second knowledge axis beside learned defect memory:

```text
learned review knowledge             operating knowledge
confirmed findings                   repositories / docs / papers
    ↓                                      ↓
defect patterns                       source distillation
counterexamples                       provenance + verification
review-plan triggers                  progressive-disclosure skills
    └──────────────────┬───────────────────┘
                       ↓
                 exact-target review
```

Learned review knowledge answers:

> What failure mechanisms has MimiSeek already observed and confirmed?

Operating knowledge answers:

> What externally grounded technology/workflow knowledge should a reviewer know how to apply and verify, even if MimiSeek has never seen that defect before?

These are complementary but must remain separately governed.

## 1. Upstream components inspected

This research is grounded in the following AREX/DisCo components at the exact upstream commit above.

### 1.1 `distill-ml-knowledge`

Path:

`cli/packages/coding-agent/src/disco/skills/distill-ml-knowledge/SKILL.md`

Relevant upstream pattern:

```text
anchor
  ↓
scope
  ↓
ground
  ↓
construct
  ↓
verify
  ↓
accepted operating graph + construction record
```

The workflow preserves source/version/trust boundaries, exclusions, conflicts, inaccessible material, assumptions, evidence, verification targets, routing decisions, and unresolved blockers.

### 1.2 `verify-repo-skill`

Path:

`cli/packages/coding-agent/src/disco/skills/verify-repo-skill/SKILL.md`

Relevant upstream patterns:

- generated skill content is not accepted merely because it exists;
- runtime skill artifacts are separated from verification/test/report artifacts;
- representative native repository checks are preferred where available;
- missing required execution environment remains visibly blocked rather than converted into a pass;
- routing/classification happens after verification and must be source-supported;
- import is transactional and can roll back skill/router state on failure.

### 1.3 `refresh-repo-skill`

Path:

`cli/packages/coding-agent/src/disco/skills/refresh-repo-skill/SKILL.md`

Relevant upstream patterns:

- current upstream repository becomes the source of truth;
- old skill identity can be preserved while stale claims are audited and refreshed;
- staleness is explicit rather than silently ignored;
- claims are divided into still-supported, stale/changed, newly relevant, and unknown;
- refreshed knowledge is verified again before managed replacement.

### 1.4 progressive-disclosure repository router

Path:

`skills/repositories/repo-skills-router/SKILL.md`

Relevant upstream patterns:

- route from broad area to family to repository root to relevant sub-skill;
- read only one or two likely branches rather than the full skill collection;
- choose the smallest useful set of skills;
- do not force a match when no exact route is supported;
- generated routing pages are projections of structured routing state rather than manually maintained truth.

### 1.5 provenance / transactional import patterns

The AREX workflows use repository provenance, source commit/version identity, external verification artifacts, routing handoffs, dedicated import/update helpers, locks, staging, validation, and rollback.

The important idea for MimiSeek is not the exact directory layout. It is that:

```text
candidate knowledge != active knowledge
```

and activation should preserve source identity, verification identity, routing identity, and rollback/recovery semantics.

## 2. What MimiSeek should take

### 2.1 Take the `scope -> ground -> construct -> verify` lifecycle

MimiSeek should not create reviewer operating knowledge by asking a model to read a README and write a permanent skill.

Research target lifecycle:

```text
SOURCE
  ↓
SCOPE
  ↓
GROUND
  ↓
CONSTRUCT
  ↓
CANDIDATE OPERATING SKILL
  ↓
INDEPENDENT VERIFY
  ↓
VERIFIED OPERATING SKILL
  ↓
ACTIVATE / ROUTE
```

#### Scope

Define:

- source anchor;
- intended reviewer use;
- capability boundaries;
- non-goals;
- applicability conditions;
- expected verification targets;
- required environment/runtime evidence;
- known unsupported areas.

#### Ground

Collect retained evidence from exact sources, including where applicable:

- exact repository commit/tree;
- authoritative documentation;
- source code;
- tests/examples;
- CLI/API behavior;
- package/release version;
- external specification or paper;
- source conflicts and inaccessible material.

Grounding must preserve provenance instead of turning source-derived claims into unattributed model memory.

#### Construct

Produce a candidate skill graph with:

- one clear root responsibility;
- progressive-disclosure sub-skills;
- evidence boundaries;
- checks;
- recovery/troubleshooting behavior;
- explicit limitations.

#### Verify

Verify source support, internal links/graph structure, representative use, executable behavior where required, and failure recovery.

A candidate with unresolved required evidence remains unverified or blocked; it does not silently become active knowledge.

### 2.2 Take source-bound provenance as a first-class object

MimiSeek should record enough identity to answer:

> What exact external state did this operating skill describe when it was verified?

Research-only candidate:

```text
OPERATING_SKILL_PROVENANCE_V1

skill_id
source_kind
source_repository
source_commit
source_tree_or_tag
source_version
source_urls[]
source_evidence_paths[]
source_license
working_state_if_relevant

verification_environment[]
verification_evidence_refs[]
known_gaps[]
refresh_signals[]

generated_by
verified_by
generated_at
verified_at
```

For repository-backed knowledge, `source_commit` should normally be immutable and exact.

A skill such as "Playwright guidance" without a supported source/version identity should not be treated as durable reviewer knowledge.

### 2.3 Take explicit stale/refresh semantics

Operating knowledge decays as dependencies, APIs, CLIs, documentation, or source behavior change.

Research candidate lifecycle:

```text
CANDIDATE
VERIFIED
ACTIVE
PARTIALLY_STALE
STALE
BLOCKED
RETIRED
```

Possible refresh sequence:

```text
existing skill + old provenance
        ↓
current source identity
        ↓
staleness audit
        ↓
retained claims
stale claims
changed behavior
new replacement behavior
unknowns
        ↓
targeted refresh
        ↓
independent re-verification
```

Old claims must not survive merely because they were previously useful.

### 2.4 Take progressive disclosure / bounded routing

MimiSeek should never inject the entire operating-knowledge library into every review.

Research routing model:

```text
exact PR diff / changed concepts
        ↓
capability + technology + workflow extraction
        ↓
small set of candidate routes
        ↓
source/version applicability check
        ↓
selected root skill(s)
        ↓
selected sub-skills/references only
```

Routing rules to preserve from AREX in adapted form:

- inspect only the smallest useful number of candidate branches;
- select multiple skills only when they contribute distinct capabilities;
- never choose by repository/product name alone;
- never infer capability from an incidental dependency or example;
- if no route is sufficiently supported, return no operating-skill match rather than forcing one.

The router is a retrieval mechanism, not semantic authority.

### 2.5 Take separation of runtime skill from verification evidence

MimiSeek should keep operating instructions separate from evidence that justified activating them.

Research layout concept:

```text
operating-knowledge/
  skills/
    <skill-id>/
      SKILL.md
      references/
      scripts/

evidence/
  operating-skill-verification/
    <skill-id>/<verification-id>/
      provenance
      cases
      results
      limitations
      independent-review-result
```

The runtime reviewer should receive concise operating knowledge, not a self-congratulatory verification report that biases it toward trusting the skill.

### 2.6 Take representative-use and native-evidence verification

Synthetic tests can verify that a skill gives internally coherent guidance, but they cannot substitute for required real execution evidence.

Adapted rule:

> If a skill claims knowledge about a behavior that can only be established in a specific environment/backend/runtime, the required environment must be observed or the claim remains visibly blocked/limited.

Possible verification states:

```text
PASS
SKILL_GAP
SOURCE_CONFLICT
NATIVE_FAIL
BLOCKED_REQUIRED_ENVIRONMENT
SKIP_UNSAFE
SKIP_NOT_SELECTED
STALE_SOURCE
UNVERIFIED
```

Exact production enums remain future schema work.

### 2.7 Take classification after verification

Routing/classification should not be based on generated skill prose alone.

A managed reusable skill should be classified only after verification using evidence from the original source.

Do not accept:

- keyword-only classification;
- dependency-only classification;
- example-only classification;
- forced taxonomy matches.

If no exact route exists, `unclassified`/no-match is safer than an invented assignment.

### 2.8 Take candidate-versus-active separation and transactional activation

Research candidate activation flow:

```text
candidate skill tree
        ↓
independent verification
        ↓
stage
        ↓
validate provenance + links + route + digests
        ↓
atomic activation
        ↓
rebuild structured routing projection
        ↓
final checks
```

On failure:

```text
rollback skill state + route state
```

A partially imported skill/router combination must not become the live reviewer context.

### 2.9 Take project-specific versus reusable scope separation

MimiSeek needs at least two knowledge scopes.

#### Project operating knowledge

Examples:

- repository-specific architecture conventions;
- local wrappers/adapters;
- project-specific test/runtime workflow;
- local terminology and constraints.

Candidate location/ownership remains future design work.

#### Reusable operating knowledge

Examples:

- Playwright API/workflow knowledge;
- GitHub Actions behavior;
- framework/library operational knowledge;
- public repository/package behavior.

Reusable knowledge requires stronger provenance, independent verification, refresh semantics, and reuse evidence than one project-local skill.

### 2.10 Take recovery knowledge, not only happy-path instructions

A useful operating skill should include what to do when expected behavior fails.

Examples:

```text
if source version mismatches -> mark stale / refresh
if required backend unavailable -> BLOCKED_REQUIRED_ENVIRONMENT
if evidence conflicts -> SOURCE_CONFLICT / investigate
if API symbol disappeared -> verify release/source replacement
if representative native case fails -> distinguish NATIVE_FAIL from SKILL_GAP
if router finds no exact match -> do not force route
```

Recovery behavior is part of the skill contract, not optional prose.

## 3. What MimiSeek should change relative to AREX

### 3.1 Replace self-refine as terminal trust with independent verification

AREX includes content-level self-refine inside skill verification. MimiSeek can retain self-refine as a drafting aid, but it should not be sufficient terminal authority for reviewer knowledge.

Preferred model:

```text
Skill Builder
    ↓
CANDIDATE
    ↓
NEW INDEPENDENT READ-ONLY VERIFIER
    ↓
VERIFIED / FINDINGS / ABSTAIN
```

Reason:

```text
same model misunderstanding source
    ↓
writes wrong skill
    ↓
checks skill using same misunderstanding
    ↓
false verification
```

Independent verification reduces correlated self-confirmation. Exact implementation/worker identity remains future architecture work.

### 3.2 Generalize ML backend concepts into verification environments

Do not import the AREX CPU/CUDA/ROCm/MPS assumptions as a MimiSeek core abstraction.

MimiSeek needs a generic concept such as:

```text
VERIFICATION_ENVIRONMENT

OS
language/runtime
browser
service/API
Git/provider capability
hardware/backend when relevant
credentials/access class
network requirement
```

ML accelerator semantics can be one specialization, not the platform model.

### 3.3 Keep operating knowledge non-authoritative for acceptance

An operating skill may tell the reviewer:

- which API semantics are relevant;
- what common failure modes exist;
- how to reproduce behavior;
- what source/native checks to run;
- how to recognize stale knowledge.

It must never independently authorize:

- `PASS`;
- merge;
- reviewer promotion;
- consumer installation;
- policy selection;
- finding adjudication;
- evidence truth.

The reviewer still reconstructs governing authority and evaluates the exact target independently.

### 3.4 Do not expose expected findings or answer keys

Operating knowledge is a capability scaffold, not benchmark leakage.

It may say:

> This API has cancellation and retry semantics; inspect those when relevant.

It must not say:

> In this target PR the expected defect is at file X line Y.

This matches the existing MimiSeek research requirement that review planning remain open-ended and not leak expected finding text/count or later fix knowledge.

### 3.5 Do not make the router a proof of relevance or completeness

No-match must not mean safe.

Selected-route must not mean exhaustive.

The ordinary semantic reviewer must retain an open-ended pass after using routed operating knowledge and learned defect patterns.

## 4. What MimiSeek should not take

### 4.1 Do not copy the whole AREX skill collection

The 5000+ upstream skill collection is not itself MimiSeek architecture.

MimiSeek should not bulk-import the library as trusted reviewer context because:

- its verification standard is designed for a different product purpose;
- individual skills may be stale relative to a target dependency version;
- reviewer independence/authority boundaries differ;
- routing taxonomy is ML/scientific-computing oriented;
- provenance and acceptance must be re-evaluated under MimiSeek requirements.

External AREX skills may later serve as candidate source material, never automatically active MimiSeek truth.

### 4.2 Do not copy AREX's taxonomy as MimiSeek's taxonomy

MimiSeek's routing should be driven by review-relevant concepts, technologies, runtime surfaces, and verification needs.

The AREX area/family hierarchy is useful as a progressive-disclosure example but is not an accepted MimiSeek classification.

### 4.3 Do not copy the home-directory managed-library layout

Paths such as `~/.disco/agent/skills/...` are DisCo implementation details.

MimiSeek needs repository/product-owned storage and durable state appropriate to its accepted architecture.

### 4.4 Do not couple production knowledge to source-checkout paths

Public/reusable skill content should be self-contained or use durable source identities, not instructions such as "open my local checkout at path X".

### 4.5 Do not silently reuse code without license handling

AREX-Skill is Apache-2.0 at the inspected upstream commit.

If MimiSeek later copies/modifies upstream code rather than independently reimplementing an idea, the implementation work must explicitly preserve required license/attribution notices and evaluate any `NOTICE` obligations at the exact copied source revision.

This research document records architecture inspiration only; it does not itself import AREX code.

## 5. Candidate MimiSeek contracts

No schema below is accepted production authority. These are research targets for later experiments.

### 5.1 `OPERATING_SKILL_V1`

Possible fields:

```text
skill_id
scope = PROJECT | REUSABLE
purpose
applicability
non_goals
routes[]
entry_points[]
subskills[]
references[]
scripts[]
checks[]
recovery_behaviors[]
provenance_ref
verification_state_ref
```

### 5.2 `OPERATING_SKILL_PROVENANCE_V1`

See section 2.2.

### 5.3 `OPERATING_SKILL_VERIFICATION_RESULT_V1`

Possible identity:

```text
skill_id
candidate_digest
source_provenance_digest
verifier_identity
verification_environment
verification_cases[]
source_support_result
native_result
static_result
routing_result
limitations[]
terminal_state
```

Terminal state candidates:

```text
VERIFIED
FINDINGS
BLOCKED
ABSTAIN
```

### 5.4 `OPERATING_SKILL_REFRESH_STATE_V1`

Possible state:

```text
skill_id
active_source_identity
current_source_identity
status = CURRENT | PARTIALLY_STALE | STALE | UNKNOWN
changed_source_surfaces[]
affected_skill_surfaces[]
refresh_required
```

### 5.5 structured router state

Routing source of truth should be structured machine state.

Human-readable indexes/pages should be generated projections and must not become a second manually maintained live inventory.

Possible route metadata:

```text
skill_id
source_identity
routing_status
capability_routes[]
applicability_features[]
non_applicability_features[]
verification_ref
```

## 6. Integration with future semantic reviewer architecture

The future reviewer should combine three conceptually different inputs.

```text
                       exact review target
                              ↓
                 changed concepts / risks
                              ↓
          ┌───────────────────┼────────────────────┐
          ↓                   ↓                    ↓
accepted authority      learned review       operating knowledge
and target evidence     knowledge             external/project skill
                        defect patterns        router
                        counterexamples        provenance/version
                        prior misses           recovery guidance
          └───────────────────┼────────────────────┘
                              ↓
                       review context
                              ↓
                   open-ended semantic review
                              ↓
                       REVIEW_RESULT
```

Rules:

1. accepted authority remains above operating knowledge;
2. operating knowledge never self-authorizes a finding or PASS;
3. defect patterns describe confirmed failure mechanisms, while operating skills describe source-grounded technology/workflow behavior;
4. both are retrieved selectively;
5. both supplement, never replace, open-ended review;
6. stale/blocked operating knowledge remains visible and cannot silently act as current guidance.

## 7. Relationship to Development Repeat Prevention

The proposed operating-knowledge layer and MimiSeek self-development repeat prevention solve different problems.

Repeat prevention asks:

> How do we stop MimiSeek development from repeating an already confirmed failure class?

Operating knowledge asks:

> How does a reviewer gain trustworthy, versioned, source-grounded knowledge about technologies/workflows before a relevant failure has ever been seen?

If Development Repeat Prevention is later accepted, its failure-pattern machinery should not be reused as the operating-skill registry. The namespaces, authorities, lifecycle, and trust semantics are different.

Possible future interaction:

```text
operating skill says API behavior X should hold
        ↓
review finds defect violating X
        ↓
consumer/governed process confirms finding
        ↓
confirmed failure may later become defect-pattern memory
```

The skill did not become the defect pattern, and the defect pattern did not become the source authority for the external API.

## 8. First prototype recommended

Do not begin with a large skill library.

Run one controlled prototype on one external technology with real MimiSeek-relevant review tasks.

Recommended initial candidate: a well-versioned repository/framework with:

- meaningful source and docs;
- native tests/examples;
- versioned APIs;
- recurring semantic review risk;
- enough historical PRs/cases to compare reviewer performance.

Practical candidates include Playwright or another repository-backed technology used in agent/browser development. GitHub Actions/provider behavior is also highly relevant but may require multiple authoritative sources rather than one clean repository anchor.

### Prototype sequence

```text
choose exact source commit/version
        ↓
SCOPE
        ↓
GROUND source/docs/tests
        ↓
construct one small skill graph
        ↓
independent skill verification
        ↓
freeze VERIFIED candidate
        ↓
run paired review evaluation
  A: reviewer without skill
  B: reviewer with routed skill
        ↓
compare governed outcomes
```

### Minimum evaluation questions

Measure whether the skill improves:

- confirmed-defect recall;
- precision / false-positive rate;
- evidence quality;
- unsupported-claim rate;
- review coverage;
- reviewer token/context cost;
- review latency/cost where measurable;
- stale-version errors;
- ability to recover from failed verification/reproduction.

Do not select production architecture because the skill subjectively feels useful.

### Critical experimental controls

- same exact target PR/base/head;
- same reviewer model/configuration where possible;
- no expected finding text leaked into skill;
- skill built only from evidence available independently of target answer key;
- independent skill verifier distinct from builder;
- target adjudication remains governed independently;
- report blocked/stale/no-route cases rather than deleting them from the denominator.

## 9. Decision gates

### Gate OK1 — operating knowledge value

Question:

> Does one independently verified, source-bound operating skill materially improve governed review outcomes over the same reviewer without the skill?

Decision:

`ACCEPT_NARROW | DEFER | REJECT`

### Gate OK2 — provenance and refresh sufficiency

Question:

> Can MimiSeek reliably detect and fail closed on stale or mismatched operating knowledge before it influences a review materially?

Decision:

`ACCEPT_NARROW | DEFER | REJECT`

### Gate OK3 — routing value

Question:

> Does progressive-disclosure routing reduce context cost while preserving or improving relevant knowledge retrieval, without forcing false matches or creating a closed checklist?

Decision:

`ACCEPT_NARROW | DEFER | REJECT`

### Gate OK4 — independent verification value

Question:

> Does separating skill builder from terminal skill verifier materially reduce unsupported or self-confirming operating knowledge at acceptable cost?

Decision:

`ACCEPT_NARROW | DEFER | REJECT`

### Gate OK5 — activation/refresh safety

Question:

> Can candidate activation, replacement, router update, and rollback remain atomic enough that a partial knowledge update cannot become live reviewer context?

Decision:

`ACCEPT_NARROW | DEFER | REJECT`

Only after these gates have evidence should production schemas/runtime be selected.

## 10. Candidate implementation sequence if research is accepted later

This is a dependency proposal, not current roadmap authority.

```text
OK-A source/provenance model
  ↓
OK-B one manual candidate skill
  ↓
OK-C independent verification artifact
  ↓
OK-D paired reviewer experiment
  ↓
OK-E staleness/refresh experiment
  ↓
OK-F structured progressive router
  ↓
OK-G transactional managed activation
  ↓
OK-H broader repo/paper distiller
```

Do **not** begin with a generic distiller that can generate thousands of skills before one skill has demonstrated measurable review value.

## 11. Reuse-versus-reimplementation decision

AREX-Skill's Apache-2.0 license permits modification and redistribution subject to its license conditions.

Future implementation should decide component by component:

### Likely reimplement from ideas first

- MimiSeek contract schemas;
- authority boundary;
- independent verification semantics;
- review-specific router inputs;
- stale-skill effect on review acceptance/context;
- integration with MimiSeek evidence and reviewer architecture.

These are MimiSeek-specific and should not inherit unrelated DisCo assumptions.

### Candidates for code-level adaptation after inspection

- provenance checking patterns;
- skill tree/static validation helpers;
- transactional import/update/rollback patterns;
- generated routing projection/update patterns;
- representative native-case runner patterns;
- source-license resolution/application patterns where useful.

Any direct code adaptation must record exact upstream file/commit provenance and preserve Apache-2.0 obligations.

## 12. Explicit non-decisions

This research does not decide:

- that MimiSeek will use AREX-Skill directly;
- that MimiSeek will import AREX's existing skill library;
- that skill files must use DisCo's directory/frontmatter format;
- that the router taxonomy will resemble AREX's ML taxonomy;
- that source repositories are the only possible anchors;
- that papers/docs may be distilled without separate source-quality policy;
- that self-refine is sufficient verification;
- that operating skills may influence acceptance without exact provenance/currentness;
- that operating knowledge should be implemented before current accepted roadmap dependencies permit it.

## 13. Research conclusion

The highest-value AREX/DisCo contribution to MimiSeek is not the existing catalog of thousands of skills. It is the operating-knowledge lifecycle:

```text
source-bound scope
  + provenance-preserving grounding
  + structured skill construction
  + explicit verification
  + progressive disclosure
  + staleness/refresh
  + transactional activation
```

MimiSeek should adapt this lifecycle under stricter review-specific rules:

```text
builder != terminal verifier
operating knowledge != authority
no route != safe
verified != permanently current
synthetic evidence != required real-runtime evidence
candidate != active
```

The recommended next research action, if separately authorized, is one small paired-review prototype rather than broad infrastructure or bulk skill ingestion.
