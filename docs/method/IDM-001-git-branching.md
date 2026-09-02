# IDM-001 — Git branches, and where a branch is recorded

**In force 2026-08-17, amended twice on 2026-08-21 and once on 2026-08-26** — "Where a branch is
recorded" gained its third row, and then a fourth: `../reference/branches.md`, which reverses this
document's refusal of a list of merged branches on the ground that made the refusal right. The
2026-08-26 amendment adds "Worktrees are the standing practice, and one branch is not work". This is the one home for the branching
rules. `CLAUDE.md` restates a small part of it — see "The one
accepted duplication" — and `../README.md` points here.

---

## The prefix says what kind of work it is

| Prefix | For |
|---|---|
| `feat/<slug>` | product work — anything that changes `src/` |
| `docs/<slug>` | documentation work |
| `fix/<slug>` | a defect |
| `chore/<slug>` | tooling, dependencies, formatter bumps |
| `fix-slop-docs/<slug>` | a documentation defect whose cause is LLM slop |
| `fix-slop-code/<slug>` | the same, in `src/` |

**The last two name a *cause* rather than a kind of artefact, and that breaks this section's own
heading on purpose.** *Added 2026-09-02 on the owner's decision.* Everything above answers *what
kind of work is this*; these two answer *what put the defect there* — a sentence that summarises a
table it has stopped matching, a number nobody re-derived, a paragraph plausible enough that two
reviews read past it. By the artefact axis they are ordinary `docs/` and `fix/` work, **and that is
exactly what makes the mechanic invisible**: a `docs/<slug>` branch repairing model-written drift is
indistinguishable in the log from one adding a section.

**What the split buys is a count nobody has to keep.** `../reference/branches.md` is generated from
git, so how often this bites — and whether it bites `docs/` harder than `src/`, which is the
interesting question — becomes a property of the branch log rather than a tally somebody maintains.
That is the same argument that admitted a derived index over the hand-maintained list this document
refused, and it is why **neither row states whether it has been used yet**: a sentence saying so
would be a hand-maintained fact about a question the index already answers, and it would go stale
silently.

**Both take a phase number like any other prefix** — the rule below is not narrowed for them, though
numbered slop work would be unusual.

**Any of them may carry a phase number:**

```
<prefix>/phase-N-<slug>
```

**Merge every branch with `--no-ff`, always.** A phase or feature boundary must stay visible in the
log, and a fast-forward erases it. Stated without exception on purpose: a rule that says "every phase
and feature branch" makes merging a `fix/` branch a judgement call at the moment somebody is trying to
finish, and the judgement is worth nothing. Phases 0 and 1 were fast-forwarded because they predate
the convention; `../milestone-1-core/README.md` says why they are left that way.

**Three branches predate it, not two.** `docs/add-claude-md` is the third and it belongs to no phase,
which is why every sentence in this repository about fast-forwarding counts two — each is counting
*phases*. `../reference/branches.md` carries all three; the section below on that file explains how a
branch stayed unrecorded for twenty-five days without any rule being broken.

**`git merge` cannot read its message from stdin.** `-F -` works for `git commit` and fails for
`git merge`, so write the message to a temporary file. This is here because it is a branching fact and
it is also in `CLAUDE.md` because a session writes `git merge -F -` confidently and wrongly.

## Worktrees are the standing practice, and one branch is not work

**Amended 2026-08-26.** Owner's decision of 2026-08-24, recorded here because it changes what a branch
*is* on this machine: a branch is now usually **a directory you can stand in**, not a thing you switch
to.

```
~/Projects/local/ilirium_llm_router/
    .bare/                      the repository — no working tree
    main/                       worktree, branch `main`
    to-run-server/              worktree, branch `temp/to-run-server`
    <slug>/                     worktree, branch `<prefix>/<slug>` — one per open branch
```

**The first three rows are standing; the fourth is whatever is open, and there may be none.**
*Amended 2026-09-02.* The diagram named `phase-11-corpus-tools/` as a concrete fourth row until
then, and that worktree was removed once the phase merged — **a layout diagram naming a particular
transient tree goes stale every time a branch lands**, which is the one thing this document already
knows about hand-maintained lists. `git worktree list` is the answer to what exists right now;
`../status.md` holds it for the current session.

**One branch is checked out in exactly one worktree, and git enforces that.** It refuses to check out
a branch that another worktree already holds. **That refusal is the whole reason `temp/to-run-server`
exists** — the router has to be *run* against a stable tree while a phase branch holds the editable
one, and "check `main` out twice" is not available. So a branch was created to be pinned, and it is
the only branch in this repository that is not work.

**`temp/` is not a fifth row of the table above, and must not be added to it.** That table answers
*what kind of work this is*; `temp/to-run-server` is not work. It carries **no commits of its own**,
it **never merges**, and its slug names a *purpose for a directory* rather than a change.

| | A work branch | `temp/to-run-server` |
|---|---|---|
| commits of its own | yes | **none, ever** |
| ends by | merging `--no-ff` | **it does not end** |
| fork point | recorded | **lost, and that is acceptable** |
| a phase folder | maybe | **never** |

**Its tip sits on the trunk by construction, so `../procedures/branch-index.py` tables it as *merged*
rather than reporting it in flight.** That is not a defect in the script and it is not to be fixed
there: the script asks git a factual question and git's answer is right. **It is why a branch that is
not work still needs a row** — the row's last column is the only place that can say so, which is
precisely the argument in "A derived index is not the hand-maintained list this document refused". The
row exists; do not remove it as noise.

### What the layout changes, and it is more than convenience

- **`logs/` is per-worktree.** A router run in `to-run-server/` writes to `to-run-server/logs/`. There
  is no shared one, and a document naming "the corpus" has to say which tree's.
- **A session started in `main` sees none of an open phase** — not its plan, not its notes, not its
  code. Handoffs must name the worktree, and `../prompt.md` does.
- **Tracked settings are read from the worktree the session started in, once, at session start.**
  Measured 2026-08-25. So a permission added on a phase branch is live **in that worktree after a
  restart** and reaches the other two **only at the merge**. → `IDM-002-harness-configuration.md`.

  ***The competing explanation is dead for the tracked half, and it is named so it is not
  re-proposed.*** It was believed for a day that tracked settings resolve *through* a worktree to the
  main checkout, which would have made a permission inert until it **merged**. They do not. Settings
  are **session-cached**: inert until the session **restarts**. The two predictions differ by days and
  by what you would do about it, and only measurement separated them.

  **The *local* half is a separate question, and the answer here is not the documented one.** Anthropic
  documents that an auto-saved approval lands in `.claude/settings.local.json` *"at the root of the git
  repository, resolved through worktrees to the main checkout"*, since v2.1.211. **On this machine, at
  v2.1.231, it does not**: all three worktrees hold their own `settings.local.json` with **different
  contents**, and this branch's was written on 2026-08-26 while `main`'s had not changed since
  2026-08-24. *The likely reason — **unverified, and stated as a hypothesis** — is that **a bare clone
  has no main checkout to resolve to**, so the fallback is the worktree. The check that would settle
  it: grant one approval here and see which file grows.* → `IDM-002-harness-configuration.md`.

*Why this is in `IDM-001` and not only in `../status.md`: the layout outlives the phase that adopted
it, and the `temp/` rule is a branching rule. `status.md` holds which worktrees exist right now.*

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
| `../status.md` | **In-flight branches only** — name, purpose, tree state, next action. **This row covers every branch**, phase-numbered or not. Merged branches leave it when they merge; the row below is where they go |
| `../reference/branches.md` | **Every merged branch, one row, newest first** — opened date, fork point, merge date, merge commit, milestone, phase, and one line on what it was for. **Generated from git** by `../procedures/branch-index.py`; only the last column is written by a person. *Fourth row, added 2026-08-21* |
| The phase note | **The permanent record of a phase** — branch, fork point, and merge commit |
| The **merge commit message** | **The permanent record of a branch carrying no phase number.** There is no phase note to put it in, and inventing one is not the answer |

**The four are not four copies.** `status.md` holds *live state*; `branches.md` holds *the index*; the
phase note holds *the work*; the merge message holds *the provenance of a branch that has no phase
note*. Only the second is new, and it is the only one that is generated.

**A branch with no phase number is recorded by its merge, and that is enough.** *Third row added
2026-08-21.* Git already holds the branch name, the fork point and the merge commit; what git cannot
hold is **why the branch existed and what it decided**, and that is what the merge message is for.
Write it as though the phase note it does not have were being written into it.

**Do not give it a phase number to solve this.** A phase number is an identity that is spent when it is
allocated — the rejected-plan rule above turns on exactly that — and manufacturing one so a branch has
somewhere to file its fork point buys a record at the price of a hole in the phase sequence.

**Two records, not one, and they do not compete.** The record of *the branch* is its merge. The record
of *the work* is the documents the branch changed, which are canonical wherever they live. A `docs/`
branch that writes a rule has already recorded the rule; what was missing was only the provenance of
the branch that carried it.

*The episode.* `docs/idm-and-claude-md`, 2026-08-21, forked from `feat/phase-10-body-store` rather than
from `main` so it could see `IDM-004`. It produced `IDM-005` and `IDM-006` and had **nowhere to record
its own fork point and merge commit** — it is documentation work belonging to no phase, which the
"orthogonal" rule above explicitly allows and this table had not caught up with. **The rule was
followed and the record still went missing**, which is the same shape as the `Merge commit` defect the
next paragraph was generalised from. It was found by a session asking where the record went, not by
any check.

*One thing that branch did which this rule does not license.* It was never listed in `../status.md`
while in flight, on the owner's instruction, because another session was concurrently rewriting the
only other row of that table. **That was a deliberate suspension for one branch, recorded so it is not
read as an exemption.** Row 1 above covers every branch, and a concurrent edit is a merge problem
rather than a reason not to record state.

**Write the merge commit in when the merge happens.** Four of Milestone 1's six phase notes said
"merge back with `--no-ff`" and never recorded what happened; only `phase-4-notes.md:7` carried the
hash. That is this repository's signature failure in miniature — a document recording intent and never
closed out — and `../backlog.md` still carries the repair as a review-phase item.

**A `Merge commit` row still reading "not yet merged" after the branch is gone is the defect, not the
placeholder.** Writing "not yet merged" while it is true is correct; leaving it there afterwards is
what four phase notes did.

## A derived index is not the hand-maintained list this document refused

**Added 2026-08-21.** Until this amendment, row 1 of the table above ended: *"Merged branches are not
listed: git already holds that, and a hand-maintained list would drift."* `../reference/branches.md`
is a list of merged branches, so this is a reversal and is written as one.

**The refusal was right, and it is not being overturned — it is being satisfied.** Both halves of it
survive intact:

| The objection | What answers it |
|---|---|
| *"git already holds that"* | It does, and the file is **read out of git** every time it is regenerated. Nothing is transcribed |
| *"a hand-maintained list would drift"* | It would, and this project has that failure four times over in Milestone 1's phase notes. A **generated** list cannot: `branch-index.py --check` exits 1 when the table no longer matches git |

**The one column git cannot hold is the one worth having.** A branch's name, dates and hashes are
already addressable — `git log --merges` gets them in a line. What no command answers is *what the
branch was for*, and that is the column a person writes and the reason the file exists at all. So the
amended rule is narrow: **an index of merged branches is admitted when its factual columns are
derived and its interpretive column is not.**

**What is still refused, unchanged.** A second hand-typed table of merge hashes anywhere. If the next
one cannot be generated, the objection above applies to it in full and it does not get made.

### Regenerating is the last step of a merge, and it cannot be part of the merge commit

**This rule is an instance of the next section, and is written here rather than there on purpose** —
the next section's own lesson is that *a rule stated as an instance gets obeyed as an instance*, so
naming this one where a person is deciding how to merge is the correction that section asks for.

**The order is fixed and it is not the obvious one:**

```
git merge --no-ff <branch> -F <message-file>
python3 docs/procedures/branch-index.py --write
git commit -m "regenerated: the branch index for <branch>"
```

**The regenerated table cannot go inside the merge commit, and this is a property of the thing rather
than a preference.** The new row records the merge hash. Writing it before the merge is impossible —
the hash does not exist. Amending the merge to include it changes the hash, which falsifies the row
that was just written; run it twice and it never converges. **So a merge that lands a branch is two
commits on the trunk, and the second is not optional tidying.**

*This was got wrong in the first draft of this section, on 2026-08-21, which said "commit the result
with the merge" three sentences after correctly observing that the row cannot be written before the
merge commit exists. Recorded rather than silently fixed: the two halves of the same paragraph
contradicted each other and it read fine.*

**The failure it is designed against is silence.** A missing row is invisible — it is the "prose that
undercounts" defect `../status.md` records twice about itself, in a new place. `--check` is what makes
it loud, and it is worth running even when you are sure. **The second commit is where the sweep in the
next section belongs too**, since by then every merge hash the phase's documents need is finally
knowable.

### Two things the index found on the day it was written, which is its case

**There were three fast-forwarded branches and every document said two.** `../status.md`,
`../milestone-1-core/README.md` and this file all say *"Phases 0 and 1 were fast-forwarded"* — each
correct, because each is talking about phases. `docs/add-claude-md` is the third: five commits on
2026-07-27 carrying the README, `CLAUDE.md`, the design decisions and the first implementation plan.
**It is the repository's first branch and it appeared in no document for twenty-five days.** It has no
phase note, it predates the milestone scheme, and it was fast-forwarded, so before the third row above
existed there was no place it could have been recorded. It was found by enumerating refs, which is
the thing a person does not do and a script does every run.

**Eight of nineteen branches carry no phase number.** Better than two in five of this repository's
merged work sits outside the phase sequence — which is the "orthogonal" rule above, measured. A
records scheme built only on phase notes would be missing eight rows, and that is the size of the gap
the third and fourth rows were added to close.

*It was seven of eighteen when this section was written on 2026-08-21, and became eight of nineteen
when that same branch merged a few hours later — a `docs/` branch with no phase number, which is the
ninth of its kind. **The ratio is not drifting toward the phase sequence; it is drifting away from
it.** Re-derive from the table rather than quoting this sentence.*

## Closing out a status placeholder is part of the merge

**Generalised 2026-08-17, after the rule above was followed and the defect happened anyway — twice in
one phase.**

**The rule is not about the `Merge commit` row. It is about any statement of unfinished state.** A
placeholder is correct while it is true and becomes a lie the moment the state changes, wherever it
sits and whatever form it takes:

| Form | Seen as |
|---|---|
| A table row | `Merge commit \| not yet merged` |
| **A bare table cell, with no marker punctuation** | `\| *(none yet)* \| Groups D, E, F \| not started \|` |
| A section marker | `### Group C — the gate *(not started)*` |
| A count in prose | *"Fifteen of sixteen tasks done; only the close-out and merge remain"* |
| A status line | *"Only tasks 1–4 have been executed"* |
| A claim of absence | *"the tracked half is **not yet built**"* |

**Why the narrow wording was not enough, which is the part worth keeping.** Phase 9 read this document
during the phase, followed it, and committed a closeout titled *"closed out: phase 9's merge hash, in
the three places that said otherwise"* — which filled in three `Merge commit` rows and **left the prose
four lines above one of them saying the work was unfinished.** The owner found it. The same session
then left `plan.md`'s group markers reading `*(not started)*` after all four groups had run; the owner
found that too.

**Neither miss came from not knowing the rule. Both came from the rule naming a *row*, so the check
was applied to rows.** A rule stated as an instance gets obeyed as an instance.

***It happened a third time at Phase 11's merge, 2026-08-28, and the grep below is why it is now
wider.*** The sweep was **not run before the merge message**, which this section says to do. The owner
then found a row in `notes.md`'s group index reading `| *(none yet)* | Groups D, E, F | not started |`
— **directly beneath two rows naming files for two of those three groups**, all marked complete. The
grep as written **could not have caught it**: the target had no parentheses, and the pattern required
them. Running the widened form afterwards found **three more** in Phase 11's own documents, including
a `Merge commit | not yet merged` row and a `*(in flight)*` section marker in the milestone plan.

**And one of the four was invisible to any grep**: a table cell reading *"evidence pending Phase 11's
Task 7"*, three days after that task ran. **A stale statement need not contain a marker word.** The
sweep narrows the problem; it does not close it, and the only thing that catches the rest is reading
the phase's own documents at the merge.

**So: closing out placeholders is part of the merge, not tidying afterwards.** Before writing the merge
message, sweep the phase's own documents — the plan, the note, `../status.md`, and the milestone plan —
for every form above.

The grep, with a warning attached:

```
grep -rniE "\(?(not started|in progress|none yet)\)?|\*\(in flight\)\*|not yet (merged|done|run|written|built|started|executed)" docs
```

**Widen it rather than trust it.** The first sweep run against this defect used `is not started` and
matched nothing, because the target was written `*(not started)*` — **a grep narrow enough to miss its
own target is worse than no grep**, since it returns clean and reads as proof. Expect hits that are
statements *of* this rule and Phase 8's plan describing a condition it then fixed; both are correct.

### What is **not** closed out, and the line between them

This licenses nothing in the archive beyond status. The distinction is sharp and it decides every case:

| | Edit it? | Because |
|---|---|---|
| A **status placeholder** — the document's own execution state | **Yes, at the merge** | It describes *this document's* progress, which is a fact about the present. Left stale it says work is outstanding when it is done |
| A **claim** — what was believed about the world | **No, ever** | `../README.md`: corrections go to `reference/`, not into archived prose |

Phase 9's `plan.md` is the worked example of both in one file. Its group markers were closed out; its
settled-decisions table still says `EPD-003` *"is now partly accepted"*, which was true when written
and is not now — **and was deliberately left**, with a header added saying the body records what was
believed before the work ran. **Closing out a marker is bookkeeping; rewriting a claim is falsifying
the record.**

## The one accepted duplication

`CLAUDE.md` keeps the prefix table, the `<prefix>/phase-N-<slug>` line, `--no-ff`, the
`git merge -F -` gotcha, "the plan opens the phase branch", and — **since 2026-08-21** — *regenerate
the branch index before writing the merge message*. **That is a fact with two homes, which
is the thing this tier exists to stop.**

*"Each of those five" read five until 2026-09-02, having not been counted again when the sixth was
admitted on 2026-08-21 — in the paragraph directly below a list of six and above a heading beginning
"The sixth was admitted". A count in prose beside the list it counts, going stale where the list
could not: the same shape as the two corrections this branch carries.*

*The prefix table grew two rows on 2026-09-02, and its restatement carries a one-sentence gloss —
that `fix-slop-docs/` and `fix-slop-code/` name a cause rather than a kind of work. **Counted as
part of the table rather than as a seventh fact**, because the row is unusable without it: a session
that reads the prefix and not the reason files the next one under `docs/`, which is the outcome the
split exists to prevent.*

It is accepted because the auto-load admission test demands it. `CLAUDE.md` is the only file loaded
into every session, and each of those six is a thing a session acts on **confidently and wrongly**
with no reason to look anything up first — `git merge -F -` most of all. `EPD-004` decision 16 makes
exactly this argument for exactly this fact.

**Mitigated by naming the direction of truth, not by pretending there is one copy.** `CLAUDE.md`'s
block says it is restated from this file, that this file is canonical, and that a change goes here
first. Compare `CLAUDE.md`'s design-decisions index, which dodges the problem by listing titles only —
*"a one-line restatement would drift, a title cannot."* Here a title cannot carry the rule, so the
restatement is accepted with its risk labelled rather than denied.

**The sixth was admitted on the argument that refused a different sixth four days earlier, and the
two are worth reading together.** The paragraph below refuses "closing out a status placeholder"
partly on the ground that six restated facts is too many. Regenerating the index was admitted anyway,
because the two fail differently and the admission test is about *how* a session gets it wrong:

| | How a session gets it wrong | Where the repair belongs |
|---|---|---|
| Closing out a placeholder | It **has read the rule** — Phase 9 read this document during the phase — and applied it to the wrong scope | **Scope.** Fixed above by restating the rule about any statement of unfinished state |
| Regenerating the index | It **does not know the file exists.** Nothing a merging session opens would name `../reference/branches.md`, and a generated file that is never regenerated is silently wrong | **Location.** No amount of rewriting *this* document reaches a session that never opens it |

**The second is the case `CLAUDE.md` is for and the first is not**, which is why the count argument
does not settle it. The restatement is one sentence and a command; a command cannot drift in meaning
the way a rule can, which is the same defence `../README.md`'s design-decisions index uses when it
lists titles only.

**"Closing out a status placeholder" was considered for `CLAUDE.md` on 2026-08-17 and refused.**
Recorded because the argument for adding it looks strong and is wrong. `../README.md`'s admission
test is whether a session would act *confidently and wrongly* **without being told** — and Phase 9
failed this rule twice having **already read this document during the phase**. It did not fail from
ignorance; it failed because the rule was scoped to a row. **The repair is scope, not location**,
and it has been made above. Copying it into `CLAUDE.md` would grow the accepted duplication to six
facts to fix a defect that a sixth copy would not have prevented. *(Six was the count on that date.
The branch-index fact was admitted four days later, so the same copy would make seven today — the
argument is unaffected and the arithmetic is left as it was made.)* The existing pointer already
names the trigger — *read it before recording where a branch went* — and that is the moment this
rule applies.

## Provenance

- **`EPD-004` decision 14** — branch naming and where branches are recorded. Its 2026-08-16 revision
  separates *which prefix* from *is this a phase*; its prefix table, its `docs/`-belonging-to-no-phase
  wording and its deleted-branch rule are superseded by this document, with addenda dated 2026-08-17 in
  place.
- **`EPD-004` decision 15** — the folder⇄branch slug rule, Phase 7's standing exception, and the
  one-way check, generalised here from `feat/phase-N-*` to `*/phase-N-*`.
- **Replaces** `../README.md`'s "Branches" section whole, and the two slug paragraphs that were in its
  "Naming and numbering". Both are now pointers here.
- **Amended 2026-08-21 on `docs/branch-index`**, which added the fourth row and the section arguing
  it. The refusal it reverses was this document's own, written 2026-08-17; the wording that was
  dropped from row 1 is quoted in full in that section rather than deleted, since the objection it
  made is the standard the new file has to keep meeting.
- **Unified from two disagreeing homes.** `CLAUDE.md` and `../README.md` both claimed to state this
  convention and differed in seven places. The disagreements and how each was resolved are tabulated in
  `../milestone-2-corpus/phase-8-method-and-guardrails/plan.md`; this file is the outcome.
