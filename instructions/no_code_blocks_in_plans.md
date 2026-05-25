---
name: no_code_blocks_in_plans
scope: global
type: feedback
description: When writing plans (superpowers:writing-plans or any plan-authoring flow), do not include code blocks in step bodies. Describe the change; show code at implementation time, not plan time.
---

When writing plans via `superpowers:writing-plans` or any plan-authoring flow, do **not** include code blocks in step bodies. Describe each change (file, function, behavior, what tests cover it, what command verifies). Show actual code at implementation time, not plan time.

**Why:** User said on 2026-05-25 that code blocks in plans make no sense for their workflow:

- They use per-task-approval ([[per_task_approval]]) — they're in the loop reviewing and writing code interactively at task-execution time.
- They use plannotator-before-commit ([[plannotator_before_commit]]) — review happens on actual code in the diff, not on pre-imagined code in the plan.
- The writing-plans skill's "complete code in every step" / "code blocks required for code steps" rules exist to serve subagent-driven-development handoffs, where a fresh agent needs the entire implementation pre-baked. The user has rejected that execution mode.

The result: code blocks in plans bloat the read-through, diverge from the eventual real implementation, and serve no consumer in this workflow.

**How to apply:**

1. When invoking `superpowers:writing-plans`, treat the skill's "complete code in every step" / "Task Structure" code-block requirements as overridden. The skill's own platform-adaptation note acknowledges user instructions take precedence.
2. Each plan step should name what changes (file path, function, intent), the test that covers it, the command that verifies. No embedded source code.
3. For TDD steps: write "add a failing test for <behavior>" instead of embedding the test source. The actual test source appears at implementation time.
4. Verification commands (e.g. `uv run pytest tests/test_x.py -v`) are not code blocks in the prose sense — keep those.
5. Exception: if the user explicitly asks for code in the plan ("include the actual test source"), comply.
6. This rule applies to plans the agent generates going forward. It does not retroactively edit existing plans.
