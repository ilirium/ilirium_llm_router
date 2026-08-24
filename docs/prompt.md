# The next session's prompt

*The one file in `docs/` allowed to go stale, per `README.md` — which is why it is rewritten at each
handoff rather than left. **Phase 11 replaced it on 2026-08-24**; whatever comes next replaces it
again.*

---

**Phase 11 is open, its plan is written, and the plan is not approved.** Branch
`feat/phase-11-corpus-tools`, forked from `main` at `f445d6f`, five commits, tree clean. Subject: the
offline tools over Phase 10's store — **extract** with selection, **dictionaries** as a first-class
command, and a **converter** to Claude Code session `JSONL` for
[`claude-code-history-viewer`](https://github.com/jhlee0409/claude-code-history-viewer). The CLI
becomes subcommands to hold them.

**Work in the worktree.** `/Users/ilirium/Projects/local/ilirium_llm_router/phase-11-corpus-tools`.
The project is now a bare clone with `main`, `to-run-server` and this phase as sibling worktrees.
**A session started in `main` sees none of Phase 11** — not the plan, not the notes, not the settings
change.

**`CLAUDE.md` is wrong about this machine and fixing it is Task 2.** It says the `code-2026` and
OneDrive paths are *"the same directory (identical inode)… editing either edits both."* That is still
true of those two, and there are now **genuinely two checkouts** because of the new local clone. A
session that believes the old note can lose work.

## What a session should do first

**Read `docs/status.md`**, then the phase's `plan.md` — its "What is settled, and by whom" and
"The re-derivation before Task 1" are the two sections that carry the day's findings. Then whichever
`docs/reference/` file the work touches.

**Read by section.** `grep -n '^## ' <file>` first. `docs/wiki/claude-code-context-budget.md` says
why.

## The two things waiting on the owner

1. **Position 3 in `plan.md`'s settled table**, and it blocks Group D's shape. The question asked
   what was missing from the dictionary tooling; the answer named a user-facing `README.md` note,
   temporary until Phase 12. Read as **no new dictionary code, document what ships** — *one word
   settles whether that is right.*
2. **Every `❓` in the plan's register**, listed in its "Placeholders in this file".

## The one check to run first, because it costs nothing

**`git add -A` on a clean tree.** A deny rule for it was added to `.claude/settings.json` on
2026-08-24 and **did not fire when driven**. Blocked now → settings are session-cached and the rule
works. Still not blocked → **a tracked permission change on a phase branch has no effect until it
merges**, which constrains the worktree practice Task 3 records.

**Neither deny rule may be described as working until this runs.** The phase's `notes.md` has the
detail, including that the check came *after* the commit, which is the wrong order and is recorded
as such.

## What the corpus actually contains, measured 2026-08-24

**The owner drove real sessions and `logs/corpus/` in `to-run-server` is no longer empty** — two day
folders, 171 index rows, 280-odd blobs. Four things a session would otherwise get wrong:

- **It was live while it was read.** 114 → 123 request blobs between two counts. **Freeze a slice
  before measuring** — that is Task 7, and nothing goes to `reference/measurements.md` until it runs.
- **It is undicted.** `request_dict_id` is `none` on every row, both day folders have an empty
  `dicts/`, and `retrain.log` says why: `too-few-samples`. **This is not the corruption
  `reference/corpus.md` warns about** — the blobs name no dictionary, so none is missing. `--extract`
  returns 280 blobs, **0 failed**, 2.815×. That figure is the number a dictionary must beat, **not a
  ratio to quote.**
- **63 of 168 calls are non-streamed**, so the converter meets **plain JSON as well as SSE**.
- **`agent_id` is empty on all 171 rows**, and **`backend` is `anthropic` on all of them.** No LM
  Studio traffic was captured, so every tool this phase builds is exercised against Anthropic
  material only.

## What this phase left standing from Phase 10, unchanged

- **Failure mode 3 is not discharged.** Whether archiving *slows* a call is unmeasured.
- **A call can still vanish**, and closing it needs a guarantee a row can never be written twice.
- **Retention is out of scope for Milestone 2** — owner's decision, a scope boundary rather than a
  backlog item.

## The classifier diagnosis, which is not this phase's work

**Claude Code's auto-mode classifier gets HTTP 429 from Anthropic, and the router is not at fault.**
66 of 232 calls, **every one non-streaming**, against 138 of 145 streaming calls succeeding — and a
streaming call to the same model succeeded five seconds after five consecutive 429s on it. The
classifier request is ~135 KB, `max_tokens: 1`, **zero `cache_control` breakpoints**. Two open
upstream issues stall on exactly the measurement this router could take:
[`anthropics/claude-code#82653`](https://github.com/anthropics/claude-code/issues/82653) and
[`BerriAI/litellm#30365`](https://github.com/BerriAI/litellm/issues/30365).

**What survives into this project is one `backlog.md` item to overturn:** the *"do not go looking"*
note on `anthropic-ratelimit-*` and `retry-after` rests on the recorder keeping the error body's
symbolic type — and **66 rows of `rate_limit_error: Error` do not say which limit was hit.** That
reasoning failed its first real test.

## Things a session gets wrong about this code

- **There is deliberately no headline compression ratio.** Every figure is a small-sample
  confirmation that the mechanism works.
- **Three compression levels, not one.** Storing and scoring use `corpus.compress_level_zstd`;
  training uses its own, lower level.
- **`python3` here is 3.14; the venv is 3.13.** Anything importing `zstandard` must run under
  `uv run python`.
- **A dictID is not a unique key.** `zstd --train` stamps **1** on everything.
- **The dictionary pickup is every 500 bodies or a day rollover**, not the next body.
- **`logs/` is gitignored and holds uncommittable things.** **Stage with explicit paths, never
  `git add -A`** — which is now also a deny rule, pending the check above.
- **Claude Code has a built-in read-only Bash set** — `ls`, `cat`, `grep`, `find`, `wc`, `du`, `cd`,
  read-only `git` and more — that runs without a prompt in every mode and **is not configurable**.
  Allow rules for those grant nothing. Task 5 records it in `IDM-002`.

## How the opening session found what it found

**Twice in one day a plausible reading and the true one differed by one check, and both times the
reasoning was available and wrong.** The empty `dicts/` looked exactly like the corruption
`corpus.md` warns about; `--extract` settled it in seconds. A blob count and an index row count
disagreed by four, and the sophisticated explanation — a CSV whose free-text column can hold
newlines — was true, available, and not the answer; the corpus was simply still growing.

**`git merge` cannot read its message from stdin.** `-F -` works for `git commit` and fails here.

Follow the working agreement in `CLAUDE.md`. **Propose before implementing, ask before touching the
machine and say what it is for, and exercise the real thing before committing** — the last one was
broken on 2026-08-24 and the phase notes say so.
