import pytest

from appa_lib.transform_pull import transform_pull


CLAUDE_INPUT = """---
name: per-task-approval
description: "Wait for explicit go-ahead per task."
metadata:
  node_type: memory
  type: feedback
  originSessionId: abc-123
---

Body line one.

Body line two.
"""

EXPECTED_OUTPUT = """---
name: per-task-approval
scope: global
type: feedback
description: Wait for explicit go-ahead per task.
---

Body line one.

Body line two.
"""


def test_drops_machine_specific_metadata():
    assert transform_pull(CLAUDE_INPUT, scope="global") == EXPECTED_OUTPUT


def test_uses_first_body_line_when_description_missing():
    src = """---
name: example
metadata:
  type: project
---

This is the first line.

Second line.
"""
    out = transform_pull(src, scope="global")
    assert "description: This is the first line." in out


def test_preserves_per_project_scope():
    out = transform_pull(CLAUDE_INPUT, scope="-Users-x-dev")
    assert "scope: -Users-x-dev" in out


def test_rejects_missing_frontmatter():
    with pytest.raises(ValueError):
        transform_pull("no frontmatter here\n", scope="global")
