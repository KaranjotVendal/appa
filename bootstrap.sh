#!/usr/bin/env bash
set -euo pipefail

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

HAVE_PLANNOTATOR=0
if command -v plannotator >/dev/null 2>&1; then
  HAVE_PLANNOTATOR=1
else
  echo "note: 'plannotator' CLI not found on PATH" >&2
  echo "      the plannotator plugin/extension will install but its skills won't work end-to-end" >&2
  echo "      install: curl -fsSL https://plannotator.ai/install.sh | bash" >&2
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
    mkdir -p "$BACKUP_DIR"
    mv "$dst" "$BACKUP_DIR/"
    echo "  backed up: $dst -> $BACKUP_DIR/"
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
if [[ $HAVE_PI -eq 1 ]]; then
  echo "pi: linking shared content"
  _link "$REPO_DIR/commands" "$HOME/.pi/agent/prompts"
  _link "$REPO_DIR/skills"   "$HOME/.pi/agent/skills"
fi

# --- install appa CLI symlink ---
mkdir -p "$HOME/.local/bin"
_link "$REPO_DIR/.venv/bin/appa" "$HOME/.local/bin/appa"

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
for plugin_id, enabled in (settings.get("enabledPlugins") or {}).items():
    if not enabled:
        continue
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
