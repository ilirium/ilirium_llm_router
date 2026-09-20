# `wiki/` — what we researched about somebody else's software

**Proposed 2026-08-19. This tier is new and its boundary with `reference/` is the whole risk**, so the
test comes before the index.

## The test

**Who is the subject?**

| The page is about… | Tier |
|---|---|
| **This router**, or a backend it dispatches to — what it does, what we measured, what we decided | `reference/` |
| **A library, protocol or tool we are built on** — what it does, established by reading it | `wiki/` |

A second question that resolves most of the rest: **would this page be just as useful to a different
project using the same library?** If yes, it is `wiki/`. `reference/backend-lmstudio.md` fails that
test — it is full of *our* probes, *our* context sizes, *our* router's interaction — and that is why
it is not here despite also being about third-party software.

**When two answers are still defensible, `../README.md`'s rule 4 applies unchanged:** put it in the
bigger file and leave a heading. **A new tier makes every filing question harder, and that cost is
paid once per document forever** — so the bar for a page here is that somebody would otherwise
re-derive it.

## What a page owes

- **A nameable trigger in its first line** — the moment you would open *it* rather than its neighbour.
  Same rule as `reference/`.
- **Its sources, linked.** This tier exists because somebody did the reading; a page without the
  reading list is a page nobody can check or extend.
- **Version pins for anything version-shaped**, and a section saying what expires. Upstream software
  moves; a page that does not say when it was true becomes a confident wrong answer.
- **How each claim was established**, when it was not simply read from the upstream documentation.
  *"Read the shipped binary"* and *"read the docs"* are different evidence and the reader should be
  able to tell which they are getting.

## What a page must not be

**A second copy of a phase note.** `../README.md`'s one-home-per-fact rule applies here as everywhere,
and the split is:

- **The wiki holds the mechanism** — how the thing works, for anyone who needs it next.
- **The phase note holds the episode** — when we looked, why, what we expected, what it cost.

So a wiki page may cite a phase note for provenance, and a phase note may cite the wiki instead of
re-explaining. Neither restates the other.

**And it is not a tutorial.** Upstream documentation is better at that and is linked. A page here
earns its place by answering something upstream does not answer, answers confusingly, or answers
differently from what the installed version actually does.

## Index

| Page | Open it when |
|---|---|
| `background-work-in-fastapi.md` | You are about to move work off the request path — a periodic job, a slow write, a compression — and need to know which of the four mechanisms fits, and which one quietly stalls the server |
| `zstandard-and-libzstd.md` | You need to know whether `zstandard` blocks the interpreter, which backend is running, what its dictionary trainer does with a parameter you left out, or how a blob finds its dictionary again |
| `reading-a-c-extension-binary.md` | You need to know what a compiled Python extension really does — does it release the GIL, does it call what you think — and the wheel ships only a `.so` |
| `claude-code-auto-mode.md` | A session is burning context on tool results, or you want to change **how** Claude edits files rather than what it may do — and need to know that auto mode's working-style instruction is undocumented and has no settings key |
| `claude-md-scopes-and-precedence.md` | You are about to put a rule in a `CLAUDE.md` and expect it to win — over another `CLAUDE.md`, a setting, or something in the system prompt — and need to know that the scopes **concatenate rather than override**, and that the whole mechanism is context rather than enforcement |
| `claude-code-first-party-gate.md` | You are putting a **proxy in front of Claude Code** — and need to know that ***the page's central claim is IN DOUBT as of 2026-09-20 and carries a banner saying why*** (the runs behind it also varied `CLAUDE_CODE_ATTRIBUTION_HEADER`, which this repository's own `README.md` prescribes), that it may withhold things from a custom `ANTHROPIC_BASE_URL`, that the one everybody hunts for is a **body field rather than a header**, that the internal override restores only part of it, and that a first-party client **gzips some request bodies** |
| `claude-code-context-budget.md` | `/context` reports a large share under one category and you want to know whether it is waste, an instruction you configured, or the price of a repository that writes everything down |
