"""Setting up the rotating log file.

Not implemented yet — this is Phase 2. Every call gets a human-readable line carrying the time, the
model, the chosen backend, the outcome and the duration. Rotation is size-based, with the size and
number of kept files taken from the config.

Log metadata only. The request body is never logged: it carries the whole conversation, and on the
cloud side it arrives alongside a real credential.
"""

from __future__ import annotations
