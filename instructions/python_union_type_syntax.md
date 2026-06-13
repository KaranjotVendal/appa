---
name: python_union_type_syntax
scope: global
type: feedback
description: Use `X | None` union syntax in Python type hints, never typing.Optional
---

In Python type hints, always write `X | None` (PEP 604 union syntax), never `typing.Optional[X]`. Don't import `Optional` at all.

**Why:** User said via plannotator review on 2026-06-08 (jot-cli scaffold, Task 5): "we never use optional but instead | as per python standard." They treat the `|` union form as the project/personal standard.

**How to apply:** When writing or editing Python, use `str | None`, `int | None`, etc. for optional values, and `A | B` for unions. Remove `from typing import Optional` and rewrite any `Optional[X]` to `X | None`. Same spirit favors built-in generics (`list[str]`, `dict[str, int]`) over `typing.List`/`typing.Dict`. Applies to the `cli/` (jot-cli) codebase and any future Python here.
