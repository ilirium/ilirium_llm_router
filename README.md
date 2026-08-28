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

Every call also leaves a line in a rotating log and a row in `logs/telemetry/calls.csv` — 20 columns
covering tokens, cache hits, time to first byte, duration and how the call ended.

**Milestone 1 is complete** — six phases, 158 tests, and the central claim measured rather than
argued: a single session reached both backends, and a local model handled tool use, file editing and
multi-turn conversation through the router. What it cost is the honest part: prompt caching cuts
time to first byte by 4× on a repeated local prefix, and a local model spends minutes prefilling
where Anthropic answers in a second.

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
one, go in `.env`. Each backend declares how its credential is obtained — `forward` for
Anthropic, `strip` or `inject` for a local server — so in the usual setup the router holds no secret
at all.

## The corpus tools

> **This section is temporary and Phase 12 replaces it.** It documents commands that exist now, in
> the shape they exist now, so the dictionary tooling and the corpus tools are not undocumented in
> the meantime. **A rewrite of this file that drops it drops the only user-facing description these
> commands have** — the commitment is recorded in
> `docs/milestone-2-corpus/implementation-plan.md`, under Phase 12.

The router can archive the bodies it relays — **off by default**, so no `logs/corpus/` is correct
behaviour. Once it is on, these read it back:

```sh
ilirium-llm-router verify-archive logs/corpus/2026-08-25
ilirium-llm-router extract logs/corpus/2026-08-25 --out ./dump --format bodies
ilirium-llm-router extract logs/corpus/2026-*/ --out ./dump --format jsonl
```

| Command | What it does |
|---|---|
| `serve` | start the router; **a bare invocation still does this** |
| `check` | validate the config and print what it means, without starting |
| `extract` | select calls and write them where a person can read them |
| `verify-archive` | read every body back and check each against the digest in its filename |
| `train-dict` | train a compression dictionary from what has been archived |
| `tune-dict` | try dictionary sizes against the same sample and print what each is worth |

**`extract` needs `--out` and `--format`, both required** — a run always states what it produces.
`--format` is repeatable, so `bodies` and `jsonl` can be asked for together and land under one root:

```
<out>/bodies/<session-id>/00001-request.json     the bodies as they crossed the wire
<out>/projects/corpus/<session-id>.jsonl         the session, rebuilt for a history viewer
```

Selection is by `--session`, `--model`, `--agent` and `--path`, **matched exactly** — `--path
/v1/messages` does not sweep in `/v1/messages/count_tokens`. Repeats of one flag are OR'd; different
flags are AND'd.

**Two things worth knowing before trusting the output.** A reconstruction is **not** a Claude Code
session record — it is rebuilt from what crossed the wire, so `cwd`, `gitBranch`, `version`,
`toolUseResult` and agent attribution are absent by construction; **each file says so in its first
record.** And a session resumed the next day has calls in two day folders: **pass both, or the
command refuses and names the one you left out** — converting half of it produces a transcript that
reads as complete and is wrong about when part of it happened.

**Point a history viewer at `<out>`, never at `~/.claude/projects/`.** Viewers that support a custom
Claude directory will read `projects/` and ignore `bodies/`. Writing reconstructions into your real
history directory would corrupt your own record with lossy copies.

**`docs/README.md` is the entry point to the documentation**: what each tier is for and how to find
an answer. In short — `docs/reference/` is what is true, `docs/procedures/` is what you can re-run,
`docs/epd/` is what is still open, and `docs/status.md` is where the project is. `CLAUDE.md` is the
short version an agent loads automatically.

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
