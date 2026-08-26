# Phase 11 — charter for the forward review

**Written 2026-08-26 on `feat/phase-11-corpus-tools`, before the review ran.** The protocol is
`../../method/IDM-004-reviewing-unexecuted-work.md`, which did not exist when Phase 10's charter was
written and now does. **Its first rule is that the charter decides what the review finds**, which is
why this file is written before anything is read rather than after.

*Fourth document in a phase folder, where `../../README.md`'s template names three. It is a file
rather than a section of `notes.md` because **it is handed to another agent verbatim**, and a thing you
hand over should be a file. `IDM-004` settled that; Phase 10's charter only proposed it.*

---

## What is under review

**`plan.md` as revised and committed at `2d04840` on 2026-08-26** — the ratification revision. Not the
version any earlier session saw. Concretely:

- **The unexecuted tasks: 2, 3, 4, 7 of Group A, and all of Groups B to F — tasks 8 to 25.**
- **The design sections they rest on**: "What is settled, and by whom", "The re-derivation before
  Task 1", "The question this phase closes", "The shape", "Non-goals".
- **The register**, sections 1 to 8. `../../method/IDM-008-the-register.md` says the register is the
  instrument; on its one prior run it caught a defect two forward-review passes had read past.
- **`notes.md`**, to the extent tasks 2–25 depend on it.

**Out of scope, and this is instruction rather than judgement:**

- **Tasks 1, 5 and 6.** They executed, ahead of the plan, on the owner's instruction. The plan records
  that rather than proposing it. **Reviewing them is the closing review's job.**
- **Phases 1 to 10.** Closed, merged, harvested.
- **The history of how a decision was reached.** The ratification exchange of 2026-08-26 is context for
  judging the plan, not a subject.
- **`../../backlog.md`, `../../../CLAUDE.md` and `status.md`.** They were edited in the same commit and
  they are not the subject. *If the plan contradicts one of them, that is in scope — as a contradiction
  in the plan.*

---

## Two runs, two questions

**They run in parallel and independently.** If the author went first it would quietly repair whatever
a cold reader would have stumbled on, **and the stumble is the signal.**

| Run | Its question |
|---|---|
| **The author** — this session | *Is this consistent with what was decided?* |
| **A cold reader** — fresh context | ***Could you execute this from the document alone? Name every place you had to guess.*** The guesses are findings |

**The cold run is a fitness test.** Sessions here are cleared deliberately, so **the next person to
execute this document is a cold reader.** A plan legible only to its author is already broken for its
purpose, and this run measures exactly that.

### One way this review departs from `IDM-004`, and it must be accounted for at reconciliation

**`IDM-004` assumes the author run is performed by the session that wrote the document, "because it
holds the reasoning". That session is gone.** This one is its successor by handoff: it has read
`plan.md`, `status.md` and the register, and it performed the 2026-08-26 ratification and revision —
but it did not hold the 2026-08-24 interviews that produced positions 1–6.

**So the author run here is weaker than the protocol assumes.** It can check the plan against the
written record. It cannot see reasoning that was never written down. **The overlap figure this review
produces is therefore not comparable with Phase 10's 18%**, and must not be recorded as if it were.

---

## What to look for

| | Looks like, in this document |
|---|---|
| **Gap** | A task whose "done" cannot be determined; a dependency no task satisfies; something the design needs that no task builds |
| **Incorrect** | A claim about `src/`, about the corpus on disk, about the viewer, or about a measurement, that is false. **Re-read the source rather than trusting the plan's summary of it** |
| **Leftover** | Scaffolding from a rejected option. **Read the false-positive list first** — this revision deliberately keeps records of superseded options, and they are not leftovers |
| **Contradiction** | Two statements that cannot both be true, especially across `plan.md`'s prose and its register, which overlap by design |
| **Unanswered question** | A `❓` that was closed with a value that does not actually answer it; a decision the plan assumes was taken and was not |
| **Concern** | The design is legal and you think it will hurt. **Questions section, not findings** |

---

## The rules

**1 · Read-only.** The review returns a work list and edits nothing. Fixing what you find destroys both
the ability to judge the finding and the record of what a cold reader misread.

**2 · Label every finding `VERIFIED` or `REPORTED`.** `VERIFIED` means you opened the file and
confirmed it. `REPORTED` means you suspect it and did not confirm. **A review that does not label
cannot be triaged.**

**3 · Findings and questions are different sections.** A finding is a defect with evidence. A question
is for the owner to decide. Mixing them turns a question into a to-do nobody chose.

**4 · Nothing found is a complete answer.** *A phase that must produce findings will manufacture them.*
Say what you checked and that it was correct. **Refusals are first-class.**

**5 · A settled decision may be questioned, never filed as a defect.** **Fourteen positions** are
settled in `plan.md`'s table, every one owned and dated — eight on 2026-08-24, six on 2026-08-26. If
one looks wrong, that is a **question**, with your reasoning. A reviewer without the record of how a
decision was reached has less information than the decision had.

**6 · Every finding carries what it would cost to be wrong** — discovered now, against discovered after
task N. That is the ranking, and it is the only one that survives disagreement about severity.

---

## The claims that must be re-verified by reading the source

**Do not take these from the plan.** Each is load-bearing, and each was checked once by whoever wrote
it — the weakest verification available.

| Claim | Where the plan rests on it |
|---|---|
| **Requests are cumulative — request *N* of a session carries turns 1..*N*** | **The converter's entire design.** Delta reconstruction, finding 5, the cross-day error, and task 12 all collapse if this is not exactly true. **It has never been checked against a stored body** — it is inferred from how the API works. Open a real request blob |
| Today's `--extract` writes no files — it reads, verifies, reports | Why `--verify-only` was struck as naming the default, and why `verify-archive` is a separate command |
| `--extract` runs **before** the config is loaded and reads only the day folder | The self-containment guarantee the extractor is said to keep executable |
| `observe.py:316–317` read `session_id`/`agent_id` from request **headers**; `observe.py:40` says `agent_id` arrives only on a subagent's call | Finding 3, the `--agent` reinstatement, and the prediction the review run tests |
| `stream` is `true` on 105 and `false` on 63 of 168 `/v1/messages` rows | Task 11's claim that the converter needs a plain-JSON path as well as SSE |
| The index has **26 columns**, and their names and order | Everything the extractor selects on. Register §3 |
| A streamed reply is stored as SSE and a buffered one as JSON | Register §7's `.sse`/`.json` extension rule, which claims the encoding is legible from the filename |
| `CorpusReader`'s surface — `directions()`, `blobs()`, `read()` | What the extractor and converter build on rather than reimplement |
| Register §6's collision list is complete and current | The register's own purpose |
| `reference/corpus.md:110` and `:193` say what the plan says they say | The phase's premise, and the no-headline-ratio rule |
| The viewer reads `<root>/projects/<project>/<session>.jsonl` and supports custom Claude directories | Register §7, position 12, and the whole output layout |

---

## Known false positives — do not spend findings on these

**Handed over deliberately.** `../../backlog.md` records that a phase plan citing files it will create
is a **recurring** false-positive class; Phase 8's plan contributed twenty-three.

- **Three forward citations** in the register: `src/ilirium_llm_router/extract.py`, `transcript.py`,
  `jsonl.py`. Created by Groups B–D. `link-check.py` reports them broken and **that is correct
  behaviour.**
- **`link-check.py` never reports zero.** **86 broken, 2 roundabout** on this branch at `2d04840`,
  unchanged by the ratification revision. **Do not predict the count — run the tool.**
- **A fresh worktree reports 13 more broken links than this one.** `.claude/settings.local.json` is
  gitignored, so `git worktree add` does not create it, and a path in backticks is a link here.
  **Artefact, not regression.**
- **The plan deliberately records superseded options rather than deleting them.** `--to-jsonl`,
  `--verify-only`, `--day` as an option, `to-jsonl` as a command, `corpus-<day>` as the project name,
  "three modules or two", and finding 2's undicted heading. **Every surviving mention sits inside a
  correction record saying what was rejected and why.** They will read as leftovers. They are not.
  *A finding is warranted only if a superseded spelling appears somewhere it is still presented as
  current.*
- **Tasks 1, 5 and 6 say they are already executed.** Deliberate, recorded in "Placeholders in this
  file", and out of scope.
- **`agent_id` is empty on all 770 captured rows.** A measured fact, not a defect, and the plan says
  what it means.
- **`link-check.py`'s file count reads 96 here against the 84 recorded in `status.md`.** Known,
  unexplained, and **not a plan defect** — the broken count is the comparable one and it did not move.
  Do not spend a finding on it. *An explanation, if you happen to find one, is welcome as a question.*

---

## What the cold reader is given

Enough to work, and nothing that says what to conclude:

1. **`plan.md` and `notes.md` in full**, and this charter.
2. **The repository, read-only** — it must read `src/`, `tests/`, `config.yaml`, `pyproject.toml` and
   the `docs/` tiers for itself.
3. **The corpus on disk**, read-only: `to-run-server/logs/corpus/` and `main/logs/corpus-gate/`. **The
   claims above about cumulative requests, stream counts and index columns can only be settled there.**
4. **The pointers a cold session gets**: `CLAUDE.md`, `../../README.md`, `../../method/IDM-001`,
   `IDM-004`, `IDM-008`, `../../reference/design-decisions.md`, `../../reference/corpus.md`,
   `../../reference/observability.md`.

**It is not given** a summary of what is believed true, a list of suspected weak points, or any
indication of which sections are thought fragile. Those would be the answer key.

**It must not write anything, run the router, start a server, or modify the corpus.** Reading the
corpus is required; changing it is out of bounds.

---

## The output

One document per run, then a reconciliation. Each finding:

```
[VERIFIED|REPORTED]  <one-line claim>
  Where:     file:line
  Evidence:  what was read, and what it said
  Cost:      what it costs to find this after task N instead of now
```

Then a **separate numbered list of questions**, each with what it would change. Then an
**executability** section — task by task, could a cold reader run it, and every place a guess was
needed. Then **what was checked and found correct**, which is what makes *nothing found* usable rather
than empty.

---

## A second thing this run produces, which is not the review

**The cold run is a subagent, and its calls pass through a capturing router.** `plan.md`'s finding 3
states the prediction before the fact:

> **After the cold run, `2026-08-26/index.csv` column 3 must hold at least one non-empty value.**
> If it is still empty on every row, `observe.py:40` is wrong, `--agent` cannot be built, and the
> phase has found a defect instead of a feature.

**This asks nothing of the reviewer** — it cannot affect whether its own requests carry a header. It is
recorded here so the author does not forget to look, and so the result is not mistaken afterwards for
something the review set out to find.

---

## Done when

Both runs have returned; **their disagreements are named rather than silently resolved**; findings are
separated from questions; every finding carries a verdict, evidence and a cost; **every refuted finding
was re-checked against the source before being accepted** — a reviewer can be confidently wrong; and
the merged work list is in `notes.md` with what was accepted, what was refused, **and why each refusal
was refused**, or the next review re-raises it.
