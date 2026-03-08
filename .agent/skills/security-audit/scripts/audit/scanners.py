"""Core scanning functions for the security audit scanner."""

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict

from .config import (
    CODE_EXTENSIONS,
    CONFIG_EXTENSIONS,
    IAC_EXTENSIONS,
    IAC_FILENAMES,
    MAX_FILE_SIZE,
    SEVERITY_ORDER,
    SKIP_DIRS,
)
from .helpers import is_self_path, shannon_entropy, sort_findings_by_severity
from .patterns import (
    CONFIG_PATTERNS,
    DANGEROUS_PATTERNS,
    IAC_PATTERNS,
    SECRET_PATTERNS,
)


def scan_dependencies(project_path: str) -> Dict[str, Any]:
    """Validate supply chain security (OWASP A06/A08, CWE-1104)."""
    results = {"tool": "dependency_scanner", "findings": [], "status": "[OK] Secure"}

    lock_files = {
        "npm": ["package-lock.json", "npm-shrinkwrap.json"],
        "yarn": ["yarn.lock"],
        "pnpm": ["pnpm-lock.yaml"],
        "pip": ["requirements.txt", "Pipfile.lock", "poetry.lock", "uv.lock"],
        "rust": ["Cargo.lock"],
        "go": ["go.sum"],
    }

    for manager, files in lock_files.items():
        if manager == "pip" and (Path(project_path) / "requirements.txt").exists():
            continue

        is_type = False
        if manager in ["npm", "yarn", "pnpm"] and (Path(project_path) / "package.json").exists():
            is_type = True
        elif manager == "rust" and (Path(project_path) / "Cargo.toml").exists():
            is_type = True
        elif manager == "go" and (Path(project_path) / "go.mod").exists():
            is_type = True

        if is_type:
            has_lock = any((Path(project_path) / f).exists() for f in files)
            if not has_lock:
                results["findings"].append({
                    "type": "Missing Lock File",
                    "severity": "high",
                    "cwe": "CWE-1104",
                    "message": f"{manager}: No lock file found. Supply chain integrity at risk."
                })

    # Run npm audit if applicable
    if (Path(project_path) / "package.json").exists():
        try:
            result = subprocess.run(
                ["npm", "audit", "--json"],
                cwd=project_path,
                capture_output=True, text=True, timeout=60
            )
            try:
                audit_data = json.loads(result.stdout)
                vulnerabilities = audit_data.get("vulnerabilities", {})
                severity_count = {"critical": 0, "high": 0}
                for vuln in vulnerabilities.values():
                    sev = vuln.get("severity", "low").lower()
                    if sev in severity_count:
                        severity_count[sev] += 1

                if severity_count["critical"] > 0:
                    results["status"] = "[!!] Critical vulnerabilities"
                    results["findings"].append({
                        "type": "npm audit",
                        "severity": "critical",
                        "cwe": "CWE-1104",
                        "message": f"{severity_count['critical']} critical vulnerabilities in dependencies"
                    })
                elif severity_count["high"] > 0:
                    results["findings"].append({
                        "type": "npm audit",
                        "severity": "high",
                        "cwe": "CWE-1104",
                        "message": f"{severity_count['high']} high vulnerabilities in dependencies"
                    })
            except json.JSONDecodeError:
                pass
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

    if results["findings"]:
        max_sev = min(SEVERITY_ORDER.get(f.get("severity", "low"), 99) for f in results["findings"])
        if max_sev == 0:
            results["status"] = "[!!] Critical vulnerabilities"
        elif max_sev == 1:
            results["status"] = "[!] HIGH: Dependency issues"

    return results


def scan_secrets(project_path: str) -> Dict[str, Any]:
    """Validate no hardcoded secrets (OWASP A02, CWE-798)."""
    results = {
        "tool": "secret_scanner",
        "findings": [],
        "status": "[OK] No secrets detected",
        "scanned_files": 0,
        "skipped_files": 0,
        "by_severity": {"critical": 0, "high": 0}
    }

    for root, dirs, files in os.walk(project_path, followlinks=False):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for file in files:
            ext = Path(file).suffix.lower()
            if ext not in CODE_EXTENSIONS and ext not in CONFIG_EXTENSIONS:
                continue

            filepath = Path(root) / file

            if is_self_path(str(filepath)):
                continue

            try:
                if filepath.stat().st_size > MAX_FILE_SIZE:
                    results["skipped_files"] += 1
                    print(f"[WARN] Skipped {filepath}: exceeds {MAX_FILE_SIZE // (1024*1024)}MB limit", file=sys.stderr)
                    continue
            except OSError:
                continue

            results["scanned_files"] += 1

            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    for pattern, secret_type, severity, cwe in SECRET_PATTERNS:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        if matches:
                            results["findings"].append({
                                "file": str(filepath.relative_to(project_path)),
                                "type": secret_type,
                                "severity": severity,
                                "cwe": cwe,
                                "count": len(matches)
                            })
                            if severity in results["by_severity"]:
                                results["by_severity"][severity] += len(matches)

                    # High-entropy string detection for suspicious variable names
                    entropy_pattern = r'(?:secret|private[_-]?key|auth[_-]?token|api[_-]?key|password|credential)\s*[=:]\s*["\']([^"\']{16,})["\']'
                    for match in re.finditer(entropy_pattern, content, re.IGNORECASE):
                        value = match.group(1)
                        entropy = shannon_entropy(value)
                        if entropy > 4.5:
                            results["findings"].append({
                                "file": str(filepath.relative_to(project_path)),
                                "type": "High-Entropy Secret",
                                "severity": "high",
                                "cwe": "CWE-798",
                                "count": 1,
                                "entropy": round(entropy, 2)
                            })
                            results["by_severity"]["high"] += 1
            except Exception as e:
                results["skipped_files"] += 1
                print(f"[WARN] Skipped {filepath}: {e}", file=sys.stderr)

    results["findings"] = sort_findings_by_severity(results["findings"])

    if results["by_severity"]["critical"] > 0:
        results["status"] = "[!!] CRITICAL: Secrets exposed!"
    elif results["by_severity"]["high"] > 0:
        results["status"] = "[!] HIGH: Secrets found"

    return results


def scan_code_patterns(project_path: str) -> Dict[str, Any]:
    """Validate dangerous code patterns (OWASP A03 Injection, CWE-79/89/78)."""
    results = {
        "tool": "pattern_scanner",
        "findings": [],
        "status": "[OK] No dangerous patterns",
        "scanned_files": 0,
        "skipped_files": 0
    }

    for root, dirs, files in os.walk(project_path, followlinks=False):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for file in files:
            ext = Path(file).suffix.lower()
            if ext not in CODE_EXTENSIONS:
                continue

            filepath = Path(root) / file

            if is_self_path(str(filepath)):
                continue

            try:
                if filepath.stat().st_size > MAX_FILE_SIZE:
                    results["skipped_files"] += 1
                    print(f"[WARN] Skipped {filepath}: exceeds {MAX_FILE_SIZE // (1024*1024)}MB limit", file=sys.stderr)
                    continue
            except OSError:
                continue

            results["scanned_files"] += 1

            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    for line_num, line in enumerate(lines, 1):
                        for pattern, name, severity, category, cwe in DANGEROUS_PATTERNS:
                            if re.search(pattern, line, re.IGNORECASE):
                                results["findings"].append({
                                    "file": str(filepath.relative_to(project_path)),
                                    "line": line_num,
                                    "pattern": name,
                                    "severity": severity,
                                    "category": category,
                                    "cwe": cwe,
                                    "snippet": line.strip()[:100]
                                })
            except Exception as e:
                results["skipped_files"] += 1
                print(f"[WARN] Skipped {filepath}: {e}", file=sys.stderr)

    results["findings"] = sort_findings_by_severity(results["findings"])

    critical = sum(1 for f in results["findings"] if f["severity"] == "critical")
    high = sum(1 for f in results["findings"] if f["severity"] == "high")
    if critical > 0:
        results["status"] = f"[!!] CRITICAL: {critical} dangerous patterns"
    elif high > 0:
        results["status"] = f"[!] HIGH: {high} dangerous patterns"
    elif results["findings"]:
        results["status"] = "[?] Patterns found"

    return results


def scan_configuration(project_path: str) -> Dict[str, Any]:
    """Validate security configuration (OWASP A05 Misconfiguration, CWE-16)."""
    results = {"tool": "config_scanner", "findings": [], "status": "[OK] Config secure", "skipped_files": 0}

    for root, dirs, files in os.walk(project_path, followlinks=False):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for file in files:
            ext = Path(file).suffix.lower()
            if ext not in CONFIG_EXTENSIONS:
                continue

            filepath = Path(root) / file

            if is_self_path(str(filepath)):
                continue

            try:
                if filepath.stat().st_size > MAX_FILE_SIZE:
                    results["skipped_files"] += 1
                    continue
            except OSError:
                continue

            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    for pattern, issue, severity, cwe in CONFIG_PATTERNS:
                        if re.search(pattern, content, re.IGNORECASE):
                            results["findings"].append({
                                "file": str(filepath.relative_to(project_path)),
                                "issue": issue,
                                "severity": severity,
                                "cwe": cwe,
                            })
            except Exception as e:
                results["skipped_files"] += 1
                print(f"[WARN] Skipped {filepath}: {e}", file=sys.stderr)

    results["findings"] = sort_findings_by_severity(results["findings"])

    if any(f["severity"] == "critical" for f in results["findings"]):
        results["status"] = "[!!] CRITICAL: Config issues"
    elif any(f["severity"] == "high" for f in results["findings"]):
        results["status"] = "[!] HIGH: Config issues"

    return results


def scan_iac(project_path: str) -> Dict[str, Any]:
    """Validate Infrastructure as Code security (Docker, K8s, Terraform)."""
    results = {
        "tool": "iac_scanner",
        "findings": [],
        "status": "[OK] IaC secure",
        "scanned_files": 0,
        "skipped_files": 0,
    }

    for root, dirs, files in os.walk(project_path, followlinks=False):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for file in files:
            filepath = Path(root) / file
            ext = Path(file).suffix.lower()
            is_iac_file = (ext in IAC_EXTENSIONS) or (file in IAC_FILENAMES) or file.startswith("Dockerfile")

            if not is_iac_file:
                continue

            if is_self_path(str(filepath)):
                continue

            try:
                if filepath.stat().st_size > MAX_FILE_SIZE:
                    results["skipped_files"] += 1
                    continue
            except OSError:
                continue

            results["scanned_files"] += 1

            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                    # Heuristic: for generic YAML/JSON files, only apply patterns
                    # matching the detected IaC type (prevents false positives on docs)
                    is_docker = file.startswith("Dockerfile") or file == "Containerfile"
                    is_k8s = re.search(r'apiVersion\s*:', content) is not None
                    is_terraform = ext in {'.tf', '.tfvars'}
                    is_cloudformation = re.search(r'AWSTemplateFormatVersion|Resources\s*:', content) is not None
                    is_compose = file in {'docker-compose.yml', 'docker-compose.yaml'}

                    for pattern, name, severity, category, cwe in IAC_PATTERNS:
                        # Skip category-specific patterns for non-matching file types
                        if category == "Docker" and not (is_docker or is_compose):
                            continue
                        if category == "Kubernetes" and not is_k8s:
                            continue
                        if category == "Terraform" and not is_terraform:
                            continue
                        if category == "CloudFormation" and not is_cloudformation:
                            continue

                        for match in re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE):
                            line_num = content[:match.start()].count('\n') + 1
                            results["findings"].append({
                                "file": str(filepath.relative_to(project_path)),
                                "line": line_num,
                                "pattern": name,
                                "severity": severity,
                                "category": category,
                                "cwe": cwe,
                            })
            except Exception as e:
                results["skipped_files"] += 1
                print(f"[WARN] Skipped {filepath}: {e}", file=sys.stderr)

    results["findings"] = sort_findings_by_severity(results["findings"])

    critical = sum(1 for f in results["findings"] if f["severity"] == "critical")
    high = sum(1 for f in results["findings"] if f["severity"] == "high")
    if critical > 0:
        results["status"] = f"[!!] CRITICAL: {critical} IaC issues"
    elif high > 0:
        results["status"] = f"[!] HIGH: {high} IaC issues"
    elif results["findings"]:
        results["status"] = "[?] IaC patterns found"

    return results


def scan_sbom(project_path: str) -> Dict[str, Any]:
    """Check for SBOM presence and optionally generate one."""
    results = {
        "tool": "sbom_scanner",
        "findings": [],
        "status": "[OK] SBOM check passed",
    }

    sbom_files = list(Path(project_path).glob("*sbom*")) + \
                 list(Path(project_path).glob("bom.json")) + \
                 list(Path(project_path).glob("bom.xml")) + \
                 list(Path(project_path).glob("*.spdx*")) + \
                 list(Path(project_path).glob("*.cdx.*")) + \
                 list(Path(project_path).glob("cyclonedx-bom.*"))

    if not sbom_files:
        results["findings"].append({
            "type": "Missing SBOM",
            "severity": "medium",
            "cwe": "CWE-1104",
            "message": "No SBOM (Software Bill of Materials) found. Required by EU CRA & EO 14028. "
                       "Generate with: npx @cyclonedx/cdxgen -o sbom.json (or syft . -o cyclonedx-json > sbom.json)"
        })
        results["status"] = "[?] SBOM missing"
    else:
        results["status"] = f"[OK] SBOM found: {', '.join(f.name for f in sbom_files[:3])}"

    # Try to run syft or cdxgen if available
    for tool_cmd, tool_name in [
        (["syft", ".", "-o", "json", "--quiet"], "syft"),
        (["npx", "@cyclonedx/cdxgen", "--no-recurse", "-o", "/dev/null"], "cdxgen"),
    ]:
        try:
            result = subprocess.run(
                [tool_cmd[0], "--version"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                print(f"[*] {tool_name} is available for SBOM generation", file=sys.stderr)
                break
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue

    return results
