#!/usr/bin/env python3
import os
import subprocess
import sys
import re

def detect_project_types(root_dir):
    types = []
    if any(f.endswith(".sol") for r, _, fs in os.walk(root_dir) for f in fs):
        types.append("solidity")
    if any(f.endswith(".py") for r, _, fs in os.walk(root_dir) for f in fs):
        types.append("python")
    if os.path.exists(os.path.join(root_dir, "package.json")):
        types.append("javascript")
    if os.path.exists(os.path.join(root_dir, "Cargo.toml")):
        types.append("rust")
    return types

def run_command(cmd, shell=False):
    print(f"[*] Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    try:
        subprocess.run(cmd, shell=shell, check=False) # Don't exit on audit failure, just report
    except FileNotFoundError:
        print(f"[!] Tool not found: {cmd[0] if isinstance(cmd, list) else cmd.split()[0]}")

def scan_secrets(root_dir):
    print("[*] Scanning for secrets (Basic Regex)...")
    patterns = {
        "Private Key": r"0x[a-fA-F0-9]{64}",
        "AWS Key": r"AKIA[0-9A-Z]{16}",
        "Generic API Key": r"[a-zA-Z0-9]{32,}"
    }
    
    for root, _, files in os.walk(root_dir):
        if ".git" in root or "node_modules" in root or "venv" in root:
            continue
        for file in files:
            try:
                path = os.path.join(root, file)
                with open(path, 'r', errors='ignore') as f:
                    content = f.read()
                    for name, pat in patterns.items():
                        if re.search(pat, content):
                            # Filter false positives (like git hashes) if needed, simple for now
                            if "lock" not in file: 
                                print(f"[!] POSSIBLE SECRET FOUND ({name}) in {path}")
            except Exception:
                pass

def main():
    root_dir = os.getcwd()
    types = detect_project_types(root_dir)
    print(f"Detected project types: {types}")

    if "solidity" in types:
        run_command(["slither", "."])
        # run_command(["aderyn", "."]) # If installed

    if "python" in types:
        run_command(["bandit", "-r", "."])
        run_command(["safety", "check"])

    if "javascript" in types:
        if os.path.exists("yarn.lock"):
            run_command(["yarn", "audit"])
        else:
            run_command(["npm", "audit"])

    if "rust" in types:
        run_command(["cargo", "audit"])
        run_command(["cargo", "clippy"])

    scan_secrets(root_dir)

if __name__ == "__main__":
    main()
