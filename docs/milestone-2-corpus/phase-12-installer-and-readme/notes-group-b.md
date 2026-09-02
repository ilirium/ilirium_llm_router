# Phase 12 — Group B: establish what already works

*Tasks 3, 4 and 5. Entry point is `notes.md`. Nothing in this group changed a file in the
repository.*

**The group's purpose was to test the phase's premise before building on it** — five of seven
Milestone 1 phases found their premise wrong. **The premise held, and the group still found the
thing the phase now exists to fix.**

## Task 3 — install, and drive from a directory that is not the repository

**Done 2026-09-02, on the owner's explicit go-ahead**, which the plan required because the task
installs software.

```
uv tool install ./main
Installed 1 executable: ilirium-llm-router   →   ~/.local/bin/ilirium-llm-router
```

**It installed clean, first try, with no `pyproject.toml` change.** `ilirium-llm-router 0.1.0`, with
`zstandard`, `uvicorn`, `pydantic` and the rest resolved into uv's own tool environment.

**From an empty scratch directory, two known states reproduced exactly:**

| Command | Result |
|---|---|
| `check`, no config present | `error: Config file not found: config.yaml`, exit **1** |
| `--version` | `unrecognized arguments: --version`, exit **2** |

## Task 4 — where an installed run writes

**The cwd model is confirmed, and it needed no code.** With a `config.yaml` copied into the scratch
directory, `check` resolved **every** path into that directory:

```
Config:   …/scratchpad/t3/config.yaml
Log:      …/scratchpad/t3/logs/telemetry/router.log
Stats:    …/scratchpad/t3/logs/telemetry/calls.csv
Corpus:   off  (would write to …/scratchpad/t3/logs/corpus)
```

**Nothing in the repository and nothing in the package.** Settled row 1 is what the code already
does, for an installed binary, from a foreign working directory.

**And `check` created no `logs/`** — `ls -a` afterwards showed only `config.yaml`. That is
`cli.py`'s documented promise that `--check` configures no logging, demonstrated for an installed
tool rather than inferred from the source. *Phase 11 established the same thing for a worktree; this
is the first time it has been shown from outside the repository.*

### The `.env` defect, driven rather than read

**The forward review predicted this from python-dotenv's source. It is now measured.** Full probe
and control in `evidence/env-discovery-probe.md`.

A `.env` containing `PHASE12_TEST_KEY=probe-value` sat in the working directory. An `inject` backend
naming that variable **reported it unset**, exit 1. Exporting the same variable made the identical
config valid, exit 0 — **so only `.env` discovery is at fault**, not the backend, the config or
`_check_api_keys`.

**The part worth carrying into the fix and into the `README.md`:** the error says *"Set it in your
.env file"* — **advice the user has already followed.** The file is in the directory they are
standing in. A silent failure would be better than an instruction that cannot work.

## Task 5 — what the corpus tools need

**Both run with no `config.yaml` anywhere**, from an empty directory, confirming `cli.py`'s two
early returns rather than trusting them.

| Command | Result |
|---|---|
| `verify-archive <day>` | exit **0** — 470 blobs, 0 failed, every blob verified against the digest in its own filename |
| `extract <one day>` | exit **1** — refused: a selected session also has calls in the sibling day |
| `extract <both days>` | exit **0** — 652 rows selected, **51 conversation files** written |

**The refusal is the more interesting result and it is correct behaviour.** Phase 11's cross-day
guard fired: reconstructing a session from one of the two days it spans *"would date part of the
transcript wrongly with nothing in the file to say so."* The plan expected task 5's exit 1 to come
from an empty selection; it came from a better reason.

*The day folders live only in `to-run-server/logs/corpus/`, as the plan warned — `logs/` is
per-worktree and neither `main` nor this worktree has the 2026-08-2x folders.*

## What is not done in this group

**The `serve` half of task 4.** Starting a long-running local server is named in `CLAUDE.md`'s
working agreement as something to ask about separately, and the owner's go-ahead covered the
install. **What it would add:** proof that `logs/telemetry/` is *created* in the working directory
rather than only *resolved* to it. The path resolution is established above; the write is not.
