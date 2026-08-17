# Phase 9 evidence — the corpus gate

Two files: the instrument and what it printed.

| File | What it is |
|---|---|
| `gate.py` | The measurement. Run from the repository root |
| `results.txt` | Its output, 2026-08-17, verbatim |

## What produced it

A capture of **73 request bodies over three runs** on 2026-08-17, driven through the router by headless
`claude -p` sessions. `../notes.md` Tasks 6–7 record how, including the two runs that failed and why.

**The corpus itself is not here and cannot be.** `EPD-003` states the rule this obeys — a body store is
*"not committable, not by redaction and not by placeholder mapping"* — and a `zstd --train` dictionary
is a concatenation of verbatim substrings of its samples, so **the dictionaries are exactly as
uncommittable as the bodies.** Both stayed under `logs/corpus-gate/`, which `.gitignore:228` covers.

**So this evidence is not reproducible from the repository.** That is a real limitation and is stated
rather than glossed: `gate.py` re-run today would find no corpus. What is citable is the instrument and
the numbers it produced, not a path from one to the other. A future re-run needs a fresh capture, and
its figures would differ — this corpus is one afternoon on one machine.

## What it proves

**`EPD-003`'s two anchor numbers, measured synthetically in July, reproduce on a real corpus.** That
document grew twenty bodies by appending random dictionary words to one captured request, and its own
Evidence section flags the tail content as synthetic. Its figures survive contact with real traffic:

| | `EPD-003`, synthetic | Measured here, real |
|---|---|---|
| Per-file, no dictionary | 3.1x | **3.12x** |
| One long-window stream | 28.6x (level 3) / 31.3x (level 19) | **29.91x** (level 19) |

**And the load-bearing unmeasured hypothesis now has a number.** A dictionary trained on *other
sessions* and applied to a held-out one reaches **12.10x** — closing **82.8%** of the byte gap between
per-file and streamed storage, and leaving the per-file store **2.47x** the size of a stream rather than
the 9.6x it would be without a dictionary.

## What it does not answer

- **Whether this transfers to interactive use.** The capture is headless, and its static preamble is
  ~28 KB smaller than the frozen interactive one (82,611 against 111,028). A dictionary has room here
  that real use would not give it.
- **Whether it transfers to a mixed-backend corpus.** LM Studio contributed 3 bodies of 73.
- **Whether the dictionary training is stable.** It is not, at this sample size — see `../notes.md`.
- **Anything about responses.** The gate measures request bodies, which is where the volume is; run 2
  found a case where that assumption inverts, and it is recorded in the notes rather than measured here.
- **Anything about the write path.** Queue, drop policy, ceiling and truncation are Phase 10's, and
  `EPD-003`'s "Constraints this inherits from the router" already lists them.
