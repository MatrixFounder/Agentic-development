
TOOLS_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "run_tests",
            "description": "Run project tests using pytest. Returns stdout, stderr and return code.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Full command to run tests. Default: 'pytest -q --tb=short'",
                        "default": "pytest -q --tb=short"
                    },
                    "cwd": {
                        "type": "string",
                        "description": "Working directory for execution (default: project root).",
                        "default": "."
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read content of a file from the project.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative path to the file."}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Create or overwrite a file in the project.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative path to the file."},
                    "content": {"type": "string", "description": "Full content of the file."}
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": "List files and folders in a directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "default": ".", "description": "Path to directory."},
                    "recursive": {"type": "boolean", "default": False}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "git_status",
            "description": "Get current git repository status.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "git_add",
            "description": "Add files to staging area.",
            "parameters": {
                "type": "object",
                "properties": {
                    "files": {"type": "array", "items": {"type": "string"}, "description": "List of file paths."}
                },
                "required": ["files"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "git_commit",
            "description": "Create a commit with the specified message.",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Commit message."}
                },
                "required": ["message"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_task_archive_filename",
            "description": "Generate a unique filename for task archival. Returns the next sequential ID or validates a proposed ID. Use before archiving docs/TASK.md to docs/tasks/.",
            "parameters": {
                "type": "object",
                "properties": {
                    "slug": {
                        "type": "string",
                        "description": "Short task name in Latin with dashes (e.g., 'new-feature'). Will be normalized."
                    },
                    "proposed_id": {
                        "type": "string",
                        "description": "Optional desired ID (e.g., '031' or '31'). If not provided, auto-generates next ID."
                    },
                    "allow_correction": {
                        "type": "boolean",
                        "default": True,
                        "description": "If True, auto-correct to next available ID on conflict. If False, return conflict status."
                    }
                },
                "required": ["slug"]
            }
        }
    }
]
