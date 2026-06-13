---
name: logging_pattern
scope: global
type: feedback
description: Canonical logger setup pattern for Python projects: file + console handlers, pathlib, idempotent initialise_logger function
---

The user has a canonical logger-setup pattern they use across Python projects. Reference implementation lives at `/Users/karanjot.vendal/dev/sold-rate-agent/src/sold_rate_agent/logging.py`. Copied verbatim (with project-specific paths) into `jiracli/logging.py`.

**Shape of the pattern:**

```python
from __future__ import annotations

import logging
import sys
from pathlib import Path

LOG_DIR = Path.home() / ".<project>" / "logs"
LOG_FILE = LOG_DIR / "<project>.log"
LOG_FORMAT = "%(levelname)s | %(message)s | %(asctime)s | %(name)s | %(funcName)s"


def initialise_logger(name: str, overwrite_level: int | None = None) -> logging.Logger:
    """Return a configured logger for `name`."""
    logger = logging.getLogger(name)

    if logger.handlers:
        # Idempotent: repeat calls return the same logger without stacking handlers.
        if overwrite_level is not None:
            logger.setLevel(overwrite_level)
        return logger

    logger.setLevel(overwrite_level if overwrite_level is not None else logging.DEBUG)
    logger.propagate = False

    formatter = logging.Formatter(LOG_FORMAT)

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
```

**CLI adaptation (jiracli, 2026-06-09):** the verbatim sold-rate-agent pattern is wrong for a CLI. It puts the **console handler on stdout at DEBUG**, which (a) spams `DEBUG | → GET ...` lines on every normal run and (b) would corrupt `--json` output piped to `jq`. For a CLI, adapt it: console handler → **stderr**, level from `JIRACLI_LOG_LEVEL` env var **defaulting to WARNING** (quiet); file handler stays DEBUG so the full trace is in `~/.jiracli/logs/jiracli.log`. Keep this adaptation for any CLI; the stdout-DEBUG version is only appropriate for a verbose interactive agent like sold-rate-agent.

**Key properties:**
- **`pathlib.Path`, not `os.path`** — the user pushed back on a prior `import os` for path work explicitly asking to use pathlib.
- **Module name is literally `logging.py`** — this is fine; absolute imports of stdlib `logging` from inside it work, and `from <project>.logging import initialise_logger` is the public API.
- **Two handlers: file + console (stdout).** Both default to DEBUG level so the file always captures everything when the logger level allows.
- **`logger.propagate = False`** — avoids double-emission if root logger has handlers. Note: this also means `pytest`'s `caplog` fixture won't capture records from this logger unless you attach `caplog.handler` directly to it. In jiracli, tests don't call `initialise_logger`, so caplog still works on the bare logger.
- **`LOG_DIR` created on demand** via `mkdir(parents=True, exist_ok=True)`.
- **Idempotent** — repeat calls don't stack handlers; if `overwrite_level` is given, it just adjusts the level on the existing logger.
- **Format intentional**: `levelname | message | asctime | name | funcName`. Includes funcName so a tailing user can see *where* in the code each log came from.

**How to apply in a new project (matches `sold-rate-agent` usage):**

1. Create `src/<project>/logging.py` from the template above, substituting project name in paths.
2. **No central setup in `__main__.py`.** The entry point doesn't call `initialise_logger`. Reference: `sold-rate-agent/src/sold_rate_agent/agent.py` — agent.py initializes its own logger.
3. **Each module that wants to log calls it at module top level:**
   ```python
   from <project>.logging import initialise_logger

   logger = initialise_logger(__name__)
   ```
   This creates `<project>.<module>` as a separate logger with its own handlers (file + stdout). Idempotent across repeat imports.
4. Inside functions: `logger.info(...)`, `logger.debug(...)`, etc. Standard `logging` API.
5. **Tests using `caplog`:** since `propagate=False`, caplog's root handler doesn't capture records from these loggers. Attach `caplog.handler` directly to the named logger inside the test and remove it in `finally`. Example in `jiracli/tests/test_client.py::test_429_retry_logged_at_info`.
