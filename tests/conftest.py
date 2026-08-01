"""Session-wide hooks for the pytest suite.

The only job here is scratch hygiene: see `tests/_scratch.py` for why in-repo scratch
exists at all, why each session owns a private subdirectory, and why the start-up sweep
removes only the debris of processes that are gone.

These are `pytest_sessionstart` / `pytest_sessionfinish` hooks rather than an autouse
fixture on purpose. A session-scoped fixture never runs when every test is deselected,
when only collection happens (`--collect-only`), or when collection fails — exactly the
runs after which stale scratch is most likely to be sitting there.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

from _scratch import sweep_session, sweep_stale_sessions  # noqa: E402 - needs the path append


def pytest_sessionstart(session):
    """Collect scratch left behind by runs whose process no longer exists."""
    sweep_stale_sessions()


def pytest_sessionfinish(session, exitstatus):
    """Remove this session's own scratch directory."""
    sweep_session()
