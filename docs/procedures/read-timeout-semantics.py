"""What does httpx's `read` timeout actually apply to?

Phase 4 found the router's `read=600.0` reachable by ordinary traffic: a ~41000-token request was
killed at exactly 600 s while LM Studio was still healthily prefilling. `handoff.md` then listed
three candidate fixes, one of which was "a timeout that resets on progress rather than on first
byte". This script exists to find out whether that is a fix at all or already the behaviour.

The question is not answerable by reading httpx's documentation, which says `read` is "the maximum
duration to wait for a chunk of data to be received" without saying whether the clock restarts. So
a backend is driven at three timing shapes against a short read timeout, and what dies is the
answer:

    /slow-headers    nothing at all for GAP seconds, then a complete quick reply
    /slow-first-body headers at once, then nothing for GAP seconds, then quick chunks
    /drip            headers at once, then a chunk every INTERVAL seconds for TOTAL seconds

With READ between INTERVAL and GAP, the outcomes separate the possibilities:

    /drip survives          -> the clock restarts on every chunk; "resets on progress" is already
                               the behaviour, and it is not one of the three fixes
    /drip dies              -> the timeout is a budget for the whole response
    the two slow ones die   -> a backend that takes a long time to start talking is killed
                               regardless, which is the Phase 4 case

Run it with no arguments; it starts its own backend on a spare port and prints a table.
"""

from __future__ import annotations

import asyncio
import time

import httpx

HOST, PORT = "127.0.0.1", 1298

GAP = 3.0  # silence before the reply starts, on the two slow paths
READ = 2.0  # the read timeout under test — between INTERVAL and GAP on purpose
INTERVAL = 1.0  # gap between chunks on /drip
TOTAL = 6.0  # how long /drip keeps going: three times READ, so a whole-response budget fails

HEAD = (
    b"HTTP/1.1 200 OK\r\n"
    b"content-type: text/event-stream\r\n"
    b"cache-control: no-cache\r\n"
    b"connection: close\r\n"
    b"\r\n"
)
CHUNK = b"event: ping\ndata: {}\n\n"


async def handle(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    request = await reader.read(4096)
    path = request.split(b" ")[1].decode() if b" " in request else "/"

    if path == "/slow-headers":
        await asyncio.sleep(GAP)
        writer.write(HEAD + CHUNK)
    elif path == "/slow-first-body":
        writer.write(HEAD)
        await writer.drain()
        await asyncio.sleep(GAP)
        writer.write(CHUNK)
    else:
        writer.write(HEAD)
        await writer.drain()
        deadline = time.monotonic() + TOTAL
        while time.monotonic() < deadline:
            writer.write(CHUNK)
            await writer.drain()
            await asyncio.sleep(INTERVAL)

    await writer.drain()
    writer.close()


async def attempt(client: httpx.AsyncClient, path: str) -> tuple[str, float, str]:
    """Read the whole streamed reply, and report what happened and how long it took."""
    started = time.monotonic()
    try:
        async with client.stream("GET", f"http://{HOST}:{PORT}{path}") as reply:
            chunks = 0
            async for _ in reply.aiter_bytes():
                chunks += 1
        return path, time.monotonic() - started, f"completed, {chunks} chunks"
    except httpx.ReadTimeout:
        return path, time.monotonic() - started, "ReadTimeout"
    except httpx.HTTPError as exc:
        return path, time.monotonic() - started, f"{type(exc).__name__}: {exc}"


async def main() -> None:
    server = await asyncio.start_server(handle, HOST, PORT)
    async with server:
        print(f"read={READ}s  gap={GAP}s  drip every {INTERVAL}s for {TOTAL}s\n")
        timeout = httpx.Timeout(connect=5.0, read=READ, write=5.0, pool=5.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            print(f"{'path':<18}{'elapsed':>9}  outcome")
            for path in ("/slow-headers", "/slow-first-body", "/drip"):
                name, elapsed, outcome = await attempt(client, path)
                print(f"{name:<18}{elapsed:>8.2f}s  {outcome}")


if __name__ == "__main__":
    asyncio.run(main())
