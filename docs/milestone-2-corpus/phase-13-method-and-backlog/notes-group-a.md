# Phase 13 — Group A, open the phase

*Tasks 1–3a. Written while working.*

## Task 1 — the branch, the folder, the plan, the in-flight row

**Done, `9976873`.** Worktree `phase-13-method-and-backlog/`, branch forked at `dec7c4a`.

**The in-flight row went in at task 1**, which is where `IDM-001` puts it rather than at the merge.
A dated line also went into `../../status.md`'s "Where we stopped", because that section would
otherwise have said Phase 12 was complete and nothing was in flight while a branch was open — the
same misread the in-flight rule exists to prevent, arriving in the section next door.

## Task 2 — the re-derivation, and it found the plan wrong twice

**`../../README.md` makes this a phase's first act, and four of six Milestone 1 phases found their
own plan wrong on contact. This one makes five.** Both defects were in the plan committed at
`9976873`, and both were figures the author had stated to the owner as fact before writing them
down — which is the specific failure `IDM-004`'s headline finding describes.

### Finding A1 — Phase 11's `for-the-owner.md` has 11 entries, not 12, and 3 `ASK`s, not 5

**VERIFIED.** `grep -c '^## '` returns **11**; by kind, **3 `ASK`, 5 `IDEA`, 3 `REGRET`**.

The plan's task 8 said *"five `ASK` entries … none of its twelve entries was ever answered."* Both
numbers were wrong: **twelve** was a miscount of eleven headings, and **five** was the `IDEA` count
read off the wrong row of the same output.

**What survives unchanged is the claim the finding was made for.** All three `ASK`s are the shape
settled row 13 now forbids — a question left in the file rather than asked out loud — and **none of
the eleven entries carries any mark of an answer**, checked by grepping the file for `Answered`,
`Resolved` and `closed`. The evidence for `IDM-010` is not weakened; only its arithmetic was wrong.

*Where it had already reached: the plan, and two messages to the owner. Not a commit message —
`9976873` states the claim without either number, which is luck rather than discipline.*

### Finding A2 — task 19's "two phase plans" is a relayed figure from 2026-08-26

**VERIFIED.** The backlog item this phase discharges says items are cited by quoting their bold
opening phrase, *"`status.md`'s 'What is next' does it, and so do two phase plans."* The plan
repeated that enumeration.

**It was written on 2026-08-26 and two phases have landed since.** Five existing phase plans
reference `backlog.md` at all. Task 19 now says to **sweep for the citing sites rather than
enumerate them**, which is the only form of that instruction that cannot go stale.

*This is the same defect as A1 in a different costume — a number relayed rather than re-derived. It
is also the third instance this repository has recorded of a count surviving into a document because
nobody re-ran it.*

### Finding A3 — the item this phase discharges describes a 545-line file that is now 855

**VERIFIED, and not fixed here.** *"Parked because it touches every item in a 545-line file"* —
`backlog.md` is **855** lines. The item's argument is strengthened rather than weakened by the
correction, so nothing about the plan changes.

**Left for task 13**, where every item is read anyway, rather than fixed now: editing one item's
prose ahead of the inventory pass would put a hand-edit inside the file the pass has to read
whole.

## Task 3a — recorded done, and one of its three files was never opened

> ***Corrected 2026-09-17.*** *This section's heading said "done, and it went further than
> renumbering". **It did less than renumbering.** Task 3a names three files; `status.md` and
> `prompt.md` were brought true and **`../implementation-plan.md` was never touched** — `git log`
> over the branch shows no commit against it — so it went on allocating **Phase 13** to the
> rate-limit headers while Phase 13 was the method-and-backlog phase. Retitled to **Phase 14** on
> 2026-09-17.*
>
> ***Neither jobs-done review run caught it.*** *Run B listed the file under "what I did not reach"
> and said its absence from the diffstat suggested the edit did not exist. **It was right, and
> nothing acted on it for thirteen days.** A task that names its own targets can be checked against
> them mechanically; nothing did.*

**The owner asked whether `status.md` and `prompt.md` held anything worth keeping, or only stale
items. The answer was: not only stale, and the difference had to be checked rather than assumed.**

### `status.md`'s "Where we stopped" was 154 lines against its own ~30-line limit

**Cut to the current session. Four dated entries removed — Phase 11's, Phase 12's two, and
`fix-slop-docs/opening-playbook-not-run-table`'s.**

**Removed, not moved, and that is the finding.** The section's own rule says that a section carrying
what outlives its session *"has become a document and gets its own file"*. **The opposite applied**:
every fact in those entries was checked for a durable home first, and every one had it.

| Entry | Where its facts already live |
|---|---|
| Phase 11, Phase 12 ×2 | their phase notes — `IDM-001`'s permanent record |
| `fix-slop-docs/opening-playbook-not-run-table` | **its row in `reference/branches.md`**, which carries the whole entry including *"each of those five"* beside a list of six |

**So a new file would have been a fifth home for facts that already had four**, which "One home per
fact" forbids. *Checked with six greps before a line was cut, not reasoned about.* The
`reference/branches.md` row is **richer than the prose it replaces**, which is the derived-index
argument `IDM-001` made when it refused a hand-typed table.

### "In-flight branches" had re-accumulated exactly what it was trimmed for

**Four paragraphs about merged branches**, in a section whose opening rule is that merged branches
are not listed. It was trimmed for this on 2026-08-25, when it had 22 lines of the same thing.
**Each of the four was verified to have a `reference/branches.md` row before being cut.**

**The second instance is what makes it worth recording.** The rule did not fail. What fails is
closing a branch out **by writing a sentence here instead of deleting one** — every paragraph cut
was a correct statement that the branch is merged and therefore not listed, which is a sentence that
should never have needed writing.

### Two things found by looking rather than by relaying

**Push state cannot be checked from this clone at all.** `origin` is configured and `git branch -r`
is **empty** — there are no remote-tracking refs. `status.md` has always said the 2026-08-28 "all
pushed" is reported rather than checked; what is new is that it is **unverifiable locally**, so a
session must ask rather than look. Recorded in `status.md`.

**`status.md`'s over-width prose lines are 15, and none is this branch's.** Verified by diffing the
set of over-100-column lines against the file at `HEAD` — zero of the 15 are new. *This answers the
question raised at the end of task 1 and closes it without a backlog item.*

### `prompt.md` was replaced whole

It described Phase 12's close and said nothing was in flight. That is what the file is *for* — it is
the one document allowed to go stale — but it had become actively misleading about what phase this
is. **One item it carried is discharged rather than carried forward:** `status.md`'s "Where we
stopped" is no longer past its limit.

---

## Task 3a — as the owner proposed it

**`../../prompt.md` is stale as of this branch opening** — it says nothing is in flight and that
Phase 13 is probably the rate-limit headers, and `../implementation-plan.md` still allocates 13 to
them. The owner proposed bringing the cross-file documents true **after Group A** rather than at the
close, and it is task 3a.

**Task 27 is not the same task.** That one records what the phase found; 3a stops a session picking
this branch up mid-phase from being misled about what the phase even is.

## Task 3 — the forward review, run on the owner's go-ahead

**Done. Its record is `notes-review-plan.md`**, beside this file rather than in it, which is what
Phase 12 settled when a second review made "the review" ambiguous.

**Eighteen distinct findings at 17% overlap.** `IDM-004`'s own forward figure is 18% and Phase 12's
backward figure is 11%, so **this is the second forward measurement and it lands within a point of
the first** — which is the outcome `IDM-004` says would *not* let it be rewritten: a run returning
60% would have meant one run is enough.

**Three of the author run's six findings were unique to it, and all three were about the record** —
a decision the owner made in interview that never reached the settled table, a task that produces no
commit, a status with no home. **Twelve of the cold run's fifteen were unique to it.** The split is
the one `IDM-004` predicts.

**The finding that paid for the run: task 5 would have made the next session re-decide an owner
row.** It named four questions as deliberately open in `review-plan-jobs-done.md`; that file leaves
**one**, and question 3 — whether the review runs before the merge — is settled row 1 there, decided
2026-09-02. Full account in `notes-review-plan.md`.

**Four findings became questions for the owner** rather than fixes, because each touches a settled
row. They were put in the session, not left in a file — settled row 13 applied to the phase that
wrote it.
