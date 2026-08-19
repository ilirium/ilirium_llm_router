# Does a background thread actually protect the event loop?

Two scripts answering one question, from inside and from outside:

| | |
|---|---|
| `event_loop_lag.py` | **The mechanism.** A coroutine ticks every 10 ms and records how late it woke. No server, no socket |
| `uvicorn_lag.py` | **The deployment.** Real FastAPI, real uvicorn on `127.0.0.1:8791`, HTTP round-trips timed from a **separate process** so the client cannot contend for the server's GIL |

```
uv run python docs/procedures/event-loop-lag/event_loop_lag.py
uv run python docs/procedures/event-loop-lag/uvicorn_lag.py
```

**`uv run python`, never bare `python3`** — `python3` on this machine is a 3.14 without `zstandard`.
Each takes about 15 seconds and prints to stdout; neither writes a file, so there is no `runs/`
directory and no `.gitignore` entry.

**The port is 8791**, chosen to avoid `8787` (the router) and `8799` (`../dying-backend/`). The
server is a subprocess and is terminated in a `finally`; the scripts have been checked to leave
nothing listening.

## Five regimes, and the two in the middle are the point

`idle` · `inline` · `thread-python` · `thread-hashlib` · `thread-zstd`

`hashlib` is in there so the central result reproduces **with no dependency at all** — CPython's own
C-API documentation names `zlib` and `hashlib` as detaching the thread state when compressing or
hashing, so it is the stdlib witness for the same mechanism `zstandard` uses.

Each run reports completed iterations per regime, so a suspiciously good result cannot come from a
load that was not actually running.

## What they found — 2026-08-19, and it corrected a document

Three consecutive runs of each, on Python 3.13.3, macOS 25.6 arm64, 5 ms switch interval. Results in
`../../wiki/background-work-in-fastapi.md`, which is the document they corrected: it had claimed a
plain thread suits *"CPU-bound background work"* without qualification, and **that is only true when
the work releases the GIL.**

**One defect was found by running rather than by reading.** The first version measured lag on the
same task that did the inline work — which serialises them, so the work consumed slack instead of
appearing as delay, and `inline` reported *better than idle*. **An inline blocking call harms every
OTHER task, so seeing it requires two.** The fix is in `run_inline`, with the reasoning in its
docstring.

## When re-running is worth it

- **After a Python upgrade**, especially a major one. The GIL's behaviour and the switch interval are
  exactly what changes, and free-threaded builds change the question entirely.
- **After changing what the corpus worker does**, if it stops being a thin wrapper around a
  GIL-releasing C call — the moment real Python work moves into that thread, `thread-python` is the
  row that describes it.
- **Before trusting the wiki page on a different machine.** Core count and OS scheduler both move
  these numbers; the ratios travel, the absolutes do not.

**Not worth re-running** to confirm a number already in the wiki page. The finding is a ratio between
regimes, and it has been stable across runs.
