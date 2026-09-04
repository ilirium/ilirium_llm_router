# The next session's prompt

*The one file in `docs/` allowed to go stale, per `README.md` — which is why it is rewritten at each
handoff rather than left. **Replaced 2026-09-04**, at the point where Phase 13 stops for the owner.
Whatever comes next replaces it again.*

---

**Phase 13 is open. The checkpoint is discharged and Group E is unblocked.** Branch and worktree
`docs/phase-13-method-and-backlog`, forked from `main` at `dec7c4a`. Milestone 2 has five phases
merged and this one in flight.

*No commit count is written here. `git log main..HEAD` answers it, and a count written at a handoff
is wrong at the next commit — which is the defect this repository has recorded four times.*

**Start in the phase worktree**, not in `main`:
`/Users/ilirium/Projects/local/ilirium_llm_router/phase-13-method-and-backlog`. It has **no venv**,
and nothing here needs one — **Phase 13 changes no `src/` and no `tests/`.** The trunk's **448
tests** stand by construction.

## The one thing to do next

**Group F — review this phase's finished work, under the `IDM-009` it wrote.** *Phase 13 is that
document's first subject, at task 21, and `IDM-009` puts the review **before** the merge.*

**Everything Groups A–E2 produce is now on disk and stable.** `backlog.md` holds 34 items,
`backlog-done.md` holds 4, every item is a `### BKL-NNNN — title` heading, and
`backlog-index.py --check` exits 0.

**What a reviewer should be told to look at hardest:** the shape changed *after* the ids were
applied, so the question is whether anything moved in the conversion. **Task 27 says nothing did**
and the check is four lines — *re-run it rather than trusting this sentence.*

---

*Group E is done and is kept here only as context for E2:*

**~~Task 15 — apply the ratified ids to `docs/backlog.md`.~~ Done, with 16, 18, 19 and 20.** It is
no longer blocked: task 14a ran on 2026-09-04, the owner ratified the same day, and
`evidence/item-inventory.md` is the ratified source. **Read it, not this file, for what to apply.**

**The inventory holds 38 items, not 36.** *The cold review found two the pass had missed —
`backlog.md:716` and `:735`. Both are struck-through `done` entries opening `~~**`, where the
enumeration matched **bold or `###`** at the line start; the two struck entries opening `**~~` were
both caught.* They are `BKL-0032` and `BKL-0033`, so **old `BKL-0032`–`0036` are now
`BKL-0034`–`0038`**, and `BKL-0025`–`0031` did not move.

**Nothing about the inventory is open.** The last two questions were settled 2026-09-04:
`BKL-0007` stays `open`, `BKL-0020` stays one id with its refused third noted in the description.

**Task 15 carries two corrections beyond the ids**, both recorded at the end of `item-inventory.md`:
`BKL-0007`'s premise is expired — it argues from *"four places across two files"* and there are now
**two copies, both in `status.md`** — and `BKL-0004`'s *"545 lines"* is 859 and must be fixed in
place, because `partly-done` means it does not move out.

**`docs/backlog.md` is still untouched.** No id has been applied to it.

**Task 14a's raw report is not kept** — `notes-review-plan.md` says why. Its outcome is in
`notes-group-e.md` and its corrections are in `item-inventory.md` itself.

## Where the phase actually is

| Group | |
|---|---|
| **A** open the phase | **done** — plan, re-derivation, forward review, cross-file update |
| **B** `IDM-009` | **done** — reviewing executed work |
| **C** `IDM-010` | **done** — the per-phase `for-the-owner.md` |
| **D** `IDM-011` | **done** — the backlog, and the `IDM-001` amendment |
| **E** the refactor | **done.** 13, 14, 14a, 15, 16, 17, 18, 19 and 20 all run; `--check` exits 0 |
| **E2** one item shape | **done.** Tasks 22–29. `### BKL-NNNN — title` headings; the table-row and bare-paragraph shapes retired. **No id changed, proved at task 27** |
| **F** the review of this phase | not started — Phase 13 reviewed under the `IDM-009` it wrote |
| **G** close | not started |

## Read these, in this order

1. **`docs/status.md`** — first, every session. The only file that holds state.
2. **`.../phase-13-method-and-backlog/plan.md`** — the **24-row settled table** and the register, at
   minimum. Grep the headings.
3. **`notes.md`**, then the group notes you need. **`notes-group-e.md`** is where the refactor is;
   **`notes-review-plan.md`** is what the forward review found.
4. **`for-the-owner.md`** if you are the owner. **Nine entries**, written during the phase.
   *Do not take that number from here either — it said five while citing entry 7 eleven lines
   below, and it is entry 5's own subject.*

**Do not read `review-charter.md`** unless you are writing task 21's charter — the forward review is
spent.

## Five things a session will get wrong here

- **A number in a document is unverified until you open the thing it counts.** This phase has been
  wrong about a count **six times** — and the entry that counts them had itself gone stale at three.
  Twice about one file's entries, once relaying a week-old figure, once a line number in the
  inventory, twice in this file about `for-the-owner.md`, and **once about the inventory's own item
  count, which was two commits from being frozen into permanent ids.** **Every one was caught by
  opening the file or by rendering it — none by rereading prose.**
- **`backlog-index.py --check` exits 1 on this branch and that is correct.** This phase's documents
  already cite `BKL` ids that `backlog.md` does not carry yet. It flips to 0 when task 15 lands.
- **`make lint` reaches neither column width nor `docs/procedures/`.** `E501` is not in ruff's
  default set, and the Makefile lints `src tests` only. Count characters **in Python, not `awk`** —
  `awk` counts bytes and gave a wrong number here once already. **And the 100-column rule is written
  for `src/` and `tests/` only** — no statement of one for markdown exists, and the documents run to
  101–103 routinely. *Open question, entry 7 of this phase's `for-the-owner.md`.*
- **`link-check.py`'s count is a property of the worktree** — **117 broken here against 91 on
  `main`**, and the delta is files Group E has still to create. Compare against a run in the *same*
  tree or not at all.
- **Push state cannot be checked from here.** `origin` is configured but this clone holds **no
  remote-tracking refs** — `git branch -r` is empty. Ask the owner; do not infer.

## What is in force now that was not a week ago

- **A session asks the owner before filing a backlog item.** If the answer is no, the decline goes
  in the phase's `notes.md`. `IDM-001` and `backlog.md` said for two days that filing was the
  phase's own act; both are amended. → `IDM-011`.
- **Every phase folder carries a `for-the-owner.md`**, written *during* the phase, to a person.
  **Anything needing a decision is asked out loud instead.** → `IDM-010`.
- **A phase is reviewed before its merge**, under a charter, by two runs. → `IDM-009`. **Phase 13 is
  its first subject**, at task 21.

## Open, and none of it blocks

- **Nobody has driven the corpus tools by hand.** Named as the owner's first job at Phase 11's
  handoff; still not done.
- **`BUG-001` is still unreported** to either upstream issue.
- **Failure mode 3 is undischarged** — whether archiving *slows* a call.
- **A call can still vanish**, and closing it needs a guarantee a row is never written twice.
- **The `uv_build` pin bump has no rule behind it.** An owner decision.
- **The Milestone 2 phase count has gone stale four times.** `CLAUDE.md` no longer carries it at
  all; the remaining copies are in `status.md`.

## The working agreement still applies

`CLAUDE.md`, in full. Three earned their place this phase, all the hard way:

**Exercise it before committing.** The script was read, looked right, and had **three defects** —
one of which only appears if you run `--write` and then `--check`, in that order.

**Propose before implementing, and raise it rather than burying it.** The plan was interviewed over
four rounds; the forward review then found it would have made the next session **re-decide a settled
row**. All three of the phase's `REGRET` entries are in `for-the-owner.md` rather than quietly
fixed.

**Check prior evidence before planning a rerun — and check a review's arithmetic too.** The author
run of the inventory cleared the exact claim that was false, and its own reconciliation summed to 61
against a real 59. **The subtraction was done and the column was never added up.** The cold run that
caught it then miscounted which ids shift. *Neither is an argument against reviewing; both are the
argument for opening the file.*
