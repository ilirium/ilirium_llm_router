# Status

**State, not inventory.** Unscheduled work lives in `backlog.md`; this file says where the project
is and what is in flight. Three sections, most volatile first.

---

## Where we stopped

*Changes every session. If this section passes ~30 lines, or starts carrying anything that outlives
the session that wrote it, it has become a document and gets its own file.*

**2026-08-21 — `docs/branch-index` merged as `3233fb7`, and the session's work is in five permanent
homes rather than here.** The branch carried two bodies of work: the **branch index** —
`reference/branches.md`, generated from git by `procedures/branch-index.py`, which `IDM-001` had
refused as a hand-maintained list and now admits as a derived one — and **four method items on the
owner's instruction**: `IDM-007` (raising a concern where it will be read), `IDM-008` (the register),
the read-by-section rule in `CLAUDE.md`, and the forward-only `notes.md` split in `README.md`.

**Read the merge message `3233fb7` for what the branch decided.** It carries no phase number, so per
`IDM-001`'s third row that message *is* its record and it was written as the phase note it does not
have.

**Two things this session established that are worth arriving knowing.** **Checking before writing
changed two of the four items** — `IDM-008` turned out to be Phase 10's register, instructed on
2026-08-19, so it is written from that instance and carries its four findings as argument rather than
assertion; the reading rule turned out to be a wiki page's lever 2 needing a *trigger* rather than a
home. And **enumerating refs found `docs/add-claude-md`**, the repository's first branch, unrecorded
in any document for twenty-five days — no rule was broken, there was simply nowhere to record a
fast-forwarded branch belonging to no phase.

**The count sweep fired on its first use, and that is the thing to trust the mechanism for.**
Regenerating the index after the merge took the table from 18 rows to 19 and made four sentences in
three live documents stale in the same instant. They were re-derived from the table, not incremented:
**eight of nineteen** branches carry no phase number. `f445d6f` records it.

**`prompt.md` was rewritten, not deleted** (`665722d`), after harvesting the two things that lived
only in it — the mutation-testing and passing-check practices into `reference/lessons.md` **§8**, and
the on-disk inventory into this file. One claim in it was **dropped rather than carried**: `logs/` is
gitignored, so its `git add -A` warning named a hazard that does not exist.

**`CLAUDE.md` is 297 lines, up from 260**, accepted deliberately by the owner against upstream's ~200
guidance; the measurement of what it could lose is in `backlog.md` as a review-phase item, which is
the condition it was accepted under.

**Phase 10 remains the last phase, merged `32c26bb`.** What it does and does not claim is in
`milestone-2-corpus/implementation-plan.md` and `backlog.md` rather than here — failure mode 3
undischarged, a call can still vanish, and no headline compression ratio.

**Baselines, run not predicted 2026-08-21 at the close of this session: `make test` **310**,
`make lint` clean, `make check` valid, `branch-index.py --check` current at **19 rows**,
`link-check.py` **44 files / 3 broken / 0 roundabout** over the live tiers — the three are `EPD-001`
and `EPD-004`'s known deliberate absences, listed in `procedures/link-check.py`'s docstring.**
*(A whole-repository run reports 91 / 76 / 2, most of it the frozen restructure archive; the absolute
count also depends on untracked files, so compare deltas rather than absolutes. `make test` is ~2 s
warm; a **first** run after the cloud folder evicts the virtualenv takes two to three minutes on
hydration alone — slow, not stuck.)*

*Trimmed from 90 lines to this at the close of 2026-08-21, per this section's own ~30-line rule and
for a second reason: its baseline line still read `link-check.py` **86 files, 75 broken** from before
this branch, which is the staleness the rule exists to prevent. **Nothing was lost** — Phase 10's
entry is `phase-10-body-store/notes.md` as frozen-primary, and this session's is `3233fb7`.*

## Where the project is

*Changes every phase.*

**One row per milestone. Per-phase detail lives in the archive** — branch, fork point and merge commit
belong to the phase note, and each milestone's own index reads its phases in order.

| | Subject | Phases | State | Read it in |
|---|---|---|---|---|
| **1** | The core router — dispatch, byte-relay, observability, failure handling | 1–7 | **complete** 2026-08-07 | `milestone-1-core/README.md`, which carries every branch and merge hash with what each phase settled |
| **2** | The corpus — capturing bodies for analysis | 8– | **open**, three phases in — 8, 9 and 10, the last merged 2026-08-21 | `milestone-2-corpus/implementation-plan.md` **until the milestone closes**; its `README.md` is a closing artefact and does not exist yet |

*Changed 2026-08-17 from a per-phase table of Milestone 1's merge commits, per the `backlog.md` item
that proposed it. **The hashes are not lost** — each one keeps two to six homes, the fewest being
`532dc86` and `9c30924` at two apiece, and `milestone-1-core/README.md`'s table is strictly richer than
the one removed. What this file kept is
the part that is **state**; a closed milestone's per-phase merge hashes are archive record, and
`status.md` says so at the top.*

Phases 0 and 1 were fast-forwarded before the `--no-ff` convention existed;
`milestone-1-core/README.md` says why they are left that way. **Milestone 2 starts at Phase 8**,
since 7 is taken.

**What Milestone 1 settles:** no protocol translation is needed, and a local model can drive a real
coding session through the router. Both halves were measured rather than argued — one session reached
both backends, and a local model handled tool use, file editing and multi-turn conversation.

**Milestone 2's subject is `EPD-003`** — capturing bodies for a corpus, **decided 2026-08-17**.

**Its central claim is now named**, at the end of Phase 9 and from what the gate returned:

> *The router can archive every body it carries — as opaque, content-addressed, per-call files
> compressed against a shared dictionary — without parsing a payload, without slowing a call, and
> without special storage infrastructure.*

**Two of its three failure modes are discharged**, and the third is not. Phase 9's measurement
settled the storage-infrastructure half; **Phase 10 settled that archiving cannot stay opaque** — tar
a day folder, unpack it elsewhere, and every blob opens and verifies against the digest in its own
filename. **Whether archiving slows a call is untested**, and is parked in `backlog.md`.

**Three phases done. The first two touched no `src/`** — Phase 8 built the method tier and the
guardrails, Phase 9 decided `EPD-003` and ran the gate that named the claim above — **and Phase 10 is
the first of this milestone that did**, merging 2026-08-21 as `32c26bb`.
*(Both sentences above were stale between Phase 10's close and this edit: they said two phases and
that Phase 10 had the opaque half still to test. **That is the paragraph below happening again, to
the paragraph that describes it** — prose that undercounts goes stale where a missing table row would
be visible. Recorded rather than quietly fixed, because it is now the second instance.)*
`milestone-2-corpus/implementation-plan.md` describes all three; **their merge
hashes are in their phase notes**, which is where `method/IDM-001-git-branching.md` puts the permanent
record. *(This sentence first said the plan indexes both hashes. It carries Phase 8's and not Phase 9's
— the plan's Record table records the branch **that file** was created on, which was Phase 8's.)*

*This paragraph carried both merge hashes and a note deferring to the `backlog.md` item above. **That
item is now decided and this is the evidence it asked for:** the prose version said "one phase of it is
done" after Phase 9 merged, and stayed wrong until the owner noticed — while the per-phase table beside
it never went stale, because a merged phase without a row is visibly missing and a sentence that
undercounts is not. **The conclusion is not "prefer tables"** — it is that the row-versus-prose choice
is about what goes stale invisibly, which is a different axis from the duplication the item was
arguing.*

## What is next

*Changes every phase. Two or three items lifted from `backlog.md` and cited to it — the file itself
is the full inventory.*

1. **Exercise the corpus by hand — the owner's, and it comes before Phase 11 opens.** The store has
   been driven by Phase 10's own checks and never by its owner in ordinary use. **It is off by
   default**, so turning it on is the first step and no `logs/corpus/` until then is correct
   behaviour; `reference/corpus.md` is the spec and names what else a session gets wrong from the
   name alone. **`logs/telemetry/` does not exist yet either** — the router creates it on its next
   start, and the old `logs/calls.csv` and `logs/router.log` were deliberately left where they are.
   *(This item read "Execute Phase 10 — the body store, from Task 16 (Group E)" until 2026-08-21,
   eight tasks after it stopped being true, and was then the merge until the merge happened. It is
   the defect this file's own milestone-table entry describes: prose that undercounts goes stale
   invisibly, where a missing row would not.)*
2. **Plan Phase 11 — and its subject is deliberately not chosen here.** The candidates are in
   `backlog.md`, which is the full inventory; picking one is a planning decision, not something the
   next session inherits from this file. **`EPD-003`'s open questions 3–6 are not among them** — they
   were closed in `EPD-003` itself on 2026-08-20 at Task 20, three answered and retention marked out
   of scope for Milestone 2 on the owner's decision rather than answered.
3. **Decide `EPD-001` or `002`.** Both are blocked on a person rather than on work, and both are argued
   on a case Phase 4 measurably weakened — see `backlog.md`, "Decisions waiting on a person". Deciding
   one is cheaper than any measurement in the list, and neither decision waits on Phase 11.
   (`EPD-003` is no longer among them — decided 2026-08-17 by Phase 9.)

*The measurement items are both in `backlog.md` under "Measurements left open" and neither is listed
here as next, because the owner has not chosen Phase 11's subject and this file is not the inventory.
Whether Claude Code shows LM Studio's context error was already there. **Whether archiving slows a
call was added there on 2026-08-21** — until then it lived only in `prompt.md`, which is the one file
allowed to go stale, and in `milestone-2-corpus/implementation-plan.md`'s table.*

## What is on disk and not in git

*Harvested here 2026-08-21 from `prompt.md`, which was the only place it was written down and which
expires by design. **Verified by looking**, not relayed. This is working-copy state, so it belongs in
this file and it goes stale — re-check before trusting a line of it.*

`logs/` is gitignored whole (`.gitignore:228`), so none of this can be committed by accident.

| Path | What it is |
|---|---|
| `logs/corpus/dicts/req-2026-08-20T110338Z-0e4d84d1.dict` | **The first real dictionary**, 262,144 bytes exactly. **Do not delete it.** `measurements.md` cites the `0e4d84d1` ID as evidence that the same parameters reproduce the same dictionary byte for byte |
| `logs/corpus-gate/` | Phase 9's corpus, **8.8 MB**. Task 15 trained the dictionary above from it, and `measurements.md` names it as the slice behind four rows. It stays |
| `logs/calls.csv`, `logs/router.log` | The router's history to 2026-08-20. **Deliberately left** where they are when the config moved to `logs/telemetry/` — owner's decision, in `milestone-2-corpus/phase-10-body-store/plan.md`'s settled table |
| `logs/telemetry/` | **Does not exist yet.** The router creates it on its next start. Its absence is correct |
| `docs/procedures/dying-backend/runs/` | Task 18's driving check. Disposable — an instrument's `runs/` is overwritten by the next run |

**One warning was dropped rather than carried across.** `prompt.md` said *"stage with explicit paths,
never `git add -A`."* The stated reason was that `logs/` holds uncommittable things — and `logs/` is
gitignored, so `git add -A` cannot stage any of it. The advice may still be worth following for other
reasons, but **the reason given for it was not a real hazard**, and repeating it would have preserved
a rule whose justification does not hold.

## In-flight branches

*Merged branches are not listed here — this section holds live state. **They are indexed in
`reference/branches.md`, generated from git**, which is the 2026-08-21 amendment to
`method/IDM-001-git-branching.md`: a hand-maintained list would drift and a derived one cannot. The
permanent record of a phase's branch, fork point and merge commit is still its phase note.*

**None. The table is empty as of 2026-08-21**, when `docs/branch-index` merged as **`3233fb7`** and
its row went with it — forked at `5352d0d`, six commits, documentation only. **Phase 11 still has no
branch because its subject is not chosen** — the plan opens the phase branch, so there is nothing to
list until one is.

*What that branch was is no longer this file's job to remember, and that is the point of it.* It
carried no phase number, so it has no phase note; its permanent record is **its merge commit
message**, which `IDM-001`'s third row added on the day it was needed, plus **its row in
`reference/branches.md`**, which the fourth row added the same day. The branch that exposed both gaps
is the first to be recorded by both.

*It was empty in exactly this way once before: `docs/phase-9-corpus-gate` merged as **`b29d502`** on
2026-08-17 and nothing replaced it until Phase 10 opened. The permanent record of both — branch, fork
point and merge commit — is in the phase notes, which is where `method/IDM-001-git-branching.md` puts
it and why this section may go empty without losing anything.*

**It was a `docs/` branch although the phase was about the router**, because no `src/` change survived
it: Task 6 patched `proxy.py` and restored it, and `git diff main -- src/` was empty at the merge.
`method/IDM-001-git-branching.md` is what makes that the right prefix — the prefix says what kind of
work it is, and `phase-N-` says it is numbered work. **Phase 10 is the opposite case**, and it is: `feat/phase-10-body-store`,
opened 2026-08-18. *(This sentence read "will be" until then.)*

`docs/phase-8-method-and-guardrails` was the first branch to **carry a phase number on a `docs/`
prefix** — the form it settled: the prefix says what kind of work it is, `phase-N-` says it is a phase.
`method/IDM-001-git-branching.md` now states that as the rule, with Phase 7 as the old form and Phase 8
as the new one. `main` is ahead of `origin/main` and nothing has been pushed;
`docs/milestone-boundary-restructure` and `docs/phase-8-method-and-guardrails` both still exist locally.
