# Phase 11 — evidence

**Empty until Task 5.** *(A placeholder line, closed out when the slice is frozen.)*

`../../../README.md`'s rule: evidence is cited to something **committed**, because `logs/` is
gitignored and rotates. This phase's material is the owner's live corpus at
`to-run-server/logs/corpus/`, which was **still growing while it was being read** — so nothing here
may cite it by path.

## What will be frozen, and what will not

**The index, redacted. Never the blobs.** Captured request bodies are real prompts and real source
code; response bodies are real model output about them. Neither is redactable to placeholders in any
meaningful sense, and neither belongs in git.

**Redaction is to stable placeholders in first-appearance order** — `session-01`, `session-02` — per
`../../../README.md`, which is explicit that blanking destroys the finding while protecting nothing:
*which rows share a `session_id`* is the whole basis of every per-session claim this phase makes.

Three rules that come with it and that Task 5 must satisfy:

1. **Redact every identifier family**, not only `session_id`, and say which extra ones were taken.
2. **Check for secrets separately.** The index carries no header and therefore no credential — but
   "no identifiers" and "no secrets" are different problems and the second needs its own pass.
3. **State plainly which files were redacted and which were not, and why.**

## What each artefact will have to say

Per `../../../README.md`: what produced it, what it proves, what was redacted and how, and whether it
can be regenerated. **The last column is the one this phase will struggle with** — the source corpus
is live, so a frozen slice here is *not* regenerable, and it must say so rather than imply a rerun
would reproduce it.
