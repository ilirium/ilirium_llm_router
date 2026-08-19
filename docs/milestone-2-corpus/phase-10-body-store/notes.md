# Phase 10 — the body store: notes

Branch: `feat/phase-10-body-store`, off `main` at `d885b2f`. **Not yet merged.**

Written **while the work is happening**, task by task. Everything below the re-derivation is added as
it is found; nothing here is assembled afterwards.

**The re-derivation ran before `plan.md` was published**, which is Phase 9's shape rather than Phase
8's. `../../README.md`: *a phase's first act is to re-derive its own plan against what is now known* —
and five of Milestone 1's and 2's phases found their plan wrong on contact. Here the plan did not
exist yet: the phase opened with an interview, and the nine findings below landed during it, so they
**shaped** the task list instead of correcting it. The trade Phase 9 named applies again and is not
free — this shape produces no committed record of a plan being wrong, which is evidence about planning
itself. What is gained is that no task numbers are spent on work that turned out to be wrong.

---

## The re-derivation, before Task 1

`plan.md`'s subject is the fenced section *"Design produced by the interview"* in
`../phase-9-corpus-gate/plan.md`. That section was written **before the gate ran**, on the owner's
instruction, because this repository's sessions are cleared deliberately and a design that exists only
in a conversation does not survive it. It is **input to be re-derived, not a specification**, and the
prompt that opened this phase says so.

**Six of the nine findings below are against that sketch. Three are against the ground it stands on.**

### What was checked and passed

| Claim | Verified |
|---|---|
| `make test` reports **158** | ✅ 158 passed |
| `procedures/link-check.py` reports **68 broken, 2 roundabout** | ✅ **run, not predicted** — 70 files, 68 broken, 2 roundabout |
| Working tree clean, `main` at `d885b2f` | ✅ |
| `zstd` present, 1.5.7 | ✅ |
| `logs/corpus-gate/` still holds Phase 9's corpus | ✅ three run directories plus **eight** dictionaries |
| `logs/` is gitignored, so a corpus under it needs no new rule | ✅ `.gitignore:228`, a bare `logs/` |
| `Proxy.record()` is the funnel every path reaches | ✅ four call sites, `proxy.py:140, 156, 205, 270` |

**The link-checker count was run rather than predicted**, per `../../status.md`'s standing warning and
Phase 8's two failed attempts to predict it from its own docstring. **The file count is now 70**,
against the 69 Phase 9 recorded at its close and the 68 it recorded at Task 4 — the count grows with
every document added, while the broken count has not moved. That is the property worth watching, and
it is why the docstring's partition by *where hits live* keeps mispredicting: what resolves a hit is
*which path it names*.

---

## The nine findings

### 1 — "A bounded off-thread queue" is unbounded in memory as written

`EPD-003`'s constraints and the sketch both say **bounded**, and the obvious reading is a `maxsize` in
items. At this workload that is not a bound at all: Phase 9 measured the **median request at 103,935
bytes**, so a 1,000-item queue is ~200 MB of resident memory before anything is refused.

**The queue must be bounded in bytes**, with the item count falling out of it. Recorded as a finding
rather than an implementation detail because *"bounded"* reads as done, and the failure only appears
under exactly the load the bound exists for.

### 2 — The capture hook belongs at `Proxy.record()`, not in `watch()`

Phase 9 measured the defect — **158 request captures against 149 responses** — and diagnosed it as
*"the paths that return before `watch` ever runs"*, but **did not name the fix**. Its own throwaway
patch hooked `begin()` for requests and `watch()`'s `finally` for responses.

`record()` has **four call sites**, and every path that produces a row reaches one:

| `proxy.py` | Path |
|---|---|
| `:140` | `begin()` — the caller went away while its body was still arriving |
| `:156` | `messages()` — the body carries no `model`, refused with a 400 before any backend was chosen |
| `:205` | `relay()` — the backend could not be reached at all; no HTTP status ever existed |
| `:270` | `watch()`'s `finally` — the normal path, and the only one Phase 9's hook covered |

**Three of the four are exactly the 9-way gap**, and they are the rows `EPD-003` calls *"the
interesting ones, not the broken ones"*. Hooking the store where the CSV row is already written gets
the body, the row and the two refs in one place, and needs no second funnel to maintain.

### 2b — But that funnel has a blind spot, and this phase does not close it

> **WRONG AS WRITTEN. Refuted 2026-08-18 by the forward review; see "the reconciliation" below.** A
> caller disconnecting after response headers **does** reach `record()` and **does** get a row — six
> measured `client_disconnect` rows say so. What survives is a race nobody has observed. **The
> paragraphs below are left as written**, because they record what was believed while the plan was
> being built, and `../../README.md` says a claim in a phase note is corrected elsewhere rather than
> rewritten.

Stated because claiming full coverage would be wrong. **If the caller vanishes after the response
headers have gone out**, Starlette never runs the body generator, so `watch`'s `finally` never fires
and `record()` is never reached. Such a call gets **no CSV row today** and will get **no corpus
entry**.

`proxy.py`'s comment on the `BackgroundTask(reply.aclose)` reasons about precisely this case for
connection cleanup — *"a generator that never runs at all, and so never reaches its own `finally`"* —
so the gap is known to the code and unclosed in the recorder. **Inferred from that comment and from
the ASGI behaviour it cites; not observed here.** Fixing it is a change to the recorder, which is not
this phase's subject; naming it is.

### 3 — The 22-column index has nowhere to record a drop

`EPD-003`'s answer to the write path is *"drop the body and record that it was dropped — a corpus with
a known hole is fine, a stalled request is not."* The sketch's index carries `request_body_ref` and
`response_body_ref`, and its column table reasons only about **truncation**, concluding correctly that
`error_status` already covers it.

**A dropped body is not an error of the call.** It is an event in the corpus, invisible to
`error_status`, and an empty ref cell would read as *"there was nothing to store"* — which is a
different fact from *"there was something and we lost it"*. Half of `EPD-003`'s own answer would have
gone unimplemented.

**The repair needs no new column:** a ref cell holds a **64-character hex digest**, or one of
`dropped` / `too_large` / `absent`. A reason word cannot be mistaken for a digest, so the encoding is
unambiguous and greppable.

### 4 — Over the cap, drop; do not store a prefix

`EPD-003`: *"The store must be able to hold a truncated body and say that it is truncated."* That is
right for the case it was written about — a stream that broke, where **the bytes that arrived are the
whole of what exists** and `error_status` already says the call failed. It is wrong for a size cap: a
prefix stored under a content address, indistinguishable from a whole body, is worse than a hole.

Splitting the two cases is what lets the sketch's *"truncation needs no new column"* stand **for the
reason it gave** rather than by accident.

### 5 — Compression needs a dependency, and nothing noticed

**Measured on this machine, 2026-08-18:** Python 3.13 has no `compression.zstd` — that module arrived
in 3.14 — and `zstandard` is not installed. `zstd` 1.5.7 exists only as a **CLI binary**, which is
what produced every compression figure in `EPD-003`, in Phase 9's gate, and in
`../../reference/measurements.md`.

**So the router cannot compress anything today**, and neither `EPD-003`, nor the fenced sketch, nor
the gate's evidence mentions it. The whole milestone rests on `subprocess` calls to a binary that the
router itself has never used.

This project declares its dependencies deliberately — `pyproject.toml` carries a paragraph explaining
why `pydantic` and `starlette` were promoted out of transitive status in Phase 6, on the ground that
*"the router's real requirement was whatever FastAPI happened to ask for"*. **A new runtime dependency
is a decision, not an implementation detail**, which is why it went to the owner rather than into the
plan.

### 6 — Deduplication scope is per day, and the sketch never says so

It follows from the tree — `<date>/requests/3f/…` puts the blobs inside the date folder — and it is
**correct**: cross-day deduplication would make `rm -rf <a-day>` orphan another day's refs, and
date-partitioned pruning by `rm -rf` is one of the things `EPD-003` counts as what per-call files buy.

But it is load-bearing and **unstated**, and a reader implementing "content-addressed store" from the
sketch would reasonably build one global store and silently break the retention answer.

### 7 — Copying dictionaries per day costs ~80 MB a year, and the deferred fork dissolves

The sketch puts dictionaries **inside** the date folder for portability — *"`tar` one folder and it
decompresses elsewhere with nothing else needed"* — names the ~80 MB/year cost, and **defers the
choice between plain copies and APFS clones** to the `--maxdict` result.

**Neither is needed.** `os.link()` is portable Python, costs zero bytes, and keeps the portability
argument intact: `tar` detects hardlinks among *archived members*, so a day folder archived without
its link partner emits a real file. One durable `dicts/` at the corpus root, hard-linked into each day
that uses it.

*Superseded 2026-08-18: the owner chose plain copies (Q7), so there are no hard links and no root
folder. **The finding stands — the sketch's ~80 MB a year is real and was accepted** — but the repair
this paragraph proposed is not the one taken.*

### 8 — `make test` can take 150 seconds on this machine, not 0.6

> **Overstated, and corrected 2026-08-18 by running it again at the end of the session: 158 passed in
> 0.62 s.** The 150 s is the **first** run after the cloud-synced folder has evicted the virtualenv,
> not this checkout's speed — so Phase 9's 0.6 s was right and this finding read as though it were
> wrong. **What survives is the actionable half**: a first run looks like a hang and is not. What does
> not survive is the framing that the suite is slow here. Found by running the check rather than by
> re-reading it, which is the `../../README.md` lesson *check the claim you are planning against,
> including when it is your own.*

Same 158 tests, all passing. Phase 9 recorded **0.60 s**; this session measured **150.85 s**, and the
first `import fastapi` alone took over 17 seconds of wall clock across its submodules.

**It is OneDrive placeholder hydration on first touch, not a repository defect** — the `.venv` lives
inside the synced folder, and a warm second run is fast. Recorded because **Phase 10 adds tests**, and
a session reading 0.6 s as the baseline will conclude the suite has hung and start debugging the wrong
thing. It cost this session three abandoned invocations before the cause was found.

### 9 — The `logs/telemetry/` sweep is smaller than it looks, and one judgement in it is not mechanical

**Live citations, which Tasks 16 and 17 must change:** `config.yaml` (two), `config.py` (two
defaults), `tests/test_config.py`, `tests/test_logging_setup.py`, `CLAUDE.md:115`, `README.md:17`,
`../../reference/observability.md`'s config-shape block, `../../procedures/testing-against-claude-code.md`
in three places, and `../../procedures/lmstudio-capability-probes/probe.py:290`.

**The archive and the EPDs also name `logs/calls.csv`, and this phase proposes to leave them.**
`../../README.md` licenses repointing a **path** in archived prose, because a path is navigation
rather than a claim. That licence does not reach these:

- `logs/` is gitignored and `link-check.py` **skips it outright**, so none of them is a link anyone
  can follow, before or after the move.
- Several are claims about what was on disk that day — Phase 9's *"`logs/calls.csv` before the capture
  — 177 lines, 29,831 bytes"* is a measurement, not an address. Repointing it would falsify the record
  to fix nothing.

**The rule that decides it:** a path is editable in the archive when repointing *preserves what the
document means*. Here it would change what the document means. So the sweep is a live-documents sweep,
and Task 17 states that rather than leaving the untouched hits looking like an oversight.

---

## Each finding as a question, with its options

**Added 2026-08-18, on the owner's request, before any task ran.** The nine findings above are written
as findings — *this is wrong and here is why* — which makes them hard to act on. This section restates
each one as **a decision with named options**, in plain terms, and says **what `plan.md` currently
assumes** so the default is visible rather than buried in a design paragraph.

**Nothing here is decided.** `plan.md` was written before this section existed and encodes one answer
per row; changing an answer changes `plan.md`, which has not been executed. **Ten questions, because
finding 2 splits into a fix and a limit** — *and thirteen since 2026-08-18, when the write-path
interview added Q10 to Q12. Those three are not findings against the sketch; they are questions this
phase raised about itself.*

| | The question in one line | What `plan.md` assumes |
|---|---|---|
| **Q1** | What stops the queue eating memory, and at what size? | **Decided:** bounded in **bytes**, **configurable**, default 64 MiB. One `queue.SimpleQueue` |
| **Q2** | Where in the code does the store get handed the bytes? | **`Proxy.record()`**, all four call sites |
| **Q2b** | Do we fix the case where no row is written at all? | **Name it, do not fix it** |
| **Q3** | How does the index say a body was not stored? | A **reason word** in the ref cell |
| **Q4** | A body over the ceiling — keep the first megabyte, or nothing? | **Decided:** nothing, marked `too_large`, and **configurable** |
| **Q5** | The offline trainer — `zstandard`, or the `zstd` binary? | **Decided: `zstandard`. One tool.** *Reversed* |
| **Q6** | The same body on two days — stored once or twice? | **Twice.** Dedup is per day |
| **Q7** | How does a day folder get the dictionary it needs? | **Decided: a plain copy**, and no root folder. *Reversed* |
| **Q8** | Where does "the tests take 150 s here" get recorded? | **This note only** |
| **Q9** | Which documents get repointed by the telemetry move? | **Live documents only** |
| **Q10** | What compression level does the write path use? | **Decided: `compress_level_zstd`**, default measured by Task 6 |
| **Q11** | Is the corpus's copy of a response a second buffer? | **Yes, separate from the scanner's** |
| **Q12** | How is "did this ever come close?" answerable later? | **Decided: A, plus one counter pair** for loss outside the corpus |

*Q10 to Q12 were added 2026-08-18, out of the write-path interview rather than the re-derivation.
They are questions this phase raised about itself, not findings against the sketch.*

---

### Q1 — What stops the queue eating memory, and at what size?

**In plain terms.** When a call finishes, the router hands its bodies to a background thread so the
caller is not kept waiting while they are compressed and written. **The worker handles one body at a
time.** If bodies arrive faster than it finishes them, the ones not yet processed sit in the queue
**still holding their bytes in RAM**.

*Expanded 2026-08-18, because the first version of this entry assumed the reader already saw why a
limit was needed at all.*

**With no limit, a burst grows that until the process is killed.** That would take the router down —
and *"telemetry must never break a call"* is the rule that forbids precisely this. So there must be a
limit. **The whole question is what it counts.**

**A limit in *items* sounds like a bound and is not one.** *At most 1,000 waiting bodies* means
anywhere between 2 MB and 200 MB here, because Phase 9 measured bodies from 2,277 bytes to 185,209.
The number that hurts is bytes, so bytes is what to count — and then the item count is free to vary,
640 median bodies or 30,000 tiny ones, both fine.

**When it is full, the request path does not wait.** Waiting is the one outcome `EPD-003` rules out.
The body is not stored and the record is enqueued anyway with `dropped` in its ref cells, so the hole
is a row rather than an absence.

**And at the measured load the queue should sit at nought or one item.** One to three calls a second
against a worker taking tens of milliseconds means 64 MiB is never approached. **So the bound is a
tripwire, not a tuning knob** — a sustained `queue_bytes` above a megabyte is the finding, long
before anything is dropped. That is what the column is for.

**It is logged explicitly**, on the owner's instruction: the first drop in a run raises a `WARNING`
carrying the reason, the body's size, the pending bytes, the queue length and the call's path and
session, so the row can be found. Subsequent drops are counted rather than logged — warning on every
one turns overload into log spam at the moment the log most needs to stay readable.

> **Decided 2026-08-18: bounded in bytes, and the bound is configurable — `queue_max_bytes` in the
> `corpus:` block, default 64 MiB.** It has been in that block since the first draft; the owner asked
> for it explicitly, so it is recorded here rather than left to be discovered by reading the config.
>
> **And the queue was named.** This plan wrote "queue" a dozen times without saying which one. **There
> is exactly one in the design** — one item per call, carrying both bodies — and it is a
> **`queue.SimpleQueue`, unbounded, with the byte accounting held beside it** under a `threading.Lock`.
>
> | Rejected | Why |
> |---|---|
> | `asyncio.Queue` | **Not thread-safe**, and the producer is the event loop while the consumer is a worker thread. The tempting mistake |
> | `queue.Queue(maxsize=N)` | Bounded — **in items**, which is Finding 1 itself |
> | `multiprocessing.Queue` | Pickles every body. Only relevant if Task 6 sends us to processes |
>
> *The item's shape given here — record plus two bodies — was **incomplete**, found 2026-08-18: it
> also carries the submit timestamp and the pending-bytes reading, because `queue_ms` and
> `queue_bytes` are values only `submit()` can see.*
>
> `SimpleQueue` because none of `Queue`'s extra machinery is used: no `maxsize`, no `task_done()`, no
> `join()`. Shutdown is a sentinel and a **timed** thread join — a full queue is ~640 bodies, and a
> router that will not stop is worse than a corpus missing its last few. Whatever is abandoned is
> counted and named in the final summary line, so that hole is recorded like any other.

| Option | Buys | Costs |
|---|---|---|
| **A — bounded in bytes, 64 MiB** *(assumed)* | Memory has an actual ceiling. ~640 median bodies may wait, which is far more backlog than compression at ~10 ms a body can produce | One number in the config that nobody will ever tune |
| **B — bounded in bytes, 8 MiB** | A backlog can never be more than a rounding error of RSS | Drops bodies during ordinary bursts. Every drop is a hole in the corpus, recorded but real |
| **C — bounded in items** | Matches how `EPD-003` and the sketch are worded, so nothing has to be explained | The bound does not bound the thing it exists to bound. This is the finding |
| **D — bounded in both** | Belt and braces | Two knobs, one of which never fires, against a project non-negotiable that configuration stays simple |

---

### Q2 — Where in the code does the store get handed the bytes?

**In plain terms.** Something in `proxy.py` has to say *here are this call's bytes, store them*. Phase
9's throwaway capture said it in two places: when the request body was read, and at the end of the
response streamer. **The response streamer never runs for a call that failed early** — that is why 158
requests produced only 149 responses. The nine missing ones are a refused request, a backend that
could not be reached, and a caller that hung up mid-upload: the rows `EPD-003` calls the interesting
ones.

`record()` is the function that writes the CSV row, and **every one of those paths already calls it.**

| Option | Buys | Costs |
|---|---|---|
| **A — hook `Proxy.record()`** *(assumed)* | One place instead of two. The body, the row and the two refs are decided together, and the three error paths are covered because they already write a row | The store's lifetime is tied to the recorder's. If `record()` is ever restructured, both move together |
| **B — keep the two-point hook** | It is the shape Phase 9 actually ran, so it is known to work | Reproduces the 9-of-158 gap exactly. The corpus would silently omit its most interesting rows |
| **C — hook `record()` and add a net for Q2b** | Total coverage | Changes how `calls.csv` rows are produced, which is Milestone 1's recorder and outside this phase. Risks writing a row twice, which is worse than missing one |

---

### Q2b — Do we fix the case where no row is written at all?

> **The premise is wrong; the question is not.** See 2b above. The case is a race rather than a class
> of calls, and the decision taken — name it, do not fix it — is unchanged and now easier. Left as
> written.

**In plain terms.** There is one path where **`calls.csv` gets no row today either.** If the caller
disappears *after* the response headers have gone out, the web framework never runs the code that
streams the body, so the code that writes the row is never reached. Hooking the store at `record()`
inherits that gap: no CSV row, no corpus entry.

This is a **pre-existing hole in the recorder**, not something the body store creates.

| Option | Buys | Costs |
|---|---|---|
| **A — name it, do not fix it** *(assumed)* | The phase stays about the body store. The limit is written down where the next person looks | A known hole stays open, and "the corpus has every call" is not quite true |
| **B — fix it in this phase** | The claim becomes exact | It is a recorder change wearing a corpus phase's clothes. The fix has to guarantee it cannot double-write a row, and it needs a live disconnect to test — which this scope has no session for |
| **C — a `fix/` branch after Phase 10** | Fixed, reviewed on its own merits, with the phase boundary intact | Another branch, and it competes with `EPD-001`/`002` for attention. It has waited since Milestone 1 without hurting anyone |

---

### Q3 — How does the index say a body was not stored?

**In plain terms.** The index has one cell per direction holding the body's fingerprint. When a body
*was not* stored — dropped because the queue was full, refused because it was too big, or never
existed because the caller vanished mid-upload — that cell needs to say which. Leaving it blank means
*there was nothing to store*, which is a different fact from *there was something and we lost it*.
`EPD-003` explicitly asks for the second: *a corpus with a known hole is fine.*

| Option | Buys | Costs |
|---|---|---|
| **A — a reason word in the same cell** *(assumed)* | 22 columns as the sketch drew them. A fingerprint is 64 hex characters, so `dropped` can never be mistaken for one. Greppable | A column holds two kinds of thing. Anyone writing an analysis script has to know that |
| **B — two extra status columns, 24 total** | Each column holds one kind of thing. Sorts and filters cleanly in a spreadsheet | The index drifts further from `calls.csv`'s 20 columns, and the sketch's argument that a rotated CSV segment and a day file are interchangeable inputs weakens |
| **C — leave it blank** | Nothing to explain | Half of `EPD-003`'s write-path answer goes unimplemented, and the corpus cannot tell a hole from an absence. This is the finding |

---

### Q4 — A body over the ceiling: keep the first megabyte, or nothing?

> **Decided 2026-08-18: option A, and the ceiling is configurable — it always was, in the
> `corpus:` block.** The owner asked *why do we need the ceiling at all*, twice, and the first answer
> was not good enough: it named what each limit protects without saying **when each is checked**,
> which is the whole reason both exist. `plan.md`'s "Two limits, because they are checked at two
> different moments" is the full version. In four sentences:
>
> 1. **The router has never held a whole response.** `proxy.py:245` streams each chunk and forgets
>    it; the only accumulation anywhere is the buffered scanner's, capped at 1 MiB. **The corpus is
>    what introduces whole-response buffering**, so the memory risk is new and arrives with it.
> 2. **The queue bound is checked once, at `submit()`, after the call has finished** — by which time
>    a 2 GB reply has already been accumulated in full. It governs bodies *waiting to be written*, and
>    has no opinion about a body still arriving.
> 3. **The ceiling is checked on every chunk**, so it bounds the peak. When it fires the copy is
>    discarded and the memory freed; **the relay is untouched**, because the copy was never in the
>    path.
> 4. **It is not hypothetical and it is not new reasoning.** `app.py`'s catch-all forwards any path —
>    Phase 9 caught it firing three times on `/api/hello` — and `observe.py` already answered this
>    exact question with `MAX_SCAN_BYTES`, whose comment is the same argument almost word for word.
>    `EPD-003` asks that the **reasoning** be reused rather than a new number invented.
>
> **One asymmetry was glossed over in the first answer and is now stated.** For **responses** the
> ceiling bounds memory. For **requests** it does not — `proxy.py:133` reads the whole body to relay
> it, long before the corpus is consulted, so refusing to store a 500 MB request saves the disk write
> and stops that body's lifetime being extended, but the peak was already spent. **Two separate knobs
> were considered and refused**: one number is simpler and the request case still gains something
> real.
>
> **In normal operation it never fires.** The largest request this project has seen is 203.2 KB and
> the largest response 135,894 bytes. **The ceiling is for the endpoint nobody thought of**, which is
> the only kind that can be arbitrarily large.

**In plain terms.** There is a size ceiling, because the router forwards paths nobody enumerated and a
reply could be any size. When a body exceeds it, we either store the part we have or store nothing.
`EPD-003` says the store must be able to hold a **truncated** body — but it was talking about a
*stream that broke*, where the bytes that arrived are all that ever existed. A body chopped at the
ceiling is a different thing: it is complete-looking and incomplete.

| Option | Buys | Costs |
|---|---|---|
| **A — store nothing, mark `too_large`** *(assumed)* | Every stored blob is a whole body. The fingerprint always identifies what it names | The largest bodies — which may be the interesting ones — are the ones lost |
| **B — store the prefix, mark it truncated** | Some data instead of none | A prefix stored under a content address looks like a whole body to every consumer, and the fingerprint no longer identifies the body. Needs the marker column Q3 option A avoids |
| **C — raise the ceiling until it never fires** | No lost bodies in practice | The ceiling exists because an unknown endpoint could return anything. Raising it hands the memory decision back to a stranger, which is what `observe.py` reasoned about and refused |

---

### Q5 — The offline trainer: `zstandard`, or the `zstd` binary?

> **Decided 2026-08-18: option B — `zstandard` everywhere, and this reverses the recommendation
> below.** The owner asked why two tools, and the comparability argument for A is weaker than the
> simplicity argument against it: one dependency, no requirement that a binary be installed, and the
> procedure runs anywhere the venv does. **The risk is real but small and checkable** — both wrap
> libzstd, so compression at the same level with the same dictionary should agree, but *training*
> defaults may differ, and training defaults are exactly where Phase 9 found non-monotonicity.
> **Task 6 compares the two trainers on the same samples**, so the risk is measured rather than
> accepted or assumed.

**In plain terms.** You have decided the **router** gets the `zstandard` package. Separately, there is
an offline tool that trains the dictionary — it never runs on the request path. Every compression
figure this milestone rests on came from the **`zstd` command-line binary**, including Phase 9's gate.

| Option | Buys | Costs |
|---|---|---|
| **A — the trainer keeps using the binary** *(assumed)* | A new dictionary is measured on the same instrument as every number already in `../../reference/measurements.md`, so the comparison is honest. `evidence/gate.py` already works this way | Two tools in one project. The procedure needs `zstd` installed, which a config file cannot check |
| **B — the trainer uses `zstandard` too** | One tool. The procedure needs nothing but the dependency the router already has | New figures are not directly comparable with Phase 9's until somebody re-measures the old ones with the new tool. That is a cost this repository has paid before for smaller reasons |
| **C — the trainer does both and compares them** | Settles whether they agree, once | A measurement nobody asked for, in a phase that already has twenty-four tasks |

---

### Q6 — The same body on two days: stored once or twice?

**In plain terms.** Bodies are filed under their fingerprint, so an identical body arriving twice is
stored once — that is what "content-addressed" buys. The question is whether that holds **across
days**. The corpus is partitioned into date folders because deleting a day should be `rm -rf` and
nothing else. If a day's blobs can be referenced by another day's index, deleting one breaks the
other.

| Option | Buys | Costs |
|---|---|---|
| **A — dedup within a day only** *(assumed)* | `rm -rf logs/corpus/2026-08-18` is always safe, which is the entire retention answer. A day folder is self-contained | A body that recurs across days is stored once per day. Compressed against the dictionary, that is a few kilobytes |
| **B — one global store, dedup across days** | Strictly less disk | Deleting a day can orphan another day's references, silently. The retention answer stops being `rm -rf` and becomes a procedure |
| **C — global, with reference counting** | Both | A garbage collector, in a project whose non-goals list *"a database, a query engine"* and whose whole claim is that this needs no special infrastructure |

---

### Q7 — How does a day folder get the dictionary it needs?

> **Decided 2026-08-18: option B, plain copies — and the root `logs/corpus/dicts/` is deleted from
> the design.** The owner's rule: **a day folder is self-contained**, holding any metadata, any
> dicts, any archives it needs.
>
> **The root folder was this plan's invention, not the sketch's.** Phase 9's fenced design put
> dictionaries inside the date folder and called them *"copies of whichever dictionaries this day
> used"*. This plan added a root folder to be the target of the hard links in option A; **declining
> the links left it with no job at all.** So the decision restores the sketch rather than departing
> from it, and option C — which kept a root folder — dies with option A.
>
> **What it buys beyond simplicity is an invariant enforced by the layout.**
> `../../reference/design-decisions.md` makes dictionaries *"append-only forever"* because losing one
> makes every blob referencing it unreadable. With a copy in every day that uses it, **deleting a day
> whole cannot affect a surviving day** — the rule is satisfied by the shape instead of by somebody
> remembering it. The cost is the ~40–80 MB a year the sketch already named.

**In plain terms.** A compressed blob cannot be read without the dictionary it was compressed against
— lose the dictionary and every blob referencing it is unreadable forever. The sketch put a copy
inside each date folder so that one folder can be moved elsewhere and still open, and priced that at
about 80 MB a year. It left the choice between plain copies and filesystem clones open.

| Option | Buys | Costs |
|---|---|---|
| **A — a hard link into the day folder** *(assumed, and rejected)* | The folder appears to contain its dictionary and costs nothing. Archiving one day still produces a real file, so portability survives | Links fail across filesystems, so an absolute `dir` on another volume needs a fallback — and the root folder it needed as a target was this plan's own invention |
| **B — plain copies** | Works everywhere, no cleverness, and a duplicate is also a backup of something that must never be lost | ~80 MB a year, roughly a quarter of the projected corpus, and more if a dictionary wants to be larger |
| **C — one `dicts/` at the root, and the day's manifest names what it uses** | Zero bytes, no links, one obvious home for a thing that is never deleted | Archiving a single day no longer produces something that opens by itself, which was the sketch's reason for the copy |

---

### Q8 — Where does "the tests take 150 seconds here" get recorded?

**In plain terms.** Phase 9 recorded `make test` at 0.6 seconds. On this machine today the same 158
tests take 150 seconds, because the virtual environment lives in a synced cloud folder and every file
is fetched on first touch. **Nothing is wrong**, but a session that expects 0.6 s will conclude the
suite has hung — this one abandoned three invocations before finding the cause.

| Option | Buys | Costs |
|---|---|---|
| **A — this note only** *(assumed)* | Costs nothing, and it is written down | A phase note is archive. Nobody reads it before running `make test` |
| **B — one line in `CLAUDE.md`'s commands table** | `CLAUDE.md` is the only file loaded into every session, and its admission test is *would a session act confidently and wrongly without this* — which is exactly what happened here | `CLAUDE.md` is kept deliberately small, and this is a fact about one laptop rather than about the project |
| **C — a row in `../../reference/measurements.md`** | The register exists so a number carries its slice, and this number's slice is the whole point | The register is for measurements the project's claims rest on. Nothing rests on this |
| **D — nowhere** | It is environment noise and will change the day the checkout moves | The next session pays the same three invocations |

---

### Q9 — Which documents get repointed by the telemetry move?

**In plain terms.** Moving `calls.csv` and `router.log` into `logs/telemetry/` makes every document
that names the old paths wrong. Some of those documents are *live* — the README, `CLAUDE.md`, a
procedure somebody follows. Others are **archive**: a phase note recording *"`logs/calls.csv` before
the capture — 177 lines, 29,831 bytes"*. The manual says a **path** in archived prose may be
repointed because a path is navigation, but a **claim** may not.

| Option | Buys | Costs |
|---|---|---|
| **A — live documents only** *(assumed)* | The archive keeps saying what was true when it was written. `logs/` is gitignored and the link checker skips it, so nothing becomes unfollowable | Two documents will name a path that no longer exists, and it will look like an oversight unless Task 17 says otherwise — which it does |
| **B — repoint everything, archive included** | Grep for the old path returns nothing, so nobody wonders | Rewrites measurements into statements that were never true. *"`logs/telemetry/calls.csv` before the capture — 177 lines"* is a sentence about a file that did not exist that day |
| **C — live documents, plus a note in each affected `evidence/README.md`** | The archive stays honest and a reader is told why the path reads oddly | More edits, in directories this phase otherwise does not touch |

---

### Q10 — What compression level does the write path use?

> **Decided 2026-08-18: option D — configurable, with a default measured by Task 6.** The owner's
> reasoning is the one the option names: this is the knob where the right answer genuinely depends on
> the machine.
>
> **The key is `compress_level_zstd`, not `level`** — renamed the same day, on the owner's
> instruction that a key should be self-describing. `level` already means something else two keys
> away in the same file: `logging.level` is a severity. A name read in isolation should say **what it
> sets and whose scale it is on**.

**In plain terms.** `zstd` has levels from 1 to 22, trading speed against ratio. **Every number this
milestone owns was measured at level 19**, because Phase 9 was measuring a *ratio* offline where time
did not matter. On the write path time does matter: published figures put level 19 at ~2–6 MB/s and
level 3 at ~350–500 MB/s — **a hundredfold difference**, against a ratio difference that nobody has
measured *with a dictionary already carrying the static preamble*.

| Option | Buys | Costs |
|---|---|---|
| **A — measure first, then choose** *(assumed; Task 6)* | The level is picked from this corpus on this machine, and the ratio it costs is known rather than guessed | One more thing before the store is written — though the corpus is on disk, so it is a sweep, not a capture |
| **B — level 19, matching every existing number** | Every figure in `../../reference/measurements.md` stays directly comparable | ~29 bodies/second per thread. Ten to thirty times the owner's stated load, which is fine — until it is not, and nothing would say so |
| **C — level 3, matching the sketch's instinct for speed** | Effectively free compression; the worker could never be the bottleneck | Gives up an unknown amount of ratio, on a milestone whose whole claim is about size |
| **D — configurable, with a measured default** | The one knob where the right answer genuinely depends on the machine | A knob. `../../README.md`'s style rule prefers an obvious explicit choice to a general one |

---

### Q11 — Is the corpus's copy of a response a second buffer?

**In plain terms.** `observe.py`'s `BufferedScanner` **already** accumulates a non-streamed reply, up
to 1 MiB, so it can find `usage` at the closing brace. If the corpus tees its own copy, the same
bytes are held twice on that one path.

| Option | Buys | Costs |
|---|---|---|
| **A — separate buffers** *(assumed)* | The scanner keeps working unchanged when the corpus is off, which is the default. Two independent things stay independent | Up to 1 MiB held twice, on the non-streamed path only. Streamed replies are unaffected — the SSE scanner keeps a line buffer, not the body |
| **B — one shared buffer** | Half the memory on that path | Couples the recorder to the store. The scanner would have to buffer *because the corpus wants it to*, which is a dependency pointing the wrong way — and it changes `observe.py`, which this phase otherwise does not touch *(no longer true from 2026-08-18: Task 12 puts the request body and the response buffer on `Call`, which lives there. **The argument for keeping the buffers separate is unaffected** — it is about coupling the recorder to the store, not about which file is edited)* |

---

### Q12 — How is "did this ever come close?" answerable later?

> **Decided 2026-08-18: option A, plus one addition the options did not cover.** The owner widened
> the question from the corpus to loss generally — *how do I learn that some requests and responses
> were not saved, and why* — and asked the same of `calls.csv`. **Three of the four answers already
> existed; one did not.**
>
> | What was lost | How you find out | Change |
> |---|---|---|
> | A **body** | The ref cell says `dropped`, `too_large`, `absent` or `error`, per call, permanently | none — this is the design |
> | A **CSV row**, because the write failed | `stats.py` and `record()` each already log a `WARNING` and carry on | none |
> | A **CSV row**, because `record()` was never reached | **nothing says so today** — the Q2b blind spot, in complete silence | **one counter pair** |
>
> **`begin()` counts calls arrived; `record()` counts rows written.** The difference is calls in
> flight plus calls silently lost, so a gap that persists across summaries — or is non-zero after the
> queue drains at shutdown — makes the blind spot visible **without changing a column of
> `calls.csv`**, which the milestone's non-goals forbid.
>
> **Reserved to `../../backlog.md` rather than built**, on the owner's instruction that reserving is
> acceptable and over-engineering is not: a metrics or status endpoint for live visibility, a
> sequence column that would make a gap self-evident, and per-failure detail beyond the counters and
> the warnings already there. **The router never *skips a call* under load** — dispatch and relay
> always happen; only a record can be lost. That distinction is what makes this set sufficient.

**In plain terms.** The owner's decision of 2026-08-18: keep the prototype simple, **and make its
failure modes diagnosable**, so that the severity of queueing and dropping under real load is a
question the data answers months later rather than one somebody has to be watching to catch.

| Option | Buys | Costs |
|---|---|---|
| **A — three index columns and two log lines** *(assumed)* | `queue_ms`, `store_ms` and `queue_bytes` on every row, plus one drop warning per run and a periodic summary. Answers the question retrospectively, from data already being written, with no component added | The index goes from 22 columns to 25. They are appended, so the first twenty stay identical to `calls.csv`'s and in its order |
| **B — a metrics endpoint** | Live visibility while a session runs | A new route on a router whose catch-all forwards every path it does not recognise, for a question that is almost always asked afterwards |
| **C — counters at shutdown only** | Nearly free | Requires stopping the router to learn anything, and loses the per-call distribution — the tail is the whole story under load |
| **D — nothing; measure if it ever hurts** | Simplest possible prototype | *How bad did it get* becomes unanswerable, which is the specific thing the owner asked to avoid |

---

## The renumbering, and the permission — 2026-08-18

**Two owner instructions, taken together because the second is what makes the first safe.**

**Permission was given to run the benchmark group** — installing `zstandard` and running the script
over `logs/corpus-gate/`. Neither starts the router nor makes an API call, and the layer-3 check in
Task 18 still asks separately, because *consent for one is not consent for the next*.

**And the task list was renumbered**, dissolving `Group B0` and the lettered `3a`/`3b`/`3c` into a
straight 1 to 24 across six groups. **This is an exception to `../../README.md`, which says task
numbers are *"never renumbered once published"*, and it is recorded rather than quietly taken.**

**Phase 9 drew the same line one step earlier and gave the reason** — it renumbered *before
publication* because *"publishing it and then amending it would have spent letters on work nobody had
started"*. That reasoning applies unchanged here: **nothing has executed**, so no number has yet been
cited by a commit doing the work.

**One cost cannot be undone.** Four commit messages already in this branch say *"Task 1 of…"* and
*"Tasks 2 and 3 of…"* against the old numbering; git history is not editable. Tasks 1 to 3 kept their
numbers, so those citations remain correct — **which is luck rather than design, and would not hold
if a renumber were done again later.** From the first task that executes, the rule applies with no
exception.

**A question left for the owner rather than answered here:** `../../README.md` says *"once
published"*, and this phase has now treated the line as *once executed*. Those are different, and the
manual should say which it means. **Amending it is a method decision**, so it is raised rather than
made.

## The diagnostics interview, 2026-08-18

**A third pass, and the shortest.** The owner asked one general question — *what else needs logging
or recording so that loss is diagnosable* — with an explicit constraint: **KISS, this is a prototype
meant to be finished and used, and reserving features in the backlog is acceptable.** Five questions
were settled with it: **Q4, Q5, Q7, Q10 and Q12.**

**Two of the five reversed this plan's own recommendation**, and both reversals are simplifications:
one compression tool instead of two (Q5), and plain copies with no root dictionary folder (Q7). **The
second is the more interesting**, because the thing the owner removed — a root `logs/corpus/dicts/` —
was never in Phase 9's sketch. This plan added it to serve a hard-link optimisation, and when the
links were declined the folder had no remaining job. **A rejected optimisation left its scaffolding
behind, and the scaffolding read as part of the design.**

The general question added exactly one thing, the arrived-against-recorded counter pair, and sent
three more to `../../backlog.md`. The reasoning is under Q12.

## The write-path interview, 2026-08-18

**A second interview, after `plan.md` was committed and before any task ran.** The owner raised
performance under concurrent harnesses and **refused the GIL claim the design rested on**. Both were
right, and the second is the more serious: this file's first version said `zstandard` *"releases the
GIL"* as fact. That is documentation nobody had read and behaviour nobody had measured, and **if it is
false, one worker thread and eight worker threads are the same thread.**

### What the arithmetic changed

The concern was hundreds of parallel requests. The measured arrival rates are two orders of magnitude
below that, and the owner's real target — **one laptop, two to five concurrent harnesses** — comes out
at roughly **1–3 calls per second at a burst**, against a single thread's published ~29 bodies/second
at level 19.

**So the bottleneck ranking inverted.** Choosing the compression level buys 50–100×; adding four
workers buys 4×. **The level is the cheap lever and it is measurable today**, on the corpus already in
`logs/corpus-gate/`, with no capture and no live session. That became Q10 and the benchmark group.

**And at that load the binding constraint is not CPU at all.** Fifteen calls in flight holding request
and response bodies is a few megabytes; what protects the router above the ceiling is the **byte bound
and the drop policy**, not the worker count. More workers raise the ceiling at which dropping starts;
they do not change what happens above it, and the design has to be correct at that moment either way.

### Several router instances, and a proxy in front

Proposed by the owner as an alternative to more workers, and **deferred to `../../backlog.md`** rather
than adopted. Two reactions, and the first retires half of it.

**The session-distinguishing half is already solved, and measured.** `session_id` and `agent_id` are
copied from request headers by a dictionary lookup, and Phase 9's corpus carries **five distinct
sessions and ten subagent rows** through a single instance. Telling harnesses apart is not a problem
this router has.

**The throughput half has one concrete blocker, and it is not the proxy.** Every multi-process form —
several instances, `uvicorn --workers N`, or a process pool — hits the same wall: **the recorder's
writers are single-process designs.** `calls.csv` rides `RotatingFileHandler`, whose lock is a thread
lock; two processes rotating one file corrupt it. So multi-process means either giving each instance
its own log, CSV and corpus — **fragmenting exactly the telemetry the corpus exists to unify** — or
making the writers multi-process safe, which is a phase in itself.

That is worth knowing because it tells you which half is expensive: **the reverse proxy is the cheap
part.** A proxy would also have to key on `x-claude-code-session-id`, which it learns only after the
first request lands — solvable, and infrastructure, against a milestone whose claim ends *"without
special storage infrastructure"*.

### What it cost the plan

A benchmark group before any store code, the queue and index tasks widened, four decisions added,
and the GIL assertion demoted from a design premise to a row in "Documented versus measured" reading
**unverified**.

## Task 3a — the forward review: this session's pass

**Run 2026-08-18 against `plan.md` Tasks 4–24 per `review-charter.md`.** **Written before the
fresh-context run returned**, so nothing in this section is influenced by it or confirmed by it —
**the reconciliation is the section below**, and one finding here was refuted there. *(This paragraph
said "Unreconciled" as a status until the reconciliation landed the same day.)*

**The question this run answers** is whether the plan is consistent with what was decided. It cannot
answer whether the plan is legible to somebody who was not here; that is the other run's, and this
session is the worst possible judge of it.

### Findings

**1 · VERIFIED · No task builds the `manifest`.**
*Where:* `plan.md:106` draws it in every day folder — schema version, router version, dictIDs
referenced — and `plan.md:603` requires the layer-3 check to *see* one. **Tasks 8 and 10 build the
blob store and the index; neither mentions it, and no other task does.**
*Cost:* found at Task 18, where the check looks for a file nothing was chartered to write. Its
contents are a schema decision, so improvising it at that point is the worst moment to take it.

**2 · VERIFIED · Nothing says how the router finds the current dictionary at startup.**
*Where:* the tree at `plan.md:100–110` after Q7. **A grep for `newest`, `scan`, `at startup` returns
nothing about dictionary discovery**, and Task 8 says a day folder holds *"a plain copy of each
dictionary the day uses"* without saying **copied from where**. Task 14's trainer has the mirror
problem: no task says where it writes.
*Cost:* **this hole was created by a decision.** The root `logs/corpus/dicts/` was the answer to
*where does the router look*; removing it as scaffolding took the mechanism with it. It is the same
class as the leftovers already found, running in the opposite direction, and it is cheapest to close
now — at Task 8 it gets improvised.

**3 · VERIFIED · Task 7 duplicates Task 4.**
*Where:* Task 4 is `uv add zstandard`, which writes `pyproject.toml` and syncs. Task 7 opens *"Add
`zstandard` to `pyproject.toml`; `make sync`"*. **Both were true before the benchmark group existed**;
inserting Task 4 took over the first clause of what is now Task 7.
*Cost:* trivial to fix, and it is exactly the leftover class this review exists to catch.

**4 · VERIFIED · Nothing freezes the benchmark's results into `evidence/`, and nothing says why the
directory is absent.**
*Where:* `evidence` appears once in `plan.md`, inside a quotation about *Phase 9's* evidence README.
Task 5 puts the script in `procedures/`, Task 6 runs it, and its output lands under `logs/`, which is
gitignored. `../../README.md` is explicit — an instrument's script goes to `procedures/` but *"its
results are frozen in the phase's `evidence/`"* — and equally explicit that where a phase has no
`evidence/`, **its `notes.md` says why.**
*Cost:* high, and it lands at Task 24. Task 21 puts the benchmark's numbers in
`../../reference/measurements.md`, whose whole rule is that a number carries its instrument and its
slice. Phase 9 froze `gate.py` and `results.txt` for exactly this reason.

**5 · VERIFIED · Task 18's layer 3 reopens a decision the scope closed, and this file does not
reconcile them.**
*Where:* the settled table records a scope with **no live driven session**. `plan.md:603` requires
the router *started, driven, and stopped*. The plan says only that layer 3 *"needs its own consent"*.
*Cost:* it is an owner decision being re-opened by a task added later, which is precisely what the
settled table exists to prevent. Either layer 3 is out of scope and the configuration check is weaker
than advertised, or the scope carries an exception nobody wrote down.

**6 · VERIFIED · The corpus's treatment of bodies the router *authored* is unstated — and a precedent
already answers it.**
*Where:* three bodies are the router's own: the 400 for a missing `model`, the 502 for an unreachable
backend, and the injected SSE `error` event. The milestone's claim is *"every body it **carries**"*.
**`../../reference/design-decisions.md` already ruled on the identical question** for the injected
event — *"not counted in `response_bytes` and not fed to the scanner … both measure what the backend
sent, and these bytes are ours"*. The plan neither applies that rule nor cites it.
*Cost:* moderate, and it decides what a corpus row **means**. Cheap now, and a silent inconsistency
with a decided rule if it is settled at Task 12 by whoever is typing.

**7 · VERIFIED · The timing columns are undefined for a body that was never stored.**
*Where:* Task 10 defines `queue_ms`, `store_ms` and `queue_bytes`. For a `dropped`, `too_large`,
`absent` or `error` row, `store_ms` describes work that did not happen. `../../reference/observability.md`
already has the governing rule — **an absent value is an empty cell, never a zero** — and Task 10 does
not invoke it.
*Cost:* low, but it is the index's schema and Task 10 is where it is fixed for good.

### Questions for the owner

1. **What is the valid range for `compress_level_zstd`?** Task 11 tests *"out of range"* without
   saying what the range is. `zstd` accepts 1–19 ordinarily, up to 22 with `--ultra`, and negative
   fast levels. Rejecting what the library would accept is as much a defect as accepting what it
   would not.
2. **Does driving the router for the configuration check count as the live session the scope
   excluded?** Finding 5. My reading is that it does not — the exclusion was about *driving real
   coding sessions to measure whether archiving slows a call*, and this is a handful of calls to see
   files appear — but that is my reading of your decision rather than your decision.

### What I checked and found correct

| Claim | Result |
|---|---|
| `stats.py`'s `COLUMNS` has 20 entries | ✅ 20, read by importing it |
| Every config model forbids unknown keys | ✅ all six subclass `Strict`, `config.py:34–127` |
| `RotatingFileHandler`'s lock is a thread lock | ✅ `logging.Handler` creates a `threading.RLock`, so the multi-process claim holds |
| `Proxy.record()` has four call sites, one per row-producing path | ✅ `proxy.py:140, 156, 205, 270` |
| Both telemetry handlers create their parent directory | ✅ `logging_setup.py:74` and `stats.py`, so `logs/telemetry/` needs no task of its own |
| Every task reference resolves to 1–24 or 3a; every group letter to A–F | ✅ mechanical pass, one defect found and fixed at `f6277dd` |
| Surviving mentions of rejected options sit inside decision records | ✅ checked individually — `os.link`, hard links, APFS, "22 columns", `Group B0` |

**Nothing was found wrong in Groups D or E**, and that is stated rather than left as silence.

## Task 3a — the fresh-context pass, and the reconciliation

**The agent returned 2026-08-18: nineteen findings, five questions, and a task-by-task executability
verdict.** It was given `review-charter.md`, both documents and the repository, read-only, with no
answer key. It read `src/` rather than the plan's account of `src/`.

### It refuted a claim this session had made twice and filed in `../../backlog.md`

**The blind spot does not exist as described, and six measured rows say so.**

This session wrote, in `plan.md`, in finding 2b above, in Q2b, and in a parked `../../backlog.md`
item: *a caller that disconnects after the response headers reaches none of `record()`'s call sites,
so that call gets no CSV row today.*

**It reaches `proxy.py:270` and it gets a row.** Re-verified here rather than taken on trust:

| Check | Result |
|---|---|
| `proxy.py:249` | catches `asyncio.CancelledError` and `GeneratorExit`, sets `client_disconnect`, **re-raises** |
| `proxy.py:268–270` | the `finally` runs on that re-raise and calls `self.record(call, scanner)` |
| `../../reference/measurements.md` | **6 `client_disconnect` rows, 5 LM Studio and 1 Anthropic** — *"starlette reaches the disconnect path **reliably** on both backends"* |
| `../../milestone-1-core/phase-2-observability/evidence/step-6-session/calls.csv:79` | `response_bytes=10027`, `ttfb_ms=48050`, `error_status=client_disconnect`. **Headers had gone out and 10 KB had streamed. The row exists** |

**What is true is far narrower**: only if the generator is closed *before its first `__anext__`* is
there no frame to throw `GeneratorExit` into, so `aclose()` runs no code and the `finally` never
fires. That is the race `proxy.py`'s `BackgroundTask` comment reasons about, and **it has never been
observed here.**

**How the error was made, because that is the reusable part.** The comment at `proxy.py:222–224`
describes the narrow case; this session **generalised from it to the whole disconnect-after-headers
class without checking the measured rows** — which sit in `measurements.md` under a slice that names
exactly this. It was labelled *Inferred*, which was honest, and inference from a correct premise to a
wrong conclusion is not repaired by labelling it.

**Consequence beyond the correction:** the counter pair's stated justification was this hole. The
hole is a microsecond race nobody has seen, not a class of calls. The counters still measure
something real, but **the case that bought them is much weaker than it looked**, and that is a
question for the owner rather than a finding.

### The merged work list

**Twenty-two distinct items from two runs, four of them found by both.** Overlap ran at 18%, which is
the argument for two passes rather than one.

| # | Finding | Found by |
|---|---|---|
| **1** | The disconnect blind spot is overstated; four documents say it wrongly | **agent** |
| **2** | No dictionary source, path or bootstrap — and `../implementation-plan.md` names "dictionary bootstrap" as this phase's to settle. Group C runs before Group D, so the store must work with **no** dictionary, a mode never described; Task 13's round-trip has nothing to round-trip against; `logs/corpus-gate/dicts/` holds **eight**, so "the held-out dictionary" is under-specified | **both** |
| **3** | The counter pair lives in `corpus.py`, which is **opt-in and off by default** — so on the default machine, the plan's only answer to *did I lose a CSV row* does not exist | **agent** |
| **4** | No task builds the `manifest` the tree draws and Task 18 checks for; its format is unspecified and *"dictIDs referenced"* implies a second concurrent writer | **both** |
| **5** | Task 18's layer 3 drives the router; the settled scope excluded a live driven session | **both** |
| **6** | *"Task 7's smoke test is where the GIL surfaces"* — a leftover from before the benchmark group; three other places correctly say Tasks 4 and 6. **If believed, an agent skips the measurement and reads a green round-trip as verification** | **agent** |
| **7** | Task 18 asserts `make test`'s **158** unchanged, while Tasks 11 and 13 add tests | **agent** |
| **8** | Task 12 requires editing `observe.py`, which Q11 says this phase *"otherwise does not touch"*; `cli.py` must change for `--check` and appears in no list | **agent** |
| **9** | Nothing freezes the benchmark's results into `evidence/`, and nothing says why the directory is absent | **this session** |
| **10** | Task 5's *"writes under `logs/`"* contradicts `../../README.md:120` — *an instrument's output directory follows the instrument* — and the exception is taken silently | **agent** |
| **11** | The queue item `(CallRecord, request, response)` **cannot produce `queue_ms` or `queue_bytes`** — both need values captured in `submit()`. Read in the worker instead, `queue_bytes` measures depth at *dequeue*, which is near zero at this load and **looks correct** | **agent** |
| **12** | Bodies the router *authored* — the 400, the 502, the injected SSE `error` — are unaddressed, though `../../reference/design-decisions.md` already ruled on the identical question | **this session** |
| **13** | The placeholder table says **six** group headings carry `*(not started)*`; **five** do. Group A's `*(executed, except 3a)*` is a placeholder, is uncatalogued, and **the prescribed grep cannot match it** | **agent** |
| **14** | `plan.md:6` says twenty-four tasks, `plan.md:456` says twenty-five. **Twenty-five is right** | **agent** |
| **15** | The *"periodic `INFO` summary"* has no period, no mechanism and no home — named four times, defined never | **agent** |
| **16** | Task 6's **negative** branch has no task, no gate and no consequence, while Tasks 8–13 assume the positive one. Symmetrically, a `workers` key is promised on one outcome and refused by Task 11 | **agent** |
| **17** | Task 17's sweep omits `../../procedures/link-check.py:45`, a live citation of `logs/calls.csv` **inside the instrument Task 24 runs** | **agent** |
| **18** | No task adds the two new procedures to `../../procedures/README.md`'s index, though Task 19 does the analogous thing for `reference/` | **agent** |
| **19** | Tasks 4 and 7 both add `zstandard`, with no note that the second finds it done | **both** |
| **20** | The memory table says the request body *"is not changed by"* the corpus. Its **lifetime** is — from freed when `relay()` returns, to held until `record()`, which on LM Studio is minutes. The plan says this correctly 80 lines later | **agent** |
| **21** | The three timing columns are undefined for a body that was never stored | **this session**, and the agent's guess list |
| **22** | `review-charter.md:128` says **72** on this branch; it is **78**, and the bullet two clauses earlier says *do not predict the count* | **this session's error, agent-reported** |

### Executability — the verdict only the cold run could give

| Group | Verdict |
|---|---|
| **B** (4–6) | Executable today. Task 6's measurement table is *"the best-specified thing in the plan"*. Two holes: which of eight dictionaries, and the undefined negative branch |
| **C** (7–13) | **The weakest group, and not finishable from these documents.** Task 8 cannot complete — no dictionary source, no manifest. Task 9 lacks the timestamp, the period and the corpus-off behaviour. Task 12 contradicts Q11 and does not say where the tee is held |
| **D** (14–15) | Task 14 clear; **Task 15 not executable** — *"install it"* has no destination |
| **E** (16–17) | **The most executable pair.** The file list re-derived by grep and found exact, one omission |
| **F** (18–24) | Clear except where earlier gaps surface. Task 18 is *"the plan's strongest section"* and carries three of the defects above |

**Thirteen things the agent had to guess** are listed in its report; the load-bearing ones are which
dictionary, where it lives, what the store does before one exists, what writes the manifest, how
often *periodic* is, and whether the response tee runs when the corpus is off.

### What both runs checked and found correct

**All eight `src/` claims were re-verified from source by the agent**, independently of this session's
own pass. Seven held exactly, including every line number; the eighth is item 1 above. It also
confirmed `EPD-003`'s open questions 3–6 map correctly onto the decision table, that
`../../backlog.md` already holds all five reserved items, that `.gitignore:228` covers the corpus,
and that `logs/corpus-gate/` holds three runs and eight dictionaries with **responses as well as
requests**, so Task 6 can sweep both.

### What this cost, for `IDM-004`

**The fresh run found fifteen items this session did not, including the refutation of a claim this
session had filed in three documents and the backlog.** This session found three the agent did not,
all of them about *the record* — `evidence/`, router-authored bodies, and an index-schema rule — which
is the class that needs knowing what was decided.

**The two runs divide along exactly the line the charter predicted**, and that is the finding
`IDM-004` is written from: **the author's pass catches inconsistency with decisions; the cold pass
catches everything the author cannot un-know.** Neither is optional, and the cold pass is the one that
found the false claim.

### `IDM-004`, written from what this cost

**`../../method/IDM-004-reviewing-unexecuted-work.md`, in force 2026-08-18.** Written after the run
rather than before it, on the owner's ordering and on `../../README.md`'s own playbook rule — *write
this playbook last, from what it cost*. `review-charter.md` is the worked example it points at, and
this section is its evidence.

**What generalised**, and it is less than was expected: the boundary against the closing review, the
charter-first iteration, the two questions, parallel-not-serial, and six rules. **What did not
generalise is the numbers.** 22 findings, 18% overlap and ~152k tokens are one measurement of one
review of one document by one agent, and `IDM-004` says so in a section headed *"One thing that is not
evidence yet"* — a second run returning 60% overlap would be evidence that one run is enough, and that
section would need rewriting rather than defending.

**The finding that justified the protocol on its own** is the refuted claim: inferred, labelled
honestly as inferred, written into four documents, and false. `IDM-004` carries it as three rules —
labelling an inference does not protect it; the author could not have found it, having repeated it
twice since; and **a wrong claim spreads at the speed of citation**, which is why the review comes
before execution rather than after.

## Task 4 — the dependency, and the GIL claim settled — 2026-08-18

**The first task of this phase to execute since Group A, and the first to change a tracked file
outside `docs/`.** Consent for the install was given the same day, on the standing rule that touching
the machine is asked for separately each time.

`uv add zstandard` resolved 30 packages and installed **`zstandard==0.25.0`**, one new runtime
dependency. `pyproject.toml` carries a comment saying why, in the shape Phase 6 set for `pydantic`
and `starlette` — a new runtime dependency is a decision, and the file is where the decision is
legible to somebody who was not here.

### The claim this task existed to settle

`plan.md`'s "Documented versus measured" carried **`zstandard` releases the GIL during compression**
as *unverified — and it is load-bearing*, because if it is false then one worker thread and eight are
the same thread and Group C's design is wrong. **It is true, and it is now verified rather than
asserted.**

**Which backend runs, first, because the answer differs by backend.** `zstandard/__init__.py` selects
`backend_c` for CPython and falls back to `backend_cffi` only on PyPy or an unknown implementation —
*"for CPython we require the C extension by default"*. So the C extension is the code path here, and
the CFFI backend's behaviour is not this project's question. **The one way that changes** is the
`PYTHON_ZSTANDARD_IMPORT_POLICY` environment variable, which can force the fallback; nothing here
sets it, and if anything ever does, this finding needs re-deriving.

### What was read, and what it establishes

**The wheel ships no C sources — only `backend_c.cpython-313-darwin.so`.** So the source was read
**as the shipped binary** rather than as `c-ext/compressor.c`, and that difference is stated rather
than glossed. What it costs: no C source line to quote. What it buys, and it is the larger half:
**this is the exact code that will run in the worker thread**, not the code a source tree says would
be compiled. A source read establishes intent; this establishes fact.

`Py_BEGIN_ALLOW_THREADS` and `Py_END_ALLOW_THREADS` are macros expanding to `PyEval_SaveThread()` and
`PyEval_RestoreThread()`, which survive compilation as linker-visible symbols. Both appear, and they
are the **only** `PyEval` symbols the extension imports at all.

The one-shot compress path — the call the write path will make — disassembles to exactly the macro
pair wrapped around the work:

```
_ZstdCompressor_compress            0x8c574
  8c690:  bl 0x90774  →  _PyEval_SaveThread          GIL released
  8c6a8:  bl _ZSTD_compressStream2                    the compression itself
  8c6b4:  bl 0x90768  →  _PyEval_RestoreThread        GIL reacquired
```

Both stub addresses were resolved through the Mach-O indirect symbol table rather than guessed:
`__stubs` begins at `0x90678` with 12-byte entries, making `0x90768` index 20 and `0x90774` index 21,
which `otool -Iv` names as `_PyEval_RestoreThread` and `_PyEval_SaveThread`.

### Every function that releases it, because one function is not an answer

A sweep of the whole disassembly, rather than the single path the plan needed, found **21 functions**
releasing the GIL — and **`SaveThread` and `RestoreThread` counts match exactly in every one of
them**, which is the property worth checking: an unbalanced pair would leak thread state rather than
merely fail to parallelise.

| Path | Function | Matters to |
|---|---|---|
| One-shot compress | `_ZstdCompressor_compress` | **The write path.** Task 9's worker |
| One-shot decompress | `_Decompressor_decompress` | Task 13's round-trip, and any reader |
| **Dictionary training** | `_train_dictionary` | **Group D.** Not required by the design, but it means Task 14's trainer cannot freeze an interpreter either |
| Streaming and chunked, both directions | `_ZstdCompressionObj_compress`, `_ZstdCompressionWriter_write`, `_ZstdCompressionChunkerIterator_iternext`, `_ZstdDecompressionWriter_write`, and the rest | Nothing this plan builds — recorded so a later phase that streams does not re-derive it |
| Batch | `_compress_from_datasources`, `_decompress_from_framesources` | `multi_compress_to_buffer`, which this phase does not use |

**`_train_dictionary` was not on anyone's list and is the incidental find.** Training is deliberately
never in a worker — `plan.md`'s "One thing that is never in a worker" — so this changes no decision.
It is recorded because the reason training is kept out is that it takes seconds to minutes, and *"it
would hold the GIL"* is now known **not** to be a second reason. If that argument is ever made, it is
wrong.

### What this settles, and what it does not

**Settled:** the mechanism. The GIL is genuinely released around libzstd, so a worker thread is a
real thread and Group C's design is not resting on a false premise. **The negative branch of Task 6 —
where the thread design is withdrawn and a process pool is measured — is now very unlikely to be
taken.**

**Not settled, and Task 6 still runs unchanged:** *released* is not *scales*. Whether four threads
finish the corpus in about a quarter of the time is a measurement, and the GIL is only one of the
things that could stop it — the per-call Python overhead outside the released region, allocation, and
the disk are all still unmeasured. **`plan.md` asks Task 6 for the scaling numbers and that is not
weakened by this result.** It is also the task that picks `compress_level_zstd`'s default and
compares `zstandard`'s trainer against `zstd --train`, neither of which this task touches.

`plan.md`'s "Documented versus measured" row is updated in place from **unverified** to what was
found, with the method named.

### Baselines, re-derived by running them

| | Before Task 4 | After |
|---|---|---|
| `make test` | **158 passed, 0.65 s** — run first, which also warmed the venv so the install was not confounded with OneDrive hydration | **158 passed, 0.70 s.** A new runtime dependency changed nothing |
| `make check` | — | Valid; every key resolves and prints. **No `corpus:` block yet** — that is Task 11 |
| `link-check.py` | **79 broken, 2 roundabout** | **80 broken, 2 roundabout, 74 files** |

**The extra broken link is this session's own and it is the expected class.** `status.md:152` now
cites `docs/procedures/corpus-benchmark/`, which **Task 5 creates** — a forward citation, which
`../../backlog.md` records as the recurring false-positive class and which `plan.md` predicts will
*"have resolved themselves"* by Task 24. **The count going up at this point is correct**, not a
regression: it falls as Group B's and Group D's tasks create their directories.

**The file count is 74**, against the 70 recorded at the re-derivation — `review-charter.md`,
`IDM-004` and the rest of Group A's output. The broken count is what moves with citations; the file
count moves with documents, and neither predicts the other. **Run it; do not predict it.**

### One thing offered and not done

**The C source was not fetched.** `c-ext/compressor.c` would give a quotable `Py_BEGIN_ALLOW_THREADS`
line, at the cost of a second network fetch for weaker evidence than the binary already gives. It is
available on request if the record should carry the source line as well as the instruction.

## Task 5 — the instrument — 2026-08-18

`docs/procedures/corpus-benchmark/`, holding `benchmark.py` and a `README.md`, with
`docs/procedures/corpus-benchmark/runs/` added to `.gitignore` as an **explicit per-instrument entry**
rather than a `docs/procedures/*/runs/` glob — the shape the two existing entries already set, and a
glob would silently start covering an instrument nobody had decided should be ignored. A row is in
`../../procedures/README.md` saying when re-running is worth it.

**Two corpora, and the script labels which produced each number.** Ratios come from `gate.py`'s rule
and split exactly — `/v1/messages` requests over 1 KB, trained on run-01 + run-02, evaluated on
run-03 — so they are comparable with Phase 9's. Throughput and scaling come from every body in every
run, both directions, which is the realistic write-path mix and yields no comparable ratio at all.

**One defect found by running it, which reading it would not have found.** The README first said
`python3 benchmark.py`. On this machine **`python3` is 3.14 and the venv is 3.13**, and `zstandard`
is in the venv — so the bare interpreter raises `ModuleNotFoundError`. Every sibling instrument here
is stdlib-only and runs either way; this is the first that does not. Corrected to `uv run python` in
both the README and the docstring, and written down because **the failure looks like a missing
dependency rather than the wrong interpreter.**

## Task 6 — the numbers, and the four things they decide — 2026-08-18

**Run 2026-08-18. Frozen into `evidence/` with its own README** — the script, its verbatim output, and
what it does and does not establish. That directory exists because the forward review found nothing
froze the results and nothing said why it was absent.

**Permission was on record** from 2026-08-18 to run the benchmark over the corpus already in
`logs/corpus-gate/`. It started no router, drove no session and made no network call.

### 1 — The GIL is released, and the thread design stands

| threads | level 19 wall | speedup | efficiency |
|---:|---:|---:|---:|
| 1 | 1.730 s | 1.00x | 100% |
| 2 | 0.950 s | 1.82x | 91% |
| 4 | 0.519 s | **3.34x** | 83% |

**Task 4 read it off the binary; this measures it, and they agree.** Level 3 scales the same way
(3.43x at four threads). **Task 6's negative branch is not taken:** the thread design is not
withdrawn, no process-pool measurement is needed, and Group C proceeds as planned.

### 2 — `compress_level_zstd` defaults to 9, measured rather than assumed

Ratio on the held-out slice, throughput on the full load set, one thread:

| level | dict | ratio | MB/s | bodies/s |
|---:|---|---:|---:|---:|
| 3 | no | 2.80x | 283.3 | 5181 |
| 3 | **yes** | **9.25x** | 727.3 | 13302 |
| 9 | no | 3.00x | 54.5 | 997 |
| 9 | **yes** | **10.28x** | 162.5 | 2971 |
| 19 | no | 3.12x | 4.2 | 77 |
| 19 | **yes** | **10.95x** | 15.0 | 274 |

**Level 9 holds 94% of level 19's dictionary-assisted ratio for an eighth of the per-body cost**, and
one worker at level 9 runs ~2,971 bodies/s against the owner's stated peak of 1–3 calls/s — roughly
**500x headroom**. Level 19 buys 6.5% more ratio for 8.0x the CPU, and its p95 compress is 11.6 ms
against 1.5 ms. **The plan's placeholder default of 9 is confirmed by measurement**, which is not the
same as having been right by luck: nobody had measured it.

**And the half nobody had asked is answered.** The dictionary is worth far more than the level —
3.12x to 10.95x at level 19, 3.00x to 10.28x at level 9. **Choosing the dictionary well matters more
than choosing the level well**, which inverts where the tuning effort belongs.

### 3 — `store_ms` is not one thing, and the level decides which

Median per body, with the dictionary:

| | level 3 | level 9 | level 19 |
|---|---:|---:|---:|
| sha256 | 4.6% | 2.1% | 0.3% |
| **compress** | 17.9% | **40.4%** | **90.5%** |
| write + fsync + rename | 77.4% | 57.5% | 9.2% |
| **total** | **0.235 ms** | **0.433 ms** | **3.483 ms** |

**At the chosen level the filesystem is the majority of `store_ms`, not compression.** That matters
for reading the column later: a `store_ms` that climbs is more likely the disk than the compressor.
**`fsync` is cheap here (~0.03 ms) and `rename` is not (~0.12 ms)** — worth knowing, because the
write path does one of each per body and the sketch assumed `fsync` was the expensive one.

**The ratio columns are deterministic and reproduce exactly; the timing columns do not** — they move a few percent between runs, and the figures here are the frozen run in `evidence/`. The scaling table is best-of-three for that reason, after a single pass put the four-thread speedup anywhere between 3.3x and 4.0x purely from noise in the baseline it divides by.

*These were measured writing real files into `logs/`, which is where the store will write — not into
a system temp directory on another filesystem. On this machine `logs/` is inside a cloud-synced
folder, so this is a measurement of this setup rather than of the disk. It is the number the router
would actually pay here.*

### 4 — No `corpus.workers` key, and the plan's live contradiction is resolved

`plan.md` promised the knob **only if** Task 6 showed the GIL released **and** more than one worker
helping, while Task 11 fixed the block at five keys — and said *"either outcome falsifies one of those
two sentences."* **It is the first sentence that gives way.** The GIL is released, so the condition's
first half is met; but one worker at level 9 already carries ~500x the peak load, so **a second worker
helps with nothing**. Configuration this project does not need is configuration it does not get.
**Task 11 stays at five keys, unchanged.**

### 5 — The trainers disagree, and the parameter matters more than the tool

**This is the finding that nearly went the other way, and the reason it is worth stating carefully.**
The first run compared the two trainers at their defaults and said the library is **worse**:

| maxdict | `zstd --train` | `zstandard`, default k |
|---:|---:|---:|
| 112,640 | 10.95x | 10.35x *(−5%)* |
| 262,144 | 12.04x | 10.29x *(−15%)* |
| 524,288 | 12.10x | 11.48x *(−5%)* |

**Reported there, it would have read as a case for reversing Q5** — the owner's "one tool" decision —
on the ground that the library gives up ratio. **It does not.** `zstandard.train_dictionary()` uses
**COVER** and, asked to pick `k` itself, picks a poor one on a corpus this small; `zstd --train`
defaults to **fastcover**. Setting `k` explicitly reverses the result:

| maxdict | `zstd --train` | `k=2000` | `k=8000` | `k=16000` |
|---:|---:|---:|---:|---:|
| 112,640 | 10.95x | 10.32x | **11.08x** | 9.39x |
| 262,144 | 12.04x | 13.31x | **13.65x** | 13.70x |
| 524,288 | 12.10x | 13.30x | **13.62x** | 13.60x |
| 1,048,576 | 12.10x | 13.30x | **13.62x** | 13.60x |

**So Q5 survives and is strengthened — with one new requirement.** One tool is right; `zstandard` is
not worse; but **Task 14's trainer must set `k` explicitly**, and the library's own optimiser is a
trap that costs up to 15%. That is a constraint on Task 14 that no document carried before today.

**Non-monotonicity is confirmed on a second instrument.** At `maxdict=112,640` the ratio peaks at
`k=8000` and falls to 9.39x at `k=16000`; `maxdict` above 262,144 buys nothing. Phase 9 found this in
`zstd --train`; it is a property of training at this sample count, not of either tool. **This is
exactly why Task 14 measures a candidate against the incumbent and refuses a worse one.**

**For Task 15: `--maxdict=262,144` at `k=8000` is the current best** — 13.65x, and the 524 KB and
1 MB settings match it while producing a larger file. **It is not yet a recommendation**, for the
reason below.

### The caveat that limits all of section 5, stated rather than buried

**There is no usable validation split in this corpus.** Splitting run-01 to train, run-02 to validate
and run-03 to test gives a validation set of **two bodies** — run-02 has three calls, two of which
qualify — and its ratios come out above 200x, which is memorisation, not evidence.

**So any `k` read off the table above was chosen with knowledge of the test slice.** The *ranking* is
stable across both slices and the plateau is real, but **the exact optimum is not established here**,
and Task 15 must not present one as if it were. The honest options for Task 15 are leave-one-session-out
across the five sessions the corpus carries, or naming the choice as provisional. **It is written down
now because it is the kind of thing that becomes invisible once a number is in
`../../reference/measurements.md`.**

### One number this does not license

**Phase 9's 12.10x remains the figure the milestone quotes, and it remains optimistic.** The 13.65x
above is **not** a replacement: it carries all three of the biases the slice note in
`../../reference/measurements.md` names — headless corpus, ~28 KB smaller preamble than interactive,
70 of 73 bodies Anthropic — **plus a fourth**, that its parameter was chosen against the slice it is
reported on. Task 21 puts these numbers in the register with all four columns, and that is where the
slice travels with the number.

## The retraining interview, 2026-08-19

**A fourth interview, and the first to reverse a position this plan had been treating as settled.**
The owner asked a plain question — *how do you plan to run dictionary training: threads, processes,
who controls it, how do you know a new dictionary is ready, and how do you check it beats the old
one?* — and the answer this file could give was **manual, offline, run by a person**, which is what
`plan.md`'s "One thing that is never in a worker" says.

**That was never the owner's decision.** It is this plan's own prose. It does not appear in "What is
settled, and by whom", no interview produced it, and **neither forward-review pass questioned it** —
both checked the plan against the code and against itself, and neither asked *who decided this*.
`../implementation-plan.md` names *"a dictionary bootstrap and retraining policy"* as something this
phase must settle; the plan settled the bootstrap and the refusal rule and left the policy half
unwritten. **The owner had assumed retraining was automatic all along.**

**This is a defect class, not an incident**, and it is why point 5 below goes to `../../backlog.md`
as a method item: a plan that carries an explicit *"settled, and by whom"* table makes the check
mechanical — any load-bearing position **not** in that table is the plan's own assumption, and a
review that inherits it silently has skipped a step no amount of self-consistency checking will
catch.

### What was decided

| | Decision | What was offered and declined |
|---|---|---|
| **Who triggers training** | **The router, automatically.** Not a person | Manual-only, which is what the plan said and what a session would have built |
| **Trigger timing** | **Measure the training wall clock first, then choose** between startup-only and startup-plus-day-rollover | Committing to rollover now. Declined on the same grounds Group B exists: the number is unknown and the design should not be argued from a guess |
| **Manual command** | **`--train-dict`**, beside `--check`. It works even when automatic retraining is disabled | Automatic-only. Typing the command is explicit consent; refusing it would leave a machine that opted out of automation unable to train at all |
| **Window** | **Rolling, `retrain.window_days`, default 1.** **`0` disables automatic retraining** and the router keeps using the newest dictionary already installed | A separate `retrain.enabled` boolean, which `0` makes redundant. The owner's encoding **removed** a key rather than adding one |
| **Sample rule** | **Size only — no path filter.** `retrain.sample_min_bytes`, default 1024 | Filtering to `/v1/messages` as well. **Measured to be a no-op** — see below — and the path filter would have excluded `count_tokens` requests, which carry the same preamble and are ideal material |
| **Parameters** | **`retrain.maxdict` (262,144) and `retrain.k` (8,000)**, both **provisional**, both overridable per run by a CLI flag. `d` is fixed at 8 as a module constant | Hard-coding them. The right values depend on the operator's own corpus, which is what the sweep tool is for |
| **Config shape** | **A nested `corpus.retrain:` block.** Five write-path keys stay top-level; the four offline settings group beneath | Nine flat keys. Nesting is what `backends`, `logging` and `stats` already do, and it separates settings that touch a live call from ones that never do |
| **Pickup on a running router** | **The worker rescans `<dir>/dicts/`** — on opening a day folder and every N bodies — and swaps when the newest differs from what it loaded | An in-process slot published by the training thread. **This was this session's own proposal and it is wrong**; see the corrections below |
| **Comparison** | **Leave-one-session-out, held-out slice from the newest day**, margin required, refusal recorded | Scoring on the training material, which inverts the refusal rule; see below |
| **Install** | **`dicts/.incoming/` → fsync → rename**, the discipline the blobs already use. Refusals recorded too | Writing in place. A router starting mid-write would read a truncated dictionary |
| **dictID** | **In the dictionary's filename**, libzstd-assigned. Plus a **26th index column**, `request_dict_id` | Setting `dict_id` explicitly, which has to dodge collisions across machines and buys nothing the filename does not |
| **Sweep tool** | **A mode of the trainer, `--tune-dict`**, never a separate instrument, and it never installs | A second tool. Task 6 already found what happens when two things that should agree do not |
| **Extraction** | **The reader ships in this phase**; the tool built on it is Phase 11's | Deferring all of it. Training cannot read its own samples without decompressing blobs, so the reader is not optional here |
| **Responses** | **Still undicted.** Parked in `../../backlog.md` | Training a response dictionary in this phase |
| **Self-restarting router** | **Rejected** | Restarting to pick up a dictionary. It severs live SSE streams mid-generation; the swap touches one object, a restart touches every open connection |

### Four things measured during the interview, none of which needed a new instrument

**1 — The path filter is a no-op on this corpus.** Every request body of 1,024 bytes or more, across
all three runs, is already a `/v1/messages` body. The only other path is `/api/hello`, whose five
requests are **0 bytes**. So size-only and size-plus-path select the identical 68 samples, and the
comparability cost of dropping the path filter — that 12.10x and 13.65x were measured under the
narrower rule — **does not exist**: the sample set is byte-for-byte the same one they were measured
on.

**2 — The duplicates in this corpus are retries after `overloaded_error`.** 73 request bodies, **47
distinct**; five groups of duplicates covering 31 bodies, the largest being one 103,935-byte body
sent **11 times** inside a single session and another sent 9 times inside a second. Every one of
those eleven calls returned 119 bytes reading
`{"type":"error","error":{"type":"overloaded_error",...}}`. The harness resent the identical body
after each refusal. **This was not known and no document recorded it.**

**3 — The duplication is concentrated in the training slice.** `run-01` is 49 bodies / **25
distinct**; `run-02` is 3 / 3; `run-03` — the held-out test slice — is 21 / **21**. So the slice the
dictionary is scored on has no duplicates at all, while the slice it was trained on is nearly half
repeats.

**4 — `gate.py` did not deduplicate.** Read, not inferred: `load()` appends one path per manifest
row, `train_paths` is that raw list, and it goes to `zstd --train` unchanged. No `hashlib`, no `set`.
Measured on its exact rule: **48 training bodies, 26 distinct — 46% repeats.**

**The owner declined a rerun to size the effect**, on the ground that these sessions were too short
for the numbers to be more than approximate and that they carry enough accuracy to execute against.
**Recorded as a decision rather than an omission**, because the alternative reading — that nobody
noticed — is exactly what this file exists to prevent. What follows from it: **Task 21 states the
training-set composition in the slice column** so the number travels with how it was produced.

### Two corrections this session made to its own proposal

**The in-process slot was wrong, and the manual command is what exposed it.** The first design had
the training thread publish a dictionary path into a slot the worker reads. **A manual `--train-dict`
runs in a different process and cannot reach that slot**, so a hand-trained dictionary would land in
`dicts/` and a long-running router would never see it — reintroducing the exact failure the swap
existed to prevent, through the feature that makes it useful. **The worker watching the directory
serves both paths with one mechanism**, and the trainer then publishes nothing at all: it writes a
file, and that is the whole interface.

**Deduplicating before training was already solved by the store, and the owner caught it.** This
session carried "walk the index and dedup by ref digest" as a required step after finding the retry
storm. But **content addressing means the store holds one blob per distinct body**, so a trainer
reading `<day>/requests/` cannot see a duplicate at a one-day window even if it wanted to. The
residual need is narrower than stated: **the store deduplicates per day by design**, so only a
multi-day window can reintroduce duplicates, and there the filename *is* the digest, so it costs one
`set()`. **The retry-storm risk was correspondingly overstated** — a day with an `overloaded_error`
storm writes one blob, not eleven. Phase 9's corpus shows 38% duplication only because
`logs/corpus-gate/` was a raw per-call capture with no content addressing.

**And deduplication loses no information**, which is worth stating because it is easy to assume
otherwise: the index keeps one row per call, all carrying the same digest, so *this body was sent
eleven times in four minutes* stays fully recoverable. The bytes collapse; the multiplicity does not.

### The comparison, and why the obvious form inverts the rule it implements

**Train on a day and score on that same day, and the candidate always wins** — it has seen those
bodies and the incumbent has not. That does not weaken Task 14's refuse-a-worse-one rule, it
**reverses** it: a worse dictionary would be installed daily while each run logged an improvement.

**With a rolling window the opposite bias appears.** Yesterday's incumbent was trained on days
N-8…N-2, so a held-out slice drawn from anywhere inside the window is material the *incumbent* has
already seen — and now the comparison flatters the incumbent and refuses good candidates forever.

**So the held-out slice comes from the newest complete day only**, which is the sole material the
incumbent certainly has not seen, and which the candidate excludes by construction. **At the chosen
default of one day this is the clean case**, since the window and the newest day are the same thing.

### How it runs, and what it is not

**There is no "call thread".** Uvicorn runs one asyncio event loop and every request is a coroutine
on it; nothing spins up a thread per call today and retraining does not either. Training is a plain
`threading.Thread(daemon=True)`, started from `app.py`'s lifespan and — if the wall clock permits —
from the worker's day-rollover path. **The project already has this pattern for the corpus worker, so
retraining adds no new concept.**

**It does not pause the router, for three reasons that fail differently:** nothing on the event loop
awaits it, so no request can block behind it; the GIL is released during the heavy work, which
Task 4 read off the shipped binary for `_train_dictionary` and `_Decompressor_decompress` alike; and
CPU contention remains real even so, which is precisely why the wall clock is measured before the
trigger is chosen.

**What FastAPI and Starlette offer, and why none of it fits** — read from the installed packages
rather than recalled:

| Mechanism | Verdict |
|---|---|
| `BackgroundTask` — `starlette/background.py:12` | **Wrong tool.** Runs after the response but is `await`ed inside that request's ASGI cycle, so a long run holds one request open. It is per-request; training is not. `proxy.py:224` already uses it correctly for its real purpose |
| `run_in_threadpool` — `starlette/concurrency.py:31` | Right mechanism, **wrong pool.** It delegates to `anyio.to_thread.run_sync`, the shared pool every sync offload uses; occupying a slot for minutes competes with all of it |
| `asyncio.create_task` | **The one that would actually pause the router.** CPU-bound work on the loop blocks every concurrent request — and it is the most tempting, because it looks like the async-native answer |
| `lifespan` | Not a background mechanism, but the correct **place** to start one. Already in use at `app.py:44` |

**Shutdown needs nothing.** Because the install is `.incoming/` → fsync → rename, a training run
killed mid-flight leaves **no trace** — no partial dictionary, nothing half-written. Abandonment is
safe by construction. That is a different rule from the corpus worker, which drains with a timeout
because it is holding bodies that would otherwise be lost, and **the two threads having different
shutdown rules is deliberate rather than inconsistent.**

### What this costs, and what is still unratified

**Named, and accepted by silence rather than by decision — so it is written here rather than
implied.** The "plain copies" decision was costed at ~40–80 MB a year when a new dictionary was a
rare event. **One dictionary per day, plus a copy in every day folder that uses it, is roughly double
that** — call it ~150 MB a year. Still small, and still the right shape, but it is a figure the owner
accepted under a different assumption and it has not been re-accepted.

**And the training wall clock is unmeasured**, which is now load-bearing in a way it was not before:
on a router left running for days, training fires unattended, and **UTC midnight is an arbitrary
local hour** — it may land in the middle of a working afternoon beside a local model that is already
the largest thing on the machine. Three seconds makes the whole question moot; four minutes of
saturated CPU makes rollover-triggering indefensible and startup-only the answer. **The measurement
comes before the trigger is wired**, and that ordering is the decision.

## The `wiki/` tier, created on this branch — 2026-08-19

**Owner's decision, at the end of the retraining interview**, and it is recorded here because it is a
change to the documentation structure that appears inside a `feat/` phase branch — which needs an
explanation rather than a reader's guess.

**What it is:** `docs/wiki/`, for behaviour of the libraries and tools this project is **built from**,
established by reading them, with sources linked and version pins. Two pages:
`background-work-in-fastapi.md`, `zstandard-and-libzstd.md` and `reading-a-c-extension-binary.md`. `docs/README.md` gains an eighth
filing row, a tier section, and a clause on rule 1 separating a **backend** (something the router
dispatches to → `reference/`) from a **dependency** (something it is built from → `wiki/`).

**Why it exists:** the answers that produced it — which background mechanism fits which shape of work,
and what `zstandard` does that its documentation does not say — were established during this phase and
**would otherwise have survived only in this file**, which is archive. Nobody opens a phase note to
find out how `BackgroundTask` behaves.

### The rule it cuts against, named rather than glossed

**`../../method/IDM-001-git-branching.md` says work belonging to a later phase never goes on an
earlier phase's branch, even documentation** — and **Phase 8 created the `method/` tier as a phase of
its own**, which is the precedent for treating a new tier as phase-shaped work.

**Three options were put to the owner** — its own `docs/` branch off `main`, this branch, or parking
it in `../../backlog.md` — **and this branch was chosen.** The argument on that side is real: the
content is Phase 10's own research, and the alternative leaves it in a session that gets cleared.
**The cost is equally real and is the reason for this section:** a reader running `git log` over this
branch finds a documentation tier appearing inside a `feat/` phase, and nothing in the phase's plan
predicts it. It is here because the owner decided it, not because it was overlooked.

**It is not in `plan.md`'s task list and no task number was spent on it.** Adding one would say this
phase planned it, and this phase did not.

### Two things deliberately not done

**No number was moved into a wiki page.** `../../README.md`'s rule that a measurement's canonical row
is `../../reference/measurements.md` is unchanged; both pages **cite** the phase evidence and say
where the numbers will live after Task 21. A tier that starts quoting numbers becomes the second copy
the structure exists to prevent.

**The upstream links were fetched after all** — consent was given later the same day, and it was
worth having. **22 URLs, 21 returned 200 and one did not resolve at all**: `www.uvicorn.org`, written
from knowledge because it looks exactly like the address that project would have. Its own README gives
`uvicorn.dev`. **A plausible URL reads as verified until somebody clicks it**, which is the whole
argument for checking rather than for writing carefully.

**Two content claims were checked rather than only the status codes**, since a 200 says a page exists
and nothing about whether it supports the sentence citing it. FastAPI's Caveat section does send heavy
computation to *"other bigger tools like Celery"*, as claimed. **Starlette's background-tasks page gives
no warning about long or heavy work at all** — which is a better justification for the wiki page than
the one originally written: the constraint is real, and the only way to find it is to read
`background.py`.

**A third page was added the same day, on the owner's instruction:**
`reading-a-c-extension-binary.md`, which was earlier recommended as a *section* of the `zstandard`
page. Writing it separately paid immediately. **Every command in it was run rather than recounted**,
and doing so found that Task 4's method had done unnecessary work: `otool -tV` annotates each stub call
with its symbol name, so the index arithmetic against the `__stubs` section and `otool -Iv` was never
required. **The finding itself re-derived exactly** — 21 functions, 0 unbalanced, the same instruction
sequence — which is the useful half: the conclusion held and only the route to it was longer than it
needed to be.

## The wiki's first claim was challenged, and it was wrong — 2026-08-19

**The owner asked whether `background-work-in-fastapi.md`'s `threading.Thread` row would "really work
as you think", and asked for supporting sources and an isolated test.** It did not, as written, and
**the page was corrected from measurement rather than from the argument.**

**What was wrong:** the row said a plain thread suits *"CPU-bound background work"* with no
qualification. **A thread only protects the event loop when the work releases the GIL.** The three
examples given — compression, a queue consumer, a periodic job — all happen to, **which is exactly why
the overgeneralisation read as proven**: every instance was correct, so nobody checked the rule.

**The instrument is `../../procedures/event-loop-lag/`**, promoted from a scratch script because it is
re-runnable and answers a question that returns with every Python upgrade. Two halves: loop lag from
inside, and HTTP round-trips against real uvicorn from a **separate process**, so the client cannot
contend for the server's GIL. Three consecutive runs of each; the ratios were stable to within
tenths of a millisecond.

**The result, in HTTP round-trip milliseconds** — idle 0.53 p50, `inline` 17.43, `thread-python` 6.57
p50 but **24.77 p99**, `thread-hashlib` 0.75, `thread-zstd` 0.73.

**Three things came out of it, and the second was not expected.** A GIL-releasing thread is
**indistinguishable from an idle server**, so this project's design holds. **A GIL-holding thread gives
a better median than inline and a worse tail** — inline yields deterministically and is bad but
bounded, while a thread is preempted at the OS's discretion, so *"move it to a thread"* can improve the
number people watch while worsening the worst case. And the floor is not zero, so the ratios travel and
the absolutes do not.

**A defect in the instrument was found by running it**, which is the working agreement's own rule
about fixing the instrument before believing the result. The first version measured lag on the **same
task** that did the inline work; that serialises them, so the work consumed slack rather than appearing
as delay, and **`inline` reported *better than idle*** — an impossible result that would have been
easy to report as a surprising finding. An inline blocking call harms every *other* task, so seeing it
requires two.

**And a link defect the status-code sweep could not catch.** `docs.python.org/3/c-api/init.html#…`
returns **200**, but the content moved to `c-api/threads.html` and `init.html` is now a bare index.
**A status code says a page exists, not that it says what you claim** — it was three wiki pages'
citation for the GIL mechanism, and the replacement carries the quote it is cited for.

**The supporting documentation is stronger than the disassembly alone.** CPython's own C-API page says
detaching the thread state *"is also useful to call it over long-running native code that doesn't need
access to Python objects or Python's C API"*, and **names `zlib` and `hashlib` as doing it when
compressing or hashing** — the same pattern Task 4 read out of `zstandard`'s binary. So the mechanism
now has an authoritative statement behind it and not only this project's measurement.

## The general case, and a claim this session got wrong twice — 2026-08-19

**The owner asked for the wiki to cover CPU-bound work that *holds* the GIL, and explicitly not to
answer "Celery" — "it itself is toooooo complex".** Fair: a task queue solves durability and
distribution, and *"this call is slow"* is a different problem that three cheaper rungs already
solve.

`cpu_offload.py` joins `../../procedures/event-loop-lag/`, measuring four mechanisms under Python
3.14.7 on ten cores, three consecutive runs. **`ProcessPoolExecutor` and `InterpreterPoolExecutor`
both protect the loop completely** — p99 of 0.74 and 0.78 ms against an idle floor of 1.10 — while a
thread sits at 13.00. **Hand-rolled `Process` workers on a bounded queue do the most work by far**,
2901 units against 1398, because fire-and-forget skips the result round trip — **and have the worst
tail, a p99 of 16 ms**, because the producer side is GIL-holding Python in your own process.

### The correction, and it was reasoned from documentation both times

**This session told the owner that subinterpreters' advantage is "startup and memory cost, not data
transfer", because the stdlib docs say both executors "serialize the callable and arguments using
pickle".** That inference is wrong, and the measurement says so plainly: handing a **16 MB argument**
costs **6.36 ms** to a process and **0.42 ms** to a subinterpreter — about **15x** — with per-call
overhead roughly halved as well.

**Pickling is not the expensive part; the pipe is.** The documentation is accurate and the inference
drawn from it was not, which is the same failure shape as the `threading.Thread` row earlier the same
day: **a true sentence, over-generalised, and believed because no instance contradicted it.** Two in
one day is a pattern worth naming rather than a coincidence.

### Two instrument defects, both found by running

**Pool warm-up.** Both executors spawn workers lazily on first submit, and with the spawn start
method that re-imports the module. Paid inside the measurement window it appears as a tail belonging
to startup rather than to steady state. The instrument now warms every pool before the clock starts —
and the hand-rolled tail **survived** the warm-up, which is what makes it a finding rather than an
artefact.

**A p50 below idle is not superiority.** Both pools read ~0.20 against an idle floor of ~1.04, and the
reason is sleep granularity: a loop with other work wakes more precisely than one sleeping a full
tick. **The p99 is the honest column**, and the page says so rather than quoting the flattering
number.

### One thing written down defensively

**The section ends by saying none of it applies to this project's worker.** `zstd` releases the GIL,
so the thread is already right, and "upgrading" it to a process pool would pickle every 100–200 KB
body down a pipe at roughly the measured cost — to buy parallelism it already has. `plan.md` rejected
multiprocessing on that reasoning before any of it was measured, and the measurement agrees. **Without
that paragraph the new section is an invitation to make the router slower.**

## The second forward review — the retraining revision, 2026-08-19

**Run under `../../method/IDM-004-reviewing-unexecuted-work.md` on the owner's instruction**, against
the 263 insertions of `git diff 379264a..HEAD -- plan.md`. Charter beside this file:
`review-charter-retraining.md`, named by subject so a third does not have to renumber it. **Nothing
was fixed during either run.**

**One deviation from the protocol, recorded rather than glossed.** `IDM-004` says the runs are
parallel *"if the author goes first it will quietly repair whatever a cold reader would have stumbled
on"*. The author pass was written **before** the cold run was launched, not during it. **The rule's
purpose was met** — the document was not touched between them, so the cold reader saw exactly what
the author reviewed — but the ordering was serial and the next run should launch the cold pass first.

### The result, and it is the strongest evidence `IDM-004` has

| | Findings |
|---|---:|
| Author run | **9** |
| Cold run | **16** |
| Found by both | **4** |
| **Author only** | **5** |
| **Cold only** | **12** |

**The cold run found every one of the four highest-cost findings, and the author run found none of
them.** `IDM-004`'s "what the first run cost" section had **one** run to reason from; this is the
second, and it says the same thing more sharply. The cold reader is not a second opinion — it is the
only pass that catches the defects that fail silently.

**The five the author found alone are all of one kind**: they need the repository's history rather
than the document. What Task 15's corpus actually looks like, that Task 6 has already run, what a
CLI flag defaults to. **The author run is worth keeping and it is not the one that finds the
dangerous things.**

### Tier 1 — accepted, and each fails silently

1. **The training `level` is unspecified, and the shipped defaults do not reproduce their own
   headline.** *Cold; verified here.* `evidence/benchmark.py:355` trained the 13.65x row with
   `{"k": 8000, "d": 8, "level": 19}`. `zstandard`'s trainer defaults `level = level or 3`
   (`backend_cffi.py:2860`) when `steps`/`threads` are unset. The `retrain:` block ships `maxdict`
   and `k` and fixes `d` as a constant **and never mentions `level`** — so an executor writes
   `train_dictionary(maxdict, samples, k=…, d=8)`, trains at level 3, and gets a dictionary
   documented as 13.65x that is not. **Nothing detects it**, and it makes Task 21's register row
   wrong.
2. **`write_dict_id` defaults to *off* on one of two construction paths.** *Cold; verified here.*
   `ZstdCompressor` defaults it true, but `ZstdCompressionParameters.__init__` defaults
   `write_dict_id=0` (`backend_cffi.py:414`) and pushes it to `ZSTD_c_dictIDFlag` (`:463`) — and the
   two are mutually exclusive (`:1759`). **The entire design rests on a frame naming its own
   dictionary.** Reach for `ZstdCompressionParameters` while tuning and every blob after that is
   unreadable by Task 13a. Task 8 must require it and assert it.
3. **The swap invariant names `<today>/dicts/`, and a blob can be written into yesterday's folder.**
   *Cold.* The plan's own risk list, added the same day, says a body submitted at 23:59:59 and
   written at 00:00:02 belongs to yesterday, and that **which timestamp decides the folder is
   unspecified in Task 8**. So across a rollover one worker writes into two day folders holding one
   compressor, and a swap copying into `<today>` leaves a later `<yesterday>` blob referencing a
   dictID with no copy beside it. **Task 18 observation 7 cannot catch this** — it exercises a swap
   *within* one day. The invariant must be per-write, not per-swap.
4. **Leave-one-session-out has no degenerate-case rule, and the ordinary day is degenerate.** *Both
   runs.* `run-02` and `run-03` carry **exactly one session each**; only `run-01` has three. One
   session in the window means an empty training set. Also unstated: which session is held out, and
   what happens on the first run when there is no incumbent — which the plan itself establishes is
   the normal first case, since Group C ships before Group D.

### Tier 2 — accepted, blocks execution

5. **The attempt record is named three times and specified nowhere.** *Both.* The cold run added what
   the author missed: **both obvious homes contradict a stated rule** — `<dir>/dicts/` collides with
   Task 14c's "newest by filename" listing, and a day folder collides with self-containment.
6. **The margin is required twice and defined nowhere.** *Both.* And the config block is **closed at
   nine settings**, so it cannot become a tenth key without contradicting Tasks 11 and 14d. A module
   constant is the answer the file does not give.
7. **Task 11 and 14d both build the config block; Task 14 and 14b both own the comparison.** *Cold.*
   **Task 11 is in Group C and executes first**, so an executor either builds nine keys there and
   finds 14d empty, or builds five and contradicts Task 11's own sentence.
8. **Task 18 observation 6 asks for something the trainer is designed to refuse.** *Cold.* It says to
   install a dictionary with `--train-dict` from a second terminal — but the today-guard stops it,
   and retraining from the same window cannot beat the incumbent trained from that window. **The
   check that proves the pickup mechanism cannot be made to fire.**
9. **Nothing gates the training thread on `corpus.enabled: false`.** *Cold.* It starts from lifespan
   unconditionally; the only "off" is `retrain.window_days: 0`. A thread that creates
   `<dir>/dicts/.incoming/` breaks Task 18 observation 1 — *"leaves no trace: no directory, no
   file"*.
10. **Window collection has no floor and no rule for fewer complete days than `window_days`.**
    *Cold.* `train_dictionary` raises rather than degrading; the benchmark wraps it in `try/except`
    for that reason. The symptom is a router that never retrains and says so only in the log.
11. **Task 15 cannot use the tool Tasks 14/14e build.** *Author only.* Task 15 trains from
    `logs/corpus-gate/`, which has no day folders; the CLI selects day folders with `--days N`. No
    flag selects another source, so Task 15 writes a second sampling path — which "one tool, not
    two" exists to prevent.
12. **Task 14a holds a decision gate with no branch instruction.** *Author finding; cold filed it as
    a question.* **The disagreement is itself the finding**: Task 6 was made to say *"on a negative
    result, stop and propose"* by the first review, and 14a says only *"decided by that number, not
    here"*. No threshold, no branch.
13. **"A run killed mid-flight leaves no trace" is false, and nothing owns `.incoming/`.** *Cold.* A
    daemon thread killed between write and rename leaves its partial file. Neither staging directory
    has a cleanup owner or a tmp-name rule, so two writers can collide and rename interleaved bytes.
14. **Neither 13a's reader nor 14's trainer names a file, and the two ref columns are never named.**
    *Cold.* The index header is re-emitted in every day file, so a rename after any real capture
    splits the corpus.

### Tier 3 — accepted, cheap

15. **`N`, the rescan cadence, is a bare letter in three places.** *Both.*
16. **`:880` still says "25-column index row".** *Cold.* Two of three restatements were updated.
17. **"Six lettered insertions" introduces a list of seven.** *Cold.* The header gets it right —
    a count disagreeing with itself inside one file, in a file with a section about exactly that.
18. **`:352` still reads "one worker until Task 6 says otherwise".** *Author.* Task 6 ran on
    2026-08-18.
19. **Task 14 says the procedure *keeps* its row in `procedures/README.md`.** *Cold question, filed
    here as a finding after checking:* `docs/procedures/corpus-dictionary/` does not exist and that
    file has no such row. "Keeping" should be "adding".
20. **`--train-dict` with `window_days: 0` and no `--days` is a silent no-op.** *Author.*
21. **Nothing says the manifest's schema version moves with the 26th column.** *Author.*
22. **Single-flight is per-process; `--train-dict` is deliberately another process.** *Cold,
    REPORTED.* Two CPU-bound runs, two writers in one staging directory, two racing guards.

### Refused

**None.** Every finding from both runs was verified or is cheap enough that verification costs more
than the fix. The cold run's five most serious claims were re-checked against the source before being
accepted, per `IDM-004`'s rule that a reviewer can be confidently wrong: `benchmark.py:355`,
`backend_cffi.py:414`/`:463`/`:2860`, `plan.md:880`, `plan.md:800`, and Tasks 11/14d read side by
side. **All five held.**

### Questions for the owner — decisions, not defects

1. **What threshold decides startup-only against startup-plus-rollover?** Does Task 14a decide alone,
   or measure and come back? `CLAUDE.md`'s propose-before-implementing suggests the latter.
2. **Should the margin, `N`, and the sweep ranges be module constants**, beside the shutdown timeout
   that already sets that precedent? Confirming it closes three findings at no design cost.
3. **Does typing `--train-dict` override the today-guard and the margin, or only `window_days: 0`?**
   Finding 8 turns on this.
4. **Which compression level does the comparison score at?** The write path is 9; every published
   ratio is 19. Separate from finding 1, which is about the *training* level.
5. **Is a fresh install expected never to train on its first day?** `window_days: 1` means the newest
   *complete* day.
6. **Does `docs/procedures/corpus-dictionary/` still need to exist**, given `--train-dict` and
   `--tune-dict` are on the router's own CLI? Three entry points may be one too many.
7. **Is the ~150 MB/year dictionary storage figure re-accepted?** Still raised-and-unratified.

## Verified by

*Not yet — this section is written at Task 24, and states what was run, when, and what it produced.*
