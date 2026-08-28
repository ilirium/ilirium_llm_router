# The corpus benchmark

**Why it matters.** Phase 10 compresses every body the router carries and writes it on a background
thread. Three properties of that design were chosen from **published figures for other people's
machines** — that a worker thread parallelises at all, that level 19 is the right level, and that the
cost is compression rather than disk. This instrument replaces all three with numbers from the
machine the router actually runs on.

It exists because of a specific failure the owner caught: the plan asserted that `zstandard` releases
the GIL, as fact, having read neither the source nor a measurement. **If that had been false, one
worker thread and eight would have been the same thread** and the whole write path would have been
built on it. Task 4 settled the mechanism by reading the shipped binary; this settles the behaviour.

## The procedure

```
uv run python docs/procedures/corpus-benchmark/benchmark.py
```

**`uv run`, not `python3`.** On this machine `python3` is 3.14 and the project's venv is 3.13;
`zstandard` is installed into the venv, so the bare interpreter raises `ModuleNotFoundError`.
The sibling instruments here are stdlib-only and run either way — this one is the first that
does not, and it is written down because the failure looks like a missing dependency rather
than the wrong interpreter.

No arguments. It **starts nothing** — no router, no backend, no network, no API call. It reads the
bodies already in `logs/corpus-gate/`, writes scratch files into `logs/` and deletes them, and puts
its output in `runs/benchmark.txt`, overwritten each run.

Five sections, each deciding something:

| | Measures | Decides |
|---|---|---|
| **1 scaling** | wall clock at 1 / 2 / 4 threads | Whether a worker thread is a real thread. A flat line withdraws the thread design and sends the phase to measure a process pool instead |
| **2 level** | ratio and throughput at levels 3 / 9 / 19, with a dictionary and without | `corpus.compress_level_zstd`'s default — and how much ratio 19 still buys **once a dictionary already carries the static preamble**, which nobody had asked |
| **3 phase split** | sha256 / compress / write / fsync per body | Whether `store_ms` is compression or the disk. If it is the disk, the level barely matters |
| **4 precompute** | compressor built once against once per body | That the router holds one compressor for the process |
| **5 trainers** | `zstandard.train_dictionary()` against `zstd --train` | The one thing "use one tool" risks. Both wrap libzstd; their *training* defaults may not agree |

**Two corpora, and they are not interchangeable.** Ratios come from `/v1/messages` request bodies
over 1 KB, trained on run-01 + run-02 and evaluated on run-03 — `evidence/gate.py`'s rule and split
exactly, which is what makes them comparable with Phase 9's. Throughput and scaling come from every
body in every run, both directions, which is the realistic write-path mix and yields **no comparable
ratio at all**. The script labels which set each number came from.

**The held-out split is by session, not by shuffle**, and that is deliberate: a dictionary is applied
to sessions that did not exist when it was trained, so holding out whole sessions is the honest test.
A self-trained dictionary has seen the bodies it is measured on and flatters every number, which is
why `heldout-*.dict` is used here and `self-*.dict` is not.

## What was observed

**Run 2026-08-18** on the 8.8 MB corpus in `logs/corpus-gate/`. The full output is frozen at
`../../milestone-2-corpus/phase-10-body-store/evidence/results.txt`; the four things it settled:

1. **The GIL is released.** 3.34x at four threads, level 19 — 83% efficiency, best of three. A thread is a
   real thread, which the phase had asserted without evidence and Task 4 confirmed from the binary.
2. **Level 9 is the default.** It holds **94%** of level 19's dictionary-assisted ratio for **an
   eighth** of the per-body cost, and one worker at level 9 runs ~2,971 bodies/s — about 500x the
   target peak load.
3. **`store_ms` is mostly the filesystem at that level** — compression 40%, write + fsync + rename
   58%. At level 19 compression is 91%. `fsync` is cheap here (~0.03 ms); `rename` is not (~0.12 ms).
4. **The trainers disagree, and `k` matters more than the tool.** `zstandard.train_dictionary()` at
   its own choice of `k` is up to **15% worse** than `zstd --train`; at `k=8000` it is **13% better**.
   The surface is **non-monotonic** in both `k` and `--maxdict`, which is the same property Phase 9
   found in the binary. **A trainer must therefore set `k` explicitly**, and a candidate dictionary
   must be measured against the incumbent rather than assumed better.

**Re-running will not reproduce these**, and that is not a defect: they are one machine, one corpus,
one day. What should reproduce is the *shape* — the scaling curve, the knee at level 9, and the
non-monotonicity.

## What it does not answer

- **Whether archiving slows a *call*.** This measures throughput on a bench, with no router running
  and no session driving it. Latency under real concurrent load is a different measurement and Phase
  10 explicitly does not discharge it — `../../milestone-2-corpus/phase-10-body-store/plan.md`, "What
  this phase does not settle".
- **Anything about interactive sessions.** `logs/corpus-gate/` is a **headless** corpus whose static
  preamble is ~28 KB smaller than the frozen interactive one, 70 of its 73 bodies are Anthropic, and
  its sessions are short. **All three flatter a dictionary.**
- **Whether a response dictionary pays.** Responses are timed here and sized here, and that is the
  first time they have been measured at all — but nothing trains one, so their ratio is the undicted
  number and nothing more.
- **What happens on other hardware.** Every figure is one machine on one day. When these figures
  were taken, `logs/` sat inside a cloud-synced folder on this machine, which the fsync number is
  measuring whether you meant it to or not — and that was the number the router would actually pay
  here. **That stopped being true on 2026-08-25**, when the working tree moved to
  `~/Projects/local/`, which is not synced. *The recorded figures are not corrected — they are what
  was measured, on the setup named. But a re-run today measures a different filesystem, so the two
  are not comparable, and the caveat is dated rather than deleted so that stays visible.*
- **Whether the corpus is representative of anything.** 8.8 MB from three runs. It is what exists.
