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

## Task 3a — added by the owner during Group A

**`../../prompt.md` is stale as of this branch opening** — it says nothing is in flight and that
Phase 13 is probably the rate-limit headers, and `../implementation-plan.md` still allocates 13 to
them. The owner proposed bringing the cross-file documents true **after Group A** rather than at the
close, and it is task 3a.

**Task 27 is not the same task.** That one records what the phase found; 3a stops a session picking
this branch up mid-phase from being misled about what the phase even is.

## Task 3 — not run

**The forward review under `IDM-004` needs the owner's go-ahead**, because its cold run is a
fresh-context agent. Raised and not yet answered. **The plan is now finished enough to be wrong,
which is `IDM-004`'s own test for when to run one** — the re-derivation above is exactly the round
of revision after which nobody holds the whole document.
