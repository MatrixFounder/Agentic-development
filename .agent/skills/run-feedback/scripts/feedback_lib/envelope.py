"""Uniform machine-readable error envelope for run-feedback CLIs.

Schema-compatible with the office-skills ``--json-errors`` contract —
a single line on stderr shaped ``{"v": 1, "error": ..., "code": <int != 0>,
"type": ..., "details": {...}}`` with the process exit code equal to
``code`` — but written independently for this Apache-licensed framework.
LICENSE FIREWALL: this file MUST NOT be replaced with a byte copy of the
proprietary office `_errors.py` (see Universal-skills CLAUDE.md §3: the
`html` skill went proprietary precisely by embedding such copies).
"""

from __future__ import annotations

import json
import sys

SCHEMA_VERSION = 1

# Exit-code taxonomy shared by every subcommand (documented in SKILL.md §4).
EXIT_OK = 0
EXIT_UNEXPECTED = 1
EXIT_USAGE = 2
EXIT_CONFIG = 3
EXIT_FILING_CONFLICT = 4
EXIT_NOT_FOUND = 5


class CliError(Exception):
    """Raised by library code; the CLI turns it into an envelope + exit code."""

    def __init__(self, message, code=EXIT_UNEXPECTED, err_type=None,
                 details=None, remediation=None):
        super().__init__(message)
        self.code = code if code != 0 else EXIT_UNEXPECTED
        self.err_type = err_type or type(self).__name__
        self.details = dict(details or {})
        if remediation:
            self.details.setdefault("remediation", remediation)


def emit_json_error(message, code=EXIT_UNEXPECTED, err_type=None,
                    details=None, stream=None):
    """Print one envelope line to *stream* (default stderr); return the exit code.

    ``code`` 0 is coerced to 1 so a failure envelope can never carry a
    success exit code (mirrors the office contract).
    """
    stream = stream or sys.stderr
    payload = {"v": SCHEMA_VERSION, "error": str(message)}
    if code == 0:
        code = EXIT_UNEXPECTED
        details = dict(details or {})
        details["coerced_from_zero"] = True
    payload["code"] = int(code)
    if err_type:
        payload["type"] = str(err_type)
    if details:
        payload["details"] = details
    stream.write(json.dumps(payload, ensure_ascii=False) + "\n")
    stream.flush()
    return int(code)


def wants_json_errors(argv=None):
    return "--json-errors" in (argv if argv is not None else sys.argv[1:])


def install_json_errors(parser, argv=None):
    """Add ``--json-errors`` and make argparse usage errors honor it.

    argparse normally prints plain-text usage and exits 2 before flag
    parsing completes, so the flag is detected from raw ``argv``.
    """
    parser.add_argument("--json-errors", action="store_true",
                        help="emit failures as a single JSON line on stderr")
    json_mode = wants_json_errors(argv)

    original_error = parser.error

    def _error(message):  # noqa: ANN001 - argparse signature
        if json_mode:
            code = emit_json_error(message, code=EXIT_USAGE,
                                   err_type="UsageError")
            sys.exit(code)
        original_error(message)

    parser.error = _error
    return parser
