# Phase 10 — charter for the forward review

**Written 2026-08-18 on `feat/phase-10-body-store`, before the review ran. Task 3a.**

> **The review has since run, and this file is now a worked example rather than an instruction.** Both
> passes and their reconciliation are in `notes.md` under Task 3a; the twenty-two findings are applied;
> and `../../method/IDM-004-reviewing-unexecuted-work.md` is the general protocol written from what it
> cost. **Nothing below was edited afterwards** — it is what the reviewers were actually given.

**A forward review examines work that has not happened yet.** `../../README.md` already specifies a
**closing** review — executed work, at a milestone's end, with a checklist. This is the other one, and
confusing the two is the first thing this document exists to prevent.

| | Closing review | **This** |
|---|---|---|
| Subject | work that ran | **work that has not** |
| Asks | did it do what it said, and is what it found true? | **will it work, and can somebody else run it?** |
| Home | `../../README.md`, "The review phase" | this file, and `method/IDM-004` once it is written |

*This file is a fourth document in a phase folder, where `../../README.md`'s template names three. It
is separate rather than a section of `notes.md` because **it is handed to another agent verbatim**, and
a thing you hand over should be a file. Whether that becomes the general rule is `IDM-004`'s to settle,
after this review has run once.*

---

## What is in scope

**The unexecuted remainder of `plan.md`: Tasks 4 to 24, Groups B to F, and the design sections they
rest on.** Concretely, everything in `plan.md` except the Record table, plus everything in `notes.md`
that Tasks 4–24 depend on.

**What is out of scope, and this is the owner's instruction rather than a judgement call:**

- **Tasks 1, 2 and 3.** They executed. Their output is this branch's four documents, and reviewing
  them is the closing review's job.
- **Phases 1 to 9.** Closed, merged, and their findings already harvested.
- **The history of how a decision was reached.** The three interview records in `notes.md` are context
  for judging the *plan*, not subjects themselves.

---

## Two runs, asking two different questions

They run **in parallel and independently**. If this session went first it would quietly repair
whatever a cold reader would have stumbled on, and **that stumble is the signal.**

| Run | The question it answers |
|---|---|
| **This session** | *Is this plan consistent with what was decided?* It holds three interviews' reasoning, so it can see a contradiction with a decision, or a question raised and never closed. **It cannot see its own blind spots** — it wrote the thing |
| **A fresh-context agent** | *Is this plan executable by someone who was not here?* |

**The second is a fitness test, not merely an independent check.** This repository's sessions are
cleared deliberately and no handoff notes are kept, so **the next session is a fresh agent**. A plan
legible only to its author is already broken for its purpose, and this run measures exactly that.

**Reconciliation is this session's job**, because it holds the reasoning needed to judge which
findings are real. **Where the two runs disagree, that is itself a finding** — usually about
legibility rather than about correctness.

---

## What to look for

The owner's list, unabridged: **gaps, incorrect points, leftovers, contradictions, issues,
unanswered questions, concerns.** Sharpened into what each means here:

| | Looks like |
|---|---|
| **Gap** | A task whose "done" cannot be determined; a dependency no task satisfies; a thing the design needs that no task builds |
| **Incorrect** | A claim about `src/`, about a tool, or about a measurement that is false. **Re-read the file rather than trusting the plan's summary of it** |
| **Leftover** | Scaffolding from an option that was rejected. **This has happened twice already** — a root `dicts/` folder that existed only to serve hard links, and two "Documented versus measured" rows that outlived the same decision |
| **Contradiction** | Two statements that cannot both be true, especially across `plan.md` and `notes.md`, which overlap by design |
| **Unanswered question** | Something raised in an interview and never closed, or a decision the plan assumes was taken and was not |
| **Concern** | The design is legal and you think it will hurt. **Goes in the questions section, not the findings section** |

---

## The rules of the review

**1. Read-only.** The review returns a work list and edits nothing. Fixing what you find destroys both
the ability to judge the finding and the record of what a cold reader misread.

**2. Label every finding `VERIFIED` or `REPORTED`.** `VERIFIED` means you opened the file and
confirmed it. `REPORTED` means you suspect it and did not confirm. **Phase 7's fresh-context review
returned five verified and roughly twenty-five reported**, and that split is what made it triageable.
A review that does not label cannot be acted on.

**3. Findings and questions are different sections.** A finding is a defect with evidence. A question
is for the owner to decide. Mixing them turns a question into a to-do nobody chose.

**4. Nothing found is a complete answer.** `../../README.md`: *a phase that must produce findings will
manufacture them.* Say what you checked and that it was correct. **Refusals are first-class.**

**5. Settled decisions may be questioned, never filed as defects.** Four decisions were taken across
three interviews — capture opt-in and off by default, no headers ever, one worker thread pending
measurement, plain dictionary copies in self-contained day folders — plus `zstandard` as a dependency,
a configurable level, and a scope with no live session. **If one looks wrong, that goes in the
questions section with your reasoning.** A reviewer without the interview record has less information
than the decision had.

**6. Every finding carries what it would cost to be wrong.** A defect that a test would catch in
Group C is worth less attention than one that is only discoverable after Group F.

---

## The claims about `src/` that must be re-verified by reading `src/`

**Do not take these from the plan.** Each is load-bearing, and each was checked once by the session
that wrote it — which is the weakest possible verification.

| Claim | Where the plan uses it |
|---|---|
| `Proxy.record()` has exactly four call sites, and every path that produces a CSV row reaches one | The whole hook-point design. If false, the corpus repeats Phase 9's 9-of-158 gap |
| A caller vanishing after response headers reaches **none** of them, so that call gets no row today | The named blind spot, and a `backlog.md` item |
| `proxy.py` reads the whole request body into memory before relaying it | Why the ceiling does not bound request memory |
| `proxy.py`'s relay loop never accumulates the response | Why whole-response buffering is **new** with the corpus |
| `observe.py`'s `BufferedScanner` accumulates to `MAX_SCAN_BYTES` and then gives up | The double-buffer question, Q11 |
| `stats.py` rides `RotatingFileHandler`, whose lock is a thread lock | Why multi-process is blocked on the writers |
| `config.py` sets `extra="forbid"` on every config model, and resolves relative paths against the config file's directory | Two rows of the configuration check |
| `stats.py`'s `COLUMNS` has 20 entries, and a test asserts header and values agree | The index's "first twenty identical, in order" claim |

---

## Known false positives — do not spend findings on these

**Handed over deliberately.** `../../backlog.md` records that a phase plan citing files it will create
is a **recurring** false-positive class; Phase 8's plan contributed twenty-three.

- **Four forward citations** in `plan.md`: `src/ilirium_llm_router/corpus.py`, `docs/reference/corpus.md`,
  `docs/procedures/corpus-benchmark/`, `docs/procedures/corpus-dictionary/`. All are created by
  Tasks 8, 19, 5 and 14. `link-check.py` reports them as broken and that is correct behaviour.
- **`link-check.py` does not report zero**, ever. 68 broken and 2 roundabout on `main`; 78 on this
  branch. Its own docstring says which hits are correct and permanent. **Do not predict the count —
  run the tool.**
- **Two deliberate absences** outside the archive: `.claude/agents/local-helper.md` and
  `docs/procedures/closing-a-milestone.md`. Both are named *in order to say they do not exist*.
- **Historical references to superseded options** — `os.link`, hard links, APFS clones, a root
  `dicts/`, "22 columns", `Group B0`, `3a`/`3b`/`3c` as task labels. Every surviving mention sits
  inside a decision record describing what was rejected. **A mechanical pass on 2026-08-18 confirmed
  this** and found exactly one real leftover, a prose count.

---

## What the fresh agent is given

Enough to work, and nothing that tells it what to conclude:

1. **`plan.md` and `notes.md` in full**, and this file.
2. **The repository**, read-only — it must read `src/`, `config.yaml`, `pyproject.toml`, `tests/` and
   the `docs/` tiers for itself.
3. **The pointers a cold session gets**: `CLAUDE.md`, `../../README.md`, `../../method/IDM-001-git-branching.md`,
   `../../reference/design-decisions.md`, `../../reference/observability.md`,
   `../../epd/EPD-003-capturing-bodies-for-a-corpus.md`, and `../phase-9-corpus-gate/`.
4. **This charter's scope, rules and false-positive list.**

**It is not given** a summary of what is thought to be true, a list of suspected problems, or any
indication of which parts are considered weak. Those would be the answer key.

---

## The output

One document per run, then a reconciliation. Each finding:

```
[VERIFIED|REPORTED]  <one-line claim>
  Where:     file:line
  Evidence:  what was read, and what it said
  Cost:      what it would cost to discover this after Task N instead of now
```

Questions for the owner are a separate numbered list, each with the reasoning and what it would change.

**And a closing statement of what was checked and found correct** — which is the part that makes
*nothing found* a usable answer rather than an empty one.

---

## Done when

Both runs have returned; their disagreements are named rather than silently resolved; findings are
separated from questions; every finding carries a verdict, evidence and a cost; and the work list is
in `notes.md` under Task 3a with what was accepted, what was refused, and why.

**Then, and only then, `IDM-004` is written from what this cost** — per the closing playbook's own
rule, *write this playbook last* (`../../README.md` when this was written;
`../../method/IDM-006-closing-a-milestone.md` step 9 from 2026-08-20), and `IDM-000`'s requirement
that a method document be evidenced from this repository rather than guessed.
