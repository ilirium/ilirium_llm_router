# Background work in a FastAPI app

**Read this before moving anything off the request path** — a periodic job, a slow write, a
compression, a retrain — and before reaching for the mechanism whose name sounds right.
**`BackgroundTask` is not the one**, and `asyncio.create_task` is the one that will quietly make
every concurrent request slower.

**Established 2026-08-19 by reading the installed packages**, not from memory and not from a search.
Versions in this venv when it was written: `fastapi 0.140.9`, `starlette 1.3.1`, `anyio 4.14.2`,
`uvicorn 0.51.0`, Python 3.13. **Line numbers below are from those versions and will drift**; the
claims should outlive them, and the way to re-derive one is at the bottom.

---

## The one thing to know first

**There is no "request thread".** Uvicorn runs a single asyncio event loop, and every request handler
is a coroutine on it. Nothing in this app spins up a thread per call. So "do it in the background"
never means "let this request's thread carry on" — it means *get the work off the loop that is
serving every other request too*.

**CPU-bound work on the event loop blocks every concurrent request for its whole duration.** That is
the failure mode all four mechanisms below are judged against.

## The four mechanisms, and what each is actually for

| | What it really does | Use it for | Do not use it for |
|---|---|---|---|
| **`BackgroundTask`** / `BackgroundTasks`<br>`starlette/background.py` | Runs **after the response is sent**, but it is `await`ed as part of that request's ASGI cycle. Sync callables are pushed to the threadpool, async ones are awaited on the loop | A short tidy-up **belonging to one request** — closing an upstream response, firing a notification | Anything long. A minutes-long task holds one request's cycle open. It is also **per-request**, so it cannot express "once a day" or "at startup" |
| **`run_in_threadpool`**<br>`starlette/concurrency.py` | `functools.partial` then `anyio.to_thread.run_sync` — the **shared** worker pool every sync offload in the app already uses | Short blocking calls you must `await` from a handler — a sync DB driver, a small file read | Long jobs. The pool is a `CapacityLimiter(40)` shared with everything else, so occupying a slot for minutes starves unrelated work. And you still need something to await it |
| **`asyncio.create_task`** | A coroutine scheduled on the **event loop itself** | Genuinely async, I/O-bound fire-and-forget | **CPU-bound work of any kind.** This is the tempting wrong answer: it looks async-native and it is the only option here that can actually stall the server |
| **`threading.Thread`** | A real OS thread, outside every pool the framework manages | **Long-running or CPU-bound background work** — a queue consumer, a periodic job, compression | Anything needing to hand a result back to a coroutine; that is what `run_in_threadpool` is for |

### And `lifespan` is not a mechanism — it is the place

`lifespan` is an async context manager the ASGI server enters before serving and exits after the last
request. It is **where** you start and stop the things above, not a way to run them. In this
repository it is `app.py`'s `lifespan`, which already owns the HTTP client and the stats writer, and
it is the natural owner of any thread that must outlive a request.

## What this project chose, and why

**A plain daemon `threading.Thread`, started from `lifespan`.** Two of them, eventually: the corpus
worker that compresses and writes bodies, and the dictionary trainer.

Three facts made that the fit rather than a preference:

1. **Compression and dictionary training are CPU-bound and blocking**, which rules out the loop.
2. **`zstandard` releases the GIL around the libzstd call** — verified against the shipped binary,
   not the documentation: `_ZstdCompressor_compress` calls `_PyEval_SaveThread`, then
   `_ZSTD_compressStream2`, then `_PyEval_RestoreThread`. 21 functions release it, balanced in every
   one, `_train_dictionary` and `_Decompressor_decompress` among them. **So a worker thread is a real
   thread**, and that is a property of the library rather than of Python.
3. **It measured 3.34x on four threads**, so *released* was confirmed to also mean *scales* — which is
   a separate claim and was treated as one.

**A released GIL is still not a free core.** Threads bound *throughput*, never *latency*, and CPU
contention with the event loop is real even when no lock is held. That is why the trainer's wall
clock is measured before deciding when it is allowed to run.

### Why not `multiprocessing`

Every payload would be pickled and copied down a pipe — the opposite of handing a thread a reference
to bytes already in memory — and a child that is OOM-killed stops working silently unless something
watches it. It becomes worth measuring only if the GIL is *not* released, which here it is.

### The queue between a coroutine and a thread

**`asyncio.Queue` is not thread-safe** and is the matching trap: producer on the loop, consumer on a
thread, is a data race rather than a queue. `queue.Queue` and `queue.SimpleQueue` are safe both ends.
`queue.Queue(maxsize=N)` bounds **items**, which is not the same as bounding memory when items vary
from 2 KB to 200 KB — this project uses `SimpleQueue` with a byte counter beside it.

## Shutdown, and the property worth designing for

A background thread needs a stop rule, and **the right rule depends on what is lost if it is
abandoned**, not on a convention:

- **Holding data that exists nowhere else** — drain it, with a timeout. A router that will not stop is
  worse than one that loses its last few records, so the timeout is not optional either.
- **Producing a file, installed atomically** — abandon it freely. If the output only becomes visible
  by `write → fsync → rename`, a thread killed mid-run leaves **nothing**: no partial file, no
  half-state, nothing to clean up. **Atomic install is what makes abandonment safe**, and it is worth
  choosing for that reason alone.

Both patterns are in this codebase, and the difference between them is deliberate.

## Reading list

**Framework**

- Starlette background tasks — <https://www.starlette.io/background/>. **Checked 2026-08-19: it says a task "will run only once the response has been sent" and gives *no* warning about long or heavy work.** That silence is why this page exists — the constraint is real and you only find it by reading `background.py`
- Starlette lifespan — <https://www.starlette.io/lifespan/>
- FastAPI background tasks — <https://fastapi.tiangolo.com/tutorial/background-tasks/>. **The one upstream page that does warn**: its Caveat section sends heavy computation to *"other bigger tools like Celery"*, which is right about the problem and aimed at a bigger deployment than a single laptop router
- FastAPI lifespan events — <https://fastapi.tiangolo.com/advanced/events/>
- ASGI lifespan specification — <https://asgi.readthedocs.io/en/latest/specs/lifespan.html>
- Uvicorn — <https://uvicorn.dev/>

**The threading layer underneath**

- AnyIO worker threads and the capacity limiter — <https://anyio.readthedocs.io/en/stable/threads.html>
- `asyncio` event loop, `run_in_executor` — <https://docs.python.org/3/library/asyncio-eventloop.html#executing-code-in-thread-or-process-pools>
- `asyncio` developer notes on blocking the loop — <https://docs.python.org/3/library/asyncio-dev.html>
- `threading` — <https://docs.python.org/3/library/threading.html>
- `queue`, including `SimpleQueue` — <https://docs.python.org/3/library/queue.html>

**The GIL, if you need to establish it rather than assume it**

- Thread State and the GIL, and the `Py_BEGIN_ALLOW_THREADS` macro pair — <https://docs.python.org/3/c-api/init.html#thread-state-and-the-global-interpreter-lock>
- `python-zstandard` documentation — <https://python-zstandard.readthedocs.io/>
- Zstandard format, including the dictionary ID a frame carries — <https://github.com/facebook/zstd/blob/dev/doc/zstd_compression_format.md>

*Upstream landing pages, chosen because they outlive version numbers. **All were checked from this
machine on 2026-08-19** and returned 200. One was wrong when written: `www.uvicorn.org` does not
resolve, and the project's own README gives `uvicorn.dev` — **which is exactly the failure the check
exists to catch**, since a plausible-looking URL written from memory reads as verified until somebody
clicks it.*

## Where these claims came from, and what expires

| Claim | How it was established |
|---|---|
| `BackgroundTask` is awaited in the request cycle; sync callables go to the threadpool | Read `starlette/background.py` in this venv |
| `run_in_threadpool` delegates to `anyio.to_thread.run_sync` | Read `starlette/concurrency.py` in this venv |
| The shared pool's default limit is **40** | Read `anyio/_backends/_asyncio.py` — `CapacityLimiter(40)`, created lazily per event loop |
| `zstandard` releases the GIL, in 21 functions, balanced | Disassembled the **shipped** `backend_c…so`; the wheel ships no C sources. Method in `../milestone-2-corpus/phase-10-body-store/notes.md`, Task 4 |
| 3.34x on four threads | `../procedures/corpus-benchmark/`, frozen in that phase's `evidence/` |

**What expires:** the line numbers, the version pins, and the 40. **What does not:** which mechanism
belongs to which shape of work, and that CPU-bound work on the event loop stalls every concurrent
request.

**To re-derive any of it**, read the installed package rather than the documentation — that is what
was done here, and in the `zstandard` case the documentation would not have settled it at all.
