# Phase 10 — the body store: plan

**Written 2026-08-18 on `feat/phase-10-body-store`, forked from `main` at `d885b2f`. Execution is
under way; the group markers under "The tasks" say how far, and are the only place that says so.**

*This line read "Group A has executed; Tasks 4 to 24 have not" until 2026-08-18, when Task 4
executed and made it false. **It was a second copy of what the group markers already carry**, and a
second copy is what this repository's own placeholder rule exists to catch — so it was repointed at
them rather than re-enumerated, which would only go stale again at Task 5.*

**Twenty-five tasks in six groups.** Group A opens the phase and records what the opening interview
decided. Group B benchmarks, before any store code exists. Group C builds the store. Group D trains
the first dictionary and writes the instrument that keeps training honest. Group E moves the
telemetry files. Group F verifies the configuration, harvests, closes out `EPD-003`'s remaining open
questions, and merges.

**This phase's first act was its re-derivation, and it ran before this file was published** — the same
shape Phase 9 used, for the same reason: findings that land during the interview should shape the task
list rather than correct it afterwards. **The nine findings are in `notes.md`**, beside this file, and
four of them changed the design below.

*Revised 2026-08-18, after a second interview on the write path — the owner raised performance under
concurrent harnesses and refused the unverified GIL claim this file rested on. **Corrected in place
with dated notes rather than rewritten**, per the precedent Phase 8's Task 17a set for a live plan.
What changed: a benchmark group is new, the queue and index tasks are widened, and four decisions
were added above. *(The task list was **renumbered** on 2026-08-18, on the owner's instruction and
before anything executed; the exception is recorded under "The tasks".)*

---

## Why this is a `feat/` branch

`../../method/IDM-001-git-branching.md` — the prefix answers *which kind of work*, and `phase-N-` is
orthogonal to it. **`feat/` is product work: anything that changes `src/`.**

**Phase 9 was `docs/` because no `src/` change survived it** — its capture patched `proxy.py` and
restored it, and `git diff main -- src/` was empty at the merge. **This phase is the opposite case.**
`src/ilirium_llm_router/` gains a module and keeps it; **`config.py`, `proxy.py`, `app.py`,
`observe.py` and `cli.py` all change and stay changed**; `pyproject.toml` gains a dependency.
*(`observe.py` and `cli.py` were missing from this list until 2026-08-18 — `Call` is defined in the
first and `--check`'s output is built entirely in the second.)* Nothing here is restored at the end.

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
| **The executor** | **One worker thread, chosen from a measurement rather than from this table.** The prototype stays simple; the benchmark below says whether it is right. A `corpus.workers` knob is added **only if** Task 6's numbers show the GIL is released *and* that more than one worker helps — configuration this project does not need is configuration it does not get |
| **Diagnosability** | **The severity question is answered from data the store already writes.** The owner's requirement, 2026-08-18: keep the first prototype simple, but instrument it so that *how bad did this get under real load* is answerable months later without having been watching. Three index columns and two log lines; see "The write path, concretely" |
| **Benchmark before code** | **Group B runs before any store code is written**, so Group C is written against numbers instead of against published throughput figures for somebody else's machine |
| **The size ceiling** | **Kept, and configurable — it already was.** `EPD-003`'s question was answered *(Q4)*: it protects against **one enormous body** during the call, which the queue bound cannot reach because that protects against **many ordinary bodies afterwards**. Neither can be disabled |
| **One tool, not two** | **`zstandard` for the router and the trainer alike** *(Q5)*. This plan first kept the `zstd` binary for the trainer, for comparability with Phase 9's figures; the owner asked why two tools and **simplicity wins**. Task 6 checks that library training and `zstd --train` agree rather than assuming it |
| **Dictionaries** | **Plain copies, and each day folder is self-contained** *(Q7)* — *any metadata, any dicts, any archives* belong to the day. **This restores the sketch**: the root `dicts/` and the hard links were this plan's addition, and declining the links left the root folder with no job |
| **Compression level** | **Configurable as `compress_level_zstd`, with a default measured by Task 6** *(Q10)* |
| **Diagnosing loss generally** | **One counter pair, and nothing else.** Calls arrived against rows written. **It lives in `Proxy` and is always on**, independent of `corpus.enabled` — *decided 2026-08-18 from the forward review, which found it built inside the opt-in corpus and therefore absent on the default machine, for a question about `calls.csv`.* A metrics endpoint and a sequence column were both considered and **reserved to `../../backlog.md`** |
| **Several router instances** | **Considered and deferred, recorded in `../../backlog.md`.** Its session-distinguishing half is already solved and measured; its throughput half has one concrete blocker that a reverse proxy does not touch — see "What this phase does not settle" |

### And two questions the owner did not have to answer

Both are `EPD-003` open questions, and both are answered here by argument rather than by preference.
**They are still open questions until Task 20 records the answers in `EPD-003` itself.**

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
construction**, and Task 13 is what makes that a test rather than an assertion. **Failure mode 3 —
archiving slows a call — is not discharged by this phase**, and that is stated rather than implied;
see below.

---

## The shape

```
logs/
  telemetry/                      calls.csv and router.log — moved in this phase, Task 16
  corpus/
    dicts/                        THE SOURCE. Where the trainer writes and the router reads
      req-2026-08-18T104500Z.dict
    2026-08-18/                   UTC-derived, never local. SELF-CONTAINED
      index.csv                   25 columns: calls.csv's 20, in order, then two refs and three timings
      manifest                    the index's schema version, and nothing else
      dicts/                      plain copies of every dictionary this day used
        req-2026-08-18T104500Z.dict     copied from ../../dicts/ at first use
      incoming/                   staging for atomic rename
      requests/3f/3f9c….zst
      responses/b2/b20e….zst
```

**A day folder is self-contained and nothing lives above it.** Owner's rule, 2026-08-18: *any
metadata, any dicts, any archives* belong to the day. `tar` one folder, or `rm -rf` one folder, and
neither operation can reach anything outside it.

### Where a dictionary lives, and how the router finds one

*Added 2026-08-18 from the forward review, which found this the largest hole in the plan — **both
runs found it**, and `../implementation-plan.md` names "a dictionary bootstrap and retraining policy"
as something this phase must settle.*

**`logs/corpus/dicts/` is the source. A day folder holds copies.** The trainer writes there, the
router reads the newest from there at startup, and copies whichever it used into each day folder it
opens.

**This is not a reversal of Q7, though it looks like one.** Q7 removed a root folder that existed
**only to be the target of hard links** — scaffolding for an optimisation that was declined. This one
has a job the design actually needs: somewhere for the trainer to write that is not inside a day, and
somewhere the router can look that does not depend on which days still exist. **A day folder is still
self-contained for reading**, which is what the rule was about: `tar` one, unpack it elsewhere, and
every blob in it opens.

**Nothing above a day may be required to read a day. Nothing inside a day is where new dictionaries
go.** Those are different directions and only the first was ever the rule.

**The store must work with no dictionary at all**, and that is the ordinary case at first run:
`logs/corpus/dicts/` is empty until Task 15, and **Group C ships before Group D**. Bodies are then
written **undicted** — plain `zstd` frames at ~3.12× — and the blobs stay valid forever, because a
frame names its own dictionary or names none. **Nothing is ever recompressed.** So the first day's
bodies are simply larger, and no task has to wait for a dictionary to exist.

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
| **Compression level** | not considered — every figure was measured at level 19 | **Configurable, with a default measured by Task 6.** Level 19 is an offline setting; the write path is a different question and nobody had asked it |
| **One compression tool** | not considered | **`zstandard` everywhere**, router and trainer alike. This plan first proposed keeping the `zstd` binary for the trainer, for comparability with Phase 9's numbers; **the owner asked why two tools, and simplicity wins.** Task 6 checks that library training and `zstd --train` agree rather than assuming it |
| **Dedup scope** *(6)* | implied by the tree, never stated | **Per day, and that is deliberate.** Cross-day dedup would make `rm -rf <a-day>` orphan another day's refs, which is the whole retention answer |
| **Per-direction dictionaries** | *"Task 9 measures whether the split pays"* | **Supported structurally, but only a request dictionary is trained.** Frames name their own dictID, so more than one is free — but the gate measured *request* bodies, and its own `evidence/README.md` says it answers nothing about responses. Responses write undicted until somebody measures it |

### One design consequence worth stating on its own

**A full queue still records the hole.** The item handed to the worker is
`(CallRecord, request_bytes, response_bytes, submitted_at, pending_at_submit)`. **The last two were
missing until 2026-08-18**, when the forward review found that `queue_ms` and `queue_bytes` are both
values only `submit()` can see: by the time the worker runs, `_pending` has moved. Read in the worker
instead, `queue_bytes` would record depth at *dequeue* — near zero at this load, and therefore
**indistinguishable from working**. When the bodies would push the queue past its byte
bound, **the record is enqueued anyway with both ref cells set to `dropped`** — a record-only item is a
few hundred bytes and is never refused.

So `EPD-003`'s *"drop the body and record that it was dropped — a corpus with a known hole is fine, a
stalled request is not"* becomes literally true rather than approximately: **the hole is a row, not an
absence.**

**Bodies the router authored are not stored.** *Decided 2026-08-18.* Three exist — the 400 for a
missing `model`, the 502 for an unreachable backend, and the injected SSE `error` event — and their
ref cell reads `absent`. This **applies a rule already on the books** rather than inventing one:
`../../reference/design-decisions.md` says of the injected event that it is *"not counted in
`response_bytes` and not fed to the scanner … both measure what the backend sent, and these bytes are
ours"*. The milestone's claim is *every body it **carries***, and these are authored. `error_status`
in the same row already says why the response side is empty.

**Everything on the request path is one append and one counter increment.** Hashing, compression,
`fsync`, rename and the index row all happen in the worker thread. The sketch never said where hashing
lived, and sha256 over a 200 KB body on the event loop is small but not free.

### The config block

```yaml
corpus:
  enabled: false              # opt-in. Nothing is written until this is true
  dir: logs/corpus            # relative paths resolve against the config file's directory
  compress_level_zstd: 9      # the zstd level the write path uses; default measured by Task 6
  max_body_bytes: 1048576     # one body bigger than this is not stored: `too_large`
  queue_max_bytes: 67108864   # total bytes waiting to be written; over it: `dropped`
```

### Two limits, because they are checked at two different moments

*Rewritten 2026-08-18. An earlier version named what each limit protects and not **when**, and the
timing is the entire reason both exist.*

**Start from what the router holds today, without any corpus.**

| | Held whole in memory today? |
|---|---|
| The **request** body | **Yes, always.** `proxy.py:133` is `body = await request.body()` — the router reads the whole body to relay it. **The corpus does not change *whether* it is held; it changes *how long*.** Today `body` becomes unreachable once `relay()` returns, so it is freed **before the model starts generating**. Task 12 keeps it alive until `record()` — the whole response, which against a local model is minutes. *(This row said "is not changed by it" until 2026-08-18, which read as "no memory thought needed here".)* |
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

**There is deliberately no `workers` key.** One worker until Task 6 says otherwise.

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
| **`multiprocessing.Queue`** | Pickles every body across a pipe. Only relevant if Task 6 sends us to processes |
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
| **One daemon thread** | **The fit, if and only if the GIL is released during compression.** That is the claim Task 4 proves or refutes, and the design rests on it. *(Task 4 ran on 2026-08-18 and it is released — read off the shipped binary, not the documentation. **The condition is met; whether more than one thread helps is still Task 6's.**)* |

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
architectures.** Both figures in that paragraph are somebody else's measurements until Task 6.

### What makes it diagnosable

The instrumentation exists to answer *did this ever come close?* **retrospectively**, from data the
store is already writing, with no component added and nobody watching at the time.

| Index column | Answers |
|---|---|
| `queue_ms` | How long this body waited before a worker took it. **The pressure signal** — near zero until the worker is the bottleneck, then climbing |
| `store_ms` | Hash, compress, write and `fsync` for this call. Says *why* it was slow, if it was |
| `queue_bytes` | Pending bytes at the moment of submit. Shows depth building **before** anything is dropped |

**On a row whose body was not stored, `store_ms` is empty** — not zero. `../../reference/observability.md`
already governs this: *an absent value is an empty cell, never a zero; an absent count and a genuine
zero are different facts.* `queue_ms` and `queue_bytes` are still real on a `dropped` row, because the
record was queued even though the body was not.

Appended after the two refs, so the first twenty columns stay identical to `calls.csv`'s and in its
order — which is what lets a rotated segment and a day file feed one spreadsheet.

Two log lines, and the restraint is as deliberate as the lines:

- **One `WARNING` the first time a body is dropped in a run**, with the reason and the pending bytes;
  then suppressed and counted. Warning on every drop turns overload into log spam, which is the
  moment the log most needs to stay readable.
- **A periodic `INFO` summary**, **emitted from the submit path every 500 calls and once at close.**
  *Defined 2026-08-18; it was named four times and specified never.* From **submit** rather than from
  the worker on purpose — a worker that has stalled emits nothing, and a stalled worker is exactly
  when the line is wanted; submits keep happening and carry the growing `pending` with them. No timer,
  so an idle router says nothing, which is correct. **No new route:** `/health` stays as it is, and
  the catch-all forwards everything else.
  **The arrived/recorded half is emitted whether or not the corpus is enabled**; the corpus totals
  join it when it is.

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
lost** — so a gap that persists, or a non-zero gap after shutdown, is the blind spot made visible
without changing a single column of `calls.csv`.

**It lives in `Proxy`, not in `corpus.py`, and it is always on.** *Corrected 2026-08-18.* It answers a
`calls.csv` question, and `calls.csv` is always on while the corpus is opt-in — built inside the
corpus it would be **absent on the default machine**, which is the only machine the question is about.

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
training is Group D's, and keeping it out is what lets the write path stay small.

---

## The tasks

**Twenty-five tasks in six groups. Group A has executed; nothing after it has.** Every later group is
marked, and the markers are placeholders to be closed out at Task 24 — see "Placeholders in this
file".

> **Renumbered once, on 2026-08-18, on the owner's instruction — and this is an exception to
> `../../README.md`, recorded rather than quietly taken.** That file says task numbers *"are never
> renumbered once published"* and that an insertion takes a letter. The lettered form had already
> been used: Group B0 held `3a`, `3b`, `3c`.
>
> **`3a` is now a different task**, added after Group A executed — the forward review. **This
> paragraph is the only place the old meaning appears**, and it is named here rather than left for
> somebody to trip over: a reused label is the cost of renumbering once, paid later than the renumber.
>
> **Phase 9 drew the same line one step earlier and gave the reason.** Its plan renumbered *before
> publication* because *"publishing it and then amending it would have spent letters on work nobody
> had started"* — and that is exactly the state here: **nothing has been executed**, so no task
> number has yet been cited by a commit doing the work.
>
> **One cost cannot be undone and is named.** Four commit messages already in this branch's history
> say *"Task 1 of…"*, *"Tasks 2 and 3 of…"* against the old numbering, and git history is not
> editable. Tasks 1 to 3 keep their numbers, so three of those four remain correct; the fourth
> refers to work whose number did not move either. **From the first task that executes, the rule
> applies again with no exception.**

### Group A — open the phase *(executed)*

| # | Task |
|---|---|
| **1** | Open the branch and the folder; commit this file and `notes.md` |
| **2** | Record the re-derivation in `notes.md` — the nine findings, and the baselines re-derived **by running them** |
| **3** | `../../status.md` — record the in-flight branch |
| **3a** | **The forward review** — `review-charter.md`, beside this file. Two runs in parallel, this session and a fresh-context agent, over Tasks 4–24 and the design they rest on. Read-only; the work list lands in `notes.md`. **Then `method/IDM-004` is written from what it cost** |

*Task **3a** carries a letter rather than a number, and the difference from the renumber above is the
point: **Tasks 1 to 3 have executed**, so the exception is spent and `../../README.md`'s rule applies
again with no exception. Inserting it as a number would shift twenty-one tasks that are now cited by
this file, `notes.md`, `review-charter.md` and `../../status.md`.*
### Group B — the benchmark, before any store code *(in progress)*

**Task 4 executed 2026-08-18; Tasks 5 and 6 have not.** The marker is written `*(in progress)*` and
the detail sits outside it **on purpose** — `*(in progress — Task 4 done)*` would not match the
prescribed grep's `\(in progress\)`, which is the same defect as Group A's uncatalogued marker and
the `is not started` sweep that returned clean. **The parenthesis stays exactly greppable; the prose
carries the state.**

*Added 2026-08-18. The group exists because the first version of this plan chose a threading design
from published figures for somebody else's machine, and asserted a GIL property it had not read the
source for. **Permission to run it was given on 2026-08-18.***

| # | Task |
|---|---|
| **4** | `uv add zstandard`; **read its source** on whether the GIL is released during compression, and record what the source says rather than what the documentation claims |
| **5** | `docs/procedures/corpus-benchmark/` — the script, over the bodies already in `logs/corpus-gate/`. **Its output goes to `docs/procedures/corpus-benchmark/runs/`, gitignored**, per `../../README.md`: *an instrument's output directory follows the instrument, never the archive.* Add the `.gitignore` line — the two existing instruments have explicit per-instrument entries, not a glob. **And a row in `../../procedures/README.md`** saying when re-running is worth it. *(This task said "writes under `logs/`, never into `docs/`" until 2026-08-18, which contradicted the tier rule it was trying to obey.)* |
| **6** | Run it and record the numbers, and **freeze the script and its output into `evidence/`** — `../../README.md`: a procedure's *results* are frozen in the phase's `evidence/`, and Phase 9 froze `gate.py` and `results.txt` for exactly this reason. Task 21 puts these numbers in `../../reference/measurements.md`, whose rule is that a number carries its instrument. *(No task froze anything until 2026-08-18, and nothing said why `evidence/` was absent — which `../../README.md` also requires.)* **It decides three things:** whether a thread buys anything, the write-path compression level, and the worker count. If the GIL is *not* released, measuring a process pool becomes the next task and the thread design is withdrawn |

**What Task 6 measures, and what each measurement decides:**

| Measurement | Decides |
|---|---|
| Wall clock across 1 / 2 / 4 threads over the same corpus | **Whether the GIL is released.** Four threads at ~a quarter of the time means yes; ~the same time means no, and the design above is wrong |
| Throughput and ratio at levels **3 / 9 / 19**, with the held-out dictionary and without | The write-path level — and the half nobody has asked: **how much ratio level 19 was buying once a dictionary carries the preamble** |
| Per-body cost split into sha256, compress, write, `fsync` | Whether `store_ms` is dominated by compression or by the disk, which decides whether the level matters at all |
| Dictionary precompute, once against per body | Confirms the compressor is built once at startup rather than per call |
| `zstandard`'s `train_dictionary()` against `zstd --train`, same samples | **The one thing "use one tool" risks.** Both wrap libzstd but their training *defaults* may differ, and defaults are where Phase 9 found non-monotonicity. If they disagree, Phase 9's figures stop being directly comparable and Task 6 says by how much |

**What it deliberately does not measure: processes.** If threads scale, a process pool is an option
we would not take, and measuring it is work spent on a road not travelled. **If the GIL is not
released, that measurement becomes the next step** — conditional rather than speculative.

**On a negative result, Task 6 stops and proposes. It does not proceed to Group C.** *Added
2026-08-18: the branch was named and left with no task, no gate and no consequence, while Tasks 8–13
assume the positive one.* The thread design is withdrawn, the process measurement is run, and **the
task list is re-planned with the owner** — `CLAUDE.md`'s working agreement, since a new design is a
design answer and not a build order. Re-planning after execution has begun means **lettered
insertions**, not a second renumber.

**The symmetric case is also live.** A `corpus.workers` key is promised *only if* Task 6 shows the GIL
released **and** more than one worker helping — while Task 11 fixes the block at five keys. **Either
outcome of Task 6 falsifies one of those two sentences**, and Task 11 is where it is reconciled.

### Group C — the store *(not started)*

| # | Task |
|---|---|
| **7** | **The smoke test only** — that a dicted frame round-trips byte-identically. **`zstandard` was already added at Task 4**, which is what `uv add` does; this task adds no dependency. *(It read "Add `zstandard` to `pyproject.toml`; `make sync`" until 2026-08-18 — true before Group B existed, and afterwards a cold agent would find the work done and be unable to tell which task was stale.)* |
| **8** | `src/ilirium_llm_router/corpus.py` — the blob store: content addressing on the plaintext, the per-day layout, `incoming/` → `fsync` → rename, dedup scoped to the day, **the `manifest` written once when a day folder opens**, and **a plain copy into `<day>/dicts/` of each dictionary the day uses, taken from `<dir>/dicts/`**. **It must work with `<dir>/dicts/` empty**, writing undicted frames |
| **9** | The byte-bounded queue and its worker thread, **plus the arrived/recorded counter pair** — one `queue.SimpleQueue` with the byte accounting beside it, the drop policy, the timed drain on close, and **it never raises**: a body store is telemetry-shaped and telemetry does not get to break a call. Plus the once-per-run drop `WARNING` and the periodic summary line |
| **10** | The day index: **25 columns**, header re-emitted in every file, a ref cell holding a digest or one of `dropped` / `too_large` / `absent` / `error`. `queue_ms`, `store_ms` and `queue_bytes` are appended after the refs, so the first twenty stay identical to `calls.csv`'s and in its order |
| **11** | The `corpus:` config block — five keys, `extra="forbid"`, relative-path resolution against the config file's directory, and `--check` prints it. Neither limit may be disabled |
| **12** | Wire into `Proxy.record()`'s four call sites and `app.py`'s lifespan; hold the request body **and the response buffer** on `Call`, which is `observe.py`'s and is therefore an in-scope edit; tee the response in `watch()` up to `max_body_bytes`. **Plus the arrived/recorded counters, which live in `Proxy` and run whether or not the corpus is enabled.** `create_app` takes the writer the way it already takes `stats`, so a test can point one at a temporary path |
| **13** | Tests, including **a non-UTF-8, non-JSON body round-tripping byte-identically** — that is what discharges failure mode 2 by construction rather than by assertion |

### Group D — the dictionary *(not started)*

| # | Task |
|---|---|
| **14** | `docs/procedures/corpus-dictionary/` — the trainer, **using `zstandard` rather than the binary**, with **a row in `../../procedures/README.md`**, which **measures a candidate against the incumbent on a held-out slice and refuses to install a worse one.** Directly from `zstd --train` being non-monotonic at 68 samples. With its README saying when re-running is worth it |
| **15** | Train the first real dictionary from the surviving `logs/corpus-gate/` corpus; **install it into `logs/corpus/dicts/`**; verify a dicted round-trip end to end and record the ratio. **Name which `--maxdict` was chosen and why** — `logs/corpus-gate/dicts/` holds eight, and `../../reference/measurements.md` records training as non-monotonic at this sample count |

### Group E — the telemetry move *(not started)*

| # | Task |
|---|---|
| **16** | Move `calls.csv` and `router.log` into `logs/telemetry/` — `config.yaml`, `config.py`'s two defaults, `tests/test_config.py`, `tests/test_logging_setup.py`, and the live files on disk |
| **17** | The sweep `../../procedures/link-check.py` **cannot see** — `CLAUDE.md`, `README.md`, `../../reference/observability.md`, `../../procedures/testing-against-claude-code.md`, `../../procedures/lmstudio-capability-probes/probe.py`, **and `../../procedures/link-check.py:45`**, whose docstring uses `logs/calls.csv` as its worked example — a stale path *inside the instrument Task 24 runs*, and one it cannot catch itself because it globs `*.md`. Stating which archive and EPD hits were **left** and why |

### Group F — verify, harvest and close *(not started)*

| # | Task |
|---|---|
| **18** | **The configuration check** — every key, old and new, against "The configuration, and how it is verified" below. It gates the harvest: nothing is written into the durable tier from a build nobody exercised |
| **19** | `docs/reference/corpus.md` — the durable spec, with a nameable trigger; its row in `../../reference/README.md`; a `CLAUDE.md` pointer that says **when** to open it |
| **20** | Close `EPD-003`'s open questions **3–6** in place and dated; graduate what changes a decision into `../../reference/design-decisions.md` |
| **21** | The numbers into `../../reference/measurements.md` — **all four columns or they do not go in** |
| **22** | `../implementation-plan.md` — Phase 10 from outline to record, and the central claim's three failure modes marked honestly, including the one this phase does not discharge |
| **23** | **Replace or delete `../../prompt.md`.** It names Phase 10 and nothing else, and `../../README.md` records that it is the one file there allowed to go stale — which is why it must be closed out rather than left |
| **24** | Close out: `notes.md`'s "Verified by"; the **widened** placeholder sweep; `make test`; `link-check.py` **run, not predicted**; merge `--no-ff` with the message from a temp file; the hash into `notes.md` **and** this file's Record table |

---

## The configuration, and how it is verified

*Added 2026-08-18 on the owner's request: **one place that lists every setting the router has, says
which of them this phase changes, and says how each is checked before the phase closes.** Task 18
runs it.*

**`config.yaml` is validated once at startup and `extra="forbid"` is set on every model**, so a
mistyped key is an error rather than a silently ignored default. `make check` loads and prints the
whole configuration without starting the server, which is the first half of every check below.

### What exists today, and what this phase does to it

| Key | What it does | This phase |
|---|---|---|
| `server.host`, `server.port` | Where the router listens. `127.0.0.1:8787` | unchanged |
| `backends.<name>.base_url` | Where that backend lives | unchanged |
| `backends.<name>.credential` | `forward` / `strip` / `inject` — the only knob that decides what happens to the caller's credential | unchanged |
| `backends.<name>.api_key_env` | Required by `inject`, forbidden by the other two | unchanged |
| `backends.<name>.read_timeout` | How long that backend may stay **silent**, not a budget for the whole reply | unchanged |
| `logging.level` | `INFO` by default | unchanged |
| `logging.file` | The rotating log uvicorn's own lines join | **`logs/router.log` → `logs/telemetry/router.log`** |
| `logging.max_bytes`, `logging.backup_count` | 10 MiB × 5 | unchanged |
| `stats.file` | The 20-column CSV, one row per call | **`logs/calls.csv` → `logs/telemetry/calls.csv`** |
| `stats.max_bytes`, `stats.backup_count` | 5 MiB × 10 | **unchanged, and deliberately** — a milestone non-goal |
| `corpus.enabled` | **new.** Opt-in; nothing is written until true | added |
| `corpus.dir` | **new.** `logs/corpus` | added |
| `corpus.compress_level_zstd` | **new.** The zstd level the write path uses; default measured by Task 6 | added |
| `corpus.max_body_bytes` | **new.** One body larger than this is not stored | added |
| `corpus.queue_max_bytes` | **new.** Total bytes waiting to be written | added |

**`compress_level_zstd` rather than `level`**, on the owner's instruction of 2026-08-18: `level`
already means something else two keys away in this file — `logging.level` is a severity — and a key
read in isolation should say what it sets and whose scale it is on.

### How each is verified at the close

**Green tests are not a sign-off** — `CLAUDE.md`'s working agreement, and every phase in this
repository was signed off by driving the real thing. So the check has three layers, and the third is
the one that counts.

| Layer | What it establishes |
|---|---|
| **1. `make check`** | Every key above appears, resolves and prints. Relative paths resolve against the **config file's** directory, not the working directory — so the printed `logs/telemetry/calls.csv` and `logs/corpus` must be absolute and under the repository. A key removed or renamed shows up here as an error rather than a default |
| **2. `make test`** | Rejections are refusals rather than warnings: an unknown key under `corpus:`, `enabled` non-boolean, either limit at zero or negative, `compress_level_zstd` outside **1–22**, hardcoded as a pydantic bound. Owner's decision 2026-08-18: *hard-code it; no need to parse another library*. It is a sanity check, not a contract with libzstd — 1–19 are the ordinary levels and 20–22 the ultra ones, and a number outside that is a typo rather than a preference. Plus the round-trip and drop-policy behaviour from Task 13 |
| **3. Driving it** | The router started with `corpus.enabled: false` writes **no** `logs/corpus/` at all; started with it true, a real call produces a day folder holding a blob, a 25-column index row, a `manifest`, and — once Task 15 has trained one — a **plain copy** of the dictionary. Stopping the router drains the queue and emits the summary line |

**Layer 3 drives `../../procedures/dying-backend/`, not a real backend.** Settled 2026-08-18. That
stub already exists, was built in Phase 3, is *"meant to be re-run"*, and sits on port 8799 with its
own `router.yaml` so it cannot touch a working router or a real LM Studio. **It is better than real
traffic for this check**, because it can produce the failure cases on demand — a forced drop, an
oversized body — which ordinary traffic will not.

**It still needs its own consent, and so does anything else that runs.** Owner's standing instruction,
2026-08-18: **a session is never driven without approval and without being told why.** That covers the
stub too, because starting it is touching the machine. `CLAUDE.md`: *consent for one is not consent for
the next.*

### The five things Task 18 must actually see

Written as observations rather than as intentions, because *"it should work"* is what a check exists
to replace:

1. **`corpus.enabled: false` leaves no trace** — no directory, no file, and the suite passing with
   the corpus off. *(This said "`make test`'s **158** unchanged" until 2026-08-18. Tasks 11 and 13 add
   tests, so it cannot be 158 by then — and a number nobody re-derives is this repository's stated
   signature failure.)*
2. **A stored body round-trips byte-identically**, decompressed outside the router with the day's own dictionary copy and nothing else.
3. **A day folder is self-contained** — `tar` it, unpack it elsewhere, and every blob in it opens.
4. **A dropped body is a row, not an absence** — force the queue bound low, and see `dropped` in the cell, the `WARNING` once, and the counter afterwards.
5. **`arrived` equals `recorded`** in the summary after a clean shutdown, which is the counter pair doing its one job.

---

## Placeholders in this file

**Written down rather than remembered**, because `../../method/IDM-001-git-branching.md`'s closeout
rule was generalised on 2026-08-17 for exactly this defect: Phase 9 read that document *during* the
phase, obeyed it, and still shipped `*(not started)*` group markers and a stale count. **A rule stated
as an instance gets obeyed as an instance**, so this section names the instances.

| Where | Placeholder | Closed out at |
|---|---|---|
| The header, first line | *"Execution is under way; the group markers … say how far"* | Task 24. *Reworded 2026-08-18: it enumerated tasks, went stale the moment Task 4 ran, and was a second copy of the group markers. It now points at them instead, so there is one place to close out rather than two* |
| **Five** group headings — B, C, D, E, F | `*(not started)*`, and `*(in progress)*` once a group's first task runs — **B carries the second form from 2026-08-18.** Both are matched by the grep below, which is why those two are the only permitted spellings | Task 24, each group as it completes |
| ~~Group **A**'s heading~~ | ~~`*(executed, except 3a)*`~~ | **Closed out 2026-08-18** when Task 3a finished, which is what this row said would close it. *Added earlier the same day: the table said "six" group headings and only five carried the marker, so the uncatalogued sixth was the one form the sweep could not see. Kept struck rather than deleted — a row that vanishes cannot show that the mechanism worked* |
| The Record table below | `Merge commit \| not yet merged` | The merge itself |
| "What is settled" | *"still open questions until Task 20"* | Task 20 |

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
| A byte-bounded queue is necessary because a 1,000-item queue is 200 MB | **Extrapolated** — from Phase 9's measured median request of 103,935 bytes |
| `zstandard`'s dictionary training matches `zstd --train`'s | **Unverified.** Both wrap libzstd, but their *defaults* may differ — and training defaults are exactly where Phase 9 found non-monotonicity. **Task 6 compares them**; if they disagree, Phase 9's figures are not directly comparable and the note says by how much |
| **`zstandard` releases the GIL during compression** | **Measured — Task 4, 2026-08-18.** *(Read **unverified — and it is load-bearing** until then, this file having asserted it as fact in its first version.)* Verified against the **shipped binary** rather than the C source, which the wheel does not carry: `_ZstdCompressor_compress` calls `_PyEval_SaveThread`, then `_ZSTD_compressStream2`, then `_PyEval_RestoreThread` — the `Py_BEGIN_ALLOW_THREADS` pair around the work. 21 functions release it in total, balanced in every one, including `_train_dictionary`. `notes.md` carries the method. **This settles the mechanism, not the scaling** — Task 6 is unchanged and still measures 1 / 2 / 4 threads |
| Single-thread zstd runs at ~2–6 MB/s at level 19, ~350–500 MB/s at level 3 | **Documented only** — published figures for other machines, quoted here to size the problem. **Task 6 re-measures both on this one** |
| Two to five concurrent harnesses is 1–3 calls/second | **Extrapolated** — from two measured sessions at 0.14 and 0.03 calls/s, scaled to the owner's stated target. One laptop, and no session has ever run five harnesses |
| Compression in the worker thread does not slow a *call* | **Unmeasured**, and this phase does not measure it — a thread bounds throughput rather than latency, but that is an argument, not a number. See below |
| ~250 MB a year at an hour a day | **Extrapolated** — from `EPD-003`'s own projection, itself extrapolated from one session |

---

## What this phase does not settle

**Failure mode 3 — "archiving slows a call" — will not be discharged**, and Task 22 says so in
`../implementation-plan.md` rather than letting the table imply otherwise. The scope decided in the
interview has no live session, and **in-process timing is not the same measurement**. What would
settle it: one driven session with capture on against one with it off, comparing `ttfb_ms` and
`duration_ms` over the same work. That is a later phase, or an addendum to this one.

**`record()` has a blind spot, and it is far narrower than this plan first said.** *Corrected
2026-08-18 by the forward review.* A caller that disconnects after the response headers **does** reach
`record()` and **does** get a row: `proxy.py:249` catches `GeneratorExit`, re-raises, and the `finally`
calls `record()`. `../../reference/measurements.md` carries **six `client_disconnect` rows across both
backends**, and the frozen CSV has one with 10,027 response bytes already streamed.

**What remains is a race, not a class of calls**: only if the generator is closed *before its first
`__anext__`* is there no frame to throw into, so nothing runs. **It has never been observed here.**
Named, not fixed, and the counter pair is what would first show it happening.

**Whether the router could run as several processes.** Recorded in `../../backlog.md` rather than
built. The idea's session-distinguishing half is **already solved and measured** — `session_id` and
`agent_id` are header-copied columns, and Phase 9's corpus carries five distinct sessions and ten
subagent rows through one instance. Its throughput half has **one concrete blocker that a reverse
proxy does not touch**: every multi-process form — several instances, `uvicorn --workers N`, or a
process pool — hits the fact that **the recorder's writers are single-process designs.** `calls.csv`
rides `RotatingFileHandler`, whose lock is a thread lock, and two processes rotating one file corrupt
it. So the cheap part is the proxy and the expensive part is the writers.

**Whether a response dictionary pays.** Unmeasured, and Task 15 trains only a request dictionary.

**Whether any of this transfers to interactive use.** The dictionary Task 15 trains comes from a
**headless** corpus whose static preamble is ~28 KB smaller than the frozen interactive one, of which
70 of 73 bodies are Anthropic and whose sessions are short. **All three flatter a dictionary.**

---

## What could go wrong

- ~~**`zstandard` does not release the GIL where it matters**~~, and the worker thread contends with
  the event loop. **Half discharged 2026-08-18 by Task 4: it is released**, around the libzstd call
  itself, in all 21 functions that enter the library. **What survives is not the GIL but the
  scaling** — released is not the same as parallel, and per-call Python overhead, allocation and the
  disk are all still unmeasured, so **Task 6 runs unchanged**. Struck rather than deleted because a
  risk that vanishes cannot show that the check worked. **Task 4 read the source and Task 6 measures
  the scaling** — that is the whole reason Group B exists. *(This bullet said Task 7's smoke test would surface it, which is left over from
  before Group B: Task 7 is a correctness round-trip and says nothing about the GIL. Believed, it
  would let an agent skip the measurement and read a green round-trip as verification — the exact
  failure the second interview was convened to prevent.)*
- **A dictionary trained from `logs/corpus-gate/` is uncommittable**, exactly as the bodies are. It
  stays under `logs/`, which `.gitignore:228` covers, and Task 15 stages with explicit paths rather
  than `git add -A` — the discipline Phase 9 adopted for the same reason.
- **The telemetry move breaks a citation nothing checks.** `link-check.py` globs `*.md` only, so
  `config.yaml`, the `Makefile`, `pyproject.toml` and `src/` are unchecked by it. Task 17 is a reading
  task, not a grep task.
- **Forward citations inflate the link-checker count.** This file names files it will create —
  `reference/corpus.md`, `procedures/corpus-dictionary/`, `src/ilirium_llm_router/corpus.py`. That is
  `../../backlog.md`'s recurring false-positive class, not breakage; Phase 8's plan contributed 23.
  **Task 24 re-derives the count by running the tool** and expects these to have resolved themselves.

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
at Task 24.*
