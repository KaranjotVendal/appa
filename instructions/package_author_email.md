---
name: package_author_email
scope: global
type: feedback
description: Use personal email karanjotgharu60@gmail.com for package authorship, not the work email
---

In package/project authorship metadata (e.g. `pyproject.toml` `[project].authors`), use **karanjotgharu60@gmail.com**, not the work email (`karanjot.vendal@mvfglobal.com`) that uv/git auto-fills.

**Why:** User said via plannotator review on 2026-06-08 (jot-cli scaffold) to change the author email to `karanjotgharu60@gmail.com`. `uv init` had populated it from the git/work identity; they want the personal address on published package metadata.

**How to apply:** After `uv init` (or any scaffolder) fills `authors`, replace the email with `karanjotgharu60@gmail.com`. The work email is still correct for git commits / session identity — this override is specifically for package author metadata.
