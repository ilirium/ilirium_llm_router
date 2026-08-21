# Background work in a FastAPI app

**Read this before moving anything off the request path** — a periodic job, a slow write, a
compression, a retrain — and before reaching for the mechanism whose name sounds right.
**`BackgroundTask` is not the one**, and `asyncio.create_task` is the one that will quietly make
every concurrent request slower.

**Two halves.** The first is *which mechanism*, and it assumes the work releases the GIL. The second
— **"If the work does *not* release the GIL"** — is the ladder for ordinary Python, where a thread
is measurably not enough, and it ends at task queues rather than starting there.

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
| **`threading.Thread`** | A real OS thread, outside every pool the framework manages | **Long-running work, and CPU-bound work *that releases the GIL*** — compression, hashing, a queue consumer, a periodic job | **Pure-Python CPU-bound work.** Measured below: a thread improves the median and *worsens* the tail. Also anything needing to hand a result back to a coroutine — that is `run_in_threadpool` |

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

## Measured: a thread is not enough on its own

**Corrected 2026-08-19.** The row above first said a thread suits *"CPU-bound background work"*
without qualification. **That is true only when the work releases the GIL**, and the three examples
originally given all happen to — which is why the overgeneralisation read as proven. It was measured
rather than argued: `../procedures/event-loop-lag/`, two instruments, three consecutive runs each.

**HTTP round-trip milliseconds against real uvicorn, timed from a separate process** — the number a
caller actually feels:

| Regime | p50 | p99 | vs idle p50 |
|---|---:|---:|---|
| `idle` | 0.53 | 1.06 | the floor |
| `inline` — CPU in a coroutine | 17.43 | 18.12 | **33x** |
| `thread-python` — a thread holding the GIL | 6.57 | 24.77 | **12x**, and a **23x** tail |
| `thread-hashlib` — a thread releasing it | 0.75 | 1.18 | **1.4x** |
| `thread-zstd` — this project's worker | 0.73 | 1.13 | **1.4x** |

**Three things to take from that, and the second is the non-obvious one.**

1. **A GIL-releasing thread is free.** `hashlib` and `zstandard` are indistinguishable from an idle
   server. This is the case the whole design rests on, and it holds.
2. **A GIL-holding thread gives a better median than inline but a *worse tail*.** 6.57 against 17.43
   at p50, and 24.77 against 18.12 at p99. **Inline yields deterministically**, so its latency is bad
   but bounded; **a thread is preempted at the OS's discretion**, so the tail is longer and less
   predictable. *"Move it to a thread"* can make the number people watch look better while making the
   worst case worse.
3. **The floor is not zero and the ratios are what travel.** Absolute figures are one machine on one
   day; core count and scheduler move them.

*The isolated instrument agrees — idle 2.04, inline 17.29, `thread-python` 11.09, `thread-hashlib`
2.04, `thread-zstd` 2.03 in loop-lag milliseconds. **These are not router measurements and are
deliberately not in `../reference/measurements.md`**, whose subject is what this router does; they
are instrument output supporting this page, and their home is the procedure that produces them.*

**One defect was found by running rather than reading**, and it is worth knowing because it is easy
to repeat: the first version measured lag on the **same task** that did the inline work. That
serialises them, so the work consumed slack instead of appearing as delay, and `inline` reported
*better than idle*. **An inline blocking call harms every *other* task**, so seeing it takes two.

## If the work does *not* release the GIL

**Everything above assumes the work is a C call that detaches the thread state.** Ordinary Python
does not, and then a thread is measurably not enough. This is the ladder for that case, **cheapest
first — and most applications never reach the bottom rung.**

**Measured 2026-08-19**, `../procedures/event-loop-lag/cpu_offload.py`, three consecutive runs on
Python 3.14.7, 10 cores, spawn start method. Same work unit as the table above, so the rows are
comparable.

| Mechanism | lag p50 | lag p99 | units done | |
|---|---:|---:|---:|---|
| `idle` | 1.04 | 1.10 | — | the floor |
| **`threading.Thread`** | 9.90 | 13.00 | 369 | **the control — a thread does not help here** |
| **`ProcessPoolExecutor`** | 0.20 | 0.74 | 1398 | loop fully protected, **3.8x the throughput** |
| **hand-rolled workers + bounded `Queue`** | 1.08 | **16.14** | **2901** | **the most work done, and the worst tail** |
| **`InterpreterPoolExecutor`** *(3.14+)* | 0.20 | 0.78 | 1413 | same protection, slightly more throughput |

**Read the p99, not the p50.** A p50 *below* idle is an artefact: a loop with other work to do wakes
more precisely than one sleeping the full tick, so the floor's own 1.04 is sleep granularity rather
than contention. The p99 is the honest column.

### 1 — `ProcessPoolExecutor`, created once in `lifespan`

The stdlib answer, and what the asyncio documentation points at. `await loop.run_in_executor(pool,
fn, arg)` gives you an awaitable, propagates exceptions through the future, and needs no protocol of
your own.

**Create it once at startup, never per request** — with the spawn start method, every worker
re-imports your module.

Two constraints the docs state and people trip over: *"only picklable objects can be executed and
returned"*, and *"the `__main__` module must be importable by worker subprocesses"*, so a lambda or a
REPL-defined function will not work.

### 2 — `InterpreterPoolExecutor`, if you are on 3.14

A `ThreadPoolExecutor` subclass where **each worker thread runs its own interpreter with its own
GIL**, so the workers genuinely run on separate cores in one process.

**And here is a correction this page owes**, because it was reasoned from the documentation and the
measurement disagreed. The docs say `submit()` *"serializes the callable and arguments using pickle"*
for **both** executors, from which it is natural — and wrong — to conclude that the data cost is the
same and that subinterpreters only save on startup and memory. **It is not the same, because the
pickled bytes do not cross a pipe:**

| Round trip for a call doing almost no work | tiny argument | 16 MB argument | ratio |
|---|---:|---:|---:|
| `ProcessPoolExecutor` | 0.170 ms | 6.36 ms | **41x** |
| `InterpreterPoolExecutor` | 0.055 ms | 0.42 ms | **8x** |

**A 16 MB argument costs ~15x less to hand to a subinterpreter than to a process**, and per-call
overhead is about half. Pickling is not the expensive part; **the pipe is.**

### 3 — Hand-rolled `Process` workers draining a bounded `Queue`

**`ProcessPoolExecutor` is `multiprocessing` underneath** — the docs say so — so this is not a
different engine, only a different owner for the lifecycle. It buys two things and costs several.

**What it buys.** **Back-pressure**, which is the real one: an executor's submit queue is
**unbounded**, so submitting faster than workers drain grows memory without limit, while
`Queue(maxsize=N)` is a genuine bound. And **fire-and-forget** — an executor mints a `Future` per
task whether or not you want a result, and an exception inside one is *swallowed* until somebody
reads it. Skipping the result round trip is why this row does the most work: **2901 units against
1398.**

**What it costs**, and the measured tail is the headline: **a p99 of 16 ms against the executor's
0.74.** The producer side lives in *your* process — `put()` pickles and a feeder thread writes to
the pipe — so it is GIL-holding Python contending with the loop. **The executor hides a producer that
somebody else got right.** Reproducible across runs; it is not startup, which the instrument warms
away.

Then the documented hazards you now own:

- **Deadlock on join.** *"if you try joining that process you may get a deadlock unless you are sure that all items which have been put on the queue have been consumed."* Drain before joining.
- **`terminate()` corrupts the queue** — *"the data in the queue is likely to become corrupted and may become unusable by other process."* Shut down with sentinels, not kills.
- **Ordering holds per producer only**, not across several.
- **Error propagation is yours.** A worker exception vanishes unless you send it back.
- **`multiprocessing.Queue` blocks and cannot be awaited**, so an async producer needs a bridge thread — which is exactly where the p99 above comes from.

**Start methods moved recently**: macOS has defaulted to **spawn** since 3.8, and **POSIX changed
from fork to forkserver in 3.14**. Both re-import your module, so the `if __name__ == "__main__"`
guard is mandatory and worker startup is not cheap.

### 4 — Only now, a task queue

**Reach for one when the work must survive a restart, run on another machine, or be retried** — a
different problem from *"this call is slow"*. If the answer is only ever needed by the process that
asked, rungs 1 to 3 are cheaper in every sense.

**Celery is not the only option and is usually more machinery than the problem needs:**

| | |
|---|---|
| **Taskiq** | Async-first, first-class FastAPI integration, dependency injection, strong typing. Closest in spirit to how FastAPI is written |
| **Dramatiq** | The nearest Celery-like API with a deliberately smaller feature set; the throughput pick |
| **RQ** | Five minutes to set up if Redis is already there. No result chaining |
| **Huey** | The least ceremony of the Redis-backed ones |
| **Procrastinate** | Postgres-backed, so no new broker if you already have a database |

**`arq` is in maintenance-only status and effectively unmaintained**, despite still being the
recommendation in a lot of async-FastAPI writing. Named here so nobody adopts it from an old post.

### And none of this applies to this project's worker

**Stated defensively, because this section is otherwise an invitation to do the wrong thing.** The
corpus worker compresses with `zstd`, which releases the GIL — measured, at the top of this page, as
indistinguishable from an idle server. **"Upgrading" it to a process pool would be a regression:** it
would pickle every 100–200 KB body down a pipe, at roughly the cost in the table above, to buy
parallelism it already has. `../milestone-2-corpus/phase-10-body-store/plan.md` rejected
multiprocessing for that reason before any of this was measured, and the measurement agrees with it.

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
- **"Running Blocking Code"**, which states the inline case exactly: *"if a function performs a CPU-intensive calculation for 1 second, all concurrent asyncio Tasks and IO operations would be delayed by 1 second"* — <https://docs.python.org/3/library/asyncio-dev.html>. It also documents `loop.slow_callback_duration`, which logs any callback over 100 ms in debug mode and is the cheapest way to catch this in a running app
- `sys.setswitchinterval`, the knob governing how badly a GIL-holding thread degrades the loop — note its warning that *"the actual value can be higher, especially if long-running internal functions or methods are used"*, and that which thread runs next is the OS's decision — <https://docs.python.org/3/library/sys.html#sys.setswitchinterval>
- `asyncio` event loop, `run_in_executor` — <https://docs.python.org/3/library/asyncio-eventloop.html#executing-code-in-thread-or-process-pools>
- `asyncio` developer notes on blocking the loop — <https://docs.python.org/3/library/asyncio-dev.html>
- `threading` — <https://docs.python.org/3/library/threading.html>
- `queue`, including `SimpleQueue` — <https://docs.python.org/3/library/queue.html>

**Offloading GIL-holding work**

- `concurrent.futures` — both executors, and the statements quoted above about picklability, the `__main__` guard, and the per-interpreter GIL — <https://docs.python.org/3/library/concurrent.futures.html>
- `concurrent.interpreters`, PEP 734's stdlib home, new in 3.14 — <https://docs.python.org/3/library/concurrent.interpreters.html> and <https://peps.python.org/pep-0734/>
- `multiprocessing`, for the queue-join deadlock, the `terminate()` corruption warning, and the start-method changes — <https://docs.python.org/3/library/multiprocessing.html>
- What's New in Python 3.14, where the interpreter pool and the forkserver default land — <https://docs.python.org/3/whatsnew/3.14.html>
- FastAPI's own discussion of mixing I/O-bound and CPU-bound work in one route — <https://github.com/fastapi/fastapi/discussions/5969>
- Task queue surveys, for the field beyond Celery — <https://judoscale.com/blog/choose-python-task-queue> and <https://aleksul.space/posts/choosing-python-task-queue-library/>

**The GIL, if you need to establish it rather than assume it**

- **Thread state and the GIL** — <https://docs.python.org/3/c-api/threads.html>. The authoritative statement of the mechanism this page rests on: *"it is also useful to call it over long-running native code that doesn't need access to Python objects or Python's C API"* — and it names `zlib` and `hashlib` as detaching the thread state when compressing or hashing. **`zstandard` follows the same pattern**, which is what makes the worker thread real. *(Cited as `c-api/init.html#thread-state-…` until 2026-08-19: that URL still returns **200**, but the content moved and `init.html` is now a bare index. **A status code says a page exists, not that it says what you claim.**)*
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
