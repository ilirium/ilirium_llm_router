# Phase 12 — evidence

| File | What it is |
|---|---|
| `env-discovery-probe.md` | The driven proof that an installed router does not read `.env` from the working directory, with the exported-variable control that isolates the cause |
| `wheel-contents.md` | Every entry inside the built wheel, with sizes and hashes — the proof that both templates ship as package data with no build configuration |
| `register-check.py` | The phase's closing check, per `IDM-008` — 28 assertions over the register, re-runnable on the trunk after the merge |

*Written 2026-09-02 at the phase's opening, when nothing was frozen here and it was not clear
anything would be. The first row arrived the same day, from Group B.*

**What this phase produces is mostly observation, not artefact.** Group B drives an installed tool
and records what it does; those records belong in `../notes.md`. Phases 9 and 11 froze real slices —
a corpus, a redacted index — because a later reader needed to re-run something against them. **Two
things here turned out to be of that kind**, and both are listed above.

**What would earn a place here**, if it happens:

- ~~**The listing that proves the config template shipped inside the wheel.**~~ **Done** —
  `wheel-contents.md`. Task 7's claim cannot be re-checked from prose, and the machine that could
  refute it — one without this repository — does not exist here, so the listing is the nearest
  available proof. *It was still an open bullet after Group C had proved the claim twice; the
  proving happened and the freezing did not.*
- ~~**The transcript of an installed run in a directory that is not the repository**, if Group B
  finds anything that contradicts the plan.~~ **It did** — `env-discovery-probe.md` above.

*If neither happens, this file is the record that neither happened.*

**`wheel-contents.md` no longer re-derives in two of its 23 rows, and it is not edited.** The review
of the finished work rebuilt the wheel at the merge and found `METADATA` and `RECORD` differing from
the frozen listing — 16853 against 7112 bytes, and 1823 against 1822. **Every other row matches
byte for byte, including both template rows, which are the ones the file exists to prove.**

*The cause is exact and it is not a defect in the wheel.* `pyproject.toml:5` sets
`readme = "README.md"`, so the README is copied into `METADATA`; task 13 grew the README from 6534
to 16275 bytes, and `METADATA` grew by the same 9741. `RECORD` moved one byte because it records
`METADATA`'s new length.

**The listing is a capture and captures are never edited** — `../../../README.md`'s rule, which says
the fix for a stale transcript is a line in the evidence directory's own `README.md`. This is that
line. *It also means the file's claim — "it is re-derivable: build a wheel and read its archive" —
is true, and re-deriving it is now how you learn that the README is inside the metadata.*

**`register-check.py` is the third and it is a different kind.** The two above are *records* — a
listing and a probe, frozen because they cannot be re-derived. This one is an *instrument*: it reads
the code and the documents and re-checks the register's 28 rows on demand, which is what makes it
worth keeping after the phase closes. Phase 11 froze one for the same reason.

**It was mutation-tested before it was trusted**, because 28 passing assertions prove nothing on
their own. Three targets were changed — the README's test count, the config template's bytes, and
`load_dotenv`'s argument back to the old broken call — and the check failed on exactly three rows,
each attributable to its own mutation. *`git status` was read immediately after restoring, per the
standing warning that an interrupted mutation once left a module comment-stripped with the suite
passing. The tree held nothing.*

**One check needed narrowing on its first run, and the reason generalises.** Testing for unvalued
register rows with a plain search for the `❓` marker matches the two sentences that *state the
rule* — the register's preamble and the plan's exit criterion — and reports the phase incomplete
because it documented what complete means. It looks at table rows only. **That is the same false
positive `IDM-001`'s placeholder sweep hits**, met independently, in a different instrument, the
same week.
