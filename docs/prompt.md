# The next session's opening prompt

**Rewritten 2026-08-18, at the end of the session that planned and reviewed Phase 10. It opens the
*execution* of Phase 10 from Task 4, and nothing else.**

*Its previous version opened the **planning** of Phase 10 and became wrong the moment planning
finished — a session pasting it would have re-planned work that is done, which is the exact failure
`docs/README.md` licenses this file to risk and requires it to be closed out for.*

Paste the block below into a fresh session. It is a *starting instruction*, not a handoff note: it
names what to read and what to distrust, and deliberately does not summarise the repository — the
documents it points at are canonical and this file must never become a second copy of them.

**This file still expires.** Phase 10's Task 23 replaces or deletes it **when the phase merges**, and
that is unchanged. **If Phase 10 is already merged, this file is wrong by definition** — check
`status.md` before trusting it.

**Paths inside the block are written from the repository root**, since that is where a session starts.
They are not relative to this file. They were verified by hand on 2026-08-18, because
`docs/procedures/link-check.py` resolves relative to the citing file and therefore does not check them.

---

```
Continue Phase 10 of Milestone 2, executing from Task 4.

The branch already exists: `feat/phase-10-body-store`, forked from `main` at
`d885b2f`, eleven commits, all documentation. **Check it out; do not open a new
one.** `git diff main -- src/` is empty and Task 4 is where that changes.

Read `docs/status.md` first, then
`docs/milestone-2-corpus/phase-10-body-store/plan.md` — twenty-five tasks in six
groups — and its `notes.md` beside it.

**Do not re-plan and do not re-review.** Both have already happened and both are
recorded. The plan was re-derived against the code before it was published, and
then forward-reviewed under `docs/method/IDM-004-reviewing-unexecuted-work.md` by
two passes — the authoring session and a fresh-context agent — which returned 22
findings. All 22 are applied. `review-charter.md` in the same folder is what the
reviewers were given. A phase's first act is normally to re-derive its own plan;
that act is done, and repeating it spends a session re-deciding settled things.

**Task numbers are never renumbered. An insertion takes a letter.** The list was
renumbered once, before execution, and that exception is spent — `plan.md` says so
where it happened.

Four decisions were taken by the owner across four interviews and are recorded in
`plan.md`'s "What is settled, and by whom" table with their rejected alternatives.
**Do not reopen them.** If one looks wrong, say so and wait — it is the owner's,
not the phase's.

Ask before anything touches the machine, and **say what it is for**. Task 4 is
`uv add zstandard`, which was cleared but confirm it. Running the router, driving
any session headless or interactive, and any API call each need their own ask.
Consent for one is not consent for the next. Task 18's layer-3 check drives
`docs/procedures/dying-backend/`, which is a local stub and still needs an ask.

Baselines to re-derive by running, never by prediction:

- `docs/procedures/link-check.py` reports **68 broken and 2 roundabout on `main`,
  79 on this branch.** It never reports zero. The extra hits are files that this
  plan's own tasks create plus `review-charter.md` naming the known false
  positives; its docstring says which hits are permanent. Two earlier sessions got
  this wrong by reading the docstring instead of running the tool.
- `make test` must report **158**. Normally ~0.6 s — but the **first** run after
  the cloud-synced folder has evicted the virtualenv takes **two to three minutes**,
  because every package file is fetched on first touch. **A slow first run is not a
  hang.** One session abandoned three invocations before finding that out.

What to distrust:

- **The 12.10x compression figure is optimistic.** Three biases flatter it and the
  slice note in `docs/reference/measurements.md` says which. Never quote it without
  them.
- **That `zstandard` releases the GIL is unverified**, and the whole worker-thread
  design rests on it. Tasks 4 and 6 settle it. If it is false, Task 6 stops and
  proposes rather than proceeding to Group C.
- **`zstd --train` was non-monotonic at 68 samples**, so a new dictionary is
  measured against the one it replaces rather than assumed better.
- **A trained dictionary is as uncommittable as the bodies**, and losing one makes
  every blob referencing it unreadable. Stage with explicit paths, never `git add -A`.

Worth knowing: `logs/corpus-gate/` holds Phase 9's 8.8 MB corpus across three run
directories plus eight dictionaries, gitignored — check before assuming a capture
is needed, and check before assuming it is there. A fresh context will prompt for
`curl`, `python3` and `uv run`; those deliberately stayed out of the tracked
allowlist, and that is by design.

Follow the working agreement in `CLAUDE.md`. Propose before implementing, and
exercise the real thing before committing — green tests are not a sign-off.
```
