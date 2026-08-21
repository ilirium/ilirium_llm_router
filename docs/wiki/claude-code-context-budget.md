# Where a Claude Code session's context actually goes

**Read this when `/context` reports a large share under one category — most often Bash results — and
you want to know whether that is waste, an instruction you configured, or the unavoidable cost of a
repository that writes everything down.** The suggestion `/context` prints names a real cost and
attributes it to the wrong cause about half the time.

**Established 2026-08-20** against **Claude Code v2.1.228**, from the upstream context-window and
memory documentation plus **one measured session in this repository** — Phase 10, Group D, a 1M-token
window taken to 50%.

---

## The question this page answers

`/context` printed:

> ⚠ **Bash results using 187.5k tokens (19%)** → save ~93.8k
> Pipe output through head, tail, or grep to reduce result size. Avoid `cat` on large files — use
> Read with offset/limit instead.

**The advice is correct and incomplete.** It names three habits and misses the largest single cause,
which is not a habit at all.

## What loads before you type anything

Startup context is small and mostly not yours to change. From the upstream simulation, with
indicative sizes:

| Loaded automatically | Roughly |
|---|---|
| System prompt | ~4,200 tokens |
| Auto memory `MEMORY.md` — **first 200 lines or 25 KB, whichever comes first** | ~700 |
| Environment info: cwd, platform, shell, OS, git status and recent commits | ~300 |
| MCP tool **names**, schemas deferred until needed | ~120 |
| `CLAUDE.md` files, **loaded in full however long they are** | yours |

**Measured in this repository:** system prompt 5.5k, system tools 12.3k, deferred tool schemas 29.6k,
memory files 5.7k, skills 2.3k — **~55k before the first prompt**, of which the project `CLAUDE.md`
is 4.7k. That is 5.5% of a 1M window and is not where a session's context goes.

## Where it actually goes, in descending order

**1 — Tool results, and the biggest one is not in the tip.**

**Editing files through Bash makes the harness echo the modified file back.** A `python - <<'PY'`
heredoc or a `sed -i` returns a *"this file was modified"* notice carrying a large excerpt — often
100+ lines. The `Edit` tool returns one line. **Measured here: ~10 such edits across five source
files, and the echoes were the largest avoidable share of that 187.5k.**

**This is not a habit — it is an instruction.** Auto mode asks Claude to edit through the shell;
`claude-code-auto-mode.md` covers it, including that it is undocumented and has no settings key.
**So the `/context` tip tells you to stop doing something the harness told the model to do.**

**2 — Reading whole files when a section would do.** `cat` on a 37 KB source file spills to a
persisted tool-result file. A 200-line `sed` sweep over a 1,600-line plan reads far more than the task
needs.

**3 — Orientation reading, which is mostly not waste.** This repository's `plan.md` is ~1,600 lines
and its `notes.md` ~3,000, both growing every session, and `CLAUDE.md` instructs reading several
before touching the relevant code. **That is the deliberate cost of a repository whose whole method is
writing things down** — the fix is reading it *by section*, not reading less of it.

**4 — Everything the conversation accumulates**: file reads, diffs, test output, web fetches.

## What to do, in the order worth doing it

| | Lever | Worth |
|---|---|---|
| 1 | **Stop editing through Bash heredocs** — use `Edit`/`Write` | The largest single item, and it is a configuration question rather than discipline. See `claude-md-scopes-and-precedence.md` for how to make that stick, and why it is harder than it looks |
| 2 | **Grep for structure before reading** — `grep -n '^## ' <file>`, then read the sections you need | Cheap, immediate, applies in every mode |
| 3 | **Pipe long output** — `tail`, `head`, `grep -c`, `wc -l` | What the tip says. Real, but smaller than 1 and 2 |
| 4 | **Split documents that every session must read** | Structural. Only worth it when a file is read in full every session and most of it is never needed |
| 5 | **Start a fresh session at a natural boundary** | The one that always works. Context spent is not context wasted if the work is committed and a handoff exists |

**Lever 5 is not a failure mode.** A session that has finished a task group, committed, and written a
handoff has *converted* its context into durable artefacts. Starting fresh then costs nothing but the
re-orientation the handoff exists to make cheap.

## Reading `/context` without over-reading it

- **The percentages are of the window, not of what you can control.** A 19% Bash figure in a
  50%-used window is 38% of what the session actually spent.
- **"Free space" is not headroom to aim at.** Auto-compaction runs before the window fills, at a
  threshold that depends on model and configuration.
- **Deferred tool schemas count.** 29.6k here for MCP and system tools that were listed but never
  loaded — real, and not something a working habit changes.
- **Memory files are capped and `CLAUDE.md` is not.** `MEMORY.md` loads its first 200 lines or 25 KB;
  a `CLAUDE.md` of any length loads whole. The upstream guidance is under 200 lines *"for adherence"*,
  not because anything truncates it.

## What survives if you do start fresh

**Project-root `CLAUDE.md` survives compaction** — re-read from disk and re-injected. **Nested
`CLAUDE.md` files and path-scoped rules do not**; they reload when a matching file is next read. **An
instruction given only in conversation does not survive at all**, which is the argument for writing a
durable rule down rather than repeating it.

## Reading list

- **Explore the context window** — the interactive breakdown of what loads and when — <https://code.claude.com/docs/en/context-window>
- Reduce token usage, and compaction — <https://code.claude.com/docs/en/costs>
- Memory, for the `MEMORY.md` limits and what survives compaction — <https://code.claude.com/docs/en/memory>
- Model configuration, for auto-compact thresholds and extended context — <https://code.claude.com/docs/en/model-config>

*Upstream landing pages, chosen to outlive version numbers. **All fetched from this machine on
2026-08-20.***

## Where these claims came from, and what expires

| Claim | How it was established |
|---|---|
| Startup composition and indicative sizes | Read the context-window page's simulation, 2026-08-20 |
| `MEMORY.md` loads 200 lines / 25 KB; `CLAUDE.md` loads in full | Read the memory page |
| What survives compaction | Read the memory page |
| **Per-category figures — 187.5k Bash results at 19%, ~55k startup, 4.7k project `CLAUDE.md`** | **Measured in one session in this repository via `/context`**, Phase 10 Group D, 2026-08-20. One session on one machine; the ratios travel, the absolutes do not |
| **Heredoc edits cause a file echo where `Edit` does not** | Observed across ~10 edits in that session |

**What expires:** the version pin, the indicative startup sizes, and the wording of the `/context`
suggestion. **What does not:** that the largest avoidable cost in that session was *editing through
the shell rather than reading carelessly*, and that the tip naming three habits will not tell you
so — which is the whole reason this page exists rather than a pointer to the tip.
