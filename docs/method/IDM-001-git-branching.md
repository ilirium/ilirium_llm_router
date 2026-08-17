# IDM-001 — Git branches, and where a branch is recorded

**In force 2026-08-17.** This is the one home for the branching rules. `CLAUDE.md` restates a small
part of it — see "The one accepted duplication" — and `../README.md` points here.

---

## The prefix says what kind of work it is

| Prefix | For |
|---|---|
| `feat/<slug>` | product work — anything that changes `src/` |
| `docs/<slug>` | documentation work |
| `fix/<slug>` | a defect |
| `chore/<slug>` | tooling, dependencies, formatter bumps |

**Any of them may carry a phase number:**

```
<prefix>/phase-N-<slug>
```

**Merge every branch with `--no-ff`, always.** A phase or feature boundary must stay visible in the
log, and a fast-forward erases it. Stated without exception on purpose: a rule that says "every phase
and feature branch" makes merging a `fix/` branch a judgement call at the moment somebody is trying to
finish, and the judgement is worth nothing. Phases 0 and 1 were fast-forwarded because they predate
the convention; `../milestone-1-core/README.md` says why they are left that way.

**`git merge` cannot read its message from stdin.** `-F -` works for `git commit` and fails for
`git merge`, so write the message to a temporary file. This is here because it is a branching fact and
it is also in `CLAUDE.md` because a session writes `git merge -F -` confidently and wrongly.

## The phase number is orthogonal to the prefix

**Settled 2026-08-17.** The prefix answers **which prefix**. `phase-N-` says **this is numbered work
with a plan and a record**. They are different questions, and `feat/phase-N-<slug>` is not an atomic
form — it is the common instance of a general one.

**The prefix rule answers *which prefix*, never *is this a phase*.** `EPD-004` decision 14 conflated
the two and its own 2026-08-16 revision says so; the correction is stated here rather than only in
`../README.md`'s phase template, because the person about to get it wrong is choosing a prefix.

Two worked examples, and they are the whole of why this rule exists:

| | Branch | Folder | Form |
|---|---|---|---|
| **Phase 7** | `docs/milestone-boundary-restructure` | `phase-7-docs-restructure/` | the **old** form — a phase on a branch whose name carries no number. The standing exception below |
| **Phase 8** | `docs/phase-8-method-and-guardrails` | `phase-8-method-and-guardrails/` | the **new** form — a `docs/` prefix *carrying* a phase number |

Phase 7 is the old form, not a violation of the new one. Phase 8 is the form to copy.

**One consequence worth stating, because it is the rule people reach for first:** a `docs/` branch can
no longer be described as *"documentation work belonging to no phase"*. It is documentation work,
full stop. EPDs and a milestone's opening are **examples** of `docs/` branches, not the definition of
one — the definition was written when every numbered phase was `feat/`.

## A phase's folder takes its branch's slug

**Moved here from `../README.md`'s "Naming and numbering" on 2026-08-17.** It was sitting under
numbering, which is half of how the two documents drifted apart: it is a rule about branches and it
was filed with the rule about filenames.

A phase folder is `phase-N-<slug>/` with the slug **identical to its branch's**. Accuracy loses to
navigability here — Milestone 1 kept `phase-5-config-and-timeouts/` over the more accurate
`credentials-and-timeout/` for exactly this reason, and the trade is only free if taken before the
folder exists.

**Check folders against branches in that direction only.** Every `*/phase-N-*` branch has a folder
with its slug — generalised on 2026-08-17 from `feat/phase-N-*`, which is what decision 15 wrote when
`feat/` was the only numbered prefix. **The converse is false in both directions:**
`feat/phase-0-skeleton` has no folder, and Phase 7's folder has no branch whose slug matches.

**Phase 7 is the standing exception**, for the reason decision 15 records: a folder name must carry the
phase number, the branch was named before there was any intention of numbering the work, and renaming
a pushed branch costs more than the agreement is worth.

## The plan opens the phase branch

**No separate planning branch.** Plan and execution share one branch and one merge commit, which is
what keeps one archive folder mapping to one branch. A separate planning branch would give a single
phase two merge commits.

This was measured rather than assumed: each Milestone 1 phase plan's creating commit is contained by
that phase's own branch and nothing earlier — `7f68d02` on `feat/phase-4-lmstudio-parity`, `4f7856a` on
`feat/phase-5-config-and-timeouts`, `8f4a46c` on `feat/phase-6-review-and-cleanup`.

**Planning that produces no code goes on a `docs/` branch.** `EPD-003` was born on
`docs/epd-index-and-corpus-proposal`; this document is on `docs/phase-8-method-and-guardrails`.

**Work belonging to a later phase never goes on an earlier phase's branch, even documentation.** Two
spec commits were moved off the Phase 1 branch for exactly this reason. The consequence is that a
branch may sit holding only an unapproved plan — which is the next section.

## A rejected plan is merged and marked, not deleted

**Reversed 2026-08-17.** `EPD-004` decision 14 ended *"if the plan is rejected the branch is deleted,
not renamed."* It is now: **the branch is merged `--no-ff` like any other, and the plan is marked
rejected in place.**

**The reversal restores consistency rather than adding a rule.** Two documents already said the
opposite of decision 14:

- `../epd/EPD-000-about-these-documents.md`'s status vocabulary: **withdrawn** — *"Superseded or shown
  wrong. Kept, with the reason, rather than deleted."*
- `../README.md`'s review phase: *"**Refusals are first-class outcomes.** Recording that a cut was
  considered and refused, with the measurement, is what stops the same cut being re-proposed every
  milestone by the next person reading the same surface signal."*

A deleted branch was the one place this project discarded a refusal. A rejected plan carries what was
proposed and why it was refused, which is precisely what stops it being proposed again.

**The risk is not the one it looks like, and it is designed against.** A rejected plan sitting in the
archive **reads exactly like an accepted-but-unexecuted plan** — which is this repository's signature
failure, four times over in Milestone 1's phase notes. So the rejection has to be legible *without
opening the file*:

| Where | What |
|---|---|
| The plan's first lines | A status line: **`REJECTED <date>. Not executed.`** — mirroring `EPD-000`'s vocabulary, which already solved this |
| The milestone's `implementation-plan.md` | A row naming the phase, the date, and **why it was refused** |

**The phase number is spent.** A rejected Phase 9 means the next phase is 10. Numbers are identities;
they are never reused or renumbered, and the attempt did happen at that point in the sequence. The cost
is named rather than waved away: the archive gains folders holding no executed work, and the status
lines are what make that legible instead of confusing.

**No branch rename, and no folder suffix.** Rejection is not knowable when the branch is created, so
marking the slug means renaming at rejection time — and decision 15 already established that renaming
a pushed branch costs more than slug agreement is worth. The status line and the milestone-plan row do
the same job and add no exception to the folder⇄branch rule.

## Where a branch is recorded

| | |
|---|---|
| `../status.md` | **In-flight branches only** — name, purpose, tree state, next action. Merged branches are not listed: git already holds that, and a hand-maintained list would drift |
| The phase note | **The permanent record** — branch, fork point, and merge commit |

**Write the merge commit in when the merge happens.** Four of Milestone 1's six phase notes said
"merge back with `--no-ff`" and never recorded what happened; only `phase-4-notes.md:7` carried the
hash. That is this repository's signature failure in miniature — a document recording intent and never
closed out — and `../backlog.md` still carries the repair as a review-phase item.

**A `Merge commit` row still reading "not yet merged" after the branch is gone is the defect, not the
placeholder.** Writing "not yet merged" while it is true is correct; leaving it there afterwards is
what four phase notes did.

## The one accepted duplication

`CLAUDE.md` keeps the prefix table, the `<prefix>/phase-N-<slug>` line, `--no-ff`, the
`git merge -F -` gotcha, and "the plan opens the phase branch". **That is a fact with two homes, which
is the thing this tier exists to stop.**

It is accepted because the auto-load admission test demands it. `CLAUDE.md` is the only file loaded
into every session, and each of those five is a thing a session acts on **confidently and wrongly**
with no reason to look anything up first — `git merge -F -` most of all. `EPD-004` decision 16 makes
exactly this argument for exactly this fact.

**Mitigated by naming the direction of truth, not by pretending there is one copy.** `CLAUDE.md`'s
block says it is restated from this file, that this file is canonical, and that a change goes here
first. Compare `CLAUDE.md`'s design-decisions index, which dodges the problem by listing titles only —
*"a one-line restatement would drift, a title cannot."* Here a title cannot carry the rule, so the
restatement is accepted with its risk labelled rather than denied.

## Provenance

- **`EPD-004` decision 14** — branch naming and where branches are recorded. Its 2026-08-16 revision
  separates *which prefix* from *is this a phase*; its prefix table, its `docs/`-belonging-to-no-phase
  wording and its deleted-branch rule are superseded by this document, with addenda dated 2026-08-17 in
  place.
- **`EPD-004` decision 15** — the folder⇄branch slug rule, Phase 7's standing exception, and the
  one-way check, generalised here from `feat/phase-N-*` to `*/phase-N-*`.
- **Replaces** `../README.md`'s "Branches" section whole, and the two slug paragraphs that were in its
  "Naming and numbering". Both are now pointers here.
- **Unified from two disagreeing homes.** `CLAUDE.md` and `../README.md` both claimed to state this
  convention and differed in seven places. The disagreements and how each was resolved are tabulated in
  `../milestone-2-corpus/phase-8-method-and-guardrails/plan.md`; this file is the outcome.
