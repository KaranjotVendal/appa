---
name: plannotator-before-commit
description: "Run plannotator-review on uncommitted changes only; don't commit a task's work until plannotator has reviewed it and the user has signed off on the feedback."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ca4807fa-11cf-4dd0-a8a9-e851cb43c413
---

`plannotator-review` reviews unstaged/uncommitted changes — once a commit lands, those changes drop out of its diff and plannotator returns an empty "no changes requested" result that looks like a pass but isn't a real review.

**Why:** User said on 2026-05-18 "there is something wrong with commits. I cannot see changes in plannotator" after I committed Task 3's work and then tried to run plannotator. Earlier passes on Tasks 1 and 2 were also likely no-ops because the changes were already committed. Confirmed the right order is: make changes → plannotator → address feedback → commit.

**How to apply:**

1. When executing a plan task per the [[per-task-approval]] flow: make all changes for the task, then **stop before committing**.
2. Wait for the user to invoke `plannotator-review` (or offer it explicitly).
3. Address any annotations returned. Changes stay unstaged.
4. Once the user signals plannotator passed AND they're ready to commit, then commit.
5. The "commit each iteration, squash per task" pattern ([[commit-each-iteration-then-squash]]) still applies inside a task — but each iteration commits *after* its own plannotator pass, not before.

**Recovery if changes were committed prematurely:** soft-reset back to before the commits (`git reset --soft <pre-task-commit>`), then unstage (`git reset HEAD`) so the diff is visible to plannotator again. Re-commit after review.
