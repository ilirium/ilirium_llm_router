# Phase 5 measurements

Three files behind the read-timeout half of `../phase-5-notes.md`. One is an instrument meant to be
re-run; two are evidence from live runs.

> **The instrument left this directory on 2026-08-16.** `read_timeout_semantics.py` is now
> `../procedures/read-timeout-semantics.py`, filed with the other re-runnable checks; the two `.txt`
> files stay here as evidence. That split is the point of the two tiers — an instrument that lives
> inside one phase's folder looks like a transcript, and the next person re-derives it.

| | |
|---|---|
| `read_timeout_semantics.py` | **Re-runnable, and no longer here** — see above. Drives a backend at three timing shapes to establish what httpx's `read` timeout applies to. A fact about a pinned library, so re-run it after a httpx bump |
| `needle-completes-at-1800.txt` | A 135391-byte request completing through the router at `read_timeout: 1800` — 41595 input tokens, first byte at 461712 ms, codeword returned |
| `needle-dies-at-30.txt` | The identical request at `read_timeout: 30`, dying at 30343 ms with Phase 4's exact failure signature |

## Why the pair, rather than one run

`needle-completes-at-1800.txt` alone proves less than it appears to. Phase 4 measured that request
being killed at 600247 ms; this run's first byte arrived at 461712 ms, **under the old ceiling**. So
it shows the request working, not the old setting failing — the machine was simply faster this time.

`needle-dies-at-30.txt` is what closes the gap. Same bytes, same model, same window, same session,
only the config changed, and it dies at the configured number. That is the per-backend field
deciding real traffic rather than merely reaching the request object, which is all a unit test can
show.

The pair also documents a spread worth remembering: **the same request straddles the old 600 s
threshold across runs.** That is the argument for a configurable number over a hard-coded one.

## Reproducing

`read_timeout_semantics.py` needs nothing — it starts its own backend and prints a table:

```
uv run python docs/phase-5-measurements/read_timeout_semantics.py
```

The needle runs need LM Studio with a model loaded, the router up on a config with the
`read_timeout` under test, and the body regenerated at the size that fills most of the window:

```
python3 docs/phase-4-probes/make_needle.py --tokens 41000
python3 docs/phase-4-probes/probe.py needle --router http://127.0.0.1:<port>
```

**Lower the config rather than enlarging the request** when the failure shape is what you want. The
30-second run reproduces Phase 4's ten-minute timeout in thirty seconds.

Note `make_needle.py` **overwrites** `../phase-4-probes/bodies/needle.json` in place, so running it
at a different size changes what `probe.py needle` does for whoever runs it next. These runs used
`--tokens 41000`; the file has been put back to its committed 12000-token default afterwards, and
anything reproducing them needs to regenerate it and put it back the same way.
