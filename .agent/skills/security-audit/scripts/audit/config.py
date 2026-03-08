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

# Self-exclusion: skip the scanner's own directory to prevent false positives
SELF_DIR = str(Path(__file__).resolve().parent.parent)

# Max file size to scan (5MB) — prevents OOM on large minified bundles
MAX_FILE_SIZE = 5 * 1024 * 1024
