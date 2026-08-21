"""Observation 2 and 3: open every blob in a day folder using ONLY that folder's own
dictionary copy, and check the content-addressed name against the plaintext."""
import hashlib
import sys
from pathlib import Path

import zstandard

day = Path(sys.argv[1])
dicts = [zstandard.ZstdCompressionDict(p.read_bytes()) for p in sorted((day / "dicts").glob("*.dict"))]
print(f"{len(dicts)} dictionary/dictionaries in {day.name}/dicts/")

ok = bad = 0
for blob in sorted(day.rglob("*.zst")):
    raw = blob.read_bytes()
    for d in dicts:
        try:
            plain = zstandard.ZstdDecompressor(dict_data=d).decompress(raw)
        except zstandard.ZstdError:
            continue
        digest = hashlib.sha256(plain).hexdigest()
        if digest == blob.stem:
            ok += 1
            print(f"  OK   {blob.parent.parent.name}/{blob.stem[:12]}…  "
                  f"{len(plain)} → {len(raw)} bytes  ({len(plain) / len(raw):.3f}x)")
        else:
            bad += 1
            print(f"  NAME MISMATCH {blob}")
        break
    else:
        bad += 1
        print(f"  UNREADABLE {blob}")
print(f"\n{ok} opened and verified, {bad} failed")
sys.exit(1 if bad else 0)
