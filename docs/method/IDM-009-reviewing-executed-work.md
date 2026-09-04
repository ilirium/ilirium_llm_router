# IDM-009 — Reviewing work that has happened

**In force 2026-09-04.** Written after running it once, on Phase 12 as executed, and from what that
cost rather than from what it seemed like it should be. `IDM-006-closing-a-milestone.md`'s step 9 —
*write this playbook last, from what it cost* — is why it did not exist before that run, and why the
document that argued for it was deliberately not written as an `IDM`.

**Read `IDM-004-reviewing-unexecuted-work.md` first if you have not.** This document is its sibling
and states only what differs; everything it inherits is named rather than restated, so that one
change lands in one place.

---

## What this is, and the line between three protocols

**There are three review protocols in this repository and they will be confused unless the line is
drawn first.**

| | Closing review | Forward review | **This one** |
|---|---|---|---|
| Where | `../README.md`, "The review phase" | `IDM-004` | here |
| Subject | a **milestone's** executed work | a document nobody has acted on | **one phase's executed work** |
| Asks | did it do what it said, and is what it found true? | will it work, and can somebody else run it? | **did it do what it said, is what it claims true, and what has the claim already reached?** |
| Method | a checklist | charter, two parallel runs, reconciliation | **`IDM-004`'s method, against work that ran** |
| When | at a milestone's close | before a plan's first substantial task | **before the merge** |

**The closing review is not a substitute, and the reason is scale.** It is chartered over a whole
milestone, runs once, and is a checklist — the right instrument for *did every phase complete its
task list*, and the wrong one for *is this particular claim true*. Its own line **"re-derive every
quoted measurement from the frozen artefacts"** is a whole review's work when aimed at one phase and
one row of nine when aimed at a milestone.

**What is new here is not the subject but the method applied to it.** `IDM-004` contributed the
charter and the two parallel runs; `../README.md` contributed what to check in work that ran.
Neither had been pointed at a single phase.

## When to run one

**Before the merge.** *Settled by the owner on 2026-09-02, and this document inherits that decision
rather than reaching it.* Two reasons were given: after the merge a fix costs its own branch, and
**the merge commit message is itself a claim-bearing artefact that cannot be corrected afterwards**
— only annotated elsewhere. The argument against was that the phase stays open longer, and it was
heard and overruled.

**Not every phase.** The same test as `IDM-004`: when the cost of a wrong claim escaping exceeds the
cost of reading the work twice. A phase whose output is bounded and cited by nothing is not worth
a two-run review.

---

## What carries over from `IDM-004` unchanged

**Do not re-derive these. They are the parts about *reviewing*, not about *plans*.**

- **Iteration 1: the charter decides what the review finds.** This is **stronger** for executed
  work, not weaker — see below.
- **Two runs, in parallel, then reconcile.** The author records findings while the cold run is in
  flight and **fixes nothing** until both return.
- **`VERIFIED` / `REPORTED` on every finding.** A review that does not label cannot be triaged.
- **Findings and questions in separate sections.**
- **Nothing found is a complete answer. Refusals are first-class.**
- **A settled decision may be questioned, never filed as a defect.**
- **Reconciliation is the author's job, and a refutation is re-verified before it is accepted.**
- **A refused finding is recorded with its reason**, or the next review re-raises it.

**Why iteration 1 is stronger here.** Executed work offers far more easy-to-verify surface than a
plan does — tests pass, lint is clean, links resolve, a checker reports 28 of 28 — and **a reviewer
told "review this" will report the green.**

---

## What is different, and all of it follows from one thing

### 1 · The review may run the thing, and a forward review has nothing to run

A plan can only be read. A finished phase has a binary, a test suite, checkers, and a repository
whose state is itself a claim. `../README.md`'s closing checklist already says **"drive the software
live"**, and the first run is the argument for it: a defect in existing code was *predicted* by
reading a dependency's source and only became a fact when a probe with a control was run. **Reading
found it; running settled it.**

Two rules the forward protocol has no need of:

- **Running is not fixing.** The review changes nothing — and it now has to say so about a *tree*
  rather than only about a document. **`git status` is read after anything is run**, and what it
  printed goes in the report. The precedent is not hypothetical: an interrupted sweep once left a
  module comment-stripped with the suite passing 427/427.
- **Anything that touches the machine needs the owner's go-ahead, and the machine is left as
  found.** Installing something to check an instruction is a machine change, not a read. **A
  go-ahead is spent when the session that received it ends.**

### 2 · Every instrument the phase leaned on gets a vacuity question

**A failure class that cannot exist in a forward review: the phase's own evidence may be green and
empty.** The charter names each check the phase cites and asks, for each, **what would this look
like if it were vacuous?**

The evidence is not thin. One phase found **twelve tests comparing the code to itself** — invisible
to every other instrument. The next had **three tools report something untrue without failing**: a
runner served a stale build and exited 0 for code that had not shipped, `$?` after a pipe reported
the wrong command's status, and an upgrade command installed changed code while printing *"Nothing
to upgrade"*, because its summary compares version numbers rather than builds. **All three exited
0**, and only reading the output distinguished them.

**So a green check is a claim under review, not a reason to skip one.** Where the phase's own
instruments were mutation-tested, the review checks the mutation was real; where they were not, that
is a finding.

**And a mutation run has its own trap.** *Found by the first run:* **a batch of mutations can mask a
member of the batch.** Three were applied at once; one redirected where code wrote, a test then
overwrote the file a third mutation's comparison depended on, and that comparison became trivially
true — reporting a survivor that was not one. **Isolate, or read `git status` and disbelieve a
survivor.**

### 3 · Did the execution honour the settled table?

**Only a backward review can ask this, and it is not a formality.** The first run's phase carried a
settled row fixing a section at four items; what shipped had five, the fifth being the executing
session's own judgement — added for a good reason that was not its to act on.

**It was caught by a mechanical row-by-row check and by no amount of rereading.** So it is a named
pass: **the settled table, one row at a time, against what shipped.**

### 4 · Read the artefact, not its account of itself

`IDM-004` has this implicitly. **For executed work it is the primary axis**, because there are now
three things that can disagree — **the code, the tests, and the prose.** A forward review has only
prose.

### 5 · Rank by what the claim has already reached

**`IDM-004`'s rule 6 does not transfer.** *"What it costs to find this after task N"* is meaningless
when every task has run. The replacement is the other half of the same finding — **a wrong claim
spreads at the speed of citation** — so the ranking is **blast radius**:

| Reach | Why it ranks where it does |
|---|---|
| `../reference/`, `CLAUDE.md` | canon; read by every later session without being questioned |
| `../status.md`, `../backlog.md`, `method/` | acted on; a wrong item becomes scheduled work |
| a milestone's `implementation-plan.md` | shapes phases not yet planned |
| the phase's own notes | frozen record; wrong but bounded, and correctable by a later note |
| a commit message | **cannot be corrected after the merge**, only annotated elsewhere |

### 6 · The documents the phase edited outside its own folder are in scope

**This is where propagation happens and none of it is in the phase folder.** The first run's phase
changed eight documents outside its own, and **a review scoped to the phase folder would have missed
every one.** Those edits include the phase's *declines* — where it recorded that work would not be
done — and a decline is a claim too: the review checks it is a real decline and not a silent drop.

### 7 · Measure the run, because the next `IDM` is written from it

Record four things, every time:

- **Overlap between the two runs**, as a percentage of distinct findings.
- **Cold-run cost** — tokens, tool calls, wall clock.
- **Findings by how they were reachable**: only by running something, only by reading code, only by
  reading prose, only by holding the record. **This is the number that says whether the two-run
  split is the right split for executed work.**
- **How many findings the phase's own mechanical checks had already caught** — whether the review
  buys anything the checkers do not.

---

## What changes from `IDM-004`

- **"Executability" becomes "reproducibility".** `IDM-004` asks a cold reader *could you execute
  this from the document alone?* The executed-work equivalent is **could you re-derive these claims
  from what is in the repository?** Same instrument, different question: the guesses are still the
  findings, but they are now guesses about *where a number came from*.
- **The known-false-positive list stops being a courtesy and becomes load-bearing.** Executed work
  has a large recurring false-positive surface that will otherwise consume the whole budget.
- **The charter states the subject as a commit hash** — see below.

### Who "the author" is when a phase ran across several sessions

***Answered here; `IDM-004` never had to.*** Its author run is *the session that wrote the
document*, which assumes one.

**The author run is performed by whoever holds the phase's record, and it declares its gap by
group.** For a group it executed first-hand it is an author run; for a group it did not, it has the
notes and the commit messages and nothing else — **that is a warm read, and it is labelled as one,
per group, in the charter rather than discovered later in the findings.**

**Where no session executed any of it, there is no author run.** Two cold runs on different charters
is the obvious alternative and **it has never been tried**, so this document does not prescribe it.
Say so in the charter and record what the substitute cost.

### When the subject commit is named

***Answered here, from a finding the first run refused precisely so it would be.*** That run's
planning document named one commit range, its charter named another, and both runs read a third —
and the finding was **not** fixed, because editing either document to name a later hash makes it
wrong again the moment anything else lands. **The defect is naming a range in a document written
before the runs start.**

**So: the charter names the subject as a single commit hash, and each run verifies the subject is
unchanged at that hash before it begins** — `git diff` against it, reported. Anything that lands
afterwards is out of scope and is named in the reconciliation rather than silently included.

### What one measurement is worth

***Answered here, and the answer is a rule about evidence rather than a number.*** `IDM-004` records
its own figure and then says **n = 1, and the numbers are not a rule.** That stands, with three
measurements now in hand:

| Run | Kind | Overlap |
|---|---|---|
| `IDM-004`'s first, on a plan | forward | **18%** |
| Phase 12 as executed | **backward** | **11%** |
| Phase 13's plan | forward | **17%** |

**The forward figure has been measured twice and is stable; the backward figure once, and lower.**
Lower is evidence in the same direction — the two runs overlap *less* on executed work, so each is
buying more.

**What would change this document: a run returning materially higher overlap — say half the findings
in common.** That would be evidence that one run is enough, and this section would need **rewriting
rather than defending.** Report the four measurements of §7 every time; that is what makes the next
rewrite possible.

---

## The rules

**1 · Read-only, including the tree and the machine.** The review returns a work list and changes
nothing. **If you run anything, read `git status` afterwards and report what it printed.**

**2 · Every finding is labelled `VERIFIED` or `REPORTED`.**

**3 · Findings and questions go in separate sections.**

**4 · Nothing found is a complete answer.** Say what you checked and found correct. **Refusals are
first-class** — a review that fixes everything it found has no refusals by construction, which is a
warning sign rather than a clean result.

**5 · A settled decision may be questioned, never filed as a defect.**

**6 · Every finding carries its blast radius**, which is what orders the list.

## The output

One report per run, then a reconciliation. Each finding:

```
[VERIFIED|REPORTED]  <one-line claim>
  Where:     file:line
  Evidence:  what was read, and what it said
  Reach:     where this claim already appears, and what acts on it
```

Then **questions**, numbered, each with what it would change. Then **reproducibility** — which
claims could be re-derived and which had to be taken on trust. Then **what was checked and found
correct**.

**The merged work list goes in the phase's notes**, in its own file when the phase has more than one
review, with what was accepted, what was refused, and why.

**A finding becomes a question rather than a fix** when acting on it would reverse or narrow an
owner decision or a settled row, change anything in `method/`, need the machine, or grow the work
beyond a small documentation or code fix. *Deliberately conservative: **one method-tier or
settled-row finding stops the merge**, however clean everything else is.*

---

## What the first run cost, and what it returned

**Measured on Phase 12 as executed, 2026-09-02** — the only backward run this document has to go on.

| | |
|---|---|
| Subject | one phase: six non-documentation files, its folder, and eight documents it edited outside it |
| Runs | the author — warm on three groups of five — and one fresh-context agent, read-only |
| Findings | **18 distinct.** 12 by the cold reader alone, 4 by the author alone, **2 by both** |
| Overlap | **11%** |

**The split fell along the predicted line and further along it than expected.** The author found
things about *the record*; **the cold reader found what the author could not un-know**, including
the two highest-blast-radius findings, one of them in the canon tier.

### The finding that justifies the protocol on its own

**A file loaded into every session carried a count that the phase had been chartered to fix — and
the phase never opened it.**

The phase fixed two copies of that count and filed a backlog item describing the problem as living
in *"three places"*, every one of them inside a single file. The fourth copy sat in the one document
no session can avoid reading, and was stale by a whole phase.

Three things worth carrying:

- **The author could not have found it.** That session wrote the item saying the count lived in
  three places, having just fixed the two it knew about. **The framing was the blind spot.**
- **It changed which fix survived.** Of three candidate fixes on the backlog, only the one that
  works across two files remained; the others had been written as though one file were the whole
  problem.
- **The instance count was understated.** The phase called it the third instance. It was the fourth,
  and the worst.

### The question no mechanical check could have settled

The phase's own register check enforced a settled count and found the work carrying one item more.
The extra fact had been **moved rather than deleted** — out of the section the row counted and into
the section above it, one bullet away.

**Both states honoured the letter of the decision. Only one was what the decision was for**, and the
owner answered by **changing the row rather than the work**: the count had been a description of the
section at the time it was settled, not a budget.

**This is the shape of finding that pays for a review even when the fix is one line.** The check
enforced a number and could not see that the number had stopped describing the intent — and **no
mechanical check could have**, because the question is what the number was protecting, and only the
person who chose it knows.

---

## Provenance

- **`../milestone-2-corpus/phase-12-installer-and-readme/review-plan-jobs-done.md`** — the argument
  for this document, written 2026-09-02 and deliberately **not** written as an `IDM`, so that the
  rules could be derived from a run rather than guessed. Its settled table holds the owner decisions
  this document inherits.
- **The same folder's `review-charter-jobs-done.md`** — the worked example of a charter, handed to
  the cold reader verbatim; and **`notes-review-jobs-done.md`** — the first run's reconciliation and
  its measurements.
- **`IDM-004`** — the method this adapts. Where a rule here is silent, that one governs.
- **`IDM-006` step 9** — *write the playbook last, from what it cost.*
- **`../README.md`, "The review phase"** — the closing review, whose *refusals are first-class* and
  *a phase that must produce findings will manufacture them* are inherited whole.
- **`IDM-000`** — the tier's conventions, and the admission test this document passes: it contains
  no fact about the router, and every rule in it survives a change of subject.
- **On shape:** `IDM-000`'s two-zone split was considered and **not** used. It is recommended for a
  document whose evidence outweighs its rules; here they are comparable, and **this document's
  reader arrives holding `IDM-004`**, which has no split. A different shape for the sibling of a
  document you are meant to read alongside costs more than the split buys.
