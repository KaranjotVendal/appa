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


def _claude_memory_dir() -> Path:
    return Path.home() / ".claude/projects" / encode_path(_primary_wd()) / "memory"


def _print_diff(name: str, ours: str, theirs: str) -> None:
    print()
    print(f"CONFLICT: {name}")
    print("----- canonical (ours) -----")
    print(ours, end="")
    print("----- live (theirs) --------")
    print(theirs, end="")
    print("----------------------------")


def cmd_memory_pull(args: argparse.Namespace) -> None:
    if not _have("claude"):
        sys.exit("memory pull is claude-only; claude not detected")
    from appa_lib.transform_pull import transform_pull

    live = _claude_memory_dir()
    snap = REPO_DIR / "memory/snapshot"
    snap.mkdir(parents=True, exist_ok=True)
    for old in snap.iterdir():
        if old.is_file():
            old.unlink()
    for src in live.iterdir():
        if src.is_file():
            (snap / src.name).write_text(src.read_text())

    conflicts = 0
    for src in sorted(live.glob("*.md")):
        if src.name == "MEMORY.md":
            continue
        base = src.stem
        if base.startswith("feedback_"):
            base = base[len("feedback_") :]
        canonical = REPO_DIR / "instructions" / f"{base}.md"
        rendered = transform_pull(src.read_text(), scope="global")
        if not canonical.exists():
            canonical.write_text(rendered)
            print(f"  pulled (new):    {base}")
            continue
        existing = canonical.read_text()
        if existing == rendered:
            continue
        if args.theirs:
            canonical.write_text(rendered)
            print(f"  pulled (theirs): {base}")
        elif args.ours:
            print(f"  kept (ours):     {base}")
        else:
            _print_diff(base, existing, rendered)
            conflicts += 1
    if conflicts:
        sys.exit(3)


def main() -> None:
    parser = argparse.ArgumentParser(prog="appa", description="Portable coding-agent workflow")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("bootstrap", help="run bootstrap.sh")
    sub.add_parser("sync", help="re-project instructions to detected agents")

    p_mem = sub.add_parser("memory", help="memory operations (claude-only)")
    sub_mem = p_mem.add_subparsers(dest="mem_cmd", required=True)
    p_pull = sub_mem.add_parser("pull")
    p_pull.add_argument("--theirs", action="store_true")
    p_pull.add_argument("--ours", action="store_true")

    args = parser.parse_args()
    if args.cmd == "memory":
        {"pull": cmd_memory_pull}[args.mem_cmd](args)
        return
    dispatch = {
        "bootstrap": cmd_bootstrap,
        "sync": cmd_sync,
    }
    dispatch[args.cmd](args)
