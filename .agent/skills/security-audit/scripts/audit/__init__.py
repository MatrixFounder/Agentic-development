"""Security Audit Scanner — modular static analysis engine.

Single source of truth for package version. SKILL.md frontmatter and
run_audit.py CLI header must match `__version__` on each release.
"""

__version__ = "3.3"

from .config import SEVERITY_ORDER
from .scanners import (
    scan_dependencies,
    scan_secrets,
    scan_code_patterns,
    scan_configuration,
    scan_iac,
    scan_sbom,
)
from .external import run_external_tools
from .helpers import detect_project_types

__all__ = [
    "__version__",
    "SEVERITY_ORDER",
    "scan_dependencies",
    "scan_secrets",
    "scan_code_patterns",
    "scan_configuration",
    "scan_iac",
    "scan_sbom",
    "run_external_tools",
    "detect_project_types",
]
