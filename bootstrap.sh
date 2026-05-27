#!/usr/bin/env bash
set -euo pipefail

# --- arg parsing ---
AGENT_OVERRIDE=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --agent)
      AGENT_OVERRIDE="${2:-}"
      shift 2
      ;;
    --agent=*)
      AGENT_OVERRIDE="${1#--agent=}"
      shift
      ;;
    -h|--help)
      cat <<USAGE
usage: bootstrap.sh [--agent claude|pi|both]

  --agent <name>   skip the prompt and configure only the named agent(s).
                   one of: claude, pi, both. when both agents are detected
                   and --agent is not passed, bootstrap prompts interactively.
USAGE
      exit 0
      ;;
    *)
      echo "error: unknown argument: $1" >&2
      echo "run with --help for usage" >&2
      exit 2
      ;;
  esac
done

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOSTNAME_SHORT="$(hostname -s)"
MACHINE_FILE="$REPO_DIR/.machine-$HOSTNAME_SHORT"
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BACKUP_DIR="$HOME/.appa-backups/pre-bootstrap-$TIMESTAMP"

if ! command -v uv >/dev/null 2>&1; then
  echo "error: 'uv' not found on PATH" >&2
  echo "install: curl -LsSf https://astral.sh/uv/install.sh | sh" >&2
  exit 1
fi

HAVE_CLAUDE=0
HAVE_PI=0
command -v claude >/dev/null 2>&1 && HAVE_CLAUDE=1
command -v pi >/dev/null 2>&1 && HAVE_PI=1

if [[ $HAVE_CLAUDE -eq 0 && $HAVE_PI -eq 0 ]]; then
  echo "error: neither 'claude' nor 'pi' installed" >&2
  echo "install at least one agent before running bootstrap" >&2
  exit 1
fi

# --- apply --agent override or prompt when both detected ---
if [[ -n "$AGENT_OVERRIDE" ]]; then
  case "$AGENT_OVERRIDE" in
    claude) HAVE_PI=0 ;;
    pi)     HAVE_CLAUDE=0 ;;
    both)   ;;
    *)
      echo "error: --agent must be one of: claude, pi, both (got: $AGENT_OVERRIDE)" >&2
      exit 2
      ;;
  esac
  if [[ $HAVE_CLAUDE -eq 0 && $HAVE_PI -eq 0 ]]; then
    echo "error: --agent $AGENT_OVERRIDE selected, but that agent is not installed" >&2
    exit 1
  fi
elif [[ $HAVE_CLAUDE -eq 1 && $HAVE_PI -eq 1 ]]; then
  echo "Both 'claude' and 'pi' are installed. Which should appa configure?"
  echo "  1) pi only"
  echo "  2) claude only"
  echo "  3) both"
  read -r -p "Choice [3]: " choice
  choice="${choice:-3}"
  case "$choice" in
    1) HAVE_CLAUDE=0 ;;
    2) HAVE_PI=0 ;;
    3) ;;
    *)
      echo "error: invalid choice '$choice'; expected 1, 2, or 3" >&2
      exit 1
      ;;
  esac
fi

HAVE_PLANNOTATOR=0
if command -v plannotator >/dev/null 2>&1; then
  HAVE_PLANNOTATOR=1
else
  echo "note: 'plannotator' CLI binary not on PATH" >&2
  echo "      needed if you invoke plannotator directly or via claude slash commands (/plannotator-review etc.)" >&2
  echo "      pi-coding-agent's plannotator extension is a separate install and doesn't require the CLI" >&2
  echo "      install the CLI: curl -fsSL https://plannotator.ai/install.sh | bash" >&2
fi

echo "appa bootstrap: repo=$REPO_DIR host=$HOSTNAME_SHORT claude=$HAVE_CLAUDE pi=$HAVE_PI uv=1 plannotator=$HAVE_PLANNOTATOR"

# --- sync venv ---
echo "uv sync ..."
( cd "$REPO_DIR" && uv sync --quiet )

# --- symlink helper ---
_link() {
  local src="$1" dst="$2"
  if [[ -L "$dst" ]]; then
    if [[ "$(readlink "$dst")" == "$src" ]]; then
      return 0
    fi
    rm "$dst"
  elif [[ -e "$dst" ]]; then
    # Mirror the path under HOME inside BACKUP_DIR so different source paths with the
    # same basename (e.g. ~/.claude/skills and ~/.pi/agent/skills) don't collide.
    local rel="${dst#$HOME/}"
    local backup_target="$BACKUP_DIR/$rel"
    mkdir -p "$(dirname "$backup_target")"
    mv "$dst" "$backup_target"
    echo "  backed up: $dst -> $backup_target"
  fi
  mkdir -p "$(dirname "$dst")"
  ln -s "$src" "$dst"
  echo "  linked:    $dst -> $src"
}

# --- claude symlinks ---
if [[ $HAVE_CLAUDE -eq 1 ]]; then
  echo "claude: linking shared content"
  _link "$REPO_DIR/commands"                    "$HOME/.claude/commands"
  _link "$REPO_DIR/skills"                      "$HOME/.claude/skills"
  _link "$REPO_DIR/agents/claude/settings.json" "$HOME/.claude/settings.json"
  if [[ -s "$REPO_DIR/agents/claude/CLAUDE.md" ]]; then
    _link "$REPO_DIR/agents/claude/CLAUDE.md" "$HOME/.claude/CLAUDE.md"
  fi
fi

# --- pi symlinks ---
# Note: pi's settings.json is managed per-machine, not in appa.
# Pi skills come from agents/pi/skills/ (cherry-picked from superpowers); appa/skills/ is reserved for shared user-authored skills.
if [[ $HAVE_PI -eq 1 ]]; then
  echo "pi: linking shared content"
  _link "$REPO_DIR/commands"         "$HOME/.pi/agent/prompts"
  _link "$REPO_DIR/agents/pi/skills" "$HOME/.pi/agent/skills"
fi

# --- install appa CLI via uv tool ---
# Migrate from the older design (symlink at ~/.local/bin/appa -> $REPO_DIR/.venv/bin/appa):
# if such a symlink exists, remove it so `uv tool install` doesn't refuse to overwrite.
if [[ -L "$HOME/.local/bin/appa" ]]; then
  link_target="$(readlink "$HOME/.local/bin/appa")"
  if [[ "$link_target" == "$REPO_DIR/.venv/bin/appa" ]]; then
    rm "$HOME/.local/bin/appa"
    echo "  removed stale symlink: ~/.local/bin/appa -> $link_target"
  fi
fi

echo "installing appa CLI via uv tool ..."
uv tool install --editable "$REPO_DIR" --force --quiet

case ":$PATH:" in
  *":$HOME/.local/bin:"*) ;;
  *)
    echo
    echo "note: $HOME/.local/bin is not on PATH. Add to your shell profile:"
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
    ;;
esac

# --- claude plugin install ---
if [[ $HAVE_CLAUDE -eq 1 ]]; then
  echo "claude: ensuring marketplaces and plugins"
  ( cd "$REPO_DIR" && uv run python - "$REPO_DIR/agents/claude/settings.json" ) <<'PY'
import json, subprocess, sys
settings = json.loads(open(sys.argv[1]).read())
for name, mp in (settings.get("extraKnownMarketplaces") or {}).items():
    src = mp.get("source", {})
    if src.get("source") == "github":
        target = src.get("repo")
    else:
        print(f"  marketplace {name}: unsupported source {src.get('source')!r}", file=sys.stderr)
        continue
    print(f"  marketplace add: {name} <- {target}", flush=True)
    subprocess.run(["claude", "plugin", "marketplace", "add", target], check=False)
seen_marketplaces = set()
for plugin_id, enabled in (settings.get("enabledPlugins") or {}).items():
    if not enabled:
        continue
    if "@" in plugin_id:
        mp_name = plugin_id.split("@", 1)[1]
        if mp_name not in seen_marketplaces:
            seen_marketplaces.add(mp_name)
            print(f"  marketplace update: {mp_name}", flush=True)
            subprocess.run(["claude", "plugin", "marketplace", "update", mp_name], check=False)
    print(f"  plugin install: {plugin_id}", flush=True)
    subprocess.run(["claude", "plugin", "install", plugin_id], check=False)
PY
fi

# --- project instructions to pi (claude-side projection deferred) ---
if [[ $HAVE_PI -eq 1 ]]; then
  echo "pi: projecting instructions to ~/.pi/agent/AGENTS.md"
  ( cd "$REPO_DIR" && uv run python -c "
from pathlib import Path
from appa_lib.project_pi import project_pi
project_pi(Path('instructions'), Path.home() / '.pi/agent/AGENTS.md')
" )
fi

# --- summary ---
echo
echo "appa bootstrap complete."
[[ -d "$BACKUP_DIR" ]] && echo "  backups:               $BACKUP_DIR"
[[ $HAVE_CLAUDE -eq 1 ]] && echo "  claude:                wired (symlinks + plugins; memory projection deferred)"
[[ $HAVE_PI -eq 1 ]] && echo "  pi:                    wired"
echo "  appa CLI:              $HOME/.local/bin/appa"
