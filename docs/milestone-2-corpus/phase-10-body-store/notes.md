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

## Verified by

*Not yet — this section is written at Task 20, and states what was run, when, and what it produced.*
