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

**Marked as inferred rather than measured**, from how `tar` resolves hardlinks. Task 5 verifies it
instead of trusting this paragraph.

### 8 — `make test` takes 150 seconds on this machine, not 0.6

Same 158 tests, all passing. Phase 9 recorded **0.60 s**; this session measured **150.85 s**, and the
first `import fastapi` alone took over 17 seconds of wall clock across its submodules.

**It is OneDrive placeholder hydration on first touch, not a repository defect** — the `.venv` lives
inside the synced folder, and a warm second run is fast. Recorded because **Phase 10 adds tests**, and
a session reading 0.6 s as the baseline will conclude the suite has hung and start debugging the wrong
thing. It cost this session three abandoned invocations before the cause was found.

### 9 — The `logs/telemetry/` sweep is smaller than it looks, and one judgement in it is not mechanical

**Live citations, which Task 13 and Task 14 must change:** `config.yaml` (two), `config.py` (two
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
and Task 14 states that rather than leaving the untouched hits looking like an oversight.

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
| **Q1** | What stops the queue eating memory, and at what size? | Bounded in **bytes**, 64 MiB |
| **Q2** | Where in the code does the store get handed the bytes? | **`Proxy.record()`**, all four call sites |
| **Q2b** | Do we fix the case where no row is written at all? | **Name it, do not fix it** |
| **Q3** | How does the index say a body was not stored? | A **reason word** in the ref cell |
| **Q4** | A body over the ceiling — keep the first megabyte, or nothing? | **Nothing**, marked `too_large` |
| **Q5** | The offline trainer — `zstandard`, or the `zstd` binary? | **The binary**, as Phase 9 used |
| **Q6** | The same body on two days — stored once or twice? | **Twice.** Dedup is per day |
| **Q7** | How does a day folder get the dictionary it needs? | **A hard link** |
| **Q8** | Where does "the tests take 150 s here" get recorded? | **This note only** |
| **Q9** | Which documents get repointed by the telemetry move? | **Live documents only** |
| **Q10** | What compression level does the write path use? | **Undecided — Task 3c measures it** |
| **Q11** | Is the corpus's copy of a response a second buffer? | **Yes, separate from the scanner's** |
| **Q12** | How is "did this ever come close?" answerable later? | **Three index columns and two log lines** |

*Q10 to Q12 were added 2026-08-18, out of the write-path interview rather than the re-derivation.
They are questions this phase raised about itself, not findings against the sketch.*

---

### Q1 — What stops the queue eating memory, and at what size?

**In plain terms.** When a call finishes, the router hands its bodies to a background thread so the
caller is not kept waiting while they are compressed and written. If that thread falls behind, bodies
pile up in memory. Something has to say *stop accepting more*, and the obvious knob — a maximum
**number** of waiting bodies — does not bound memory here, because one body can be 200 KB. A thousand
of them is 200 MB.

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

**In plain terms.** You have decided the **router** gets the `zstandard` package. Separately, there is
an offline tool that trains the dictionary — it never runs on the request path. Every compression
figure this milestone rests on came from the **`zstd` command-line binary**, including Phase 9's gate.

| Option | Buys | Costs |
|---|---|---|
| **A — the trainer keeps using the binary** *(assumed)* | A new dictionary is measured on the same instrument as every number already in `../../reference/measurements.md`, so the comparison is honest. `evidence/gate.py` already works this way | Two tools in one project. The procedure needs `zstd` installed, which a config file cannot check |
| **B — the trainer uses `zstandard` too** | One tool. The procedure needs nothing but the dependency the router already has | New figures are not directly comparable with Phase 9's until somebody re-measures the old ones with the new tool. That is a cost this repository has paid before for smaller reasons |
| **C — the trainer does both and compares them** | Settles whether they agree, once | A measurement nobody asked for, in a phase that already has twenty tasks |

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

**In plain terms.** A compressed blob cannot be read without the dictionary it was compressed against
— lose the dictionary and every blob referencing it is unreadable forever. The sketch put a copy
inside each date folder so that one folder can be moved elsewhere and still open, and priced that at
about 80 MB a year. It left the choice between plain copies and filesystem clones open.

| Option | Buys | Costs |
|---|---|---|
| **A — a hard link into the day folder** *(assumed)* | The folder appears to contain its dictionary and costs nothing. Archiving one day still produces a real file, so portability survives | Links fail across filesystems, so an absolute `dir` on another volume needs a fallback. **This is inferred, not measured** — Task 5 verifies it |
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
| **A — live documents only** *(assumed)* | The archive keeps saying what was true when it was written. `logs/` is gitignored and the link checker skips it, so nothing becomes unfollowable | Two documents will name a path that no longer exists, and it will look like an oversight unless Task 14 says otherwise — which it does |
| **B — repoint everything, archive included** | Grep for the old path returns nothing, so nobody wonders | Rewrites measurements into statements that were never true. *"`logs/telemetry/calls.csv` before the capture — 177 lines"* is a sentence about a file that did not exist that day |
| **C — live documents, plus a note in each affected `evidence/README.md`** | The archive stays honest and a reader is told why the path reads oddly | More edits, in directories this phase otherwise does not touch |

---

### Q10 — What compression level does the write path use?

**In plain terms.** `zstd` has levels from 1 to 22, trading speed against ratio. **Every number this
milestone owns was measured at level 19**, because Phase 9 was measuring a *ratio* offline where time
did not matter. On the write path time does matter: published figures put level 19 at ~2–6 MB/s and
level 3 at ~350–500 MB/s — **a hundredfold difference**, against a ratio difference that nobody has
measured *with a dictionary already carrying the static preamble*.

| Option | Buys | Costs |
|---|---|---|
| **A — measure first, then choose** *(assumed; Task 3c)* | The level is picked from this corpus on this machine, and the ratio it costs is known rather than guessed | One more thing before the store is written — though the corpus is on disk, so it is a sweep, not a capture |
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
| **B — one shared buffer** | Half the memory on that path | Couples the recorder to the store. The scanner would have to buffer *because the corpus wants it to*, which is a dependency pointing the wrong way — and it changes `observe.py`, which this phase otherwise does not touch |

---

### Q12 — How is "did this ever come close?" answerable later?

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
`logs/corpus-gate/`, with no capture and no live session. That became Q10 and Group B0.

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

Group B0 (`3a`, `3b`, `3c`), Tasks 6 and 7 widened, four decisions added, and the GIL assertion
demoted from a design premise to a row in "Documented versus measured" reading **unverified**. **No
task was renumbered.**

## Verified by

*Not yet — this section is written at Task 20, and states what was run, when, and what it produced.*
