"""The FastAPI application.

Four routes: the `HEAD /` probe Claude Code sends before its first real call, a health check,
`POST /v1/messages` where the model name in the body decides the backend, and a catch-all so a path
we did not anticipate is forwarded rather than refused.

The catch-all is registered last on purpose — the first matching route wins, so it must not shadow
the three above it.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import AsyncExitStack, asynccontextmanager

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import Response

from .config import Config
from .proxy import Proxy, create_client
from .stats import StatsWriter

CATCH_ALL_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]


def create_app(
    config: Config,
    client: httpx.AsyncClient | None = None,
    stats: StatsWriter | None = None,
) -> FastAPI:
    """Build the app.

    `client` and `stats` exist for tests, which pass a client wired to a stand-in backend and a
    writer pointed at a temporary path, and close both themselves. In normal use the app owns them
    and closes them on shutdown.
    """

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        async with AsyncExitStack() as stack:
            http = client or await stack.enter_async_context(create_client())
            writer = stats
            if writer is None:
                writer = StatsWriter(config.stats)
                stack.callback(writer.close)
            app.state.proxy = Proxy(config, http, config.api_keys(), writer)
            yield

    app = FastAPI(title="ilirium_llm_router", lifespan=lifespan)
    app.state.config = config

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
