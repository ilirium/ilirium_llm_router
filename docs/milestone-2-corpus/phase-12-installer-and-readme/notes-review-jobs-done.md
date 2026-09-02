# Phase 12 — the review of the finished work

**Run 2026-09-02, before the merge**, per `review-plan-jobs-done.md` and the charter beside it. Two
runs in parallel — this session as author, one fresh-context agent as cold reader — read-only,
against the tree at `0c5ce2d`. This file is the reconciliation.

**It is the first review of executed work this repository has run.** The forward protocol
(`../../method/IDM-004-reviewing-unexecuted-work.md`) supplied the method; what had to change for
executed work is argued in `review-plan-jobs-done.md` and was settled by the owner before the run.

---

## The headline

**Eighteen distinct findings. Two runs overlapped on two of them — 11%.**

`IDM-004`'s forward review overlapped at **18%** and called that the number justifying two runs. **A
backward review overlapped less, not more**, which is evidence in the same direction and is the
measurement `review-plan-jobs-done.md` §7 asked for. *n = 1 for the backward case, exactly as
`IDM-004` says of its own figure; one measurement is not a rule.*

**The split fell along the predicted line and further along it than expected.** The author found
things about *the record* — a claim contradicted between documents, a list nobody had walked. **The
cold reader found what the author could not un-know**, including the two highest-blast-radius
findings in the phase, one of which is in the canon tier.

| | Author | Cold | Both |
|---|---|---|---|
| Distinct findings | 4 | 12 | 2 |

---

## The finding that justifies the protocol on its own

**`CLAUDE.md` said Milestone 2 was "three phases in, last merged 2026-08-21" — a fourth copy of the
exact count this phase was chartered to fix, in the one file loaded into every session.**

Task 12 fixed `status.md`'s two undercounts and `backlog.md` filed the mechanism, framed throughout
as *"three places"* — **every one of them inside `status.md`**. `CLAUDE.md` was never opened.
`git log 5cdc1c9..HEAD -- CLAUDE.md` is empty: the phase that existed to fix this count did not
touch the file where being wrong costs the most, and named Phase 10's merge date where `status.md`
names Phase 11's, so it was stale by a whole phase.

**Three things worth carrying:**

- **The author could not have found it.** This session wrote the backlog item that says the count
  lives in three places, having just fixed the two it knew about. The framing was the blind spot.
- **It changes which fix survives.** Of the three candidates in `backlog.md`, only *derive the count
  from the implementation plan's headings* works across two files. The other two were written as
  though `status.md` were the whole problem, and are now recorded as such.
- **The instance count was understated.** The phase called this the third instance. With `CLAUDE.md`
  it is the fourth, and the worst.

---

## Findings, in blast-radius order

*`C` = found by the cold run, `A` = by the author, `AC` = both. All are VERIFIED unless marked.
**Every one is fixed** unless its row says otherwise.*

| | Finding | Reach | Disposition |
|---|---|---|---|
| **C1** | `CLAUDE.md` said "three phases in, last merged 2026-08-21" | **canon** — loaded every session | fixed; `backlog.md`'s item widened to four places across two files, and its candidate fixes re-judged |
| **AC2** | "133 lines to 304" — the README is **310** | `status.md`, `prompt.md`, `implementation-plan.md`, `notes-group-d.md` | fixed in the three live homes; recorded in place in the phase note |
| **C3** | `implementation-plan.md` said the pin was checked against "23 wheel entries"; the comparison covered **22** | milestone index | fixed. *`evidence/wheel-contents.md` says 22 in a sentence written specifically to prevent this, and the previous session's commit message records catching the same error once already* |
| **A3** | `status.md` and `prompt.md` asserted an unconditional wait for the owner before the merge | acted-on | fixed — the task list authorises the merge conditionally |
| **C4** | `notes-group-c.md` said the `uv_build` pin was **"Not bumped … not this phase's decision"**, under a heading reading "deliberately not acted on" — it was bumped in that same group, one commit later | phase note, contradicting the milestone index | fixed, with the old wording kept |
| **C5** | `notes-group-c.md`'s "438 → 445" and "Seven tests" — the group ended at **448** and **ten** | phase note; **the wrong figure had already propagated into the review charter** | fixed |
| **C6** | The "What was built" table has four rows, omits `env-template`, and describes `init` as writing one file | phase note → `implementation-plan.md`'s "two of four" | fixed; the denominator is five by the table's own count and the sentence now says so |
| **AC7** | Two instruments are weaker than their names. `register-check.py`'s `--help` check tested **one substring of a 28-line block**; its `init refuses` check tested the **message**, where the register row names the **exit code** | the instrument frozen to be re-run on the trunk | both strengthened, and the new `--help` check was mutation-tested and bites |
| **C8** | `notes-group-d.md` said the fifth caveat "rides in the same section" — Group E had moved it out | phase note | fixed, with the old wording kept |
| **C9** | Seven lines this phase added exceed 100 columns, **five in `evidence/register-check.py`** — a `.py` under `docs/`, which `make lint` never inspects | `prompt.md` is acted-on | fixed |
| **C10** | Only 3 of the 10 tests were ever shown capable of failing; the three added last were never mutated | phase note | **run — see below.** All three kill their mutants |
| **A4** | The plan's six **"Done when"** criteria were never walked as a list | process | walked, in `notes-group-e.md`; all six met, one weaker than it reads |
| **C11** | `notes-review-plan.md` has a list marker inlined mid-paragraph, so two bullets render as one | phase note | fixed |
| **C12** | `notes-review-plan.md` cites `dotenv/main.py:418`; the call is at **:419** *(REPORTED — the pin allows a different resolved version)* | phase note | fixed |
| **A5** | The plan and the charter name **different commit ranges** for the same review, both ending before the tree actually read | the review's own provenance | recorded here rather than fixed — see "Refused" |
| **C13** | `branch-index.py --check` exits 0 while skipping the branch under review, by construction | instrument | **not a defect.** Recorded so nobody reads its green as clearance |
| **C14** | `evidence/wheel-contents.md` no longer re-derives in 2 of 23 rows | phase evidence | **the capture is not edited.** A note in `evidence/README.md` explains why — see below |

---

## The mutation run that finding C10 forced, and what it found instead

**The three tests added with `.env.example` had never been shown capable of failing.** The phase's
recorded mutation run — *"3 failed, 4 passed"* — was against a **seven**-test file, and three more
arrived one commit later.

**All three kill their mutants. But the first attempt said one of them did not, and the reason is
the finding.**

Three mutations were applied at once, following the method `notes-group-c.md` records: `init`'s
target path redirected to the working directory, the both-targets existence check narrowed to one,
and the env template's bytes changed. **Three tests failed — and not the three expected.**
`test_env_template_matches_the_repository_env_example` **passed under a mutation that should have
killed it.**

**Because the first mutation repaired the third one's precondition.** Redirecting `init` to
`Path.cwd()` made a test write `.env.example` into the repository root — overwriting the real file
with the mutated template — so the comparison the third test makes became trivially true. `git
status` showed a modified tracked file that no edit had touched.

**Isolated, the third mutation kills its test.** All three are sound.

**The lesson is about the method, not the tests.** *A batch of mutations can mask a member of the
batch*, and nothing in the phase's account of its own mutation run guards against it. Group C's
three happened not to interact; it had no way of knowing that. **A mutation that changes where code
writes can also change what the test suite writes** — which is the same hazard as the interrupted
sweep that once left a module comment-stripped, arriving from the other direction.

---

## Refused, with the reason

**A5 — the two review instruments name different commit ranges.** `review-plan-jobs-done.md` says
`80914a0..b0070e5`; the charter says `..15cb2bb`; the runs actually read the working tree at
`0c5ce2d`. **Not fixed, because editing either document to name a later hash would make it wrong
again the moment anything else lands** — which is the defect, not the cure. *The general fix is to
state the range at the moment the runs start, and it belongs in the `IDM` that gets written from
this run rather than in a patch to a spent charter.* Recorded here so the next review inherits it.

*`IDM-004` rule 4 makes refusals first-class: a review that fixes everything it found has no
refusals by construction, which is a warning sign rather than a clean result.*

---

## The question for the owner — and it is why this branch is not merged

**Settled row 6 makes a finding a *question* when acting on it would reverse or narrow an owner
decision. There is exactly one, and the review did not create it — it confirmed one this session had
already raised.**

**Settled row 6 of `plan.md` fixes the `README.md`'s caveats section at four items.** Group E found
a fifth there, written by this session, and moved it out to "What it does, and what it does not"
rather than deleting it. The cold reader's observation is sharper than the note's:

> *the move made the README's caveats section pass a check that counts paragraphs, not facts — the
> same fact is still one bullet away.*

**Both states honour the letter of the decision. Only one of them is what the decision was for.** If
four caveats meant *"do not bury the reader"*, the current state is right. If it meant *"these four
facts are the caveats"*, then a fifth caveat-shaped fact sitting one section up is the thing the row
was meant to prevent.

**It is one line, either direction, and it is the owner's.** Everything else in this review is
fixed, refused with a reason, or filed.

---

## What was checked and found correct

**This section is what makes *nothing found* usable rather than empty**, and most of the review is
in it.

- **All 448 tests pass**, `make lint` clean at the pinned `0.16.1`, `register-check.py` 28 of 28,
  `branch-index.py --check` exits 0, `link-check.py` at its expected count. **The tree was clean
  before and after everything either run executed**, checked with `git status` each time.
- **No assertion in `register-check.py` compares a file to itself.** All 28 read; checks 13 and 14
  compare a package template against a distinct repository file, which is the one thing that would
  make them vacuous and exactly what they exist to prevent. Seven pass by absence — weak, not
  vacuous.
- **The `--help` block in `README.md` is byte-identical to the shipped binary's**, verified
  independently by the cold run at `COLUMNS=80`.
- **Settled rows 1–12, each against what shipped.** Row 1 in particular: no environment variable for
  the config path was introduced. Row 7 held — the phase declined scope through `backlog.md` rather
  than silently. Row 8's inherited commitment is discharged into "Commands", carrying the dictionary
  commands, `extract`'s selection grammar, the cross-day refusal and the history-viewer warning.
- **The plan's register is honest**, with no unvalued rows, and the two rows Group E corrected say
  so in the row itself.
- **Nine claims re-derived from the repository with no trust required**, including `load_dotenv`'s
  behaviour read from python-dotenv's own source, both template byte-identities, the wheel's
  contents, `corpus.py`'s unstored-not-truncated rule, the absence of any retry construct in the
  proxy, `stats.py`'s 20 columns, and the brief's 1027 bytes against `5895359`.
- **Nothing this phase wrote reached `docs/reference/`**, which caps the blast radius of everything
  above. `CLAUDE.md` was the one canon-tier file it touched, and it touched it by *not* touching it.

**Taken on trust, and named rather than hidden:** the `uv tool install` / `uv tool upgrade`
behaviours, which cannot be re-checked without installing — the charter's own instruction was that a
claim settleable only by installing is a finding saying so. What *could* be checked is that
`README.md` says exactly what the seven-run table records, in both directions, and it does. Also
untraced: the "33 inherited" half of task 14's sweep, whose 38-element list was never frozen —
**33 + 5 = 38 is arithmetic, not evidence.**
