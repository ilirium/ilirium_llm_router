"""Writes `bodies/needle.json` — a conversation too long for the window, with a codeword at the front.

The question this exists to answer is what LM Studio does when a request will not fit: refuse it, or
quietly drop the part that does not fit and answer anyway. The second is much worse, because a reply
built on a truncated conversation looks exactly like a reply built on a whole one — it is wrong
without ever failing, which is the concern `epd/EPD-002-token-counting-for-local-backends.md` raises
and the reason a local model with a small window is dangerous rather than merely limited.

So: a codeword at the very start, filler in the middle, and a question at the end asking for the
codeword back. If it comes back, nothing was dropped from the front. If it does not, something was —
and the `input_tokens` LM Studio reports says whether it admits to it.

    python3 docs/phase-4-probes/make_needle.py --tokens 12000
    python3 docs/phase-4-probes/probe.py needle

The codeword is deliberately not a word: a model that lost it cannot reconstruct it by being sensible.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

CODEWORD = "ZARDOZ-QUILL-7734"

# One filler line is about 22 tokens. Numbered so a truncated middle is visible in a reply, and
# varied enough not to collapse into a degenerate repeat the tokenizer or the cache would flatten.
FILLER = (
    "Line {n:05d}: the archivist recorded item {n} in the ledger, noting its weight as {w} grams "
    "and its shelf as {s}, before moving on to the next crate in the long row."
)
TOKENS_PER_LINE = 50  # measured, not guessed: 181 lines came back as 9166 input_tokens


def padding(target_tokens: int) -> str:
    lines = max(1, target_tokens // TOKENS_PER_LINE)
    return "\n".join(
        FILLER.format(n=n, w=(n * 37) % 900 + 100, s=chr(65 + n % 26) + str(n % 40))
        for n in range(lines)
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--tokens", type=int, default=12000, help="approximate filler size")
    args = parser.parse_args()

    filler = padding(args.tokens)
    body = {
        "model": "qwen/qwen3.5-9b",
        "max_tokens": 64,
        "stream": True,
        "messages": [
            {
                "role": "user",
                "content": (
                    f"Remember this codeword, I will ask for it at the end: {CODEWORD}\n\n"
                    f"Now here is the inventory log.\n\n{filler}\n\n"
                    "That is the end of the log. What was the codeword I gave you at the very "
                    "beginning, before the log? Reply with the codeword only, nothing else. "
                    "If you cannot find it, reply exactly: NOT FOUND"
                ),
            }
        ],
    }

    out = Path(__file__).resolve().parent / "bodies" / "needle.json"
    out.write_text(json.dumps(body, indent=2) + "\n")
    chars = len(body["messages"][0]["content"])
    print(f"wrote {out}")
    print(f"  filler ~{args.tokens} tokens, {chars} chars total, codeword {CODEWORD}")
    print("  expect the codeword back if nothing was dropped from the front")


if __name__ == "__main__":
    main()
