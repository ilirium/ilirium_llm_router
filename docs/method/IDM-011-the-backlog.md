# IDM-011 — The backlog: who files an item, and how one is identified

**In force 2026-09-04.**

**One rule here is in force the moment you read it and the rest describes a scheme being built in
the same phase.** *Said plainly because an `IDM` is normally something you can act on entirely.*

| | |
|---|---|
| **In force now** | **who may file an item** — see below. It changes what a session does today |
| **Describes what Phase 13 builds** | the `BKL` identifier, the metadata line, the generated table, `backlog-done.md`. Until that phase's Group E lands, `../backlog.md` has no ids |

---

## What the backlog is

**Inventory, not state.** What is in flight and where the project stopped are in `../status.md`;
**nothing here says when anything happens.** An item is named in `../status.md`'s "What is next"
when it is picked up.

**Every item names why it is parked**, and several name why the question is weaker than it looks.
**That is the point of the file.** An item that has lost its reason has become a to-do, and a to-do
nobody has justified in six months cannot be told apart from one nobody wants.

---

## Who files an item

**A session asks before filing one. The item lands on the owner's word.**

*Owner's instruction, 2026-09-04, and it changes a rule set two days earlier.* The reason given: **a
large backlog is not itself a good outcome.** A file whose items are added by whoever notices
something becomes a list nobody chose.

**If the owner declines, the decline is recorded in the phase's `notes.md`.** Nothing is dropped
silently — what changes is *where* the record goes, not whether there is one.

### What this amends, and what it leaves alone

**`IDM-001` says filing a backlog item *is* how a phase declines scope.** That is still true of the
mechanism and no longer true of the authority:

| | Before | Now |
|---|---|---|
| A phase declines scope by | filing an item | **asking**, then filing if the answer is yes |
| If the answer is no | *(did not arise)* | **the decline goes in `notes.md`** |
| An item opens its own branch | **never** | **never** — unchanged |

**The branch rule is untouched and is `IDM-001`'s**, not this document's: an item goes on whatever
branch you are already on. A branch per item costs a worktree, a merge, an index description and a
row in `../reference/branches.md`, for a paragraph.

---

## The identifier

**`BKL-NNNN`** — four digits, zero-padded, starting at `BKL-0001`.

**Allocated in file order**, top to bottom as `../backlog.md` reads, and then **never reused and
never renumbered** — `IDM-000`'s scheme for `IDM-NNN`, with one ambiguity closed.

*The ambiguity: `IDM-000` says "in order written", which is unambiguous for documents written one at
a time and not for a bulk pass over items already written. **File order, not `added`-date order** —
the section order is deliberate, so ids follow the reading a person actually does, and **date order
is not merely different but unusable**, because several older items carry no recorded date and
inferring one would freeze a permanent id on a guess.*

**Why an id at all.** Items were cited by quoting their bold opening phrase — `../status.md` did it
and so did phase plans. **A quoted title is not an identifier:** editing a title silently breaks
every citation of it, nothing checks that, and the break stays invisible until a reader follows one.

## An item is a heading

**One shape, and only one.** An item is a `###` heading carrying its id and a short title, and
nothing else in either file is one:

```
### BKL-0007 — The open milestone's phase count goes stale at every merge

documentation-defects · open · added 2026-09-02

<the item: what the work is, and why it is parked>
```

**The heading is the boundary.** A paragraph without one is not an item — preamble, section
scoping, advice that applies to a whole section — and that is now visible rather than inferred.

**The metadata line sits directly under the heading and carries no id**, because the heading holds
it. `<category> · <status> · added YYYY-MM-DD`, and **a done item adds** `· done YYYY-MM-DD ·
phase N`. **Visible, never an HTML comment** — the data a reader needs in order to cite an item must
not be invisible to the reader.

**`· see <refs>` is optional and comes last** — a comma-separated list of the documents an item
points at and of any `BKL` id it supersedes or was reversed from. **Empty is normal**; most items
point nowhere, and thirteen of thirty-eight carry one today.

**A metadata line is never wrapped**, whatever its length — the parser matches it as a single line,
so a wrapped one silently stops being an item. *Two exceed 100 characters today, which is the same
exception a table row already has.*

***A `superseded` item is the one case where it is required***, and `--check` enforces it: the
status means "replaced by another item", so an empty `See` makes the definition false. *That check
was added 2026-09-17, after the column spent thirteen days named by this document and written by no
code — during which nothing could fail, because **`--check` cannot notice a value nothing
produces.***

**The title is written once.** It lives in the heading; the body does not restate it. *Where an
item's opening sentence carried facts a title cannot hold, those facts stay in the body — unbolded,
because bold is no longer how an item begins.*

### This replaced three shapes, and two of the three were how items went missing

***Amended 2026-09-04, and the amendment is the point of this section.*** Until then this document
said `../backlog.md` *"does not hold one kind of item"* and defined **three** placements — a line
under a bold opening for prose items, a line under the heading for `###` subsections, and **an extra
leading column** for the rows of the one table in `Decisions waiting on a person`.

**That was written to fit the file as it already stood, and it cost two items.** With no structural
marker, an item opening with a bold sentence is **indistinguishable from a continuation paragraph**
that also opens with one. The compile pass enumerated openings as bold-or-`###` at line start;
`../backlog.md`'s two struck-through entries open `~~**` — strike before bold — **and were invisible
to it.** They survived the compile, an author review and two forward-review passes, and were found
only by a cold reviewer told to look for a boundary nobody had flagged.

*The table shape failed differently and less dangerously: it was merely unreadable, and grew to
seven columns once metadata was added to it.*

**A heading cannot be missed by a regex on bold runs**, and `backlog-index.py --check` rejects any
heading at any level that carries a `BKL` id and is not exactly `### BKL-NNNN — title` — **so an
item quietly demoted or re-punctuated is named rather than skipped.**

*`--check` also compares the heading count against the items parsed. **That assertion is a duplicate
and is documented here as one**: it can only fire where a per-item error has already been raised. It
was added believing it caught the demotion case and it does not — the demoted heading is not counted
either, so both totals fall together. Corrected 2026-09-17, after this document had credited it with
that coverage for thirteen days.*

## Statuses

**Five**, and **which file an item lives in follows from its status**:

| Status | Meaning | Lives in |
|---|---|---|
| `open` | live, unscheduled | `../backlog.md` |
| `partly-done` | some of it discharged, the rest still real | `../backlog.md` |
| `refused` | considered and declined | `../backlog.md`, in "Not on this list, and why" |
| `superseded` | replaced by another item, which the `See` column names | `../backlog.md` |
| **`done`** | **the only status that leaves** | **`../backlog-done.md`** |

**`../backlog-done.md` means exactly one thing: work that was done.** Keeping it to a single meaning
is what makes it readable without a status column doing the work.

**A refusal is first-class and keeps its id.** `../README.md` states the general form — recording
that something was considered and refused is what stops it being re-proposed every milestone by the
next person reading the same surface signal. **A refusal can be reversed**, and this repository has
reversed one; when that happens the reversed item is `superseded` and `See` names what replaced it.

## Categories

**The category is the section the item sits in**, and there are eight. **The sections are not
reorganised by this document** — their order was set deliberately, method first, so that a session
reading only the top of the file still reads the part governing its behaviour.

*One of the eight, "Not on this list, and why", is a status container rather than a kind of work.
That is a known wrinkle and it is left alone: fixing it means moving items, and the sections were
settled as they stand.*

## The table is generated, never typed

**`../procedures/backlog-index.py`**, with `--write` and `--check`, in the shape
`../procedures/branch-index.py` established.

**One table per file** — `../backlog.md` tables the live items, `../backlog-done.md` the done ones,
so each file is readable on its own. Columns, in order:

`ID` · `Added` · `Status` · `Category` · `What it is` · `Done` · `Phase` · `See`

**`See`** holds the documents an item points at — an `EPD`, an `IDM`, a `BUG`, a phase note — **and
any `BKL` id it supersedes or was reversed from.** Empty is normal.

**Why generated.** A hand-typed table of this kind was refused once already, in `IDM-001`, and the
derived index that refusal produced turned out **richer** than the prose it replaced. This
repository has recorded a hand-maintained count going stale four separate times, and every one went
stale at the moment the thing it counted changed — which is the moment nobody is re-reading prose.

**`--check` validates** that ids are unique, that every item has a row and every row an item, and
that every `BKL-NNNN` citation in the live tier resolves to an item.

### Never write an id that does not exist, not even as an example

**Any `BKL-NNNN` written anywhere under `docs/` or in `CLAUDE.md` is a citation.** `--check`
resolves every one of them against the items, and it **cannot tell a citation from a mention** — so
a document discussing a hypothetical id fails the check.

***That is the smaller reason. The real one is that the check would later go green on a false
statement.*** **Ids are allocated in order and never reused**, so an invented id is not permanently
unresolvable — it is the **next** id to be handed out. The moment an item claims that number, a
sentence written about something imaginary becomes a **citation of a real and unrelated item**, and
`--check` starts passing on it. *A checker that fails today and passes tomorrow because the text
became wrong is worse than one that never looked.*

**So: describe, never name.** *"A synthetic item one past the highest id"* costs nothing and cannot
rot. **The rule covers review reports, notes, plans and examples in this document** — everything the
checker scans, which is everything.

*Owner's decision, 2026-09-17, after a reconciliation quoted a review's test id and turned
`--check` red. **The alternative was to teach the checker an escape hatch**; it was refused, because
an escape hatch only suppresses the failure and leaves the sentence to go quietly false later.*

### What `--check` cannot see, said here so nobody reads its silence as coverage

**The frozen archive is out of scope.** A quoted item title inside a closed phase's document is a
**claim** about what the backlog said at the time, and `../README.md`'s archive rule is *paths yes,
claims no* — so those citations are not repointed to ids.

**So the promise "nothing cites a backlog item by title any more" is true of the live tier and false
of the archive**, and `--check` **cannot tell the difference**: it validates the `BKL` citations
that exist and never the title citations that remain. *Written down because a green check would
otherwise be read as proof of something it does not test.*

**And it cannot see a *newly added* item deleted again.** *This is the one worth understanding,
because the obvious reading of it is backwards.*

**An item that has been cited somewhere cannot vanish silently.** Every `BKL-NNNN` written anywhere
under `docs/` is resolved against the items, so deleting one that any document mentions fails the
check — *three times over, for a typical item.* **All the ids allocated up to and including Phase 13
are cited in that phase's own record**, so none of them can be deleted without `--check` saying so.

***But that protection is a side effect, not a design.*** It comes from a check written to catch
citation typos, and it covers exactly the items something happens to cite. **An item added later,
never yet referenced, and then removed leaves nothing behind at all** — no citation to dangle, no
heading to count, no gap that is distinguishable from the gap a `done` item leaves when it moves.
**`--check` exits 0 and reports the smaller total as though it were correct.** *Demonstrated by
mutation, 2026-09-17.*

**So the practical rule is: a brand-new item is unprotected until something cites it**, and the
window is widest at exactly the moment an item is most likely to be edited by hand.

*This section said the opposite until 2026-09-17 — that deletion was invisible in general and that
the one time it was caught was luck. **Both halves were wrong**, and the section exists precisely so
its silence is not misread. It misread its own.*

**Closing it properly would mean a manifest of every id ever issued**, which is a second copy of the
thing the ids already are. *That trade is stated rather than resolved, and it is the same trade
`IDM-001` refused for merge hashes.*

---

## Provenance

- **The owner's instructions, 2026-09-03 and 2026-09-04**, over four rounds of interview plus four
  questions raised by a forward review. Recorded in
  `../milestone-2-corpus/phase-13-method-and-backlog/plan.md`'s settled table, rows 1–10 and 21–24.
- **`../backlog.md`'s own item asking for this — `BKL-0004`**, added 2026-08-26 on the owner's
  instruction — *"a quoted title is not an identifier"* — which names the three things it would
  take: an id, an allocation rule that survives items being deleted when done, and a decision on
  whether a checker verifies them. **All three are answered here**; the checker is `backlog-index.py
  --check` rather than `link-check.py`, to keep id checking out of an instrument whose own count is
  worktree- dependent and routinely misread.
- **`IDM-001`** — the branch rule, which is that document's and is cited rather than restated here.
  Its authority claim is amended by "Who files an item" above.
- **`IDM-000`** — the numbering scheme this copies, and the admission test this document passes: it
  holds no fact about the router, and every rule survives a change of subject.
