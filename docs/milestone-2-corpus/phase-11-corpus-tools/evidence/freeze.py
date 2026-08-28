"""Freeze Phase 11's evidence slice: the corpus index, redacted. Never the blobs.

**What this is.** Phase 11's Task 7. `../../../README.md` says evidence is cited to something
committed, because `logs/` is gitignored and rotates. The source here is the owner's live corpus at
`to-run-server/logs/corpus/`, which **grows while it is read** — so this script freezes a labelled
snapshot and stamps the moment it was taken into the output.

**It is not reproducible, and that is not a defect.** Re-running it on a later day produces a larger
slice with a different mapping. The committed CSVs are the record; this file is here so the redaction
is auditable, not so the result can be regenerated.

**Redaction is to stable placeholders in first-appearance order**, never by blanking —
`../../../README.md` is explicit that blanking destroys the finding while protecting nothing, because
*which rows share a `session_id`* is the basis of every per-session claim this phase makes. Equality
is preserved exactly; the values are not recorded anywhere.

Run with `python3 <this file>` from anywhere. It imports nothing outside the standard library, so it
does **not** need the project venv — unlike anything touching `zstandard`.
"""

from __future__ import annotations

import csv
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

CORPUS = Path("/Users/ilirium/Projects/local/ilirium_llm_router/to-run-server/logs/corpus")
OUT = Path(__file__).resolve().parent
DAYS = ["2026-08-21", "2026-08-24", "2026-08-25", "2026-08-26"]

# The five `request_ref` sentinels — values, not digests. A sentinel passed through a digest
# redactor would become a fake identifier and break the "no blob here" reading the extractor needs.
SENTINELS = {"dropped", "too_large", "absent", "error", "none", ""}

# Identifier families redacted. `request_dict_id` is deliberately NOT one: it names a dictionary,
# not a person, and `9dd33823` is already committed in docs/status.md.
FAMILIES = {"session_id": "session", "agent_id": "agent",
            "request_ref": "req", "response_ref": "resp"}

# Secrets are a separate problem from identifiers — README.md's second practical rule.
#
# **The scan runs on the redacted row, not the raw one, and nothing is written until it is clean.**
# What matters is whether the *committed* file carries a secret, and scanning the output also covers
# a column this script does not redact.
#
# `(?![0-9a-f]+$)` is not decoration. A first version without it reported **1913 suspect cells** and
# every one was a **sha256 digest** — 64 hex characters satisfy any "long base64-ish blob" rule.
# `CLAUDE.md`: when a check comes back negative, fix the instrument before believing the result.
SECRET = re.compile(
    r"(sk-[A-Za-z0-9_\-]{8,}|Bearer\s+\S+|api[_-]?key|authorization|x-api-key"
    r"|(?![0-9a-f]+$)[A-Za-z0-9+/]{60,}={0,2})",
    re.IGNORECASE,
)


def main() -> int:
    if not CORPUS.is_dir():
        print(f"error: {CORPUS} is not a directory", file=sys.stderr)
        return 1

    taken = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    maps: dict[str, dict[str, str]] = {name: {} for name in FAMILIES}
    hits: list[str] = []
    totals = Counter()

    def placeholder(family: str, raw: str) -> str:
        """First-appearance order, stable, equality-preserving. Empty and sentinel stay themselves."""
        if raw == "" or (family in ("request_ref", "response_ref") and raw in SENTINELS):
            return raw
        table = maps[family]
        if raw not in table:
            table[raw] = f"{FAMILIES[family]}-{len(table) + 1:02d}"
        return table[raw]

    for day in DAYS:
        source = CORPUS / day / "index.csv"
        with source.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            columns = reader.fieldnames or []
            rows = list(reader)

        for row in rows:
            for family in FAMILIES:
                row[family] = placeholder(family, row[family])
            for column, cell in row.items():
                if cell and SECRET.search(cell):
                    hits.append(f"{day}, column {column}: {cell[:80]}")

        if hits:
            break  # nothing is written once anything is suspect

        target = OUT / f"index-{day}.csv"
        with target.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)

        totals[day] = len(rows)
        print(f"{day}: {len(rows)} rows → {target.name}")

    print(f"\ntaken: {taken}")
    print(f"total rows: {sum(totals.values())}")
    for family in FAMILIES:
        print(f"{family}: {len(maps[family])} distinct value(s) redacted")

    print("\nsecrets pass (separate from identifiers, per README.md):")
    if hits:
        print(f"  {len(hits)} SUSPECT CELL(S) — nothing was written, inspect before committing")
        for hit in hits[:20]:
            print(f"    {hit}")
        return 1
    print("  clean — no cell matched a key, bearer token or long base64 pattern")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
