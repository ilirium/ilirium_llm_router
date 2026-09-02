# The original project description

**Input, not results — and nobody edits it.** This is the brief the project started from, written by
the owner before any code existed. It is reproduced below **exactly as written**, including its
punctuation, its line breaks and the two trailing spaces that end the first future-work bullet.
Three of its lines run past this project's 100-column convention; they are the brief's own, and
rewrapping them would edit it.

**Where it came from, and it has not moved since.** It was the whole of `README.md` at `cae861d`
(2026-07-27); the `uv` line was added the same day at `5895359`, and the text has been **byte for
byte identical ever since** — 1027 bytes, verified against both commits when this file was created.
It lived on as `README.md`'s "Description" section until Phase 12 rewrote that file and moved the
brief here.

**What it is for.** It is the only statement of what was wanted *before* anything was built, so it
is the thing later work is measured against. Several documents cite it that way —
`../reference/architecture.md` and `../../CLAUDE.md`'s "Goal" both restate parts of it, and both
are derived from this rather than the other way round.

**Do not correct it.** Two things in it are already overtaken by what was built, and that is the
point of keeping it: Pydantic validates the routing-relevant fields only, not whole requests,
because full-body parsing costs fidelity — see `../reference/design-decisions.md` — and "simple
configuration at first" has since acquired a config file with backends, rotation and a corpus
store. A brief that was edited to match the code could not show either.

---

Goal of the project.

I want to be able to connect Claude Code to all Anthropic models (Haiku, Sonnet, Opus, Fable) and to locally served models.

I am going to use LM Studio to serve models. I want to be able to pick up different models in LM Studio to work on.

Claude Code should have access to all its own models and to locally served models simultaneously.

In the future:
- I plan to expand to other commercial harnesses: OpenAI Codex, Google Antigravity, GitHub Copilot, JetBrains Junie.  
- Also, I plan to expand to open-source harnesses: Pi, Hermes, OpenCode, OpenClaw, etc.
- To be able to use cloud-served models through APIs: OpenAI, Google Gemini, OpenRouter, and so on.

Features:
- Simple configuration at first.
- Simple and human-readable code.

Implementation details:
- Language: Python.
- Web framework: FastAPI.
- YAML as config.
- `.env` to store API keys.
- Using type hints.
- Using Pydantic for data validation (requests, responses, messages, etc).
- `uv` for dependencies and the project management.
