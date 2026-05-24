---
name: no-spec-commits
description: User does not want brainstorming spec / design docs committed to the repo; write them locally and skip the commit step.
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ca4807fa-11cf-4dd0-a8a9-e851cb43c413
---

Do not commit spec or design documents produced by `superpowers:brainstorming` (e.g. files under `docs/superpowers/specs/`) or other planning artifacts unless the user explicitly asks. Write the spec to disk for them to review, then stop — do not run `git add` / `git commit` on it.

**Why:** User said "we do not need to commit spec doc" on 2026-05-18 after I tried to commit a freshly-written brainstorming spec. They use spec files as a working artifact, not durable repo content.

**How to apply:** When the brainstorming skill (or any similar planning flow) reaches the "commit the design document to git" step, skip the commit and just ask the user to review the file. Implementation commits (code that comes after the spec) are still expected unless they say otherwise.
