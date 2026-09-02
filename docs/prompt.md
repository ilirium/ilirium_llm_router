# The next session's prompt

*The one file in `docs/` allowed to go stale, per `README.md` — which is why it is rewritten at each
handoff rather than left. **Replaced 2026-09-02**, at the close of the session that finished Phase
12's Groups D and E. Whatever comes next replaces it again.*

---

**Phase 12 is executed, all seventeen tasks, and waits only on the merge — which the owner asked to
be consulted about before it runs.** Branch `feat/phase-12-installer-and-readme`, worktree
`…/phase-12-installer-and-readme`, **448 tests**, `register-check.py` 28 of 28, tree clean. `main`
is at `5cdc1c9` and has none of this.

**If the merge is the first thing you do, the order is fixed and it is not the obvious one:** merge
`--no-ff` from `main` (write the message to a temp file — `git merge` cannot read stdin), then fill
`plan.md`'s `Merge commit:` line, then `python3 docs/procedures/branch-index.py --write` on the
trunk and commit the regenerated table. **The index row names the merge hash, so it cannot go inside
the merge commit.** Do not delete the branch afterwards: `branch-index.py` refuses to render when a
description names a branch that is gone.

## Read these, in this order

1. **`docs/status.md`** — first, every session. The only file that holds state.
2. **`docs/milestone-2-corpus/phase-12-installer-and-readme/notes.md`**, then the group notes you
   need. `notes-group-c.md` is the `src/` work; `notes-group-e.md` is the close.
3. `docs/backlog.md` when choosing work, not before.

**Do not read Phase 12's `plan.md` or `review-charter.md` unless you are re-opening the phase.** The
plan is the settled table plus the register; the charter is spent.

## What Phase 12 built

| | |
|---|---|
| `init` | writes `config.yaml` **and** `.env.example` into the working directory; refuses rather than overwriting, and there is no `--force` |
| `--version` | an argparse `action="version"`, so it answers in a directory holding nothing |
| the `.env` fix | `load_dotenv(args.config.parent / ".env")` — the phase's largest finding |
| two templates | `config-template.yaml` and `env-template`, package data, byte-identical to the repo's copies and pinned by tests |
| `README.md` | ten sections, 133 lines to 304, with the `--help` quoted from the shipped binary |
| `evidence/register-check.py` | 28 assertions over the register, re-runnable on the trunk |

## Five things a session will get wrong here

- **An exit code answers a different question from the one being asked.** Three instruments reported
  something untrue *without failing* in this phase: `uvx --from` served a stale build, `$?` after a
  pipe gave the wrong command's status, and **`uv tool upgrade` installs changed code while printing
  "Nothing to upgrade"** — its summary compares version numbers, not builds. All three exited 0.
- **`uv tool install <path>` needs no `--force`.** It rebuilds and replaces even when the version
  has not moved. The README said otherwise until it was driven.
- **`link-check.py`'s runtime exemption keys on a path's first segment**, so `./logs/` is reported
  broken where `logs/` is not. Its count is also a property of the worktree — compare against a run
  in the *same* tree or not at all. **109 broken, 2 roundabout here**; three of those are the
  backlog paragraph that describes the defect.
- **`make lint` cannot see column width.** `E501` is not in ruff's default set. Count characters by
  hand, exclude table rows, and **re-measure after every fix** — fixing over-width lines created new
  ones three times this session.
- **A check for a marker matches the documents that describe the marker.** `register-check.py`'s
  unvalued-rows test failed on its first run against the two sentences stating the rule. It reads
  table rows only. `IDM-001`'s placeholder sweep has the same false positive.

## Open, and none of it blocks

- **The `uv_build` pin bump to `<0.13` has no rule behind it.** `IDM-003` covers the formatter pin
  only. In `backlog.md`, and it is an owner decision.
- **`status.md`'s Milestone 2 phase count has gone stale three times.** Fixed again here; the
  mechanism is filed in `backlog.md` with three candidate fixes and **none chosen**, because
  choosing one changes what `status.md` is.
- **Nobody has driven the corpus tools by hand.** Phase 11's handoff named this as the owner's first
  job and it has not happened. Group B drove `extract` for a different question — whether it runs
  with no config — not whether its output reads correctly.
- **`BUG-001` is still unreported** to either upstream issue.
- **Failure mode 3 is undischarged** — whether archiving *slows* a call.
- **A call can still vanish**, and closing it needs a guarantee a row is never written twice.
- **`status.md`'s "Where we stopped" is well past its own ~30-line limit**, at which point its own
  preamble says it has become a document and should get its own file.

## What the next phase probably is

**Phase 13 — the Anthropic rate-limit response headers**, per
`milestone-2-corpus/implementation-plan.md`. **It arrives carrying a collision that allocating a
number did not clear:** *"changing `calls.csv`, not its rotation, not its columns"* is a standing
Milestone 2 non-goal, and the headers need a home. Either the non-goal is overturned or they go
somewhere that is not a CSV column. **Neither is chosen, and Phase 13's plan cannot skip it.**

## The working agreement still applies

`CLAUDE.md`, in full. Three earned their place this session: **propose before implementing**; **ask
before touching the machine and say what it is for** — the install go-ahead was taken separately and
the machine was left exactly as it was found; and **exercise the real thing before committing**,
which is the only reason two wrong lines did not ship.

To which this phase adds one: **a plan's settled table is not overridden by the plan being
executed.** The register check found five caveats where the owner had settled four. The fifth had a
good argument and it was not the session's to make.
