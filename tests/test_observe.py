"""Reading `usage` and `stop_reason` off a reply on its way past.

The happy path is the least interesting thing here. What these tests are really for is the failure
that looks like success: a scanner that reads `input_tokens` from `message_delta` passes every
LM Studio test anyone would think to write, and then records an empty input count for every single
Anthropic call. `test_input_tokens_are_never_taken_from_message_delta` is the reason this file
exists; the rest guards the edges around it.

The SSE fixtures are the event shapes recorded in `docs/procedures/lmstudio-usage-check.md`,
shortened.
"""

from __future__ import annotations

import json

import pytest

from ilirium_llm_router.observe import (
    MAX_SCAN_BYTES,
    BufferedScanner,
    Observation,
    Scanner,
    SseScanner,
    scanner_for,
)


def sse(*events: dict[str, object]) -> bytes:
    """The events as a real backend frames them: an `event:` line, a `data:` line, a blank line."""
    return b"".join(
        f"event: {event['type']}\ndata: {json.dumps(event)}\n\n".encode() for event in events
    )


def message_start(**usage: int) -> dict[str, object]:
    return {"type": "message_start", "message": {"role": "assistant", "usage": usage}}


def message_delta(stop_reason: str | None = "end_turn", **usage: int) -> dict[str, object]:
    return {
        "type": "message_delta",
        "delta": {"stop_reason": stop_reason},
        "usage": usage,
    }


def observed(scanner: Scanner, payload: bytes, chunk_size: int = 4096) -> Observation:
    """Feed `payload` through in chunks, the way it arrives off the wire."""
    for start in range(0, len(payload), chunk_size):
        scanner.feed(payload[start : start + chunk_size])
    scanner.finish()
    return scanner.observation


def test_the_content_type_picks_the_path_not_the_request() -> None:
    """The content-type says what the bytes are; the request's `stream` flag says what was asked."""
    assert isinstance(scanner_for("text/event-stream"), SseScanner)
    assert isinstance(scanner_for("text/event-stream; charset=utf-8"), SseScanner)
    assert isinstance(scanner_for("application/json"), BufferedScanner)
    assert isinstance(scanner_for(""), BufferedScanner)


def test_a_streamed_reply_gives_up_its_usage_and_stop_reason() -> None:
    result = observed(
        SseScanner(),
        sse(
            message_start(
                input_tokens=15, cache_read_input_tokens=5, cache_creation_input_tokens=2
            ),
            {"type": "content_block_delta", "delta": {"text": "hi"}},
            message_delta(stop_reason="end_turn", output_tokens=29),
            {"type": "message_stop"},
        ),
    )

    assert result.input_tokens == 15
    assert result.output_tokens == 29
    assert result.cache_read_input_tokens == 5
    assert result.cache_creation_input_tokens == 2
    assert result.stop_reason == "end_turn"
    assert result.stream_error is False


def test_input_tokens_are_never_taken_from_message_delta() -> None:
    """The trap. LM Studio repeats `input_tokens` in `message_delta`; Anthropic does not.

    Keying on `message_delta` would pass against the local backend and record an empty input count
    for every Anthropic call — a bug that only shows up in the backend nobody tested against.
    Here `message_start` says 15 and the delta lies and says 999.
    """
    result = observed(
        SseScanner(),
        sse(
            message_start(input_tokens=15),
            message_delta(output_tokens=29, input_tokens=999),
        ),
    )

    assert result.input_tokens == 15


def test_a_stream_with_no_message_start_records_no_input_count() -> None:
    """Empty is the honest answer. Falling back to `message_delta` is how the trap gets sprung."""
    result = observed(SseScanner(), sse(message_delta(output_tokens=29, input_tokens=999)))

    assert result.input_tokens is None
    assert result.output_tokens == 29


def test_events_split_across_chunks_are_still_read() -> None:
    """Chunk boundaries fall wherever the network puts them, not on event boundaries."""
    payload = sse(message_start(input_tokens=15), message_delta(output_tokens=29))

    for chunk_size in (1, 3, 17, 64):
        result = observed(SseScanner(), payload, chunk_size=chunk_size)
        assert result.input_tokens == 15, f"broke at chunk size {chunk_size}"
        assert result.output_tokens == 29, f"broke at chunk size {chunk_size}"


def test_an_intermediate_delta_cannot_wipe_out_the_real_stop_reason() -> None:
    """A null `stop_reason` arriving after the real one must not overwrite it."""
    result = observed(
        SseScanner(),
        sse(
            message_delta(stop_reason="max_tokens", output_tokens=29),
            message_delta(stop_reason=None, output_tokens=29),
        ),
    )

    assert result.stop_reason == "max_tokens"


def test_an_error_event_mid_stream_is_caught() -> None:
    """A streamed reply returns HTTP 200 before content exists, so this is the only signal."""
    result = observed(
        SseScanner(),
        sse(
            message_start(input_tokens=15),
            {
                "type": "error",
                "error": {"type": "overloaded_error", "message": "Overloaded"},
            },
        ),
    )

    assert result.stream_error is True
    assert result.error_type == "overloaded_error"
    assert result.error_message == "Overloaded"
    assert result.input_tokens == 15, "what did arrive before the error is still worth recording"


def test_one_unreadable_line_does_not_stop_the_rest_of_the_stream() -> None:
    payload = (
        b"data: {this is not json\n\n"
        + sse(message_start(input_tokens=15))
        + b"data: \n\n"
        + sse(message_delta(output_tokens=29))
    )

    result = observed(SseScanner(), payload)

    assert result.input_tokens == 15
    assert result.output_tokens == 29


def test_a_final_line_with_no_newline_after_it_is_still_read() -> None:
    """The line held back is the *last* one — where `output_tokens` and `stop_reason` live.

    A backend that stops after the closing brace rather than sending a blank line would otherwise
    cost exactly the two numbers the stream was being watched for.
    """
    payload = sse(
        message_start(input_tokens=15), message_delta(stop_reason="end_turn", output_tokens=29)
    ).rstrip(b"\n")

    result = observed(SseScanner(), payload)

    assert result.output_tokens == 29
    assert result.stop_reason == "end_turn"


def test_a_stream_cut_off_mid_event_keeps_what_it_saw() -> None:
    """A reply cut off inside a JSON document still has an input count worth writing down."""
    payload = sse(
        message_start(input_tokens=15), message_delta(stop_reason="end_turn", output_tokens=29)
    )
    cut_inside_the_last_event = payload[: -len(b'okens":29}}\n\n')]

    result = observed(SseScanner(), cut_inside_the_last_event)

    assert result.input_tokens == 15
    assert result.output_tokens is None
    assert result.stop_reason is None


def test_a_non_streaming_reply_is_read_from_the_top_level() -> None:
    body = json.dumps(
        {
            "type": "message",
            "stop_reason": "end_turn",
            "usage": {
                "input_tokens": 15,
                "output_tokens": 29,
                "cache_read_input_tokens": 5,
            },
        }
    ).encode()

    result = observed(BufferedScanner(), body)

    assert result.input_tokens == 15
    assert result.output_tokens == 29
    assert result.cache_read_input_tokens == 5
    assert result.cache_creation_input_tokens is None
    assert result.stop_reason == "end_turn"


def test_usage_is_found_wherever_it_sits_in_the_object() -> None:
    """JSON guarantees no field order, and a tail buffer was rejected for betting on it."""
    body = json.dumps(
        {"usage": {"input_tokens": 15, "output_tokens": 29}, "content": ["x" * 5000]}
    ).encode()

    result = observed(BufferedScanner(), body)

    assert result.input_tokens == 15


def test_a_non_streaming_error_body_gives_its_wording_but_is_not_a_stream_error() -> None:
    """It came back with an HTTP status that already says it failed; only the wording is new."""
    body = json.dumps(
        {"type": "error", "error": {"type": "rate_limit_error", "message": "slow down"}}
    ).encode()

    result = observed(BufferedScanner(), body)

    assert result.stream_error is False
    assert result.error_type == "rate_limit_error"
    assert result.error_message == "slow down"


def test_a_reply_past_the_cap_is_abandoned_rather_than_held() -> None:
    """The cap exists for the catch-all route, whose replies nobody has enumerated."""
    scanner = BufferedScanner()
    body = b'{"usage":{"input_tokens":15},"padding":"' + b"x" * MAX_SCAN_BYTES + b'"}'

    result = observed(scanner, body)

    assert scanner.gave_up is True
    assert result.input_tokens is None


def test_an_endless_sse_line_is_abandoned_rather_than_held() -> None:
    scanner = SseScanner()

    result = observed(scanner, b"data: " + b"x" * (MAX_SCAN_BYTES + 1))

    assert scanner.gave_up is True
    assert result.input_tokens is None


def test_a_big_chunk_of_short_lines_is_read_rather_than_abandoned() -> None:
    """The cap is about one unbroken line, not about how much arrived at once.

    Checked before the split, it measured the previous tail plus the whole incoming chunk, so a
    single large chunk of ordinary events tripped it and cost every token column — which reads in
    the CSV exactly like the SSE scanner failing, for a stream that was perfectly well formed.
    """
    scanner = SseScanner()
    filler = sse({"type": "content_block_delta", "delta": {"text": "x" * 40}})
    chunk = (
        sse(message_start(input_tokens=15))
        + filler * (MAX_SCAN_BYTES // len(filler) + 10)
        + sse(message_delta(output_tokens=7, stop_reason="end_turn"))
    )

    assert len(chunk) > MAX_SCAN_BYTES, "the chunk is over the cap"
    assert max(len(line) for line in chunk.split(b"\n")) < 200, "no single line is anywhere near it"

    # Delivered whole, not in `observed`'s 4096-byte slices: one big read is the case that broke,
    # and slicing it up is what hid the defect from every test until now.
    result = observed(scanner, chunk, chunk_size=len(chunk))

    assert scanner.gave_up is False
    assert result.input_tokens == 15
    assert result.output_tokens == 7
    assert result.stop_reason == "end_turn"


def test_a_long_stream_does_not_accumulate() -> None:
    """Memory stays flat however long the model talks — the point of discarding as it goes."""
    scanner = SseScanner()
    scanner.feed(sse(message_start(input_tokens=15)))
    for _ in range(2000):
        scanner.feed(sse({"type": "content_block_delta", "delta": {"text": "word "}}))
    scanner.feed(sse(message_delta(output_tokens=29)))
    scanner.finish()

    assert len(scanner._pending) == 0
    assert scanner.observation.input_tokens == 15
    assert scanner.observation.output_tokens == 29


@pytest.mark.parametrize(
    "body",
    [b"", b"not json at all", b"[]", b'"a string"', b"null"],
)
def test_an_unreadable_non_streaming_body_is_survived(body: bytes) -> None:
    """The catch-all route forwards paths whose replies are not JSON at all."""
    result = observed(BufferedScanner(), body)

    assert result == Observation()


@pytest.mark.parametrize("value", [True, "15", None, 1.5, {"n": 1}])
def test_a_token_count_that_is_not_a_number_reads_as_absent(value: object) -> None:
    """`True` is an `int` in Python, and would otherwise be recorded as one token."""
    result = observed(
        SseScanner(),
        sse(message_start(input_tokens=value)),  # type: ignore[arg-type]
    )

    assert result.input_tokens is None


def test_a_scanner_that_breaks_internally_does_not_raise() -> None:
    """Watching a call must never break it, whatever goes wrong in here."""
    scanner = BufferedScanner()

    def explode(chunk: bytes) -> None:
        raise RuntimeError("something unforeseen")

    scanner._feed = explode  # type: ignore[method-assign]
    scanner.feed(b"anything")
    scanner.finish()

    assert scanner.gave_up is True
    assert scanner.observation == Observation()
