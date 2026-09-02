# Phase 12 — charter for the review of the finished work

**Written 2026-09-02, before either run.** Per `review-plan-jobs-done.md` beside this file, which
the owner settled the same day. **The charter decides what the review finds** — that rule is
`IDM-004`'s and it carries over unchanged, because a reviewer told "review this" verifies what is
easy to verify and returns a tidy list that misses the thing that matters. **This file is handed to
the cold reader verbatim.**

**This is not the forward review.** That one ran before task 1, against an unexecuted plan; its
charter is `review-charter.md` and its findings are `notes-review-plan.md`. **This one is against
work that ran**, and the difference is the whole reason a separate charter exists.

---

## What is under review

**Phase 12 as executed** — branch `feat/phase-12-installer-and-readme`, commits `80914a0` through
`15cb2bb`, forked from `main` at `5cdc1c9`. Three things, and all three are in scope:

**1 · The six non-documentation files it changed.**

| File | What changed |
|---|---|
| `src/ilirium_llm_router/cli.py` | `init`, `--version`, the `.env` search fix, two module constants |
| `src/ilirium_llm_router/config-template.yaml` | new, package data |
| `src/ilirium_llm_router/env-template` | new, package data |
| `tests/test_cli_init.py` | new, seven tests |
| `pyproject.toml` | the `uv_build` pin, `>=0.11.32,<0.12.0` → `<0.13` |
| `.env.example` | one line reworded so byte-identity with the shipped template is honest |

**2 · The phase folder** — `plan.md`, `notes.md`, the five group notes, `notes-review-plan.md`, and
`evidence/`.

**3 · The eight documents the phase edited outside its folder.** *Owner's decision; this is where a
wrong claim propagates.* `README.md` (the deliverable, rewritten whole), `docs/status.md`,
`docs/backlog.md`, `docs/prompt.md`, `docs/milestone-2-corpus/implementation-plan.md`,
`docs/captures/README.md`, `docs/captures/original-project-description.md`, and
**`docs/method/IDM-001-git-branching.md` — a method-tier rule now in force, amended by a `feat/`
branch.**

### Explicitly out of scope

- **Phases 1–11 as executed.** If Phase 12 *mis-describes* them that is a finding; they are not.
- **How any settled decision was reached.** `plan.md`'s "What is settled, and by whom" and
  `review-plan-jobs-done.md`'s equivalent hold the owner's decisions. **Rule 5 below.**
- **This charter and `review-plan-jobs-done.md`.** A review that reviews its own instructions is
  circular. `notes-review-plan.md` *is* in scope — it is a record of work that ran.
- **The `README.md` that was replaced**, except where a claim is made about it.
- **Anything requiring the machine.** Do not install, uninstall or start a server. The owner's
  go-ahead was given once, for one session, and is spent. **If a claim can only be settled by
  installing something, that is a finding saying so.**

---

## Two runs, two questions

| Run | Question |
|---|---|
| **Author** — this session | *Is this consistent with what was decided, and is what it claims true?* |
| **Cold reader** — fresh context | ***Could you re-derive these claims from what is in the repository? Name every place you had to take something on trust.*** |

**The cold reader's question is not `IDM-004`'s.** That one asks *could you execute this document?*
— right for a plan, meaningless for work that has run. **The executed-work equivalent is
reproducibility:** every number in the notes should trace to something frozen, something in the
code, or a command a reader can re-run. **The places where it does not are the findings.**

**The author run declares a gap and does not paper over it.** Phase 12 ran across two sessions:
Groups A–C in one, D–E in another. **For A–C this session has the notes and the commit messages and
nothing else** — a warm read, not an author run. Findings about A–C carry that label.

---

## What a finding looks like *in executed work*

- **A claim that the artefact refutes.** The prose says one thing; `cli.py`, a test, a template or a
  frozen file says another. **This is the primary axis** — there are three things that can disagree
  here where a plan has only one.
- **A number that cannot be re-derived.** It appears in a note, a commit message or the `README.md`
  and nothing in the repository produces it.
- **A settled row the execution did not honour.** `plan.md`'s settled table, row by row, against
  what shipped. *One such was already found by the phase's own register check and fixed; the check
  was mechanical and this pass is not, so do not assume it caught the rest.*
- **An instrument that cannot fail.** See the next section.
- **A claim that has propagated.** The same statement in two places with two values, or a claim in
  `reference/`, `status.md`, `backlog.md` or `IDM-001` that its source does not support.
- **Something the phase declined without saying so.** Adding a backlog item is how a phase declines
  scope; silently dropping something is not.
- **A leftover.** Text that was true at some commit and is not true at `15cb2bb`.

**Rank every finding by what the claim has already reached**, not by how hard it was to find:

`reference/` and `CLAUDE.md` (canon) → `status.md`, `backlog.md`, `IDM-001` (acted on) →
`implementation-plan.md` (shapes unplanned phases) → the phase's own notes (frozen, correctable) →
a commit message (**cannot be corrected after the merge**, only annotated elsewhere).

---

## The claims that must be re-verified by reading the source

**Named individually, never as a category.** Each was checked once by whoever wrote it, which is the
weakest verification available. **Read the artefact, not the note's account of the artefact.**

1. **`load_dotenv()` never read the working directory**, and `load_dotenv(args.config.parent /
   ".env")` fixes it. `notes-review-plan.md` and `evidence/env-discovery-probe.md`.
2. **`init` returns before `load_config`, and `--version` before dispatch.** `cli.py`'s `main()`.
3. **Both templates are byte-identical to the repository's `config.yaml` and `.env.example`**, and a
   test pins each. `tests/test_cli_init.py`.
4. **Both templates ship inside the wheel with no build configuration** — no
   `[tool.uv.build-backend]`, no `MANIFEST.in`. `evidence/wheel-contents.md`.
5. **`README.md`'s test count, phase counts and version string.** 448, seven, four, `0.1.0`.
6. **`README.md`'s `--help` block is the shipped one**, not a paraphrase.
7. **`README.md`'s `body_max_bytes` caveat** says calls go *unstored*, never that bodies are
   truncated — `corpus.py`.
8. **`README.md`'s "no retries of its own".**
9. **`README.md`'s `BUG-001` summary** — 2.8× larger, 0.6 seconds later — against
   `docs/bugs/BUG-001-*.md`.
10. **`uv tool install` needs no `--force`, and `uv tool upgrade` prints "Nothing to upgrade" while
    installing changed code.** `notes-group-d.md`. **Do not re-run these; check that what is written
    matches what the notes record was observed.**
11. **The brief is byte-identical to `README.md` at `5895359`, 1027 bytes**, and the capture's
    header says which commit "as written" means.
12. **Task 14's sweep** — 38 elements, 33 inherited, five dropped, the `docs/` pointer appearing
    once.
13. **"Two of its four `src/` changes are defects"** — in `implementation-plan.md` and
    `notes-group-c.md`. *This number was wrong once already and was corrected; the correction is
    what needs checking now.*
14. **`status.md`'s Milestone 2 count is four in every place it appears.**
15. **The `README.md` caveats section is four items**, per settled row 6.
16. **`IDM-001`'s amendment** — that adding a backlog item is how a phase declines scope — against
    what `notes.md` says was decided.

---

## The instruments, and what each would look like if it were vacuous

**A green check is a claim under review, not a reason to skip one.** This milestone has three
precedents: Phase 11 found **twelve tests comparing the code to itself**, and Phase 12 had **three
tools report something untrue without failing** — `uvx --from` served a stale build and exited 0 for
code that had not shipped, `$?` after a pipe reported the wrong command's status, and `uv tool
upgrade` installs changed code while printing "Nothing to upgrade".

| Instrument | The vacuity question |
|---|---|
| `tests/test_cli_init.py`, 7 tests | Does each one fail if the behaviour it names is removed? The notes claim three mutations produced exactly three failures — **check the mutations were the ones described** |
| `evidence/register-check.py`, 28 checks | Same question. It was mutation-tested on three targets; are the other 25 assertions capable of failing? **Are any comparing a file to itself?** |
| `make test`, 448 | Does the count include the seven new tests, and do they test `init`/`--version`/`.env` rather than argparse? |
| `make lint`, clean | **It cannot see column width.** Its silence says nothing about `E501` |
| `link-check.py` | Its exit code carries no information and its count is worktree-dependent |
| `branch-index.py --check` | Does it exit 0 *because* the state is right, or because this branch is unmerged and it skips it? |
| the driven runs in `notes-group-b.md` and `-d.md` | Was each result read, or inferred from an exit code? The stale-build incident is the precedent |

---

## Known false positives — do not spend findings on these

- **`link-check.py` reports 109 broken links and that is expected.** Phase plans legitimately cite
  files they will create; `.claude/settings.local.json` is untracked **by policy**, so the count
  differs between worktrees; and `./logs/` is reported broken where `logs/` is not, because the
  runtime exemption keys on a path's first segment. All recorded in `backlog.md`.
- **Table rows longer than 100 characters are correct.** The 100-column rule is for prose.
- **`IDM-001`'s placeholder grep matches sentences that state the rule** — `IDM-001` itself,
  `EPD-004`, and notes describing past instances. Those are mentions, not uses.
- **The same is true of the `❓` marker** in `plan.md`'s register preamble and exit criterion.
- **`implementation-plan.md`'s steps 3 and 5 read "not started" and genuinely are.**
- **`logs/` is absent from this worktree and that is correct** — it is per-worktree and gitignored.
- **The corpus day folders live only in `to-run-server/`.** Their absence here is not a defect.

---

## The rules — copied in, not cited

**1 · Read-only.** The review returns a work list and changes nothing — no file, no tree, no
machine. **If you run anything, read `git status` afterwards.** An interrupted mutation sweep once
left a module comment-stripped with the suite passing 427/427.

**2 · Every finding is labelled `VERIFIED` or `REPORTED`.** VERIFIED means you opened the file and
confirmed it. REPORTED means suspected. **A review that does not label cannot be triaged.**

**3 · Findings and questions go in separate sections.** A finding is a defect with evidence. A
question is for the owner to decide.

**4 · Nothing found is a complete answer.** A phase that must produce findings will manufacture
them. Say what you checked and found correct. **Refusals are first-class.**

**5 · A settled decision may be questioned, never filed as a defect.** It goes in the questions
section with the reasoning.

**6 · Every finding carries its blast radius** — see the ranking above. That is what orders the
list.

---

## The output

One report. Each finding:

```
[VERIFIED|REPORTED]  <one-line claim>
  Where:     file:line
  Evidence:  what was read, and what it said
  Reach:     where this claim already appears, and what acts on it
```

Then **questions**, numbered, each with what it would change. Then **reproducibility** — which
claims you could re-derive and which you had to take on trust. Then **what was checked and found
correct**, which is what makes *nothing found* usable rather than empty.

---

## Reading budget

**About 2,500 lines of documentation and 900 of code and tests.** The largest single files are
`cli.py` (704), `README.md` (310), `tests/test_cli_init.py` (171), `notes-group-d.md` (186),
`plan.md` (187) and `notes-review-plan.md` (121).

**Read by section, not whole.** `grep -n '^## '` first. **Do not read `../../backlog.md` or
`../../status.md` end to end** — grep them for the claims named above; they are long and most of
what is in them predates this phase.

**If you run out of room, say so and name what you did not reach.** An honest gap is worth more than
a skim, and this review's whole subject is claims that nobody checked.
