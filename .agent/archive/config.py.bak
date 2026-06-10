"""Configuration constants for the security audit scanner."""

from pathlib import Path

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}

SKIP_DIRS = {
    'node_modules', '.git', 'dist', 'build', '__pycache__', '.venv', 'venv', '.next',
    '.cache', '.idea', '.vscode', 'vendor', 'tmp', 'coverage', '.tox', '.mypy_cache',
    '.terraform', '.pulumi',
}

CODE_EXTENSIONS = {
    '.js', '.ts', '.jsx', '.tsx', '.py', '.go', '.java',
    '.rb', '.php', '.sol', '.rs', '.cs', '.swift',
}

CONFIG_EXTENSIONS = {
    '.json', '.yaml', '.yml', '.toml',
    '.env', '.env.local', '.env.development', '.env.production',
}

IAC_EXTENSIONS = {'.tf', '.tfvars', '.yaml', '.yml', '.json'}

IAC_FILENAMES = {
    'Dockerfile', 'docker-compose.yml', 'docker-compose.yaml', '.dockerignore',
    'Containerfile', 'kustomization.yaml', 'kustomization.yml',
}

# Self-exclusion: skip the scanner's ENTIRE skill directory (scripts + tests +
# fixtures that intentionally contain "bad" patterns as regression evidence).
# __file__ = .../security-audit/scripts/audit/config.py
# .parent.parent.parent = .../security-audit/ (skill root)
SELF_DIR = str(Path(__file__).resolve().parent.parent.parent)

# Max file size to scan (15MB default). Minified production bundles
# (vendor.js, bundle.js) can be 10-25MB; 5MB skipped too many of them.
# Mutable so CLI can override via --max-size (see run_audit.py).
MAX_FILE_SIZE = 15 * 1024 * 1024

# ReDoS guard: lines longer than this are skipped during pattern scanning.
# Minified JS lines regularly exceed 100k chars and trigger catastrophic backtracking
# on some patterns. Real source code lines almost never exceed 4k chars.
MAX_LINE_LENGTH = 4000
