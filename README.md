# ilirium_llm_router

Repo: https://github.com/ilirium/ilirium_llm_router
Git: git@github.com:ilirium/ilirium_llm_router.git

## What it does today

Claude Code accepts exactly one `ANTHROPIC_BASE_URL`. Point it at Anthropic and you give up your
local models; point it at LM Studio and you give up Haiku, Sonnet, Opus and Fable. This router sits
in front of both and dispatches per request on the model name, so one session reaches both.

**It works.** A `claude-…` model behaves as a normal session; a model loaded in LM Studio drives
real work — tool use, file editing, running commands — through the same address. No protocol
translation is involved: LM Studio implements the same `/v1/messages`, so the request body is
forwarded byte for byte and the reply streamed back untouched.

Every call also leaves a line in a rotating log and a row in `logs/calls.csv` — 20 columns covering
tokens, cache hits, time to first byte, duration and how the call ended.

## Quick start

```sh
uv sync                 # install
make check              # validate config.yaml and print what it means, without starting
make run                # start the router
```

Then point Claude Code at it:

```sh
ANTHROPIC_BASE_URL=http://localhost:8787 \
CLAUDE_CODE_ATTRIBUTION_HEADER=0 \
claude
```

Pick a model with `/model`: anything starting with `claude-` goes to Anthropic, anything else goes
to whatever LM Studio currently has loaded. There is no model list to maintain — the rule is a
prefix check in code, so new models on either side need no configuration.

`make` on its own lists every target. Configuration is `config.yaml`; secrets, if a backend needs
one, go in `.env`. In the usual setup the router holds no secret at all — the credential arriving
from Claude Code is forwarded to Anthropic and stripped before anything reaches LM Studio.

`CLAUDE.md` is the working reference: what has been measured, what was decided and why.

## Description

*The original brief, kept as written. Everything above is what has since been built.*

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
