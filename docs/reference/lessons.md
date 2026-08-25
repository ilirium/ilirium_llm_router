# Lessons

How this project has been wrong, and what caught it.

Every episode here was recorded as an aside at the bottom of the phase note that produced it, which
is exactly where it will not be read at the start of the next milestone. This file is the harvest.
The phase notes stay frozen; corrections land here and in `measurements.md`.

Read it as a list of **habits with evidence**, not as a code of conduct. Each rule below is followed
by the episodes that produced it, because a rule whose origin is forgotten is re-litigated.

**Numbers here are stable and never reused: lessons are appended, never inserted.** They are cited
by number from `CLAUDE.md`'s pointers and from the session memory store, which git cannot check —
the same reasoning that keeps numeric prefixes off the filenames in this tier (`EPD-004` decision
7). So the order is discovery, not weight, and 6 and 7 are as load-bearing as 1.

---

## 1. Five times, a phase found its own premise wrong

The single most reliable pattern in Milestone 1. Five of seven phases discovered, in their first
hour or during execution, that the thing they were scheduled to do was already done, already
measured, or wrongly described.

| Phase | What the plan assumed | What was true |
|---|---|---|
| 3 | Five pieces of error handling to build | **Four were already built, with tests.** Phase 2 could not write an `error_status` column without them, so it delivered most of Phase 3 as a by-product of being right about something else |
| 4 | A real session and a set of probes to run | **A third of it was already measured** by Phase 2's frozen session. Reading the CSV first removed a whole step and one probe |
| 5 | Three candidate fixes for the read timeout | **Two of the three did not exist as described.** "Resets on progress" was already the behaviour, and "a wedged backend fails in bounded time" had never been true of duration |
| 6 | The source comments re-argue `CLAUDE.md` and can be cut | **They share a mean 2.8% of their wording with it.** The comments carry measurements recorded nowhere else, and the cut was refused |
| 7 | "The four references" to repoint at the last commit, and **10** of 11 code citations needing edits | **18 references in 8 documents**, and **all 11** citations. The exemption — that `proxy.py:3` cites a section title which survives — was true about the title and wrong about the file, and had been asserted four times across three documents |

**The rule: before planning work, check whether it has already been done — and check the claim you
are planning against, including when it is your own.**

*This was titled "Four times" with four rows until Phase 7 added a fifth on 2026-08-16. A count in a
heading goes stale the moment the thing it counts grows, and nothing re-checks it — which is lesson
6 below, arriving in the file that records it.*

Three things follow that are worth stating separately.

**Artefacts committed for one phase keep answering the next one.** A real session exercises far more
than the question it was run for, so the cheap habit is: before planning a run, grep the frozen CSVs
for the same model and the same question. Phase 4 found this the third time it happened and named it
rather than rediscovering it a fourth.

**Its limit is equally worth knowing.** The router logs metadata and never bodies, so those rows can
prove *a real request succeeded* and can never prove *a request containing `context_management`
succeeded*. That gap is what kept the replay of a known body in Phase 4's plan when the rest of the
step was cut.

**Phases 5 and 6 are a harder version of the same lesson**, because what was wrong was the *record*
rather than the code. Phase 5's timeout options had been repeated across four documents; Phase 6's
comment-density claim was in the review's own plan. Notes about the code drift from the code, and
only a measurement catches it.

## 2. The two ways a number fails

Both happened here, and they are opposite failures. Recorded as a pair, because either one alone
reads as a one-off while the two together are a rule.

**A number can be right and unusable.** `median time to first byte was 1426 ms against Anthropic and
37136 ms against LM Studio, a 26× gap` was quoted forward through three phases. Both figures are
exactly reproducible — but only over *successful streamed `/v1/messages` calls*. Recompute over
every row in the same file, which is the obvious thing to do, and the gap is **3.9×**. A reader
checking the documentation would conclude it was wrong by a factor of seven. Nothing was false; the
slice was missing.

**A number can be reproducible and pointless.** "253 mentions of the 22 moving documents" was
measured because it was measurable, then given jobs by proximity: sizing the work, then standing in
for the work list. It could do neither — it overcounts prose mentions that break nothing and
undercounts relative links that break by depth without naming anything — and it did not reproduce,
because no recipe was recorded. It was **withdrawn rather than re-derived**, which is the part worth
copying. Re-deriving it would have produced a precise number that still had no job.

**The rule, EPD-004 decision 20: a number must have a job, and must be able to do it.** Before
recording one, answer four questions — what is it for, what population is it over, how was it
computed, and with what. `measurements.md` makes this structural: four columns, and a row that
cannot be filled is a number to withdraw. Enforced by a shape, not by remembering.

### A third way, seen once

Assembling `measurements.md` on 2026-08-16 produced a failure that is neither of the above: **two
true numbers joined into a false one.** `CLAUDE.md` said a warmup probe "took 111 seconds for a 31
KB body". The longest warmup probe took 111559 ms and carried **1960 bytes**; the 31786-byte probe
took 103395 ms. The maximum of one column had been paired with a different row's value in another.

It is recorded as an instance rather than a rule, because one occurrence is exactly what the pair
above says not to generalise from. The test it suggests is cheap: **a claim joining two numbers must
name the row they share.**

## 3. Green tests are not evidence

Three times, a full passing suite certified behaviour that was wrong in the field. The tests were
not weak — they confirmed the code did what it was written to do. What they cannot do is show that
what it was written to do is wrong.

- **Phase 2, step 6.** The recorder passed its whole suite and then wrote `stream` blank for 83 of
  142 rows in a real session, because Claude Code omits the field where the tests always supplied
  it. Three more recorder defects came out of the same session.
- **Phase 3.** 146 tests passed while the injected error event read `ReadError:` with a dangling
  colon, because httpx raises a mid-stream reset as `ReadError("")` and every unit test had supplied
  a message.
- **Phase 4.** All 147 tests passed with a read timeout that ordinary local traffic could reach. The
  number was chosen against a hazard that was not the one that arrived.

**The rule: exercise the real thing before believing it works.** Every one of these was found by
driving live traffic, and none of them by a test — which is also why `../procedures/` exists as a
tier: the instruments that produce real traffic are kept runnable rather than described.

## 4. Fix the instrument before believing its result

The companion failure, and it has appeared in three different forms. A measurement that disagrees
with expectation is a claim about *two* things — the world, and the tool.

- **Phase 2.** A mock backend answers instantly, so the first "concurrent writes" test passed
  without ever putting two writes near each other. And the router's own log was rounding timestamps
  to the second, in the phase whose subject was millisecond timing.
- **Phase 6.** The plan's AST comparison declared the first prose-only commit **DIFFERENT**, because
  a docstring is an `Expr` node. Raw AST equality is stricter than "cosmetic" and would have failed
  every edit the review recommended. The tool now compares twice — strict, and with docstrings
  stripped — and only the second is allowed to be a behaviour change.
- **Phase 6 again.** A regression test that has never failed proves nothing: C1's test was run
  against the stashed broken code and confirmed to fail there first. That mattered, because the
  existing helper fed payloads in 4096-byte slices and *slicing was what hid the defect* — the
  obvious test would have passed against the broken code and locked the bug in behind a green check.

**The rule: when an instrument reports something surprising, check the instrument first — and when a
negative result would end an investigation, check it before believing it.**

## 5. Two smaller ones worth keeping

**A design agreed from the shape of a protocol is not a measurement.** The SSE `error` event
injected into a broken stream is Anthropic's documented shape, was implemented, unit-tested and
verified by curl — and Claude Code ignores it. All of that established that the bytes were correct,
never that anyone consumed them. The feature was kept deliberately; what changed is that the record
now says it has **no measured consumer**.

**A number and a superlative in one sentence must use the same unit.** `Status` was called "the
largest section in `CLAUDE.md`" beside a line count. It is largest by *bytes* and third by *lines*.
The claim was false for the unit it named — the same shape of error as the 111-second probe above,
and cheaper to catch than either.

## 6. A count that sizes work is a measurement, not an estimate

Lesson 2 is about numbers in **findings** — what was observed. This one is about numbers in
**plans** — how much work is left. They fail differently and the consequence differs: a wrong
finding misleads a reader, a wrong plan count under-scopes the job and you discover it halfway
through doing it.

Three instances, all from Phase 7, all within about a day of each other:

| The plan said | It was | Found |
|---|---|---|
| "the **four** references" to repoint when two documents move | **18**, across 8 documents | by running the grep at the moment of moving them |
| **10** of 11 code citations need editing | **11** | by editing them |
| **three** permanent link-checker hits that can never be fixed | **seven** | by running the checker over the repository instead of one tier |

**What they have in common is the diagnostic.** Every one was produced by recall or by reasoning,
and none by running a command — in a repository that had the command. Two were a single `grep` away
and the third was the checker's own whole-repository run, which takes under a second. The third is
mine: I measured the live tiers, wrote the number down as though it covered the repository, and the
population I had actually counted was in my head rather than in the sentence.

**The rule: if a number sizes work, run the thing that produces it and name the population.** An
estimate is fine when it is labelled as one. What is not fine is an estimate written in the same
voice as a measurement, because the next person schedules against it.

**It is a sibling of decision 20, not a restatement.** Decision 20 asks whether a number can do its
stated job. This asks something cruder and earlier: *was it ever counted at all.* The failing rows
above would have passed decision 20's four columns — they had a job, a population and an instrument.
They simply had no run.

## 7. A check can pass because its question was too narrow

The companion to lesson 4, and the distinction matters because the remedy is opposite. **Lesson 4 is
an instrument giving a wrong answer** — you fix the tool. **This is an instrument giving a correct
answer to a question that cannot catch the defect** — the tool is fine and was never asked.

Three from Phase 7, in ascending order of how invisible they were:

- **A path can be simultaneously valid and wrong.** Repointing the archive produced
  the roundabout form `../../milestone-1-core/closing-notes.md` → `../closing-notes.md` in a file
  that *is* inside `milestone-1-core/` — it resolves, and it says "go out to `docs/` and come back"
  about the file next door. The link checker
  was satisfied, correctly: it was asked *does this resolve*, and it does.
- **A path inside a code fence may be addressed from somewhere else.** A runnable snippet introduced
  by "run from the repository root" had its path rewritten relative to the citing document. Right
  for a reader, wrong for the command, and both forms resolve to a real file.
- **Nothing in this repository can see a duplicated section**, and one survived two commits — an
  earlier draft of two sections outliving a revert that covered the wrong directories, then a later
  edit inserting before *both* copies because `str.replace` has no count. Not tests, not `ruff`, not
  the link checker, and not a reading of either commit's diff. **What exposed it was the
  roundabout-path check reporting the same unusual path at two line numbers 49 apart** — a check
  asked about path shape, answering a question about document structure by accident. That is luck,
  not coverage, and it is the reason this bullet is in a lesson rather than a changelog.

**The rule: when a check passes, know which property it checked.** A green run is evidence about
that property and about nothing else, and the defects that survive longest are the ones sitting in
the gap between what was checked and what was meant.

**The resolution that worked, all three times, was the same and is worth copying: one more rule in
an instrument that already runs.** The roundabout-path check is fifteen lines added to a script
executed on every commit, and it caught the first class within a minute of being written. The
alternative on the table was a new tool that would have run twice a year — see `EPD-004` decision
21, which measured that trade and refused it.

## 8. Two practices that turn lessons 3, 4 and 7 into something a session can run

**Harvested 2026-08-21 from `docs/prompt.md`, which was the only place they were written down.** The
three lessons above say *what goes wrong with a check*. Phase 10 arrived at two practices that make
them actionable rather than cautionary, and neither had a home outside a file that expires.

**1 — Mutation testing as a matter of course.** Introduce one deliberate fault into finished code and
confirm that a targeted test fails. **A mutation that survives is either a missing test or a line
doing nothing — find out which**, because the two look identical from the outside and have opposite
remedies.

This is lesson 4's rule pointed at the suite rather than at an instrument, and it generalises the
Phase 6 case above: *a regression test that has never failed proves nothing.* That case checked one
test against one stashed defect, by hand, because somebody thought to. The practice is doing it
without being prompted.

**2 — Interrogating a passing check: "what would make this positive anyway?"** Every green result has
at least two explanations, and the second is usually that nothing looked.

- **An unchanged link-check count is also what a tool that never looked reports.** Phase 10 read the
  mechanism rather than the number.
- **Two mutations failing the *same* test is what a short circuit looks like**, not what two
  independent tests look like.

Both were checked before the result was allowed to mean anything, and both times the mechanism had to
be verified first. This is lesson 7's rule — *when a check passes, know which property it checked* —
turned into a question that can be asked out loud.

**The sharpest case, and the reason these are worth keeping.** Phase 10's Task 18 found that **the
number needed to measure a defect *was* the defect.** The instrument has lied repeatedly in this
project and always with a plausible number, which is what makes plausibility worthless as a signal.

*One caution on scope: every defect Phase 10 found was found by driving the thing or by attacking the
tests, and **none would have failed the suite as written.** That is a statement about Phase 10, not a
measured claim about the practices — they were adopted mid-phase and nothing compared a phase with
them against a phase without.*

---

## What this file does not claim

Seven phases on one project, mostly by one person, with one harness and two backends. These are
**this project's** failure modes with the evidence attached, and the sample is too small to say
which of them generalise.

**Lessons 6 and 7 carry an extra caveat.** Both come entirely from Phase 7, which is documentation
work — no `src/` changes, no live traffic, and the only phase of the seven with that shape. Every
other lesson here was drawn from a phase that drove the real thing. Their evidence is real and it is
narrow, and the agent that produced most of the errors behind them also wrote them up the same day,
which is the condition under which a fresh mistake looks more general than it is. That is
deliberate: a methodology extracted from n=1 is a guess about what generalises, which is why
`EPD-004` decision 18 defers extracting one until there is a project #2 to test it against.
