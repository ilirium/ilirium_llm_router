"""If the CPU work does NOT release the GIL, what should it run on instead?

`event_loop_lag.py` establishes that a thread only protects the event loop when the work releases
the GIL. This answers the follow-up: for work that HOLDS it -- ordinary Python -- which offload
actually works, and what does each one cost?

FOUR MECHANISMS:

    thread              threading.Thread.                    The control. Known not to work.
    process-pool        ProcessPoolExecutor + run_in_executor.
    mp-workers          Hand-rolled Process workers draining a BOUNDED
                        multiprocessing.Queue, fire-and-forget.
    interpreter-pool    InterpreterPoolExecutor. One GIL per interpreter.
                        Python 3.14+; skipped below that.

TWO THINGS ARE MEASURED, because the second is where the surprise is:

    A. loop protection  Event-loop lag while the offload runs flat out, plus throughput.
                        Directly comparable with event_loop_lag.py's numbers.

    B. payload cost     Per-task round trip for a TINY argument against a 16 MB one.
                        Processes and subinterpreters BOTH pickle their arguments -- the
                        stdlib docs are explicit -- so this is the cost that decides whether
                        an offload is worth it for data-heavy work. It is the thing people
                        assume subinterpreters avoid, and they do not.

Run with `uv run python cpu_offload.py` (3.13, no interpreter pool) and with
`python3 cpu_offload.py` (3.14 here, all four). No dependencies either way -- the work is pure
arithmetic on purpose, since GIL-holding work is the whole subject.

Nothing is written, no server, no network. Expect roughly a minute.
"""

from __future__ import annotations

import asyncio
import multiprocessing as mp
import statistics
import sys
import threading
import time
from concurrent.futures import ProcessPoolExecutor

try:
    from concurrent.futures import InterpreterPoolExecutor
except ImportError:                                  # Python < 3.14
    InterpreterPoolExecutor = None                   # type: ignore[assignment]

TICK = 0.010
DURATION = 3.0
UNIT = 200_000            # same work unit as event_loop_lag.py, so numbers are comparable
INFLIGHT = 4              # tasks kept in flight against a pool
BIG = 16 * 1024 * 1024


# ---- module-level workers, because spawn pickles them by qualified name -----------------------
# "target must have been defined within an importable module in order to be loaded during
# unpickling" -- a lambda or a REPL-defined function will not work here.

def cpu_unit(n: int = UNIT) -> int:
    x = 0
    for i in range(n):
        x += i * i
    return x


def cpu_with_payload(buf: bytes) -> int:
    """Trivial work, large argument. Isolates transfer cost from compute cost."""
    return len(buf)


def mp_worker(q: "mp.Queue", counter) -> None:
    """Drains the bounded queue until the sentinel. Fire-and-forget: no result is returned."""
    while True:
        item = q.get()
        if item is None:                             # the sentinel, not a kill
            return
        cpu_unit(item)
        with counter.get_lock():
            counter.value += 1


# ---- measurement -------------------------------------------------------------------------------

async def tick_for(duration: float) -> list[float]:
    lags: list[float] = []
    deadline = time.perf_counter() + duration
    nxt = time.perf_counter() + TICK
    while time.perf_counter() < deadline:
        await asyncio.sleep(max(0.0, nxt - time.perf_counter()))
        lags.append((time.perf_counter() - nxt) * 1000.0)
        nxt += TICK
    return lags


async def load_thread() -> tuple[list[float], int]:
    stop = threading.Event()
    done = [0]

    def run() -> None:
        while not stop.is_set():
            cpu_unit()
            done[0] += 1

    t = threading.Thread(target=run, daemon=True)
    t.start()
    try:
        return await tick_for(DURATION), done[0]
    finally:
        stop.set()
        t.join(timeout=30)


async def load_executor(ex) -> tuple[list[float], int]:
    """Keep INFLIGHT tasks running on the pool while the loop ticks."""
    loop = asyncio.get_running_loop()
    done = 0
    stop = False

    # Warm the pool BEFORE the clock starts. Both executors spawn workers lazily on first
    # submit, and with the spawn start method that re-imports this module -- paid inside the
    # measurement window it shows up as a tail that has nothing to do with steady state.
    await asyncio.gather(*[loop.run_in_executor(ex, cpu_unit, 1) for _ in range(INFLIGHT * 2)])

    async def feed() -> None:
        nonlocal done
        pending = {loop.run_in_executor(ex, cpu_unit) for _ in range(INFLIGHT)}
        while not stop:
            finished, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)
            done += len(finished)
            pending |= {loop.run_in_executor(ex, cpu_unit) for _ in finished}
        await asyncio.gather(*pending)

    task = asyncio.ensure_future(feed())
    try:
        lags = await tick_for(DURATION)
    finally:
        stop = True
        await task
    return lags, done


async def load_mp_workers(n: int) -> tuple[list[float], int]:
    """Hand-rolled: bounded queue, N processes, sentinel shutdown, no Futures."""
    q: mp.Queue = mp.Queue(maxsize=64)               # THE BOUND an executor does not give you
    counter = mp.Value("i", 0)
    procs = [mp.Process(target=mp_worker, args=(q, counter), daemon=True) for _ in range(n)]
    for p in procs:
        p.start()

    stop = threading.Event()

    def feeder() -> None:
        """`Queue.put` blocks when full, so the producer lives on a thread. This is the part
        an executor gives you for free and the part that provides back-pressure."""
        while not stop.is_set():
            try:
                q.put(UNIT, timeout=0.1)
            except Exception:
                pass

    # Same warm-up for the same reason: ten spawned processes re-importing this module during
    # the measurement is startup cost, not steady state.
    deadline = time.perf_counter() + 30
    while counter.value < n and time.perf_counter() < deadline:
        try:
            q.put(1, timeout=0.1)
        except Exception:
            pass
        await asyncio.sleep(0.02)
    with counter.get_lock():
        counter.value = 0

    ft = threading.Thread(target=feeder, daemon=True)
    ft.start()
    try:
        lags = await tick_for(DURATION)
    finally:
        stop.set()
        ft.join(timeout=5)
        try:
            while not q.empty():                     # drain BEFORE joining, or deadlock
                q.get_nowait()
        except Exception:
            pass
        for _ in procs:
            q.put(None)
        for p in procs:
            p.join(timeout=10)
            if p.is_alive():
                p.terminate()                        # last resort; corrupts the queue, which is
                                                     # why the sentinel path exists
    return lags, counter.value


# ---- part B: what does the argument cost to get there? -----------------------------------------

async def payload_cost(ex, buf: bytes, reps: int = 20) -> float:
    """Median per-call round trip in ms for a near-zero-compute call with this argument."""
    loop = asyncio.get_running_loop()
    times = []
    for _ in range(reps):
        t0 = time.perf_counter()
        await loop.run_in_executor(ex, cpu_with_payload, buf)
        times.append((time.perf_counter() - t0) * 1000.0)
    return statistics.median(times)


# ---- reporting ---------------------------------------------------------------------------------

def row(name: str, lags: list[float], work: int, note: str) -> None:
    s = sorted(lags)
    print(f"  {name:<18} {statistics.median(s):>8.2f} {s[int(len(s) * 0.99) - 1]:>9.2f} "
          f"{work:>7}   {note}")


async def main() -> int:
    cpus = mp.cpu_count()
    print(__doc__.split("\n")[0])
    print()
    print(f"python  {sys.version.split()[0]}   start method  {mp.get_start_method()}   "
          f"cpus  {cpus}")
    print(f"InterpreterPoolExecutor  {'available' if InterpreterPoolExecutor else 'NOT in this version — skipped'}")
    print()
    print("A. LOOP PROTECTION — event-loop lag in ms while the offload runs flat out")
    print()
    print(f"  {'mechanism':<18} {'p50':>8} {'p99':>9} {'work':>7}   what it shows")
    print(f"  {'-' * 18} {'-' * 8} {'-' * 9} {'-' * 7}   {'-' * 13}")

    lags, w = await tick_for(DURATION), 0
    row("idle", lags, w, "the floor")

    lags, w = await load_thread()
    row("thread", lags, w, "GIL held — the control")

    with ProcessPoolExecutor(max_workers=cpus) as ex:
        lags, w = await load_executor(ex)
    row("process-pool", lags, w, "ProcessPoolExecutor")

    lags, w = await load_mp_workers(cpus)
    row("mp-workers", lags, w, "hand-rolled, bounded queue")

    if InterpreterPoolExecutor is not None:
        with InterpreterPoolExecutor(max_workers=cpus) as ex:
            lags, w = await load_executor(ex)
        row("interpreter-pool", lags, w, "one GIL per interpreter")

    print()
    print("B. PAYLOAD COST — median round trip in ms for a call that does almost NO work")
    print()
    print(f"  {'mechanism':<18} {'tiny arg':>10} {'16 MB arg':>11} {'ratio':>8}")
    print(f"  {'-' * 18} {'-' * 10} {'-' * 11} {'-' * 8}")
    big = b"\xa5" * BIG
    small = b"x"

    with ProcessPoolExecutor(max_workers=2) as ex:
        a, b = await payload_cost(ex, small), await payload_cost(ex, big)
    print(f"  {'process-pool':<18} {a:>10.3f} {b:>11.3f} {b / a:>7.0f}x")

    if InterpreterPoolExecutor is not None:
        with InterpreterPoolExecutor(max_workers=2) as ex:
            a, b = await payload_cost(ex, small), await payload_cost(ex, big)
        print(f"  {'interpreter-pool':<18} {a:>10.3f} {b:>11.3f} {b / a:>7.0f}x")

    print()
    print("  Both pickle their arguments. A large payload is paid for on every call, which is")
    print("  what decides whether offloading data-heavy work is worth it at all.")
    return 0


if __name__ == "__main__":                           # required: spawn re-imports this module
    raise SystemExit(asyncio.run(main()))
