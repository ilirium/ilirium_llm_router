#!/usr/bin/env python3
"""Phase 11's register, checked against the code — Task 22, per `IDM-008`.

**Run it, do not trust it alone.** It checks what a machine can: that every name the register lists
exists, that every value it states is the value in the code, that the CLI spells its subcommands and
flags the way the register says, and that no `❓` is left in a register cell. **What it cannot check
is prose** — a row whose *description* has drifted passes here, so the closing task is this script
**and** a read.

    uv run python docs/milestone-2-corpus/phase-11-corpus-tools/evidence/register-check.py

Exits 1 on any mismatch, so it can be a gate rather than a report.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PLAN = ROOT / "docs/milestone-2-corpus/phase-11-corpus-tools/plan.md"
SRC = ROOT / "src/ilirium_llm_router"

failures: list[str] = []
checks = 0


def check(label: str, ok: bool, detail: str = "") -> None:
    global checks
    checks += 1
    if not ok:
        failures.append(f"{label}{': ' + detail if detail else ''}")


def main() -> int:
    plan = PLAN.read_text(encoding="utf-8")
    register = plan.split("## The register", 1)[1].split("## Placeholders", 1)[0]

    # --- §1 · every module the register names exists -------------------------------------------
    for module in ("extract.py", "transcript.py", "jsonl.py", "cli.py"):
        check(f"§1 module {module}", (SRC / module).is_file())

    # --- §5 · constants, by value, imported rather than grepped --------------------------------
    sys.path.insert(0, str(ROOT / "src"))
    from ilirium_llm_router import extract, jsonl, transcript

    check("§5 CONVERSATION_KEY_CHARS == 8", transcript.CONVERSATION_KEY_CHARS == 8,
          repr(transcript.CONVERSATION_KEY_CHARS))
    check("§5 GAP_NO_REQUEST_BODY", transcript.GAP_NO_REQUEST_BODY == "no-request-body",
          repr(transcript.GAP_NO_REQUEST_BODY))
    check("§5 SCHEMA_NOTE_SUBTYPE", jsonl.SCHEMA_NOTE_SUBTYPE == "corpus-reconstruction",
          repr(jsonl.SCHEMA_NOTE_SUBTYPE))
    check("§5 GAP_SUBTYPE", jsonl.GAP_SUBTYPE == "corpus-gap", repr(jsonl.GAP_SUBTYPE))
    check("§5 PROJECT_NAME_DEFAULT", jsonl.PROJECT_NAME_DEFAULT == "corpus")
    check("§5 SYNTHETIC_UUID_NAMESPACE literal is the one the register names",
          str(jsonl.SYNTHETIC_UUID_NAMESPACE) in register, str(jsonl.SYNTHETIC_UUID_NAMESPACE))
    check("§5 eight SSE events", len(transcript.SSE_EVENTS) == 8, str(transcript.SSE_EVENTS))
    for event in ("message_start", "content_block_start", "content_block_delta",
                  "content_block_stop", "message_delta", "message_stop", "ping", "error"):
        check(f"§5 SSE event {event}", event in transcript.SSE_EVENTS)
    skips = {transcript.SKIP_EMPTY, transcript.SKIP_ERROR, transcript.SKIP_STREAM_ERROR,
             transcript.SKIP_NOT_A_MESSAGE, transcript.SKIP_MALFORMED, transcript.SKIP_INCOMPLETE}
    check("§5 six skip reasons", skips == {"empty", "error", "stream-error", "not-a-message",
                                           "malformed", "incomplete"}, str(sorted(skips)))
    check("§5 ABSENT_BY_CONSTRUCTION names five",
          len(jsonl.ABSENT_BY_CONSTRUCTION) == 5, str(jsonl.ABSENT_BY_CONSTRUCTION))

    # --- §7 · the names that go on disk --------------------------------------------------------
    check("§7 SEQ_DIGITS == 5", extract.SEQ_DIGITS == 5, repr(extract.SEQ_DIGITS))
    check("§7 _no-session bucket", extract.NO_SESSION == "_no-session")

    # --- §11 · five sentinels, and the one whose constant name differs from its value ----------
    from ilirium_llm_router import corpus

    stated = {corpus.DROPPED, corpus.TOO_LARGE, corpus.ABSENT, corpus.STORE_ERROR,
              corpus.NO_DICTIONARY}
    check("§11 five sentinel values", stated == {"dropped", "too_large", "absent", "error", "none"},
          str(sorted(stated)))
    check("§11 STORE_ERROR's value is `error`, not `store_error`", corpus.STORE_ERROR == "error")
    check("§11 extract knows all five", extract.SENTINELS == stated,
          str(sorted(extract.SENTINELS ^ stated)))
    check("§11 FANOUT == 2", corpus.FANOUT == 2)
    check("§11 BLOB_SUFFIX == .zst", corpus.BLOB_SUFFIX == ".zst")

    # --- §10 · the index is 26 columns, in the order the register prints ------------------------
    check("§10 INDEX_COLUMNS is 26", len(corpus.INDEX_COLUMNS) == 26,
          str(len(corpus.INDEX_COLUMNS)))
    check("§10 INDEX_SCHEMA_VERSION == 1", corpus.INDEX_SCHEMA_VERSION == 1)
    listed = re.search(r"```\n(timestamp,.*?)```", register, re.S)
    if listed:
        named = [c.strip() for c in listed.group(1).replace("\n", " ").split(",") if c.strip()]
        check("§10 the register's column list matches the code", named == list(corpus.INDEX_COLUMNS),
              f"register has {len(named)}")
    else:
        check("§10 the register prints the column list", False)

    # --- §6 · nothing this phase added collides with a name the register reserved ---------------
    reserved = ["CorpusReader", "CorpusError", "CorpusWriter", "DictionaryTrainer", "Corpus",
                "Call", "CallRecord", "COLUMNS", "MAX_ERROR_MESSAGE", "TRAIN_LEVEL", "RESCAN_EVERY",
                "SUMMARY_EVERY", "DRAIN_TIMEOUT_S"]
    for name in reserved:
        for module in (transcript, jsonl, extract):
            check(f"§6 {module.__name__.split('.')[-1]} does not redefine {name}",
                  not (hasattr(module, name) and getattr(module, name).__module__ == module.__name__
                       if hasattr(getattr(module, name, None), "__module__") else False))

    # --- §2/§3/§4 · the CLI spells what the register says --------------------------------------
    help_text = _run(["--help"])
    for command in ("serve", "check", "train-dict", "tune-dict", "extract", "verify-archive"):
        check(f"§2 subcommand {command}", command in help_text, "not in --help")
    check("§2 no `to-jsonl` command", "to-jsonl" not in help_text)
    extract_help = _run(["extract", "--help"])
    for flag in ("--out", "--format", "--session", "--model", "--agent", "--path",
                 "--project-name"):
        check(f"§3 extract {flag}", flag in extract_help, "not in extract --help")
    for struck in ("--day", "--verify-only", "--to-jsonl"):
        check(f"§3 {struck} is struck and absent", struck not in extract_help)
    verify_help = _run(["verify-archive", "--help"])
    check("§4 verify-archive takes no --out", "--out" not in verify_help)

    # --- IDM-008's closing rule: no `❓` left in a register cell --------------------------------
    cells = [line for line in register.splitlines() if line.startswith("|") and "❓" in line]
    check("register holds no `❓` in any cell", not cells,
          f"{len(cells)} row(s) still marked")

    print(f"{checks} check(s), {len(failures)} failed")
    for failure in failures:
        print(f"  FAILED  {failure}")
    return 1 if failures else 0


def _run(argv: list[str]) -> str:
    finished = subprocess.run(
        [sys.executable, "-m", "ilirium_llm_router", *argv],
        capture_output=True, text=True, check=False, cwd=ROOT,
    )
    return finished.stdout + finished.stderr


if __name__ == "__main__":
    raise SystemExit(main())
