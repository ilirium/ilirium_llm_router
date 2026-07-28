"""Forwarding requests to a backend and streaming the reply back.

Not implemented yet — this is Phase 1. The notes below are the constraints established before
writing any code; see CLAUDE.md ("Observed request shape") for the evidence behind them.

- Relay the request body byte for byte. Do not parse and rebuild it. Beyond forward-compatibility,
  the requests carry prompt-cache markers that match on the exact bytes of the prefix, so even a
  harmless-looking reserialization breaks cache hits and costs money on every call.
- Peek at the body only far enough to find the model name, which is all routing needs.
- Forward the path *and* its query string: the real path is `/v1/messages?beta=true`.
- Credentials: forward for cloud, strip for local. Pass `anthropic-beta` through untouched; one of
  its entries is what makes the bearer token acceptable, so trimming the list breaks authentication.
- Drop hop-by-hop and connection-describing headers (host, content-length) and let the HTTP client
  set fresh ones.
- Ask the backend for an uncompressed reply. Claude Code asks for compression on the way in, so
  this has to be overridden deliberately rather than merely left unset.
- Answer the `HEAD /` probe Claude Code sends before its first real call.
"""

from __future__ import annotations
