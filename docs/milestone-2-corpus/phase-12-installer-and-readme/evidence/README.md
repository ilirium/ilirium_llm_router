# Phase 12 — evidence

| File | What it is |
|---|---|
| `env-discovery-probe.md` | The driven proof that an installed router does not read `.env` from the working directory, with the exported-variable control that isolates the cause |
| `wheel-contents.md` | Every entry inside the built wheel, with sizes and hashes — the proof that both templates ship as package data with no build configuration |

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
