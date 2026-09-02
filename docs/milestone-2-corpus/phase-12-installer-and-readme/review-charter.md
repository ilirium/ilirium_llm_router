# Phase 12 — charter for the forward review

**Written 2026-09-02, before either run.** Per `../../method/IDM-004-reviewing-unexecuted-work.md`,
iteration 1: **the charter decides what the review finds.** A reviewer told "review this" verifies
what is easy to verify and returns a tidy list that misses the thing that matters. This file is
handed to the cold reader verbatim.

## What is under review

**`plan.md` in this folder, at commit `80914a0`, and nothing else.** It is unexecuted: no task has
run, no `src/` file has been touched, and the phase's first task needs the owner's go-ahead because
it installs software.

**Explicitly out of scope:**

- **Executed work.** Phases 1–11 and everything in `../../milestone-1-core/`. If the plan
  *mis-describes* executed work that is a finding; the executed work itself is not. - **How a
  decision was reached.** The plan's "What is settled, and by whom" table holds decisions the owner
  made on 2026-09-02. Per rule 5 below, a settled decision may be **questioned** and may never be
  filed as a defect. - **The `README.md`'s current prose.** It is being replaced. Its *content*
  matters only where the plan claims something about it. - **Whether `uv tool install` works.** That
  is Task 1's job. Do not try to install anything.

## Two runs, two questions

| Run | Question |
|---|---|
| **Author** — the session that wrote the plan | *Is this consistent with what was decided?* |
| **Cold reader** — fresh context, was not present for the interview | ***Could you execute this from the document alone? Name every place you had to guess.*** |

**The guesses are the findings.** Where sessions are cleared deliberately, the next person to
execute this document is a cold reader — so a plan legible only to its author is already broken for
its purpose. Do not resolve an ambiguity by inferring what was probably meant; report it.

## What to look for, in terms of *this* document

- **A gap** — a task that names an outcome but not how to reach it, or a decision the plan needs and
  does not have. - **An incorrect point** — a claim about `src/`, `pyproject.toml`, `README.md` or
  another document that reading the file refutes. - **A leftover** — anything carried from the
  interview that the settled table then changed. This plan was rewritten twice: eight README
  sections became ten, and one unratified position became settled. - **A contradiction** — between
  the settled table, the section table, the task list and the register. - **An unanswered question**
  — raised in the plan and never closed. - **An ordering risk** — a task whose output another task
  documents, where the second could be written against a shape the first then changes.

## The claims that must be re-verified by reading the source

**Named individually and never as a category.** Each was checked once, by the session that wrote the
plan, which is the weakest verification available. Open the file; do not trust the plan's quotation.

1. `src/ilirium_llm_router/cli.py:30` — `DEFAULT_CONFIG_PATH = Path("config.yaml")`, and that it is
   relative to the working directory rather than to the package. 2.
   `src/ilirium_llm_router/cli.py:38–42` — that `extract` and `verify-archive` return **before**
   `load_config` is called, so they need no config file. 3. `src/ilirium_llm_router/config.py:259` —
   that relative log, stats and corpus paths resolve against the **config file's** directory. 4.
   `README.md:100–103` — that the pointer to `docs/README.md` exists there and that no section in
   the plan's ten-section table other than "For developers" would inherit it. 5. `README.md` — that
   it says Milestone 1 was **six** phases, and that `CLAUDE.md`, `docs/status.md` and
   `docs/milestone-1-core/README.md` say **seven**. Count the phase folders. 6. `pyproject.toml` —
   that `[project.scripts]` defines the entry point, that the build backend is `uv_build`, and that
   `requires-python` is `>=3.13`. 7. `README.md`'s corpus-tools section — that it is marked
   temporary and names Phase 12 as its replacement, and that `../implementation-plan.md`'s Phase 12
   entry records the commitment. 8. `src/ilirium_llm_router/cli.py` — that a `--version` output
   already exists. 9. That `load_dotenv()` is called with no argument, and what python-dotenv's
   default search does. **This one is a genuine uncertainty**, not a check of a known answer: the
   plan asserts `.env` is read from cwd and the author did not read python-dotenv's source.

## Known false positives — do not spend findings on these

- **The plan cites files it will create** — `notes.md`, `evidence/`,
  `../../captures/original-project-description.md`. Every phase plan here does;
  `procedures/link-check.py` reports them as broken and they are correct. - **`Merge commit: (to be
  filled at the merge)`** is a placeholder that is correct while true, per
  `../../method/IDM-001-git-branching.md`. - **The three `❓` rows in the register** are required by
  `../../method/IDM-008-the-register.md`, which asks for `❓` against anything named and never
  valued. They are the instrument working, not omissions. - **`link-check.py` reports ~100 broken
  links repository-wide** and its count differs by worktree. Both are known and recorded in
  `../../backlog.md`. - **The plan is short.** Phase 12 is deliberately narrow; the owner scoped it
  that way because mixing subjects produced bloat before. "Should do more" is not a finding unless
  the plan cannot meet its own "Done when".

## The rules — copied in, not cited

1. **Read-only.** Return a work list; edit nothing. Fixing what you find destroys both the ability
   to judge the finding and the record of what a cold reader misread.
2. **Label every finding `VERIFIED` or `REPORTED`.** VERIFIED means you opened the file and
   confirmed the claim. REPORTED means suspected and not confirmed. An unlabelled review cannot be
   triaged.
3. **Findings and questions are separate sections.** A finding is a defect with evidence; a question
   is for the owner to decide.
4. **Nothing found is a complete answer.** A review that must produce findings will manufacture
   them. Say what you checked and found correct. **Refusals are first-class.**
5. **A settled decision may be questioned, never filed as a defect.** It goes in questions, with
   reasoning.
6. **Every finding carries what it would cost to be wrong** — found now, against found after task N.
   That is the ranking.

## The output

```
[VERIFIED|REPORTED]  <one-line claim>
  Where:     file:line
  Evidence:  what was read, and what it said
  Cost:      what it costs to find this after task N instead of now
```

Then, as separate sections: **questions** (each with what it would change), **executability** — task
by task, could you run it, and every place you had to guess — and **what was checked and found
correct**.

## Reading budget

Read `plan.md` whole; it is 120 lines. Read the named source claims by grepping to the line rather
than reading whole files. **Do not read** Phase 10's or Phase 11's notes, or any `plan.md` other
than this one — they are the largest documents here and none of them is under review.