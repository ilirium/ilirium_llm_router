# The next session's prompt

*The one file in `docs/` allowed to go stale, per `README.md` — which is why it is rewritten at each
handoff rather than left. **Replaced 2026-08-28, at the close of the session that ran Tasks 12–25 and
merged Phase 11.** Whatever comes next replaces it again.*

---

**Phase 11 is complete and merged. Nothing is in flight.** Merge `7e53f74`, branch index `f97c4b6`,
**438 tests**, `main` clean. **Milestone 2 is four phases in.**

**Start in `main`**, at `/Users/ilirium/Projects/local/ilirium_llm_router/main`. There is **no open
phase branch**; whatever you do next opens its own. *The `phase-11-corpus-tools` worktree still
exists and is spent — do not work in it, and **do not delete the branch**: `branch-index.py` refuses
to render when a description names a branch that no longer exists, so deleting a merged one breaks
the next merge.*

**Nothing is queued and nothing is blocked.** Three things wait on the owner and none of them blocks
work — they are in `milestone-2-corpus/phase-11-corpus-tools/for-the-owner.md`.

## Read these, in this order

1. **`docs/status.md`** — first, every session. It is the only file that holds state.
2. **`docs/backlog.md`** — the inventory. `status.md` lifts two or three items from it and is not a
   substitute for it.
3. Only then, whatever the chosen work needs. **Grep headings first** — `grep -n '^## ' <file>`.

**Do not read Phase 11's `plan.md` or group notes unless you are working on the corpus tools.** They
are large and the phase is closed. If you do need them: `plan.md` is the settled table plus the
register; `notes.md` is the entry point and the five `notes-group-*.md` hold the task work.

## The first thing to do, and it is the owner's

**Nobody has driven the corpus tools by hand.** Task 14 was struck on the owner's decision precisely
so this would happen after the merge, which means **Phase 11's evidence is mechanical throughout** —
code, tests, corpus drives and a mutation sweep. **Do not read "Phase 11 is merged" as "the tools
were tried."**

```sh
ilirium-llm-router extract logs/corpus/2026-*/ --out ./dump --format jsonl --format bodies
```

Then point a history viewer's Custom Claude Directory at `./dump` — **never at
`~/.claude/projects/`**, which is position 12 and is not a reversible mistake.

## What Phase 11 built

| | |
|---|---|
| `transcript.py` | reassembly (SSE + buffered), **delta reconstruction**, cross-day ordering |
| `jsonl.py` | the viewer's record shapes, `uuid5` chaining, the in-band fidelity note |
| `extract.py` | selection over an index, output layout, the sibling-day scan |
| `cli.py` | subcommands: `serve`, `check`, `train-dict`, `tune-dict`, `extract`, `verify-archive` |
| `evidence/` | the frozen slice, plus **`register-check.py`** and **`mutate.py`**, both re-runnable |

## Five things a session will get wrong about this code

- **A `session_id` is not one conversation.** 36 across 9 sessions, including a **66-call subagent
  carrying its parent's id**. They are separated by **root message**, which never asks "is this a
  probe?" — one file per conversation, the deepest taking the plain `<session>.jsonl`.
- **"Requests are cumulative" is false on raw bytes.** Two normalisations fix it and **one scores
  0/76 alone**, because the other's breakage masks it. And a **third mechanism is not a
  normalisation**: a request's tail is provisional — 100 messages were revised by a later call, 9
  changing role — so turns come from a conversation's *latest* state.
- **Every long session loses its ending, permanently, at capture time.** Request bodies grow
  monotonically and cross `body_max_bytes` once; 45 contiguous calls at the end of the largest
  session have no stored request. **Raising the cap is unactioned and is in `for-the-owner.md`.**
- **`SSE_EVENTS` is a record, not a guard.** Nothing in `src/` reads it. An unlisted event is passed
  over, not rejected.
- **`python3` here is 3.14; the venv is 3.13.** Anything importing `zstandard` needs `uv run python`.

## Instruments, and the two that bite

- **`make lint` cannot see column width.** `E501` is not in ruff's default set while `pyproject.toml`
  sets `line-length = 100`. **Check added lines by hand — in *characters*.** `awk` counts bytes and
  reported 13 over-width lines where there were 4. **And re-measure after fixing**: rewrapping pushes
  words onto the next line and creates new ones. Both happened again this session, both already
  written down.
- **`$?` after a pipe reports the last command's status.** It said `0` for a run that had failed,
  again, while checking an exit code. Redirect instead of piping when the code matters.
- **`evidence/mutate.py` edits `src/` while it runs.** It has three restore paths because
  `try/finally` was not enough: a timeout killed the first run and left `transcript.py` as
  `ast.unparse` output — **every comment stripped, 256 of 670 lines gone, suite passing 427/427**.
  **If a sweep is interrupted, check `git status` before anything else.**
- **Stage with explicit paths, never `git add -A`** — there is a deny rule and it fires.
- **`git checkout` prompts; use `git switch`.** `git merge` cannot read its message from stdin.

## Open, and none of it blocks

- **`BUG-001` has still not been reported** to either upstream issue, and it is now much stronger:
  **93 of 94** — every 429 in the corpus is a non-streamed `POST /v1/messages`, zero streamed
  requests were ever rate-limited, and all 66 non-streamed `count_tokens` succeeded. **The corpus
  cannot show the router's part** — every row went through it, so there is no control. It belongs on
  its own `docs/` or `fix/` branch.
- **Does `git --version` prompt?** With auto mode off. **A model cannot run this check**: a denial is
  a tool error and an approval is invisible. Recorded unresolved in `IDM-002`.
- **`Bash(uvx ruff *)` permits an unpinned ruff.** Raised in every recent phase, owned by nobody.
- **Failure mode 3 is undischarged** — whether archiving *slows* a call is unmeasured.
- **A call can still vanish**, and closing it needs a guarantee a row can never be written twice.
- **~24 mutation survivors are parked** in `backlog.md` as error-message wording, with the reasoning
  and the honest denominator: **"105 survived" overstates the real gap by about a quarter.**
- **A mutation-testing tool** is parked under `IDM-003`, with the test for judging it later.

## What the next phase probably is

**Phase 12 — the installer and the `README.md` rewrite**, per `milestone-2-corpus/implementation-plan.md`.

**It inherits a commitment and the commitment is written in only two places.** Phase 11 added a
**temporary** corpus-tools section to the top-level `README.md`, explicitly superseded by Phase 12.
**A rewrite that drops it drops the only user-facing description the dictionary and corpus commands
have.** The section opens with that warning so a rewrite meets it before deciding what to keep.

## The working agreement still applies

`CLAUDE.md`, in full — but the three that earned their place this phase: **propose before
implementing**; **ask before touching the machine and say what it is for**; and **exercise the real
thing before committing**, because green tests are not evidence. To which this phase adds one:
**a targeted mutation tests the tests you wrote; a systematic sweep tests the ones you did not.**
→ `reference/lessons.md` §8.
