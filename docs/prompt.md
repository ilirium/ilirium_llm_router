# The next session's opening prompt

**Rewritten 2026-08-19, at the end of the session that executed Group C.** It opens execution **from
Task 14**, and nothing else.

*Its previous version opened from Task 7. **This is the fifth rewrite in two days**, which is what a
file that tracks a task pointer costs, and why `README.md` licenses this one file to go stale and
requires it to be closed out. Task 23 replaces or deletes it when the phase ends.*

Paste the block below into a fresh session. It is a *starting instruction*, not a handoff note: it
names what to read and what to distrust, and deliberately does not summarise the repository — the
documents it points at are canonical and this file must never become a second copy of them.

---

Continue Phase 10 of Milestone 2, executing from Task 14 — the trainer, opening Group D.

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

**Groups A, B and C are done. Do not redo them.** `src/ilirium_llm_router/corpus.py`
holds **`CorpusWriter` and `CorpusReader`**; `config.py` carries the nine-key
`corpus:` block; `proxy.py`, `observe.py`, `app.py`, `cli.py` and `config.yaml`
are wired; `tests/test_corpus.py` exists. **A body already goes in through
`POST /v1/messages` and comes back out verified.** `zstandard 0.25.0` is already
a dependency; **`uv add` it again and you have misread this.**

**Every constant, key, name and magic number is in one place: `plan.md`'s "The
register".** Read it before writing code that needs a value, and **do not invent
one.** **Task 24 checks the register row by row against the code**, so a value
that ships different from its row is a defect, not a variation. Group D needs
`TRAIN_LEVEL` (3), `TRAIN_D` (8), `INSTALL_MARGIN` (0.02), `TRAIN_BUDGET_S` (60),
`WINDOW_MAX_DAYS` (30), `MIN_SESSIONS` (2) and `LOCK_STALE_S` (3600) — **none of
them is in the code yet.**

**Task numbers are never renumbered; an insertion takes a letter.** `13a` and
`14a`–`14f` exist for that reason. **`14d` is struck and absorbed into Task 11**
— the letter is spent and not reused.

Baselines to re-derive **by running, never by prediction**:

- `make test` must report **218**. Normally ~1 s, but the **first** run after
  the cloud-synced folder evicts the virtualenv takes **two to three minutes**
  on hydration alone. **A slow first run is not a hang.**
- `make lint` clean, `make check` valid.
- `docs/procedures/link-check.py` reports **82 broken, 2 roundabout, 82 files**
  on this branch, run 2026-08-19 **after this file was written**. **It never
  reports zero.** The excess is forward citations to files this plan's own tasks
  create — **`src/ilirium_llm_router/dictionary.py` is cited and Task 14 creates
  it**, so **expect this number to fall when it appears.** Treat it as a
  direction, not a target.

  *It was **81** before this file existed, and **one of the 82 is this very
  section**, citing `dictionary.py` to tell you about it. **The handoff file moving
  the baseline it quotes is the recursion to expect here**, not a defect — the
  previous handoff hit it too. Three earlier sessions got the number wrong by
  reading the docstring or quoting a stale figure instead of running the tool.*

What to distrust:

- **`python3` on this machine is 3.14; the venv is 3.13.** Anything importing
  `zstandard` must run under `uv run python`, or it fails looking like a missing
  dependency rather than the wrong interpreter.
- **There are three compression levels, not one, and conflating them is the trap
  of the phase.** **Archiving** and **scoring a candidate against the incumbent**
  both read `corpus.compress_level_zstd` (9). **Training** uses `TRAIN_LEVEL`,
  which is **3**. Training levels 3 to 19 move the held-out ratio by **0.03%**,
  so it is not a parameter — but it *does* change the dictionary bytes.
- **A dictID is not a unique key, and this is measured, not theoretical.**
  `zstd --train` stamps **1** on everything — Phase 9's eight frozen
  dictionaries are six distinct files all carrying `1`. libzstd's own ID does
  **not** cover the entropy tables, so levels 3/9/19 give **one ID and three
  different files**. **Decided 2026-08-19: the router stamps its own**, via
  `content_dict_id()` — sha256 of the dictionary with its own ID field zeroed,
  first four bytes, `or 1`. **Task 14 must implement that**, and must mask to 32
  bits: an out-of-range `dict_id` **does not raise**, it silently falls back to
  libzstd's own.
- **`13.65x` is not reproducible** — Task 6 produced it at **write** level 19.
  The level-9 figure is **12.920x**. **Task 15 still records its own**, and if it
  lands far from 12.9x something is wrong.
- **Phase 9's `12.10x` remains the milestone's figure and remains optimistic.**
  It was trained on **48 bodies of which 26 are distinct**; 46% of its training
  set was `overloaded_error` retries.
- **Dictionary training is non-monotonic in both `k` and `maxdict`**, on both
  trainers. A new dictionary is measured against the one it replaces and never
  assumed better.
- **The corpus has no usable validation split**, and **most days carry one
  session** — that is why the training window widens until two sessions are
  present.
- **A trained dictionary is as uncommittable as the bodies.** Stage with
  explicit paths, never `git add -A`.
- **Check a number against the phase's `evidence/` before believing the prose.**
  The plan's drain-timeout estimate was out by ~70x against a measurement frozen
  in its own folder, and two forward reviews inherited it.

**Green tests are not a sign-off, and Group C is the evidence.** Every one of its
four defects was found by *driving the thing*, and none would have failed a suite,
because none had a test until it was found. **One of them was found only because a
first test gave a false PASS** — two dictionaries shared a dictID, so the check
agreed by accident. **When a check comes back positive, ask what would make it
positive anyway.**

Read before writing the relevant code, not after:

- `docs/wiki/zstandard-and-libzstd.md` — **before touching compression or
  training.** In particular `write_dict_id`, and the section on assigning your
  own dictID.
- `docs/wiki/background-work-in-fastapi.md` — **before starting the training
  thread.** `BackgroundTask` is not the mechanism and `asyncio.create_task` is
  the one that quietly stalls every concurrent request.
- `docs/reference/design-decisions.md` and `docs/reference/observability.md` —
  before changing dispatch, the recorder, or adding a column.

Ask before anything touches the machine, and **say what it is for.** Running the
router, driving any session headless or interactive, and any API call each need
their own ask. Consent for one is not consent for the next. Task 18's layer-3
check drives `docs/procedures/dying-backend/`, a local stub, and still needs an
ask.

Worth knowing: `logs/corpus-gate/` holds Phase 9's 8.8 MB corpus across three run
directories plus eight dictionaries, gitignored — **Task 15 trains from it**, and
Task 14e's `--from <dir>` exists because it has no day folders. A fresh context
will prompt for `curl`, `python3` and `uv run`; those deliberately stayed out of
the tracked allowlist.

Follow the working agreement in `CLAUDE.md`. Propose before implementing, and
exercise the real thing before committing.

---

## What the next session should know that is not an instruction

**Three things are open and none of them blocks Task 14.** They are recorded in
`milestone-2-corpus/phase-10-body-store/notes.md` under "Open at the end of
Group C" and repeated here only as a pointer.

1. **`compress_level_zstd` reaching the trainer.** Task 14b scores at that key,
   and `DictionaryTrainer` will need the config passed in. `CorpusWriter` takes
   plain values rather than a config block, by the owner's decision of
   2026-08-19; the trainer should follow whichever shape reads better and say
   which it chose.
2. **Whether `CorpusWriter` should switch to taking `Corpus`** now that Task 11
   has built it. The owner said Task 8's shape stands; this is the "one-line
   change at Task 11 or 12" that was deferred and is still deferred.
3. **`_days` grows one entry per day** in a long-running router — a few hundred
   small objects a year. Named so nobody rediscovers it as a leak.
