---
name: gitignore-superpowers-docs
description: "When initialising a new repo, add an entry to .gitignore that excludes files created by superpowers skills (specs, plans, etc. — typically under docs/superpowers/ or docs/*)."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 431ad1f1-5adb-4d42-9a4c-4e499e14a21d
---

When setting up a new project's `.gitignore`, include a pattern that excludes any artifacts produced by superpowers skills (brainstorming specs, writing-plans plans, anything else those skills drop into `docs/superpowers/...`). These files are local-only working artifacts and should never enter git history.

A reasonable default pattern is `/docs/*` (the user picked this on 2026-05-24 in the `appa` repo), but the broader principle is: anything written by a superpowers skill into the working tree is intended for local review only — gitignore it from the start. This extends [[no-spec-commits]] from "don't commit" to "make it impossible to accidentally commit."

**Why:** User said on 2026-05-24 "we always want to gitignore every created by superpowers which usually sits in docs/*". The earlier rule (skip the commit) relied on me remembering — gitignoring removes that footgun entirely.

**How to apply:** During the first task of any new-project plan (or whenever I'm authoring a fresh `.gitignore`), include a `/docs/*` (or equivalent project-appropriate) line. If the project already has a `.gitignore` without this, add it. If superpowers files have already been staged before this rule was applied, `git rm --cached` them before the commit.
