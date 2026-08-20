# The next session's prompt

*The one file in `docs/` allowed to go stale, per `README.md` — which is why it is rewritten at each
handoff rather than left. **Task 23 replaces or deletes it**; the phase does not close with it in
this state.*

---

Continue Phase 10 of Milestone 2, executing from Task 16 — the telemetry move, opening Group E.

The branch already exists: `feat/phase-10-body-store`, forked from `main` at
`d885b2f`. **Check it out; do not open a new one.**

Read `docs/status.md` first, then
`docs/milestone-2-corpus/phase-10-body-store/plan.md` — **thirty-two tasks in
six groups** — and its `notes.md` beside it.

**Do not re-plan and do not re-review.** The plan was re-derived against the
code before publication, then forward-reviewed **twice** under
`docs/method/IDM-004-reviewing-unexecuted-work.md`. **All findings from both are
applied.** Owner decisions live in `plan.md`'s "What is settled, and by whom"
with their rejected alternatives — **do not reopen them.** If one looks wrong,
say so and wait.

**Groups A, B, C and D are all done. Do not redo them.** The store, the reader,
the trainer, the automatic retraining, the pickup and the manual commands all
exist and are driven. `src/ilirium_llm_router/corpus.py` holds `CorpusWriter`
and `CorpusReader`; `dictionary.py` holds `DictionaryTrainer`,
`content_dict_id()` and `stamp()`; `config.py` carries the nine-key `corpus:`
block; `proxy.py`, `observe.py`, `app.py`, `cli.py` and `config.yaml` are wired.
**A real dictionary is installed** — see "What exists on disk" below.

**Every constant, key, name and magic number is in one place: `plan.md`'s "The
register".** Read it before writing code that needs a value, and **do not invent
one.** **Task 24 checks the register row by row against the code**, so a value
that ships different from its row is a defect, not a variation. Group D added
three rows to it during execution — `DICT_MAGIC`, `TUNE_MAXDICT`, `TUNE_K` —
and **corrected one that described code which did not exist**; that correction
is the shape to copy if you find another.

**Task numbers are never renumbered; an insertion takes a letter.** `13a` and
`14a`–`14f` exist for that reason. **`14d` is struck and absorbed into Task 11**
— the letter is spent and not reused.

## What Group E is

**Task 16** moves `calls.csv` and `router.log` into `logs/telemetry/` —
`config.yaml`, `config.py`'s two defaults, `tests/test_config.py`,
`tests/test_logging_setup.py`, **and the live files on disk**. That last clause
is why this needs an ask before it runs: those two files are real, they are
`logs/router.log` at ~60 KB and `logs/calls.csv` at ~42 KB, and moving them is
not something to detect-and-proceed on.

**Task 17** is the sweep `docs/procedures/link-check.py` **cannot see**, because
it globs `*.md` — including a stale `logs/calls.csv` in **the instrument's own
docstring at line 45**, which Task 24 then runs. Task 17 must also state which
archive and EPD hits were **left** and why.

**`logs/corpus/` is not part of this move** and must not be swept into it. The
corpus has its own directory by design.

Baselines to re-derive **by running, never by prediction**:

- `make test` must report **308**. Normally ~2 s, but the **first** run after
  the cloud-synced folder evicts the virtualenv takes **two to three minutes**
  on hydration alone. **A slow first run is not a hang.**
- `make lint` clean, `make check` valid.
- `docs/procedures/link-check.py` reports **79 broken, 2 roundabout, 82 files**
  on this branch, run 2026-08-20 **after this file was written**. **It never
  reports zero.** The excess is `backlog.md`'s known false-positive class plus
  forward citations to files later tasks create.

  *It fell **82 → 79** when `dictionary.py` appeared, and this session predicted
  81 and was wrong: the file was cited **three** times, once here and **twice in
  the plan's own register**, not once. **The handoff file moving the baseline it
  quotes is the recursion to expect**, and it is why this number is quoted from
  a run made after the file was saved. Four earlier sessions got it wrong by
  reading the docstring or quoting a stale figure. **Run the tool.**
  This rewrite deliberately cites no unbuilt file, so it should not move it.*

## What exists on disk, and is not in git

`logs/` is gitignored. Two things there matter and neither is committed:

- **`logs/corpus/dicts/req-2026-08-20T110338Z-0e4d84d1.dict`** — the first real
  dictionary, 262,144 bytes, installed by Task 15 through the router's own
  `--train-dict`. **Do not delete it and do not commit it.**
- **`logs/corpus/retrain.log`** — one line, the install that produced it.
- `logs/corpus-gate/` still holds Phase 9's 8.8 MB corpus across three run
  directories plus eight dictionaries. **Task 15 trained from it** and it stays.

**A trained dictionary and a captured body are as uncommittable as each other.
Stage with explicit paths, never `git add -A`.**

## What to distrust

- **`python3` on this machine is 3.14; the venv is 3.13.** Anything importing
  `zstandard` must run under `uv run python`, or it fails looking like a missing
  dependency rather than the wrong interpreter.
- **There are three compression levels, not one.** **Archiving** and **scoring a
  candidate against the incumbent** both read `corpus.compress_level_zstd` (9).
  **Training** uses `TRAIN_LEVEL`, which is **3**.
- **A dictID is not a unique key.** `zstd --train` stamps **1** on everything.
  **The router stamps its own** via `content_dict_id()`. The reader still tries
  every candidate and keeps the one that verifies, because a day folder is a
  directory anyone can drop a file into.
- **`13.65x` is not reproducible** — it was produced at **write** level 19.
  **The phase's figure is `12.919x`** on held-out material, measured on disk by
  Task 15, against `2.997x` undicted.
- **Anything near `26x` on this corpus is a self-scoring accident until proven
  otherwise.** It happened **twice** in one day by two different mechanisms —
  `26.210x` from training on `logs/corpus-gate/dicts/`, and `26.870x` from
  scoring on the training set. Both looked plausible.
- **Phase 9's `12.10x` remains the milestone's figure and remains optimistic.**
- **Dictionary training is non-monotonic in both `k` and `maxdict`.** A new
  dictionary is measured against the one it replaces and never assumed better.
- **Check a number against the phase's `evidence/` before believing the prose.**

## How this phase has actually found defects

**Green tests are not a sign-off, and Groups C and D are the evidence.** Every
defect this phase has found was found by *driving the thing* or by *attacking
the tests*, and none would have failed the suite as written.

**Two practices earned their place and should continue:**

1. **Mutation testing as a matter of course.** Introduce a deliberate fault into
   finished code, one at a time, and check that a targeted test fails. It caught
   two assertions that were decoration, one test that exercised the library
   rather than this module, and one line of dead code. **A mutation that
   survives is either a missing test or a line doing nothing — find out which.**
2. **Interrogating a passing check.** *"What would make this positive anyway?"*
   A randomised soak reported `0 failures` while never producing the case it
   existed to test. **Look at what the randomisation actually produced.**

**The instrument has lied at least three times, always with a plausible number.**
Fix the instrument before believing the result.

Read before writing the relevant code, not after:

- `docs/wiki/zstandard-and-libzstd.md` — **before touching compression or
  training.** In particular: **`ZstdCompressionDict` accepts arbitrary bytes**
  and the result reports dictID **0**, which silently destroys blobs. That
  section was written from a Task 14c defect.
- `docs/wiki/background-work-in-fastapi.md` — **before starting any thread.**
- `docs/reference/design-decisions.md` and `docs/reference/observability.md` —
  before changing dispatch, the recorder, or adding a column.

Ask before anything touches the machine, and **say what it is for.** Running the
router, driving any session headless or interactive, any API call, **and Task
16's move of the live `calls.csv` and `router.log`** each need their own ask.
Consent for one is not consent for the next. Task 18's layer-3 check drives
`docs/procedures/dying-backend/`, a local stub, and still needs an ask.

A fresh context will prompt for `curl`, `python3` and `uv run`; those
deliberately stayed out of the tracked allowlist.

Follow the working agreement in `CLAUDE.md`. Propose before implementing, and
exercise the real thing before committing.
