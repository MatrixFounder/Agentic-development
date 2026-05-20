#!/usr/bin/env bash
# agentic-development framework installer (bash wrapper).
# Plan: /Users/sergey/.claude/plans/snug-foraging-wind.md
set -euo pipefail

if [ -z "${BASH_VERSION:-}" ]; then
  echo "This installer requires bash. Run it as: bash install.sh ..." >&2
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 not found. Install Python >= 3.9 and retry." >&2
  exit 2
fi

if ! python3 -c "import yaml" >/dev/null 2>&1; then
  echo "PyYAML not found. Install it with: pip3 install --user pyyaml" >&2
  exit 2
fi

exec python3 "$SCRIPT_DIR/System/scripts/install.py" --installer-script-dir "$SCRIPT_DIR" "$@"
