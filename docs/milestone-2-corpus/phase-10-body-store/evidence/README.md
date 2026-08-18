# Phase 10 evidence — the corpus benchmark

Two files: the instrument and what it printed.

| File | What it is |
|---|---|
| `benchmark.py` | The measurement, frozen at Task 6. The live copy is `../../../procedures/corpus-benchmark/benchmark.py` and it will drift; this one is what produced the numbers below |
| `results.txt` | Its output, 2026-08-18, verbatim |

**Run the live copy, not this one** — `../../../procedures/` is the re-runnable tier and this is the
archive. The rule is `../../../README.md`'s: an instrument's script lives in `procedures/`, and the
results a claim rests on are frozen in the phase's `evidence/`. Phase 9 froze `gate.py` and
`results.txt` for exactly this reason.

*This directory exists because the forward review found that **nothing froze the benchmark's results**
and nothing said why the directory was absent — both of which `../../../README.md` requires. It was
finding 9 of this session's pass and finding 4 in the merged list.*

## What produced it

The **8.8 MB corpus already on disk** at `logs/corpus-gate/`, captured by Phase 9 on 2026-08-17 —
136 bodies over three runs, 68 requests and 68 responses. **Nothing was captured for this phase.**
The benchmark starts no router, drives no session and makes no network call; that was the scope the
opening interview settled, and it is why Task 6 needed no capture.

**The corpus is not here and cannot be**, for the reason `EPD-003` gives and Phase 9's
`../../phase-9-corpus-gate/evidence/README.md` states in full: a body store is not committable, and a
trained dictionary is a concatenation of verbatim substrings of its samples, **so the dictionaries are
exactly as uncommittable as the bodies.** Both stay under `logs/`, which `.gitignore:228` covers.

**So these numbers are not reproducible from a clone.** A clone has the instrument and the output and
no path between them. On *this* machine the corpus still exists and the script re-runs — but it is
untracked and unbacked-up, and nothing should be built on its being there.

## What it establishes, in four lines

1. **The GIL is released** — 3.34x at four threads, level 19, best of three. Task 4 read that off the binary; this
   measures it. The worker thread is a real thread.
2. **Level 9 is the default**, measured rather than assumed: it sits at the knee, holding 94% of level
   19's dictionary-assisted ratio for **an eighth** of the per-body cost.
3. **`store_ms` is not one thing.** At level 9 compression is 40% of it and the filesystem is 58%; at
   level 19 compression is 91%. The level decides which.
4. **The two trainers disagree, and the parameter matters more than the tool** — `zstandard` at
   default `k` is up to 15% *worse* than `zstd --train`, and at `k=8000` it is 13% *better*.

## What it does not establish

- **Whether archiving slows a call.** No router ran. Phase 10 does not discharge that failure mode and
  `../plan.md` says so.
- **The right `k` or `--maxdict`.** The corpus has **no usable validation split** — run-02 contributes
  two qualifying bodies — so any parameter read off `results.txt` was chosen with knowledge of the test
  slice. The ranking is stable and the plateau is real; the optimum is not established.
- **Anything about interactive sessions or about responses under a dictionary.** The corpus is
  headless, 70 of its 73 request bodies are Anthropic, and no response dictionary was trained.
