---
name: git_branching_workflow
scope: global
type: feedback
description: Branch-per-milestone, one commit per task at explicit sign-off, push when the milestone is done, merge to main with --no-ff.
---

Git policy for multi-task feature work, established 2026-05-14 during the mvfdata-agent-stack pi-port and carried forward as a general preference:

- **One branch per milestone** (e.g., `m1-ai-provider`, `m2-ai-agent`).
- **One commit per task in the final history** — but only *after the user explicitly signs off on the task*.
- **Sign-off is explicit, not inferred.** The user will say so in words. Do not guess based on phrases like "looks good" or "let's move on" unless they are unambiguous; if in doubt, treat the task as not yet signed off.
- **Within an in-progress task, multiple WIP commits are fine.** Do not preemptively amend or squash before sign-off.
- **Squash WIP commits down to one task-shaped commit at sign-off time** (`git rebase -i` or `git reset --soft` + recommit).
- **Push the branch only when all tasks in the milestone are complete** — not after each task.
- **Merge into main with `--no-ff`** (preserves milestone grouping).
- **Review-driven polish** (e.g., addressing plannotator feedback) goes into the same task's final commit, after sign-off.

**Why:** Squashing prematurely hides iteration that may matter if review surfaces issues; squashing too late loses the "one logical change per commit" property that makes `git log` and `git bisect` useful long-term. Sign-off is the natural boundary because the task is then considered shippable.

**How to apply:** During task execution, commit normally (WIP commits OK). When the user signs off, squash before moving to the next task. Don't squash during review iteration — that loses the audit trail of what changed in response to feedback. This composes with [[commit_each_iteration_then_squash]] (the per-task micro-commit/squash cadence) and [[plannotator_before_commit]] (review gates each commit).
