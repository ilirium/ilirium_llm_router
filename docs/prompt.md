# The next session's prompt

*The one file in `docs/` allowed to go stale, per `README.md` — which is why it is rewritten at each
handoff rather than left. **Replaced 2026-09-22**, at Phase 14's merge. Whatever comes next replaces
it again.*

---

**Phase 14 merged 2026-09-22 at `8afdaa1`. Nothing is in flight.** Work in `main`:
`/Users/ilirium/Projects/local/ilirium_llm_router/main`. *No phase is open, so there is no phase
worktree to start in.*

***The version is 0.2.0 and `../CHANGELOG.md` is new.*** *It is the first bump the project has ever
had — `0.1.0` was set at Phase 0 and carried the body store, the tools and the installer without
moving.*

**The first decision of the next session is which phase to open, and that is the owner's.**

## Read this first, because Phase 14 ended in an unusual shape

***The phase merged. The phase's own branch did not.*** **Two branches share the slug**, and telling
them apart matters:

| `feat/phase-14-rate-limit-headers` | what shipped | merged at `8afdaa1` |
|---|---|---|
| **`unmerged/phase-14-rate-limit-headers`** | the investigation | ***never merges, never delete it*** |

***`milestone-2-corpus/phase-14-rate-limit-headers/README.md` is the summary and the pointer.***
**`IDM-001` has the rules** — *a phase may close without merging; the branch is declared in
`branch-index.py`'s `NOT_IN_FLIGHT`, takes the `unmerged/` prefix, and `main` gets a summary saying
what crossed over.*

***Three things about that branch a session will otherwise get wrong:***

- ***Its worktree holds the ONLY copy of the 2026-09-18 to `-21` corpora and the id mapping***, both
  in gitignored `logs/`. **Removing the worktree destroys them.**
- ***Every session and request id on it is SYNTHETIC.*** *History rewritten 2026-09-22; the
  originals are gone from this machine.* **`git-refs-and-the-history-rewrite.md`** *in that phase
  folder explains the mechanics, and its command blocks name the branch by its pre-rename name on
  purpose.*
- ***Its own `status.md` and `prompt.md` are an archive's copies.*** **This file and `main`'s
  `status.md` are the live ones.**

## What Phase 14 settled, in one paragraph

***`BUG-001` is resolved and the cause was this repository's own `README.md`.***
**`CLAUDE_CODE_ATTRIBUTION_HEADER=0`** *suppresses an attribution block Claude Code sends in its
request body, and Anthropic refuses a non-streamed `/v1/messages` that arrives without one.* **The
router was never at fault.** *Do not put that variable back into any command block; five documents
carried it and Phase 1's evidence is annotated rather than edited.*

## What is next, and none of it is chosen

**`status.md`'s "What is next" is the list.** *Three items, and the owner picks.*

***Two things Phase 14 left open by name:***

- ***No run has produced a BLOCKED verdict from auto mode's classifier through the router.***
  **Every classifier call measured came back at stage 1**, so *the allow path is demonstrated and
  the block path is assumed.* **`BUG-000`.** *It needs no adversarial content — only a command auto
  mode declines to run.*
- ***Where the rate-limit headers durably live.*** **They reach `router.log` and nowhere else** —
  `BKL-0043`, *and one of its three options needs settled position 6 overturned, which is the
  owner's alone.*

**Also open:** *`BKL-0040` (the dropped `content-length`, a latent HTTP defect), `BKL-0041`,
`BKL-0042`, `BKL-0044`, `BKL-0017`, `BKL-0007`, `EPD-001` and `EPD-002`.*

## Five things a session will still get wrong here

- ***`link-check.py`'s count is a property of the worktree.*** **92 in `main`**; *the phase-14
  archive reads 112.* **Compare within one tree or not at all.**
- ***`branch-index.py --write` used to delete a row it must not delete.*** **Fixed 2026-09-22** —
  *a branch that is a worktree pin or an archive is now **declared** in `NOT_IN_FLIGHT`, because a
  pin fast-forwarded to the trunk and a branch cut from the trunk's head are topologically
  identical.* **`BKL-0041` is the general guard and is not done.**
- ***A fresh worktree has neither a venv nor `logs/`.*** *`uv run python` does not work in a new
  tree until one is made there.*
- ***The backlog's ids ascend within a SECTION, not across the file.*** *Amended 2026-09-19;
  before it, there was exactly one legal position for a new item and it was under "Not on this
  list, and why".*
- ***There is no reflog anywhere in this repository.*** **Expired and pruned 2026-09-22** to finish
  the sanitization, *so `git reset --hard` has no undo until new entries accumulate.*

## Push state, measured rather than reported

***`git ls-remote origin` reads the remote and writes nothing.*** **This clone has no
remote-tracking refs because `origin` carries no fetch refspec** — *`git branch -r` being empty is
not evidence about what is pushed, and `status.md` recorded the opposite for two weeks.*

**As of 2026-09-22 the owner deleted the old remote branch and pushed the renamed one.** *A session
that needs the current state runs `ls-remote` rather than reading this line.*

## The working agreement still applies

`CLAUDE.md`, in full. **Two earned their keep again in Phase 14:**

***Ask before inferring.*** *The owner supplied what no log could — the environment variable, and
then the confirmation that both halves of the A/B carried it.* **Without that second answer the pair
was not a controlled experiment.**

***Exercise it before committing.*** *The test run caught a ported test that was named for one
feature and asserted on another.* **Reading the name would not have found it.**
