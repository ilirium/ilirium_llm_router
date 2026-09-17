# IDM-010 — `for-the-owner.md`: the phase's digest for a person

**In force 2026-09-04.** One instance existed before this document — Phase 11's, written 2026-08-26
on the owner's suggestion, and it says of itself: *"No tier, no rule, no template. If it turns out
to earn a convention, that is a later decision and this file is the evidence for it."* **This is
that decision.**

**The next phase wrote none at all**, which is most of the argument: a practice invented without a
rule did not survive one phase.

---

## What it is

**One `for-the-owner.md` per phase, in the phase folder, written to a person.**

**It is a digest of what is worth a human's attention after the phase** — not an inbox, not a
queue, and not a place anything is *required* to go. **Zero entries is a valid phase. So is a long
one**, when the phase was heavy; the length is information about the phase rather than clutter.

### The audience is the whole of the distinction

**This is why the file exists, and every other rule follows from it.**

| | `notes.md` and `notes-group-<letter>.md` | **`for-the-owner.md`** |
|---|---|---|
| Written for | a later session, or a review | **a person** |
| Read by | machine, in depth, one section at a time | **a human skimming headings** |
| Optimised for | completeness — it is the context a deep review works from | **selection** |
| Length | whatever the work took | **whatever survives the test below** |

**The notes are too big and too detailed to be read by a person after a phase, and that is correct
rather than a defect** — they exist to hold context. A phase's notes and group notes routinely run
to thousands of lines. **Nothing in this document licenses shortening them.**

## What goes in it

**Four kinds**, marked so the file can be skimmed:

| | |
|---|---|
| **`ASK`** | A question that **was asked out loud during the phase** and is still open at its close |
| **`IDEA`** | A suggestion the owner can ignore |
| **`REGRET`** | Something the session would do differently, told rather than quietly fixed |
| **`ERRAND`** | **An action only a person at a keyboard can perform.** Not a decision — a task the session is unable to do |

**Headings carry a number and an importance, in this shape:**

```
## 4 · ASK · high · <title>
```

**Numbers run 1..N within the phase, in order of appearance, and are never renumbered.** Importance
is `high` / `medium` / `low`. **Entries are *not* ordered by importance** — ordering adds friction
at write time and a title is easy to search for.

### The test an entry has to pass

**Would a person, rereading this after the phase, act differently for having read it?**

That is the whole of the size rule. **There is no line limit**, and this repository has recorded a
written number going stale four separate times; a test survives what a limit does not.

## What does not go in it

**Anything that needs a decision is asked out loud, in the session.** *Owner's instruction.* Not
written here for somebody to find later. A session that has a question raises it where it will be
read — which is `IDM-007`, and this is that rule applied to a file that could otherwise become a
place questions go to rest.

**`ASK` is therefore narrow.** It records a question **already asked aloud** that is still open when
the phase ends. It is never the first place a question appears.

**And nothing formally closes an entry.** *Owner's decision.* The file is **one-way by design**:
there is no disposition to record, no closing pass, and **an unanswered `ASK` is not a defect.**
Written down explicitly because the opposite reading is the available one — a reader who finds
several unanswered entries in an old phase folder will otherwise see a dropped ball and re-raise
them.

## When it is written

**During the phase, as things arise. Nothing is removed or rewritten at its close.**

**There is no trim, and the reason is that a per-phase file cannot accumulate.** *A draft of this
rule had a closing pass that removed entries overtaken by events; the owner asked what it was for,
and the answer did not survive the question.* Two things kill it:

- **The file is bounded by the phase**, so nothing builds up across phases for a trim to solve.
- **`../README.md`'s archive rule is *paths yes, claims no*.** Once the phase merges its folder is
  archive, and removing an entry would be editing a claim out of it — the same reason a long
  `notes.md` is left whole.

**So the discipline is entirely at write time**: an entry goes in only if it passes the test above.

## Two rules that stop it going missing

**The file always exists**, and says so in one line when it has no entries. **An omitted file cannot
be told apart from a forgotten one** — which is exactly what happened between the first instance and
this rule.

**Forward-only.** No closed phase gets one written retroactively. Writing one for a finished phase
means reconstructing, weeks later, what a person would have wanted to know at the time — invented
after the fact, which is the guesswork the file exists to avoid. *Same shape as the task-not-commit
naming rule, which left one early phase saying "commit N", and the notes-splitting rule, which left
one phase's notes whole.*

---

## The evidence, told straight

**There is one instance: Phase 11's, eleven entries — 3 `ASK`, 5 `IDEA`, 3 `REGRET` — and none of
the eleven was ever marked answered.**

### It does not show the rules above being broken. It shows a category was missing

**This has to be said plainly, because the convenient reading is available and wrong.** A draft of
this document claimed all three of that file's `ASK`s were questions parked instead of asked — the
failure the *asked out loud* rule prevents. **A review checked the file and refuted it.** Read
against the four kinds above:

| Entry | What it actually is |
|---|---|
| *Does `git --version` prompt?* | **An `ERRAND`.** Its own text: *"I cannot run this check. A denial reaches me as a tool error; an approval is invisible."* There is nothing for the owner to decide — it is an observation only a person at a keyboard can make |
| *Does a bare clone break the settings-resolution rule?* | **An `ERRAND`**, for the same reason: *"The check is one approval"* |
| *A permission entry belongs to nobody* | **A conforming `ASK`** — *"raised in every recent phase"*, asked aloud, still open |

**Zero of the three are the failure the rule prevents.** Two are errands, and they were filed as
questions **because `ERRAND` did not exist**. The file's own preamble said as much and was not read
closely enough: *"Nothing here blocks the build — anything that did was asked in the session
instead."*

**That is a better finding than the one it replaced**, and it is why `ERRAND` is one of the four
kinds rather than three. *It was only visible from inside the taxonomy this document introduces,
which is why nobody reading that file earlier could have seen it.*

### What the second phase showed

**The phase after it wrote no such file.** Nothing was withheld and nothing went wrong; there was
simply no rule, and a practice with no rule reached exactly one phase. **That is the argument for
"the file always exists"**, and it is worth more than any single entry in the one file that does.

### The one thing left standing about unanswered entries

**Eleven entries, none marked answered, and under this document that is not a defect** — it is what
a one-way channel looks like. *The instinct on first reading that file is to treat it as a backlog
of unanswered questions. It is not one, and a reader who acts on that instinct will re-raise things
the owner already chose not to spend attention on.*

---

## Provenance

- **`../milestone-2-corpus/phase-11-corpus-tools/for-the-owner.md`** — the only instance, and the
  worked example. **Read it whole**; it is short, and it is both the example and the evidence.
- **The owner's instruction, 2026-09-03 and 2026-09-04**, over four rounds of interview: the
  audience split, the four kinds, the heading shape, the one-way rule, and the removal of the
  closing trim. Recorded in `../milestone-2-corpus/phase-13-method-and-backlog/plan.md`'s settled
  table, rows 11–18 and 20.
- **`IDM-007`** — *raise it where it will be read*, of which the *asked out loud* rule is a direct
  application. A concern placed where it will not be read has not been raised, and a file the owner
  reads after the phase is exactly such a place for anything that needed answering during it.
- **`../README.md`'s phase template** — where a phase folder's contents are specified, and which
  this document amends rather than merely appends to.
- **`IDM-000`** — the tier's conventions, and the admission test this document passes: it holds no
  fact about the router, and every rule survives a change of subject.
