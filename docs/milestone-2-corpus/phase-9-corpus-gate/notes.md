# Phase 9 — decide EPD-003, and run its gate: notes

Branch: `docs/phase-9-corpus-gate`, off `main` at `97f6563`, **not yet merged.** Per
`../../method/IDM-001-git-branching.md`, filling that hash in is the one edit this note takes after
being written — and leaving it reading "not yet merged" after the branch is gone is the defect four
Milestone 1 phase notes committed.

Written **while the work is happening**, task by task, rather than assembled afterwards.

**`evidence/` does not exist yet and may stay small.** The gate's input — captured bodies and the
dictionaries trained on them — **cannot be committed**, on `EPD-003`'s own rule: a body store is *"not
committable, not by redaction and not by placeholder mapping"*, and a `zstd --train` dictionary is a
concatenation of verbatim substrings of its samples, so it inherits that rule exactly. What can be
frozen is the derived table and the script. `../../README.md`'s phase template allows an absent
`evidence/`; this note says why in advance rather than after.

---

## Task 2 — the re-derivation, run **before** Task 1

`../../README.md`: *a phase's first act is to re-derive its own plan against what is now known.*
Five of Milestone 1's and 2's phases found their plan wrong on contact.

**This phase ran the re-derivation before publishing its plan rather than after**, which is a
departure from Phase 8's shape — that phase re-derived at "Task 0", against a plan already committed.
Here the plan did not exist yet: the phase opened with an interview, and five findings landed during
it. So the findings **shaped** the task list instead of correcting it, and no task numbers were spent
on work that turned out to be wrong.

The trade is worth naming, because it is not free. Phase 8's shape produces a visible record of a plan
being wrong, which is evidence about planning itself. This shape produces no such record — the wrong
version was never committed. **What is lost is the diff; what is gained is four fewer lettered
insertions.** The findings themselves are in `plan.md`, "What the re-derivation found, before Task 1".

### What was checked and passed

| Claim | Verified |
|---|---|
| `make test` reports **158** | ✅ 158 passed, 1 warning, 0.60s |
| `procedures/link-check.py` reports **68 broken, 2 roundabout** | ✅ **run, not predicted** |
| Working tree clean, `main` at `97f6563` | ✅ |
| `zstd` present, 1.5.x from Homebrew as `EPD-003`'s Evidence assumes | ✅ 1.5.7 |
| `logs/` is gitignored, so a capture directory under it needs **no new rule** | ✅ `.gitignore:228`; `git check-ignore -v` confirms it covers `logs/corpus-gate/*.dict` |
| `--maxdict` default | ✅ **112,640 bytes**, from `zstd --help` |
| `config.yaml` stats rotation | ✅ `max_bytes: 5242880`, `backup_count: 10` |

**The link-checker count was run rather than predicted.** `../../status.md` carries that as a standing
warning, and Phase 8 proved twice that reading the docstring gives the wrong answer. Predicting it
here would have been the third time.

### The five findings

Recorded in full in `plan.md` rather than duplicated here. In one line each:

1. **The capture is not discharged.** `../implementation-plan.md:103` hedged that step 3 *"may already
   be discharged"*; it is not. `../../captures/` holds **one** body, and one body cannot exercise a
   cross-body dictionary. The gate is a live capture plus twenty minutes of `zstd`, not twenty minutes
   of `zstd`.
2. **`EPD-003`'s gate, run as written, trains on its test set** — and the fix, a held-out split, turns
   out to measure the static-versus-session-local decomposition directly rather than merely adding
   rigour.
3. **`--maxdict` defaults to 112,640 bytes and the static preamble is ~110 KB** — so a single-point run
   could not tell "a dictionary cannot recover this" from "the dictionary was capped below the thing it
   needed to hold".
4. **`calls.csv` expires**, so `EPD-003`'s plan to use it as the corpus's join table would leave bodies
   outliving their own index. **Independent of the gate** — true whatever the compression numbers say.
5. **Concurrency dilutes a dictionary**, and the capture as first planned would have hidden it.

**Findings 3, 4 and 5 came out of the opening interview rather than out of any document**, and two of
them are about `EPD-003` being wrong in ways the gate would never have caught. Finding 4 in particular
is a storage-design defect surfaced by a compression question — recorded here because it is the kind
of thing that is expensive to rediscover.

---

## Task 3 — the decision, and the sweep it grew

`EPD-003` → **partly accepted**, `EPD-000`'s vocabulary for *"one named piece was accepted on a stated
date; the rest is still a proposal"*. Open question 1 decided; open question 7 struck as stale, since
it asks whether capture lands before or after Phase 3 and Phase 3 shipped as `cc65aed`.

**The task as published named three edits and took five.** `../../README.md`: *"When you record a
finding, sweep the other documents for claims it makes stale. That sweep is expected, not optional —
it is half of what filing a finding means."* So the sweep is part of the task rather than a new one,
and no task letter was spent.

| Swept | Was |
|---|---|
| `EPD-000`'s index row | `proposal`, waiting on *"a decision on the fine-tuning goal"* |
| `CLAUDE.md`'s EPD table | same, and `CLAUDE.md` is auto-loaded — a stale row there is the "acts confidently and wrongly" case its own admission test is about |
| `../../backlog.md`'s "Decisions waiting on a person" row | **struck, not deleted.** What remains of `EPD-003` is its gate, which is *work*, and that section's premise is *"None of these is blocked on work"* |

**Two findings were marked in place inside `EPD-003` rather than only in this phase folder** — the
gate training on its test set, and `calls.csv` being unable to serve as the join table. A finding
recorded only next to the phase that made it leaves the wrong document still saying the wrong thing to
whoever opens it next.

## Task 4 — the in-flight branch, and three stale claims

`../../status.md` gains the branch row. Two things worth recording about the edit:

**"Where we stopped" was already over its own limit.** The section's rule is that it gets its own file
past ~30 lines; it was at ~44 before this task. So Phase 8's and Phase 7's closed narrative was cut to
two sentences — their permanent records are their phase notes, and `status.md` is state. Adding Phase 9
on top without cutting would have pushed it to ~60.

**The task also took `../implementation-plan.md`,** which was stale in three places the moment Task 3
landed: `EPD-003` described as *"still a proposal"*; step 3 of the opening playbook described as *"may
already be discharged"*, which Finding 1 disproves; and Phase 9 marked *(outline)* when its plan is now
published in full. Corrected **in place with dated notes**, not rewritten — that file is a live
milestone plan rather than a frozen phase note, and Phase 8's Task 17a set the precedent for correcting
it in place.

**The central-claim blank survives the decision, and this is worth being explicit about.** `EPD-003`
being partly accepted might look like grounds to name the milestone's claim now. It is not: the half
that was decided is not the half a claim would rest on. The storage question is what the milestone is
*about*, and it is open until the gate runs.

---

## Task 5 — the ignore, and a rotation risk that was not in the plan

**Verify, not add.** Both checks pass, and neither needed a new rule.

| Check | Result |
|---|---|
| Every path Task 6 writes — `requests/`, `responses/`, `*.dict`, `manifest.csv` | all covered by **`.gitignore:228`**, a bare `logs/` |
| `make clean` | `rm -rf .pytest_cache .ruff_cache build dist *.egg-info` plus a `find` over `src tests` only. **Never touches `logs/`** |

**The `make clean` check was run against the Makefile target, not against `CLAUDE.md`'s claim that it
leaves `logs/` alone.** Both agree — but a phase whose whole first finding is that a document
overstated what was already done should not verify one document with another.

**The rule is in this repository's own tracked `.gitignore`,** not in a global exclude. That matters
here for the reason Phase 8 recorded when it added `.claude/settings.local.json`: a convention resting
on a store that exists only outside the repository protects this machine and nothing else. The corpus
is the most sensitive thing this project will ever write, so the rule that keeps it out has to travel
with the repository.

### The baseline, for Task 7's cross-check

Task 7 verifies captured bodies against **the same run's** `calls.csv` rows, which means knowing where
the existing rows stop.

| | |
|---|---|
| `logs/calls.csv` before the capture | **177 lines** — 176 rows and a header — **29,831 bytes** |
| Last existing row | `2026-08-07T14:15:14.218+00:00` |
| Rotated backups present | **none.** `calls.csv.1` does not exist; this file has never rolled over |

**A risk the plan did not name, now retired.** `stats.max_bytes` is 5 MiB and the file is at 29,831
bytes, leaving room for roughly **36,900** more rows at the ~141 bytes/row the frozen session measures.
A capture of a few hundred rows cannot trigger a rollover — so Task 7's cross-check cannot be
confounded by rows moving into `calls.csv.1` mid-capture, and the header re-emission that would follow
cannot land in the middle of the slice being read.

Had this gone the other way it would have been found *after* the capture, while trying to explain a
row count that did not match. It cost one `wc`.

**One discipline carried into Group B:** Tasks 6–10 stage with **explicit paths**, not `git add -A`.
The ignore makes `-A` safe and it is verified above — but "verified safe" and "not relied upon" are
different, and the cost of being wrong once is a committed body.

---

## Task 6 — the capture. **Partly failed: Anthropic was overloaded**

Run 2026-08-17, ~13:35–13:50 UTC. **The capture is short of its own floor and is missing a dimension
the plan called load-bearing.** What happened, in order, before what it produced.

### The patch, verbatim

Applied to the working tree only, **never committed**, and removed with `git restore src/`. 48 lines
added to one file.

```diff
@@ -45,6 +45,33 @@ from .stats import StatsWriter
 logger = logging.getLogger(__name__)
+# PHASE 9 CAPTURE — THROWAWAY. NOT TO BE COMMITTED. Removed by `git restore`.
+import itertools  # noqa: E402
+import pathlib  # noqa: E402
+import threading  # noqa: E402
+
+_CAP_DIR = pathlib.Path(__file__).resolve().parents[2] / "logs" / "corpus-gate"
+_CAP_SEQ = itertools.count(1)
+_CAP_LOCK = threading.Lock()
+(_CAP_DIR / "requests").mkdir(parents=True, exist_ok=True)
+(_CAP_DIR / "responses").mkdir(parents=True, exist_ok=True)
+
+def _cap_write(kind: str, seq: int, data: bytes) -> int:
+    """Write one body verbatim. Returns what actually landed on disk, not what we were handed."""
+    (_CAP_DIR / kind / f"{seq:05d}.bin").write_bytes(data)
+    return len(data)
+
+def _cap_manifest(row: str) -> None:
+    with _CAP_LOCK, (_CAP_DIR / "manifest.csv").open("a", encoding="utf-8") as handle:
+        handle.write(row + "\n")

@@ -140,6 +167,13 @@ class Proxy:   # in begin(), after call.request_bytes = len(body)
+        try:
+            call._cap_seq = next(_CAP_SEQ)
+            call._cap_req = _cap_write("requests", call._cap_seq, body)
+        except Exception as exc:  # noqa: BLE001 — capture must never break a call
+            logger.warning("capture failed: %s", exc)
+            call._cap_seq, call._cap_req = 0, -1

@@ -241,10 +275,12 @@ class Proxy:   # in watch()
+        cap_buf: list[bytes] = []
             async for chunk in reply.aiter_raw():
                 call.saw_bytes(len(chunk))
                 scanner.feed(chunk)
+                cap_buf.append(chunk)
                 yield chunk

@@ -266,6 +302,18 @@ class Proxy:   # in watch()'s finally, before scanner.finish()
+            # The manifest records what the *capture* saw; calls.csv records what the *router*
+            # relayed. Task 7 compares them, so they must not share a source.
+            try:
+                seq = getattr(call, "_cap_seq", 0)
+                res_n = _cap_write("responses", seq, b"".join(cap_buf))
+                _cap_manifest(
+                    f"{seq},{call.session_id},{call.agent_id},{call.path},"
+                    f"{getattr(call, '_cap_req', -1)},{res_n}"
+                )
+            except Exception as exc:  # noqa: BLE001 — capture must never break a call
+                logger.warning("capture failed: %s", exc)
```

**Both call sites are wrapped**, because *"telemetry must never break a call"* is a project
non-negotiable and a body write is telemetry-shaped. **The manifest deliberately does not read
`call.request_bytes`** — it records the byte count `_cap_write` returned from disk, so Task 7's
cross-check compares two independently produced numbers rather than one number against itself.

**Verified before pointing real traffic at it:** `make test` → **158 passed** with the patch applied.
That run also produced its own finding, below. Its capture output was deleted before the real run.

### What was driven

| | |
|---|---|
| Session A | this repository — 12 named files one at a time, then a `general-purpose` subagent. `--allowedTools "Read Glob Task"` |
| Session B | `/Users/ilirium/Projects/code-2026/pytorch_mps_deform_conv2d` — 5 named files, then every `tests/*.py`. `--allowedTools "Read Glob"` |

Both headless, concurrent, `ANTHROPIC_BASE_URL=http://127.0.0.1:8787`. **Neither session had a write
tool**, so neither project could be modified.

**Project 2 has no `CLAUDE.md`.** So the two sessions differ by working directory and by the
*presence* of project instructions, not by two different instruction files. Arguably a sharper
contrast than planned — session A carries this repository's ~200-line file and session B carries
none — but it is **a different test from the one described to the owner**, recorded as such rather
than relabelled.

### The failure: Anthropic returned 529 for a third of the run

| Outcome | Rows |
|---|---|
| `ok` | 20 |
| `http_error,529` — `overloaded_error: Overloaded` | 11 |
| `client_disconnect` | 2 |
| `stream_error,overloaded_error` | 1 |

**Session B completed** — all 14 files read. **Session A did not**: it aborted on a 529 before
reaching the `Task` tool, so **no subagent traffic exists in this corpus and `agent_id` is empty on
every row.** Finding 5's specific test — that concurrency dilutes a dictionary by adding preamble
families — is the reason the subagent was in the plan at all, and it did not run.

A one-call probe sent afterwards to test recovery produced six more consecutive 529s with Claude Code
backing off 6 s → 12 s → 19 s → 35 s → 37 s. **Anthropic was still degraded when the phase stopped**,
so re-capturing was not possible.

**This is a backend outage, not an instrument failure**, and Task 7's cross-check below is what
establishes the difference. The router behaved correctly throughout: it recorded every 529 with the
backend's own symbolic type, which is exactly the behaviour `../../backlog.md` predicts under "Not on
this list" for rate-limit errors — *"the next 429 through the router writes `rate_limit_error: Error`
into the CSV by itself"*. Same mechanism, different code. **Observed rather than reconstructed.**

### Two findings that came free

**The capture misses the calls `EPD-003` says are most interesting.** The verification test run
produced **158 request captures but only 149 responses.** The 9-way gap is the paths that return
before `watch` ever runs — the no-model 400, transport errors, and disconnect-during-upload. So a body
store built at this hook point **silently drops exactly the rows `EPD-003` calls *"the interesting
ones, not the broken ones"***. Phase 10 must capture at the point of failure, not only in the
streaming path.

**The sequence counter restarts with the process.** `_CAP_SEQ` begins at 1 on every router start, so a
second capture run into the same directory would **overwrite `00001.bin` onward**. The current corpus
survived only because there was one run. **Any top-up must move the existing capture aside first**, or
seed the counter past the highest existing file. Noted before it costs anything.

## Task 7 — verifying the instrument. **Passes. The corpus is one body short of its floor**

| | |
|---|---|
| Captured | **49 requests, 49 responses** |
| Request bytes on disk | **4,757,752** |
| Response bytes on disk | **91,779** |
| Request size min / median / max | 0 / **103,935** / 185,209 |
| Distinct session ids | 4 |
| **Rows carrying `agent_id`** | **0** |
| Paths | `/v1/messages` × 46, `/api/hello` × 3 |

**The cross-check passes exactly.** The multiset of request lengths recorded by the capture manifest
is **identical** to the multiset of `request_bytes` in the 49 new `calls.csv` rows. Two independently
written records agree, so nothing was truncated, dropped or double-counted. **The instrument is
sound; the corpus is merely short.**

**The `/api/hello` rows are the catch-all route firing** — `path` doing precisely the job
`../../reference/observability.md` claims for it, *"turns a standing 'other endpoints' worry into a
list of facts"*. Three requests to an endpoint nobody enumerated, visible for free.

### The preamble comparison — and a difference that matters to the gate

Largest captured body against the frozen `../../captures/log-the-whole-request.txt` of 2026-07-28:

| | Frozen, interactive | Captured, headless |
|---|---|---|
| Top-level keys | 10 | **identical 10** |
| `system` blocks | 3 | 3 |
| `system` bytes | 28,303 | **10,800** |
| `tools` count / bytes | 27 / 82,725 | 30 / **71,811** |
| **Static preamble total** | **111,028** | **82,611** |
| `messages` | 2 | **35** |

**The key set is identical**, so a headless session produces the same request *shape* — the plan
recorded that as **assumed** and it is now measured.

**But the static preamble is ~28 KB smaller headless than interactive**, almost all of it a shorter
system prompt. Two consequences, and the second is a caveat that must ride on any number this corpus
produces:

- **Finding 3 is confirmed for interactive use.** The frozen interactive preamble is **111,028 bytes**
  against `--maxdict`'s **112,640** default — within 1.5% of the cap, and independently confirming
  `stats.py`'s measured "~110 KB".
- **This corpus makes the dictionary's job easier than reality.** At 82.6 KB the headless preamble sits
  comfortably under the default cap, so a dictionary trained here has room the interactive case would
  not give it. **A favourable gate result from this corpus would not transfer to interactive use
  without re-checking.**

`messages` grew from 2 to 35, so the O(N²) re-send this whole gate is about is present in the corpus.

**Median request 103,935 bytes against `EPD-003`'s measured 20.5 KB.** Five times larger, because these
sessions read source files one at a time and each read stays in context. Not a contradiction of
`EPD-003` — a different workload, and it is the *shape* of the sessions this capture was told to drive.

### The floor is not met

`plan.md` requires **≥50 request bodies or capture again**. There are **49**, and more importantly
**0 with `agent_id`**. Capturing again is blocked on Anthropic. **Stopped here rather than proceeding
to Group C**, because the threshold exists to stop a weak number being computed and then quoted.

---

## Task 6, runs 2 and 3 — the capture completed on a third attempt

**Run 1's shortfall was repaired by two further runs**, and the two structural fixes made between them
are worth as much as the bodies.

**The counter hazard was removed structurally, not by remembering it.** Run 1's capture directory was
renamed to `run-01-anthropic/` and the patch gained
`os.environ.get("CAPTURE_RUN", "run-unlabelled")` in its path. **The default proved itself
immediately**: the verification `make test` wrote into `run-unlabelled/`, exactly where a mislabelled
run belongs, leaving run 1 untouched. A capture that cannot say which run it came from is now
impossible rather than merely unlikely. The manifest also gained a `model` column, so the corpus splits
by backend without a join.

### Run 2 — LM Studio. **Underdelivered, for a reason worth keeping**

`lfm2.5-8b-a1b-mlx`, loaded by the owner at a **40,000-token** context window, `parallel: 4`.
**Three bodies, no subagent.**

**The local model would not drive the tools.** Asked to read two files one at a time and then spawn a
subagent, it produced fluent, generic descriptions of `routing.py` and `cli.py` — *"implements the core
message routing and dispatching logic"* — and never reached the `Task` tool. Two `/v1/messages` calls
in total. This is not a router finding and not an LM Studio finding; it is a **capability** finding
about an 8B model, and it is the reason the local path could not supply the dimension run 1 lacked.

**Two observations from those three calls are worth more than the bodies.**

**`EPD-002`'s case is weaker again, and now measured rather than documented.** Claude Code printed, on
being handed an unrecognised model:

> *"`lfm2.5-8b-a1b-mlx` is not a model this version of Claude Code recognizes, so auto-compact will keep
> this session within 200k tokens (the context window it assumes)… set `CLAUDE_CODE_MAX_CONTEXT_TOKENS`
> to its real window"*

That is precisely the mechanism `EPD-002` is organised around — the assumed 200k window — but **stated
out loud rather than silently**, and carrying a **supported fix** (`CLAUDE_CODE_MAX_CONTEXT_TOKENS`, a
`modelOverrides` setting, and a `[1m]` suffix). `../../backlog.md` already grades that EPD as *"a
decision, on a weakened case"*. This is **observed on this machine**, unlike most of what that document
rests on.

**A local response can be larger than its request**, which `EPD-003`'s volume table does not allow for:

| | Request | Response | TTFB |
|---|---:|---:|---:|
| Run 2's third call | 99,970 | **135,894** | 52,230 ms |

`EPD-003` measures *"requests are 93% of the volume; median response 0.3 KB"* — true of the session it
measured, where the local replies were short. **A verbose local model inverts the ratio.** The O(N²)
argument is untouched, since that concerns re-sent history — but **93% is a property of the models in
that session, not of the corpus**, and a response-heavy local model changes the storage mix. Run 2
produced *more* response bytes (137,917) than request bytes (102,507); both Anthropic runs produced the
opposite by a factor of twenty.

### Run 3 — Anthropic, after it recovered. **The missing dimension**

Anthropic's health was re-tested **outside the router** — `claude -p` with no `ANTHROPIC_BASE_URL`, so
the probe could not pollute the corpus — and answered instantly.

**21 bodies, every one `ok`, 10 of them carrying an `agent_id` across 2 distinct subagents.**

**The prompt was reordered rather than repeated.** Run 1 died before reaching the `Task` tool because
the subagent came after twelve file reads. Run 3 asked for five reads and then two subagents, so the
scarce part came first. The failure was in the ordering, not in the instruction.

### The corpus, as it now stands

| Run | Requests | Request bytes | Response bytes | Agent rows | Sessions |
|---|---:|---:|---:|---:|---:|
| `run-01-anthropic` | 49 | 4,757,752 | 91,779 | 0 | 3 |
| `run-02-lmstudio` | 3 | 102,507 | 137,917 | 0 | 1 |
| `run-03-anthropic` | 21 | 2,102,371 | 243,854 | **10** | 1 |
| **total** | **73** | **6,962,630** | | **10** | **5** |

**68 bodies exceed 1 KB** — min 2,277, median 103,935, max 185,209. **The floor is met with margin,
and the subagent dimension exists.** Group C may proceed.

**Three biases ride on any number this corpus produces, and all three flatter the dictionary:**

1. **The headless preamble is ~28 KB smaller than the interactive one** (82,611 against 111,028), so the
   dictionary has room the real case would not give it.
2. **LM Studio is represented by 3 bodies of 73.** The corpus is effectively Anthropic-only, so it does
   not test a genuinely mixed-backend store.
3. **Run 3's session is short.** Less session-local growth means a larger share of each body is static
   material — which is exactly the part a dictionary *can* capture.

Stated here so the gate's verdict is read against them rather than in spite of them.

---

## Tasks 8–10 — the gate. **It passes, and EPD-003's own anchors reproduce**

`evidence/gate.py`, output frozen verbatim in `evidence/results.txt`. Held-out slice: run-03's whole
session, 20 bodies, 2,102,371 bytes. Training set: run-01's three sessions, 48 bodies. **Split by
session, never shuffled** — within a session an earlier body is nearly a prefix of a later one, so a
shuffled split would leak the answer.

### The bracket

| On the held-out slice | Bytes | Ratio |
|---|---:|---:|
| raw | 2,102,371 | 1.00x |
| **per-file, no dictionary** | 673,087 | **3.12x** |
| **one long-window stream** | 70,282 | **29.91x** |

**`EPD-003`'s synthetic figures reproduce on real traffic**, which was not guaranteed — that document
grew twenty bodies by appending random dictionary words and flagged the tail as synthetic. It predicted
3.1x and 28.6–31.3x. Measured: **3.12x and 29.91x.** The synthetic construction was sound.

### The answer to the load-bearing hypothesis

| `--maxdict` | self-trained | held-out | gap closed |
|---:|---:|---:|---:|
| 112,640 *(default)* | 12.08x | **10.94x** | 79.8% |
| 262,144 | 21.76x | **12.03x** | 82.7% |
| 524,288 | 16.44x | **12.10x** | 82.8% |
| 1,048,576 | 16.44x | **12.10x** | 82.8% |

**Held-out, a dictionary reaches 12.10x against 3.12x without one.** It closes **82.8%** of the byte
gap, leaving the per-file store at **2.47x** the size of a stream — not the **9.6x** it would be
unaided.

### Verdict: **per-call files survive. The sketch ships as written**

`EPD-003` set the test: *"If the dictionary lands near the stream figure, the sketch above works as
written. If it lands near the 3x per-file figure, then per-call files are the wrong unit."*

**12.10x is not near 3.12x** — it is four times better, and it closes five-sixths of the distance to
the stream. The residual is 2.47x, and that is the price of everything per-file buys, which `EPD-003`
itself enumerates as the reason per-session is *"far worse on everything else"*: random access, partial
writes, a process that stops mid-session, content addressing, and date-partitioned pruning by `rm -rf`.

**On the projection that motivated the question:** ~3 GB a year naive becomes ~100 MB streamed or
~250 MB per-file-with-dictionary. `EPD-003`'s own criterion was that *"neither figure justifies special
storage infrastructure"* — and both of these are still the low hundreds of megabytes it was talking
about. **The 2.47x does not change the conclusion the number was for.**

### Three things the sweep found that were not the question

**Finding 3 is answered, and it was a real effect but a small one.** The 112,640 default **does** bind
— the trained dictionary comes out at exactly 112,640 bytes, capped. Lifting it to 256 KB buys 10%
(10.94x → 12.03x) and then saturates: at 512 KB and 1 MB the dictionary settles at ~178 KB of its own
accord and the figures stop moving. So the concern that a single run at the default might report a
false negative was justified — but it would have understated the answer by a tenth, not reversed it.

**`zstd --train` is unstable at this sample count, and says so.** The self-trained column is
**non-monotonic**: 12.08x → 21.76x → 16.44x as the cap rises, and the dictionary *sizes* wobble the same
way (112,640 → 212,215 → 197,926). More budget producing a worse dictionary is not a property of
compression; it is the cover algorithm sampling differently on 68 inputs. **The held-out column is
stable** (10.94 → 12.03 → 12.10 → 12.10), which is the one being relied on — but this is direct evidence
that a Phase 10 retraining policy must **measure the new dictionary before adopting it** rather than
assume a retrain is an improvement.

**Finding 5 measured: a second preamble family costs about 20%.** With one dictionary trained on
run-01 — which contains **zero** subagent bodies — the held-out slice splits:

| | Bodies | Ratio |
|---|---:|---:|
| main conversation | 10 | **13.39x** |
| subagent | 10 | **10.75x** |

The subagent's preamble was never seen in training and still compresses at 10.75x, so a dictionary
**generalises across preamble families rather than collapsing** — at a measurable ~20% penalty. This is
the concern that made parallel sessions and subagents worth capturing, and the answer is that dilution
is real, bounded, and does not threaten the design.

### What this verdict is *not* good for

**All three biases recorded before the run flatter the dictionary**, and none is repaired by the
result: the headless preamble is ~28 KB smaller than interactive, LM Studio is 3 bodies of 73, and the
sessions are short. **12.10x should be read as an optimistic estimate**, and the honest claim is
directional: a dictionary recovers *most* of the cross-body ratio, not that it recovers 82.8% of it in
every setting. The verdict survives the biases because the margin is large — 12.10x against a 3.12x
failure threshold — not because the biases are small.

---

## Superseded: the pause after run 1

*Kept rather than rewritten. This is what was true after run 1, and the runs above are what resolved
it — the record of a threshold **stopping** work is worth more than a tidy note that never mentions
it. Only the "blocked" heading above it is corrected.*

**Tasks 1–7 were stopped before Group C**, because the gate's input did not meet the threshold the plan
set for it.

**The machine is left clean.** Router stopped, `src/` restored — `git diff main -- src/` is empty —
working tree clean, `make test` **158 passed**. Nothing captured is committed, and nothing captured is
committable.

| Blocker | State |
|---|---|
| **49 request bodies against a floor of 50** | one short |
| **No subagent traffic at all** | Finding 5's dimension is untested |
| **Anthropic returning 529** | re-capture impossible at the time of writing |

**The corpus is preserved** in `logs/corpus-gate/`, gitignored, so a top-up is possible when the
backend recovers — **provided the sequence-counter hazard above is handled first.**

**A number was not computed from the short corpus.** The threshold exists to stop a weak figure being
produced and then quoted as the gate's answer, and this repository has the specific failure it is
guarding against: `../../reference/lessons.md` records a number that was *"correct and unusable
because its slice was missing"*. A dictionary ratio from a corpus with no subagent traffic and a
headless-shortened preamble would be exactly that.

Task 6 needs the owner's go-ahead in its own right: it patches `proxy.py`, runs the router, and makes
real API calls. `CLAUDE.md`'s working agreement — *"Ask before touching the machine … consent for one
is not consent for the next"* — is why that is a separate ask rather than covered by the go-ahead that
opened this branch.

### Verified by, Group A — run 2026-08-17, after Task 4's commit

| Check | Result |
|---|---|
| `make test` | **158 passed**, 1 warning, 0.68 s |
| `procedures/link-check.py` | **68 files, 68 broken, 2 roundabout** — the broken count **unchanged** from the fork |
| `git diff main --stat -- src/` | **empty** — the `docs/` prefix still holds |
| `git status --porcelain` | clean; no captured body or dictionary exists yet to leak |

**The link-checker's file count rose 66 → 68 while its broken count did not move**, and that is
checked rather than assumed: `link-check.py` reports **zero** hits from `phase-9-corpus-gate/`, and the
only `epd/` hits are the two that predate this branch. So the two new documents cite nothing that does
not exist, and nothing edited in Tasks 3–4 broke a path.

**That differs from Phase 8, whose plan contributed 23 forward citations** to files it intended to
create — a false-positive class `../../backlog.md` records as recurring. This plan has none, because
Group B's and C's outputs live under `logs/`, which is gitignored and therefore never cited as a
repository path. Not a virtue of this plan; a property of where its outputs go.
