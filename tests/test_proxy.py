"""Phase 1 promises that a request reaches the right backend unaltered and the reply comes back.

The backend here is a stand-in that records what arrived, so these tests check the two things that
are easy to get wrong and expensive when wrong: which address a request went to, and exactly what
bytes and headers it carried when it got there.
"""

from __future__ import annotations

import json
from collections.abc import AsyncIterator, Iterable, Iterator
from contextlib import contextmanager

import httpx
import pytest
from fastapi.testclient import TestClient

from ilirium_llm_router.app import create_app
from ilirium_llm_router.config import Backend, Backends, Config
from ilirium_llm_router.proxy import peek_model

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


class Upstream:
    """A stand-in backend: records the requests that reach it, replies with what it was given."""

    def __init__(
        self, reply: httpx.Response | None = None, error: Exception | None = None
    ) -> None:
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
        assert len(self.requests) == 1, (
            f"expected one request, got {len(self.requests)}"
        )
        return self.requests[0]


def make_config(lmstudio: Backend | None = None) -> Config:
    return Config(
        backends=Backends(
            anthropic=Backend(
                base_url="https://api.anthropic.com", credential="forward"
            ),
            lmstudio=lmstudio
            or Backend(base_url="http://localhost:1234", credential="strip"),
        )
    )


@contextmanager
def running(upstream: Upstream, config: Config | None = None) -> Iterator[TestClient]:
    """The router, with every outgoing request answered by `upstream` instead of the network."""
    client = httpx.AsyncClient(transport=httpx.MockTransport(upstream.handle))
    with TestClient(create_app(config or make_config(), client)) as test_client:
        yield test_client


def test_the_startup_probe_is_answered() -> None:
    """Claude Code sends a bare `HEAD /` before its first real call, from a separate client."""
    upstream = Upstream()
    with running(upstream) as client:
        assert client.head("/").status_code == 200
    assert upstream.requests == []


def test_health_is_answered_locally() -> None:
    upstream = Upstream()
    with running(upstream) as client:
        assert client.get("/health").json() == {"status": "ok"}
    assert upstream.requests == []


def test_a_claude_model_goes_to_anthropic() -> None:
    upstream = Upstream()
    with running(upstream) as client:
        client.post("/v1/messages", content=CLAUDE_BODY, headers=CLAUDE_CODE_HEADERS)

    assert str(upstream.received.url) == "https://api.anthropic.com/v1/messages"


def test_any_other_model_goes_to_lmstudio() -> None:
    upstream = Upstream()
    with running(upstream) as client:
        client.post("/v1/messages", content=LOCAL_BODY, headers=CLAUDE_CODE_HEADERS)

    assert str(upstream.received.url) == "http://localhost:1234/v1/messages"


def test_the_query_string_is_forwarded() -> None:
    """The captured path is `/v1/messages?beta=true`, not a bare path."""
    upstream = Upstream()
    with running(upstream) as client:
        client.post(
            "/v1/messages?beta=true", content=CLAUDE_BODY, headers=CLAUDE_CODE_HEADERS
        )

    assert (
        str(upstream.received.url) == "https://api.anthropic.com/v1/messages?beta=true"
    )


def test_the_body_arrives_byte_for_byte() -> None:
    """Prompt caching matches on the exact bytes of the prefix, so odd spacing must survive too."""
    body = b'{ "messages" : [] ,  "model" : "claude-sonnet-5" }'
    upstream = Upstream()
    with running(upstream) as client:
        client.post("/v1/messages", content=body, headers=CLAUDE_CODE_HEADERS)

    assert upstream.received.content == body


def test_the_credential_is_forwarded_to_anthropic() -> None:
    upstream = Upstream()
    with running(upstream) as client:
        client.post("/v1/messages", content=CLAUDE_BODY, headers=CLAUDE_CODE_HEADERS)

    assert upstream.received.headers["authorization"] == "Bearer sk-ant-oat01-example"


@pytest.mark.parametrize("header", ["authorization", "x-api-key"])
def test_the_credential_is_stripped_for_lmstudio(header: str) -> None:
    """A real Anthropic token is useless locally and should not reach something that might log it."""
    upstream = Upstream()
    with running(upstream) as client:
        client.post(
            "/v1/messages",
            content=LOCAL_BODY,
            headers={**CLAUDE_CODE_HEADERS, header: "secret"},
        )

    assert header not in upstream.received.headers


def test_the_beta_list_reaches_anthropic_verbatim() -> None:
    upstream = Upstream()
    with running(upstream) as client:
        client.post("/v1/messages", content=CLAUDE_BODY, headers=CLAUDE_CODE_HEADERS)

    received = upstream.received
    assert received.headers["anthropic-beta"] == BETA
    assert received.headers["anthropic-version"] == "2023-06-01"
    assert received.headers["x-app"] == "cli"


def test_headers_describing_the_old_connection_are_replaced() -> None:
    upstream = Upstream()
    with running(upstream) as client:
        client.post("/v1/messages", content=CLAUDE_BODY, headers=CLAUDE_CODE_HEADERS)

    received = upstream.received
    assert received.headers["host"] == "api.anthropic.com"
    assert received.headers["content-length"] == str(len(CLAUDE_BODY))


def test_an_uncompressed_reply_is_requested() -> None:
    """Claude Code asks for compression, so identity has to be set deliberately, not just unset."""
    upstream = Upstream()
    with running(upstream) as client:
        client.post("/v1/messages", content=CLAUDE_BODY, headers=CLAUDE_CODE_HEADERS)

    assert upstream.received.headers["accept-encoding"] == "identity"


def test_a_configured_key_replaces_the_incoming_credential(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """LM Studio's "Require Authentication" setting: send its key rather than stripping."""
    monkeypatch.setenv("LMSTUDIO_API_KEY", "local-key")
    config = make_config(
        lmstudio=Backend(
            base_url="http://localhost:1234",
            credential="strip",
            api_key_env="LMSTUDIO_API_KEY",
        )
    )

    upstream = Upstream()
    with running(upstream, config) as client:
        client.post("/v1/messages", content=LOCAL_BODY, headers=CLAUDE_CODE_HEADERS)

    assert upstream.received.headers["authorization"] == "Bearer local-key"


def test_the_backends_own_connection_headers_do_not_come_back() -> None:
    """Our server writes `date` and `server` itself; relaying the backend's leaves two of each."""
    upstream = Upstream(
        streamed(headers={"date": "Wed, 01 Jan 2025 00:00:00 GMT", "server": "Express"})
    )
    with running(upstream) as client:
        reply = client.post(
            "/v1/messages", content=CLAUDE_BODY, headers=CLAUDE_CODE_HEADERS
        )

    assert "server" not in reply.headers
    assert "date" not in reply.headers


def test_a_streamed_reply_is_relayed_as_it_arrives() -> None:
    upstream = Upstream(
        streamed(
            headers={"content-type": "text/event-stream"},
            chunks=[
                b'event: message_start\ndata: {"type":"message_start"}\n\n',
                b'event: content_block_delta\ndata: {"delta":{"text":"hi"}}\n\n',
                b'event: message_stop\ndata: {"type":"message_stop"}\n\n',
            ],
        )
    )
    with running(upstream) as client:
        reply = client.post(
            "/v1/messages", content=CLAUDE_BODY, headers=CLAUDE_CODE_HEADERS
        )

    assert reply.headers["content-type"] == "text/event-stream"
    assert reply.text.count("event: ") == 3
    assert reply.text.endswith('data: {"type":"message_stop"}\n\n')


def test_a_non_streaming_reply_comes_back_whole() -> None:
    upstream = Upstream(streamed(chunks=[b'{"type":"message","content":[]}']))
    with running(upstream) as client:
        reply = client.post(
            "/v1/messages", content=CLAUDE_BODY, headers=CLAUDE_CODE_HEADERS
        )

    assert reply.json() == {"type": "message", "content": []}


def test_a_backend_error_is_passed_through_unchanged() -> None:
    """A real Anthropic error should reach the user intact rather than be replaced by one of ours."""
    rate_limited = json.dumps(
        {"type": "error", "error": {"type": "rate_limit_error", "message": "slow down"}}
    ).encode()
    upstream = Upstream(
        streamed(
            429,
            chunks=[rate_limited],
            headers={"anthropic-ratelimit-requests-remaining": "0"},
        )
    )
    with running(upstream) as client:
        reply = client.post(
            "/v1/messages", content=CLAUDE_BODY, headers=CLAUDE_CODE_HEADERS
        )

    assert reply.status_code == 429
    assert reply.json()["error"]["message"] == "slow down"
    assert reply.headers["anthropic-ratelimit-requests-remaining"] == "0"


def test_a_request_without_a_model_is_rejected() -> None:
    upstream = Upstream()
    with running(upstream) as client:
        reply = client.post(
            "/v1/messages", content=b'{"messages":[]}', headers=CLAUDE_CODE_HEADERS
        )

    assert reply.status_code == 400
    assert reply.json()["error"]["type"] == "invalid_request_error"
    assert upstream.requests == []


def test_an_unreachable_backend_is_reported_as_an_error() -> None:
    """LM Studio not running is the common failure; it must not surface as a crash."""
    upstream = Upstream(error=httpx.ConnectError("Connection refused"))
    with running(upstream) as client:
        reply = client.post(
            "/v1/messages", content=LOCAL_BODY, headers=CLAUDE_CODE_HEADERS
        )

    assert reply.status_code == 502
    assert reply.json()["error"]["type"] == "api_error"
    assert "localhost:1234" in reply.json()["error"]["message"]


def test_an_unanticipated_path_is_forwarded_rather_than_refused() -> None:
    upstream = Upstream()
    with running(upstream) as client:
        client.get("/v1/models?limit=5", headers=CLAUDE_CODE_HEADERS)

    received = upstream.received
    assert received.method == "GET"
    assert str(received.url) == "https://api.anthropic.com/v1/models?limit=5"


def test_an_unanticipated_path_still_routes_on_the_model_when_there_is_one() -> None:
    upstream = Upstream()
    with running(upstream) as client:
        client.post(
            "/v1/messages/count_tokens", content=LOCAL_BODY, headers=CLAUDE_CODE_HEADERS
        )

    assert (
        str(upstream.received.url) == "http://localhost:1234/v1/messages/count_tokens"
    )


@pytest.mark.parametrize(
    "body",
    [
        b"",
        b"not json",
        b"[]",
        b'{"messages":[]}',
        b'{"model":null}',
        b'{"model":""}',
    ],
)
def test_peek_model_returns_nothing_when_there_is_no_usable_model(body: bytes) -> None:
    assert peek_model(body) is None


def test_peek_model_finds_the_model() -> None:
    assert peek_model(CLAUDE_BODY) == "claude-sonnet-5"
