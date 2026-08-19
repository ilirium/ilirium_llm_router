"""Does a background thread actually protect the asyncio event loop?

`docs/wiki/background-work-in-fastapi.md` says a plain `threading.Thread` is the fit for
"long-running or CPU-bound background work". This measures whether that is true, and the answer
is not the same for all CPU-bound work.

THE METRIC is event-loop lag. A coroutine schedules a tick every TICK seconds and records how
late it actually woke. On an idle loop that is tens of microseconds. Lag is exactly what a
request waiting to be served would experience, which is why it is the number that matters.

FIVE REGIMES, and the middle two are the whole point:

    idle            nothing else running.                          The control.
    inline          CPU work in a coroutine on the loop.           What "bad" looks like.
    thread-python   a thread running PURE PYTHON cpu work.         Holds the GIL.
    thread-hashlib  a thread running hashlib.sha256.               Releases the GIL — the
                                                                   CPython docs name hashlib
                                                                   as doing exactly this.
    thread-zstd     a thread running zstandard compression.        This project's actual case.

Run with `uv run python event_loop_lag.py` — NOT bare `python3`, which on this machine is a 3.14
without `zstandard` installed. The zstd regime is skipped if the import fails, so the rest still
runs anywhere.

Nothing is written, no server is started, no network is used. It takes about 15 seconds.
"""

from __future__ import annotations

import asyncio
import hashlib
import statistics
import sys
import threading
import time

TICK = 0.010          # how often the loop wants to wake up
DURATION = 3.0        # seconds per regime
BUF = b"\xa5" * (16 * 1024 * 1024)   # big enough that the C call is worth releasing the GIL for

try:
    import zstandard
except ImportError:
    zstandard = None


# ---- the workloads ----------------------------------------------------------------------------

def burn_python(stop: threading.Event) -> int:
    """Pure Python arithmetic. Holds the GIL the entire time, releasing only every switch
    interval when the interpreter forces a handoff."""
    n = 0
    while not stop.is_set():
        x = 0
        for i in range(200_000):
            x += i * i
        n += 1
    return n


def burn_hashlib(stop: threading.Event) -> int:
    """sha256 over a large buffer. CPython detaches the thread state around the C call."""
    n = 0
    while not stop.is_set():
        hashlib.sha256(BUF).digest()
        n += 1
    return n


def burn_zstd(stop: threading.Event) -> int:
    """What the corpus worker will actually do."""
    cctx = zstandard.ZstdCompressor(level=9)
    n = 0
    while not stop.is_set():
        cctx.compress(BUF)
        n += 1
    return n


# ---- the measurement --------------------------------------------------------------------------

async def measure(duration: float) -> list[float]:
    """Wake every TICK and record how late we were, in milliseconds."""
    lags: list[float] = []
    deadline = time.perf_counter() + duration
    nxt = time.perf_counter() + TICK
    while time.perf_counter() < deadline:
        await asyncio.sleep(max(0.0, nxt - time.perf_counter()))
        now = time.perf_counter()
        lags.append((now - nxt) * 1000.0)
        nxt += TICK
    return lags


async def run_idle() -> tuple[list[float], int]:
    return await measure(DURATION), 0


async def run_inline() -> tuple[list[float], int]:
    """CPU work in a SEPARATE coroutine on the same loop, while the ticker measures.

    The ticker must not be the thing doing the work. Measured on one task, inline CPU work is
    serialised with the tick and simply consumes the slack -- it never shows up as lag, and the
    first version of this script reported `inline` as *faster than idle* because of it. That is
    not what an inline blocking call does to a server: it delays every OTHER task, which is what
    two tasks are needed to see.

    It yields between slices, which is the charitable version of the mistake -- one long call
    would freeze the loop outright and there would be nothing to measure."""
    done = 0
    stop = False

    async def hog() -> None:
        nonlocal done
        while not stop:
            x = 0
            for i in range(200_000):
                x += i * i
            done += 1
            await asyncio.sleep(0)      # a yield, which is the most generous reading

    task = asyncio.ensure_future(hog())
    try:
        lags = await measure(DURATION)
    finally:
        stop = True
        await task
    return lags, done


async def run_threaded(fn) -> tuple[list[float], int]:
    stop = threading.Event()
    result: list[int] = []
    t = threading.Thread(target=lambda: result.append(fn(stop)), daemon=True)
    t.start()
    try:
        lags = await measure(DURATION)
    finally:
        stop.set()
        t.join(timeout=30)
    return lags, (result[0] if result else 0)


# ---- reporting --------------------------------------------------------------------------------

def report(name: str, lags: list[float], work: int, note: str) -> None:
    lags = sorted(lags)
    p50 = statistics.median(lags)
    p99 = lags[int(len(lags) * 0.99) - 1]
    print(f"  {name:<16} {p50:>8.2f} {p99:>9.2f} {max(lags):>9.2f} {len(lags):>7} {work:>7}   {note}")


async def main() -> int:
    print(__doc__.split("\n")[0])
    print()
    print(f"python            {sys.version.split()[0]}")
    print(f"switch interval   {sys.getswitchinterval() * 1000:.1f} ms   (sys.getswitchinterval)")
    print(f"tick              {TICK * 1000:.0f} ms over {DURATION:.0f} s per regime")
    print(f"zstandard         {zstandard.__version__ if zstandard else 'NOT INSTALLED — regime skipped'}")
    print()
    print("  Lag is how late the loop woke, in milliseconds. Lower is better; the p99 is what a")
    print("  request would feel. 'work' is completed iterations, proving the load was real.")
    print()
    print(f"  {'regime':<16} {'p50':>8} {'p99':>9} {'max':>9} {'ticks':>7} {'work':>7}   what it shows")
    print(f"  {'-' * 16} {'-' * 8} {'-' * 9} {'-' * 9} {'-' * 7} {'-' * 7}   {'-' * 13}")

    lags, w = await run_idle()
    report("idle", lags, w, "the floor")
    baseline = statistics.median(sorted(lags))

    lags, w = await run_inline()
    report("inline", lags, w, "CPU on the loop — the mistake")

    lags, w = await run_threaded(burn_python)
    report("thread-python", lags, w, "GIL HELD — a thread is not enough")

    lags, w = await run_threaded(burn_hashlib)
    report("thread-hashlib", lags, w, "GIL released — stdlib proof")

    if zstandard is not None:
        lags, w = await run_threaded(burn_zstd)
        report("thread-zstd", lags, w, "GIL released — this project")

    print()
    print(f"  idle p50 was {baseline:.2f} ms. Read every other row against that, not against zero.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
