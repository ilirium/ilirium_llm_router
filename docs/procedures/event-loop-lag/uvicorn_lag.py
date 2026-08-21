"""The same question, against a real uvicorn server: what does a client actually feel?

`event_loop_lag.py` measures the event loop from inside. This measures the thing that matters --
HTTP round-trip latency, from a separate PROCESS, against a real FastAPI app served by real
uvicorn. The server is a subprocess so the client's own work cannot contend for the server's GIL
and confound the result.

    GET  /ping              returns immediately. This is what is timed.
    POST /load/<regime>     starts a background load: python | hashlib | zstd | inline
    POST /stop              stops it

Regimes are the same five as the isolated test, so the two are directly comparable.

Run with `uv run python uvicorn_lag.py`. Binds 127.0.0.1:8791 -- NOT 8787 (the router) and NOT
8799 (the dying-backend stub). Nothing is written and nothing leaves the machine.
"""

from __future__ import annotations

import asyncio
import hashlib
import os
import statistics
import subprocess
import sys
import threading
import time

PORT = 8791
TICK = 0.010
DURATION = 3.0
BUF = b"\xa5" * (16 * 1024 * 1024)

try:
    import zstandard
except ImportError:
    zstandard = None


# ---- the server -------------------------------------------------------------------------------

def serve() -> None:
    from fastapi import FastAPI
    import uvicorn

    app = FastAPI()
    state: dict = {"stop": None, "thread": None, "task": None, "work": 0}

    def burn_python(stop: threading.Event) -> None:
        while not stop.is_set():
            x = 0
            for i in range(200_000):
                x += i * i
            state["work"] += 1

    def burn_hashlib(stop: threading.Event) -> None:
        while not stop.is_set():
            hashlib.sha256(BUF).digest()
            state["work"] += 1

    def burn_zstd(stop: threading.Event) -> None:
        cctx = zstandard.ZstdCompressor(level=9)
        while not stop.is_set():
            cctx.compress(BUF)
            state["work"] += 1

    BURNERS = {"python": burn_python, "hashlib": burn_hashlib, "zstd": burn_zstd}

    @app.get("/ping")
    async def ping() -> dict:
        return {"ok": True}

    @app.post("/load/{regime}")
    async def load(regime: str) -> dict:
        state["work"] = 0
        if regime == "inline":
            # a coroutine hogging the loop, yielding between slices -- the charitable version
            async def hog() -> None:
                while not state["stop_flag"]:
                    x = 0
                    for i in range(200_000):
                        x += i * i
                    state["work"] += 1
                    await asyncio.sleep(0)
            state["stop_flag"] = False
            state["task"] = asyncio.ensure_future(hog())
        else:
            stop = threading.Event()
            t = threading.Thread(target=BURNERS[regime], args=(stop,), daemon=True)
            t.start()
            state["stop"], state["thread"] = stop, t
        return {"started": regime}

    @app.post("/stop")
    async def stop_load() -> dict:
        state["stop_flag"] = True
        if state["task"] is not None:
            await state["task"]
            state["task"] = None
        if state["stop"] is not None:
            state["stop"].set()
            state["thread"].join(timeout=30)
            state["stop"] = state["thread"] = None
        return {"work": state["work"]}

    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="error")


# ---- the client -------------------------------------------------------------------------------

def measure(client, n: int) -> list[float]:
    """Round-trip milliseconds for `n` paced GET /ping calls."""
    out = []
    nxt = time.perf_counter()
    for _ in range(n):
        nxt += TICK
        d = nxt - time.perf_counter()
        if d > 0:
            time.sleep(d)
        t0 = time.perf_counter()
        client.get(f"http://127.0.0.1:{PORT}/ping")
        out.append((time.perf_counter() - t0) * 1000.0)
    return out


def report(name: str, lat: list[float], work: int, note: str) -> None:
    s = sorted(lat)
    print(f"  {name:<16} {statistics.median(s):>8.2f} {s[int(len(s) * 0.99) - 1]:>9.2f} "
          f"{max(s):>9.2f} {len(s):>7} {work:>7}   {note}")


def drive() -> int:
    import httpx

    print(__doc__.split("\n")[0])
    print()
    env = dict(os.environ, LAG_SERVER="1")
    proc = subprocess.Popen([sys.executable, __file__, "--serve"], env=env)
    try:
        with httpx.Client(timeout=60.0) as client:
            for _ in range(100):                       # wait for readiness
                try:
                    client.get(f"http://127.0.0.1:{PORT}/ping")
                    break
                except Exception:
                    time.sleep(0.1)
            else:
                print("server never came up")
                return 1

            n = int(DURATION / TICK)
            print(f"  uvicorn on 127.0.0.1:{PORT}, server pid {proc.pid}, "
                  f"{n} paced GET /ping per regime")
            print()
            print("  HTTP round-trip milliseconds, measured from a separate process.")
            print()
            print(f"  {'regime':<16} {'p50':>8} {'p99':>9} {'max':>9} {'reqs':>7} {'work':>7}   what it shows")
            print(f"  {'-' * 16} {'-' * 8} {'-' * 9} {'-' * 9} {'-' * 7} {'-' * 7}   {'-' * 13}")

            report("idle", measure(client, n), 0, "the floor")

            for regime, note in (
                ("inline", "CPU on the loop — the mistake"),
                ("python", "GIL HELD — a thread is not enough"),
                ("hashlib", "GIL released — stdlib proof"),
                ("zstd", "GIL released — this project"),
            ):
                if regime == "zstd" and zstandard is None:
                    continue
                client.post(f"http://127.0.0.1:{PORT}/load/{regime}")
                lat = measure(client, n)
                work = client.post(f"http://127.0.0.1:{PORT}/stop").json()["work"]
                label = regime if regime == "inline" else f"thread-{regime}"
                report(label, lat, work, note)
    finally:
        proc.terminate()
        proc.wait(timeout=10)
    print()
    return 0


if __name__ == "__main__":
    if "--serve" in sys.argv:
        serve()
    else:
        raise SystemExit(drive())
