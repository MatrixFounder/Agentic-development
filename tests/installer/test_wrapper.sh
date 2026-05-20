#!/usr/bin/env bash
# Smoke test for install.sh — the bash wrapper (Task 063-11, Issue I10.3).
#
# Verifies the wrapper runs under bash, refuses non-bash shells, and carries
# the PyYAML install hint. Run: bash tests/installer/test_wrapper.sh
set -u

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WRAPPER="$REPO/install.sh"
FAIL=0
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

pass() { echo "PASS: $1"; }
fail() { echo "FAIL: $1"; FAIL=1; }
skip() { echo "SKIP: $1"; }

# 1. The wrapper runs under bash (doctor on an empty dir exits 0).
if bash "$WRAPPER" doctor --target "$TMP" >/dev/null 2>&1; then
    pass "install.sh runs under bash"
else
    fail "install.sh did not run cleanly under bash"
fi

# 2. The BASH_VERSION guard is present in the wrapper.
if grep -q 'BASH_VERSION' "$WRAPPER"; then
    pass "wrapper carries the BASH_VERSION guard"
else
    fail "wrapper is missing the BASH_VERSION guard"
fi

# 2b. A genuine non-bash shell is rejected. macOS /bin/sh IS bash-as-sh (it
#     sets BASH_VERSION), so this is only meaningful with a true POSIX shell
#     such as dash — skipped when dash is unavailable.
if command -v dash >/dev/null 2>&1; then
    if dash "$WRAPPER" doctor --target "$TMP" >/dev/null 2>&1; then
        fail "install.sh did not reject dash"
    else
        pass "install.sh rejects a non-bash shell (dash)"
    fi
else
    skip "dash not available — non-bash rejection not exercised here"
fi

# 3. Missing PyYAML — the wrapper must abort (exit 2) with a hint, *before*
#    exec'ing the installer. Simulated with a stub python3 that fails the
#    `import yaml` probe.
FAKEBIN="$TMP/fakebin"
mkdir -p "$FAKEBIN"
cat > "$FAKEBIN/python3" <<'STUB'
#!/usr/bin/env bash
# Stub python3: pretend PyYAML is not installed.
if [ "${1:-}" = "-c" ] && printf '%s' "${2:-}" | grep -q 'import yaml'; then
    exit 1
fi
exit 0
STUB
chmod +x "$FAKEBIN/python3"
OUT="$(PATH="$FAKEBIN:$PATH" bash "$WRAPPER" doctor --target "$TMP" 2>&1)"
RC=$?
if [ "$RC" -eq 2 ] && printf '%s' "$OUT" | grep -qi 'pyyaml'; then
    pass "wrapper aborts (exit 2) with a PyYAML hint when the dependency is missing"
else
    fail "wrapper did not abort with a PyYAML hint (rc=$RC)"
fi

if [ "$FAIL" -eq 0 ]; then
    echo "wrapper smoke: OK"
else
    echo "wrapper smoke: FAILED"
fi
exit "$FAIL"
