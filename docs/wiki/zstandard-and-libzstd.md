# `zstandard`, and what libzstd does underneath it

**Read this before assuming anything about the Python `zstandard` package** — whether it blocks the
interpreter, which backend is actually running, what its dictionary trainer does when you leave a
parameter out, or how a compressed frame finds its dictionary again. **Three of those four have an
answer that the documentation does not give and one that it gets misleading.**

**Established 2026-08-18 and 2026-08-19**, against `zstandard 0.25.0` on CPython 3.13, macOS arm64.
**Numbers are cited, never owned** — this page points at where they live, per `../README.md`'s rule
that a measurement has one canonical row.

---

## Which backend is running, because the answers differ by backend

`zstandard/__init__.py` selects **`backend_c`** on CPython and falls back to `backend_cffi` only on
PyPy or an unrecognised implementation — *"for CPython we require the C extension by default"*. **So
the C extension is the code path**, and the CFFI backend's behaviour is a different question.

**One thing changes that:** the `PYTHON_ZSTANDARD_IMPORT_POLICY` environment variable can force the
fallback. If anything ever sets it, everything below needs re-deriving.

**A trap that follows from this:** the CFFI backend is *readable Python* and the C one is not, so it
is the tempting place to go looking. Its docstrings describe **its own** implementation. Where the two
backends could differ, a claim read out of `backend_cffi.py` is evidence about the backend you are
not running.

## Does it release the GIL? Yes — and here is how to establish that rather than believe it

**It matters because it decides whether a worker thread is a real thread.** If libzstd held the GIL,
one worker and eight would be the same worker, and any threaded design built on it is wrong.

**The wheel ships no C sources** — only `backend_c.cpython-313-darwin.so`. So there is no
`Py_BEGIN_ALLOW_THREADS` line to quote. **Read the shipped binary instead**, which is strictly better
evidence: a source tree tells you what *would* be compiled, and the binary is what will actually run.

`Py_BEGIN_ALLOW_THREADS` / `Py_END_ALLOW_THREADS` expand to `PyEval_SaveThread()` and
`PyEval_RestoreThread()`, which survive compilation as **linker-visible symbols**. In this extension
they are the only `PyEval` symbols imported at all, which makes the search easy.

The one-shot compress path disassembles to exactly the macro pair around the work:

```
_ZstdCompressor_compress
     bl  … → _PyEval_SaveThread        GIL released
     bl  _ZSTD_compressStream2          the compression itself
     bl  … → _PyEval_RestoreThread      GIL reacquired
```

**Resolve the stub targets rather than guessing them:** on Mach-O, `__stubs` has fixed-size entries,
so a stub's address gives its index, and `otool -Iv` names the indirect symbol at that index.

**21 functions release it, and `SaveThread`/`RestoreThread` counts match in every one** — the balance
is the property worth checking, because an unbalanced pair leaks thread state rather than merely
failing to parallelise. They cover one-shot compress and decompress, the streaming and chunked paths
both directions, the batch helpers, and **`_train_dictionary`**.

**`_train_dictionary` releasing the GIL is the one people get wrong in the other direction.** Training
is kept off request-serving threads because it takes seconds to minutes — **not** because it would
freeze the interpreter. If you ever hear that second reason, it is wrong.

### Released is not the same as scales

Two separate claims, and they need separate evidence. A released GIL says the lock is not the
bottleneck; it says nothing about per-call Python overhead, allocation, or the disk. **The scaling was
measured separately** — see `../milestone-2-corpus/phase-10-body-store/evidence/`, whose benchmark
covers 1 / 2 / 4 threads, and `../procedures/corpus-benchmark/` for the instrument.

## Dictionary training: the parameter matters more than the tool

**`train_dictionary(dict_size, samples, k=, d=, f=, split_point=, accel=, notifications=, dict_id=,
level=, steps=, threads=)`.** Four of those decide whether you get a good dictionary and three of them
are easy to leave out.

| Parameter | What to know |
|---|---|
| **`k`** — segment size | **Set it explicitly.** Left to the library's own optimiser, the result on a small corpus is materially worse than `zstd --train`'s default; set to a sensible value it is materially better. **The tool is not the variable — `k` is**, and comparing only the defaults leads to the wrong conclusion about which tool to use |
| **`d`** — dmer size | Constraint `0 < d <= k`, reasonable range 6–16. Fixing it is fine; varying it is a sweep nobody here has needed |
| **`dict_size`** — the cap | **Non-monotonic.** A bigger cap is not a better dictionary, and this is confirmed on **both** trainers, so it is a property of training at small sample counts rather than of either tool |
| **`threads`** | **Only parallelises parameter variations.** With `k` fixed there are no variations, so it does nothing. `0` means one thread, negative means all logical CPUs |
| **`dict_id`** | **Defaults to `0`, which does *not* mean "no ID"** — libzstd assigns one. **It is not random per call either**, which the docstring's word "random" invites you to assume: identical training input gives an identical ID. See below, because this is load-bearing |

**Both trainers are libzstd underneath, and their *defaults* differ.** That is the whole finding, and
it is why "we use one tool everywhere" survives as a decision while "so the numbers are comparable"
does not follow from it. The measured gap is in
`../milestone-2-corpus/phase-10-body-store/notes.md`, Task 6.

**Non-monotonicity has a practical consequence:** a candidate dictionary is **measured against the one
it would replace**, never assumed better because its parameters look better. And it is measured on a
slice it did not train on, or the comparison flatters whichever side saw the data.

*One unresolved detail, recorded rather than smoothed over:* the **CFFI** backend's docstring says it
*"always calls `ZDICT_optimizeTrainFromBuffer_fastCover()`"* while describing the algorithm as COVER.
Whether the C backend does the same has not been checked here. It does not change the guidance —
setting `k` explicitly is what the measurement supports either way — but anyone reasoning from
algorithm names rather than from measurements should establish it first.

## How a compressed blob finds its dictionary again

**A zstd frame is self-describing: its header carries the dictionary ID.** Nothing external has to
record the pairing.

- `ZstdCompressionDict.dict_id()` — the ID of a dictionary you hold
- `zstandard.get_frame_parameters(blob)` → `FrameParameters` with `.dict_id`, plus `content_size`, `window_size`, `has_checksum`
- A frame compressed with no dictionary reports **`dict_id == 0`**
- A "content-only" dictionary built from raw bytes has `k == d == 0`, unlike a trained one

**Three consequences worth stating, because designs rest on them:**

1. **A blob never needs recompressing when the dictionary changes.** Old frames keep naming their old
   dictionary, so a new one applies to new data only.
2. **A dictionary can never be deleted** while any frame references it. The frame says which one it
   needs; it cannot reconstruct it.
3. **`dict_id=0` is ambiguous in a record, and 0 is the wrong value to write down.** "No dictionary"
   genuinely *is* ID 0, so a column recording it must distinguish that from "nothing was stored" some
   other way — a word rather than a number.

**An ID identifies a dictionary but does not describe it** — it does not say when it was trained or
from what. Putting the ID in the **filename** costs nothing and makes the pairing discoverable without
opening every candidate file.

### But a dictID is not a unique key, and two ways of getting one collide

*Corrected 2026-08-19. This page said the default `dict_id=0` yields a **random** ID, read off
`backend_cffi.py`'s docstring — **the backend that is not running**, which is the trap named at the top
of this page. Measured on `cext` instead, and the measurement is in
`../milestone-2-corpus/phase-10-body-store/notes.md`, Task 7.*

| Measured | Result |
|---|---|
| `train_dictionary(dict_id=0)`, three runs, identical input | **The same ID every time.** Not random per call |
| The same samples trained at levels **3, 9, 19** | **One ID, three different files** |
| Eight dictionaries from **`zstd --train`** | **Six distinct files, all carrying dictID `1`** |

**So the ID is determined by the training input and does not cover the entropy tables the level layers
on top.** Whether libzstd hashes the content or seeds a PRNG from it was not established, and the
design does not need it.

**Two consequences, and the second is the one that bites:**

1. **Do not bind a training level to an editable setting.** Change the level and you get different
   dictionary bytes under the *same* ID — a file the reader looks up by ID and finds the wrong version
   of.
2. **A wrong dictionary of a matching ID fails loudly.** Decompressing against it raises
   **`Data corruption detected`**; a frame decompressed with no dictionary at all raises
   **`Dictionary mismatch`**. Neither returns plausible wrong bytes, so a reader keying on dictID can
   afford to **try each candidate and keep the one that verifies**.

**`zstd --train`'s constant `1` is the practical hazard**, because it is not hypothetical: every
dictionary that tool produces collides with every other. A store that looks dictionaries up by ID has
to tolerate that or refuse CLI-trained input.

### You can assign the ID yourself, by either of two routes

**Measured 2026-08-19, same place.** This is the answer to *"can we stop relying on libzstd's ID?"*,
and it is yes.

| Route | What to know |
|---|---|
| `train_dictionary(dict_id=N)` | Takes **any `uint32` verbatim** — 1, 32767, 32768, `2**31`, `2**32-1` all reach the frame unchanged |
| **Bytes `[4:8]` of the dictionary file** | Little-endian, straight after magic `0xEC30A437`. Rewrite them and `dict_id()` reports the new value. **`ZstdCompressionDict` has no `dict_id` argument**, so this is the only way to change one after training |

**Re-stamping is safe and free.** The re-stamped dictionary round-trips and the compressed output is
**byte-for-byte the same size** — the ID plays no part in compression, only in what the frame records.
The original-ID copy then refuses those blobs with `Dictionary mismatch`, as it should.

**Two traps if you do this:**

1. **An out-of-range `dict_id` does not raise.** `2**32` silently yields libzstd's own assigned ID,
   which is indistinguishable from having passed `0`. **Mask to 32 bits in the caller.**
2. **Never let a derived ID be `0`.** Zero means *no dictionary*, so a hash landing there makes every
   frame claim to be undicted.

**If the ID is derived from the dictionary's content, zero its own ID field first.** The field lives
inside the bytes being hashed, so the derivation needs a canonical form; with the field zeroed it is a
fixed point, and re-stamping an already-stamped dictionary is idempotent.

## Reading list

- `python-zstandard` documentation — <https://python-zstandard.readthedocs.io/>
- `python-zstandard` source — <https://github.com/indygreg/python-zstandard>
- Zstandard — <https://facebook.github.io/zstd/>
- **The frame format, including the dictionary ID field** — <https://github.com/facebook/zstd/blob/dev/doc/zstd_compression_format.md>
- **Dictionary training API and the COVER/fastCover parameters** — <https://github.com/facebook/zstd/blob/dev/lib/zdict.h>
- The manual, for what a level actually maps to — <https://github.com/facebook/zstd/blob/dev/doc/zstd_manual.html>
- Thread State and the GIL, and the `Py_BEGIN_ALLOW_THREADS` pair — <https://docs.python.org/3/c-api/threads.html>
- `otool(1)`, for `-Iv` and the indirect symbol table — Apple's developer documentation, or `man otool`

*Upstream landing pages, chosen to outlive version numbers. **All checked from this machine on
2026-08-19**; every one returned 200.*

## Where these claims came from, and what expires

| Claim | How |
|---|---|
| `backend_c` on CPython; the env var can override | Read `zstandard/__init__.py` in this venv |
| The GIL is released, in 21 balanced functions | Disassembled the shipped `backend_c…so`; stubs resolved through the Mach-O indirect symbol table with `otool -Iv`. Full record in `../milestone-2-corpus/phase-10-body-store/notes.md`, Task 4 |
| `train_dictionary`'s signature and parameter semantics | Read `zstandard/__init__.pyi` and `zstandard/backend_cffi.py` in this venv |
| `dict_id=0` means libzstd assigns one, **deterministically in the training input** | The docstring calls it *random*, and that is the **CFFI** backend's docstring. **Measured on `cext`** at Phase 10's Task 7 — three runs, identical input, identical ID; and one ID across levels 3 / 9 / 19 with three different files |
| The trainers disagree at their defaults; training is non-monotonic | Measured — `../milestone-2-corpus/phase-10-body-store/evidence/`, Task 6. **The numbers live there and, after Phase 10's Task 21, in `../reference/measurements.md`** |

**What expires:** everything version-shaped — the symbol layout, the parameter list, which backend
ships. **What does not:** that a frame names its own dictionary, that `dict_id=0` is a real value
rather than an absence, that an ID is **not** a unique key, and that training defaults are where two
tools quietly disagree.

**And one method note, since this page has now been wrong once in exactly this way:** every claim here
that came from `backend_cffi.py` is evidence about the backend we do not run. The `dict_id` row was
corrected for that reason; the `k`, `d` and `threads` rows are still docstring-sourced and have not
been measured against `cext`.

**To re-derive any of it, read the installed package.** In the GIL case the documentation could not
have settled it at all, and the CFFI source would have answered about the backend that is not running.
