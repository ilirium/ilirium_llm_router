# Closing Phase 14 without merging it

*Written 2026-09-22, before any of it is executed, at the owner's request. **The phase's goal
changed**: the branch is no longer heading for a merge. It stays as an unmerged archive — every
experiment, every piece of evidence and every ready-to-use script kept where it is — and a small,
deliberately chosen set of things lands on `main` instead.*

***Nothing on this branch is reverted.*** *If the injection, the hosts route or the imitation work
is ever wanted, it is all here and it all still runs.*

---

## What goes to `main`, and what stays here

| To `main` | Why |
|---|---|
| **The gzip `400` fix** (`298fc55`) | ***A live defect, not experiment scaffolding.*** It is in `peek`, which every request crosses. A client that gzips its body gets a `400` blaming a `model` field that is present. First-party Claude Code gzips some bodies — that is how it was found — and the hosts route makes a client first-party by design |
| **Group B — the header recorder** | `RECORDED_RESPONSE_HEADERS` and `response_headers()`. ***The phase's original subject***, and self-contained: a module constant and one extraction function, no config and no experiment dependency |
| **`README.md`** | The env-var line removed, with a short note saying why it is not recommended |
| **`procedures/testing-against-claude-code.md`** | The same line removed. *This is the procedure a session follows to drive these very sessions — leaving it is the most likely way the bug returns* |
| **`reference/architecture.md`** | ***The line out of the usage example, and a note added in its place.*** **Owner's call, 2026-09-22, and it is better than the recommendation it overrode**: *whether suppressing attribution to LM Studio is needed or even safe has never been measured*, so the example should not prescribe it — while the variable exists, does something, and is worth documenting as an option for the cases where somebody wants it |
| **`BUG-001`** | Rewritten on `main` to state the cause and the resolution. *`main`'s copy is the pre-investigation version; this branch's copy is a record of three retractions and does not belong on the trunk* |
| **The phase summary** | A new `docs/milestone-2-corpus/phase-14-rate-limit-headers/README.md` on `main` — why the phase opened, what was tried, what was concluded, ***what was taken to `main` and what deliberately was not***, and how to reach this branch |
| **`branch-index.py`** | Task 19's fix. ***New work — it was never started***, so this is written fresh rather than cherry-picked |
| **Phase 1 evidence** | *Annotated, never edited.* A note pointing at the finding; the recorded command stays as it was actually run |
| **Backlog** | `BKL-0040`, `BKL-0041`, `BKL-0042` ported, plus a new item for Group D |
| **`status.md`, `IDM-001`** | Phase 14 recorded as **closed without merge**; the method amended, because *a phase that deliberately does not merge* is a case `IDM-001` has never had |

| Stays on the branch | |
|---|---|
| The three failed experiments, `config-boringssl.yaml`, `make forwarder` / `run-boringssl` | Negative results, kept reproducible |
| **Group C4** — the attribution injection | *Measured working. Not needed once the README line is gone, and kept here in case it ever is* |
| The hosts route, the TLS terminator, `escape-the-hosts-file.py` | The fallback, if the attribution behaviour ever changes |
| `config-attribution.yaml`, `config-hosts.yaml`, `make run-with-attribution`, `run-hosts` | |
| All 24 `for-the-owner.md` entries, `notes.md`, `plan.md`, the whole `evidence/` folder | ***The investigation record.*** This is what the branch is FOR |

## Order, and why this order

***The sanitization happens FIRST.*** **Rewriting history changes every commit hash on this
branch**, and the phase summary going to `main` will cite this branch's commits by hash. *Writing
the summary first would mean citing hashes that stop existing an hour later.*

### 0 · Safety, before anything is rewritten

1. **Tag the current tip**: `archive/phase-14-pre-sanitize` at `25f2e21`. *Cheap, and the only
   complete undo for step 1.*
2. Record `25f2e21` and the fork point `ac2976e` in this file. **Both are needed to verify the
   rewrite did what it claimed.**

### 1 · Sanitize this branch's history

3. **Build the replacement map.** *Eleven session ids and about forty request ids.*
   ***Two UUIDs are excluded and must not be touched:*** **`5791f885-4f45-4b01-bbd1-5ac2631bf167` is
   `SYNTHETIC_UUID_NAMESPACE`**, a live constant in `src/ilirium_llm_router/jsonl.py:41` — *replacing
   it silently changes every id the tool derives* — and `00000000-0000-0000-0000-000000000000` is a
   nil placeholder.
4. ***Restrict the rewrite to `ac2976e..HEAD`.*** **A full-history rewrite would also rewrite
   `main`'s ancestor commits**, because one of them carries session `20260825-1` in phase-11's
   `plan.md` — *the branch would lose its merge base with `main` and `git diff main..HEAD` would
   stop meaning anything.* Every id being replaced lives in a branch-only commit, so the range is
   sufficient as well as necessary.
5. **Run `filter-repo` in a throwaway clone**, not against the shared bare object store —
   *three worktrees share it.* Bring the rewritten branch back and reset the local ref.
6. **Verify, and all four must hold**: the merge base with `main` is still `ac2976e`; no target id
   survives anywhere in `ac2976e..HEAD`; the working tree at the new tip is **byte-identical to the
   old tip except for the replaced ids**; `make test` and `make lint` still pass.
7. **Write the id mapping to `logs/`**, which is gitignored and per-worktree. ***The corpus folders
   on disk keep the real ids***, so the tie the evidence README relies on breaks otherwise — this
   keeps it locally without committing anything.

### 2 · Fix `main`'s one id forward

8. Replace `20260825-1…` in `phase-11-corpus-tools/plan.md` with its mapped value, in an ordinary
   commit on the branch built in step 3. **No history rewrite on `main`** — *rewriting it would
   invalidate every merge hash this repository has deliberately recorded across its milestone
   READMEs and phase notes.*

### 3 · Build the `main`-bound branch

*Cut from `main`, merged `--no-ff` per `IDM-001`.*

9. **Port the gzip fix**: `decoded_for_peek`, `PEEK_MAX_DECOMPRESSED`, `PEEKABLE_ENCODINGS`,
   `BodyUnreadable`, the two-reason `400`, and its eight tests.
10. **Port Group B**: `RECORDED_RESPONSE_HEADERS`, `response_headers()`, the `>= 400` log line, and
    its tests. ***Both ports are by feature, not by patch*** — `proxy.py` differs by 591 lines here
    and most of that is experiments. **A verification gate**: after porting, `grep` the result for
    `experiments` and for every Group C/C4 name, and the answer must be nothing.
11. `README.md` and `procedures/testing-against-claude-code.md` — the line out, with the reason.
12. `BUG-001` rewritten; Phase 1 evidence annotated.
13. The phase summary at `docs/milestone-2-corpus/phase-14-rate-limit-headers/README.md`.
14. `branch-index.py` — task 19's declarative fix. ***It also needs a category it has never had***:
    a branch that is kept, unmerged, and not in flight. *`--check` is `STALE` on a clean `main`
    today for the reason this fix addresses.*
15. Backlog ported; `status.md` and `IDM-001` updated.
16. **Every check green before the merge**: `make test`, `make lint`, `backlog-index --check`,
    `link-check.py`, and `branch-index.py --write` as the *last* step of the merge.

## Risks, named in advance

- ***The two ports are the delicate part.*** **`proxy.py` here is 591 lines from `main`'s**, and
  almost all of it is experiment code that must not travel. *The grep gate in step 10 is the check,
  and the ported tests passing on `main` is the proof.*
- ***`branch-index.py` gains a branch category while being fixed for a different defect.*** *Two
  changes in one tool in one pass is how the row it must not delete got deleted in the first place.*
- ***The remote state is now MEASURED, 2026-09-22, by `git ls-remote` — and it is narrower than
  feared.*** **`origin/feat/phase-14-rate-limit-headers` is at `4b40063`: 47 of the 54 commits, and
  a clean ancestor of local `HEAD`** — *behind, not diverged.* **The last seven commits — everything
  from `ca05ba1` (Group C4) forward — have never been pushed.**

  | | On GitHub | Never left this machine |
  |---|---|---|
  | **Session ids** | **four**, from 09-18 and 09-19 | ***five***, `20260920-1` and all four of 09-21 — *both halves of the A/B* |
  | **Request ids** | **39** | the `[cyber]` id from the owner's report |

  ***So the entire 09-20 and 09-21 record — the run that named the cause — is unexposed.*** *What is
  on GitHub is the 09-18/09-19 material.*
- ***A force-push is still required, and it is 47 commits' worth.*** *Every pushed commit gets a new
  hash in step 1.* **Or delete the remote branch and push the rewritten one**, which leaves the old
  commits unreachable rather than merely superseded. ***Neither is in this plan and neither happens
  without the owner saying so.***
- ***Forward-fixing `main` does NOT remove `20260825-1` from GitHub.*** **`origin/main` is at
  `ac2976e`, identical to local `main`, and that id sits ~20 commits deep in its history.** *A
  forward fix cleans the tip, here and on the remote after a normal push; the history keeps it in
  both places.* **Removing it would mean rewriting `main`, which the owner declined — correctly, as
  it would invalidate every merge hash this repository records.** *The record should say this
  plainly rather than let "sanitized" imply more than was done.*
- ***A rewrite is not retroactive, and GitHub keeps unreachable objects.*** *They stay fetchable by
  SHA for some time after a force-push.* **The repository is private and visible only to the owner**,
  so this is hygiene rather than incident response — *and the record should say exactly that, rather
  than imply the cleanup reached further than it did.*
