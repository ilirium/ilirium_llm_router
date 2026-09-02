# Reviewing executed work — what `IDM-004` needs, and a plan for the baseline run

**Written 2026-09-02, on the owner's instruction, and deliberately not executed.** The owner intends
an `IDM` for this later; this document exists so the first run has a charter rather than an
improvisation, and so the `IDM` can be written from what the run *cost* rather than from what it
seemed like it should be.

**That ordering is not a preference, it is `IDM-006`'s step 9** — *write the playbook last, from
what it cost* — which is the stated reason `IDM-004` itself did not exist until after its first run.
A proto-`IDM` written now would be a guess wearing the tier's authority. **So this is a plan, and
the sections below are its argument, not a rule in force.**

---

## The gap: there are two protocols and this is a third

`IDM-004` draws the line between itself and the closing review in `../../README.md`. **Neither of
them is what the owner asked for.** The third column is new.

| | Closing review | Forward review | **This** |
|---|---|---|---|
| Where | `../../README.md`, "The review phase" | `../../method/IDM-004-reviewing-unexecuted-work.md` | nowhere yet |
| Subject | a **milestone's** executed work | a document nobody has acted on | **one phase's executed work** |
| Asks | did it do what it said, and is what it found true? | will it work, and can somebody else run it? | **did it do what it said, is what it claims true, and what has the claim already reached?** |
| Method | a checklist | charter, two parallel runs, reconciliation | **the forward method, against executed work** |
| When | at a milestone's close | before a plan's first substantial task | **before the merge** — see below |

**The closing review is not a substitute and the reason is scale.** It is chartered over a whole
milestone, runs once, and is a checklist — which is the right instrument for *did every phase
complete its task list*, and the wrong one for *is this particular claim true*. Its own checklist
line **"re-derive every quoted measurement from the frozen artefacts"** is a whole review's work
when aimed at one phase, and it is one row of nine when aimed at a milestone.

**What is genuinely new here is not the subject but the method applied to it.** `IDM-004`'s
contribution is the charter and the two parallel runs; `../../README.md`'s contribution is what to
check in work that ran. **Neither has been pointed at a single phase.**

---

## What carries over from `IDM-004` unchanged

**Do not re-derive these. They are the parts that are about *reviewing*, not about *plans*.**

- **Iteration 1: the charter decides what the review finds.** This is *stronger* for executed work,
  not weaker. Executed work offers far more easy-to-verify surface than a plan does — tests pass,
  lint is clean, links resolve, a register check reports 28 of 28 — and **a reviewer told "review
  this" will report the green.** The evidence `IDM-004` cites is a fresh-context review that
  verified eleven citations line for line and missed the defect anyway.
- **Two runs, in parallel, then reconcile.** 18% overlap at n=1. The split fell along the predicted
  line: the author found things about *the record*, the cold reader found what the author could not
  un-know.
- **Read-only** — with one amendment below, which is the largest single difference.
- **`VERIFIED` / `REPORTED` on every finding.** A review that does not label cannot be triaged.
- **Findings and questions in separate sections.**
- **Nothing found is a complete answer. Refusals are first-class.**
- **A settled decision may be questioned, never filed as a defect.**
- **Reconciliation is the author's job, and a refutation is re-verified before it is accepted.**
- **A refused finding is recorded with its reason**, or the next review re-raises it.

---

## What must be added

### 1 · The review may run the thing, and a forward review has nothing to run

**This is the largest difference and everything else follows from it.** A plan can only be read. A
finished phase has a binary, a test suite, checkers, and a repository whose state is itself a claim.

`../../README.md`'s closing checklist already says **"drive the software live"**, and Phase 12 is
the argument for it: the `.env` defect was *predicted* by reading python-dotenv and only became a
fact when a probe with a control was run. **Reading found it; running settled it.**

Two rules the forward protocol has no need of:

- **Running is not fixing.** Rule 1 stands — the review changes nothing — but it now has to say so
  about a *tree* rather than only about a document. **`git status` is read after anything is run.**
  The precedent is not hypothetical: an interrupted mutation sweep once left a module
  comment-stripped with the suite passing 427/427.
- **Anything that touches the machine needs the owner's go-ahead, and the machine is left as
  found.** Installing the tool to check the quick start is a machine change, not a read.

### 2 · Every instrument the phase leaned on gets a vacuity question

**A failure class that cannot exist in a forward review: the phase's own evidence may be green and
empty.** The charter names each check the phase cites and asks, for each, **what would this look
like if it were vacuous?**

The evidence is this milestone's, and it is not thin:

- **Phase 11 found twelve tests comparing the code to itself** — invisible to every other
  instrument.
- **Phase 12 had three tools report something untrue without failing.** `uvx --from` served a stale
  build and exited 0 for code that had not shipped; `$?` after a pipe reported the wrong command's
  status; `uv tool upgrade` installs changed code while printing *"Nothing to upgrade"*. **All three
  exited 0**, and only reading the output distinguished them.

**So a green check is a claim under review, not a reason to skip one.** Where the phase's own
instruments were mutation-tested, the review checks the mutation was real; where they were not, that
is a finding.

### 3 · Did the execution honour the settled table?

**Only a backward review can ask this, and it is not a formality.** Phase 12's own register check
found the `README.md` carrying **five** caveats where settled row 6 says **four** — the fifth being
the executing session's own judgement, added for a good reason that was not its to act on.

**It was caught by a mechanical row-by-row check and not by any amount of rereading**, which is the
argument for making it a named pass: the settled table, one row at a time, against what shipped.

### 4 · Read the artefact, not its account of itself

`IDM-004` has this implicitly — its charter names claims to re-verify *by reading the source*. **For
executed work it is the primary axis rather than one item**, because there are now three things that
can disagree: **the code, the tests, and the prose.** A forward review has only prose.

The precedent is `IDM-004`'s own headline finding: a claim inferred from a code comment about a
narrow case, generalised, labelled honestly as inferred, and written into four documents. **The cold
reader found it by reading `proxy.py` instead of the document's account of `proxy.py`.**

### 5 · Rank by what the claim has already reached, not by what it would cost to find later

**`IDM-004`'s rule 6 does not transfer.** *"What it costs to find this after task N instead of now"*
is meaningless when every task has run. The replacement is the other half of the same finding —
**a wrong claim spreads at the speed of citation** — so the ranking is **blast radius**:

| Reach | Why it ranks where it does |
|---|---|
| `reference/`, `CLAUDE.md` | canon; read by every later session without being questioned |
| `status.md`, `backlog.md` | acted on; a wrong item becomes scheduled work |
| `../implementation-plan.md` | shapes phases not yet planned |
| the phase's own notes | frozen record; wrong but bounded, and correctable by a later note |
| a commit message | **cannot be corrected after the merge**, only annotated elsewhere |

### 6 · The documents the phase edited outside its own folder are in scope

**This is where propagation happens and none of it is in the phase folder.** Phase 12 changed
**eight documents outside it** — `../../status.md`, `../../backlog.md`, `../implementation-plan.md`,
`../../prompt.md`, the top-level `README.md`, both files in `../../captures/`, and — on this branch,
deliberately — `../../method/IDM-001-git-branching.md`. Two non-documentation files go with them,
`pyproject.toml` and `.env.example`.

**A review scoped to the phase folder would miss every one of them**, including the two edits made
under the rule that *adding a backlog item is how a phase declines scope*. Those declines are claims
too: the review checks they are real declines and not silent drops.

### 7 · What to measure, because the `IDM` will be written from it

`IDM-004` records its own cost and then says **`n = 1`, and the numbers are not a rule**. This run
should produce the second data point deliberately rather than incidentally:

- **Overlap between the two runs**, as a percentage of distinct findings. `IDM-004`'s forward number
  is 18%. **A backward number near 60% would be evidence that one run is enough**, and would be
  worth more than a confirmation.
- **Cold-run cost** — tokens, tool calls, wall clock.
- **Findings by how they were reachable**: only by running something, only by reading code, only by
  reading prose, only by holding the record. **This is the number that says whether the two-run
  split is the right split for executed work**, or whether the axis should be *ran it* against *read
  it*.
- **How many findings the phase's own mechanical checks had already caught** — a check on whether
  the review is buying anything the register check and the sweeps do not.

---

## What must be removed or changed

- **"Executability" becomes "reproducibility".** `IDM-004` asks a cold reader *could you execute
  this from the document alone?* The executed-work equivalent is **could you re-derive these claims
  from what is in the repository?** Same instrument, different question: the guesses are still the
  findings, but they are now guesses about *where a number came from*.
- **"Before the plan's first substantial task" becomes "before the merge".** Two reasons. After the
  merge a fix costs its own branch, and **the merge commit message is itself a claim-bearing
  artefact that cannot be corrected afterwards.** *This is the one timing decision the owner has to
  make now, because Phase 12 is at exactly that point.*
- **"The author" needs redefining, and Phase 12 breaks it.** `IDM-004`'s author run is *the session
  that wrote the document*. **Phase 12 was executed across two sessions** — Groups A–C in one, D–E
  in another — and neither holds the whole. The author run is therefore partial by construction, and
  the notes are the only shared record. **Left open deliberately**; it is a real question and this
  document should not presume the answer.
- **The known-false-positive list stops being a courtesy and becomes load-bearing.** Executed work
  has a large recurring false-positive surface that will otherwise consume the whole budget:
  `link-check.py`'s 109 broken links and its **worktree-dependent count**, phase plans legitimately
  citing files they create, `make lint`'s blindness to column width, and table rows that correctly
  run past 100 columns.

---

## The plan for the baseline run

**Subject:** Phase 12 as executed — commits `80914a0` through `b0070e5` on
`feat/phase-12-installer-and-readme`, the six non-documentation files it changed — three under
`src/`, one under `tests/`, plus `pyproject.toml` and `.env.example` — the phase folder, and the
eight documents the phase edited outside it.

**Out of scope:** Phases 1–11 as executed; how any settled decision was reached; and the `README.md`
the phase replaced, except where a claim is made about it.

1. **Write the charter**, from the sections above, as a file handed to the cold reader verbatim —
   scope, the two questions, what a finding looks like *in executed work*, the claims to re-verify
   by reading the source, the instruments to test for vacuity, the known false positives, the rules,
   the output shape, and a reading budget.
2. **Run both, in parallel, read-only.** The author records findings while the cold run is in flight
   and fixes nothing.
3. **Reconcile**, as `IDM-004` specifies: verify every refutation before accepting it, and treat a
   disagreement between the runs as itself a finding.
4. **Record the merged work list**, with what was accepted, what was refused, and why.
5. **Record the four measurements above**, so the `IDM` can be written from cost.

**Then decide what to fix before the merge and what becomes a backlog item** — which is a decision,
not a review outcome, and belongs to the owner.

---

## Open questions for the owner

1. **Before the merge, or after?** This document argues **before**, on the grounds that the merge
   message is an artefact the review should cover and that a later fix costs a branch. Against it:
   the branch is finished and green, and the review will find things, which means the phase stays
   open longer.
2. **Does the scope include the seven documents edited outside the phase folder?** This document
   argues **yes**, because that is where a wrong claim propagates. It roughly doubles the reading.
3. **What is the author run, given the phase spans two sessions?** Options: a partial-author run
   scoped to Groups D–E only; treating A–C as cold and running a third pass; or accepting that the
   notes are the shared record and running one author pass over the whole with the gap declared.
4. **One cold run or two?** `IDM-004` uses one. Executed work splits naturally into *the code and
   its tests* and *the documents and their claims*, and two narrower charters may find more than one
   wide one. It also roughly doubles the cost, and **`n = 1` is not enough to know.**
5. **Where does the output live?** `IDM-004` puts the merged work list in the document's own notes.
   This phase's notes are already six files. A separate `review-executed.md` beside this plan is the
   alternative.

---

## What would make this a bad review

**A phase chartered to find defects will manufacture them.** `../../README.md` says it about the
closing review and `IDM-004` inherits it as rule 4; it applies here with one extra edge.

**The extra edge is that executed work always has something to say.** Every phase has a prose
sentence that could be tighter and a test that could be stronger, and a review that returns thirty
of those has spent its budget and found nothing. **The output that would justify this run is one
wrong claim that had already propagated** — which is exactly what the forward protocol's first run
returned, and the reason it exists.
