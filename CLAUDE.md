# CLAUDE.md

Guidance for Claude Code (claude.ai/code) working in this repository. **This file is what a session
knows without looking anything up.** Everything else is in `docs/`, which is not auto-loaded — so a
pointer here has to name *when* to open the file, not merely that it exists.

`docs/README.md` is the manual: how documents are filed, named, corrected and retired. Read it before
adding a document or moving one.

## Status

**Milestone 1 is complete — seven phases, and 158 tests *at its close on 2026-08-07*.** The router
dispatches, relays and records; the central claim is settled, that **no protocol translation is
needed and a local model can drive a real coding session through the router.**

**Milestone 2 is open — the corpus.** Do not read the 158 above as the current count; it is
Milestone 1's, and it is dated for that reason.

***How many phases are in is `docs/status.md`'s to say, and this file deliberately no longer says
it.*** *It carried that count and was **wrong** about it — during the very phase chartered to fix
the count, which never opened this file. It was found by a review, not by a check. A number here is
read by every session without being questioned and goes stale at the one moment nobody is rereading
prose: when a phase lands.*

**No number here is current by construction. `docs/status.md` is the only file that holds state** —
read it first, every session, for where the project is, what is on disk and what is next.
How Milestone 1 got there is in `docs/milestone-1-core/`.

**The repository is a bare clone with sibling worktrees**, at
`~/Projects/local/ilirium_llm_router` — `main`, `to-run-server` and one per open branch,
**one branch checked out each**. Editing one **does not** edit another, `logs/` is per-worktree, and a
session started in `main` sees none of the open phase.

*This note said the opposite until 2026-08-26 — that `~/Projects/code-2026/ilirium_llm_router` and the
OneDrive path were the **same directory** (identical inode) and "editing either edits both". **The
symlink half is still true and the checkout is gone**: `~/Projects/code-2026` still resolves into
OneDrive, but the working tree under it was archived to `ilirium_llm_router.zip` on 2026-08-25, and
`~/Projects/local/` is not synced at all. The note was not merely stale — it told a session that two
paths were one directory at the moment the project acquired three that genuinely are not.*

## Working agreement

- **Propose before implementing.** A design answer is not a build order — present the recommendation
  and wait for an explicit go-ahead. Commits do *not* need a separate ask.
- **Ask before touching the machine.** GUI settings, `.env`, long-running local servers: ask rather
  than detect-and-proceed. Consent for one is not consent for the next. **Driving a session — headless
  or interactive — is never done freely: ask, and say what it is for.** A request to run one that does
  not state why is not a request the owner can answer.
- **Exercise it before committing.** Green tests are not evidence. Drive the real thing — and when a
  check comes back negative, fix the instrument before believing the result.
- **Check prior evidence before planning a rerun.** Earlier phases keep answering later ones; mine
  the frozen artefacts first. Phases 3, 4 and 5 each found a third or more of their work already
  done, measured, or misdescribed.
- **Raise it, do not bury it.** A question, a concern, or something found wrong goes in its own
  sentence where it will be read first — never inside a long description, where it reads as commentary
  and gets skimmed. **If something is wrong, say it is wrong rather than working around it.** A
  question carries the detail needed to answer it and the options visible from here, each stated
  plainly enough to choose between without reconstructing the problem first. **A concern raised where
  it will not be read has not been raised.** *Restated from `docs/method/IDM-007-raising-a-concern.md`,
  which is canonical and holds the three prior instances — all three about documents rather than
  people, and all three found by the owner rather than by a check.*

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
- Bodies are archived as content-addressed per-call files, compressed against a shared dictionary
- Backend authentication is a first-class feature, not a leftover
- *(discharged)* First milestone is a minimal end-to-end proxy

## Observability

Every call leaves two traces: a line in a rotating log that uvicorn's own lines join, and a row in
`logs/telemetry/calls.csv` with 20 columns. Usage is read off a **tee** of the passing bytes, never
by parsing and rebuilding them.

→ `docs/reference/observability.md` — read it before touching the recorder, adding a column, or
interpreting a row. In particular: telemetry never breaks a call, the CSV is in **completion order**
so sort before analysing, and nothing body-shaped goes in **the CSV**. *(That last rule was narrowed on
2026-08-17: `EPD-003` was decided, so bodies are archived — but to a separate store, opaque, never as a
CSV column. The recorder's rule is unchanged.)*

→ `docs/reference/corpus.md` — **read it before storing, reading or retraining against the corpus**:
before adding an index column, before changing where a blob or a dictionary lives, before assuming a
day folder needs anything outside itself, and **before quoting a compression ratio**. Four things a
session gets wrong from the name alone: the store is **off by default**, so no `logs/corpus/` is
correct behaviour; **there are three compression levels, not one**; **there is deliberately no
headline ratio** — every figure is a small-sample confirmation that the mechanism works; and **the
store holds bodies only, never headers.**

**That last one has two reasons and a session that carries only the first will propose the wrong
fix.** The one people expect: **a credential never reaches disk** — no `Authorization`, no OAuth
token, no API key, because nothing header-shaped is ever written. The one they do not: the store is
attached to a **tee of the body bytes and never sees a header at all**, so capturing headers is not a
policy switch but a **write-path change**. And the header-derived facts that matter are already
columns — `session_id` and `agent_id`, read at `observe.py:316`. *Added 2026-08-26.*

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

## What we learned about somebody else's software

→ `docs/wiki/` — **read the relevant page before putting work in the background, and before assuming
anything about `zstandard`.** It holds what was established by *reading* a dependency rather than by
trusting its documentation, with the sources linked and the versions pinned.

Two things a session would otherwise get confidently wrong. **`BackgroundTask` is not the mechanism
for background work** — it is awaited inside a request's ASGI cycle — and **`asyncio.create_task` is
the one that quietly stalls every concurrent request**, because CPU-bound work on the event loop
blocks it. And **`zstandard`'s dictionary trainer needs `k` set explicitly**; left to its own
optimiser it is materially worse on a small corpus, and the tool is not the variable.

`docs/wiki/README.md` holds the test that separates this tier from `reference/`: **`reference/` is
this router and the backends it dispatches to; `wiki/` is what it is built from.**

## Open proposals — the EPDs

Questions **written up and deliberately not decided** live in `docs/epd/`, indexed by
`EPD-000-about-these-documents.md`. **Nothing in an EPD is implemented unless it names the date it
was accepted. Do not build from one.**

| | Waiting on | In one line |
|---|---|---|
| `EPD-001` | a decision — its Phase 4 gate is met | Picking a local model mid-session, and subagents on local models |
| `EPD-002` | a decision, on a weakened case | LM Studio has no `count_tokens`; the harm it was organised around was measured and not found |

**`EPD-003` is no longer in that table — it was decided on 2026-08-17** and graduated into
`docs/reference/design-decisions.md`. Bodies are archived as content-addressed per-call files;
fine-tuning is dropped. Its open questions 3–6 are Phase 10 design detail, not parked decisions.

**Do not read `docs/method/`'s `IDM-NNN` documents with that reflex.** The two schemes sit adjacent
and look alike; an **IDM is in force now and you are expected to act on it**, which is the exact
opposite of an EPD. `docs/method/IDM-000-about-these-documents.md` is the index. `IDM-001`,
`IDM-003`, `IDM-005`, `IDM-006`, `IDM-008`, `IDM-010` and `IDM-011` are pointed at below; `IDM-002`
holds the permission allowlist policy **and what else may go in the tracked settings file**;
**`IDM-004` is the protocol for reviewing a plan before it runs — read it before reviewing one,
because its first rule is that the charter decides what the review finds**; **`IDM-009` is its
sibling for work that has *run* — read it before reviewing a finished phase, and note that it puts
the review **before the merge**, so a phase is not merged and then reviewed**; `IDM-007` is the
Working agreement's fourth bullet, canonical.

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
| `fix-slop-docs/<slug>` | a documentation defect whose cause is LLM slop |
| `fix-slop-code/<slug>` | the same, in `src/` |

**The last two name a cause rather than a kind of work** — a defect a model put there — and are kept
separate so that the branch log counts how often it happens without anyone keeping a tally.

**Any prefix may carry a phase number: `<prefix>/phase-N-<slug>`.** The prefix says what kind of work
it is; `phase-N-` says it is numbered work with a plan and a record.

**The plan opens the phase branch** — no separate planning branch, so one phase means one branch and
one merge commit. Work belonging to a later phase never goes on an earlier phase's branch, even
documentation.

**Merge with `--no-ff`, always.** A phase or feature boundary must stay visible in the history; a
fast-forward erases it. And **`git merge` cannot read its message from stdin** — `-F -` works for
`git commit` and fails for `git merge`, so write the message to a temp file.

**Regenerating the branch index is the last step of a merge, and it comes *after* the merge commit.**
Merge `--no-ff` first, then `python3 docs/procedures/branch-index.py --write`, then commit the
regenerated table on the trunk. **It cannot go inside the merge commit** — the new row names the merge
hash, so writing it first is impossible and amending afterwards changes the hash the row just recorded.
A landed branch with no row is a defect `--check` will find and a reader will not.

→ `docs/method/IDM-001-git-branching.md` — **read it before naming a phase folder, before rejecting a
plan, or before recording where a branch went.** It holds the folder⇄branch slug rule and its one-way
check, what happens to a rejected plan (merged and marked, not deleted — the phase number is spent),
and the **four** homes where a branch is recorded — `docs/status.md` while it is in flight,
`docs/reference/branches.md` once it lands, the phase note permanently, and **the merge commit message
for a branch carrying no phase number**, which has no phase note to put it in. **Amended 2026-08-26
with the worktree layout and the one branch here that is not work**: `temp/to-run-server` is `main`
pinned into a worktree because git will not check a branch out twice — it carries no commits, never
merges, and `temp/` is deliberately **not** a fifth row of the prefix table above.

→ `docs/reference/branches.md` — **read it to find out what a branch or a merge hash was**, and before
hand-typing any table of merge hashes: `IDM-001` refused one, and this file is the derived answer that
refusal earns. Two things it holds that no other document does — there are **three** fast-forwarded
branches, not the two every other sentence in this repository counts, and **eight of nineteen branches
carry no phase number**, which is the size of the gap a phase-notes-only scheme leaves. *(Counts move
with the table — re-derive them from it rather than relaying them from here.)*

## Reading

**Read long documents by section.** Grep the headings first — `grep -n '^## ' <file>` — then read
only the sections the task needs. This matters most for a phase's `plan.md` and `notes.md`: they are
the largest documents here and they grow every session. A `cat` over a whole source file, or a
200-line `sed` sweep over a plan, spends the session's room before any work starts.

→ `docs/wiki/claude-code-context-budget.md` — **read it before concluding a session is short of room,
and before deciding that reading less is the fix.** It ranks the levers by measured size, with the
figures dated, which is why no line counts are quoted here. Reading by section is **lever 2**; lever 1
is larger, is about how files are *edited* rather than read, and is a configuration question rather
than a habit. And item 3 is what stops the over-correction: orientation reading in this repository is
**mostly not waste** — the fix is reading it by section, not reading less of it.

## Planning a phase

→ `docs/method/IDM-008-the-register.md` — **read it before writing a phase plan, and before the
phase's closing task.** The plan carries one reachable section listing every name and number the phase
will introduce — modules, config keys, constants, on-disk names, flags, magic numbers — with `❓` on
anything named and never valued, and the closing task checks it against the code. It is not
bookkeeping: on its one run it found eight unvalued names, contradicted a number that had survived two
reviews, and exposed a defect **two forward-review passes had read past**, because a constant and a
config key only look wrong when they sit in adjacent rows.

→ `docs/method/IDM-010-writing-for-the-owner.md` — **read it the first time something in a phase is
worth telling the owner rather than a later session.** Every phase folder carries a
`for-the-owner.md`, written **during** the phase and **to a person**; the notes stay long on purpose
and this file is the digest. **Anything needing a decision is asked out loud instead of being parked
in it.** Pointed at here rather than left in `docs/` because **there is no look-it-up moment** — the
rule applies when somebody is already writing, which is `IDM-007`'s test.

→ `docs/method/IDM-011-the-backlog.md` — **read it before adding anything to `docs/backlog.md`.**
**A session asks the owner before filing an item**; if the answer is no, the decline goes in the
phase's `notes.md`. *This reverses the reflex a session would otherwise have — `IDM-001` and the
backlog's own preamble said for two days that filing an item was the phase's own act, and a session
that learned that will file confidently and wrongly.* Adding an item still goes on whatever branch
you are on and never opens one.

## Shell

**Keep bash commands statically analyzable — no `$(...)`.** The general rule, which is the documented
one: **a command Claude Code cannot fully parse asks for approval instead of being treated as
read-only**, and **anything over 10,000 characters always prompts** because it exceeds what the
analysis parses. Command substitution is the instance met here, so it turns a silent call into a
prompt even for an otherwise-approved command. Use absolute paths, and prefer the Read/Grep/Glob tools
over shelling out to `cat`/`grep`/`find`.

**Compound commands are *not* the trigger.** `cd packages/api && ls` runs unprompted when each part
qualifies on its own; a rule must match **each subcommand** independently. The one exception worth
carrying, because git is constant here: **`cd` into a different directory followed by `git` prompts**,
since that directory's hooks could run. *The "compound commands prompt" claim came from a user-filed
issue and was repeated here on 2026-08-24 without checking; corrected 2026-08-26 against the source.*

→ `docs/method/IDM-002-harness-configuration.md` — **read it before adding an allow rule, and before
assuming a command is silent.** It holds the built-in read-only set that no allowlist can extend, the
wrappers that get stripped before matching, and why `git` is not in that set.

## Opening and closing a milestone

**The two playbooks are `docs/method/IDM-005-opening-a-milestone.md` and
`docs/method/IDM-006-closing-a-milestone.md`. Read the relevant one and work from it rather than
improvising** — this is the one pointer whose omission costs a whole milestone's worth of harvest,
which is why it is called out separately from the pointers above.

*Both were in `docs/README.md` until 2026-08-20, which is where a session that has read this file
before will look. The closing one was **repaired** as it moved: the version there was the narrative of
the restructure that wrote it, and five of the seven decided steps were missing from it — including the
harvest into `reference/lessons.md` and `reference/measurements.md`, which is the thing this pointer
exists to protect.*

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
