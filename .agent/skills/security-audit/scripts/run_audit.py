#!/usr/bin/env python3
"""
Skill: security-audit
Script: run_audit.py v3.12
Purpose: CLI entry point for security audit scanner.
Usage: python run_audit.py [project_path] [--scan-type all|deps|secrets|patterns|config|iac|mcp|external|sbom]
       [--fail-on critical|high|medium] [--output json|summary] [--no-limit]
Exit: 0 every requested part ran and no gate cause; 1 a `--fail-on` cause (a finding at the
      threshold or above, or an external tool's non-zero exit), or a JSON `error` for a missing
      directory or a non-positive `--max-size`; 2 a usage error (argparse); 3 a requested part did
      not run.
"""
import argparse
import json
import os
import sys
from datetime import datetime
from typing import Any, Dict, List

# Fix Windows console encoding for Unicode output
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except AttributeError:
    pass  # Python < 3.7

from audit import (
    SEVERITY_ORDER,
    __version__ as AUDIT_VERSION,
    detect_project_types,
    external_section,
    incomplete_slots,
    printable,
    run_external_tools,
    scan_code_patterns,
    scan_configuration,
    scan_dependencies,
    scan_iac,
    scan_mcp_agentic,
    scan_sbom,
    scan_secrets,
)
from audit import config as _audit_config

#: The severities the summary counts (TASK 118 R2.4).
SUMMARY_SEVERITIES = ("critical", "high", "medium", "low", "info")
#: Findings each section keeps unless `--no-limit` is given; the summary counts all of them.
MAX_FINDINGS = 30


def run_full_scan(project_path: str, scan_type: str = "all", no_limit: bool = False,
                  fail_on=None) -> Dict[str, Any]:
    """Execute the requested scans and produce a unified report.

    The in-process scans of `scan_type` run first, then the external layer for `all` and
    `external`, also for a project with no detected type (TASK 118 R1.4). The summary counts every
    finding before each section is cut to `MAX_FINDINGS` (R2.5). `fail_on` sets npm's
    `--audit-level` (R2.10).
    """
    report = {
        "project": project_path,
        "timestamp": datetime.now().isoformat(),
        "scan_type": scan_type,
        "scans": {},
    }

    scanners = {
        "deps": ("dependencies", scan_dependencies),
        "secrets": ("secrets", scan_secrets),
        "patterns": ("code_patterns", scan_code_patterns),
        "config": ("configuration", scan_configuration),
        "iac": ("iac", scan_iac),
        "mcp": ("mcp_agentic", scan_mcp_agentic),
        "sbom": ("sbom", scan_sbom),
    }

    for key, (name, scanner) in scanners.items():
        if scan_type == "all" or scan_type == key:
            print(f"[*] Running {name} scan...", file=sys.stderr)
            report["scans"][name] = scanner(project_path)

    if scan_type in ("all", "external"):
        types = detect_project_types(project_path)
        report["external"] = external_section(run_external_tools(project_path, types, fail_on))

    report["summary"] = summarize(report)

    # Truncate findings (already sorted by severity), after the summary counted them all.
    if not no_limit:
        for result in report["scans"].values():
            if len(result.get("findings", [])) > MAX_FINDINGS:
                result["truncated"] = len(result["findings"]) - MAX_FINDINGS
                result["findings"] = result["findings"][:MAX_FINDINGS]

    return report


def summarize(report: Dict[str, Any]) -> Dict[str, Any]:
    """The summary of a report (TASK 118 R2.1 to R2.4, R2.9)."""
    summary = {"total_findings": 0, **dict.fromkeys(SUMMARY_SEVERITIES, 0)}
    not_run: List[str] = []
    for name, result in report["scans"].items():
        for finding in result.get("findings", []):
            summary["total_findings"] += 1
            sev = finding.get("severity", "low")
            if sev in summary:
                summary[sev] += 1
            if finding.get("audited") is False:
                not_run.append(f"{name}: {finding.get('message')}")

    records = report.get("external", {}).get("tools", [])
    for slot, last in incomplete_slots(records):
        entry = f"external {slot}: {last['tool']} {last['status']}"
        if last["status"] == "not_run":
            entry += f", {last['reason']}"
        not_run.append(entry)
    tool_exits = [f"{r['tool']} exited {r['exit_code']} ({r['slot']})"
                  for r in records if r["status"] == "ran" and r["exit_code"] != 0]

    summary["not_run"] = not_run
    summary["scan_complete"] = not not_run
    summary["tool_exits"] = tool_exits

    if summary["critical"] > 0:
        summary["overall_status"] = "[!!] CRITICAL ISSUES FOUND"
    elif summary["high"] > 0:
        summary["overall_status"] = "[!] HIGH RISK ISSUES"
    elif not_run:
        summary["overall_status"] = f"[?] INCOMPLETE: {len(not_run)} part(s) did not run"
    elif summary["total_findings"] > 0 or tool_exits:
        summary["overall_status"] = "[?] REVIEW RECOMMENDED"
    else:
        summary["overall_status"] = "[OK] SECURE"
    return summary


def gate_causes(report: Dict[str, Any], fail_on) -> List[str]:
    """Each cause of exit 1 under `--fail-on` (TASK 118 R2.6, R2.8); empty without `fail_on`."""
    if not fail_on:
        return []
    summary = report["summary"]
    threshold = SEVERITY_ORDER[fail_on]
    causes = [f"{summary[sev]} {sev} finding(s)" for sev, order in SEVERITY_ORDER.items()
              if order <= threshold and summary.get(sev, 0) > 0]
    return causes + list(summary["tool_exits"])


def exit_code(report: Dict[str, Any], fail_on) -> int:
    """1 on a `--fail-on` cause, else 3 when a requested part did not run, else 0 (R2.6, R2.7)."""
    if gate_causes(report, fail_on):
        return 1
    return 0 if report["summary"]["scan_complete"] else 3


def print_summary(report: Dict[str, Any]):
    """Print human-readable summary to stdout; text from the scanned tree is escaped (R1.10)."""
    summary = report["summary"]
    print(f"\n{'='*60}")
    print(f"Security Scan v{AUDIT_VERSION}: {printable(report['project'])}")
    print(f"Timestamp: {report['timestamp']}")
    print(f"{'='*60}")
    print(f"Status: {summary['overall_status']}")
    print(f"Total Findings: {summary['total_findings']}")
    for sev in SUMMARY_SEVERITIES:
        print(f"  {sev.capitalize()}: {summary[sev]}")

    total_skipped = sum(s.get('skipped_files', 0) for s in report['scans'].values())
    if total_skipped > 0:
        print(f"  Skipped Files: {total_skipped} (see stderr)")

    total_truncated = sum(s.get('truncated', 0) for s in report['scans'].values())
    if total_truncated > 0:
        print(f"  Truncated: {total_truncated} findings hidden (use --no-limit)")

    if summary["not_run"]:
        print("Not run:")
        for entry in summary["not_run"]:
            print(f"  - {printable(entry)}")
    if summary["tool_exits"]:
        print("Tool exits:")
        for entry in summary["tool_exits"]:
            print(f"  - {printable(entry)}")

    print(f"{'='*60}\n")

    for scan_name, scan_result in report['scans'].items():
        print(f"\n{scan_name.upper()}: {printable(scan_result['status'])}")
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
            print(printable(f_str))

    if "external" in report:
        print(f"\nEXTERNAL: {report['external']['status']}")
        for record in report["external"]["tools"]:
            line = f"  - {record['slot']}: {record['tool']} {record['status']}"
            if record["status"] in ("ran", "killed"):
                line += f" (exit {record['exit_code']})"
            elif record["reason"]:
                line += f" ({record['reason']})"
            print(printable(line))


def main(argv=None):
    parser = argparse.ArgumentParser(description=f"Security Audit Tool v{AUDIT_VERSION}")
    parser.add_argument("project_path", nargs="?", default=".", help="Project directory")
    parser.add_argument("--scan-type",
                        choices=["all", "deps", "secrets", "patterns", "config", "iac", "mcp", "sbom", "external"],
                        default="all", help="Type of scan")
    parser.add_argument("--output", choices=["json", "summary"], default="summary",
                        help="Output format")
    parser.add_argument("--fail-on", choices=["critical", "high", "medium"],
                        default=None, help="Exit with code 1 if findings >= this severity, or an "
                                           "external tool exits non-zero (for CI/CD)")
    parser.add_argument("--no-limit", action="store_true",
                        help="Do not truncate findings list")
    parser.add_argument("--max-size", type=int, default=None, metavar="MB",
                        help=f"Max file size to scan in MB (default: {_audit_config.MAX_FILE_SIZE // (1024*1024)}). "
                             "Increase for large minified bundles.")

    args = parser.parse_args(argv)

    if args.max_size is not None:
        if args.max_size <= 0:
            print(json.dumps({"error": "--max-size must be positive"}))
            sys.exit(1)
        _audit_config.MAX_FILE_SIZE = args.max_size * 1024 * 1024

    if not os.path.isdir(args.project_path):
        print(json.dumps({"error": f"Directory not found: {args.project_path}"}))
        sys.exit(1)

    report = run_full_scan(args.project_path, args.scan_type, args.no_limit, args.fail_on)

    if args.output == "summary":
        print_summary(report)
    else:
        print(json.dumps(report, indent=2))
    sys.stdout.flush()

    code = exit_code(report, args.fail_on)
    causes = gate_causes(report, args.fail_on)
    if causes:
        print(f"\n[GATE] --fail-on {args.fail_on}:", file=sys.stderr)
        for cause in causes:
            print(f"  - {printable(cause)}", file=sys.stderr)
    if not report["summary"]["scan_complete"]:
        print("\n[INCOMPLETE]", file=sys.stderr)
        for entry in report["summary"]["not_run"]:
            print(f"  - {printable(entry)}", file=sys.stderr)

    sys.exit(code)


if __name__ == "__main__":
    main()
