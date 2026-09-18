#!/usr/bin/env python3
"""Terminate TLS on 443 as `api.anthropic.com` and hand the plaintext to the router.

**PHASE 14 EXPERIMENT, 2026-09-18. Not part of the router and not on its import path.**

The client decides it is first-party by comparing `new URL(base).host` against the literal string
`api.anthropic.com`, and with `ANTHROPIC_BASE_URL` unset that name is reached on **443 over TLS**.
The router speaks plain HTTP and its `Server` config has no certificate keys, so something has to
stand in front. This is that thing, and it is deliberately the dumbest possible version:

    Claude Code -> api.anthropic.com:443 [hosts -> 127.0.0.1]
                -> this, with an mkcert certificate          <- sudo, because 443 is privileged
                -> http://127.0.0.1:8787, the router unchanged
                -> run-pinned.py breaks the resolution loop on the way out

**Why this rather than patching the binary.** `CE()` reads `process.env.ANTHROPIC_BASE_URL`
directly, so leaving it unset is what makes the client first-party -- and a hosts entry does that
with nothing modified. The alternative was editing a 200 MB code-signed Bun executable whose
bundle is marked `@bun @bytecode`, where a compiled copy of the patched source may exist alongside
the text and the edit may simply not take.

**It reads nothing and changes nothing.** Headers pass through untouched apart from the connection
framing this hop necessarily re-derives; the credential travels the same localhost hop it already
travels to reach the router.

**Streaming is the one thing that must not be got wrong.** `stream=True` and a chunk-by-chunk
relay: buffering would stall every streamed call until the model finished and turn the router's
`ttfb_ms` into a measurement of this process. The BoringSSL forwarder beside this file records
that hazard and this file inherits it.

Run:  sudo .venv/bin/python <this> --cert <fullchain.pem> --key <key.pem> [--to 127.0.0.1:8787]
"""

from __future__ import annotations

import argparse
import sys

import httpx
import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import StreamingResponse
from starlette.routing import Route

# Ours to set, not the caller's to carry across a new connection.
DROPPED_FROM_REQUEST = frozenset({"host", "content-length", "connection", "keep-alive",
                                  "transfer-encoding"})
# The body is re-framed on the way out, so anything describing the old framing goes with it.
DROPPED_FROM_RESPONSE = frozenset({"content-length", "content-encoding", "transfer-encoding",
                                   "connection", "keep-alive", "date"})

TARGET = "http://127.0.0.1:8787"


async def forward(request: Request) -> StreamingResponse:
    body = await request.body()
    url = TARGET + request.url.path + (f"?{request.url.query}" if request.url.query else "")
    headers = {n: v for n, v in request.headers.items() if n.lower() not in DROPPED_FROM_REQUEST}
    # `host` is re-set rather than dropped: the router logs it, and a hop that silently rewrote it
    # would be a second variable in an experiment that exists to remove one.
    headers["host"] = "api.anthropic.com"

    client = httpx.AsyncClient(timeout=None)
    req = client.build_request(request.method, url, headers=headers, content=body)
    reply = await client.send(req, stream=True)

    async def relay():
        try:
            async for chunk in reply.aiter_raw():
                yield chunk
        finally:
            await reply.aclose()
            await client.aclose()

    print(f"  {request.method} {request.url.path} -> {reply.status_code}", flush=True)
    return StreamingResponse(
        relay(),
        status_code=reply.status_code,
        headers={n: v for n, v in reply.headers.multi_items()
                 if n.lower() not in DROPPED_FROM_RESPONSE},
    )


app = Starlette(routes=[Route("/{path:path}", forward,
                             methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD"])])


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--cert", required=True, help="mkcert certificate for api.anthropic.com")
    p.add_argument("--key", required=True, help="its private key")
    p.add_argument("--port", type=int, default=443, help="listen port (default 443)")
    p.add_argument("--to", default="127.0.0.1:8787", help="the router (default 127.0.0.1:8787)")
    args = p.parse_args()
    TARGET = f"http://{args.to}"
    print(f"TLS terminator on 127.0.0.1:{args.port} -> {TARGET}", file=sys.stderr)
    uvicorn.run(app, host="127.0.0.1", port=args.port, log_level="warning",
                ssl_certfile=args.cert, ssl_keyfile=args.key)
