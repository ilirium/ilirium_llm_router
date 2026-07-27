# Handoff

Snapshot of where the work stands. Written 2026-07-27. This is a living file — update it in place
rather than adding new dated copies, and delete it once the project has enough code to speak for
itself.

It is deliberately thin. The design lives in `CLAUDE.md`, which is loaded automatically every
session; the phased plan lives in `implementation-plan.md`; the authentication procedure lives in
`anthropic-auth-check.md`. Read those for substance. This file only records session state — where we
stopped and what happens next.

## Where the project stands

**No code has been written.** The repository contains documentation only: `README.md`, `CLAUDE.md`,
and three files in `docs/`. There is no `pyproject.toml`, no source tree, and no tests. Phase 0 of
the plan has not started.

Everything decided so far came from reading vendor documentation and reasoning about the design.
**Nothing has been executed or tested.** That distinction matters — see the caveats below.

## Git state

On branch `docs/add-claude-md`, four commits ahead of `origin/main`, nothing pushed:

- `5895359` initial CLAUDE.md
- `c9be81f` correction to CLAUDE.md
- `f7c71d4` design decisions and observability spec
- `1636024` implementation plan

Two files are uncommitted:

- `docs/anthropic-auth-check.md` — new, untracked
- `docs/implementation-plan.md` — modified, its authentication risk entry corrected and pointed at
  the new file

The branch is four commits of documentation under a name that suggests docs, and is about to grow
code. Consider merging it to `main` and starting implementation on a fresh branch.

## What we were doing when we stopped

The immediate next step is **running Test A in `anthropic-auth-check.md`** to find out what kind of
credential Claude Code puts on the wire. This was deliberately placed before Phase 0 because the
answer decides whether the router needs to hold an Anthropic API key at all, which changes what gets
built.

Once the answer is known: record it in that file's Result section, adjust the plan if key injection
turns out to be unnecessary, then begin Phase 0.

## Caveats worth carrying forward

**The documentation describes intentions, not observed behaviour.** Nothing in `CLAUDE.md` or the
plan has been validated by running anything. Treat statements about how the router will behave as
design intent until code exists to check them against.

**Claims about LM Studio come from its own documentation.** That it implements an Anthropic-compatible
`/v1/messages` is well supported. What is *not* known is how completely: LM Studio publishes no
compatibility table, so its handling of system prompts, tool results, thinking blocks, images, and
usage reporting is unverified. Phase 4 exists to find out. Do not assume passthrough is lossless
before then.

**One claim in this repository was already wrong once.** The first version of `CLAUDE.md` asserted
that a protocol translation layer between the Anthropic and OpenAI formats was needed and was the
hard part of the project. That was incorrect — LM Studio speaks the Anthropic format natively — and
was corrected in `c9be81f` after the repository owner checked the vendor documentation. The lesson
worth carrying: verify vendor capabilities against their current documentation rather than assuming,
and prefer correcting the record openly over quietly rewriting it.
