"""agentic-development framework installer package.

Bootstrap-time tool that deploys the framework into a target project under
a chosen vendor profile. See docs/ARCHITECTURE.md §9 and docs/TASK.md
(Task 063).

Modules
-------
cli            - subcommand dispatch (install/switch/update/uninstall/doctor)
vendors        - vendors.yaml loader + per-action schema validator
state          - <target>/.agentic-installer-state.json read/write
framework_root - creates/validates target/.agentic-development/ (symlink|copy)
symlinks       - link_one / link_per_item / link_folder / make_dir
copy           - shutil.copytree wrapper with ignore-list
managed_block  - marker block + sha256 hash (shared by gitignore + bootstrap)
bootstrap      - at_import / marker_block / none bootstrap strategies
gitignore      - managed block + !-exception scanner
backup         - timestamped snapshots + retention
platform       - Windows detection, symlink capability probe
errors         - InstallerError hierarchy + exit codes
"""
