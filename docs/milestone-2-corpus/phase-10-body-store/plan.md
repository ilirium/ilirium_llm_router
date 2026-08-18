# Phase 10 — the body store: plan

**Written 2026-08-18 on `feat/phase-10-body-store`, forked from `main` at `d885b2f`. Not yet
executed — no task below has been started.**

**Twenty tasks in five groups.** Group A opens the phase and records what the opening interview
decided. Group B builds the store. Group C trains the first dictionary and writes the instrument that
keeps training honest. Group D moves the telemetry files. Group E harvests, closes out `EPD-003`'s
remaining open questions, and merges.

**This phase's first act was its re-derivation, and it ran before this file was published** — the same
shape Phase 9 used, for the same reason: findings that land during the interview should shape the task
list rather than correct it afterwards. **The nine findings are in `notes.md`**, beside this file, and
four of them changed the design below.

*Revised 2026-08-18, after a second interview on the write path — the owner raised performance under
concurrent harnesses and refused the unverified GIL claim this file rested on. **Corrected in place
with dated notes rather than rewritten**, per the precedent Phase 8's Task 17a set for a live plan.
What changed: Group B0 is new, Tasks 6 and 7 are widened, and four decisions were added above. **No
task was renumbered** — `../../README.md`: an insertion is a letter.*

---

## Why this is a `feat/` branch

`../../method/IDM-001-git-branching.md` — the prefix answers *which kind of work*, and `phase-N-` is
orthogonal to it. **`feat/` is product work: anything that changes `src/`.**

**Phase 9 was `docs/` because no `src/` change survived it** — its capture patched `proxy.py` and
restored it, and `git diff main -- src/` was empty at the merge. **This phase is the opposite case.**
`src/ilirium_llm_router/` gains a module and keeps it; `config.py`, `proxy.py` and `app.py` all change
and stay changed; `pyproject.toml` gains a dependency. Nothing here is restored at the end.

The folder takes the branch's slug, per the same document.

---

## What is settled, and by whom

Decided by the owner on 2026-08-18, in the interview that opened this branch. **The first two close
two of `EPD-003`'s four remaining open questions**; the other two are this phase's own.

| | Decision |
|---|---|
| **Capture default** — `EPD-003` open question 4 | **Opt-in, one switch, off by default.** `corpus.enabled: false`. The CSV is always on because it is cheap and holds nothing sensitive, and **neither is true here** — bodies hold source code, file contents and anything typed. **The named cost:** the durable day-partitioned index exists only when the corpus does, so `calls.csv`'s expiry stays unfixed on a machine that never turns the corpus on. A two-switch shape — index always-on, bodies opt-in — was offered and declined, on one config knob rather than two |
| **Headers** — `EPD-003` open question 6, *"the single most sensitive thing the router touches"* | **No headers, ever.** The store takes bodies only. What analysis wants from headers — `session_id` and `agent_id` — is **already two columns of the index**, copied by the recorder from a dictionary lookup. This keeps the corpus merely sensitive rather than a secret store, and keeps the write path a byte queue with no filtering logic in it. An allowlist, and a redact-the-credential variant, were both offered and declined |
| **The zstd binding** | **Add `zstandard` to dependencies.** Finding 5 in `notes.md`: Python 3.13 has no `compression.zstd` and nothing in `EPD-003`, the sketch or the gate noticed. Shelling out to the `zstd` CLI per body, and bumping to Python 3.14 for its stdlib module, were both offered and declined |
| **Scope** | **Build, test, and train from the surviving corpus.** No live driven session, no new API calls. `logs/corpus-gate/` still holds Phase 9's three runs and eight dictionaries — verified present on 2026-08-18 — so a real dictionary is available without capturing anything. **What this costs is named below**, under "What this phase does not settle" |
| **The executor** | **One worker thread, chosen from a measurement rather than from this table.** The prototype stays simple; the benchmark below says whether it is right. A `corpus.workers` knob is added **only if** Task 3c's numbers show the GIL is released *and* that more than one worker helps — configuration this project does not need is configuration it does not get |
| **Diagnosability** | **The severity question is answered from data the store already writes.** The owner's requirement, 2026-08-18: keep the first prototype simple, but instrument it so that *how bad did this get under real load* is answerable months later without having been watching. Three index columns and two log lines; see "The write path, concretely" |
| **Benchmark before code** | **Group B0 runs before any store code is written**, so Group B is written against numbers instead of against published throughput figures for somebody else's machine |
| **The size ceiling** | **Kept, and configurable — it already was.** `EPD-003`'s question was answered *(Q4)*: it protects against **one enormous body** during the call, which the queue bound cannot reach because that protects against **many ordinary bodies afterwards**. Neither can be disabled |
| **One tool, not two** | **`zstandard` for the router and the trainer alike** *(Q5)*. This plan first kept the `zstd` binary for the trainer, for comparability with Phase 9's figures; the owner asked why two tools and **simplicity wins**. Task 3c checks that library training and `zstd --train` agree rather than assuming it |
| **Dictionaries** | **Plain copies, and each day folder is self-contained** *(Q7)* — *any metadata, any dicts, any archives* belong to the day. **This restores the sketch**: the root `dicts/` and the hard links were this plan's addition, and declining the links left the root folder with no job |
| **Compression level** | **Configurable, with a default measured by Task 3c** *(Q10)* |
| **Diagnosing loss generally** | **One counter pair, and nothing else.** Calls arrived against rows written, in the same periodic summary as the corpus totals — which makes `record()`'s blind spot visible without changing a column of `calls.csv`. A metrics endpoint and a sequence column were both considered and **reserved to `../../backlog.md`** |
| **Several router instances** | **Considered and deferred, recorded in `../../backlog.md`.** Its session-distinguishing half is already solved and measured; its throughput half has one concrete blocker that a reverse proxy does not touch — see "What this phase does not settle" |

### And two questions the owner did not have to answer

Both are `EPD-003` open questions, and both are answered here by argument rather than by preference.
**They are still open questions until Task 16 records the answers in `EPD-003` itself.**

**Question 3 — what is captured by default: everything.** No path-exclusion knob. `EPD-003`'s worry
was that the 32 `count_tokens` non-answers are *"pure noise"*, but **content addressing collapses
identical bodies to one file for free** — and those 32 identical 85-byte errors are the exact case it
measured. Excluding by path would also exclude the catch-all's genuinely unexpected traffic, which is
what `../../reference/observability.md` says the `path` column exists to surface. A knob can be added
the day it hurts; adding one now is configuration nobody asked for, against a project non-negotiable
that configuration stays simple.

**Question 5 — retention: nothing is deleted automatically.** UTC date folders make
`rm -rf logs/corpus/2026-08-18` the whole tool, and ~250 MB a year at an hour a day does not justify a
policy engine. **Dictionaries are exempt permanently** — `../../reference/design-decisions.md` records
that losing one makes every blob referencing it unreadable, and they cost ~110–200 KB each. If this
needs revisiting it will be against a real growth number rather than against `llm.log` having grown a
prune command.

---

## The question this phase closes

**What does the router store, and where** — and, of the milestone's three failure modes, **it tests
two.**

`../implementation-plan.md` names the claim: *the router can archive every body it carries — as
opaque, content-addressed, per-call files compressed against a shared dictionary — without parsing a
payload, without slowing a call, and without special storage infrastructure.* Phase 9 discharged the
third by measurement. **Failure mode 2 — archiving cannot stay opaque — is discharged here by
construction**, and Task 10 is what makes that a test rather than an assertion. **Failure mode 3 —
archiving slows a call — is not discharged by this phase**, and that is stated rather than implied;
see below.

---

## The shape

```
logs/
  telemetry/                      calls.csv and router.log — moved in this phase, Task 13
  corpus/
    2026-08-18/                   UTC-derived, never local. SELF-CONTAINED
      index.csv                   25 columns: calls.csv's 20, in order, then two refs and three timings
      manifest                    schema version, router version, dictIDs referenced
      dicts/                      plain copies of every dictionary this day used
        req-2026-08-18T104500Z.dict
      incoming/                   staging for atomic rename
      requests/3f/3f9c….zst
      responses/b2/b20e….zst
```

**A day folder is self-contained and nothing lives above it.** Owner's rule, 2026-08-18: *any
metadata, any dicts, any archives* belong to the day. `tar` one folder, or `rm -rf` one folder, and
neither operation can reach anything outside it.

**That makes the never-delete-a-dictionary rule automatic rather than remembered.**
`../../reference/design-decisions.md` warns that losing a dictionary makes every blob referencing it
unreadable, and made dictionaries append-only forever to prevent it. **With a copy in every day that
uses it, a day can be deleted whole and no surviving day is affected** — the invariant is enforced by
the layout instead of by a rule somebody has to know.

**Carried unchanged from `../phase-9-corpus-gate/plan.md`'s fenced sketch**, which was written before
the gate ran and is input rather than specification: hash the **plaintext** and not the compressed
bytes; frames are self-describing, so `zstd`'s embedded dictID is what binds a blob to its dictionary;
blobs are immutable and never recompressed; `write → fsync → rename` out of `incoming/`; UTC-derived
date folders, because both existing files timestamp in UTC and a local-time folder name would
contradict the `timestamp` column of the rows inside it twice a day; **full** telemetry per day rather
than a subset, with the header row in every day file; no session or agent subfolder layer; no
per-session dictionaries; and `calls.csv` **is not changed** — not its columns, not its rotation.

### What changed from the sketch

Each of these is a finding in `notes.md`, numbered there.

| Changed | From | To |
|---|---|---|
| **Queue bound** *(1)* | *"a bounded off-thread queue"*, which reads as a `maxsize` in items | **Bounded in bytes.** At a median request of 103,935 bytes, a 1,000-item queue is 200 MB of RSS. The item count falls out of the byte bound |
| **Hook point** *(2)* | implied `watch()`, which Phase 9 measured missing 9 of 158 calls | **`Proxy.record()`** — four call sites, and every path reaches one. The same funnel that writes the CSV row |
| **Recording a drop** *(3)* | 22 columns with no way to say a body was dropped | **A ref cell holds a 64-char hex digest, or one of `dropped` / `too_large` / `absent` / `error`.** A reason word can never be mistaken for a digest, so this needs no new column. *`error` added 2026-08-18 — a compression or write failure in the worker must land in the cell too, or the one case where the store itself broke is the one case the index cannot describe* |
| **Over the cap** *(4)* | *"the store must be able to hold a truncated body and say that it is truncated"* | **Drop, do not store a prefix.** A prefix labelled as a whole body is worse than a hole. This splits cap-truncation from the case `EPD-003` actually meant — a stream that broke, where the bytes that arrived are all there is and `error_status` already says so. The sketch's *"truncation needs no new column"* survives intact, for the reason it gave |
| **Dictionary placement** *(5)* | copies into each date folder, ~80 MB/year, with *"plain copies against APFS clones"* left open pending the `--maxdict` result | **Plain copies, and the sketch was right.** *Superseded 2026-08-18, twice.* This row first proposed `os.link()` into a **root** `logs/corpus/dicts/`, to get portability at zero bytes. **The owner declined it and restored the sketch**: plain copies, no root folder, each day self-contained. The root folder existed only to be the link target, so declining the links removed its whole job — **it was this plan's addition, not the sketch's.** The cost is the ~40–80 MB/year the sketch already named and the owner accepted, and what it buys is one fewer concept and an invariant the layout enforces |
| **Compression level** | not considered — every figure was measured at level 19 | **Configurable, with a default measured by Task 3c.** Level 19 is an offline setting; the write path is a different question and nobody had asked it |
| **One compression tool** | not considered | **`zstandard` everywhere**, router and trainer alike. This plan first proposed keeping the `zstd` binary for the trainer, for comparability with Phase 9's numbers; **the owner asked why two tools, and simplicity wins.** Task 3c checks that library training and `zstd --train` agree rather than assuming it |
| **Dedup scope** *(6)* | implied by the tree, never stated | **Per day, and that is deliberate.** Cross-day dedup would make `rm -rf <a-day>` orphan another day's refs, which is the whole retention answer |
| **Per-direction dictionaries** | *"Task 9 measures whether the split pays"* | **Supported structurally, but only a request dictionary is trained.** Frames name their own dictID, so more than one is free — but the gate measured *request* bodies, and its own `evidence/README.md` says it answers nothing about responses. Responses write undicted until somebody measures it |

### One design consequence worth stating on its own

**A full queue still records the hole.** The item handed to the worker is
`(CallRecord, request_bytes, response_bytes)`. When the bodies would push the queue past its byte
bound, **the record is enqueued anyway with both ref cells set to `dropped`** — a record-only item is a
few hundred bytes and is never refused.

So `EPD-003`'s *"drop the body and record that it was dropped — a corpus with a known hole is fine, a
stalled request is not"* becomes literally true rather than approximately: **the hole is a row, not an
absence.**

**Everything on the request path is one append and one counter increment.** Hashing, compression,
`fsync`, rename and the index row all happen in the worker thread. The sketch never said where hashing
lived, and sha256 over a 200 KB body on the event loop is small but not free.

### The config block

```yaml
corpus:
  enabled: false              # opt-in. Nothing is written until this is true
  dir: logs/corpus            # relative paths resolve against the config file's directory
  level: 9                    # zstd level. The default is whatever Task 3c measures
  max_body_bytes: 1048576     # one body bigger than this is not stored: `too_large`
  queue_max_bytes: 67108864   # total bytes waiting to be written; over it: `dropped`
```

### Two limits, because they are checked at two different moments

*Rewritten 2026-08-18. An earlier version named what each limit protects and not **when**, and the
timing is the entire reason both exist.*

**Start from what the router holds today, without any corpus.**

| | Held whole in memory today? |
|---|---|
| The **request** body | **Yes, always.** `proxy.py:133` is `body = await request.body()` — the router reads the whole body to relay it. This predates the corpus and is not changed by it |
| The **response** body | **No, never.** `proxy.py:245` streams chunk by chunk and forgets each one after yielding it. The only accumulation anywhere is `observe.py`'s buffered scanner, which stops at **1 MiB** and gives up |

**So the corpus introduces something the router has never done: holding a whole response.** To store
a response, `watch()` has to keep a copy of every chunk. **That is new memory**, and nothing bounds
it unless something is made to.

#### Why the queue bound cannot cover it

The two checks happen at opposite ends of a call:

```
  response starts arriving
    │
    ├─ chunk … chunk … chunk …      ← the copy grows HERE, while the call runs
    │                                  max_body_bytes is checked on every chunk
    │
  call finishes, record() runs
    │
    └─ submit()                     ← queue_max_bytes is checked HERE, once
```

**By the time `submit()` runs, the memory has already been spent.** The queue bound governs bodies
*waiting to be written*; it has no opinion at all about a body still arriving. A single 2 GB reply
would be fully accumulated before the queue ever saw it.

And the reverse is equally true: **the ceiling cannot bound a backlog.** A thousand perfectly ordinary
100 KB bodies are each far under it, and together they are 100 MB in the queue.

| | Bounds | Checked | Cannot help with |
|---|---|---|---|
| **`max_body_bytes`** | peak memory for **one** body | on every chunk, during the call | many bodies at once |
| **`queue_max_bytes`** | total memory for **all waiting** bodies | once, at submit | one body that is huge |

#### What the ceiling does when it fires

The accumulated copy is **discarded and the memory freed**, accumulation stops for the rest of that
response, and the ref cell reads `too_large`. **The relay is untouched** — every byte still streams to
the caller exactly as before, because the copy was never in the path.

#### Why this is not a hypothetical

`app.py`'s catch-all forwards **any** path the router did not anticipate, which is a deliberate design
decision — and Phase 9's capture caught it firing three times on `/api/hello`, an endpoint nobody
here has ever enumerated. A harness calling something like a file-download or batch-results endpoint
through `ANTHROPIC_BASE_URL` would have its reply forwarded by this router, at whatever size that
endpoint returns.

**`observe.py` already faced exactly this and answered it**, in a comment worth quoting because it is
the same argument: *"how much is it worth remembering about a reply nobody enumerated? The catch-all
route forwards any path, so the reply to an unanticipated endpoint could be any size at all, and this
turns 'memory decided by a stranger' into a known ceiling."* **`EPD-003` asks that this reasoning be
reused rather than a new number invented**, and that is what the ceiling is.

**In normal operation it never fires.** The largest request this project has ever seen is 203.2 KB and
the largest response 135,894 bytes; 1 MiB is roughly five times either. **It exists for the endpoint
nobody thought of**, which is the only kind that can be arbitrarily large.

#### The asymmetry, stated because it is real

**For responses the ceiling bounds memory. For requests it does not** — the body is already held whole
by `await request.body()` before the corpus sees it, so refusing to store a 500 MB request saves the
**disk write** and stops that body's lifetime being extended until the response completes, but the
peak was spent before the corpus was consulted.

**Two separate knobs were considered and refused.** One number is simpler, the request case still
gains something real, and a second key would buy a distinction nobody tuning this file would want to
think about.

**Neither limit may be disabled.** An "unlimited" setting reads as *capture everything* and means
*let an unknown endpoint decide how much memory this process uses*.

**There is deliberately no `workers` key.** One worker until Task 3c says otherwise.

---

## The write path, concretely

*Added 2026-08-18 from the second interview. The first version of this plan said "worker thread"
without saying why, which is what the interview was about.*

`src/ilirium_llm_router/proxy.py`'s `record()` runs **on the event loop** and today does two
small things: append a CSV line and emit a log line. A few hundred bytes, microseconds. That is why
it is safe inline. **A body is 100–200 KB and has to be hashed, compressed, `fsync`ed and renamed**,
so `record()` gains a third line that must do none of that work itself:

```
event loop thread                          worker thread
─────────────────                          ─────────────
record(call, scanner)
  ├─ stats.write(row)          unchanged, inline, microseconds
  ├─ logger.info(…)            unchanged
  └─ corpus.submit(row, req, res)
        · lock
        · pending_bytes + len(req) + len(res) > bound?
            yes  enqueue (row, DROPPED, DROPPED)
            no   enqueue (row, req, res); pending_bytes += …
        · unlock, return                       ────────►  queue.get()
                                                            ├─ sha256 the plaintext
    Returns in microseconds. Nothing here                   ├─ compress with the loaded dictionary
    blocks and nothing here raises.                         ├─ incoming/tmp, fsync, rename
                                                            ├─ append the index row
                                                            └─ pending_bytes -= …
```

### What `queue_max_bytes` is actually for

**The worker compresses one body at a time.** If bodies arrive faster than it finishes them, the ones
not yet processed sit in the queue **still holding their bytes in RAM**. With no limit, a burst grows
that until the process is killed — which would take the router down, and *"telemetry must never break
a call"* is the rule that forbids exactly this.

**So there has to be a limit, and what it counts is the whole question.** A limit of *1,000 waiting
bodies* sounds like a bound and is not one: bodies here run from 2 KB to 185 KB, so that is anywhere
between 2 MB and 200 MB of RAM. **Counting bytes bounds the thing that actually hurts**, and lets the
item count vary — 640 median bodies, or 30,000 tiny ones, both fine.

**When it is full the request path does not wait**, because waiting is the one outcome `EPD-003`
rules out. The body is not stored, and the record is enqueued anyway with the ref cells reading
`dropped`, so the hole is a row rather than an absence.

**At the measured load the queue should sit at nought or one item.** One to three calls a second
against a worker that takes tens of milliseconds a body means 64 MiB is never approached. **So the
bound is a tripwire, not a tuning knob** — and any sustained `queue_bytes` above a megabyte is itself
the finding, long before a single body is dropped.

**Nothing crosses a process boundary.** The queue item holds *references* to `bytes` that already
exist in memory — the request body read at `begin()`, and the response copy tee'd in `watch()`.
Enqueueing is a pointer, not a copy.

### Which queue, exactly

*Added 2026-08-18. This plan said "queue" a dozen times without naming one.*

**There is exactly one queue in the whole design.** One item per call, carrying both bodies. Not one
per direction, not one per day, and nothing else in the router uses one — `stats.py` writes its row
synchronously and always has.

| Candidate | Verdict |
|---|---|
| **`asyncio.Queue`** | **Wrong, and it is the tempting mistake.** It is **not thread-safe.** The producer is the event loop and the consumer is a worker thread, so `put_nowait` here and `get` there is a data race, not a queue |
| **`queue.Queue(maxsize=N)`** | Thread-safe and bounded — **but `maxsize` counts items**, which is Finding 1. Bounding what we do not care about while leaving bytes unbounded is the defect, not the fix |
| **`multiprocessing.Queue`** | Pickles every body across a pipe. Only relevant if Task 3c sends us to processes |
| **`queue.SimpleQueue`, unbounded, with the byte accounting outside it** | **The choice.** Thread-safe, C-implemented, `put` never blocks, and it carries none of the machinery this does not use — no `maxsize`, no `task_done()`, no `join()` |

**The bound lives beside the queue rather than inside it**, because the bound is in bytes and no
standard queue offers that:

```
_queue    queue.SimpleQueue    unbounded FIFO, thread-safe both ends
_lock     threading.Lock       guards the counter below
_pending  int                  bytes currently waiting
```

`submit()` takes the lock, adds `len(request) + len(response)`, compares against `queue_max_bytes`,
decides store-or-drop, and puts. The worker `get()`s, does the work, and subtracts under the same
lock. **The lock is held for nanoseconds and never across I/O** — which is what keeps the promise
that the request path cannot block.

**It counts payload bytes, not `sys.getsizeof`.** Each `bytes` object carries ~33 bytes of header,
and ignoring that makes the real ceiling a fraction of a percent higher. **This is a tripwire, not an
accountant.**

### Shutdown

`close()` puts a sentinel and joins the worker **with a timeout**, then logs the final summary. A
timeout rather than an unbounded wait because a full queue is ~640 bodies, which at tens of
milliseconds each is a twenty-second shutdown — and a router that will not stop is worse than a
corpus missing its last few bodies. **Anything abandoned is counted and named in that last line**, so
the hole is recorded here exactly as it is anywhere else.

The timeout is a module constant rather than a sixth config key, on the same KISS grounds as the
`workers` key that is also absent.

### Why a thread, and not the other two

| | Verdict |
|---|---|
| **`asyncio` task and `asyncio.Queue`** | **Wrong tool.** Compression is CPU-bound and blocking; a coroutine doing it stalls every other request for its duration. The escape is `run_in_executor`, which *is* a thread pool — async arrives back at threads with a layer added. There is no true async file I/O on this platform either |
| **`multiprocessing`** | **Pays a large cost for a problem this load does not have.** Every body is pickled and copied down a pipe — the opposite of taking a reference to bytes already in memory — and a child that is OOM-killed stops archiving silently unless something watches it. `EPD-003`'s non-goals name *"an ingestion service"* |
| **One daemon thread** | **The fit, if and only if the GIL is released during compression.** That is the claim Task 3a proves or refutes, and the design rests on it |

**And why not simply write it inline?** Because a 200 KB compress-and-`fsync` on the event loop
stalls every concurrent request for tens of milliseconds. **That is failure mode 3 of the milestone's
central claim, stated as a mechanism.** The queue exists for that reason and no other.

### The load this is actually for

Measured from what this project has already captured, rather than assumed:

| Session | Calls | Over | Arrival rate |
|---|---:|---|---|
| Phase 9 `run-01` — two concurrent headless sessions | 49 | ~6 min | **~0.14 calls/s** |
| The frozen step-6 session — eleven sessions | 142 | 77 min | **~0.03 calls/s** |

**The owner's target is one laptop with two to five concurrent harnesses**, each possibly spawning
subagents — call it **1–3 calls/second at a burst**. Against a single thread's *published* ~29
bodies/second at level 19, that is **ten to thirty times inside the limit**, and peak memory for
~15 calls in flight is a few megabytes.

**So the benchmark's job is to confirm a simple design on this machine, not to choose between
architectures.** Both figures in that paragraph are somebody else's measurements until Task 3c.

### What makes it diagnosable

The instrumentation exists to answer *did this ever come close?* **retrospectively**, from data the
store is already writing, with no component added and nobody watching at the time.

| Index column | Answers |
|---|---|
| `queue_ms` | How long this body waited before a worker took it. **The pressure signal** — near zero until the worker is the bottleneck, then climbing |
| `store_ms` | Hash, compress, write and `fsync` for this call. Says *why* it was slow, if it was |
| `queue_bytes` | Pending bytes at the moment of submit. Shows depth building **before** anything is dropped |

Appended after the two refs, so the first twenty columns stay identical to `calls.csv`'s and in its
order — which is what lets a rotated segment and a day file feed one spreadsheet.

Two log lines, and the restraint is as deliberate as the lines:

- **One `WARNING` the first time a body is dropped in a run**, with the reason and the pending bytes;
  then suppressed and counted. Warning on every drop turns overload into log spam, which is the
  moment the log most needs to stay readable.
- **A periodic `INFO` summary** — bodies stored, bytes in and out, drops by reason, peak pending
  bytes, longest `queue_ms`. **No new route:** `/health` stays as it is, and the catch-all forwards
  everything else, so a new endpoint is a surface this does not need.

### Two kinds of "it was not saved", and only one of them was covered

*Added 2026-08-18, from the owner's question about diagnosing loss generally rather than only in the
corpus.*

**First, and worth stating because it is easy to fear the wrong thing: the router never skips a
call.** Dispatch and relay always happen — *"telemetry must never break a call"* is a
non-negotiable, and every failure in the recorder is caught and dropped. What can be lost under load
is a **record**, never a request. Those are different words and the difference matters when reading a
gap.

| What was lost | How you find out | Change needed |
|---|---|---|
| **A body** | The index row's ref cell says `dropped`, `too_large`, `absent` or `error` — per call, permanently | None. This is the design |
| **A CSV row, because the write failed** | `stats.py` and `record()` both already log a `WARNING` and carry on | None |
| **A CSV row, because `record()` was never reached** | **Nothing says so today.** This is the blind spot: no row, no log line, complete silence | **One counter pair** |

**The counter pair is the whole addition, and it is deliberately small.** `begin()` counts calls that
arrived; `record()` counts rows written. **The difference is calls in flight plus calls silently
lost** — so a gap that persists across the periodic summary, and a non-zero gap after the queue has
drained at shutdown, is the blind spot made visible without changing a single column of `calls.csv`.

The same summary carries the corpus totals, so one line answers both questions:

```
corpus: 412 arrived, 412 recorded, 0 lost | stored 806 (78.1 MB → 6.4 MB),
        dropped 0, too_large 1, error 0 | pending peak 214 KB, queue_ms max 31
```

**What was considered and deliberately left out**, all recorded in `../../backlog.md` rather than
built: a metrics or status endpoint for live visibility, a sequence column in `calls.csv` to make a
gap self-evident — which the milestone's own non-goals forbid, since that file does not change — and
any per-failure detail beyond the counters and the existing warnings. **This is a prototype meant to
be finished and used**, and the set above answers *did anything get lost, and why* without adding a
component.

### One thing that is never in a worker

**Dictionary training.** It runs over thousands of samples and takes seconds to minutes, and it
belongs to an offline procedure the router never calls. Compression and writing are the worker's;
training is Group C's, and keeping it out is what lets the write path stay small.

---

## The tasks

**Nothing below has been executed.** Every group is marked, and the markers are placeholders to be
closed out at Task 20 — see "Placeholders in this file".

### Group A — open the phase *(not started)*

| # | Task |
|---|---|
| **1** | Open the branch and the folder; commit this file and `notes.md` |
| **2** | Record the re-derivation in `notes.md` — the nine findings, and the baselines re-derived **by running them** |
| **3** | `../../status.md` — record the in-flight branch |

### Group B0 — the benchmark, before any store code *(not started)*

*Added 2026-08-18. **Task numbers are never renumbered; an insertion is a letter**, so these follow
Task 3 rather than shifting Group B. The group exists because the first version of this plan chose a
threading design from published figures for somebody else's machine, and asserted a GIL property it
had not read the source for.*

| # | Task |
|---|---|
| **3a** | `uv add zstandard`; **read its source** on whether the GIL is released during compression, and record what the source says rather than what the documentation claims |
| **3b** | `docs/procedures/corpus-benchmark/` — the script, over the bodies already in `logs/corpus-gate/`. Reads and writes under `logs/`, **never into `docs/`** |
| **3c** | Run it and record the numbers. **It decides three things:** whether a thread buys anything, the write-path compression level, and the worker count. If the GIL is *not* released, measuring a process pool becomes the next task and the thread design is withdrawn |

**What 3c measures, and what each measurement decides:**

| Measurement | Decides |
|---|---|
| Wall clock across 1 / 2 / 4 threads over the same corpus | **Whether the GIL is released.** Four threads at ~a quarter of the time means yes; ~the same time means no, and the design above is wrong |
| Throughput and ratio at levels **3 / 9 / 19**, with the held-out dictionary and without | The write-path level — and the half nobody has asked: **how much ratio level 19 was buying once a dictionary carries the preamble** |
| Per-body cost split into sha256, compress, write, `fsync` | Whether `store_ms` is dominated by compression or by the disk, which decides whether the level matters at all |
| Dictionary precompute, once against per body | Confirms the compressor is built once at startup rather than per call |
| `zstandard`'s `train_dictionary()` against `zstd --train`, same samples | **The one thing "use one tool" risks.** Both wrap libzstd but their training *defaults* may differ, and defaults are where Phase 9 found non-monotonicity. If they disagree, Phase 9's figures stop being directly comparable and Task 3c says by how much |

**What it deliberately does not measure: processes.** If threads scale, a process pool is an option
we would not take, and measuring it is work spent on a road not travelled. **If the GIL is not
released, that measurement becomes the next step** — conditional rather than speculative.

### Group B — the store *(not started)*

| # | Task |
|---|---|
| **4** | Add `zstandard`; `make sync`; a smoke test that a dicted frame round-trips byte-identically |
| **5** | `src/ilirium_llm_router/corpus.py` — the blob store: content addressing on the plaintext, the per-day layout, `incoming/` → `fsync` → rename, dedup scoped to the day, dictionaries hard-linked into the day folder |
| **6** | The byte-bounded queue and its worker thread, **plus the arrived/recorded counter pair** — the drop policy, drain on close, and **it never raises**: a body store is telemetry-shaped and telemetry does not get to break a call. **Widened 2026-08-18:** the counters, the once-per-run drop `WARNING`, and the periodic summary line |
| **7** | The day index: header re-emitted in every file, a ref cell holding a digest or a reason word. **Widened 2026-08-18 from 22 columns to 25** — `queue_ms`, `store_ms` and `queue_bytes` appended after the refs, so the first twenty stay identical to `calls.csv`'s and in its order |
| **8** | The `corpus:` config block — five keys, `extra="forbid"`, relative-path resolution against the config file's directory, and `--check` prints it. Neither limit may be disabled |
| **9** | Wire into `Proxy.record()`'s four call sites and `app.py`'s lifespan; hold the request body on `Call`; tee the response into a capped buffer in `watch()` |
| **10** | Tests, including **a non-UTF-8, non-JSON body round-tripping byte-identically** — that is what discharges failure mode 2 by construction rather than by assertion |

### Group C — the dictionary *(not started)*

| # | Task |
|---|---|
| **11** | `docs/procedures/corpus-dictionary/` — the trainer, **using `zstandard` rather than the binary**, which **measures a candidate against the incumbent on a held-out slice and refuses to install a worse one.** Directly from `zstd --train` being non-monotonic at 68 samples. With its README saying when re-running is worth it |
| **12** | Train the first real dictionary from the surviving `logs/corpus-gate/` corpus; install it; verify a dicted round-trip end to end and record the ratio |

### Group D — the telemetry move *(not started)*

| # | Task |
|---|---|
| **13** | Move `calls.csv` and `router.log` into `logs/telemetry/` — `config.yaml`, `config.py`'s two defaults, `tests/test_config.py`, `tests/test_logging_setup.py`, and the live files on disk |
| **14** | The sweep `../../procedures/link-check.py` **cannot see** — `CLAUDE.md`, `README.md`, `../../reference/observability.md`, `../../procedures/testing-against-claude-code.md`, `../../procedures/lmstudio-capability-probes/probe.py` — stating which archive and EPD hits were **left** and why |

### Group E — harvest and close *(not started)*

| # | Task |
|---|---|
| **15** | `docs/reference/corpus.md` — the durable spec, with a nameable trigger; its row in `../../reference/README.md`; a `CLAUDE.md` pointer that says **when** to open it |
| **16** | Close `EPD-003`'s open questions **3–6** in place and dated; graduate what changes a decision into `../../reference/design-decisions.md` |
| **17** | The numbers into `../../reference/measurements.md` — **all four columns or they do not go in** |
| **18** | `../implementation-plan.md` — Phase 10 from outline to record, and the central claim's three failure modes marked honestly, including the one this phase does not discharge |
| **19** | **Replace or delete `../../prompt.md`.** It names Phase 10 and nothing else, and `../../README.md` records that it is the one file there allowed to go stale — which is why it must be closed out rather than left |
| **20** | Close out: `notes.md`'s "Verified by"; the **widened** placeholder sweep; `make test`; `link-check.py` **run, not predicted**; merge `--no-ff` with the message from a temp file; the hash into `notes.md` **and** this file's Record table |

---

## Placeholders in this file

**Written down rather than remembered**, because `../../method/IDM-001-git-branching.md`'s closeout
rule was generalised on 2026-08-17 for exactly this defect: Phase 9 read that document *during* the
phase, obeyed it, and still shipped `*(not started)*` group markers and a stale count. **A rule stated
as an instance gets obeyed as an instance**, so this section names the instances.

| Where | Placeholder | Closed out at |
|---|---|---|
| The header, first line | *"Not yet executed — no task below has been started"* | Task 20 |
| The **six** group headings | `*(not started)*` | Task 20, each group as it completes. *Five until Group B0 was added on 2026-08-18* |
| The Record table below | `Merge commit \| not yet merged` | The merge itself |
| "What is settled" | *"still open questions until Task 16"* | Task 16 |

**The grep, and it must be widened rather than trusted:**

```
grep -rniE "\(not started\)|\(in progress\)|not yet (merged|done|run|written|built|started|executed)" docs
```

The first sweep run against Phase 9's defect used `is not started` and matched nothing, because the
target was written `*(not started)*`. **A grep narrow enough to miss its own target is worse than no
grep**, since it returns clean and reads as proof.

---

## Documented versus measured

| Claim | Status |
|---|---|
| `make test` reports **158**; `link-check.py` reports **68 broken, 2 roundabout** | **Measured** — run 2026-08-18, not predicted |
| Python 3.13 has no `compression.zstd`, and `zstandard` is not installed | **Measured** — on this interpreter, 2026-08-18 |
| `zstd` 1.5.7 is present | **Measured** |
| `logs/corpus-gate/` still holds Phase 9's three runs and eight dictionaries | **Measured** — listed 2026-08-18 |
| `Proxy.record()` is reached by every path that produces a row | **Measured** — four call sites read off `proxy.py`, each traced to its entry point |
| A caller vanishing after headers produces **no** row today | **Inferred** — from Starlette skipping a body generator on disconnect, which `proxy.py`'s own comment on `BackgroundTask` reasons about. Not observed here |
| `os.link()` into a date folder is portable and `tar` still emits a real file | **Inferred** — from how `tar` detects hardlinks among archived members. **Task 5 measures it** rather than trusting this row |
| A byte-bounded queue is necessary because a 1,000-item queue is 200 MB | **Extrapolated** — from Phase 9's measured median request of 103,935 bytes |
| `zstandard`'s dictionary training matches `zstd --train`'s | **Unverified.** Both wrap libzstd, but their *defaults* may differ — and training defaults are exactly where Phase 9 found non-monotonicity. **Task 3c compares them**; if they disagree, Phase 9's figures are not directly comparable and the note says by how much |
| **`zstandard` releases the GIL during compression** | **Unverified — and it is load-bearing.** If it is false, one thread and eight threads are the same thread and the design above is wrong. Asserted as fact in this file's first version; **Task 3a reads the source and Task 3c measures the scaling** |
| Single-thread zstd runs at ~2–6 MB/s at level 19, ~350–500 MB/s at level 3 | **Documented only** — published figures for other machines, quoted here to size the problem. **Task 3c re-measures both on this one** |
| Two to five concurrent harnesses is 1–3 calls/second | **Extrapolated** — from two measured sessions at 0.14 and 0.03 calls/s, scaled to the owner's stated target. One laptop, and no session has ever run five harnesses |
| Compression in the worker thread does not slow a *call* | **Unmeasured**, and this phase does not measure it — a thread bounds throughput rather than latency, but that is an argument, not a number. See below |
| ~250 MB a year at an hour a day | **Extrapolated** — from `EPD-003`'s own projection, itself extrapolated from one session |

---

## What this phase does not settle

**Failure mode 3 — "archiving slows a call" — will not be discharged**, and Task 18 says so in
`../implementation-plan.md` rather than letting the table imply otherwise. The scope decided in the
interview has no live session, and **in-process timing is not the same measurement**. What would
settle it: one driven session with capture on against one with it off, comparing `ttfb_ms` and
`duration_ms` over the same work. That is a later phase, or an addendum to this one.

**`record()`'s blind spot stays open.** A caller that vanishes after response headers gets no CSV row
today and will get no corpus entry either — `watch`'s `finally` never runs, so the funnel is never
reached. **Named, not fixed**; fixing it is a change to the recorder, which is not this phase's
subject.

**Whether the router could run as several processes.** Recorded in `../../backlog.md` rather than
built. The idea's session-distinguishing half is **already solved and measured** — `session_id` and
`agent_id` are header-copied columns, and Phase 9's corpus carries five distinct sessions and ten
subagent rows through one instance. Its throughput half has **one concrete blocker that a reverse
proxy does not touch**: every multi-process form — several instances, `uvicorn --workers N`, or a
process pool — hits the fact that **the recorder's writers are single-process designs.** `calls.csv`
rides `RotatingFileHandler`, whose lock is a thread lock, and two processes rotating one file corrupt
it. So the cheap part is the proxy and the expensive part is the writers.

**Whether a response dictionary pays.** Unmeasured, and Task 12 trains only a request dictionary.

**Whether any of this transfers to interactive use.** The dictionary Task 12 trains comes from a
**headless** corpus whose static preamble is ~28 KB smaller than the frozen interactive one, of which
70 of 73 bodies are Anthropic and whose sessions are short. **All three flatter a dictionary.**

---

## What could go wrong

- **`zstandard` does not release the GIL where it matters**, and the worker thread contends with the
  event loop. Task 4's smoke test is where that surfaces, before anything is wired in.
- **The hard-link trick fails across a filesystem boundary** — `logs/` and the corpus are the same
  volume here, but a configured absolute `dir` on another mount would raise. Task 5 falls back to a
  copy and says which happened.
- **A dictionary trained from `logs/corpus-gate/` is uncommittable**, exactly as the bodies are. It
  stays under `logs/`, which `.gitignore:228` covers, and Task 12 stages with explicit paths rather
  than `git add -A` — the discipline Phase 9 adopted for the same reason.
- **The telemetry move breaks a citation nothing checks.** `link-check.py` globs `*.md` only, so
  `config.yaml`, the `Makefile`, `pyproject.toml` and `src/` are unchecked by it. Task 14 is a reading
  task, not a grep task.
- **Forward citations inflate the link-checker count.** This file names files it will create —
  `reference/corpus.md`, `procedures/corpus-dictionary/`, `src/ilirium_llm_router/corpus.py`. That is
  `../../backlog.md`'s recurring false-positive class, not breakage; Phase 8's plan contributed 23.
  **Task 20 re-derives the count by running the tool** and expects these to have resolved themselves.

---

## Done when

The benchmark has numbers and the executor was chosen from them rather than argued; the store exists
and is off by default; a body round-trips byte-identically through it; a full queue
produces a row saying `dropped` rather than a stall; `EPD-003`'s open questions 3–6 carry dated
answers; a real dictionary is trained, installed and measured against the incumbent by an instrument
that would refuse a worse one; `calls.csv` and `router.log` live under `logs/telemetry/` with every
citation swept; `../../prompt.md` is replaced or deleted; `make test` passes; `link-check.py`'s count
is re-derived **by running it**; the index carries `queue_ms`, `store_ms` and `queue_bytes` so the
severity question is answerable later without anyone having watched; and **no captured body and no
dictionary is committed.**

---

## Record

| | |
|---|---|
| Branch | `feat/phase-10-body-store` |
| Fork point | `d885b2f` |
| Merge commit | *not yet merged* |

*Writing "not yet merged" while it is true is correct; leaving it there after the branch is gone is
this repository's signature failure, and `../../method/IDM-001-git-branching.md` names it. Closed out
at Task 20.*
