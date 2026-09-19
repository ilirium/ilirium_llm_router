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

Run:  PINNED_ANTHROPIC_IP=$(dig +short @1.1.1.1 api.anthropic.com | head -1) .venv/bin/python <this> [args]

Arguments are passed through to the router's own CLI, so `-c config.yaml` works as ever.

***THE PIN DID NOT WORK ON 2026-09-19 AND THIS FILE IS THE FIXED VERSION.*** *It patched
`socket.getaddrinfo` alone. The router runs under **uvloop** -- `uvicorn.run` takes `loop="auto"`,
uvloop is installed, and **uvloop resolves names with its own native resolver that never calls
`socket.getaddrinfo`.** So the patch was inert, the router resolved the name through `/etc/hosts`
to itself, connected to the terminator and rejected its mkcert certificate: `unable to get local
issuer certificate`, sixty-seven 502s, no measurement.* **`uvloop.Loop.getaddrinfo` is patched too,
and `verify_the_pin` refuses to start the router unless the patch is observed doing the work.**
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

    # Every substitution appends here, so the check below can ask whether the patch FIRED rather
    # than only whether the answer looks right. See `verify_the_pin`.
    fired: list[str] = []

    real_getaddrinfo = socket.getaddrinfo

    def pinned(host, port, *args, **kwargs):  # type: ignore[no-untyped-def]
        if host == PINNED_NAME:
            fired.append("socket")
            host = target
        return real_getaddrinfo(host, port, *args, **kwargs)

    socket.getaddrinfo = pinned  # type: ignore[assignment]

    # **uvloop does not call `socket.getaddrinfo` at all** -- it resolves natively, so the patch
    # above is invisible to it. `uvicorn.run(loop="auto")` picks uvloop whenever it is installed,
    # and it is, so on 2026-09-19 the pin was silently inert: the router resolved the name through
    # /etc/hosts to 127.0.0.1, connected to the terminator, and rejected its mkcert certificate
    # with `unable to get local issuer certificate`. Sixty-seven 502s and no measurement.
    #
    # Patching the class rather than forcing `loop="asyncio"` keeps the experiment running on the
    # loop the router really uses; changing that would be a second variable in a phase that has
    # spent a fortnight eliminating them one at a time.
    try:
        import uvloop
    except ImportError:
        pass
    else:
        real_loop_getaddrinfo = uvloop.Loop.getaddrinfo

        async def pinned_loop(self, host, port, **kwargs):  # type: ignore[no-untyped-def]
            if host in (PINNED_NAME, PINNED_NAME.encode()):
                fired.append("uvloop")
                host = target
            return await real_loop_getaddrinfo(self, host, port, **kwargs)

        uvloop.Loop.getaddrinfo = pinned_loop

    if not verify_the_pin(target, fired):
        return 2

    from ilirium_llm_router.cli import main as router_main

    return router_main()


def verify_the_pin(target: str, fired: list[str]) -> bool:
    """Resolve the name the way the router will, and refuse to start unless the patch did it.

    ***This replaced a line that printed `[pinned] ... ` unconditionally*** -- which proved the
    script had run and nothing else, and which was green on the day the pin did not work. The
    runbook told the owner to stop if that line was missing; it was there, and the run still looped.

    **Two facts are checked, not one.** The address has to come back as `target`, *and the patched
    resolver has to have been what returned it* -- because with no hosts entry in place an
    unpatched lookup returns the real address too, and a check that cannot tell those apart is the
    same blindness one level in. **`fired` is the instrument reporting that it ran**, which is the
    thing this phase keeps discovering it never had.
    """
    from uvicorn.config import Config

    loop = Config("unused:app", loop="auto").get_loop_factory()()
    try:
        fired.clear()
        results = loop.run_until_complete(loop.getaddrinfo(PINNED_NAME, 443))
    finally:
        loop.close()

    addresses = {str(entry[4][0]) for entry in results}
    if not fired:
        print(
            f"{sys.argv[0]}: the pin did NOT take. {PINNED_NAME} resolved to "
            f"{', '.join(sorted(addresses))} without the patched resolver being called, so the "
            f"router would resolve it the same way -- through /etc/hosts, to itself. "
            f"Loop: {type(loop).__module__}.{type(loop).__name__}. Not starting.",
            file=sys.stderr,
        )
        return False
    if addresses != {target}:
        print(
            f"{sys.argv[0]}: the pin fired but answered {', '.join(sorted(addresses))} "
            f"rather than {target}. Not starting.",
            file=sys.stderr,
        )
        return False

    print(
        f"[pinned] {PINNED_NAME} -> {target}, verified by resolving it through "
        f"{type(loop).__module__}.{type(loop).__name__} -- patch fired via {'+'.join(fired)}",
        file=sys.stderr,
    )
    return True


if __name__ == "__main__":
    raise SystemExit(main())
