# The next session's prompt

*The one file in `docs/` allowed to go stale, per `README.md` — which is why it is rewritten at each
handoff rather than left. **Replaced 2026-09-02**, at the close of the session that merged
`fix-slop-docs/opening-playbook-not-run-table` and took Phase 12 through Group C. Whatever comes
next replaces it again.*

---

**Phase 12 is open and unfinished. Groups A, B and C are done; D and E are not.** Branch
`feat/phase-12-installer-and-readme`, worktree `…/phase-12-installer-and-readme`, nine commits,
**448 tests**, tree clean. `main` is at `5cdc1c9`.

**Start in the phase worktree**, at
`/Users/ilirium/Projects/local/ilirium_llm_router/phase-12-installer-and-readme`. Not in `main` —
`main` has none of this work, and `logs/` is per-worktree.

## Read these, in this order

1. **`docs/status.md`** — first, every session. The only file that holds state.
2. **`docs/milestone-2-corpus/phase-12-installer-and-readme/plan.md`** — 17 tasks in five groups,
   the settled table, and the register. **Groups A–C carry a completion marker; D and E carry none,
   which is deliberate** — a "not started" marker is the defect this repository keeps finding.
3. **`notes.md` in that folder, then `notes-group-c.md`** — C is where the `src/` work is.
4. `docs/backlog.md` when choosing work, not before.

**Do not read the `review-charter.md` unless you are running another review.** It is spent.

## What is left: tasks 11–17

**Group D — the documents.** Extract the brief from `README.md` to
`docs/captures/original-project-description.md` **and add its row to `docs/captures/README.md`'s
index table**. Fix `docs/status.md`'s Milestone 2 count — line 35 says four, two other places
say three; **four is right**. Then **rewrite `README.md` to the ten sections** the plan lists, and
sweep the old `README.md` for anything no planned section inherits.

**Group E — close.** Register check, update `milestone-2-corpus/implementation-plan.md`'s Phase 12
entry, sweep placeholders, close out `status.md`, merge `--no-ff`, **then** regenerate the branch
index.

## Four things about the README rewrite that are already decided

- **Ten sections**, listed in the plan with a note each. Section 6 (Commands) is where Phase 11's
  temporary corpus-tools block lands, which is the commitment Phase 12 inherited.
- **Quote the shipped `--help` rather than paraphrase it**, so the two cannot drift.
- **Milestone 1 was seven phases; the file says six.** Milestone 2 is four phases in. The test count
  in the file reads **158**, which is Milestone 1's — it must become whatever `make test` reports at
  the merge.
- **The `body_max_bytes` caveat says calls go *unstored*, never that bodies are truncated.**
  `corpus.py:130`: *"a prefix labelled as a whole body is worse than a hole."*
- **Quick start must carry `uv tool update-shell`.** The owner hit `command not found` where this
  session did not, because `~/.local/bin` was already on its `PATH` — the environment that makes a
  step unnecessary makes it invisible to whoever writes the instructions.

## What Group C built, and the one thing to know about each

| | |
|---|---|
| `init` | writes `config.yaml` **and** `.env.example` beside the config; **returns before `load_config`**, or it would need the file it exists to create |
| `--version` | an argparse `action="version"`, so it answers in a directory holding nothing |
| the `.env` fix | `load_dotenv(args.config.parent / ".env")` — see below, this is the phase's largest finding |
| two templates | `config-template.yaml` and `env-template`, package data, **byte-identical to the repo's copies and pinned by tests** |

**`uv_build` ships non-Python package data with no configuration** — verified by building a wheel
and reading it, not assumed. There is no `[tool.uv.build-backend]` section and no `MANIFEST.in`.

## Five things a session will get wrong here

- **`load_dotenv()` never read the working directory.** It walks up from `cli.py` — in a
  checkout that reaches the repo root **by accident**, in an installed tool it reaches `$HOME`.
  Fixed, and `evidence/env-discovery-probe.md` holds the driven proof with its control.
- **`uvx --from <path>` serves a stale build and `--refresh` does not fix it.** It produced a run
  that **exited 0 for a feature that had not shipped**. Build a wheel and install it into a
  throwaway venv instead: `uv build --wheel -o /tmp/w && uv venv v && uv pip install --python
  v/bin/python /tmp/w/*.whl`.
- **`$?` after a pipe is the last command's status.** It reported 0 for a run that exited 1 — again,
  in this session, having been warned in the previous handoff. Redirect when the code matters.
- **A paragraph rewrapper will silently join numbered list items into prose.** It ate seven blocks
  across three files here. Fix width by explicit replacement, and **re-measure after every fix** —
  fixing over-width lines created new ones **five times** this session.
- **`make lint` cannot see column width.** `E501` is not in ruff's default set. Count characters by
  hand, and exclude table rows: they legitimately run past 100.

## Instruments

- `make test` **448**, `make lint` clean at the pinned `0.16.1`, `make check` valid.
- **`link-check.py`'s count is worthless without naming the worktree** — 83 in `main`, 102 in a
  clean checkout, because `.claude/settings.local.json` is untracked by policy. Recorded in
  `backlog.md`. Compare against a run in the *same* tree or not at all.
- **A phase plan legitimately cites files it will create**, so `link-check` reports them broken.
  Read the hits; do not chase the number.
- **Stage with explicit paths, never `git add -A`** — there is a deny rule and it fires.
- **`git checkout` prompts; use `git switch`.** `git merge` cannot read its message from stdin.

## Open, and none of it blocks

- **`IDM-003` has no rule for the build backend**, only the formatter pin. The `uv_build` bump to
  `<0.13` followed it by analogy and checked 22 wheel entries byte for byte. **In `backlog.md`, and
  it is the one open decision this session left.**
- **`BUG-001` is still unreported** to either upstream issue.
- **Failure mode 3 is undischarged** — whether archiving *slows* a call.
- **A call can still vanish**, and closing it needs a guarantee a row is never written twice.
- **The group-notes rule is invisible when it applies** — in `backlog.md`, four candidate homes,
  none chosen.
- **`status.md`'s "Where we stopped" is well past its own ~30-line limit**, at which point its own
  preamble says it has become a document and should get its own file. Not acted on.

## The working agreement still applies

`CLAUDE.md`, in full. Three earned their place this session: **propose before implementing**;
**ask before touching the machine** — the owner's go-ahead was taken separately for the install and
again for `serve`; and **exercise the real thing before committing**, which is what caught the
stale `uvx` build.

To which this phase adds one: **a green test proves the code you ran, not the code you shipped.**
Two instruments returned success for something untrue here, and neither reported an error.
