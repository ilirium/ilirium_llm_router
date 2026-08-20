# Status

**State, not inventory.** Unscheduled work lives in `backlog.md`; this file says where the project
is and what is in flight. Three sections, most volatile first.

---

## Where we stopped

*Changes every session. If this section passes ~30 lines, or starts carrying anything that outlives
the session that wrote it, it has become a document and gets its own file.*

**2026-08-20, later — Group E is done. Tasks 16 and 17 have run, and Group F is next.** `calls.csv`
and `router.log` are now `logs/telemetry/calls.csv` and `logs/telemetry/router.log` in `config.yaml`
and in `config.py`'s two defaults, and **eleven live sites** across four repository files, four
documents and two instruments were repointed. **No test was added: this changes where two files are
written, not what the router does.**

**The live files were not moved, and that is an owner decision rather than an omission.**
`logs/calls.csv` (42,479 bytes) and `logs/router.log` (60,244 bytes) stay at `logs/`; the router
creates the new pair on its next start, so **`logs/telemetry/` does not exist yet.** The row is in
`plan.md`'s "What is settled, and by whom". **Task 18's layer-3 check therefore starts from an empty
location**, which makes *"a real call produces a row"* unambiguous.

**Task 17's sweep list was one citation short, and the missing one was the load-bearing half.**
`notes.md` finding 9 names `probe.py:290` — the printed message. The path the probe *opens* is
`probe.py:48`, `CALLS_CSV = ROOT / "logs" / "calls.csv"`, assembled from segments and so invisible to
the grep that built the list. Repointing only the message would have left the probe reading a file
that no longer exists while naming the new one. **Both are fixed.** The audit that found it searched
for the segment, not the path.

**Two green results were interrogated rather than accepted.** `link-check.py` reporting an unchanged
count is also what a tool that never looked would report — so the mechanism was read: `resolves()`
returns `True` for any first segment in `RUNTIME = {"logs"}`, so the new paths **are** reached and
**are** deliberately skipped. And two mutations that both failed the *same* test were re-read for
*which* assertion fired; the two `config.py` defaults are pinned separately, not by a short circuit.

**Baselines, run not predicted: `make test` 308, `make lint` clean, `make check` valid,
`link-check.py` 85 files, 79 broken, 2 roundabout — unchanged.** *(The entry below reads **82
files**, and that is not a stale figure copied forward: the three commits since it added three `.md`
files — 69 tracked then, 72 now. Checked, because a count that drifts while everything around it
holds is exactly the shape of a number nobody re-ran.)*

**2026-08-20, later — Task 15 has run and Group D is complete.** A real dictionary is installed:
`logs/corpus/dicts/req-2026-08-20T110338Z-0e4d84d1.dict`, 262,144 bytes, put there by the router's
own `--train-dict` rather than by hand. **The first durable state this phase has created outside a
scratchpad**, and only two files were written — the dictionary and `retrain.log`. **Group E (the
telemetry move) is next.**

**The figure is `12.919x` on held-out material, measured on disk** — bodies written through the store
and read back with `--extract` — against **`2.997x`** undicted. It agrees with the trainer's own
in-memory `12.920x` to four significant figures by two independent paths, and the undicted baseline
reproduces Task 6's frozen 701,407 bytes to within 9.

**A third 26x nearly went into the record.** Storing all 73 corpus bodies and reading the folder back
gives **26.870x** — meaningless, because 48 of the 73 are the dictionary's own training material.
That is *"train on a day and score on that same day, and the candidate always wins"*, which this plan
states and which the held-out slice exists to prevent. **It is the second 26-point-something of the
phase**, after Task 14e's `26.210x` leakage, by a different mechanism and to a suspiciously similar
number — **anything near 26x on this corpus should now be read as a self-scoring accident until
proven otherwise.**

**The parameter choice was re-derived rather than cited, and the best cell was deliberately not
taken.** `maxdict=262,144` because the **plateau starts there** — bigger caps give the same ratio in
a 478,604-byte file, and that size recurs in every day folder that uses it. `k=8,000` although the
surface's best is **k=16,000 at 12.964x**: the margin is **0.34%**, an eighth of `INSTALL_MARGIN`;
this corpus has **no usable validation split**, so taking a surface's argmax is selecting on the
slice being reported; and at `maxdict=112,640` that same `k=16,000` is the **worst** cell on the
board at 8.657x. **Provisional, not optimal**, and the shipped defaults are unchanged.

**What travels with the number, for Task 21:** the training set was **48 bodies, 26 distinct — 46%
`overloaded_error` retries**; the held-out slice is run-03, **21 bodies, all distinct, no retries**.
Phase 9's `12.10x` remains the milestone's figure and remains optimistic; `13.65x` is still not
reproducible, being a *write* level 19 measurement.

**The round trip was verified in a scratchpad holding a copy of the installed file, not by writing a
day folder into `logs/corpus/`** — the bodies are Phase 9 captures, and filing them under today's
date would leave a day of traffic that never went through the router in the one place meant to be a
faithful record.

**Baselines, run not predicted: `make test` 308, `make lint` clean, `make check` valid,
`link-check.py` 82 files, 79 broken, 2 roundabout — unchanged.**

**2026-08-20, later — Task 14f has run. Every lettered task in Group D is done; only Task 15
remains.** **`make test` went 301 → 308.**

**14f's three named cases had already landed with 14c**, so this task began with a **coverage audit
rather than with writing tests** — the only honest way to answer *"tests for all of the above"*
without padding. Thirty-five methods in `dictionary.py` checked against whether the test file names
them at all; seven unmentioned, four of those covered through their callers, and **three genuinely
untested — one of them a stated behaviour of the design**: `_sweep_staging` (*"`.incoming/` is swept
at startup"*), `_spawn` (in-process single-flight, which sits **on top of** the cross-process lock,
not instead of it), and `_run_quietly`. Two positive cases were missing beside them — `on_day_rollover`
was only tested where the budget **refuses**, and `start()` had never been driven from call to
installed file.

**One test would have been worthless written the obvious way.** *"The training thread never raises"*
cannot be asserted by the process surviving: an uncaught exception in a thread **also** leaves the
process alive, so spawn-join-assert-still-here passes with the handler deleted. It asserts on the
**log** instead, which is the only observable the behaviour has. **`caplog` is new to this repository**
and is introduced for exactly that one case.

**Six mutations, all caught**, two of them failing two tests each — the sweep mutation also broke
Task 18's observation 1, that a disabled corpus leaves no trace.

**Baselines, run not predicted: `make test` 308, `make lint` clean, `make check` valid,
`link-check.py` 82 files, 79 broken, 2 roundabout — unchanged.**

**2026-08-20, end of session — Task 14e has run; only 14f remains and Task 15 is unblocked.**
`--train-dict`, `--tune-dict` and `--from <dir>` all work and were driven against the real corpus.
**`make test` went 293 → 301.**

**A leakage defect was caught by its own number being too good.** The first
`--train-dict --from logs/corpus-gate` reported **26.210x** against an expected ~12.9x, because
`logs/corpus-gate/dicts/` — **eight dictionaries trained on those very captures** — was swept in as
a "session" of training material while `run-01`, whose content sits inside them, was the held-out
slice. **The exact leakage leave-one-session-out exists to prevent, reintroduced through a directory
listing.** Now excluded **by content**: a file starting with zstd's dictionary magic is never a
training sample, wherever it sits, because the folder name is a convention and the magic number is a
fact.

**The split rule was wrong beside it.** It held out the *largest* session — on this corpus `run-01`
is 46 of 70 usable bodies, so the majority would be held out and the minority trained on. It now
holds out **the last session by name**, which is `run-03-anthropic`: **exactly `gate.py`'s split**,
which is what makes the result comparable with the frozen evidence — the whole reason
"one subdirectory is one session" was chosen.

**After both fixes it lands on 12.920x and dictID `0e4d84d1` — the same ratio and the same
dictionary Task 14's hand-written exercise produced by a different route.** A CLI path and a script
independently reproducing one dictionary is the strongest cross-check this phase has had.

**Each behaviour driven separately:** `--train-dict` works with **`corpus.enabled: false`**; a second
run **bypasses the guard and is refused on the margin** (`+0.00%` against 2%); `--tune-dict` prints
the **whole 4×3 surface** and installs nothing (1 dictionary before and after); `--maxdict 0` is
rejected by the config model's own bounds rather than by libzstd much later. The sweep **reproduces
Task 6's shape** — non-monotonic in `k` at 112,640, plateau above 262,144.

**Five mutations; four caught.** The survivor was a **genuine redundancy, not a gap**:
`_with_overrides` validated the `retrain` block and then rebuilt the whole `Corpus`, which validates
it again. The dead line is gone and removing the remaining validation now fails a test. **A surviving
mutation is either a missing test or a line doing nothing, and it is worth finding out which.**

**Baselines, run not predicted: `make test` 301, `make lint` clean, `make check` valid,
`link-check.py` 82 files, 79 broken, 2 roundabout — unchanged.**

**2026-08-20, later still — Task 14c has run and a running router picks up a new dictionary.** The
worker relists `<dir>/dicts/` every `RESCAN_EVERY` (500) bodies **and** on opening a day folder, and
swaps when the newest name differs. **`make test` went 282 → 293.** **14e and 14f remain**, then
Task 15. *(14f's three named cases were built with 14c, because they prove the pickup rather than
check it afterwards.)*

**The task's real output is a defect that would have made blobs permanently unreadable.**
`ZstdCompressionDict` **accepts arbitrary bytes**, returning a valid *content-only* dictionary whose
`dict_id()` is **0** — so a stray `*.dict` file in `<dir>/dicts/` was adopted silently, which the
pickup is what made reachable. Frames written against it report dictID **0**, which is exactly how
*"stored with no dictionary"* is spelled, so **`CorpusReader` never tries a dictionary at all** and
the blob raises `Data corruption detected`. **A day folder that looks complete and cannot be opened
— failure mode 2 in the one form nothing else here catches.**

**Fixed where the guarantee already lives.** `_build_compressor` exists to prove the compressor
writes a dictID into every frame; one reporting 0 proves it does not. It now refuses, which lands
correctly on both paths with no second rule: **construction raises and the router refuses to start**
(the owner's 2026-08-19 decision, unchanged), and **rescan catches it, keeps the current dictionary
and warns**. Recorded in the settled table as an **extension of that row**, not a new decision.

**It was found by a test written from driving intent, and nearly closed as a non-issue.** The first
measurement was *benign*: junk bytes sharing nothing with the body give a self-contained frame that
decompresses fine. Only a content-only dictionary the body actually matches against shows the loss.
**The reassuring measurement was the wrong one.**

**Driven mid-day and across a rollover** on real corpus-gate bodies: undicted, install, not swapped on
the next body (by design), swapped after 500, a second dictionary picked up at the rollover.
**504/504 blobs verified** from folders mixing undicted and two-dictionary material, and the day that
used two dictionaries **keeps both copies**.

**The instrument was wrong a third time, in the same shape.** A swap looked failed — `dict_id=none`
after the threshold — while the writer plainly held the new dictionary. **The body was a duplicate**,
so `store()` correctly read the dictID off the blob already on disk: Group C's rule working as
decided, caught by an instrument testing a swap with a repeat body. **Three instrument errors this
phase, every one producing a plausible number.**

**Six mutations; five caught immediately.** The surviving one — dropping the "did the name actually
change?" check — is invisible behaviourally, since rebuilding yields an identical compressor. What it
costs is a probe compression per rescan and a log line announcing a switch that did not happen, so
the new test asserts **object identity**, the only observable there is.

**Three open questions were also settled by the owner and applied:** the sample floor **gets no
constant** (libzstd's refusal is caught and recorded instead — its limit is total bytes, not a count);
`--from <dir>` will treat **each subdirectory as a session** so leave-one-session-out runs on
`logs/corpus-gate/`; and **`CorpusWriter` keeps plain values** — which required correcting the
register, since it described the writer as *"built from its config block"* when it is not. Group C's
open item 2 is closed. **Task 15 will install into `logs/corpus/dicts/`**, the live directory, as its
row says.

**Baselines, run not predicted: `make test` 293, `make lint` clean, `make check` valid,
`link-check.py` 82 files, 79 broken, 2 roundabout — unchanged.**

**2026-08-20, later — Tasks 14a and 14b have run and the router retrains itself.**
`DictionaryTrainer` now carries the training thread, both triggers, the cross-process lock, the
today-guard, the window, the leave-one-session-out split and `retrain.log`. **`make test` went
250 → 282.** **14c, 14e and 14f remain**, then Task 15.

**They landed in one commit** — the same departure Tasks 9 and 10 made, for the same reason: split,
14a would have committed a thread that collects a window and discards it, since a run cannot reach a
verdict without 14b's held-out slice.

**Driven end to end on a two-day corpus built from `logs/corpus-gate/`, in a scratchpad.** The window
**widened** to two days because each day carries one session; the split held out 20 and trained on 24
with no body on both sides; the first run **installed**, the second was **stopped by the guard**, and
`--train-dict`'s bypass trained and was **refused on the margin**. A fresh `CorpusWriter` then loaded
the installed dictionary by name, stored a body against it, and that body **read back byte-identical
from the day folder alone**. A genuinely separate process held the lock and this one could not
acquire.

**A race was found by reading and would not have been found by driving.** The today-guard was checked
only *before* the lock, so two processes could both pass it, queue, and have the loser retrain from
exactly what the winner just used. **Checked twice now** — the cheap check first so the common case
never takes the lock, the correct one under it.

**The sample floor should not get a number, and that is the finding to carry.** `plan.md` stops
training *"below a viable sample count"* and the register gives no value. Measured: libzstd refuses at
5 and accepts at 8 **for these sizes**, and the threshold moves with `k` and sample length — its error
is `Src size is incorrect`, about **total bytes, not a count**. **A fixed `MIN_SAMPLES` would wrap a
constraint that is not a count.** What ships: the two floors needing no constant are checked and
recorded, and libzstd's own refusal is caught into `retrain.log`. **Flagged for the owner, not
closed.**

**The lock is `O_EXCL`, not `flock`, and that is a reading of the plan rather than a preference** —
*"a stale lock from a killed process is broken by age"* only describes `O_EXCL`, since `flock` is
released by the kernel on death and would make `LOCK_STALE_S` dead code. The cost is named: a
`kill -9` holds it for up to an hour. **Its age is read from inside the file, never from mtime**, and
a test touches the mtime to prove it.

**Two more register holes closed:** `retrain.log`'s *format* was never shaped (now UTC stamp plus
`key=value`), and its `seconds` field is load-bearing — `TRAIN_BUDGET_S` is read back from it so the
rollover trigger survives a restart, which the in-memory design could not do. The `.incoming/` versus
`incoming/` question the register raised is also **closed**: the dot-prefix keeps staging out of the
listing the pickup globs.

**Eight mutations, all caught** — including the holdout taking the smallest session, the window never
widening, and the rollover firing on a process's first day. **One test helper was wrong twice**, both
times the helper and not the code: it generated 26 distinct bodies and repeated, so the
content-addressed store collapsed two sessions into one; and its bodies were ~410 bytes, **under the
1,024-byte sample floor**, so the trainer correctly refused them all.

**Baselines, run not predicted: `make test` 282, `make lint` clean, `make check` valid,
`link-check.py` 82 files, 79 broken, 2 roundabout — unchanged**, correctly: this task cited nothing
unbuilt and added no `*.md`.

**2026-08-20 — Task 14 has run and Group D is open.** `src/ilirium_llm_router/dictionary.py` exists:
`content_dict_id()`, `stamp()`, and `DictionaryTrainer` with `train` / `score` / `consider` /
`install`. **`make test` went 218 → 250.** The thread and trigger are 14a's, the split and the margin
14b's — `consider()` takes both the holdout slice and the margin as arguments, which is the narrowing
the second review applied.

**The number landed exactly where two earlier instruments said it would: 12.920x** on gate.py's split
at write level 9, with the undicted baseline at **701,407 bytes / 2.997x** — Task 6's frozen figure to
the byte. **A third instrument agreeing with two written on different days** is what makes it worth
recording. Training took **0.03 s** against `TRAIN_BUDGET_S` of 60, so 14a's gate is a formality at
this corpus size — **re-measure it, do not inherit it.** `13.65x` is still not reproducible and no
attempt was made; Task 15 records its own.

**Two tests were green and proving nothing, and seven deliberate mutations are what found them.** The
`or 1` guard against a zero dictID was **unreachable through its own public function** — no
dictionary's sha256 starts with four zero bytes — so the arithmetic was split into `_id_from_digest`
to make the branch testable. And the `k` test called `zstandard.train_dictionary` **directly**, so it
passed unchanged with the trainer no longer forwarding `k` at all — the exact 15%-worse trap Task 6
measured, and it would have shipped silently. A third weakness needed no mutation: the refusal test
retrained on identical material, which is **byte-identical**, so its improvement was exactly `0.0` and
it never touched a genuinely *worse* candidate. **All three are fixed and all seven mutations now fail
exactly one targeted test.**

**One instrument lied plausibly.** The first exercise run reported our stamped dictID and libzstd's as
the same value — it was reading the "libzstd" ID off bytes that were *already stamped*. Measured
against an unstamped run, libzstd says **2026200612** and we say **239961297**. **Fix the instrument
before believing the result**, and this one is written down because the wrong number was *plausible*.

**Three owner decisions, in `plan.md`'s register and `notes.md` with their rejected alternatives:**
`DICT_MAGIC` gets a name and a register row; `newest_dictionary()` is **lifted into `corpus.py` and
shared** so the worker and the trainer cannot drift on which dictionary is current (`_write_atomically`
went public as `write_atomically` on the same reasoning); and `DictionaryTrainer` takes the **`Corpus`
config block**, closing Group C's open item 1.

**Baselines, run not predicted: `make test` 250, `make lint` clean, `make check` valid, `link-check.py`
82 files, **79 broken**, 2 roundabout.** **It fell 82 → 79, and this session predicted 81 and was
wrong** — `dictionary.py` was cited **three** times, once in `prompt.md` and **twice in the plan's own
register**, not once. The prediction was caught only because the tool was run before the commit, which
is the fourth time this phase has made that mistake and the first time it was caught in the same
session.

**2026-08-19, later still — Task 7 has run and Group C is open.** The smoke test passed on the first
run: 40 bodies, both directions, dicted at level 9 and undicted, **all byte-identical**, sha256 of the
round trip equal to sha256 of the original. Frozen as `evidence/smoke.py` / `smoke.txt`. **Still no
`src/` change** — `git diff main -- src/` is empty and **Task 8 is where that changes.**

**It found something nobody had listed as an assumption: a dictID is not a unique key.** `zstd --train`
stamps **1** on everything, so Phase 9's eight frozen dictionaries are **six distinct files all
carrying `1`**. `zstandard`'s own trainer at `dict_id=0` is **not random per call** — identical input,
identical ID. And the same samples at levels **3 / 9 / 19** give **one ID and three different files**,
which is `plan.md`'s stated `TRAIN_LEVEL` hazard **reproduced independently**.

**Both failure modes are loud, which is the half the plan did not state.** The wrong file of a matching
ID raises `Data corruption detected`; no dictionary at all raises `Dictionary mismatch`. Neither
returns plausible wrong bytes. **So Task 13a treats the dictID as a lookup hint** — try each candidate
in the day's `dicts/`, keep the one that verifies against the digest in the blob's filename — and that
constraint is now in its row.

**`write_dict_id` was confirmed on the backend that actually runs.** Task 8's requirement cited
`backend_cffi.py`, which `wiki/zstandard-and-libzstd.md` warns is **the backend we are not on**;
measured on `cext`, the trap is real. **That wiki page was corrected**, per the rule that a
contradicting finding's measurement stays in the phase note and the correction goes to the file that
owns the fact — it had called `dict_id=0` a *random* ID, from a CFFI docstring.

**The owner then asked whether we can stamp our own dictID, and we can — so we will.** Measured:
`train_dictionary(dict_id=N)` takes **any `uint32` verbatim**, and the ID also lives at **bytes `[4:8]`
of the dictionary file** after magic `0xEC30A437`, so a trained dictionary can be **re-stamped in
place** with the compressed output byte-for-byte the same size. **Decided 2026-08-19: the router
derives its own** — sha256 of the dictionary with its own ID field zeroed, first four bytes, `or 1`,
as `content_dict_id()` in `dictionary.py`, applied by Task 14. It gives **three IDs across levels 3 /
9 / 19 where libzstd gives one**, so that hazard is closed by construction. **`TRAIN_LEVEL` is not
reversed** and stays 3 on its own measurement. Two traps are recorded: an out-of-range `dict_id`
**does not raise**, and a derived ID of **0** would make every frame claim to be undicted.

**One thing deliberately left unmeasured:** zstd's frame-format spec reserves dictionary IDs `<=
32767` and `>= 2**31` for public distribution. libzstd accepted every value tried, this corpus is
private, and the owner declined to constrain the derived ID to the non-reserved band — **recorded as a
known gap** rather than closed.

**Baselines, run not predicted: `make test` 158 (0.66 s), `link-check.py` 82 files, 86 broken, 2
roundabout — both unchanged.** 86 is correct here: this task cited nothing unbuilt, and the two files
it added are not `*.md`.

**2026-08-19, later still — Task 8 has landed and `git diff main -- src/` is no longer empty.**
`src/ilirium_llm_router/corpus.py`, the blob store: content addressing on the plaintext, the per-day
layout, `write → fsync → rename`, dedup scoped to the day, the `manifest`, and the per-day dictionary
copy. **The queue is Task 9's, the index rows Task 10's, the config Task 11's, the reader 13a's.**

**It was exercised rather than asserted, and `make test`'s 158 is not the evidence** — no test touches
the file until Task 13. What was driven against `logs/corpus-gate/run-03-anthropic/`: an undicted
first run, a byte-identical round trip whose sha256 equals the blob's filename, dedup, the stale-`.tmp`
sweep, and **a writer that stores nothing creating no directory at all** (Task 18's observation 1).
**The one that counts: `tar` the day, unpack it elsewhere, and all 40 blobs opened and verified
against their own filenames from that folder alone.**

**The `write_dict_id` assertion was checked by breaking it on purpose.** Forced onto the
`ZstdCompressionParameters` path, construction raises `CorpusError`. **An assertion nobody has seen
fail is a comment.** It raises rather than falling back to undicted: *"telemetry must never break a
call"* governs the request path, and construction is not a call.

**A gap the plan flagged is closed.** *"Which timestamp decides the folder is unspecified in Task 8"* —
it is the **call's own `timestamp`**, so a body stamped `23:59:59` lands in yesterday's folder even
when it is written after midnight. Driven across the boundary, not assumed.

**Two judgement calls, both in `notes.md`:** the index's column *names* are declared at Task 8 so the
`manifest` can write `len(INDEX_COLUMNS)` rather than a hardcoded 26 that could drift from Task 10's
tuple; and `CorpusWriter` takes a directory and a level rather than a config block, because **Task 11
is the only task that builds that block** and it runs later. No register value moved.

**Baselines, run not predicted: `make test` 158 (0.75 s), `make check` valid, and `link-check.py`
82 files, 2 roundabout, and broken down from 86 to `81`.** **The fall is the point** — five forward
citations to `src/ilirium_llm_router/corpus.py` resolved the moment the file appeared, which is the
behaviour this file and `plan.md` both describe: *it rises when a task cites what it is about to build
and falls when the file appears.* **`dictionary.py`'s citations are still outstanding and Task 14
resolves them.**

**2026-08-19, end of session — Group C is complete and the store works end to end.** Tasks 7 to 13a
all ran. `src/ilirium_llm_router/corpus.py` holds `CorpusWriter` and `CorpusReader`; `config.py` has
the nine-key block; `proxy.py`, `observe.py`, `app.py` and `cli.py` are wired. **`make test` went
158 → 218.** **Group D, from Task 14, is where the next session starts.**

**The claim this group had to make good, and did:** a body goes in through `POST /v1/messages` and
comes back out through the reader, **byte-identical, verified against the digest in its own
filename, from the day folder alone.** `tar` a day, unpack it elsewhere, and every blob opens. That
is failure mode 2 — *archiving cannot stay opaque* — discharged by construction, and the test that
makes it a check uses a body that is not UTF-8 and not JSON at all.

**Four defects were found by driving rather than by reading, and they are the session's real
output.** A repeat body after a mid-day dictionary swap named the **wrong dictionary** — and the
first test missed it because two dictionaries shared a dictID, which is *this morning's* finding
biting the instrument. The summary line reported **`→ 0 bytes`** because a counter was declared and
never incremented. A malformed timestamp made the **corpus root** the day folder, writing `manifest`
and `requests/` beside `dicts/`. And the `write_dict_id` assertion was only worth its line once it
had been **broken on purpose** and seen to fire. **None of these would have failed a test suite,
because none of them had a test until they were found.**

**Four owner decisions were taken and are in `plan.md`'s settled table with their rejected
alternatives:** the router stamps its **own content-derived dictID** (`content_dict_id()`, closing
the levels-3/9/19 collision by construction); a repeat body's dictID is **read off the blob**; the
`write_dict_id` check **refuses to start** rather than degrading quietly; and Task 8's two scope
stretches stand.

**Baselines, run not predicted: `make test` **218**, `make lint` clean, `make check` valid,
`link-check.py` 82 files, **82 broken**, 2 roundabout.** It fell 86 → 81 when `corpus.py` appeared,
then rose to 82 when the rewritten `prompt.md` cited `dictionary.py` — **the handoff file moving the
baseline it quotes, which is the recursion to expect and not a defect.** Task 14 resolves it.

**2026-08-19, later the same day — Phase 10 gained a register, and is *still* at Task 7.** **No `src/`
change exists**; four commits, all documentation. `plan.md` gained **"The register"** — one reachable
section holding **every constant, key, name and magic number the phase would build**, on the owner's
instruction, so they can be checked against the code at the close. **Task 24 now checks it row by
row.**

**Compiling it found eight values the plan named and never gave**, and **all eight were closed the same
day**. `DRAIN_TIMEOUT_S` 5, `LOCK_STALE_S` 3600, `SUMMARY_EVERY` 500 beside `RESCAN_EVERY`'s 500,
`INDEX_SCHEMA_VERSION` 1, the four CLI flag names, `Call`'s three new fields, and the class names —
**`CorpusWriter`, `CorpusReader`, `DictionaryTrainer`**. `corpus.max_body_bytes` was renamed to
**`corpus.body_max_bytes`** so the three size keys share one shape.

**Three of the eight were not holes, and that is why the register is now a `backlog.md` method item.**
The drain timeout **contradicted this phase's own frozen evidence** — *"tens of milliseconds each …
twenty-second shutdown"* against `evidence/results.txt`'s measured **0.433 ms per body**, out by ~70x.
The cadence's justification **did not survive reading**. And `Call` **already uses** `request_bytes` /
`response_bytes` for integer counts. **Two `IDM-004` passes missed all three**, because a review reads
a plan as prose and an absent value reads perfectly well in a sentence.

**`TRAIN_LEVEL` was split from `compress_level_zstd`, reversing a decision made the same morning.**
**There are three levels, not one:** archiving and **scoring** read `corpus.compress_level_zstd` (9),
**training** uses `TRAIN_LEVEL`, now **3**. Measured on the held-out slice, training levels 3 to 19 move
the ratio by **0.03%** — it is not a parameter. Binding both to the key was **refused on a hazard**:
every training level yields **one dictID**, so editing it would change dictionary bytes without
changing the ID the reader finds them by.

**2026-08-19 — Phase 10 was re-scoped, reviewed again, and is still at Task 7.** **The router now
retrains its own dictionary automatically** — the plan had said training was offline and manual,
**that was never an owner decision**, and no review had asked whose it was. **Thirty-two tasks**,
seven lettered, nothing renumbered; the config block went five keys to nine under a nested
`corpus.retrain:`.

**A second forward review ran under `method/IDM-004` and its 22 findings are applied** — charter is
`review-charter-retraining.md`, merged list is in the phase's `notes.md`. **Do not re-review it.**
**The cold run found 16 to the author run's 9, including all four that fail silently**, which is the
strongest evidence `IDM-004` has. Eight findings needed owner decisions and all eight were made.

**The correction worth carrying:** `train_dictionary` takes a `level` that changes which dictionary
you get and defaults to **3**; Task 6's **13.65×** was produced at **19**. So **13.65× is no longer
reproducible**, and Task 15 records the level-9 ratio it actually gets — **measured 2026-08-19 at
12.920×** on the provisional `maxdict`/`k`, which is where it should land.

*This paragraph read "the trainer now trains and scores at **9**" until 2026-08-19, when compiling
`plan.md`'s new **"The register"** found that one constant was doing **two jobs**. **There are three
levels, not one:** archiving and **scoring** both read `corpus.compress_level_zstd` (9), while
**training** uses `TRAIN_LEVEL`, now **3**. Scoring had to follow the key or an operator editing it
would silently score at a level nothing writes at; training was measured to be **irrelevant — 0.03%
across levels 3 to 19** on the held-out slice. Binding **both** to the key was refused on a hazard:
every training level yields **one dictID**, so an edit would change dictionary bytes without changing
the ID the reader finds them by.*

**Two new homes exist.** **`docs/wiki/`** — a tier for what was established by *reading* a dependency,
with three pages and its test in `wiki/README.md`; and **`procedures/event-loop-lag/`**, which
measured that a thread only protects the event loop when the work **releases the GIL**.
`.claude/settings.json` gained `attribution.sessionUrl: false`, the first non-permission entry in it,
with `IDM-002` amended to say what sorts anything that is not a permission.

**2026-08-18 — Phase 10 is executing. Groups A and B are done; the next task is 7.**
`feat/phase-10-body-store`, forked at `d885b2f`. Its `plan.md`
was re-derived and then forward-reviewed under `method/IDM-004`, 22 findings, all applied — **do not
re-plan or re-review it**, and do not reopen the owner decisions in its settled table. **No `src/`
change exists yet**; `git diff main -- src/` is empty and **Task 8** is where that changes.

**Group B benchmarked before any store code and decided four things Group C is written against** —
the GIL **is** released (3.34x on four threads), `compress_level_zstd` defaults to **9**, there is
**no `corpus.workers` key**, and **Task 14 must set `k` explicitly** because the two dictionary
trainers disagree by up to 15% on their defaults alone. **The reasoning and the numbers are in the
phase's `notes.md` and frozen in its `evidence/`**; restating them here is the second copy this file
exists to avoid.

**Two traps worth carrying.** The dictionary is worth far more than the level (3.1x → 11.0x), so
tuning effort belongs there. And **the corpus has no usable validation split** — the smallest run has
two qualifying bodies — so Task 6's best `k` was chosen knowing the test slice, and **Task 15 must
call it provisional rather than optimal.**

**2026-08-17 — Phase 9 is merged** as **`b29d502`**. **Per-call files are the unit**; the decision is
in `reference/design-decisions.md` and the numbers in `reference/measurements.md`. **Read the 12.10×
as optimistic** — three biases flatter it and the slice beside it says which. **Phase 10's 13.65×
does not supersede it**: same three biases plus a fourth, its parameter chosen against the slice it
is reported on.

`main` is ahead of `origin/main` and nothing has been pushed. Phases 7 and 8 are closed. **The
documentation review is still parked whole** in `backlog.md`, including one cheap finding that would
make a session act wrongly — `reference/measurements.md:34`, a slice whose sign reverses.

**Before touching anything:** `procedures/link-check.py` before and after anything that moves, and
`make test` must report **158**. The checker **does not report zero**: **68 broken and 2 roundabout on
`main`** (2026-08-18), and **86 broken, 2 roundabout, 82 files on this branch**, re-derived by running
on **2026-08-19**. *(It was 83 the same day, until `plan.md`'s new "The register" cited `corpus.py` and
`dictionary.py`, then 86 when `prompt.md` cited `corpus.py` too — three forward citations that Tasks 8
and 14 resolve. **The handoff file moving the baseline it quotes is the recursion to expect here**, not
a defect.)* The excess is
`backlog.md`'s recurring false-positive class, and **it rises when a task cites what it is about to
build and falls when the file appears** — today it went 79 → 80 → 76. **Run the tool; do not predict
it from the docstring**, which Phase 8 proved twice gives the wrong answer. *(`make test` is ~0.6 s
warm; a **first** run after the cloud folder evicts the virtualenv takes two to three minutes on
hydration alone — slow, not stuck.)*

## Where the project is

*Changes every phase.*

**One row per milestone. Per-phase detail lives in the archive** — branch, fork point and merge commit
belong to the phase note, and each milestone's own index reads its phases in order.

| | Subject | Phases | State | Read it in |
|---|---|---|---|---|
| **1** | The core router — dispatch, byte-relay, observability, failure handling | 1–7 | **complete** 2026-08-07 | `milestone-1-core/README.md`, which carries every branch and merge hash with what each phase settled |
| **2** | The corpus — capturing bodies for analysis | 8– | **open**, two phases in | `milestone-2-corpus/implementation-plan.md` **until the milestone closes**; its `README.md` is a closing artefact and does not exist yet |

*Changed 2026-08-17 from a per-phase table of Milestone 1's merge commits, per the `backlog.md` item
that proposed it. **The hashes are not lost** — each one keeps two to six homes, the fewest being
`532dc86` and `9c30924` at two apiece, and `milestone-1-core/README.md`'s table is strictly richer than
the one removed. What this file kept is
the part that is **state**; a closed milestone's per-phase merge hashes are archive record, and
`status.md` says so at the top.*

Phases 0 and 1 were fast-forwarded before the `--no-ff` convention existed;
`milestone-1-core/README.md` says why they are left that way. **Milestone 2 starts at Phase 8**,
since 7 is taken.

**What Milestone 1 settles:** no protocol translation is needed, and a local model can drive a real
coding session through the router. Both halves were measured rather than argued — one session reached
both backends, and a local model handled tool use, file editing and multi-turn conversation.

**Milestone 2's subject is `EPD-003`** — capturing bodies for a corpus, **decided 2026-08-17**.

**Its central claim is now named**, at the end of Phase 9 and from what the gate returned:

> *The router can archive every body it carries — as opaque, content-addressed, per-call files
> compressed against a shared dictionary — without parsing a payload, without slowing a call, and
> without special storage infrastructure.*

**One of its three failure modes is already discharged** by Phase 9's measurement; the other two —
that archiving cannot stay opaque, and that it slows a call — are Phase 10's to test.

**Two phases done, neither touching `src/`** — Phase 8 built the method tier and the guardrails, Phase 9
decided `EPD-003` and ran the gate that named the claim above. **Phase 10 is the first of this milestone
to touch `src/`.** `milestone-2-corpus/implementation-plan.md` describes both phases; **their merge
hashes are in their phase notes**, which is where `method/IDM-001-git-branching.md` puts the permanent
record. *(This sentence first said the plan indexes both hashes. It carries Phase 8's and not Phase 9's
— the plan's Record table records the branch **that file** was created on, which was Phase 8's.)*

*This paragraph carried both merge hashes and a note deferring to the `backlog.md` item above. **That
item is now decided and this is the evidence it asked for:** the prose version said "one phase of it is
done" after Phase 9 merged, and stayed wrong until the owner noticed — while the per-phase table beside
it never went stale, because a merged phase without a row is visibly missing and a sentence that
undercounts is not. **The conclusion is not "prefer tables"** — it is that the row-versus-prose choice
is about what goes stale invisibly, which is a different axis from the duplication the item was
arguing.*

## What is next

*Changes every phase. Two or three items lifted from `backlog.md` and cited to it — the file itself
is the full inventory.*

1. **Execute Phase 10 — the body store, from Task 16 (Group E).** **Planned and reviewed 2026-08-18, re-scoped
   and reviewed a second time 2026-08-19; Groups A, B and C are done, and **Group D is complete** — the trainer, its automatic path, the pickup, the manual commands and their tests all landed on 2026-08-20, and a real dictionary is installed in `logs/corpus/dicts/`.**
   The branch is in the table below and the task list is in
   `milestone-2-corpus/phase-10-body-store/plan.md`. **Do not re-plan or re-review it** — its
   re-derivation and **two** forward reviews have run, and **all findings from both are applied**
   (22 in each; the second's charter is `review-charter-retraining.md`).
   *(The 2026-08-19 re-scope is not an exception to that: it was an **owner interview**, not a session
   re-planning work it had been handed, and what it settled is in the plan's settled table with its
   rejected alternatives.)*
   `EPD-003`'s open questions 3–6 are answered in that plan and are **not yet written back into
   `EPD-003` itself** — that is its Task 20. *(This item read "Plan and execute" and restated what the
   phase must settle; the plan now holds that, so restating it here would be the second copy this
   structure exists to prevent.)*
2. **Decide `EPD-001` or `002`.** Both are blocked on a person rather than on work, and both are argued
   on a case Phase 4 measurably weakened — see `backlog.md`, "Decisions waiting on a person". Deciding
   one is cheaper than any measurement in the list. (`EPD-003` is no longer among them — decided
   2026-08-17 by Phase 9.)
3. **Measure whether Claude Code shows LM Studio's context error.** The strongest of the open
   measurements: it decides whether the most actionable message the local backend produces is ever
   seen. `backlog.md`, "Measurements left open".

## In-flight branches

*Merged branches are not listed — git already holds that, and a hand-maintained list would drift.
The permanent record of a phase's branch, fork point and merge commit belongs in its phase note.*

| Branch | Purpose | Tree | Next |
|---|---|---|---|
| `feat/phase-10-body-store` | Phase 10 — the body store, forked at `d885b2f` | docs, the benchmark instrument, `pyproject.toml` / `uv.lock`, and **the whole store: `corpus.py` new, `config.py`, `proxy.py`, `observe.py`, `app.py`, `cli.py` and `config.yaml` all changed, `tests/test_corpus.py` new — and now **`dictionary.py` new, `tests/test_dictionary.py` new**, with `corpus.py` gaining the shared `newest_dictionary()` / `write_atomically()` and an `on_day_rollover` hook, and `app.py` starting the training thread, and `cli.py` carrying `--train-dict` / `--tune-dict` / `--from`. `make test` 308.** `plan.md` now carries **"The register"**, and every value in it is settled, and the telemetry paths now read `logs/telemetry/` | **Task 18** — the configuration check, opening Group F. **Groups A, B, C, D and E are all done** — **E moved nothing on disk**, on the owner's decision, so `logs/telemetry/` does not exist until the router next starts; the benchmark is frozen in `evidence/`, and the executor was chosen from measurement rather than argued. The trainer measured **0.03 s**, so the `TRAIN_BUDGET_S` gate permits day-rollover triggering — **re-measure, do not inherit.** **Re-scoped and re-reviewed 2026-08-19** to thirty-two tasks — the router retrains itself, `13a`/`14a`–`14f` are lettered because execution has begun, and `14d` is **struck and absorbed into Task 11**. The tree also now carries `docs/wiki/`, `procedures/event-loop-lag/` and an `attribution` block in `.claude/settings.json` |

*`docs/phase-9-corpus-gate` merged as **`b29d502`** on 2026-08-17 and this table was empty until Phase
10 opened.*

**It was a `docs/` branch although the phase was about the router**, because no `src/` change survived
it: Task 6 patched `proxy.py` and restored it, and `git diff main -- src/` was empty at the merge.
`method/IDM-001-git-branching.md` is what makes that the right prefix — the prefix says what kind of
work it is, and `phase-N-` says it is numbered work. **Phase 10 is the opposite case**, and it is: `feat/phase-10-body-store`,
opened 2026-08-18. *(This sentence read "will be" until then.)*

`docs/phase-8-method-and-guardrails` was the first branch to **carry a phase number on a `docs/`
prefix** — the form it settled: the prefix says what kind of work it is, `phase-N-` says it is a phase.
`method/IDM-001-git-branching.md` now states that as the rule, with Phase 7 as the old form and Phase 8
as the new one. `main` is ahead of `origin/main` and nothing has been pushed;
`docs/milestone-boundary-restructure` and `docs/phase-8-method-and-guardrails` both still exist locally.
