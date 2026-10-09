"""Security Audit Scanner — modular static analysis engine.

Single source of truth for package version. SKILL.md frontmatter and
run_audit.py CLI header must match `__version__` on each release.
"""

__version__ = "3.12"

from .config import SEVERITY_ORDER
from .scanners import (
    scan_dependencies,
    scan_secrets,
    scan_code_patterns,
    scan_configuration,
    scan_iac,
    scan_mcp_agentic,
    scan_sbom,
)
from .external import external_section, find_git_entry, incomplete_slots, run_external_tools
from .helpers import detect_project_types, printable

__all__ = [
    "__version__",
    "SEVERITY_ORDER",
    "scan_dependencies",
    "scan_secrets",
    "scan_code_patterns",
    "scan_configuration",
    "scan_iac",
    "scan_mcp_agentic",
    "scan_sbom",
    "run_external_tools",
    "external_section",
    "find_git_entry",
    "incomplete_slots",
    "printable",
    "detect_project_types",
]
