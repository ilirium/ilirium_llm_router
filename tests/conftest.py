"""The stand-in backend and the router wired to it, shared by the tests that go through the app.

Kept here rather than in one test file so that `test_proxy.py` (what the router forwards) and
`test_recording.py` (what it writes down about the forwarding) can describe the same call from
their two different angles without either owning the scaffolding.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterable, Iterator
from contextlib import contextmanager

import httpx
from fastapi.testclient import TestClient

from ilirium_llm_router.app import create_app
from ilirium_llm_router.config import Backend, Backends, Config
from ilirium_llm_router.stats import CallRecord

CLAUDE_BODY = b'{"model":"claude-sonnet-5","messages":[{"role":"user","content":"hi"}]}'
LOCAL_BODY = b'{"model":"qwen3-coder-30b","messages":[{"role":"user","content":"hi"}]}'

# What Claude Code actually sends, shortened. The beta list matters: `oauth-2025-04-20` is what
# makes the bearer token acceptable to Anthropic, so it has to arrive whole.
BETA = "claude-code-20250219,oauth-2025-04-20,context-management-2025-06-27"
CLAUDE_CODE_HEADERS = {
    "authorization": "Bearer sk-ant-oat01-example",
    "content-type": "application/json",
    "anthropic-beta": BETA,
    "anthropic-version": "2023-06-01",
    "accept-encoding": "gzip, deflate, br, zstd",
    "user-agent": "claude-cli/2.1.212 (external, sdk-cli)",
    "x-app": "cli",
}


def streamed(
    status: int = 200,
    *,
    chunks: Iterable[bytes] = (b'{"ok":true}',),
    headers: dict[str, str] | None = None,
) -> httpx.Response:
    """A reply that arrives as a stream, the way a real backend's does.

    Worth spelling out rather than using `httpx.Response(content=b"...")`: that form is already
    fully read, and the router — rightly — will not stream a response a second time.
    """

    async def body() -> AsyncIterator[bytes]:
        for chunk in chunks:
            yield chunk

    return httpx.Response(status, headers=headers, content=body())


def dies_after(chunk: bytes) -> AsyncIterator[bytes]:
    """A reply that delivers `chunk` and then has its connection reset under it.

    The backend-died-mid-answer case, which both test files need: `test_proxy.py` to check what the
    caller is told, `test_recording.py` to check what the row says. It was defined four times with
    identical bodies before Phase 6 noticed.
    """

    async def body() -> AsyncIterator[bytes]:
        yield chunk
        raise httpx.ReadError("Connection reset by peer")

    return body()


class Upstream:
    """A stand-in backend: records the requests that reach it, replies with what it was given."""

    def __init__(self, reply: httpx.Response | None = None, error: Exception | None = None) -> None:
        self.reply = reply
        self.error = error
        self.requests: list[httpx.Request] = []

    def handle(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        if self.error is not None:
            raise self.error
        return self.reply if self.reply is not None else streamed()

    @property
    def received(self) -> httpx.Request:
        """The one request that arrived, asserting there was exactly one."""
        assert len(self.requests) == 1, f"expected one request, got {len(self.requests)}"
        return self.requests[0]


class Rows:
    """Stands in for the CSV file, keeping the rows the router wrote so a test can read them back.

    A stand-in rather than a real `StatsWriter` at a temporary path: these tests are about what the
    router *decided* to record, and `test_stats.py` already covers how a row reaches disk.
    """

    def __init__(self) -> None:
        self.written: list[CallRecord] = []

    def write(self, record: CallRecord) -> None:
        self.written.append(record)

    def close(self) -> None:
        pass

    @property
    def one(self) -> CallRecord:
        """The single row for the single call, asserting there was exactly one."""
        assert len(self.written) == 1, f"expected one row, got {len(self.written)}"
        return self.written[0]


def make_config(lmstudio: Backend | None = None) -> Config:
    return Config(
        backends=Backends(
            anthropic=Backend(base_url="https://api.anthropic.com", credential="forward"),
            lmstudio=lmstudio or Backend(base_url="http://localhost:1234", credential="strip"),
        )
    )


@contextmanager
def running(
    upstream: Upstream, config: Config | None = None, rows: Rows | None = None
) -> Iterator[TestClient]:
    """The router, with every outgoing request answered by `upstream` instead of the network."""
    client = httpx.AsyncClient(transport=httpx.MockTransport(upstream.handle))
    app = create_app(config or make_config(), client, rows or Rows())  # type: ignore[arg-type]
    with TestClient(app) as test_client:
        yield test_client
