# MimiSeek Review

MimiSeek Review is a standalone, reusable code-review system intended for `BogdanAIP/chat-agent-platform`, `BogdanAIP/uv-studio`, and future repositories.

The repository owns the generic reviewer lifecycle, versioning, learning history, regression corpus, learner, and independent evaluator. Project-specific architecture and acceptance rules remain in each consuming repository.

## Start here

A new development chat must read, in order:

1. `AGENTS.md`
2. `docs/PRODUCT.md`
3. `docs/CURRENT_STATE.md`
4. `docs/ROADMAP.md`
5. the relevant sections of `docs/ARCHITECTURE.md`
6. applicable records under `docs/decisions/`

Do not use chat history as project authority. Git, GitHub, and the document owners above are the durable source of truth.
