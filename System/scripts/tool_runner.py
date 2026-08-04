import json
import shlex
import subprocess
from pathlib import Path
from typing import Any, Dict, List

DEFAULT_TEST_COMMAND = "pytest -q --tb=short"
DEFAULT_TEST_TIMEOUT_SECONDS = 120
MAX_TEST_TIMEOUT_SECONDS = 1800
DISALLOWED_SHELL_CHARS = (";", "|", "&", "`", "<", ">", "$(")


def _normalize_tool_call(tool_call) -> Dict[str, Any]:
    """Normalize tool call input into a dict with name and arguments."""
    if hasattr(tool_call, "function"):
        name = tool_call.function.name
        args_raw = tool_call.function.arguments
    elif isinstance(tool_call, dict):
        name = tool_call.get("name")
        args_raw = tool_call.get("arguments")
    else:
        return {"error": "Invalid tool_call format", "success": False}

    if not name or not isinstance(name, str):
        return {"error": "Invalid tool name", "success": False}

    if args_raw is None:
        args = {}
    elif isinstance(args_raw, dict):
        args = args_raw
    elif isinstance(args_raw, str):
        try:
            args = json.loads(args_raw)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON arguments", "success": False}
    else:
        return {"error": "Invalid arguments format", "success": False}

    if not isinstance(args, dict):
        return {"error": "Arguments must be a JSON object", "success": False}

    return {"name": name, "args": args}


def _contains_disallowed_shell_chars(command: str) -> bool:
    return any(token in command for token in DISALLOWED_SHELL_CHARS)


def _is_allowed_test_command(parts: List[str]) -> bool:
    if not parts:
        return False

    exe = parts[0]

    if exe == "pytest":
        return True

    if exe in {"python", "python3"} and len(parts) >= 3 and parts[1] == "-m" and parts[2] == "pytest":
        return True

    if exe == "npm" and len(parts) >= 2 and parts[1] == "test":
        return True

    if exe == "npx" and len(parts) >= 2 and parts[1] == "jest":
        return True

    if exe == "cargo" and len(parts) >= 2 and parts[1] == "test":
        return True

    return False


def _parse_timeout_seconds(value: Any) -> int:
    if value is None:
        return DEFAULT_TEST_TIMEOUT_SECONDS

    if isinstance(value, str) and value.isdigit():
        value = int(value)

    if not isinstance(value, int):
        raise ValueError("timeout_seconds must be an integer")

    if value <= 0:
        raise ValueError("timeout_seconds must be positive")

    if value > MAX_TEST_TIMEOUT_SECONDS:
        raise ValueError(f"timeout_seconds must be <= {MAX_TEST_TIMEOUT_SECONDS}")

    return value


def _resolve_repo_path(repo_root: Path, path_str: str) -> Path:
    candidate = Path(path_str)
    if not candidate.is_absolute():
        candidate = repo_root / candidate

    resolved = candidate.resolve(strict=False)
    try:
        resolved.relative_to(repo_root)
    except ValueError as exc:
        raise ValueError("Path traversal detected") from exc

    return resolved


def execute_tool(tool_call) -> Dict[str, Any]:
    """
    Executes a tool call and returns the result in a format suitable for the 'tool' message role.

    Args:
        tool_call: An object or dict with 'function' attribute/key, containing 'name' and 'arguments'.
                   If it's a dict (from testing), expected keys: {'name': str, 'arguments': str|dict}.
                   If it's an object (from OpenAI lib), expected attrs: function.name, function.arguments.

    Returns:
        Dict with keys like 'output', 'error', 'success', or tool-specific data.
    """
    normalized = _normalize_tool_call(tool_call)
    if "error" in normalized:
        return normalized

    name = normalized["name"]
    args = normalized["args"]
    repo_root = Path.cwd().resolve()

    try:
        if name == "run_tests":
            command = args.get("command", DEFAULT_TEST_COMMAND)
            if not isinstance(command, str) or not command.strip():
                return {"error": "Invalid command", "success": False}

            if _contains_disallowed_shell_chars(command):
                return {"error": "Command not allowed (shell metacharacters are forbidden)", "success": False}

            try:
                parts = shlex.split(command)
            except ValueError:
                return {"error": "Invalid command syntax", "success": False}

            if not _is_allowed_test_command(parts):
                return {
                    "error": "Command not allowed (only pytest/python -m pytest/npm test/npx jest/cargo test)",
                    "success": False,
                }

            cwd_arg = args.get("cwd", ".")
            if not isinstance(cwd_arg, str) or not cwd_arg:
                return {"error": "Invalid working directory", "success": False}

            try:
                safe_cwd = _resolve_repo_path(repo_root, cwd_arg)
            except ValueError:
                return {"error": "Invalid working directory", "success": False}

            if not safe_cwd.exists() or not safe_cwd.is_dir():
                return {"error": "Invalid working directory", "success": False}

            try:
                timeout_seconds = _parse_timeout_seconds(args.get("timeout_seconds", DEFAULT_TEST_TIMEOUT_SECONDS))
            except ValueError as exc:
                return {"error": str(exc), "success": False}

            try:
                result = subprocess.run(
                    parts,
                    shell=False,
                    capture_output=True,
                    text=True,
                    cwd=str(safe_cwd),
                    timeout=timeout_seconds,
                )
            except subprocess.TimeoutExpired as exc:
                return {
                    "output": exc.stdout or "",
                    "errors": exc.stderr or "",
                    "error": f"Test command timed out after {timeout_seconds}s",
                    "returncode": None,
                    "success": False,
                }
            except FileNotFoundError:
                return {"error": f"Executable not found: {parts[0]}", "success": False}

            return {
                "output": result.stdout,
                "errors": result.stderr,
                "returncode": result.returncode,
                "success": result.returncode == 0,
            }

        elif name == "read_file":
            path_str = args.get("path")
            if not path_str:
                return {"error": "Missing 'path' argument", "success": False}

            try:
                path = _resolve_repo_path(repo_root, path_str)
            except ValueError:
                return {"error": "Path traversal detected", "success": False}

            if not path.exists():
                return {"error": f"File {path_str} not found", "success": False}

            content = path.read_text(encoding="utf-8")
            return {"content": content, "path": path_str, "success": True}

        elif name == "write_file":
            path_str = args.get("path")
            content = args.get("content")
            if not path_str or content is None:
                return {"error": "Missing 'path' or 'content'", "success": False}

            try:
                path = _resolve_repo_path(repo_root, path_str)
            except ValueError:
                return {"error": "Path traversal detected", "success": False}

            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            return {"status": "written", "path": path_str, "size_bytes": len(content), "success": True}

        elif name == "list_directory":
            path_str = args.get("path", ".")
            recursive = args.get("recursive", False)

            try:
                path = _resolve_repo_path(repo_root, path_str)
            except ValueError:
                return {"error": "Path traversal detected", "success": False}

            if not path.exists() or not path.is_dir():
                return {"error": "Directory not found", "success": False}

            if recursive:
                files = [str(p.relative_to(repo_root)) for p in path.rglob("*")]
            else:
                files = [str(p.relative_to(repo_root)) for p in path.iterdir()]

            return {"files": files, "count": len(files), "success": True}

        elif name == "git_status":
            result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, cwd=str(repo_root))
            return {"output": result.stdout, "success": result.returncode == 0}

        elif name == "git_add":
            files = args.get("files", [])
            if not files:
                return {"error": "No files provided", "success": False}
            if not isinstance(files, list) or not all(isinstance(f, str) for f in files):
                return {"error": "Invalid 'files' argument", "success": False}

            normalized_files = []
            for file_path in files:
                try:
                    safe_path = _resolve_repo_path(repo_root, file_path)
                except ValueError:
                    return {"error": f"Path traversal detected: {file_path}", "success": False}
                normalized_files.append(str(safe_path.relative_to(repo_root)))

            cmd = ["git", "add"] + normalized_files
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(repo_root))
            return {"output": result.stdout, "error": result.stderr, "success": result.returncode == 0}

        elif name == "git_commit":
            message = args.get("message")
            if not message:
                return {"error": "Missing commit message", "success": False}

            result = subprocess.run(["git", "commit", "-m", message], capture_output=True, text=True, cwd=str(repo_root))
            return {"output": result.stdout, "error": result.stderr, "success": result.returncode == 0}

        elif name == "generate_task_archive_filename":
            # Import here to avoid circular imports and keep tool_runner standalone
            import sys

            tools_path = repo_root / ".agent" / "tools"
            if str(tools_path) not in sys.path:
                sys.path.insert(0, str(tools_path))

            from task_id_tool import generate_task_archive_filename

            slug = args.get("slug")
            if not slug:
                return {"error": "Missing 'slug' argument", "success": False}

            proposed_id = args.get("proposed_id")
            # ARC-1: renumbering a task whose id is already cited in its
            # sub-tasks, plan archive, commits and ledgers is a human
            # decision. Opt in explicitly; the default reports a conflict.
            allow_correction = args.get("allow_correction", False)
            tasks_dir = str(repo_root / "docs" / "tasks")

            result = generate_task_archive_filename(
                slug=slug,
                proposed_id=proposed_id,
                allow_correction=allow_correction,
                tasks_dir=tasks_dir,
            )
            result["success"] = result["status"] in ("generated", "corrected")
            return result

        else:
            return {"error": f"Unknown tool: {name}", "success": False}

    except Exception as e:
        return {"error": str(e), "success": False}
