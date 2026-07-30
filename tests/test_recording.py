"""What the router writes down about a call it forwarded.

`test_proxy.py` covers the forwarding; this covers the row it produces. The two tests worth reading
first are `test_watching_a_reply_does_not_change_a_byte_of_it`, which is the promise everything else
here is allowed to exist on top of, and `test_a_writer_that_raises_does_not_break_the_call`, which is
the rule that outranks every column in the file.
"""

from __future__ import annotations

import asyncio
import json

import httpx
import pytest
from conftest import (
    CLAUDE_BODY,
    CLAUDE_CODE_HEADERS,
    LOCAL_BODY,
    Rows,
    Upstream,
    make_config,
    running,
    streamed,
)
from starlette.requests import Request

from ilirium_llm_router.observe import Call
from ilirium_llm_router.proxy import Proxy

SSE_HEADERS = {"content-type": "text/event-stream"}
JSON_HEADERS = {"content-type": "application/json"}


def arriving_request(headers: list[tuple[bytes, bytes]] | None = None) -> Request:
    """The bare ASGI scope a `Call` needs: a path, a query string and headers."""
    return Request(
        {
            "type": "http",
            "http_version": "1.1",
            "method": "POST",
            "scheme": "http",
            "path": "/v1/messages",
            "raw_path": b"/v1/messages",
            "query_string": b"beta=true",
            "root_path": "",
            "headers": headers or [],
            "client": ("127.0.0.1", 54321),
            "server": ("127.0.0.1", 8787),
        }
    )


def sse_reply(status: int = 200) -> httpx.Response:
    """A streamed reply carrying usage the way both backends do."""
    return streamed(
        status,
        headers=SSE_HEADERS,
        chunks=[
            (
                b'event: message_start\ndata: {"type":"message_start","message":{"usage":'
                b'{"input_tokens":15,"cache_read_input_tokens":5}}}\n\n'
            ),
            (
                b'event: content_block_delta\ndata: {"type":"content_block_delta",'
                b'"delta":{"text":"hi"}}\n\n'
            ),
            (
                b'event: message_delta\ndata: {"type":"message_delta","delta":'
                b'{"stop_reason":"end_turn"},"usage":{"output_tokens":29}}\n\n'
            ),
            b'event: message_stop\ndata: {"type":"message_stop"}\n\n',
        ],
    )


def test_watching_a_reply_does_not_change_a_byte_of_it() -> None:
    """The tee is passive. Whatever the scanner does, the caller gets what the backend sent."""
    chunks = [b'{"a":1}', b"\xff\xfe binary-ish", b"", b"tail"]
    upstream = Upstream(streamed(chunks=chunks, headers=JSON_HEADERS))

    with running(upstream) as client:
        reply = client.post(
            "/v1/messages", content=CLAUDE_BODY, headers=CLAUDE_CODE_HEADERS
        )

    assert reply.content == b"".join(chunks)


def test_a_streamed_call_records_its_usage_and_stop_reason() -> None:
    rows = Rows()
    with running(Upstream(sse_reply()), rows=rows) as client:
        client.post(
            "/v1/messages",
            content=b'{"model":"claude-sonnet-5","stream":true}',
            headers=CLAUDE_CODE_HEADERS,
        )

    row = rows.one
    assert row.backend == "anthropic"
    assert row.model == "claude-sonnet-5"
    assert row.path == "/v1/messages"
    assert row.stream is True
    assert (row.input_tokens, row.output_tokens) == (15, 29)
    assert row.cache_read_input_tokens == 5
    assert row.cache_creation_input_tokens is None
    assert row.stop_reason == "end_turn"
    assert row.error_status == "ok"
    assert (row.error_code, row.error_message) == ("", "")


def test_a_non_streaming_call_records_from_the_top_level() -> None:
    body = json.dumps(
        {"stop_reason": "end_turn", "usage": {"input_tokens": 20, "output_tokens": 39}}
    ).encode()
    rows = Rows()
    with running(Upstream(streamed(chunks=[body], headers=JSON_HEADERS)), rows=rows) as client:
        client.post(
            "/v1/messages",
            content=b'{"model":"qwen3-coder-30b","stream":false}',
            headers=CLAUDE_CODE_HEADERS,
        )

    row = rows.one
    assert row.backend == "lmstudio"
    assert row.stream is False
    assert (row.input_tokens, row.output_tokens) == (20, 39)
    assert row.stop_reason == "end_turn"


def test_the_identifiers_are_copied_off_the_headers() -> None:
    rows = Rows()
    with running(Upstream(sse_reply()), rows=rows) as client:
        client.post(
            "/v1/messages",
            content=CLAUDE_BODY,
            headers={
                **CLAUDE_CODE_HEADERS,
                "x-claude-code-session-id": "sess-abc",
                "x-claude-code-agent-id": "agent-xyz",
            },
        )

    assert rows.one.session_id == "sess-abc"
    assert rows.one.agent_id == "agent-xyz"


def test_a_missing_agent_id_is_empty_rather_than_absent() -> None:
    """Empty `agent_id` is the signal for the main conversation, not a gap in the data."""
    rows = Rows()
    with running(Upstream(sse_reply()), rows=rows) as client:
        client.post("/v1/messages", content=CLAUDE_BODY, headers=CLAUDE_CODE_HEADERS)

    assert rows.one.agent_id == ""
    assert rows.one.session_id == ""


def test_the_byte_counts_are_recorded() -> None:
    chunks = [b"hello ", b"world"]
    rows = Rows()
    with running(Upstream(streamed(chunks=chunks, headers=JSON_HEADERS)), rows=rows) as client:
        client.post("/v1/messages", content=CLAUDE_BODY, headers=CLAUDE_CODE_HEADERS)

    assert rows.one.request_bytes == len(CLAUDE_BODY)
    assert rows.one.response_bytes == len(b"".join(chunks))


def test_both_clocks_run_and_the_first_byte_comes_before_the_last() -> None:
    rows = Rows()
    with running(Upstream(sse_reply()), rows=rows) as client:
        client.post("/v1/messages", content=CLAUDE_BODY, headers=CLAUDE_CODE_HEADERS)

    row = rows.one
    assert row.ttfb_ms is not None
    assert 0 <= row.ttfb_ms <= row.duration_ms


def test_an_http_error_records_the_status_and_the_backends_wording() -> None:
    rate_limited = json.dumps(
        {"type": "error", "error": {"type": "rate_limit_error", "message": "slow down"}}
    ).encode()
    rows = Rows()
    upstream = Upstream(streamed(429, chunks=[rate_limited], headers=JSON_HEADERS))
    with running(upstream, rows=rows) as client:
        client.post("/v1/messages", content=CLAUDE_BODY, headers=CLAUDE_CODE_HEADERS)

    row = rows.one
    assert row.error_status == "http_error"
    assert row.error_code == "429"
    assert row.error_message == "slow down"


def test_an_error_event_mid_stream_is_recorded_despite_the_200() -> None:
    """The status line said 200 before any content existed. Only the tee can see this."""
    rows = Rows()
    upstream = Upstream(
        streamed(
            200,
            headers=SSE_HEADERS,
            chunks=[
                (
                    b'event: message_start\ndata: {"type":"message_start","message":'
                    b'{"usage":{"input_tokens":15}}}\n\n'
                ),
                (
                    b'event: error\ndata: {"type":"error","error":'
                    b'{"type":"overloaded_error","message":"Overloaded"}}\n\n'
                ),
            ],
        )
    )
    with running(upstream, rows=rows) as client:
        reply = client.post(
            "/v1/messages", content=CLAUDE_BODY, headers=CLAUDE_CODE_HEADERS
        )

    assert reply.status_code == 200, "the failure never reached the status line"
    row = rows.one
    assert row.error_status == "stream_error"
    assert row.error_code == "overloaded_error"
    assert row.error_message == "Overloaded"
    assert row.input_tokens == 15, "what arrived before the error is still worth having"


def test_an_unreachable_backend_records_a_transport_error() -> None:
    """LM Studio not running is the common failure, and it never gets an HTTP status at all."""
    rows = Rows()
    upstream = Upstream(error=httpx.ConnectError("Connection refused"))
    with running(upstream, rows=rows) as client:
        client.post("/v1/messages", content=LOCAL_BODY, headers=CLAUDE_CODE_HEADERS)

    row = rows.one
    assert row.error_status == "transport_error"
    assert row.error_code == "connect_error"
    assert "Connection refused" in row.error_message
    assert row.backend == "lmstudio"
    assert row.response_bytes == 0
    assert row.ttfb_ms is None, "nothing ever came back, so there was no first byte"


@pytest.mark.parametrize(
    ("error", "expected"),
    [
        (httpx.ConnectError("refused"), "connect_error"),
        (httpx.ConnectTimeout("timed out"), "connect_timeout"),
        (httpx.ReadTimeout("timed out"), "read_timeout"),
        (httpx.RemoteProtocolError("bad frame"), "remote_protocol_error"),
        (httpx.PoolTimeout("no connection"), "pool_timeout"),
    ],
)
def test_transport_error_codes_come_from_the_exception_class(
    error: Exception, expected: str
) -> None:
    """Derived rather than tabulated, so an httpx error nobody listed still reads as something."""
    rows = Rows()
    with running(Upstream(error=error), rows=rows) as client:
        client.post("/v1/messages", content=LOCAL_BODY, headers=CLAUDE_CODE_HEADERS)

    assert rows.one.error_code == expected


def test_a_request_without_a_model_still_gets_a_row() -> None:
    """It never reached a backend, but a silent gap is worse than a row with blanks."""
    rows = Rows()
    with running(Upstream(), rows=rows) as client:
        client.post(
            "/v1/messages", content=b'{"messages":[]}', headers=CLAUDE_CODE_HEADERS
        )

    row = rows.one
    assert row.backend == ""
    assert row.model == ""
    assert row.error_status == "http_error"
    assert row.error_code == "400"


def test_an_unanticipated_path_records_which_one_it_was() -> None:
    """The whole point of the column: the catch-all's traffic is otherwise indistinguishable."""
    rows = Rows()
    with running(Upstream(), rows=rows) as client:
        client.get("/v1/models?limit=5", headers=CLAUDE_CODE_HEADERS)

    row = rows.one
    assert row.path == "/v1/models", "the query string does not belong in the column"
    assert row.backend == "anthropic"
    assert row.model == ""


def test_one_row_per_call_and_no_row_for_a_local_answer() -> None:
    """`HEAD /` and `/health` are answered here and never forwarded, so they are not calls."""
    rows = Rows()
    with running(Upstream(sse_reply()), rows=rows) as client:
        client.head("/")
        client.get("/health")

    assert rows.written == []


def test_a_client_that_goes_away_mid_stream_is_recorded() -> None:
    """Neither a success nor a backend failure — the case the old `is_error` boolean could not say.

    Driven against the generator directly, because a `TestClient` request always reads its reply to
    the end: there is no way through it to be the caller that stops listening. `aclose()` throws
    `GeneratorExit` in at the yield, which is what starlette does when the connection drops.
    """

    async def scenario() -> Rows:
        rows = Rows()
        proxy = Proxy(make_config(), httpx.AsyncClient(), {}, rows)  # type: ignore[arg-type]
        call = Call(arriving_request())
        chunks = proxy.watch(sse_reply(), call)

        await chunks.__anext__()  # the caller reads one chunk...
        await chunks.aclose()  # ...and then goes away

        return rows

    rows = asyncio.run(scenario())

    row = rows.one
    assert row.error_status == "client_disconnect"
    assert row.error_code == "client_disconnect"
    assert row.response_bytes > 0, "the part that was delivered still counts"
    assert row.input_tokens == 15, "and what the scanner saw before that is still worth keeping"


def test_a_writer_that_raises_does_not_break_the_call() -> None:
    """The rule that outranks every column: telemetry never breaks a call."""

    class Broken(Rows):
        def write(self, record: object) -> None:
            raise OSError("No space left on device")

    upstream = Upstream(sse_reply())
    with running(upstream, rows=Broken()) as client:
        reply = client.post(
            "/v1/messages", content=CLAUDE_BODY, headers=CLAUDE_CODE_HEADERS
        )

    assert reply.status_code == 200
    assert b"message_stop" in reply.content
