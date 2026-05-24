"""Transform a Claude Code memory file into a canonical appa instruction file.

Also exposes minimal YAML-subset frontmatter helpers (used by the projector modules).
"""


def _split_frontmatter(text: str) -> tuple[str, str]:
    if not text.startswith("---\n"):
        raise ValueError("file missing leading '---' frontmatter delimiter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("file missing closing '---' frontmatter delimiter")
    return text[4:end], text[end + 5:]


def _parse_frontmatter(fm: str) -> dict:
    """Parse a tiny YAML subset: top-level scalars + one level of nested map under a key whose value is empty."""
    result: dict = {}
    current_key: str | None = None
    for raw in fm.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw.startswith("  ") and current_key is not None:
            k, _, v = raw.strip().partition(":")
            result.setdefault(current_key, {})[k.strip()] = v.strip().strip('"')
            continue
        k, _, v = raw.partition(":")
        key = k.strip()
        val = v.strip().strip('"')
        if val == "":
            result[key] = {}
            current_key = key
        else:
            result[key] = val
            current_key = None
    return result


def _first_body_line(body: str) -> str:
    for line in body.splitlines():
        if line.strip():
            return line.strip()
    return ""


def transform_pull(text: str, scope: str) -> str:
    fm_raw, body = _split_frontmatter(text)
    fm = _parse_frontmatter(fm_raw)
    name = fm.get("name", "").strip()
    if not name:
        raise ValueError("frontmatter missing 'name'")
    metadata = fm.get("metadata") or {}
    if not isinstance(metadata, dict):
        metadata = {}
    type_ = metadata.get("type", "feedback")
    description = fm.get("description") or _first_body_line(body)
    return (
        "---\n"
        f"name: {name}\n"
        f"scope: {scope}\n"
        f"type: {type_}\n"
        f"description: {description}\n"
        "---\n"
        + body
    )
