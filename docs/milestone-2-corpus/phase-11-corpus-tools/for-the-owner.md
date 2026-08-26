# Phase 11 — for the owner

**Read this after the phase is finished.** It is the one document in this folder written *to a person*
rather than to a future session: questions that need you, things I would do differently, and ideas that
are not Phase 11's business. **Nothing here blocks the build** — anything that did was asked in the
session instead.

**No tier, no rule, no template.** Started 2026-08-26 on the owner's suggestion. If it turns out to
earn a convention, that is a later decision and this file is the evidence for it.

**Three kinds of entry**, marked so you can skim: **`ASK`** needs an answer only you can give,
**`IDEA`** is a suggestion you can ignore, **`REGRET`** is something I would do differently and am
telling you rather than quietly fixing.

---

## ASK · Does `git --version` prompt? — one observation, opened 2026-08-26

**Anthropic documents that the built-in read-only set includes *"read-only forms of `git`"*. This
branch measured the opposite on 2026-08-25** — seven probes, the decisive one being that `git --version`
prompted.

**Checked first:** there is no blanket `ask` or `deny` on git in the tracked settings, so the documented
way of forcing a prompt on a read-only command is not what happened here. Two readings survive and
**reading cannot separate them**: the clause postdates your measurement, or `git --version` is not a
*read-only form* to the classifier.

**I cannot run this check.** A denial reaches me as a tool error; **an approval is invisible**. Silence
and approved-after-prompt are the same observation from inside the session. **Auto mode removes the
prompt entirely**, so a probe taken with it on measures nothing.

> **With auto mode off, run `git --version`.** A prompt means your 2026-08-25 measurement stands.
> Silence means the ~20 git allow entries in the tracked settings are fossils that `IDM-002`'s pruning
> rule says to remove.

**No rule was removed on the strength of this.** Deleting twenty entries on an unverified reading is
the expensive direction of the mistake. Recorded unresolved in `../../method/IDM-002-harness-configuration.md`.

## IDEA · `BUG-001` can be strengthened from one paired control to 93 of 94 — opened 2026-08-26

Task 7's frozen slice settles something `BUG-001` currently argues from a single pair:

| `/v1/messages` | ok | 429 |
|---|---|---|
| **streamed** | **807** | **0** |
| **non-streamed** | **1** | **93** |

**Every 429 in the corpus is a non-streamed `POST /v1/messages`.** Across all four days, 8 of 9
sessions, both `claude-opus-5` and `claude-sonnet-5` — so it is not a burst, not one afternoon, and not
model-specific. **And it is not "non-streamed traffic" in general:** `count_tokens` is also non-streamed
and all **66** succeeded. The failure is specific to one request shape, which is exactly what `BUG-001`
claims.

**What it does not show, and the distinction matters for your hypothesis.** You suspect the router
causes the rate-limit errors. **Every row in this corpus went through the router, so there is no
control** — the slice cannot separate "the router causes it" from "this request shape gets 429'd
wherever it comes from". **And a session run direct, bypassing the router, produces no rows at all**, so
the control you would need never appears that way. The measurement that would settle it is a
non-streamed `/v1/messages` sent **without** the router, paired with one through it.

**Deliberately not done here.** `docs/bugs/` merged on its own branch; work belonging elsewhere does not
go on a phase branch. It wants a `docs/` or `fix/` branch of its own, and the numbers above are already
committed in `evidence/` for it to cite.

## IDEA · Four of the five sentinels have never been observed — opened 2026-08-26

Only `too_large` appears in the corpus, on **45 rows**. `dropped`, `absent` and `error` have never
occurred, and `none` never appears as a *response* ref. **`absent` does not even appear on the nine
router-authored `/api/hello` rows**, which carry real digests.

**Why it is worth your attention rather than mine:** the extractor must handle all five, and four of
them will only ever be exercised by **synthetic** test data. That is not a defect — it is a fact about
how much of that path real traffic can confirm, and it is the kind of thing that reads as coverage
later. If you ever want it exercised for real, `dropped` and `too_large` are both reachable by
tightening `corpus.body_max_bytes` and the queue bound for one driven session.

## ASK · Does a bare clone break Anthropic's settings-resolution rule? — opened 2026-08-26

**Documented, since v2.1.211:** an auto-saved approval lands in `.claude/settings.local.json` *"at the
root of the git repository, **resolved through worktrees to the main checkout**"*.

**Observed here at v2.1.231: it does not.** All three worktrees hold their own `settings.local.json`
with **different contents** — this branch's written 2026-08-26, `main`'s untouched since 2026-08-24.

**Hypothesis, and it is only that: a bare clone has no main checkout to resolve to**, so the fallback is
the worktree. **The check is one approval**: grant a new one here and see which file grows.

**Why it matters beyond curiosity.** `IDM-002` wants the local half kept empty so it cannot silently
contradict the tracked half. If approvals accumulate **per worktree**, that job has to be done three
times instead of once — and the one this branch emptied on 2026-08-25 had already refilled with six
rules by 2026-08-26.

*Careful reading required: this is the **local** half. The **tracked** half's session-caching is settled
and measured, and the two claims are one word apart. `IDM-001`'s worktree section had to be amended
after it was written for exactly this reason.*

## ASK · `Bash(uvx ruff *)` is still nobody's — raised repeatedly, opened before this phase

It permits an **unpinned** ruff, which `CLAUDE.md` says never to invoke as a side effect, and
`make lint` cannot catch a line-length regression because `E501` is not in ruff's default set. **It is
in two places**: this branch's tracked `settings.json` and `main`'s `settings.local.json`.

**It has been raised in every recent phase and belongs to nobody.** Either it is accepted with a reason
written down, or it narrows to `Bash(uvx ruff@0.16.1 *)`. **Both are one-line changes; the current state
is the only one that costs anything**, because it is a standing invitation to bump a pin invisibly.

## REGRET · Task 2 grew from two files to eight, and I asked rather than assumed — opened 2026-08-26

`plan.md`'s Task 2 named two files. The dead mtime justification in one of them turned out to have
**eight homes across seven files** — `corpus.py` carries it twice — of which **seven sit outside the
task and two of those are in `src/`**. **I stopped and asked rather than widening the task**, and you
said fix all seven, which was right; the commit is separate from Task 2 so the boundary stays visible.

*The count itself drifted while being written down — this entry and `notes.md` said "seven homes" and
"two files to nine" in the same afternoon. **Reconciled at the session's close, and recorded rather
than silently corrected**, because a count going stale inside the document describing a count going
stale is this repository's signature failure and it should keep being visible.*

**Recording it because the instinct could have gone the other way and cost you.** Position 20 is *"step
by step, not leaps by leaps"*, and a task that quietly grows from two files to eight is exactly what that
position rejects. **If you would rather I just fixed obvious verbatim-duplicate corrections in future
without asking, say so** — the cost of asking is a round trip, the cost of not asking is a commit you
did not sanction. I do not think either default is obviously right, which is why it is here.

## IDEA · The failure mode that got past a full forward review — opened 2026-08-26

**Task 5 was recorded as executed and half of it had not been done.** Its settings work ran on
2026-08-24; the `IDM-002` amendment its *title* names was never written. Found only because Task 4 went
to cite it and there was nothing there.

**`IDM-004`'s review could not have caught it.** A review checks what a document **says**, and the
document said something true — about one half of a two-part task. **The plan's `Placeholders` item
counted three executed tasks for two days and the count was wrong.**

**A cheap check if you want one:** a task claiming early execution must name **every** artefact it
produced, and the closing register check confirms each exists. That is `IDM-008`'s instrument pointed at
task records instead of at names — it would have caught this in one grep. **Not proposed as a rule
here**, because one instance is not a pattern and this file is not where rules get made.

## IDEA · `make lint`'s blindness to line width bit inside one session — opened 2026-08-26

**`CLAUDE.md` warns that `make lint` cannot see column width**, because `E501` is not in ruff's default
rule set while `pyproject.toml` sets `line-length = 100`. **It stopped being a theoretical warning
today: a 101-character line went into task 8's commit**, passed `make lint`, and was found only because
I checked by hand afterwards.

**The fix is bounded and I measured it rather than guessing:**

```
uvx ruff@0.16.1 check --select E501 src tests   →   23 errors, 9 files
```

**Nine files, twenty-three lines, and every one I looked at is prose in a docstring** — rewraps, not
code changes. None of them is a deliberate exception; the one that *looked* like it (`test_recording.py`
saying *"the rule that outranks every column in the file"*) is a sentence about telemetry, not about
formatting.

**Not done, because it is a tooling change and `../../method/IDM-003-development-tooling.md` owns
those** — and because `CLAUDE.md` says nothing bumps or extends the linter as a side effect. **It is
one line in the `Makefile` plus twenty-three rewraps**, and the argument for it is that the warning in
`CLAUDE.md` currently asks every session to do by hand what the tool would do for free — and this
session, holding that warning, still missed one.

## REGRET · I checked width on the diff for one commit and not the next — opened 2026-08-26

For task 2 I checked added-line width deliberately and reported zero. **For task 8 I did not, and that
is the commit with the over-width line in it.** The check was treated as a one-off rather than as
something the absent lint rule makes necessary every time.

**Recorded because the fix is not "remember harder"** — it is either the entry above, or a habit, and
between those two the entry above is the one that survives a session ending.
