# Lessons

How this project has been wrong, and what caught it.

Every episode here was recorded as an aside at the bottom of the phase note that produced it, which
is exactly where it will not be read at the start of the next milestone. This file is the harvest.
The phase notes stay frozen; corrections land here and in `measurements.md`.

Read it as a list of **habits with evidence**, not as a code of conduct. Each rule below is followed
by the episodes that produced it, because a rule whose origin is forgotten is re-litigated.

---

## 1. Four times, a phase found its own premise wrong

The single most reliable pattern in Milestone 1. Four of six phases discovered, in their first hour,
that the thing they were scheduled to do was already done, already measured, or wrongly described.

| Phase | What the plan assumed | What was true |
|---|---|---|
| 3 | Five pieces of error handling to build | **Four were already built, with tests.** Phase 2 could not write an `error_status` column without them, so it delivered most of Phase 3 as a by-product of being right about something else |
| 4 | A real session and a set of probes to run | **A third of it was already measured** by Phase 2's frozen session. Reading the CSV first removed a whole step and one probe |
| 5 | Three candidate fixes for the read timeout | **Two of the three did not exist as described.** "Resets on progress" was already the behaviour, and "a wedged backend fails in bounded time" had never been true of duration |
| 6 | The source comments re-argue `CLAUDE.md` and can be cut | **They share a mean 2.8% of their wording with it.** The comments carry measurements recorded nowhere else, and the cut was refused |

**The rule: before planning work, check whether it has already been done — and check the claim you
are planning against, including when it is your own.**

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
exactly reproducible — but only over *successful streamed `/v1/messages` calls*. Recompute over every
row in the same file, which is the obvious thing to do, and the gap is **3.9×**. A reader checking
the documentation would conclude it was wrong by a factor of seven. Nothing was false; the slice was
missing.

**A number can be reproducible and pointless.** "253 mentions of the 22 moving documents" was
measured because it was measurable, then given jobs by proximity: sizing the work, then standing in
for the work list. It could do neither — it overcounts prose mentions that break nothing and
undercounts relative links that break by depth without naming anything — and it did not reproduce,
because no recipe was recorded. It was **withdrawn rather than re-derived**, which is the part worth
copying. Re-deriving it would have produced a precise number that still had no job.

**The rule, EPD-004 decision 20: a number must have a job, and must be able to do it.** Before
recording one, answer four questions — what is it for, what population is it over, how was it
computed, and with what. `measurements.md` makes this structural: four columns, and a row that cannot
be filled is a number to withdraw. Enforced by a shape, not by remembering.

### A third way, seen once

Assembling `measurements.md` on 2026-08-16 produced a failure that is neither of the above: **two true
numbers joined into a false one.** `CLAUDE.md` said a warmup probe "took 111 seconds for a 31 KB
body". The longest warmup probe took 111559 ms and carried **1960 bytes**; the 31786-byte probe took
103395 ms. The maximum of one column had been paired with a different row's value in another.

It is recorded as an instance rather than a rule, because one occurrence is exactly what the pair
above says not to generalise from. The test it suggests is cheap: **a claim joining two numbers must
name the row they share.**

## 3. Green tests are not evidence

Three times, a full passing suite certified behaviour that was wrong in the field. The tests were not
weak — they confirmed the code did what it was written to do. What they cannot do is show that what
it was written to do is wrong.

- **Phase 2, step 6.** The recorder passed its whole suite and then wrote `stream` blank for 83 of
  142 rows in a real session, because Claude Code omits the field where the tests always supplied it.
  Three more recorder defects came out of the same session.
- **Phase 3.** 146 tests passed while the injected error event read `ReadError:` with a dangling
  colon, because httpx raises a mid-stream reset as `ReadError("")` and every unit test had supplied
  a message.
- **Phase 4.** All 147 tests passed with a read timeout that ordinary local traffic could reach. The
  number was chosen against a hazard that was not the one that arrived.

**The rule: exercise the real thing before believing it works.** Every one of these was found by
driving live traffic, and none of them by a test — which is also why `../procedures/` exists as a tier:
the instruments that produce real traffic are kept runnable rather than described.

## 4. Fix the instrument before believing its result

The companion failure, and it has appeared in three different forms. A measurement that disagrees
with expectation is a claim about *two* things — the world, and the tool.

- **Phase 2.** A mock backend answers instantly, so the first "concurrent writes" test passed without
  ever putting two writes near each other. And the router's own log was rounding timestamps to the
  second, in the phase whose subject was millisecond timing.
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

**A design agreed from the shape of a protocol is not a measurement.** The SSE `error` event injected
into a broken stream is Anthropic's documented shape, was implemented, unit-tested and verified by
curl — and Claude Code ignores it. All of that established that the bytes were correct, never that
anyone consumed them. The feature was kept deliberately; what changed is that the record now says it
has **no measured consumer**.

**A number and a superlative in one sentence must use the same unit.** `Status` was called "the
largest section in `CLAUDE.md`" beside a line count. It is largest by *bytes* and third by *lines*.
The claim was false for the unit it named — the same shape of error as the 111-second probe above,
and cheaper to catch than either.

---

## What this file does not claim

Six phases on one project, mostly by one person, with one harness and two backends. These are
**this project's** failure modes with the evidence attached, and the sample is too small to say which
of them generalise. That is deliberate: a methodology extracted from n=1 is a guess about what
generalises, which is why `EPD-004` decision 18 defers extracting one until there is a project #2 to
test it against.
