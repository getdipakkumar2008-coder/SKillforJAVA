#!/usr/bin/env python3
"""Trigger tests for the skill descriptions (standard library only).

Subcommands
  lint      validate tests/triggers/cases.json against the skills, show coverage and
            description overlap (offline, deterministic)
  lexical   rank skills for every prompt with a TF-IDF similarity of the prompt against
            the skill descriptions (offline). This is a HEURISTIC proxy for activation: it
            shows whether descriptions are discriminable, not what an agent will really do.
  claude    REAL test: run each prompt in a headless Claude Code session in a scratch
            project that contains only these skills, and record which skills the agent
            actually invoked. Spends API credits; requires --yes.

Examples
  python scripts/check-triggers.py lint
  python scripts/check-triggers.py lexical --top 3
  python scripts/check-triggers.py claude --ids core-01,sec-01,neg-01 --yes
  python scripts/check-triggers.py claude --yes --jobs 3 --budget 0.30

Semantics of a case (see tests/triggers/cases.json)
  expect_all  every listed skill must activate
  expect_any  at least one listed skill must activate
  forbid      none of the listed skills may activate
  forbid_all  none of the skills in this repository may activate (non-Java prompts)
  Activation of java-engineering-core is always acceptable. Other activations are reported
  as "extra" (possible over-activation) but do not fail a case.
"""
import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / ".claude" / "skills"
CASES_FILE = ROOT / "tests" / "triggers" / "cases.json"
CORE = "java-engineering-core"
STOP = set("a an and are as at be but by can for from has have how i if in into is it its me my no not of on or our so that the their then there this to up use used using we what when where which while will with without you your do does did get got make out about also any all each other per via over under should would could these those they them than more most such".split())


# ---------------------------------------------------------------- loading
def load_skills():
    skills = {}
    for d in sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir()):
        f = d / "SKILL.md"
        if not f.exists():
            continue
        lines = f.read_text(encoding="utf-8").splitlines()
        desc = ""
        for ln in lines[1:4]:
            if ln.startswith("description:"):
                desc = ln[len("description:"):].strip()
        skills[d.name] = desc
    return skills


def load_cases(path=CASES_FILE):
    return json.loads(Path(path).read_text(encoding="utf-8"))["cases"]


# ---------------------------------------------------------------- text model
def tokens(text):
    out = []
    for t in re.findall(r"[a-z0-9]+", text.lower()):
        if t in STOP or len(t) < 2:
            continue
        for suf in ("ies", "es", "s"):
            if len(t) > 4 and t.endswith(suf):
                t = t[: -len(suf)] + ("y" if suf == "ies" else "")
                break
        out.append(t)
    return out


def build_model(skills):
    docs = {n: tokens(n.replace("-", " ") + " " + d) for n, d in skills.items()}
    df = {}
    for toks in docs.values():
        for t in set(toks):
            df[t] = df.get(t, 0) + 1
    n = len(docs)
    idf = {t: math.log((1 + n) / (1 + c)) + 1 for t, c in df.items()}
    return docs, idf


def vec(toks, idf):
    tf = {}
    for t in toks:
        if t in idf:
            tf[t] = tf.get(t, 0) + 1
    v = {t: (1 + math.log(c)) * idf[t] for t, c in tf.items()}
    norm = math.sqrt(sum(x * x for x in v.values())) or 1.0
    return {t: x / norm for t, x in v.items()}


def cos(a, b):
    if len(a) > len(b):
        a, b = b, a
    return sum(x * b.get(t, 0.0) for t, x in a.items())


# ---------------------------------------------------------------- evaluation
def evaluate(case, activated, all_skills, gate=False):
    """Return (passed, reasons). activated = set of skill names invoked/ranked.

    gate=True (bootstrap mode): the core skill must activate for every Java prompt (cases with
    only "forbid", or marked "no_gate" such as purely conceptual questions, are exempt), and for
    cases marked "gate_only" (simple tasks) the specialised-skill expectations are not required.
    """
    reasons = []
    act = set(activated)
    if case.get("forbid_all"):
        bad = act & set(all_skills)
        if bad:
            reasons.append("activated for a non-Java prompt: " + ", ".join(sorted(bad)))
    else:
        if gate and CORE not in act and (case.get("expect_all") or case.get("expect_any")) and not case.get("no_gate"):
            reasons.append("core skill java-engineering-core did not load (gate)")
        if not (gate and case.get("gate_only")):
            miss = [s for s in case.get("expect_all", []) if s not in act]
            if miss:
                reasons.append("missing required: " + ", ".join(miss))
            anyl = [x for x in case.get("expect_any", []) if not (gate and x == CORE)]
            if anyl and not (act & set(anyl)) and not (gate and CORE in act and CORE in case.get("expect_any", [])):
                reasons.append("none of expected activated: " + ", ".join(anyl))
        bad = act & set(case.get("forbid", []))
        if bad:
            reasons.append("forbidden activated: " + ", ".join(sorted(bad)))
    return (not reasons), reasons


def expected_set(case):
    return set(case.get("expect_all", [])) | set(case.get("expect_any", []))


# ---------------------------------------------------------------- lint
def cmd_lint(args):
    skills = load_skills()
    cases = load_cases(args.cases)
    problems = []
    ids = [c["id"] for c in cases]
    for i in {x for x in ids if ids.count(x) > 1}:
        problems.append(f"duplicate case id {i}")
    for c in cases:
        for key in ("expect_all", "expect_any", "forbid"):
            for s in c.get(key, []):
                if s not in skills:
                    problems.append(f"{c['id']}: unknown skill {s}")
        if not (c.get("forbid_all") or c.get("forbid") or c.get("expect_all") or c.get("expect_any")):
            problems.append(f"{c['id']}: needs expect_all, expect_any, forbid or forbid_all")
    # coverage: every skill expected by >= 2 cases
    cover = {s: 0 for s in skills}
    for c in cases:
        for s in expected_set(c):
            if s in cover:
                cover[s] += 1
    print(f"skills: {len(skills)}  cases: {len(cases)}  negatives: {sum(1 for c in cases if c.get('forbid_all') or str(c['id']).startswith('neg'))}")
    thin = [s for s, n in cover.items() if n < 2 and s != CORE]
    print("coverage (cases that expect each skill):")
    for s, n in sorted(cover.items(), key=lambda x: x[1]):
        print(f"  {n:2d}  {s}")
    for s in thin:
        problems.append(f"skill {s} is expected by fewer than 2 cases")
    # description overlap
    docs, idf = build_model(skills)
    vecs = {n: vec(t, idf) for n, t in docs.items()}
    names = sorted(skills)
    pairs = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            pairs.append((cos(vecs[a], vecs[b]), a, b))
    pairs.sort(reverse=True)
    print(f"\nmost similar description pairs (cosine, higher = more overlap risk; warn > {args.overlap}):")
    for sc, a, b in pairs[:8]:
        flag = "  <-- overlap" if sc > args.overlap else ""
        print(f"  {sc:.2f}  {a}  ~  {b}{flag}")
    over = [p for p in pairs if p[0] > args.overlap]
    for sc, a, b in over:
        print(f"WARN: descriptions of {a} and {b} overlap heavily ({sc:.2f})")
    for p in problems:
        print("PROBLEM:", p)
    print("\nlint:", "FAILED" if problems else "OK")
    return 1 if problems else 0


# ---------------------------------------------------------------- lexical
def cmd_lexical(args):
    skills = load_skills()
    cases = load_cases(args.cases)
    docs, idf = build_model(skills)
    svecs = {n: vec(t, idf) for n, t in docs.items()}
    fails = skipped = 0
    for c in cases:
        pv = vec(tokens(c["prompt"]), idf)
        ranked = sorted(((cos(pv, v), n) for n, v in svecs.items()), reverse=True)
        best = ranked[0][0]
        # candidates: within the top-k, with a non-trivial score relative to the best match
        cand = [(s_, n) for s_, n in ranked[: args.top] if s_ >= args.min_score and s_ >= 0.4 * best]
        top = [n for _, n in cand]
        top_scores = ", ".join(f"{n}={s_:.2f}" for s_, n in ranked[: args.top])
        if c.get("forbid_all"):
            skipped += 1
            print(f"SKIP  {c['id']:9s} {top_scores}   (non-Java prompts need a real model; see 'claude')")
            continue
        ok, reasons = evaluate(c, set(top), skills)
        if c.get("expect_all"):
            wide = {n for _, n in ranked[: args.top + 2]}
            reasons = [r for r in reasons if not r.startswith("missing required")]
            miss = [s_ for s_ in c["expect_all"] if s_ not in wide]
            if miss:
                reasons.append("missing required (top %d): %s" % (args.top + 2, ", ".join(miss)))
            ok = not reasons
        fails += 0 if ok else 1
        print(f"{'PASS' if ok else 'FAIL'}  {c['id']:9s} {top_scores}" + ("" if ok else "   <- " + "; ".join(reasons)))
    total = len(cases) - skipped
    print(f"\nlexical heuristic: {total - fails}/{total} scored cases consistent with expectations (top {args.top}); {skipped} negative case(s) skipped.")
    print("This is a similarity proxy, not real activation. Use the 'claude' subcommand for that.")
    return 1 if (fails and args.strict) else 0


# ---------------------------------------------------------------- claude (real)
FIXTURE_DIR = ROOT / "tests" / "triggers" / "fixture"
BOOTSTRAP = ROOT / "adapters" / "claude" / "CLAUDE.md"


FIXTURES = {"spring": ROOT / "tests" / "triggers" / "fixture", "android": ROOT / "tests" / "triggers" / "fixture-android"}
EXTRAS_DIR = ROOT / "tests" / "triggers" / "extras"


def prepare_workdir(base, fixture="spring", bootstrap=False, dirty=False):
    """Create a scratch project: fixture + skills (+ CLAUDE.md) as a git repository.
    dirty=True adds an uncommitted file so review prompts have something to review."""
    if base:
        Path(base).mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="trigger-", dir=base))
    src = FIXTURES.get(fixture)
    if src and src.is_dir():
        shutil.copytree(src, work, dirs_exist_ok=True)
    else:
        (work / "README.md").write_text("Scratch project for skill trigger tests.\n", encoding="utf-8")
    shutil.copytree(SKILLS_DIR, work / ".claude" / "skills")
    if bootstrap:
        shutil.copyfile(BOOTSTRAP, work / "CLAUDE.md")
    git = shutil.which("git")
    if git:
        env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
        for a in (["init", "-q"], ["add", "-A"], ["commit", "-qm", "initial"]):
            subprocess.run([git] + a, cwd=work, env=env, capture_output=True)
    if dirty:
        extra = EXTRAS_DIR / "PromoController.java.txt"
        dst = work / "src" / "main" / "java" / "com" / "example" / "demo" / "web" / "PromoController.java"
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(extra, dst)
    return work


def parse_stream(stdout):
    invoked, cost, err = [], None, None
    for line in stdout.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        if ev.get("type") == "assistant":
            for blk in (ev.get("message", {}).get("content") or []):
                if isinstance(blk, dict) and blk.get("type") == "tool_use" and blk.get("name") == "Skill":
                    inp = blk.get("input") or {}
                    name = inp.get("skill") or inp.get("name") or inp.get("command")
                    if name:
                        invoked.append(str(name).split(":")[-1].lstrip("/"))
        elif ev.get("type") == "result":
            cost = ev.get("total_cost_usd", cost)
            if ev.get("is_error"):
                err = str(ev.get("result"))[:200]
    return invoked, cost, err


ALL_TOOLS = ["Bash", "Edit", "Write", "Read", "Glob", "Grep", "WebFetch", "WebSearch", "Agent"]


def run_one(case, work, args, claude_bin):
    allowed = ["Skill"] + [t for t in args.tools.split(",") if t]
    cmd = [claude_bin, "-p", case["prompt"], "--output-format", "stream-json", "--verbose",
           "--no-session-persistence", "--setting-sources", "project",
           "--allowedTools", *allowed,
           "--disallowedTools", *[t for t in ALL_TOOLS if t not in allowed]]
    if args.budget and args.budget > 0:
        cmd += ["--max-budget-usd", str(args.budget)]
    if args.model:
        cmd += ["--model", args.model]
    t0 = time.time()
    try:
        p = subprocess.run(cmd, cwd=work, capture_output=True, text=True, timeout=args.timeout, encoding="utf-8", errors="replace")
        invoked, cost, err = parse_stream(p.stdout)
        if args.transcripts:
            td = Path(args.transcripts)
            td.mkdir(parents=True, exist_ok=True)
            (td / f"{case['id']}.jsonl").write_text(p.stdout, encoding="utf-8")
        if p.returncode != 0 and not invoked and not err:
            err = (p.stderr or "")[:200] or f"exit {p.returncode}"
    except subprocess.TimeoutExpired:
        invoked, cost, err = [], None, "timeout"
    return {"id": case["id"], "invoked": invoked, "cost": cost, "error": err, "seconds": round(time.time() - t0, 1)}


def cmd_claude(args):
    claude_bin = shutil.which("claude")
    if not claude_bin:
        print("claude CLI not found on PATH")
        return 2
    skills = load_skills()
    cases = load_cases(args.cases)
    if args.ids:
        want = set(args.ids.split(","))
        cases = [c for c in cases if c["id"] in want]
        unknown = want - {c["id"] for c in cases}
        if unknown:
            print("unknown case ids:", ", ".join(sorted(unknown)))
            return 2
    if args.limit:
        cases = cases[: args.limit]
    if args.batch:
        size = args.batch_size
        nbatches = (len(cases) + size - 1) // size
        if args.batch < 1 or args.batch > nbatches:
            print(f"--batch must be between 1 and {nbatches} (batch size {size})")
            return 2
        cases = cases[(args.batch - 1) * size: args.batch * size]
        print(f"batch {args.batch} of {nbatches} (size {size}): " + ", ".join(c["id"] for c in cases))
    cap_text = "no cap" if not args.budget else "capped at $%.2f per case" % args.budget
    print(f"{len(cases)} case(s); {cap_text}; model: {args.model or 'default'}; "
          f"tools: Skill+{args.tools or 'none'}; fixture: {'no' if args.no_fixture else 'yes'}; bootstrap CLAUDE.md: {'yes' if args.bootstrap else 'no'}")
    if not args.yes:
        print("This spends API credits. Re-run with --yes to proceed.")
        return 0
    keys = sorted({("none" if args.no_fixture else c.get("fixture", "spring"), bool(c.get("dirty"))) for c in cases})
    works = {k: prepare_workdir(args.workdir, fixture=k[0], bootstrap=args.bootstrap, dirty=k[1]) for k in keys}
    for k, w in works.items():
        print(f"scratch project {k}: {w}")
    try:
        with ThreadPoolExecutor(max_workers=args.jobs) as ex:
            results = list(ex.map(lambda c: run_one(c, works[("none" if args.no_fixture else c.get("fixture", "spring"), bool(c.get("dirty")))], args, claude_bin), cases))
    finally:
        if not args.keep:
            for w in works.values():
                shutil.rmtree(w, ignore_errors=True)
    by_id = {c["id"]: c for c in cases}
    fails = errors = 0
    total_cost = 0.0
    recall = {}
    for r in results:
        c = by_id[r["id"]]
        mine = [s for s in r["invoked"] if s in skills]
        if r["error"] and not r["invoked"]:
            errors += 1
            print(f"ERROR {r['id']:9s} {r['error']}")
            continue
        ok, reasons = evaluate(c, set(mine), skills, gate=args.bootstrap)
        extra = sorted(set(mine) - expected_set(c) - {CORE})
        note = ""
        if args.bootstrap and c.get("gate_only"):
            spec = sorted(expected_set(c) - {CORE})
            note = "  [gate_only: specialised " + ("loaded" if set(spec) & set(mine) else "not loaded (allowed): " + ",".join(spec)) + "]"
        fails += 0 if ok else 1
        total_cost += r["cost"] or 0.0
        for s in expected_set(c):
            recall.setdefault(s, [0, 0])
            recall[s][1] += 1
            recall[s][0] += 1 if s in mine else 0
        line = f"{'PASS' if ok else 'FAIL'}  {r['id']:9s} invoked={mine or '-'}"
        if extra and not c.get("forbid_all"):
            line += f"  extra={extra}"
        line += note
        if not ok:
            line += "  <- " + "; ".join(reasons)
        print(line)
    done = len(results) - errors
    print(f"\nreal activation: {done - fails}/{done} passed, {errors} error(s), cost ~${total_cost:.2f}")
    if recall:
        print("per-skill recall (cases listing the skill as expected, where it was invoked):")
        for s, (a, b) in sorted(recall.items()):
            print(f"  {a}/{b}  {s}")
    out = Path(args.out) if args.out else ROOT / "tests" / "triggers" / "results" / f"{time.strftime('%Y%m%d-%H%M%S')}-claude.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"model": args.model, "tools": args.tools, "fixture": not args.no_fixture, "bootstrap": args.bootstrap, "results": results}, indent=2), encoding="utf-8")
    print("results written to", out)
    return 1 if (fails or errors) else 0


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cases", default=str(CASES_FILE))
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("lint"); p.add_argument("--overlap", type=float, default=0.45); p.set_defaults(fn=cmd_lint)
    p = sub.add_parser("lexical"); p.add_argument("--top", type=int, default=3); p.add_argument("--min-score", type=float, default=0.08); p.add_argument("--strict", action="store_true"); p.set_defaults(fn=cmd_lexical)
    p = sub.add_parser("claude")
    p.add_argument("--ids", help="comma-separated case ids"); p.add_argument("--limit", type=int)
    p.add_argument("--batch", type=int, help="run only batch N (1-based) of the selected cases"); p.add_argument("--batch-size", type=int, default=5)
    p.add_argument("--model"); p.add_argument("--jobs", type=int, default=2)
    p.add_argument("--budget", type=float, default=0.0, help="max USD per case (0 = no cap; a cap made the agent skip skills \"to stay within budget\" in testing)")
    p.add_argument("--timeout", type=int, default=180); p.add_argument("--workdir", default=None)
    p.add_argument("--tools", default="Read,Glob,Grep", help="comma-separated extra tools besides Skill (default: read-only Read,Glob,Grep; use '' for Skill only)")
    p.add_argument("--no-fixture", action="store_true", help="use an empty scratch project instead of tests/triggers/fixture")
    p.add_argument("--bootstrap", action="store_true", help="include adapters/claude/CLAUDE.md in the scratch project")
    p.add_argument("--transcripts", help="directory to save the raw stream-json of every case (for diagnosis)")
    p.add_argument("--keep", action="store_true"); p.add_argument("--out"); p.add_argument("--yes", action="store_true")
    p.set_defaults(fn=cmd_claude)
    args = ap.parse_args()
    sys.exit(args.fn(args))


if __name__ == "__main__":
    main()
