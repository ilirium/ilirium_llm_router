# The next session's prompt

*The one file in `docs/` allowed to go stale, per `README.md` — which is why it is rewritten at each
handoff rather than left. **Replaced 2026-09-04**, at the point where Phase 13 stops for the owner.
Whatever comes next replaces it again.*

---

**Phase 13 is open and stopped at a checkpoint that is the owner's.** Branch and worktree
`docs/phase-13-method-and-backlog`, forked from `main` at `dec7c4a`, **13 commits**. Milestone 2 has
five phases merged and this one in flight.

**Start in the phase worktree**, not in `main`:
`/Users/ilirium/Projects/local/ilirium_llm_router/phase-13-method-and-backlog`. It has **no venv**,
and nothing here needs one — **Phase 13 changes no `src/` and no `tests/`.** The trunk's **448
tests** stand by construction.

## The one thing to do next

**Run the review of the item inventory — task 14a — in a session of its own.** *It is deliberately
not run in the session that produced the inventory.*

> Hand a fresh-context agent this file, verbatim, and nothing else:
> `docs/milestone-2-corpus/phase-13-method-and-backlog/evidence/item-inventory-review-charter.md`

**It is written to be self-contained** — the reviewer is assumed to know nothing about this
repository. It names the subject, the frozen source to check against, eight checks, the known false
positives, and the rules.

**Then bring its report back here.** Tasks 15, 16, 18, 19 and 20 all take the ratified inventory as
input, and **none of them may run before it returns**: ids are permanent, so a wrong boundary
applied is a wrong boundary forever.

## Where the phase actually is

| Group | |
|---|---|
| **A** open the phase | **done** — plan, re-derivation, forward review, cross-file update |
| **B** `IDM-009` | **done** — reviewing executed work |
| **C** `IDM-010` | **done** — the per-phase `for-the-owner.md` |
| **D** `IDM-011` | **done** — the backlog, and the `IDM-001` amendment |
| **E** the refactor | **part-done.** 13 and 17 are done; **14a is next**; 15, 16, 18, 19, 20 are blocked on it |
| **F** the review of this phase | not started — Phase 13 reviewed under the `IDM-009` it wrote |
| **G** close | not started |

**`docs/backlog.md` is untouched.** No id has been applied to it.

## Read these, in this order

1. **`docs/status.md`** — first, every session. The only file that holds state.
2. **`.../phase-13-method-and-backlog/plan.md`** — the **24-row settled table** and the register, at
   minimum. Grep the headings.
3. **`notes.md`**, then the group notes you need. **`notes-group-e.md`** is where the refactor is;
   **`notes-review-plan.md`** is what the forward review found.
4. **`for-the-owner.md`** if you are the owner. Five entries, written during the phase.

**Do not read `review-charter.md`** unless you are writing task 21's charter — the forward review is
spent.

## Five things a session will get wrong here

- **A number in a document is unverified until you open the thing it counts.** This phase has been
  wrong about a count **four times**: twice about one file's entries, once relaying a week-old
  figure, and once a line number in the inventory itself. **Every one was caught by opening the
  file or by rendering it — none by rereading prose.**
- **`backlog-index.py --check` exits 1 on this branch and that is correct.** This phase's documents
  already cite `BKL` ids that `backlog.md` does not carry yet. It flips to 0 when task 15 lands.
- **`make lint` reaches neither column width nor `docs/procedures/`.** `E501` is not in ruff's
  default set, and the Makefile lints `src tests` only. Count characters **in Python, not `awk`** —
  `awk` counts bytes and gave a wrong number here once already.
- **`link-check.py`'s count is a property of the worktree** — **117 broken here against 91 on
  `main`**, and the delta is files Group E has still to create. Compare against a run in the *same*
  tree or not at all.
- **Push state cannot be checked from here.** `origin` is configured but this clone holds **no
  remote-tracking refs** — `git branch -r` is empty. Ask the owner; do not infer.

## What is in force now that was not a week ago

- **A session asks the owner before filing a backlog item.** If the answer is no, the decline goes
  in the phase's `notes.md`. `IDM-001` and `backlog.md` said for two days that filing was the phase's
  own act; both are amended. → `IDM-011`.
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

`CLAUDE.md`, in full. Two earned their place this phase, both the hard way:

**Exercise it before committing.** The script was read, looked right, and had **three defects** —
one of which only appears if you run `--write` and then `--check`, in that order.

**Propose before implementing, and raise it rather than burying it.** The plan was interviewed over
four rounds; the forward review then found it would have made the next session **re-decide a settled
row**. Both of the phase's `REGRET` entries are in `for-the-owner.md` rather than quietly fixed.
