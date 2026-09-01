# MimiSeek reviewer architecture research

Status: **research input only / non-authoritative / no production architecture selected**

Research baseline: 2026-09-01.

This document studies how MimiSeek should become a strong reusable semantic code reviewer. CAP research is an important experimental input, but CAP is not the authority for MimiSeek reviewer design.

The intended long-term product split is:

```text
CAP
= agent / execution environment / transport / sandbox / durable handoff

MimiSeek
= reviewer / review methodology / repository exploration strategy /
  candidate finding generation / falsification / review decision
```

This document does not change Stage 1 state, create a baseline/candidate/stable reviewer, authorize a consumer installation, or select Temporary Chat, snapshots, graphs, MCP, a context engine, or any other production implementation.

Its purpose is to preserve existing evidence, extend the research with current external practice, define falsifiable reviewer-context hypotheses, and specify experiments that can choose the architecture later from measured review quality rather than convenience.

## 1. Product boundary

Accepted MimiSeek ADR 0001 and ADR 0006 already establish the durable ownership boundary:

- CAP/UV/future consumers own their normal development/review/fix workflows and project-local policy;
- MimiSeek owns reusable reviewer methodology, learning, evaluation, versioning and release lifecycle;
- generic worker orchestration may live in CAP, while reviewer-specific semantic behavior belongs to MimiSeek.

### CAP should eventually provide generic execution mechanics

Candidate responsibilities for CAP/general agent infrastructure:

- launch a genuinely fresh bounded worker/reviewer context;
- prove context/capability isolation;
- bind one run to immutable task/repository identities;
- exactly-once/one-Send or equivalent consequence ownership;
- browser/process lifecycle, crash/restart and stale-run handling;
- expose bounded read-only repository/test capabilities to the reviewer;
- capture a structured terminal result and return it durably;
- enforce privilege separation and fail-closed dispatch/result handling.

CAP must not become the semantic selector of which unchanged files are sufficient for a review finding. If CAP chooses the reviewer's semantic context too narrowly, MimiSeek cannot recover evidence that was never exposed.

### MimiSeek should own reviewer semantics

Reviewer-specific concerns belong here:

- exact review identity and governing-policy reconstruction;
- PR intent versus actual implementation;
- changed/unchanged cross-file impact analysis;
- repository exploration strategy;
- source/config/test/schema/document relationship discovery;
- candidate finding generation;
- risk-directed investigation;
- falsification and validation of candidate findings;
- review-specific use of tests/static/runtime evidence;
- high-signal final output and `PASS/FINDINGS/ABSTAIN/STALE` semantics;
- learning from hits, misses and false positives;
- regression/protected-capability evaluation of context strategies and reviewer versions.

## 2. What CAP #145 already established experimentally

Source repository: `BogdanAIP/chat-agent-platform`.

Experiment source: PR #145, head used by this research: `df0aa462ade7d36172347adfcbc292dd1c6f95da`.

The main value of #145 for MimiSeek is its **experimental method**, not its browser implementation.

### 2.1 Positive, stale and hidden-defect controls

#145 used materially different controls:

1. accepted exact PR -> reviewer should be capable of returning `PASS`;
2. superseded requested identity -> reviewer should reject it as `STALE` rather than review a fetchable old commit as current;
3. known defective exact range -> reviewer must recover real historical defects without being told the expected findings/count.

The known-defect control reproduced the historical CAP #140 defective range and the fresh reviewer recovered the same four later-confirmed P1 categories without the launcher supplying those answers.

Reusable MimiSeek lesson:

> Reviewer experiments need positive, stale, negative/known-finding and later false-positive controls. A PASS-shaped response is not evidence of reviewer quality.

### 2.2 Answer-leakage controls

#145 tests explicitly prevented the launcher from embedding expected finding count/category in the review request.

Reusable MimiSeek lesson:

> Regression/evaluation fixtures must separate task inputs from ground truth. Expected findings, disposition and post-fix knowledge must not leak into the candidate reviewer context.

### 2.3 Private-context isolation controls

#145 compared public reconstruction with private evidence transport, including bundle/file experiments whose repository truth could not be supplemented through public repository lookup.

Reusable MimiSeek lesson:

> Context quality and execution transport must be measurable independently. A reviewer should not appear better merely because one transport leaks more historical or public answer evidence.

### 2.4 Result binding and failure discipline

The experiment bound requests/results to exact run identity, required a terminal marker, classified malformed output as unstructured, and treated the transport as non-authoritative.

Reusable MimiSeek lesson:

> Semantic quality evidence is useful only when the exact reviewer run, source identity and result are durably correlated.

## 3. What CAP #147 / snapshot research already established

Relevant CAP research source: PR #147, research head `d732ef190160891b60c953bb584a273b10be0a7e` plus `experiments/chatgpt-snapshot-reviewer/build_snapshot.py` from the related research branch.

The important result is not a selected CAP production design. It is a set of context-integrity properties that MimiSeek should test and likely preserve regardless of transport.

### 3.1 Provider/Git object authority

For provider-backed PR review, developer working-tree bytes should not silently define repository truth.

Research sequence:

```text
live provider PR identity
 -> exact BASE_SHA / HEAD_SHA
 -> isolated Git mirror/cache
 -> fetch exact remote refs/objects
 -> verify expected commits
 -> verify tree/blob identities
 -> construct reviewer evidence from those immutable objects
 -> independently classify local checkout parity
```

Useful parity states include:

`MATCH | LOCAL_AHEAD | REMOTE_AHEAD | DIVERGED | DIRTY | LOCAL_ONLY | REMOTE_UNAVAILABLE`.

This distinction is reviewer-relevant because a locally correct checkout does not prove a remote PR head and a remotely correct PR does not prove a dirty local workspace.

### 3.2 Explicit omissions instead of silent truncation

The snapshot experiment inventories text, binary, non-UTF8, LFS pointers, symlinks and submodules and raises `SNAPSHOT_OVERSIZE` instead of silently deleting source context to fit the transport budget.

Reusable MimiSeek lesson:

> Context incompleteness must be represented explicitly. Silent omission is incompatible with an authoritative PASS.

### 3.3 Whole-repository hypothesis

A reviewer must have a path to evidence outside the diff. The unchanged caller/control case exists specifically because semantic breakage often lives in code that did not change.

A graph/index is useful for finding such evidence, but it cannot become source authority. Dynamic dispatch, reflection, generated code, runtime registration, configuration coupling and unsupported languages can make structural indexes incomplete.

Reusable MimiSeek rule candidate:

> `not found in the graph/index` must never mean `not relevant` or `does not exist` unless the indexing contract proves that conclusion for the concrete language/mechanism.

## 4. External practice reviewed for MimiSeek

These sources are research evidence, not authority over MimiSeek policy. Product claims can change and must be re-verified when an implementation decision is made.

### 4.1 OpenAI Codex code review

Sources:

- `https://openai.com/index/introducing-upgrades-to-codex/`
- `https://help.openai.com/en/articles/20001107-codex-security`

Current published Codex review description says the reviewer navigates the codebase, reasons through dependencies, and runs code/tests to validate correctness. Codex Security goes further for security analysis by building a codebase-specific threat model, exploring realistic paths, and attempting reproduction in an isolated environment before surfacing a vulnerability.

Research implications:

- repository exploration is part of review, not merely preprocessing;
- execution can be used as **validation**, not only as generation tooling;
- a useful reviewer may build risk/domain models (for example trust boundaries) before searching for findings;
- validation/reproduction is a strong mechanism for reducing false positives.

### 4.2 GitHub Copilot code review

Sources:

- `https://docs.github.com/en/copilot/concepts/agents/code-review`
- `https://docs.github.com/en/copilot/how-tos/copilot-on-github/use-copilot-agents/copilot-code-review`

Current GitHub documentation describes agentic full-project context gathering for code review and support for repository instructions, `AGENTS.md`, skills and MCP context.

Important caution for MimiSeek: GitHub documents that Copilot review reads relevant custom instructions/skills from the PR **head**. MimiSeek already has a stronger accepted governance requirement for its own acceptance reviews: accepted BASE policy governs and proposed HEAD governance is target semantics only unless BASE delegates otherwise.

Research implications:

- full-project context gathering is a useful capability class;
- repository-local instructions and skills are valuable context;
- context tools can be externalized behind bounded interfaces;
- MimiSeek must preserve its own BASE/HEAD authority semantics rather than copy another product's instruction precedence.

### 4.3 CodeRabbit

Source:

- `https://docs.coderabbit.ai/overview/architecture`

Current documentation describes a sandboxed full repository clone, many static analyzers/linters/SAST tools, agentic codebase exploration and specialized review/verification agents.

Research implications:

- LLM reasoning and deterministic analyzers are complementary;
- a reviewer can use multiple evidence producers without treating their agreement as ground truth;
- a separate verification pass/role is worth evaluating for precision.

### 4.4 Greptile

Sources:

- `https://www.greptile.com/docs/how-greptile-works/graph-based-codebase-context`
- `https://www.greptile.com/docs/code-review/key-features`

Current Greptile documentation describes a repository graph over functions/classes/imports/dependencies and review reasoning about ripple effects beyond the diff, including callers/contracts and cross-file inconsistencies.

Research implications:

- callers/references/dependency traversal is a high-value reviewer capability;
- graph-assisted impact expansion deserves a direct controlled comparison;
- graph evidence should remain a retrieval hint/finding lead, not immutable repository truth.

### 4.5 Sourcegraph

Sources:

- `https://sourcegraph.com/docs/code-navigation`
- `https://sourcegraph.com/docs/code-navigation/precise-code-navigation`

Sourcegraph exposes definitions, references, implementations and cross-repository navigation. It distinguishes search-based navigation from precise compile/index-derived navigation and explicitly notes that search-based navigation can have false positives and false negatives.

Research implications:

- MimiSeek should distinguish approximate search results from precise semantic navigation when both exist;
- callers/references/implementations can be first-class review tools;
- tool result confidence/provenance should be visible to the reviewer.

### 4.6 SWE-Review

Source:

- `https://arxiv.org/abs/2607.06065`

SWE-Review reports that an agentic reviewer which explores a repository outperforms single-turn fixed-context review on its benchmark in review decision accuracy and downstream revision usefulness.

Research implication:

> MimiSeek should directly test agentic repository exploration against fixed snapshot review on identical cases rather than assume that increasing static context alone is optimal.

### 4.7 SWE-Explore

Source:

- `https://arxiv.org/abs/2606.07297`

SWE-Explore isolates repository exploration quality and evaluates coverage, ranking and context efficiency. Its results report modern agentic explorers above classical retrieval, with line-level coverage/ranking remaining important differentiators.

Research implications:

- repository exploration should be evaluated as its own reviewer capability;
- finding recall alone cannot diagnose whether a failure came from poor localization or poor semantic reasoning;
- context efficiency/ranking should be measured, not treated only as implementation cost.

### 4.8 CR-Bench / CR-Evaluator

Source:

- `https://arxiv.org/abs/2603.11078`

CR-Bench emphasizes the real cost of spurious review findings and reports a resolution-versus-noise trade-off when agents are driven to identify all hidden issues.

Research implication:

> MimiSeek should optimize high-signal defect discovery, not maximum emitted issue count. Its existing falsification discipline and rejected-finding corpus are core reviewer features, not reporting polish.

## 5. Current research thesis

The strongest current hypothesis is:

> **MimiSeek should be an agentic semantic reviewer that independently explores an immutable repository state through bounded read-only capabilities. CAP may provide the execution/sandbox/transport layer, but CAP should not preselect the semantic evidence that is sufficient for MimiSeek's conclusions.**

This is a **hypothesis to test**, not a production decision.

A fixed whole-repository snapshot remains a serious candidate and a valuable control. It may prove sufficient or even preferable for some repository sizes/languages. The experiments below must decide.

## 6. Candidate reviewer capability model

The research should evaluate reviewer capability as layers rather than as one opaque prompt.

### 6.1 Identity and authority layer

Required inputs/capabilities:

- repository/provider identity;
- PR identity when applicable;
- exact BASE and HEAD commits/trees;
- accepted governing review-policy ref;
- applicable target/project skills/instructions under explicit precedence;
- current/stale determination before and immediately after review;
- explicit evidence completeness state.

A reviewer that cannot prove its review identity must not emit authoritative PASS.

### 6.2 Intent model

Before line-level defect search, the reviewer should reconstruct:

- issue/PR stated goal where available;
- architecture/current-state intent;
- expected invariants/compatibility contract;
- what the diff claims to change and what it explicitly leaves unchanged.

This permits mismatch findings such as “implementation does not achieve the stated migration/recovery/compatibility goal” rather than only local syntax/logic comments.

### 6.3 Core immutable context

Every compared architecture should expose a minimal stable context envelope such as:

```text
REVIEW_CONTEXT_CORE_V1
repository/provider
PR
BASE/HEAD commit + tree identity
governing policy identity
applicable project/reviewer instructions
changed-file inventory
exact diff
relevant CI/check identity
context/tool-session identity and completeness declarations
```

The core envelope is not expected to contain all source code.

### 6.4 Read-only repository exploration candidate

Candidate capability families:

```text
list_tree(ref, path)
read_file(ref, path/range)
search_text(ref, query/path scope)
show_diff(base, head, path)
show_history(path/symbol/range)
```

No arbitrary repository mutation is needed for semantic review.

The reviewer decides which unchanged paths to inspect.

### 6.5 Structural navigation candidate

Optional higher-level tools:

```text
find_symbol
find_definition
find_references
find_implementations
find_callers
find_importers/dependents
```

Results must declare whether they are precise/index-derived, parser-derived or search/heuristic so MimiSeek can reason about possible omissions.

### 6.6 Bounded validation/execution candidate

Potential read/validation-only operations:

- run repository-governed focused tests;
- run predefined static analyzers/lints/type checks;
- inspect already-produced CI logs/artifacts;
- execute a bounded reproduction harness when governing policy explicitly permits it.

The reviewer does not need general deployment/write authority to validate many correctness hypotheses.

A test failure is evidence; a test pass is not proof that an untested invariant is correct.

### 6.7 Candidate finding + falsification layer

For each candidate finding, MimiSeek should try to answer:

1. What exact introduced path causes the problem?
2. Which invariant/contract is violated?
3. Which unchanged callers/config/schema/recovery paths could falsify or support it?
4. Is the behavior intentional under governing policy?
5. Does a test/static/runtime artifact reproduce or disprove it?
6. Is the finding current for exact HEAD?
7. Is severity justified by concrete consequence?

Only surviving candidates enter final output.

### 6.8 Sparse final result

Final review quality should reward:

- real, actionable defects;
- complete source/line/identity evidence;
- calibrated severity;
- explicit uncertainty/ABSTAIN where evidence is insufficient;
- few/no speculative nitpicks.

## 7. CAP/MimiSeek execution contract hypothesis

A possible future relationship, intentionally implementation-neutral:

```text
CAP resolves/locks exact review operation
        |
        v
CAP creates immutable read-only repository session
        |
        v
CAP launches fresh bounded reviewer context
        |
        v
MimiSeek receives REVIEW_CONTEXT_CORE_V1
        |
        v
MimiSeek independently explores repository through read-only capabilities
        |
        v
MimiSeek generates + falsifies candidate findings
        |
        v
optional bounded validation evidence
        |
        v
MimiSeek returns structured exact-identity result
        |
        v
CAP durably correlates/returns that result to the consumer workflow
```

CAP owns lifecycle and capability enforcement. MimiSeek owns semantic search strategy and review decision.

This contract must not require CAP to predict all relevant unchanged files before MimiSeek begins reasoning.

## 8. Controlled architecture experiment matrix

Do not choose the production context architecture from documentation/intuition alone. Compare architectures on **the same hidden cases** with the same reviewer model/policy where technically possible.

### A — Public provider reconstruction baseline

Reviewer gets exact request and independently uses available public Git/provider evidence.

Purpose:

- establish current ordinary fresh-review performance;
- measure real public-tool variability;
- retain a baseline close to today's manual workflow.

### B — Fixed deterministic whole-repository snapshot

Reviewer receives exact Git-object-derived core + diff + complete supported source shards within explicit bounds.

Purpose:

- test whether deterministic static full context is sufficient;
- remove provider navigation variability;
- quantify oversize/context-pressure behavior.

### C — Agentic read-only repository session

Reviewer gets core context plus primitive read/search/history tools over immutable BASE/HEAD repository state.

Purpose:

- let semantic reasoning choose its own unchanged context;
- test SWE-Review/SWE-Explore-style exploration benefit;
- measure exploration efficiency and missed-context failures.

### D — Structural/graph-assisted exploration

C plus definitions/references/callers/implementations/dependency hints.

Purpose:

- measure improvement in cross-file/impact recall;
- measure false confidence/false positives from incomplete graph/index data;
- compare precise versus heuristic navigation where available.

### E — Exploration plus bounded validation

D plus governed tests/static analysis/reproduction capabilities.

Purpose:

- test whether active validation improves precision/severity calibration;
- measure cases where execution evidence prevents a false positive or confirms a subtle defect.

### F — Multi-pass/specialist/judge variants

Only after A-E establish a strong single-reviewer baseline.

Possible variants:

- independent general correctness + security/authority + persistence/concurrency passes;
- separate candidate generator and verifier/judge;
- repeated independent samples under a fixed compute budget.

Purpose:

- measure whether additional passes improve precision/recall enough to justify complexity;
- avoid introducing multi-agent machinery merely because other products use it.

## 9. Evaluation corpus design

Architecture experiments should use cases whose ground truth is independently governed.

### Required case classes

- confirmed BUGGY cases;
- corresponding FIXED cases;
- confirmed rejected/false-positive historical findings;
- exact stale-identity cases;
- unchanged-caller/cross-file cases;
- compatibility/schema migration cases;
- persistence/recovery/crash cases;
- concurrency/transaction/locking cases;
- authority/security boundary cases;
- documentation/current-authority cases where documentation is actually acceptance-significant;
- large-repository/context-boundary cases;
- configuration/runtime-registration/dynamic-dispatch cases that may defeat a simple graph.

CAP/UV historical evidence is useful, but a case becomes MimiSeek evaluation ground truth only through normal provenance/adjudication rules.

### Leakage controls

For each evaluation case:

- expected finding text/category/count is stored outside reviewer-visible context;
- later fix/disposition must not be visible to the BUGGY review unless intentionally part of the test;
- reviewer must not receive a developer-written list of “relevant files” derived from ground truth;
- public-search experiments must record whether historical review comments/fixes were accessible and whether that invalidates the case for blind evaluation;
- when evaluating context architectures, the same allowed public/private evidence policy should be enforced across variants where possible.

## 10. Metrics

A context architecture is not better merely because it emits more findings.

Measure at least:

### Semantic quality

- target defect recall;
- finding precision / confirmed-findings ratio;
- false-positive/rejected-finding rate;
- FIXED-case old-defect persistence;
- severity calibration;
- review decision correctness (`PASS/FINDINGS/ABSTAIN/STALE`).

### Context/exploration quality

- relevant-file/region coverage where ground truth can support it;
- unchanged-file/caller recall;
- exploration ranking/context efficiency;
- number of source reads/searches/tool calls;
- bytes/tokens delivered/read;
- silent omission rate (must normally be zero by contract);
- correct behavior when context exceeds limits.

### Reliability

- exact identity/stale behavior;
- reproducibility of repository/context identity;
- malformed/partial tool response handling;
- crash/restart/result-correlation behavior supplied by CAP;
- public/private leakage-policy compliance.

### Cost/latency

- model turns;
- wall time;
- test/static-analysis runtime;
- context bytes/tokens;
- external compute/tool usage.

Do not optimize cost before establishing a minimally acceptable semantic-quality region; then compare efficiency among architectures that meet quality requirements.

## 11. Research controls that should be built next

The next research work should target discriminating cases rather than more transport mechanics.

### 11.1 Unchanged caller control

A changed producer/API function changes semantic return/contract while an unchanged caller continues to rely on the old behavior.

Goal: distinguish diff-only/static-local review from real repository impact exploration.

### 11.2 Similar-name false-reference control

Repository contains multiple same/similar symbol names. Search-based navigation can return plausible but wrong references.

Goal: compare heuristic search versus precise/index-assisted navigation and verify that MimiSeek does not treat approximate results as complete.

### 11.3 Dynamic registration/configuration control

Behavior is connected through registry/config/plugin string rather than an obvious static call graph.

Goal: falsify graph-only completeness assumptions.

### 11.4 Large repository / shard pressure control

Relevant unchanged evidence lands outside the most obvious shard/ranking boundary.

Goal: compare snapshot packing/ranking with agentic search and explicit oversize behavior.

### 11.5 Validation-value control

Static reading produces a plausible candidate issue that a focused test/reproduction either confirms or disproves.

Goal: measure precision gain from bounded execution.

### 11.6 FIXED false-positive control

Reviewer sees the materially fixed version without being told it is fixed.

Goal: ensure a “stronger” architecture does not simply learn to repeat historical findings.

### 11.7 Governance self-change control

PR changes reviewer/governance instructions in HEAD.

Goal: prove MimiSeek preserves accepted BASE-derived authority rather than letting the proposed review policy grade itself.

## 12. Experiment fairness

When comparing A-F:

- freeze repository/BASE/HEAD/policy identities;
- freeze model/version/reasoning budget where possible;
- keep expected findings hidden;
- run enough repeated trials to detect stochastic instability where cost allows;
- log tool calls/context consumed without exposing chain-of-thought;
- evaluate findings through governed adjudication, not majority vote;
- compare the same BUGGY and FIXED pairs;
- preserve raw result artifacts so later evaluator improvements can re-score them.

Where an architecture intrinsically exposes different evidence (for example public web versus private frozen repository), classify that as part of the experiment rather than pretending the comparison is perfectly controlled.

## 13. Research decision gates

### Gate R1 — static snapshot sufficiency

Question:

> Does deterministic whole-repository snapshot B match or exceed agentic repository session C on recall/precision across cross-file and normal cases within acceptable size limits?

If yes, a simpler snapshot architecture remains viable.

If no, MimiSeek requires agentic read-only exploration or an equivalent mechanism.

### Gate R2 — structural navigation value

Question:

> Does D materially improve quality/efficiency over primitive C without creating unacceptable false confidence from index incompleteness?

If yes, structural navigation becomes a strong capability candidate.

### Gate R3 — validation value

Question:

> Does E materially improve precision/severity/recall enough to justify sandbox/test complexity?

If yes, bounded validation becomes a reviewer capability requirement/candidate.

### Gate R4 — multi-pass value

Question:

> After a strong E baseline exists, does F materially improve review quality per unit cost/latency?

Only then consider specialist/judge/multi-review production complexity.

## 14. What is already a strong candidate principle versus still open

### Strong candidate principles supported by current internal/external evidence

- exact immutable repository/review identity;
- explicit governing-policy identity;
- repository-wide evidence must be reachable somehow;
- unchanged code can be semantically required review evidence;
- silent context truncation is unacceptable for PASS authority;
- graphs/search/indexes are retrieval mechanisms, not repository truth;
- candidate findings should be actively falsified;
- false positives are first-class quality failures;
- validation evidence can be used to confirm/disprove candidates;
- reviewer semantic authority should remain read-only/least-privileged;
- reviewer quality and launch/handoff reliability must be measured separately.

### Open questions

- static full snapshot versus agentic repository session;
- exact primitive tool set;
- need/value of symbol graph/index;
- need/value of runnable tests/static tools;
- optimal context/ranking strategy;
- Temporary Chat versus another fresh reviewer execution environment;
- direct file transport versus capability-based repository session;
- single reviewer versus specialist/judge/multi-pass architecture;
- private repository context transport and retention details;
- acceptable latency/compute after semantic-quality baselines exist.

## 15. Relationship to MimiSeek stages

This research does **not** replace current Stage 1 bootstrap/provenance work and should not be used to claim Stage 1 implementation exists.

However it is not merely “future CAP handoff” material. It directly informs what MimiSeek must eventually generate, evaluate and distribute as a reviewer.

Expected later use:

- Stage 1 historical corpus provides initial real BUGGY/FIXED/false-positive cases;
- Stage 2 consumer contract should preserve enough exact identity/evidence to support reviewer runs;
- Stage 3 collection preserves outcomes needed to score experiments;
- Stage 4 learning events identify missing/overbroad reviewer mechanics;
- before Stage 5 candidate creation, the repository should decide which reviewer capability architecture has sufficient experimental evidence;
- Stage 5 candidates then encode reviewer methodology/tool-use behavior rather than only a larger prompt;
- Stage 6 regression/protected-capability evaluation should include context/exploration capabilities demonstrated by this research.

No research result here authorizes a candidate, stable reviewer or consumer installation.

## 16. Immediate next research sequence

After the current Stage 1 data-integrity issue is corrected, research can proceed independently without selecting production architecture:

1. turn the unchanged-caller control into a governed MimiSeek research/evaluation case without leaking its answer;
2. select a small representative subset of reconciled CAP/UV BUGGY→FIXED + false-positive cases;
3. define a common `REVIEW_CONTEXT_CORE_V1` identity envelope for experiments only;
4. implement/compose experiment A and B from existing public/snapshot mechanics;
5. implement the smallest read-only repository session C sufficient for `list/read/search/diff/history` over frozen Git objects;
6. run A/B/C on identical hidden cases and score semantic quality plus exploration behavior;
7. only if C shows value, add D structural navigation and repeat;
8. only if candidate findings show validation ambiguity, add E bounded tests/static validation;
9. consider F only after a strong single-reviewer baseline exists.

The goal is not to copy Codex, Copilot, CodeRabbit, Greptile or Sourcegraph. The goal is to isolate which reviewer capabilities measurably improve MimiSeek on governed real defects while preserving exact identity, independence, low false-positive rate and least privilege.
