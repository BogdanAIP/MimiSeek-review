# MimiSeek Review

MimiSeek Review is a standalone, reusable reviewer-improvement system intended for `BogdanAIP/chat-agent-platform`, `BogdanAIP/uv-studio`, and future repositories.

The repository owns the generic reviewer lifecycle, versioning, learning history, regression corpus, learner, independent candidate evaluation, and safe distribution of promoted stable reviewer versions. Project-specific architecture and acceptance rules remain in each consuming repository.

## ChatGPT usage

Canonical workflows live in:

- `.agents/skills/mimiseek-run/SKILL.md` — user command: **«Запусти Мимисик»**;
- `.agents/skills/mimiseek-update/SKILL.md` — in a new independent chat: **«Обнови Мимисик»**.

On ChatGPT surfaces where Personal Skills cannot be installed, use a dedicated ChatGPT Project with `docs/CHATGPT_PROJECT_INSTRUCTIONS.md` as its Project Instructions. The Project is only a launcher/router; the repository `SKILL.md` files remain authoritative.

## Start here

A new development chat must read, in order:

1. `AGENTS.md`
2. `docs/PRODUCT.md`
3. `docs/CURRENT_STATE.md`
4. `docs/ROADMAP.md`
5. the relevant sections of `docs/ARCHITECTURE.md`
6. applicable records under `docs/decisions/`

Do not use chat history as project authority. Git, GitHub, and the document owners above are the durable source of truth.
