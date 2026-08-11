"""Frozen-tree contract test (TASK 105, RF-7).

``skill-parallel-orchestration`` §2.4 obliges the caller to run what a Bash-less role cannot,
and bounds only when the running starts. RF-7 measured what the missing upper bound costs: a
reviewer read a suite run and a ``git diff --stat`` that both came from the caller's own
in-progress mutation, and filed a HIGH finding against the measurement chain.

The fix has two halves and this file pins both:

* the **caller** freezes the artifacts under review for the round and carries a fingerprint of
  them in the brief (``TC-01``);
* the **role** quotes the fingerprint it was given and is never told to compute one — computing
  requires an execution tool it does not have, which is the defect §2.4 already forbids
  (``TC-02``).

``TC-03`` is what makes this a verification rather than a restatement. The site set is
enumerated **from disk** by the token every carrier of the evidence contract already has, and
every carrier must land in exactly one of three declared sets. A workflow or wrapper authored
tomorrow is in none of them and fails here.
"""

import json
import re
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.resolve()

#: The token every carrier of the §2.4 evidence contract already contains. Used to enumerate
#: the site set from disk rather than from this file's own lists.
CONTRACT_TOKEN = "NOT RUN"

#: Roots scanned for carriers. `.agent/archive/` holds `.bak` rollback copies of these same
#: files and is excluded by `_is_scanned` — counting a backup as a site makes the partition
#: fail on a rollback that worked.
SCAN_ROOTS = (
    ".agent",
    ".claude/agents",
    ".gemini/agents",
    ".codex/agents",
    ".cursor/agents",
    ".antigravity/agents",
)

#: Carriers that INSTRUCT someone to write a brief. Each must carry the fingerprint line, so a
#: role reading that brief receives a value to quote.
CALLER_SITES = {
    ".agent/skills/skill-parallel-orchestration/SKILL.md": "§2.4, source of truth",
    ".agent/skills/skill-parallel-orchestration/references/sequential-fallback.md": "concrete pattern step 0",
    ".agent/workflows/vdd-multi.md": "Step 1.0 + Step 1.1 skeleton",
    ".agent/workflows/vdd-adversarial.md": "step 2a block",
    ".agent/workflows/vdd-enhanced.md": "§4 evidence item",
    ".agent/workflows/01-start-feature.md": "TASK + ARCHITECTURE gate spawns",
    ".agent/workflows/vdd-01-start-feature.md": "TASK + ARCHITECTURE gate spawns",
    ".agent/workflows/02-plan-implementation.md": "PLAN gate spawn",
    ".agent/workflows/vdd-02-plan.md": "PLAN gate spawn",
}

#: Carriers that DEFINE a role which reads a brief. `security-auditor` is listed here because it
#: is a role definition, and flagged non-read-only because its `tools:` line carries Bash — it
#: runs the scanner itself, so the negative check below does not apply to it.
ROLE_SITES = {
    ".claude/agents/critic-logic.md": True,
    ".claude/agents/critic-security.md": True,
    ".claude/agents/critic-performance.md": True,
    ".claude/agents/task-reviewer.md": True,
    ".claude/agents/plan-reviewer.md": True,
    ".claude/agents/architecture-reviewer.md": True,
    ".claude/agents/security-auditor.md": False,
    ".gemini/agents/critic-logic.md": True,
    ".gemini/agents/critic-security.md": True,
    ".gemini/agents/critic-performance.md": True,
    ".codex/agents/critic-logic.toml": True,
    ".codex/agents/critic-security.toml": True,
    ".codex/agents/critic-performance.toml": True,
    ".cursor/agents/critic-logic.md": True,
    ".cursor/agents/critic-security.md": True,
    ".cursor/agents/critic-performance.md": True,
    ".antigravity/agents/critic-logic/agent.json": True,
    ".antigravity/agents/critic-security/agent.json": True,
    ".antigravity/agents/critic-performance/agent.json": True,
    # Generator source for the 12 scaffold wrappers above. Hand-editing a generated wrapper is
    # forbidden by the manifest's own comment, so the clause has to be here to survive a
    # regeneration.
    ".agent/skills/skill-parallel-orchestration/scripts/wrappers_manifest.json": True,
}

#: Carriers that are neither. A reason is required: an exclusion nobody can read is how a set
#: rots (the rule `test_resolver_wiring` states for its own EXCLUDED set).
EXCLUDED_SITES = {
    ".agent/workflows/full-robust.md": "consumes a verdict; writes no brief, defines no role",
    ".agent/skills/security-audit/SKILL.md": "methodology read by a role that holds Bash",
    ".agent/skills/skill-adversarial-security/SKILL.md": "persona methodology; the wrapper carries the block contract",
    ".agent/skills/skill-adversarial-performance/SKILL.md": "persona methodology; the wrapper carries the block contract",
    ".agent/skills/vdd-adversarial/SKILL.md": "persona methodology; the wrapper carries the block contract",
}

#: The line a caller writes into the brief. Matched case-insensitively so a heading and a block
#: line both count, but the words are fixed: a caller that invents its own name for the value
#: gives roles nothing to quote back.
FINGERPRINT_MARKER = re.compile(r"tree fingerprint", re.IGNORECASE)

#: What a role is told to do with it. The role has no execution tool, so its only verb is to
#: report the value onward.
QUOTE_MARKER = re.compile(r"quote (?:the|this|that|it)?\s*(?:supplied\s+|given\s+)?tree fingerprint",
                          re.IGNORECASE)

#: Commands that compute a fingerprint. None may appear in a read-only role definition —
#: handing one to a Bash-less role is the instruction §2.4 exists to forbid, measured at a
#: 600-second turn.
HASH_COMMANDS = re.compile(
    r"\b(?:shasum|sha256sum|sha1sum|md5sum|openssl\s+dgst"
    r"|git\s+rev-parse|git\s+hash-object|git\s+diff\b[^\n]*\|)", re.IGNORECASE)


def _is_scanned(path: Path) -> bool:
    """A path under a scan root that is not a rollback copy or a build artifact."""
    parts = path.relative_to(PROJECT_ROOT).parts
    if "archive" in parts or "__pycache__" in parts:
        return False
    return path.suffix in {".md", ".json", ".toml"}


def _carriers() -> set:
    """Every file under the scan roots containing the §2.4 evidence contract token."""
    found = set()
    for root in SCAN_ROOTS:
        base = PROJECT_ROOT / root
        if not base.is_dir():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or not _is_scanned(path):
                continue
            if CONTRACT_TOKEN in path.read_text(encoding="utf-8", errors="replace"):
                found.add(str(path.relative_to(PROJECT_ROOT)))
    return found


class TestCallerCarriesFingerprint(unittest.TestCase):
    """TC-01 — every caller-side brief carries the fingerprint line."""

    def test_tc01_every_caller_site_declares_the_fingerprint(self):
        missing = []
        for rel, site in CALLER_SITES.items():
            path = PROJECT_ROOT / rel
            self.assertTrue(path.is_file(), f"declared caller site is absent: {rel}")
            if not FINGERPRINT_MARKER.search(path.read_text(encoding="utf-8")):
                missing.append(f"{rel} ({site})")
        self.assertEqual(
            [], missing,
            "caller sites with no tree-fingerprint line — a role spawned from these briefs "
            "receives no value to quote, so a mid-round edit stays invisible:\n  "
            + "\n  ".join(missing))


class TestRoleQuotesFingerprint(unittest.TestCase):
    """TC-02 — every role definition quotes the value and computes nothing."""

    def test_tc02_every_role_site_is_told_to_quote_it(self):
        missing = []
        for rel in ROLE_SITES:
            path = PROJECT_ROOT / rel
            self.assertTrue(path.is_file(), f"declared role site is absent: {rel}")
            if not QUOTE_MARKER.search(path.read_text(encoding="utf-8")):
                missing.append(rel)
        self.assertEqual(
            [], missing,
            "role definitions not told to quote the supplied tree fingerprint:\n  "
            + "\n  ".join(missing))

    def test_tc02_no_read_only_role_is_handed_a_hash_command(self):
        offenders = []
        for rel, read_only in ROLE_SITES.items():
            if not read_only:
                continue
            hit = HASH_COMMANDS.search((PROJECT_ROOT / rel).read_text(encoding="utf-8"))
            if hit:
                offenders.append(f"{rel}: {hit.group(0)!r}")
        self.assertEqual(
            [], offenders,
            "a role with no execution tool was handed a command to run — the defect "
            "skill-parallel-orchestration §2.4 already forbids:\n  " + "\n  ".join(offenders))

    def test_tc02_manifest_clause_reaches_every_generated_wrapper(self):
        """The 12 scaffolds are generated; the clause must live in their source."""
        manifest = json.loads(
            (PROJECT_ROOT / ".agent/skills/skill-parallel-orchestration/scripts/"
                            "wrappers_manifest.json").read_text(encoding="utf-8"))
        without = [c["name"] for c in manifest["critics"]
                   if not QUOTE_MARKER.search(c.get("evidence", ""))]
        self.assertEqual(
            [], without,
            "manifest critics whose `evidence` field omits the quote instruction — "
            "regenerating would strip it from their wrappers: " + ", ".join(without))


class TestPartitionIsComplete(unittest.TestCase):
    """TC-03 — every carrier on disk is in exactly one declared set."""

    def test_tc03_every_carrier_is_classified(self):
        declared = set(CALLER_SITES) | set(ROLE_SITES) | set(EXCLUDED_SITES)
        unclassified = sorted(_carriers() - declared)
        self.assertEqual(
            [], unclassified,
            "files carrying the §2.4 evidence contract but in no declared set. Add each to "
            "CALLER_SITES, ROLE_SITES, or EXCLUDED_SITES with a reason:\n  "
            + "\n  ".join(unclassified))

    def test_tc03_no_declared_site_is_a_phantom(self):
        on_disk = _carriers()
        phantom = sorted(s for s in set(CALLER_SITES) | set(ROLE_SITES) | set(EXCLUDED_SITES)
                         if s not in on_disk)
        self.assertEqual(
            [], phantom,
            "declared sites that carry no evidence contract — the set has drifted from the "
            "corpus it describes:\n  " + "\n  ".join(phantom))

    def test_tc03_sets_are_disjoint(self):
        pairs = (("caller", CALLER_SITES, "role", ROLE_SITES),
                 ("caller", CALLER_SITES, "excluded", EXCLUDED_SITES),
                 ("role", ROLE_SITES, "excluded", EXCLUDED_SITES))
        for a_name, a, b_name, b in pairs:
            overlap = sorted(set(a) & set(b))
            self.assertEqual([], overlap,
                             f"{a_name} and {b_name} both claim: {overlap}")


if __name__ == "__main__":
    unittest.main()
