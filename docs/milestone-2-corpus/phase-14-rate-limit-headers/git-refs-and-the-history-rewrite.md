# Refs, namespaces, and how the history rewrite actually worked

*Written 2026-09-22, from questions the owner asked while Phase 14 was being closed. **It is a
reference note, not a record of the phase*** — the phase's own story is in `README.md` beside this
file. *What is here is the git mechanics underneath the sanitization, written down because the
commands involved are ones this repository will not run again for months and the reasoning behind
them is not obvious from the command line alone.*

---

## 1. A ref is a file whose path is its name

***There is no such thing as "creating a namespace" in git.*** **A ref is a file under `refs/`
containing one 40-character SHA**, and git writes whatever path you name. `refs/sanitized/` exists
because something asked for a ref at that path; git created the directory the way `mkdir -p` would.

On this repository, during the rewrite, `.bare/refs/` held:

```
refs/heads/…                                    the branches
refs/tags/archive/phase-14-pre-sanitize         a tag
refs/sanitized/phase-14                         an invented namespace
```

**All three are the same kind of object.** *The difference is only where they sit, and what reads
that location.*

### Why `git branch -a` does not show two of them

***`git branch` reads exactly two namespaces: `refs/heads/` and `refs/remotes/`.*** **Anything
else is invisible to it**, however branch-shaped the name looks.

| Ref | Where it lives | What lists it |
|---|---|---|
| `feat/phase-14-rate-limit-headers` | `refs/heads/` | `git branch` |
| `archive/phase-14-pre-sanitize` | `refs/tags/` | `git tag -l` |
| `refs/sanitized/phase-14` | *nowhere standard* | `git for-each-ref`, `git show-ref` |

***The slash in `archive/phase-14-pre-sanitize` makes it read like a branch and it is not one.***
*It is a hierarchy separator inside `refs/tags/`; the ref was made with `git tag`, so that is where
it landed.*

**When the question is "what is actually in this repository", `git for-each-ref` is the honest
answer and `git branch -a` is not.** *On 2026-09-22 the repository held 30 refs and `git branch -a`
listed 28.*

### Two other things that output shows

***`git branch -a` printed no remote-tracking branches at all***, which is not because nothing has
been pushed. **`[remote "origin"]` in `.bare/config` carries a `url` and no `fetch` refspec**, so
nothing ever populates `refs/remotes/origin/*` and the `-a` flag has nothing to add. *`git ls-remote
origin` reads the remote directly, writes nothing, and is what answers "what is pushed" here.*
**`status.md` recorded the opposite for two weeks** — *see its "In-flight branches" section.*

***The `+` beside a branch in `git branch` output means it is checked out in another worktree.***
*On a bare clone with siblings, most branches wear it.*

---

## 2. The rewrite copied commits; it never moved or edited any

***A commit cannot be edited.*** **Its hash is a digest of its content**, so changing a byte
produces a different commit — *a "rewrite" always means **new objects**, never modified ones.*

Three separate things happened, and only the first made commits:

1. ***`git filter-repo`, inside a throwaway clone, WROTE 55 new commits.*** *The originals stayed
   in that clone, untouched, until it was discarded.*
2. ***`git fetch` COPIED those objects into `.bare`.*** *It transferred the commits, trees and blobs
   this repository lacked and then wrote one ref file.* **The clone kept its copy; nothing moved.**
3. ***`git reset --hard` MOVED A POINTER.*** *It rewrote the 40 bytes in
   `refs/heads/feat/phase-14-rate-limit-headers` so the branch named the new history instead of the
   old.* **No objects were copied at that step** — *both histories were already in the store.*

***So the pre-rewrite commits were never deleted.*** **They are still in `.bare`, reachable from the
tag**, which is exactly why the tag is both the safety net and the reason the local cleanup is not
yet finished.

### Why the rewrite was confined to a range

**`--refs ac2976e..feat/phase-14-rate-limit-headers` rather than the whole branch.** *The branch's
history includes `main`'s as ancestors, and one of those ancestors carries a session id.* **A
full-history rewrite would have rewritten `main`'s commits too, and the branch would have lost its
merge base with `main`** — *`git diff main..HEAD` would have stopped meaning anything.*

***The cost of that choice, and it is visible in the result:*** **blobs inherited unchanged from
before the fork point never enter the rewrite**, so four files last modified on `main` kept their
original content. *That is why one id deliberately survives on the branch, and why `main` fixed its
own copies forward instead.*

---

## 3. Every command, in order

***Stage 0 — the safety net.***

```sh
git add .../phase-14-rate-limit-headers/closing-plan.md   # that file lives on the archive branch
git commit -q -F -
git tag archive/phase-14-pre-sanitize 25f2e21    # WRONG — one commit behind
git tag -f archive/phase-14-pre-sanitize HEAD    # corrected, to 53e0041
```

***The first tag was wrong and it mattered.*** *Committing the plan had already moved `HEAD`;
tagging the remembered SHA pinned the state **before** that commit.* **A safety net that restores a
state missing a commit is worse than no net, because it looks like one.**

***Inventory — all read-only.***

```sh
for c in $(git rev-list ac2976e..HEAD); do
  git grep -hoE '<pattern>' $c -- docs src
done
git log --format='%H%n%B' ac2976e..HEAD
git check-ignore -q logs/id-mapping-DO-NOT-COMMIT.txt
```

**`git grep <pattern> <commit>` searches a commit's tree without checking anything out**, which is
how 55 commits were swept without touching the working tree. *The `git log` pass was to confirm no
id lived in a commit **message** — `--replace-text` rewrites file contents only.*

***The rewrite, in a throwaway clone.***

```sh
git clone --no-local --branch feat/phase-14-rate-limit-headers  <bare>  <scratch>/sanitize-clone

cd <scratch>/sanitize-clone
git filter-repo --replace-text <scratch>/replacements.txt \
                --refs ac2976e..feat/phase-14-rate-limit-headers --force
```

***`--no-local` is the flag that makes this safe.*** **Cloning from a local path normally HARDLINKS
object files**, so the two repositories would share them on disk — *and a rewrite in the clone could
reach back into `.bare`.* **`--no-local` forces a real transfer.** *Three worktrees share that
object store; none of them was exposed to the rewrite.*

***Verification, before anything came back.***

```sh
git cat-file -t ac2976e…             # the fork point still exists
git merge-base HEAD ac2976e…         # still the merge base
git rev-list --count ac2976e..HEAD   # still 55 commits
git grep -n '<id>' $c -- docs        # nothing survived
```

***Bringing it back, and the ref that caused the questions.***

```sh
git fetch <scratch>/sanitize-clone feat/phase-14-rate-limit-headers:refs/sanitized/phase-14
```

**The `<source>:<destination>` refspec is what created `refs/sanitized/`.** *An invented namespace
was chosen on purpose:* **a ref outside `refs/heads/` cannot be checked out by accident, is not
pushed by a default refspec, and cannot be mistaken for somebody's work** — *which matters when what
it holds has not been verified yet.*

```sh
git diff --name-only archive/phase-14-pre-sanitize refs/sanitized/phase-14
git diff -U0        archive/phase-14-pre-sanitize refs/sanitized/phase-14
```

***This is the step that made the rewrite trustworthy.*** **19 files changed, and ZERO changed lines
that did not contain an id.** *Everything before it was preparation; everything after it was
bookkeeping.*

```sh
git reset --hard refs/sanitized/phase-14
git add -- docs && git commit -q -F -
```

### Which commands actually changed state

| | What it changed | Undo |
|---|---|---|
| `git tag -f …` | created the safety net | `git tag -d` |
| `git filter-repo …` | 55 new commits **in the throwaway clone** | *irrelevant — discarded* |
| `git fetch …:refs/sanitized/…` | copied objects in, wrote one ref | `git update-ref -d` |
| **`git reset --hard`** | ***moved the branch*** | *only while the tag exists* |

**Everything else read.**

---

## 4. What is still holding the old ids, and what removing it means

***Two refs keep the pre-rewrite commits reachable, and `git branch -a` shows neither.***

- **`refs/tags/archive/phase-14-pre-sanitize` → `53e0041`.** *The pre-rewrite tip.* **This is the one
  that matters**: while it exists, every real session and request id is still in this repository, and
  `git reset --hard archive/phase-14-pre-sanitize` would put the branch back.
- **`refs/sanitized/phase-14` → `1ffaf1c`.** *Points into the **new** history and is an **ancestor**
  of the branch* — **deleting it frees nothing and loses nothing.** *(An earlier verbal answer called
  it a duplicate of the branch tip. It is not: the branch moved one commit further when the
  sanitization record was committed.)*

***Deleting the tag is the finishing move and the point of no return.*** **Until then the local
cleanup is a rename, not a removal** — *unreachable objects are only collected once nothing points
at them.*

***And none of this reaches GitHub.*** **`origin` still holds 47 pre-rewrite commits**; a local
rewrite cannot change a remote. *Either force-push the rewritten branch or delete the remote branch
and push it fresh — the second at least leaves the old commits unreachable rather than merely
superseded.*
