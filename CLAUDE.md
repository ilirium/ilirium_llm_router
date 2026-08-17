# CLAUDE.md

Guidance for Claude Code (claude.ai/code) working in this repository. **This file is what a session
knows without looking anything up.** Everything else is in `docs/`, which is not auto-loaded — so a
pointer here has to name *when* to open the file, not merely that it exists.

`docs/README.md` is the manual: how documents are filed, named, corrected and retired. Read it before
adding a document or moving one.

## Status

**Milestone 1 is complete — seven phases, 158 tests.** The router dispatches,
relays and records; the central claim is settled, that **no protocol translation is needed and a
local model can drive a real coding session through the router.**

Current state and what is next are in `docs/status.md`; how Milestone 1 got there is in
`docs/milestone-1-core/`.

Note: `/Users/ilirium/Projects/code-2026/ilirium_llm_router` and the OneDrive path are the *same
directory* (identical inode), not two checkouts. Editing either edits both.

## Working agreement

- **Propose before implementing.** A design answer is not a build order — present the recommendation
  and wait for an explicit go-ahead. Commits do *not* need a separate ask.
- **Ask before touching the machine.** GUI settings, `.env`, long-running local servers: ask rather
  than detect-and-proceed. Consent for one is not consent for the next.
- **Exercise it before committing.** Green tests are not evidence. Drive the real thing — and when a
  check comes back negative, fix the instrument before believing the result.
- **Check prior evidence before planning a rerun.** Earlier phases keep answering later ones; mine
  the frozen artefacts first. Phases 3, 4 and 5 each found a third or more of their work already
  done, measured, or misdescribed.

## Layout and commands

```
config.yaml                 backend definitions, server, log/stats rotation — no model list
.env.example / .env         keys named by a backend's `api_key_env`; only `inject` backends need one
src/ilirium_llm_router/
  config.py                 YAML → validated Config; raises ConfigError with a readable message
  routing.py                the `claude-` prefix rule
  proxy.py                  forwarding: peek the body, rebuild headers, tee the reply back
  observe.py                the two usage scanners, and `Call` — one call from arrival to row
  stats.py                  the CSV: one row per call, size-rotated, header re-emitted
  logging_setup.py          the rotating log; uvicorn's loggers are pointed at it too
  app.py                    FastAPI app factory; the four routes, HTTP client and stats writer
  cli.py                    entry point; `--check` validates config and exits
tests/
docs/                       see docs/README.md
```

`make` on its own lists the targets. The useful ones:

| | |
|---|---|
| `make run` | start the server (`uv run ilirium-llm-router`) |
| `make check` | validate and print the config without starting |
| `make test` | run the tests; `make test ARGS="tests/test_config.py::test_empty_file_is_rejected"` for one |
| `make lint` / `make format` | ruff, fetched on demand via `uvx` — not a dependency, but **pinned** |
| `make sync` | install |
| `make clean` | caches and build artefacts; leaves `logs/` alone |

`make run CONFIG=other.yaml` overrides the config path on any target that takes one. **There is no
reload target** — the app is built by a factory, which `uvicorn --reload` cannot import, so
`uvicorn <module>:app` does not apply either. Start it through the CLI.

Config models set `extra="forbid"`, so a mistyped YAML key is an error rather than a silently ignored
default. Relative log/stats paths resolve against the config file's directory, not the working
directory.

**Never bump the ruff pin as a side effect.** `pyproject.toml` sets `line-length = 100` and the
Makefile pins `RUFF ?= ruff@0.16.1`. **`make lint` will not catch it if you do** — line length is
`E501`, which is not in ruff's default rule set, so a passing lint says nothing about column width.

→ `docs/method/IDM-003-development-tooling.md` — **read it before bumping the pin, before adding a
linter or type checker, or before reading `make lint`'s silence as approval.** It holds why both halves
of the pin exist, how to try a version without committing to it, that an accepted bump goes in its own
commit checked by AST comparison, and that `ty` was tried and **refused** — so a project with no type
checker is a decision rather than an omission.

## Goal

A router that lets one coding harness reach several model backends at once — Claude Code seeing
Anthropic's models **and** locally served LM Studio models simultaneously, switchable by picking a
model. Planned later: other harnesses (Codex, Antigravity, Copilot, Junie; Pi, Hermes, OpenCode,
OpenClaw) and other cloud backends (OpenAI, Gemini, OpenRouter).

## Architecture, in four lines

**No protocol translation.** LM Studio natively implements Anthropic's `POST /v1/messages`, the same
SSE event sequence, `tools` and `tool_choice` — so both sides speak the same protocol and the router
is a **model-name dispatcher**, not a translator. It exists because Claude Code accepts exactly one
`ANTHROPIC_BASE_URL`. Requests are **relayed byte for byte**; the body is peeked for `model` and
`stream` only.

→ `docs/reference/architecture.md` — read it before adding a backend, changing dispatch, or assuming
what a request contains. That premise stops at OpenAI and Gemini, and the file says where.

## Design decisions

**Read `docs/reference/design-decisions.md` before reversing, narrowing or contradicting any of
these.** This is an index, not a summary — a one-line restatement would drift, a title cannot.

- Routing is a prefix rule in code, not a config table
- No special case for background or auxiliary traffic
- Relay the body, log only metadata
- One exception to byte-relay: a broken stream is ended with an SSE `error` event
- Backend authentication is a first-class feature, not a leftover
- *(discharged)* First milestone is a minimal end-to-end proxy

## Observability

Every call leaves two traces: a line in a rotating log that uvicorn's own lines join, and a row in
`logs/calls.csv` with 20 columns. Usage is read off a **tee** of the passing bytes, never by parsing
and rebuilding them.

→ `docs/reference/observability.md` — read it before touching the recorder, adding a column, or
interpreting a row. In particular: telemetry never breaks a call, the CSV is in **completion order**
so sort before analysing, and nothing body-shaped is stored.

## Anthropic models

→ `docs/reference/backend-anthropic.md` — **read it before naming an Anthropic model ID or adding a
sampling parameter.** Model IDs take no date suffix, `thinking.budget_tokens` is rejected, and
`temperature`/`top_p`/`top_k` are rejected outright on current models, so a naive passthrough that
injects them will 400.

## The local backend

→ `docs/reference/backend-lmstudio.md` — read it before assuming what LM Studio supports, or before
choosing a local model or a context size. LM Studio publishes no parity matrix, so that file is
measurement rather than documentation, and its answers expire with each release. Three things in it
are easy to get wrong: nothing sent has ever been *rejected*, a large fixed preamble arrives before
the user types anything, and prefill on a local model is measured in minutes.

## Open proposals — the EPDs

Questions **written up and deliberately not decided** live in `docs/epd/`, indexed by
`EPD-000-about-these-documents.md`. **Nothing in an EPD is implemented unless it names the date it
was accepted. Do not build from one.**

| | Waiting on | In one line |
|---|---|---|
| `EPD-001` | a decision — its Phase 4 gate is met | Picking a local model mid-session, and subagents on local models |
| `EPD-002` | a decision, on a weakened case | LM Studio has no `count_tokens`; the harm it was organised around was measured and not found |
| `EPD-003` | a decision on the fine-tuning goal | Storing every body as a corpus |

**Do not read `docs/method/`'s `IDM-NNN` documents with that reflex.** The two schemes sit adjacent and
look alike; an **IDM is in force now and you are expected to act on it**, which is the exact opposite of
an EPD. `docs/method/IDM-000-about-these-documents.md` is the index. `IDM-001` and `IDM-003` are pointed
at below; `IDM-002` holds the permission allowlist policy.

## Git and branches

**Restated from `docs/method/IDM-001-git-branching.md`, which is canonical. A change goes there
first.** This block is here because these are things a session gets confidently wrong with no reason to
look anything up; it is a second copy of a fact, and that is the risk it carries.

| Prefix | For |
|---|---|
| `feat/<slug>` | product work — anything that changes `src/` |
| `docs/<slug>` | documentation work |
| `fix/<slug>` | a defect |
| `chore/<slug>` | tooling, dependencies, formatter bumps |

**Any prefix may carry a phase number: `<prefix>/phase-N-<slug>`.** The prefix says what kind of work
it is; `phase-N-` says it is numbered work with a plan and a record.

**The plan opens the phase branch** — no separate planning branch, so one phase means one branch and
one merge commit. Work belonging to a later phase never goes on an earlier phase's branch, even
documentation.

**Merge with `--no-ff`, always.** A phase or feature boundary must stay visible in the history; a
fast-forward erases it. And **`git merge` cannot read its message from stdin** — `-F -` works for
`git commit` and fails for `git merge`, so write the message to a temp file.

→ `docs/method/IDM-001-git-branching.md` — **read it before naming a phase folder, before rejecting a
plan, or before recording where a branch went.** It holds the folder⇄branch slug rule and its one-way
check, what happens to a rejected plan (merged and marked, not deleted — the phase number is spent),
and the split between `docs/status.md` for in-flight branches and the phase note for the permanent
record.

## Shell

**Keep bash commands statically analyzable — no `$(...)`.** Command substitution defeats the
guardrails firewall even for otherwise-approved commands, so it turns a silent call into a prompt.
Use absolute paths, and prefer the Read/Grep/Glob tools over shelling out to `cat`/`grep`/`find`.

## Opening and closing a milestone

**Both playbooks are in `docs/README.md`. Read the relevant one and work from it rather than
improvising** — this is the one pointer whose omission costs a whole milestone's worth of harvest,
which is why it is called out separately from the pointers above.

## Stack

Python 3.13, FastAPI, type hints throughout. **Pydantic** for the routing-relevant fields only —
full-body parsing costs fidelity when either side adds a field. **YAML** for configuration, **`.env`**
for keys, **`uv`** for dependencies.

## Style

Two non-negotiables from the README: **simple configuration** and **simple, human-readable code**.
Prefer an obvious explicit mapping over a clever generic one. Comment density here is high and that
is deliberate — it was measured in Phase 6 and kept.

A path is written in backticks; a rename is written with `→`, which
`docs/procedures/link-check.py` depends on.
