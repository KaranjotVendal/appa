---
name: per-task-approval
description: "When executing a written implementation plan, walk through each task one at a time — describe what it does, wait for explicit go-ahead before implementing, and never bundle multiple tasks without permission."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ca4807fa-11cf-4dd0-a8a9-e851cb43c413
---

When executing a multi-task plan (e.g. the output of `superpowers:writing-plans`), do NOT pick a batch execution mode (subagent-driven or inline). Instead:

1. Describe the next task's purpose and what files it touches.
2. Wait for the user's explicit "go ahead" / "do it" / similar before running any of its steps.
3. Wait for explicit instruction before any other action (commits, branch ops, plannotator runs, etc.).

**Why:** User said on 2026-05-18 "we are going to go through each task one by one, validate what it is suppose to do and then I will give explicit go ahead for implementation and explicit command for any other actions". They want tight per-step control during implementation.

**How to apply:** Override the writing-plans skill's "Execution Handoff" prompt that offers Subagent-Driven vs Inline. Default to interactive per-task review instead. Confirm with the user only if the project is genuinely large and per-task review feels excessive — but assume per-task by default.
