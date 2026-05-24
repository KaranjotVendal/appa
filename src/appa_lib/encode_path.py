"""Encode an absolute filesystem path the way Claude Code names per-project memory dirs."""


def encode_path(path: str) -> str:
    if not path.startswith("/"):
        raise ValueError(f"encode_path requires an absolute path, got: {path!r}")
    stripped = path.rstrip("/") or "/"
    return stripped.replace("/", "-")
