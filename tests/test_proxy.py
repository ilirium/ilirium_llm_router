"""Phase 1 promises that a request reaches the right backend unaltered and the reply comes back.

The backend here is a stand-in that records what arrived, so these tests check the two things that
are easy to get wrong and expensive when wrong: which address a request went to, and exactly what
bytes and headers it carried when it got there.
"""

from __future__ import annotations

import json
import logging
import uuid

import httpx
import pytest
from conftest import (
    BETA,
    CLAUDE_BODY,
    CLAUDE_CODE_HEADERS,
    LOCAL_BODY,
    Rows,
    Upstream,
    dies_after,
    make_config,
    running,
    streamed,
)
from fastapi.testclient import TestClient

from ilirium_llm_router.app import create_app
from ilirium_llm_router.config import Backend, Config
from ilirium_llm_router.proxy import create_client, imitation_headers, peek


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
        client.post("/v1/messages?beta=true", content=CLAUDE_BODY, headers=CLAUDE_CODE_HEADERS)

    assert str(upstream.received.url) == "https://api.anthropic.com/v1/messages?beta=true"


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


def test_a_streamed_request_asks_for_an_uncompressed_reply() -> None:
    """Claude Code asks for compression, so identity has to be set deliberately, not just unset.

    The SSE scanner reads raw bytes off the wire, so this half is not negotiable.
    """
    upstream = Upstream()
    body = b'{"model":"claude-sonnet-5","stream":true,"messages":[]}'
    with running(upstream) as client:
        client.post("/v1/messages", content=body, headers=CLAUDE_CODE_HEADERS)

    assert upstream.received.headers["accept-encoding"] == "identity"


def test_a_non_streamed_request_forces_identity_by_default() -> None:
    """***The shipped behaviour, and the one this test exists to pin.***

    The experiment below was live from 2026-09-18 and is **off by default since 2026-09-19**: it
    came back negative for the 429, and the run that settled that showed the classifier still
    failing afterwards with this the only change altering what a non-streamed reply looks like.
    A test that does not mention an experiment tests the router as it ships.
    """
    upstream = Upstream()
    with running(upstream) as client:
        client.post("/v1/messages", content=CLAUDE_BODY, headers=CLAUDE_CODE_HEADERS)

    assert upstream.received.headers["accept-encoding"] == "identity"


def test_a_non_streamed_request_relays_the_callers_own_accept_encoding() -> None:
    """Phase 14 experiment, **on only when asked for**: `relay_accept_encoding`.

    The classifier works direct and 429s through the router, on the same credential and client.
    This was the first variable flipped -- see the block comment in `outgoing_headers`.
    """
    upstream = Upstream()
    with running(upstream, make_config(relay_accept_encoding=True)) as client:
        client.post("/v1/messages", content=CLAUDE_BODY, headers=CLAUDE_CODE_HEADERS)

    assert upstream.received.headers["accept-encoding"] == "gzip, deflate, br, zstd"


def test_the_experiment_never_touches_a_streamed_request() -> None:
    """Even switched on, a streamed reply still gets `identity` -- the SSE scanner reads raw bytes.

    The half that was never in question, asserted so that turning the experiment on cannot quietly
    take the scanner with it.
    """
    upstream = Upstream()
    streaming = b'{"model":"claude-sonnet-5","stream":true,"messages":[]}'
    with running(upstream, make_config(relay_accept_encoding=True)) as client:
        client.post("/v1/messages", content=streaming, headers=CLAUDE_CODE_HEADERS)

    assert upstream.received.headers["accept-encoding"] == "identity"


def test_httpx_supplies_its_own_accept_encoding_when_the_caller_sends_none() -> None:
    """Relaying "absent" is NOT available, and this test exists to say so rather than to approve it.

    httpx fills in its own `accept-encoding` when the header is missing, so the router cannot pass
    a caller's *absence* through the way it passes a value through. It does not matter for the
    experiment -- Claude Code always sends one -- but it is a real floor on how transparent this
    header can be, and finding it in a debugging session later would cost more than the line.

    **Only reachable with the experiment on.** Off, the router appends `identity` itself and httpx
    never gets the chance -- which is the same fact from the other side and is why that append
    exists rather than a discard.
    """
    upstream = Upstream()
    headers = {k: v for k, v in CLAUDE_CODE_HEADERS.items() if k != "accept-encoding"}
    with running(upstream, make_config(relay_accept_encoding=True)) as client:
        client.post("/v1/messages", content=CLAUDE_BODY, headers=headers)

    supplied = upstream.received.headers["accept-encoding"]
    assert supplied and supplied != "identity"


def _injecting_config() -> Config:
    return make_config(
        lmstudio=Backend(
            base_url="http://localhost:1234",
            credential="inject",
            api_key_env="LMSTUDIO_API_KEY",
        )
    )


def test_a_configured_key_replaces_the_incoming_credential(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """LM Studio's "Require Authentication" setting: send its key rather than stripping."""
    monkeypatch.setenv("LMSTUDIO_API_KEY", "local-key")

    upstream = Upstream()
    with running(upstream, _injecting_config()) as client:
        client.post("/v1/messages", content=LOCAL_BODY, headers=CLAUDE_CODE_HEADERS)

    assert upstream.received.headers["authorization"] == "Bearer local-key"


def test_inject_removes_the_incoming_key_header_as_well(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`inject` is `strip` plus a key, so the caller's own `x-api-key` must not survive either."""
    monkeypatch.setenv("LMSTUDIO_API_KEY", "local-key")

    upstream = Upstream()
    with running(upstream, _injecting_config()) as client:
        client.post(
            "/v1/messages",
            content=LOCAL_BODY,
            headers={**CLAUDE_CODE_HEADERS, "x-api-key": "secret"},
        )

    received = upstream.received
    assert "x-api-key" not in received.headers
    assert received.headers["authorization"] == "Bearer local-key"


def _patient_lmstudio() -> Config:
    return make_config(
        lmstudio=Backend(
            base_url="http://localhost:1234",
            credential="strip",
            read_timeout=1800,
        )
    )


def test_each_backend_carries_its_own_tolerance_for_silence() -> None:
    """Phase 4 killed a healthy local prefill at a shared 600 s. The number is now per backend."""
    config = _patient_lmstudio()

    local = Upstream()
    with running(local, config) as client:
        client.post("/v1/messages", content=LOCAL_BODY, headers=CLAUDE_CODE_HEADERS)

    cloud = Upstream()
    with running(cloud, config) as client:
        client.post("/v1/messages", content=CLAUDE_BODY, headers=CLAUDE_CODE_HEADERS)

    assert local.received.extensions["timeout"]["read"] == 1800
    assert cloud.received.extensions["timeout"]["read"] == 600


def test_a_patient_backend_is_still_reached_impatiently() -> None:
    """Waiting 30 minutes for a model to think must not mean waiting 30 minutes to find it absent.

    LM Studio simply not running is the common failure, and it is a connect error, not silence.
    """
    upstream = Upstream()
    with running(upstream, _patient_lmstudio()) as client:
        client.post("/v1/messages", content=LOCAL_BODY, headers=CLAUDE_CODE_HEADERS)

    timeout = upstream.received.extensions["timeout"]
    assert timeout["connect"] == 5.0
    assert timeout["write"] == 30.0


def test_the_backends_own_connection_headers_do_not_come_back() -> None:
    """Our server writes `date` and `server` itself; relaying the backend's leaves two of each."""
    upstream = Upstream(
        streamed(headers={"date": "Wed, 01 Jan 2025 00:00:00 GMT", "server": "Express"})
    )
    with running(upstream) as client:
        reply = client.post("/v1/messages", content=CLAUDE_BODY, headers=CLAUDE_CODE_HEADERS)

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
        reply = client.post("/v1/messages", content=CLAUDE_BODY, headers=CLAUDE_CODE_HEADERS)

    assert reply.headers["content-type"] == "text/event-stream"
    assert reply.text.count("event: ") == 3
    assert reply.text.endswith('data: {"type":"message_stop"}\n\n')


def test_a_non_streaming_reply_comes_back_whole() -> None:
    upstream = Upstream(streamed(chunks=[b'{"type":"message","content":[]}']))
    with running(upstream) as client:
        reply = client.post("/v1/messages", content=CLAUDE_BODY, headers=CLAUDE_CODE_HEADERS)

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
        reply = client.post("/v1/messages", content=CLAUDE_BODY, headers=CLAUDE_CODE_HEADERS)

    assert reply.status_code == 429
    assert reply.json()["error"]["message"] == "slow down"
    assert reply.headers["anthropic-ratelimit-requests-remaining"] == "0"


def test_a_request_without_a_model_is_rejected() -> None:
    upstream = Upstream()
    with running(upstream) as client:
        reply = client.post("/v1/messages", content=b'{"messages":[]}', headers=CLAUDE_CODE_HEADERS)

    assert reply.status_code == 400
    assert reply.json()["error"]["type"] == "invalid_request_error"
    assert upstream.requests == []


def test_an_unreachable_backend_is_reported_as_an_error() -> None:
    """LM Studio not running is the common failure; it must not surface as a crash."""
    upstream = Upstream(error=httpx.ConnectError("Connection refused"))
    with running(upstream) as client:
        reply = client.post("/v1/messages", content=LOCAL_BODY, headers=CLAUDE_CODE_HEADERS)

    assert reply.status_code == 502
    assert reply.json()["error"]["type"] == "api_error"
    assert "localhost:1234" in reply.json()["error"]["message"]


def test_a_stream_that_breaks_ends_with_an_error_event() -> None:
    """The one place the router adds bytes of its own, and why it is worth the exception.

    A 200 has already gone out, so the failure cannot go in the status line. Without the event the
    caller sees a stream that simply ends — indistinguishable from a model that finished talking.
    """

    upstream = Upstream(
        httpx.Response(
            200,
            headers={"content-type": "text/event-stream"},
            content=dies_after(b'event: message_start\ndata: {"type":"message_start"}\n\n'),
        )
    )
    with running(upstream) as client:
        reply = client.post("/v1/messages", content=LOCAL_BODY, headers=CLAUDE_CODE_HEADERS)

    assert reply.status_code == 200
    assert "message_start" in reply.text, "what did arrive still reaches the caller first"

    last = reply.text.rstrip().splitlines()[-1]
    assert last.startswith("data: ")
    said = json.loads(last[len("data: ") :])
    assert said["type"] == "error"
    assert said["error"]["type"] == "api_error"
    assert "lmstudio" in said["error"]["message"], "which backend broke is the useful half"


def test_a_buffered_reply_that_breaks_is_left_alone() -> None:
    """No event here: an SSE frame appended to a half-written JSON object is just corruption.

    The caller gets truncated JSON either way. The difference is that truncated JSON fails to parse
    where JSON with an SSE frame stapled to it fails to parse *and* looks like the router's doing.
    """

    upstream = Upstream(
        httpx.Response(
            200,
            headers={"content-type": "application/json"},
            content=dies_after(b'{"type":"message","content":['),
        )
    )
    with running(upstream) as client:
        reply = client.post("/v1/messages", content=LOCAL_BODY, headers=CLAUDE_CODE_HEADERS)

    assert reply.content == b'{"type":"message","content":['


def test_an_unexpected_failure_comes_back_in_anthropics_shape() -> None:
    """Nothing should reach a caller as a framework's plain-text 500.

    `raise_server_exceptions=False` so the test sees what the client would see; starlette re-raises
    after the handler has answered, which is what keeps the traceback in the log.
    """

    class Exploding:
        async def messages(self, request: object) -> None:
            raise RuntimeError("boom")

    app = create_app(make_config(), httpx.AsyncClient(), Rows())  # type: ignore[arg-type]
    with TestClient(app, raise_server_exceptions=False) as client:
        app.state.proxy = Exploding()
        reply = client.post("/v1/messages", content=CLAUDE_BODY, headers=CLAUDE_CODE_HEADERS)

    assert reply.status_code == 500
    assert reply.json()["error"]["type"] == "api_error"
    assert "RuntimeError: boom" in reply.json()["error"]["message"]


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
        client.post("/v1/messages/count_tokens", content=LOCAL_BODY, headers=CLAUDE_CODE_HEADERS)

    assert str(upstream.received.url) == "http://localhost:1234/v1/messages/count_tokens"


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
def test_peek_returns_nothing_when_there_is_no_usable_model(body: bytes) -> None:
    assert peek(body).model is None


def test_peek_finds_the_model() -> None:
    assert peek(CLAUDE_BODY).model == "claude-sonnet-5"


@pytest.mark.parametrize(
    ("body", "expected"),
    [
        (b'{"model":"m","stream":true}', True),
        (b'{"model":"m","stream":false}', False),
        # Absent is the API default, and it is how Claude Code sends every non-streaming call —
        # measured on 2026-07-31, where reading it as unknown left 83 of 142 rows saying nothing.
        (b'{"model":"m"}', False),
        # Only these two leave the column empty, so an empty cell means one thing: we could not tell.
        (b'{"model":"m","stream":"yes"}', None),
        (b"not json", None),
    ],
)
def test_peek_finds_the_stream_flag(body: bytes, expected: bool | None) -> None:
    """Absent reads as false; only an unparseable body or a non-boolean reads as unknown."""
    assert peek(body).stream is expected


# ---------------------------------------------------------------------------------------------
# Phase 14: what a failed reply is allowed to say about why it failed.
#
# A 429 body is the single word "Error". Which bucket was hit and when it clears are in the
# response headers or nowhere, and the recorder has never read one.
# ---------------------------------------------------------------------------------------------

RATE_LIMITED = {
    "retry-after": "42",
    "anthropic-ratelimit-requests-limit": "1000",
    "anthropic-ratelimit-requests-remaining": "0",
    "anthropic-ratelimit-requests-reset": "2026-09-18T12:00:00Z",
    "request-id": "req_redacted0000000000000001",
}


def test_a_failed_reply_logs_the_allowlisted_headers_with_their_values(
    caplog: pytest.LogCaptureFixture,
) -> None:
    upstream = Upstream(streamed(429, headers=RATE_LIMITED, chunks=[b'{"type":"error"}']))
    with (
        caplog.at_level(logging.WARNING, logger="ilirium_llm_router.proxy"),
        running(upstream) as client,
    ):
        client.post("/v1/messages", content=CLAUDE_BODY, headers=CLAUDE_CODE_HEADERS)

    line = "\n".join(caplog.messages)
    assert "replied 429" in line
    assert "retry-after=42" in line
    assert "anthropic-ratelimit-requests-remaining=0" in line
    assert "request-id=req_redacted0000000000000001" in line


def test_a_header_outside_the_allowlist_never_reaches_the_log(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """The promise is that nothing unnamed is written. A credential is the case that matters."""
    upstream = Upstream(
        streamed(
            429,
            headers={
                **RATE_LIMITED,
                "authorization": "Bearer sk-secret-value",
                "set-cookie": "session=secret-value",
                "anthropic-organization-id": "org_secret_value",
            },
            chunks=[b'{"type":"error"}'],
        )
    )
    with (
        caplog.at_level(logging.WARNING, logger="ilirium_llm_router.proxy"),
        running(upstream) as client,
    ):
        client.post("/v1/messages", content=CLAUDE_BODY, headers=CLAUDE_CODE_HEADERS)

    line = "\n".join(caplog.messages)
    assert "secret-value" not in line
    assert "authorization" not in line
    assert "set-cookie" not in line
    assert "organization" not in line
    # ...while the allowlisted ones still came through, so this is not passing by logging nothing.
    assert "retry-after=42" in line


def test_an_unlisted_rate_limit_bucket_is_named_but_never_valued(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """A bucket Anthropic adds later must become visible without its value being recorded."""
    upstream = Upstream(
        streamed(
            429,
            headers={**RATE_LIMITED, "anthropic-ratelimit-tokens-per-hour-remaining": "7"},
            chunks=[b'{"type":"error"}'],
        )
    )
    with (
        caplog.at_level(logging.WARNING, logger="ilirium_llm_router.proxy"),
        running(upstream) as client,
    ):
        client.post("/v1/messages", content=CLAUDE_BODY, headers=CLAUDE_CODE_HEADERS)

    line = "\n".join(caplog.messages)
    assert "anthropic-ratelimit-tokens-per-hour-remaining=<unlisted>" in line
    assert "=7" not in line


def test_a_rejection_carrying_no_rate_limit_headers_says_so(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """The finding this phase is most likely to make, and a blank tail would hide it.

    A `rate_limit_error` that names no exhausted bucket is not a rate limit.
    """
    upstream = Upstream(streamed(429, chunks=[b'{"type":"error"}']))
    with (
        caplog.at_level(logging.WARNING, logger="ilirium_llm_router.proxy"),
        running(upstream) as client,
    ):
        client.post("/v1/messages", content=CLAUDE_BODY, headers=CLAUDE_CODE_HEADERS)

    assert "replied 429" in "\n".join(caplog.messages)
    assert "(none)" in "\n".join(caplog.messages)


def test_a_successful_reply_never_warns(caplog: pytest.LogCaptureFixture) -> None:
    """Nothing is wrong, so nothing warns. The success path logs at INFO and only once -- below."""
    upstream = Upstream(streamed(200, headers=RATE_LIMITED))
    with (
        caplog.at_level(logging.WARNING, logger="ilirium_llm_router.proxy"),
        running(upstream) as client,
    ):
        client.post("/v1/messages", content=CLAUDE_BODY, headers=CLAUDE_CODE_HEADERS)

    assert caplog.messages == []


def test_the_relayed_reply_is_untouched_by_reading_its_headers() -> None:
    """Byte-relay is not negotiable. Reading headers must not change what the caller receives."""
    upstream = Upstream(streamed(429, headers=RATE_LIMITED, chunks=[b'{"type":"error"}']))
    with running(upstream) as client:
        reply = client.post("/v1/messages", content=CLAUDE_BODY, headers=CLAUDE_CODE_HEADERS)

    assert reply.status_code == 429
    assert reply.content == b'{"type":"error"}'
    # The client still receives the headers; recording them is a copy, not a move.
    assert reply.headers["retry-after"] == "42"
    assert reply.headers["anthropic-ratelimit-requests-remaining"] == "0"


# The control for the four tests above. "The 429 carried no rate-limit headers" is only evidence
# that something is odd if a *successful* reply on the same credential carries some.

INFO = "ilirium_llm_router.proxy"


def test_the_first_successful_reply_samples_its_headers_once(
    caplog: pytest.LogCaptureFixture,
) -> None:
    upstream = Upstream(streamed(200, headers=RATE_LIMITED))
    with caplog.at_level(logging.INFO, logger=INFO), running(upstream) as client:
        client.post("/v1/messages", content=CLAUDE_BODY, headers=CLAUDE_CODE_HEADERS)

    sampled = [m for m in caplog.messages if "sampling rate-limit headers" in m]
    assert len(sampled) == 1
    assert "anthropic-ratelimit-requests-limit=1000" in sampled[0]


def test_the_sample_is_taken_only_once_per_process(caplog: pytest.LogCaptureFixture) -> None:
    """Every call reporting its buckets would drown the file the failures have to be found in."""
    upstream = Upstream(streamed(200, headers=RATE_LIMITED))
    with caplog.at_level(logging.INFO, logger=INFO), running(upstream) as client:
        for _ in range(3):
            upstream.reply = streamed(200, headers=RATE_LIMITED)
            client.post("/v1/messages", content=CLAUDE_BODY, headers=CLAUDE_CODE_HEADERS)

    assert len([m for m in caplog.messages if "sampling rate-limit headers" in m]) == 1


def test_a_burst_of_failures_does_not_consume_the_sample(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """The case the real session produced: it opened with 429s, and a success came later.

    If a failure took the latch, a session shaped like that one would never sample a success at
    all -- and the control would be silently missing exactly when it is needed.
    """
    upstream = Upstream(streamed(429, headers=RATE_LIMITED, chunks=[b'{"type":"error"}']))
    with caplog.at_level(logging.INFO, logger=INFO), running(upstream) as client:
        for _ in range(2):
            upstream.reply = streamed(429, headers=RATE_LIMITED, chunks=[b'{"type":"error"}'])
            client.post("/v1/messages", content=CLAUDE_BODY, headers=CLAUDE_CODE_HEADERS)
        assert not [m for m in caplog.messages if "sampling rate-limit headers" in m]

        upstream.reply = streamed(200, headers=RATE_LIMITED)
        client.post("/v1/messages", content=CLAUDE_BODY, headers=CLAUDE_CODE_HEADERS)

    assert len([m for m in caplog.messages if "sampling rate-limit headers" in m]) == 1


def test_the_sample_obeys_the_same_allowlist(caplog: pytest.LogCaptureFixture) -> None:
    """A second place headers are written is a second place a credential could land."""
    upstream = Upstream(
        streamed(200, headers={**RATE_LIMITED, "authorization": "Bearer sk-secret-value"})
    )
    with caplog.at_level(logging.INFO, logger=INFO), running(upstream) as client:
        client.post("/v1/messages", content=CLAUDE_BODY, headers=CLAUDE_CODE_HEADERS)

    # Scoped to the reply sampler's own line. Asserting over every message was wrong once the
    # ARRIVING sampler landed: that one prints `authorization=<unlisted>`, which is the name with
    # no value and is exactly what it is supposed to print.
    line = next(m for m in caplog.messages if "sampling rate-limit headers" in m)
    assert "secret-value" not in line
    assert "authorization" not in line
    assert "retry-after=42" in line


def test_a_reply_with_no_rate_limit_headers_still_samples(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """`(none)` on a success is the answer that makes the 429's `(none)` mean nothing."""
    upstream = Upstream(streamed(200))
    with caplog.at_level(logging.INFO, logger=INFO), running(upstream) as client:
        client.post("/v1/messages", content=CLAUDE_BODY, headers=CLAUDE_CODE_HEADERS)

    sampled = [m for m in caplog.messages if "sampling rate-limit headers" in m]
    assert len(sampled) == 1 and "(none)" in sampled[0]


# Discovered 2026-09-18: a subscription credential is metered by `anthropic-ratelimit-unified-*`,
# and not one of the documented API-key bucket names ever arrives on it.

UNIFIED = {
    "anthropic-ratelimit-unified-status": "allowed",
    "anthropic-ratelimit-unified-5h-utilization": "31",
    "anthropic-ratelimit-unified-7d-status": "allowed",
    "anthropic-ratelimit-unified-representative-claim": "whatever-this-is",
}


def test_the_unified_family_is_recorded_with_its_values(
    caplog: pytest.LogCaptureFixture,
) -> None:
    upstream = Upstream(streamed(200, headers=UNIFIED))
    with caplog.at_level(logging.INFO, logger=INFO), running(upstream) as client:
        client.post("/v1/messages", content=CLAUDE_BODY, headers=CLAUDE_CODE_HEADERS)

    line = "\n".join(caplog.messages)
    assert "anthropic-ratelimit-unified-status=allowed" in line
    assert "anthropic-ratelimit-unified-5h-utilization=31" in line
    assert "anthropic-ratelimit-unified-7d-status=allowed" in line


def test_the_representative_claim_is_named_but_its_value_withheld(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Its name is not the vocabulary of counters, and nobody has established what it holds.

    Held back on purpose rather than by oversight: adding a name to the allowlist is one line,
    and taking a value back out of a log file is not.
    """
    upstream = Upstream(streamed(200, headers=UNIFIED))
    with caplog.at_level(logging.INFO, logger=INFO), running(upstream) as client:
        client.post("/v1/messages", content=CLAUDE_BODY, headers=CLAUDE_CODE_HEADERS)

    line = "\n".join(caplog.messages)
    assert "anthropic-ratelimit-unified-representative-claim=<unlisted>" in line
    assert "whatever-this-is" not in line


def test_the_probe_endpoint_does_not_spend_the_sample(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Regression, 2026-09-18: it did, on a real run, and the line it wrote said `(none)`.

    Claude Code probes `/api/hello` before its first real call. That endpoint meters nothing, so
    it can only ever report an empty header set -- which is the same string a rejection prints.
    A control that samples it answers the opposite of the question it was built to answer.
    """
    upstream = Upstream(streamed(200))
    with caplog.at_level(logging.INFO, logger=INFO), running(upstream) as client:
        client.get("/api/hello")
        assert not [m for m in caplog.messages if "sampling rate-limit headers" in m]

        upstream.reply = streamed(200, headers=RATE_LIMITED)
        client.post("/v1/messages", content=CLAUDE_BODY, headers=CLAUDE_CODE_HEADERS)

    sampled = [m for m in caplog.messages if "sampling rate-limit headers" in m]
    assert len(sampled) == 1
    assert "/v1/messages" in sampled[0]
    assert "retry-after=42" in sampled[0]


def test_the_client_offers_http2() -> None:
    """Phase 14 experiment: the router spoke HTTP/1.1 where the direct path speaks HTTP/2.

    Asserted on the real client factory rather than on the mock transport the other tests use,
    because `http2=True` is a property of the client and the mock never negotiates anything.

    It NEGOTIATES: httpx offers h2 over ALPN and falls back to 1.1 if the backend declines, so
    LM Studio is unaffected. If the experiment comes back negative this test goes with it.

    **This assertion reads httpx private attributes** and will break on an httpx upgrade that
    renames them. That is accepted deliberately: the alternative is asserting nothing, and an
    experiment nobody can confirm is running is the failure mode this phase has already hit twice.
    A breakage here means "check how to ask httpx this question now", not "the router is wrong".
    """
    import h2  # noqa: F401  -- the stack httpx needs; absent, http2=True is silently inert

    assert create_client(http2=True)._transport._pool._http2 is True


def test_the_client_speaks_http_1_1_by_default() -> None:
    """***The shipped behaviour since 2026-09-19.***

    The experiment is eliminated twice over -- the nine classifier calls Anthropic answered
    correctly on 2026-09-19 went over HTTP/1.1 on both legs -- so the default is off. Inbound is
    HTTP/1.1 regardless: uvicorn speaks only `h11`/`httptools`. -> `BKL-0039`.
    """
    assert create_client()._transport._pool._http2 is False


# Phase 14, the byte-capture half that costs no session: what Claude Code sends the router.

def test_the_arriving_request_is_sampled_once_per_shape(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Two latches, because the PAIR is the measurement.

    The streamed request succeeds and the non-streamed one is rejected, so what the client sends
    differently between them is the thing being looked for. One latch would sample whichever
    arrived first and never the other.
    """
    upstream = Upstream(streamed(200))
    streaming_body = b'{"model":"claude-sonnet-5","stream":true,"messages":[]}'
    with caplog.at_level(logging.INFO, logger=INFO), running(upstream) as client:
        for _ in range(2):
            upstream.reply = streamed(200)
            client.post("/v1/messages", content=CLAUDE_BODY, headers=CLAUDE_CODE_HEADERS)
            upstream.reply = streamed(200)
            client.post("/v1/messages", content=streaming_body, headers=CLAUDE_CODE_HEADERS)

    arriving = [m for m in caplog.messages if m.startswith("arriving")]
    assert len(arriving) == 2
    assert sum("non-streamed" in m for m in arriving) == 1
    assert sum(m.startswith("arriving streamed") for m in arriving) == 1


def body_of(size: int) -> bytes:
    """A routable request body of exactly `size` bytes — the model name has to survive the padding."""
    head = b'{"model":"claude-sonnet-5","messages":[{"role":"user","content":"'
    tail = b'"}]}'
    return head + b"x" * (size - len(head) - len(tail)) + tail


def test_size_band_is_the_decimal_order_of_magnitude() -> None:
    """The ladder itself, stated in the two numbers that made it necessary."""
    from ilirium_llm_router.proxy import size_band

    assert size_band(323) == 2
    assert size_band(127_949) == 5
    # Exact at a power of ten, which is where a log10 implementation would be at the mercy of floats.
    assert [size_band(n) for n in (0, 1, 9, 10, 99, 100, 999, 1_000)] == [0, 0, 0, 1, 1, 2, 2, 3]


def test_both_sizes_of_one_shape_are_sampled(caplog: pytest.LogCaptureFixture) -> None:
    """***The regression test for the defect the whole key change exists to fix.***

    On 2026-09-18 at 14:52 the non-streamed latch was spent on a **323-byte `haiku` warm-up**, and
    the classifier requests that followed — **127,949 bytes**, same path, same shape — were never
    sampled. So the run could not answer the question it was run to answer.

    **Same path, same shape, arriving in the order they really arrived in.** A single latch keyed on
    the shape alone logs one line here; the size band makes it two.
    """
    warm_up, classifier = body_of(323), body_of(127_949)
    upstream = Upstream()
    with caplog.at_level(logging.INFO, logger=INFO), running(upstream) as client:
        client.post("/v1/messages", content=warm_up, headers=CLAUDE_CODE_HEADERS)
        client.post("/v1/messages", content=classifier, headers=CLAUDE_CODE_HEADERS)

    arriving = [m for m in caplog.messages if m.startswith("arriving")]
    assert len(arriving) == 2
    assert sum("323 bytes" in m for m in arriving) == 1
    assert sum("127949 bytes" in m for m in arriving) == 1


def test_a_second_request_in_the_same_band_is_not_sampled(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """The half that keeps the log small: once per shape, not once per request.

    Two bodies that differ in size but share a band are one shape, or a busy session would log
    every request it carried.
    """
    upstream = Upstream()
    with caplog.at_level(logging.INFO, logger=INFO), running(upstream) as client:
        client.post("/v1/messages", content=body_of(200), headers=CLAUDE_CODE_HEADERS)
        client.post("/v1/messages", content=body_of(999), headers=CLAUDE_CODE_HEADERS)

    assert len([m for m in caplog.messages if m.startswith("arriving")]) == 1


def test_sampling_stops_at_the_cap_and_says_so(caplog: pytest.LogCaptureFixture) -> None:
    """The bound, and the announcement that keeps it from being a silent stop.

    The key carries the request path and `app.py` has a catch-all route, so the key space is
    whatever a caller types. **An instrument that quietly gives up looking is this phase's own
    recurring defect** — hence the line, which is the part worth testing.
    """
    from ilirium_llm_router.proxy import ARRIVAL_SAMPLE_CAP

    upstream = Upstream()
    with caplog.at_level(logging.INFO, logger=INFO), running(upstream) as client:
        for n in range(ARRIVAL_SAMPLE_CAP + 3):
            client.post(f"/v1/messages/{n}", content=CLAUDE_BODY, headers=CLAUDE_CODE_HEADERS)

    assert len([m for m in caplog.messages if m.startswith("arriving")]) == ARRIVAL_SAMPLE_CAP
    stopped = [m for m in caplog.messages if m.startswith("arrival sampling stopped")]
    assert len(stopped) == 1
    assert str(ARRIVAL_SAMPLE_CAP) in stopped[0]


def test_the_arriving_sample_never_logs_the_credential(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """The whole reason this is safe to point at a request that carries the token.

    `authorization` is outside RECORDED_REQUEST_HEADERS, so it is named and never valued -- by the
    rule, not by a special case for it.
    """
    upstream = Upstream(streamed(200))
    with caplog.at_level(logging.INFO, logger=INFO), running(upstream) as client:
        client.post("/v1/messages", content=CLAUDE_BODY, headers=CLAUDE_CODE_HEADERS)

    line = next(m for m in caplog.messages if m.startswith("arriving"))
    assert "sk-ant-oat01-example" not in line
    assert "authorization=<unlisted>" in line
    # ...while the headers that matter for the diff came through with their values.
    assert f"anthropic-beta={BETA}" in line
    assert "user-agent=claude-cli/2.1.212 (external, sdk-cli)" in line


def test_the_arriving_sample_preserves_header_order() -> None:
    """Order is a difference a client could have, so sorting it away would hide the quarry."""
    from starlette.datastructures import Headers

    from ilirium_llm_router.proxy import describe_request_headers

    class _Req:
        headers = Headers(raw=[(b"x-app", b"cli"), (b"accept", b"*/*"), (b"x-app", b"again")])

    line = describe_request_headers(_Req())  # type: ignore[arg-type]
    assert line == "x-app=cli accept=*/* x-app=again"


def test_the_probe_endpoint_cannot_spend_the_messages_latch(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """The trap the reply sampler fell into: /api/hello arrives first on every session.

    ***This asserted that the probe logs NOTHING until 2026-09-19***, because the sampler refused
    every path but `/v1/messages`. The path is now part of the key instead, so the probe gets a line
    of its own and still cannot take the one that matters. **The concern was never that the probe is
    uninteresting** — it was that it must not consume somebody else's sample, and that is now true
    by construction rather than by exclusion.
    """
    upstream = Upstream()
    with caplog.at_level(logging.INFO, logger=INFO), running(upstream) as client:
        client.get("/api/hello")
        client.post("/v1/messages", content=CLAUDE_BODY, headers=CLAUDE_CODE_HEADERS)

    arriving = [m for m in caplog.messages if m.startswith("arriving")]
    assert len(arriving) == 2
    assert sum("to /api/hello:" in m for m in arriving) == 1
    assert sum("to /v1/messages:" in m for m in arriving) == 1


def test_the_path_is_part_of_the_shape_key(caplog: pytest.LogCaptureFixture) -> None:
    """Two requests identical in every way the key looks at **except the path**.

    ***Written because the test above passed a mutation that deleted the path from the key.*** Its
    probe is a bodiless `GET` and its real call carries 71 bytes, so the two stay distinct on the
    size band alone and the path assertion rode along for free. **The mutation was right and the
    test was vacuous** — so this one varies nothing but the path.
    """
    upstream = Upstream()
    with caplog.at_level(logging.INFO, logger=INFO), running(upstream) as client:
        client.post("/v1/messages", content=CLAUDE_BODY, headers=CLAUDE_CODE_HEADERS)
        client.post("/api/hello", content=CLAUDE_BODY, headers=CLAUDE_CODE_HEADERS)

    arriving = [m for m in caplog.messages if m.startswith("arriving")]
    assert len(arriving) == 2
    assert sum("to /api/hello:" in m for m in arriving) == 1
    assert sum("to /v1/messages:" in m for m in arriving) == 1


# Phase 14 experiment: imitating what Claude Code withholds from a custom base URL.

def test_no_attribution_is_fabricated_by_default() -> None:
    """***The shipped behaviour, and the reason it is the default.***

    The client's `x-anthropic-billing-header` is a **system-prompt block in the request body**, not
    an HTTP header, so this experiment tests a channel the client never uses -- and with a
    first-party client it puts a fabricated header alongside the client's own genuine attribution,
    disagreeing with it. The router fabricates nothing unless asked.
    """
    upstream = Upstream()
    with running(upstream) as client:
        client.post("/v1/messages", content=CLAUDE_BODY, headers=CLAUDE_CODE_HEADERS)

    sent = upstream.received.headers
    assert "x-anthropic-billing-header" not in sent
    assert "x-client-request-id" not in sent


def test_the_withheld_attribution_headers_are_supplied_to_anthropic() -> None:
    upstream = Upstream()
    with running(upstream, make_config(imitate_attribution_headers=True)) as client:
        client.post("/v1/messages", content=CLAUDE_BODY, headers=CLAUDE_CODE_HEADERS)

    sent = upstream.received.headers
    assert sent["x-anthropic-billing-header"].startswith(
        "cc_version=2.1.212.0a3; cc_entrypoint=sdk-cli; cch=00000; cc_prompt_id="
    )
    assert uuid.UUID(sent["x-client-request-id"])  # a real uuid, not a placeholder


def test_the_imitation_never_reaches_lmstudio() -> None:
    """The attribution is about Claude Code and Anthropic. LM Studio has no use for any of it."""
    upstream = Upstream()
    with running(upstream, make_config(imitate_attribution_headers=True)) as client:
        client.post("/v1/messages", content=LOCAL_BODY, headers=CLAUDE_CODE_HEADERS)

    assert "x-anthropic-billing-header" not in upstream.received.headers
    assert "x-client-request-id" not in upstream.received.headers


def test_the_imitation_never_overrides_what_the_caller_sent() -> None:
    """Only gaps are filled. A client that sends its own attribution keeps it."""
    upstream = Upstream()
    headers = {**CLAUDE_CODE_HEADERS, "x-anthropic-billing-header": "cc_version=theirs;"}
    with running(upstream, make_config(imitate_attribution_headers=True)) as client:
        client.post("/v1/messages", content=CLAUDE_BODY, headers=headers)

    assert upstream.received.headers["x-anthropic-billing-header"] == "cc_version=theirs;"


def test_an_unrecognised_client_is_not_imitated() -> None:
    """No measured shape, so nothing to imitate -- and a guessed one is worse than none."""
    upstream = Upstream()
    headers = {**CLAUDE_CODE_HEADERS, "user-agent": "curl/8.4.0"}
    with running(upstream, make_config(imitate_attribution_headers=True)) as client:
        client.post("/v1/messages", content=CLAUDE_BODY, headers=headers)

    assert "x-anthropic-billing-header" not in upstream.received.headers


def test_each_call_gets_its_own_prompt_id() -> None:
    """`cc_prompt_id` is per prompt on the direct path, so a constant would be a visible tell."""
    seen = set()
    upstream = Upstream()
    with running(upstream, make_config(imitate_attribution_headers=True)) as client:
        for _ in range(3):
            upstream.reply = streamed()
            client.post("/v1/messages", content=CLAUDE_BODY, headers=CLAUDE_CODE_HEADERS)
            seen.add(upstream.requests[-1].headers["x-anthropic-billing-header"])
    assert len(seen) == 3


def test_every_imitated_header_is_legal_http() -> None:
    """Regression, 2026-09-18: the billing value ended `"; "` and h11 refuses a trailing space.

    **The existing tests could not see it.** They assert against `MockTransport`, which stores what
    it is handed and validates nothing -- so the header was malformed for the whole imitation
    experiment, went to Anthropic over HTTP/2 without complaint, and surfaced as a 502 in the
    caller's face the moment the egress hop was plaintext HTTP/1.1.

    So this validates through h11 itself rather than through anything this repository wrote.
    """
    import h11
    from starlette.datastructures import Headers

    class _Req:
        headers = Headers(raw=[(b"user-agent", b"claude-cli/2.1.267 (external, cli)")])

    made = imitation_headers(_Req())  # type: ignore[arg-type]
    assert made, "nothing was imitated, so this test would pass vacuously"
    # Raises LocalProtocolError on an illegal name or value.
    h11.Request(method="POST", target="/v1/messages", headers=[(b"host", b"x")] + made)
