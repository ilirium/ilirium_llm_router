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
    dicts/                        the durable home. Append-only, never deleted
      req-2026-08-18T104500Z.dict
    2026-08-18/                   UTC-derived, never local
      index.csv                   22 columns: calls.csv's 20, in order, plus two refs
      manifest                    schema version, router version, dictIDs referenced
      dicts/                      hard links into ../dicts/ — portable, and zero bytes
      incoming/                   staging for atomic rename
      requests/3f/3f9c….zst
      responses/b2/b20e….zst
```

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
| **Recording a drop** *(3)* | 22 columns with no way to say a body was dropped | **A ref cell holds a 64-char hex digest, or one of `dropped` / `too_large` / `absent`.** A reason word can never be mistaken for a digest, so this needs no new column |
| **Over the cap** *(4)* | *"the store must be able to hold a truncated body and say that it is truncated"* | **Drop, do not store a prefix.** A prefix labelled as a whole body is worse than a hole. This splits cap-truncation from the case `EPD-003` actually meant — a stream that broke, where the bytes that arrived are all there is and `error_status` already says so. The sketch's *"truncation needs no new column"* survives intact, for the reason it gave |
| **Dictionary placement** *(5)* | copies into each date folder, ~80 MB/year, with *"plain copies against APFS clones"* left open pending the `--maxdict` result | **`os.link()`.** Portable Python, zero bytes, and `tar` of a single day still emits a real file because the link partner is not in the archive. The deferred fork dissolves rather than being decided |
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
  max_body_bytes: 1048576     # over this: not stored, and the cell reads `too_large`
  queue_max_bytes: 67108864   # 64 MiB pending; over it, the cell reads `dropped`
```

`max_body_bytes` **reuses the reasoning** behind `observe.py`'s `MAX_SCAN_BYTES` rather than the
number, which is what `EPD-003` asks for: the catch-all route forwards paths nobody enumerated, so a
body could be any size at all, and the cap turns *memory decided by a stranger* into a known ceiling.

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

**Nothing crosses a process boundary.** The queue item holds *references* to `bytes` that already
exist in memory — the request body read at `begin()`, and the response copy tee'd in `watch()`.
Enqueueing is a pointer, not a copy.

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

**What it deliberately does not measure: processes.** If threads scale, a process pool is an option
we would not take, and measuring it is work spent on a road not travelled. **If the GIL is not
released, that measurement becomes the next step** — conditional rather than speculative.

### Group B — the store *(not started)*

| # | Task |
|---|---|
| **4** | Add `zstandard`; `make sync`; a smoke test that a dicted frame round-trips byte-identically |
| **5** | `src/ilirium_llm_router/corpus.py` — the blob store: content addressing on the plaintext, the per-day layout, `incoming/` → `fsync` → rename, dedup scoped to the day, dictionaries hard-linked into the day folder |
| **6** | The byte-bounded queue and its worker thread — the drop policy, drain on close, and **it never raises**: a body store is telemetry-shaped and telemetry does not get to break a call. **Widened 2026-08-18:** the counters, the once-per-run drop `WARNING`, and the periodic summary line |
| **7** | The day index: header re-emitted in every file, a ref cell holding a digest or a reason word. **Widened 2026-08-18 from 22 columns to 25** — `queue_ms`, `store_ms` and `queue_bytes` appended after the refs, so the first twenty stay identical to `calls.csv`'s and in its order |
| **8** | The `corpus:` config block — `extra="forbid"`, relative-path resolution against the config file's directory, and `--check` prints it |
| **9** | Wire into `Proxy.record()`'s four call sites and `app.py`'s lifespan; hold the request body on `Call`; tee the response into a capped buffer in `watch()` |
| **10** | Tests, including **a non-UTF-8, non-JSON body round-tripping byte-identically** — that is what discharges failure mode 2 by construction rather than by assertion |

### Group C — the dictionary *(not started)*

| # | Task |
|---|---|
| **11** | `docs/procedures/corpus-dictionary/` — the trainer, which **measures a candidate against the incumbent on a held-out slice and refuses to install a worse one.** Directly from `zstd --train` being non-monotonic at 68 samples. With its README saying when re-running is worth it |
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
