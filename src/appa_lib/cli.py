import argparse
import os
import shutil
import sys
from pathlib import Path

from appa_lib.encode_path import encode_path
from appa_lib.project_claude import project_claude
from appa_lib.project_pi import project_pi


REPO_DIR = Path(__file__).resolve().parent.parent.parent
HOSTNAME = os.uname().nodename.split(".")[0]
MACHINE_FILE = REPO_DIR / f".machine-{HOSTNAME}"


def _have(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def _primary_wd() -> str:
    if not MACHINE_FILE.exists():
        sys.exit(f"error: {MACHINE_FILE} missing; run ./bootstrap.sh first")
    for line in MACHINE_FILE.read_text().splitlines():
        if line.startswith("primary_wd="):
            return line.split("=", 1)[1].strip()
    sys.exit(f"error: {MACHINE_FILE} has no primary_wd; re-run bootstrap")


def _project_for_claude() -> None:
    target = Path.home() / ".claude/projects" / encode_path(_primary_wd()) / "memory"
    target.mkdir(parents=True, exist_ok=True)
    project_claude(REPO_DIR / "instructions", target, machine_scope="global")
    print(f"claude: projected -> {target}")


def _project_for_pi() -> None:
    agents_md = Path.home() / ".pi/agent/AGENTS.md"
    agents_md.parent.mkdir(parents=True, exist_ok=True)
    project_pi(REPO_DIR / "instructions", agents_md)
    print(f"pi: projected -> {agents_md}")


def cmd_sync(args: argparse.Namespace) -> None:
    # TODO: if both are present. can be deferred to v2
    if _have("claude"):
        _project_for_claude()
    if _have("pi"):
        _project_for_pi()


def cmd_bootstrap(args: argparse.Namespace) -> None:
    script = REPO_DIR / "bootstrap.sh"
    os.execv(str(script), [str(script)])


def main() -> None:
    parser = argparse.ArgumentParser(prog="appa", description="Portable coding-agent workflow")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("bootstrap", help="run bootstrap.sh")
    sub.add_parser("sync", help="re-project instructions to detected agents")

    args = parser.parse_args()
    dispatch = {
        "bootstrap": cmd_bootstrap,
        "sync": cmd_sync,
    }
    dispatch[args.cmd](args)
