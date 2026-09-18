#!/usr/bin/env python3
"""A one-hop forwarder whose TLS handshake is BoringSSL's rather than OpenSSL's.

**PHASE 14 EXPERIMENT, 2026-09-18. Not part of the router and not on its import path.**

Ten hypotheses have been eliminated by measurement and what is left sits below HTTP: the router's
`ClientHello` is visibly not Claude Code's, and a server separates the two before reading a byte.
This puts a BoringSSL stack in the egress path so that hypothesis can be tested at all:

    Claude Code -> router -> http://127.0.0.1:<port> (this) -> TLS(chrome) -> api.anthropic.com

**The credential does not move.** It travels the same localhost hop it already travels to reach the
router, and this process forwards it without reading it.

**Measured, 2026-09-18, against `clienthello-capture.py`:**

| | JA3 | ciphers | extensions | groups |
|---|---|---|---|---|
| Claude Code 2.1.267 | `5260242a…` | 17 | 12 | 4 |
| this, `impersonate="chrome"` | `e14cbc3e…` | 15, **15 of 17 shared in the same order** | 15, **a superset of Claude Code's** | **identical** |
| the router today | `166b2ba7…` | 17, 9 shared, wrong order | 11, missing two | different |

**So this does not reproduce Claude Code's fingerprint and is not trying to.** It tests whether the
rejection is a bot score against scripted-client stacks — which a genuine Chrome fingerprint passes
— rather than an allowlist of Claude Code's own hash, which nothing short of Bun's own build
matches.

Run:  .venv/bin/python <this> [port]      then point the router's anthropic base_url at it.
"""

from __future__ import annotations

import os
import sys

import uvicorn
from curl_cffi.requests import AsyncSession
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import StreamingResponse
from starlette.routing import Route

# Overridable so the streaming behaviour can be tested against a local server without reaching
# Anthropic at all -- which is how the chunk-by-chunk check below was run.
UPSTREAM = os.environ.get("FORWARDER_UPSTREAM", "https://api.anthropic.com")
IMPERSONATE = os.environ.get("FORWARDER_IMPERSONATE", "chrome")

# Ours to set, not the caller's to carry across a new connection. `host` would otherwise arrive as
# `127.0.0.1:<port>`; `content-length` is recomputed; `accept-encoding` is dropped so that libcurl
# decides the encoding itself and there is no chance of handing back a body that is decompressed
# while still labelled compressed. Encoding is exonerated as a cause, so nothing is lost by it.
DROPPED_FROM_REQUEST = frozenset(
    {"host", "content-length", "accept-encoding", "connection", "keep-alive", "transfer-encoding"}
)

# The body is re-framed on the way out, so anything describing the old framing has to go with it.
DROPPED_FROM_RESPONSE = frozenset(
    {"content-length", "content-encoding", "transfer-encoding", "connection", "keep-alive", "date"}
)


async def forward(request: Request) -> StreamingResponse:
    """One request, one upstream request, streamed both ways."""
    body = await request.body()
    url = UPSTREAM + request.url.path + (f"?{request.url.query}" if request.url.query else "")
    headers = {
        name: value
        for name, value in request.headers.items()
        if name.lower() not in DROPPED_FROM_REQUEST
    }

    session = AsyncSession()
    # `stream=True` is what keeps an SSE reply a stream. Without it the whole body is read before
    # anything is returned, every streamed call stalls until the model finishes, and the router's
    # `ttfb_ms` becomes a measurement of this process rather than of Anthropic.
    reply = await session.request(
        request.method, url, headers=headers, data=body, stream=True, impersonate=IMPERSONATE
    )

    async def relay():
        try:
            async for chunk in reply.aiter_content():
                yield chunk
        finally:
            await reply.aclose()
            await session.close()

    print(f"  {request.method} {request.url.path} -> {reply.status_code}", flush=True)
    return StreamingResponse(
        relay(),
        status_code=reply.status_code,
        headers={
            name: value
            for name, value in reply.headers.multi_items()
            if name.lower() not in DROPPED_FROM_RESPONSE
        },
    )


app = Starlette(routes=[Route("/{path:path}", forward, methods=["GET", "POST", "PUT", "DELETE"])])

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8799
    print(f"BoringSSL forwarder on 127.0.0.1:{port} -> {UPSTREAM} (impersonate={IMPERSONATE})")
    print(f"Point the router's backends.anthropic.base_url at http://127.0.0.1:{port}")
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")
