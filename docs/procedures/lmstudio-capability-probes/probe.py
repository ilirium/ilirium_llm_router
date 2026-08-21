"""Sends one deliberately awkward request through the router and reports what LM Studio did with it.

Phase 4 asks where a local backend falls short. LM Studio publishes no compatibility table, so the
only way to know is to send the shape and look at the answer. Each file in `bodies/` is a minimal
request carrying exactly one unusual element, so a rejection names the element rather than the
request. `replay` instead sends the real captured request from
`../../captures/log-the-whole-request.txt`, which carries several at once.

Three things this checks that a bare curl would not:

- **An error hiding inside a 200.** LM Studio answers `count_tokens` with HTTP 200 and an error body
  (`../../epd/EPD-002-token-counting-for-local-backends.md`), so a status code is not a verdict here.
- **Accepted versus honoured.** A field can be taken without being acted on. Listing the content
  block types that come back is what separates "did not reject `thinking`" from "actually thought".
- **The CSV row.** Every probe tags itself with a session id, so the row it wrote can be found and
  shown next to the reply. What the recorder made of a strange call is part of the finding.

Usage, from the repository root, with the router running (`make run`) and LM Studio loaded:

    python3 docs/procedures/lmstudio-capability-probes/probe.py --list
    python3 docs/procedures/lmstudio-capability-probes/probe.py baseline
    python3 docs/procedures/lmstudio-capability-probes/probe.py replay
    python3 docs/procedures/lmstudio-capability-probes/probe.py replay --max-tokens 2048

The full transcript of every run lands in `runs/`, which is gitignored: this directory is a tool, and
the findings it produces belong in `../../reference/backend-lmstudio.md` rather than in a committed
log. A run worth keeping is copied into a phase's `evidence/` instead.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
# docs/procedures/lmstudio-capability-probes/ → three levels to the repository root. This was two
# until 2026-08-16, when the probes moved a directory deeper; nothing raised on import and `--list`
# went on working, because only `replay` and the CSV lookup reach outside this directory.
ROOT = HERE.parent.parent.parent
BODIES = HERE / "bodies"
RUNS = HERE / "runs"
CAPTURE = ROOT / "docs" / "captures" / "log-the-whole-request.txt"
CALLS_CSV = ROOT / "logs" / "telemetry" / "calls.csv"

DEFAULT_ROUTER = "http://127.0.0.1:8787"
DEFAULT_MODEL = "qwen/qwen3.5-9b"

# Headers we set ourselves rather than copying from the capture. `host` and `content-length` describe
# the old connection, `accept-encoding` would let the reply come back compressed, and the session id
# is how each probe finds its own CSV row.
OWN_HEADERS = {"host", "content-length", "accept-encoding", "x-claude-code-session-id"}


def capture_lines() -> list[str]:
    return CAPTURE.read_text().splitlines()


def captured_headers() -> dict[str, str]:
    """The real headers Claude Code sent, read out of the capture rather than retyped.

    Taken from the file so the ten-entry `anthropic-beta` list stays exactly as it arrived — one of
    its entries is what makes the bearer token acceptable to Anthropic, and whether LM Studio ignores
    the rest quietly is one of the questions this phase exists to answer.
    """
    headers: dict[str, str] = {}
    for line in capture_lines()[7:]:  # line 8 onward: the POST request, after the HEAD probe
        if not line.strip():
            break
        if line.startswith("POST "):
            continue
        name, _, value = line.partition(":")
        if name.strip().lower() not in OWN_HEADERS:
            headers[name.strip().lower()] = value.strip()
    return headers


def captured_body() -> dict:
    """The captured request body. It is one 118 KB line, the last in the file."""
    return json.loads(capture_lines()[-1])


def load_body(name: str) -> dict:
    if name == "replay":
        return captured_body()
    path = BODIES / f"{name}.json"
    if not path.exists():
        sys.exit(f"no such probe: {name}. Try --list.")
    return json.loads(path.read_text())


def probe_names() -> list[str]:
    return sorted(p.stem for p in BODIES.glob("*.json"))


def send(url: str, body: dict, headers: dict[str, str]) -> dict:
    """Send the request and collect everything about the reply, streaming or not."""
    raw = json.dumps(body).encode()
    request = urllib.request.Request(url, data=raw, headers=headers, method="POST")

    result: dict = {"request_bytes": len(raw), "events": [], "lines": []}
    started = time.monotonic()
    try:
        with urllib.request.urlopen(request) as reply:
            result["status"] = reply.status
            result["headers"] = dict(reply.headers)
            result["ttfb_ms"] = None
            for raw_line in reply:
                if result["ttfb_ms"] is None:
                    result["ttfb_ms"] = round((time.monotonic() - started) * 1000)
                result["lines"].append(raw_line.decode("utf-8", "replace").rstrip("\r\n"))
    except urllib.error.HTTPError as exc:  # a real HTTP error status, body and all
        result["status"] = exc.code
        result["headers"] = dict(exc.headers)
        result["ttfb_ms"] = round((time.monotonic() - started) * 1000)
        result["lines"] = exc.read().decode("utf-8", "replace").splitlines()
    except OSError as exc:  # the router is not running, most likely
        result["status"] = None
        result["transport_error"] = f"{type(exc).__name__}: {exc}"

    result["duration_ms"] = round((time.monotonic() - started) * 1000)
    result["response_bytes"] = sum(len(line) for line in result["lines"])
    return result


def parse_stream(lines: list[str]) -> list[tuple[str, dict | str]]:
    """Pull `event:`/`data:` pairs out of an SSE reply. Non-JSON data is kept as text."""
    events: list[tuple[str, dict | str]] = []
    pending = None
    for line in lines:
        if line.startswith("event:"):
            pending = line[6:].strip()
        elif line.startswith("data:"):
            payload = line[5:].strip()
            try:
                events.append((pending or "?", json.loads(payload)))
            except json.JSONDecodeError:
                events.append((pending or "?", payload))
            pending = None
    return events


def find_error(events: list[tuple[str, dict | str]], lines: list[str]) -> str | None:
    """An error anywhere in the reply, *including* inside an HTTP 200.

    LM Studio answers some unimplemented requests with 200 and an error body, so the status code
    alone is not a verdict. This is the check that keeps a probe from reading as a pass.
    """
    for name, payload in events:
        if name == "error" or (isinstance(payload, dict) and payload.get("type") == "error"):
            return json.dumps(payload)
    if not events and lines:
        try:
            whole = json.loads("\n".join(lines))
        except json.JSONDecodeError:
            return None
        if isinstance(whole, dict) and (whole.get("type") == "error" or "error" in whole):
            return json.dumps(whole.get("error", whole))
    return None


def summarize(result: dict) -> dict:
    """What came back, in the terms the phase cares about."""
    events = parse_stream(result["lines"])
    summary: dict = {
        "events": [name for name, _ in events],
        "blocks": [],
        "text": "",
        "thinking": "",
        "stop_reason": None,
        "usage": None,
        "error": find_error(events, result["lines"]),
    }

    for name, payload in events:
        if not isinstance(payload, dict):
            continue
        if name == "content_block_start":
            summary["blocks"].append(payload.get("content_block", {}).get("type"))
        elif name == "content_block_delta":
            delta = payload.get("delta", {})
            if delta.get("type") == "text_delta":
                summary["text"] += delta.get("text", "")
            elif delta.get("type") == "thinking_delta":
                summary["thinking"] += delta.get("thinking", "")
        elif name == "message_start":
            summary["usage"] = payload.get("message", {}).get("usage")
        elif name == "message_delta":
            summary["stop_reason"] = payload.get("delta", {}).get("stop_reason")
            summary["usage"] = payload.get("usage") or summary["usage"]

    if not events and result["lines"]:  # a non-streaming reply is one JSON object
        try:
            whole = json.loads("\n".join(result["lines"]))
        except json.JSONDecodeError:
            return summary
        if isinstance(whole, dict) and whole.get("type") == "message":
            summary["blocks"] = [b.get("type") for b in whole.get("content", [])]
            summary["text"] = "".join(
                b.get("text", "") for b in whole.get("content", []) if b.get("type") == "text"
            )
            summary["thinking"] = "".join(
                b.get("thinking", "")
                for b in whole.get("content", [])
                if b.get("type") == "thinking"
            )
            summary["stop_reason"] = whole.get("stop_reason")
            summary["usage"] = whole.get("usage")
    return summary


def csv_row(session_id: str) -> dict | None:
    """The row this probe wrote, found by its own session id."""
    if not CALLS_CSV.exists():
        return None
    import csv

    with CALLS_CSV.open() as handle:
        rows = [r for r in csv.DictReader(handle) if r.get("session_id") == session_id]
    return rows[-1] if rows else None


def counted(names: list[str]) -> str:
    """`message_start, content_block_delta ×7, message_stop` — order kept, repeats folded."""
    if not names:
        return "(none)"
    out, run, count = [], names[0], 0
    for name in names + [None]:
        if name == run:
            count += 1
            continue
        out.append(run if count == 1 else f"{run} ×{count}")
        run, count = name, 1
    return ", ".join(out)


def report(name: str, body: dict, result: dict, summary: dict, row: dict | None) -> str:
    lines = [f"=== {name} " + "=" * (72 - len(name))]

    if result.get("transport_error"):
        lines.append(f"could not reach the router: {result['transport_error']}")
        lines.append("is it running? `make run`")
        return "\n".join(lines)

    verdict = "REJECTED" if summary["error"] else "accepted"
    if summary["error"] and result["status"] == 200:
        verdict = "REJECTED — inside an HTTP 200"
    lines += [
        f"verdict        {verdict}",
        f"status         {result['status']}",
        f"request        {result['request_bytes']} bytes"
        + (f", max_tokens {body['max_tokens']}" if "max_tokens" in body else ""),
        (
            f"reply          {result['response_bytes']} bytes, "
            f"ttfb {result['ttfb_ms']} ms, total {result['duration_ms']} ms"
        ),
        f"events         {counted(summary['events'])}",
        f"blocks         {counted([b for b in summary['blocks'] if b])}",
        f"stop_reason    {summary['stop_reason']}",
        f"usage          {json.dumps(summary['usage'])}",
    ]
    if summary["error"]:
        lines.append(f"error          {summary['error'][:400]}")
    if summary["thinking"]:
        lines.append(f"thinking       {summary['thinking'][:300]!r}")
    lines.append(f"text           {summary['text'][:500]!r}")

    if row:
        lines.append(
            "csv row        "
            + ", ".join(
                f"{k}={row[k]}"
                for k in (
                    "backend",
                    "stream",
                    "input_tokens",
                    "output_tokens",
                    "stop_reason",
                    "error_status",
                    "error_code",
                )
                if row.get(k) != ""
            )
        )
    else:
        lines.append("csv row        not found — is the router writing logs/telemetry/calls.csv?")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("probe", nargs="?", help="a name from --list, or `replay`")
    parser.add_argument("--list", action="store_true", help="list the probes and exit")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--router", default=DEFAULT_ROUTER)
    parser.add_argument("--max-tokens", type=int, help="override the body's own max_tokens")
    parser.add_argument("--no-stream", action="store_true", help="ask for a buffered reply")
    args = parser.parse_args()

    if args.list or not args.probe:
        print("probes (each is a minimal request carrying one unusual element):")
        for name in probe_names():
            print(f"  {name}")
        print("  replay        the real captured request, several elements at once")
        return

    body = load_body(args.probe)
    body["model"] = args.model
    if args.max_tokens:
        body["max_tokens"] = args.max_tokens
    if args.no_stream:
        body["stream"] = False

    session_id = f"phase-4-{args.probe}-{int(time.time())}"
    headers = captured_headers() | {
        "content-type": "application/json",
        "accept-encoding": "identity",
        "x-claude-code-session-id": session_id,
    }

    result = send(f"{args.router}/v1/messages", body, headers)
    summary = summarize(result)
    time.sleep(0.2)  # the row is appended when the call completes, a moment after we see the end
    text = report(args.probe, body, result, summary, csv_row(session_id))
    print(text)

    RUNS.mkdir(exist_ok=True)
    transcript = RUNS / f"{args.probe}.txt"
    transcript.write_text(
        text
        + f"\n\nsession_id: {session_id}\n\n--- request body ---\n"
        + json.dumps(body, indent=2)[:20000]
        + "\n\n--- reply, verbatim ---\n"
        + "\n".join(result["lines"])
    )
    print(f"\nfull transcript: {transcript.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
