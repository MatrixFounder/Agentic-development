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
  echo "python3 not found. Install Python 3.11 or newer (3.14 is the main version) and retry." >&2
  exit 2
fi

# The minimum Python, stated in README §3. It is checked before the installer runs.
if ! python3 - <<'PY'
import sys
if sys.version_info < (3, 11):
    sys.stderr.write("Python %d.%d found. The framework needs Python 3.11 or newer"
                     " (3.14 is the main version).\n" % tuple(sys.version_info[:2]))
    sys.exit(1)
PY
then
  exit 2
fi

# -P (Python 3.11+, checked above): import nothing from the current directory, which is the
# target project.
if ! python3 -P -c "import yaml" >/dev/null 2>&1; then
  echo "PyYAML not found. Install it with: pip3 install --user pyyaml" >&2
  exit 2
fi

exec python3 "$SCRIPT_DIR/System/scripts/install.py" --installer-script-dir "$SCRIPT_DIR" "$@"
