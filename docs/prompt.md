# The next session's prompt

*The one file in `docs/` allowed to go stale, per `README.md` — which is why it is rewritten at each
handoff rather than left. **Phase 10 replaced it at Task 23**; whatever opens next replaces it
again.*

---

**Phase 10 is complete and the branch is not merged. Merging it is the owner's, not a session's.**

`feat/phase-10-body-store`, forked from `main` at `d885b2f`. Thirty-three tasks in six groups —
thirty-two planned plus **Task 18a**, inserted during execution. `make test` **158 → 310**.

**Do not re-open the phase.** Its plan, notes and record are in
`docs/milestone-2-corpus/phase-10-body-store/`. Owner decisions live in `plan.md`'s "What is
settled, and by whom" with their rejected alternatives. If one looks wrong, say so and wait.

## What a session should do first

**Read `docs/status.md`.** It says where the project is, what is in flight, and what is next. Then
whichever `docs/reference/` file the work touches — `README.md` there is the index and names the
trigger for each.

**Read those by section, not in wide sweeps.** `plan.md` is ~1,600 lines and `notes.md` ~3,200. Grep
the headings first (`grep -n '^## ' <file>`) and read what the task needs.
`docs/wiki/claude-code-auto-mode.md` says why a whole-file `cat` costs more than it looks like under
auto mode.

## The one thing waiting on the owner

```
git merge --no-ff feat/phase-10-body-store
```

**`git merge` cannot read its message from stdin** — `-F -` works for `git commit` and fails here,
so write the message to a temp file. After merging, two placeholders close: the **Record table** at
the foot of `plan.md`, and **`notes.md`'s first line**, which reads *"Not yet merged."* Both are
listed in `plan.md`'s "Placeholders in this file", which is the section that exists so they are not
forgotten.

## What the phase left standing, deliberately

- **Failure mode 3 of the central claim is not discharged.** Archiving cannot *break* a call — that
  was driven. Whether it *slows* one is **unmeasured**, and settling it needs one driven session
  with capture on against one with it off, comparing `ttfb_ms` and `duration_ms`.
  `docs/milestone-2-corpus/implementation-plan.md` says so in the table rather than implying
  otherwise.
- **A call can still vanish, and now says so.** A caller already gone when the response starts
  leaves no CSV row, no log line and no corpus entry. Observed and reproduced 2026-08-20. The
  shutdown line `calls: N arrived, N recorded, N lost` reports it; **closing** it is still open in
  `docs/backlog.md` and needs a guarantee that a row can never be written twice.
- **Retention is out of scope for Milestone 2** — owner's decision. Nothing deletes an archived
  body and **no policy was decided**. Deliberately *not* in `backlog.md`: it is a scope boundary,
  and it sits in the milestone's non-goals.
- **The extraction tool is a later phase's subject.** The *reader* ships here and `--extract`
  works; selection by day, session, call or model does not exist.

## Things a session gets wrong about this code

- **There is deliberately no headline compression ratio.** Every figure is a small-sample
  confirmation that the mechanism works, not a capability. `docs/reference/measurements.md` carries
  each with its slice and says this in a note. **Anything near 26× on this corpus is a self-scoring
  accident until proven otherwise** — it happened twice in one day by two different mechanisms.
- **Three compression levels, not one.** Storing and scoring a candidate use
  `corpus.compress_level_zstd`; training uses its own, lower level.
- **`python3` here is 3.14; the venv is 3.13.** Anything importing `zstandard` must run under `uv
  run python` or it fails looking like a missing dependency.
- **A dictID is not a unique key.** `zstd --train` stamps **1** on everything; the router derives
  and stamps its own from the dictionary's content.
- **The dictionary pickup is every 500 bodies or a day rollover**, not the next body.
- **`logs/` is gitignored and holds uncommittable things** — a trained dictionary and a captured
  body alike. **Stage with explicit paths, never `git add -A`.**

## What is on disk and not in git

- `logs/corpus/dicts/req-2026-08-20T110338Z-0e4d84d1.dict` — the first real dictionary, 262,144
  bytes. **Do not delete it and do not commit it.**
- `logs/calls.csv` and `logs/router.log` — the router's history to 2026-08-20. **They were
  deliberately left where they are** when the config moved to `logs/telemetry/`; the router creates
  a fresh pair on its next start. Owner's decision, recorded in `plan.md`'s settled table.
- `logs/corpus-gate/` — Phase 9's 8.8 MB corpus. Task 15 trained from it and it stays.
- `docs/procedures/dying-backend/runs/` — Task 18's driving check. Disposable.

## How this phase found what it found

**Green tests are not a sign-off.** Every defect Phase 10 found was found by *driving the thing* or
by *attacking the tests*, and none would have failed the suite as written. Two practices earned
their place:

1. **Mutation testing as a matter of course.** Introduce one deliberate fault into finished code
   and check that a targeted test fails. **A mutation that survives is either a missing test or a
   line doing nothing — find out which.**
2. **Interrogating a passing check.** *"What would make this positive anyway?"* An unchanged
   link-check count is also what a tool that never looked reports; two mutations failing the *same*
   test is what a short circuit looks like. Both were read rather than accepted, and both times the
   mechanism had to be checked before the result meant anything.

**The instrument has lied repeatedly, always with a plausible number. Fix the instrument before
believing the result** — and Task 18 added the sharpest case: the number needed to measure a defect
*was* the defect.

Follow the working agreement in `CLAUDE.md`. **Propose before implementing, ask before touching the
machine and say what it is for, and exercise the real thing before committing.**
