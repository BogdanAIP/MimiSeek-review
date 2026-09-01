# MimiSeek Review

MimiSeek Review is a standalone, reusable reviewer-improvement system intended for `BogdanAIP/chat-agent-platform`, `BogdanAIP/uv-studio`, and future repositories.

The repository owns the generic reviewer lifecycle, versioning, learning history, regression corpus, learner, independent candidate evaluation, and safe distribution of promoted stable reviewer versions. Project-specific architecture and acceptance rules remain in each consuming repository.

## ChatGPT usage

MimiSeek Review exposes two ChatGPT roles:

- native skill `mimiseek-review-run`, with canonical repository workflow `.agents/skills/mimiseek-run/SKILL.md`;
- native skill `mimiseek-review-update`, with canonical repository workflow `.agents/skills/mimiseek-update/SKILL.md`, used in a new independent chat for promotion/distribution authority.

The installed skill is an entry point; the repository is the evolving source of truth. During bootstrap, the run role continues the next canonical repository-development action rather than pretending the later learning pipeline already exists.

On ChatGPT surfaces where native skills cannot be installed, `docs/CHATGPT_PROJECT_INSTRUCTIONS.md` may be used only as an equivalent routing/bootstrap layer.

## Start here

A new development chat must read, in order:

1. `AGENTS.md`
2. `docs/PRODUCT.md`
3. `docs/CURRENT_STATE.md`
4. `docs/ROADMAP.md`
5. the relevant sections of `docs/ARCHITECTURE.md`
6. applicable records under `docs/decisions/`

Do not use chat history as project authority. Git, GitHub, and the document owners above are the durable source of truth.
