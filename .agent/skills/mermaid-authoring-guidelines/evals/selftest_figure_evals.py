#!/usr/bin/env python3
"""Instrument selftest of the mermaid-authoring-guidelines figure evals (TASK 108, R12.3).

Zero tokens and zero renders: `run_evals.spawn` and the render functions `render_corpus` uses
are replaced by sentinels that raise, and the last rows assert that neither was reached. CI runs
this file as a step of its own; it verifies the INSTRUMENT, never the skill. Nothing here shows
that the skill changes what a model draws; only a campaign does.

What it pins:

  * the case set, the checks and the decision rule of `evals.json` and the README (TASK D8
    revision 3: validity criteria V1, V2, V3, C1 first, then H1, H2, H3, V4);
  * the arms: the `with_skill` prompt is the skill block followed by the `without_skill` prompt,
    byte for byte, for every case; the template and requests carry no rule of the skill;
  * isolation: a context file above the working directory is refused; the named session and pin
    variables leave the child environment, authentication stays;
  * the keys: every quote sits on its lines; decoy types come from the vocabulary of `evals.json`;
  * the fixtures: `pass.md` lints clean, matches its key and passes every contract check that
    applies; `fail.md` fails a check it declares;
  * the grader: one synthetic answer per fidelity rule (with the four fixes of revision 3:
    undirected coverage, legend lists, name numbers, the decoy vocabulary), the geometry checks
    with the dark render and author-set contrast, acceptable forms, K03, a synthetic campaign
    graded end to end, and the `skill-creator` benchmark it feeds;
  * the D8 scores on synthetic runs: median case scores, Δ over the ten cases, a run without a
    figure, validity first, C1, and the reasons of a criterion not evaluated;
  * the calibration: a seeded stratified worksheet with no detector verdict, the top-up, and V2
    from a synthetic labels file;
  * the statistics on toy data;
  * a committed campaign, when one exists: its report and gradings re-derive;
  * the fixes of review round 1 (EI-*, SEC-*): the D8 numbers read from the README rows and
    the predicates at their boundaries; ASCII figures outside fences and labels on ASCII links;
    duplicates, parts, captions, gantt dates, number decoys, edges to invented nodes; the
    sequence legend; provenance and amendments; the shared budget, the repetitions, the bound
    settings; the calibration top-up by construction; the browser of a render; the paths a
    case names;
  * the follow-up of that round (R1-R6 and the cross-area notes): the title and the claim
    sentence of a caption, numbers drawn without a unit, the subjects of a note, indented
    blocks in a document, stages on a fork, the budget lock file, the ASCII budget rules
    outside Q16, blockquoted fences, the lint's legend count, the grader's registration, and
    amendment a1 against the registered keys;
  * wave 1c: a label over the T of a `+` junction, a stage of a chain on a fork line, a
    caption decoy that matches a bare claim only, the residual of the title rule, and the
    ASCII lint over a blockquoted fence;
  * the wave 1c verification: a bracketed reference with an abbreviation at the end of the
    claim sentence, and the time a long caption takes to read;
  * the calibration of campaign 2026-10-opus55-xhigh-r1: an edge through another edge's label
    fails Q05 and is no `label_overlap_or_clip` defect;
  * the fixes of review round 2 in the eval instrument: unlabelled calibration items reported,
    top-up items without a PNG refused (R2-03); Q17 reads the legend only and needs both
    colour-only classes named (R2-07); the sign test's "ahead" as the README defines it (R2-14);
    nan and inf refused as budget, run cap and timeout (SEC2-04); no home path in a committed
    file (SEC2-05); the budget lock in the user's checkout, with a deadline (SEC2-07); the
    matcher heuristics in linear time (SEC2-09).

Every row prints `PASS`, `FAIL` or `SKIP` with its reason. `EXPECTED_CASES` is the number of
rows, pinned as a literal; the last row asserts it.

Exit codes
  0  every row passed or was skipped with a printed reason
  1  a row failed
  2  instrument error: a module did not import, or a test function raised

Standard library only.
"""

from __future__ import annotations

import contextlib
import copy
import glob
import hashlib
import io
import json
import math
import os
import re
import shutil
import sys
import tempfile
import threading
import time
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
sys.path.insert(0, str(SKILL / "scripts"))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(SKILL.parent / "skill-creator" / "scripts"))

#: Rows this battery prints, pinned as a literal. Deriving it from the run would let a deleted
#: row agree with itself.
EXPECTED_CASES = 223

#: The cases of eval delta 4, by slug and id. A case missing from evals.json fails its rows.
CASES = (("c0-control-thumbnails", 0), ("c1-wms-container-view", 1),
         ("c2-card-3ds-sequence", 2), ("c3-leave-request-lifecycle", 3),
         ("c4-reporting-migration-gantt", 4), ("c5-sales-pipeline-dataflow", 5),
         ("c6-clinic-deployment", 6), ("c7-refund-decision", 7),
         ("c8-frontends-services-k33", 8), ("f1-ci-stages-terminal", 9),
         ("f2-roles-operations-matrix", 10))

#: The environment lines of eval delta 8, identical in both arms. The document cases extend the
#: document line with the Mermaid 10.9 previews (the reason Q02 is a fair headline check).
ENV_TERMINAL = ("Your reply is printed in a terminal that shows plain text; it does not render "
                "Markdown or diagrams.")
ENV_DOCUMENT = "Readers open this document on GitHub and in VS Code and JetBrains Markdown previews."

#: The skill's rule vocabulary (r7 section 6). No request, template line or instruction holds it.
NEUTRAL = (r"\bbudgets?\b", r"\bcaptions?\b", r"\blegends?\b", r"\bcrossings?\b", r"classdef",
           r"\binit\b", r"\bpalettes?\b", r"\bone concern\b", r"\bfidelity\b", r"\binvent\w*",
           r"top-to-bottom", r"<small>", r"\bsubgraph titles?\b", r"\baggregat\w*",
           r"\brender it in both\b")
NEUTRAL_CASED = (r"\bTB\b",)

#: Identifiers of the skill's own examples (task-033). No case document may hold one.
MIRAGE = ("n8n", "cvj", "conversationorchestrator", "conversationdispatch", "transcribeworker",
          "diarization", "whisper", "nudge")

#: Tokens that make a multi-word alias generic, so its presence in the paired examples is not a
#: case leak.
GENERIC_TOKENS = {"client", "clients", "app", "apps", "api", "service", "services", "event",
                  "bus", "gateway", "database", "db", "front", "end", "ends", "domain", "the",
                  "and", "of"}

RUN_EVALS_API = ("ARMS", "load_evals", "number_lines", "parse_routing", "bundle_for",
                 "build_prompt", "LEAK_NAMES", "leaks_above", "isolated_workdir", "NotIsolated",
                 "sanitized_env", "build_command", "spawn", "extract_answer")

RESULTS = []          # (name, status, detail)
INSTRUMENT = []       # test functions that raised


def check(name, ok, detail=""):
    RESULTS.append((name, "PASS" if ok else "FAIL", str(detail)))


def skip(name, reason):
    RESULTS.append((name, "SKIP", str(reason)))


class Sentinel:
    """Stands in for a call that spends tokens or renders."""

    def __init__(self, what):
        self.what = what
        self.calls = 0

    def __call__(self, *a, **kw):
        self.calls += 1
        raise AssertionError(f"the selftest reached {self.what}")


SPAWN = Sentinel("run_evals.spawn")
RENDER = Sentinel("a render function")

try:
    import mermaid_model as mm
    import lint_mermaid as lint
    import svg_geometry as sg
    import fidelity as fd
    import stats
    import grade_figures as gf
    import run_evals
    import render_corpus
    import render_check
except Exception as _exc:  # noqa: BLE001 - nothing below can run
    print(f"instrument error: an eval module did not import: {type(_exc).__name__}: {_exc}")
    sys.exit(2)

run_evals.spawn = SPAWN
for _mod in (render_corpus, render_check):
    for _name in ("render", "find_renderers"):
        if hasattr(_mod, _name):
            setattr(_mod, _name, RENDER)

NOTATION = mm.load_notation()


def _ev():
    return gf.load_evals()


def _case(ev, slug):
    for c in ev["evals"]:
        if c.get("slug") == slug or Path(c.get("document", "x/x")).parent.name == slug:
            return c
    return None


def _read(rel):
    return (HERE / rel).read_text(encoding="utf-8")


def _q(result, cid):
    return result["q"][cid]["status"]


# =========================================================================== set shape


def t_api():
    missing = [n for n in RUN_EVALS_API if not hasattr(run_evals, n)]
    check("TC-ME-01 run_evals exposes the API the battery calls", not missing,
          f"missing: {missing}" if missing else f"{len(RUN_EVALS_API)} names")
    check("TC-ME-02 spawn and every render function are sentinels",
          run_evals.spawn is SPAWN and render_corpus.render is RENDER,
          f"spawn={run_evals.spawn!r} render={getattr(render_corpus, 'render', None)!r}")


def t_set_shape():
    ev = _ev()
    found = {(c.get("slug"), int(c["id"])) for c in ev["evals"]}
    check("TC-ME-03a evals.json holds the eleven cases of eval delta 4",
          found == set(CASES), f"extra={sorted(found - set(CASES))} missing={sorted(set(CASES) - found)}")
    q = [c["id"] for c in ev["checks"]]
    k = [c["id"] for c in ev["contract_checks"]]
    core = gf.h_core_ids(ev)
    fam = gf.families_of(ev)
    want_core = [f"Q{i:02d}" for i in (1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 15, 16, 17)]
    check("TC-ME-03b checks Q01-Q17 and K01-K09; H-core leaves out Q07, Q13 and Q14",
          q == [f"Q{i:02d}" for i in range(1, 18)] and k == [f"K{i:02d}" for i in range(1, 10)]
          and core == want_core and set(fam) == set(q) and len(set(fam.values())) == 9,
          f"q={q} k={k} core={core} families={sorted(set(fam.values()))}")
    missing = []
    for c in ev["evals"]:
        for f in ("document", "key", "pass", "fail"):
            if not c.get(f) or not (HERE / c[f]).is_file():
                missing.append(f"{c.get('slug')}:{f}")
    check("TC-ME-03c every declared case file exists", not missing, f"missing={missing}")
    vocab = set(ev.get("decoy_types", []))
    used = set()
    for c in ev["evals"]:
        key = json.loads(_read(c["key"]))
        used |= {d.get("type") for d in key.get("traps", []) + key.get("decoys", [])}
    probe = {"entities": [{"id": "a", "aliases": ["Alpha"]}],
             "traps": [{"id": "t1", "type": "listed_elsewhere", "aliases": ["Omega"]}]}
    try:
        fd.compile_key(probe, vocabulary=vocab | {"listed_elsewhere"})
        accepted = True
    except fd.KeyInvalid:
        accepted = False
    try:
        fd.compile_key(probe, vocabulary=vocab)
        refused = False
    except fd.KeyInvalid:
        refused = True
    check("TC-ME-03d decoy vocabulary: the keys use the types evals.json lists; the matcher has a "
          "rule (a check or a stress role) for each; a listed type is accepted, an unlisted one "
          "refused",
          used <= vocab and vocab <= set(fd.DECOY_CHECK) and gf.decoy_vocabulary(ev) == vocab
          and accepted and refused,
          f"unlisted in keys={sorted(used - vocab)} without a rule={sorted(vocab - set(fd.DECOY_CHECK))} "
          f"accepted={accepted} refused={refused}")
    camp = ev.get("campaign") or {}
    check("TC-ME-03e campaign: claude-opus-5-5 at xhigh, an odd number of reps, 60 USD",
          camp.get("model") == "claude-opus-5-5" and camp.get("effort") == "xhigh"
          and int(camp.get("reps", 0)) % 2 == 1 and float(camp.get("budget_usd", 0)) == 60.0,
          f"{camp}")
    readme = (HERE / "README.md").read_text(encoding="utf-8") if (HERE / "README.md").is_file() else ""
    rows, order = {}, []
    for line in readme.splitlines():
        m = re.match(r"^\|\s*(H1|H2|H3|C1|V1|V2|V3|V4)\s*\|\s*(.+?)\s*\|\s*$", line)
        if m:
            rows[m.group(1)] = m.group(2).replace("`", "")
            order.append(m.group(1))
    empty = Path(tempfile.mkdtemp(prefix="mfe-empty-"))
    try:
        report = gf.build_report([], ev, NOTATION, empty, {},
                                 calibration=HERE / "calibration" / "labels.json")
    finally:
        shutil.rmtree(empty, ignore_errors=True)
    graded = {c["id"]: c["criterion"].replace("`", "") for c in report["decision"]["criteria"]}
    diff = sorted(cid for cid in graded if rows.get(cid) != graded[cid])
    stale = sorted(set(re.findall(r"(?m)^\|\s*([A-Z]\d)\s*\|", readme)) - set(gf.CRITERIA))
    check("TC-ME-03f the README pre-registers the decision table the grader applies, validity "
          "criteria first, and no criterion outside the eight of D8 revision 3",
          not diff and len(rows) == 8 and order == list(gf.VALIDITY + gf.EFFECT)
          and [c["id"] for c in report["decision"]["criteria"]] == order and not stale,
          f"differing={diff} rows={len(rows)} order={order} stale={stale}")
    parsed = readme_rule(readme)
    differ = [f"{path}: README {want} rule {got}" for path, want, got in _rule_pairs(parsed)
              if want is None or got is None or (want != got if isinstance(want, str)
                                                 else float(want) != float(got))]
    check("TC-ME-03g every number of the README's D8 rows equals the DECISION_RULE the grader "
          "applies (EI-12)", not differ and len(list(_rule_pairs(parsed))) == 17,
          _join(differ) or f"{len(list(_rule_pairs(parsed)))} values agree")
    R = gf.DECISION_RULE
    edges = [("H1 Δ 0.249", gf.h1_met(R, 0.249, 0.2), False),
             ("H1 Δ 0.25", gf.h1_met(R, 0.25, 0.2), True),
             ("H1 low 0.099", gf.h1_met(R, 0.3, 0.099), False),
             ("H1 low 0.10", gf.h1_met(R, 0.3, 0.10), True),
             ("H2 Δ 0.149", gf.h2_met(R, 0.149, 0.05), False),
             ("H2 Δ 0.15", gf.h2_met(R, 0.15, 0.05), True),
             ("H2 low 0", gf.h2_met(R, 0.2, 0.0), False),
             ("H2 low 0.001", gf.h2_met(R, 0.2, 0.001), True),
             ("V3 0.899", gf.v3_met(R, [0.899]), False), ("V3 0.9", gf.v3_met(R, [0.9]), True),
             ("C1 0.799", gf.c1_met(R, 0.799), False), ("C1 0.8", gf.c1_met(R, 0.8), True),
             ("V4 0", gf.v4_met(R, [0.2, 0.0]), False),
             ("V4 0.001", gf.v4_met(R, [0.2, 0.001]), True),
             ("V2 0.899", gf.v2_type_met(R["V2"], 0.899, 1.0, 1.0), False),
             ("V2 0.9 and κ 0.8", gf.v2_type_met(R["V2"], 0.9, 0.9, 0.8), True)]
    for n_ahead, want in ((7, False), (8, True)):
        ahead, behind = gf.h3_counts(R, {i: (0.2 if i < n_ahead else 0.0) for i in range(10)},
                                     {0: -0.10})
        edges.append((f"H3 {n_ahead} ahead", gf.h3_met(R, ahead, behind), want))
    ahead, behind = gf.h3_counts(R, {i: 0.2 for i in range(10)}, {0: -0.101})
    edges.append(("H3 C0 behind by 0.101", gf.h3_met(R, ahead, behind), False))
    wrong = [name for name, got, want in edges if got is not want]
    check("TC-ME-03h the D8 predicates decide at the README's boundaries: Δ_H 0.249 not met and "
          "0.25 met, lower bound 0.099 and 0.10, V3 0.899 and 0.9, H3 at 7 and 8 cases ahead "
          "(EI-12)", not wrong, f"wrong={wrong}" if wrong else f"{len(edges)} boundaries hold")


def readme_rule(readme: str) -> dict:
    """The numbers of D8 the README pre-registers, read from its criterion rows and its
    definitions (EI-12). A number the README does not state reads None."""
    rows = {m.group(1): m.group(2) for m in re.finditer(
        r"(?m)^\|\s*(V1|V2|V3|C1|H1|H2|H3|V4)\s*\|\s*(.+?)\s*\|\s*$", readme)}
    num = r"(\d+(?:[.,]\d+)*)"

    def f(pattern, text):
        m = re.search(pattern, text or "")
        return float(m.group(1).replace(",", "")) if m else None

    level = f(r"(\d+) % case-cluster", rows.get("H1"))
    return {
        "V2": {"precision_min": f(r"precision and recall ≥ " + num, rows.get("V2")),
               "recall_min": f(r"precision and recall ≥ " + num, rows.get("V2")),
               "kappa_min": f(r"κ ≥ " + num, rows.get("V2")),
               "items_min": f(r"sample of at least (\d+) outputs", readme)},
        "V3": {"hcore_min": f(r"H-core ≥ " + num, rows.get("V3"))},
        "C1": {"with_min": f(r"rate ≥ " + num, rows.get("C1"))},
        "H1": {"delta_min": f(r"Δ_H ≥ " + num, rows.get("H1")),
               "lower_min": f(r"lower bound ≥ " + num, rows.get("H1"))},
        "H2": {"delta_min": f(r"Δ_H-core ≥ " + num, rows.get("H2")),
               "lower_above": f(r"lower bound > " + num, rows.get("H2"))},
        "H3": {"ahead_min": f(r"ahead on (\d+) or more", rows.get("H3")),
               "behind_beyond": f(r"behind beyond " + num, rows.get("H3"))},
        "V4": {"delta_above": f(r"Δ_H > " + num, rows.get("V4"))},
        "case_score": "median" if re.search(r"A case's score is the median", readme) else None,
        "bootstrap": {"b": f(r"bootstrap with ([\d,]+) resamples", readme),
                      "seed": f(r"resamples and seed (\d+)", readme),
                      "level": level / 100 if level is not None else None}}


def _rule_pairs(parsed: dict):
    """`(path, README value, DECISION_RULE value)` for every value the README states."""
    for key, want in parsed.items():
        if isinstance(want, dict):
            for field, value in want.items():
                yield f"{key}.{field}", value, (gf.DECISION_RULE.get(key) or {}).get(field)
        else:
            yield key, want, gf.DECISION_RULE.get(key)


# =========================================================================== prompts


def t_prompts():
    ev = _ev()
    evals = run_evals.load_evals()
    # the texts the executor sends come from prepare_prompts; the hash it records comes from
    # _write_metadata: the rows compare those, not a second code path (EI-28)
    prompts, _bundles, _errors = run_evals.prepare_prompts(
        evals, run_evals.plan_runs(evals, None, None, 1))
    meta_dir = Path(tempfile.mkdtemp(prefix="mfe-meta-"))
    try:
        ex = run_evals._Executor(types.SimpleNamespace(), meta_dir, prompts, "selftest",
                                 run_evals.Spend(), "selftest", {"sha256": "0" * 64})
        for slug, _cid in CASES:
            name = f"TC-ME-04 {slug}: with_skill is the skill block, then the without_skill prompt"
            case = _case(evals, slug)
            if case is None:
                check(name, False, "case absent from evals.json")
                continue
            try:
                without = prompts[(case["id"], "without_skill")]
                with_ = prompts[(case["id"], "with_skill")]
                block, files = run_evals.bundle_for(case["figure_kind"])
                ok = with_["text"] == block + without["text"]
                same = (without["text"] == run_evals.build_prompt(case, "without_skill", evals)
                        and with_["text"] == run_evals.build_prompt(case, "with_skill", evals))
                carried = all((SKILL / rel).read_text(encoding="utf-8").rstrip("\n") in block
                              for rel in files)
                recorded = True
                for arm, prompt in (("without_skill", without), ("with_skill", with_)):
                    ex._write_metadata(case, arm, prompt)
                    side = json.loads((meta_dir / run_evals.eval_dir_name(case) / arm
                                       / "eval_metadata.json").read_text(encoding="utf-8"))
                    recorded = recorded and side["arm_prompt_sha256"] == hashlib.sha256(
                        prompt["text"].encode("utf-8")).hexdigest()
                check(name, ok and same and carried and recorded and files[0] == "SKILL.md",
                      f"{len(files)} bundle file(s), {len(block)} bytes; identical={ok} "
                      f"build_prompt={same} carried={carried} recorded={recorded}")
            except Exception as exc:  # noqa: BLE001
                check(name, False, f"{type(exc).__name__}: {exc}")
    finally:
        shutil.rmtree(meta_dir, ignore_errors=True)
    try:
        routing = run_evals.parse_routing((SKILL / "SKILL.md").read_text(encoding="utf-8"))
        kinds = {c["figure_kind"] for c in ev["evals"]}
        files = [f for fs in routing.values() for f in fs]
        check("TC-ME-05 the routing table of SKILL.md routes every case kind to files that exist",
              kinds <= set(routing) and all((SKILL / f).is_file() for f in files),
              f"kinds={sorted(kinds)} routed={sorted(routing)}")
    except Exception as exc:  # noqa: BLE001
        check("TC-ME-05 the routing table of SKILL.md routes every case kind to files that exist",
              False, f"{type(exc).__name__}: {exc}")
    texts = [("template", _read(ev.get("prompt_template", "prompts/task-template.md")))]
    for c in ev["evals"]:
        for f in ("request", "environment_line", "output_instruction"):
            texts.append((f"{c.get('slug')}.{f}", str(c.get(f, ""))))
    hits = []
    for where, t in texts:
        hits += [f"{where}: {p}" for p in NEUTRAL if re.search(p, t, re.IGNORECASE)]
        hits += [f"{where}: {p}" for p in NEUTRAL_CASED if re.search(p, t)]
    check("TC-ME-06 no request, environment line, instruction or template names a rule of the skill",
          not hits, f"hits={hits}")
    env = {c.get("slug"): str(c.get("environment_line", "")) for c in ev["evals"]}
    doc_lines = {env.get(s) for s, _ in CASES if s.startswith("c")}
    doc = next(iter(doc_lines)) if len(doc_lines) == 1 else ""
    f2 = env.get("f2-roles-operations-matrix", "")
    problems = []
    if len(doc_lines) != 1:
        problems.append(f"the document cases hold {len(doc_lines)} different lines")
    if not doc.startswith(ENV_DOCUMENT.rstrip(".")) or "Mermaid 10.9" not in doc:
        problems.append("the document line does not name the previews and Mermaid 10.9")
    if env.get("f1-ci-stages-terminal") != ENV_TERMINAL:
        problems.append("f1 does not carry the terminal line")
    if not f2.startswith(ENV_DOCUMENT.rstrip(".")) or "10.9" in f2:
        problems.append("f2 does not carry the document line without a Mermaid version")
    check("TC-ME-07 environment lines: one for the document cases, naming Mermaid 10.9; the "
          "terminal line for f1; the document line for f2",
          not problems, _join(problems) if problems else f"{doc!r}")


# =========================================================================== isolation


def t_isolation():
    base = tempfile.mkdtemp(prefix="mfe-iso-")
    try:
        for name, make in (("CLAUDE.md", lambda p: Path(p).write_text("x", encoding="utf-8")),
                           (".claude", os.makedirs)):
            room = tempfile.mkdtemp(dir=base)
            make(os.path.join(room, name))
            child = os.path.join(room, "work")
            os.makedirs(child)
            leaks = run_evals.leaks_above(child)
            check(f"TC-ME-08 leaks_above finds {name} above the working directory",
                  any(x.endswith(name) for x in leaks), f"leaks={leaks}")
        room = tempfile.mkdtemp(dir=base)
        Path(room, "CLAUDE.md").write_text("x", encoding="utf-8")
        refused = False
        try:
            made = run_evals.isolated_workdir(base=room)
            shutil.rmtree(made, ignore_errors=True)
        except run_evals.NotIsolated:
            refused = True
        check("TC-ME-08 isolated_workdir refuses a directory under a context file", refused,
              "isolated_workdir returned instead of raising NotIsolated")
        clean_base = tempfile.mkdtemp(dir=base)
        clean = run_evals.isolated_workdir(base=clean_base)
        check("TC-ME-08 a clean temporary directory is accepted",
              os.path.isdir(clean) and not run_evals.leaks_above(clean),
              f"leaks={run_evals.leaks_above(clean)}")
    finally:
        shutil.rmtree(base, ignore_errors=True)
    named = tuple(getattr(run_evals, "REMOVED_ENV_VARS", ()))
    auth = tuple(getattr(run_evals, "AUTH_ENV_VARS", ()))
    env = {name: "x" for name in named}
    env.update({name: "secret" for name in auth})
    env.update({"HOME": "/home/u", "PATH": "/bin"})
    out = run_evals.sanitized_env(env)
    removed = run_evals.removed_env_names(env) if hasattr(run_evals, "removed_env_names") else []
    check("TC-ME-09 sanitized_env removes the named list, CLAUDECODE and CLAUDE_EFFORT among "
          "them, keeps the authentication variables, and names what it removed",
          {"CLAUDECODE", "CLAUDE_EFFORT"} <= set(named) and not set(named) & set(out)
          and all(out.get(a) == "secret" for a in auth) and bool(auth)
          and out.get("HOME") == "/home/u" and out.get("PATH") == "/bin"
          and sorted(removed) == sorted(named),
          f"named={len(named)} kept={sorted(set(out) - set(auth) - {'HOME', 'PATH'})} "
          f"auth={len(auth)} removed={len(removed)}")
    cmd = run_evals.build_command("PROMPT", "claude-opus-5-5", "xhigh")
    flags_ok = all(f in cmd for f in ("--safe-mode", "--disable-slash-commands",
                                      "--strict-mcp-config", "--no-session-persistence",
                                      "--max-budget-usd", "--output-format", "--disallowed-tools"))
    check("TC-ME-10 the command pins model and effort, turns tools off, and passes the prompt whole",
          flags_ok and cmd[cmd.index("--model") + 1] == "claude-opus-5-5"
          and cmd[cmd.index("--effort") + 1] == "xhigh" and cmd[cmd.index("-p") + 1] == "PROMPT"
          and cmd[cmd.index("--tools") + 1] == "" and "Skill" in cmd,
          " ".join(c if c else '""' for c in cmd[:14]))
    wrapped = ("````markdown\n**Figure 1.** X.\n\n```mermaid\nflowchart TB\n  A --> B\n```\n````\n")
    ans = run_evals.extract_answer({"result": wrapped})
    check("TC-ME-11 extract_answer removes an outer Markdown wrapper and keeps the inner fence",
          ans.lstrip().startswith("**Figure 1.**") and "```mermaid" in ans, repr(ans[:60]))
    listing = "```\nlint -> unit tests -> build site\n```\n\nRun it with:\n\n```\nmake ci\n```\n"
    figures = "```\nlint -> test\n```\n\n```mermaid\nflowchart TB\n  A --> B\n```\n"
    bare = "````\n**Figure 1.** X.\n\n```mermaid\nflowchart TB\n  A --> B\n```\n````\n"
    kept = [run_evals.unwrap_outer_fence(t) for t in (listing, figures)]
    opened = run_evals.unwrap_outer_fence(bare)
    check("TC-ME-11b a bare fence that its own closing line ends before the last line is a "
          "figure, not a wrapper: a figure then a listing, or an ASCII then a Mermaid figure, "
          "stay as written; a longer bare wrapper still opens (EI-14)",
          kept == [(listing, False), (figures, False)] and opened[1]
          and opened[0].startswith("**Figure 1.**") and opened[0].rstrip().endswith("```"),
          f"kept={[k[1] for k in kept]} opened={opened[1]}")
    out_s, err_s = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out_s), contextlib.redirect_stderr(err_s):
        rc = run_evals.main(["--dry-run", "--reps", "1", "--cases", "8"])
    plan_out = out_s.getvalue()
    c8 = _case(run_evals.load_evals(), "c8-frontends-services-k33") or {}
    labels = [f"{run_evals.eval_dir_name(c8)}/{arm}/run-1" for arm in run_evals.ARMS] if c8 else []
    routed = run_evals.bundle_for("flowchart")[1]
    listed = labels and all(lab in plan_out for lab in labels) \
        and all(f in plan_out for f in routed)
    check("TC-ME-12 a dry run on the committed tree exits 0, lists the planned runs and the bundle "
          "files, and spawns nothing (EI-21)", rc == 0 and SPAWN.calls == 0 and bool(listed),
          f"exit={rc} spawn calls={SPAWN.calls} listed={bool(listed)} "
          f"{err_s.getvalue().strip()[:160]}")
    evals = run_evals.load_evals()
    first = evals["evals"][0]
    refused = []
    for field_, value in (("document", "../" * 12 + "etc/hosts"), ("key", "../evals.json")):
        try:
            if field_ == "document":
                run_evals.case_prompt(dict(first, document=value), evals)
            else:
                run_evals.load_key(dict(first, key=value), evals)
        except run_evals.InstrumentError:
            refused.append(f"run_evals {field_}")
        try:
            gf.case_file(_ev(), dict(first, **{field_: value}), field_)
        except gf.InstrumentError:
            refused.append(f"grader {field_}")
    check("TC-ME-35 a case document or key outside fixtures/ never reaches a prompt or the "
          "grader: the executor and the grader refuse it (SEC-13)", len(refused) == 4,
          f"refused={refused}")


# =========================================================================== keys


def _quote_sites(node, out):
    if isinstance(node, dict):
        if isinstance(node.get("quote"), str) and isinstance(node.get("lines"), list):
            out.append(node)
        for v in node.values():
            _quote_sites(v, out)
    elif isinstance(node, list):
        for v in node:
            _quote_sites(v, out)
    return out


def t_keys():
    ev = _ev()
    vocab = set(ev.get("decoy_types", []))
    fams = set((ev.get("families") or {}).keys())
    for slug, cid in CASES:
        name = f"TC-ME-13 {slug}: key quotes sit on their lines; types, ids and families valid"
        case = _case(ev, slug)
        if case is None:
            check(name, False, "case absent from evals.json")
            continue
        problems = []
        try:
            key = json.loads(_read(case["key"]))
            lines = _read(case["document"]).split("\n")
            fd.compile_key(key)
            for site in _quote_sites(key, []):
                try:
                    block = " ".join(lines[n - 1] for n in site["lines"])
                except (IndexError, TypeError):
                    problems.append(f"lines {site['lines']} outside the document")
                    continue
                if " ".join(site["quote"].split()) not in " ".join(block.split()):
                    problems.append(f"quote {site['quote'][:40]!r} not on lines {site['lines']}")
            for d in key.get("traps", []) + key.get("decoys", []):
                if d.get("type") not in vocab:
                    problems.append(f"decoy {d.get('id')} type {d.get('type')!r} outside the vocabulary")
            ids = [x["id"] for sec in ("entities", "groups") for x in key.get(sec, [])]
            dids = [d.get("id") for d in key.get("traps", []) + key.get("decoys", [])]
            for label, seq in (("entity or group", ids), ("decoy", dids)):
                dup = sorted({x for x in seq if seq.count(x) > 1})
                if dup:
                    problems.append(f"duplicate {label} ids {dup}")
            used = set(key.get("families") or []) | set(key.get("families_conditional") or {}) \
                | set(key.get("families_not_applicable") or {})
            if not used <= fams:
                problems.append(f"unknown families {sorted(used - fams)}")
            if key.get("case") != cid or key.get("medium") not in ("document", "terminal") \
                    or key.get("medium") != case.get("medium", key.get("medium")):
                problems.append(f"case {key.get('case')} medium {key.get('medium')}")
        except Exception as exc:  # noqa: BLE001
            problems.append(f"{type(exc).__name__}: {exc}")
        check(name, not problems, _join(problems) or "ok")


def t_mirage():
    ev = _ev()
    hits = []
    for c in ev["evals"]:
        text = _read(c["document"]).casefold()
        hits += [f"{c.get('slug')}: {w}" for w in MIRAGE if w in text]
    check("TC-ME-14 no case document holds an identifier of the skill's own examples", not hits,
          f"hits={hits}")
    pe = SKILL / "references" / "paired-examples.md"
    if not pe.is_file():
        skip("TC-ME-14 the paired examples hold no case identifier",
             "references/paired-examples.md is absent")
        return
    toks = fd.tokens(pe.read_text(encoding="utf-8"))
    leaks = []
    for c in ev["evals"]:
        key = json.loads(_read(c["key"]))
        for sec in ("entities", "groups"):
            for it in key.get(sec, []):
                for alias in it.get("aliases", []):
                    t = fd.tokens(alias)
                    if len(t) >= 2 and not set(t) <= GENERIC_TOKENS and fd._contains(toks, t):
                        leaks.append(f"{c.get('slug')}: {alias}")
    check("TC-ME-14 the paired examples hold no case identifier", not leaks, f"leaks={leaks}")


# =========================================================================== fixtures


def _fixture_geometry(case, which):
    for name in (f"{which}.geometry.json", f"{which}.geom.json"):
        p = HERE / Path(case[which]).parent / name
        if p.is_file():
            return json.loads(p.read_text(encoding="utf-8"))
    return None


#: Declared failures a fixture does not show yet, with the change that makes it show them
#: (EI-20). The row stays strict for every other check; an entry whose check fails already is
#: stale and fails the row, so the list cannot outlive the fix. C1 fail.md draws BUS as a
#: rectangle beside SLOT now, so its classes differ by fill alone and Q17 fails as declared.
PENDING_DECLARATIONS = {}


def declared_misses(slug: str, want: list, statuses: dict, pending=None) -> tuple:
    """`(missed, stale, render_only)` of a fail.md against the checks it declares (EI-20).
    *missed*: a declared check the grader computes and that does not fail, or that never
    applies; *stale*: a pending entry whose check fails already; *render_only*: the declared
    checks that need renders the fixture does not carry. *pending*: default
    `PENDING_DECLARATIONS`."""
    pending = PENDING_DECLARATIONS if pending is None else pending
    missed = [c for c in want if statuses.get(c) in ("pass", "na") and (slug, c) not in pending]
    stale = [c for c in want if (slug, c) in pending and statuses.get(c) == "fail"]
    render_only = [c for c in want if statuses.get(c) == "skip"]
    return missed, stale, render_only


def t_fixtures():
    ev = _ev()
    settings_bad, contract_bad, contract_pass = [], [], 0
    for slug, _cid in CASES:
        case = _case(ev, slug)
        names = (f"TC-ME-15 {slug}: pass.md has no lint error",
                 f"TC-ME-16 {slug}: pass.md matches its key (Q09-Q12, no decoy)",
                 f"TC-ME-16 {slug}: pass.md passes every static headline check",
                 f"TC-ME-17 {slug}: fail.md fails every check it declares that the grader "
                 f"computes without renders")
        if case is None:
            for n in names:
                check(n, False, "case absent from evals.json")
            continue
        try:
            key, ck, _sha = gf.load_key(ev, case)
            text = _read(case["pass"])
            errors = [f"{f.rule}@{f.line}" for f in lint.lint_text(text, case["pass"], notation=NOTATION)
                      if f.severity == "error"]
            check(names[0], not errors, f"errors={errors}")
            res = gf.grade_answer(text, case, key, ck, ev, NOTATION, _fixture_geometry(case, "pass"))
            bad = [f"{c}: {res['q'][c]['evidence'][:160]}" for c in ("Q09", "Q10", "Q11", "Q12")
                   if _q(res, c) != "pass"]
            check(names[1], not bad and not res["fidelity"]["decoy_hits"],
                  _join(bad + [f"decoys {res['fidelity']['decoy_hits']}"] if res["fidelity"]["decoy_hits"] else bad)
                  or "Q09-Q12 pass")
            static = [c for c in ("Q07", "Q08", "Q13", "Q14", "Q15", "Q16", "Q17")
                      if _q(res, c) == "fail"]
            check(names[2], not static,
                  _join(f"{c}: {res['q'][c]['evidence'][:140]}" for c in static) or "no static check fails")
            want = list(case.get("fail_expect_failed") or [])
            fres = gf.grade_answer(_read(case["fail"]), case, key, ck, ev, NOTATION,
                                   _fixture_geometry(case, "fail"))
            statuses = {c: _q(fres, c) for c in want}
            missed, stale, render_only = declared_misses(slug, want, statuses)
            if not want:
                check(names[3], False, "evals.json lists no fail_expect_failed for this case")
            elif len(render_only) == len(want):
                skip(names[3], f"{want} need renders, and the fixture carries no committed geometry")
            else:
                pending = [c for c in want if (slug, c) in PENDING_DECLARATIONS]
                check(names[3], not missed and not stale,
                      f"declared={want} missed={missed} stale={stale} "
                      f"render-dependent={render_only} pending={pending}")
            for kid, st in res["k"].items():
                if st["status"] == "pass":
                    contract_pass += 1
                elif st["status"] == "fail":
                    contract_bad.append(f"{slug} {kid}: {st['evidence'][:100]}")
            fences = mm.extract_fences(text, ("mermaid",))
            for f in fences:
                kind = mm.parse_figure(f).kind
                if f.body.split("\n")[0] != NOTATION["settings"].get(kind):
                    settings_bad.append(f"{slug} line {f.start}")
        except Exception as exc:  # noqa: BLE001
            for n in names:
                if not any(r[0] == n for r in RESULTS):
                    check(n, False, f"{type(exc).__name__}: {exc}")
    probe = declared_misses("probe", ["Q09", "Q12", "Q04"], {"Q09": "pass", "Q12": "fail",
                                                            "Q04": "skip"})
    pending = {("probe", "Q17"): "a fixture change pending"}
    stale = declared_misses("probe", ["Q17"], {"Q17": "fail"}, pending)
    waiting = declared_misses("probe", ["Q17"], {"Q17": "pass"}, pending)
    check("TC-ME-17c the fixture row names every declared check that passes or never applies, "
          "lists the ones that need renders, and calls a pending entry stale once its check "
          "fails; no entry is pending, C1 Q17 included (EI-20)",
          probe == (["Q09"], [], ["Q04"]) and stale == ([], ["Q17"], [])
          and waiting == ([], [], []) and PENDING_DECLARATIONS == {},
          f"probe={probe} stale={stale} waiting={waiting} pending={PENDING_DECLARATIONS}")
    check("TC-ME-17b every pass.md opens each Mermaid fence with the current settings line of "
          "notation.json and passes every contract check that applies",
          not settings_bad and not contract_bad and contract_pass > 0,
          _join(settings_bad + contract_bad) or f"{contract_pass} contract check(s) pass")


def _join(items):
    items = [str(i) for i in items]
    return "; ".join(items[:5]) + (f"; and {len(items) - 5} more" if len(items) > 5 else "")


# =========================================================================== grader unit cases

UNIT_KEY = {
    "schema": "mermaid-key/v1", "case": 99, "medium": "document", "required_concern": "structure",
    "families": ["renders", "geometry", "budget", "concern", "fidelity", "docs", "form", "colour"],
    "families_conditional": {"ascii": "only when the answer holds a text fence"},
    "entities": [{"id": "a", "aliases": ["Alpha service"], "soft_aliases": ["Alpha"]},
                 {"id": "b", "aliases": ["Beta store"]},
                 {"id": "c", "aliases": ["Gamma app"]}, {"id": "d", "aliases": ["Delta app"]}],
    "groups": [{"id": "apps", "aliases": ["client apps"], "members": ["c", "d"]},
               {"id": "core", "aliases": ["core zone"], "members": ["a", "b"]}],
    "relations": [{"id": "r1", "from": "apps", "to": "a", "required": True},
                  {"id": "r2", "from": "a", "to": "b", "required": True},
                  {"id": "r3", "from": "b", "to": "d", "directed": False, "required": False}],
    "numbers": [{"value": 30, "unit": "s", "subjects": ["a"]},
                {"value": 5, "unit": "min", "subjects": ["b"]}],
    "name_numbers": [{"text": "Release 7.4"}],
    "traps": [{"id": "t1", "type": "invented_hub", "aliases": ["Message broker"]},
              {"id": "t2", "type": "unstated_relation", "relation": {"from": "c", "to": "b"}},
              {"id": "t3", "type": "number_from_other_rule", "value": 5, "unit": "min",
               "wrong_subjects": ["a"]},
              {"id": "t4", "type": "invented_group", "aliases": ["Backend"]}],
    "caption_claim_traps": [{"id": "cc1", "claims": ["every call is encrypted"]}],
}
UNIT_CASE = {"id": 99, "slug": "unit", "figure_kind": "flowchart", "concern": "structure",
             "medium": "document"}


def _fence(body, lang="mermaid"):
    return f"```{lang}\n{body}\n```\n"


def _match(key, answer):
    ck = fd.compile_key(key)
    ans = gf.read_answer(answer, UNIT_CASE, ck)
    return fd.match(ck, [u.facts for u in ans.units], ans.forms)


def t_fidelity_rules():
    nf = fd.normalize("«Ёлка» <b>Front-Ends</b>#quot; Узел_2")
    check("TC-ME-18 normalize: NFC, tags, entities, quotes, casefold, Cyrillic, yo to ye",
          nf == "елка front ends узел 2" and fd.NORMALIZE_VERSION.startswith("fidelity-normalize/"),
          repr(nf))
    nums = [(n.value, n.unit) for n in fd.extract_numbers(
        "100 requests/s, 60 s, p99 80 ms, S3, v2, app-01, 3-D Secure, $50, 0,1 %, 2026-11-02, "
        "§2.4, 5 лет, 3 рабочих дня")]
    check("TC-ME-18 numbers keep their units and skip identifiers and section references",
          nums == [("2026-11-02", "date"), (100.0, "req/s"), (60.0, "s"), (80.0, "ms"),
                   (50.0, "$"), (0.1, "%"), (5.0, "y"), (3.0, "d")], f"{nums}")
    agg = _match(UNIT_KEY, _fence('flowchart TB\n  APPS["client apps<br/><small>Gamma app · Delta app'
                                  '</small>"] --> A["Alpha service<br/>Release 7.4"]\n'
                                  '  A -->|"30 s"| B[("Beta store")]'))
    v = agg["verdicts"]
    check("TC-ME-18 an aggregate node covers its group's relation in one stroke; name numbers are names",
          all(v[c]["passed"] for c in v) and not agg["decoy_hits"], f"{_verdicts(v)} {agg['decoy_hits']}")
    rev = _match(UNIT_KEY, _fence('flowchart TB\n  C["Gamma app"] --> A["Alpha service"]\n'
                                  '  D["Delta app"] --> A\n  B["Beta store"] --> A'))
    check("TC-ME-18 an edge against the stated direction reads backwards and fails Q09",
          not rev["verdicts"]["Q09"]["passed"] and any("reads backwards" in u for u in rev["unsupported"])
          and not rev["verdicts"]["Q10"]["passed"], _verdicts(rev["verdicts"]))
    und = _match(UNIT_KEY, _fence('flowchart TB\n  D["Delta app"] --> B["Beta store"]'))
    check("TC-ME-18 an undirected relation holds in either direction",
          und["verdicts"]["Q09"]["passed"], _verdicts(und["verdicts"]))
    trap = _match(UNIT_KEY, _fence('flowchart TB\n  C["Gamma app"] --> B["Beta store"]\n'
                                   '  M["Message broker"] --> B'))
    check("TC-ME-18 an unstated relation and an invented hub hit their decoys and fail Q09 and Q12",
          {"t1", "t2"} <= set(trap["decoy_hits"]) and not trap["verdicts"]["Q09"]["passed"]
          and not trap["verdicts"]["Q12"]["passed"], f"{trap['decoy_hits']} {_verdicts(trap['verdicts'])}")
    soft = _match(UNIT_KEY, _fence('flowchart TB\n  A["Alpha"] --> B["Beta store"]'))
    check("TC-ME-18 a soft alias maps the node and flags it renamed, for K07 only",
          soft["verdicts"]["Q12"]["passed"] and soft["renamed"], f"renamed={soft['renamed']}")
    grp = _match(UNIT_KEY, _fence('flowchart TB\n  subgraph X["Backend"]\n    A["Alpha service"]\n'
                                  '    C["Gamma app"]\n  end\n  subgraph Z["core zone"]\n'
                                  '    B["Beta store"]\n  end\n  A --> B'))
    same = _match(UNIT_KEY, _fence('flowchart TB\n  subgraph X["Storage tier"]\n    A["Alpha service"]'
                                   ' --> B["Beta store"]\n  end'))
    check("TC-ME-18 a group the document does not define is invented; a stated group fits, and "
          "its members under another title are a rename",
          not grp["verdicts"]["Q12"]["passed"] and "t4" in grp["decoy_hits"]
          and sum("Backend" in i for i in grp["invented"]) == 1
          and not any("core zone" in i for i in grp["invented"])
          and same["verdicts"]["Q12"]["passed"] and any("Storage tier" in r for r in same["renamed"]),
          f"{grp['invented']} | renamed={same['renamed']}")
    num = _match(UNIT_KEY, _fence('flowchart TB\n  A["Alpha service<br/>5 min"] --> B["Beta store"]'))
    check("TC-ME-18 a number on the wrong subject fails Q11 and hits its decoy",
          not num["verdicts"]["Q11"]["passed"] and "t3" in num["decoy_hits"], _verdicts(num["verdicts"]))
    seq_key = {"entities": [{"id": "p", "aliases": ["Portal"]}, {"id": "s", "aliases": ["Server"]}],
               "messages": [{"id": "m1", "from": "p", "to": "s", "keywords": ["login"], "step": 1},
                            {"id": "m2", "from": "s", "to": "p", "reply": True, "keywords": ["token"],
                             "step": 2},
                            {"id": "m3", "from": "p", "to": "s", "keywords": ["fetch"], "step": 3}],
               "order": ["m1", "m2", "m3"],
               "blocks": [{"id": "b1", "kind": ["loop"], "messages": ["m3"]}],
               "traps": [{"id": "t1", "type": "invented_block",
                          "block": {"kind": ["loop"], "encloses_any": ["m1"]}}]}
    head = "sequenceDiagram\n  participant P as Portal\n  participant S as Server\n"
    good = _match(seq_key, _fence(head + "  P->>S: login\n  S-->>P: token\n  loop retry\n"
                                         "    P->>S: fetch\n  end"))
    bad = _match(seq_key, _fence(head + "  loop retry\n    P->>S: login\n  end\n  P->>S: fetch\n"
                                        "  S-->>P: token"))
    check("TC-ME-18 sequence: a stated loop passes; an invented loop and a broken order fail Q09",
          all(x["passed"] for x in good["verdicts"].values()) and not bad["verdicts"]["Q09"]["passed"]
          and "t1" in bad["decoy_hits"], f"good={_verdicts(good['verdicts'])} bad={bad['unsupported']}")
    st_key = {"entities": [{"id": "o", "aliases": ["Open"]}, {"id": "c", "aliases": ["Closed"]},
                           {"id": "u", "kind": "writer", "aliases": ["user"]}],
              "relations": [{"id": "tr1", "kind": "transition", "from": "o", "to": "c",
                             "writer": None, "condition": "timeout"},
                            {"id": "tr0", "kind": "transition", "from": "[*]", "to": "o"}],
              "initial": ["o"], "final": ["c"],
              "traps": [{"id": "t1", "type": "invented_writer", "transitions": ["tr1"],
                         "aliases": ["user", "cron"]}]}
    st = _match(st_key, _fence("stateDiagram-v2\n  [*] --> Open\n  Open --> Closed : user"))
    check("TC-ME-18 state: a writer on a transition the text drives by a condition is invented",
          not st["verdicts"]["Q12"]["passed"] and "t1" in st["decoy_hits"] and st["verdicts"]["Q10"]["passed"],
          _verdicts(st["verdicts"]))
    g_key = {"entities": [{"id": "x", "aliases": ["Build"]}, {"id": "y", "aliases": ["Test"]},
                          {"id": "z", "aliases": ["Ship"]}],
             "groups": [{"id": "dev", "aliases": ["Dev"], "members": ["x", "y", "z"]}],
             "relations": [{"id": "d1", "kind": "dependency", "from": "x", "to": "y"},
                           {"id": "d2", "kind": "dependency", "from": "x", "to": "z"}],
             "numbers": [{"value": 2, "unit": "d", "subjects": ["x"]},
                         {"value": 1, "unit": "d", "subjects": ["y", "z"]}],
             "calendar": {"start": "2026-11-02", "excludes": ["saturday", "sunday"]},
             "tasks": [{"id": "x", "start": "2026-11-02", "duration_days": 2, "deps": []},
                       {"id": "y", "start": "2026-11-04", "duration_days": 1, "deps": ["x"]},
                       {"id": "z", "start": "2026-11-04", "duration_days": 1, "deps": ["x"]}],
             "traps": [{"id": "t1", "type": "invented_dependency", "relation": {"from": "y", "to": "z"}},
                       {"id": "t2", "type": "calendar_rule", "required_statement": "excludes weekends"},
                       {"id": "t3", "type": "invented_number"}]}
    gh = "gantt\n  dateFormat YYYY-MM-DD\n"
    g_good = _match(g_key, _fence(gh + "  excludes weekends\n  section Dev\n  Build :x, 2026-11-02, 2d\n"
                                       "  Test :y, after x, 1d\n  Ship :z, after x, 1d"))
    g_bad = _match(g_key, _fence(gh + "  section Dev\n  Build :x, 2026-11-03, 2d\n"
                                      "  Test :y, after x, 1d\n  Ship :z, after y, 1d"))
    check("TC-ME-18 gantt: an invented dependency, a wrong date and no weekend rule fail; the plan passes",
          all(x["passed"] for x in g_good["verdicts"].values())
          and {"t1", "t2", "t3"} <= set(g_bad["decoy_hits"]) and not g_bad["verdicts"]["Q10"]["passed"],
          f"good={_verdicts(g_good['verdicts'])} bad={g_bad['decoy_hits']}")
    chain = fd.parse_ascii("lint -> test -+-> docs ---+-> deploy\n"
                           "              |           |\n"
                           "              +-> check --+")
    names = {n: t for (t, _r, n) in chain["nodes"]}
    edges = {(names[a], names[b]) for a, b in chain["edges"]}
    tree = fd.parse_ascii("root\n├── left\n└── right")
    tnames = {n: t for (t, _r, n) in tree["nodes"]}
    tedges = {(tnames[a], tnames[b]) for a, b in tree["edges"]}
    check("TC-ME-18 ASCII: an arrowed chain with a parallel branch and a tree without heads read right",
          edges == {("lint", "test"), ("test", "docs"), ("test", "check"), ("docs", "deploy"),
                    ("check", "deploy")} and tedges == {("root", "left"), ("root", "right")},
          f"chain={sorted(edges)} tree={sorted(tedges)}")
    m_key = {"entities": [{"id": "r1", "aliases": ["Reader"]}, {"id": "w1", "aliases": ["Writer"]},
                          {"id": "o1", "aliases": ["read"]}, {"id": "o2", "aliases": ["write"]}],
             "matrix": {"rows": ["o1", "o2"], "cols": ["r1", "w1"],
                        "allowed": [["o1", "r1"], ["o1", "w1"], ["o2", "w1"]], "complete": True},
             "traps": [{"id": "t1", "type": "unstated_relation", "relation": {"from": "r1", "to": "o2"}}]}
    good_t = "| Role | read | write |\n| :--- | :---: | :---: |\n| Reader | yes | no |\n| Writer | ✓ | ✓ |\n"
    bad_t = "| Role | read | write |\n| :--- | :---: | :---: |\n| Reader | yes | x |\n| Writer | yes | — |\n"
    mg, mb = _match(m_key, good_t), _match(m_key, bad_t)
    check("TC-ME-18 table: a transposed matrix passes; an extra cell is unsupported, a missing one missing",
          all(x["passed"] for x in mg["verdicts"].values()) and not mb["verdicts"]["Q09"]["passed"]
          and not mb["verdicts"]["Q10"]["passed"] and "t1" in mb["decoy_hits"],
          f"good={_verdicts(mg['verdicts'])} bad={_verdicts(mb['verdicts'])}")
    l_key = {"entities": [{"id": "a", "aliases": ["lint"]}, {"id": "b", "aliases": ["test"]},
                          {"id": "c", "aliases": ["docs check"]}, {"id": "d", "aliases": ["deploy"]}],
             "relations": [{"id": "o1", "kind": "order", "from": "a", "to": "b"},
                           {"id": "o2", "kind": "order", "from": "a", "to": "c"},
                           {"id": "o3", "kind": "order", "from": "b", "to": "d"},
                           {"id": "o4", "kind": "order", "from": "c", "to": "d"}],
             "stage_order": {"layers": [["a"], ["b", "c"], ["d"]]},
             "traps": [{"id": "t1", "type": "order_violation", "relation": {"from": "b", "to": "c"}}]}
    list_case = dict(UNIT_CASE, figure_kind="ascii")
    ckl = fd.compile_key(l_key)
    lg = gf.read_answer("1. lint\n2. test and docs check, in parallel\n3. deploy\n", list_case, ckl)
    lb = gf.read_answer("1. lint\n2. test\n3. docs check\n4. deploy\n", list_case, ckl)
    rg = fd.match(ckl, [u.facts for u in lg.units], lg.forms)
    rb = fd.match(ckl, [u.facts for u in lb.units], lb.forms)
    check("TC-ME-18 list: one item for parallel stages passes; consecutive items claim an order",
          all(x["passed"] for x in rg["verdicts"].values()) and "t1" in rb["decoy_hits"]
          and not rb["verdicts"]["Q09"]["passed"], f"good={_verdicts(rg['verdicts'])} bad={rb['decoy_hits']}")
    d_key = {"entities": [{"id": "age", "aliases": ["age check"]}, {"id": "amt", "aliases": ["amount check"]},
                          {"id": "ok", "aliases": ["Approve"]}, {"id": "no", "aliases": ["Decline"]}],
             "relations": [{"id": "b1", "kind": "branch", "from": "age", "to": "amt"},
                           {"id": "b2", "kind": "branch", "from": "age", "to": "no"},
                           {"id": "b3", "kind": "branch", "from": "amt", "to": "ok"},
                           {"id": "b4", "kind": "branch", "from": "amt", "to": "no"}],
             "decisions": [{"id": "r1", "checks": ["age"]}, {"id": "r2", "checks": ["amt"]}],
             "order": [{"first": "r1", "then": "r2"}],
             "traps": [{"id": "t1", "type": "order_violation", "before": "amt", "after": "age"}]}
    dec = _match(d_key, _fence('flowchart TB\n  M{"amount check"} --> G{"age check"}\n'
                               '  G --> N["Decline"]\n  M --> K["Approve"]'))
    check("TC-ME-18 decision flow: a check drawn before the check the text puts first fails Q09",
          not dec["verdicts"]["Q09"]["passed"] and "t1" in dec["decoy_hits"], f"{dec['unsupported']}")
    ck = fd.compile_key(UNIT_KEY)
    cc = fd.caption_claims("**Figure 1.** Alpha service and Beta store — every call is encrypted.",
                           ck, {"a", "b"}, [])
    over = fd.caption_claims("**Figure 2.** Gamma app calls Alpha service within 30 s.", ck, {"a"}, [])
    fine = fd.caption_claims("**Figure 3.** Alpha service writes to Beta store within 30 s.", ck,
                             {"a", "b"}, [[30.0, "s"]])
    check("TC-ME-18 caption: a decoy claim and an undrawn name fail; the label number is not a claim",
          not cc["ok"] and "cc1" in cc["decoy_hits"] and not over["ok"] and fine["ok"],
          f"{cc['problems']} | {over['problems']} | {fine['problems']}")
    one = _match(UNIT_KEY, _fence('flowchart TB\n  A["Alpha service"]'))
    check("TC-ME-18 a one-node figure passes Q09 and fails Q10",
          one["verdicts"]["Q09"]["passed"] and not one["verdicts"]["Q10"]["passed"],
          _verdicts(one["verdicts"]))


def _verdicts(v):
    return " ".join(f"{k}={'P' if x['passed'] else 'F'}" for k, x in v.items())


def _metrics(kind, crossings=0, font=14.0, texts=(), page="#ffffff", **extra):
    """Synthetic `svg_geometry` metrics of a clean render; *extra* replaces any key."""
    metrics = {k: [] for k in ("crossing_pairs", "edges_through_nodes", "title_crossings",
                               "label_overlaps", "clipped_labels", "duplicate_edges", "warnings")}
    metrics.update({"diagram": gf.ROLES.get(kind, (kind,))[0], "width": 600, "height": 400,
                    "nodes": 2, "edges": 1, "crossings": crossings, "font_px": 14.0,
                    "effective_font_px": font, "sequence": {}, "gantt": {}, "measured": True,
                    "contrast": {"page": page, "measured": True, "texts": list(texts)}})
    metrics.update(extra)
    return metrics


def _low_text(scope):
    """A measured text at 1.1:1, whose colours the figure sets (`author`) or the theme draws."""
    return {"text": "Alpha service", "kind": "node", "fg": "#F0F0F0", "bg": "#FFFFFF",
            "ratio": 1.1, "scope": scope}


def _geom_for(answer, status=("rendered", "rendered"), crossings=0, font=14.0, version=None,
              sha=None, dark="rendered", contrast=None):
    """Synthetic `geometry.json` of an answer: every headline render of every Mermaid fence, in
    the layout of `render_corpus.py`. *dark*: status of the dark render, None for no entry.
    *contrast*: `{render key: [measured texts]}`."""
    geom = {}
    pair = list(NOTATION["renderers"]["check_pair"])
    darks = gf.dark_keys(_ev(), NOTATION)
    for n, f in enumerate(mm.extract_fences(answer, ("mermaid",)), 1):
        fig = mm.parse_figure(f)
        plan = [(tag, tag, status[i]) for i, tag in enumerate(pair)]
        if dark is not None:
            plan += [(key, light, dark) for key, light in darks.items()]
        ent = {}
        for key, tag, st in plan:
            pinned = NOTATION["renderers"]["installs"][tag]["mermaid"]
            metrics = _metrics(fig.kind, crossings, font, (contrast or {}).get(key, ()),
                               "#0d1117" if key in darks else "#ffffff")
            ent[key] = {"render": key, "renderer": {"tag": tag, "mermaid": version or pinned},
                        "dark": key in darks, "status": st, "ok": st == "rendered",
                        "metrics": metrics if st == "rendered" else {},
                        "fence_sha256": sha or mm.fence_sha256(f.body),
                        "log_head": "" if st == "rendered" else "Parse error on line 2"}
        geom[f"fig-{n}"] = ent
    return geom


def t_grader():
    ev = _ev()
    key = copy.deepcopy(UNIT_KEY)
    ck = fd.compile_key(key)
    res = gf.grade_answer("Nothing to draw here.", UNIT_CASE, key, ck, ev, NOTATION, {})
    owed = [c for c, s in res["q"].items() if s["status"] != "na"]
    check("TC-ME-19 an answer without a figure fails every check it owes",
          res["no_figure"] and owed and all(res["q"][c]["status"] == "fail" for c in owed),
          f"owed={owed}")
    cap = "**Figure 1.** Alpha service — writes to Beta store within 30 s.\n\n"
    body = 'flowchart TB\n  A("Alpha service") -->|"30 s"| B[("Beta store")]'
    answer = cap + _fence(body)
    good = gf.grade_answer(answer, UNIT_CASE, key, ck, ev, NOTATION, _geom_for(answer))
    grading = gf.build_grading(good, ev)
    texts = [e["text"] for e in grading["expectations"]]
    q_texts = [c["text"] for c in ev["checks"]]
    check("TC-ME-19 grading.json: Q texts verbatim and in order, K checks apart, no timing key",
          texts == [t for t in q_texts if t in texts] and set(texts) <= set(q_texts)
          and not set(e["text"] for e in grading["contract_checks"]) & set(q_texts)
          and "timing" not in grading and grading["summary"]["total"] == len(texts),
          f"{len(texts)} expectations, {len(grading['contract_checks'])} contract checks")
    q04 = gf.grade_answer(answer, UNIT_CASE, key, ck, ev, NOTATION,
                          _geom_for(answer, crossings=NOTATION["thresholds"]["max_crossings"] + 1))
    q02 = gf.grade_answer(answer, UNIT_CASE, key, ck, ev, NOTATION,
                          _geom_for(answer, status=("rendered", "parse_error")))
    q06 = gf.grade_answer(answer, UNIT_CASE, key, ck, ev, NOTATION,
                          _geom_for(answer, font=NOTATION["min_effective_font_px"] - 1))
    check("TC-ME-19 geometry: Q01-Q06 pass on a clean render; crossings, a parse error and small "
          "text fail Q04, Q02 and Q06",
          all(_q(good, c) == "pass" for c in ("Q01", "Q02", "Q03", "Q04", "Q05", "Q06"))
          and _q(q04, "Q04") == "fail" and _q(q02, "Q02") == "fail" and _q(q02, "Q01") == "pass"
          and _q(q06, "Q06") == "fail",
          f"good={[_q(good, c) for c in ('Q01', 'Q02', 'Q03', 'Q04', 'Q05', 'Q06')]} "
          f"Q04={_q(q04, 'Q04')} Q02={_q(q02, 'Q02')} Q06={_q(q06, 'Q06')}")
    through, stored = _geom_for(answer), _geom_for(answer)
    for tag in NOTATION["renderers"]["check_pair"]:
        through["fig-1"][tag]["metrics"]["edges_through_labels"] = [
            {"edge": "A->B", "label": "30 s", "inside_px": 12.0}]
        stored["fig-1"][tag]["metrics"]["label_overlaps"] = [
            {"a": "edge:A->B", "b": "label:30 s", "area_px": 12.0, "kind": "edge-label"}]
    q05 = gf.grade_answer(answer, UNIT_CASE, key, ck, ev, NOTATION, through)
    q05_stored = gf.grade_answer(answer, UNIT_CASE, key, ck, ev, NOTATION, stored)
    check("TC-ME-19 geometry: an edge through another edge's label fails Q05 (TASK R7.6), read "
          "from edges_through_labels and from a label_overlaps entry of kind edge-label that "
          "metrics stored before that check hold",
          _q(q05, "Q05") == "fail" and "inside the label" in q05["q"]["Q05"]["evidence"]
          and _q(q05_stored, "Q05") == "fail"
          and q05_stored["q"]["Q05"]["evidence"] == q05["q"]["Q05"]["evidence"]
          and all(_q(q05, c) == "pass" for c in ("Q03", "Q04", "Q06")),
          f"Q05={_q(q05, 'Q05')}: {q05['q']['Q05']['evidence'][:120]} | "
          f"stored={_q(q05_stored, 'Q05')}")
    dark_key = next(iter(gf.dark_keys(ev, NOTATION)))
    light_key, floor_key = NOTATION["renderers"]["check_pair"]
    c_dark = gf.grade_answer(answer, UNIT_CASE, key, ck, ev, NOTATION,
                             _geom_for(answer, contrast={dark_key: [_low_text("author")]}))
    c_v10 = gf.grade_answer(answer, UNIT_CASE, key, ck, ev, NOTATION,
                            _geom_for(answer, contrast={floor_key: [_low_text("author")]}))
    c_theme = gf.grade_answer(answer, UNIT_CASE, key, ck, ev, NOTATION, _geom_for(
        answer, contrast={k: [_low_text("theme")] for k in (light_key, floor_key, dark_key)}))
    check("TC-ME-19 Q06 contrast: an author-set text below the minimum fails Q06 in the dark "
          "11.17 render and in 10.9; text in the viewer's theme colours is information only",
          _q(c_dark, "Q06") == "fail" and dark_key in c_dark["q"]["Q06"]["evidence"]
          and _q(c_v10, "Q06") == "fail" and _q(c_theme, "Q06") == "pass"
          and all(_q(c_dark, c) == "pass" for c in ("Q03", "Q04", "Q05")),
          f"dark={c_dark['q']['Q06']['evidence'][:120]} | v10={_q(c_v10, 'Q06')} "
          f"theme={_q(c_theme, 'Q06')}")
    try:
        gf.grade_answer(answer, UNIT_CASE, key, ck, ev, NOTATION, _geom_for(answer, dark=None))
        no_dark = False
    except gf.RunExcluded:
        no_dark = True
    broken = gf.grade_answer(answer, UNIT_CASE, key, ck, ev, NOTATION,
                             _geom_for(answer, dark="render_error"))
    check("TC-ME-19 the dark render is a headline render: absent, it excludes the run; failed "
          "while the light one drew, it fails Q06",
          no_dark and _q(broken, "Q06") == "fail", f"absent={no_dark} failed={_q(broken, 'Q06')}")
    try:
        gf.grade_answer(answer, UNIT_CASE, key, ck, ev, NOTATION, _geom_for(answer, version="9.0.0"))
        wrong_version = False
    except gf.InstrumentError:
        wrong_version = True
    try:
        gf.grade_answer(answer, UNIT_CASE, key, ck, ev, NOTATION, _geom_for(answer, sha="0" * 64))
        stale = False
    except gf.RunExcluded:
        stale = True
    check("TC-ME-19 geometry from another renderer version breaks the instrument; stale geometry "
          "excludes the run", wrong_version and stale, f"version={wrong_version} stale={stale}")
    term_key = dict(copy.deepcopy(UNIT_KEY), medium="terminal")
    term_ck = fd.compile_key(term_key)
    term = gf.grade_answer(answer, UNIT_CASE, term_key, term_ck, ev, NOTATION, _geom_for(answer))
    check("TC-ME-19 medium: a Mermaid fence fails Q15 in a terminal even in an accepted form; in a "
          "document it passes Q15 when the key accepts its form",
          _q(term, "Q15") == "fail" and "terminal" in term["q"]["Q15"]["evidence"]
          and _q(good, "Q15") == "pass", f"{_q(term, 'Q15')} {_q(good, 'Q15')}")
    txt = cap + _fence("Alpha service\t-> Beta store", "text")
    tab = gf.grade_answer(txt, UNIT_CASE, key, ck, ev, NOTATION, {})
    clean = gf.grade_answer(cap + _fence("Alpha service -> Beta store", "text"), UNIT_CASE, key, ck,
                            ev, NOTATION, {})
    check("TC-ME-19 ASCII lint reads every text fence as a figure, with or without the `figure` "
          "marker the baseline cannot know: a tab fails Q16; a clean chain passes it",
          _q(tab, "Q16") == "fail" and _q(clean, "Q16") == "pass", f"{_q(tab, 'Q16')} {_q(clean, 'Q16')}")
    low = cap + _fence(body + "\n  classDef c fill:#FFFFFF,color:#BBBBBB\n  class A c")
    fill = cap + _fence('flowchart TB\n  A["Alpha service"]:::x --> B["Beta store"]:::y\n'
                        '  classDef x fill:#E8F0FB,color:#0F2A47\n  classDef y fill:#EEF7EE,color:#0F2A47')
    lo = gf.grade_answer(low, UNIT_CASE, key, ck, ev, NOTATION, _geom_for(low))
    fo = gf.grade_answer(fill, UNIT_CASE, key, ck, ev, NOTATION, _geom_for(fill))
    check("TC-ME-19 colour: low contrast fails Q17; two categories by fill alone without a legend fail Q17",
          _q(lo, "Q17") == "fail" and _q(fo, "Q17") == "fail" and _q(good, "Q17") == "na",
          f"{lo['q']['Q17']['evidence'][:90]} | {fo['q']['Q17']['evidence'][:90]}")
    by_fill = _fence('flowchart TB\n  A["Alpha service"]:::new --> B["Beta store"]:::old\n'
                     '  classDef new fill:#E8F0FB,color:#0F2A47\n'
                     '  classDef old fill:#EEF7EE,color:#0F2A47')
    comma = "**Figure 1.** Containers, who calls whom.\n\n"
    q17 = {name: _q(gf.grade_answer(text, UNIT_CASE, key, ck, ev, NOTATION, None), "Q17")
           for name, text in (
               ("caption with a comma", comma + by_fill),
               ("unrelated legend", comma + by_fill + "\nSolid arrow: a call, dashed arrow: a reply.\n"),
               ("one class named", comma + by_fill + "\nnew: added in 2026, and the rest.\n"),
               ("names below", comma + by_fill + "\nnew: added in 2026; old: kept from 2019.\n"),
               ("colours below", comma + by_fill + "\n#E8F0FB: added; #EEF7EE: kept.\n"),
               ("legend above", "New: added in 2026; old: kept from 2019.\n\n" + by_fill))}
    check("TC-ME-44 Q17 reads only the legend, below the fence or above it when that paragraph is "
          "no caption, and needs both colour-only classes named in it by class name or colour: "
          "a caption with a comma, a legend of other encodings and a legend naming one class "
          "fail (R2-07)",
          q17 == {"caption with a comma": "fail", "unrelated legend": "fail",
                  "one class named": "fail", "names below": "pass", "colours below": "pass",
                  "legend above": "pass"}, f"{q17}")
    below = _fence(body) + "\nAlpha service writes to Beta store within 30 s.\n"
    heading = "### Alpha and Beta\n\n" + _fence(body)
    two = (cap + _fence('flowchart TB\n  A["Alpha service"]:::x -.-> B[("Beta store")]:::y\n'
                        '  classDef x fill:#E8F0FB,color:#0F2A47\n  classDef y fill:#F3EEF9,color:#2A1653')
           + "\n- dashed arrow: asynchronous\n- rounded box: service\n- cylinder: store\n")
    bl = gf.grade_answer(below, UNIT_CASE, key, ck, ev, NOTATION, _geom_for(below))
    hd = gf.grade_answer(heading, UNIT_CASE, key, ck, ev, NOTATION, _geom_for(heading))
    tw = gf.grade_answer(two, UNIT_CASE, key, ck, ev, NOTATION, _geom_for(two))
    check("TC-ME-19 caption and legend by position: below counts, a heading does not, a list names "
          "the encodings", _q(bl, "Q13") == "pass" and _q(hd, "Q13") == "fail" and _q(tw, "Q14") == "pass"
          and _q(good, "Q14") == "na", f"{_q(bl, 'Q13')} {_q(hd, 'Q13')} {_q(tw, 'Q14')}")
    shapes = NOTATION.get("shapes", {}).get("flowchart", {})
    rect_db = cap + _fence('flowchart TB\n  A("Alpha service"):::wf --> B["Beta store"]:::db\n'
                           f'  classDef wf {NOTATION["palette"]["flowchart"]["wf"]}\n'
                           f'  classDef db {NOTATION["palette"]["flowchart"]["db"]}')
    k03_bad = gf.grade_answer(rect_db, UNIT_CASE, key, ck, ev, NOTATION, None)["k"]["K03"]
    c1 = _case(ev, "c1-wms-container-view")
    c7 = _case(ev, "c7-refund-decision")
    k03_c1 = k03_c7 = {"status": "absent"}
    if c1 is not None and c7 is not None:
        k1, ck1, _s = gf.load_key(ev, c1)
        k7, ck7, _s = gf.load_key(ev, c7)
        k03_c1 = gf.grade_answer(_read(c1["pass"]), c1, k1, ck1, ev, NOTATION, None)["k"]["K03"]
        k03_c7 = gf.grade_answer(_read(c7["pass"]), c7, k7, ck7, ev, NOTATION, None)["k"]["K03"]
    check("TC-ME-19 K03 reads the shapes table of notation.json: a db node drawn as a rectangle "
          "fails; c1 passes; the diamonds of the c7 decision flow pass in class wf",
          shapes.get("db") == "cylinder" and k03_bad["status"] == "fail"
          and k03_c1["status"] == "pass" and k03_c7["status"] == "pass",
          f"bad={k03_bad['status']} c1={k03_c1['status']} c7={k03_c7['status']}")
    src = Path(gf.__file__).read_text(encoding="utf-8") + Path(fd.__file__).read_text(encoding="utf-8") \
        + Path(stats.__file__).read_text(encoding="utf-8")
    keys = list(NOTATION["thresholds"]) + list(NOTATION["labels"]) + [
        "min_effective_font_px", "contrast_min", "column_px", "lr_max_nodes", "max_columns"]
    restated = [k for k in keys if re.search(r"(?m)^\s*" + re.escape(k.upper()) + r"\s*=", src)
                or re.search(r'"' + re.escape(k) + r'"\s*:\s*\d', src)]
    check("TC-ME-19 the grader holds the production modules and restates no threshold",
          gf.lint is lint and gf.geometry is sg and gf.mm is mm and not restated,
          f"restated={restated}")


def t_corpus():
    ev = _ev()
    case = _case(ev, "c8-frontends-services-k33")
    control = _case(ev, "c0-control-thumbnails")
    tmp = Path(tempfile.mkdtemp(prefix="mfe-corpus-"))
    try:
        camp = tmp / "campaign"
        att = []
        for c, which in ((case, {"with_skill": "pass", "without_skill": "fail"}),
                         (control, {"with_skill": "pass", "without_skill": "pass"})):
            ed = camp / f"eval-{c['id']}-{c['name']}"
            ed.mkdir(parents=True)
            (ed / "eval_metadata.json").write_text(json.dumps({"eval_id": c["id"], "prompt": "p"}),
                                                   encoding="utf-8")
            for arm, src in which.items():
                for rep in (1, 2, 3):
                    rd = ed / arm / f"run-{rep}"
                    (rd / "outputs").mkdir(parents=True)
                    text = _read(c[src])
                    (rd / "outputs" / "answer.md").write_text(text, encoding="utf-8")
                    meta = {"model": "claude-opus-5-5", "served_model_ok": True, "is_error": False,
                            "total_cost_usd": 0.25, "total_tokens": 1000, "duration_ms": 1000}
                    geom = _geom_for(text)
                    if c is case and arm == "without_skill" and rep == 2:
                        meta["is_error"] = True
                    if c is case and arm == "without_skill" and rep == 3:
                        geom = None
                    if c is control and arm == "with_skill" and rep == 3:
                        meta["served_model_ok"] = False
                    (rd / "run.meta.json").write_text(json.dumps(meta), encoding="utf-8")
                    (rd / "timing.json").write_text(json.dumps({"total_tokens": 1000,
                                                                "total_duration_seconds": 1.0}),
                                                    encoding="utf-8")
                    if geom is not None:
                        (rd / "outputs" / "geometry.json").write_text(json.dumps(geom), encoding="utf-8")
                    att.append({"arm": arm, "total_cost_usd": 0.25})
        (camp / "attempts.jsonl").write_text("".join(json.dumps(a) + "\n" for a in att), encoding="utf-8")
        # An unlabelled scaffold, not the committed labels: this synthetic campaign has no calibration.
        unlabelled = tmp / "labels.json"
        unlabelled.write_text(json.dumps({"schema": "mermaid-calibration/v1", "labeller": None,
                                          "corroborated": True, "items": []}), encoding="utf-8")
        runs, report = gf.grade_corpus(camp, ev, NOTATION, unlabelled)
        reasons = sorted(x["reason"].split(" ")[0] for x in report["excluded"])
        crit = {c["id"]: c["status"] for c in report["decision"]["criteria"]}
        dec = report["decision"]
        check("TC-ME-19 a campaign: excluded runs are named, both arms are measured, D8 is a table "
              "of eight criteria with V1 V2 V3 C1 first; an excluded run makes it invalid",
              len(report["excluded"]) == 3 and set(report["arms"]) >= {"with_skill", "without_skill"}
              and list(crit) == list(gf.VALIDITY + gf.EFFECT) and crit["V1"] == "not met"
              and dec["validity"] == "invalid" and dec["campaign_invalid"] is True
              and dec["claim_holds"] is False and dec["statement"].startswith("the campaign is invalid")
              and crit["V2"] == f"not evaluated ({gf.NE_LABELS})"
              and crit["H1"] == f"not evaluated ({gf.NE_ARM})",
              f"excluded={reasons} criteria={crit}")
        _r2, again = gf.grade_corpus(camp, ev, NOTATION, unlabelled)
        check("TC-ME-19 grading is a pure function: a second pass gives the same report",
              json.dumps(again, sort_keys=True) == json.dumps(report, sort_keys=True), "")
        out = tmp / "out"
        sink = io.StringIO()            # aggregate_benchmark names each excluded run on stdout
        with contextlib.redirect_stdout(sink):
            notes = gf.write_outputs(camp, out, runs, report, ev)
        try:
            import aggregate_benchmark as ab
            import verify_pin
            with contextlib.redirect_stdout(sink):
                bench = ab.generate_benchmark(out)
                holds, diffs = verify_pin.pin_holds(out, out / "benchmark.json")
            configs = sorted({r["configuration"] for r in bench["runs"]})
            check("TC-ME-19 the skill-creator benchmark reads the gradings, and its pin holds",
                  configs == ["with_skill", "without_skill"] and holds and not notes,
                  f"configs={configs} diffs={diffs[:3]} notes={notes}")
        except (ImportError, SyntaxError, TypeError) as exc:   # absent, or for a newer Python
            skip("TC-ME-19 the skill-creator benchmark reads the gradings, and its pin holds",
                 f"skill-creator did not import: {type(exc).__name__}: {exc}")
        empty = gf.calibration_v2(HERE / "calibration" / "labels.json", NOTATION,
                                  gf.DECISION_RULE["V2"], ev)
        labels = json.loads(_read("calibration/labels.json"))
        labelled = [it for it in labels.get("items") or []
                    if any(v is not None for v in (it.get("labels") or {}).values())]
        check("TC-ME-21 calibration labels: schema, corroborated, and V2 not evaluated (no "
              "calibration labels) while no item is labelled",
              labels.get("schema") == gf.CALIBRATION_SCHEMA and labels.get("corroborated") is True
              and isinstance(labels.get("items"), list)
              and labels.get("defect_types", list(gf.DEFECT_TYPES)) == list(gf.DEFECT_TYPES)
              and labels.get("information_types", list(gf.INFO_LABEL_TYPES)) == list(gf.INFO_LABEL_TYPES)
              and (empty["status"] == f"not evaluated ({gf.NE_LABELS})") == (not labelled),
              f"{empty.get('status')}: {empty.get('reason', '')}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# =========================================================================== calibration (D16)


def _defect_evidence(defect):
    """Synthetic detector evidence of one flowchart output that carries *defect* (or none)."""
    th = NOTATION["thresholds"]
    light = {"effective_font_px": 14.0}
    dark_texts = []
    if defect == "crossings_over_allowance":
        light["crossings"] = th["max_crossings"] + 1
    elif defect == "edge_through_node":
        light["edges_through_nodes"] = [{"edge": "a->b", "node": "c",
                                         "depth_px": th["through_node_min_depth_px"] + 5}]
    elif defect == "title_crossing":
        light["title_crossings"] = [{"edge": "a->b", "title": "Zone", "near_miss": False}]
    elif defect == "label_overlap_or_clip":
        light["label_overlaps"] = [{"a": "a->b", "b": "c->d", "area_px": 40.0}]
    elif defect == "illegible_at_column":
        light["effective_font_px"] = NOTATION["min_effective_font_px"] - 3
    elif defect == "dark_contrast":
        dark_texts = [_low_text("author")]
    pair = list(NOTATION["renderers"]["check_pair"])
    renders = {tag: {"status": "rendered", "metrics": _metrics("flowchart", **light)}
               for tag in pair}
    for key in gf.dark_keys(_ev(), NOTATION):
        renders[key] = {"status": "rendered",
                        "metrics": _metrics("flowchart", texts=dark_texts, page="#0d1117")}
    accepted = ["table"] if defect == "form_unfit" else ["flowchart"]
    return {"kind": "flowchart", "renders": renders, "units_forms": [["flowchart"]],
            "accepted": accepted, "medium": "document", "images": 0}


def _labels_file(path, items, labeller="selftest"):
    path.write_text(json.dumps({"schema": gf.CALIBRATION_SCHEMA, "labeller": labeller,
                                "corroborated": True, "seed": 0, "items": items}),
                    encoding="utf-8")
    return path


def t_calibration():
    ev = _ev()
    rule = gf.DECISION_RULE["V2"]
    tmp = Path(tempfile.mkdtemp(prefix="mfe-cal-"))
    try:
        items = []
        for i in range(35):
            defect = gf.DEFECT_TYPES[i % len(gf.DEFECT_TYPES)]
            items.append({"id": f"s{i}", "seeded": False, "evidence": _defect_evidence(defect),
                          "labels": {t: t == defect for t in gf.DEFECT_TYPES}})
        agree = gf.calibration_v2(_labels_file(tmp / "agree.json", items), NOTATION, rule, ev)
        flipped = copy.deepcopy(items)
        hits = [it for it in flipped if it["labels"]["crossings_over_allowance"]]
        for it in hits[:2]:
            it["labels"]["crossings_over_allowance"] = False
        miss = gf.calibration_v2(_labels_file(tmp / "flip.json", flipped), NOTATION, rule, ev)
        few = copy.deepcopy(items)
        for it in few[:6]:
            it["seeded"] = True
        seeded = gf.calibration_v2(_labels_file(tmp / "few.json", few), NOTATION, rule, ev)
        nobody = gf.calibration_v2(_labels_file(tmp / "nobody.json", items, None), NOTATION, rule, ev)
        per = agree.get("per_type") or {}
        check("TC-ME-21 V2 on a synthetic labelled set: per defect type precision, recall and "
              "Cohen's kappa of the detector against the labels; met when every type holds",
              agree["met"] is True and set(per) == set(gf.DEFECT_TYPES)
              and all(per[t]["precision"] == 1.0 and per[t]["recall"] == 1.0
                      and per[t]["kappa"] == 1.0 for t in per),
              f"{agree.get('status')} {[(t, per[t]['precision'], per[t]['recall'], per[t]['kappa']) for t in per][:3]}")
        pt = (miss.get("per_type") or {}).get("crossings_over_allowance", {})
        check("TC-ME-21 V2 is not met when labels and verdicts disagree, when fewer than 30 sampled "
              "items remain without the seeded ones, or when no labeller is named",
              miss["met"] is False and pt.get("precision") == 0.6 and pt.get("recall") == 1.0
              and seeded["met"] is False and seeded["sampled"] == 29 and seeded["seeded"] == 6
              and nobody["met"] is False,
              f"recall={pt.get('recall')} kappa={pt.get('kappa')} sampled={seeded.get('sampled')} "
              f"nobody={nobody.get('status')}")
        none_ = gf.calibration_v2(_labels_file(tmp / "none.json", []), NOTATION, rule, ev)
        try:
            (tmp / "bad.json").write_text(json.dumps({"schema": "other", "items": []}), encoding="utf-8")
            gf.calibration_v2(tmp / "bad.json", NOTATION, rule, ev)
            refused = False
        except gf.InstrumentError:
            refused = True
        check("TC-ME-21 V2 with no labelled item is not evaluated (no calibration labels); a file of "
              "another schema breaks the instrument",
              none_["met"] is None and none_["status"] == f"not evaluated ({gf.NE_LABELS})" and refused,
              f"{none_.get('status')} refused={refused}")
        items = []
        for i in range(35):
            defect = gf.DEFECT_TYPES[i % len(gf.DEFECT_TYPES)]
            found = {t: (t == "invented_element" and i % 2 == 0) for t in gf.INFO_LABEL_TYPES}
            labels = {t: t == defect for t in gf.DEFECT_TYPES}
            labels.update(found)
            items.append({"id": f"s{i}", "seeded": False, "labels": labels,
                          "evidence": dict(_defect_evidence(defect), fidelity=found)})
        for j in range(3):          # carry crossings by construction; the detector misses them
            items.append({"id": f"t{j}", "labels": {t: t == "crossings_over_allowance"
                                                    for t in gf.DEFECT_TYPES},
                          "evidence": dict(_defect_evidence(None), seeded=True,
                                           known=["crossings_over_allowance"])})
        mixed = gf.calibration_v2(_labels_file(tmp / "topup.json", items), NOTATION, rule, ev)
        cross = mixed["per_type"]["crossings_over_allowance"]
        check("TC-ME-21 V2 comes from the random sample alone: top-up items the detector misses "
              "leave precision and recall as the sample has them and are reported apart; the "
              "information types are scored apart and never decide V2 (EI-22, EI-11)",
              mixed["met"] is True and cross["recall"] == 1.0 and mixed["sampled"] == 35
              and mixed["seeded"] == 3
              and mixed["top_up"]["crossings_over_allowance"] == {"items": 3, "detector": 0,
                                                                  "labelled": 3, "unlabelled": 0}
              and mixed["information_only"]["invented_element"]["pairs"] == 35
              and mixed["information_only"]["invented_element"]["kappa"] == 1.0
              and "seven defect types" in mixed["scope"],
              f"met={mixed['met']} recall={cross['recall']} "
              f"top_up={mixed['top_up']['crossings_over_allowance']}")
        blank = copy.deepcopy(items) + [
            {"id": "t9", "labels": {t: None for t in gf.DEFECT_TYPES},
             "evidence": dict(_defect_evidence(None), seeded=True, known=["title_crossing"])},
            {"id": "s99", "seeded": False, "labels": {t: None for t in gf.DEFECT_TYPES},
             "evidence": _defect_evidence(None)}]
        un = gf.calibration_v2(_labels_file(tmp / "blank.json", blank), NOTATION, rule, ev)
        only = gf.calibration_v2(_labels_file(tmp / "only-blank.json", blank[-2:]), NOTATION,
                                 rule, ev)
        unl = un.get("unlabelled") or {}
        title = (un.get("top_up") or {}).get("title_crossing") or {}
        check("TC-ME-21 an item without a label is reported by count and id, never dropped in "
              "silence: a top-up item among them shows under its type's `unlabelled`, and a set "
              "with no labelled item still lists them (R2-03)",
              un.get("items") == 38 and un.get("items_total") == 40 and un["sampled"] == 35
              and unl.get("count") == 2 and unl.get("ids") == ["t9", "s99"]
              and unl.get("seeded") == 1 and unl.get("sampled") == 1
              and title.get("unlabelled") == 1 and title.get("items") == 0
              and only["met"] is None and (only.get("unlabelled") or {}).get("count") == 2,
              f"items={un.get('items')}/{un.get('items_total')} unlabelled={unl} "
              f"title_crossing={title} only-blank={only.get('unlabelled')}")
        pair, darks = list(NOTATION["renderers"]["check_pair"]), list(gf.dark_keys(ev, NOTATION))

        def overlap_or_clip(**light):
            evid = _defect_evidence(None)
            for tag in pair:
                evid["renders"][tag]["metrics"].update(light)
            return gf.detector_verdicts(evid, NOTATION, pair, darks)["label_overlap_or_clip"]

        through = overlap_or_clip(edges_through_labels=[
            {"edge": "a->b", "label": "30 s", "inside_px": 12.0}])
        stored = overlap_or_clip(label_overlaps=[
            {"a": "edge:a->b", "b": "label:30 s", "area_px": 12.0, "kind": "edge-label"}])
        texts = overlap_or_clip(label_overlaps=[
            {"a": "label:30 s", "b": "label:60 s", "area_px": 40.0, "kind": "label-label"}])
        check("TC-ME-21 an edge through another edge's label is no label_overlap_or_clip defect "
              "(D16; TASK R7.6 lists it apart), whether the metrics hold it as edges_through_labels "
              "or, stored before that check, as a label_overlaps entry of kind edge-label; two "
              "texts over each other still are one; a marker that names edges_through_labels "
              "carries no defect type",
              through is False and stored is False and texts is True
              and "edges_through_labels" not in gf.NAMED_TYPE
              and gf.NAMED_TYPE.get("label_overlaps") == "label_overlap_or_clip",
              f"through={through} stored={stored} texts={texts}")
        camp = _synthetic_campaign(tmp / "camp", ev)
        paired = tmp / "paired.json"
        negatives = {}
        for line in (10, 20, 30, 40):
            ev_neg = _defect_evidence("crossings_over_allowance")
            negatives[str(line)] = {"fence_end": line + 3, "kind": "flowchart-v2", "negative": True,
                                    "negative_names": ["crossings", "MA-FLOW-02"],
                                    "renders": {k: dict(v, status="ok")
                                                for k, v in ev_neg["renders"].items()}}
        negatives["50"] = {"fence_end": 53, "kind": "flowchart", "negative": False,
                           "renders": _defect_evidence(None)["renders"]}
        unnamed = _defect_evidence("crossings_over_allowance")
        negatives["60"] = {"fence_end": 63, "kind": "flowchart-v2", "negative": True,
                           "negative_names": ["MA-FLOW-02"],
                           "renders": {k: dict(v, status="ok")
                                       for k, v in unnamed["renders"].items()}}
        paired.write_text(json.dumps({"schema": "render-evidence-fixture/v1", "files": {
            "references/paired-examples.md": {"figures": negatives}}}), encoding="utf-8")
        sheet, evidence = gf.calibration_sample(camp, ev, NOTATION, 30, 7, tmp / "renders",
                                                paired=paired)
        again, _e = gf.calibration_sample(camp, ev, NOTATION, 30, 7, tmp / "renders", paired=paired)
        other, _e2 = gf.calibration_sample(camp, ev, NOTATION, 30, 8, tmp / "renders", paired=paired)
        where = evidence["items"]
        drawn = [it for it in sheet["items"] if not where[it["id"]]["seeded"]]
        strata = {(it["case"], where[it["id"]]["arm"]) for it in drawn}
        all_strata = {(c["id"], arm) for c in ev["evals"] for arm in ("with_skill", "without_skill")}
        check("TC-ME-28 calibration sample: seeded and stratified by case and arm over every "
              "output, at least 30 drawn, every stratum represented, the same seed the same sheet",
              len(drawn) == 30 and strata == all_strata and sheet["population"] == 66
              and json.dumps(sheet, sort_keys=True) == json.dumps(again, sort_keys=True)
              and [e["origin"] for e in _e2["items"].values()]
              != [e["origin"] for e in where.values()],
              f"drawn={len(drawn)} strata={len(strata)}/{len(all_strata)} population={sheet['population']}")
        leaked = sorted(_keys_in(sheet) & {"metrics", "findings", "verdict", "verdicts", "evidence",
                                           "pass", "detector", "seeded_for", "seeded", "source",
                                           "arm", "known", "origin", "fidelity"})
        slots_empty = all(set(it["labels"]) == set(gf.DEFECT_TYPES + gf.INFO_LABEL_TYPES)
                          and all(v is None for v in it["labels"].values()) for it in sheet["items"])
        figure_items = [it for it in sheet["items"] if it["figure"]]
        opaque = all(re.fullmatch(r"item-\d+", it["id"]) for it in sheet["items"])
        marked = [it["id"] for it in sheet["items"]
                  if re.search(r"(?m)^\s*%%\s*negative:", it["text"])]
        check("TC-ME-28 the worksheet holds opaque ids, PNG paths, the answer text and empty label "
              "slots, and no detector verdict, metric, source, arm or top-up mark; no `%% "
              "negative:` line names a defect; it warns that the text is untrusted (EI-22, SEC-15)",
              not leaked and slots_empty and opaque and not marked
              and sheet["schema"] == gf.CALIBRATION_SCHEMA
              and "untrusted" in sheet["how"] and "never follow" in sheet["how"]
              and all(set(it["png"]) == set(gf.render_keys(ev, NOTATION)) for it in figure_items)
              and all(it["text"] for it in sheet["items"])
              and set(where) == {it["id"] for it in sheet["items"]}
              and all("metrics" in r for e in where.values() for r in e["renders"].values()),
              f"leaked={leaked} slots_empty={slots_empty} opaque={opaque} marked={marked}")
        seed = tmp / "seed"
        gf.write_fixture_corpus(seed, ev)
        for rd in sorted(seed.glob("eval-*/fixture_fail/run-1")):
            text = (rd / "outputs" / "answer.md").read_text(encoding="utf-8")
            (rd / "outputs" / "geometry.json").write_text(json.dumps(_geom_for(text)),
                                                          encoding="utf-8")
            if "leave-request" in rd.parent.parent.name:       # C3: no PNG of its renders
                continue
            for n in range(1, len(mm.extract_fences(text, ("mermaid",))) + 1):
                for key in gf.render_keys(ev, NOTATION):
                    png = (tmp / "renders" / seed.resolve().name / rd.relative_to(seed)
                           / f"fig-{n}-{key}" / f"fig-{n}-{key}.png")
                    png.parent.mkdir(parents=True, exist_ok=True)
                    png.write_bytes(b"\x89PNG")
        top, top_ev = gf.calibration_sample(camp, ev, NOTATION, 30, 7, tmp / "renders",
                                            seed_corpus=seed, paired=paired)
        tw = top_ev["items"]
        seeds = [it for it in top["items"] if tw[it["id"]]["seeded"]]
        blind = [it["id"] for it in seeds
                 if set(tw[it["id"]]["known"]) & set(getattr(gf, "RENDER_TYPES", ()))
                 and not any(it["png"].get(k) for k in pair)]
        refused = {r["origin"]: r["types"] for r in top_ev.get("refused", [])}
        paired_refused = sorted(o for o in refused if "#L" in o)
        c3 = [o for o in refused if "leave-request" in o]
        check("TC-ME-28 each defect type is topped up with up to 3 items that carry it by "
              "construction, that its evidence lets the detector judge, and whose PNG the "
              "labeller sees: a paired example or a fixture with no PNG of its renders is "
              "refused for a render type and listed under `refused`; a negative that names no "
              "type is never picked (EI-22, R2-03)",
              seeds and not blind and all(tw[it["id"]]["known"] for it in seeds)
              and not any(tw[it["id"]]["source"].get("kind") == "paired" for it in seeds)
              and paired_refused == [f"seed:references/paired-examples.md#L{n}"
                                     for n in (10, 20, 30, 40)]
              and all(refused[o] == ["crossings_over_allowance"] for o in paired_refused)
              and c3 and all("crossings_over_allowance" in refused[o] for o in c3)
              and top_ev["top_up_types"]["crossings_over_allowance"] == sum(
                  1 for it in seeds if "crossings_over_allowance" in tw[it["id"]]["known"]) > 0,
              f"seeded={[tw[it['id']]['origin'] for it in seeds]} blind={blind} "
              f"refused={refused} types={top_ev['top_up_types']}")
        run = next(r for r in sorted((camp).glob("eval-*/with_skill/run-1")))
        rel = run.relative_to(camp).as_posix()
        png = tmp / "renders" / camp.resolve().name / rel / "fig-1-v11" / "fig-1-v11.png"
        png.parent.mkdir(parents=True)
        png.write_bytes(b"\x89PNG")
        paths = gf._png_paths(tmp / "renders", camp, rel, "fig-1", gf.render_keys(ev, NOTATION))
        try:
            gf.calibration_sample(camp, ev, NOTATION, 29, 7, tmp / "renders", paired=paired)
            small = False
        except ValueError:
            small = True
        check("TC-ME-28 PNG paths follow the render layout of render_corpus.py and are null where "
              "no PNG exists; a sample below 30 is refused",
              paths.get("v11") == gf.home_relative(png)
              and all(v is None for k, v in paths.items() if k != "v11")
              and small, f"{paths} small_refused={small}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _keys_in(node, out=None):
    out = set() if out is None else out
    if isinstance(node, dict):
        out.update(node)
        for v in node.values():
            _keys_in(v, out)
    elif isinstance(node, list):
        for v in node:
            _keys_in(v, out)
    return out


def _synthetic_campaign(camp, ev, which=None, dark="rendered"):
    """A campaign of every case, both arms and three repetitions: `with_skill` answers with
    pass.md, `without_skill` with fail.md; synthetic geometry of clean renders."""
    which = which or {"with_skill": "pass", "without_skill": "fail"}
    for c in ev["evals"]:
        ed = camp / f"eval-{c['id']}-{c['name']}"
        ed.mkdir(parents=True, exist_ok=True)
        (ed / "eval_metadata.json").write_text(json.dumps({"eval_id": c["id"], "prompt": "p"}),
                                               encoding="utf-8")
        for arm, src in which.items():
            for rep in (1, 2, 3):
                rd = ed / arm / f"run-{rep}"
                (rd / "outputs").mkdir(parents=True, exist_ok=True)
                text = _read(c[src])
                (rd / "outputs" / "answer.md").write_text(text, encoding="utf-8")
                (rd / "outputs" / "geometry.json").write_text(
                    json.dumps(_geom_for(text, dark=dark)), encoding="utf-8")
                (rd / "run.meta.json").write_text(json.dumps(
                    {"model": "claude-opus-5-5", "served_model_ok": True, "is_error": False,
                     "total_cost_usd": 0.25, "total_tokens": 1000, "duration_ms": 1000}),
                    encoding="utf-8")
                (rd / "timing.json").write_text(json.dumps(
                    {"total_tokens": 1000, "total_duration_seconds": 1.0}), encoding="utf-8")
    return camp


def t_cli():
    tmp = Path(tempfile.mkdtemp(prefix="mfe-cli-"))
    try:
        sink_o, sink_e = io.StringIO(), io.StringIO()
        (tmp / "empty").mkdir()
        ev = json.loads(_read("evals.json"))
        case = dict(ev["evals"][0], key="bad-key.json", document=str(HERE / ev["evals"][0]["document"]))
        (tmp / "evals.json").write_text(json.dumps(dict(ev, evals=[case])), encoding="utf-8")
        (tmp / "bad-key.json").write_text(json.dumps(
            {"entities": [{"id": "a", "aliases": ["A"]}], "relations": [{"from": "a", "to": "zz"}]}),
            encoding="utf-8")
        rd = tmp / "camp" / f"eval-{case['id']}-x" / "with_skill" / "run-1" / "outputs"
        rd.mkdir(parents=True)
        (rd / "answer.md").write_text("No figure.\n", encoding="utf-8")
        with contextlib.redirect_stdout(sink_o), contextlib.redirect_stderr(sink_e):
            codes = (gf.main([]), gf.main(["--corpus", str(tmp / "absent")]),
                     gf.main(["--corpus", str(tmp / "empty")]),
                     gf.main(["--corpus", str(tmp / "camp"), "--evals", str(tmp / "evals.json"),
                              "--out", str(tmp / "out")]))
        check("TC-ME-19 grader CLI: a usage error exits 3, a malformed key exits 2",
              codes == (3, 3, 3, 2), f"exit codes {codes}")
        full = _synthetic_campaign(tmp / "full", _ev())
        sheet_dir = tmp / "sheet"
        with contextlib.redirect_stdout(sink_o), contextlib.redirect_stderr(sink_e):
            cal = (gf.main(["--calibration-sample", "10", "--seed", "1", "--corpus", str(full),
                            "--out", str(sheet_dir)]),
                   gf.main(["--calibration-sample", "30", "--corpus", str(full),
                            "--out", str(sheet_dir)]),
                   gf.main(["--calibration-sample", "30", "--seed", "1", "--corpus", str(full),
                            "--out", str(sheet_dir), "--render-dir", str(tmp / "renders")]),
                   gf.main(["--fixture-corpus", str(tmp / "fixture-corpus")]))
        written = sorted(p.name for p in sheet_dir.glob("*.json")) if sheet_dir.is_dir() else []
        runs = list((tmp / "fixture-corpus").glob("eval-*/fixture_fail/run-1/outputs/answer.md"))
        check("TC-ME-28 calibration CLI: a sample below 30 or without a seed exits 3; a sample "
              "writes worksheet.json and evidence.json; --fixture-corpus lays out every fail.md",
              cal == (3, 3, 0, 0) and written == ["evidence.json", "worksheet.json"]
              and len(runs) == len(CASES),
              f"exit codes {cal} written={written} fixture runs={len(runs)}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# =========================================================================== forms (R11.2)

C8_TABLE = ("**Table 1.** Front-ends and domain services — which front-end calls which domain "
            "service.\n\n"
            "| Front-end | Catalog service | Pricing service | Stock service |\n"
            "| :--- | :---: | :---: | :---: |\n"
            "| Web shop | yes | yes | yes |\n"
            "| Mobile BFF | yes | yes | yes |\n"
            "| Partner API | yes | yes | yes |\n")
F1_LIST = ("**Figure 1.** Pipeline stages in run order.\n\n1. lint\n2. unit tests\n3. build site\n"
           "4. link check and accessibility check, in parallel\n5. deploy preview\n6. publish\n")
C1_SEQUENCE = ("**Figure 1.** Handheld calls.\n\n" + _fence(
    "sequenceDiagram\n  participant H as Handheld app\n  participant G as API gateway\n"
    "  H->>G: HTTPS"))


def _grade(ev, slug, text, geom=None):
    case = _case(ev, slug)
    key, ck, _s = gf.load_key(ev, case)
    return gf.grade_answer(text, case, key, ck, ev, NOTATION, geom)


def t_forms():
    ev = _ev()
    names = ("TC-ME-30 acceptable forms: C8 accepts a table for its flowchart request (Q08 and "
             "Q15 pass); a sequence diagram for the C1 flowchart request fails Q08 and Q15",
             "TC-ME-30 F1 accepts an ASCII figure and a list (Q15 passes); a Mermaid fence in the "
             "terminal fails Q15",
             "TC-ME-30 F2 accepts a table; a flowchart fails Q15 only, since a request that names "
             "no kind leaves the form to Q15",
             "TC-ME-30 without acceptable_forms the key's kind decides, then the case figure_kind",
             "TC-ME-30 F1 in a terminal: K04 passes the plain label `Figure 1.` and fails a bold "
             "one, which that medium prints as typed (ascii.md §7)")
    if any(_case(ev, s) is None for s in ("c1-wms-container-view", "c8-frontends-services-k33",
                                          "f1-ci-stages-terminal", "f2-roles-operations-matrix")):
        for n in names:
            check(n, False, "a case is absent from evals.json")
        return
    c8 = _grade(ev, "c8-frontends-services-k33", C8_TABLE)
    c1 = _grade(ev, "c1-wms-container-view", C1_SEQUENCE, _geom_for(C1_SEQUENCE))
    check(names[0], _q(c8, "Q08") == "pass" and _q(c8, "Q15") == "pass"
          and _q(c1, "Q08") == "fail" and _q(c1, "Q15") == "fail",
          f"c8 Q08={_q(c8, 'Q08')} Q15={_q(c8, 'Q15')} | c1 Q08={c1['q']['Q08']['evidence'][:90]} "
          f"Q15={_q(c1, 'Q15')}")
    f1 = _case(ev, "f1-ci-stages-terminal")
    ascii_ = _grade(ev, "f1-ci-stages-terminal", _read(f1["pass"]))
    listed = _grade(ev, "f1-ci-stages-terminal", F1_LIST)
    merm = _grade(ev, "f1-ci-stages-terminal", _read(f1["fail"]))
    check(names[1], _q(ascii_, "Q15") == "pass" and _q(listed, "Q15") == "pass"
          and _q(merm, "Q15") == "fail" and _q(listed, "Q08") == "pass",
          f"ascii={_q(ascii_, 'Q15')} list={_q(listed, 'Q15')} mermaid={_q(merm, 'Q15')}")
    f2 = _case(ev, "f2-roles-operations-matrix")
    table = _grade(ev, "f2-roles-operations-matrix", _read(f2["pass"]))
    flow = _grade(ev, "f2-roles-operations-matrix", _read(f2["fail"]))
    check(names[2], _q(table, "Q15") == "pass" and _q(flow, "Q15") == "fail"
          and _q(flow, "Q08") == "pass",
          f"table={_q(table, 'Q15')} flowchart Q15={_q(flow, 'Q15')} Q08={_q(flow, 'Q08')}")
    state_case = {"figure_kind": "state"}
    check(names[3], gf.acceptable_forms({}, state_case) == ("state",)
          and gf.acceptable_forms({"kind": "gantt"}, state_case) == ("gantt",)
          and gf.acceptable_forms({"kind": "flowchart", "acceptable_forms": ["flowchart", "table"]},
                                  state_case) == ("flowchart", "table"),
          f"{gf.acceptable_forms({}, state_case)} {gf.acceptable_forms({'kind': 'gantt'}, state_case)}")
    plain_text = _read(f1["pass"])
    bold_text = re.sub(r"^Figure 1\.", "**Figure 1.**", plain_text, count=1, flags=re.M)
    plain, bold = (_grade(ev, "f1-ci-stages-terminal", x) for x in (plain_text, bold_text))
    check(names[4], bold_text != plain_text and plain["k"]["K04"]["status"] == "pass"
          and bold["k"]["K04"]["status"] == "fail",
          f"plain={plain['k']['K04']['status']} bold={bold['k']['K04']['status']}")


# =========================================================================== fidelity fixes


def t_fixes():
    ev = _ev()
    c0, c6 = _case(ev, "c0-control-thumbnails"), _case(ev, "c6-clinic-deployment")
    if c0 is None or c6 is None:
        for n in ("TC-ME-31a", "TC-ME-31b", "TC-ME-31c"):
            check(f"{n} fidelity fix", False, "a case is absent from evals.json")
        return
    k0, ck0, _s = gf.load_key(ev, c0)
    fail0 = gf.grade_answer(_read(c0["fail"]), c0, k0, ck0, ev, NOTATION, None)
    pass6 = _grade(ev, "c6-clinic-deployment", _read(c6["pass"]))
    undirected = [r.id for r in ck0.relations if not r.directed]
    directed = [r.id for r in ck0.relations if r.directed]
    reverse = _fence("flowchart TB\n" + "\n".join(
        f'  {r.dst.upper()}["{ck0.entities[r.dst]["names"][0]}"] --> '
        f'{r.src.upper()}["{ck0.entities[r.src]["names"][0]}"]' for r in ck0.relations))
    rev = fd.match(ck0, [u.facts for u in gf.read_answer(reverse, c0, ck0, k0).units])
    check("TC-ME-31a Q10: a relation with directed false is covered by an edge either way (the c0 "
          "fail.md and c6 pass.md); a directed relation is not covered by the reverse edge, even "
          "when an undirected relation of the same pair is drawn",
          _q(fail0, "Q10") == "pass" and _q(pass6, "Q10") == "pass" and bool(undirected)
          and set(undirected) <= set(rev["covered"])
          and set(directed) <= set(rev["missing_required"]),
          f"c0 fail Q10={_q(fail0, 'Q10')} c6 pass Q10={_q(pass6, 'Q10')} "
          f"covered={rev['covered']} missing={rev['missing_required']}")
    f2 = _case(ev, "f2-roles-operations-matrix")
    k2, ck2, _s = gf.load_key(ev, f2)
    flow = _read(f2["fail"]).rstrip("\n") + "\n"
    legend = "\n1. Arrow: the role may perform the operation\n2. Box: a role or an operation\n"
    below = gf.read_answer(flow + legend, f2, ck2, k2)
    apart = gf.read_answer(flow + "\n### Notes\n" + legend, f2, ck2, k2)
    q12_below = gf.grade_answer(flow + legend, f2, k2, ck2, ev, NOTATION, None)["q"]["Q12"]
    q12_alone = gf.grade_answer(flow, f2, k2, ck2, ev, NOTATION, None)["q"]["Q12"]
    check("TC-ME-31b a list directly below a Mermaid fence is its legend, not a list figure; "
          "after a heading it is a figure again",
          [u.form for u in below.units] == ["mermaid"] and below.legend_lists == 1
          and [u.form for u in apart.units] == ["mermaid", "list"]
          and q12_below["status"] == q12_alone["status"],
          f"below={[u.form for u in below.units]} apart={[u.form for u in apart.units]} "
          f"Q12 {q12_below['status']} vs {q12_alone['status']}")
    k6, ck6, _s = gf.load_key(ev, c6)
    c2 = _case(ev, "c2-card-3ds-sequence")
    _k2, ck2s, _s = gf.load_key(ev, c2)
    spaced = fd._numbers_of("PostgreSQL  15", ck6)
    tabbed = fd._numbers_of("see Table\t4.3", ck2s)
    split = fd.map_text(["СУБД основная", "PostgreSQL", "15"], ck6, "node", "DB1", 1).numbers
    kept = [(n.value, n.unit) for n in fd._numbers_of("PostgreSQL 150 · 5 s", ck6)]
    check("TC-ME-31c Q11 honours name_numbers across white space and across the lines of a "
          "label; a number that only starts like one stays a number",
          "PostgreSQL 15" in ck6.name_numbers and "Table 4.3" in ck2s.name_numbers
          and not spaced and not tabbed and not split and kept == [(150.0, ""), (5.0, "s")],
          f"spaced={spaced} tabbed={tabbed} split={split} kept={kept}")


# =========================================================================== review round 1


#: The three F1 baseline answers of campaign 2026-10-opus55-xhigh-r1, rebuilt as synthetic
#: answers: ASCII written outside a fence, indented four spaces, two spaces, and as `->` lines.
F1_INDENTED = ("The pipeline is mostly a straight chain, with one point where it splits:\n\n"
               "    push to merge request\n      |\n      v\n    lint\n      |\n      v\n"
               "    unit tests\n      |\n      v\n    build site\n      |\n"
               "      +------------------+\n      |                  |\n"
               "      v                  v\n"
               "    link check     accessibility check     (run in parallel)\n"
               "      |                  |\n      +------------------+\n      |\n      v\n"
               "    deploy preview                         (needs BOTH checks passed)\n"
               "      |\n      v\n"
               "    publish  <-- also needs a maintainer approval comment in the MR\n\n"
               "How the hand-offs work:\n\n- Every push starts a new run at lint.\n")
F1_PIPES = ("Each push to a merge request starts a new run:\n\n"
            "  push\n   |\n  lint\n   |\n  unit tests\n   |\n  build site\n   |\n"
            "   +----------------+\n   |                |\n"
            "  link check    accessibility check     (run in parallel)\n"
            "   |                |\n   +----------------+\n   |\n"
            "  deploy preview    (needs both checks to pass)\n   |\n"
            "  publish           (also needs a maintainer approval comment on the MR)\n")
F1_ARROWS = ("The stages form a single chain that splits after the build:\n\n"
             "  push\n   -> lint\n   -> unit tests\n   -> build site\n"
             "       -> link check            \\  run in parallel,\n"
             "       -> accessibility check   /  both must pass\n"
             "   -> deploy preview\n"
             "   -> publish  (also needs a maintainer approval comment in the MR)\n\n"
             "How a run moves through it:\n\n"
             "1. Every push to a merge request starts a new run at lint.\n\n"
             "2. When build site passes, link check and accessibility check start at once.\n\n"
             "3. If any stage fails, the run stops.\n")


def _fid_q(res):
    return {c: res["q"][c]["status"] for c in ("Q09", "Q10", "Q11", "Q12")}


def t_unfenced():
    """EI-01: ASCII figures outside fences."""
    ev = _ev()
    f1 = _case(ev, "f1-ci-stages-terminal")
    k1, ck1, _s = gf.load_key(ev, f1)
    shapes = {}
    for name, text in (("indented", F1_INDENTED), ("pipes", F1_PIPES), ("arrows", F1_ARROWS)):
        res = gf.grade_answer(text, f1, k1, ck1, ev, NOTATION, None)
        shapes[name] = ([(u.form, u.unfenced) for u in res["units"]], _fid_q(res),
                        res["q"]["Q15"]["status"], res["no_figure"])
    ok = all(units == [("text", True)] and set(fq.values()) == {"pass"} and q15 == "pass"
             and not nofig for units, fq, q15, nofig in shapes.values())
    check("TC-ME-36 F1 in a terminal: ASCII written outside a fence (indented 4 or 2 spaces, or "
          "as `->` lines) is one ASCII figure that matches the key; the explanatory list below "
          "it is no figure (EI-01)", ok, f"{shapes}")
    c1 = _case(ev, "c1-wms-container-view")
    kc1, ckc1, _s = gf.load_key(ev, c1)
    code = ("Calls:\n\n    Handheld app -> API gateway -> Picking service\n"
            "    Supervisor console -> API gateway\n")
    para = "Calls:\n\nHandheld app\n  |\n  v\nAPI gateway\n  |\n  v\nPicking service\n"
    in_doc = gf.read_answer(code, c1, ckc1, kc1)
    prose = gf.read_answer(para, c1, ckc1, kc1)
    term = gf.read_answer(para, f1, ck1, k1)
    check("TC-ME-36 an indented code block of links is an ASCII figure in any medium; a run of "
          "unindented link lines is one only in a terminal, where it prints as typed (EI-01)",
          [(u.form, u.unfenced) for u in in_doc.units] == [("text", True)]
          and not any(u.unfenced for u in prose.units)
          and [(u.form, u.unfenced) for u in term.units] == [("text", True)],
          f"document code={[(u.form, u.unfenced) for u in in_doc.units]} "
          f"document lines={[(u.form, u.unfenced) for u in prose.units]} "
          f"terminal lines={[(u.form, u.unfenced) for u in term.units]}")
    base = _read(c1["pass"]).rstrip("\n") + "\n"
    extra = {"an indented legend": "\nLegend:\n\n    solid arrow -> synchronous call\n"
                                   "    dashed arrow -> event on the bus\n",
             "indented code": "\nExample client code:\n\n    $client->call('pick');\n"
                              "    $client->close();\n"}
    plain = gf.grade_answer(base, c1, kc1, ckc1, ev, NOTATION, None)
    seen = {}
    for name, tail in extra.items():
        res = gf.grade_answer(base + tail, c1, kc1, ckc1, ev, NOTATION, None)
        seen[name] = ([u.form for u in res["units"]],
                      {c: _q(res, c) for c in ("Q08", "Q12", "Q15")})
    drawing = gf.read_answer("Calls:\n\n    Handheld app\n      |\n      v\n    API gateway\n",
                             c1, ckc1, kc1)
    f1_code = gf.read_answer(_read(f1["pass"]) + extra["indented code"], f1, ck1, k1)
    want = ([u.form for u in plain["units"]], {c: _q(plain, c) for c in ("Q08", "Q12", "Q15")})
    check("TC-ME-36 in a document an indented block must draw to be a figure: an indented legend "
          "with one arrow per line and indented code (`$client->call`) add no figure, so C1 "
          "pass.md keeps Q08, Q12 and Q15; an indented drawing with `|` and `v` lines is one. "
          "An arrow glued to words is code in a terminal too (R4)",
          all(v == want for v in seen.values()) and set(want[1].values()) == {"pass"}
          and [(u.form, u.unfenced) for u in drawing.units] == [("text", True)]
          and not any(u.unfenced for u in f1_code.units),
          f"pass.md={want} with tails={seen} drawing={[u.form for u in drawing.units]} "
          f"F1 with code={[(u.form, u.unfenced) for u in f1_code.units]}")


def t_ascii_labels():
    """EI-03: text on an ASCII link labels the link."""
    ev = _ev()
    a_key = {"entities": [{"id": "sensor", "aliases": ["sensor"]},
                          {"id": "gateway", "aliases": ["gateway"]},
                          {"id": "broker", "aliases": ["broker"]},
                          {"id": "decoder", "aliases": ["decoder"]},
                          {"id": "tss", "aliases": ["time-series store"]}],
             "relations": [{"id": "r1", "from": "sensor", "to": "gateway"},
                           {"id": "r2", "from": "gateway", "to": "broker"},
                           {"id": "r3", "from": "broker", "to": "decoder"},
                           {"id": "r4", "from": "decoder", "to": "tss"}]}
    ack = fd.compile_key(a_key)
    figs = {"Figure 1": "sensor ──MQTT──▶ gateway ──AMQP──▶ broker ──▶ decoder ──▶ "
                        "time-series store",
            "Figure 1 in pure ASCII": "sensor --MQTT--> gateway --AMQP--> broker --> decoder "
                                      "--> time-series store",
            "Figure 2": "sensor\n  │ MQTT\n  ▼\ngateway\n  │ AMQP\n  ▼\nbroker\n  │\n  ▼\n"
                        "decoder\n  │\n  ▼\ntime-series store"}
    seen = {}
    for name, body in figs.items():
        f = fd.facts_from_ascii(body, ack, 1)
        res = fd.match(ack, [f], {"text"})
        seen[name] = (all(v["passed"] for v in res["verdicts"].values()),
                      sorted({c.label for c in f.claims if c.label}))
    check("TC-ME-18 ASCII: a label on a link (`──MQTT──▶`, `│ MQTT`) labels the link and is no "
          "node: ascii.md Figures 1 and 2 match their key (EI-03)",
          all(ok_ and labs == ["AMQP", "MQTT"] for ok_, labs in seen.values()), f"{seen}")
    c0 = _case(ev, "c0-control-thumbnails")
    k0, ck0, _s = gf.load_key(ev, c0)
    above = ("**Figure 1.** Media bucket relations.\n\n```text figure\n"
             "+-------------------+   writes originals         +--------------+\n"
             "| Upload API        |--------------------------->|              |\n"
             "+-------------------+                            |              |\n"
             "                        reads originals          |              |\n"
             "+-------------------+   writes thumbnails        |              |\n"
             "| Thumbnail service |--------------------------->| Media bucket |\n"
             "+-------------------+                            |              |\n"
             "+-------------------+   reads thumbnails         |              |\n"
             "| CDN               |--------------------------->|              |\n"
             "+-------------------+                            +--------------+\n```\n")
    beside = ("**Figure 1.** Media bucket access.\n\n```text figure\n"
              "+------------+    +-------------------+        +-----+\n"
              "| Upload API |    | Thumbnail service |        | CDN |\n"
              "+-----+------+    +---------+---------+        +--+--+\n"
              "      | writes originals    | reads originals     | reads thumbnails\n"
              "      |                     | writes thumbnails   |\n"
              "      v                     v                     v\n"
              "+----------------------------------------------------+\n"
              "|                    Media bucket                    |\n"
              "+----------------------------------------------------+\n```\n")
    boxes = {}
    for name, text in (("above the arrows", above), ("beside the lines", beside)):
        res = gf.grade_answer(text, c0, k0, ck0, ev, NOTATION, None)
        boxes[name] = _fid_q(res)
    check("TC-ME-18 ASCII boxes: labels above a link, stacked, or beside a vertical link are no "
          "stage; the C0 relations are covered (EI-03)",
          all(set(v.values()) == {"pass"} for v in boxes.values()), f"{boxes}")
    compact = ("push to a merge request\n          |\n          v\n        lint\n          |\n"
               "          v\n     unit tests\n          |\n          v\n     build site\n"
               "+---------+---------+\n|                   |\nv                   v\n"
               "link check     accessibility check\n|                   |\n"
               "+---------+---------+\n   deploy preview\n          |\n          v\n       publish")
    f1 = _case(ev, "f1-ci-stages-terminal")
    k1, ck1, _s = gf.load_key(ev, f1)
    g = fd.parse_ascii(compact)
    res = fd.match(ck1, [fd.facts_from_ascii(compact, ck1, 1)], {"text"})
    stages = [n[0] for n in g["nodes"]]
    fork = {"o_build_site__link_check", "o_build_site__accessibility_check",
            "o_unit_tests__build_site", "o_deploy_preview__publish"}
    check("TC-ME-18 ASCII: a stage drawn on the line of a fork or a join, over its junction, is a "
          "stage and no label of the line: build site and deploy preview stay nodes, and the "
          "fork from build site is covered (R5)",
          "build site" in stages and "deploy preview" in stages and not g["free_labels"]
          and not g["labels"] and not fork & set(res["missing_required"]),
          f"nodes={stages} free={g['free_labels']} missing={res['missing_required']}")
    # ---------------------------------------------------------------- R5 follow-up (wave 1c)
    head = ("push to a merge request\n          |\n          v\n        lint\n          |\n"
            "          v\n     unit tests\n          |\n          v\n")
    tee = head + ("                  on success\n"
                  "     build site ----------+---------> link check\n"
                  "                          |\n                          v\n"
                  "                 accessibility check")
    g = fd.parse_ascii(tee)
    names = {n[2]: n[0] for n in g["nodes"]}
    on_tee = {(names[a], names[b]): v for (a, b), v in g["labels"].items()}
    res = gf.grade_answer("The stages:\n\n```text figure\n" + tee + "\n```\n", f1, k1, ck1, ev,
                          NOTATION, None)
    mq = fd.parse_ascii("   MQTT\nA ----+----> B\n      |\n      v\n      C")
    mq_names = {n[2]: n[0] for n in mq["nodes"]}
    on_mq = {(mq_names[a], mq_names[b]): v for (a, b), v in mq["labels"].items()}
    bx = fd.parse_ascii("       label\n  A ----+----> B\n  +-----+-----+\n  |     C     |\n"
                        "  +-----------+")
    bx_names = {n[2]: n[0] for n in bx["nodes"]}
    on_bx = {(bx_names[a], bx_names[b]): v for (a, b), v in bx["labels"].items()}
    check("TC-ME-18 ASCII: a `+` that a vertical link continues on the far side is a T that opens "
          "away from the text over it, so that text labels the link: 'on success' over "
          "`build site ---+---> link check` labels both edges from build site, Q09 and Q12 pass; "
          "'MQTT' over `A ---+---> B` labels A -> B and A -> C; a box border below the `+` "
          "continues it as well (R5 follow-up)",
          "on success" not in names.values()
          and on_tee.get(("build site", "link check")) == ["on success"]
          and on_tee.get(("build site", "accessibility check")) == ["on success"]
          and _q(res, "Q09") == "pass" and _q(res, "Q12") == "pass"
          and sorted(mq_names.values()) == ["A", "B", "C"]
          and on_mq.get(("A", "B")) == ["MQTT"] and on_mq.get(("A", "C")) == ["MQTT"]
          and sorted(bx_names.values()) == ["A", "B", "C"] and on_bx.get(("A", "B")) == ["label"],
          f"nodes={sorted(names.values())} labels={on_tee} Q09={_q(res, 'Q09')} "
          f"Q12={_q(res, 'Q12')} MQTT nodes={sorted(mq_names.values())} labels={on_mq} "
          f"box nodes={sorted(bx_names.values())} labels={on_bx}")
    chains = {
        "a stage on a 3-way fork line, an arrow into it":
            ("  unit tests\n      |\n      v\n build site\n+-----+-----+\n|     |     |\n"
             "v     v     v\na     b     c", "build site",
             {("unit tests", "build site"), ("build site", "a"), ("build site", "b"),
              ("build site", "c")}),
        "a stage under a 3-way join line, a link out of it":
            ("a     b     c\n|     |     |\n+-----+-----+\n deploy now\n      |\n      v\n"
             "   publish", "deploy now", {("deploy now", "publish")}),
        "a stage over a plain link, an arrow into it":
            ("     unit tests\n          |\n          v\n      build site\n"
             "   ----------------> link check", "build site",
             {("unit tests", "build site"), ("build site", "link check")})}
    seen = {}
    for name, (body, stage, want_edges) in chains.items():
        g = fd.parse_ascii(body)
        names = {n[2]: n[0] for n in g["nodes"]}
        got_edges = {(names[a], names[b]) for a, b in g["edges"]}
        seen[name] = (stage in names.values() and want_edges <= got_edges
                      and not g["free_labels"] and not g["labels"],
                      sorted(names.values()), sorted(got_edges), g["free_labels"])
    check("TC-ME-18 ASCII: text over or under a horizontal link that a vertical link meets on its "
          "other side is a stage of a chain, never a label: a stage on a 3-way fork line whose "
          "middle `+` goes on down, a stage under a 3-way join, a stage over a plain link "
          "(R5 follow-up)", all(v[0] for v in seen.values()), f"{seen}")


def t_duplicates():
    """EI-04: a label that extends a stated name is an invented element."""
    ev = _ev()
    c1 = _case(ev, "c1-wms-container-view")
    kc1, ckc1, _s = gf.load_key(ev, c1)
    base = _read(c1["pass"])

    def variant(nodes, edges, swap=None):
        t = base
        for a, b in swap or ():
            t = t.replace(a, b)
        t = t.replace('  IDB[("Inventory DB")]\n', '  IDB[("Inventory DB")]\n' + nodes)
        return t.replace('  INV -->|"owns"| IDB\n', '  INV -->|"owns"| IDB\n' + edges)

    inventions = {
        "Slotting DB": variant('  SDB[("Slotting DB")]\n', '  SLOT -->|"owns"| SDB\n'),
        "Inventory cache": variant('  CACHE[("Inventory cache<br/>Redis")]\n', '  INV --> CACHE\n'),
        "Picking DB replica": variant('  PREP[("Picking DB replica")]\n',
                                      '  PDB -->|"streams"| PREP\n'),
        "API gateway WAF": variant('  WAF["API gateway WAF"]\n', '',
                                   [('  HH -->|"HTTPS"| GW\n  SC -->|"HTTPS"| GW\n',
                                     '  HH -->|"HTTPS"| WAF\n  SC -->|"HTTPS"| WAF\n  WAF --> GW\n')])}
    caught = {name: _q(gf.grade_answer(t, c1, kc1, ckc1, ev, NOTATION, None), "Q12")
              for name, t in inventions.items()}
    c7 = _case(ev, "c7-refund-decision")
    k7, ck7, _s = gf.load_key(ev, c7)
    repeated = _fence('flowchart TB\n  REQ["Refund request"] --> DEF{"Reported as defective?"}\n'
                      '  DEF -->|yes| AG["Support agent"]\n  AG --> AQ{"Agent approves?"}\n'
                      '  AQ -->|yes| OK1["Approved"]\n  AQ -->|no| NO1["Declined"]\n'
                      '  AG --> NO2["Declined"]')
    rep = gf.grade_answer(repeated, c7, k7, ck7, ev, NOTATION, None)
    dupes = [i for i in rep["fidelity"]["invented"] if "a second time" in i]
    check("TC-ME-18 an element whose label extends a stated name is invented beside the stated "
          "one (Slotting DB, Inventory cache, Picking DB replica, API gateway WAF fail Q12); the "
          "same outcome drawn twice and a check about an actor are no invention (EI-04)",
          set(caught.values()) == {"fail"} and _q(gf.grade_answer(base, c1, kc1, ckc1, ev,
                                                                   NOTATION, None), "Q12") == "pass"
          and not dupes, f"{caught} repeated={dupes}")


def t_captions():
    """EI-05, EI-06: caption labels and the first sentence."""
    ev = _ev()
    ck = fd.compile_key(UNIT_KEY)
    labels = ("Figure 6.1 shows the Alpha service.", "Рис. 6.1 — Alpha service.",
              "*Figure 3: Alpha service.*", "_Figure 3. Alpha service._",
              "**Figure 2.4.1** Alpha service.", "Figure 1. Alpha service (ci/PIPELINE.md:6-14).")
    claims = {t: fd.caption_claims(t, ck, {"a"}, [])["ok"] for t in labels}
    real = fd.caption_claims("Figure 3. Alpha service retries 7 times.", ck, {"a"}, [])
    check("TC-ME-18 caption: a plain dotted, Cyrillic, italic or underscored label and a cited "
          "file position claim no number; a number in the sentence still does (EI-05)",
          all(claims.values()) and not real["ok"], f"{claims} real={real['problems']}")
    # ---------------------------------------------------------------- EI-06
    c8 = _case(ev, "c8-frontends-services-k33")
    k8, ck8, _s = gf.load_key(ev, c8)
    calls = _fence('flowchart LR\n  subgraph FE["Front-ends"]\n    WEB["Web shop"]\n'
                   '    BFF["Mobile BFF"]\n    PAPI["Partner API"]\n  end\n'
                   '  subgraph DS["Domain services"]\n    CAT["Catalog service"]\n'
                   '    PRC["Pricing service"]\n    STK["Stock service"]\n  end\n'
                   '  WEB --> CAT & PRC & STK\n  BFF --> CAT & PRC & STK\n'
                   '  PAPI --> CAT & PRC & STK')
    below = calls + ("\n*Figure 2.4 — Front-end calls to domain services.* Each front-end calls "
                     "each domain service. The figure leaves out the Admin console and the "
                     "Warehouse feed.\n")
    legend = ("**Figure 1.** Front-ends and domain services — who calls which service.\n\n"
              + calls + "\nNot drawn: the Admin console and the Warehouse feed.\n")
    overclaim = calls + "\n*Figure 2.4 — Calls from the Admin console to the services.*\n"
    q13 = [_q(gf.grade_answer(t, c8, k8, ck8, ev, NOTATION, None), "Q13")
           for t in (below, legend, overclaim)]
    check("TC-ME-18 caption claims come from the title and the claim sentence, above or below "
          "the fence: an omission stated after them costs nothing; a title that names an "
          "undrawn element still fails Q13 (EI-06)", q13 == ["pass", "pass", "fail"], f"{q13}")
    # ---------------------------------------------------------------- R1
    c3 = _case(ev, "c3-leave-request-lifecycle")
    k3, ck3, _s = gf.load_key(ev, c3)
    fig3 = _read(c3["pass"])
    fig3 = fig3[fig3.index("```mermaid"):]
    planted = ("**Рисунок 2.3.** Состояния заявки на отпуск. Каждый переход подписан "
               "исполнителем.\n\n" + fig3)
    cases8 = {
        "title, then a claim that names the Admin console":
            "**Figure 2.4.** Front-ends and domain services. Every call of the Web shop, the "
            "Mobile BFF, the Partner API and the Admin console is drawn.\n\n" + calls,
        "a title in the bold label that names the Admin console":
            "**Figure 2.4. Calls of the Admin console.** Each front-end calls each domain "
            "service.\n\n" + calls,
        "a claim, then an omission, below the fence":
            calls + "\n*Figure 2.4:* Each front-end calls each domain service directly (FS-1), "
            "with no gateway between them (FS-2). Calls from the Admin console are not shown.\n",
        "title, claim, then an omission":
            "**Figure 2.4.** Front-end calls. Each front-end calls each domain service. The "
            "figure leaves out the Admin console.\n\n" + calls,
        "no label: a claim, then an omission":
            "The figure shows the calls of the front-ends. The Admin console is not drawn.\n\n"
            + calls}
    got = {"planted C3 caption": _q(gf.grade_answer(planted, c3, k3, ck3, ev, NOTATION, None),
                                    "Q13")}
    got.update({name: _q(gf.grade_answer(t, c8, k8, ck8, ev, NOTATION, None), "Q13")
                for name, t in cases8.items()})
    want = ["fail", "fail", "fail", "pass", "pass", "pass"]
    check("TC-ME-18 a caption of the skill's form claims its title and its claim sentence: a title "
          "that stands as its own sentence leaves the next sentence a claim (the planted C3 "
          "caption hits t6), a title inside the bold label is read, and a sentence after the "
          "claim, such as an omission, is not; a paragraph without a label claims its first "
          "sentence (R1)", list(got.values()) == want, f"{got}")
    # ---------------------------------------------------------------- bare claims (wave 1c)
    every = set(ck3.entities) | set(ck3.groups)
    title3 = "**Рисунок 2.3.** Состояния заявки на отпуск. "
    t6_cases = {
        "C3 run 1: the claim sentence ends with the alias":
            (title3 + "Каждый переход подписан исполнителем. Где §2.3.1 исполнителя не называет, "
             "переход подписан условием.", True),
        "C3 run 2: the same sentence qualifies the claim":
            (title3 + "Каждый переход подписан исполнителем, а где текст исполнителя не называет, "
             "условием.", False),
        "C3 run 3: the same sentence qualifies the claim":
            (title3 + "Каждый переход подписан исполнителем, а где текст исполнителя не называет, "
             "подписан условием.", False),
        "the skill's P13 caption":
            ("**Figure P9.** The states of a step — each transition labelled with its writer, or "
             "with its condition where the source names no writer.", False),
        "the skill's N13 caption":
            ("**Figure P9.** The states of a step and the writer of each transition.", True),
        "a reference in brackets after the alias":
            (title3 + "Каждый переход подписан исполнителем (§2.3.1).", True),
        "a qualification in brackets after the alias":
            (title3 + "Каждый переход подписан исполнителем (или условием, где его нет).", False),
        "a title that ends with the alias, then a claim":
            ("**Figure 1.** The writer of each transition. Each arrow carries a label.", True)}
    hits = {name: "t6" in fd.caption_claims(cap, ck3, every, [])["decoy_hits"]
            for name, (cap, _want) in t6_cases.items()}
    q13 = {run: _q(gf.grade_answer(t6_cases[name][0] + "\n\n" + fig3, c3, k3, ck3, ev, NOTATION,
                                   None), "Q13")
           for run, name in (("run 1", "C3 run 1: the claim sentence ends with the alias"),
                             ("run 2", "C3 run 2: the same sentence qualifies the claim"))}
    cc1 = fd.caption_claims("**Figure 1.** Alpha service and Beta store — every call is encrypted, "
                            "at rest and in transit.", fd.compile_key(UNIT_KEY), {"a", "b"}, [])
    check("TC-ME-18 a caption_overclaim decoy matches a bare claim only, one whose sentence ends "
          "with the alias: C3 run 1 hits t6 and fails Q13; runs 2 and 3 qualify the claim in the "
          "same sentence and pass; the skill's P13 caption passes and N13 hits; a reference in "
          "brackets after the alias still hits; a caption claim trap still matches anywhere "
          "(wave 1c)",
          all(hits[n] == want for n, (_c, want) in t6_cases.items())
          and q13 == {"run 1": "fail", "run 2": "pass"} and "cc1" in cc1["decoy_hits"],
          f"t6 hits={hits} Q13={q13} cc1={cc1['decoy_hits']}")
    title_en = "**Figure 2.3.** The states of a leave request. "
    refs = {"(см. §2.3.1)": title3 + "Каждый переход подписан исполнителем (см. §2.3.1).",
            "(п. 2.3.1)": title3 + "Каждый переход подписан исполнителем (п. 2.3.1).",
            "(см. рис. 3)": title3 + "Каждый переход подписан исполнителем (см. рис. 3).",
            "(see Fig. 3)": title_en + "The writer of each transition (see Fig. 3).",
            "(cf. §2.3)": title_en + "The writer of each transition (cf. §2.3).",
            "(§2.3.1) (FS-1)": title3 + "Каждый переход подписан исполнителем (§2.3.1) (FS-1)."}
    ref_hits = {name: "t6" in fd.caption_claims(cap, ck3, every, [])["decoy_hits"]
                for name, cap in refs.items()}
    ref_q13 = _q(gf.grade_answer(refs["(см. §2.3.1)"] + "\n\n" + fig3, c3, k3, ck3, ev, NOTATION,
                                 None), "Q13")
    qualified = "t6" in fd.caption_claims(
        title3 + "Каждый переход подписан исполнителем (см. §2.3.1), а где текст исполнителя не "
        "называет, условием.", ck3, every, [])["decoy_hits"]
    t6_toks = next(cd["toks"] for cd in ck3.caption_decoys if cd["id"] == "t6")
    direct = any(fd._bare_claim("Каждый переход подписан исполнителем (см. §2.3.1). Где §2.3.1 "
                                "исполнителя не называет, переход подписан условием.", tk)
                 for tk in t6_toks)
    check("TC-ME-18 a reference in brackets that ends the claim sentence is dropped before the "
          "sentences are split, so an abbreviation inside it (`см.`, `п.`, `Fig.`, `cf.`) does not "
          "cut the claim: each such caption hits t6, and C3 run 1 with `(см. §2.3.1)` fails Q13; "
          "a reference that the sentence goes on after is kept (wave 1c verification)",
          all(ref_hits.values()) and ref_q13 == "fail" and not qualified and direct,
          f"t6 hits={ref_hits} Q13={ref_q13} qualified hit={qualified} _bare_claim={direct}")
    long_captions = {
        "32,000 spaces in the claim": "**Рисунок 1.** Каждый переход" + " " * 32000 + "x",
        "8,000 bracket groups after the alias":
            "**Рисунок 1.** Каждый переход подписан исполнителем" + " (1)" * 8000 + "."}
    took, long_hits = {}, {}
    for name, cap in long_captions.items():
        started = time.perf_counter()
        long_hits[name] = "t6" in fd.caption_claims(cap, ck3, every, [])["decoy_hits"]
        took[name] = round(time.perf_counter() - started, 3)
    check("TC-ME-18 a caption with a long white-space run, or with many bracket groups after the "
          "alias, is read in under 0.5 s; the groups are dropped, so the alias still ends the "
          "claim (wave 1c verification)",
          all(t < 0.5 for t in took.values())
          and long_hits == {"32,000 spaces in the claim": False,
                            "8,000 bracket groups after the alias": True},
          f"seconds={took} t6 hits={long_hits}")
    residual = ("**Figure 2.4.** Each front-end calls each domain service. Calls from the Admin "
                "console are not shown.\n\n" + calls)
    broken = ("**Figure 2.4.** Each front-end calls each domain service, directly. Calls from the "
              "Admin console are not shown.\n\n" + calls)
    pin = {name: _q(gf.grade_answer(t, c8, k8, ck8, ev, NOTATION, None), "Q13")
           for name, t in (("claim with no clause break", residual),
                           ("claim with a clause break", broken))}
    check("TC-ME-18 the residual of the title rule, recorded in AMENDMENTS.md: after a label, a "
          "claim sentence with no clause break reads as the title, so the omission sentence after "
          "it reads as the claim and fails Q13; a clause break in the claim sentence leaves the "
          "omission unread (wave 1c)",
          pin == {"claim with no clause break": "fail", "claim with a clause break": "pass"},
          f"{pin}")


def t_gantt_dates():
    """EI-07: the dates a gantt computes are dates it shows."""
    ev = _ev()
    c4 = _case(ev, "c4-reporting-migration-gantt")
    k4, ck4, _s = gf.load_key(ev, c4)
    chart = _fence("gantt\n  dateFormat YYYY-MM-DD\n  excludes weekends\n  section Platform\n"
                   "  P1 Provision the new cluster :p1, 2026-11-02, 4d\n"
                   "  P2 Configure replication :p2, after p1, 3d\n  section Data\n"
                   "  D1 Backfill dimension tables :d1, after p2, 2d\n"
                   "  D2 Backfill fact tables :d2, after p2, 6d\n  section QA\n"
                   "  Q1 Reconcile row counts :q1, after d1 d2, 2d\n  section Release\n"
                   "  R1 Write freeze :r1, after q1, 1d\n"
                   "  R2 Switch dashboards :milestone, r2, after r1, 0d")
    claim = "**Figure 1.** Migration — R2 falls at the end of the write freeze on {} November 2026.\n\n"
    true_, false_ = claim.format(23), claim.format(30)
    g = mm.parse_figure(mm.extract_fences(chart, ("mermaid",))[0]).gantt
    sched = {g.tasks[i].id: tuple(d.isoformat() for d in v)
             for i, v in fd.gantt_schedule(g, "YYYY-MM-DD").items()}
    got = [_q(gf.grade_answer(t + chart, c4, k4, ck4, ev, NOTATION, None), "Q13")
           for t in (true_, false_)]
    check("TC-ME-18 gantt: the dates a chart computes from `after`, durations and `excludes "
          "weekends` are dates it shows; a caption that states one passes Q13, a date the "
          "chart never reaches fails (EI-07)",
          got == ["pass", "fail"] and sched.get("q1") == ("2026-11-19", "2026-11-20", "2026-11-23")
          and sched.get("r1") == ("2026-11-23", "2026-11-23", "2026-11-24")
          and sched.get("r2", ("", "", ""))[0] == "2026-11-24", f"{got} {sched}")
    c2 = _case(ev, "c2-card-3ds-sequence")
    k2, ck2, _s = gf.load_key(ev, c2)
    head = "sequenceDiagram\n  participant OA as Orders API\n  participant PS as Payment service\n"
    auto = _fence(head.replace("sequenceDiagram\n", "sequenceDiagram\n  autonumber\n")
                  + "  OA->>PS: place order\n  PS-->>OA: answer\n  OA->>PS: confirm")
    marked = _fence(head + "  OA->>PS: 1. place order\n  PS-->>OA: 2. answer\n"
                    "  OA->>PS: 3. confirm")
    step = "**Figure 1.** One order — steps 1 to {} of the exchange.\n\n"
    steps = [_q(gf.grade_answer(step.format(n) + fig, c2, k2, ck2, ev, NOTATION, None), "Q13")
             for fig in (auto, marked) for n in (3, 4)]
    check("TC-ME-18 the step numbers a figure draws, by `autonumber` or as `1.` markers, are "
          "numbers it shows: a caption that cites steps 1 to 3 of three messages passes Q13, "
          "steps 1 to 4 fail (EI-07)", steps == ["pass", "fail", "pass", "fail"], f"{steps}")
    unit = "**Figure 1.** {}\n\n"
    bare = {"C2 steps 1 to 3": (c2, k2, ck2, "One order — steps 1 to 3 of the exchange.", auto),
            "C2 every 3 min": (c2, k2, ck2, "One order — the PSP retries every 3 min.", auto),
            "C2 after 2 minutes": (c2, k2, ck2, "One order — the challenge expires after 2 "
                                                "minutes.", auto),
            "C4 on 23 November": (c4, k4, ck4, "Migration — R2 falls on 23 November 2026.", chart),
            "C4 takes 23 h": (c4, k4, ck4, "Migration — the switch-over takes 23 h.", chart),
            "C4 lasts 11 hours": (c4, k4, ck4, "Migration — the write freeze lasts 11 hours.",
                                  chart)}
    got = {name: _q(gf.grade_answer(unit.format(cap) + fig, c, k, ck, ev, NOTATION, None), "Q13")
           for name, (c, k, ck, cap, fig) in bare.items()}
    check("TC-ME-18 a step number a figure draws and a part of a date it computes back only a "
          "caption number without a unit: steps 1 to 3 and 23 November pass Q13; 3 min, 2 "
          "minutes, 23 h and 11 hours fail (R2)",
          list(got.values()) == ["pass", "fail", "fail", "pass", "fail", "fail"], f"{got}")


def t_parts():
    """EI-08: a box titled with an entity holds the entity or its parts."""
    parts_key = {"entities": [{"id": "up", "aliases": ["Upload API"]},
                              {"id": "mb", "aliases": ["Media bucket"]},
                              {"id": "orig", "aliases": ["Originals prefix"], "part_of": "mb"},
                              {"id": "thumb", "aliases": ["Thumbnails prefix"], "part_of": "mb"}],
                 "relations": [{"id": "r1", "from": "up", "to": "mb"}]}
    no_parts = copy.deepcopy(parts_key)
    no_parts["entities"] = no_parts["entities"][:2]
    box = _fence('flowchart TB\n  UP["Upload API"]\n  subgraph MB["Media bucket"]\n'
                 '    O[("Originals prefix")]\n    T[("Thumbnails prefix")]\n  end\n  UP --> O')
    named_key = {"entities": [{"id": "lb", "aliases": ["Load balancer"]},
                              {"id": "app", "aliases": ["App nodes", "app-01", "app-02"]}],
                 "relations": [{"id": "r", "from": "lb", "to": "app"}]}
    named = _fence('flowchart TB\n  LB["Load balancer"]\n  subgraph APP["App nodes"]\n'
                   '    A1["app-01"]\n    A2["app-02"]\n  end\n  LB --> A1\n  LB --> A2')
    with_parts, without, own_names = (_match(parts_key, box), _match(no_parts, box),
                                      _match(named_key, named))
    check("TC-ME-18 a box titled with a stated entity holds that entity or its parts: the C6 "
          "shape (named nodes in a box of their entity) fits; with parts in the key, a link to a "
          "part covers its container's relation; without them the parts stay invented (EI-08)",
          all(v["passed"] for v in with_parts["verdicts"].values())
          and all(v["passed"] for v in own_names["verdicts"].values())
          and not without["verdicts"]["Q12"]["passed"]
          and not any("subgraph" in i for i in without["invented"]),
          f"parts={_verdicts(with_parts['verdicts'])} names={_verdicts(own_names['verdicts'])} "
          f"no parts={without['invented']}")
    site_key = {"entities": [{"id": "lb", "aliases": ["Load balancer"]},
                             {"id": "app", "aliases": ["App nodes"]},
                             {"id": "a1", "aliases": ["app-01"], "part_of": "app"},
                             {"id": "a2", "aliases": ["app-02"], "part_of": "app"}],
                "groups": [{"id": "dc1", "aliases": ["Site 1"], "members": ["lb", "app"]}],
                "relations": [{"id": "r", "from": "lb", "to": "app"}]}
    site = _fence('flowchart TB\n  subgraph S1["Site 1"]\n    LB["Load balancer"]\n'
                  '    A1["app-01"]\n    A2["app-02"]\n  end\n  LB --> A1\n  LB --> A2')
    in_site = _match(site_key, site)
    check("TC-ME-18 toward a group box a stated part counts as its container: a box `Site 1` "
          "that holds app-01 and app-02 holds the app nodes the group names, so it is no "
          "invented group (EI-08, amendment a1 C6)",
          all(v["passed"] for v in in_site["verdicts"].values()), f"{in_site['invented']}")


def t_number_subjects():
    """EI-10: a note that names the number's subject attributes it there."""
    ev = _ev()
    c2 = _case(ev, "c2-card-3ds-sequence")
    k2, ck2, _s = gf.load_key(ev, c2)
    head = ("sequenceDiagram\n  participant OA as Orders API\n  participant PS as Payment service\n"
            "  participant PSP as Paylane PSP\n  PSP->>PS: Webhook payment.succeeded\n"
            "  PS-->>PSP: HTTP 200\n")
    right = gf.grade_answer(_fence(head + "  Note over PS,PSP: Paylane PSP repeats an unanswered "
                                   "webhook<br/>every 5 min for up to 24 h"), c2, k2, ck2, ev,
                            NOTATION, None)
    wrong = gf.grade_answer(_fence(head + "  Note over PS: Payment service retries for up to "
                                   "24 h"), c2, k2, ck2, ev, NOTATION, None)
    check("TC-ME-18 a number in a note that names the subject the document gives it is that "
          "subject's, wherever the note sits: no number decoy; the same number on another "
          "subject hits it and fails Q11 (EI-10)",
          _q(right, "Q11") == "pass" and "t3" not in right["fidelity"]["decoy_hits"]
          and _q(wrong, "Q11") == "fail" and "t3" in wrong["fidelity"]["decoy_hits"],
          f"right={right['q']['Q11']['evidence'][:90]} wrong={wrong['fidelity']['decoy_hits']}")
    target = gf.grade_answer(_fence(head + "  Note over PSP: repeats an unanswered webhook to the "
                                    "Payment service<br/>every 5 min for up to 24 h"), c2, k2, ck2,
                             ev, NOTATION, None)
    both = gf.grade_answer(_fence(head + "  Note over PS,PSP: repeats an unanswered webhook<br/>"
                                  "every 5 min for up to 24 h"), c2, k2, ck2, ev, NOTATION, None)
    check("TC-ME-18 a note's numbers belong to the participants it sits over and to the entities "
          "it names: a note over Paylane PSP that names the Payment service as its target keeps "
          "5 min and 24 h on the PSP, and a note over both that names none hits no decoy (R3)",
          all(_q(r, "Q11") == "pass" and "t3" not in r["fidelity"]["decoy_hits"]
              for r in (target, both)),
          f"target={target['q']['Q11']['evidence'][:90]} {target['fidelity']['decoy_hits']} "
          f"both={both['q']['Q11']['evidence'][:90]} {both['fidelity']['decoy_hits']}")


def t_invented_ends():
    """EI-30: an edge to an invented node; the condition decoy."""
    ev = _ev()
    f1 = _case(ev, "f1-ci-stages-terminal")
    k1, ck1, _s = gf.load_key(ev, f1)
    inv = _match(UNIT_KEY, _fence('flowchart TB\n  A["Alpha service"] --> X["Zeta cache"]\n'
                                  '  A --> B["Beta store"]'))
    beside_ = gf.grade_answer("Stages:\n\n```text figure\nlint -> unit tests -> build site\n"
                              "deploy preview -> publish <-- maintainer approval\n```\n",
                              f1, k1, ck1, ev, NOTATION, None)
    between = gf.grade_answer("Stages:\n\n```text figure\ndeploy preview -> maintainer approval "
                              "-> publish\n```\n", f1, k1, ck1, ev, NOTATION, None)
    f1_fail = gf.grade_answer(_read(f1["fail"]), f1, k1, ck1, ev, NOTATION, None)
    check("TC-ME-18 an edge to an invented node is a relation the document does not state (Q09, "
          "F1 fail.md included); a condition drawn beside its stage is no `condition_as_entity` "
          "decoy, and one drawn between two stages is (EI-30)",
          not inv["verdicts"]["Q09"]["passed"] and not inv["verdicts"]["Q12"]["passed"]
          and _q(f1_fail, "Q09") == "fail"
          and "t8" not in beside_["fidelity"]["decoy_hits"]
          and "t8" in between["fidelity"]["decoy_hits"],
          f"invented end={inv['unsupported'][:1]} f1 fail Q09={_q(f1_fail, 'Q09')} "
          f"beside={beside_['fidelity']['decoy_hits']} between={between['fidelity']['decoy_hits']}")


def t_ascii_budget():
    """Q16 leaves the element budgets to Q07 (MA-ASCII-05 and MA-ASCII-06)."""
    ev = _ev()
    f1 = _case(ev, "f1-ci-stages-terminal")
    k1, ck1, _s = gf.load_key(ev, f1)
    doc = "Stages:\n\n" + lint._ascii_probe("hard-fire")(NOTATION)
    rules = sorted({f.rule for f in lint.lint_text(doc, "answer.md", notation=NOTATION)})
    res = gf.grade_answer(doc, f1, k1, ck1, ev, NOTATION, None)
    ids = gf._ascii_rule_ids()
    check("TC-ME-37 an ASCII figure over the hard element budget fails Q07 once; Q16 reads the "
          "ASCII rules without the soft and the hard budget (MA-ASCII-05, MA-ASCII-06) and keeps "
          "the connector rule MA-ASCII-07",
          rules == ["MA-ASCII-06"] and _q(res, "Q07") == "fail" and _q(res, "Q16") == "pass"
          and not {"MA-ASCII-05", "MA-ASCII-06"} & ids and "MA-ASCII-07" in ids,
          f"lint={rules} Q07={_q(res, 'Q07')} Q16={res['q']['Q16']['evidence'][:100]} "
          f"Q16 rules={sorted(ids)}")


def t_fences():
    """The matcher finds fenced lines as `mermaid_model.extract_fences` does."""
    ev = _ev()
    f1 = _case(ev, "f1-ci-stages-terminal")
    k1, ck1, _s = gf.load_key(ev, f1)
    quoted = "The stages:\n\n> ```text\n> lint -> unit tests -> build site\n> ```\n\nDone.\n"
    ans = gf.read_answer(quoted, f1, ck1, k1)
    spans = [(f.start, f.end) for f in mm.extract_fences(quoted, ("text",))]
    check("TC-ME-18 a fence inside a blockquote is fenced for the matcher as for "
          "`mermaid_model.extract_fences`: its lines hold no chain, so the answer holds one "
          "figure, the fence",
          fd.fenced_line_ranges(quoted) == [(3, 5)] and spans == [(3, 5)]
          and [(u.form, u.unfenced) for u in ans.units] == [("text", False)],
          f"ranges={fd.fenced_line_ranges(quoted)} fences={spans} "
          f"units={[(u.form, u.unfenced) for u in ans.units]}")
    drift = ("gateway --> decoder --+--> raw store ---------+--> batch ack\n"
             "                      |                        |\n"
             "                       +--> threshold check ---+")
    fence = "```text\n" + drift + "\n```"
    plain = "**Figure 1.** Decoded readings — two paths.\n\n" + fence + "\n"
    inside = ("**Figure 1.** Decoded readings — two paths.\n\n"
              + "\n".join("> " + ln for ln in fence.split("\n")) + "\n")
    q16 = {name: gf.grade_answer(t, f1, k1, ck1, ev, NOTATION, None)["q"]["Q16"]
           for name, t in (("plain", plain), ("blockquoted", inside))}
    check("TC-ME-37 the ASCII lint reads a blockquoted text fence as a figure too: a connector "
          "that moves by one column fails Q16 inside a blockquote as outside it (wave 1c)",
          all(v["status"] == "fail" and "MA-ASCII-07" in v["evidence"] for v in q16.values()),
          f"{ {k: v['evidence'][:90] for k, v in q16.items()} }")


# =========================================================================== D8 scores and decision


def _fake_run(ev, cid, arm, rep, passes, k=(4, 0), served=True):
    """A graded run whose first ten headline checks hold *passes* passes, then fails."""
    q_ids = [c["id"] for c in ev["checks"]]
    k_ids = [c["id"] for c in ev["contract_checks"]]
    checks = {q: ("pass" if i < passes else "fail") if i < 10 else "na"
              for i, q in enumerate(q_ids)}
    contract = {kk: ("pass" if i < k[0] else "fail") if i < k[0] + k[1] else "na"
                for i, kk in enumerate(k_ids)}
    grading = {"checks": checks, "contract": contract, "strict_pass": passes == 10,
               "figures": 1, "no_figure": False, "fidelity": {"decoys": {}}}
    return {"rel": f"eval-{cid}-x/{arm}/run-{rep}", "case": cid, "arm": arm, "rep": rep,
            "grading": grading, "excluded": None, "meta": {"served_model_ok": served}}


def _fake_campaign(ev, with_reps, without_reps, c0_with, c0_without, arms=None):
    runs = []
    arms = arms or ("with_skill", "without_skill")
    for c in ev["evals"]:
        cid = int(c["id"])
        plan = {"with_skill": c0_with if c.get("control") else with_reps,
                "without_skill": c0_without if c.get("control") else without_reps}
        for arm in arms:
            for rep, passes in enumerate(plan[arm], 1):
                runs.append(_fake_run(ev, cid, arm, rep, passes))
    return runs


def t_scores():
    ev = _ev()
    tmp = Path(tempfile.mkdtemp(prefix="mfe-d8-"))
    try:
        no_labels = tmp / "absent-labels.json"
        report = gf.build_report(_fake_campaign(ev, [10, 5, 8], [2, 9, 4], [10, 10, 10], [0, 0, 0]),
                                 ev, NOTATION, tmp, {}, calibration=no_labels)
        nofig = gf.run_metrics(gf.build_grading(gf.grade_answer(
            "Nothing to draw here.", UNIT_CASE, UNIT_KEY, fd.compile_key(UNIT_KEY), ev, NOTATION, {}),
            ev), ev)
        row = report["cases"]["1"]["with_skill"]
        check("TC-ME-29 D8 scores: a case's score is the median of its repetitions; Δ_H is the "
              "mean over the ten cases C1-C8, F1, F2; C0 stays out; a run without a figure scores 0",
              report["deltas"]["H"]["delta"] == 0.4 and report["deltas"]["H"]["cases"] == 10
              and row["H"] == 0.8 and row["H_mean"] == round(2.3 / 3, 6)
              and report["arms"]["with_skill"]["H"] == 0.8 and nofig["H"] == 0.0,
              f"delta={report['deltas']['H']} case={row} no-figure H={nofig['H']}")
        labels = _labels_file(tmp / "labels.json", [
            {"id": f"s{i}", "seeded": False,
             "evidence": _defect_evidence(gf.DEFECT_TYPES[i % len(gf.DEFECT_TYPES)]),
             "labels": {t: t == gf.DEFECT_TYPES[i % len(gf.DEFECT_TYPES)] for t in gf.DEFECT_TYPES}}
            for i in range(35)])
        good_runs = _fake_campaign(ev, [10, 10, 10], [5, 5, 5], [10, 10, 10], [10, 10, 10])
        valid = gf.build_report(good_runs, ev, NOTATION, tmp, {}, calibration=labels)
        st = {c["id"]: c["status"] for c in valid["decision"]["criteria"]}
        c1v = next(c for c in valid["decision"]["criteria"] if c["id"] == "C1")["value"]
        check("TC-ME-29 the decision table lists V1, V2, V3, C1 before H1, H2, H3, V4; C1 needs "
              "0.8 with the skill and only reports the rate without it; a valid campaign that "
              "meets every criterion holds the claim",
              list(st) == list(gf.VALIDITY + gf.EFFECT) and set(st.values()) == {"met"}
              and valid["decision"]["validity"] == "valid" and valid["decision"]["claim_holds"]
              and c1v["without_skill_information"] == 1.0
              and [c["group"] for c in valid["decision"]["criteria"]] == ["validity"] * 4 + ["effect"] * 4,
              f"{st} validity={valid['decision']['validity']} C1={c1v}")
        bad_runs = good_runs + [{"rel": "eval-1-x/with_skill/run-4", "case": 1, "arm": "with_skill",
                                 "rep": 4, "grading": None, "excluded": "not rendered: v11 infra_error",
                                 "meta": {}}]
        invalid = gf.build_report(bad_runs, ev, NOTATION, tmp, {}, calibration=labels)
        ist = {c["id"]: c["status"] for c in invalid["decision"]["criteria"]}
        check("TC-ME-29 validity first: an ungraded run fails V1 and marks the campaign invalid; "
              "the effect criteria are still reported and decide nothing",
              ist["V1"] == "not met" and invalid["decision"]["campaign_invalid"] is True
              and invalid["decision"]["validity"] == "invalid" and not invalid["decision"]["claim_holds"]
              and invalid["decision"]["statement"].startswith("the campaign is invalid")
              and all(ist[e] in ("met", "not met") for e in gf.EFFECT),
              f"{ist} {invalid['decision']['statement'][:100]}")
        only = _fake_campaign(ev, [10, 10, 10], [5, 5, 5], [10, 10, 10], [10, 10, 10],
                              arms=("without_skill",))
        arm_dir, budget_dir = tmp / "arm", tmp / "budget"
        arm_dir.mkdir()
        budget_dir.mkdir()
        cap = float(ev["campaign"]["budget_usd"])
        per = round(cap / 33.5, 4)
        (budget_dir / "attempts.jsonl").write_text("".join(
            json.dumps({"arm": "without_skill", "total_cost_usd": per}) + "\n" for _ in range(33)),
            encoding="utf-8")
        missing = gf.build_report(only, ev, NOTATION, arm_dir, {}, calibration=no_labels)
        budget = gf.build_report(only, ev, NOTATION, budget_dir, {}, calibration=no_labels)
        mst = {c["id"]: c["status"] for c in missing["decision"]["criteria"]}
        bst = {c["id"]: c["status"] for c in budget["decision"]["criteria"]}
        arm_ne, budget_ne = f"not evaluated ({gf.NE_ARM})", f"not evaluated ({gf.NE_BUDGET})"
        check("TC-ME-29 a criterion without its data is `not evaluated (<reason>)`: missing arm, "
              "budget when the ledger reached the cap, no calibration labels for V2",
              all(mst[c] == arm_ne for c in ("C1", "H1", "H2", "H3", "V4"))
              and all(bst[c] == budget_ne for c in ("C1", "H1", "H2", "H3", "V4"))
              and mst["V3"] == "met" and mst["V1"] == "met"
              and mst["V2"] == f"not evaluated ({gf.NE_LABELS})"
              and budget["cost"]["shared_budget"]["exhausted"] is True
              and missing["decision"]["validity"] == "not established",
              f"missing={mst} budget={bst}")
        first = _synthetic_campaign(tmp / "round-1", ev)
        second = _synthetic_campaign(tmp / "round-2", ev, which={"with_skill": "pass"})
        alone_runs, alone = gf.grade_corpus(second, ev, NOTATION, labels)
        both_runs, both = gf.grade_corpus(second, ev, NOTATION, labels, baseline=first)
        out = tmp / "round-2-graded"
        with contextlib.redirect_stdout(io.StringIO()):
            gf.write_outputs(second, out, both_runs, both, ev)
        astat = {c["id"]: c["status"] for c in alone["decision"]["criteria"]}
        bstat = {c["id"]: c["status"] for c in both["decision"]["criteria"]}
        leaked = list(out.glob("round-1*")) + list(first.glob("eval-*/*/run-*/grading.json"))
        check("TC-ME-29 a revision round reads the arms it lacks from the first round "
              "(--baseline-corpus), is labelled post-revision, same cases, and writes no grading "
              "into the first round",
              astat["H1"] == f"not evaluated ({gf.NE_ARM})" and bstat["H1"] in ("met", "not met")
              and both["round"]["label"] == gf.POST_REVISION
              and both["round"]["arms_from_baseline"] == ["without_skill"]
              and both["round"]["baseline_campaign"] == "round-1"
              and sum(1 for r in both_runs if r.get("baseline")) == 33 and not leaked,
              f"alone H1={astat['H1']} with baseline H1={bstat['H1']} round={both['round']} "
              f"leaked={leaked[:2]}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def t_report_completeness():
    ev = _ev()
    tmp = Path(tempfile.mkdtemp(prefix="mfe-reps-"))
    try:
        no_labels = tmp / "absent-labels.json"
        runs = [r for r in _fake_campaign(ev, [10, 10, 10], [5, 5, 5], [10, 10, 10], [10, 10, 10])
                if not (r["case"] == 10 and r["arm"] == "with_skill" and r["rep"] > 1)]
        short = gf.build_report(runs, ev, NOTATION, tmp, {}, calibration=no_labels)
        st = {c["id"]: c["status"] for c in short["decision"]["criteria"]}
        budget_dir = tmp / "budget"
        budget_dir.mkdir()
        cap = float(ev["campaign"]["budget_usd"])
        (budget_dir / "attempts.jsonl").write_text("".join(
            json.dumps({"arm": "with_skill", "total_cost_usd": round(cap / 30.5, 4)}) + "\n"
            for _ in range(30)), encoding="utf-8")
        stopped = gf.build_report(runs, ev, NOTATION, budget_dir, {}, calibration=no_labels)
        bst = {c["id"]: c["status"] for c in stopped["decision"]["criteria"]}
        check("TC-ME-29 a case and arm with fewer graded runs than the campaign's repetitions is "
              "missing, never scored on fewer runs: its criteria are not evaluated, for the "
              "budget when the budget stopped that arm (EI-18)",
              "10:with_skill" in short["missing"]
              and short["incomplete"] == {"10:with_skill": "1 of 3 graded"}
              and all(st[c] == f"not evaluated ({gf.NE_ARM})"
                      for c in ("C1", "H1", "H2", "H3", "V4"))
              and all(bst[c] == f"not evaluated ({gf.NE_BUDGET})" for c in ("H1", "H2", "H3", "V4")),
              f"missing={short['missing']} short={st['H1']} budget={bst['H1']}")
        ledger_dir = tmp / "ledger"
        ledger_dir.mkdir()
        rows = ([{"arm": "without_skill", "total_cost_usd": 0} for _ in range(60)]
                + [{"arm": "without_skill", "total_cost_usd": 0.5} for _ in range(33)]
                + [{"arm": "with_skill", "total_cost_usd": 2.0} for _ in range(21)])
        (ledger_dir / "attempts.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows),
                                                   encoding="utf-8")
        state = gf.budget_state(ledger_dir, ev)
        check("TC-ME-29 the report measures the budget as the executor does: attempts that cost "
              "nothing count nothing and each arm's next run is projected at its own mean, so "
              "a with_skill run the executor refuses is missing for the budget (EI-15)",
              state["spent_usd"] == 58.5 and state["next_run_usd"]["with_skill"] == 2.0
              and state["exhausted_for"] == {"with_skill": True, "without_skill": False},
              f"{state}")
        mixed = [dict(r, meta=dict(r["meta"], timeout_s=1200 if r["arm"] == "without_skill"
                                   else 30)) for r in _fake_campaign(ev, [10] * 3, [5] * 3,
                                                                     [10] * 3, [10] * 3)]
        flagged = gf.build_report(mixed, ev, NOTATION, tmp, {}, calibration=no_labels)
        with contextlib.redirect_stdout(io.StringIO()):
            text = gf.summarize(flagged)
        check("TC-ME-29 the report states what V2 covers, and flags run records whose executor "
              "settings differ between the arms (EI-11, EI-19)",
              flagged["invocation"]["differ"] == ["timeout_s"] and "timeout_s" in text
              and "seven defect types" in flagged["v2_scope"]
              and all(t in flagged["v2_scope"] for t in gf.DEFECT_TYPES),
              f"invocation={flagged['invocation']['differ']}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def t_sequence_legend():
    ev = _ev()
    c2 = _case(ev, "c2-card-3ds-sequence")
    k2, ck2, _s = gf.load_key(ev, c2)
    fail = gf.grade_answer(_read(c2["fail"]), c2, k2, ck2, ev, NOTATION, None)
    good = gf.grade_answer(_read(c2["pass"]), c2, k2, ck2, ev, NOTATION, None)
    one = gf.grade_answer(_fence("sequenceDiagram\n  participant A as Orders API\n"
                                 "  participant B as Payment service\n  A->>B: pay"),
                          c2, k2, ck2, ev, NOTATION, None)
    check("TC-ME-19 a sequence with solid and dashed arrows uses two encodings: without a legend "
          "Q14 fails (C2 fail.md); a legend that names them passes (C2 pass.md); one arrow style "
          "needs none (EI-29)",
          _q(fail, "Q14") == "fail" and _q(good, "Q14") == "pass" and _q(one, "Q14") == "na",
          f"fail={_q(fail, 'Q14')} pass={_q(good, 'Q14')} one style={_q(one, 'Q14')}")
    # ---------------------------------------------------------------- the lint's legend count
    three = ("**Figure 1.** One payment — the calls, the replies and the webhook.\n\n"
             + _fence("sequenceDiagram\n  participant OA as Orders API\n"
                      "  participant PS as Payment service\n  participant PSP as Paylane PSP\n"
                      "  OA->>PS: pay\n  PS-->>OA: payment id\n  PSP-)PS: webhook") + "\n{}\n")
    two_items = "Solid arrow: a call; dashed arrow: a reply."
    three_items = two_items[:-1] + "; open arrow: a message nobody waits on."
    q14 = [_q(gf.grade_answer(three.format(leg), c2, k2, ck2, ev, NOTATION, None), "Q14")
           for leg in (two_items, three_items)]
    ctx = types.SimpleNamespace(notation=NOTATION)
    mirror, own = [], []
    for slug, _cid in CASES:
        case = _case(ev, slug)
        for which in ("pass", "fail"):
            for f in mm.extract_fences(_read(case[which]), ("mermaid",)):
                fig = mm.parse_figure(f)
                if gf._legend_trigger(fig, NOTATION) != bool(lint._legend_reasons(fig, ctx)):
                    mirror.append(f"{slug} {which} line {f.start}")
                if fig.sequence is not None:
                    found = gf._sequence_encodings(fig)
                    th = NOTATION.get("lint", {})
                    mine = (len(found[0]) >= int(th.get("legend_min_classes", 2))
                            or len(found[1]) >= int(th.get("legend_min_edge_styles", 2)))
                    if mine != gf._legend_trigger(fig, NOTATION):
                        own.append(f"{slug} {which} line {f.start}")
    check("TC-ME-19 Q14 counts the encodings of the lint's legend rule (MA-DOC-02): its trigger "
          "agrees with the lint on every fixture figure and with the grader's own sequence count "
          "on C2; a sequence with three arrow kinds needs three legend items (EI-29)",
          q14 == ["fail", "pass"] and not mirror and not own,
          f"two items={q14[0]} three items={q14[1]} lint disagrees={mirror} own count "
          f"disagrees={own}")


# ============================================================================ provenance (EI-13)


def _registered_campaign(root, ev, cases=("c7-refund-decision", "c0-control-thumbnails")):
    """A synthetic campaign of two cases whose campaign.json registers the files graded."""
    camp = _synthetic_campaign(root, dict(ev, evals=[_case(ev, s) for s in cases]))
    files = {"evals.json": hashlib.sha256((HERE / "evals.json").read_bytes()).hexdigest()}
    for c in ev["evals"]:
        files[c["key"]] = hashlib.sha256((HERE / c["key"]).read_bytes()).hexdigest()
    (camp / "campaign.json").write_text(json.dumps(
        {"campaign_id": camp.name, "created": "2026-10-03T00:00:00Z",
         "provenance": {"file": "PROVENANCE.txt", "files": files}}), encoding="utf-8")
    return camp, files


def t_provenance():
    ev = _ev()
    tmp = Path(tempfile.mkdtemp(prefix="mfe-prov-"))
    saved = gf.AMENDMENTS_DIR
    sink_o, sink_e = io.StringIO(), io.StringIO()
    try:
        camp, files = _registered_campaign(tmp / "camp", ev)
        _runs, report = gf.grade_corpus(camp, ev, NOTATION, tmp / "no-labels.json")
        prov, grader = report["provenance"], report["grader"]
        check("TC-ME-38 a campaign graded under the files it registered: provenance verified, not "
              "post-hoc; the report records the full key hashes, the evals hash, the hash of the "
              "normalisation rule and of the grader and matcher (EI-13)",
              prov["status"] == "verified" and report["post_hoc"] is False
              and grader["normalize_sha256"] == fd.NORMALIZE_SHA256
              and fd.NORMALIZE_SHA256 == hashlib.sha256(fd._normalize_source().encode()).hexdigest()
              and all(len(v) == 64 for v in grader["keys_sha256"].values())
              and grader["evals_sha256"] == files["evals.json"]
              and set(grader["instrument"]) == {"grade_figures.py", "fidelity.py", "normalize"},
              f"status={prov['status']} post_hoc={report['post_hoc']}")
        inst = prov["instrument"]
        summary = gf.summarize(report)
        check("TC-ME-38 the report, benchmark.md and the summary say that the campaign registered "
              "neither the normalisation rule nor the grader: their sha256 is recorded at grading "
              "time, and a change after the runs is not refused (EI-13)",
              inst["registered"] == {"grade_figures.py": False, "fidelity.py": False,
                                     "normalize": False}
              and "not registered" in inst["statement"] and inst["sha256"] == grader["instrument"]
              and f"grader provenance: {inst['statement']}" in summary
              and "## Grader provenance" in gf.benchmark_markdown("# page\n", report),
              f"{inst['registered']} {inst['statement'][:120]}")
        meta = json.loads((camp / "campaign.json").read_text(encoding="utf-8"))
        regs = {}
        for name, value in (("same", gf.instrument_hashes()),
                            ("other rule", dict(gf.instrument_hashes(), normalize="0" * 64))):
            meta["provenance"]["instrument"] = value
            (camp / "campaign.json").write_text(json.dumps(meta), encoding="utf-8")
            regs[name] = gf.grade_corpus(camp, ev, NOTATION, tmp / "no-labels.json")[1][
                "provenance"]["instrument"]
        del meta["provenance"]["instrument"]
        (camp / "campaign.json").write_text(json.dumps(meta), encoding="utf-8")
        check("TC-ME-38 a campaign that registers the grader's hashes in campaign.json is reported "
              "registered; a registered normalisation rule that differs from the one graded is "
              "named (EI-13)",
              all(regs["same"]["registered"].values())
              and "were registered" in regs["same"]["statement"]
              and regs["other rule"]["registered"] == {"grade_figures.py": True,
                                                       "fidelity.py": True, "normalize": False}
              and "differs" in regs["other rule"]["statement"],
              f"same={regs['same']['registered']} other={regs['other rule']['statement'][:120]}")
        c7 = _case(ev, "c7-refund-decision")
        meta = json.loads((camp / "campaign.json").read_text(encoding="utf-8"))
        meta["provenance"]["files"][c7["key"]] = "0" * 64
        (camp / "campaign.json").write_text(json.dumps(meta), encoding="utf-8")
        try:
            gf.grade_corpus(camp, ev, NOTATION, tmp / "no-labels.json")
            refused = False
        except gf.InstrumentError as exc:
            refused = c7["key"] in str(exc)
        with contextlib.redirect_stdout(sink_o), contextlib.redirect_stderr(sink_e):
            code = gf.main(["--corpus", str(camp), "--out", str(tmp / "out-changed")])
        check("TC-ME-38 a graded key whose sha256 differs from the campaign's registration and that "
              "no amendment names breaks the instrument: exit 2 (EI-13)",
              refused and code == 2, f"refused={refused} exit={code}")
        meta["provenance"]["files"] = files
        (camp / "campaign.json").write_text(json.dumps(meta), encoding="utf-8")
        gf.AMENDMENTS_DIR = tmp / "evals" / "amendments"
        (gf.AMENDMENTS_DIR / "A1").mkdir(parents=True)
        key7 = json.loads(_read(c7["key"]))
        key7["entities"][0].setdefault("aliases", []).append("Customer asks for a refund")
        amended = gf.AMENDMENTS_DIR / "A1" / "c7.key.json"
        amended.write_text(json.dumps(key7), encoding="utf-8")
        entry = {"registered": c7["key"], "registered_sha256": files[c7["key"]],
                 "amended": "amendments/A1/c7.key.json",
                 "amended_sha256": hashlib.sha256(amended.read_bytes()).hexdigest(),
                 "reason": "the document's own start wording (selftest)"}
        doc = {"schema": gf.AMENDMENT_SCHEMA, "id": "A1", "campaign": camp.name,
               "decided_by": "operator (selftest)", "date": "2026-10-03",
               "reason": "selftest", "files": [entry]}
        apath = gf.AMENDMENTS_DIR / "A1.json"
        apath.write_text(json.dumps(doc), encoding="utf-8")
        out = tmp / "out-amended"
        with contextlib.redirect_stdout(sink_o), contextlib.redirect_stderr(sink_e):
            code = gf.main(["--corpus", str(camp), "--out", str(out), "--amendment", str(apath)])
        rep = json.loads((out / "report.json").read_text(encoding="utf-8")) \
            if (out / "report.json").is_file() else {}
        bench = (out / "benchmark.md").read_text(encoding="utf-8").split("\n")[0] \
            if (out / "benchmark.md").is_file() else None
        check("TC-ME-38 an amendment under evals/amendments/ is the one sanctioned departure: the "
              "report is stamped post_hoc with the amendment id, its statement and benchmark.md "
              "open with POST-HOC SENSITIVITY (EI-13)",
              code == 0 and rep.get("post_hoc") is True
              and rep["provenance"]["amendment"]["id"] == "A1"
              and rep["decision"]["statement"].startswith("POST-HOC SENSITIVITY")
              and (bench is None or bench.startswith("POST-HOC SENSITIVITY")),
              f"exit={code} post_hoc={rep.get('post_hoc')} benchmark first line={bench!r}")
        stranger = gf.AMENDMENTS_DIR / "A4.json"
        stranger.write_text(json.dumps(dict(doc, id="A4", campaign="another-campaign")),
                            encoding="utf-8")
        with contextlib.redirect_stdout(sink_o), contextlib.redirect_stderr(sink_e):
            code = gf.main(["--corpus", str(camp), "--out", str(tmp / "o4"),
                            "--amendment", str(stranger)])
        check("TC-ME-38 an amendment for another campaign breaks the instrument: exit 2, no "
              "report (EI-13)", code == 2 and not (tmp / "o4" / "report.json").exists(),
              f"exit={code}")
        outside = tmp / "A2.json"
        outside.write_text(json.dumps(doc), encoding="utf-8")
        amended.write_text(json.dumps(dict(key7, note="tampered")), encoding="utf-8")
        with contextlib.redirect_stdout(sink_o), contextlib.redirect_stderr(sink_e):
            codes = (gf.main(["--corpus", str(camp), "--out", str(tmp / "o2"),
                              "--amendment", str(outside)]),
                     gf.main(["--corpus", str(camp), "--out", str(tmp / "o3"),
                              "--amendment", str(apath)]))
        check("TC-ME-38 an amendment outside evals/amendments/ is a usage error (exit 3); an "
              "amended file whose sha256 differs from the amendment's record breaks the "
              "instrument (exit 2) (EI-13)", codes == (3, 2), f"exit codes {codes}")
    finally:
        gf.AMENDMENTS_DIR = saved
        shutil.rmtree(tmp, ignore_errors=True)


#: The registered keys amendment a1 amends (evals/AMENDMENTS.md).
A1_SLUGS = ("c0-control-thumbnails", "c5-sales-pipeline-dataflow", "c6-clinic-deployment",
            "c7-refund-decision", "c8-frontends-services-k33")


def _a1_expected(slug: str, key: dict) -> dict:
    """The registered *key* with the changes a1 lists for *slug*, its `written` note left out."""
    k = copy.deepcopy(key)
    k.pop("written", None)
    ents = {e["id"]: e for e in k.get("entities", [])}
    if slug == "c0-control-thumbnails":
        k["acceptable_forms"] = ["flowchart", "ascii"]
        k["entities"] += [
            {"id": "mb_orig", "kind": "store", "part_of": "mb", "optional": True,
             "aliases": ["Originals prefix", "originals prefix"], "lines": [27],
             "quote": "under the originals prefix."},
            {"id": "mb_thumb", "kind": "store", "part_of": "mb", "optional": True,
             "aliases": ["Thumbnails prefix", "thumbnails prefix"], "lines": [28],
             "quote": "under the thumbnails prefix."}]
    elif slug == "c5-sales-pipeline-dataflow":
        k["groups"] += [
            {"id": "consumers", "kind": "category", "aliases": ["Consumers", "consumers"],
             "members": ["dash", "fc", "dq"], "lines": [25], "quote": "### 5.2 Consumers"},
            {"id": "pipeline", "kind": "category", "aliases": ["Pipeline", "pipeline"],
             "members": ["raw", "norm", "stg", "dedup", "clean", "loader", "wh"], "lines": [3],
             "quote": "reaches the Sales warehouse through the pipeline of this section"}]
    elif slug == "c6-clinic-deployment":
        ents["app"]["aliases"] = [a for a in ents["app"]["aliases"] if not a.startswith("app-")]
        k["entities"] += [{"id": f"app{n}", "kind": "node", "part_of": "app", "optional": True,
                           "aliases": [f"app-{n}"], "lines": [14],
                           "quote": "| Узлы приложения | app-01, app-02, app-03 |"}
                          for n in ("01", "02", "03")]
    elif slug == "c7-refund-decision":
        ents["request"]["aliases"].append("Customer asks for a refund")
        ents["request"]["soft_aliases"].append("Customer")
    elif slug == "c8-frontends-services-k33":
        for r in k["relations"]:
            if r["id"] in ("r_adm_cat", "r_adm_pri"):
                r["required"] = False
    return k


def t_amendment_a1():
    """Amendment a1 (evals/amendments/a1.json), post-hoc, against the registered keys."""
    ev = _ev()
    names = ("TC-ME-43 amendment a1 loads: it amends the C0, C5, C6, C7 and C8 keys from the "
             "sha256 PROVENANCE.txt registers, for campaign 2026-10-opus55-xhigh-r1, and every "
             "entry says it was made on 2026-10-03, after the runs: POST-HOC",
             "TC-ME-43 each a1 key is its registered key with the listed changes only: C0 accepts "
             "ascii and has the two prefixes as parts, C5 has the groups consumers and pipeline, "
             "C6 has app-01..03 as parts, C7 maps its start wording, C8 requires no Admin console "
             "relation",
             "TC-ME-43 a campaign graded under a1 is stamped post-hoc with the id a1, and the C0 "
             "ASCII figure that fails Q15 under the registered key passes under a1")
    path = HERE / "amendments" / "a1.json"
    try:
        a = gf.load_amendment(path)
    except Exception as exc:  # noqa: BLE001
        for n in names:
            check(n, False, f"{type(exc).__name__}: {exc}")
        return
    registered = {}
    for line in _read("PROVENANCE.txt").splitlines():
        if line.strip() and not line.startswith("#"):
            sha, rel = line.split(None, 1)
            registered[rel.strip()] = sha
    want = {f"fixtures/{s}/key.json" for s in A1_SLUGS}
    entries = a["entries"]
    check(names[0], set(entries) == want and a["campaign"] == "2026-10-opus55-xhigh-r1"
          and all(e["registered_sha256"] == registered.get(r) for r, e in entries.items())
          and all("2026-10-03" in e["reason"] and "POST-HOC" in e["reason"]
                  for e in entries.values())
          and "POST-HOC" in a["reason"],
          f"amended={sorted(entries)} campaign={a['campaign']}")
    wrong = []
    for slug in A1_SLUGS:
        reg = json.loads(_read(f"fixtures/{slug}/key.json"))
        got = json.loads((HERE / entries[f"fixtures/{slug}/key.json"]["amended"]).read_text(
            encoding="utf-8"))
        written = got.pop("written", "")
        fd.compile_key(got, vocabulary=gf.decoy_vocabulary(ev))
        if got != _a1_expected(slug, reg) or "amendment a1, 2026-10-03" not in written:
            wrong.append(slug)
    check(names[1], not wrong, f"keys that differ from their listed changes: {wrong}")
    tmp = Path(tempfile.mkdtemp(prefix="mfe-a1-"))
    sink = io.StringIO()
    try:
        camp, _files = _registered_campaign(tmp / "2026-10-opus55-xhigh-r1", ev)
        out = tmp / "post-hoc-a1"
        with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
            code = gf.main(["--corpus", str(camp), "--out", str(out), "--amendment", str(path)])
        rep = json.loads((out / "report.json").read_text(encoding="utf-8")) \
            if (out / "report.json").is_file() else {}
        c0 = _case(ev, "c0-control-thumbnails")
        ev_a1 = gf.load_evals(amendment=a)
        ascii_c0 = ("**Figure 1.** Media bucket relations.\n\n```text figure\n"
                    "Upload API --writes originals--> Media bucket\n"
                    "Thumbnail service --reads originals--> Media bucket\n"
                    "Thumbnail service --writes thumbnails--> Media bucket\n"
                    "CDN --reads thumbnails--> Media bucket\n```\n")
        q15 = []
        for e in (ev, ev_a1):
            k0, ck0, _s = gf.load_key(e, c0)
            q15.append(_q(gf.grade_answer(ascii_c0, c0, k0, ck0, e, NOTATION, None), "Q15"))
        check(names[2], code == 0 and rep.get("post_hoc") is True
              and rep["provenance"]["amendment"]["id"] == "a1" and q15 == ["fail", "pass"],
              f"exit={code} post_hoc={rep.get('post_hoc')} C0 ASCII Q15 registered/a1={q15}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ====================================================================== executor (EI-17, EI-19)


def _budget_lock_rows(tmp: Path, fake: Path):
    """SEC2-07, with `run_evals.HERE` pointed at *fake*: where the budget lock lies, what it
    refuses, its deadline, and the ledger record of a paid attempt when the lock fails."""
    names = ("TC-ME-39 the budget lock sits in evals/corpus/ of the user's checkout, not in the "
             "shared temporary directory; a symlink or a file of another owner at its path is "
             "refused (exit 2), and the symlink's target stays untouched (SEC2-07)",
             "TC-ME-39 a budget lock held elsewhere stops a waiter at its deadline (exit 2) "
             "instead of blocking it; a paid attempt is recorded in its ledger even when the "
             "lock fails, and no further run is admitted (SEC2-07)")
    try:
        import fcntl  # noqa: F401
    except ImportError:
        for n in names:
            skip(n, "no fcntl here: the lock is the operator's to keep")
        return
    target = tmp / "target.txt"
    target.write_text("keep", encoding="utf-8")

    def refused(lock) -> bool:
        try:
            with lock:
                return False
        except run_evals.InstrumentError:
            return True

    try:
        lock = run_evals._BudgetLock(tmp / "root-a")
        where = (lock.path.parent == fake / "corpus"
                 and lock.path.parent.resolve() != Path(tempfile.gettempdir()).resolve())
        os.symlink(target, lock.path)
        via_link = refused(lock)
        with contextlib.suppress(FileNotFoundError):
            os.unlink(lock.path)
        uid = run_evals.os.getuid
        run_evals.os.getuid = lambda: uid() + 1
        try:
            foreign = refused(run_evals._BudgetLock(tmp / "root-a"))
        finally:
            run_evals.os.getuid = uid
        check(names[0], where and via_link and foreign
              and target.read_text(encoding="utf-8") == "keep",
              f"path={lock.path} in corpus={where} symlink refused={via_link} "
              f"foreign owner refused={foreign} target={target.read_text(encoding='utf-8')!r}")
    except Exception as exc:  # noqa: BLE001 - an executor without the fix
        check(names[0], False, f"{type(exc).__name__}: {exc}")
    try:
        with run_evals._BudgetLock(tmp / "root-b"):
            t0 = time.monotonic()
            stopped = refused(run_evals._BudgetLock(tmp / "root-b", wait_s=0.3))
            waited = time.monotonic() - t0
        out = tmp / "settle"
        out.mkdir()
        args = types.SimpleNamespace(budget_usd=100.0, run_cap_usd=1.0, retries=0, timeout=1,
                                     budget_root=str(tmp / "root-c"), model="m", effort="xhigh")
        ex = run_evals._Executor(args, out, {}, "cli", run_evals.Spend(1.0), "c",
                                 {"sha256": "0" * 64})
        os.symlink(target, ex.budget_lock.path)
        ex.inflight = 1
        ex._settle({"arm": "with_skill", "total_cost_usd": 0.5}, 0.5)
        ledger = [json.loads(x) for x in (out / "attempts.jsonl").read_text(
            encoding="utf-8").splitlines()]
        after, _res = ex._reserve("with_skill")
        check(names[1], stopped and waited < 5 and ledger == [{"arm": "with_skill",
                                                               "total_cost_usd": 0.5}]
              and bool(ex.stop) and str(after).startswith("stopped"),
              f"waiter stopped={stopped} after {waited:.2f} s; ledger={ledger} stop={ex.stop!r} "
              f"next admission={after!r}")
    except Exception as exc:  # noqa: BLE001 - an executor without the fix
        check(names[1], False, f"{type(exc).__name__}: {exc}")


def _budget_arg_rows():
    """SEC2-04: a budget, run cap or timeout of nan or inf is a usage error."""
    codes = {}
    sink = io.StringIO()
    with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
        for flag in ("--budget-usd", "--run-cap-usd", "--timeout"):
            for value in ("nan", "inf", "-inf"):
                codes[f"{flag}={value}"] = run_evals.main(
                    ["--dry-run", "--cases", "0", "--reps", "1", f"{flag}={value}"])
        finite = run_evals.main(["--dry-run", "--cases", "0", "--reps", "1", "--budget-usd=60",
                                 "--run-cap-usd=5", "--timeout=1200"])
    check("TC-ME-45 --budget-usd, --run-cap-usd and --timeout take finite positive numbers "
          "only: nan, inf and -inf are a usage error (exit 3), since a cap of nan or inf "
          "admitted every run (SEC2-04)",
          all(c == run_evals.EXIT_USAGE for c in codes.values()) and finite == run_evals.EXIT_OK,
          f"{codes} finite={finite}")


def t_executor():
    tmp = Path(tempfile.mkdtemp(prefix="mfe-exec-"))
    saved = run_evals.HERE
    try:
        fake = tmp / "evals"
        (fake / "corpus" / "other").mkdir(parents=True)
        (fake / "corpus" / "other" / "attempts.jsonl").write_text(
            json.dumps({"arm": "with_skill", "total_cost_usd": 0.95}) + "\n", encoding="utf-8")
        outside = tmp / "scratch-round"
        outside.mkdir()
        run_evals.HERE = fake
        counted = [p.parent.name for p in run_evals.ledger_files(outside)]
        args = types.SimpleNamespace(budget_usd=1.0, run_cap_usd=1.0, budget_root=None,
                                     retries=0, timeout=1, model="m", effort="xhigh")
        ex = run_evals._Executor(args, outside, {}, "cli", run_evals.Spend(1.0), "c",
                                 {"sha256": "0" * 64})
        refused, _res = ex._reserve("with_skill")
        check("TC-ME-39 the budget counts every evals/corpus*/ ledger wherever the out-root lies, "
              "and each admission reads the ledgers again: an attempt another executor recorded "
              "stops a run this one would start (EI-17)",
              counted == ["other"] and bool(refused) and refused.startswith("budget"),
              f"counted={counted} refused={refused}")
        admitted_lock = ex.budget_lock.path
        path = run_evals._BudgetLock(tmp / "lock-root").path
        held, active, overlap = [], [0], []
        guard = threading.Lock()

        def hold():
            for _ in range(25):
                with run_evals._BudgetLock(tmp / "lock-root"):
                    with guard:
                        active[0] += 1
                        overlap.extend([1] if active[0] > 1 else [])
                    held.append(path.exists())
                    time.sleep(0.0002)
                    with guard:
                        active[0] -= 1

        workers = [threading.Thread(target=hold) for _ in range(4)]
        for w in workers:
            w.start()
        for w in workers:
            w.join(30)
        check("TC-ME-39 the budget lock leaves no lock file once released, and four holders that "
              "take it 100 times never overlap (R6)",
              not admitted_lock.exists() and not path.exists() and not overlap
              and len(held) == 100 and all(held),
              f"after an admission={admitted_lock.exists()} after the holders={path.exists()} "
              f"overlaps={len(overlap)} held={len(held)}")
        _budget_lock_rows(tmp, fake)
    finally:
        run_evals.HERE = saved
        shutil.rmtree(tmp, ignore_errors=True)
    _budget_arg_rows()
    tmp = Path(tempfile.mkdtemp(prefix="mfe-camp-"))
    try:
        args = types.SimpleNamespace(model="m", effort="xhigh", run_cap_usd=5.0, timeout=1200.0,
                                     retries=1, reps=3, evals=str(HERE / "evals.json"))
        prov = {"files": {"README.md": "a" * 64}}
        run_evals._check_campaign(tmp, args, {}, [], "c", prov, "2.1.287")
        written = json.loads((tmp / "campaign.json").read_text(encoding="utf-8"))
        refusals = []
        for change in ({"run_cap_usd": 0.25}, {"timeout": 30.0}, {"retries": 0}, {"reps": 1}):
            other = types.SimpleNamespace(**dict(vars(args), **change))
            try:
                run_evals._check_campaign(tmp, other, {}, [], "c", prov, "2.1.287")
            except run_evals.InstrumentError:
                refusals.append(next(iter(change)))
        try:
            run_evals._check_campaign(tmp, args, {}, [], "c", prov, "2.1.300")
        except run_evals.InstrumentError:
            refusals.append("cli_version")
        old = tmp / "old"
        rd = old / "eval-0-x" / "without_skill" / "run-1"
        rd.mkdir(parents=True)
        (old / "campaign.json").write_text(json.dumps({"model": "m", "effort": "xhigh"}),
                                           encoding="utf-8")
        (rd / "run.meta.json").write_text(json.dumps({"timeout_s": 1200, "run_cap_usd": 5.0,
                                                      "cli_version": "2.1.287"}), encoding="utf-8")
        try:
            run_evals._check_campaign(old, types.SimpleNamespace(**dict(vars(args), timeout=30.0)),
                                      {}, [], "c", prov, "2.1.287")
            old_refused = False
        except run_evals.InstrumentError:
            old_refused = True
        run_evals._check_campaign(old, args, {}, [], "c", prov, "2.1.287")
        check("TC-ME-40 a campaign binds run cap, timeout, retries, reps and CLI version: "
              "campaign.json records them and a differing invocation exits 2; a campaign.json "
              "written before is checked against its run records (EI-19)",
              all(written.get(k) is not None for k in run_evals.BOUND_SETTINGS)
              and refusals == ["run_cap_usd", "timeout", "retries", "reps", "cli_version"]
              and old_refused, f"recorded={[k for k in run_evals.BOUND_SETTINGS if k in written]} "
                               f"refused={refusals} old={old_refused}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ======================================================================= renders (EI-26, SEC-04)


#: A string value that starts with a home directory, on any machine: `/Users/<name>/`,
#: `/home/<name>/` or `/root/` right after the opening quote.
HOME_PATH_VALUE = re.compile(r'"(?:/Users/[^/"]+|/home/[^/"]+|/root)/')


def _home_rows():
    """SEC2-05: every writer of a committed file writes a path under the home as `~/...`, and
    the committed campaign and calibration files name none."""
    names = ("TC-ME-46 render_corpus writes the browser executable and a failed render's log, "
             "and grade_figures the gradings' browser path and the worksheet's PNG paths, with "
             "the home directory as `~`, by exact prefix; a stored entry in either form is "
             "reused (SEC2-05)",
             "TC-ME-46 the committed campaign and calibration files name no path under a home "
             "directory (SEC2-05)")
    home = os.path.expanduser("~").rstrip("/")
    if not home:
        for n in names:
            skip(n, "the home directory is /: no path lies under it")
        return
    exe = home + "/.cache/puppeteer/chrome/headless"
    tmp = Path(tempfile.mkdtemp(prefix="mfe-home-"))
    saved = os.environ.get("HOME")
    try:
        renderer = types.SimpleNamespace(mermaid="11.17.2", browser=exe)
        info = render_corpus._renderer_info("v11", renderer, NOTATION)
        stored = {"status": "rendered", "fence_sha256": "f", "dark": False,
                  "instrument_sha256": "i", "renderer": {"mermaid": "11.17.2", "browser_path": exe}}
        tilde = dict(stored, renderer=dict(stored["renderer"], browser_path=info["browser_path"]))
        reuse = (render_corpus._reusable(tilde, "f", False, renderer, "i"),
                 render_corpus._reusable(stored, "f", False, renderer, "i"))
        log = render_corpus._log_head(f"Error: no Chrome at {home}/.cache/x\n  at {home}/a.js:1")
        summary = gf._summary_entry({"renderer": {"browser_path": exe}})
        probes = (exe, home, home + "x/y", "/opt/chrome", None, "rel/path", "/mnt" + home + "/x")
        same = all(gf.home_relative(p) == render_corpus.home_relative(p) for p in probes)
        kept = [gf.home_relative(p) for p in probes[2:]]
        os.environ["HOME"] = str(tmp)      # a PNG under a home this test owns
        rel = "eval-1-x/with_skill/run-1"
        png = tmp / "renders" / "camp" / rel / "fig-1-v11" / "fig-1-v11.png"
        png.parent.mkdir(parents=True)
        png.write_bytes(b"\x89PNG")
        (tmp / "camp").mkdir()
        paths = gf._png_paths(tmp / "renders", tmp / "camp", rel, "fig-1", ["v11", "v10"])
        check(names[0], info["browser_path"] == "~/.cache/puppeteer/chrome/headless"
              and reuse == (True, True) and home not in log and "~/.cache/x" in log
              and "~/a.js:1" in log and summary["browser_path"] == info["browser_path"] and same
              and kept == [home + "x/y", "/opt/chrome", None, "rel/path", "/mnt" + home + "/x"]
              and paths == {"v11": f"~/renders/camp/{rel}/fig-1-v11/fig-1-v11.png", "v10": None},
              f"browser_path={info['browser_path']} reuse={reuse} log={log!r} "
              f"summary={summary['browser_path']} same={same} kept={kept} paths={paths}")
    except Exception as exc:  # noqa: BLE001 - writers without the fix
        check(names[0], False, f"{type(exc).__name__}: {exc}")
    finally:
        if saved is None:
            os.environ.pop("HOME", None)
        else:
            os.environ["HOME"] = saved
        shutil.rmtree(tmp, ignore_errors=True)
    found = []
    for p in sorted(list(HERE.glob("corpus*/**/*.json")) + list(HERE.glob("calibration/*.json"))):
        text = p.read_text(encoding="utf-8")
        if (home and f'"{home}/' in text) or HOME_PATH_VALUE.search(text):
            found.append(p.relative_to(HERE).as_posix())
    check(names[1], not found, f"{len(found)} file(s): {found[:3]}")


def t_render():
    renderer = types.SimpleNamespace(mermaid="11.17.2", browser="/cache/chrome-131/headless")
    entry = {"status": "rendered", "fence_sha256": "f", "dark": False, "instrument_sha256": "i",
             "renderer": {"mermaid": "11.17.2", "browser_path": "/cache/chrome-131/headless"}}
    moved = dict(entry, renderer=dict(entry["renderer"], browser_path="/cache/chrome-140/headless"))
    keep = render_corpus._reusable(entry, "f", False, renderer, "i")
    again = render_corpus._reusable(moved, "f", False, renderer, "i")
    runs = [{"grading": {"geometry": {"fig-1": {"v11": {"browser": b}}}}}
            for b in ("HeadlessChrome/131.0", "HeadlessChrome/140.0")]
    try:
        gf._browsers(runs)
        mixed = False
    except gf.InstrumentError:
        mixed = True
    check("TC-ME-41 a stored render measured by another browser is rendered again, and the "
          "grader refuses a corpus whose renders name two browsers (EI-26)",
          keep and not again and mixed
          and gf._browsers(runs[:1])["browser"] == "HeadlessChrome/131.0",
          f"same browser kept={keep} other browser kept={again} two browsers refused={mixed}")
    _home_rows()
    name = ("TC-ME-42 render_corpus refuses a render directory through a symlink and `..` into a "
            "work tree (exit 3, nothing created), and decides with "
            "`render_check.inside_git_work_tree`, the check of every render (SEC-04)")
    tmp = Path(tempfile.mkdtemp(prefix="mfe-link-"))
    saved = render_check.inside_git_work_tree
    try:
        repo = tmp / "repo"
        (repo / ".git").mkdir(parents=True)
        (repo / "sub").mkdir()
        (tmp / "elsewhere").mkdir()
        (tmp / "camp").mkdir()
        link = tmp / "elsewhere" / "link"
        try:
            os.symlink(repo / "sub", link)
        except (OSError, NotImplementedError) as exc:
            skip(name, f"no symlink here: {exc}")
            return
        sink = io.StringIO()
        with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
            code = render_corpus.main([str(tmp / "camp"), "--render-dir",
                                       str(link) + "/../renders"])
            render_check.inside_git_work_tree = lambda path: True
            spied = render_corpus.main([str(tmp / "camp"), "--render-dir",
                                        str(tmp / "elsewhere" / "renders")])
        check(name, code == 3 and not (repo / "renders").exists() and spied == 3,
              f"through the link: exit {code}, created={(repo / 'renders').exists()}; with the "
              f"shared check answering inside: exit {spied}")
    finally:
        render_check.inside_git_work_tree = saved
        shutil.rmtree(tmp, ignore_errors=True)


# =========================================================================== statistics


def t_stats():
    data = {"a": {"with_skill": [{"H": 0.9}, {"H": 0.8}, {"H": 1.0}],
                  "without_skill": [{"H": 0.5}, {"H": 0.4}, {"H": 0.6}]},
            "b": {"with_skill": [{"H": 0.7}, {"H": 0.7}, {"H": 0.6}],
                  "without_skill": [{"H": 0.7}, {"H": 0.5}, {"H": 0.6}]}}
    one = stats.cluster_bootstrap(data, ["H"], b=2000, seed=0)
    two = stats.cluster_bootstrap(data, ["H"], b=2000, seed=0)
    mean_based = stats.cluster_bootstrap(data, ["H"], b=200, seed=0, how="mean")
    check("TC-ME-20 the bootstrap is seeded; its delta is the mean over cases of the with_skill "
          "minus the without_skill median",
          one == two and one["H"]["delta"] == round(((0.9 - 0.5) + (0.7 - 0.6)) / 2, 6)
          and one["H"]["case_score"] == "median"
          and mean_based["H"]["delta"] == round((0.4 + (2.0 - 1.8) / 3) / 2, 6)
          and one["H"]["ci_low"] <= one["H"]["delta"] <= one["H"]["ci_high"], f"{one['H']}")
    check("TC-ME-20 median: odd and even counts, None skipped; a case score is the median of its "
          "repetitions",
          stats.median([0.2, 0.9, 0.4]) == 0.4 and stats.median([0.5, 0.25]) == 0.375
          and stats.median([None, 1.0]) == 1.0 and stats.median([]) is None
          and stats.case_score([{"H": 1.0}, {"H": 0.5}, {"H": 0.8}], "H") == 0.8,
          f"{stats.median([0.2, 0.9, 0.4])} {stats.median([0.5, 0.25])}")
    s = stats.sign_test([0.3, 0.2, 0.05, -0.2, 0.5, 0.4, 0.11, 0.0, 0.3, 0.25], 0.10)
    check("TC-ME-20 the sign test is exact and drops deltas within the noise floor",
          (s["ahead"], s["behind"], s["ties"]) == (7, 1, 2) and s["p_one_sided"] == 0.035156
          and s["p_two_sided"] == 0.070312, f"{s}")
    plain = stats.sign_test([0.3, 0.2, 0.05, -0.2, 0.5, 0.4, 0.11, 0.0, 0.3, 0.25])
    ev = _ev()
    tmp = Path(tempfile.mkdtemp(prefix="mfe-sign-"))
    try:                       # every case one check ahead: a case delta of 0.1, inside the floor
        rep = gf.build_report(_fake_campaign(ev, [6, 6, 6], [5, 5, 5], [10, 10, 10], [10, 10, 10]),
                              ev, NOTATION, tmp, {}, calibration=tmp / "absent-labels.json")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    sign = rep["sign_test"]
    h3 = next(c for c in rep["decision"]["criteria"] if c["id"] == "H3")["value"]
    sens = sign.get("sensitivity") or {}
    check("TC-ME-20 the sign test counts a case ahead above 0, as the README and H3 define it; "
          "the 0.10 floor, which the README does not register, is a sensitivity reading reported "
          "apart (R2-14)",
          (plain["ahead"], plain["behind"], plain["ties"]) == (8, 1, 1) and plain["floor"] == 0.0
          and sign["floor"] == 0.0 and sign["ahead"] == h3["ahead"] == 10
          and sens.get("floor") == 0.10 and sens.get("ahead") == 0 and sens.get("ties") == 10
          and "noise_floor" not in gf.DECISION_RULE,
          f"default={plain} report={ {k: sign.get(k) for k in ('floor', 'ahead', 'ties')} } "
          f"H3 ahead={h3['ahead']} sensitivity={sens}")
    check("TC-ME-20 Wilson intervals", stats.wilson(3, 10) == (0.107791, 0.603222)
          and stats.wilson(0, 0) == (None, None), f"{stats.wilson(3, 10)}")
    pairs = [(True, True), (True, True), (False, False), (False, False), (True, False), (False, False)]
    pr = stats.precision_recall(pairs)
    check("TC-ME-20 Cohen's kappa and per-class precision and recall",
          stats.cohen_kappa(pairs) == 0.666667 and pr["precision"] == 1.0 and pr["recall"] == 0.666667,
          f"kappa={stats.cohen_kappa(pairs)} {pr}")
    check("TC-ME-20 means use math.fsum", stats.fmean([0.1] * 10) == 0.1
          and stats.fmean([0.1] * 10) == math.fsum([0.1] * 10) / 10, repr(stats.fmean([0.1] * 10)))


#: The three matcher patterns before SEC2-09, kept as the oracle of their linear forms.
OLD_FILE_REF = r"[\w./-]*\w\.[A-Za-z]\w{0,7}:\d+(?:[-–]\d+)?"
OLD_INLINE_ARROW = r"\s*(?:-{1,2}>|─+[>►]|=>|→|⟶|➜|➔|⇒)\s*"
OLD_SEP = r"^\s*\|?\s*:?-{1,}:?\s*(?:\|\s*:?-{1,}:?\s*)*\|?\s*$"


def t_heuristics():
    """SEC2-09: the file-reference, inline-arrow and table-delimiter heuristics give what the
    old patterns gave, in linear time on a long line of model output."""
    names = ("TC-ME-47 the file-reference, inline-arrow and table-delimiter heuristics equal "
             "their old patterns on 9,000 seeded inputs (SEC2-09)",
             "TC-ME-47 a 30,000-character line of blanks, `a.` pairs or `─` reaches each of "
             "them in linear time: under 1 s for all six, where the old patterns took minutes "
             "(SEC2-09)")
    import random
    rng = random.Random(108)
    file_ref, arrow, sep = re.compile(OLD_FILE_REF), re.compile(OLD_INLINE_ARROW), re.compile(OLD_SEP)

    def draw(alphabet, most):
        return "".join(rng.choice(alphabet) for _ in range(rng.randint(0, most)))

    bad = []
    try:
        for _ in range(3000):
            t = draw("aZ_9./-–: é", 22)
            if fd.strip_file_refs(t) != file_ref.sub(" ", t):
                bad.append(("file reference", t))
            t = draw("ab -─>►=→⇒\t\xa0", 16)
            if fd.split_arrows(t) != arrow.split(t) \
                    or bool(fd._INLINE_ARROW.search(t)) != bool(arrow.search(t)):
                bad.append(("arrow", t))
            t = draw(" \t|:-x\xa0", 14)
            if bool(fd._SEP.match(t.strip())) != bool(sep.match(t)):
                bad.append(("delimiter row", t))
        check(names[0], not bad, f"{len(bad)} differ: {bad[:3]}")
    except Exception as exc:  # noqa: BLE001 - a matcher without the fix
        check(names[0], False, f"{type(exc).__name__}: {exc}")
    n = 30000
    t0 = time.perf_counter()
    fd.parse_tables("| a |\n" + " " * n + "-x\n")
    fd.parse_tables("| a |\n|" + " " * n + "-x\n")
    fd.parse_chains("a" + " " * n + "b")
    fd.parse_chains("─" * n)
    fd.extract_numbers("a." * (n // 2))
    fd.extract_numbers("a." * (n // 2) + ":1")
    took = time.perf_counter() - t0
    check(names[1], took < 1.0, f"{took:.3f} s")


# =========================================================================== committed campaigns


def _campaigns():
    return sorted(Path(p).parent for p in glob.glob(str(HERE / "corpus*" / "*" / "report.json")))


def t_committed():
    ev = _ev()
    camps = _campaigns()
    names = ("TC-ME-22 every committed report re-derives from its corpus",
             "TC-ME-23 every committed grading re-derives",
             "TC-ME-24 every committed benchmark pin holds")
    if not camps:
        for n in names:
            skip(n, "no committed campaign with a report.json under evals/corpus*")
        return
    drift_r, drift_g, drift_b = [], [], []
    for camp in camps:
        committed = json.loads((camp / "report.json").read_text(encoding="utf-8"))
        base = (committed.get("round") or {}).get("baseline_campaign")
        runs, report = gf.grade_corpus(camp, ev, NOTATION,
                                       baseline=camp.parent / base if base else None)
        if json.dumps(committed, sort_keys=True) != json.dumps(json.loads(json.dumps(report)), sort_keys=True):
            drift_r.append(camp.name)
        for r in runs:
            if r.get("baseline"):
                continue
            path = camp / r["rel"] / "grading.json"
            have = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None
            want = json.loads(json.dumps(r["grading"])) if r["grading"] is not None else None
            if have != want:
                drift_g.append(r["rel"])
        try:
            import verify_pin
            if (camp / "benchmark.json").is_file():
                with contextlib.redirect_stdout(io.StringIO()):
                    holds, _d = verify_pin.pin_holds(camp, camp / "benchmark.json")
                if not holds:
                    drift_b.append(camp.name)
            else:
                drift_b.append(f"{camp.name}: no benchmark.json")
        except (ImportError, SyntaxError, TypeError):     # absent, or for a newer Python
            drift_b.append("skill-creator did not import")
    check(names[0], not drift_r, f"drifted={drift_r}")
    check(names[1], not drift_g, f"drifted={drift_g[:5]}")
    check(names[2], not drift_b, f"broken={drift_b}")


def t_bundle_words():
    """TASK R1.5: the skill stays loadable — SKILL.md and each routed bundle under their limits."""
    words = run_evals.routing_words(run_evals.SKILL_DIR)
    skill_words = run_evals.word_count((Path(run_evals.SKILL_DIR) / "SKILL.md").read_text(encoding="utf-8"))
    over = {k: v for k, v in words.items()
            if not isinstance(v, int) or v >= run_evals.BUNDLE_WORD_LIMIT}
    check(f"TC-ME-32 SKILL.md holds fewer than {run_evals.SKILL_WORD_LIMIT} words and each routed "
          f"bundle fewer than {run_evals.BUNDLE_WORD_LIMIT} (TASK R1.5)",
          skill_words < run_evals.SKILL_WORD_LIMIT and not over and len(words) >= 7,
          f"SKILL.md {skill_words}; " + ", ".join(f"{k} {v}" for k, v in words.items()))


def t_envelope_error():
    """A failed attempt records the cause the CLI gives, never its subtype alone."""
    cli = {"is_error": True, "subtype": "success", "api_error_status": 529,
           "result": "API Error: Overloaded", "total_cost_usd": 0}
    got = run_evals.envelope_error(cli)
    check("TC-ME-33 a CLI error envelope is recorded with its API status and result text; an "
          "envelope without an error is an empty answer",
          "529" in got and "Overloaded" in got
          and run_evals.envelope_error({"is_error": False, "result": ""}) == "empty answer"
          and run_evals.envelope_error({"is_error": True, "error": "timed out"}) == "timed out",
          got)


def t_zero():
    check("TC-ME-25 the battery spawned no agent", SPAWN.calls == 0, f"spawn called {SPAWN.calls} time(s)")
    check("TC-ME-26 the battery rendered nothing", RENDER.calls == 0, f"render called {RENDER.calls} time(s)")


# =========================================================================== main


def main() -> int:
    for fn in (t_api, t_set_shape, t_prompts, t_isolation, t_keys, t_mirage, t_fixtures,
               t_fidelity_rules, t_fixes, t_unfenced, t_ascii_labels, t_duplicates, t_captions,
               t_gantt_dates, t_parts, t_number_subjects, t_invented_ends, t_ascii_budget,
               t_fences, t_forms, t_grader, t_sequence_legend,
               t_corpus, t_scores, t_report_completeness, t_calibration, t_provenance,
               t_amendment_a1, t_executor, t_render, t_cli, t_stats, t_heuristics, t_committed,
               t_bundle_words, t_envelope_error, t_zero):
        try:
            fn()
        except Exception as exc:  # noqa: BLE001 - a raising test is a broken instrument
            INSTRUMENT.append(fn.__name__)
            check(f"{fn.__name__} raised", False, f"{type(exc).__name__}: {exc}")
    total = len(RESULTS) + 1      # this row counts itself
    check("TC-ME-27 the battery ran every row it declares", total == EXPECTED_CASES,
          f"ran={total} declared={EXPECTED_CASES}")
    for name, status, detail in RESULTS:
        line = f"{status:4s}  {name}"
        if status != "PASS" and detail:
            line += f"  — {detail}"
        print(line)
    failed = [r for r in RESULTS if r[1] == "FAIL"]
    skipped = [r for r in RESULTS if r[1] == "SKIP"]
    print(f"\n{len(RESULTS) - len(failed) - len(skipped)} passed, {len(failed)} failed, "
          f"{len(skipped)} skipped of {len(RESULTS)} rows (0 agents spawned, 0 renders)")
    if INSTRUMENT:
        print(f"instrument error in: {', '.join(INSTRUMENT)}")
        return 2
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
