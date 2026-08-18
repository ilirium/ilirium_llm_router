# The next session's opening prompt

**Rewritten 2026-08-18, at the end of the session that executed Groups A and B of Phase 10. It opens
the execution of Phase 10 **from Task 7**, and nothing else.**

*Its previous version opened execution from Task 4 and became wrong as soon as Group B finished — a
session pasting it would have re-installed a dependency and re-run a benchmark whose output is
already frozen in `evidence/`. That is the failure `docs/README.md` licenses this file to risk and
requires it to be closed out for. **This is the second rewrite in one day**, which is what a file
that tracks a task pointer costs.*

Paste the block below into a fresh session. It is a *starting instruction*, not a handoff note: it
names what to read and what to distrust, and deliberately does not summarise the repository — the
documents it points at are canonical and this file must never become a second copy of them.

**This file still expires.** Phase 10's Task 23 replaces or deletes it **when the phase merges**, and
that is unchanged. **If Phase 10 is already merged, this file is wrong by definition** — check
`status.md` before trusting it.

**Paths inside the block are written from the repository root**, since that is where a session starts.
They are not relative to this file. All twelve were verified to exist on 2026-08-18, because
`docs/procedures/link-check.py` resolves relative to the citing file and therefore does not check them.

---

```
Continue Phase 10 of Milestone 2, executing from Task 7.

The branch already exists: `feat/phase-10-body-store`, forked from `main` at
`d885b2f`. **Check it out; do not open a new one.** It carries documentation,
`pyproject.toml`, `uv.lock` and a new instrument under
`docs/procedures/corpus-benchmark/`. **`git diff main -- src/` is still empty,
and Task 8 is where that changes** — Task 7 is only a round-trip smoke test.

Read `docs/status.md` first, then
`docs/milestone-2-corpus/phase-10-body-store/plan.md` — twenty-five tasks in six
groups — and its `notes.md` beside it.

**Do not re-plan and do not re-review.** Both have already happened and both are
recorded. The plan was re-derived against the code before it was published, and
then forward-reviewed under `docs/method/IDM-004-reviewing-unexecuted-work.md` by
two passes — the authoring session and a fresh-context agent — which returned 22
findings. All 22 are applied. `review-charter.md` in the same folder is what the
reviewers were given.

**Groups A and B are done. Do not redo them.** Group B benchmarked before any
store code existed, and Group C is written against what it found:

- **The GIL is released** — read off the shipped binary at Task 4 and measured at
  **3.34x on four threads** at Task 6. The worker-thread design stands and the
  negative branch was not taken. `zstandard 0.25.0` is already a declared
  dependency; **`uv add` it again and you have misread this.**
- **`compress_level_zstd` defaults to 9**, measured, not assumed.
- **There is no `corpus.workers` key.** One worker carries ~500x the target peak.
  Task 11 stays at five keys.
- **Task 14's trainer must set `k` explicitly.** The two dictionary trainers
  disagree by up to 15% at their defaults, and the tool was never the variable.

The numbers are frozen at
`docs/milestone-2-corpus/phase-10-body-store/evidence/results.txt`, with the
instrument beside it. Task 21 puts them in `docs/reference/measurements.md`.

**Task numbers are never renumbered. An insertion takes a letter.** The list was
renumbered once, before execution, and that exception is spent.

Owner decisions are recorded in `plan.md`'s "What is settled, and by whom" table
with their rejected alternatives. **Do not reopen them.** If one looks wrong, say
so and wait — it is the owner's, not the phase's.

Ask before anything touches the machine, and **say what it is for**. Running the
router, driving any session headless or interactive, and any API call each need
their own ask. Consent for one is not consent for the next. Task 18's layer-3
check drives `docs/procedures/dying-backend/`, which is a local stub and still
needs an ask.

Baselines to re-derive by running, never by prediction:

- `docs/procedures/link-check.py` reports **68 broken and 2 roundabout on `main`,
  76 on this branch.** It never reports zero. The excess is files this plan's own
  tasks have yet to create plus `review-charter.md` naming the known false
  positives. **It rises when a task cites what it is about to build and falls when
  the file appears** — it went 79 → 80 → 76 in one session. Treat it as a
  direction, not a target. Two earlier sessions got this wrong by reading the
  docstring instead of running the tool.
- `make test` must report **158**. Normally ~0.6 s — but the **first** run after
  the cloud-synced folder has evicted the virtualenv takes **two to three minutes**,
  because every package file is fetched on first touch. **A slow first run is not a
  hang.** One session abandoned three invocations before finding that out.

What to distrust:

- **`python3` on this machine is 3.14; the venv is 3.13.** Anything importing
  `zstandard` must run under `uv run python`, or it fails in a way that looks like
  a missing dependency rather than the wrong interpreter.
- **The 12.10x compression figure is optimistic.** Three biases flatter it and the
  slice note in `docs/reference/measurements.md` says which. Never quote it without
  them. **Phase 10's 13.65x does not supersede it** — same three biases plus a
  fourth, its parameter having been chosen against the slice it is reported on.
- **Dictionary training is non-monotonic in both `k` and `--maxdict`**, now
  confirmed on both trainers rather than one. A new dictionary is measured against
  the one it replaces and never assumed better.
- **The corpus has no usable validation split** — the smallest run has two
  qualifying bodies. Task 15 must call its parameter choice provisional, not
  optimal, and must not present a tuned number as measured-optimal.
- **A trained dictionary is as uncommittable as the bodies**, and losing one makes
  every blob referencing it unreadable. Stage with explicit paths, never
  `git add -A`.

Worth knowing: `logs/corpus-gate/` holds Phase 9's 8.8 MB corpus across three run
directories plus eight dictionaries, gitignored — check before assuming a capture
is needed, and check before assuming it is there. A fresh context will prompt for
`curl`, `python3` and `uv run`; those deliberately stayed out of the tracked
allowlist, and that is by design.

Follow the working agreement in `CLAUDE.md`. Propose before implementing, and
exercise the real thing before committing — green tests are not a sign-off.
```
