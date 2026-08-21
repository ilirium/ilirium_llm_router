# Backlog — unscheduled work

**Inventory, not state.** What is in flight and where the project stopped are in `status.md`; nothing
here says when anything happens. An item lands in `status.md`'s "What is next" when it is picked up,
and is deleted from here when it is done.

**Every item names why it is parked, and several name why the question is weaker than it looks.**
That column is the point of this file. An item that has lost its reason has become a to-do, and a
to-do nobody has justified in six months cannot be told apart from one nobody wants.

Started 2026-08-16 from the live items of `milestone-1-core/outstanding-work.md`, which stays in the
archive as the survey it was. Where an item is fully argued elsewhere this file **points rather than
restates** — three of the heaviest are EPDs, and copying their substance here would create the second
copy the documentation structure exists to prevent.

**Grouped by kind, method first.** *Section order set 2026-08-19, on the owner's instruction.* Method
items come first because they change **how the next piece of work is done**, so a session that reads
only the top of this file still reads the part that governs the rest of its behaviour. After that:
documentation defects, decisions waiting on a person, measurements left open, work with an owner-shaped
decision behind it, and instruments and housekeeping.

---

## Method — how work is planned, reviewed and recorded

**These change the `docs/method/` tier, and an `IDM` is in force the moment it is written** — unlike an
EPD, which is parked by definition. An item here is therefore a proposal to change what sessions are
*required* to do.

**A forward review must classify each position by *authority*, not only by correctness.** Proposed
2026-08-19, from the defect that produced Phase 10's retraining interview.

*What happened:* `phase-10-body-store/plan.md` stated, in its own prose, that dictionary training
*"belongs to an offline procedure the router never calls"* — training run by hand, by a person. **The
owner had assumed all along that the router retrained itself automatically**, and only found out by
asking a direct question after Group B had closed. The position appeared **nowhere** in that plan's
"What is settled, and by whom" table. `milestone-2-corpus/implementation-plan.md` names *"a dictionary
bootstrap and retraining policy"* as something the phase must settle; the bootstrap was settled and the
policy half was never written.

*Why it is a method item and not an incident:* the plan was reviewed forward under
`method/IDM-004-reviewing-unexecuted-work.md` by **two passes** — the authoring session and a
fresh-context agent — which returned 22 findings between them. **Neither asked whose decision it
was.** Both checked the plan against the code and against itself, which is what the protocol asks for,
and self-consistency cannot detect a position that is consistently wrong.

*The proposed rule, and it is mechanical rather than a matter of judgement:* a plan that carries an
explicit settled-by-whom table makes the check trivial — **any load-bearing position not in that table
is the plan's own assumption, and the review reports it as unratified rather than inheriting it.** The
instrument already exists; nothing asked the reviewer to use it that way.

*Where it should land:* **an amendment to `IDM-004` rather than a new IDM**, on the argument that it is
a rule about what a review must *find*, and `IDM-004` is the review protocol — two review protocols
would be the drift the method tier exists to prevent. **Left open deliberately**, because that is a
judgement for whoever writes it and this item should not presume it.

*Why it is parked rather than done:* it is a documentation change with no deadline, and Phase 10 is
executing. Doing it mid-phase would put method work on a `feat/` branch, which
`method/IDM-001-git-branching.md` is explicit about.

---

**A forward review must check the plan's numbers against the phase's own `evidence/`, and a value
register is the instrument that does it.** Proposed 2026-08-19, from what compiling Phase 10's
register found.

*What happened:* `phase-10-body-store/plan.md` justified its shutdown drain with *"a full queue is
~640 bodies, which at **tens of milliseconds each** is a **twenty-second** shutdown"*. That phase's
**own** `evidence/results.txt` measures the whole store path at 0.433 ms per body, making the real
figure **0.28 s** — the plan was out by roughly **70x**, against a number frozen in the same folder.
Compiling the register also found **eight constants named and never valued** — one of them cited as
*"the precedent the shutdown timeout already set"*, so the precedent had no value — and a **name
collision** with fields already on `observe.Call`.

*Why it is a method item:* **two `IDM-004` passes missed all of it**, and not by carelessness. A review
reads a plan **as prose, task by task**, checking it against the code and against itself. That cannot
see a stale arithmetic estimate sitting beside a measurement in a sibling file, and it cannot see an
absent value at all — **a constant with no number reads perfectly well in a sentence.** Both defects
are only visible when the values are pulled into a column.

*The proposed rule:* a plan that introduces constants, keys or names carries **one register section
listing every one with its value**, and the forward review checks that (a) no row is empty and (b)
every number the plan asserts is reconciled against the phase's `evidence/` where one exists. **This is
the same shape as the item above** — an instrument the plan already has, that nothing asked the
reviewer to use.

*Where it should land:* also an **amendment to `IDM-004`**, and probably the same amendment as the item
above — both are rules about what a review must *find*. `../README.md` would gain the register as a
named plan section.

*Why it is parked:* same reason as above — method work does not belong on a `feat/` branch. **Phase 10
is the worked example either way**, since its register and the defects it caught are already recorded
in `milestone-2-corpus/phase-10-body-store/notes.md`.

**The merge of `docs/idm-and-claude-md` leaves a work list.** Written 2026-08-21.

*What it is:* `merge-idm-and-claude-md.md` at the root of `docs/`, naming what that merge into
`feat/phase-10-body-store` deliberately does not do — three edits to
`milestone-2-corpus/implementation-plan.md` and two stale playbook citations inside
`phase-10-body-store/`, all of them left because that branch was being written concurrently.

*Why it is parked:* it is not parked, it is **scheduled for the merge**. This row exists only so the
work is reachable from a file that is read routinely, since **`link-check.py` cannot find any of it** —
every stale citation still resolves. Delete this row when the merge file is deleted.

---

## Documentation defects found and not fixed

**The whole of `milestone-1-core/documentation-review-2026-08-16.md`.** A fresh-context agent
reviewed the documentation Phase 7 produced — 23 files, ~5400 lines — and returned a work list:
**five findings verified independently**, roughly 25 more reported but not re-checked, and **six
questions for the owner (Q1–Q6)**. Its Part 5 orders the work by consequence and that order still
stands for what is left. **One of its findings has been acted on; see below. The rest has not.**

*Parked because* the owner parked it whole on 2026-08-17, in favour of opening Milestone 2 and
building router features. It is not blocked on anything and it is not scheduled; picking it up is a
decision to spend a session on documentation instead of on the router.

*Weaker than it looks?* **Two items were not, and both have now been fixed.** Everything else in the
file can wait. Both are recorded below rather than deleted — a finding that vanishes cannot show the
next reader whether it was fixed or forgotten, which is the same reasoning the entries themselves
carry.

> **`reference/measurements.md:34` was fixed on 2026-08-21, on the owner's instruction and outside
> any review phase.** It stated its slice as *"26.6× (no warmup probes)"* while silently inheriting
> the `/v1/messages` filter from the row above it; read as written it recomputes to **0.245×**, LM
> Studio four times *faster* than Anthropic, the sign reversed. **The number was always right and the
> slice label was not** — `measurements.md` now states the filter in full, and keeps 0.245× beside it
> as the trap, on the same reasoning that keeps the 3.9× counter-example. Finding **V1** in the
> review file is untouched and stays the primary record.
>
> This does **not** unpark the review. It was the one item the entry singled out as making a session
> act confidently and wrongly, and it was cheap; the other ~30 findings and the six owner questions
> are exactly where they were.

> **The `README.md` worked example was fixed on 2026-08-17 by Phase 8, and is recorded here rather than
> dropped.** `README.md`'s closing worked example told a filer to create a **second Phase 7**,
> contradicting "Naming and numbering" in the same file. Phase 8's Task 4 was already rewriting that
> sentence for two unrelated reasons of its own, so leaving a known bug inside it would not have been
> scope discipline. See `milestone-2-corpus/phase-8-method-and-guardrails/notes.md`. *The "Weaker
> than it looks?" paragraph above named both items until then, and this note was added when the first
> was fixed: silently deleting one would leave the next reader unable to tell whether it was fixed or
> forgotten. That paragraph was rewritten again on 2026-08-21 when the second was fixed too, on the
> same reasoning — which is why there are now two notes under it rather than none.*

> **G1 — the highest-consequence finding — was fixed on 2026-08-20, and is recorded here rather than
> dropped.** *"The closing playbook is a log of this restructure, not a closing procedure"*: five of
> `EPD-004` decision 12's seven steps were absent from it, the harvest among them. The playbook was
> extracted to `method/IDM-006-closing-a-milestone.md` and repaired on the way — decision 12's seven
> steps restored as its spine, the two landed steps that generalise lifted, the six warnings attached
> to the steps they warn about, and the 2026-08-16 narrative kept in full as evidence. The review's own
> Part 5 said this one is *"bigger than the rest and it wants its own task"*, which is what it got, and
> prescribed *"the generic procedure from decision 12 restored, with the restructure narrative kept
> alongside rather than instead of it"* — which is what `IDM-006` is.
>
> **One thing the finding got wrong, kept because it changes what the repair is.** It read the absent
> steps as work that never happened. All seven *were run*, in Phase 7's own commits, and `IDM-006`
> names the commit for each. They were performed and not written down.

**This entry points and does not restate, deliberately.** The findings, their evidence and the six
questions stay in that one file; copying any of it here would create the second copy this structure
exists to prevent, and the file is far too long to live in an inventory.

**Two consequences of it already landed and are not parked.** Phase 7 is **not** treated as
open — Q2 asked whether it was closed at all, and the owner closed it. And Q5 — where a finding goes
when it belongs to no phase — was answered **for that file only**, by filing it in the archive at the
milestone root; as a general rule for `README.md` it is still open, inside the file with the rest.

## Decisions waiting on a person

None of these is blocked on work. Each is blocked on somebody deciding, and each is argued in full in
`epd/`.

| | Blocked on | Why it may be weaker than it looks |
|---|---|---|
| `epd/EPD-001-model-selection-and-mixed-model-sessions.md` | **a decision only** | Its gate — that a local model can hold a real session — was discharged by Phase 4. Per-request dispatch already satisfies the subagent half with no code, and the `session_id`/`agent_id` columns were accepted separately |
| `epd/EPD-002-token-counting-for-local-backends.md` | **a decision, on a weakened case** | Phase 4 measured the harm it was organised around and found none: the context boundary refuses cleanly rather than trimming silently. Its addendum also records the proposal reading `max_context_length` where it needs the loaded `context_length` |
| ~~`epd/EPD-003-capturing-bodies-for-a-corpus.md`~~ | **nothing — decided 2026-08-17** | Fine-tuning is dropped (analysis only), and its gate ran and passed: a dictionary trained on other sessions reaches **12.10×** against **3.12×** unaided, so **per-call files are the unit**. Graduated into `reference/design-decisions.md`. Its open questions 3–6 survive as **Phase 10 design detail**, not as parked decisions. **Struck rather than deleted** so the next reader can tell it was resolved rather than dropped |

## Measurements left open

Carried from Phase 4's own honest list. Phase 6 graded the live-behaviour claims among these
**consistent with their committed transcripts but not re-measured**, which is the label they should
keep.

**Whether Claude Code shows LM Studio's context error.** It arrives as an SSE `error` event inside an
HTTP 200 — the shape Phase 3 measured being ignored — but as the *sole* event, with no `message_start`
before it, where Phase 3's case followed partial content. *Parked because* nobody has needed it.
*Weaker than it looks?* No — this is the strongest item in the list. It decides whether the most
actionable message LM Studio produces is ever seen by anyone.

**Non-streaming replies.** Every Phase 4 probe ran streamed. `procedures/lmstudio-capability-probes/probe.py`
already has `--no-stream` and it has never been used; the recorder takes a different path for
buffered replies and LM Studio reports `usage` differently there. *Parked because* Claude Code always
streams, so this is about the router's second code path rather than about live traffic.

**Other local models.** All of Phase 4 is `qwen/qwen3.5-9b`. `capabilities` in `GET /api/v1/models`
varies per model — several have no `vision`, several no `reasoning` — so nothing in the
honoured/ignored table transfers without re-running the probes. *Parked because* it is re-running an
existing instrument rather than building one, and expires with each LM Studio release anyway.

**What one day of real use actually contains, and where the training floor is.** *Added 2026-08-19,
from Phase 10's retraining interview; `EPD-003`'s corpus is the subject.* Phase 10 retrains from a
rolling window whose **default is one day**, and nothing anywhere says whether one day holds enough
material to train a dictionary from. *For scale, measured:* Phase 9's **entire** corpus — three runs,
8.8 MB — yields **68 qualifying request bodies**, and its dictionaries were trained on **48**. A quiet
day could plausibly be under ten. *Parked because* **no day-partitioned corpus has ever existed** —
Phase 10's store is the first thing that will produce one, so the measurement cannot be taken until it
has been running for a while. *Weaker than it looks?* No, and it has a consequence already built:
until it is answered the sample floor is a guess, and **the refuse-a-worse-one rule is what stops a
guess doing damage.**

**Whether a response dictionary pays.** *Added 2026-08-19.* Responses are stored **undicted, forever,
by default** — Phase 10 trains a request dictionary only. *Parked because* nothing has measured it.
*Weaker than it looks?* **The opposite — it is stronger than its absence suggests**, and that is the
reason it is written down. The asymmetry is not a finding that responses do not benefit; it is
inherited from what Phase 9's gate happened to measure, and its own `evidence/README.md` says it
answers nothing about responses. **Under automatic retraining it would otherwise become permanent by
default rather than by decision.** Responses may well be the larger volume; nobody has looked.

**Whether archiving slows a call — failure mode 3 of Milestone 2's central claim.** *Added
2026-08-21, from what Phase 10 deliberately did not settle; until then it lived only in `prompt.md`,
which is the one file allowed to go stale, and in `milestone-2-corpus/implementation-plan.md`'s
table.* The claim reads *"…without parsing a payload, **without slowing a call**, and without special
storage infrastructure."* Phase 10 discharged the *break* half by driving it and left the *slow* half
untouched. Settling it needs **one driven session with capture on against one with it off**, comparing
`ttfb_ms` and `duration_ms`. *Parked because* it needs somebody to drive two comparable sessions, which
is not a thing a session arranges for itself. *Weaker than it looks?* **No — it is the only open item
in this file holding a published claim open.** Everything else here is improvement; this one decides
whether a sentence the project already asserts is true. **One trap, from this repository's own
numbers:** the local backend's variance is large — `reference/measurements.md` has the same request
size differing by ≥30% on two days — so a two-session comparison against LM Studio can be swamped by
noise, and the Anthropic rows are the tighter instrument.

**Before planning any of these, grep the frozen artefacts first.** Phases 3, 4 and 5 each found a
third or more of their work already done, measured, or misdescribed. The limit is worth knowing too:
the router logs metadata and never bodies, so old rows prove *a request succeeded* and can never
prove *a request carrying a particular field succeeded* — which is exactly the gap `EPD-003` proposes
to close.

## Work with an owner-shaped decision behind it

**Prompt-cache warmup probes cost 44% of local wall-clock time.** 40 calls returning zero content
tokens, 20.0 of 45.6 minutes in the frozen step 6 session. *Parked because* it has no owner and is
not a bug: `reference/design-decisions.md` records it under "No special case for background or
auxiliary traffic" as an argument *against* that decision rather than a defect in it. Fixing it buys
back nearly half the local wall clock at the price of the first special case in the dispatch rule.
*Weaker than it looks?* The opposite — this is the largest measured cost in the project, and the
reason it is parked is that nobody has been willing to take the trade.

**Three diagnostics reserved out of Phase 10, deliberately.** Named 2026-08-18 when the owner asked
what else should be logged so that loss is diagnosable, and answered *KISS — this is a prototype meant
to be finished and used*. **A live metrics or status endpoint**, for watching queue depth and drop
counts while a session runs rather than reading them afterwards. **A sequence column in `calls.csv`**,
which would make a missing row self-evident instead of inferable from a counter. **Per-failure detail
beyond the counters**, such as an errors file listing every body that was not stored.

*Parked because* the cheap versions of all three already ship in Phase 10: the corpus index says per
call why a body was not stored, the recorder already logs a warning when a CSV write fails, and an
arrived-against-recorded counter pair makes the one silent case visible. *Weaker than they look?*
**The sequence column is refused rather than parked** — `milestone-2-corpus/implementation-plan.md`
makes *"changing `calls.csv`, not its rotation, not its columns"* an explicit non-goal, so that one
needs the non-goal overturned first, not merely scheduling.

**A caller that disconnects before the response generator's first step leaves no `calls.csv` row.**
*Narrowed 2026-08-18, and the original wording was wrong.* This item first said `record()` is never
reached whenever a caller disconnects after the response headers. **It is reached, and a row is
written**: `proxy.py:249` catches `GeneratorExit`, re-raises, and the `finally` calls `record()`.
`reference/measurements.md` carries **six `client_disconnect` rows across both backends**, and the
frozen step-6 CSV has one with 10,027 response bytes already streamed.

**What remains is a race**: if Starlette closes the generator before its first step, there is no frame
to throw into and nothing runs. *Parked because* **it has never been observed** — not in a 142-call
session, not in a 158-call test run — it is a change to Milestone 1's recorder, and the fix must
guarantee it cannot write a row twice, which is worse than missing one. *Weaker than it looks?*
**Yes, and that is the correction:** the original claim would have justified real work; the true one
justifies watching. Phase 10's arrived-against-recorded counters are what would first show it
happening.

> **Observed 2026-08-20, at Phase 10's Task 18a. The "never been observed" clause above is spent.**
> Driven on the ASGI app directly, because the window is too narrow to hit reliably over a socket: a
> caller already gone when the response starts makes `send` raise on `http.response.start`, the
> streaming generator never takes its first step, `watch`'s `finally` never runs, and **`record()` is
> never called** — `1 arrived, 0 recorded, 1 lost`, no CSV row, no log line, no corpus entry. An
> ordinary *queued* disconnect still records, exactly as the 2026-08-18 correction says.
>
> **`proxy.py:256` already named the case**, in the comment justifying `BackgroundTask(reply.aclose)`
> — *"a generator that never runs at all, and so never reaches its own `finally`"*. `record()` is
> inside that `finally`. The case was covered for the connection and not for the row.
>
> **Still parked, and deliberately.** The owner's decision of 2026-08-20 is *report it, do not close
> it*: the duplicate-row guarantee named above is unchanged and is the whole difficulty. What changed
> is that the loss is now **visible** — `app.py`'s `_report_counters` emits the pair at shutdown on
> every configuration, and `tests/test_integration.py` pins the losing case, so closing the hole
> later will announce itself by failing that test.

> **Recorded rather than quietly rewritten.** The wrong version was written into this file, into
> `milestone-2-corpus/phase-10-body-store/plan.md` and twice into its `notes.md`, and it was found by
> a fresh-context review that read `proxy.py` instead of the plan's account of it. It was labelled
> *inferred* throughout, which was honest — **and inference from a correct premise to a wrong
> conclusion is not repaired by labelling it.** The premise was a code comment about the narrow case;
> the leap was to the general one, without checking the measured rows that name exactly this.

**Running the router as several processes — instances behind a proxy, `uvicorn --workers N`, or a
process pool.** Raised by the owner on 2026-08-18 while planning Phase 10, for two reasons: spreading
compression load across cores, and distinguishing concurrent harnesses. *Parked because* **the second
reason is already discharged and the first is not needed at the measured load.** `session_id` and
`agent_id` are header-copied CSV columns, and `milestone-2-corpus/phase-9-corpus-gate/` captured five
distinct sessions and ten subagent rows through one instance — telling harnesses apart is not a
problem this router has. Two to five concurrent harnesses extrapolates to 1–3 calls/second, which is
ten to thirty times inside what a single thread absorbs.

*Weaker than it looks?* **The blocker is not where it appears to be.** Every multi-process form hits
the same wall, and a reverse proxy does not touch it: **the recorder's writers are single-process
designs.** `stats.py` rides `RotatingFileHandler`, whose lock is a thread lock, so two processes
rotating one file corrupt it. Multi-process therefore means either a separate log, CSV and corpus per
instance — fragmenting the telemetry the corpus exists to unify — or making the writers
multi-process safe, which is a phase in itself. **The proxy is the cheap part; the writers are the
expensive part.** Reconsider only if Phase 10's benchmark shows a single worker is actually the
bottleneck.

**The per-backend authentication header name.** `inject` means `Authorization: Bearer` today, which
suits LM Studio and OpenAI; Anthropic's native key is `x-api-key` and Gemini's is `x-goog-api-key`.
*Parked deliberately:* it is needed before the second cloud provider, not before. Phase 5 was told
explicitly not to settle it while editing the same function.

**Extract the portable methodology.** `EPD-004` decision 18 defers this **with a trigger rather than
a date**: when project #2 starts, extraction is a copy of `docs/README.md` with the backend rows
deleted, plus `CLAUDE.md`'s rule block, plus the whole of `method/` unfiltered — `IDM-000` settles that
the tier needs no such filter, because no IDM contains a fact about the router. *Parked because* a
methodology extracted from n=1 is a guess about what generalises. Do not create a global
`~/.claude/CLAUDE.md` before then.

> **Narrowed 2026-08-17. This item is now the extraction only.** The `docs/method/` tier itself was
> **built** in Phase 8 — `IDM-000` through `IDM-003`. Decision 18 declined the tier on a *structural*
> ground, that it would split `docs/README.md`'s acceptance test across two files, and that objection
> was answered rather than overruled: the manual answers *where does a document go* and the tier
> answers *how is the work done*. The n=1 reasoning above is untouched and is still the whole reason
> extraction waits — it was aimed at copying to project #2, which it always was, and never at the tier.
> *This item said "do not build a `docs/method/` tier" until then, which is why the change is recorded
> in place instead of edited away.*

## Instruments and housekeeping

**`procedures/link-check.py`'s exit code carries no information.** `link-check.py:222` is
`return 1 if check(...) else 0` and **there is no expected-failures mechanism in the code** — the
correct-and-permanent hits exist only as prose in the docstring. So the tool exits 1 permanently, can
never gate a commit or a hook despite its own docstring saying *"exits 1 … so it can gate a commit"*, and
reading its output requires a human holding a number from a comment.

**Four pieces of evidence, all from Phase 8, all new:**

- The docstring's counts are **hand-maintained state**, re-derived by Phase 8's Task 17 rather than by
  the tool. A number nobody re-derives is this repository's signature failure.
- **Five of seven "permanent" hits stopped being permanent in a single phase**, and ten further copies of
  the same two paths resolved inside the frozen archive at the same moment — which is why the docstring's
  71 became 61, under a sentence that had said "always".
- **Two independent attempts to predict the new count from the old prose were both wrong**, in the same
  direction, before anyone ran the tool. The prose partitions hits by *where they live*; what resolves
  them is *which path they name*.
- **Every phase plan legitimately cites files it will create.** Phase 8's added 23, all correct, all
  reported as breakage. That is a recurring false-positive class rather than drift.

**Two narrower gaps ride along**, and they are what this item used to be *about* rather than what it is
for. **Heading anchors** are stripped in `candidates()` although `README.md`'s naming table says findings
are "linked by anchor", and **`file.py:N` line citations** are skipped by `is_candidate` for containing
no `/`. Both were verified by hand and both passed — the 11 code citations in a fresh-context review, the
six section titles at commit 6 of the restructure — so they buy repeatability rather than fixing a known
defect. From `EPD-004` decision 21. **Two more were found in Phase 8:** the whole-repository run globs
`*.md`, so citations in `config.yaml`, the `Makefile`, `pyproject.toml`, `.env.example` and `src/` are
unchecked — one stale path was found that way — and a line containing `→` is skipped whole, which leaves
`CLAUDE.md`'s five `→` pointer lines unchecked.

*Parked because* the redesign should be argued from the measurement Task 17 produced, not from the
irritation of having done it once — `EPD-004` decision 12's reasoning, that an instrument which has never
been run should not be committed, applied to an instrument that has. **Decide at Milestone 2's close.**
The cost measured in `milestone-2-corpus/phase-8-method-and-guardrails/notes.md` is the input.

> **The roundabout gap this item once listed is closed.** A roundabout-path check was added on
> 2026-08-16, ahead of the rest, because commit 13 produced two live instances of the defect rather than
> a hypothetical one. See decision 21's second half.

**Static analysis beyond ruff.** Other type checkers, AST-level linters, a language server — over a CLI
or over MCP. `ruff` is all this project runs today; `method/IDM-003-development-tooling.md` records the
pin and what it does and does not catch. *Parked because* nothing depends on it: the code is small, typed
throughout, and covered by 158 tests. *Weaker than it looks?* **Yes, and it is worth saying why the
obvious argument runs the wrong way.** `ty` was tried and **refused** — warnings without useful
information — so the one data point this project has **weakens** the case rather than strengthening it.
The honest reading is that the useful signal may be scarce generally rather than absent from that one
tool, which was at version 0.0.14. **So the next attempt states what it expects to catch *before* it is
run**, and is judged against that rather than against whether it produced output.

~~**`status.md`'s shape — one row per milestone rather than per phase.**~~ **Done 2026-08-17.**
Proposed during Phase 8, deliberately not done there, executed once Phase 9 supplied the evidence it
was missing. `status.md` now carries one row per milestone pointing at that milestone's index.

*Two things checked before executing it, because the proposal rested on both.* **Milestone 1's hashes
were safe to remove** — `milestone-1-core/README.md` holds a strictly richer table (branch, merge hash,
and what each phase settled), and every hash has three to five homes. **But the proposal's "point at
that archive" does not hold for an open milestone:** `milestone-2-corpus/` has no `README.md`, because
per `README.md`'s template that is a *closing* artefact — *"what the milestone was, what it proved"*.
Milestone 2 points at its `implementation-plan.md` until it closes, and `status.md` says so in place.

*The counter-argument this item carried is preserved and was not overturned:* a separate `history.md`
is still declined as a third copy. **What decided it was new evidence rather than the old argument.**
The item said the file "is not actually accreting — the duplication is the whole of the complaint",
and that stayed true. What changed is that Milestone 2's state had been written as **prose** precisely
to avoid pre-empting this decision, and that prose went stale invisibly — it said "one phase of it is
done" after Phase 9 merged. The per-phase table beside it never went stale. **So the axis that decided
it was not duplication but what goes stale visibly**, which the item had not considered.

~~**Close out the four `Branch:` lines that record intent instead of outcome.**~~ **Done 2026-08-21,
on the owner's instruction.** Five lines existed across four of the six phases, in inconsistent
places, and only `milestone-1-core/phase-4-lmstudio-parity/notes.md` recorded the merge commit; the
other four said "Merge back with `--no-ff`" — written before the merge and never updated. All four
now carry their merge commit in the form Phases 4, 8 and 9 already used:
`milestone-1-core/phase-2-observability/notes.md` → `4d7d7f6`,
`milestone-1-core/phase-3-failure-handling/notes.md` → `cc65aed`,
`milestone-1-core/phase-4-lmstudio-parity/plan.md` → `50444c5`,
`milestone-1-core/phase-5-config-and-timeouts/plan.md` → `c8401e9`. Every hash was read from
`git log --merges` and cross-checked against `milestone-1-core/README.md`'s table.

*It was parked as a review-phase checklist item under `EPD-004` decision 14, and the owner took it
out of that ordering rather than waiting for the review.* **Two things are deliberately not done.**
Phases 1 and 6 still carry no `Branch:` line at all — owner's decision, on the ground that the rule
did not exist when they were written, and `milestone-1-core/README.md` holds both records anyway.
And `EPD-004:703`'s *"four of six left open"* is **untouched**: that row records what Phase 6's review
found, not what is outstanding now.

*Kept struck rather than deleted, like the two entries above it.* This was this repository's
signature failure in miniature — a document recording intent and never closed out — and an item that
vanishes cannot show that the mechanism caught it.

---

## Not on this list, and why

**The Anthropic 429 rate-limit headers.** `anthropic-ratelimit-*` and `retry-after` are never
recorded, because the router tees bodies and not headers. Marked **do not go looking**: the recorder
keeps the error body's symbolic type, so the next 429 through the router writes `rate_limit_error:
Error` into the CSV by itself — measured rather than reconstructed. Listed here so it is not
rediscovered and filed as an omission.

**Everything struck through in `milestone-1-core/outstanding-work.md`.** The credential shape and the
read timeout were built in Phase 5; silent trimming below the context boundary was measured and
closed the same day. That file marks them in place rather than deleting them, because what a phase
found already answered is worth as much as what it found outstanding.
