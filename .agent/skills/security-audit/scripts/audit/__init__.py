"""Security Audit Scanner v3.0 — modular static analysis engine."""

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
