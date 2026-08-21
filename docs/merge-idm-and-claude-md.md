# Merging `docs/idm-and-claude-md` into `feat/phase-10-body-store`

*What the merge leaves for a follow-up session, and nothing else.* Written 2026-08-21, on the owner's
decision, because this branch's work reaches into three documents that another session was writing at
the same time. `docs/README.md`'s root-files table admits this file and `prompt-idm-and-claude-md.md`
as one class: **pointers, never a summary; paths from the repository root; deleted by the merge that
retires it.**

**Read this file, then act on it. It is a work list, not a record** — the record of what happened is
`git log main..docs/idm-and-claude-md`, eleven-plus commits each naming its task in the body.

**Cite by phrase, not by line number.** Every target below is quoted rather than numbered, because
`phase-10-body-store/notes.md` is still being appended to and any line number here is stale on arrival.

---

## The merge itself

**Target: `feat/phase-10-body-store`**, which is this branch's fork parent at `273057f` — not `main`.
This branch cannot reach `main` until Phase 10 merges.

`--no-ff`, always. **`git merge` cannot read its message from stdin** — write it to a temp file and use
`-F <file>`; `-F -` works for `git commit` and fails here.

**Expect no conflicts, and check rather than assume.** Four files are touched by both branches —
`CLAUDE.md`, `docs/backlog.md`, `docs/procedures/link-check.py`,
`docs/milestone-2-corpus/implementation-plan.md` — and every hunk pair was compared on 2026-08-21 and
found far apart. `docs/status.md` is the one file this branch deliberately did **not** touch for that
reason; Phase 10 rewrote the very hunk a row would have landed in.

---

## What the merge leaves undone

### 1. `docs/milestone-2-corpus/implementation-plan.md` — three edits

*Deferred because Phase 10 was writing this file concurrently and it is Milestone 2's document, not
this branch's.* All three are consequences of `method/IDM-005-opening-a-milestone.md` losing a step.

| Find this | Do this |
|---|---|
| *"per the opening playbook's step 7"* | **→ step 6.** The steps renumbered on 2026-08-21 |
| *"four of Milestone 1's six phases found their own plan wrong on contact"* | **Delete the count and point instead** at `docs/reference/lessons.md` lesson 1, which is canonical. *Owner's decision 2026-08-21.* **Both numbers are wrong** — canonical is *five of seven* — and `IDM-005`'s closing note already records *four of six* as the stale form circulating in several documents. Replacing it with a pointer removes the class, not just the instance |
| *"The opening playbook has eight steps. **Steps 1–7 are not run**"*, and the **eight-row table** under *"What is deliberately not done yet"* | **Renumber to seven, and fold row 2 into row 1.** Old row 2 was *"Run the cheapest experiment that could refute it — deferred; it *is* Phase 9's gate"*; that is now part of step 1, and the observation survives the fold. Every row below it shifts down one |

### 2. Two citations of the closing playbook that resolve perfectly and are wrong

Both still send a reader to `docs/README.md`, which no longer holds the playbook. Both should name
`docs/method/IDM-006-closing-a-milestone.md`, **step 9 — "Rewrite this playbook, last"**.

| File | The phrase |
|---|---|
| `docs/milestone-2-corpus/phase-10-body-store/notes.md` | grep **"own playbook rule"** — *"...write this playbook last, from what it cost"* |
| `docs/milestone-2-corpus/phase-10-body-store/review-charter.md` | grep **"own playbook rule"** — *"...write this playbook last"* |

Both phrases reach `docs/README.md` by a `../../` hop. **They are quoted here without that path on
purpose**, so this file does not add two permanently broken links to a count it also predicts.

**`link-check.py` will not report either of these, and a clean run is not evidence.** `docs/README.md`
still exists, so both paths resolve; what moved is a *rule inside it*. This is `IDM-006`'s `E12`
exactly — *searching for what moves will not find what gets cut* — and both were found by reading.

### 3. `docs/status.md`, and an open question underneath it

This branch was never recorded there, on the owner's instruction, because Phase 10 is rewriting that
table. **Once this merges, the branch is no longer in flight**, so `status.md` never needs a row for it
and nothing on that list touches `status.md` at all.

**`IDM-001` was amended on 2026-08-21 to answer this**, and the answer is the merge you are about to
make. Its "Where a branch is recorded" table gained a third row: **a branch carrying no phase number is
recorded by its merge commit message**, because it has no phase note and inventing a phase number to
give it one would spend an identity to buy a filing slot.

**So the merge message is the record. Write it as though the phase note this branch does not have were
being written into it** — the fork point (`273057f` on `feat/phase-10-body-store`, not `main`, so the
branch could see `IDM-004`), why the branch existed, and what it decided. The rules it produced are
already recorded in `IDM-005`, `IDM-006` and `IDM-000`; what only the merge can carry is the
provenance.

### 4. Checked, and deliberately left alone — do not "fix" these

**Frozen archive.** `docs/README.md`'s rule is *paths yes, claims no*: a claim records what was believed
at the time and is not revised.

- `phase-9-corpus-gate/notes.md` and `phase-9-corpus-gate/plan.md` each cite **"step 3 of the opening
  playbook"**. Step 3 was *Capture the real input*; it is step 2 from 2026-08-21. Phase 9 merged at
  `b29d502` and its notes are frozen. **Leave them.**
- `milestone-1-core/` cites both playbooks in several places, all of them claims about what was true
  during Phase 7. **Leave them.**

### 5. Retire both branch-scoped files

**Delete `docs/merge-idm-and-claude-md.md` and `docs/prompt-idm-and-claude-md.md`** once the list above
is done. → `method/IDM-001-git-branching.md`, *"Closing out a status placeholder is part of the
merge"* — this file is a statement of unfinished state, which is the exact form that rule covers, and
leaving it behind is the defect it was written about. **Neither file is archived; both are deleted.**

### 6. Re-check, and read the number correctly

Run `docs/procedures/link-check.py`. **The count depends on where you run it, and the docstring says
so** — measured 2026-08-21 on this branch:

| | Broken | |
|---|---|---|
| This worktree | **104** | measured 2026-08-21, with this file in the tree |
| The main checkout | **89** | arithmetic, not measured — no session has run it there |

The gap is **15 hits naming `.claude/settings.local.json`**, which is untracked and therefore absent
from a worktree. **A separate 6 hits name `.claude/agents/local-helper.md`, which exists in neither
checkout** — those are broken everywhere, are older than this branch, and are not a worktree artefact.
Do not fold them into the 15.

**Deleting the two branch-scoped files at step 5 removes four more hits** — one of each kind from this
file, one of each from `prompt-idm-and-claude-md.md`, all of them paths quoted inside the caveat you
are reading. That is arithmetic too. **Run the tool after the deletions and take its number; do not
carry any of these forward.** This phase has predicted this count wrong four times.
