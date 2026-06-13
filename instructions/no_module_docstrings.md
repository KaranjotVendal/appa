---
name: no_module_docstrings
scope: global
type: feedback
description: Skip module-level docstrings at the top of Python files; module name + content makes the purpose clear without a docstring
---

Don't add module-level docstrings (the `"""..."""` block at the very top of a `.py` file, before imports).

**Why:** The user finds them noise — the module's filename, its contents, and the package it lives in already convey purpose. Repeating that purpose in a docstring adds rot risk (the docstring drifts from the code) and visual clutter. Plannotator has flagged module docstrings as "get rid of these" multiple times across this project (`logging.py`, `verdict.py`).

**How to apply:**
- New Python modules: start the file with `from __future__ import annotations` (or imports), not a triple-quoted string.
- **When you edit an existing module that has a module-level docstring, remove the docstring as part of that edit.** (Earlier guidance said "leave existing alone" — the user corrected this: plannotator flagged fetcher docstrings on a file being edited and asked them removed. The filename should be descriptive enough; the docstring is redundant.) Don't go out of your way to open untouched files just to strip docstrings, but any file you're already modifying gets its module docstring removed.
- Function and class docstrings are fine and useful — this rule is specifically about the *module-level* docstring.
- Exception: if a module legitimately needs a usage example or non-obvious API contract documented (e.g. `__init__.py` for a public package), a docstring is OK. Default to skipping.

Related: [[feedback_no_code_blocks_in_plans]] (same "less prose, more code/content" preference applied to plans).
