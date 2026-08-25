# The next session's prompt

*The one file in `docs/` allowed to go stale, per `README.md` — which is why it is rewritten at each
handoff rather than left. **Phase 11 replaced it on 2026-08-24, revised it on 2026-08-25, and replaced
it again at the end of that day**; whatever comes next replaces it again.*

---

**Phase 11 is open, its plan is written, and the plan is not approved.** Branch
`feat/phase-11-corpus-tools`, forked from `main` at `f445d6f`, **twelve commits plus a merge bringing
`main` in, clean tree**. Subject:
the offline tools over Phase 10's store — **extract** with selection, **dictionaries** as a
first-class command, and a **converter** to Claude Code session `JSONL` for
[`claude-code-history-viewer`](https://github.com/jhlee0409/claude-code-history-viewer). The CLI
becomes subcommands to hold them.

**Work in the worktree.** `/Users/ilirium/Projects/local/ilirium_llm_router/phase-11-corpus-tools`.
The project is a bare clone with `main`, `to-run-server` and this phase as sibling worktrees.
**A session started in `main` sees none of Phase 11.**

## Nothing is queued before the first task. Two things are queued before the owner.

**The previous handoff opened with three permission probes. They ran, all three matched, and
`.claude/settings.json` is committed** — `b70769a`. **Do not re-run them and do not re-open the
question.** What was learned from running them is in
`docs/milestone-2-corpus/phase-11-corpus-tools/notes.md`, under "What `.claude/settings.json` now
says".

**The two things waiting on the owner are unchanged and still block the plan:**

1. **Position 3 in `plan.md`'s settled table.** Documentation only, or dictionary work too — it
   decides Group D's shape. The plan states both readings and what each costs; **the response
   dictionary option means an index schema bump**, which is the part that makes it more than an
   addition.
2. **Every `❓` in the plan's register**, listed in its "Placeholders in this file".

**After those, the plan is reviewed under `docs/method/IDM-004-reviewing-unexecuted-work.md` before
Task 2** — read `IDM-004` before reviewing, because its first rule is that the charter decides what
the review finds.

## What to read, and in what order

**Read `docs/status.md` first**, then the phase's `plan.md` — its "What is settled, and by whom" and
"The re-derivation before Task 1" carry the design findings. Then whichever `docs/reference/` file the
work touches.

**Read by section.** `grep -n '^## ' <file>` first. `docs/wiki/claude-code-context-budget.md` says
why, and says the fix is reading by section rather than reading less.

## There is a new documentation tier — `docs/bugs/`

**Created 2026-08-25 on its own branch, merged to `main`, and `main` then merged into this one** —
defects in software this project does not own, where no commit of ours is the ending.

`docs/bugs/BUG-000-about-these-documents.md` holds the conventions. **Read it before filing one.** Two
things it decides that a session would otherwise re-litigate: the boundary against `wiki/` is
**lifetime** — a wiki page is written to stay true, a bug document hoping to stop being true — and
**our own defects do not go there**, because a `fix/` branch is already their ending.

*Why the trunk was merged into a phase branch: the handoff documents cite `BUG-001`, and a path in
backticks is a link here, so the branch could not resolve them — seven broken links that were not
repairable from this side. Un-backticking them would have silenced the checker without fixing
anything.*

## Auto mode is broken upstream, it is measured, and one action is open

`docs/bugs/BUG-001-non-streaming-messages-rejected-as-rate-limited.md`, on `main`, status **open**,
last confirmed 2026-08-25. **Do not re-derive this.** The short form is that non-streamed
`POST /v1/messages` fails categorically while streaming does not, and the control that proves it is
not a rate limit is a streamed request **2.8× larger** to the same model succeeding **0.6 s** after a
non-streamed one was rejected.

**The open action: neither upstream issue has been told.** They are named in the document, and both
stall on exactly the paired control it contains. **This is an action, not a finished thing.**

**The practical consequence while it is open:** auto mode makes every `Bash` call depend on a
classifier that is failing, while `Read`/`Grep`/`Glob` do not use it at all. **Prefer the dedicated
tools** — which `CLAUDE.md` says anyway, for unrelated reasons.

## What changed on this branch that later work depends on

- **Phase 13 is allocated** in `docs/milestone-2-corpus/implementation-plan.md`, for the rate-limit
  response headers. **Read its entry before planning it** — it carries two gates, and neither is
  discharged by having a number.
- **Phases 11 and 12 were added to that file at the same time.** The list ran 8, 9, 10, "closing
  review". **Phase 12 inherits a commitment from Phase 11** — the temporary `README.md` dictionary
  note — and that is recorded in only one other place.
- **The capture step is marked discharged in fact, evidence pending Task 7.** Task 7 freezes a slice;
  until it runs, the material exists only in a gitignored folder on one machine.
- **Task 5 still needs widening before it runs.** `IDM-002` describes the local settings half as
  *"machine accretion"*; the owner stopped following that on 2026-08-25 and the half is deliberately
  empty. The structure is intact, the practice changed, and `IDM-002` does not say so.

## Things a session gets wrong about this code

- **There is deliberately no headline compression ratio.** Every figure is a small-sample
  confirmation that the mechanism works.
- **Three compression levels, not one.** Storing and scoring use `corpus.compress_level_zstd`;
  training uses its own, lower level.
- **`python3` here is 3.14; the venv is 3.13.** Anything importing `zstandard` must run under
  `uv run python`.
- **A dictID is not a unique key.** `zstd --train` stamps **1** on everything.
- **The dictionary pickup is every 500 bodies or a day rollover**, not the next body.
- **Stage with explicit paths, never `git add -A`** — there is a deny rule and it fires. **Not**
  because `logs/` holds uncommittable things: `logs/` is gitignored at `.gitignore:228`, so
  `git add -A` cannot stage any of it. *That justification was examined and dropped on 2026-08-21;
  this file re-asserted it on 2026-08-25 by being written from a stale base, and it is removed
  again. The advice is right and the old reason for it is not.*
- **Claude Code's built-in no-prompt set does not include git.** `ls`, `cat`, `grep`, `find`, `wc`,
  `du`, `cd` run free; every git command prompts unless an allow rule matches it. **`git checkout`
  prompts every time, deliberately — use `git switch`.**
- **A fresh worktree reports 13 more broken links than this one.** `.claude/settings.local.json` is
  gitignored, so `git worktree add` does not create it, and a path in backticks is a link here.
  **That is an artefact, not a regression.**
- **`CLAUDE.md` is wrong about this machine and fixing it is Task 2.** It says the `code-2026` and
  OneDrive paths are *"the same directory"*. True of those two; there are now **genuinely two
  checkouts** because of the local clone.

## What this phase left standing, unchanged

- **Failure mode 3 is not discharged.** Whether archiving *slows* a call is unmeasured.
- **A call can still vanish**, and closing it needs a guarantee a row can never be written twice.
- **Retention is out of scope for Milestone 2** — a scope boundary, not a backlog item.
- **One conflict left standing by the owner:** `Bash(uvx ruff *)` permits an **unpinned** ruff, which
  `CLAUDE.md` says never to invoke as a side effect.

## How the sessions found what they found

**Five times in three days a plausible reading and the true one differed by one check.** The empty
`dicts/` looked exactly like corpus corruption; `--extract` settled it in seconds. A blob count and an
index row count disagreed by four, and the sophisticated explanation was true, available, and not the
answer. A prompting `git status` was explained twice, persuasively, before `git --version` showed git
is simply not in the built-in set. And a 429 that looked like a rate limit was one query away from a
2.8×-larger request succeeding in the same second.

**The instrument lesson underneath all of them.** A probe whose outcomes are indistinguishable to its
reader is not a probe. A model cannot see an approval; an absence of errors is not a pass; a quiet
session and a fixed bug look identical. **Name what a positive result would look like before running
anything.**

**`git merge` cannot read its message from stdin.** `-F -` works for `git commit` and fails here.

Follow the working agreement in `CLAUDE.md`. **Propose before implementing, ask before touching the
machine and say what it is for, and exercise the real thing before committing.**
