# The next session's prompt

*The one file in `docs/` allowed to go stale, per `docs/README.md` — which is why it is rewritten at each
handoff rather than left. **It names what to read and what to distrust; it never summarises what
those documents say.** Check `docs/status.md` before trusting a word of it.*

**Rewritten 2026-08-21, and shortened from 111 lines to this.** The version it replaces had expired:
it opened Phase 10, which merged as `32c26bb`. It had also drifted into being a summary — five
sections restating what `docs/reference/lessons.md`, `docs/status.md`, `docs/reference/corpus.md` and the phase notes already
held, which is the one thing this file is not for. Two things in it existed nowhere else and were
**harvested before it was cut**, named at the bottom.

---

## No phase is open

**Phase 10 merged on 2026-08-21. Phase 11's subject is not chosen**, and choosing it is a planning
decision that is not inherited from this file. **So there is nothing here to execute.** A session
starting now is picking up work, not resuming it.

## Read these, in this order

1. **`docs/status.md`** — where the project is, what is on disk, what is next. It is the only file
   here that is *state*, and everything below defers to it.
2. **`docs/backlog.md`** — the inventory Phase 11's subject gets picked from. `docs/status.md`'s "What is
   next" names three candidates and is deliberately not the full list.
3. **Whichever `docs/reference/` file the work touches.** `docs/reference/README.md` is the index and
   names the trigger for each — the moment you would open *that* file rather than its neighbour.

**Read them by section.** `CLAUDE.md`'s "Reading" section says how and why, and points at the wiki
page that ranks the levers. This matters most for a phase's `plan.md` and `notes.md`.

## What to distrust

- **This file, first.** It is the one document allowed to be wrong. `docs/status.md` wins every
  disagreement.
- **Any count in prose.** This repository's signature failure is a sentence that undercounts going
  stale where a missing table row would have been visible — `docs/status.md` records it happening twice to
  itself, and once more on 2026-08-21 when regenerating `docs/reference/branches.md` made four sentences
  stale at once. **Re-derive a number from its table or its instrument; never relay it.**
- **An `EPD-NNN` document.** Nothing in one is implemented unless it names an acceptance date.
  `IDM-NNN` documents are the opposite — in force, and to be acted on.
- **A green check.** `docs/reference/lessons.md` §3, §4, §7 and §8 are four different ways this project has
  been wrong about a passing result. §8 is the one that says what to *do* about it.

## Before opening a phase

→ **`docs/method/IDM-008-the-register.md`** before writing `plan.md`, and
→ **`docs/method/IDM-005-opening-a-milestone.md`** only if a *milestone* is opening, which it is not.

Milestone 2 is open with three phases done. `docs/milestone-2-corpus/implementation-plan.md` is its live
plan until it closes.

## What the owner has not done yet

**Exercising the corpus by hand comes before Phase 11 opens** — `docs/status.md`'s first "What is next"
item, and it is the owner's, not a session's. The store has been driven by Phase 10's own checks and
never in ordinary use. **It is off by default**, so no `logs/corpus/` from a fresh start is correct
behaviour rather than a fault.

---

*What was harvested out of the previous version, so nothing was lost in the cut:*

- **Two testing practices** — mutation testing as a matter of course, and interrogating a passing
  check — are now `docs/reference/lessons.md` **§8**, beside the three lessons they operationalise. They
  had no home outside this file.
- **The on-disk inventory** — the trained dictionary, Phase 9's corpus, the pre-move telemetry files
  — is now `docs/status.md`'s "What is on disk and not in git", verified by looking rather than relayed.
  **One warning in it was dropped rather than carried**, and `docs/status.md` says why.

*Everything else the previous version said was already in `docs/status.md`, `docs/reference/lessons.md`,
`docs/reference/corpus.md`, `docs/reference/measurements.md`, `CLAUDE.md` or the Phase 10 notes. It was cut as
duplication, not discarded as wrong.*
