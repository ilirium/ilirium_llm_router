# Phase 12 — the installer and the `README.md` rewrite

**Branch:** `feat/phase-12-installer-and-readme`, forked from `main` at `5cdc1c9`.
**Merge commit:** *(to be filled at the merge)*

**The question it exists to close:** can the router and its corpus tools be installed and used
without the repository, and does the `README.md` say so?

---

## What is settled, and by whom

*Positions this plan does not get to revisit. Anything load-bearing that is **not** in this table is
the plan's own assumption — see `../../backlog.md`, "A forward review must classify each position by
authority".*

| | Settled | By whom, when |
|---|---|---|
| 1 | **The cwd is the config and log root.** An installed router reads `./config.yaml` and writes logs beside it. No XDG paths, no `~/.ilirium-llm-router/`, no new environment variable | Owner, 2026-09-02, when the four options were put |
| 2 | **A first `config.yaml` comes from an `init` subcommand**, not from copying one out of the repo and not from a block pasted in the `README.md` | Owner, 2026-09-02 |
| 3 | **Install is `uv tool install <local path>`, a snapshot** — not editable, not git-over-SSH, not PyPI | Owner, 2026-09-02 |
| 4 | **The original brief moves to `../../captures/original-project-description.md`**, not to `reference/historical/` | Owner, 2026-09-02, after the tier objection was raised |
| 5 | **The `README.md` carries ten sections** — listed below. Four were added after the first eight were settled, when the question "what might be missing" was put | Owner, 2026-09-02, in two passes |
| 6 | **The caveats section is four items** — `BUG-001`, corpus off by default, nothing is ever deleted, and long sessions lose their tail at `body_max_bytes` | Owner, 2026-09-02 |
| 7 | **The phase is scoped to the installer and a basic `README.md`.** Mixing several subjects in one phase produced bloat before, and this phase is deliberately narrow | Owner, 2026-09-02 |
| 8 | **Phase 12 inherits Phase 11's commitment**: the temporary corpus-tools section may not be dropped without its content landing somewhere | `../implementation-plan.md`, Phase 12 entry |

*This plan carried one unratified position — that the `README.md` should document re-installing
after a merge, which the owner's "snapshot (plain install)" choice had not asked for. **It was put and
accepted on 2026-09-02**, and is now settled row 5's section 5. Recorded rather than deleted: it is
the worked example of the rule in `../../backlog.md` that a plan's own assumptions are reported as
unratified rather than inherited.*

**The ten sections, in order.** *Three of the four late additions are absorbed rather than
standalone, which is the plan's own judgement and not the owner's instruction — the owner chose the
content, not the arrangement.*

| | Section | Note |
|---|---|---|
| 1 | TL;DR | |
| 2 | What it does, and what it does not | The log line and the 20-column CSV live here rather than in an observability section of their own |
| 3 | Status | **Says seven phases for Milestone 1. The current file says six and is wrong** |
| 4 | Prerequisites | **Added 2026-09-02.** Python 3.13+, `uv`, LM Studio for the local half. Its own section because it is what a reader scans before deciding to try anything |
| 5 | Quick start | Install, run, point Claude Code at it — **and upgrade and uninstall**, added 2026-09-02 and absorbed here rather than given a section |
| 6 | Commands | **Where Phase 11's temporary corpus-tools content lands**, discharging the inherited commitment |
| 7 | Configuration | `config.yaml`, `.env`, and the `forward`/`strip`/`inject` credential model — the router usually holds no secret, which belongs here rather than in Quick start |
| 8 | Bugs and caveats | Four items, per settled row 6 |
| 9 | Roadmap | **Added 2026-09-02**, replacing what leaves with the brief. Placed **beside** what the router does not do, because "not" and "not yet" are the same question to a reader deciding whether to use it |
| 10 | For developers | `make` targets, the repo flow, **and the `docs/` pointer** — added 2026-09-02, and it is the one addition that is a *rescue*: it exists in the file today at `README.md:100–103` and no other planned section is its home |

---

## Groups and tasks

### Group A — establish what already works

**Nothing here changes a file.** The phase's premise is that installation is nearly free; five of
seven Milestone 1 phases found their premise wrong, so it is checked before it is built on.

1. **Install the tool and drive it from a directory that is not the repo.** `uv tool install` from the
   local path, then `serve`, `check`, `extract` and `verify-archive` from a scratch directory.
   Record what each does. **Needs the owner's go-ahead — it installs software on the machine.**
2. **Establish where an installed run writes.** Confirm by looking, not by reading `config.py`: that
   `./config.yaml` is found, that `logs/` lands beside it, and that `.env` is read from cwd.
3. **Establish what the corpus tools need.** `extract` and `verify-archive` return before the config
   loads (`cli.py:38–42`); confirm they run with no `config.yaml` present at all.

### Group B — the installer

4. **`init`, as a subcommand.** Writes a commented starter `config.yaml` into cwd. Refuses rather than
   overwrites. Decide in the task whether it also writes `.env.example`, and record why.
5. **The template as package data.** It must ship inside the wheel, not be read from the source tree.
   Confirm by running `init` from an installed tool with no repo on disk.
6. **Tests for `init`.** Fresh directory, refusal on an existing file, and the written file passing
   `check` unmodified — the last is the one that matters.

### Group C — the documents

7. **Extract the brief** to `../../captures/original-project-description.md`, kept as written, with a
   header saying what it is and that it is not edited.
8. **Rewrite `README.md`** to the eight sections. The corpus-tools content lands in "commands"; the
   temporary-section warning goes with it.
9. **Check the four late additions landed**, and that nothing the old `README.md` carried was lost
   by omission — the `docs/` pointer is the known case, and the sweep is for the unknown ones.

### Group D — close

10. **Register check** against the code, per `../../method/IDM-008-the-register.md`.
11. **Sweep and close out**, then merge — sweep *before* the merge message, per
    `../../method/IDM-001-git-branching.md`.

---

## The register

*Every name and number this phase introduces. `❓` marks anything named and never valued;
`IDM-008` requires the closing task to check this against the code.*

| Name | Kind | Value |
|---|---|---|
| `init` | CLI subcommand | `ilirium-llm-router init` |
| `config.yaml` | on-disk name written by `init` | unchanged from the repo's name |
| the template's location | package data path | ❓ — decided in Task 5 |
| `.env.example` | on-disk name, maybe written by `init` | ❓ — decided in Task 4 |
| `init`'s refusal exit code | integer | ❓ — decided in Task 4 |
| `README.md` sections | count | 10 |
| caveats listed | count | 4 |
| install command | documented string | `uv tool install <path to the repo worktree>` |
| `DEFAULT_CONFIG_PATH` | existing constant, unchanged | `Path("config.yaml")` — `cli.py:30` |
| Milestone 1 phase count in `README.md` | corrected number | **7** (it reads 6 today) |

---

## Done when

- `uv tool install` from a local path yields a working `ilirium-llm-router` that `serve`s, `check`s,
  `extract`s and `verify-archive`s **from a directory that is not the repository**.
- `init` produces a `config.yaml` that `check` accepts with no edits, on a machine with no checkout.
- `README.md` carries the ten sections, the brief is in `captures/`, and no `❓` remains above.
- `make test` passes, and the count is recorded rather than predicted.
