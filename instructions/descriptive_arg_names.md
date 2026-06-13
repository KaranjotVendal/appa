---
name: descriptive_arg_names
scope: global
type: feedback
description: Use descriptive parameter and variable names; avoid terse abbreviations like el, v_el, idx, sr_el
---

Use descriptive parameter and local-variable names. Avoid terse abbreviations even for short-lived locals.

**Why:** The user values readability over brevity in names. Plannotator flagged `sr_el`, `v_el`, `idx`, `c_el` etc. in the verdict parser as too terse — "we need to have descriptive arg names here." A name like `verdict_element` reads at a glance; `v_el` forces the reader to decode it.

**How to apply:**
- Elements / objects: name the thing, not an abbreviation — `verdict_element` not `v_el`, `sr_element` not `sr_el`, `channel_element` not `c_el`.
- Don't over-correct into verbosity — `element` is fine for a generic helper; the point is no cryptic abbreviations, not maximal length.
- Applies to function parameters and local variables alike.
- **Accepted conventional exceptions:** `idx` (loop index) and `e` (exception binding in `except ... as e`) are fine — the user confirmed these read clearly enough and don't need expanding. Don't rename `idx`→`verdict_index` or `e`→`error`. The rule targets domain-object abbreviations (`v_el`, `sr_el`), not these universal idioms.

Related: [[feedback_no_module_docstrings]], [[feedback_no_code_blocks_in_plans]] — same readability-first preference.
