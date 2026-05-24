"""Project canonical instructions into the appa-managed block of pi's user-global AGENTS.md."""

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


def project_pi(instructions_dir: Path, agents_md_path: Path) -> None:
    instructions_dir = Path(instructions_dir)
    agents_md_path = Path(agents_md_path)
    block = _build_block(instructions_dir)

    if not agents_md_path.exists():
        agents_md_path.parent.mkdir(parents=True, exist_ok=True)
        agents_md_path.write_text(block)
        return

    existing = agents_md_path.read_text()
    pattern = re.compile(re.escape(BEGIN) + r".*?" + re.escape(END) + r"\n?", re.DOTALL)
    if pattern.search(existing):
        new = pattern.sub(block, existing)
    else:
        sep = "" if existing.endswith("\n") else "\n"
        new = existing + sep + "\n" + block
    agents_md_path.write_text(new)
