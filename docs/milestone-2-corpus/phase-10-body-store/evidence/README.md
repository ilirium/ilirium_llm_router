# Phase 10 evidence — the benchmark, the smoke test, and Task 18's two probes

**Four runs, six files.** Task 6's benchmark, Task 7's smoke test, and the two instruments Task 18
used to drive observations no test covers.

| File | What it is |
|---|---|
| `benchmark.py` | The measurement, frozen at Task 6. The live copy is `../../../procedures/corpus-benchmark/benchmark.py` and it will drift; this one is what produced the numbers below |
| `results.txt` | Its output, 2026-08-18, verbatim |
| `smoke.py` | **Task 7's round-trip check, 2026-08-19.** It has **no live copy** — see below |
| `smoke.txt` | Its output, 2026-08-19, verbatim |
| `task-18-open-a-day-folder.py` | **Observations 2, 3 and 7, 2026-08-20.** Opens every blob in a day folder using **only that folder's own `dicts/`**, and checks each plaintext against the sha256 in its filename. Takes the day folder as its one argument, so it runs against any of them |
| `task-18-rollover-with-a-swap.py` | **Observation 10, 2026-08-20.** A day rollover **with a dictionary swap inside it** — a body stored into *yesterday's* folder after the writer has swapped. **The one observation no test covers**, because the day comes from the call's own timestamp and neither `curl` nor `TestClient` can set that |
**For the benchmark, run the live copy, not this one** — `../../../procedures/` is the re-runnable
tier and this is the archive. The rule is `../../../README.md`'s: an instrument's script lives in
`procedures/`, and the results a claim rests on are frozen in the phase's `evidence/`. Phase 9 froze
`gate.py` and `results.txt` for exactly this reason.

**`smoke.py` is the exception and it is deliberate: it has no `procedures/` copy at all.** That tier is
for checks *worth re-running*, and this one is a **one-shot gate** in front of Task 8 — Tasks 13 and
14f take over every assertion in it as real tests against real code, at which point re-running a
standalone script would be testing the library rather than the router. **Where the two tiers would
say different things, a check that has been superseded belongs only in the archive.**

**Both want `uv run python`, never bare `python3`** — on this machine `python3` is 3.14 and
`zstandard` is in the 3.13 venv, so the wrong interpreter fails looking like a missing dependency.

**Task 18's two probes are frozen here and have no `procedures/` copy, for different reasons than
`smoke.py`.** `task-18-open-a-day-folder.py` is genuinely re-runnable and takes a path, but what it
checks — a day folder opening from itself alone — is now asserted by `tests/test_corpus.py` against
real code, so the script is the *record of how it was driven* rather than the check itself.
`task-18-rollover-with-a-swap.py` is the opposite case: **nothing in the suite covers it**, because
the day a blob lands in comes from the call's own timestamp and no test client can set that. It is
kept because losing it would mean rewriting it from the notes.

**Neither is the reproduction of the counter defect.** That one became a permanent test —
`tests/test_integration.py::test_a_caller_gone_at_response_start_is_counted_as_lost` — which is
strictly better than an evidence script, and is why no third file sits here.

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

## What the benchmark establishes, in four lines

1. **The GIL is released** — 3.34x at four threads, level 19, best of three. Task 4 read that off the binary; this
   measures it. The worker thread is a real thread.
2. **Level 9 is the default**, measured rather than assumed: it sits at the knee, holding 94% of level
   19's dictionary-assisted ratio for **an eighth** of the per-body cost.
3. **`store_ms` is not one thing.** At level 9 compression is 40% of it and the filesystem is 58%; at
   level 19 compression is 91%. The level decides which.
4. **The two trainers disagree, and the parameter matters more than the tool** — `zstandard` at
   default `k` is up to 15% *worse* than `zstd --train`, and at `k=8000` it is 13% *better*.

## What the smoke test establishes

**Its own headline is the boring one and that is the point:** a dicted frame round-trips
byte-identically at level 9, over 40 bodies, both directions — and so does an undicted one, which is
what Group C actually ships on, `<dir>/dicts/` being empty until Task 15.

**Three things behind it are worth more than the headline:**

1. **The `write_dict_id` trap is real on the backend that is running.** A compressor built through
   `ZstdCompressionParameters.from_level(9)` writes frames with **dictID 0** while holding a
   dictionary. Task 8's requirement to assert the field cited `backend_cffi.py`, which is the backend
   we are **not** on; this measures `cext`. The plain `ZstdCompressor(level=, dict_data=)` path is
   safe.
2. **A dictID is not a unique key.** Phase 9's eight frozen dictionaries are six distinct files
   carrying **one** dictID — `zstd --train` stamps `1` on everything. And `zstandard`'s own trainer at
   `dict_id=0` is **not random per call**: identical input gives an identical ID, three runs running.
3. **One dictID, three files, at levels 3 / 9 / 19** — `../plan.md`'s stated hazard, reproduced
   independently, and the reason `TRAIN_LEVEL` is a fixed constant. **The consequence the plan does not
   state:** using the wrong file of a matching ID raises **`Data corruption detected`**. It does not
   return plausible wrong bytes.

## What the smoke test does not establish

- **Any ratio worth quoting.** Its `10.732x` mixes both directions against a request-trained
  dictionary. The comparable figure is Task 15's, and `../plan.md` expects it near **12.920x**.
- **The mechanism behind the dictID.** Whether libzstd hashes the dictionary content or seeds a PRNG
  from it was not established and does not need to be. What is established is that the ID is
  **determined by the training input and does not cover the entropy tables the level layers on top**.
- **Anything about the router.** No code of ours ran; `corpus.py` did not exist yet.

## What the benchmark does not establish

- **Whether archiving slows a call.** No router ran. Phase 10 does not discharge that failure mode and
  `../plan.md` says so.
- **The right `k` or `--maxdict`.** The corpus has **no usable validation split** — run-02 contributes
  two qualifying bodies — so any parameter read off `results.txt` was chosen with knowledge of the test
  slice. The ranking is stable and the plateau is real; the optimum is not established.
- **Anything about interactive sessions or about responses under a dictionary.** The corpus is
  headless, 70 of its 73 request bodies are Anthropic, and no response dictionary was trained.
