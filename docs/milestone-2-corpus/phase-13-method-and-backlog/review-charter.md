# Phase 13 — charter for the forward review of the plan

**Written 2026-09-04, before either run.** Per `../../method/IDM-004-reviewing-unexecuted-work.md`,
whose iteration 1 is that **the charter decides what the review finds** — a reviewer told "review
this" verifies what is easy to verify and returns a tidy list that misses the thing that matters.
**This file is handed to the cold reader verbatim.**

**This is the forward review**, against a plan nobody has acted on. It keeps the plain name
`review-charter.md`, which Phase 10 settled and `IDM-004` cites. *If this phase later reviews its
own finished work — task 21 — that is a different charter with a different name.*

---

## What is under review

**`plan.md` in this folder, at commit `6345eb8`**, on branch `docs/phase-13-method-and-backlog`,
forked from `main` at `dec7c4a`. 282 lines.

**Tasks 1 and 2 have run. Everything from task 3a to task 28 has not.** The review is of the
unexecuted remainder, its settled table, and its register.

Also in scope, as **context that may contradict the plan**: `notes.md` and `notes-group-a.md` in
this folder. A claim in either that the plan contradicts is a finding.

### Explicitly out of scope

- **How any of the nineteen settled rows was reached.** They are the owner's decisions, taken across
  four rounds of interview on 2026-09-03 and 2026-09-04. **Rule 5 below: a settled decision may be
  questioned, never filed as a defect.**
- **Phases 1–12 as executed.** If this plan *mis-describes* them, that is a finding; they are not.
- **This charter.** A review that reviews its own instructions is circular.
- **Anything requiring the machine.** Do not install anything, start a server, or run the router.
- **Whether the four deliverables are the right work.** The owner set them. The question is whether
  the plan can be executed and whether what it claims is true.

---

## Two runs, two questions

| Run | Question |
|---|---|
| **Author** — the session that wrote the plan | *Is this consistent with what was decided, and is what it claims true?* |
| **Cold reader** — fresh context | ***Could you execute this plan from the document alone? Name every place you had to guess.*** |

**The cold question is a fitness test, not politeness.** Where sessions are cleared deliberately,
**the next person to execute this document is a cold reader** — so a plan legible only to its author
is already broken for its purpose. The guesses are the findings.

---

## What a finding looks like in this plan

- **A task that cannot be executed as written** — it names no file, or names a decision it does not
  make, or depends on something an earlier task does not produce.
- **A task whose ordering is wrong.** Task N needs something task N+3 creates.
- **A claim the source refutes.** The plan says one thing; `IDM-001`, `backlog.md`, `IDM-000`,
  `docs/README.md` or a phase folder says another. **Read the artefact, not the plan's account of
  it** — this plan has already been wrong twice about a file it cites, and both were caught by
  reading the file.
- **A register row that is wrong, missing, or unvalued without a `❓`.** `IDM-008` makes the register
  the authority for values. **A name the plan introduces and the register does not list is a
  finding.**
- **A settled row the plan does not honour**, or two settled rows that contradict each other.
- **A gap the plan does not know it has** — a decision the work needs that no task makes and no
  settled row settles.
- **A leftover.** Text true at an earlier draft and not true at `6345eb8`.

**Rank every finding by what it costs to be wrong** — discovered now, against discovered after task
N. That is `IDM-004` rule 6 and it is the only ranking that survives disagreement about severity.

---

## The claims that must be re-verified by reading the source

**Named individually, never as a category.** Each was checked once by whoever wrote it, which is the
weakest verification available.

1. **Phase 11's `for-the-owner.md` has 11 entries — 3 `ASK`, 5 `IDEA`, 3 `REGRET` — and none of the
   eleven is marked answered.** `../phase-11-corpus-tools/for-the-owner.md`. *These numbers were
   wrong in an earlier draft; the correction is what needs checking now.*
2. **Phase 12's folder contains no `for-the-owner.md`.**
3. **`IDM-001` currently says filing a backlog item IS how a phase declines scope**, and says an
   item never opens a branch. Settled row 9 amends the first and keeps the second — check task 11
   describes what is actually there.
4. **`backlog.md`'s preamble says an item is deleted when done.** Settled row 1 replaces it.
5. **`backlog.md` is 855 lines, and its items have no machine-detectable boundary** — items open
   with a bold paragraph and bold *continuations* inside an item look identical. This is the
   argument for task 13 being a judgement pass and for the task 14 checkpoint.
6. **The five statuses cover every state the file contains.** Find the partly-discharged item and
   the refusal that was later overturned; check `superseded` is not a status nothing needs.
7. **`backlog.md` has eight sections**, which is where the eight category tokens come from.
8. **`IDM-008` is the highest existing IDM**, and `IDM-000` states the numbering rule the three new
   ones follow.
9. **`branch-index.py` has `--write` and `--check` and exits 0/1** — the shape task 17 copies.
10. **`IDM-004` requires a charter, two parallel runs, read-only, and `VERIFIED`/`REPORTED`** —
    check task 3 and this document match it.
11. **`IDM-008` requires one reachable register section and a numbered closing task** — check the
    plan's register and task 25 match it.
12. **`../implementation-plan.md` allocates Phase 13 to the rate-limit headers**, and this
    milestone's non-goal names *"changing `calls.csv`, not its rotation, not its columns"*. Task 26
    renumbers the first; the plan claims the collision is untouched.
13. **`../../README.md`'s archive rule is "paths yes, claims no"**, cited by settled row 14.
14. **`../phase-12-installer-and-readme/review-plan-jobs-done.md` leaves exactly four questions
    open**, and task 5's list of four is that list. *If it leaves a fifth, that is a finding.*
15. **`link-check.py` resolves a repo-root-relative path**, which the register relies on.

---

## Known false positives — do not spend findings on these

- **The plan cites files it will create.** `IDM-009`, `IDM-010`, `IDM-011`, `backlog-done.md`,
  `backlog-index.py`, `review-charter-jobs-done.md`, `notes-review-jobs-done.md`,
  `for-the-owner.md`, `evidence/register-check.py`. `link-check.py` reports them broken and that is
  correct behaviour, recorded in `../../backlog.md`.
- **`link-check.py`'s count is a property of the worktree**, not of the repository. Do not compare a
  run here against a figure taken elsewhere.
- **`❓` appears in prose describing the marker** as well as in the two rows that carry it. Two rows
  is the true count. The same false positive is recorded for `IDM-001`'s placeholder sweep.
- **Table rows longer than 100 characters are correct.** The 100-column rule is for prose.
- **`logs/` is absent from this worktree and that is correct** — it is per-worktree and gitignored.
- **There is no `.venv` here**, so `uv run` does not work in this tree. Not a defect.
- **Task numbers jump 3 → 3a → 4.** Insertion by letter is the rule, not a mistake.

---

## The rules — copied in, not cited

**1 · Read-only.** The review returns a work list and changes nothing — no file, no tree, no
machine. **Do not edit, create or delete anything.** If you run any command, read `git status`
afterwards and report what it said. An interrupted sweep once left a module comment-stripped in this
repository with the suite passing 427/427.

**2 · Every finding is labelled `VERIFIED` or `REPORTED`.** VERIFIED means you opened the file and
confirmed it. REPORTED means suspected and not confirmed. **A review that does not label cannot be
triaged.**

**3 · Findings and questions go in separate sections.** A finding is a defect with evidence. A
question is for the owner to decide.

**4 · Nothing found is a complete answer.** A phase that must produce findings will manufacture
them. **Say what you checked and found correct.** Refusals are first-class.

**5 · A settled decision may be questioned, never filed as a defect.** It goes in the questions
section with the reasoning.

**6 · Every finding carries what it would cost to be wrong** — found now against found after task N.

---

## The output

One report. Each finding:

```
[VERIFIED|REPORTED]  <one-line claim>
  Where:     file:line
  Evidence:  what was read, and what it said
  Cost:      what it costs to find this after task N instead of now
```

Then **questions**, numbered, each with what it would change. Then **executability** — task by task,
could you run it, and every place you had to guess. Then **what was checked and found correct**,
which is what makes *nothing found* usable rather than empty.

---

## Reading budget

**`plan.md` is 282 lines and is the subject — read it whole.** Everything else by section:
`grep -n '^## '` first, then only what a claim above needs.

`../../backlog.md` is 855 lines — **do not read it end to end.** Claims 4, 5, 6 and 7 need its
preamble, its section headings, and two named items; nothing else.

**If you run out of room, say so and name what you did not reach.** An honest gap is worth more than
a skim.
