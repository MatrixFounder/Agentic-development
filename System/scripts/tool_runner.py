
import subprocess
import json
import os
from pathlib import Path
from typing import Dict, Any, Union

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
    # Normalize input
    if hasattr(tool_call, 'function'):
        name = tool_call.function.name
        args_str = tool_call.function.arguments
        try:
            args = json.loads(args_str) if isinstance(args_str, str) else args_str
        except json.JSONDecodeError:
            return {"error": "Invalid JSON arguments", "success": False}
    elif isinstance(tool_call, dict):
        name = tool_call.get('name')
        args = tool_call.get('arguments')
        if isinstance(args, str):
            try:
                args = json.loads(args)
            except json.JSONDecodeError:
                return {"error": "Invalid JSON arguments", "success": False}
    else:
        return {"error": "Invalid tool_call format", "success": False}

    repo_root = Path.cwd()

    def is_safe_path(path_str: str) -> bool:
        """Check for path traversal."""
        try:
            # Resolve resolves symlinks and generally returns absolute path
            target_path = (repo_root / path_str).resolve()
            # Check if it starts with repo_root
            return str(target_path).startswith(str(repo_root))
        except Exception:
            return False

    try:
        if name == "run_tests":
            command = args.get("command", "pytest -q --tb=short")
            cwd = args.get("cwd", ".")
            # Safety check: simplistic white-listing or just reliance on container
            # specific strict check for this POC
            valid_starts = ["pytest", "python -m pytest", "npm test"]
            if not any(command.strip().startswith(p) for p in valid_starts):
                 return {"error": "Command not allowed (only pytest/npm test)", "success": False}
            
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, cwd=cwd
            )
            return {
                "output": result.stdout,
                "errors": result.stderr,
                "returncode": result.returncode,
                "success": result.returncode == 0
            }

        elif name == "read_file":
            path_str = args.get("path")
            if not path_str:
                return {"error": "Missing 'path' argument", "success": False}
            
            if not is_safe_path(path_str):
                 return {"error": "Path traversal detected", "success": False}

            path = repo_root / path_str
            if not path.exists():
                return {"error": f"File {path_str} not found", "success": False}
            
            content = path.read_text(encoding="utf-8")
            return {"content": content, "path": path_str, "success": True}

        elif name == "write_file":
            path_str = args.get("path")
            content = args.get("content")
            if not path_str or content is None:
                return {"error": "Missing 'path' or 'content'", "success": False}

            if not is_safe_path(path_str):
                 return {"error": "Path traversal detected", "success": False}
            
            path = repo_root / path_str
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            return {"status": "written", "path": path_str, "size_bytes": len(content), "success": True}

        elif name == "list_directory":
            path_str = args.get("path", ".")
            recursive = args.get("recursive", False)

            if not is_safe_path(path_str):
                return {"error": "Path traversal detected", "success": False}
            
            path = repo_root / path_str
            if not path.exists() or not path.is_dir():
                return {"error": "Directory not found", "success": False}
            
            if recursive:
                 # Minimal implementation of recursive
                 files = [str(p.relative_to(repo_root)) for p in path.rglob("*")]
            else:
                 files = [str(p.relative_to(repo_root)) for p in path.iterdir()]
            
            return {"files": files, "count": len(files), "success": True}

        elif name == "git_status":
            result = subprocess.run(
                "git status --porcelain", shell=True, capture_output=True, text=True
            )
            return {"output": result.stdout, "success": result.returncode == 0}

        elif name == "git_add":
            files = args.get("files", [])
            if not files:
                 return {"error": "No files provided", "success": False}
            
            cmd = ["git", "add"] + files
            result = subprocess.run(cmd, capture_output=True, text=True)
            return {"output": result.stdout, "error": result.stderr, "success": result.returncode == 0}

        elif name == "git_commit":
            message = args.get("message")
            if not message:
                return {"error": "Missing commit message", "success": False}
            
            result = subprocess.run(
                ["git", "commit", "-m", message], capture_output=True, text=True
            )
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
            allow_correction = args.get("allow_correction", True)
            tasks_dir = str(repo_root / "docs" / "tasks")
            
            result = generate_task_archive_filename(
                slug=slug,
                proposed_id=proposed_id,
                allow_correction=allow_correction,
                tasks_dir=tasks_dir
            )
            result["success"] = result["status"] in ("generated", "corrected")
            return result



        else:
            return {"error": f"Unknown tool: {name}", "success": False}

    except Exception as e:
        return {"error": str(e), "success": False}

