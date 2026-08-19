"""The FastAPI application.

Four routes: the `HEAD /` probe Claude Code sends before its first real call, a health check,
`POST /v1/messages` where the model name in the body decides the backend, and a catch-all so a path
we did not anticipate is forwarded rather than refused.

The catch-all is registered last on purpose — the first matching route wins, so it must not shadow
the three above it.

Two exception handlers sit under all four. Every failure a client can see should arrive in the
shape it expects, and the shape Claude Code expects is Anthropic's error object — a bare framework
500, in plain text, tells the person at the keyboard nothing about what went wrong.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import AsyncExitStack, asynccontextmanager

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import Response
from starlette.requests import ClientDisconnect

from .config import Config
from .corpus import CorpusWriter
from .proxy import Proxy, create_client, error_response
from .stats import StatsWriter

CATCH_ALL_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]


def create_app(
    config: Config,
    client: httpx.AsyncClient | None = None,
    stats: StatsWriter | None = None,
    corpus: CorpusWriter | None = None,
) -> FastAPI:
    """Build the app.

    `client`, `stats` and `corpus` exist for tests, which pass a client wired to a stand-in backend
    and writers pointed at temporary paths, and close them themselves. In normal use the app owns
    them and closes them on shutdown.
    """

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        async with AsyncExitStack() as stack:
            http = client or await stack.enter_async_context(create_client())
            writer = stats
            if writer is None:
                writer = StatsWriter(config.stats)
                stack.callback(writer.close)
            # The store is opt-in, so a disabled corpus is not merely an unused object: it is no
            # object at all, no worker thread, and nothing created under `corpus.dir`.
            store = corpus
            if store is None and config.corpus.enabled:
                store = CorpusWriter(
                    directory=config.corpus.dir,
                    compress_level=config.corpus.compress_level_zstd,
                    body_max_bytes=config.corpus.body_max_bytes,
                    queue_max_bytes=config.corpus.queue_max_bytes,
                )
                # Registered on the stack so the drain happens on the way out of lifespan, before
                # the process exits and takes the daemon thread with it.
                stack.callback(store.close)
            app.state.proxy = Proxy(config, http, config.api_keys(), writer, store)
            yield

    app = FastAPI(title="ilirium_llm_router", lifespan=lifespan)

    @app.exception_handler(ClientDisconnect)
    async def gone(request: Request, exc: ClientDisconnect) -> Response:
        """The caller left while its request body was still arriving.

        `proxy.begin` has already written the row; this only keeps the exception from surfacing as
        an unhandled server error. Nothing here reaches anyone — there is no longer a connection to
        answer on — so the status is chosen for the log rather than for a reader: 499 is nginx's
        code for exactly this, and reads better in a log than a 500 nobody caused.
        """
        return error_response(
            499,
            "invalid_request_error",
            "The caller went away before its request had arrived.",
        )

    @app.exception_handler(Exception)
    async def unexpected(request: Request, exc: Exception) -> Response:
        """Anything nobody anticipated.

        Starlette re-raises after this returns, so uvicorn still logs the traceback — into the
        router's own rotating log, which is where the two are already merged. The handler's job is
        only the half the traceback cannot do: give the caller an error it can display.
        """
        return error_response(
            500,
            "api_error",
            f"The router failed to handle this request: {type(exc).__name__}: {exc}",
        )

    @app.head("/")
    async def probe() -> Response:
        """Claude Code checks the address is alive before using it. Unanswered, we look dead."""
        return Response(status_code=200)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/v1/messages")
    async def messages(request: Request) -> Response:
        return await request.app.state.proxy.messages(request)

    @app.api_route("/{path:path}", methods=CATCH_ALL_METHODS)
    async def anything_else(request: Request) -> Response:
        return await request.app.state.proxy.anything_else(request)

    return app
