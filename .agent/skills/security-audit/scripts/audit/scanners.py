"""Core scanning functions for the security audit scanner."""

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict

from . import config as _config
from .config import (
    CODE_EXTENSIONS,
    CONFIG_EXTENSIONS,
    IAC_EXTENSIONS,
    IAC_FILENAMES,
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

    # Ecosystem -> (type markers, accepted lock files).
    # `requirements.txt` lists deps but does NOT pin a full transitive graph
    # with hashes, so it is NOT counted as a lock file by default. Exception:
    # pip-compile output with `--hash=sha256:` lines IS effectively a lock.
    ecosystems = {
        "javascript": {
            "markers": ["package.json"],
            "locks": ["package-lock.json", "npm-shrinkwrap.json", "yarn.lock", "pnpm-lock.yaml"],
        },
        "python": {
            "markers": ["pyproject.toml", "setup.py", "setup.cfg", "requirements.txt", "Pipfile"],
            "locks": ["Pipfile.lock", "poetry.lock", "uv.lock", "pdm.lock"],
        },
        "rust": {
            "markers": ["Cargo.toml"],
            "locks": ["Cargo.lock"],
        },
        "go": {
            "markers": ["go.mod"],
            "locks": ["go.sum"],
        },
    }

    def _python_has_hash_pinned_requirements(base: Path) -> bool:
        """pip-compile output: requirements.txt with `--hash=sha256:` is a de-facto lock."""
        req = base / "requirements.txt"
        if not req.exists():
            return False
        try:
            with open(req, 'r', encoding='utf-8', errors='ignore') as f:
                # Stop scanning after 1MB; hash lines appear early in real pip-compile output.
                sample = f.read(1024 * 1024)
            return '--hash=sha256:' in sample
        except OSError:
            return False

    for eco, spec in ecosystems.items():
        base = Path(project_path)
        is_type = any((base / m).exists() for m in spec["markers"])
        if not is_type:
            continue
        has_lock = any((base / f).exists() for f in spec["locks"])
        if not has_lock and eco == "python" and _python_has_hash_pinned_requirements(base):
            has_lock = True  # pip-compile hash-pinned requirements.txt counts as lock
        if not has_lock:
            results["findings"].append({
                "type": "Missing Lock File",
                "severity": "high",
                "cwe": "CWE-1104",
                "message": f"{eco}: No lock file found (expected one of: {', '.join(spec['locks'])}). Supply chain integrity at risk."
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
                if filepath.stat().st_size > _config.MAX_FILE_SIZE:
                    results["skipped_files"] += 1
                    print(f"[WARN] Skipped {filepath}: exceeds {_config.MAX_FILE_SIZE // (1024*1024)}MB limit", file=sys.stderr)
                    continue
            except OSError:
                continue

            results["scanned_files"] += 1

            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    # ReDoS guard: filter out pathologically long lines before regex.
                    # All SECRET_PATTERNS are line-local (no multi-line matches in the
                    # current pattern set, including BEGIN...KEY which is one-line marker).
                    safe_lines = [
                        ln for ln in content.splitlines()
                        if len(ln) <= _config.MAX_LINE_LENGTH
                    ]
                    safe_content = "\n".join(safe_lines)
                    skipped_lines = content.count("\n") + 1 - len(safe_lines)
                    if skipped_lines > 0:
                        print(f"[WARN] {filepath}: skipped {skipped_lines} line(s) > {_config.MAX_LINE_LENGTH} chars (ReDoS guard)", file=sys.stderr)
                    for pattern, secret_type, severity, cwe in SECRET_PATTERNS:
                        matches = re.findall(pattern, safe_content, re.IGNORECASE)
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
                    for match in re.finditer(entropy_pattern, safe_content, re.IGNORECASE):
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
                if filepath.stat().st_size > _config.MAX_FILE_SIZE:
                    results["skipped_files"] += 1
                    print(f"[WARN] Skipped {filepath}: exceeds {_config.MAX_FILE_SIZE // (1024*1024)}MB limit", file=sys.stderr)
                    continue
            except OSError:
                continue

            results["scanned_files"] += 1

            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    for line_num, line in enumerate(lines, 1):
                        # ReDoS guard: skip pathologically long lines (minified bundles, token blobs).
                        if len(line) > _config.MAX_LINE_LENGTH:
                            continue
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
                if filepath.stat().st_size > _config.MAX_FILE_SIZE:
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
                if filepath.stat().st_size > _config.MAX_FILE_SIZE:
                    results["skipped_files"] += 1
                    continue
            except OSError:
                continue

            results["scanned_files"] += 1

            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                    # ReDoS guard: IaC patterns may span lines (re.MULTILINE). Instead of
                    # filtering lines (breaks multi-line patterns), skip the entire file
                    # if any line is pathologically long. Legit YAML/Dockerfile/Terraform
                    # never has >4k-char lines; only minified blobs do.
                    if any(len(ln) > _config.MAX_LINE_LENGTH for ln in content.splitlines()):
                        results["skipped_files"] += 1
                        print(f"[WARN] Skipped IaC {filepath}: line > {_config.MAX_LINE_LENGTH} chars (ReDoS guard)", file=sys.stderr)
                        continue

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
    """Check for SBOM presence recursively via os.walk with early SKIP_DIRS prune.

    Uses os.walk (not Path.rglob) because rglob traverses SKIP_DIRS first and only
    filters after yielding — on a monorepo with node_modules, that is O(millions).
    os.walk with `dirs[:] = ...` pruning skips those subtrees entirely.
    """
    results = {
        "tool": "sbom_scanner",
        "findings": [],
        "status": "[OK] SBOM check passed",
    }

    # Compiled fnmatch-style checks; case-insensitive so "SBOM.json" is caught.
    sbom_patterns_re = [
        re.compile(r'.*sbom.*', re.IGNORECASE),
        re.compile(r'^bom\.(?:json|xml)$', re.IGNORECASE),
        re.compile(r'.*\.spdx.*', re.IGNORECASE),
        re.compile(r'.*\.cdx\..*', re.IGNORECASE),
        re.compile(r'^cyclonedx-bom\..*$', re.IGNORECASE),
    ]

    sbom_files = []
    for current_dir, dirs, files in os.walk(project_path, followlinks=False):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if any(rx.match(f) for rx in sbom_patterns_re):
                sbom_files.append(Path(current_dir) / f)

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

    return results
