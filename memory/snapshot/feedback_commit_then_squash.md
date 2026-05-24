---
name: commit-each-iteration-then-squash
description: "During plan execution, commit each iteration (TDD step, refactor, etc.) within a task as a separate commit; at task completion, squash to one commit per task."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ca4807fa-11cf-4dd0-a8a9-e851cb43c413
---

When executing a multi-step task from a plan, commit at natural checkpoints inside the task (e.g. after writing failing tests, after making them pass, after smoke-test verification). At the **end of each task**, squash those intermediate commits into a single commit representing the whole task.

**Why:** User said on 2026-05-18 they want the eventual git history to show one commit per task, but with finer-grained commits during execution so individual iterations are reviewable / revertible. This combines the benefits of micro-commits during work with a clean final history.

**How to apply:**

1. Inside a task, after each natural checkpoint, run a regular `git commit` with a short message describing that iteration (e.g. `tests: failing tests for SessionLog.drain`, `impl: add drain queue`).
2. When the task is fully done and the user signals "task complete" or "next task", offer to squash the iteration commits into one commit per task. Use `git reset --soft <commit-before-task-started>` followed by a fresh `git commit -m "<task-summary>"`, or `git rebase -i <commit-before-task-started>` with all the iteration commits set to `fixup` except the first. Confirm the target message before squashing — destructive op.
3. **For tasks already complete with one commit (Tasks 1 and 2 as of 2026-05-18):** nothing to squash; they're already at the target shape.
4. Continue per-task-approval flow ([[per-task-approval]]).
