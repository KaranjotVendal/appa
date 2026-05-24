"""Project canonical instruction files into Claude Code's per-project memory directory."""

from pathlib import Path

from appa_lib.transform_pull import _parse_frontmatter, _split_frontmatter


def _render_claude(instruction_text: str) -> tuple[str, str, str]:
    fm_raw, body = _split_frontmatter(instruction_text)
    fm = _parse_frontmatter(fm_raw)
    name = fm["name"]
    description = fm.get("description", "")
    type_ = fm.get("type", "feedback")
    rendered = (
        "---\n"
        f"name: {name}\n"
        f'description: "{description}"\n'
        "metadata:\n"
        f"  type: {type_}\n"
        "---\n"
        + body
    )
    return name, description, rendered


def project_claude(instructions_dir: Path, target_dir: Path, machine_scope: str) -> None:
    instructions_dir = Path(instructions_dir)
    target_dir = Path(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    index_entries: list[str] = []
    written: set[str] = set()

    for path in sorted(instructions_dir.glob("*.md")):
        text = path.read_text()
        fm_raw, _ = _split_frontmatter(text)
        scope = _parse_frontmatter(fm_raw).get("scope", "global")
        if scope != "global" and scope != machine_scope:
            continue
        name, description, rendered = _render_claude(text)
        out_path = target_dir / f"{name}.md"
        out_path.write_text(rendered)
        written.add(out_path.name)
        index_entries.append(f"- [{name}]({name}.md) — {description}")

    for existing in target_dir.glob("*.md"):
        if existing.name == "MEMORY.md":
            continue
        if existing.name not in written:
            existing.unlink()

    (target_dir / "MEMORY.md").write_text("\n".join(index_entries) + "\n")
