"""Does a worker thread buy anything, and what compression level should it run at?

Phase 10 puts body compression on a background thread so the request path never waits for it. Three
things about that design were chosen from *published figures for other people's machines*, and this
script replaces all three with numbers from this one. It is Task 5 of
`../../milestone-2-corpus/phase-10-body-store/plan.md`; Task 6 runs it.

**It answers five questions, and each one decides something.**

    1. scaling      wall clock at 1 / 2 / 4 threads over the same bodies.
                    -> Four threads at ~a quarter of the time means the GIL is genuinely released
                       and a worker thread is a real thread. ~The same time means it is not, the
                       thread design is withdrawn, and a process pool becomes the next measurement.

    2. level        ratio and throughput at levels 3 / 9 / 19, with a dictionary and without.
                    -> `corpus.compress_level_zstd`'s default. Every figure this milestone owns was
                       measured at 19, which was an *offline* setting where time did not matter. The
                       half nobody has asked: how much ratio 19 still buys once a dictionary already
                       carries the static preamble.

    3. phase split  sha256 / compress / write / fsync, per body.
                    -> Whether `store_ms` is dominated by compression or by the disk. If it is the
                       disk, the level barely matters and question 2 is nearly moot.

    4. precompute   building the compressor once against once per body.
                    -> Confirms the router should hold one compressor for the process rather than
                       constructing one per call.

    5. trainers     `zstandard.train_dictionary()` against `zstd --train`, same samples.
                    -> The one thing "use one tool" risks. Both wrap libzstd, but their *training*
                       defaults may differ, and training defaults are exactly where Phase 9 found
                       non-monotonicity. If they disagree, Phase 9's figures stop being directly
                       comparable and this says by how much.

**On the corpus, and on which numbers may be compared with Phase 9's.** Two sets are used and they
are not interchangeable:

    ratio set   `/v1/messages` request bodies over 1 KB — `evidence/gate.py`'s rule exactly, so the
                ratios below sit on the same corpus definition Phase 9 measured. Trained on
                run-01 + run-02, evaluated on run-03, which is the held-out split gate.py used:
                a dictionary is applied to sessions that did not exist when it was trained, so the
                honest test holds out whole sessions rather than shuffling bodies.

    load set    every body in every run, both directions, any size. This is the realistic write-path
                mix and it is what the throughput and scaling numbers use. It is NOT comparable with
                Phase 9's ratios, and no ratio is reported from it.

**Responses are reported separately and this is the first time they are measured at all.** Phase 9's
gate measured request bodies only and its own `evidence/README.md` says it answers nothing about
responses. Nothing here trains a response dictionary; the point is only to stop guessing at their
size and cost.

**Where the scratch writes go, and why it matters here.** The write and fsync timings write real
files into `logs/`, because that is where the store will actually write — not into a system temp
directory on a different filesystem. On this machine `logs/` sits inside a cloud-synced folder, so
an fsync here is a measurement of *this* setup rather than of the disk, and that is the number the
router would actually pay. The scratch directory is removed at the end.

Run it with `uv run python <this file>` and no arguments — **not bare `python3`**, which on this
machine is a 3.14 that has no `zstandard` installed; the package lives in the project's 3.13 venv.
Output goes to stdout and to `runs/benchmark.txt`, overwritten each run —
per `../README.md`, a result worth keeping is copied out into a phase's `evidence/`.
"""

from __future__ import annotations

import hashlib
import os
import pathlib
import shutil
import statistics
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import zstandard

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CORPUS = ROOT / "logs" / "corpus-gate"
DICTS = CORPUS / "dicts"
RUNS = HERE / "runs"
SCRATCH = ROOT / "logs" / ".corpus-benchmark-scratch"

# run-03 postdates run-01 and carries the only subagent traffic, so it is both the honest test and
# the one that exercises a second preamble family. gate.py's choice, kept so the split matches.
TEST_RUN = "run-03-anthropic"

LEVELS = [3, 9, 19]
THREADS = [1, 2, 4]
# 112640 is zstd's own default. The others bracket it because the static preamble is ~110 KB, so the
# default cap sits *on* the thing the dictionary most needs to hold. gate.py's four, kept.
MAXDICTS = [112640, 262144, 524288, 1048576]
# The dictionary the level and phase-split sections use. Held-out rather than self-trained: a
# self-trained dictionary has seen the bodies it is measured on and flatters every number.
WORKING_DICT = DICTS / "heldout-112640.dict"

_local = threading.local()


class Tee:
    """Print once, land in two places. The run file is overwritten, per ../README.md."""

    def __init__(self, path: pathlib.Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self.fh = path.open("w")

    def __call__(self, line: str = "") -> None:
        print(line)
        self.fh.write(line + "\n")
        self.fh.flush()


def load(kind: str, min_size: int = 1, messages_only: bool = False) -> list[tuple[str, bytes]]:
    """Bodies from every run directory, tagged with the run they came from.

    `kind` is "requests" or "responses". With `messages_only` and `min_size=1001` this reproduces
    gate.py's rule exactly, which is what makes the ratio numbers comparable with Phase 9's.
    """
    out: list[tuple[str, bytes]] = []
    for run in sorted(CORPUS.iterdir()):
        manifest = run / "manifest.csv"
        if not run.is_dir() or not manifest.exists():
            continue
        for line in manifest.read_text().splitlines():
            f = line.split(",")
            if len(f) < 4:
                continue
            if messages_only and f[3] != "/v1/messages":
                continue
            body = run / kind / f"{int(f[0]):05d}.bin"
            if body.exists() and body.stat().st_size >= min_size:
                out.append((run.name, body.read_bytes()))
    return out


def cctx(level: int, dict_data: zstandard.ZstdCompressionDict | None) -> zstandard.ZstdCompressor:
    if dict_data is None:
        return zstandard.ZstdCompressor(level=level)
    return zstandard.ZstdCompressor(level=level, dict_data=dict_data)


def _chunk_worker(chunk: list[bytes], level: int, dict_data) -> int:
    """One compressor per thread, then a plain loop. This is what the router's worker does."""
    c = cctx(level, dict_data)
    return sum(len(c.compress(b)) for b in chunk)


def wall(bodies: list[bytes], level: int, dict_data, threads: int,
         repeats: int = 1) -> tuple[float, int]:
    """Wall seconds and total compressed bytes, compressing every body across N threads.

    `repeats` takes the MINIMUM rather than the mean. Wall time on a laptop is contaminated
    upwards by scheduling and thermal noise and never downwards, so the minimum is the closest
    estimate of the real cost. The scaling table needs this: a single pass put four-thread
    speedup anywhere between 3.3x and 4.0x across runs, purely from noise in the 1-thread
    baseline it is divided by, which is enough to make a recorded figure unreproducible.
    """
    chunks = [bodies[i::threads] for i in range(threads)]
    best, total = None, 0
    for _ in range(repeats):
        t0 = time.perf_counter()
        with ThreadPoolExecutor(max_workers=threads) as ex:
            total = sum(ex.map(lambda c: _chunk_worker(c, level, dict_data), chunks))
        secs = time.perf_counter() - t0
        best = secs if best is None else min(best, secs)
    return best or 0.0, total


def load_dict(path: pathlib.Path) -> zstandard.ZstdCompressionDict | None:
    if not path.exists():
        return None
    return zstandard.ZstdCompressionDict(path.read_bytes())


def section(say, title: str) -> None:
    say()
    say("=" * 78)
    say(title)
    say("=" * 78)


def main() -> int:
    say = Tee(RUNS / "benchmark.txt")

    if not CORPUS.exists():
        say(f"! no corpus at {CORPUS} — nothing to measure")
        return 1

    ratio_rows = load("requests", 1001, True)
    ratio_train = [b for run, b in ratio_rows if run != TEST_RUN]
    ratio_test = [b for run, b in ratio_rows if run == TEST_RUN]
    per_run: dict[str, int] = {}
    for run, _b in ratio_rows:
        per_run[run] = per_run.get(run, 0) + 1
    req_all = [b for _, b in load("requests")]
    res_all = [b for _, b in load("responses")]
    load_set = req_all + res_all

    say(f"zstandard {zstandard.__version__}, backend {zstandard.backend}, "
        f"libzstd {zstandard.ZSTD_VERSION}")
    say(f"python    {sys.version.split()[0]}   cpus {os.cpu_count()}")
    say()
    say(f"ratio set : train {len(ratio_train)} bodies / test {len(ratio_test)} bodies "
        f"({sum(len(b) for b in ratio_test):,} raw test bytes) — gate.py's rule and split")
    say("            per run: " + ",  ".join(f"{r} {n}" for r, n in sorted(per_run.items())))
    # Printed rather than asserted: section 5's caveat rests on the smallest run being far too
    # small to validate against, and a number stated only in prose is one nobody re-derives.
    smallest = min(per_run.values()) if per_run else 0
    if smallest < 10:
        say(f"            !! smallest run has {smallest} qualifying bodies — there is NO usable")
        say("            !! validation split in this corpus. See the caveat under section 5.")
    say(f"load  set : {len(req_all)} requests + {len(res_all)} responses = {len(load_set)} bodies, "
        f"{sum(len(b) for b in load_set):,} bytes")
    if req_all:
        say(f"            requests  median {statistics.median(len(b) for b in req_all):>9,.0f}  "
            f"max {max(len(b) for b in req_all):>9,}")
    if res_all:
        say(f"            responses median {statistics.median(len(b) for b in res_all):>9,.0f}  "
            f"max {max(len(b) for b in res_all):>9,}")

    wd = load_dict(WORKING_DICT)
    say(f"dictionary: {WORKING_DICT.name} "
        f"({WORKING_DICT.stat().st_size:,} bytes)" if wd else "dictionary: NONE FOUND")

    # ---- 1. scaling -------------------------------------------------------------------------
    section(say, "1. SCALING — is the GIL actually released, and does a second thread help?")
    say()
    say("Same bodies, same work, more threads. The GIL question is settled by the *shape* of this")
    say("table: near-linear speedup means released, a flat line means the threads are serialised.")
    say("Best of three passes at each thread count — a single pass moved the 4-thread figure")
    say("between 3.3x and 4.0x on this machine, all of it noise in the baseline it divides by.")
    for level in (19, 3):
        say()
        say(f"  level {level}, no dictionary, {len(load_set)} bodies")
        say(f"    {'threads':>8}  {'wall s':>9}  {'MB/s':>8}  {'speedup':>8}  {'efficiency':>10}")
        base = None
        for n in THREADS:
            secs, _ = wall(load_set, level, None, n, repeats=3)
            base = base if base is not None else secs
            mbs = sum(len(b) for b in load_set) / secs / 1e6
            say(f"    {n:>8}  {secs:>9.3f}  {mbs:>8.1f}  {base / secs:>7.2f}x  "
                f"{100 * base / secs / n:>9.0f}%")

    # ---- 2. level and dictionary -------------------------------------------------------------
    section(say, "2. LEVEL — ratio and throughput, with a dictionary and without")
    say()
    say("Ratio is measured on the HELD-OUT slice only, so it is comparable with Phase 9's numbers.")
    say("Throughput is on the full load set, single-threaded, which is what one worker is.")
    raw_test = sum(len(b) for b in ratio_test)
    raw_load = sum(len(b) for b in load_set)
    say()
    say(f"    {'level':>5}  {'dict':>6}  {'ratio':>7}  {'test bytes':>12}  {'MB/s':>8}  "
        f"{'bodies/s':>9}")
    for level in LEVELS:
        for label, d in (("no", None), ("yes", wd)):
            if label == "yes" and wd is None:
                continue
            c = cctx(level, d)
            comp_test = sum(len(c.compress(b)) for b in ratio_test)
            secs, _ = wall(load_set, level, d, 1)
            say(f"    {level:>5}  {label:>6}  {raw_test / comp_test:>6.2f}x  {comp_test:>12,}  "
                f"{raw_load / secs / 1e6:>8.1f}  {len(load_set) / secs:>9.0f}")

    # ---- 3. phase split ----------------------------------------------------------------------
    section(say, "3. PHASE SPLIT — is store_ms compression, or is it the disk?")
    say()
    say(f"Real files into {SCRATCH.relative_to(ROOT)} — the filesystem the store will use,")
    say("not a system temp directory. write -> fsync -> rename, which is the store's sequence.")
    SCRATCH.mkdir(parents=True, exist_ok=True)
    try:
        for level in LEVELS:
            c = cctx(level, wd)
            t = {"sha256": [], "compress": [], "write": [], "fsync": [], "rename": []}
            for i, b in enumerate(load_set):
                t0 = time.perf_counter()
                digest = hashlib.sha256(b).hexdigest()
                t1 = time.perf_counter()
                blob = c.compress(b)
                t2 = time.perf_counter()
                tmp = SCRATCH / f"tmp-{i}"
                fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC)
                os.write(fd, blob)
                t3 = time.perf_counter()
                os.fsync(fd)
                t4 = time.perf_counter()
                os.close(fd)
                os.replace(tmp, SCRATCH / digest[:16])
                t5 = time.perf_counter()
                t["sha256"].append(t1 - t0)
                t["compress"].append(t2 - t1)
                t["write"].append(t3 - t2)
                t["fsync"].append(t4 - t3)
                t["rename"].append(t5 - t4)
            total = sum(statistics.median(v) for v in t.values())
            say()
            say(f"  level {level} — median per body, and the share of the total")
            for k, v in t.items():
                med = statistics.median(v)
                say(f"    {k:>9}  {med * 1000:>8.3f} ms  {100 * med / total:>5.1f}%  "
                    f"(p95 {sorted(v)[int(len(v) * 0.95)] * 1000:.3f} ms)")
            say(f"    {'TOTAL':>9}  {total * 1000:>8.3f} ms   -> {1 / total:>6.0f} bodies/s")
    finally:
        shutil.rmtree(SCRATCH, ignore_errors=True)

    # ---- 4. precompute -----------------------------------------------------------------------
    section(say, "4. PRECOMPUTE — build the compressor once, or once per body?")
    say()
    if wd is not None:
        sample = load_set[: min(200, len(load_set))]
        t0 = time.perf_counter()
        c = cctx(9, wd)
        for b in sample:
            c.compress(b)
        once = time.perf_counter() - t0
        t0 = time.perf_counter()
        for b in sample:
            cctx(9, wd).compress(b)
        per_body = time.perf_counter() - t0
        say(f"  {len(sample)} bodies at level 9, with the dictionary loaded")
        say(f"    compressor built once      {once:>8.4f} s")
        say(f"    compressor built per body  {per_body:>8.4f} s   "
            f"({per_body / once:.2f}x, {1000 * (per_body - once) / len(sample):.3f} ms per call)")
        say()
        say("  The router builds it once at startup. This is the cost of getting that wrong.")
    else:
        say("  skipped — no dictionary")

    # ---- 5. trainers -------------------------------------------------------------------------
    section(say, "5. TRAINERS — does zstandard.train_dictionary() agree with `zstd --train`?")
    say()
    say("All evaluated on the same held-out slice at level 19. The binary column is Phase 9's")
    say("frozen dictionary, trained by `zstd --train` on exactly these samples — so this compares")
    say("two trainers, not two corpora.")
    say()
    say("THE PARAMETER MATTERS MORE THAN THE TOOL, and that is the finding. zstandard uses COVER")
    say("and, asked to optimise k itself, picks a poor one on a corpus this small. `zstd --train`")
    say("defaults to fastcover. Comparing only the defaults would have said the library is worse;")
    say("comparing at an explicit k says it is better. Both rows are printed for that reason.")
    say()
    say(f"    {'maxdict':>9}  {'trainer':>24}  {'bytes':>9}  {'ratio':>7}  {'vs binary':>9}")
    for maxdict in MAXDICTS:
        binary = DICTS / f"heldout-{maxdict}.dict"
        base = None
        if binary.exists():
            bd = zstandard.ZstdCompressionDict(binary.read_bytes())
            base = raw_test / sum(len(cctx(19, bd).compress(b)) for b in ratio_test)
            say(f"    {maxdict:>9,}  {'zstd --train (phase 9)':>24}  "
                f"{binary.stat().st_size:>9,}  {base:>6.2f}x  {'-':>9}")
        for label, kw in (
            ("zstandard, k auto", {}),
            ("zstandard, k=2000", {"k": 2000, "d": 8, "level": 19}),
            ("zstandard, k=8000", {"k": 8000, "d": 8, "level": 19}),
            ("zstandard, k=16000", {"k": 16000, "d": 8, "level": 19}),
        ):
            try:
                d = zstandard.train_dictionary(maxdict, ratio_train, **kw)
            except Exception as exc:  # a trainer that refuses is a result, not a crash
                say(f"    {maxdict:>9,}  {label:>24}  ! {type(exc).__name__}: {str(exc)[:30]}")
                continue
            r = raw_test / sum(len(cctx(19, d).compress(b)) for b in ratio_test)
            delta = f"{100 * (r - base) / base:+.0f}%" if base else "-"
            say(f"    {maxdict:>9,}  {label:>24}  {len(d.as_bytes()):>9,}  {r:>6.2f}x  "
                f"{delta:>9}")
        say()
    say("Read the columns, not one number: the surface is NON-MONOTONIC in both k and maxdict,")
    say("which is the same property Phase 9 found in `zstd --train` at this sample count. A")
    say("candidate dictionary is therefore measured against the incumbent, never assumed better.")
    say()
    say("!! There is no usable validation split in this corpus. run-02 contributes 2 qualifying")
    say("!! bodies, so any k chosen by reading the table above has been chosen with knowledge of")
    say("!! the test slice. The RANKING is stable across both slices and the plateau is real, but")
    say("!! the exact optimum is not established here, and Task 15 must not pretend otherwise.")

    say()
    say("=" * 78)
    say("Numbers above are this machine, this corpus, this day. Copy into evidence/ to keep them.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
