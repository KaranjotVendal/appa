import re
from pathlib import Path

from appa_lib.transform_pull import _parse_frontmatter, _split_frontmatter


BEGIN = "<!-- BEGIN appa-managed -->"
END = "<!-- END appa-managed -->"


def _build_block(instructions_dir: Path) -> str:
    sections: list[str] = []
    for path in sorted(instructions_dir.glob("*.md")):
        text = path.read_text()
        fm_raw, body = _split_frontmatter(text)
        fm = _parse_frontmatter(fm_raw)
        if fm.get("scope", "global") != "global":
            continue
        sections.append(f"## {fm['name']}\n{body.rstrip()}\n")
    body_block = "\n".join(sections) if sections else ""
    return f"{BEGIN}\n{body_block}{END}\n"


def project_block(instructions_dir: Path, target_path: Path) -> None:
    """Write the appa-managed block of global instructions into target_path.

    Any content outside the BEGIN/END markers is preserved. Used for both
    pi's AGENTS.md and claude's user-global CLAUDE.md.
    """
    instructions_dir = Path(instructions_dir)
    target_path = Path(target_path)
    block = _build_block(instructions_dir)

    if not target_path.exists():
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(block)
        return

    existing = target_path.read_text()
    pattern = re.compile(re.escape(BEGIN) + r".*?" + re.escape(END) + r"\n?", re.DOTALL)
    if pattern.search(existing):
        new = pattern.sub(block, existing)
    else:
        sep = "" if existing.endswith("\n") else "\n"
        new = existing + sep + "\n" + block
    target_path.write_text(new)
