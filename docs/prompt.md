# The next session's opening prompt

**Rewritten 2026-08-19, at the end of the session that re-scoped Phase 10 and reviewed the re-scope.**
It opens execution **from Task 7**, and nothing else.

*Its previous version also opened from Task 7 and became misleading the same day: the plan grew from
twenty-five tasks to thirty-two, the config block from five keys to nine, and the link-checker
baseline it quoted moved from 76 to 83. **This is the third rewrite in two days**, which is what a
file that tracks a task pointer costs — and why `README.md` licenses this one file to go stale and
requires it to be closed out.*

Paste the block below into a fresh session. It is a *starting instruction*, not a handoff note: it
names what to read and what to distrust, and deliberately does not summarise the repository — the
documents it points at are canonical and this file must never become a second copy of them.

**This file still expires.** Phase 10's Task 23 replaces or deletes it **when the phase merges**.
**If Phase 10 is already merged, this file is wrong by definition** — check `status.md` first.

**Paths inside the block are written from the repository root**, since that is where a session starts.
They are not relative to this file, so `procedures/link-check.py` does not check them; all were
verified to exist on 2026-08-19.

---

```
Continue Phase 10 of Milestone 2, executing from Task 7.

The branch already exists: `feat/phase-10-body-store`, forked from `main` at
`d885b2f`. **Check it out; do not open a new one.** `git diff main -- src/` is
still empty and **Task 8 is where that changes** — Task 7 is only a round-trip
smoke test.

Read `docs/status.md` first, then
`docs/milestone-2-corpus/phase-10-body-store/plan.md` — **thirty-two tasks in
six groups** — and its `notes.md` beside it.

**Do not re-plan and do not re-review.** The plan was re-derived against the
code before publication, then forward-reviewed **twice** under
`docs/method/IDM-004-reviewing-unexecuted-work.md`: once over Tasks 4–24
(charter: `review-charter.md`, 22 findings) and once over the 2026-08-19
retraining revision (charter: `review-charter-retraining.md`, 22 findings).
**All of both are applied.** Owner decisions live in `plan.md`'s "What is
settled, and by whom" with their rejected alternatives — **do not reopen them.**
If one looks wrong, say so and wait.

**Groups A and B are done. Do not redo them.** Group B benchmarked before any
store code existed and its numbers are frozen in the phase's `evidence/`.
`zstandard 0.25.0` is already a dependency; **`uv add` it again and you have
misread this.** The GIL is released (3.34x on four threads),
`compress_level_zstd` defaults to 9, and there is **no `corpus.workers` key** —
that was settled by measurement, not argument.

**Task numbers are never renumbered; an insertion takes a letter.** `13a` and
`14a`–`14f` exist for that reason. **`14d` is struck and absorbed into Task 11**
— the letter is spent and not reused.

Baselines to re-derive **by running, never by prediction**:

- `make test` must report **158**. Normally ~0.6 s, but the **first** run after
  the cloud-synced folder evicts the virtualenv takes **two to three minutes**
  on hydration alone. **A slow first run is not a hang.**
- `docs/procedures/link-check.py` reports **83 broken, 2 roundabout, 82 files**
  on this branch and **68 broken on `main`**, both run on 2026-08-19. **It never
  reports zero.** The excess is forward citations to files this plan's own tasks
  create. **It rises when a task cites what it is about to build and falls when
  the file appears.** Treat it as a direction, not a target. Two earlier sessions
  got this wrong by reading the docstring instead of running the tool, and a
  third quoted a stale number from this very file.

What to distrust:

- **`python3` on this machine is 3.14; the venv is 3.13.** Anything importing
  `zstandard` must run under `uv run python`, or it fails looking like a missing
  dependency rather than the wrong interpreter. *(`docs/procedures/event-loop-lag/cpu_offload.py`
  is the one exception and says so — it is stdlib-only and wants 3.14.)*
- **`13.65x` is no longer reproducible, and this is the trap of the day.**
  `train_dictionary` takes a `level` that changes which dictionary you get, and
  `zstandard` defaults it to **3**; Task 6 produced 13.65x by passing **19**. The
  trainer now trains **and** scores at **`TRAIN_LEVEL = 9`**, the write-path
  level. **Task 15 records the level-9 ratio it actually gets.**
- **Phase 9's `12.10x` remains the milestone's figure and remains optimistic** —
  three biases flatter it and the slice note in `docs/reference/measurements.md`
  says which. It was also trained on **48 bodies of which 26 are distinct**;
  `gate.py` never deduplicated, and 46% of its training set was
  `overloaded_error` retries.
- **Dictionary training is non-monotonic in both `k` and `maxdict`**, on both
  trainers. A new dictionary is measured against the one it replaces and never
  assumed better.
- **The corpus has no usable validation split**, and **most days carry one
  session** — `run-02` and `run-03` have exactly one each. That is why the
  training window widens until two sessions are present.
- **A trained dictionary is as uncommittable as the bodies.** Stage with
  explicit paths, never `git add -A`.

Read before writing the relevant code, not after:

- `docs/wiki/background-work-in-fastapi.md` — **before starting any thread.**
  `BackgroundTask` is not the mechanism and `asyncio.create_task` is the one that
  quietly stalls every concurrent request. Measured, not argued.
- `docs/wiki/zstandard-and-libzstd.md` — **before touching compression or
  training.** In particular `write_dict_id`, which one construction path
  silently defaults **off**, and which the whole design depends on.
- `docs/reference/design-decisions.md` and `docs/reference/observability.md` —
  before changing dispatch, the recorder, or adding a column.

Ask before anything touches the machine, and **say what it is for.** Running the
router, driving any session headless or interactive, and any API call each need
their own ask. Consent for one is not consent for the next. Task 18's layer-3
check drives `docs/procedures/dying-backend/`, a local stub, and still needs an
ask.

Worth knowing: `logs/corpus-gate/` holds Phase 9's 8.8 MB corpus across three run
directories plus eight dictionaries, gitignored — check before assuming a capture
is needed, and before assuming it is there. A fresh context will prompt for
`curl`, `python3` and `uv run`; those deliberately stayed out of the tracked
allowlist.

Follow the working agreement in `CLAUDE.md`. Propose before implementing, and
exercise the real thing before committing — green tests are not a sign-off.
```
