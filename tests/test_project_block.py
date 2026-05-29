from pathlib import Path

from appa_lib.project_block import project_block


GLOBAL_INSTR = """---
name: per-task-approval
scope: global
type: feedback
description: Wait per task.
---

Body alpha.
"""

LOCAL_INSTR = """---
name: per-project-thing
scope: -Users-x-myproject
type: project
description: Local only.
---

Body beta.
"""

BEGIN = "<!-- BEGIN appa-managed -->"
END = "<!-- END appa-managed -->"


def _setup(tmp_path: Path) -> tuple[Path, Path]:
    instr = tmp_path / "instructions"
    instr.mkdir()
    (instr / "per-task-approval.md").write_text(GLOBAL_INSTR)
    (instr / "per-project-thing.md").write_text(LOCAL_INSTR)
    return instr, tmp_path / "AGENTS.md"


def test_creates_file_with_block_when_missing(tmp_path):
    instr, agents_md = _setup(tmp_path)
    project_block(instr, agents_md)
    text = agents_md.read_text()
    assert BEGIN in text and END in text
    assert "## per-task-approval" in text
    assert "Body alpha." in text
    assert "Body beta." not in text


def test_preserves_user_content_outside_block(tmp_path):
    instr, agents_md = _setup(tmp_path)
    agents_md.write_text("My local notes.\n\nKeep me.\n")
    project_block(instr, agents_md)
    text = agents_md.read_text()
    assert "My local notes." in text
    assert "Keep me." in text
    assert BEGIN in text


def test_replaces_existing_block_idempotently(tmp_path):
    instr, agents_md = _setup(tmp_path)
    agents_md.write_text(f"Header.\n\n{BEGIN}\nstale content\n{END}\n\nFooter.\n")
    project_block(instr, agents_md)
    text = agents_md.read_text()
    assert "Header." in text
    assert "Footer." in text
    assert "stale content" not in text
    assert "Body alpha." in text
