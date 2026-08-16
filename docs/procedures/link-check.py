"""Reports every path in the documentation that no longer resolves.

Nothing tests a link. This repository's documents cite each other constantly — a reference file names
the procedure that established it, a phase note names its evidence, a docstring names the measurement
behind a rule — and every one of those rots silently the moment something moves. The restructure of
2026-08-16 moved twenty-two documents and this script is what produced the work list.

**Its output is a work list, not a verdict.** Two rules govern what to do with a report:

- Paths in *prose* are repointed, including inside the milestone archive. A path is navigation rather
  than a claim, so updating it preserves what a frozen document means.
- Paths inside *captured output* — an `evidence/*.txt` transcript of what a command printed — are
  **never** edited. A stale command line in a transcript is correct: it is what was run that day.

Usage, from anywhere:

    python3 docs/procedures/link-check.py                  # the whole repository
    python3 docs/procedures/link-check.py docs/reference    # one tier
    python3 docs/procedures/link-check.py CLAUDE.md

Exits 1 if anything is broken, so it can gate a commit.

## What it deliberately ignores, and why

Run unfiltered on this repository it reports about forty hits of which five-sixths are noise. Four
classes are excluded, each because a real document has a good reason to contain them:

- **Template placeholders** — `phase-N-<slug>/`, `reference/backend-<name>.md`. The manual describes
  shapes that do not exist yet; that is its job.
- **Globs** — `bodies/*.json`.
- **Rename notation** — any line containing `→`. A sentence explaining that `phase-4-probes/` became
  `lmstudio-capability-probes/` names a path that is *supposed* to be gone. Writing renames with an
  arrow is therefore a convention this script depends on: use `→`, and neither side is checked.
- **Repository-root paths named in prose** — `src/`, `logs/calls.csv`. These are resolved from the
  repository root as well as from the citing file, and only reported when both miss.
- **Names that are not addresses** — a bare `runs/` or `evidence/`. The manual writes "an
  instrument's `runs/` follows the instrument"; that is the name of a kind of directory, not a path
  from the file saying it. A candidate is checked only when its first segment is `.`, `..`, or a
  directory that exists at the repository root.

`logs/` is skipped outright: it is written by running the router and is legitimately absent in a
fresh clone.

**One class is not filtered and cannot be:** a document whose *subject* is a migration names old
paths on purpose. Use `→` when writing about a rename and both sides are skipped; a sentence that
says "moving X to Y" in words will still be reported. Expect a migration plan to be noisy, and read
its hits rather than fixing them.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
TICKED = re.compile(r"`([^`\n]+)`")
BARE = re.compile(r"(?:^|\s)((?:docs|src|tests)/[^\s`'\"]+)")

SUFFIXES = (".md", ".txt", ".csv", ".py", ".yaml", ".yml", ".json", ".log", ".toml")

# Written by running the router, not by committing anything, so absent in a fresh clone.
RUNTIME = {"logs"}


def repo_root() -> Path:
    out = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=Path(__file__).resolve().parent,
        capture_output=True,
        text=True,
        check=True,
    )
    return Path(out.stdout.strip())


def is_candidate(text: str) -> bool:
    """A string worth resolving: path-shaped, not a URL, not a placeholder or a glob."""
    if not text or any(c in text for c in " <>*|") or text.startswith(("http://", "https://", "#")):
        return False
    if "/" not in text:
        return False
    return text.endswith("/") or text.endswith(SUFFIXES)


def candidates(line: str) -> set[str]:
    if "→" in line:  # a sentence about a rename; both sides are meant to be stale
        return set()
    found = set(LINK.findall(line))
    found |= {t for t in TICKED.findall(line)}
    found |= set(BARE.findall(line))
    return {c.split("#")[0].rstrip(".,;:") for c in found if is_candidate(c.split("#")[0])}


def is_addressed(candidate: str, root: Path) -> bool:
    """True if the path is *addressed* rather than merely named.

    `../reference/lessons.md` and `docs/status.md` point somewhere. A bare `runs/` or `evidence/` is
    a name for a kind of directory — the manual says "an instrument's `runs/` follows the
    instrument" — and resolving it against whichever file happens to mention it is meaningless. The
    test is the first segment: a relative marker, or a directory that exists at the repository root.
    """
    if candidate.startswith(("./", "../")):
        return True
    first = candidate.split("/")[0]
    return first in RUNTIME or (root / first).is_dir()


def resolves(candidate: str, from_file: Path, root: Path) -> bool:
    """True if the path exists relative to the citing file *or* to the repository root."""
    if candidate.split("/")[0] in RUNTIME:
        return True  # written by running the thing; legitimately absent in a fresh clone
    if (from_file.parent / candidate).exists():
        return True
    # Not `startswith(".")`: a dotted directory like `.claude/` is rooted, not relative. Getting
    # that wrong made this script report an existing file as missing the first time it was run.
    return not candidate.startswith(("./", "../", "/")) and (root / candidate).exists()


def check(paths: list[Path], root: Path) -> int:
    files = sorted({p for t in paths for p in ([t] if t.is_file() else t.rglob("*.md"))})
    broken = 0
    for f in files:
        for number, line in enumerate(f.read_text().splitlines(), start=1):
            for candidate in sorted(candidates(line)):
                if not is_addressed(candidate, root):
                    continue
                if not resolves(candidate, f, root):
                    print(f"{f.relative_to(root)}:{number}  {candidate}")
                    broken += 1
    print(f"\n{len(files)} files, {broken} broken", file=sys.stderr)
    return broken


def main() -> int:
    root = repo_root()
    args = sys.argv[1:]
    targets = [Path(a).resolve() for a in args] if args else [root]
    missing = [t for t in targets if not t.exists()]
    if missing:
        sys.exit(f"no such path: {missing[0]}")
    return 1 if check(targets, root) else 0


if __name__ == "__main__":
    raise SystemExit(main())
