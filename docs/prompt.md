# The next session's prompt

*The one file in `docs/` allowed to go stale, per `README.md` — which is why it is rewritten at each
handoff rather than left. **Replaced 2026-09-17**, at Phase 13's merge. Whatever comes next replaces
it again.*

---

**Phase 13 merged 2026-09-17 at `97fd822`. Nothing is in flight.** Work in `main`:
`/Users/ilirium/Projects/local/ilirium_llm_router/main`. **No phase is open, so there is no phase
worktree to start in** — that is different from the last four handoffs.

*No commit count is written here. A count written at a handoff is wrong at the next commit, and this
repository has recorded that defect five times.*

## Read these, in this order

1. **`docs/status.md`** — first, every session. The only file that holds state.
2. **`docs/backlog.md`** — **it has changed shape completely.** Every item is now a
   `### BKL-NNNN — title` heading with a metadata line under it, and the table at the top is
   **generated**. `docs/backlog-done.md` is new and holds the four done items.
3. **`docs/method/IDM-011-the-backlog.md`** before touching either file.

## What is in force now that was not before

- **A session asks the owner before filing a backlog item.** If the answer is no, the decline goes
  in the phase's `notes.md`. → `IDM-011`, which amends `IDM-001`'s authority claim.
- **Every phase folder carries a `for-the-owner.md`**, written *during* the phase, to a person.
  **Anything needing a decision is asked out loud instead.** → `IDM-010`.
- **A phase is reviewed before its merge**, under a charter, by two runs, with the subject verified
  by `git diff` at the moment the runs start. → `IDM-009`. **Phase 13 was its first subject and it
  stopped its own author's merge.**

## Five things a session will get wrong here

- **Never hand-type inside a generated table.** `backlog.md`, `backlog-done.md` and
  `reference/branches.md` all carry one. Edit the item or the description and re-run `--write`.
  *`--write` refuses while any problem is outstanding, so fix the problem first.*
- **Never write a `BKL-NNNN` that does not exist — not even as an example.** Ids are allocated in
  order and never reused, so an invented id is the **next** one to be handed out; the moment an item
  claims it, a sentence about something imaginary becomes a citation of a real and unrelated item
  and `--check` starts **passing** on it. *Describe it instead: "a synthetic id one past the
  highest."* → `IDM-011`.
- **A green check is a claim, not evidence.** Phase 13 shipped **three** checks that passed while
  testing nothing, and none was found by reading — a count assertion blind to the case it was built
  for, a table column named by two documents and written by no code, and a test whose header-row
  exclusion skipped the rows it existed to find. **Make the thing go wrong and see whether the check
  notices**, and have the harness report "mutation applied" separately from "check failed".
- **`link-check.py`'s count is a property of the worktree.** **92 broken on `main` today.** Compare
  against a run in the *same* tree or not at all.
- **Push state cannot be checked from here — ask, do not infer.** `origin` is configured, this clone
  holds **no remote-tracking refs**, and `git branch -r` is empty. *The owner reported the branch
  pushed on 2026-09-17; that is a report, not a check.*

## Open, and none of it blocks

- **Nobody has driven the corpus tools by hand.** Named as the owner's first job at Phase 11's
  handoff; still not done, four phases later.
- **`BUG-001` is still unreported** to either upstream issue.
- **Failure mode 3 is undischarged** — whether archiving *slows* a call. `BKL-0017`.
- **`EPD-001` and `EPD-002` are both waiting on a decision**, not on work.
- **Phase 14 is allocated** to the Anthropic rate-limit response headers — `BKL-0034`, and
  `milestone-2-corpus/implementation-plan.md` holds what its plan cannot skip.
- **`for-the-owner.md` entry 1 is an open errand:** run `git fetch origin` once, so push state
  becomes checkable at all.
- **The Milestone 2 phase count went stale a fifth time at this very merge**, in the paragraph that
  describes itself going stale. `BKL-0007` has the evidence and needs the decision, not more
  examples.

## The working agreement still applies

`CLAUDE.md`, in full. Two earned their place in Phase 13, both the hard way:

**Exercise it before committing.** Three instruments passed while testing nothing, and a mutation
harness silently never ran its mutations — which looks identical to a clean pass.

**Raise it rather than burying it, and say it is wrong rather than working around it.** Three of the
five findings that stopped the merge were found, written down, and then **not put to the owner**
until a later session went looking. A finding that stops a merge and is then not raised is worse
than one nobody found.
