---
name: tooling_stack
scope: global
type: feedback
description: Preferred Python tooling: uv (+uv_build), ruff, ty, pytest, httpx/respx, latest stable Python; never `uv run` to invoke the finished CLI
---

The user's standard Python stack for CLI/tool projects (established across jiracli, 2026-05/06):

- **`uv`** for env + deps. **`uv_build`** backend in `pyproject.toml` (`requires = ["uv_build>=0.11,<0.12"]`, `build-backend = "uv_build"`). Dev deps in `[dependency-groups]`.
- **Install the CLI via `uv tool install --editable .`** (puts the binary on PATH, tracks source).
- **Never use `uv run` to invoke the finished CLI** — use the installed binary. `uv run` is only for dev tasks (tests, lint, type check, ad-hoc scripts). The skill/README install step should `command -v <cli> || uv tool install --editable .`.
- **Latest stable Python**, pinned via `.python-version` (don't default to an old floor like 3.11 — use current, e.g. 3.14).
- **Quality gates, all must pass before staging:** `ruff check`, `ruff format --check`, `ty check` (Astral's type checker — config under `[tool.ty.environment]`/`[tool.ty.src]`), `pytest`.
- **HTTP: `httpx`** (long-lived `httpx.Client` for pooling); tests mock with **`respx`** (fixture style, not the decorator). Not requests/responses.
- **Config as JSON** via stdlib `json` at `~/.config/<tool>/config.json` (the user rejected TOML/tomli-w). Secrets in the **OS keychain** (`keyring`), never in the config file.
- **Typer** for the CLI; add `typer.Option`/`typer.Argument` to ruff `flake8-bugbear.extend-immutable-calls` to silence B008.

See [[feedback-logging-pattern]], [[feedback-no-emojis]], [[feedback-git-workflow]], [[feedback-review-loop]].
