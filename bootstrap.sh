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
