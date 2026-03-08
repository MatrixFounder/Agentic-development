#!/usr/bin/env python3
"""
Skill: security-audit
Script: run_audit.py v3.2
Purpose: CLI entry point for security audit scanner.
Usage: python run_audit.py [project_path] [--scan-type all|deps|secrets|patterns|config|iac|external|sbom]
       [--fail-on critical|high|medium] [--output json|summary] [--no-limit]
"""
import argparse
import json
import os
import sys
from datetime import datetime
from typing import Any, Dict

# Fix Windows console encoding for Unicode output
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except AttributeError:
    pass  # Python < 3.7

from audit import (
    SEVERITY_ORDER,
    detect_project_types,
    run_external_tools,
    scan_code_patterns,
    scan_configuration,
    scan_dependencies,
    scan_iac,
    scan_sbom,
    scan_secrets,
)


def run_full_scan(project_path: str, scan_type: str = "all", no_limit: bool = False) -> Dict[str, Any]:
    """Execute security validation scans and produce a unified report."""
    report = {
        "project": project_path,
        "timestamp": datetime.now().isoformat(),
        "scan_type": scan_type,
        "scans": {},
        "summary": {
            "total_findings": 0,
            "critical": 0,
            "high": 0,
            "medium": 0,
            "overall_status": "[OK] SECURE"
        }
    }

    scanners = {
        "deps": ("dependencies", scan_dependencies),
        "secrets": ("secrets", scan_secrets),
        "patterns": ("code_patterns", scan_code_patterns),
        "config": ("configuration", scan_configuration),
        "iac": ("iac", scan_iac),
        "sbom": ("sbom", scan_sbom),
    }

    max_findings = 999999 if no_limit else 30

    for key, (name, scanner) in scanners.items():
        if scan_type == "all" or scan_type == key:
            print(f"[*] Running {name} scan...", file=sys.stderr)
            result = scanner(project_path)

            # Truncate findings (already sorted by severity)
            if len(result.get("findings", [])) > max_findings:
                truncated = len(result["findings"]) - max_findings
                result["findings"] = result["findings"][:max_findings]
                result["truncated"] = truncated

            report["scans"][name] = result

            for finding in result.get("findings", []):
                sev = finding.get("severity", "low")
                report["summary"]["total_findings"] += 1
                if sev in report["summary"]:
                    report["summary"][sev] += 1

    if report["summary"]["critical"] > 0:
        report["summary"]["overall_status"] = "[!!] CRITICAL ISSUES FOUND"
    elif report["summary"]["high"] > 0:
        report["summary"]["overall_status"] = "[!] HIGH RISK ISSUES"
    elif report["summary"]["total_findings"] > 0:
        report["summary"]["overall_status"] = "[?] REVIEW RECOMMENDED"

    return report


def print_summary(report: Dict[str, Any]):
    """Print human-readable summary to stdout."""
    print(f"\n{'='*60}")
    print(f"Security Scan v3.2: {report['project']}")
    print(f"Timestamp: {report['timestamp']}")
    print(f"{'='*60}")
    print(f"Status: {report['summary']['overall_status']}")
    print(f"Total Findings: {report['summary']['total_findings']}")
    print(f"  Critical: {report['summary']['critical']}")
    print(f"  High: {report['summary']['high']}")
    print(f"  Medium: {report['summary']['medium']}")

    total_skipped = sum(s.get('skipped_files', 0) for s in report['scans'].values())
    if total_skipped > 0:
        print(f"  Skipped Files: {total_skipped} (see stderr)")

    total_truncated = sum(s.get('truncated', 0) for s in report['scans'].values())
    if total_truncated > 0:
        print(f"  Truncated: {total_truncated} findings hidden (use --no-limit)")

    print(f"{'='*60}\n")

    for scan_name, scan_result in report['scans'].items():
        print(f"\n{scan_name.upper()}: {scan_result['status']}")
        for finding in scan_result.get('findings', [])[:10]:
            sev = finding.get('severity', 'INFO').upper()
            desc = finding.get('type') or finding.get('pattern') or finding.get('issue')
            cwe = finding.get('cwe', '')
            f_str = f"  - [{sev}] {desc}"
            if cwe:
                f_str += f" ({cwe})"
            if 'file' in finding:
                f_str += f" in {finding['file']}"
            if 'line' in finding:
                f_str += f":{finding['line']}"
            if 'message' in finding:
                f_str += f" - {finding['message']}"
            print(f_str)


def main():
    parser = argparse.ArgumentParser(description="Security Audit Tool v3.2")
    parser.add_argument("project_path", nargs="?", default=".", help="Project directory")
    parser.add_argument("--scan-type",
                        choices=["all", "deps", "secrets", "patterns", "config", "iac", "sbom", "external"],
                        default="all", help="Type of scan")
    parser.add_argument("--output", choices=["json", "summary"], default="summary",
                        help="Output format")
    parser.add_argument("--fail-on", choices=["critical", "high", "medium"],
                        default=None, help="Exit with code 1 if findings >= this severity (for CI/CD)")
    parser.add_argument("--no-limit", action="store_true",
                        help="Do not truncate findings list")

    args = parser.parse_args()

    if not os.path.isdir(args.project_path):
        print(json.dumps({"error": f"Directory not found: {args.project_path}"}))
        sys.exit(1)

    exit_code = 0

    # Run Pattern Matching Scans
    if args.scan_type != "external":
        result = run_full_scan(args.project_path, args.scan_type, args.no_limit)

        if args.output == "summary":
            print_summary(result)
        else:
            print(json.dumps(result, indent=2))

        # CI/CD gate: exit with error if findings meet threshold
        if args.fail_on:
            threshold = SEVERITY_ORDER[args.fail_on]
            for sev_name, sev_order in SEVERITY_ORDER.items():
                if sev_order <= threshold and result["summary"].get(sev_name, 0) > 0:
                    exit_code = 1
                    print(f"\n[GATE] --fail-on {args.fail_on}: Found {sev_name} issues. Exit code 1.")
                    break

    # Run External Tools
    if args.scan_type == "all" or args.scan_type == "external":
        types = detect_project_types(args.project_path)
        if types:
            run_external_tools(args.project_path, types)

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
