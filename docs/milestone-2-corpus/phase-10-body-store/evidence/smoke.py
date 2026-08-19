"""Task 7 — the smoke test: a dicted frame round-trips byte-identically.

**Run it with `uv run python`, never bare `python3`.** On this machine `python3` is
3.14 and `zstandard` lives in the 3.13 venv, so the wrong interpreter fails looking
like a missing dependency rather than like the wrong interpreter. The sibling
instruments here are stdlib-only and run either way; this one is not.

    uv run python docs/milestone-2-corpus/phase-10-body-store/evidence/smoke.py

It reads Phase 9's frozen corpus at `logs/corpus-gate/` and **writes nothing**. It
starts no router, drives no session and makes no network call.

Five checks, and each one is a thing Group C's store rests on:

  1. a dicted frame round-trips byte-identically at `compress_level_zstd` = 9,
     and every frame carries this dictionary's own dictID
  2. an undicted frame round-trips too and reports dictID 0 — the ordinary
     first-run case, since Group C ships before Group D
  3. the `ZstdCompressionParameters` path silently turns `write_dict_id` OFF,
     which is the trap Task 8 asserts against
  4. a dicted frame decompressed without its dictionary RAISES
  5. **a dictID is not a unique key.** What it does and does not identify, which
     is what Tasks 8, 13a and 14 have to be built against
  6. **but we can stamp our own**, and a content-derived one closes the gap that
     5 opens -- the measurement behind the owner's decision of 2026-08-19

**This is a one-shot gate, not an instrument**, which is why it is frozen here and
has no copy in `docs/procedures/`. Tasks 13 and 14f take over its assertions as
real tests against real code.
"""

import hashlib
import struct
import sys
from pathlib import Path

import zstandard


def content_dict_id(raw: bytes) -> int:
    """The dictID this project stamps: sha256 of the dictionary with its OWN id
    field zeroed, first four bytes, big-endian.

    Zeroing the field first is what makes it a defined fixed point rather than a
    self-reference. **`or 1` is not decoration:** dictID 0 means *no dictionary*,
    so a hash landing there would make every frame claim to be undicted.
    """
    b = bytearray(raw)
    b[4:8] = b"\x00\x00\x00\x00"
    return int.from_bytes(hashlib.sha256(bytes(b)).digest()[:4], "big") or 1


def restamp(raw: bytes, new_id: int) -> bytes:
    """Write a dictID into an already-trained dictionary. Bytes [4:8], LE."""
    b = bytearray(raw)
    b[4:8] = struct.pack("<I", new_id)
    return bytes(b)

REPO = Path(__file__).resolve().parents[4]
GATE = REPO / "logs" / "corpus-gate"
DICTS = GATE / "dicts"
# heldout-262144: trained by Phase 9's gate.py on run-01 + run-02, holding out
# run-03. So every body round-tripped below is material it has not seen -- which
# matters for the ratio printed, not for the round-trip, but costs nothing.
DICT = DICTS / "heldout-262144.dict"
LEVEL = 9  # corpus.compress_level_zstd's default, measured at Task 6
TRAIN_LEVEL = 3  # dictionary.py's constant, per plan.md's register
TRAIN_K, TRAIN_D = 8000, 8  # retrain.k's default, and TRAIN_D

failures: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}{'  ' + detail if detail else ''}")
    if not ok:
        failures.append(label)


def bodies() -> list[tuple[str, bytes]]:
    """Every non-empty body in run-03, both directions."""
    out = []
    for direction in ("requests", "responses"):
        for p in sorted((GATE / "run-03-anthropic" / direction).glob("*.bin")):
            data = p.read_bytes()
            if data:
                out.append((f"run-03/{direction}/{p.name}", data))
    return out


def training_samples() -> list[bytes]:
    """run-01's request bodies at or above retrain.sample_min_bytes."""
    d = GATE / "run-01-anthropic" / "requests"
    return [p.read_bytes() for p in sorted(d.glob("*.bin")) if p.stat().st_size >= 1024]


print(f"zstandard {zstandard.__version__}, backend {zstandard.backend}")
print(f"python {sys.version.split()[0]}")

zdict = zstandard.ZstdCompressionDict(DICT.read_bytes())
dict_id = zdict.dict_id()
corpus = bodies()
print(f"dictionary {DICT.name}, {DICT.stat().st_size} bytes, dictID {dict_id} = {dict_id:08x}")
print(f"corpus {len(corpus)} bodies from run-03, both directions\n")

cctx = zstandard.ZstdCompressor(level=LEVEL, dict_data=zdict)
dctx = zstandard.ZstdDecompressor(dict_data=zdict)

# ---- 1: the round-trip this task exists for --------------------------------
print("1 -- dicted round-trip at level 9, and the dictID in every frame")
plain = blobs = mismatched = missing_id = wrong_id = 0
for name, data in corpus:
    blob = cctx.compress(data)
    back = dctx.decompress(blob)
    if back != data:
        mismatched += 1
        print(f"        MISMATCH {name}")
    # the store content-addresses the PLAINTEXT, never the compressed bytes
    if hashlib.sha256(back).hexdigest() != hashlib.sha256(data).hexdigest():
        mismatched += 1
    frame_id = zstandard.get_frame_parameters(blob).dict_id
    if frame_id == 0:
        missing_id += 1
    elif frame_id != dict_id:
        wrong_id += 1
    plain += len(data)
    blobs += len(blob)

check("every body round-trips byte-identically", mismatched == 0,
      f"{len(corpus)} bodies, {mismatched} mismatched")
check("every frame carries a dictID", missing_id == 0, f"{missing_id} frames at 0")
check("and it is this dictionary's", wrong_id == 0, f"{wrong_id} naming another")
print(f"        {plain} -> {blobs} bytes, {plain / blobs:.3f}x"
      "  (both directions mixed -- NOT a comparable ratio)\n")

# ---- 2: what the store writes on day one -----------------------------------
print("2 -- undicted round-trip, the ordinary first-run case")
nc, nd = zstandard.ZstdCompressor(level=LEVEL), zstandard.ZstdDecompressor()
un_bad = un_plain = un_blob = 0
un_ids = set()
for _, data in corpus:
    blob = nc.compress(data)
    if nd.decompress(blob) != data:
        un_bad += 1
    un_ids.add(zstandard.get_frame_parameters(blob).dict_id)
    un_plain += len(data)
    un_blob += len(blob)
check("every body round-trips undicted", un_bad == 0, f"{un_bad} mismatched")
check("and every undicted frame reports dictID 0", un_ids == {0}, f"seen: {sorted(un_ids)}")
print(f"        {un_plain} -> {un_blob} bytes, {un_plain / un_blob:.3f}x\n")

# ---- 3: the trap Task 8 asserts against ------------------------------------
print("3 -- write_dict_id: the tuning path silently drops the dictID")
trap = zstandard.ZstdCompressor(
    dict_data=zdict,
    compression_params=zstandard.ZstdCompressionParameters.from_level(LEVEL),
)
trap_id = zstandard.get_frame_parameters(trap.compress(b"x" * 4096)).dict_id
check("compression_params WITHOUT write_dict_id loses it", trap_id == 0, f"frame dictID {trap_id}")

fixed = zstandard.ZstdCompressor(
    dict_data=zdict,
    compression_params=zstandard.ZstdCompressionParameters.from_level(LEVEL, write_dict_id=1),
)
fixed_id = zstandard.get_frame_parameters(fixed.compress(b"x" * 4096)).dict_id
check("write_dict_id=1 restores it", fixed_id == dict_id, f"frame dictID {fixed_id}")

safe_id = zstandard.get_frame_parameters(cctx.compress(b"x" * 4096)).dict_id
check("the plain ZstdCompressor(level=, dict_data=) path is safe", safe_id == dict_id,
      f"frame dictID {safe_id}")
print()

# ---- 4: a missing dictionary is loud ---------------------------------------
print("4 -- a dicted frame without its dictionary")
try:
    zstandard.ZstdDecompressor().decompress(cctx.compress(b"y" * 4096))
    check("raises rather than returning wrong bytes", False, "it returned")
except zstandard.ZstdError as exc:
    check("raises rather than returning wrong bytes", True, f"{exc}")
print()

# ---- 5: what a dictID actually identifies ----------------------------------
print("5 -- a dictID is NOT a unique key")

print("      a) Phase 9's eight frozen dictionaries, all from `zstd --train`:")
cli_ids, cli_shas = set(), set()
for p in sorted(DICTS.glob("*.dict")):
    raw = p.read_bytes()
    did = zstandard.ZstdCompressionDict(raw).dict_id()
    cli_ids.add(did)
    cli_shas.add(hashlib.sha256(raw).hexdigest())
    print(f"         {p.name:24} {len(raw):>7} bytes  dictID {did:>10} = {did:08x}")
check("`zstd --train` stamps ONE id on all of them", cli_ids == {1},
      f"{len(cli_shas)} distinct files, ids {sorted(cli_ids)}")

print("      b) the library's default dict_id=0, three runs on identical input:")
samples = training_samples()
lib = [zstandard.train_dictionary(112640, samples, k=TRAIN_K, d=TRAIN_D, level=TRAIN_LEVEL)
       for _ in range(3)]
for i, d in enumerate(lib):
    print(f"         run {i}: dictID {d.dict_id():>10} = {d.dict_id():08x}"
          f"  sha {hashlib.sha256(d.as_bytes()).hexdigest()[:12]}")
check("it is NOT random per call -- identical input, identical id",
      len({d.dict_id() for d in lib}) == 1, f"{len(samples)} samples")

print("      c) the same samples at three levels:")
by_level = {}
for lvl in (3, 9, 19):
    d = zstandard.train_dictionary(112640, samples, k=TRAIN_K, d=TRAIN_D, level=lvl)
    by_level[lvl] = d
    print(f"         level {lvl:>2}: dictID {d.dict_id():>10} = {d.dict_id():08x}"
          f"  sha {hashlib.sha256(d.as_bytes()).hexdigest()[:12]}")
check("one dictID, three DIFFERENT files",
      len({d.dict_id() for d in by_level.values()}) == 1
      and len({d.as_bytes() for d in by_level.values()}) == 3,
      "this is the hazard TRAIN_LEVEL is a fixed constant to keep latent")

print("      d) so what happens if the wrong file of a matching id is used?")
body = (GATE / "run-03-anthropic" / "requests" / "00002.bin").read_bytes()
blob = zstandard.ZstdCompressor(level=LEVEL, dict_data=by_level[19]).compress(body)
print(f"         blob trained at 19, frame dictID {zstandard.get_frame_parameters(blob).dict_id}")
try:
    back = zstandard.ZstdDecompressor(dict_data=by_level[19]).decompress(blob)
    check("the right file reads it", back == body, f"{len(back)} bytes")
except zstandard.ZstdError as exc:
    check("the right file reads it", False, f"{exc}")
try:
    zstandard.ZstdDecompressor(dict_data=by_level[3]).decompress(blob)
    check("the WRONG file of the same id fails loudly", False, "it returned bytes -- SILENT CORRUPTION")
except zstandard.ZstdError as exc:
    check("the WRONG file of the same id fails loudly", True, f"{exc}")

print()

# ---- 6: stamping our own dictID --------------------------------------------
print("6 -- we can assign the dictID ourselves, and it fixes what 5 found")

print("      a) train_dictionary(dict_id=N) takes any uint32 verbatim:")
for n in (0, 1, 32767, 32768, 2**31, 2**32 - 1, 2**32):
    d = zstandard.train_dictionary(112640, samples, k=TRAIN_K, d=TRAIN_D, level=TRAIN_LEVEL,
                                   dict_id=n)
    blob = zstandard.ZstdCompressor(level=LEVEL, dict_data=d).compress(body)
    print(f"         dict_id={n:<11} -> dict {d.dict_id():<11} frame "
          f"{zstandard.get_frame_parameters(blob).dict_id:<11} "
          f"round-trip {zstandard.ZstdDecompressor(dict_data=d).decompress(blob) == body}")
over = zstandard.train_dictionary(112640, samples, k=TRAIN_K, d=TRAIN_D, level=TRAIN_LEVEL,
                                  dict_id=2**32)
auto = zstandard.train_dictionary(112640, samples, k=TRAIN_K, d=TRAIN_D, level=TRAIN_LEVEL)
check("an OUT-OF-RANGE dict_id falls back silently, it does not raise",
      over.dict_id() == auto.dict_id(), "2**32 gave libzstd's own id, with no error")

print("      b) the id lives at bytes[4:8] of the dictionary file:")
d = zstandard.train_dictionary(112640, samples, k=TRAIN_K, d=TRAIN_D, level=TRAIN_LEVEL)
raw = d.as_bytes()
magic, embedded = struct.unpack("<II", raw[:8])
print(f"         magic 0x{magic:08X}, bytes[4:8] LE = {embedded}, dict_id() = {d.dict_id()}")
check("the field and the reported id agree", embedded == d.dict_id())

print("      c) so a trained dictionary can be re-stamped in place:")
stamped = zstandard.ZstdCompressionDict(restamp(raw, 0xDEADBEEF))
blob = zstandard.ZstdCompressor(level=LEVEL, dict_data=stamped).compress(body)
check("the new id is reported and lands in the frame",
      stamped.dict_id() == 0xDEADBEEF
      and zstandard.get_frame_parameters(blob).dict_id == 0xDEADBEEF)
check("it still round-trips",
      zstandard.ZstdDecompressor(dict_data=stamped).decompress(blob) == body)
check("compressed size is unchanged -- the id is pure metadata",
      len(blob) == len(zstandard.ZstdCompressor(level=LEVEL, dict_data=d).compress(body)))
try:
    zstandard.ZstdDecompressor(dict_data=d).decompress(blob)
    check("the original-id copy refuses the blob", False, "it read it")
except zstandard.ZstdError as exc:
    check("the original-id copy refuses the blob", True, f"{exc}")

print("      d) a CONTENT-derived id, which libzstd's is not:")
levels = {}
for lvl in (3, 9, 19):
    dd = zstandard.train_dictionary(112640, samples, k=TRAIN_K, d=TRAIN_D, level=lvl)
    levels[lvl] = dd.as_bytes()
    print(f"         level {lvl:>2}: libzstd {dd.dict_id():>10}   ours "
          f"{content_dict_id(levels[lvl]):>10} = {content_dict_id(levels[lvl]):08x}")
check("one libzstd id across the three levels",
      len({zstandard.ZstdCompressionDict(r).dict_id() for r in levels.values()}) == 1)
check("THREE distinct ids from the content", len({content_dict_id(r) for r in levels.values()}) == 3,
      "which is the collision closed")

print("      e) and the derivation is a defined fixed point:")
once = restamp(raw, content_dict_id(raw))
twice = restamp(once, content_dict_id(once))
check("re-stamping a stamped dictionary is idempotent", once == twice)
check("its id survives re-derivation", content_dict_id(once) == content_dict_id(raw))
check("a stamped dictionary still round-trips",
      zstandard.ZstdDecompressor(dict_data=zstandard.ZstdCompressionDict(once)).decompress(
          zstandard.ZstdCompressor(
              level=LEVEL, dict_data=zstandard.ZstdCompressionDict(once)).compress(body)) == body)

print()
if failures:
    print(f"FAILED: {len(failures)}")
    for f in failures:
        print(f"  - {f}")
    sys.exit(1)
print("all checks passed")
