# The next session's prompt

*The one file in `docs/` allowed to go stale, per `README.md` — which is why it is rewritten at each
handoff rather than left. **Phase 11 replaced it on 2026-08-24 and revised it on 2026-08-25**;
whatever comes next replaces it again.*

---

**Phase 11 is open, its plan is written, and the plan is not approved.** Branch
`feat/phase-11-corpus-tools`, forked from `main` at `f445d6f`, **five commits, one uncommitted file on
purpose.** Subject: the offline tools over Phase 10's store — **extract** with selection,
**dictionaries** as a first-class command, and a **converter** to Claude Code session `JSONL` for
[`claude-code-history-viewer`](https://github.com/jhlee0409/claude-code-history-viewer). The CLI
becomes subcommands to hold them.

**Work in the worktree.** `/Users/ilirium/Projects/local/ilirium_llm_router/phase-11-corpus-tools`.
The project is a bare clone with `main`, `to-run-server` and this phase as sibling worktrees.
**A session started in `main` sees none of Phase 11** — not the plan, not the notes, not the settings.

**`CLAUDE.md` is wrong about this machine and fixing it is Task 2.** It says the `code-2026` and
OneDrive paths are *"the same directory (identical inode)… editing either edits both."* That is still
true of those two, and there are now **genuinely two checkouts** because of the new local clone. A
session that believes the old note can lose work.

## The first thing to do, and it must come before the commit

**`.claude/settings.json` was rewritten on 2026-08-25 and is deliberately uncommitted.** It cannot be
exercised by the session that writes it — settings are read once at session start — so it was left in
the working tree for *this* session to check. `3d8ae54` committed a permission change and checked it
afterwards; `notes.md` records that as the wrong order and the point.

**Run three probes on a clean tree, then commit.** Each costs nothing and stages nothing:

| probe | expected now | what a surprise would mean |
|---|---|---|
| `git status` | **silent** — an allow rule now covers it | the read-only git allows do not match as written |
| `git add -A .` | **prompts** — no allow covers it any more | `Bash(git add *)` survived somewhere |
| `git stash clear` | **blocked** | the new denies did not land |

**Only after all three: `git add .claude/settings.json` and commit.** If any of them surprises you,
fix the file first and say so in `notes.md` — that is the whole reason it was left uncommitted.

*Note the practice change while probing: **`git checkout` now prompts every time, deliberately.** Use
`git switch` for branches. `checkout` was removed from the allow list because it carries
`git checkout -- .`, and a deny entry cannot be relied on to catch a spelling.*

## What a session should do first, after that

**Read `docs/status.md`**, then the phase's `plan.md` — its "What is settled, and by whom" and
"The re-derivation before Task 1" are the two sections that carry the design findings. Then whichever
`docs/reference/` file the work touches.

**Read by section.** `grep -n '^## ' <file>` first. `docs/wiki/claude-code-context-budget.md` says
why.

## The two things waiting on the owner — unchanged, still waiting

1. **Position 3 in `plan.md`'s settled table**, and it blocks Group D's shape. The question asked
   what was missing from the dictionary tooling; the answer named a user-facing `README.md` note,
   temporary until Phase 12. Read as **no new dictionary code, document what ships** — *one word
   settles whether that is right.*
2. **Every `❓` in the plan's register**, listed in its "Placeholders in this file".

## What 2026-08-25 settled about permissions, because Task 5 has to record it

**The `git add -A` deny check ran and it was blocked.** Settings are **session-cached**; a tracked
permission change on a phase branch is inert until **restart**, not until merge. The competing
explanation — that tracked settings resolve through the worktree to the main checkout — is dead, and
**Task 3 does not need to record that constraint.**

**Chasing why `git status` still prompted found the larger thing, and it inverted this branch's
assumptions.** Seven measurements, accept-edits mode, in this worktree: `ls` silent; `git status`,
`git status && echo ok`, `git --version` and `git --no-optional-locks status` **all prompted**;
`git add -A` and `git stash` **denied**; `git add -A .` **ran unprompted**. From those:

- **Git is not in the built-in read-only set.** `git --version` touches no repository and still
  prompted, so it is neither the worktree layout nor the index refresh — both were proposed and both
  were wrong.
- **A deny entry matches exactly; an allow entry with `*` does not.** `git add -A .` fell through the
  deny to `Bash(git add *)`. **A deny list of spellings is not a guard.**
- **The allow list was permissive where git destroys work and absent where it is safe** —
  `git checkout -- .` and `git stash clear` were both allowed silently, while `git status` cost a
  prompt.

**The correction that matters most is about instruments, not git.** The previous handoff asserted that
read-only git *"runs without a prompt in every mode"*. No session could have observed that: **a model
sees a denial as a tool error and cannot see an approval at all**, so a silent run and an
approved-after-prompt run are indistinguishable from the inside. The owner was the only instrument and
was never asked. **`IDM-002` gets the measured version; do not re-assert the old claim.**

**`settings.local.json` was merged into the tracked file and emptied** — it exists, holds an empty
`permissions` block, and grants nothing. Every rule is now tracked and reaches `main` and
`to-run-server` at the merge; until then those two worktrees prompt for git, which is a temporary cost
and not a landmine.

**Task 5 grew, and the reason survives even though the breakage did not.** `IDM-002` describes the
local half as *"machine accretion: whatever this laptop clicked allow on"* — the owner stopped
following that on 2026-08-25 and the half is now deliberately empty. The split's structure is intact;
its practice changed, and `IDM-002` does not say so. It was left alone because the plan is unapproved.
**Widen Task 5 before running it.**

*While the file was briefly absent, `link-check.py` went 86 → 99 → 86: a path in backticks is a link
here, so removing any referenced file breaks documents that had no defect — ten of those thirteen were
frozen historical records that could not have been repaired at all. **Check the link count before
deleting a file the documentation names.***

**One conflict was raised and left standing by the owner:** `Bash(uvx ruff *)` permits an **unpinned**
ruff, which `CLAUDE.md` says never to invoke as a side effect. Recorded in `notes.md` so it is not
rediscovered as a surprise.

## What the corpus actually contains, measured 2026-08-24

**`logs/corpus/` in `to-run-server` is no longer empty** — two day folders, 171 index rows, 280-odd
blobs. Four things a session would otherwise get wrong:

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
  `git add -A`** — which is a deny rule that *does* fire, and staging is now allowed only under
  `docs/`, `src/`, `tests/`, `.claude/` and six tracked root files.
- **Claude Code's built-in no-prompt set does not include git.** `ls`, `cat`, `grep`, `find`, `wc`,
  `du`, `cd` run free; **every git command prompts unless an allow rule matches it.** *(This bullet
  said the opposite until 2026-08-25, on no evidence.)*

## How the sessions found what they found

**Four times in two days a plausible reading and the true one differed by one check, and every time
the reasoning was available and wrong.** The empty `dicts/` looked exactly like the corruption
`corpus.md` warns about; `--extract` settled it in seconds. A blob count and an index row count
disagreed by four, and the sophisticated explanation — a CSV whose free-text column can hold newlines
— was true, available, and not the answer; the corpus was simply still growing. Then on 2026-08-25 the
prompting `git status` was explained twice, first by the worktree layout and then by `git status`
writing the index, both persuasively, before `git --version` showed that git is simply not in the
built-in set at all.

**`git merge` cannot read its message from stdin.** `-F -` works for `git commit` and fails here.

Follow the working agreement in `CLAUDE.md`. **Propose before implementing, ask before touching the
machine and say what it is for, and exercise the real thing before committing** — the last one was
broken on 2026-08-24, and the uncommitted settings file at the top of this page is the repair.
