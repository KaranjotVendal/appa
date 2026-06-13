---
name: verify_live_api
scope: global
type: feedback
description: Verify behavior against the live API before trusting reference docs; live-verify write paths on a throwaway entity
---

When building a tool against an external API, **treat any provided reference doc as suspect and verify against the live instance** — especially before relying on field IDs, endpoints, and workflow rules.

**Why:** On jiracli the supplied Jira API doc was wrong repeatedly (2026-06):
- `/rest/api/3/search` was **removed** (HTTP 410) → had to migrate to `/rest/api/3/search/jql` (token pagination, not `startAt`).
- Custom-field IDs were wrong for the instance: Story Points `customfield_10004` (doc said `10028`), Sprint `customfield_10007` (doc said `10020`). Confirmed via `GET /rest/api/3/field`.
- Undocumented workflow constraints surfaced only live: sprint assignment is reverted by **async** automation unless the issue is past "Ready for Development"; the sprint **board only renders board-column statuses**; the project **requires an assignee** (no unassign). Each was found by running the real command, not from the doc.

**How to apply:**
- Pull field IDs / metadata from the live API (`/field`, createmeta, board config) rather than the doc.
- **Live-verify write paths**, not just reads — mocks can't catch server-side automation, gates, or async reverts. Use ONE throwaway entity, exercise the full lifecycle, and **close it (don't delete)** if the account lacks delete permission.
- Beware **async** server automation: an immediate read-back after a write can be a false positive (the rule reverts it seconds later). Decide from durable signals (e.g. status vs board columns), not a racy re-read.
- When a doc claim contradicts live behavior, trust live and record the correction in the spec/plan.
