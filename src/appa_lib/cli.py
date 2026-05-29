import argparse
import datetime
import os
import shutil
import subprocess
import sys
from pathlib import Path

from appa_lib.encode_path import encode_path
from appa_lib.project_claude import project_claude
from appa_lib.project_block import project_block


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


def _project_for_claude() -> bool:
    """Project canonical instructions into claude's per-project memory dir.

    Returns True on success, False if skipped because the machine file is missing
    (claude memory projection is deferred; see spec 'Open work' item).
    """
    if not MACHINE_FILE.exists():
        print(f"  claude: projection deferred (no {MACHINE_FILE.name})")
        return False
    target = Path.home() / ".claude/projects" / encode_path(_primary_wd()) / "memory"
    target.mkdir(parents=True, exist_ok=True)
    project_claude(REPO_DIR / "instructions", target, machine_scope="global")
    print(f"claude: projected -> {target}")
    return True


def _project_for_pi() -> None:
    agents_md = Path.home() / ".pi/agent/AGENTS.md"
    agents_md.parent.mkdir(parents=True, exist_ok=True)
    project_block(REPO_DIR / "instructions", agents_md)
    print(f"pi: projected -> {agents_md}")


def _project_for_claude_global() -> None:
    claude_md = Path.home() / ".claude/CLAUDE.md"
    claude_md.parent.mkdir(parents=True, exist_ok=True)
    project_block(REPO_DIR / "instructions", claude_md)
    print(f"claude: projected -> {claude_md}")


def cmd_sync(args: argparse.Namespace) -> None:
    if _have("claude"):
        _project_for_claude_global()
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
    if not MACHINE_FILE.exists():
        sys.exit(f"error: {MACHINE_FILE} missing; claude memory projection is currently deferred")
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


def cmd_memory_push(args: argparse.Namespace) -> None:
    if not _have("claude"):
        sys.exit("memory push is claude-only; claude not detected")
    if not MACHINE_FILE.exists():
        sys.exit(f"error: {MACHINE_FILE} missing; claude memory projection is currently deferred")
    _project_for_claude()


def cmd_memory_diff(args: argparse.Namespace) -> None:
    subprocess.run(
        ["git", "-C", str(REPO_DIR), "diff", "--", "memory/snapshot/", "instructions/"],
        check=False,
    )


def cmd_commit(args: argparse.Namespace) -> None:
    msg = args.message or f"sync: {HOSTNAME} {datetime.date.today().isoformat()}"
    subprocess.run(["git", "-C", str(REPO_DIR), "add", "-A"], check=True)
    diff = subprocess.run(
        ["git", "-C", str(REPO_DIR), "diff", "--cached", "--quiet"],
        check=False,
    )
    if diff.returncode == 0:
        print("nothing to commit")
        return
    subprocess.run(["git", "-C", str(REPO_DIR), "commit", "-m", msg], check=True)


def cmd_status(args: argparse.Namespace) -> None:
    print("repo:", flush=True)
    subprocess.run(["git", "-C", str(REPO_DIR), "status", "--short"], check=False)
    print()
    print("live memory diff (claude):", flush=True)
    if not _have("claude"):
        print("  claude not present")
    elif not MACHINE_FILE.exists():
        print(f"  deferred (no {MACHINE_FILE.name})")
    else:
        live = _claude_memory_dir()
        subprocess.run(
            ["diff", "-rq", str(REPO_DIR / "memory/snapshot"), str(live)],
            check=False,
        )


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
    sub_mem.add_parser("push")
    sub_mem.add_parser("diff")

    p_commit = sub.add_parser("commit", help="stage + commit tracked files")
    p_commit.add_argument("-m", dest="message", default=None)
    sub.add_parser("status", help="show drift between repo and live state")

    args = parser.parse_args()
    if args.cmd == "memory":
        {
            "pull": cmd_memory_pull,
            "push": cmd_memory_push,
            "diff": cmd_memory_diff,
        }[args.mem_cmd](args)
        return
    dispatch = {
        "bootstrap": cmd_bootstrap,
        "sync": cmd_sync,
        "commit": cmd_commit,
        "status": cmd_status,
    }
    dispatch[args.cmd](args)
