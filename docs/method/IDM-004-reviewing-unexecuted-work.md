# IDM-004 — Reviewing work that has not happened yet

**In force 2026-08-18.** Written after running it once, on Phase 10's plan, and from what that cost
rather than from what it seemed like it should be. `IDM-006-closing-a-milestone.md`'s step 9 — *write
this playbook last, from what it cost* — is why it did not exist before that run.

---

## What this is, and what it is not

**A forward review examines work that has not happened.** `../README.md` already specifies a
**closing** review — executed work, at a milestone's end, with a checklist. Two review protocols in
one repository will be confused unless the line is drawn first, so it is drawn here.

| | Closing review | Forward review |
|---|---|---|
| Subject | work that ran | **work that has not** |
| Asks | did it do what it said, and is what it found true? | **will it work, and can somebody else run it?** |
| Outcome | findings harvested into `../reference/` | **a work list against a document nobody has acted on** |
| Home | `../README.md`, "The review phase" | this file |
| Cost of a miss | a wrong fact in the durable tier | **a phase built on a gap** |

**It applies to any unexecuted, forward-looking document** — a phase plan, a milestone
`implementation-plan.md`, a proposal in `../epd/`. The test is whether the document describes work
nobody has done yet.

## When to run one

**When the cost of executing a wrong plan exceeds the cost of reading it twice.** In practice: before
a plan's first substantial task, and after any round of revision large enough that nobody holds the
whole document in their head any more.

**Not after every edit.** A review is expensive and its findings decay; run it once, against a
document that is finished enough to be wrong.

---

## Iteration 1 — derive the charter, before reviewing anything

**The charter decides what the review finds. This is the whole of why the iteration exists.**

The evidence is in this repository and it is unambiguous. `../README.md` records a fresh-context
review that verified eleven citations line for line and **missed the defect anyway**:

> *"It was wrong, and it survived a fresh-context review that verified all eleven citations line for
> line — **because that review checked the citations existed, not what they would need.**"*

**A reviewer told "review this" verifies what is easy to verify and returns a tidy list that misses
the thing that matters.** So the first iteration is not review; it is deciding what question is being
asked.

**A charter is a document, not a paragraph**, because it is handed to another agent verbatim and a
thing you hand over should be a file. It states:

| | |
|---|---|
| **Scope** | What is under review, and — as explicitly — **what is not.** Executed work is out; so is the history of how a decision was reached |
| **The two questions** | One per run. See iteration 2 |
| **What to look for** | Gaps, incorrect points, leftovers, contradictions, unanswered questions, concerns — each defined in terms of what it looks like *in this document* |
| **The claims to re-verify by reading the source** | Named individually, never as a category. Each was checked once by whoever wrote the document, which is the weakest verification available |
| **Known false positives** | Handed over, so findings are not spent on them |
| **The rules** | Below. Copied in, not cited |
| **The output shape** | Below |

**Naming the false positives is not a courtesy.** A reviewer that spends its attention on a
recurring, already-understood false positive has spent the budget you were paying for.

---

## Iteration 2 — two runs, in parallel, then reconcile

**They ask different questions. Neither is optional and neither substitutes for the other.**

| Run | The question it answers |
|---|---|
| **The author** — the session that wrote the document | *Is this consistent with what was decided?* It holds the reasoning, so it can see a contradiction with a decision, or a question raised and never closed. **It cannot see its own blind spots** |
| **A cold reader** — a fresh-context agent | *Is this executable by somebody who was not here?* |

### The cold run is a fitness test, not merely an independent check

**This is the reframing that makes it worth its cost.** Where sessions are cleared deliberately and
handoff notes are not kept, **the next person to execute the document is a cold reader.** So a
document legible only to its author is **already broken for its purpose**, and the cold run measures
exactly that.

That changes what the cold reader should be asked. Not only *is this true*, but: **could you execute
this from the document alone? Name every place you had to guess.** The guesses are findings.

### Parallel, not serial

**If the author goes first it will quietly repair whatever a cold reader would have stumbled on, and
the stumble is the signal.** Run both against the same unmodified document.

The author may *record* findings while the cold run is in flight — writing them down changes nothing
a reader sees — but **it must not fix anything** until both have returned.

### Reconciliation is the author's job

Because it holds the reasoning needed to judge which findings are real. Two rules:

- **Where the runs disagree, that is itself a finding** — usually about legibility rather than
  correctness.
- **Verify a refutation before accepting it.** A reviewer can be confidently wrong. When the first
  run of this protocol refuted one of the author's claims, the refutation was re-checked against the
  source and the frozen evidence before anything was rewritten. It held; the discipline is not
  conditional on that.

---

## The rules

**1 · Read-only.** A review returns a work list and edits nothing. Fixing what you find destroys both
the ability to judge the finding and the record of what a cold reader misread.

**2 · Every finding is labelled `VERIFIED` or `REPORTED`.** VERIFIED means the file was opened and the
claim confirmed. REPORTED means suspected and not confirmed. **A review that does not label cannot be
triaged**, and the split is what made this repository's earlier fresh-context review usable at all.

**3 · Findings and questions are separate sections.** A finding is a defect with evidence. A question
is for the owner to decide. Mixing them turns a question into a to-do nobody chose.

**4 · Nothing found is a complete answer.** `../README.md`: *a phase that must produce findings will
manufacture them.* The reviewer says what it checked and that it was correct. **Refusals are
first-class.**

**5 · A settled decision may be questioned, never filed as a defect.** It goes in the questions
section with the reasoning. A reviewer without the record of how a decision was reached has less
information than the decision had.

**6 · Every finding carries what it would cost to be wrong** — discovered now, against discovered
after task N. That is what ranks the list, and it is the only ranking that survives disagreement
about severity.

---

## The output

One report per run, then a reconciliation. Each finding:

```
[VERIFIED|REPORTED]  <one-line claim>
  Where:     file:line
  Evidence:  what was read, and what it said
  Cost:      what it costs to find this after task N instead of now
```

Then a separate numbered list of questions, each with what it would change. Then an **executability**
section — task by task, could a cold reader run it, and every place a guess was needed. Then **what
was checked and found correct**, which is what makes *nothing found* usable rather than empty.

**The merged work list goes in the document's own notes**, with what was accepted, what was refused,
and why. **A refused finding is recorded with its reason**, or it is re-raised by the next review.

---

## What the first run cost, and what it returned

**Measured on Phase 10's plan, 2026-08-18** — the only run this document has to go on, and the reason
it exists.

| | |
|---|---|
| Subject | one plan and its notes, ~1,400 lines, twenty-one unexecuted tasks |
| Runs | the author, and one fresh-context agent, read-only |
| Cold run's cost | ~152k tokens, 35 tool calls, ~10 minutes |
| Findings | **22 distinct.** 15 by the cold reader alone, 3 by the author alone, **4 by both** |
| Overlap | **18%** |

**The overlap is the number that justifies two runs.** At 18%, a single run of either kind would have
missed most of what was found.

**And the split fell exactly along the predicted line.** The author's unique findings were all about
*the record* — a rule in the filing manual nobody had applied, a precedent already decided elsewhere,
an index convention. Those need knowing what was decided. **The cold reader's unique findings were
about what the author could not un-know**, including three that would have silently produced working
code doing the wrong thing.

### The finding that justifies the protocol on its own

**A claim the author had inferred, labelled honestly as inferred, and written into four documents —
including the repository's backlog — was false.** It had been generalised from a code comment about a
narrow case to the general case, without checking measured evidence that named exactly that case and
sat in the reference tier.

Three things about it are worth carrying:

- **Labelling an inference does not protect it.** *Inferred* was the correct label. Inference from a
  correct premise to a wrong conclusion is not repaired by labelling it.
- **The author could not have found it**, having made it twice more since. The cold reader found it by
  reading the code instead of the document's account of the code — which is rule 1 of any charter's
  re-verification list.
- **It had already propagated.** By the time it was caught it was in a plan, twice in a note, and in
  the inventory a future session acts on. **A wrong claim spreads at the speed of citation**, which is
  why the review comes before execution rather than after.

### One thing that is not evidence yet

**n = 1.** The 18% overlap, the cost, and the shape of the split are one measurement of one review of
one document by one agent. **The protocol is written from it; the numbers are not a rule.** A second
run that returned 60% overlap would be evidence that one run is enough, and this section would need
rewriting rather than defending.

---

## Provenance

- **`../README.md`, "The review phase"** — the closing review, whose *refusals are first-class* and
  *a phase that must produce findings will manufacture them* are inherited here whole. The boundary
  between the two protocols is stated above rather than in that file, because a reader arriving at a
  plan is holding this one.
- **`IDM-006-closing-a-milestone.md`, step 9** — *write this playbook last, from what it cost*, which
  is why this document was written after the first run and not before it. The owner chose that ordering
  explicitly on 2026-08-18, against the alternative of specifying the protocol first. *(That rule was
  in `../README.md`'s closing playbook until 2026-08-20.)*
- **`IDM-006-closing-a-milestone.md`, step 8's record of a fresh-context review that verified the
  wrong thing** — the single piece of evidence that iteration 1 exists to answer. *(In `../README.md`'s
  closing playbook until 2026-08-20.)*
- **`IDM-000`** — the tier's conventions, and the admission test this document passes: it contains no
  fact about the router, and every rule in it survives a change of subject.
- **First run:** `../milestone-2-corpus/phase-10-body-store/review-charter.md` is the worked example
  of a charter; that phase's `notes.md` holds both reports and the reconciliation.
