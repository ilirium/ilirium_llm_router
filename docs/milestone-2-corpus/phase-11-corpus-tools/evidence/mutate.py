#!/usr/bin/env python3
"""Systematic mutation testing of the converter — Phase 11 Task 23.

**The point is the survivors.** A mutation that the suite kills tells you almost nothing; a mutation
that **lives** is either a missing test or a dead line, and the task is to find out which. This is
why the targeted mutations run alongside each task are *not* this: every one of those was chosen
because it was expected to fail, so by construction none of them could survive.

**Hand-rolled rather than a dependency, on the owner's decision of 2026-08-28.** A tool
(`mutmut`, `cosmic-ray`) is parked in `../../../backlog.md` under "Instruments and housekeeping",
pointed at `IDM-003`, which owns tooling decisions. *The honest weakness of this harness is written
into that entry: it mutates what its author thought to mutate, which is the same blind spot the
tests already have.*

    uv run python docs/milestone-2-corpus/phase-11-corpus-tools/evidence/mutate.py
    uv run python .../mutate.py --list        # count the sites, run nothing

Each mutation is applied to one file, the suite is run with `-x` so a kill is cheap, and the file is
restored afterwards.

**`try/finally` was not enough and this is written down because it nearly cost the module.** The
first run was killed by a timeout partway through, and `finally` does not run on `SIGTERM` — so
`transcript.py` was left as the `ast.unparse` output: behaviour identical, **every comment gone, 256
lines deleted, and the suite passing 427/427.** Nothing failed. It was caught by `git status`.

**So the restore is now belt, braces and a third thing.** A `.mutation-backup` sidecar is written
*before* the mutation and removed only on a clean exit; `SIGTERM` and `SIGINT` are handled and
restore; and **a run that finds a stale sidecar restores from it and refuses to start**, because a
sidecar on disk means the last run did not finish and the tree cannot be trusted yet.

*`--start` and `--count` exist for the same reason: a sweep long enough to hit a timeout is a sweep
that should be run in slices.*
"""

from __future__ import annotations

import argparse
import ast
import signal
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]

BACKUP_SUFFIX = ".mutation-backup"

# **The converter**, which is what Task 23 names — not the whole package. `extract.py` is selection
# and layout and has its own targeted mutations; this is the part that decides what a transcript says.
TARGETS = ("transcript.py", "jsonl.py")

COMPARE = {
    ast.Eq: ast.NotEq, ast.NotEq: ast.Eq,
    ast.Lt: ast.GtE, ast.GtE: ast.Lt,
    ast.Gt: ast.LtE, ast.LtE: ast.Gt,
    ast.In: ast.NotIn, ast.NotIn: ast.In,
    ast.Is: ast.IsNot, ast.IsNot: ast.Is,
}
ARITH = {ast.Add: ast.Sub, ast.Sub: ast.Add}


@dataclass
class Mutant:
    path: Path
    line: int
    description: str
    source: str


def docstring_nodes(tree: ast.AST) -> set[int]:
    """Every docstring's `Constant` node, by id, so mutating prose is not counted as a mutation."""
    out: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Module | ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
            first = node.body[0] if node.body else None
            if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant):
                out.add(id(first.value))
    return out


def mutants_for(path: Path) -> list[Mutant]:
    original = path.read_text(encoding="utf-8")
    tree = ast.parse(original)
    skip = docstring_nodes(tree)
    found: list[Mutant] = []

    # One pass per site: re-parse each time so exactly one node differs from the original.
    for index, target in enumerate(ast.walk(tree)):
        if isinstance(target, ast.Compare) and target.ops and type(target.ops[0]) in COMPARE:
            found.append(_build(path, original, index, "compare"))
        elif isinstance(target, ast.BoolOp):
            found.append(_build(path, original, index, "boolop"))
        elif isinstance(target, ast.UnaryOp) and isinstance(target.op, ast.Not):
            found.append(_build(path, original, index, "not"))
        elif isinstance(target, ast.BinOp) and type(target.op) in ARITH:
            found.append(_build(path, original, index, "arith"))
        elif isinstance(target, ast.Constant) and id(target) not in skip:
            if isinstance(target.value, bool):
                found.append(_build(path, original, index, "bool"))
            elif isinstance(target.value, int):
                found.append(_build(path, original, index, "int"))
            elif isinstance(target.value, str) and target.value:
                found.append(_build(path, original, index, "str"))
    return [m for m in found if m is not None and m.source != original]


def _build(path: Path, original: str, index: int, kind: str) -> Mutant | None:
    """Re-parse, walk to the same index, apply one change, unparse."""
    tree = ast.parse(original)
    node = list(ast.walk(tree))[index]
    line = getattr(node, "lineno", 0)
    if kind == "compare":
        was = type(node.ops[0]).__name__
        node.ops[0] = COMPARE[type(node.ops[0])]()
        description = f"{was} -> {type(node.ops[0]).__name__}"
    elif kind == "boolop":
        was = type(node.op).__name__
        node.op = ast.Or() if isinstance(node.op, ast.And) else ast.And()
        description = f"{was} -> {type(node.op).__name__}"
    elif kind == "not":
        return _replace_not(path, original, index, line)
    elif kind == "arith":
        was = type(node.op).__name__
        node.op = ARITH[type(node.op)]()
        description = f"{was} -> {type(node.op).__name__}"
    elif kind == "bool":
        description = f"{node.value} -> {not node.value}"
        node.value = not node.value
    elif kind == "int":
        description = f"{node.value} -> {node.value + 1}"
        node.value = node.value + 1
    else:
        shown = node.value if len(node.value) < 24 else node.value[:21] + "..."
        description = f"{shown!r} -> ''"
        node.value = ""
    try:
        source = ast.unparse(ast.fix_missing_locations(tree))
    except Exception:
        return None
    return Mutant(path, line, f"{kind}: {description}", source)


def _replace_not(path: Path, original: str, index: int, line: int) -> Mutant | None:
    """`not X` -> `X`. Done by rebuilding the parent, which `ast.unparse` handles for us."""
    tree = ast.parse(original)
    node = list(ast.walk(tree))[index]
    for parent in ast.walk(tree):
        for field, value in ast.iter_fields(parent):
            if value is node:
                setattr(parent, field, node.operand)
            elif isinstance(value, list):
                for position, item in enumerate(value):
                    if item is node:
                        value[position] = node.operand
    try:
        source = ast.unparse(ast.fix_missing_locations(tree))
    except Exception:
        return None
    return Mutant(path, line, "not: `not X` -> `X`", source)


def run_suite() -> bool:
    """True when the suite passes. `-x` so a killed mutant costs one failing test, not 427."""
    finished = subprocess.run(
        [sys.executable, "-m", "pytest", "-x", "-q", "--no-header", "-p", "no:cacheprovider"],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    return finished.returncode == 0


def _recover() -> bool:
    """Restore from any stale sidecar, and refuse to start if one was found.

    **A sidecar on disk means the previous run did not finish.** Restoring and carrying on would
    hide that; the run stops so a person can confirm the tree before another sweep writes over it.
    """
    stale = sorted((ROOT / "src/ilirium_llm_router").glob(f"*{BACKUP_SUFFIX}"))
    if not stale:
        return True
    for backup in stale:
        target = backup.with_name(backup.name[: -len(BACKUP_SUFFIX)])
        target.write_text(backup.read_text(encoding="utf-8"), encoding="utf-8")
        backup.unlink()
        print(f"restored {target.name} from a stale backup — the last run did not finish")
    print("refusing to start. Check `git status`, then run again.")
    return False


def _install_handlers(path: Path, backup: Path) -> None:
    """Restore on `SIGTERM`/`SIGINT`, which `finally` does not cover."""

    def restore(signum: int, frame: object) -> None:
        path.write_text(backup.read_text(encoding="utf-8"), encoding="utf-8")
        backup.unlink(missing_ok=True)
        print(f"\ninterrupted by signal {signum}; {path.name} restored")
        raise SystemExit(130)

    for received in (signal.SIGTERM, signal.SIGINT):
        signal.signal(received, restore)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true", help="count the sites and run nothing")
    parser.add_argument("--start", type=int, default=0, help="first mutant, for running in slices")
    parser.add_argument("--count", type=int, help="how many to run from --start")
    args = parser.parse_args()

    if not _recover():
        return 1

    mutants: list[Mutant] = []
    for name in TARGETS:
        mutants.extend(mutants_for(ROOT / "src/ilirium_llm_router" / name))

    total = len(mutants)
    end = total if args.count is None else min(total, args.start + args.count)
    window = mutants[args.start:end]
    print(f"{total} mutant(s) across {', '.join(TARGETS)}; "
          f"running {args.start}..{end - 1} ({len(window)})")
    if args.list:
        return 0
    mutants = window

    print("baseline: ", end="", flush=True)
    if not run_suite():
        print("FAILING — fix the suite before mutating it")
        return 1
    print("green")

    survivors: list[Mutant] = []
    for number, mutant in enumerate(mutants, 1):
        original = mutant.path.read_text(encoding="utf-8")
        backup = mutant.path.with_name(mutant.path.name + BACKUP_SUFFIX)
        backup.write_text(original, encoding="utf-8")
        _install_handlers(mutant.path, backup)
        try:
            mutant.path.write_text(mutant.source, encoding="utf-8")
            alive = run_suite()
        finally:
            mutant.path.write_text(original, encoding="utf-8")
            backup.unlink(missing_ok=True)
        if alive:
            survivors.append(mutant)
        print(f"\r{args.start + number}/{args.start + len(mutants)}  "
              f"survivors: {len(survivors)}   ", end="", flush=True)

    print(f"\n\n{len(mutants)} mutant(s), {len(mutants) - len(survivors)} killed, "
          f"{len(survivors)} survived")
    for mutant in survivors:
        print(f"  SURVIVED  {mutant.path.name}:{mutant.line}  {mutant.description}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
