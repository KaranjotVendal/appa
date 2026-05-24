from pathlib import Path

from appa_lib.project_claude import project_claude


CANONICAL = """---
name: per-task-approval
scope: global
type: feedback
description: Wait for go-ahead per task.
---

Body content.
"""


def _make_instr(tmp_path: Path, name: str, body: str) -> Path:
    p = tmp_path / "instructions"
    p.mkdir(exist_ok=True)
    (p / f"{name}.md").write_text(body)
    return p


def test_writes_claude_formatted_file(tmp_path):
    instr = _make_instr(tmp_path, "per-task-approval", CANONICAL)
    target = tmp_path / "memory"
    target.mkdir()
    project_claude(instr, target, machine_scope="global")
    out = (target / "per-task-approval.md").read_text()
    assert "name: per-task-approval" in out
    assert 'description: "Wait for go-ahead per task."' in out
    assert "metadata:" in out
    assert "type: feedback" in out
    assert "scope:" not in out
    assert out.rstrip().endswith("Body content.")


def test_regenerates_memory_index(tmp_path):
    instr = _make_instr(tmp_path, "per-task-approval", CANONICAL)
    target = tmp_path / "memory"
    target.mkdir()
    project_claude(instr, target, machine_scope="global")
    index = (target / "MEMORY.md").read_text()
    assert "- [per-task-approval](per-task-approval.md) — Wait for go-ahead per task." in index


def test_skips_non_matching_scope(tmp_path):
    instr = _make_instr(tmp_path, "alpha", CANONICAL.replace("per-task-approval", "alpha"))
    (instr / "beta.md").write_text(
        CANONICAL.replace("scope: global", "scope: -other-machine").replace("per-task-approval", "beta")
    )
    target = tmp_path / "memory"
    target.mkdir()
    project_claude(instr, target, machine_scope="global")
    assert not (target / "beta.md").exists()
    assert (target / "alpha.md").exists()
