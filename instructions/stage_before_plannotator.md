---
name: stage_before_plannotator
scope: global
type: feedback
description: Always git add changes before running plannotator review so the diff is staged and ready for commit after the review passes
---

Always `git add` the changed files before running plannotator on them.

**Why:** User's workflow expects the diff to be staged when plannotator reviews it — keeps the path from "review passed" → "commit" frictionless (no separate staging step between approval and commit). Aligns with [[feedback_plannotator_before_commit]] (plannotator gates commits) and [[feedback_commit_then_squash]] (per-task commit at end).

**How to apply:** After implementing a task's changes and verifying (ruff/ty/tests), stage everything before invoking `plannotator review`. Don't stage incrementally if there are unrelated dirty files in the tree — be explicit about what's part of this task.
