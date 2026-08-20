# The next session's prompt — the `docs/idm-and-claude-md` branch

*A second prompt file, and it exists because `prompt.md` is occupied.* That file opens **Phase 10** and
tells its session *"check out `feat/phase-10-body-store`; do not open a new one"* — a different session
is working from it right now. Overwriting it would misdirect that session and conflict at merge. This
file follows `README.md`'s rule for `prompt.md` otherwise: **it names what to read and what to
distrust, and never summarises what those documents say.** It expires when this branch merges.

---

## Where you are

**Work in the worktree, not the main checkout.**

```
/Users/ilirium/Projects/worktrees/idm-and-claude-md      branch docs/idm-and-claude-md
```

The two paths in `CLAUDE.md`'s note — the OneDrive one and `~/Projects/code-2026/…` — are the **same
directory**, checked out on `feat/phase-10-body-store` and in use by another session. `git switch`
there would pull the tree out from under them. This worktree shares that repository's `.git`; no clone
was made.

**This branch forks from `feat/phase-10-body-store` at `273057f`, not from `main`.** It carries that
branch's 53 commits and cannot reach `main` until Phase 10 merges. That was the owner's choice, made so
this work could see `IDM-004`, which exists nowhere else.

## What was done

Read `git log main..HEAD` — eleven commits, each naming its task in the body. Two things happened, in
this order:

1. **Both milestone playbooks moved out of `docs/README.md` into `docs/method/`**, as `IDM-005` and
   `IDM-006`, with every consequence repointed. The closing one was **repaired** on the way: it had
   become the narrative of the restructure that produced it, which was
   `milestone-1-core/documentation-review-2026-08-16.md`'s highest-consequence finding (G1), parked in
   `backlog.md` and unactioned since 2026-08-17. `backlog.md` now records it closed.
2. **Both were then reshaped into two zones** on the owner's design — procedure above an
   `End of procedure` line, one evidence row per rule below it. Read `IDM-006` before `IDM-005`; it is
   where the shape was worked out. Two intermediate drafts are in history at `83d039e` and are not in
   the tree.

## What to distrust

- **`docs/prompt.md` is not yours.** It opens Phase 10. Leave it alone.
- **Do not touch `milestone-2-corpus/phase-10-body-store/`.** `notes.md:889` and `review-charter.md:187`
  both cite the playbook rule and were deliberately left stale; that branch is being written
  concurrently and editing those files here would conflict. Same reasoning for `docs/status.md` and for
  `implementation-plan.md` beyond the one line already changed.
- **`link-check.py`'s counts depend on an untracked file.** 13 of its hits name
  `.claude/settings.local.json`, which a worktree does not have. A run here reports 99 broken; the main
  checkout reports 86. The docstring says so — read it before concluding anything broke.
- **`CLAUDE.md` differs between this branch and Phase 10's.** Both edited it; different sections, so
  the merge should be clean, but check rather than assume.

## Open decisions, none of them started

| | |
|---|---|
| The two-zone shape is undocumented | `IDM-000` records nothing about it. The recommendation put to the owner was that it is **the shape a playbook takes** — `IDM-001`–`IDM-004` are consulted, not executed — against the alternatives of blessing it for any IDM, or leaving it a per-document choice. **Undecided** |
| A stale count in a live document | `milestone-2-corpus/implementation-plan.md:9` says *"four of Milestone 1's six phases"*. `reference/lessons.md` lesson 1 is canonical at **five of seven** and says the count grew on 2026-08-16. Left alone as Milestone 2's document. The owner was asked whether to fix it and **has not answered** |
| This branch is not in `status.md` | `IDM-001` says in-flight branches are recorded there. It is not, because that table's only other row is Phase 10's and is being actively rewritten. The owner was asked now-or-at-merge and **has not answered** |
| `IDM-005` step 2 has no evidence | *"Run the cheapest experiment that could refute it"* is the one step of the eight with nothing behind it — Milestone 1 went from the claim to Phase 0's skeleton, and the claim was settled by Phase 1's first relay, after the spec. `E2` says so. Whether the step survives on those terms is the owner's call and **was not asked** |

## What the owner expects of a session here

`CLAUDE.md`'s working agreement governs, and two parts of it were load-bearing all session: **propose
before implementing — a design answer is not a build order**, and **raise problems explicitly rather
than working around them**. Findings during this branch's work included three defects in work this
same branch had just produced; each was reported plainly and fixed rather than smoothed over. That is
the expected behaviour, not an exception.

The owner also asked, more than once, that questions carry **clear options with their costs** rather
than an open-ended ask.
