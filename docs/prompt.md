# The next session's prompt

*The one file in `docs/` allowed to go stale, per `README.md` — which is why it is rewritten at each
handoff rather than left. **Replaced 2026-08-26, at the close of the session that ratified, reviewed
and revised Phase 11's plan.** Whatever comes next replaces it again.*

---

**Phase 11 is open, its plan is ratified, reviewed and revised, and work may begin at Task 2.**
Branch `feat/phase-11-corpus-tools`, forked from `main` at `f445d6f`, **30 commits, clean tree**.

**Nothing is queued before the owner.** For the first time in this phase there is no pending decision
— twenty positions are settled, every one owned and dated. **Task 2 is the next action and it needs no
permission.**

**Work in the worktree.** `/Users/ilirium/Projects/local/ilirium_llm_router/phase-11-corpus-tools`.
The project is a bare clone with `main`, `to-run-server` and this phase as sibling worktrees.
**A session started in `main` sees none of Phase 11.**

## What to read, and in what order

1. **`docs/status.md`** — first, every session.
2. **`docs/milestone-2-corpus/phase-11-corpus-tools/plan.md`** — the settled table, then "The
   re-derivation before Task 1" (six findings), then the task group you are about to run, then the
   register section that covers it.
3. **That phase's `notes.md`, section "The forward review"** — **before writing any converter code.**
   It holds seventeen findings with their evidence and what each costs. **Do not re-derive them.**

**Read by section.** `grep -n '^## ' <file>` first. `plan.md` is 846 lines and `notes.md` is 512;
neither should be read whole. `docs/wiki/claude-code-context-budget.md` says why, and says the fix is
reading by section rather than reading less.

## The review is done. Do not run another one.

**`IDM-004` ran on 2026-08-26** — charter written first, author and cold runs in parallel, then
reconciliation. `review-charter.md` is the worked example; `notes.md` holds both runs. **The protocol
says run it once, against a document finished enough to be wrong.** It has been run.

**The single most useful thing it returned, and the thing to carry into every task:**

> The plan's model of a captured session — *cumulative calls, one user turn and one assistant turn
> each* — **is simpler than the traffic on disk.** The real thing is five interleaved request classes,
> three roles, two content serialisations, a migrating `cache_control` annotation, 94 error responses,
> and a 45-call tail with no request body at all. **Every one was an hour's reading away, and the plan
> asserted the opposite of several of them in bold.**

**So: read the corpus before writing code that assumes what is in it.** Reading `index.csv` directly
with `cut`/`awk`/`csv.DictReader` is cheap and settles most questions. Decompressing a blob needs
`uv run python` — see the environment note below.

## Phase 11 is a baseline tool. Do not widen it.

**Position 20, the owner's words:** *"step by step, not leaps by leaps."*

**Deferred to a later phase — do not build these:** error responses, `count_tokens` calls, subagent
partitioning, the `corpus-gate` second-source check, and all dictionary work.

**Tasks 14 and 15 are struck.** They are struck **in place**, not renumbered, so every cross-reference
to Task 13 and Task 22 still resolves. **Do not resurrect them**, and do not renumber the rest.

**The baseline's one mechanical rule:** a call contributes a turn **only if its response is a
message**; the rest are skipped and counted. It is lossless because requests are cumulative, and it
asks *"is this response a message?"*, never *"is this call a probe?"* — **do not turn it back into
classification.**

**Three `❓` are live and deliberate**, all resolved at Task 13: `JSONL_SCHEMA_NOTE`'s wording,
`SYNTHETIC_UUID_NAMESPACE`'s literal, and **the fidelity record's `type` — which must not be a plain
`system` record**, because a real `system` role occurs inside `messages` and would be indistinguishable
from the marker announcing *"this is not a real record"*.

## The gap this phase carries on purpose

**Task 14 was struck, and with it the phase's only *exercise the real thing* step.** The owner tests
the tools **by hand after the phase is finished**, having judged that a ground-truth diff costs too
much and settles too little before anyone has held the tool.

**So the phase's evidence is tests and mutation testing, and nothing else.** `CLAUDE.md` says green
tests are not evidence. **The closing record must say the central question was answered mechanically
and confirmed by hand afterwards** — a phase note reporting green tests as though the question were
closed is the exact failure the plan's first "does not settle" bullet exists to prevent.

**Task 23's mutation testing is therefore not optional polish.** It is the strongest evidence the
phase produces.

## What is open, and what is merely available

- **`BUG-001` has not been reported to either upstream issue.** Named in
  `docs/bugs/BUG-001-non-streaming-messages-rejected-as-rate-limited.md`, status **open**. Both issues
  stall on exactly the paired control it contains. **This is an action, not a finished thing**, and it
  is the only open item not attached to Phase 11.
- ~~**The `make` baseline is stale.**~~ **Closed 2026-08-26** — re-run in this worktree: **310 passed
  in 2.5 s, ruff clean at the pinned `0.16.1`, config valid.** Identical to the 2026-08-21 figure,
  which is the finding: **no test has been added or removed**, consistent with no phase task having
  started. **So the suite you inherit is green and the number to beat is 310.** *One new
  `StarletteDeprecationWarning` (`httpx` → `httpx2`) is recorded in `status.md` and deliberately not
  actioned — `IDM-003` governs dependency bumps, and nothing bumps a pin as a side effect.*
- **Failure mode 3 is still not discharged** — whether archiving *slows* a call is unmeasured.
- **A call can still vanish**, and closing it needs a guarantee a row can never be written twice.
- **`Bash(uvx ruff *)` permits an unpinned ruff**, which `CLAUDE.md` says never to invoke as a side
  effect. Raised, standing, owned by nobody.

## Things a session gets wrong about this code

- **`python3` here is 3.14; the venv is 3.13.** Anything importing `zstandard` must run under
  `uv run python`. **The `.venv` in this worktree exists — the owner created it on 2026-08-26.**
- **The corpus is live and grows while you read it.** It went **770 → 904 rows in one afternoon**, and
  two copies of one index a minute apart differed by 259 bytes. Every figure needs its moment attached.
- **The corpus captures this session's own traffic**, including subagents. That is how
  `observe.py:40` was finally confirmed. It also means a subagent you spawn writes rows.
- **A session spans day folders.** `extract` takes **positional, repeatable** day folders; the shell's
  glob is the "all of it" case. A selected session with calls in a folder that was not passed is an
  **error**, not a partial reconstruction.
- **There is deliberately no headline compression ratio**, and **2.815× and 3.317× must never be
  compared** — different measurements of different things. The register says so at length.
- **Three compression levels, not one.** Storing and scoring use `corpus.compress_level_zstd`;
  training uses its own, lower level.
- **A dictID is not a unique key.** `zstd --train` stamps **1** on everything.
- **`STORE_ERROR`'s value is `"error"`, not `"store_error"`.** Register §11 holds all five sentinels;
  only `too_large` is present in the corpus, on 45 rows.
- **The index is in completion order.** Sort before analysing. `<seq>` in extracted output is
  **timestamp** order for exactly this reason.
- **Stage with explicit paths, never `git add -A`** — there is a deny rule and it fires.
- **Claude Code's built-in no-prompt set does not include git.** Every git command prompts unless an
  allow rule matches. **`git checkout` prompts every time, deliberately — use `git switch`.**
- **`git merge` cannot read its message from stdin.** `-F -` works for `git commit` and fails here;
  write the message to a temp file.
- **Auto mode was turned off by the owner on 2026-08-26**, after `BUG-001` made every `Bash` call
  depend on a failing classifier. `Read`/`Glob` do not use it. Prefer the dedicated tools, which
  `CLAUDE.md` says anyway.

## Two retractions from 2026-08-26 — do not resurrect either

Both are struck rather than deleted, in `notes.md`, so the mechanism that caught them stays visible.

- **The cold reader claimed the `agent_id` prediction had resolved *before* the review.** It was
  reading **its own traffic** — one distinct `agent_id` in the whole corpus. The prediction resolved
  **because of** the run, exactly as predicted.
- **This session claimed the cold run created the `.venv`.** **The owner created it.** A governance
  lesson built on that inference — that the charter template needs an environment clause — was
  **withdrawn, not adopted.** If a delegate does one day exceed its brief, *that* is the evidence.

**The shape under both:** a plausible reading and the true one, one question apart. It is now the
sixth and seventh recorded instance, and one of them was the author's, inside the document recording
the reviewer's. **`IDM-004`'s "verify a refutation before accepting it" is what caught the first.
Asking the owner is what caught the second.**

## The instrument lesson, which keeps paying

**Name what a positive result would look like before running anything.** `plan.md`'s finding 3 wrote
down *"column 3 must hold a non-empty value afterwards, or `observe.py:40` is wrong"* **before** the
review ran. It did, and a comment nobody had ever observed became a measurement. **A probe whose
outcomes are indistinguishable to its reader is not a probe.**

Follow the working agreement in `CLAUDE.md`. **Propose before implementing, ask before touching the
machine and say what it is for, and exercise the real thing before committing** — noting that for this
phase the owner has taken the exercising step for themselves, afterwards.
