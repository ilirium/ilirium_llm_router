# Phase 6 — review the basement

Written 2026-08-07, with all five phases merged and the tree clean. The first phase whose subject is
the project itself rather than a capability.

## Why

Each phase was verified in its own terms, but nobody has read the whole thing at once. This project
has a documented habit of drift, and it has changed shape three times:

- **Phase 3** found four of its five work items already *built* by Phase 2.
- **Phase 4** found a third of its plan already *measured* by Phase 2's frozen session.
- **Phase 5** found work already **misdescribed** — two of the three timeout options recorded across
  four documents did not exist as stated, and the property those documents said the 600 s number
  bought had never been true.

The third variant is why this phase exists. The failure mode is not broken code: the tests pass and
the router has carried real sessions. It is **claims written once and quoted forward**, and code
that accumulated as each phase added a column or a mode without anyone looking back at the whole.

## Shape: three acts

1. **Review** — read everything, write `phase-6-notes.md`, change nothing.
2. **Gate** — the findings are presented ranked; a person picks what gets done.
3. **Fix and verify** — refactor only what was picked, against a baseline captured beforehand.

Act 3 does not begin without Act 2. If the findings are thin, Act 3 is allowed to be empty and the
phase still ends properly; a negative result is a result.

## Scope

**In:** all of `src/`, all of `tests/`, `config.yaml`, `.env.example`, `Makefile`,
`pyproject.toml`, `uv.lock`, `README.md`, `CLAUDE.md`, and every `docs/*.md` except the EPDs.

**Out:** `docs/epd/` — all four, unread and unevaluated, since they propose work not yet done. The
one mechanical exception is `CLAUDE.md`'s EPD index table: if it misstates an EPD's *status*, that
is a docs-accuracy finding about `CLAUDE.md`.

**Also out:** new features, the per-backend auth header name, and the `max_tokens: 1` warmup-probe
question — all decisions waiting on a person in `outstanding-work.md`. Phase 5 warned about settling
such a question by accident while editing nearby code; this phase inherits that warning.

## The five passes

1. **Read the code end to end**, in dependency order, for behaviour rather than style.
2. **Duplication, bloat, AI slop** — kept separate, so a style opinion is never filed as a bug.
   Long comments are classified as *carries a fact*, *duplicates `CLAUDE.md`*, or *restates the code
   below it*, and only the third group is proposed for deletion.
3. **Static analysis** — a type check with `ty`, pinned and fetched through `uvx` like ruff and
   **not** added to `pyproject.toml`; plus an AST inventory of every module-level name defined
   against every name referenced.
4. **Audit every "done" claim** — each assertion of *built* / *fixed* / *verified* / *measured*
   checked against the code, the frozen artefacts, or the test suite, and graded **holds** /
   **holds but overstated** / **contradicted** / **unverifiable from what is committed**.
5. **Repo hygiene** — declared versus imported dependencies, config against what the loader accepts,
   tracked artefacts, Makefile help text.

Plus a sixth, added at the gate-setting conversation: **the documents as artefacts**, not only as
claims — `CLAUDE.md`'s size, and whole documents that may be superseded.

## Verification

Static plus the test suite plus the router driven for real against **local stubs only**. No LM
Studio, no Anthropic, no GUI setting, no money. A finding that needs live traffic to settle is
recorded as *unverifiable without a live run* rather than guessed at.

| | |
|---|---|
| `make test` | the full suite |
| `make lint` | ruff at the pinned 0.16.1 |
| `uvx ruff@0.16.1 format --check` | is the committed tree already formatted — check mode, never rewriting |
| `uvx ty@0.0.14 check` | type findings, before against after |
| `make check` | config validation |
| AST comparison | per file, for every commit claiming to be cosmetic |
| the router, live | started for real against `dying_backend.py` and two purpose-built stubs |

## Act 3 discipline

Borrowed from `d1def4f`, the formatting-bump precedent:

- **One commit per finding**, so a bad fix reverts alone.
- **Behaviour and cosmetics never share a commit.**
- **AST equivalence is the test for anything claimed cosmetic** — identical AST before and after is
  the proof, and a difference means the commit was mislabelled.

## The phase ends when

`phase-6-notes.md` records both halves — what was found and what was done — the suite is green, the
router has been driven, and `CLAUDE.md` and `handoff.md` are corrected wherever the audit found them
wrong. That last item is the one most likely to be forgotten, and it is the entire reason this phase
is worth running.
