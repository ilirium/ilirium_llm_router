# The next session's prompt

*The one file in `docs/` allowed to go stale, per `README.md` — which is why it is rewritten at each
handoff rather than left. **Replaced 2026-08-26, at the close of the session that ran Groups A and B
and Task 11.** Whatever comes next replaces it again.*

---

**Phase 11 is open. Tasks 1–11 are done and work resumes at Task 12.** Branch
`feat/phase-11-corpus-tools`, **clean tree, 355 tests green.** Twelve commits landed on
2026-08-26, the last of them this handoff.

**Nothing is queued before the owner and nothing is blocked.** One question is waiting for them and it
blocks nothing — it is in `for-the-owner.md`, described below.

**Work in the worktree.** `/Users/ilirium/Projects/local/ilirium_llm_router/phase-11-corpus-tools`.
The project is a **bare clone** with `main`, `to-run-server` and this phase as sibling worktrees.
**A session started in `main` sees none of Phase 11**, and editing one worktree does not edit another.

## What to read, and in what order

1. **`docs/status.md`** — first, every session.
2. **`docs/milestone-2-corpus/phase-11-corpus-tools/plan.md`** — the settled table (twenty positions),
   then the task group you are about to run, then the register section covering it.
3. **That phase's `notes.md`, section "The forward review"** — **before writing any converter code.**
   Seventeen findings with their evidence. **Do not re-derive them.**
4. **`for-the-owner.md`, in the same folder — this is new.** Everything addressed to a person rather
   than to a session: **three `ASK`, four `IDEA`, two `REGRET`**, each marked so they skim. **Add to
   it rather than burying an owner-facing point in `notes.md`**, and do not invent a rule or a tier
   for it — the owner asked for the file and explicitly not for a convention.

**Read by section.** `grep -n '^## ' <file>` first. `plan.md` and `notes.md` are the two largest
documents here and both grew again; neither should be read whole.

## Task 12 is next, and it is the hard core of the phase

**Delta reconstruction.** Requests are cumulative — request *N* carries turns 1..*N* — so walk a
session's calls in **timestamp** order and emit only the new user-side entries, then the assistant
turn from that call's response.

Three things it must do, all settled and none optional:

1. **The two normalisations, without which "requests are cumulative" is false on raw bytes.**
   `cache_control` markers migrate between calls, and the same message is serialised as a bare string
   in one call and as content blocks in the next. **Raw: 9 prefix / 84 not. Normalised: 85 / 8.**
   → review finding 2.
2. **Order across day folders**, so the diff for the first call after midnight is taken against the
   last call of the previous day rather than against nothing.
3. **Error when a selected session has calls in a folder that was not passed.** *That error is the
   whole defence.* Without it a cross-day session reconstructs into a plausible transcript whose
   opening turn silently contains a day of prior conversation — which reads as real.

**Also known and not yet handled:** retries produce **byte-identical consecutive requests**, and delta
reconstruction has no defined behaviour for a zero delta (finding 17). And `messages` carries a
**third role, `system`** — on 14 calls the *last* message is one (finding 5).

## What exists now that did not this morning

| | |
|---|---|
| `cli.py` | **subcommands**: `serve`, `check`, `train-dict`, `tune-dict`, `extract`, `verify-archive`. Bare still serves. **Old flags deleted, not aliased** |
| `transcript.py` | **reassembly only.** `reassemble(body) -> Reply \| NotAMessage`, both encodings, six skip reasons. **Delta reconstruction is task 12 and goes in this file** |
| `tests/test_cli.py` | new — the CLI had **no test file at all** before |
| `tests/test_transcript.py` | new |
| `evidence/` | **the frozen slice — 979 rows, four days, redacted**, with `freeze.py` beside it |
| `for-the-owner.md` | new |
| `extract.py`, `jsonl.py` | **do not exist yet.** Groups C and D |

**`extract` parses its full flag surface and returns 2**, naming the tasks that will build it. That is
deliberate, not an oversight.

## Two things that are evidence, and neither is a test

- **`verify-archive` over the whole live corpus: 1793 blobs, 0 failed.** Phase 10's round-trip promise
  driven at scale for the first time. **This discharged task 19 ahead of its group.**
- **`reassemble` over every response blob, joined back to the index: 979 rows, 0 unresolved, 0
  contradictions** against an `error_status` column written at capture time months earlier.

**`CLAUDE.md` says green tests are not evidence, and this phase has to keep producing the other kind**
— task 14 is struck, so the owner exercises the tools **by hand after the phase**. **Task 23's mutation
testing is the strongest evidence the phase produces**, not optional polish.

## Numbers this session established — use these, not the older ones

- **979 index rows**, four day folders, frozen at **2026-08-26T15:16:22Z**. The corpus was at 770 four
  hours earlier. **It is live and it moves.**
- **One buffered assistant reply in the whole corpus.** Not 66 — that is the `count_tokens` count, and
  `plan.md` carried it as the buffered count until this session.
- **808 SSE, 93 error JSON, 47 `count_tokens`, 4 zero-length, 1 buffered.**
- **Five `content_block` types**: `text`, `tool_use`, `thinking`, `server_tool_use`,
  `web_search_tool_result`. *The last two are invisible in a two-day sample.*
- **64,260 `input_json_delta` against 2,071 `text_delta`** — the deltas are overwhelmingly tool
  arguments, not prose.
- **`verify-archive` ratios**: `2026-08-21` 3.140×, `2026-08-24` **2.553×**, `2026-08-25` 3.120×,
  `2026-08-26` 3.056×, all four **2.927×**.
- **45 `too_large` rows**, all in one 292-call session. **Four of the five sentinels have never been
  observed** — `dropped`, `absent`, `error`, and `none` as a response ref.
- **67 `agent_id` rows, one agent, all inside one parent session.** A **partition key**, not a filter.
- **A session spanning two day folders is now 276 calls**, up from 39 + 19 when finding 5 was written.

**`2026-08-24` read 2.815× at 280 blobs mid-day and 2.553× complete.** Same folder, same command, no
dictionary either time. **A ratio goes stale exactly like a count and never looks it.**

## Things a session gets wrong about this code

- **`python3` here is 3.14; the venv is 3.13.** Anything importing `zstandard` must run under
  `uv run python`.
- **`make lint` cannot see column width.** `E501` is not in ruff's default set while `pyproject.toml`
  sets `line-length = 100`. **A 101-character line was committed this session and lint passed it.**
  **Check added lines by hand.** The fix is measured and parked in `for-the-owner.md`.
- **Rewrapping an over-width line pushes words onto the next line and creates a new one.** It happened
  twice. **Re-measure after the fix; a fix that is not re-measured is a hypothesis.**
- **The corpus is live and grows while you read it**, and this session's own traffic is *not* in it —
  the owner ran it **bypassing the router**.
- **Stage with explicit paths, never `git add -A`** — there is a deny rule and it fires.
- **`git checkout` prompts every time — use `git switch`.** And `git merge` cannot read its message
  from stdin; write it to a temp file.
- **A sentinel is not a digest.** All five must read as "no blob here"; used as a filename they fail at
  the filesystem, which is a worse error than the honest one.
- **The index is in completion order.** Sort before analysing.

## Three instrument errors this session, and none was caught by anything failing

**All three were caught because a number looked wrong.** `awk` counting **bytes** not characters and
reporting eleven over-width lines that were em-dashes; a secrets scan reporting **1913** suspect cells
that were every one a **sha256 digest**; and `$?` after a pipe into `tail` reporting **0** for a run
that had failed.

**`CLAUDE.md`: when a check comes back negative, fix the instrument before believing the result.** The
corollary this session adds: **a rule that fires on everything is indistinguishable from one that fires
on nothing**, so a clean result is only worth having once the check has been made capable of returning
a dirty one.

## The one question waiting on the owner

**Does `git --version` prompt?** Anthropic's documented built-in read-only set ends *"and read-only
forms of `git`"*; seven measurements on this branch on 2026-08-25 concluded the opposite. There is no
blanket `ask`/`deny` on git in the tracked settings, so that is not the explanation. **Recorded
unresolved in `IDM-002` with the check named, and no allow rule removed.**

**A model cannot run this check.** A denial arrives as a tool error and **an approval is invisible**,
so silence and approved-after-prompt are the same observation from the inside. **Auto mode removes the
prompt entirely.** It needs the owner, with auto mode off.

## Still open, and not attached to Phase 11

- **`BUG-001` has not been reported to either upstream issue** — and this session found it can go from
  one paired control to **93 of 94**: every 429 in the corpus is a **non-streamed `POST /v1/messages`**,
  zero streamed requests were ever rate-limited, and all 66 non-streamed `count_tokens` succeeded.
  **The corpus cannot show the router's part** — every row went through it, so there is no control, and
  a session run direct produces no rows at all. **Not done here: it belongs on its own branch.**
  → `for-the-owner.md`.
- **`Bash(uvx ruff *)`** permits an unpinned ruff. Raised in every recent phase, owned by nobody, and
  now in two files.
- **Failure mode 3 is still not discharged** — whether archiving *slows* a call is unmeasured.
- **A call can still vanish**, and closing it needs a guarantee a row can never be written twice.

## Three `❓` are live and deliberate, all resolved at Task 13

`JSONL_SCHEMA_NOTE`'s wording, `SYNTHETIC_UUID_NAMESPACE`'s literal, and **the fidelity record's
`type` — which must not be a plain `system` record**, because a real `system` role occurs inside
`messages` and would be indistinguishable from the marker announcing *"this is not a real record."*

**Task 13 settles the viewer's schema from two sources — position 17, the owner's:** the viewer's own
source, and **one** real session file read only far enough to learn field names. **Schema knowledge at
design time is not the same act as the converter reading `~/.claude/` at runtime**, which is what
*"oracle, never input"* forbids.

## Do not widen the phase

**Position 20, the owner's words: *"step by step, not leaps by leaps."*** Deferred and **not to be
built**: error responses, `count_tokens` calls, subagent partitioning, the `corpus-gate` second-source
check, and all dictionary work. **Tasks 14 and 15 are struck in place, not renumbered** — do not
resurrect them and do not renumber the rest.

**When a task turns out to be larger than it was written, ask rather than widening it.** Task 2 named
two files; the dead justification in one of them had **eight homes across seven files**, seven of them
outside the task and two of those in `src/`. **The owner was asked and said fix all seven**, and the
extra work went in **its own commit** so the task's boundary stayed visible in the history.

Follow the working agreement in `CLAUDE.md`. **Propose before implementing, ask before touching the
machine and say what it is for, and exercise the real thing before committing** — noting that for this
phase the owner has taken the final exercising step for themselves, afterwards.
