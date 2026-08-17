#!/usr/bin/env python3
"""Phase 9's gate: does a trained zstd dictionary recover the cross-body ratio for per-file storage?

Run from the repository root, after a capture exists under `logs/corpus-gate/`:

    python3 docs/milestone-2-corpus/phase-9-corpus-gate/evidence/gate.py

**It reads the corpus and writes dictionaries under `logs/`, and prints its results.** It never
writes into `docs/` — an instrument's output follows the instrument, and this instrument's input is
uncommittable, so its working files must stay where the corpus already is.

The question, from `../../../epd/EPD-003-capturing-bodies-for-a-corpus.md`: the sketch stores each
body as its own content-addressed file, which cannot see across bodies and so gets ~3x rather than the
28.6x measured across a concatenation. A shared dictionary is the only mechanism that would give that
back while keeping files independent. If it does, the sketch ships; if it does not, per-call files are
the wrong unit.

**The split is by session, not by shuffle.** A dictionary is trained once and applied to sessions that
did not exist when it was trained, so the honest test holds out *whole sessions*. Shuffling bodies
would leak: within a session, an earlier body is very nearly a prefix of a later one.

Two dictionaries are built and evaluated on the *same* held-out slice:

  self-trained   trained over every body, including the ones it is then measured on. This is what
                 EPD-003's "cheapest next step" specifies, and it is an upper bound rather than a
                 deployment figure.
  held-out       trained only on the training sessions. This is the deployable number.

**The gap between them is the point**, not a rigour footnote: a self-trained dictionary can memorise
session-local content, a held-out one can only carry the static preamble. So the difference measures
the static-versus-session-local split directly, and that is what decides the design.
"""

from __future__ import annotations

import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[4]
CORPUS = ROOT / "logs" / "corpus-gate"
DICTS = CORPUS / "dicts"

LEVEL = "-19"
# 112640 is zstd's own default. The others bracket it because `stats.py` measures the static preamble
# at ~110 KB and the frozen interactive capture at 111,028 bytes — so the default cap sits *on* the
# thing the dictionary most needs to hold, and a single point could not tell "a dictionary cannot
# recover this" from "the cap was too small".
MAXDICTS = [112640, 262144, 524288, 1048576]

# Sessions captured in run-01 train the dictionary; run-03's session is held out. run-03 genuinely
# postdates run-01 and carries the only subagent traffic, so it is both the honest test and the one
# that exercises a second preamble family.
TEST_RUN = "run-03-anthropic"


def load() -> list[tuple[str, str, bool, pathlib.Path]]:
    """Every `/v1/messages` request body over 1 KB, tagged with run, session and subagent-ness."""
    out = []
    for run in sorted(CORPUS.iterdir()):
        manifest = run / "manifest.csv"
        if not run.is_dir() or not manifest.exists():
            continue
        for line in manifest.read_text().splitlines():
            f = line.split(",")
            if len(f) < 4 or f[3] != "/v1/messages":
                continue
            body = run / "requests" / f"{int(f[0]):05d}.bin"
            if body.exists() and body.stat().st_size > 1000:
                out.append((run.name, f[1], bool(f[2]), body))
    return out


def zstd(args: list[str], data: bytes | None = None) -> bytes:
    return subprocess.run(
        ["zstd", "-q", LEVEL, *args], input=data, capture_output=True, check=False
    ).stdout


def per_file(paths: list[pathlib.Path], dictionary: pathlib.Path | None) -> int:
    """Each body compressed on its own, as the sketch would store it."""
    extra = ["-D", str(dictionary)] if dictionary else []
    return sum(len(zstd([*extra, "-c", str(p)])) for p in paths)


def stream(paths: list[pathlib.Path]) -> int:
    """One long-window pass over the concatenation — the ceiling per-file storage is chasing."""
    return len(zstd(["-c"], data=b"".join(p.read_bytes() for p in paths)))


def train(samples: list[pathlib.Path], name: str, maxdict: int) -> pathlib.Path | None:
    DICTS.mkdir(parents=True, exist_ok=True)
    target = DICTS / f"{name}-{maxdict}.dict"
    proc = subprocess.run(
        ["zstd", "--train", *[str(p) for p in samples], "-o", str(target),
         f"--maxdict={maxdict}", "--dictID=1"],
        capture_output=True, text=True, check=False,
    )
    if not target.exists():
        print(f"    ! --train failed for {name}/{maxdict}: {proc.stderr.strip()[:120]}")
        return None
    return target


def report(label: str, raw: int, size: int) -> None:
    print(f"    {label:28} {size:11,}  {raw / size:6.2f}x")


def main() -> int:
    bodies = load()
    if not bodies:
        print("No corpus under logs/corpus-gate/. Run the capture first.")
        return 1

    train_set = [b for b in bodies if b[0] != TEST_RUN]
    test_set = [b for b in bodies if b[0] == TEST_RUN]
    test_main = [p for *_, sub, p in ((b[0], b[1], b[2], b[3]) for b in test_set) if not sub]
    test_sub = [b[3] for b in test_set if b[2]]
    train_paths = [b[3] for b in train_set]
    test_paths = [b[3] for b in test_set]

    raw_test = sum(p.stat().st_size for p in test_paths)
    print(f"corpus     : {len(bodies)} bodies, {sum(p.stat().st_size for _, _, _, p in bodies):,} bytes")
    print(f"train      : {len(train_paths)} bodies, {sum(p.stat().st_size for p in train_paths):,} bytes")
    print(f"held-out   : {len(test_paths)} bodies, {raw_test:,} bytes "
          f"({len(test_main)} main + {len(test_sub)} subagent)")
    print(f"zstd level {LEVEL}\n")

    print("=== the two figures that bracket the question, on the held-out slice ===")
    report("raw", raw_test, raw_test)
    nodict = per_file(test_paths, None)
    report("per-file, no dictionary", raw_test, nodict)
    streamed = stream(test_paths)
    report("one long-window stream", raw_test, streamed)
    print(f"\n    the gap a dictionary must close: {nodict / streamed:.1f}x\n")

    print("=== per-file with a dictionary, swept over --maxdict ===")
    for maxdict in MAXDICTS:
        print(f"  --maxdict={maxdict:,}")
        selfd = train([p for _, _, _, p in bodies], "self", maxdict)
        heldd = train(train_paths, "heldout", maxdict)
        if selfd:
            report("per-file, self-trained dict", raw_test, per_file(test_paths, selfd))
        if heldd:
            held = per_file(test_paths, heldd)
            report("per-file, held-out dict", raw_test, held)
            print(f"    {'':28} {'':11}  recovers "
                  f"{100 * (nodict - held) / (nodict - streamed):5.1f}% of the gap")
        print()

    print("=== does a second preamble family dilute it? (held-out dict, 512 KB) ===")
    d = DICTS / "heldout-524288.dict"
    if d.exists():
        for label, paths in (("main conversation", test_main), ("subagent", test_sub)):
            if paths:
                r = sum(p.stat().st_size for p in paths)
                report(f"{label} ({len(paths)} bodies)", r, per_file(paths, d))
    return 0


if __name__ == "__main__":
    sys.exit(main())
