"""Writes `bodies/image.json` — a request carrying a base64 PNG the answer can be checked against.

The image is four coloured quadrants: red, green, blue, yellow, clockwise from top left. A model
that cannot see it has to guess four colours in a stated order, which it will not do by accident —
so the reply distinguishes "the image arrived" from "the model was agreeable about an image it never
received". A single solid colour would not: one lucky guess reads as a pass.

Written by hand rather than with Pillow because the project has no image dependency and this needs
none: a PNG is a signature, three chunks and a zlib stream.

    python3 docs/phase-4-probes/make_image.py
"""

from __future__ import annotations

import base64
import json
import struct
import zlib
from pathlib import Path

SIZE = 64
RED, GREEN, BLUE, YELLOW = (220, 30, 30), (30, 170, 60), (40, 70, 210), (240, 210, 40)


def chunk(tag: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + tag
        + data
        + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    )


def quadrant_png() -> bytes:
    rows = []
    for y in range(SIZE):
        top, row = y < SIZE // 2, b"\x00"  # filter byte 0: no filtering on this scanline
        for x in range(SIZE):
            left = x < SIZE // 2
            row += bytes(RED if (top and left) else GREEN if top else BLUE if left else YELLOW)
        rows.append(row)
    header = struct.pack(">IIBBBBB", SIZE, SIZE, 8, 2, 0, 0, 0)  # 8-bit, truecolour RGB
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", header)
        + chunk(b"IDAT", zlib.compress(b"".join(rows)))
        + chunk(b"IEND", b"")
    )


def main() -> None:
    body = {
        "model": "qwen/qwen3.5-9b",
        "max_tokens": 256,
        "stream": True,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": base64.b64encode(quadrant_png()).decode(),
                        },
                    },
                    {
                        "type": "text",
                        "text": (
                            "This image has four coloured quadrants. Name the colour of each, "
                            "in this order: top-left, top-right, bottom-left, bottom-right. "
                            "Answer with four words only."
                        ),
                    },
                ],
            }
        ],
    }
    out = Path(__file__).resolve().parent / "bodies" / "image.json"
    out.write_text(json.dumps(body, indent=2) + "\n")
    print(f"wrote {out} — expect: red green blue yellow")


if __name__ == "__main__":
    main()
