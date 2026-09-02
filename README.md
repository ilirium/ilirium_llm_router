# ilirium_llm_router

## TL;DR

**Claude Code accepts exactly one `ANTHROPIC_BASE_URL`.** Point it at Anthropic and you give up your
local models; point it at LM Studio and you give up Haiku, Sonnet, Opus and Fable. This router sits
in front of both and dispatches per request on the model name, so **one session reaches both** —
switch with `/model`, and there is no model list to maintain.

## What it does, and what it does not

**It dispatches, relays and records.** A model named `claude-…` goes to Anthropic; anything else
goes to whatever LM Studio currently has loaded. The rule is a prefix check in code, so a new model
on either side needs no configuration.

**There is no protocol translation, and that is the whole design.** LM Studio natively implements
Anthropic's `POST /v1/messages` — the same SSE event sequence, the same `tools` and `tool_choice` —
so both sides speak one protocol and the router forwards the request **byte for byte**, streaming
the reply back untouched. The body is peeked for `model` and `stream` and is never parsed or
rebuilt.

**Every call leaves two traces.** A line in a rotating log, which uvicorn's own lines join, and a
row in `logs/telemetry/calls.csv` — **20 columns** covering tokens, cache reads and writes, time to
first byte, duration, and how the call ended. Usage figures are read off a **tee** of the passing
bytes, never by parsing them. The CSV is written in **completion order**, so sort it before
analysing.

**What it is not:**

- **Not a translator.** OpenAI, OpenRouter and Gemini speak different wire shapes and would each
  need translation in both directions. Nothing here does that yet — see
  `docs/reference/architecture.md`, which says exactly where the premise stops.
- **Not a load balancer, a cache or a queue.** One process, one hop, no retries of its own.
- **Not a body log.** The log and the CSV hold metadata only. Bodies go to the corpus store, which
  is a separate opt-in thing described below.
- **Not multi-process.** The log, CSV and corpus writers are single-process designs; running several
  workers over one directory would corrupt them.

## Status

**Milestone 1 is complete — seven phases.** The central claim was measured rather than argued: one
session reached both backends, and a local model drove real work through the router — tool use, file
editing, running commands, multi-turn conversation.

**Milestone 2 is open — the corpus, four phases in.** The router can archive the bodies it carries
as opaque, content-addressed, per-call files compressed against a shared dictionary, and read them
back out into something a person can read.

**448 tests.** What it costs is the honest part: prompt caching cuts time to first byte by 4× on a
repeated local prefix, and a local model spends **minutes** prefilling where Anthropic answers in a
second.

## Prerequisites

- **Python 3.13 or newer.**
- **[`uv`](https://docs.astral.sh/uv/)** — used to install the tool and to manage the project.
- **[LM Studio](https://lmstudio.ai/)** for the local half, with a model loaded and its server
  running on `http://localhost:1234`. Anthropic-only use needs none of this.
- **A Claude Code credential** you already use. The router forwards it and holds no key of its own.

## Quick start

**Install it from a checkout.** There is no PyPI release; `uv tool install` takes a local path and
installs a **snapshot**, so a later `git pull` does not change the installed copy.

```sh
git clone git@github.com:ilirium/ilirium_llm_router.git
cd ilirium_llm_router
uv tool install .
```

**Then make sure the executable is on your `PATH`, and open a new shell.**

```sh
uv tool update-shell     # "Ensure that the tool executable directory is on the PATH"
uv tool dir --bin        # where that is — ~/.local/bin on macOS
```

*This step is easy to skip and it is the first thing that bites.* If `~/.local/bin` was already on
your `PATH` you will never see it; if it was not, the next command is `command not found`.

**Check the install answered, then create a config and run.** `--version` needs no config file, so
it works in an empty directory:

```sh
ilirium-llm-router --version      # ilirium-llm-router 0.1.0
mkdir ~/router && cd ~/router
ilirium-llm-router init           # writes config.yaml and .env.example here
ilirium-llm-router check          # validates it and prints what it means
ilirium-llm-router serve          # starts on 127.0.0.1:8787
```

**The working directory is the root.** The router reads the `config.yaml` it finds there and writes
`logs/` beside it — no XDG paths, no `~/.ilirium-llm-router/`, no environment variable. Run it from wherever you
want its logs to live, or pass `-c /path/to/config.yaml` and everything resolves against that file's
directory instead.

**Point Claude Code at it**, in another shell:

```sh
ANTHROPIC_BASE_URL=http://localhost:8787 \
CLAUDE_CODE_ATTRIBUTION_HEADER=0 \
claude
```

Pick a model with `/model`. Anything starting with `claude-` goes to Anthropic; anything else goes
to whatever LM Studio has loaded.

**Re-installing and removing.** The install is a snapshot, so after pulling new commits — or after
merging your own — install again over it:

```sh
cd /path/to/ilirium_llm_router && git pull
uv tool install --force .            # replaces the installed snapshot
uv tool uninstall ilirium-llm-router # removes it entirely
```

## Commands

**The shipped `--help`, quoted rather than paraphrased so the two cannot drift:**

```
usage: ilirium-llm-router [-h] [-c CONFIG] [--version] COMMAND ...

Route Claude Code to Anthropic and to locally served models at the same time.

positional arguments:
  COMMAND
    serve              start the server (the same thing a bare invocation
                       does)
    init               write a starter config.yaml into the current directory,
                       and exit
    check              validate the configuration, report it, and exit without
                       starting the server
    train-dict         train a dictionary now and install it if it beats the
                       one in use; works even when automatic retraining is
                       off, and does not start the server
    tune-dict          sweep maxdict x k and print the whole surface; never
                       installs anything
    extract            read bodies out of one or more day folders, with
                       selection, into files
    verify-archive     read every body back out of one or more day folders,
                       verify each against the digest in its own filename, and
                       report; writes nothing

options:
  -h, --help           show this help message and exit
  -c, --config CONFIG  path to the YAML config file (default: config.yaml)
  --version            print the version and exit
```

**`init`, `--version`, `extract` and `verify-archive` run without a config file.** Every other
command loads one first and exits 1 if it is missing. `init` refuses rather than overwriting an
existing `config.yaml`, and there is no `--force`.

### Reading the corpus back

The router can archive the bodies it relays — **off by default**, so no `logs/corpus/` is correct
behaviour until you turn it on. Once it is on, these read it back:

```sh
ilirium-llm-router verify-archive logs/corpus/2026-08-25
ilirium-llm-router extract logs/corpus/2026-08-25 --out ./dump --format bodies
ilirium-llm-router extract logs/corpus/2026-*/ --out ./dump --format jsonl
```

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

### Dictionaries

`train-dict` trains a compression dictionary from what has been archived and installs it **only if
it beats the one in use**; `tune-dict` sweeps the training parameters and prints what each is worth
without installing anything. Both run offline and neither starts the server. The router also
retrains on its own, in a background thread, on the window set in `config.yaml`.

**There is deliberately no headline compression ratio.** The figures in `docs/reference/corpus.md`
are small-sample confirmations that the mechanism works, and two of them — the trainer's holdout
score and `extract`'s ratio over stored blobs — **measure different things and must not be
compared.**

## Configuration

**`config.yaml` sits in the working directory** and `init` writes a commented starter. Relative
paths inside it resolve against **its own directory**, not against wherever you happen to be
standing. `check` prints every resolved path without starting anything.

**There is no model list.** Routing is a prefix rule in code.

**Secrets go in `.env` beside the config**, and `init` writes a `.env.example` there to copy. Each
backend declares how its credential is obtained, and that is the only knob:

| Mode | What it does | Used by |
|---|---|---|
| `forward` | pass the caller's credential through untouched | Anthropic — your own token is the real one |
| `strip` | remove it | LM Studio, which needs none |
| `inject` | remove it and send the key named by `api_key_env` instead | a backend with its own key |

`api_key_env` is **required** by `inject` and **forbidden** by the other two; both contradictions
are refused at startup rather than resolved silently. In the shipped configuration the router
**holds no secret at all**. Every key in the config is checked — a mistyped one is an error, not a
silently ignored default.

**`read_timeout` bounds silence, not duration.** Every chunk that arrives restarts it, so 1800
seconds for LM Studio is not a half-hour budget for a reply; it is how long the backend may say
nothing before the call is abandoned. Local prefill is genuinely slow — 27924 tokens took 197
seconds — which is why the two backends differ.

**The corpus store is one switch, and it is off.** `calls.csv` is always on because it is cheap and
holds nothing sensitive; neither is true of bodies, which hold source code, file contents and
anything typed.

## Bugs and caveats

**`BUG-001` — non-streamed `/v1/messages` are rejected as rate-limited.** Every `POST /v1/messages`
sent to Anthropic with `stream: false` returns HTTP 429 `rate_limit_error`, while a streamed request
**2.8× larger** to the same model on the same credential succeeds **0.6 seconds later**. It is not a
rate limit; it is a categorical rejection of one request shape wearing a rate limit's status code.
**Claude Code's auto mode is unusable while this holds**, because its safety classifier request is
non-streaming. The workaround is to prefer the harness's own file tools over shelling out. Full
measurement in `docs/bugs/BUG-001-non-streaming-messages-rejected-as-rate-limited.md`.

**The corpus is off by default.** An absent `logs/corpus/` is correct behaviour, not a failure.
Nothing under `dir` is created until the switch is on.

**Nothing deletes an archived body.** There is no retention policy and no pruning — that was left
out of scope deliberately, not overlooked. The store grows until you remove something yourself.

**A long session loses its ending, permanently, at capture time.** Request bodies grow monotonically
through a conversation, and once one crosses `body_max_bytes` (1 MiB by default) **that call is
stored without its request** — the body is not truncated, because a prefix labelled as a whole body
is worse than a hole. In the largest session captured so far, 45 contiguous calls at the end have no
stored request.

**And one hole worth naming:** a caller that disconnects before the response generator's first step
leaves no row in `calls.csv` and no corpus entry. It has been observed once, deliberately, and is
*reported* rather than closed — the shutdown line counts calls arrived against calls recorded, so
the loss is visible.

## Roadmap

**What it does not do yet, and what is planned, are one question** to anyone deciding whether to use
it — so they are in one place.

- **Other cloud backends** — OpenAI, Gemini, OpenRouter. Each needs **protocol translation in both
  directions**, which is the one thing this design does not do today.
- **Other harnesses** — OpenAI Codex, Google Antigravity, GitHub Copilot, JetBrains Junie; Pi,
  Hermes, OpenCode, OpenClaw.
- **The Anthropic rate-limit response headers**, so a 429 can say *which* limit and *when it clears*
  rather than only `rate_limit_error`. Planned as Phase 13.
- **Picking a local model mid-session, and subagents on local models** — written up and **not
  decided**, in `docs/epd/EPD-001-model-selection-and-mixed-model-sessions.md`.
- **Token counting for local backends** — LM Studio has no `count_tokens`. Also written up and not
  decided: `docs/epd/EPD-002-token-counting-for-local-backends.md`.

**Deliberately not planned:** a model list in configuration, retries, multi-process serving, and any
change to `calls.csv`'s columns.

## For developers

```sh
uv sync                 # install dependencies
make                    # list every target
make check              # validate config.yaml and print what it means
make run                # start the router
make test               # run the tests
make lint / make format # ruff, pinned and fetched on demand
```

`make run CONFIG=other.yaml` overrides the config path on any target that takes one. **There is no
reload target** — the app is built by a factory, which `uvicorn --reload` cannot import.

**`make lint` cannot see column width.** `line-length = 100` is set in `pyproject.toml`, but `E501`
is not in ruff's default rule set, so a passing lint says nothing about how long a line is.

**Work happens on branches, one per phase, merged with `--no-ff`** so the boundary stays visible in
the history. The prefix says what kind of work it is: `feat/`, `docs/`, `fix/`, `chore/`, and
`fix-slop-docs/` or `fix-slop-code/` for a defect a language model put there.

**`docs/README.md` is the entry point to the documentation**: what each tier is for and how to find
an answer. In short — `docs/reference/` is what is true, `docs/procedures/` is what you can re-run,
`docs/epd/` is what is still open, and `docs/status.md` is where the project is. `CLAUDE.md` is the
short version an agent loads automatically. The brief this project started from is kept unedited at
`docs/captures/original-project-description.md`.
