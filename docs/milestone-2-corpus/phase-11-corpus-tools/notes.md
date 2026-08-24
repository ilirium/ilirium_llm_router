# Phase 11 — corpus tools: notes

**Not yet merged.** *(Closed out at the merge, per `plan.md`'s "Placeholders in this file".)*

**Branch `feat/phase-11-corpus-tools`, forked from `main` at `f445d6f`, opened 2026-08-24.** The
first phase of this project worked in a **git worktree** rather than in the trunk checkout —
`../../../../phase-11-corpus-tools`, beside `main` and `to-run-server` under a bare clone.

## Index of the group files

*In the order they were written, which is the chronology the letter-sorted split otherwise breaks.*

| | |
|---|---|
| *(none yet)* | Group A has not started |

## The re-derivation before Task 1

**Held 2026-08-24, before the plan was written, and it moved three things.** The findings are in
`plan.md`'s section of that name rather than duplicated here; what belongs in the notes is *how* they
were found, because two of them were found by accident and that is worth not repeating by accident.

**The corpus was read twice by chance.** The first read counted 114 request blobs; a later
re-count, run only because a blob total and an index row count disagreed by four, returned **123**.
The router in `to-run-server` was still up. **The disagreement was the signal, and it was nearly
explained away** — the plausible story was that `wc -l` miscounts a CSV whose free-text
`error_message` column can hold newlines, which is *also true* and would have accounted for a small
gap. Two mechanisms, one of them real, and the wrong one was the more sophisticated.

*This is `../phase-10-body-store/`'s "interrogating a passing check" arriving unprompted: **what
would make this discrepancy innocent anyway?** The answer existed, and it was not the explanation.*

**The empty `dicts/` looked like the invariant failing and was not.** `reference/corpus.md` warns
that a day folder holding a blob whose dictID names an absent dictionary is a real corruption that
**nothing reports until somebody reads it back** — so an empty `dicts/` in both day folders read as
exactly that. Reading it back is the check, `--extract` is the instrument, and it returned **280
blobs, 0 failed**. `request_dict_id` is `none`, not a dictID: the blobs name no dictionary, so there
is none to be missing. **The alarming reading and the true one differ by one column of the index.**

## A tracked deny rule written on a phase branch did not take effect

**Found 2026-08-24 by driving it, immediately after committing it — which is the wrong order and is
the point.** `../../../CLAUDE.md` says *exercise it before committing*; this was committed first and
the check came second. It would have been a defect in the phase record if the next session had
inherited *"two deny rules added"* with nothing saying they were never seen to work.

**What happened.** `Bash(git add -A)` was added to `.claude/settings.json`'s `deny` list and
committed as `3d8ae54`. Running `git add -A` immediately afterwards **was not blocked**. The tree was
clean, so nothing was staged and no harm followed — but the rule plainly did not fire.

**What is established:** the rule is on disk and correct in *this* worktree, and **absent from
`main`'s copy** — `main` is on the `main` branch, which does not carry the commit. Measured with
`grep -c`, one file against the other.

**Two explanations remain open, and they have very different consequences:**

| | If it is this | Consequence |
|---|---|---|
| **a** | Claude Code resolves `.claude/settings.json` **through the worktree to the main checkout**, the way the permissions doc says saved rules resolve | **A tracked permission change on a phase branch does nothing until it merges.** Every phase that edits the tracked settings file is writing a rule that cannot take effect during the phase that writes it |
| **b** | Settings are read once at session start and not reloaded | A restart fixes it, and the finding is ordinary |

**A fresh session distinguishes them**, and costs nothing: if the deny fires after a restart it is
**b**; if it still does not, it is **a**. Until then neither deny rule may be described as working.

*Why this belongs in the notes rather than only in the plan: it is the second time today that a
plausible reading and the true one differed by one check — the empty `dicts/` was the first. Both
were resolved by running the thing rather than reasoning about it, and in both cases the reasoning
was available and wrong.*

## Where the opening session stopped — 2026-08-24

**The project-level handoff is `../../prompt.md`, rewritten for this phase on 2026-08-24, and
`../../status.md` carries the in-flight row.** This section is the *phase's* record of its opening
session and does not repeat them.

*It briefly claimed both files were stale "until Task 6 fixes them", which was wrong twice over:
Task 6 is about `../implementation-plan.md`, and `status.md`'s in-flight table is **live state** that
`../../method/IDM-001-git-branching.md` requires a branch to appear in the moment it opens — not
phase work to be scheduled. Both were updated the same day.*

**Start in the `phase-11-corpus-tools` worktree.** The plan, these notes and the settings change are
on the branch; a session started in `main` sees none of them.

**Three commits, tree clean:** `052ea3e` opened the phase, `12ada32` fixed a dead WebFetch domain,
`3d8ae54` added the deny rules and folded the git allows, `9e0b59d` recorded that the denies did not
fire.

### The first thing to do, and it costs nothing

**Run `git add -A` on a clean tree.** Blocked → settings are session-cached and the rules work.
Not blocked → a tracked permission change on a phase branch has no effect until it merges, which is
a constraint Task 3 must record. **Do not describe either deny rule as working until this runs.**

### Two things waiting on the owner

1. **Position 3** in `plan.md`'s settled table — whether *"document the dictionary tooling"* also
   means build something. One word, and it changes whether Group D has another section.
2. **Every `❓` in the register**, listed in "Placeholders in this file".

### What is deliberately not in the plan

**The auto-mode classifier diagnosis.** A day of telemetry was spent establishing that Claude Code's
auto-mode classifier gets HTTP 429 from Anthropic — 66 of 232 calls, **every one of them
non-streaming**, against 138 of 145 streaming calls succeeding. It is **not a router defect**: the
router relays the upstream status with its headers, `retry-after` and `anthropic-ratelimit-*` are not
in `DROPPED_FROM_RESPONSE`, and a streaming call to the same model succeeded five seconds after five
consecutive 429s on it.

**It is not Phase 11's subject and no task covers it.** What it left behind that *is* the project's:
a `backlog.md` item to overturn, since `backlog.md`'s *"do not go looking"* note on the rate-limit
headers rests on the recorder keeping the error body's symbolic type — and 66 rows of
`rate_limit_error: Error` do not say **which** limit. That reasoning failed its first real test.
**Two open upstream issues stall on exactly the measurement this router could take:**
[`anthropics/claude-code#82653`](https://github.com/anthropics/claude-code/issues/82653) and
[`BerriAI/litellm#30365`](https://github.com/BerriAI/litellm/issues/30365).

## The git allows are, for now, only on this branch — and that is a self-inflicted gap

**`main` and `to-run-server` currently have no `git add`, `git commit`, `git checkout` or `git stash`
approval at all.** Measured 2026-08-24: `grep -c git` returns **0** against both of `main`'s settings
files.

**How it happened, plainly:** the four mutating git rules were removed from the local half and added
to the tracked half in the same pass. The tracked half is a **branch commit**, so the removal took
effect everywhere and the replacement took effect nowhere except here.

**Left as it is, deliberately.** Restoring them to the local files of the other two worktrees would
put the same permission in both halves, which `../../method/IDM-002-harness-configuration.md` refuses
in as many words — *"narrowing the tracked file later appears to do nothing, because the local copy
still grants it."* Trading a permanent landmine for a temporary prompt is the wrong way round. The
cost is one approval when committing in `main`, and it clears when this branch merges.

**It is also the open question in miniature.** If tracked settings resolve through a worktree to the
main checkout, then *this* worktree has no git allows either and the rules on this branch are inert
everywhere — the same test settles both.

## What is open at the end of Group A

*(Group A has not started. The items above are Task 5's, executed ahead of the plan.)*
