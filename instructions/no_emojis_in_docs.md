---
name: no_emojis_in_docs
scope: global
type: feedback
description: Do not use emojis in documentation (or generally) unless explicitly asked; default to plain text
---

Default to **no emojis** in documentation and written output. Do not use status icons (✅, 🔌, ⚠️, etc.) or decorative emojis in catalogs, READMEs, specs, plans, or other docs unless the user explicitly asks for them.

**Why:** User said on 2026-06-02, while reviewing the metrics catalog (`.docs/20_metrics/README.md`) where I'd used ✅/🔌 for integration status, that they don't want emojis in the documentation. They prefer plain, professional text.

**How to apply:**
- Convey status/emphasis with words, not icons — e.g. "Wired" / "Not integrated" instead of ✅ / 🔌; "Note:" instead of ⚠️.
- This applies to all written artifacts (docs, catalogs, READMEs, [[feedback_no_module_docstrings]]-style code comments, commit bodies, PR descriptions) — keep them emoji-free by default.
- If the user explicitly asks for emojis (or a legend with icons), use them for that case only; don't carry it forward as a new default.
