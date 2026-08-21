"""Reports every path in the documentation that no longer resolves, or resolves the long way round.

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

Exits 1 if anything is broken **or roundabout**, so it can gate a commit.

## Two kinds of finding

**Broken** — the path does not resolve at all. **Roundabout** — it resolves, and a shorter relative
form of the same target exists. The second was added 2026-08-16 after the archive repoint produced
two paths that were valid and absurd: a file inside `milestone-1-core/` addressing its own sibling by
going out to `docs/` and back, and a phase plan naming the file beside it by full path. Neither was
broken, so nothing caught them but a human reading the diff.

It reports zero on the tree it was written against, which is the property that makes it worth
having — it is silent until something is actually wrong.

## What it deliberately ignores, and why

Run unfiltered on this repository it reports about forty hits of which five-sixths are noise. Four
classes are excluded, each because a real document has a good reason to contain them:

- **Template placeholders** — `phase-N-<slug>/`, `reference/backend-<name>.md`. The manual describes
  shapes that do not exist yet; that is its job.
- **Globs** — `bodies/*.json`.
- **Rename notation** — any line containing `→`. A sentence explaining that `phase-4-probes/` became
  `lmstudio-capability-probes/` names a path that is *supposed* to be gone. Writing renames with an
  arrow is therefore a convention this script depends on: use `→`, and neither side is checked.
- **Repository-root paths named in prose** — `src/`, `logs/telemetry/calls.csv`. These are
  resolved from the repository root as well as from the citing file, and only reported when both
  miss.
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

**In this repository that class has a permanent address:**
`docs/milestone-1-core/phase-7-docs-restructure/`, the 2026-08-16 restructure's plan and notes. Those
two files account for **61** of the whole-repository run's 68 broken hits — they are frozen archive
describing paths that no longer exist, which is what they are *for*. The useful invocation is therefore
usually:

    python3 docs/procedures/link-check.py CLAUDE.md README.md docs/reference docs/procedures \
        docs/epd docs/captures docs/README.md docs/status.md docs/backlog.md

## A clean run is not a zero run

**A whole-repository run reports 68 broken and 2 roundabout, and every one of them is correct.**
Re-derived 2026-08-17 by running it, at the close of Phase 8:

- **61** — the restructure plan and notes above.
- **3** — `docs/milestone-1-core/documentation-review-2026-08-16.md`, whose own header explains them: it
  quotes broken paths as its subject. Both **roundabout** hits are in that file too, written in another
  file's frame of reference, so shortening them would falsify a finding.
- **2** — the deliberate absences, listed next.
- **2** — `docs/milestone-2-corpus/phase-8-method-and-guardrails/plan.md` quoting that same list of
  deliberate absences, which makes them the same class rather than a new one.

**Some hits are correct and permanent.** A document that names a path in order to say *this
deliberately does not exist* is right, and nothing distinguishes it from a broken link — the `→`
convention covers renames, not deliberate absences. Outside the archive there are **two**, and a
session expecting zero would either "fix" the prose or conclude the work is unfinished:

- `.claude/agents/local-helper.md` — `EPD-001` naming the subagent file it *would* create.
- `docs/procedures/closing-a-milestone.md` — `EPD-004`'s escape hatch if a playbook outgrows the
  manual. **Named and not taken.** The closing playbook did outgrow it — 51 lines against a 40-line
  trigger — and on 2026-08-20 it went to `docs/method/IDM-006-closing-a-milestone.md` instead, because
  `method/` did not exist when the hatch was written. So this path stays a deliberate absence
  permanently rather than pending: `EPD-004:626` still names it, and nothing will ever build it.

**This list was seven until 2026-08-17, and five of the seven stopped being permanent in a single
phase.** Phase 8 built the tracked `.claude/settings.json` and the `docs/method/` tier, so
`.claude/settings.json` ×3 and `docs/method/` ×2 now resolve. **That is the argument for not trusting
any of the numbers above without re-running this script**, and it is stronger than it looks: the ten
*further* copies of those two paths inside the frozen archive resolved at the same moment, which is why
the 71 above is now 61 — and the sentence that used to follow it said those 71 would be broken "always".
Two attempts at predicting this count from the old prose, one in Phase 8's plan and one in its
re-derivation, were both wrong and wrong in the same direction, because the prose partitions hits by
*where they live* while what resolves them is *which path they name*.

**Re-run 2026-08-20, mid-Phase-10: 99 broken, 2 roundabout — and the partition above no longer holds.**
Two things moved it, and neither is a documentation defect:

- **Phase 10 is in flight.** Nineteen hits name `reference/corpus.md`, `procedures/corpus-dictionary/`
  and `procedures/corpus-benchmark/runs/` — a plan and two review charters describing files their own
  phase has not landed yet. They resolve when it merges, exactly as `docs/method/` ×2 did in Phase 8.
- **Thirteen name `.claude/settings.local.json`, which is untracked**, and that is a property of this
  script worth knowing before comparing any two runs: **the count depends on files git does not
  carry.** A fresh clone — or a second `git worktree`, which is where this was found — reports **99**;
  the checkout holding the local settings file reports **86**. Neither is wrong, and a session that
  compares its own run against a docstring written on the other one will conclude something broke.

Deriving a fresh partition here would bake in a number that changes the day Phase 10 merges, so the
list above is Phase 8's and is left as Phase 8's. What this run does establish is narrower and is the
reason it was made: **moving both playbooks out to `docs/method/` on 2026-08-20 added no broken path.**

**Also worth knowing before trusting a clean run:** this script reads `*.md` only when handed a
directory, so citations in `config.yaml`, the `Makefile`, `pyproject.toml`, `.env.example` and `src/` are
unchecked unless named on the command line — one stale path was found that way in Phase 8. And a line
containing `→` is skipped whole, which means `CLAUDE.md`'s five `→` pointer lines are not checked at all.

Check the list before adding to it. Teaching this script to recognise them is filed in
`../backlog.md`, which also carries what Phase 8 measured about maintaining this docstring by hand.
"""

from __future__ import annotations

import os
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


def roundabout(candidate: str, from_file: Path) -> str | None:
    """The shorter relative form of a path that resolves, or None if it is already shortest.

    A path can be valid and still wrong. Repointing the archive produced
    `../../milestone-1-core/closing-notes.md` in a file that *is* inside `milestone-1-core/` — it
    resolves, and it says "go out to `docs/` and come back" about the file next door. The same pass
    gave a phase plan `../phase-4-lmstudio-parity/notes.md`, meaning `notes.md`. Both survived the
    broken-link check because neither is broken.

    Only paths used as *relative* addresses are compared. `docs/status.md` cited from `docs/README.md`
    is resolved from the repository root, and rewriting it to `status.md` would be wrong — so the
    test is whether the path resolves against the citing file's own directory.
    """
    target = from_file.parent / candidate
    if not target.exists():
        return None  # rooted, or broken; neither is this check's business
    shortest = os.path.relpath(target.resolve(), from_file.parent.resolve())
    if candidate.endswith("/") and not shortest.endswith("/"):
        shortest += "/"
    return shortest if len(shortest) < len(candidate) else None


def check(paths: list[Path], root: Path) -> int:
    files = sorted({p for t in paths for p in ([t] if t.is_file() else t.rglob("*.md"))})
    broken: list[str] = []
    long_way: list[str] = []
    for f in files:
        for number, line in enumerate(f.read_text().splitlines(), start=1):
            for candidate in sorted(candidates(line)):
                if not is_addressed(candidate, root):
                    continue
                where = f"{f.relative_to(root)}:{number}"
                if not resolves(candidate, f, root):
                    broken.append(f"{where}  {candidate}")
                elif (shorter := roundabout(candidate, f)) is not None:
                    long_way.append(f"{where}  {candidate}  →  {shorter}")
    for line in broken:
        print(line)
    if long_way:
        print("\nresolves, but the long way round:")
        for line in long_way:
            print(line)
    print(
        f"\n{len(files)} files, {len(broken)} broken, {len(long_way)} roundabout",
        file=sys.stderr,
    )
    return len(broken) + len(long_way)


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
