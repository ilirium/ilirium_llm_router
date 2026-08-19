# Phase 10 — the body store: plan

**Written 2026-08-18 on `feat/phase-10-body-store`, forked from `main` at `d885b2f`. Execution is
under way; the group markers under "The tasks" say how far, and are the only place that says so.**

*This line read "Group A has executed; Tasks 4 to 24 have not" until 2026-08-18, when Task 4
executed and made it false. **It was a second copy of what the group markers already carry**, and a
second copy is what this repository's own placeholder rule exists to catch — so it was repointed at
them rather than re-enumerated, which would only go stale again at Task 5.*

**Thirty-two tasks in six groups.** *(Twenty-five until 2026-08-19, when the retraining interview added seven lettered ones — `13a` and `14a`–`14f`. Nothing was renumbered; see "The tasks".)* Group A opens the phase and records what the opening interview
decided. Group B benchmarks, before any store code exists. Group C builds the store **and the reader
that gets bodies back out of it**. Group D builds the trainer, **the automatic retraining the router
runs itself**, and the instrument that keeps training honest. Group E moves the telemetry files. Group
F verifies the configuration, harvests, closes out `EPD-003`'s remaining open questions, and merges.

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

**A second block of rows was added 2026-08-19**, from the retraining interview, and it **reverses a
position this file had been stating as settled**. `notes.md` carries that interview in full, including
the rejected alternatives. *(The rows are marked with their date. This section is the only place a
decision's authority is recorded, which is exactly why the 2026-08-19 interview happened at all — see
the row on retraining below.)*

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
| **Who retrains** — *2026-08-19* | **The router, automatically. Not a person.** This **reverses** what this file said: "One thing that is never in a worker" made training an offline procedure run by hand, and that was **never an owner decision** — it was this plan's own prose, absent from this table, and neither forward-review pass questioned it. `../implementation-plan.md` names *"a dictionary bootstrap and retraining policy"* as this phase's to settle; the bootstrap was settled and the policy was not. Manual-only was what a session would have built |
| **When it retrains** — *2026-08-19* | **Measure the training wall clock first, then choose** between startup-only and startup-plus-day-rollover. Committing now was offered and declined, on the grounds Group B exists for: **UTC midnight is an arbitrary local hour**, so a four-minute run is indefensible mid-afternoon and a three-second one makes the question moot. The number decides it |
| **The manual command** — *2026-08-19* | **`--train-dict`, beside `--check`**, and it works **even when automatic retraining is disabled** — typing it is explicit consent. It is also what forced the pickup mechanism below: a manual run is a **separate process**, so an in-process hand-off cannot reach a running router |
| **The window** — *2026-08-19* | **Rolling, `retrain.window_days`, default 1. `0` disables automatic retraining** and the router keeps using the newest dictionary already installed. The owner's encoding **removed** a key: a separate `retrain.enabled` boolean was this session's proposal and `0` makes it redundant |
| **What is trained on** — *2026-08-19* | **Size only, no path filter** — `retrain.sample_min_bytes`, default 1024. **Measured to be a no-op on this corpus**: every request body ≥ 1,024 bytes is already `/v1/messages`, the only other path being `/api/hello` at **0 bytes**. So the published ratios stay exactly comparable. A path filter would also have excluded `count_tokens` requests, which carry the same preamble and are ideal material |
| **Training parameters** — *2026-08-19* | **`retrain.maxdict` (262,144) and `retrain.k` (8,000), both provisional**, both overridable per run by a CLI flag; `d` fixed at **8** as a module constant, so it is a decision rather than an omission. Hard-coding them was declined — the right values depend on the operator's own corpus, which is what `--tune-dict` is for |
| **Config shape** — *2026-08-19* | **A nested `corpus.retrain:` block.** The five write-path keys stay top-level; the four offline settings group beneath. Nine flat keys was the alternative. Nesting is what `backends`, `logging` and `stats` already do, and it separates settings that touch a live call from ones that never do |
| **How a running router picks one up** — *2026-08-19* | **The worker rescans `<dir>/dicts/`** and swaps when the newest differs from what it loaded. An in-process slot was this session's proposal and is **wrong**, because the manual command runs elsewhere. The trainer therefore publishes nothing: it writes a file, and that is the entire interface |
| **Restarting to pick one up** — *2026-08-19* | **Rejected.** A router that restarts itself severs live SSE streams mid-generation; against a local model that is minutes of work destroyed. The swap touches one object between two queue items, a restart touches every open connection |
| **Extraction** — *2026-08-19* | **The reader ships in this phase; the tool built on it is Phase 11's.** Not optional here — training cannot assemble a sample list without decompressing blobs, which is extraction's core path. Deferring all of it was the earlier plan and the owner corrected it |
| **The training level, and the scoring level** — *2026-08-19* | **They are two different things and get two different sources.** Training uses **`TRAIN_LEVEL`, now 3**; scoring uses **`corpus.compress_level_zstd`**, read from config. This **narrows** the training-parameters row above: that decision was right that *scoring* belongs at the level bodies are stored at, and **overreached in binding training to it too**. Measured the same day on `gate.py`'s held-out split — training levels 3, 6, 9, 12 and 19 land within **0.03%** of each other, so the training level is **not a parameter**, while 19 costs 8x the wall clock. **Two alternatives were rejected.** *Keeping 9* — once the two are split, the only argument 9 ever had ("it matches the write path") belongs to scoring, leaving training at a value with nothing behind it, where 3 is the library's own default. *Making both follow `compress_level_zstd`* — simpler-looking, and **refused on a hazard**: all five training levels produce **one dictID**, so a key change would alter dictionary bytes without altering the ID the reader looks them up by. A fixed `TRAIN_LEVEL` keeps that latent |
| **The retry finding** — *2026-08-19* | **No rerun.** `gate.py` trained on **48 bodies, 26 distinct** — 46% repeats, being `overloaded_error` retries — and the owner declined a measurement of the effect, on the ground that these sessions are too short for the numbers to be more than approximate and that they carry enough accuracy to execute against. **Task 21 states the training-set composition in the slice column** instead |

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
      .incoming/                  staging for atomic install — a trainer never writes in place
      req-2026-08-18T104500Z-a3f91c2b.dict      name carries the UTC stamp AND the dictID
    2026-08-18/                   UTC-derived, never local. SELF-CONTAINED
      index.csv                   26 columns: calls.csv's 20, in order, two refs, three timings, dictID
      manifest                    the index's schema version, and nothing else
      dicts/                      plain copies of every dictionary this day used — PLURAL, and
                                  routinely so once a retrain can install one mid-day
        req-2026-08-18T104500Z-a3f91c2b.dict     copied from ../../dicts/ at first use
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
router reads the newest from there, and copies whichever it used into each day folder it opens.

*Amended 2026-08-19, in two places this said too little.* **"The newest" is by filename, never by
mtime** — `logs/` sits inside a cloud-synced folder here and mtime is not trustworthy, which is why the
name leads with a UTC stamp. And **"at startup" is now "at startup and on rescan"**: the worker relists
this folder when it opens a day and every N bodies, so a dictionary installed by a **separate process**
— which is what `--train-dict` is — reaches a router that is already running. The trainer therefore
publishes nothing but a file; **the file is the whole interface**, and that is what lets one mechanism
serve both the automatic and the manual path.

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
  compress_level_zstd: 9      # the zstd level the write path uses -- AND the level the trainer scores
                              # a candidate dictionary against the incumbent at, so the comparison
                              # cannot drift from what is actually stored (2026-08-19). It does NOT
                              # set the level a dictionary is TRAINED at; that is TRAIN_LEVEL = 3,
                              # measured to move the ratio by 0.03%. MEASURED by Task 6, 2026-08-18:
                              # 94% of level 19's dicted ratio for an eighth of the per-body cost,
                              # and ~500x the target peak load on one worker
  max_body_bytes: 1048576     # one body bigger than this is not stored: `too_large`
  queue_max_bytes: 67108864   # total bytes waiting to be written; over it: `dropped`
  retrain:                    # OFFLINE ONLY. Nothing under here touches a live call
    window_days: 1            # complete days of material to train from. 0 DISABLES automatic
                              # retraining; the newest installed dictionary keeps being used
    sample_min_bytes: 1024    # a body smaller than this is not a training sample. No path filter:
                              # measured 2026-08-19, every request body at or above this size in
                              # the whole corpus is already `/v1/messages`
    maxdict: 262144           # PROVISIONAL, not measured-optimal — Task 6's best, chosen with
    k: 8000                   # knowledge of the slice it was scored on. `--tune-dict` re-derives
                              # both against the operator's own corpus
```

**The nesting is the point, not decoration.** *Chosen 2026-08-19 over nine flat keys.* Everything
under `retrain:` runs **offline, in its own thread, and never in the path of a call**; everything above
it is spent per body. That is a real boundary and the flat form hides it behind a name prefix. It is
also what `backends`, `logging` and `stats` already do.

**All four `retrain` values take a CLI flag on the trainer**, and the flag wins for that one run. The
config is what automatic retraining uses; the flags are for experiments, which are run by hand.

### The constants beside it, and why they are not keys

*Added 2026-08-19 from the second forward review, which found three of these named in the plan and
given no value anywhere.* **Module constants, on the precedent the shutdown timeout already set** —
owner's decision, the same day. Configuration this project does not need is configuration it does not
get, and none of these is a number an operator would know how to choose.

**The complete list of every constant, key and name is "The register" below**; this table carries the
six whose *reason for not being a config key* needed arguing. *(Pointer added 2026-08-19 with the
register. The register is authoritative for the value, this table for the why — so a number is changed
there.)*

| Constant | Value | What it is |
|---|---|---|
| `TRAIN_LEVEL` | **3** | The zstd level used to **train** a dictionary, and **nothing else**. *(Was 9 and also did the scoring, until 2026-08-19 — see below.)* **Scoring is not a constant**: it reads `corpus.compress_level_zstd` |
| `TRAIN_D` | 8 | COVER's dmer size. Task 6 used it throughout and never varied it |
| `INSTALL_MARGIN` | **2%** | A candidate must beat the incumbent by more than this to be installed |
| `RESCAN_EVERY` | 500 bodies | How often the worker relists `<dir>/dicts/`. Matches the summary line's cadence, so the worker has one periodic rhythm rather than two |
| `TRAIN_BUDGET_S` | **60** | Above this, training is **startup-only**; at or below it, startup **and** day-rollover. Task 14a measures and applies it |
| `WINDOW_MAX_DAYS` | 30 | The cap on widening the window in search of a second session; see below |

**The level is a correction, and it is the one the review called silent.** *Found 2026-08-19.*
`train_dictionary` takes a `level` that changes **which dictionary you get**, and `zstandard` defaults
it to **3** when `steps` and `threads` are unset — `backend_cffi.py:2860`, `level = level or 3`.
Task 6 produced **13.65x** by passing `level=19` explicitly (`evidence/benchmark.py:355`). The config
block shipped `maxdict` and `k` and **never mentioned `level`**, so an executor would have trained at
3 and shipped a dictionary documented as 13.65x that is not — with nothing detecting it, and Task 21's
register row wrong.

**That correction was right about scoring and overreached to training, and the second half was undone
the same day.** *Amended 2026-08-19, after compiling "The register" below.* It concluded *"train and
score at the level bodies are actually stored at"* and made **one** constant do both — but the two are
independent knobs. **Scoring at the write level is sound**, and it is the question that matters:
*which dictionary compresses better in production*. **Training at the write level answers no question
at all** — a dictionary trained at 3 is perfectly valid for archives written at 9, and nothing binds
one to the other.

**So the constant was split, and each half went to its proper source.** Scoring reads
`corpus.compress_level_zstd`, because a constant that merely *equals* the key today is a coincidence
that breaks the moment an operator edits it — the scoring level would silently stop being the level
anything writes at, falsifying the sentence the whole decision rests on. **Training keeps a constant,
now 3**, on a measurement rather than on an argument: across levels 3, 6, 9, 12 and 19 the held-out
ratio moves by **0.03%**, two orders of magnitude below `INSTALL_MARGIN` — so a change to
`TRAIN_LEVEL` alone can never install a dictionary, and the choice is **self-limiting**. `notes.md`
carries the table.

**Pass it explicitly even so.** Relying on `level = level or 3` means relying on a branch that fires
only when `steps` **and** `threads` are both unset, and that same branch quietly sets `steps = 4`.
The discipline is the one `k` already earned: **pass the parameter, do not inherit it.**

**The cost is named and the split does not change it:** `13.65x` is no longer the reproducible figure,
because it was measured at **write** level 19. **Task 15 records the level-9 ratio it actually gets** —
measured 2026-08-19 at **12.920x** on the provisional `maxdict`/`k`, which is where it should land —
and Task 21 carries **both** levels in the slice column, since one number now has two of them.

**`INSTALL_MARGIN = 2%` is provisional and says so.** There is no data to choose it from: the frozen
sweep shows neighbouring parameter choices differing by −15% to +14%, so anything from 1% to 10% is
arguable. 2% is above run-to-run noise and below every real improvement the sweep found. **It is
revisited against real installs, not against arithmetic** — the same footing as the storage figure.

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

**There is deliberately no `workers` key.** One worker — **settled by Task 6 on 2026-08-18**, which measured ~2,930 bodies/s against a target peak of 1–3 calls a second. *(This read "until Task 6 says otherwise" until 2026-08-19, after Task 6 had already said it; the second review caught it as a leftover inside a section rewritten that day.)*

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

### The retraining path, concretely

*Added 2026-08-19 from the retraining interview. `notes.md` carries the reasoning and the rejected
alternatives; this is the specification.*

**Training runs in the router, automatically, in a thread of its own.** Not on the event loop, not on
the corpus worker, and not in another process.

```
   day folder rolls over  ──┐
   (worker notices)         ├──►  start training thread   ──►  writes a file into <dir>/dicts/
   startup (lifespan)     ──┘        (single-flight)                        │
                                                                            │
   worker, on day open and every N bodies:  list <dir>/dicts/  ◄─────────────┘
        newest differs from what is loaded?
             └─ copy it into <today>/dicts/  →  build compressor  →  swap
```

**The trainer publishes nothing.** It writes a file, and that is the entire interface between the two
threads — which is what lets `--train-dict` in a **separate process** be picked up by exactly the same
mechanism. An in-process hand-off cannot do that, and the manual command is what proved it.

**The swap ordering is an invariant, not a preference: the dictionary is in the day folder before any
blob referencing it is written there.** Reversed, a crash between the two steps leaves a day holding a
blob whose dictID names a dictionary that is not in that folder — self-containment broken, and broken
silently.

**It is a per-write precondition, not a per-swap step.** *Corrected 2026-08-19 from the second review.*
Stated as "copy into `<today>/dicts/` at the moment of the swap", it is wrong across a rollover: this
plan's own risk list records that a body submitted at 23:59:59 and written at 00:00:02 belongs to
**yesterday**, so one worker can be writing into two day folders while holding one compressor. The
rule is therefore **whichever day folder this blob is going into must already hold this dictionary** —
checked per write, cheap because it is a set membership test after the first time. **Task 18's
observation 7 cannot catch the rollover case**, since it exercises a swap within one day.

| Step | Rule |
|---|---|
| **Enabled** | **`corpus.enabled` must be true.** No thread starts otherwise, and nothing under `<dir>/` is created — Task 18's observation 1 is *"leaves no trace: no directory, no file"*, and a trainer that makes `<dir>/dicts/.incoming/` breaks it. `retrain.window_days: 0` is the second, independent off switch |
| **Trigger** | Startup, **and** day-rollover if the measured training time is at or under **`TRAIN_BUDGET_S` (60 s)**. Above it, startup only. *Task 14a measures and applies the constant; it does not choose a policy* |
| **Guard** | A dictionary **or a retrain-log line** dated today ⇒ stop. **Refusals are recorded too**, or a candidate that loses is retrained from identical input on every restart, forever, for a verdict that cannot change. **`--train-dict` bypasses this guard** — see below |
| **The retrain log** | **`<dir>/retrain.log`**, one line per attempt: UTC timestamp, window, sample count, candidate ratio, incumbent ratio, **the scoring level**, verdict. *(The level was added 2026-08-19 when scoring moved to `compress_level_zstd`: it is now operator-editable, so two ratios logged on different days are not comparable unless the line says what they were scored at.)* *Its home was chosen against two collisions the review found: `<dir>/dicts/` would be relisted by the pickup, and a day folder would make training state something a day needs — so it sits beside them, at the corpus root. **Nothing reads it to read a day**, which is the direction the self-containment rule actually forbids* |
| **Single-flight** | One training run at a time **across processes**, not merely across threads — `--train-dict` is deliberately another process. An exclusive lock on `<dir>/retrain.lock`, released on exit; a stale lock from a killed process is broken by age |
| **Material** | The newest **complete** day folders — `retrain.window_days` is a **minimum, not a fixed count**. Blobs read from `<day>/requests/`, decompressed through Task 13a's reader, which finds each day's dictionary by the frame's own dictID |
| **Widening** | **Keep adding older complete days until the window holds at least two sessions**, up to `WINDOW_MAX_DAYS` (30). *Owner's decision 2026-08-19, and it exists because the split below cannot run otherwise: `run-02` and `run-03` each carry **exactly one session**, and one harness on one laptop — the stated target — produces single-session days as the ordinary case* |
| **Floor** | Below a viable sample count, or with **no complete day at all**, it does not train: one `INFO` line and a retrain-log entry. **A fresh install therefore trains nothing on its first day**, which is correct — the store writes undicted frames meanwhile, at ~3.12x, and they stay valid forever |
| **Sampling** | Plaintext length ≥ `retrain.sample_min_bytes`. **No dedup step is needed within one day** — content addressing means the store holds one blob per distinct body. Across a widened window duplicates return, and there the filename *is* the digest, so it costs one `set()` |
| **Split** | Leave-one-session-out, **held-out slice from the newest day**, holding out its largest session. `session_id` is index column 2; membership is not in the blob store, so the index is read for the split even though sampling does not need it |
| **Compare** | Candidate and incumbent both compressed at **`corpus.compress_level_zstd`** — read from config, **not `TRAIN_LEVEL`**, so the comparison cannot drift from the level the write path actually stores at. Install only on a win exceeding **`INSTALL_MARGIN`**. **With no incumbent, any candidate that trains is installed** — the ordinary first case, since Group C ships before Group D |
| **Install** | `<dir>/dicts/.incoming/<pid>-<uuid>.tmp` → fsync → rename to `req-<UTC>-<dictID>.dict`. **The tmp name is unique per run**, so two processes cannot rename interleaved bytes into one valid-looking file |
| **Never** | Raises into a call. Telemetry-shaped: it logs and dies quietly |

**`.incoming/` is swept at startup**, both the dictionary staging directory and each day's. *Added
2026-08-19: the plan claimed a killed run "leaves no trace", and that is only true of the **installed**
path — a daemon thread killed between write and rename leaves its partial file behind, and no task
owned cleaning it up.*

**Shutdown needs no drain.** Because the install is atomic, a run killed mid-flight publishes
**nothing** — no half-written dictionary is ever visible under a name the router would load. **That is
a different rule from the corpus worker**, which drains with a timeout because it is holding bodies
that would otherwise be lost, and the difference is deliberate.

*Corrected 2026-08-19: this read "leaves no trace", which is false. It leaves a partial file in
`.incoming/`; what it leaves is merely **harmless and invisible to readers**. The sweep above is what
makes the stronger sentence true.*

#### Why the obvious comparison inverts the rule it implements

**Train on a day and score on that same day, and the candidate always wins** — it has seen those
bodies and the incumbent has not. That does not weaken the refuse-a-worse-one rule, it **reverses**
it: a worse dictionary is installed daily while every run logs an improvement.

**A rolling window produces the opposite bias.** Yesterday's incumbent trained on days N-8…N-2, so a
slice drawn from inside the window is material the *incumbent* has seen — now the comparison flatters
the incumbent and refuses good candidates forever.

**So the held-out slice comes from the newest complete day only.** It is the sole material the
incumbent certainly has not seen, and the candidate excludes it by construction. **At the default of
one day this is the clean case**, the window and the newest day being the same thing.

#### It does not pause the router, for three reasons that fail differently

1. **Nothing awaits it.** No coroutine on the event loop waits for training, so no request blocks behind it. This is the one that matters.
2. **The GIL is released during the heavy work** — Task 4 read that off the shipped binary for `_train_dictionary` and `_Decompressor_decompress` alike, and the blobs have to be decompressed to be sampled.
3. **CPU contention is still real.** A released GIL is not a free core. **That is why the wall clock is measured before the trigger is chosen** — UTC midnight is an arbitrary local hour.

**And the three async-shaped answers are all wrong**, checked in the installed packages on 2026-08-19
rather than recalled: `BackgroundTask` (`starlette/background.py:12`) is `await`ed inside a request's
ASGI cycle and is per-request; `run_in_threadpool` (`starlette/concurrency.py:31`) delegates to the
shared `anyio.to_thread` pool that every sync offload uses; and **`asyncio.create_task` is the one
that would genuinely pause the router**, CPU-bound work on the loop blocking every concurrent request
— and it is the most tempting, because it looks async-native. `lifespan` is not a background
mechanism at all, but it is the right **place** to start one.

### One thing that is never in *the* worker

**Dictionary training.** It runs over thousands of samples and takes seconds to minutes. Compression
and writing are the corpus worker's; **training gets its own thread**, and keeping it off the worker
is what lets the write path stay small.

*Corrected 2026-08-19, and the correction is larger than the heading suggests. This section read
"never in a worker" and said training "belongs to an offline procedure the router never calls" — **the
second half is now false.** The router does call it, automatically, from a thread of its own; see "Who
retrains" above. What survives is the part that was actually load-bearing: **training never runs on
the corpus worker**, because that thread is what stands between a body and the disk.*

*The stated reason was wrong twice over. Task 4 established that `_train_dictionary` **releases the
GIL**, so "it would freeze the interpreter" was never a reason to keep training out of the process —
duration and memory are. And the sentence's real defect was one of authority rather than fact: it read
as a settled decision while appearing nowhere in "What is settled, and by whom", and **two forward
review passes inherited it without asking whose it was.**

---

## The tasks

**Thirty-two tasks in six groups. Groups A and B have executed; nothing after them has.** Every later group is
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
### Group B — the benchmark, before any store code *(executed)*

**All three tasks ran on 2026-08-18** and the group is closed. Its numbers are in `notes.md` and
frozen in `evidence/`. **What it decided:** the GIL is released and the thread design stands, so the
negative branch was not taken; `compress_level_zstd` defaults to **9**; there is **no `corpus.workers`
key**; and `zstandard`'s trainer must set `k` explicitly, which is a new constraint on Task 14.

*While the group was mid-flight this heading read `*(in progress)*`, with the detail outside the
parenthesis on purpose — `*(in progress — Task 4 done)*` would not match the prescribed grep's
`\(in progress\)`, which is the same defect as Group A's uncatalogued marker and the `is not started`
sweep that returned clean. **The parenthesis stays exactly greppable; the prose carries the state.***

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

> **Reconciled 2026-08-18, and it is the first sentence that gives way. There is no `corpus.workers`
> key.** The GIL *is* released — 3.34x at four threads — so the condition's first half is met. Its
> second half is not: one worker at level 9 runs ~2,930 bodies/s against a target peak of 1–3 calls a
> second, so **a second worker helps with nothing that needs helping.** Task 11 stays at five keys,
> unchanged. Adding the knob would be configuration this project does not need, against the
> non-negotiable that configuration stays simple.

> **Amended 2026-08-19. "Task 11 stays at five keys" is now false, and `corpus.workers` still does not
> exist.** The retraining interview added **four** settings — `window_days`, `sample_min_bytes`,
> `maxdict`, `k` — under a nested `retrain:` block, taking the block from five to **nine**. *(This
> session first proposed a fifth, a `retrain.enabled` boolean; the owner's `window_days: 0` encoding
> made it redundant and it was dropped.)*
>
> **The reasoning above is not weakened by this and the distinction is worth keeping.**
> `corpus.workers` was refused because it is a knob **nobody would ever need to turn** — one worker
> already carries ~500x the target peak, measured. The four new settings are the opposite case: their
> right values **depend on the operator's own corpus** and are not knowable from here, which is the
> same ground on which `compress_level_zstd` became a key rather than a constant. **Simple
> configuration means no knob without a question behind it, not the fewest possible keys.**
>
> **And none of the four touches the write path.** That is what the nesting says: everything under
> `retrain:` runs offline in its own thread, and a reader tuning a live call never has to look at it.

### Group C — the store *(not started)*

| # | Task |
|---|---|
| **7** | **The smoke test only** — that a dicted frame round-trips byte-identically. **`zstandard` was already added at Task 4**, which is what `uv add` does; this task adds no dependency. *(It read "Add `zstandard` to `pyproject.toml`; `make sync`" until 2026-08-18 — true before Group B existed, and afterwards a cold agent would find the work done and be unable to tell which task was stale.)* |
| **8** | `src/ilirium_llm_router/corpus.py` — the blob store: content addressing on the plaintext, the per-day layout, `incoming/` → `fsync` → rename, dedup scoped to the day, **the `manifest` written once when a day folder opens, carrying the index's schema version and its column count** *(the count added 2026-08-19, when the index went from 25 columns to 26 and nothing said the manifest moved with it)*, and **a plain copy into `<day>/dicts/` of each dictionary the day uses, taken from `<dir>/dicts/`**. **It must work with `<dir>/dicts/` empty**, writing undicted frames. **And `write_dict_id` must be on, asserted rather than assumed** — *added 2026-08-19*: `ZstdCompressor` defaults it true, but `ZstdCompressionParameters` defaults it to **0** (`backend_cffi.py:414`) and the two are mutually exclusive, so reaching for the tuning path silently stops frames naming their dictionary and makes every blob after it unreadable by Task 13a. The whole design rests on that field |
| **9** | The byte-bounded queue and its worker thread, **plus the arrived/recorded counter pair** — one `queue.SimpleQueue` with the byte accounting beside it, the drop policy, the timed drain on close, and **it never raises**: a body store is telemetry-shaped and telemetry does not get to break a call. Plus the once-per-run drop `WARNING` and the periodic summary line |
| **10** | The day index: **26 columns**, header re-emitted in every file, the two ref cells named **`request_ref`** and **`response_ref`**, each holding a digest or one of `dropped` / `too_large` / `absent` / `error`. *(Named 2026-08-19: they were "two refs" everywhere and never a header string, and the header is re-emitted in every day file, so a rename after any real capture would split the corpus.)* `queue_ms`, `store_ms` and `queue_bytes` are appended after the refs, so the first twenty stay identical to `calls.csv`'s and in its order — then **`request_dict_id`**, added 2026-08-19 *(see below)* |
| **11** | **The whole `corpus:` config block, and the only task that builds it** — **nine settings: five top-level and four under a nested `retrain:`**, `extra="forbid"` on **both** models, relative-path resolution against the config file's directory, and `--check` prints it. Neither limit may be disabled. `retrain.window_days` accepts **0**, which disables automatic retraining and is the one "off" value in the block |
| **12** | Wire into `Proxy.record()`'s four call sites and `app.py`'s lifespan; hold the request body **and the response buffer** on `Call`, which is `observe.py`'s and is therefore an in-scope edit; tee the response in `watch()` up to `max_body_bytes`. **Plus the arrived/recorded counters, which live in `Proxy` and run whether or not the corpus is enabled.** `create_app` takes the writer the way it already takes `stats`, so a test can point one at a temporary path |
| **13** | Tests, including **a non-UTF-8, non-JSON body round-tripping byte-identically** — that is what discharges failure mode 2 by construction rather than by assertion |
| **13a** | **The reader, in `src/ilirium_llm_router/corpus.py` beside the store** — blob plus the day's `dicts/` → plaintext, finding the dictionary by the frame's own dictID, and **verifying as it reads**: the blob's filename *is* the sha256 of the plaintext, so every read is a free integrity check. **Not optional and not deferrable to Phase 11** — Task 14a's trainer cannot assemble a sample list without it. Plus a minimal `--extract`, which is what makes Task 18's layer-3 check repeatable rather than a snippet written once |

**The 26th column, and why it is not empty when a body is stored undicted.** *Added 2026-08-19.*
`request_dict_id` holds the 8-character hex dictID, or the word **`none`** when the request was stored
with no dictionary, or **empty** when no request body was stored at all — `dropped`, `too_large`,
`absent` or `error`. It reuses the ref cell's own trick: **a word can never be mistaken for a
digest.**

**Writing `0` there would have been the natural mistake**, because libzstd's "no dictionary" genuinely
*is* dictID 0 — and `../../reference/observability.md` forbids it: *an absent value is an empty cell,
never a zero.* An undicted body is not an absent one, so it gets a word.

**One column, not two.** Responses are undicted by design, so a `response_dict_id` would read `none`
on every row forever. It is added the day responses get a dictionary, which is now a `../../backlog.md`
item.

**It exists because a mid-day swap made the question routine.** While a dictionary changed rarely,
"which bodies used the old one" was worth opening a blob for. With automatic retraining installing one
inside a running day, it is an ordinary analysis question and the index should answer it.

### Group D — the dictionary *(not started)*

| # | Task |
|---|---|
| **14** | **The trainer, in `src/ilirium_llm_router/dictionary.py`** — its own module, because the store and the trainer share only the reader — `zstandard` rather than the binary, **the refusal mechanism** — it measures a candidate against the incumbent and will not install a worse one. *(The **split and the margin** that mechanism uses are Task 14b's; this task builds the machinery, not the rule. Narrowed 2026-08-19, the second review having found both tasks claiming the comparison.)* Directly from `zstd --train` being non-monotonic at 68 samples. **It must set `k` explicitly** — *added 2026-08-18 from Task 6*: `zstandard` uses COVER and its own choice of `k` is up to **15% worse** than `zstd --train`, while `k=8000` is **13% better**. The library's optimiser is a trap at this sample count, and nothing said so before the measurement. **It records its own wall clock**, which Task 14a then needs. *(Amended 2026-08-19: this task read `docs/procedures/corpus-dictionary/` — the trainer must live in `src/` because the router now calls it, and `docs/procedures/` is the documentation tier. **There is no `docs/procedures/corpus-dictionary/`** — owner's decision 2026-08-19: `--train-dict` and `--tune-dict` live on the router's own CLI and are documented in `../../reference/corpus.md` at Task 19, so a procedure folder would be a third place describing one command. *This row previously said the procedure "keeps its row" in `../../procedures/README.md`; there was no row and no folder to keep.)* |
| **14a** | **The trigger and the training thread** — `threading.Thread(daemon=True)`, started from `app.py`'s lifespan and, if the measurement permits, from the worker's day-rollover path. Single-flight; the today-guard including the **attempt record** so a refusal is not retried from identical input forever; window collection and blob decompression through Task 13a's reader; the sample floor. **It never raises into a call.** **Its first act is to measure the training wall clock**, log it, and **apply `TRAIN_BUDGET_S`**: at or under 60 s it registers both triggers, above it registers startup only. *The threshold is the owner's, set 2026-08-19, so this task applies a rule rather than choosing a policy — the second review found it holding a gate with no branch instruction, which is the defect the first review had already fixed once in Task 6.* **Say so out loud if the measured time lands near the budget**, since the widening rule above is what would push it there |
| **14b** | **The split and the margin** — leave-one-session-out holding out the **largest session of the newest complete day**, **scoring both dictionaries at `corpus.compress_level_zstd`** — the config key, *not* `TRAIN_LEVEL`, which trains only *(narrowed 2026-08-19)* — installing on a win above `INSTALL_MARGIN`, and **installing unconditionally when there is no incumbent**. Plus the widening rule: keep adding complete days until two sessions are present, capped at `WINDOW_MAX_DAYS`. Both biases are live and they run in opposite directions: scoring on the training day guarantees the candidate wins, and scoring anywhere inside a rolling window guarantees the incumbent does. Session membership comes from the index; sampling does not need it |
| **14c** | **The pickup** — the worker rescans `<dir>/dicts/` on opening a day folder and every N bodies, and swaps when the newest name differs from what it loaded. **Ordering is the invariant: copy into the day folder, then build the compressor, then swap.** Newest is by **filename**, never mtime — `logs/` sits in a cloud-synced folder here. One `listdir` per N bodies, in the worker, off the request path |
| ~~**14d**~~ | ~~The config~~ — **struck 2026-08-19 and absorbed into Task 11**, which already specified every clause of it: the nested block, `extra="forbid"` on both models, `--check` printing it, and `window_days: 0`. *The second review found two tasks owning one deliverable, with Task 11 executing first — so a reader would build nine keys at 11 and find 14d empty. **The letter is spent and not reused**, per `../../README.md`; a struck row shows the mechanism worked where a deleted one cannot* |
| **14e** | **`--train-dict` and `--tune-dict`** — the manual command with a flag per `retrain` setting, flag winning over config for that one run, **working even when `window_days` is 0**, and **bypassing the once-a-day guard** — owner's decision 2026-08-19: typing the command is explicit consent to retrain, **but it does not bypass the margin**, so a hand-run cannot install a dictionary that loses. Plus **`--from <dir>`**, without which Task 15 cannot use this tool at all: it trains from `logs/corpus-gate/`, which has no day folders and is not a `corpus.dir`. `--tune-dict` sweeps `maxdict` × `k`, **prints the whole surface rather than the winner** (non-monotonic on both trainers), **labels its own output provisional** (no usable validation split), and **never installs.** It is a mode of the trainer, not a second instrument — Task 6 already found what happens when two things that should agree do not |
| **14f** | Tests for all of the above, including **a swap mid-day leaving every blob in that day folder readable from the folder alone**, **the same across a day rollover** — the case a mid-day test cannot reach — and **an assertion that every frame written carries a dictID**, which is the field the reader and the whole no-recompression rule depend on |
| **15** | Train the first real dictionary from the surviving `logs/corpus-gate/` corpus; **install it into `logs/corpus/dicts/`**; verify a dicted round-trip end to end and record the ratio. **Name which `maxdict` was chosen and why** — `logs/corpus-gate/dicts/` holds eight, and `../../reference/measurements.md` records training as non-monotonic at this sample count. **Task 6's best is `maxdict=262,144` at `k=8000` (13.65x), with 524 KB and 1 MB matching it on a larger file — but it is provisional, not a recommendation:** the corpus has **no usable validation split** (run-02 contributes two qualifying bodies), so that `k` was chosen with knowledge of the test slice. Either hold out by *session* rather than by run — the corpus carries five — or **name the choice as provisional.** Do not present it as measured-optimal. *(Added 2026-08-19: those two values are now the **defaults of `retrain.maxdict` and `retrain.k`**, so "provisional" is a property of the shipped configuration and not only of this task's write-up. And **the training set behind them was 48 bodies, 26 distinct** — 46% `overloaded_error` retries, which `gate.py` did not deduplicate and nobody had noticed.)* |

**Seven lettered insertions, and the letters are the rule rather than an exception.** *Added 2026-08-19.*
`13a` and `14a`–`14f` carry letters because **execution has begun** — Tasks 1 to 6 have run, and
`../../README.md`'s rule that a task number is never renumbered applies with no exception left. The
one exception this phase holds was spent before anything executed, and Group B's own note says so.
**Renumbering now would shift every task this file, `notes.md`, `review-charter.md` and
`../../status.md` already cite**, which is the cost the rule exists to avoid.

**Group D is where they land, and not Group C, deliberately.** `13a`'s reader is the exception, and it
sits in Group C because **Group C ships before Group D** and the reader is what Group D's trainer
depends on — a dependency cannot be scheduled after the thing that needs it.

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
| **24** | Close out: `notes.md`'s "Verified by"; **"The register" checked row by row against the code, every ❓ closed or carried forward with a reason**; the **widened** placeholder sweep; `make test`; `link-check.py` **run, not predicted**; merge `--no-ff` with the message from a temp file; the hash into `notes.md` **and** this file's Record table |

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
| `corpus.compress_level_zstd` | **new.** The zstd level the write path uses, **and the level the trainer scores candidate against incumbent at** *(2026-08-19)*. Not the training level — that is `TRAIN_LEVEL`. Default measured by Task 6 | added |
| `corpus.max_body_bytes` | **new.** One body larger than this is not stored | added |
| `corpus.queue_max_bytes` | **new.** Total bytes waiting to be written | added |
| `corpus.retrain.window_days` | **new, 2026-08-19.** Complete days of material to train from; **`0` disables automatic retraining** | added |
| `corpus.retrain.sample_min_bytes` | **new, 2026-08-19.** A body below this is not a training sample. No path filter | added |
| `corpus.retrain.maxdict` | **new, 2026-08-19.** Dictionary size cap. Default **provisional** | added |
| `corpus.retrain.k` | **new, 2026-08-19.** COVER segment size. Default **provisional**; the library's own optimiser is a trap at this sample count | added |

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
| **2. `make test`** | Rejections are refusals rather than warnings: an unknown key under `corpus:`, `enabled` non-boolean, either limit at zero or negative, `compress_level_zstd` outside **1–22**, hardcoded as a pydantic bound. Owner's decision 2026-08-18: *hard-code it; no need to parse another library*. It is a sanity check, not a contract with libzstd — 1–19 are the ordinary levels and 20–22 the ultra ones, and a number outside that is a typo rather than a preference. Plus the round-trip and drop-policy behaviour from Task 13. **And, from 2026-08-19:** an unknown key under `corpus.retrain:` — `extra="forbid"` has to be on the nested model too, or the whole block silently accepts typos — `window_days` negative, `sample_min_bytes` below 1, `maxdict` or `k` at zero or negative. **`window_days: 0` is the one value in the block that must be *accepted*,** since it is how automatic retraining is switched off |
| **3. Driving it** | The router started with `corpus.enabled: false` writes **no** `logs/corpus/` at all; started with it true, a real call produces a day folder holding a blob, a **26-column** index row, a `manifest`, and — once Task 15 has trained one — a **plain copy** of the dictionary. Stopping the router drains the queue and emits the summary line |

**Layer 3 drives `../../procedures/dying-backend/`, not a real backend.** Settled 2026-08-18. That
stub already exists, was built in Phase 3, is *"meant to be re-run"*, and sits on port 8799 with its
own `router.yaml` so it cannot touch a working router or a real LM Studio. **It is better than real
traffic for this check**, because it can produce the failure cases on demand — a forced drop, an
oversized body — which ordinary traffic will not.

**It still needs its own consent, and so does anything else that runs.** Owner's standing instruction,
2026-08-18: **a session is never driven without approval and without being told why.** That covers the
stub too, because starting it is touching the machine. `CLAUDE.md`: *consent for one is not consent for
the next.*

### The ten things Task 18 must actually see

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
6. **A dictionary installed while the router is running is picked up without a restart** — write one into `<dir>/dicts/` with `--train-dict` from a second terminal, and see the next bodies compressed against it. *Added 2026-08-19, and **runnable only because the manual command bypasses the once-a-day guard** — the second review found this check asking for something the trainer was designed to refuse.*
7. **A day folder that saw a mid-day swap still opens from itself alone** — two dictionaries in its `dicts/`, blobs referencing both, and `tar`-and-unpack-elsewhere still reads every one. This is what the copy-before-swap ordering exists for, and it is the only observation that can catch that ordering being wrong.
8. **`retrain.window_days: 0` trains nothing** — no thread, no retrain-log line, no new dictionary, and the router still using the newest one already installed.
9. **`corpus.enabled: false` starts no trainer either** — the stronger form of observation 1, and a separate switch from the one above. No `<dir>/`, no `dicts/`, no `.incoming/`, nothing.
10. **A rollover with a swap in it still opens** — the case observation 7 cannot reach. Force a day boundary while a new dictionary installs, and check that the blob written into **yesterday's** folder afterwards has its dictionary beside it there.

*The list was five until 2026-08-19. Items 6 to 8 are the retraining interview's, and item 7 is the
one worth insisting on: **the swap ordering fails silently.** Get it backwards and everything works
until a crash lands between two steps, after which one day folder holds a blob whose dictID names a
dictionary that is not in it — and nothing reports that until somebody tries to read it back.*

---

## The register — every name and number this phase introduces

*Added 2026-08-19, on the owner's instruction: **one reachable section holding every constant, magic
number and new name the phase would implement, so they can be checked against the code when the phase
is ready.** Task 24 checks it, and Task 18 already checks the configuration half.*

**This section is authoritative for the *value*; the prose above is authoritative for the *why*.**
That split is deliberate and the risk in it is named rather than hidden: six of the constants below
also appear in "The constants beside it, and why they are not keys", so **a value changed in one place
and not the other is drift this repository has been bitten by before.** The rule is therefore —
**change the number here, and the prose above keeps only the reason.**

**Rows marked ❓ are named by this plan and given no value anywhere.** They were found by compiling
this register, which is the first time anything enumerated them; see "What is not yet decided" at the
end.

### 1 · New modules

| Module | Holds | Task |
|---|---|---|
| `src/ilirium_llm_router/corpus.py` | The blob store, the byte-bounded queue and its worker, the day index, **and the reader** | 8, 9, 10, 13a |
| `src/ilirium_llm_router/dictionary.py` | The trainer, the training thread, the split, the margin | 14, 14a, 14b |

**Two modules, not one or three.** The store and the trainer share only the reader, which is why the
reader lives with the store and the trainer imports it.

### 2 · Configuration — nine keys

**`Corpus(Strict)` and `Retrain(Strict)`**, following `config.py`'s existing one-class-per-block shape
(`Server`, `Logging`, `Stats`). **`extra="forbid"` comes from `Strict` and must be on both**, or the
nested block silently accepts typos.

| Key | Type | Default | Bound | Built by |
|---|---|---|---|---|
| `corpus.enabled` | `bool` | `false` | must be boolean | 11 |
| `corpus.dir` | `Path` | `logs/corpus` | resolved against the **config file's** directory | 11 |
| `corpus.compress_level_zstd` | `int` | **9** | `ge=1, le=22`, **hardcoded** | 11 |
| | | | *also the **scoring** level the trainer compares at — the one key read by both the write path and `dictionary.py`* | 14b |
| `corpus.max_body_bytes` | `int` | **1_048_576** (1 MiB) | `gt=0` — **not disableable** | 11 |
| `corpus.queue_max_bytes` | `int` | **67_108_864** (64 MiB) | `gt=0` — **not disableable** | 11 |
| `corpus.retrain.window_days` | `int` | **1** | `ge=0`; **`0` disables automatic retraining** and is the one "off" value in the block | 11 |
| `corpus.retrain.sample_min_bytes` | `int` | **1024** | `ge=1` | 11 |
| `corpus.retrain.maxdict` | `int` | **262_144** | `gt=0` — **provisional**, not measured-optimal | 11 |
| `corpus.retrain.k` | `int` | **8000** | `gt=0` — **provisional**, not measured-optimal | 11 |

`Config.resolve_paths()` gains `corpus.dir`, beside the two it already resolves.

### 3 · Module constants

| Symbol | Value | Module | Task | Also in the prose table |
|---|---|---|---|---|
| `TRAIN_LEVEL` | **3** | `dictionary.py` | 14 | yes — **training only**; scoring reads `corpus.compress_level_zstd` |
| `TRAIN_D` | **8** | `dictionary.py` | 14 | yes |
| `INSTALL_MARGIN` | **0.02** (2%) | `dictionary.py` | 14b | yes |
| `RESCAN_EVERY` | **500** bodies | `corpus.py` | 14c | yes |
| `TRAIN_BUDGET_S` | **60** | `dictionary.py` | 14a | yes |
| `WINDOW_MAX_DAYS` | **30** | `dictionary.py` | 14b | yes |
| `MIN_SESSIONS` *(name proposed)* | **2** | `dictionary.py` | 14b | no — the widening rule states the number in prose only |
| the drain timeout on `close()` | ❓ **unset** | `corpus.py` | 9 | named twice as "a module constant", never given a number |
| the summary cadence | **500** calls | `corpus.py` | 9 | **❓ one symbol or two?** — see below |
| the index schema version in `manifest` | ❓ **unset** | `corpus.py` | 8 | no |

**The cadence question is not pedantry.** `RESCAN_EVERY` is **500 bodies in the worker**; the summary
line is **500 calls from the submit path**. Different threads, different counters, the same number —
and the prose says they match *on purpose*, so that "the worker has one periodic rhythm rather than
two". **One shared symbol makes that true and keeps it true; two symbols that happen to be 500 make it
a coincidence that will drift.** The plan does not say which, and the code will have to.

**`TRAIN_BUDGET_S = 60` is a gate with a branch, not a threshold to record.** At or under it Task 14a
registers **both** triggers; above it, startup only. A run that measures the number and does not act
on it leaves the design with the hole "Placeholders in this file" names.

### 4 · Constants that already exist and that this phase must not collide with

*Compiled because two of them share a value with something new, and a reader who conflates them will
be wrong in a way nothing catches.*

| Existing | Value | Why it is here |
|---|---|---|
| `observe.MAX_SCAN_BYTES` | **1_048_576** | **The same number as `max_body_bytes`'s default and a different job entirely** — it caps what the *usage scanner* buffers, and it is not configurable. Changing one does not change the other, and they are free to diverge |
| `stats.COLUMNS` | 20 names | **The index's first twenty columns are this tuple, in this order.** That is what lets a rotated `calls.csv` segment and a day index feed one spreadsheet |
| `stats.MAX_ERROR_MESSAGE` | 200 | Applies to the index's `error_message` too, since the column is copied |
| `proxy.TIMEOUT` | `connect=5, read=600, write=30, pool=5` | Unchanged. Named so a session does not read the corpus's timeouts as related to it |
| `app.CATCH_ALL_METHODS` | 7 methods | The catch-all is **why** `max_body_bytes` exists — an unenumerated endpoint's reply can be any size |

### 5 · The index — 26 columns, in order

**Columns 1–20 are `stats.COLUMNS` verbatim.** Columns 21–26 are this phase's, and the order is
load-bearing:

| # | Column | Holds |
|---|---|---|
| 21 | `request_ref` | 64-char sha256 hex, **or** `dropped` / `too_large` / `absent` / `error` |
| 22 | `response_ref` | the same |
| 23 | `queue_ms` | wait before a worker took it. Real on a `dropped` row |
| 24 | `store_ms` | hash + compress + write + fsync. **Empty, never `0`, when no body was stored** |
| 25 | `queue_bytes` | pending bytes at submit. Real on a `dropped` row |
| 26 | `request_dict_id` | 8-char hex dictID, **or** `none` when stored undicted, **or empty** when no request body was stored |

**The header is re-emitted in every day file**, so these six strings are on disk in every day folder
and **a rename after any real capture splits the corpus.** They are names, not labels.

### 6 · The sentinel words, and why words

| Word | Where | Means |
|---|---|---|
| `dropped` | ref cells | the queue was over its byte bound |
| `too_large` | ref cells | one body over `max_body_bytes` |
| `absent` | ref cells | **the router authored this body** — the 400, the 502, the injected SSE `error` event |
| `error` | ref cells | compression or the write itself failed in the worker |
| `none` | `request_dict_id` | stored with **no** dictionary |
| *(empty cell)* | `store_ms`, `request_dict_id` | genuinely absent |

**A word can never be mistaken for a 64-char digest, and `0` is a real dictID** — which is why the
undicted case gets a word and not a zero. `../../reference/observability.md`: *an absent value is an
empty cell, never a zero.*

### 7 · Names that go on disk

**These are as much a schema as the columns are** — a rename after any capture is a migration.

| Path | Form | Note |
|---|---|---|
| `<dir>/dicts/` | — | **the source**; the trainer writes here, the router reads here |
| `<dir>/dicts/.incoming/` | — | **dot-prefixed**, unlike a day's `incoming/` |
| a dictionary | `req-<UTC>-<dictID>.dict` | e.g. `req-2026-08-18T104500Z-a3f91c2b.dict` |
| the UTC stamp in it | `%Y-%m-%dT%H%M%SZ` | **"newest" is by filename, never mtime** — `logs/` is inside a cloud-synced folder here |
| the dictID in it | **8 lowercase hex** | a dictID is a `uint32`, so 8 is exact |
| the trainer's staging file | `<pid>-<uuid>.tmp` | unique per run, so two processes cannot interleave into one valid-looking name |
| `<dir>/retrain.log` | one line per attempt | UTC stamp, window, sample count, candidate ratio, incumbent ratio, verdict |
| `<dir>/retrain.lock` | exclusive, released on exit | **across processes**; a stale lock is broken by age ❓ *(the age is unset)* |
| a day folder | `YYYY-MM-DD` | **UTC-derived, never local** |
| `<day>/index.csv`, `<day>/manifest`, `<day>/dicts/`, `<day>/incoming/` | — | `incoming/` here has **no** dot |
| a blob | `<day>/{requests,responses}/<2 hex>/<64 hex>.zst` | **2-character fan-out**, sha256 of the **plaintext**, `.zst` |

**The `.incoming/` versus `incoming/` asymmetry is real and unexplained in the plan.** The defensible
reason is that `<dir>/dicts/` is *listed* by the pickup and a dot-prefix keeps staging out of that
listing, while a day's `incoming/` sits among named siblings nothing globs. **If that is the reason it
should be written down; if it is not, one of the two should change.**

### 8 · The queue, and its item

| Name | Type | Note |
|---|---|---|
| `_queue` | `queue.SimpleQueue` | **unbounded**; thread-safe both ends, `put` never blocks |
| `_lock` | `threading.Lock` | guards `_pending` only. **Held for nanoseconds, never across I/O** |
| `_pending` | `int` | **payload bytes** waiting — `len(req) + len(res)`, *not* `sys.getsizeof` |

**The item is a 5-tuple:** `(CallRecord, request_bytes, response_bytes, submitted_at,
pending_at_submit)`. The last two exist because `queue_ms` and `queue_bytes` are values **only
`submit()` can see** — read in the worker, `queue_bytes` would record depth at dequeue, near zero, and
therefore indistinguishable from working.

**The ~33-byte `bytes` header is deliberately not counted.** This is a tripwire, not an accountant.

### 9 · Derived numbers — arithmetic, not settings

*Here so that nobody re-derives them wrongly or writes one into the code as a constant.*

| Number | From |
|---|---|
| **~640 bodies** — the queue's item capacity at the default | 67_108_864 ÷ 103_935 ≈ 645 |
| **103_935 bytes** — the median request | Phase 9's measured corpus, not a setting |
| **~1–3 calls/s** — the target peak | extrapolated from 0.14 and 0.03 calls/s measured |
| **~2,930 bodies/s** — one worker at level 9 | Task 6, and it is **~500×** the target peak. This is why there is no `workers` key |
| **~250 MB/year** bodies, **~150 MB/year** dictionaries | extrapolations the owner has accepted as too small to act on |

### 10 · New surface on existing objects

| Where | Change | Task |
|---|---|---|
| `Proxy.record()` | a third line, `corpus.submit(...)` — **four call sites** | 12 |
| `Proxy` | the **arrived/recorded counter pair**, always on, independent of `corpus.enabled` | 9, 12 |
| `Proxy.begin()` | increments `arrived` | 12 |
| `observe.Call` | holds the request body **and** the response buffer ❓ *(field names unset)* | 12 |
| `observe.watch()` | tees the response up to `max_body_bytes`, then **discards the copy and frees it** | 12 |
| `app.create_app()` | takes the writer **the way it already takes `stats`** | 12 |
| `app.py` lifespan | starts and stops the worker; starts the training thread | 12, 14a |
| `cli.py` | `--check` prints the block; **`--train-dict`, `--tune-dict`, `--extract`, `--from <dir>`** | 11, 13a, 14e |

**No new route.** `/health` is unchanged and the catch-all forwards everything else.

### 11 · CLI flags

`--train-dict` and `--tune-dict` each take **a flag per `retrain` setting**, and the flag wins for
that one run. ❓ **The four flag names are not fixed by this plan** — the obvious spelling is
`--window-days`, `--sample-min-bytes`, `--maxdict`, `--k`, and `14e` should state them rather than
invent them at the keyboard.

`--train-dict` **bypasses the once-a-day guard** and works with `window_days: 0`; it **does not bypass
the margin**. `--tune-dict` **never installs** and labels its own output provisional.

### 12 · What is not yet decided — the ❓ rows collected

**Compiling this register is what found them.** None is large; all of them are the class where a
session at the keyboard invents a number and nothing records that it was invented.

| # | Missing | Why it matters | Whose |
|---|---|---|---|
| 1 | **The drain timeout's value** | Named as "a module constant" **twice**, and line 270 cites *"the precedent the shutdown timeout already set"* to justify the other six — **so the precedent itself has no value.** The prose reasons about a ~20 s worst case without proposing a number | owner |
| 2 | **The `manifest`'s schema version** | Task 8 writes it. A version with no first value is a version nobody can compare against | owner, cheap |
| 3 | **One cadence symbol or two** | The prose says the rhythms match *on purpose*; two symbols make that a coincidence | session, if the owner has no preference |
| 4 | **The stale-lock age** on `retrain.lock` | "broken by age" with no age | owner |
| 5 | **The four `--train-dict` flag names** | Task 14e | session |
| 6 | **`Call`'s two new field names** | Task 12 | session |
| 7 | **The class names** in `corpus.py` and `dictionary.py` | Tasks 8, 9, 13a, 14 | session |
| ~~8~~ | ~~**Whether the scoring level should follow `compress_level_zstd`**~~ | **Closed out 2026-08-19**, the day it opened: **it does.** `TRAIN_LEVEL` drops to **3** and trains only. Kept struck rather than deleted — a row that vanishes cannot show the mechanism worked | owner, **decided** |

### 13 · The one substantive finding this register produced — **found and closed the same day**

**What it found.** `TRAIN_LEVEL` was a module constant at 9 doing **two jobs**, while
`compress_level_zstd` was a config key defaulting to 9. The decision of 2026-08-19 justified the
constant as *"the level bodies are actually stored at"* — **and an operator setting
`compress_level_zstd: 19` silently falsifies that sentence**, leaving the comparison scoring candidate
against incumbent at a level nothing writes at. That is the exact defect the decision was made to
remove, reintroduced through the back door by making the write level configurable and the scoring
level not.

**Three levels, not one.** Naming them separately is most of the fix:

| | Source | Value | Job |
|---|---|---|---|
| **Archive** | `corpus.compress_level_zstd` | 9 | what bodies are compressed at, per body, in the worker |
| **Scoring** | `corpus.compress_level_zstd` | 9 | what candidate and incumbent are compared at |
| **Training** | `TRAIN_LEVEL` | **3** | what `train_dictionary(level=)` is passed |

**What was decided, 2026-08-19.** Scoring follows the key, because a constant that merely *equals* it
today is a coincidence with a fuse in it. Training keeps a constant and drops to **3** — measured
irrelevant at **0.03%** across levels 3 to 19 on the held-out slice, so the value is chosen on the
library's own default rather than on a borrowed argument. The settled table carries the row and both
rejected alternatives.

**Why "both from the key" was refused, since it is the simpler-looking answer.** All five training
levels produce **one dictID** — the ID comes from content that `k`, `d` and the samples fix, and the
level changes only the entropy tables layered on it. Bind training to an editable key and **editing
that key changes dictionary bytes without changing the ID the reader looks them up by.** A fixed
`TRAIN_LEVEL` keeps that hazard latent, which is why the two-source answer is not merely tidier but
**safer than the one-source one.**

**And the register is what produced it.** Two forward-review passes read this plan as prose and neither
asked what value each name held; the defect is invisible until a constant and a config key sit in
adjacent columns with the same number in them.

---

## Placeholders in this file

**Written down rather than remembered**, because `../../method/IDM-001-git-branching.md`'s closeout
rule was generalised on 2026-08-17 for exactly this defect: Phase 9 read that document *during* the
phase, obeyed it, and still shipped `*(not started)*` group markers and a stale count. **A rule stated
as an instance gets obeyed as an instance**, so this section names the instances.

| Where | Placeholder | Closed out at |
|---|---|---|
| The header, first line | *"Execution is under way; the group markers … say how far"* | Task 24. *Reworded 2026-08-18: it enumerated tasks, went stale the moment Task 4 ran, and was a second copy of the group markers. It now points at them instead, so there is one place to close out rather than two* |
| ~~**Five**~~ **Four** group headings — ~~B,~~ C, D, E, F | `*(not started)*`, and `*(in progress)*` once a group's first task runs. Both are matched by the grep below, which is why those two are the only permitted spellings — **a third form would be invisible to it**, which is the defect finding 13 caught. **Group B closed out 2026-08-18** when Task 6 finished, and this count moved with it; a count that does not move is how this table went wrong before | Task 24, each group as it completes |
| ~~Group **A**'s heading~~ | ~~`*(executed, except 3a)*`~~ | **Closed out 2026-08-18** when Task 3a finished, which is what this row said would close it. *Added earlier the same day: the table said "six" group headings and only five carried the marker, so the uncatalogued sixth was the one form the sweep could not see. Kept struck rather than deleted — a row that vanishes cannot show that the mechanism worked* |
| The Record table below | `Merge commit \| not yet merged` | The merge itself |
| "What is settled" | *"still open questions until Task 20"* | Task 20 |
| ~~"What this phase does not settle"~~ | ~~*"Raised 2026-08-19 and not ratified"* — the dictionary storage figure~~ | **Closed out 2026-08-19**, the same day it opened: the owner accepted it as too small to act on and not judgeable without real usage data. Kept struck rather than deleted — a row that vanishes cannot show the mechanism worked |
| "The retraining path" and Task 14a | *"which of the two is decided by Task 14a's measurement"* — the trigger is startup-only **or** startup-plus-rollover, and this file deliberately does not say which | **Task 14a**, by measuring the training wall clock. **If it is never closed out, the phase ships a design with a hole in it** and the group marker will not show that, because the hole is inside a task rather than in front of one |

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
| `zstandard`'s dictionary training matches `zstd --train`'s | **Measured — Task 6, 2026-08-18: they do not match, and the defaults were exactly where it went wrong.** *(Read **unverified** until then.)* `zstandard` uses COVER and `zstd --train` fastcover, so at default `k` the library is **up to 15% worse**; at `k=8000` it is **13% better**. **The tool is not the variable — `k` is.** Q5's "one tool" decision survives and gains a requirement: Task 14 sets `k` explicitly. Phase 9's figures remain comparable only against the library's *tuned* output, and `notes.md` says by how much |
| **`zstandard` releases the GIL during compression** | **Measured — Task 4, 2026-08-18.** *(Read **unverified — and it is load-bearing** until then, this file having asserted it as fact in its first version.)* Verified against the **shipped binary** rather than the C source, which the wheel does not carry: `_ZstdCompressor_compress` calls `_PyEval_SaveThread`, then `_ZSTD_compressStream2`, then `_PyEval_RestoreThread` — the `Py_BEGIN_ALLOW_THREADS` pair around the work. 21 functions release it in total, balanced in every one, including `_train_dictionary`. `notes.md` carries the method. **This settles the mechanism, not the scaling** — Task 6 is unchanged and still measures 1 / 2 / 4 threads |
| Single-thread zstd runs at ~2–6 MB/s at level 19, ~350–500 MB/s at level 3 | **Measured — Task 6, 2026-08-18**, and the published range was about right undicted: **4.2 MB/s at level 19, 286 MB/s at level 3**. *(Read **documented only** until then.)* **With a dictionary both roughly treble** — 14.7 and 771 MB/s — which no published figure covers, because it depends on the corpus |
| Two to five concurrent harnesses is 1–3 calls/second | **Extrapolated** — from two measured sessions at 0.14 and 0.03 calls/s, scaled to the owner's stated target. One laptop, and no session has ever run five harnesses |
| Compression in the worker thread does not slow a *call* | **Unmeasured**, and this phase does not measure it — a thread bounds throughput rather than latency, but that is an argument, not a number. See below |
| ~250 MB a year at an hour a day | **Extrapolated** — from `EPD-003`'s own projection, itself extrapolated from one session |
| **Dictionary training takes "seconds to minutes"** | **Unmeasured, and now load-bearing.** Task 6 trained sixteen dictionaries and timed none of them. **Task 14a measures it first**, because it decides startup-only against startup-plus-rollover — and UTC midnight is an arbitrary local hour, so a four-minute run mid-afternoon is a different proposition from a three-second one *(2026-08-19)* |
| **The path filter is a no-op on this corpus** | **Measured 2026-08-19.** Every request body ≥ 1,024 bytes across all three runs is already `/v1/messages`; the only other path, `/api/hello`, has **0-byte** request bodies. So dropping the path filter costs no comparability at all — the sample set is byte-for-byte the one 12.10x and 13.65x were measured on |
| **Duplicates in the corpus are `overloaded_error` retries** | **Measured 2026-08-19**, and not previously recorded anywhere. 73 request bodies, **47 distinct**; one 103,935-byte body sent **11 times** inside one session, another 9 times inside a second, each answered with 119 bytes of `overloaded_error`. **The duplication sits almost entirely in the training slice** — run-01 is 49 bodies / 25 distinct, while run-03, the held-out test slice, is 21 / **21** |
| **`gate.py` deduplicated its training set** | **Refuted — read, not inferred, 2026-08-19.** It appends one path per manifest row and passes the raw list to `zstd --train`; there is no `hashlib` and no `set` in the file. On its exact rule: **48 training bodies, 26 distinct — 46% repeats.** Whether dedup would improve or degrade the result is **unmeasured and stays that way**, by the owner's decision that these sessions are too short for the numbers to be more than approximate. Task 21 carries the composition in the slice column |
| **Deduplication loses the retry information** | **False, and worth stating because the opposite is assumed.** The store writes one blob per distinct body, but the index keeps **one row per call**, all carrying the same digest — so *this body was sent eleven times in four minutes* stays fully recoverable. The bytes collapse; the multiplicity does not |

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
**Recorded in `../../backlog.md` on 2026-08-19** rather than left implicit: the asymmetry is inherited
from what Phase 9's gate happened to measure, not from any finding that responses do not benefit — and
under automatic retraining it would otherwise become permanent by default rather than by decision.

**The extraction *tool*. The reader ships here; the tool is Phase 11's.** *Added 2026-08-19, and the
split is not arbitrary.* Task 13a builds the reader — blob plus the day's dictionaries → plaintext,
verified against the digest in the filename — because **Task 14a's trainer cannot assemble a sample
list without it.** What is deferred is everything built on top: selection by day, session, call or
model, output layout, and bulk verification. **So Phase 11's subject is not "build extraction" but
"build the tool", on a reader this phase ships and Task 18 exercises.**

**How long training takes, and therefore when it should run.** Task 14a measures it and the trigger
follows from the number. **If it comes back large, startup-only is the answer** and the day-rollover
trigger is dropped — the manual command plus the directory rescan already cover the long-running
router, which is the case rollover-triggering exists for.

**Whether the dictionary storage figure is still acceptable — settled 2026-08-19, and it is not a
blocker.** The "plain copies" decision was costed at ~40–80 MB a year when a new dictionary was a rare
event; one per day plus a copy in each day that uses it is roughly double, call it ~150 MB a year.
**The owner's decision: too small to act on, and the number is a raw approximation anyway.** Severity
is not judgeable until there is real usage data, and there is none — no day-partitioned corpus has
ever existed. **So the figure is accepted as-is and revisited against measurement rather than against
arithmetic**, which is the same shape as the day-thinness item in `../../backlog.md`. *(This paragraph
read "Raised 2026-08-19 and not ratified" for part of that day; it is closed out here rather than left
for Task 24, because it was never a task's to close.)*

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
- **The swap ordering fails silently, and only one check can catch it.** *Added 2026-08-19.* Copy the
  dictionary into the day folder, then build the compressor, then swap — reversed, everything works
  until a crash lands between two steps, after which a day holds a blob whose dictID names a
  dictionary that is not in that folder. **Nothing reports it at the time**; it surfaces only when
  somebody tries to read that day back, possibly months later. Task 18's observation 7 is what makes
  it a check rather than a hope.
- **A day trained from is a day the router may still be writing to.** A body submitted at 23:59:59 and
  written at 00:00:02 belongs to *yesterday* if the folder is derived from the call's timestamp — so
  the day folder can grow while training reads it. Harmless in effect, the dictionary missing a body
  or two, but **which timestamp decides the folder is unspecified in Task 8** and the trainer must
  tolerate the directory changing under it. *Found 2026-08-19; it is a Task 8 gap, not only a
  retraining one.*
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

**And, from 2026-08-19:** a body comes back **out** of the store through a reader that verifies it
against its own digest; **the router retrains itself** from the days it has already captured, refusing
a candidate that loses to the incumbent; a dictionary installed while the router is running is picked
up **without a restart**, and the day folder that saw the swap still opens from itself alone;
`retrain.window_days: 0` trains nothing; and **the training wall clock is measured before the trigger
is wired**, not after.

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
