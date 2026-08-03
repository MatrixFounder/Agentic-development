#!/usr/bin/env python3
"""Validate the workflow loop contract (design spec 095, Component B).

Every `.agent/workflows/*.md` declares, in its YAML frontmatter, the retry loops it
OWNS and the sub-workflows it CALLS. This script checks that those declarations agree
with the workflow bodies and with each other.

The rule this file exists for is R3: a bound written in frontmatter must equal the
bound written in the prose that executes it. R3 is worth exactly as much as `site` is
resolvable, so `site` has a grammar (§4.3.1) with two forms and no fallback, and so
does the bound itself (`max <N>`). A locator that does not resolve is an error, never
a pass — the framework has already shipped a gate that matched nothing while printing
OK (`check_prompt_references.py`, fixed in TASK 095), and that is the failure mode
every rule here is shaped against.

Phase 3 ships this warn-only: findings are printed and the exit code stays 0 unless
--strict is passed. Phase 4 turns --strict on in CI.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - environment error, reported as exit 2
    print("error: PyYAML is required (pip install -r requirements-dev.txt)", file=sys.stderr)
    raise SystemExit(2)

EXIT_OK = 0
EXIT_VIOLATIONS = 1
EXIT_USAGE = 2
EXIT_YAML = 3

# §4.3.1 — the canonical prose bound. Whole word, case-insensitive, digits only.
# `max-2` and `max_attempts` deliberately do NOT match: the separator must be space.
BOUND_RE = re.compile(r"(?i)\bmax(?:imum)?\s+(\d+)\b")
MARKER_RE = re.compile(r"<!--\s*loop:([A-Za-z0-9_-]+)\s*-->")
LINE_SITE_RE = re.compile(r"^line:(\d+)-(\d+)$")
KEBAB_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
# §1.2 spelling 1 — the only call spelling any script can detect (smoke_workflows.py:19).
CALL_RE = re.compile(r"\b(?:Call|call)\s+`?/([a-z0-9-]+)`?")
# §4.7 — retry vocabulary that contradicts an empty `loops[]`.
RETRY_KEYWORDS = ("Repeat", "GOTO", "Go to Step", "until clean")

DEFAULT_WINDOW = 12
OVERRIDE_VALUES = {"forbidden", "allowed", "required"}
SCOPE_VALUES = {"per_run", "per_item", "global"}
ON_EXHAUST_VALUES = {"escalate_user", "stop_success", "warn_continue", "needs_human"}
CALL_KINDS = {"invoke", "escalate"}
REGISTRY_PATH = Path(".agent/skills/documentation-standards/SKILL.md")
REGISTRY_ANCHOR = "`loop:<id>`"


@dataclass
class Finding:
    rule: str
    severity: str  # "error" | "warn"
    workflow: str
    code: str
    detail: str
    loop: str | None = None

    def as_dict(self) -> dict:
        return {
            "rule": self.rule,
            "severity": self.severity,
            "workflow": self.workflow,
            "loop": self.loop,
            "code": self.code,
            "detail": self.detail,
        }

    def as_line(self) -> str:
        tag = "ERROR" if self.severity == "error" else "WARN"
        where = f"{self.workflow}.{self.loop}" if self.loop else self.workflow
        return f"{tag}: [{self.rule}] {where}: {self.code} — {self.detail}"


@dataclass
class Workflow:
    name: str
    path: Path
    contract: dict | None
    body: list[str] = field(default_factory=list)

    @property
    def loops(self) -> list[dict]:
        return (self.contract or {}).get("loops") or []

    @property
    def calls(self) -> list[dict]:
        return (self.contract or {}).get("calls") or []


def split_frontmatter(text: str) -> tuple[str | None, list[str]]:
    """Return (frontmatter_text, body_lines). Body line numbers start at 1 after the
    closing `---`, which is what §4.3.1's `line:NN-MM` form counts."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None, lines
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "\n".join(lines[1:i]), lines[i + 1 :]
    return None, lines


def load_workflows(root: Path) -> list[Workflow]:
    wf_dir = root / ".agent" / "workflows"
    if not wf_dir.is_dir():
        raise FileNotFoundError(f"no workflow directory at {wf_dir}")
    workflows: list[Workflow] = []
    for path in sorted(wf_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        fm_text, body = split_frontmatter(text)
        contract = None
        if fm_text is not None:
            try:
                data = yaml.safe_load(fm_text) or {}
            except yaml.YAMLError as exc:
                raise ValueError(f"{path}: {exc}") from exc
            if isinstance(data, dict):
                contract = data.get("contract")
        workflows.append(Workflow(path.stem, path, contract, body))
    return workflows


def resolve_site(wf: Workflow, loop: dict) -> tuple[tuple[int, int] | None, str]:
    """Resolve `site` to a 0-based [start, end) body slice.

    Returns (span, code). `code` names WHICH thing failed: a caller that reports
    SITE_UNRESOLVABLE for a bad `window` sends the author to inspect the one part of
    the declaration that is correct.

    Resolution is deliberately over `wf.body`, never the whole file: once Component A
    ships, the marker also appears in frontmatter as the `site` value, so a whole-file
    search finds two hits for every correctly-placed marker (spec §4.3.1).
    """
    site = loop.get("site")
    if not isinstance(site, str):
        return None, "SITE_UNRESOLVABLE"
    marker = MARKER_RE.fullmatch(site.strip())
    if marker:
        name = marker.group(1)
        if name != loop.get("id"):
            return None, "SITE_ID_MISMATCH"
        hits = [i for i, line in enumerate(wf.body) if f"<!-- loop:{name} -->" in line]
        if len(hits) == 0:
            return None, "SITE_UNRESOLVABLE"
        if len(hits) > 1:
            return None, "SITE_AMBIGUOUS"
        window = loop.get("window", DEFAULT_WINDOW)
        if not isinstance(window, int) or isinstance(window, bool) or window < 1:
            return None, "WINDOW_INVALID"
        return (hits[0], min(len(wf.body), hits[0] + window + 1)), "OK"
    rng = LINE_SITE_RE.fullmatch(site.strip())
    if rng:
        start, end = int(rng.group(1)), int(rng.group(2))
        if start < 1 or end < start or end > len(wf.body):
            return None, "SITE_OUT_OF_RANGE"
        return (start - 1, end), "OK"
    return None, "SITE_UNRESOLVABLE"


def check_loop_schema(wf: Workflow, loop: dict, out: list[Finding]) -> None:
    lid = loop.get("id")
    dmax = loop.get("default_max", "<missing>")
    override = loop.get("override", "forbidden")
    judgment = bool(loop.get("judgment_terminated", False))
    gated = loop.get("gated_by")

    if not isinstance(lid, str) or not lid:
        out.append(Finding("R6", "error", wf.name, "ID_MISSING", "loop has no `id`"))
        return
    # R14 — casing (D9). The id IS the anchor name, so it obeys the anchor grammar.
    if not KEBAB_RE.fullmatch(lid):
        out.append(Finding("R14", "error", wf.name, "ID_NOT_KEBAB",
                           "`id` must be lowercase kebab-case (documentation-standards §4.3)", lid))
    if not isinstance(loop.get("what"), str) or not loop["what"].strip():
        out.append(Finding("R6", "error", wf.name, "WHAT_MISSING", "`what` is required", lid))
    if override not in OVERRIDE_VALUES:
        out.append(Finding("R6", "error", wf.name, "OVERRIDE_INVALID",
                           f"`override: {override!r}` not in {sorted(OVERRIDE_VALUES)}", lid))
    scope = loop.get("scope", "per_run")
    if scope not in SCOPE_VALUES:
        out.append(Finding("R6", "error", wf.name, "SCOPE_INVALID",
                           f"`scope: {scope!r}` not in {sorted(SCOPE_VALUES)}", lid))
    # R7 — every loop declares where exhaustion goes.
    on_exhaust = loop.get("on_exhaust")
    if on_exhaust not in ON_EXHAUST_VALUES:
        out.append(Finding("R7", "error", wf.name, "ON_EXHAUST_INVALID",
                           f"`on_exhaust: {on_exhaust!r}` not in {sorted(ON_EXHAUST_VALUES)}", lid))
    # R1 — one direction only (D8): null needs a justification; an int never does.
    if dmax is None:
        if not (override == "required" or judgment or gated == "hitl"):
            out.append(Finding("R1", "error", wf.name, "UNBOUNDED",
                               "`default_max: null` requires `override: required`, "
                               "`judgment_terminated: true`, or `gated_by: hitl`", lid))
    elif not isinstance(dmax, int) or isinstance(dmax, bool) or dmax < 1:
        out.append(Finding("R1", "error", wf.name, "DEFAULT_MAX_INVALID",
                           f"`default_max: {dmax!r}` must be an int >= 1 or null", lid))
    elif override == "required":
        out.append(Finding("R1", "error", wf.name, "REQUIRED_NEEDS_NULL",
                           "`override: required` states no cap, so `default_max` must be null", lid))


def check_site_and_bound(wf: Workflow, loop: dict, out: list[Finding]) -> None:
    lid = loop.get("id")
    span, code = resolve_site(wf, loop)
    if span is None:
        detail = {
            "SITE_UNRESOLVABLE": f"`site: {loop.get('site')!r}` resolves to nothing "
                                 "(§4.3.1: marker or line:NN-MM, no third form)",
            "SITE_ID_MISMATCH": f"`site` names a marker that is not this loop's id ({lid!r})",
            "SITE_AMBIGUOUS": f"the marker for {lid!r} occurs more than once in the body",
            "SITE_OUT_OF_RANGE": f"`site: {loop.get('site')!r}` falls outside the body",
            "WINDOW_INVALID": f"`window: {loop.get('window')!r}` must be an int >= 1 "
                              "(the site itself resolves — only the window is wrong)",
        }[code]
        out.append(Finding("R3", "error", wf.name, code, detail, lid))
        return
    start, end = span
    window_text = wf.body[start:end]

    # R10 — a judgment bar must be quotable from the body it terminates.
    if loop.get("judgment_terminated"):
        bar = loop.get("exit_bar")
        if not isinstance(bar, str) or not bar.strip():
            out.append(Finding("R10", "error", wf.name, "EXIT_BAR_MISSING",
                               "`judgment_terminated: true` requires `exit_bar`", lid))
        elif not any(bar in line for line in window_text):
            out.append(Finding("R10", "error", wf.name, "EXIT_BAR_NOT_QUOTED",
                               f"`exit_bar` is not a verbatim substring of the body at `site`: "
                               f"{bar!r}", lid))
    elif loop.get("exit_bar") is not None:
        out.append(Finding("R10", "error", wf.name, "EXIT_BAR_WITHOUT_JUDGMENT",
                           "`exit_bar` declared without `judgment_terminated: true`", lid))

    # R3 — the frontmatter number and the prose number, or the rule is decoration.
    dmax = loop.get("default_max", "<missing>")
    if dmax is None:
        return  # policed by R10 instead (§4.3.1)
    hits = [int(m.group(1)) for line in window_text for m in BOUND_RE.finditer(line)]
    if not hits:
        out.append(Finding("R3", "error", wf.name, "BOUND_UNRESOLVABLE",
                           f"no canonical `max <N>` in the {end - start}-line window at `site`", lid))
    elif len(set(hits)) > 1:
        out.append(Finding("R3", "error", wf.name, "BOUND_AMBIGUOUS",
                           f"window holds disagreeing bounds {sorted(set(hits))}; "
                           "narrow `window` until one loop's bound is in view", lid))
    elif isinstance(dmax, int) and hits[0] != dmax:
        out.append(Finding("R3", "error", wf.name, "BOUND_MISMATCH",
                           f"prose says max {hits[0]}, frontmatter says default_max: {dmax}", lid))


def check_calls(wf: Workflow, by_name: dict[str, Workflow], out: list[Finding]) -> None:
    for edge in wf.calls:
        if not isinstance(edge, dict):
            out.append(Finding("R4", "error", wf.name, "CALL_MALFORMED",
                               f"`calls[]` entry is not a mapping: {edge!r}"))
            continue
        target = edge.get("workflow")
        kind = edge.get("kind", "invoke")
        if kind not in CALL_KINDS:
            out.append(Finding("R4", "error", wf.name, "CALL_KIND_INVALID",
                               f"`kind: {kind!r}` not in {sorted(CALL_KINDS)}"))
        # R4 — the AUTHORED basename resolves. Prose spellings are never a validator input (R5).
        if not isinstance(target, str) or target not in by_name:
            out.append(Finding("R4", "error", wf.name, "CALL_UNRESOLVED",
                               f"`workflow: {target!r}` has no .agent/workflows/<name>.md"))
            continue
        callee = by_name[target]
        callee_loops = {l.get("id"): l for l in callee.loops if isinstance(l, dict)}
        binds = edge.get("binds") or {}
        if not isinstance(binds, dict):
            out.append(Finding("R12", "error", wf.name, "BINDS_MALFORMED",
                               f"`binds` for {target} is not a mapping"))
            continue
        for loop_id, spec in binds.items():
            # R12 — a bind names a loop the callee actually declares.
            if loop_id not in callee_loops:
                out.append(Finding("R12", "error", wf.name, "BIND_UNKNOWN_LOOP",
                                   f"binds `{target}.{loop_id}`, which the callee does not declare"))
                continue
            # R9 — ownership boundary.
            if callee_loops[loop_id].get("override", "forbidden") == "forbidden":
                out.append(Finding("R9", "error", wf.name, "BIND_FORBIDDEN",
                                   f"`{target}.{loop_id}` is `override: forbidden`"))
            if isinstance(spec, dict) and "max" in spec:
                if not isinstance(spec["max"], int) or isinstance(spec["max"], bool) or spec["max"] < 1:
                    out.append(Finding("R12", "error", wf.name, "BIND_MAX_INVALID",
                                       f"`{target}.{loop_id}.max` must be an int >= 1"))
            # §4.5 constraint 1 — on a `partial` edge only loops INSIDE the delegated
            # fragment may be bound. The fragment is named in prose ("Step 3"), so no
            # script can decide reachability: this warns and says why, rather than
            # claiming a check it cannot perform. It is silent on the correct case —
            # `vdd-05` delegates a fragment and binds nothing — and fires on exactly the
            # shape that produced F10, where a caller bound a loop it never reaches.
            if edge.get("partial"):
                out.append(Finding("R12", "warn", wf.name, "BIND_OVER_PARTIAL_EDGE",
                                   f"binds `{target}.{loop_id}` across a fragment delegation "
                                   f"({edge['partial']!r}); reachability is stated in prose and "
                                   "must be confirmed by a human (§4.5 constraint 1)"))
        for loop_id in edge.get("suppresses") or []:
            if loop_id not in callee_loops:
                out.append(Finding("R12", "error", wf.name, "SUPPRESS_UNKNOWN_LOOP",
                                   f"suppresses `{target}.{loop_id}`, which the callee does not declare"))


def check_required_overrides(workflows: list[Workflow], out: list[Finding]) -> None:
    """R2 — `override: required` loops must be bound by every non-optional caller edge."""
    callers: dict[str, list[tuple[Workflow, dict]]] = {}
    for wf in workflows:
        for edge in wf.calls:
            if isinstance(edge, dict) and isinstance(edge.get("workflow"), str):
                callers.setdefault(edge["workflow"], []).append((wf, edge))
    for wf in workflows:
        for loop in wf.loops:
            if not isinstance(loop, dict) or loop.get("override") != "required":
                continue
            for caller, edge in callers.get(wf.name, []):
                if edge.get("optional"):
                    continue
                if loop["id"] not in (edge.get("binds") or {}):
                    out.append(Finding("R2", "error", caller.name, "REQUIRED_BIND_MISSING",
                                       f"must bind `{wf.name}.{loop['id']}` (`override: required`)"))


def check_acyclic(workflows: list[Workflow], out: list[Finding]) -> None:
    """R5 — the authored call graph is acyclic, except a self-edge paired with a
    `recursive: true` loop in the same workflow (§4.5)."""
    graph: dict[str, list[str]] = {}
    for wf in workflows:
        recursive = any(isinstance(l, dict) and l.get("recursive") for l in wf.loops)
        targets = []
        for edge in wf.calls:
            if not isinstance(edge, dict):
                continue
            target = edge.get("workflow")
            if not isinstance(target, str):
                continue
            if target == wf.name:
                if not recursive:
                    out.append(Finding("R5", "error", wf.name, "SELF_EDGE_UNPAIRED",
                                       "`calls[]` self-edge without a `recursive: true` loop"))
                continue  # the paired self-edge is the documented exception
            targets.append(target)
        graph[wf.name] = targets
        if recursive and wf.name not in [e.get("workflow") for e in wf.calls if isinstance(e, dict)]:
            out.append(Finding("R5", "error", wf.name, "RECURSIVE_WITHOUT_SELF_EDGE",
                               "a `recursive: true` loop requires a `calls[]` self-edge (§4.5)"))

    state: dict[str, int] = {}
    reported: set[tuple[str, str]] = set()

    def walk(node: str, stack: list[str]) -> None:
        state[node] = 1
        for nxt in graph.get(node, []):
            if state.get(nxt) == 1:
                pair = (node, nxt)
                if pair not in reported:
                    reported.add(pair)
                    cycle = " -> ".join(stack[stack.index(nxt):] + [nxt]) if nxt in stack else f"{node} -> {nxt}"
                    out.append(Finding("R5", "error", node, "CALL_CYCLE", f"cycle: {cycle}"))
            elif state.get(nxt) is None:
                walk(nxt, stack + [nxt])
        state[node] = 2

    for name in graph:
        if state.get(name) is None:
            walk(name, [name])


def check_body_heuristics(wf: Workflow, out: list[Finding]) -> None:
    """§4.7 — declarations that the body contradicts. Warnings: prose is evidence, not proof."""
    body_text = "\n".join(wf.body)
    if not wf.loops:
        hit = next((k for k in RETRY_KEYWORDS if k in body_text), None)
        if hit:
            out.append(Finding("R6", "warn", wf.name, "EMPTY_LOOPS_WITH_RETRY_PROSE",
                               f"`loops: []` declared on a body containing {hit!r}"))
    # R13 — an omitted call edge. Only spelling 1 is mechanically detectable (§1.2).
    declared = {e.get("workflow") for e in wf.calls if isinstance(e, dict)}
    for i, line in enumerate(wf.body, 1):
        for m in CALL_RE.finditer(line):
            target = m.group(1)
            if target not in declared and (wf.path.parent / f"{target}.md").is_file():
                out.append(Finding("R13", "warn", wf.name, "CALL_NOT_DECLARED",
                                   f"body line {i} calls /{target}, absent from `calls[]`"))


def check_anchor_registry(root: Path, workflows: list[Workflow], out: list[Finding]) -> None:
    """R14 — `documentation-standards` §4.4: a gate that reads an unregistered anchor is
    a defect. This script is that gate, so it checks its own registration."""
    uses_marker = any(
        isinstance(l, dict) and isinstance(l.get("site"), str) and MARKER_RE.fullmatch(l["site"].strip())
        for wf in workflows for l in wf.loops
    )
    if not uses_marker:
        return
    registry = root / REGISTRY_PATH
    if not registry.is_file():
        out.append(Finding("R14", "error", "<registry>", "REGISTRY_MISSING",
                           f"{REGISTRY_PATH} not found; the `loop:<id>` anchor cannot be registered"))
        return
    rows = [l for l in registry.read_text(encoding="utf-8").splitlines()
            if l.lstrip().startswith("|") and REGISTRY_ANCHOR in l]
    if not rows:
        out.append(Finding("R14", "error", "<registry>", "ANCHOR_UNREGISTERED",
                           f"`loop:<id>` has no row in {REGISTRY_PATH} §4.4"))


def run(root: Path) -> tuple[list[Finding], int]:
    """Return (findings, loops_checked). The count is returned rather than recomputed:
    a summary that re-derives its own number can disagree with the run it summarises."""
    workflows = load_workflows(root)
    findings: list[Finding] = []
    by_name = {wf.name: wf for wf in workflows}

    for wf in workflows:
        # R6 — the declaration is mandatory, including for workflows already bounded.
        if wf.contract is None:
            findings.append(Finding("R6", "error", wf.name, "CONTRACT_MISSING",
                                    "no `contract:` block in frontmatter"))
            continue
        if wf.contract.get("version") != 1:
            findings.append(Finding("R6", "error", wf.name, "VERSION_INVALID",
                                    f"`contract.version` must be 1, got {wf.contract.get('version')!r}"))
        if "loops" not in wf.contract:
            findings.append(Finding("R6", "error", wf.name, "LOOPS_MISSING",
                                    "`contract.loops` is required (use `loops: []` if none)"))
            continue

        seen: set[str] = set()
        for loop in wf.loops:
            if not isinstance(loop, dict):
                findings.append(Finding("R6", "error", wf.name, "LOOP_MALFORMED",
                                        f"`loops[]` entry is not a mapping: {loop!r}"))
                continue
            lid = loop.get("id")
            if isinstance(lid, str):
                if lid in seen:
                    findings.append(Finding("R6", "error", wf.name, "ID_DUPLICATE",
                                            "duplicate `id` within this workflow", lid))
                seen.add(lid)
            check_loop_schema(wf, loop, findings)
            check_site_and_bound(wf, loop, findings)
        check_calls(wf, by_name, findings)
        check_body_heuristics(wf, findings)

    check_required_overrides(workflows, findings)
    check_acyclic(workflows, findings)
    check_anchor_registry(root, workflows, findings)
    return findings, sum(len(wf.loops) for wf in workflows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate the workflow loop contract (design spec 095, Component B).",
    )
    parser.add_argument("--root", default=".", help="repository root (default: .)")
    parser.add_argument("--strict", action="store_true",
                        help="exit 1 on errors (Phase 4; warn-only without it)")
    parser.add_argument("--json", action="store_true", help="emit one JSON object per finding")
    args = parser.parse_args(argv)

    root = Path(args.root)
    try:
        findings, loops_checked = run(root)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_USAGE
    except ValueError as exc:  # YAML parse failure, raised with the offending path
        print(f"error: frontmatter is not valid YAML — {exc}", file=sys.stderr)
        return EXIT_YAML
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_USAGE

    errors = [f for f in findings if f.severity == "error"]
    warns = [f for f in findings if f.severity == "warn"]

    if args.json:
        for finding in findings:
            print(json.dumps(finding.as_dict(), ensure_ascii=False))
    else:
        for finding in findings:
            print(finding.as_line())
        # The count is the point: a run that checked nothing must not read like a clean one.
        print(f"checked {loops_checked} loops: {len(errors)} error(s), {len(warns)} warning(s)")

    if errors and args.strict:
        return EXIT_VIOLATIONS
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
