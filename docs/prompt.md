# The next session's opening prompt

**Written 2026-08-17 at the end of Phase 9, refreshed the same day. It opens Phase 10 and nothing
else.**

*Refreshed after seven commits landed behind it. Only one of them changed what a session needs told:
`IDM-001` gained a closeout rule, so the block now points at it. `status.md`'s shape also changed —
one row per milestone — and the block needed **no** edit for it, because it points at that file rather
than restating it. **That is the design working**, and it is the reason the pointing rule is worth
keeping when this file is next rewritten.*

Paste the block below into a fresh session. It is a *starting instruction*, not a handoff note: it
names what to read and what to distrust, and deliberately does not summarise the repository — the
documents it points at are canonical and this file must never become a second copy of them.

**This file expires.** Replace it wholesale when Phase 10 merges, or delete it. A stale opening prompt
is worse than none: it would send a session to re-derive work that is already done, which is the
failure `method/IDM-001-git-branching.md` calls this repository's signature one — a document recording
intent that nobody closed out. **If the phase it names is already merged, this file is wrong by
definition.** Check `status.md` before trusting it.

**Paths inside the block are written from the repository root**, because that is where a session
starts. They are not relative to this file.

---

```
Plan and execute Phase 10 of Milestone 2.

Read `docs/status.md` first, then `docs/milestone-2-corpus/implementation-plan.md`
(Phase 10 is there in outline, and the milestone's central claim is now named at
the top — Phase 10 tests two of its three failure modes). Phase 9 is merged as
`b29d502`; there is no handoff note and none is needed.

Phase 10 builds the body store. `EPD-003` is **decided** — do not reopen it. Its
decision lives in `docs/reference/design-decisions.md` under "Bodies are archived
as content-addressed per-call files"; the EPD is kept for reasoning only. What it
left open as design detail is its own open questions 3-6: what is captured by
default, opt-in versus always-on, retention, and whether headers are stored.
Question 6 is the sensitive one — headers carry the credential.

`docs/milestone-2-corpus/phase-9-corpus-gate/plan.md` carries a fenced section,
"Design produced by the interview", holding a full tree and dictionary lifecycle.
It was written *before* the gate ran and is **input to be re-derived, not a
specification**. Re-derive it against what is now known, and say plainly where it
is wrong — Phase 9's own re-derivation found five things wrong, three of them in
`EPD-003`.

Four things Phase 9 established that bear directly on this one:

- **`calls.csv` cannot be the corpus's join table.** `backup_count: 10` means it
  discards its oldest segment, so bodies would outlive their index. Do not change
  `calls.csv` — not its columns, not its rotation. The corpus carries its own
  durable index.
- **A capture hook in `watch()` misses the error paths.** Phase 9 measured 158
  requests but 149 responses in one test run; the gap is calls returning before the
  response generator runs. Those are the rows `EPD-003` calls the interesting ones.
- **`zstd --train` was non-monotonic at 68 samples** — a larger `--maxdict`
  produced a *worse* dictionary. Any retraining policy must measure a new
  dictionary against the one it replaces rather than assume improvement.
- **A trained dictionary contains verbatim substrings of its samples**, so it is
  exactly as uncommittable as the bodies, and losing one makes every blob
  referencing it unreadable.

The 12.10x gate figure is optimistic — three biases flatter it, and the slice note
in `docs/reference/measurements.md` says which. Do not quote it without the slice.

Pick the branch prefix per `docs/method/IDM-001-git-branching.md` and say in the
plan why. Note Phase 9 was `docs/` because no `src/` change survived it; this one
is different.

Read that document's section "Closing out a status placeholder is part of the
merge" **before** you merge, not after. It was added on 2026-08-17 because Phase 9
obeyed the narrower rule it replaced and still shipped two stale placeholders —
`*(not started)*` group markers in its own plan, and a task count in `status.md`.
Both were caught by the owner rather than by the phase.

When Phase 10 merges, **replace or delete `docs/prompt.md`** — this file. It names
Phase 10 and nothing else, and a stale opening prompt sends the next session to
redo finished work. `docs/README.md` records that it is the one file there allowed
to go stale, and why that means it must be closed out.

Bundled into this phase deliberately: move `calls.csv` and `router.log` into
`logs/telemetry/`, alongside the new `logs/corpus/`. It touches `config.yaml` and
paths cited from `src/` docstrings, which `link-check.py` cannot see — so it wants
one move and one sweep, not two.

Do you want to ask me anything? Please interview first. If you find anything
wrong, say so rather than working around it.

Follow the working agreement: propose the plan and wait for an explicit go-ahead
before executing. Ask again before anything touches the machine — running the
router, driving real sessions, or making API calls. Consent for one is not consent
for the next.

Baselines to re-derive rather than trust: `procedures/link-check.py` reports 68
broken and 2 roundabout today — run it, do not predict it from its docstring.
`make test` must report 158.

Worth knowing: `logs/corpus-gate/` may still hold Phase 9's 8.8 MB corpus across
three run directories plus dictionaries — check before assuming a fresh capture is
needed, and check before assuming it is there. A fresh context will prompt for
`curl`, `python3` and `uv run` if the local allowlist is lost; those deliberately
stayed out of the tracked file, and that is by design.
```
