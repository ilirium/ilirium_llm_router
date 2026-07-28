"""The FastAPI application.

Phase 0: the app starts and reports that it is alive. Request forwarding arrives in Phase 1, in
`proxy.py`.
"""

from __future__ import annotations

from fastapi import FastAPI

from .config import Config


def create_app(config: Config) -> FastAPI:
    app = FastAPI(title="ilirium_llm_router")
    app.state.config = config

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app
