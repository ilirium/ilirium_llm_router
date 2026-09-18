#!/usr/bin/env python3
"""Start the router with `api.anthropic.com` pinned to its real address.

**PHASE 14 EXPERIMENT, 2026-09-18. Not part of the router and not on its import path.**

This exists because of a loop. The experiment points `/etc/hosts` at `127.0.0.1` so that Claude
Code believes it is talking to Anthropic directly -- `NA()` in the client compares
`new URL(e).host` against the literal string `api.anthropic.com`, so nothing short of that name
satisfies it. But `/etc/hosts` is machine-wide, so **the router would resolve the same name to
itself and forward to its own listener, forever.**

Pinning `getaddrinfo` in the router's own process breaks the loop without touching `src/`, without
a second hop, and without a config that disables certificate verification: the connection still
carries SNI `api.anthropic.com` and still validates against Anthropic's real certificate. **Only
the address lookup is overridden, and only inside this process.**

    Claude Code -> api.anthropic.com:443 [hosts -> 127.0.0.1]
                -> tls-terminator.py (sudo, mkcert cert)
                -> the router on 8787        <- this process
                -> 160.79.104.10, SNI api.anthropic.com

**The address is not hardcoded.** It is read from `PINNED_ANTHROPIC_IP`, because an address
baked into a file outlives the day the file was written and this one is a CDN edge.

Run:  PINNED_ANTHROPIC_IP=$(dig +short api.anthropic.com | head -1) .venv/bin/python <this> [args]

Arguments are passed through to the router's own CLI, so `-c config.yaml` works as ever.
"""

from __future__ import annotations

import os
import socket
import sys

PINNED_NAME = "api.anthropic.com"


def main() -> int:
    target = os.environ.get("PINNED_ANTHROPIC_IP", "").strip()
    if not target:
        print(
            f"{sys.argv[0]}: set PINNED_ANTHROPIC_IP to the real address of {PINNED_NAME}.\n"
            "  Take it BEFORE the hosts entry goes in, or from a resolver that ignores it:\n"
            "    dig +short @1.1.1.1 api.anthropic.com | head -1",
            file=sys.stderr,
        )
        return 2
    if target.startswith("127.") or target == "::1":
        # The loop this file exists to prevent, caught rather than entered.
        print(
            f"{sys.argv[0]}: PINNED_ANTHROPIC_IP is {target}, which is loopback. That is the hosts "
            "entry answering, not DNS -- the router would forward to itself. Use a resolver that "
            "ignores /etc/hosts: dig +short @1.1.1.1 api.anthropic.com",
            file=sys.stderr,
        )
        return 2

    real_getaddrinfo = socket.getaddrinfo

    def pinned(host, port, *args, **kwargs):  # type: ignore[no-untyped-def]
        if host == PINNED_NAME:
            host = target
        return real_getaddrinfo(host, port, *args, **kwargs)

    socket.getaddrinfo = pinned  # type: ignore[assignment]
    print(f"[pinned] {PINNED_NAME} -> {target} for this process only", file=sys.stderr)

    from ilirium_llm_router.cli import main as router_main

    return router_main()


if __name__ == "__main__":
    raise SystemExit(main())
