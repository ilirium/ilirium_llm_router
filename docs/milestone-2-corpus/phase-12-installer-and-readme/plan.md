# Phase 12 — the installer and the `README.md` rewrite

**Branch:** `feat/phase-12-installer-and-readme`, forked from `main` at `5cdc1c9`.
**Merge commit:** *(to be filled at the merge)*

**The question it exists to close:** can the router and its corpus tools be installed and used
without the repository, and does the `README.md` say so?

**Revised 2026-09-02 after the forward review.** The first version is commit `80914a0`; what the
review found and what was accepted is in `notes.md`. **Three of its findings were defects in `src/`
rather than in the plan**, which is why this version has tasks the first did not.

---

## What is settled, and by whom

*Positions this plan does not get to revisit. Anything load-bearing that is **not** in this table is
the plan's own assumption — see `../../backlog.md`, "A forward review must classify each position by
authority".*

| | Settled | By whom, when |
|---|---|---|
| 1 | **The cwd is the config and log root.** An installed router reads `./config.yaml` and writes logs beside it. No XDG paths, no `~/.ilirium-llm-router/`, no new environment variable | Owner, 2026-09-02 |
| 2 | **A first `config.yaml` comes from an `init` subcommand**, not from copying one out of the repo and not from a block pasted in the `README.md` | Owner, 2026-09-02 |
| 3 | **Install is `uv tool install <local path>`, a snapshot** — not editable, not git-over-SSH, not PyPI | Owner, 2026-09-02 |
| 4 | **The original brief moves to `../../captures/original-project-description.md`**, not to `reference/historical/` | Owner, 2026-09-02, after the tier objection was raised |
| 5 | **The `README.md` carries ten sections** — listed below | Owner, 2026-09-02, in two passes |
| 6 | **The caveats section is four items** — `BUG-001`, corpus off by default, nothing is ever deleted, and long sessions go unstored past `body_max_bytes` | Owner, 2026-09-02 |
| 7 | **The phase is scoped to the installer and a basic `README.md`.** Mixing subjects produced bloat before | Owner, 2026-09-02 |
| 8 | **Phase 12 inherits Phase 11's commitment**: the temporary corpus-tools section may not be dropped without its content landing somewhere | `../implementation-plan.md`, Phase 12 entry |
| 9 | **The `.env` search is fixed in this phase.** It is a `src/` defect the review found, and the `README.md` cannot honestly describe where secrets go until it is fixed | Owner, 2026-09-02, after the review |
| 10 | **A `--version` flag is added in this phase.** There is none today | Owner, 2026-09-02, after the review |
| 11 | **`init` gets no `--force`.** It refuses on an existing file, full stop | Owner, 2026-09-02 — the option was offered and declined |
| 12 | **`status.md`'s Milestone 2 phase count is fixed inside this phase**, rather than on a separate `fix-slop-docs/` branch | Owner, 2026-09-02 |

*This plan carried one unratified position — that the `README.md` should document re-installing
after a merge, which the owner's "snapshot (plain install)" choice had not asked for. **It was put
and accepted on 2026-09-02.** Recorded rather than deleted: it is the worked example of the
`../../backlog.md` rule that a plan's own assumptions are reported as unratified rather than
inherited.*

**The ten sections, in order.** *The arrangement is the plan's own judgement; the owner chose the
content.*

| | Section | Note |
|---|---|---|
| 1 | TL;DR | |
| 2 | What it does, and what it does not | The log line and the 20-column CSV live here rather than in an observability section |
| 3 | Status | **Milestone 1 was seven phases, not six. Milestone 2 is four phases in. The test count is whatever `make test` reports at the merge** — see the register |
| 4 | Prerequisites | Python 3.13+, `uv`, LM Studio for the local half |
| 5 | Quick start | Install, **`uv tool update-shell` and a new shell** — the owner hit `command not found` where this session did not — run, point Claude Code at it, **verify with `--version`**, upgrade, uninstall |
| 6 | Commands | **Where Phase 11's temporary corpus-tools content lands**, discharging the inherited commitment |
| 7 | Configuration | `config.yaml`, `.env`, and the `forward`/`strip`/`inject` credential model |
| 8 | Bugs and caveats | Four items, per settled row 6. `BUG-001` is `../../bugs/BUG-001-non-streaming-messages-rejected-as-rate-limited.md` |
| 9 | Roadmap | Placed beside what the router does not do, because "not" and "not yet" are one question to a reader deciding whether to use it |
| 10 | For developers | `make` targets, the repo flow, **and the `docs/` pointer** rescued from `README.md:100–103` |

---

## Groups and tasks

**Why the order is what it is.** Group C must finish before Group D: task 15 documents `init`,
`--version` and the `.env` fix, and task 12's tests can still change their shape. **The phase
therefore looks untouched on its most visible artefact until late, and that is deliberate.**

### Group A — open the phase *(complete, 2026-09-02)*

1. **Record the branch in `../../status.md`'s "In-flight branches".** *The review found it missing —
   `status.md` says "None" while this branch is open, which that section's own text records as a
   defect that has happened before.* Fork point `5cdc1c9`, `feat/` prefix.
2. **`evidence/README.md`** — what this phase freezes, or a statement that it freezes nothing, which
   is itself the record.

### Group B — establish what already works *(complete, 2026-09-02)*

**Nothing here changes a file.** The phase's premise is that installation is nearly free; five of
seven Milestone 1 phases found their premise wrong (`../../reference/lessons.md:19`), so it is
checked before it is built on.

3. **Install the tool and drive it from a directory that is not the repo.** `uv tool install` from
   the local path, then `serve` and `check`. **Needs the owner's go-ahead — it installs software.**
   *Two inputs the first plan did not name:* Group B's `config.yaml` is copied by hand from the repo
   **for testing only** — settled row 2 governs what is *documented*, not how this task gets a file
   before task 10 exists.
4. **Establish where an installed run writes.** Confirm by looking, not by reading `config.py`: that
   `./config.yaml` is found and that `logs/` lands beside it. **And drive the `.env` defect** rather
   than trusting the review's reading of python-dotenv.
5. **Establish what the corpus tools need.** `extract` and `verify-archive` return before
   `load_config` — `cli.py:40–43` against `cli.py:46`. Confirm they run with no `config.yaml` at
   all. *The corpus day folders live **only** in `to-run-server/logs/corpus/`; `logs/` is
   per-worktree and this worktree has none.* `extract` returns 1 when nothing is selected, so this
   needs real rows.

### Group C — the installer *(complete, 2026-09-02)*

6. **`init`, and it must return before `load_config`.** *The review's sharpest finding: `main()` has
   exactly two early returns, so an ordinary subcommand would fail with `Config file not found` in
   the empty directory `init` exists to serve.* Writes a commented starter `config.yaml` into cwd;
   refuses on an existing file, with no override (settled row 11).
7. **The template — its content, its name and how it ships.** Whether it is the repo's `config.yaml`
   verbatim, a trimmed version, or newly written. It must ship **inside the wheel**;
   `pyproject.toml` has no `[tool.uv.build-backend]` section and there is no `MANIFEST.in`, and
   whether `uv_build` includes non-Python files by default is **not known** — establish it, do not
   assume it.
8. **Fix the `.env` search.** `load_dotenv()` walks from the *caller's file* to `/` and never reads
   cwd; it worked in the repo by accident. Within settled row 1: no new environment variable, no XDG
   path.
9. **Add `--version`**, returning before `load_config` for the same reason as task 6.
10. **Tests** for `init`, the `.env` fix and `--version`. For `init`: a fresh directory, refusal on
    an existing file, and **the written file passing `check` unmodified** — the last is the one that
    matters. *It works only because the template uses `forward`/`strip`; an `inject` template would
    fail `_check_api_keys` for a reason that has nothing to do with `init`.*

### Group D — the documents

11. **Extract the brief** to `../../captures/original-project-description.md`, kept as written, with
    a header saying what it is and that it is not edited. **Add its row to
    `../../captures/README.md`'s index table**, which currently lists one of what will be two files.
12. **Fix `../../status.md`'s Milestone 2 count.** Line 35 says four; lines 87 and 117 say three,
    both written before Phase 11 merged. **Four is correct** — 8, 9, 10, 11.
13. **Rewrite `README.md`** to the ten sections. The corpus-tools content lands in "commands"; the
    temporary-section warning goes with it. **The `body_max_bytes` caveat says calls go *unstored*,
    never that bodies are truncated** — `corpus.py:130`: *"a prefix labelled as a whole body is
    worse than a hole"*.
14. **Sweep the old `README.md` for anything no planned section inherits.** The `docs/` pointer is
    the known case — **and the risk is a duplicate, not a loss**: it sits at the tail of the
    corpus-tools block that task 13 moves wholesale into section 6, so it can land twice. Lines 3–4
    carry repo and git URLs that map to no planned section.

### Group E — close

15. **Register check** against the code, per `../../method/IDM-008-the-register.md`.
16. **Update `../implementation-plan.md`'s Phase 12 entry** to record what was built, as Phases 10
    and 11 did, and mark the inherited commitment discharged.
17. **Sweep placeholders, close out `status.md`, merge `--no-ff`** — sweep *before* the message —
    **then regenerate the branch index** with `docs/procedures/branch-index.py --write` and commit
    it on the trunk. *It cannot go inside the merge commit: the row names the merge hash.*

---

## The register

*Every name and number this phase introduces. `❓` marks anything named and never valued;
`IDM-008` requires task 15 to check this against the code.*

| Name | Kind | Value |
|---|---|---|
| `init` | CLI subcommand | `ilirium-llm-router init` |
| `--version` | CLI flag | `--version`, no short form |
| `--force` on `init` | CLI flag | **none — declined**, settled row 11 |
| `_init` | function in `cli.py` | `_init(path: Path) -> int`, in `cli.py` |
| `CONFIG_TEMPLATE` | module constant in `cli.py` | `"config-template.yaml"` |
| `.env` search path | where `load_dotenv` looks | `args.config.parent / ".env"` |
| `init`'s refusal exit code | integer | `1`, matching the config-error path at `cli.py:49` |
| the template's file name | on-disk name inside the package | `config-template.yaml` |
| the template's location | package data path | `src/ilirium_llm_router/config-template.yaml` |
| the template's content | a copy, a subset, or newly written | **`config.yaml` byte for byte**, pinned by a test |
| `uv_build` package-data configuration | `pyproject.toml` section | **none** — verified by building the wheel and reading it |
| `.env.example` | on-disk name written by `init` | **written**, beside the config — owner's decision, reversing this phase's own |
| `ENV_TEMPLATE` | module constant in `cli.py` | `"env-template"` |
| `ENV_EXAMPLE` | module constant in `cli.py` | `".env.example"` |
| the env template's location | package data path | `src/ilirium_llm_router/env-template` |
| `config.yaml` | on-disk name written by `init` | unchanged from the repo's name |
| `original-project-description.md` | on-disk name, in `../../captures/` | fixed |
| the test file | on-disk name, in `tests/` | `tests/test_cli_init.py` |
| `DEFAULT_CONFIG_PATH` | existing constant, unchanged | `Path("config.yaml")` — `cli.py:30` |
| install command | documented string | `uv tool install <path to the repo worktree>` |
| `README.md` sections | count | 10 |
| caveats listed | count | 4 |
| Milestone 1 phases, in `README.md` | corrected number | **7** (it reads 6 today) |
| Milestone 2 phases, in `README.md` and `status.md` | corrected number | **4** (`status.md` says both 4 and 3) |
| test count in `README.md` | number | whatever `make test` reports at the merge — **it reads 158 today**, which is Milestone 1's |

---

## Done when

- `uv tool install` from a local path yields a working `ilirium-llm-router` that `serve`s, `check`s,
  `init`s, `extract`s and `verify-archive`s **from a directory that is not the repository**.
- **The template is proven to ship inside the wheel** — by inspecting the installed package, since a
  machine without this repository is not available to test on.
- `init` produces a `config.yaml` that `check` accepts with no edits.
- `.env` in the working directory is read by an installed router, and `--version` prints and exits 0
  with no config present.
- `README.md` carries the ten sections, the brief is in `captures/` and indexed there, and no `❓`
  remains above.
- `make test` passes, and the count is recorded rather than predicted.
