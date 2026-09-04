# IDM-000 — What a method document is, and the index of them

**IDM stands for Ilirium Development Method.**

A method document states **how the work is done** — how a branch is named, how the harness is
configured, which tools are pinned and why, how a milestone is opened and closed. Not how the router
works: that is `../reference/`.

## An IDM is the opposite of an EPD in status

**Read this line before anything else in the tier.** `CLAUDE.md` says of EPDs:

> Nothing in an EPD is implemented unless it names the date it was accepted. **Do not build from one.**

**An IDM is the reverse. It is in force now, and you are expected to act on it.** An EPD asks a
question; an IDM answers one and the answer is already the practice.

That sentence exists because of a foreseeable accident: two three-letter numbered schemes sit adjacent
in `docs/`, they look alike, they are indexed alike, and a session that reads `IDM-001` with the reflex
it learned from `EPD-001` will treat a rule as a proposal and ignore it. The similarity of shape is
deliberate — `EPD-000` already solved indexing, numbering and status vocabularies, and reinventing them
would be waste — so the *difference* has to be stated loudly rather than inferred.

| | Asks or answers | What to do with it |
|---|---|---|
| `EPD-NNN` | asks a design question, and may pick nothing | do not build from it unless it names an acceptance date |
| `IDM-NNN` | answers a process question | follow it; if it is wrong, change it here first |

## What belongs here, and what does not

**The admission test: would this rule still be true if the subject of the project changed?** A rule
about branches, commits, tasks, permissions or tooling survives a change of subject. A fact about
LM Studio does not.

**No IDM contains a fact about the router.** That is not a stylistic preference — it is what makes the
tier a unit, and it is the whole of what "portable" means below.

Where the neighbouring tiers draw the line:

| | |
|---|---|
| `../README.md` | **where a document goes.** The filing manual |
| `method/` | **how the work is done.** These files |
| `../reference/` | what is true about the router |
| `../epd/` | what has not been decided |
| `CLAUDE.md` | the subset of the above that a session must hold in its head without looking anything up |

A rule may be **restated** in `CLAUDE.md` when a session would otherwise act confidently and wrongly.
That restatement is a second copy of a fact and is accepted only with the direction of truth written
into it: *this is restated from `IDM-NNN`, which is canonical; change it there first.*

**Two such restatements exist today** — `CLAUDE.md`'s "Git and branches", named by `IDM-001`, and its
Working agreement's fourth bullet, named by `IDM-007`. *(One until 2026-08-21.)* Each earns it on a
different reading of the same test, which is worth knowing before proposing a third:

| | Why the session cannot look it up first |
|---|---|
| `IDM-001` | It would **not discover the file**. A session merging a branch has no reason to open `../reference/branches.md`, and no rewrite of `IDM-001` reaches a session that never opens it |
| `IDM-007` | There is **no "first"**. The rule governs how a concern is written, so the moment it applies is the moment somebody is already writing |

**`IDM-008` was considered for restatement on 2026-08-21 and settled as a pointer**, and it is the
useful contrast: writing a phase plan is a deliberate, once-per-phase, look-it-up moment, which
`../README.md` says belongs in `docs/` rather than `CLAUDE.md`. `IDM-005` and `IDM-006` are pointers
for the same reason. **Neither shortness nor importance earns a restatement** — only the absence of a
moment at which the rule could have been looked up.

## Whose method it is

**Settled 2026-08-17: it is the owner's method, evidenced from this repository.** The rules are meant
to travel; every one of them was learned here, and none has been tested against a second subject.

Both halves of that sentence do work:

- Because it is **the owner's**, an IDM is written to be readable without knowing what the router is,
  and it takes no project-specific facts. That is the admission test above.
- Because it is **evidenced from this repository**, the reasoning in each document cites what happened
  here — a formatter that rewrote every file, an allowlist entry that repealed a written rule — rather
  than asserting a principle. A rule with its evidence attached can be argued with; a bare principle
  can only be obeyed or ignored.

**What this decides.** `EPD-004` decision 18 defers extracting a portable methodology until project #2,
on the ground that *a methodology extracted from n=1 is a guess about what generalises*. That deferral
is untouched. What this settles is what extraction will copy when it happens: **the whole of
`method/`, unfiltered.** Contrast `../README.md`, which decision 18 says is extracted by copying it
and *deleting the rows naming a backend*. This tier needs no such filter, because the admission test
keeps those rows out in the first place.

## Numbering

`IDM-NNN-kebab-slug.md`, allocated **in order written**, never reused and never renumbered. `IDM-000`
is this index. Numbers imply neither priority nor dependency.

**The number is what is cited; the slug is for grepping and may drift.** A slug that stops describing
its contents may be changed, and the number carries the identity across the rename. Write the rename
with `→`, which `../procedures/link-check.py` depends on.

This mirrors `EPD-000`'s scheme on purpose, and for the same reason the reference tier has *no*
numeric prefixes: reference documents are cited by name from `src/` docstrings, where a prefix would
mean inserting one file renumbers the rest and churns citations in code. Nothing in `src/` cites a
method document, so the identity is worth more here than the churn costs.

## Two zones, when the evidence is bulky

**Settled 2026-08-21. Any method document may split itself into two zones**, and one whose evidence
outweighs its rules is recommended to. `IDM-006` worked the shape out and `IDM-005` adopted it — both
are playbooks, but the option is not restricted to playbooks, and nothing here makes it a duty.

The form, so that the shape is recognisable across documents rather than reinvented per file:

- The rules first; then a line reading exactly **`End of procedure`**; then the evidence — one row per
  rule, saying what it cost and where the frozen record is.
- A **stop instruction in the header**, naming that line: *read to `End of procedure` and stop.*
- Markers in the rules pointing into the evidence table. They are **not sequential** — a marker stays
  with its rule when the rules renumber — and **nothing above the line may depend on them**, because
  the reader who obeys the stop instruction never sees them.

**What the split buys, and the hazard it carries.** It buys a document that can be acted on without
reading its argument, and argued with without re-deriving its rules. It costs a standing hazard, found
the first time it was used: **a caveat that qualifies a rule is invisible if it lives only in that
rule's evidence row.** `IDM-005`'s step 2 was exactly that — the one step with nothing behind it, and
its disclaimer sat below the line where a session following the stop instruction would never reach it.
It was folded into step 1 on 2026-08-21 rather than left standing with a hidden caveat. **A rule that
needs a caveat gets it above the line, or it stops being a rule.**

## Status

Every IDM opens with a status line: the status, and the date it came into force.

| Status | Meaning |
|---|---|
| **in force** | The current practice. Act on it |
| **superseded by IDM-NNN** | Replaced. Kept, with the successor named, because the reasoning is often still the best account of why the successor looks the way it does |
| **withdrawn** | Shown wrong, or the practice stopped. Kept, with the reason |

**A superseded or withdrawn document is never deleted.** `EPD-000` established this for proposals and
`../README.md` states the general form — *refusals are first-class outcomes; recording that something
was considered and refused is what stops it being re-proposed every milestone by the next person
reading the same surface signal.* A deleted method document is a rule that comes back.

## The objection this tier had to answer

**`EPD-004` decision 18 declined a `docs/method/` tier**, at `../epd/EPD-004-documentation-structure.md`,
and not on the n=1 ground that is easy to assume — that argument was aimed at extraction to project #2,
which is still parked. The tier was declined structurally:

> Declined: it splits the manual, and `docs/README.md`'s acceptance test — *file a new document
> correctly from this file alone* — would then span two files.

**The objection is answered rather than overridden, and the answer is why the tier is safe:** the two
files answer different questions, so the acceptance test never spans them.

- `../README.md` stays the **filing** manual. *Where does this document go?* Its acceptance test is
  about filing, and it survives intact **because its "Where does it go?" table has a `method/` row.**
- `method/` holds **rules about how the work is done**. *How do I name this branch?* Somebody filing a
  document never has to open one of these files to file it correctly.

**If that table row is ever removed, decision 18's objection becomes correct again.** Written down here
because the row looks like decoration and is load-bearing.

## The index

Each document adds its own row when it is written, rather than the index describing files that do not
exist yet.

| IDM | Title | In force | What it is about |
|---|---|---|---|
| **000** | About these documents | 2026-08-17 | This file: what a method document is, how they are numbered, and the index |
| **001** | [Git branches, and where a branch is recorded](IDM-001-git-branching.md) | 2026-08-17 | The four prefixes by kind of work, `phase-N-` as an orthogonal form any of them may take, `--no-ff` always, the folder⇄branch slug rule, what happens to a rejected plan, and **closing out status placeholders as part of the merge** — generalised from the `Merge commit` row after the narrow wording was followed and the defect happened anyway. **Amended 2026-08-21**: a branch carrying no phase number has no phase note, so its permanent record is its merge commit message |
| **002** | [Harness configuration: the permission allowlist](IDM-002-harness-configuration.md) | 2026-08-17 | The tracked/local split and its admission test, the exact-match `.env` deny and why it does not reopen `EPD-004` decision 19, and what an allowlist entry does to a rule nobody re-read |
| **003** | [Development tooling](IDM-003-development-tooling.md) | 2026-08-17 | The ruff pin, both halves, why `make lint` cannot catch a column-width change, and how to try a version. And `ty`: tried and refused, recorded rather than deleted |
| **004** | [Reviewing work that has not happened yet](IDM-004-reviewing-unexecuted-work.md) | 2026-08-18 | The **forward** review, and the line between it and `../README.md`'s closing one. Derive the charter before reviewing; run the author and a cold reader **in parallel** on different questions; six rules including read-only and *nothing found is a complete answer*. Written from one run that returned 22 findings at 18% overlap, and refuted a claim the author had already written into four documents |
| **005** | [Opening a milestone](IDM-005-opening-a-milestone.md) | 2026-08-20 | Seven steps mined from Milestone 1's opening: name the falsifiable central claim, the non-goals **and the experiment that would refute it**, **capture the real input before specifying anything**, spike, fork the expensive questions as EPDs, mark the spec measured / inferred / assumed, plan at decreasing resolution, open the folder and the branch. Two zones. Moved from `../README.md` with the steps unchanged and the shape not — and then **amended 2026-08-21**: the old step 2 was folded into step 1, because it was the one step of the eight with no evidence behind it |
| **006** | [Closing a milestone](IDM-006-closing-a-milestone.md) | 2026-08-20 | Nine steps: freeze, write the milestone README, harvest into `../reference/`, `lessons.md`, `measurements.md`, `../backlog.md`, reset `../status.md`, repoint and re-check, rewrite the playbook. **Two zones, and the line between them is load-bearing**: the nine steps, then `End of procedure`, then one evidence row per rule saying what it cost and where the frozen record is. To run a close, read to the line and stop. Moved from `../README.md` **and repaired** — the version written there was the narrative of the restructure that produced it, with five of the seven decided steps missing |
| **007** | [Raising a concern where it will be read](IDM-007-raising-a-concern.md) | 2026-08-21 | Placement, plainness, answerability — a concern goes in its own sentence where the reader arrives; if something is wrong, say so rather than working around it; a question carries its options. **Placement is the rule, not the polish**, and the evidence is three prior instances *about documents* — `IDM-005`'s step 2 caveat below the stop line, and `../status.md`'s two records of prose that undercounts going stale invisibly. Restated in `CLAUDE.md`'s Working agreement |
| **008** | [The register](IDM-008-the-register.md) | 2026-08-21 | One reachable section in the plan holding every name and number the phase introduces, `❓` on anything named and never valued, checked against the code by the phase's closing task. **Not a tidying exercise**: on its one run it found eight unvalued names, contradicted a figure ~70× out that had survived two reviews, exposed a live name collision, and produced a finding two forward-review passes had read past — because a constant and a config key only look wrong in adjacent rows. `CLAUDE.md` points at it and does not restate it |
| **009** | [Reviewing work that has happened](IDM-009-reviewing-executed-work.md) | 2026-09-04 | `IDM-004`'s sibling, for **executed** work, and the line between three review protocols. What it adds: the review may **run** the thing, every instrument the phase leaned on gets a **vacuity question**, the settled table is walked row by row against what shipped, and findings rank by **blast radius** rather than by cost-to-find-later. Written from one run that returned 18 findings at **11% overlap** — and whose headline was a count in the one file loaded into every session, in the phase chartered to fix that count, which never opened it. Answers three questions `IDM-004` never had to: who "the author" is across sessions, when the subject commit is named, and what one measurement is worth |
| **010** | [`for-the-owner.md`: the phase's digest for a person](IDM-010-writing-for-the-owner.md) | 2026-09-04 | One per phase, written **to a person** rather than to a session — the audience split is the whole of it, and the notes stay long on purpose. Four kinds `ASK` / `IDEA` / `REGRET` / `ERRAND`, numbered in order of appearance with an importance, **not** ordered by it. **Anything needing a decision is asked out loud, never parked here**; nothing formally closes an entry, so an unanswered `ASK` is not a defect; and there is **no closing trim**, because a per-phase file cannot accumulate. Written from one instance whose three `ASK`s a review showed were **not** rule-breaking — two were errands, which is why `ERRAND` exists |
