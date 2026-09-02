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

1. **Write the charter** — `review-charter-jobs-done.md` beside this file, handed to the cold reader
   verbatim. From the sections above: scope, the two questions, what a finding looks like *in
   executed work*, the claims to re-verify by reading the source, **the instruments to test for
   vacuity**, the known false positives, the rules copied in rather than cited, the output shape,
   and a reading budget. *A second charter file rather than a section here, because a thing you hand
   over should be a file — `IDM-004`'s reason, unchanged.*
2. **Run both, in parallel, read-only.** One author run over all five groups, one cold run. The
   author records findings while the cold run is in flight and **fixes nothing**. Anything either
   run executes leaves the tree and the machine as it found them, and `git status` is read after.
3. **Reconcile.** Verify every refutation before accepting it; a disagreement between the runs is
   itself a finding. **The author run declares its gap on Groups A–C** rather than reporting on them
   as though it had been there.
4. **Write `notes-review-jobs-done.md`** — the merged work list, what was accepted, what was refused
   and why, and the executability-turned-reproducibility section.
5. **Record the four measurements named above**, so the `IDM` can be written from cost rather than
   from intention. *The list lives in one place — §7 — deliberately; a count restated here is the
   second copy this repository keeps finding wrong.*

**Then decide what to fix before the merge and what becomes a backlog item** — a decision, not a
review outcome, and the owner's. **Fixes land as ordinary commits on this branch**, since the review
runs before the merge and the branch is still open.

---

## What is settled, and by whom

*The five questions this document opened with, answered by the owner on 2026-09-02 after reading it.
Positions the review does not get to revisit — the same rule `plan.md`'s settled table carries.*

| | Settled | Note |
|---|---|---|
| 1 | **The review runs before the merge** | The merge message is a claim-bearing artefact that cannot be corrected afterwards, and a later fix costs its own branch. The phase stays open longer, which was the argument against |
| 2 | **Scope includes all eight documents edited outside the phase folder** | Not only the four a later session acts on. The `README.md` was in scope regardless — it is the deliverable |
| 3 | **One author run, over the whole phase, with the gap declared** | First-hand for Groups D–E; for A–C only what the notes and commit messages record. **For A–C it is a warm read rather than an author run**, so the author/cold split is weaker exactly there — recorded as a measurement, not hidden |
| 4 | **One cold run** | As `IDM-004` does. The two-narrow-charters alternative is untested and doubles the cost, and `n = 1` is not enough to choose it |
| 5 | **The output goes in `notes-review-jobs-done.md`**, beside the group notes | Names settled by the owner on 2026-09-02, after this table was first written: two reviews in one phase need two distinguishable names, so the forward review's record moved out of `notes.md` to `notes-review-plan.md` at the same time. **`review-charter.md` keeps its plain name** — Phase 10 settled that the other way, and `IDM-004` cites it |

**Nothing else in this document is settled.** The seven additions and three removals below are its
argument, and the charter written from them is the first thing the run produces — at which point
they stop being a proposal and become what the reviewer was told.

---

## What would make this a bad review

**A phase chartered to find defects will manufacture them.** `../../README.md` says it about the
closing review and `IDM-004` inherits it as rule 4; it applies here with one extra edge.

**The extra edge is that executed work always has something to say.** Every phase has a prose
sentence that could be tighter and a test that could be stronger, and a review that returns thirty
of those has spent its budget and found nothing. **The output that would justify this run is one
wrong claim that had already propagated** — which is exactly what the forward protocol's first run
returned, and the reason it exists.
