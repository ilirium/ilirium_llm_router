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

### 8 — `make test` takes 150 seconds on this machine, not 0.6

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

**Run 2026-08-18 against `plan.md` Tasks 4–24 per `review-charter.md`. Unreconciled** — the
fresh-context run was launched first and had not returned when this was written, so nothing here is
influenced by it and nothing here is confirmed by it either.

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

## Verified by

*Not yet — this section is written at Task 24, and states what was run, when, and what it produced.*
