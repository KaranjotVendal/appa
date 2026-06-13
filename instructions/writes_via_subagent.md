---
name: writes_via_subagent
scope: global
type: feedback
description: Delegate write/authoring tasks (code, SQL, tests, docs) to a subagent; the main thread orchestrates and reviews. Keeps main context clean.
---

Do write/authoring work through a subagent rather than editing files directly in the main
thread. The main thread stays the orchestrator: it reads, decides, reviews diffs, runs
verification (cortex/tests), and handles git — but the actual file mutations (writing code,
SQL, tests, docs) are delegated to a subagent.

**Why:** User said on 2026-06-11 (kicking off the metrics-wiring stream) "we want to do all
write tasks through a subagent this keeps our context clean." Generalizes the narrower
[[subagent_for_spec_plan_edits]] rule (which was spec/plan docs only) to all authoring work.
Keeping authoring out of the main thread preserves context budget for orchestration and review.

**How to apply:**
1. When a task requires writing or editing file content, dispatch a subagent with a precise
   brief (exact files, the change, the tests/verify command) instead of calling Write/Edit
   directly.
2. The main thread still owns: reading/assessing, the per-task plan, reviewing the subagent's
   diff, running cortex validation and tests, staging, and committing.
3. Gates are unchanged — [[per_task_approval]], [[stage_before_plannotator]],
   [[plannotator_before_commit]] still apply on top; the subagent authors, the user/main
   thread approves.
4. Trivial/mechanical edits and git operations can stay in the main thread unless the user
   says otherwise — the rule targets authoring work, not every keystroke.
