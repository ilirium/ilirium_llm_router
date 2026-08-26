# The corpus — the body store

`calls.csv` records what a call *was*; the corpus records what it *said*. This file is the
specification of the body store: what lands on disk, in what shape, and what may be relied on.

**Read it before storing, reading or retraining against the corpus** — before adding an index
column, before changing where a blob or a dictionary lives, before assuming a day folder needs
anything outside itself, and before quoting a compression ratio. **It is off by default**, so the
first thing to know is that a machine with no `logs/corpus/` is a machine behaving correctly.

**Built in Phase 10**, `docs/milestone-2-corpus/phase-10-body-store/`, which holds the reasoning;
the decisions themselves are in `design-decisions.md`. Numbers come from `measurements.md` and
nowhere else.

## The switch, and what "off" means

`corpus.enabled: false` ships. Off is not an unused object — **it is no object, no worker thread,
and nothing created under `corpus.dir` at all**, and no trainer either. The two are independent
switches: `corpus.enabled` turns the store off, `corpus.retrain.window_days: 0` turns only the
automatic retraining off.

**`calls.csv` is always on because it is cheap and holds nothing sensitive. Neither is true here** —
bodies hold source code, file contents and anything typed. That asymmetry is the whole reason for
the switch.

## What is captured

**Everything, with no path filter.** All four routes reach `Proxy.record()`, which hands the call to
`CorpusWriter.submit()`. `count_tokens` noise is admitted deliberately: the `path` column makes it
filterable when you analyse, whereas a capture-time filter would also drop the unanticipated
catch-all traffic that column exists to surface.

**Bodies only. Never headers.** The store reads the same tee the recorder reads and never sees a
header, so the credential never reaches disk. The two header-derived values worth having —
`session_id` and `agent_id` — were already CSV columns and are copied into the index.

## The layout on disk

```
logs/corpus/
  dicts/                            the SOURCE. The trainer writes here, the router reads here
    .incoming/                      staging, dot-prefixed so the pickup's listing never sees it
    req-<UTC>-<dictID>.dict
  retrain.log                       one line per training attempt
  retrain.lock                      exclusive, across processes
  2026-08-20/                       a day folder. UTC-derived, never local
    index.csv                       26 columns
    manifest                        index_schema_version: 1 / index_columns: 26
    dicts/                          a PLAIN COPY of every dictionary this day's blobs reference
    incoming/                       staging, no dot here
    requests/<2 hex>/<64 hex>.zst
    responses/<2 hex>/<64 hex>.zst
```

**A day folder is self-contained, and that is a guarantee rather than a happy accident.** `tar` one,
unpack it on another machine, and every blob in it opens — because its own `dicts/` holds every
dictionary its blobs name. Verified by driving in Phase 10's Task 18, including the awkward case: a
day that saw a **mid-day dictionary swap** holds both dictionaries, and so does *yesterday's* folder
when a late body lands in it after a swap.

**The invariant that makes that true:** whichever day folder a blob is going into must **already**
hold the dictionary that blob names. Reversed, a crash between the two steps leaves a day holding a
blob whose dictID names a dictionary that is not there — and **nothing reports that until somebody
tries to read it back.**

### Names are a schema

A rename after any capture is a migration.

| Path | Form |
|---|---|
| a blob | `<day>/{requests,responses}/<first 2 hex>/<sha256 of the plaintext>.zst` |
| a dictionary | `req-<UTC>-<dictID>.dict`, stamp `%Y-%m-%dT%H%M%SZ`, dictID **8 lowercase hex** |
| the trainer's staging file | `<pid>-<uuid>.tmp`, unique per run |

**"Newest" is by filename, never by mtime.** An mtime is not a property of this store — **`tar` and
unpack rewrites every one of them**, and the paragraph above promises precisely that a day folder can
be moved to another machine and still read. Filename ordering survives that move; mtime ordering does
not.

*The reason given here until 2026-08-26 was that `logs/` sat inside a cloud-synced folder and a sync
rewrote mtimes. **That was a fact about one machine, and it is no longer true of that machine** — the
live `logs/` is now per-worktree under `~/Projects/local/`, which is not synced. The rule does not
move; only its argument was local, and the durable one was sitting four lines above it the whole
time.*

## The index

**26 columns. The first 20 are `stats.COLUMNS` verbatim, in order**, which is what lets a rotated
`calls.csv` segment and a day index feed one spreadsheet. The six that are this store's:

| Column | What it holds |
|---|---|
| `request_ref` | the blob's sha256, or a **reason word** |
| `response_ref` | the same, for the reply |
| `queue_ms` | how long the body waited before the worker took it |
| `store_ms` | how long hashing, compressing and writing took |
| `queue_bytes` | bytes waiting at the moment this call was submitted |
| `request_dict_id` | the dictionary the request blob was written against |

**The reason words, and why words rather than empty cells:** `dropped` (the queue was over its byte
bound), `too_large` (one body over `body_max_bytes`), `absent` (the router authored it, so there was
no body), `error` (storing it failed). **A hole is a row, not an absence** — an empty cell cannot
tell you which of four things happened.

**`request_dict_id` is read off the stored blob's own header, never from the compressor.** A
dictionary can be installed mid-day, so a body first stored at 10:00 against dictionary A and seen
again at 15:00 under B would otherwise get a row claiming B for a file that names A.

## Reading a body back

`CorpusReader` takes a blob and the day's dictionaries and returns the plaintext, **verified against
the digest in the filename**. It tries every candidate dictionary and keeps the one that verifies,
because a day folder is a directory anyone can drop a file into — **a dictID is not a unique key.**
`zstd --train` stamps **1** on everything it produces, which is why the router derives and stamps
its own.

The CLI has `--extract`. The general extraction *tool* — selection by day, session, call or model,
output layout, bulk verification — is **not** here; it is a later phase's subject.

## The write path

**Telemetry never breaks a call, and this is telemetry.** `submit()` runs on the event loop and does
a lock, an integer compare and a `put`; everything expensive happens in a worker thread. It never
raises.

Two limits, checked at two different moments, and neither covers the other:

| Key | Bounds |
|---|---|
| `body_max_bytes` | **one** body, checked on every chunk while the call runs |
| `queue_max_bytes` | **all waiting** bodies, checked once at submit |

A thousand ordinary 100 KB bodies are each far under the first and together are 100 MB against the
second. **Over the bound, the body is dropped and the row still written** — the request path never
waits. The first drop logs one `WARNING`, then it is counted rather than repeated, because the
moment of overload is when a log most needs to stay readable.

**On a clean shutdown the worker drains** with a 5 s timeout and emits a summary line; anything
abandoned is counted and named. A separate line reports `arrived`, `recorded` and `lost` — see
`observability.md`, which explains why that pair exists and what a non-zero `lost` means.

## The dictionary lifecycle

The store compresses against a **shared dictionary**, which is where nearly all of its ratio comes
from: request bodies are mostly a large repeated preamble.

- **The router trains its own**, offline, in a plain thread — never on the event loop, never in a
  request. `docs/wiki/background-work-in-fastapi.md` says why the async answers are wrong.
- **A candidate is measured against the incumbent on held-out material and installed only if it wins
  by a margin.** Training is **non-monotonic in both `maxdict` and `k`** — a larger budget has
  produced a worse dictionary here — so a new dictionary is never assumed better.
- **Install is write → fsync → rename**, so a run killed mid-flight publishes nothing.
- **A dictionary installed by another process is picked up without a restart**, by relisting
  `dicts/`. That is what makes `--train-dict` work against a running router. **The relist happens
  every 500 bodies, or when a day folder opens** — not on the next body.
- **The dictID is derived from the dictionary's content**, so identical bytes always give the
  identical name.

**Three compression levels, not one.** Storing a body and scoring a candidate against the incumbent
both use `corpus.compress_level_zstd`; **training uses its own, lower level.** Conflating them is
easy and the numbers move.

**`ZstdCompressionDict` accepts arbitrary bytes** and reports dictID **0** for content that is not a
real dictionary — which is exactly how "stored with no dictionary" is spelled, so blobs written that
way become permanently unreadable. The router refuses to start rather than write them.
`docs/wiki/zstandard-and-libzstd.md` has the detail.

## Configuration

Nine keys. `config.yaml` carries them with their comments; `make check` prints every one resolved.

| Key | |
|---|---|
| `corpus.enabled` | opt-in; nothing is written until true |
| `corpus.dir` | where it all goes |
| `corpus.compress_level_zstd` | the store's zstd level, **and** the level a candidate is scored at |
| `corpus.body_max_bytes` | one body larger than this is not stored |
| `corpus.queue_max_bytes` | total bytes waiting |
| `corpus.retrain.window_days` | complete days to train from; **`0` disables automatic retraining** |
| `corpus.retrain.sample_min_bytes` | below this is not a training sample. **No path filter** |
| `corpus.retrain.maxdict` | dictionary size cap. **Provisional** |
| `corpus.retrain.k` | COVER segment size. **Provisional**, and the library's own optimiser is a trap at this sample count |

**`maxdict` and `k` are provisional rather than measured-optimal**, and say so: the corpus has no
usable validation split, so the values were chosen knowing the slice they were scored on.

## What this is not

- **Not a database, a query engine, or a schema for message content.** It is files, and export
  is an offline concern.
- **Not a training set.** Fine-tuning was decided out; the corpus is for analysis.
- **Not retained or pruned.** Nothing deletes an archived body. **Retention is out of scope for
  Milestone 2** and no policy was decided — see `../milestone-2-corpus/implementation-plan.md`.
- **Not a change to `calls.csv`.** Not its columns, not its rotation. The corpus brings its own
  durable index precisely because the CSV is a capped rolling window and bodies would outlive it.
- **Not a guarantee that every call is archived.** A call that never reaches `record()` reaches
  neither the CSV nor the corpus. That hole is real, observed, and *reported* rather than closed —
  `observability.md`.

## Before quoting a ratio

**There is no headline number, deliberately.** Every compression figure here comes from a small
sample and exists to show the mechanism works, not to state a capability. `measurements.md` carries
each with its slice, and the note beside them explains why a ratio lifted out of that context is
being misused. **Anything near 26× on this corpus is a self-scoring accident until proven
otherwise** — it happened twice in one day by two different mechanisms.
