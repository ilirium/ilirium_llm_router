"""Observation 10: a day rollover with a dictionary swap in it.

The case observation 7 cannot reach. A blob is written into YESTERDAY's folder *after* the
writer has swapped to a new dictionary, so yesterday's folder must gain the new dictionary
too. Get the ordering backwards and this passes until a crash lands between two steps.

Driven against the real CorpusWriter rather than through the router, because the day comes
from the call's own timestamp and curl cannot set that.

**Two dictionaries are the prerequisite, and this frozen copy does not ship them.** The run it
was written against used `docs/procedures/dying-backend/runs/corpus-swap/dicts/`, which is
gitignored and disposable. To re-run: train a deliberately weak dictionary with
`--train-dict --maxdict 4096 --k 2000 --from logs/corpus-gate`, then a real one with
`--maxdict 262144 --k 8000`, and point DICT_A and DICT_B at the two files. They have to differ
enough that the swap is visible in the index.

**`uv run python`, never bare `python3`** -- 3.14 here, and `zstandard` is in the 3.13 venv.
"""
import hashlib
import shutil
import sys
from pathlib import Path

import zstandard

sys.path.insert(0, "src")
from ilirium_llm_router.corpus import CorpusWriter  # noqa: E402
from ilirium_llm_router.stats import CallRecord  # noqa: E402

SWAP = Path("docs/procedures/dying-backend/runs/corpus-swap/dicts")
DICT_A = SWAP / "req-2026-08-20T124341Z-16ac5f5a.dict"
DICT_B = SWAP / "req-2026-08-20T124405Z-0e4d84d1.dict"

root = Path(sys.argv[1])
shutil.rmtree(root, ignore_errors=True)
(root / "dicts").mkdir(parents=True)
shutil.copy(DICT_A, root / "dicts")


def rec(ts: str) -> CallRecord:
    return CallRecord(
        timestamp=ts, session_id="s", agent_id="", backend="lmstudio", model="local-test",
        path="/v1/messages", stream=True, input_tokens=1, output_tokens=1,
        cache_read_input_tokens=None, cache_creation_input_tokens=None, stop_reason="end_turn",
        request_bytes=1, response_bytes=1, ttfb_ms=1, duration_ms=1,
        error_status="ok", error_code="", error_message="",
    )


YESTERDAY = "2026-08-19T23:59:59.000+00:00"
TODAY = "2026-08-20T00:00:02.000+00:00"

w = CorpusWriter(directory=root, compress_level=9, body_max_bytes=1 << 20,
                 queue_max_bytes=1 << 26)
print("writer opened against:", w._dictionary_name if hasattr(w, "_dictionary_name") else "?")

# 1. A body into yesterday, against dictionary A.
w.submit(rec(YESTERDAY), b'{"body":"yesterday, against A, padded out a little"}', None)
w._queue.join() if hasattr(w._queue, "join") else None
import time; time.sleep(0.5)

# 2. Dictionary B appears while the writer is live.
shutil.copy(DICT_B, root / "dicts")

# 3. A body into TODAY -- opening a new day forces the rescan, so B is adopted.
w.submit(rec(TODAY), b'{"body":"today, first body of the new day, padded out a little"}', None)
time.sleep(0.5)

# 4. THE CASE: another body into YESTERDAY, now that the writer holds B.
w.submit(rec(YESTERDAY), b'{"body":"yesterday again, but the writer has swapped to B now"}', None)
time.sleep(0.5)
w.close()

for day in sorted(p for p in root.iterdir() if p.is_dir() and p.name[0].isdigit()):
    names = sorted(p.name for p in (day / "dicts").glob("*.dict"))
    print(f"\n{day.name}/dicts/  -> {len(names)}: {[n[-13:] for n in names]}")
    dicts = [zstandard.ZstdCompressionDict((day / 'dicts' / n).read_bytes()) for n in names]
    for blob in sorted(day.rglob("*.zst")):
        for d in dicts:
            try:
                plain = zstandard.ZstdDecompressor(dict_data=d).decompress(blob.read_bytes())
            except zstandard.ZstdError:
                continue
            status = "OK " if hashlib.sha256(plain).hexdigest() == blob.stem else "BAD"
            print(f"  {status} {blob.stem[:12]}…  {plain[:44]!r}")
            break
        else:
            print(f"  UNREADABLE {blob.stem[:12]}…  <- the silent failure this observation exists for")
    ids = [r.split(",")[-1] for r in (day / "index.csv").read_text().splitlines()[1:]]
    print(f"  index dict_ids: {ids}")
