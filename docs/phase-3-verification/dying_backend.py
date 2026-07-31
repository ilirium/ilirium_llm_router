"""A backend that answers convincingly and then drops the connection, for Phase 3 verification.

Stands in for LM Studio being killed mid-answer. The first version of this file sent a stub
`message_start` carrying nothing but `usage`, and framed its events with a mix of CRLF and LF.
Claude Code answered "API returned an empty or malformed response (HTTP 200)" — which could equally
have been a complaint about *this file* as about the error event the router injects. So the reply
below is now the real event sequence, in the real shape, with consistent framing: whatever Claude
Code says next is about the router.

Two paths:

- anything else — a full `message_start`, a text block and a few deltas, then a reset with the
  answer half-written, which is the case the injected `error` event exists for;
- `/slow` — the same opening, then deltas for a minute, so the *caller* can be the one to go away.
"""

from __future__ import annotations

import json
import socket
import time

HOST, PORT = "127.0.0.1", 1299

HEAD = (
    b"HTTP/1.1 200 OK\r\n"
    b"content-type: text/event-stream\r\n"
    b"cache-control: no-cache\r\n"
    b"connection: close\r\n"
    b"\r\n"
)


def event(name: str, payload: dict[str, object]) -> bytes:
    """One SSE event, framed the way both backends frame theirs: LF throughout, blank line after."""
    return f"event: {name}\ndata: {json.dumps(payload)}\n\n".encode()


OPENING = (
    event(
        "message_start",
        {
            "type": "message_start",
            "message": {
                "id": "msg_01PhaseThreeStandIn",
                "type": "message",
                "role": "assistant",
                "model": "local-test",
                "content": [],
                "stop_reason": None,
                "stop_sequence": None,
                "usage": {
                    "input_tokens": 11,
                    "output_tokens": 1,
                    "cache_read_input_tokens": 0,
                    "cache_creation_input_tokens": 0,
                },
            },
        },
    )
    + event(
        "content_block_start",
        {"type": "content_block_start", "index": 0, "content_block": {"type": "text", "text": ""}},
    )
    + event("ping", {"type": "ping"})
)


def delta(text: str) -> bytes:
    return event(
        "content_block_delta",
        {"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": text}},
    )


def main() -> None:
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind((HOST, PORT))
    listener.listen(8)
    print(f"dying backend on {HOST}:{PORT}", flush=True)

    while True:
        conn, _ = listener.accept()
        request = conn.recv(65536)
        slow = b"/slow" in request.split(b"\r\n", 1)[0]
        conn.sendall(HEAD + OPENING)

        try:
            if slow:
                # Keep talking, so the caller is the one that gives up.
                for i in range(600):
                    conn.sendall(delta(f"tick {i} "))
                    time.sleep(0.1)
            else:
                # Say enough that a real client has started rendering an answer...
                for word in ("Here ", "is ", "the ", "beginning ", "of ", "an ", "answer"):
                    conn.sendall(delta(word))
                    time.sleep(0.05)
                # ...then cut it off with a reset rather than a clean end of stream.
                conn.setsockopt(
                    socket.SOL_SOCKET, socket.SO_LINGER, b"\x01\x00\x00\x00\x00\x00\x00\x00"
                )
        except OSError:
            print("caller went away", flush=True)

        conn.close()
        print("closed a connection", flush=True)


if __name__ == "__main__":
    main()
