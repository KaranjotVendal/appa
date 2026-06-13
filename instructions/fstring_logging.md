---
name: fstring_logging
scope: global
type: feedback
description: Use f-strings in logging calls (logger.warning/info/etc.), not %-style lazy args
---

Use f-strings in logging calls — `logger.warning(f"missing <{tag}> in verdict[{idx}]")` — not the %-style lazy form `logger.warning("missing <%s> in verdict[%d]", tag, idx)`.

**Why:** The user prefers the readability of f-strings and asked for it explicitly during a verdict.py review. The codebase's ruff config does not enable the `G` (flake8-logging-format) family, so there's no tooling objection.

**Trade-off to be aware of (not a blocker):** %-style defers string formatting until the record is actually emitted; f-strings format eagerly. For `warning`/`error` (almost always emitted) the cost is negligible. If we ever add hot-path `logger.debug` calls that are usually filtered out, reconsider for those specific lines — but default to f-strings per the user's preference.

**How to apply:** any new or edited `logger.*` call uses an f-string. Applies to all log levels.

Related: [[feedback_descriptive_arg_names]] (same readability-first preference).
