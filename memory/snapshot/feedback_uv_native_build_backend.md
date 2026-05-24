---
name: uv-native-build-backend
description: "When setting up a Python project with uv, use uv's own build backend (uv_build) — not hatchling or setuptools. Configure module-name / module-root if the source dir name differs from the project name."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 431ad1f1-5adb-4d42-9a4c-4e499e14a21d
---

When initialising a Python project that uses `uv` for environment + lockfile management, also use uv's native build backend in `pyproject.toml`. Do NOT default to `hatchling.build`, `setuptools.build_meta`, or anything else — uv_build is the user's preferred backend for uv projects.

Minimum config:

```toml
[build-system]
requires = ["uv_build>=0.11.13,<0.12.0"]
build-backend = "uv_build"
```

If the source directory name differs from the project name (e.g. project `appa`, package at `src/appa_lib/`), add:

```toml
[tool.uv.build-backend]
module-name = "appa_lib"
module-root = "src"
```

By default `module-root = "src"` and `module-name` is derived from `[project].name` with dots/dashes → underscores, so a project named `appa` with code at `src/appa/` needs no `[tool.uv.build-backend]` block at all.

**Why:** User said on 2026-05-24 (during the `appa` repo bootstrap) "I want to change build system to uv. these uv docs might help to set it up correctly. https://docs.astral.sh/uv/guides/package/#building-your-package". They want consistency: if uv manages the project, uv builds the project.

**How to apply:** When `uv init` isn't run by hand and I'm writing a `pyproject.toml` from scratch, default to `uv_build` for `[build-system]`. If unsure of the current uv version's compatible bound, the value `uv init --build-backend uv` produced on 2026-05-24 was `["uv_build>=0.11.13,<0.12.0"]` — adjust to current major version.
