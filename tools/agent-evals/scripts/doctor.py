#!/usr/bin/env python3
"""Static health check for the whole agent + skill collection.

Fast, free, no LLM — the always-on complement to the (slow, token-spending)
routing and body evals. Run it before you bother paying for an eval, and in CI.

Checks per definition:
  - frontmatter present, with `name` and `description`            [ERROR]
  - `name` matches its location (agent filename / skill dir)      [ERROR]
  - bundled references exist (references|reference|scripts|assets) [ERROR]
  - description present and substantive, with trigger context     [WARN]
  - body within the progressive-disclosure budget                 [WARN]
  - over-reliance on rigid ALL-CAPS NEVER/ALWAYS/MUST              [WARN]

Across the collection:
  - duplicate `name`s (install links by basename -> silent clobber)[ERROR]
  - high description overlap between definitions (routing/trigger
    conflict risk — catch it statically before a routing eval)    [WARN]

Exit code: 1 if any ERROR, else 0 (CI-ready). Python 3.9; stdlib only.
"""

import argparse
import os
import re
import sys
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from trigger_eval import _fm_value, parse_agent_md  # noqa: E402

BODY_SOFT_LIMIT = 500
DESC_MIN_CHARS = 80
RIGID = ("NEVER", "ALWAYS", "MUST")
RIGID_LIMIT = 6
REF_DIRS = ("references", "reference", "scripts", "assets")
OVERLAP_THRESHOLD = 0.40
# Agents that exist outside .claude/agents/ and so must not be flagged as stale.
BUILTIN_AGENTS = {"general-purpose", "explore", "plan", "claude", "subagent",
                  "statusline-setup", "output-style-setup"}
# High-precision "this is an agent invocation" patterns; each captures the name.
AGENT_REF_RE = re.compile(
    r"`([a-z][a-z0-9-]{2,})`\s+(?:sub-?agents?|agents?)\b"
    r"|spawn\s+(?:a|an)\s+`?([a-z][a-z0-9-]{2,})`?\s+(?:sub-?agents?|agents?)"
    r"|subagent[_-]?type\s*[:=]\s*[\"'`]?([a-z][a-z0-9-]{2,})")
STOPWORDS = set("""the a an and or of to for with when use used using this that
these those your you user users it its on in at by as is are be will would can
should from into about across via per each any all both new make sure want need
skill skills agent agents claude code task tasks work works working help helps
output outputs file files document documents create creates creating write writes
writing run runs based provide provides handle handles""".split())


class Finding:
    def __init__(self, level: str, item: str, msg: str):
        self.level, self.item, self.msg = level, item, msg


def discover(repo: str) -> List[dict]:
    items = []
    agents_dir = os.path.join(repo, ".claude", "agents")
    if os.path.isdir(agents_dir):
        for fn in sorted(os.listdir(agents_dir)):
            if fn.endswith(".md"):
                path = os.path.join(agents_dir, fn)
                name, desc, body = parse_agent_md(path)
                items.append({"kind": "agent", "path": path, "dir": agents_dir,
                              "loc_name": fn[:-3], "name": name, "desc": desc, "body": body})
    for root in (os.path.join(repo, ".claude", "skills"), os.path.join(repo, "skills")):
        if not os.path.isdir(root):
            continue
        for dirpath, _, files in os.walk(root):
            if "SKILL.md" in files:
                path = os.path.join(dirpath, "SKILL.md")
                name, desc, body = parse_agent_md(path)
                items.append({"kind": "skill", "path": path, "dir": dirpath,
                              "loc_name": os.path.basename(dirpath), "name": name,
                              "desc": desc, "body": body})
    return items


def _rel(repo: str, path: str) -> str:
    return os.path.relpath(path, repo)


def build_file_index(repo: str) -> List[str]:
    skip = {".git", "bin", "obj", "node_modules", ".venv", "venv", "__pycache__"}
    paths = []
    for dirpath, dirs, files in os.walk(repo):
        dirs[:] = [d for d in dirs if d not in skip]
        for f in files:
            paths.append(os.path.join(dirpath, f))
    return paths


def check_item(repo: str, item: dict, file_index: List[str], valid_agents: set) -> List[Finding]:
    out = []
    rel = _rel(repo, item["path"])
    name, desc, body = item["name"], item["desc"], item["body"]

    if not name:
        out.append(Finding("ERROR", rel, "frontmatter missing `name`"))
    elif name != item["loc_name"]:
        out.append(Finding("ERROR", rel, "name `{}` != {} `{}` (install links by "
                           "location)".format(name, "filename" if item["kind"] == "agent"
                                               else "directory", item["loc_name"])))
    if not desc:
        out.append(Finding("ERROR", rel, "frontmatter missing `description` (the trigger)"))
    else:
        if len(desc) < DESC_MIN_CHARS:
            out.append(Finding("WARN", rel, "description is short ({} chars) — say what it "
                               "does AND when to use it".format(len(desc))))
        if not re.search(r"(?i)\bwhen\b|\btrigger\b|keywords?:|\buse (this|it|for|at|after|"
                         r"before|to)\b", desc):
            out.append(Finding("WARN", rel, "description states no usage context (no 'when…' / "
                               "'use for…' / 'trigger' / 'keywords:') — may under-trigger"))

    # bundled reference existence: a ref is only genuinely broken if the file
    # exists NOWHERE in the repo. Resolving relative to the def dir alone would
    # false-flag valid cross-pointers (e.g. "see references/x.md in the Y skill").
    seen = set()
    for m in re.finditer(r"(?<![\w./])((?:%s)/[\w./-]+\.\w+)" % "|".join(REF_DIRS), body):
        ref = m.group(1)
        if ref in seen:
            continue
        seen.add(ref)
        local = os.path.isfile(os.path.join(item["dir"], ref))
        anywhere = local or any(p.replace(os.sep, "/").endswith("/" + ref) for p in file_index)
        if not anywhere:
            out.append(Finding("ERROR", rel, "references a file that exists nowhere in the "
                               "repo: `{}`".format(ref)))

    # references to agents that no longer exist (e.g. reorg-deleted subagents)
    seen_agents = set()
    for m in AGENT_REF_RE.finditer(body):
        ref = (m.group(1) or m.group(2) or m.group(3) or "").lower()
        if not ref or ref in seen_agents:
            continue
        seen_agents.add(ref)
        if ref not in valid_agents:
            out.append(Finding("WARN", rel, "references a subagent that doesn't exist in "
                               ".claude/agents/: `{}`".format(ref)))

    # body length
    n = len([l for l in body.splitlines() if l.strip()])
    if n > BODY_SOFT_LIMIT:
        out.append(Finding("WARN", rel, "body {} non-blank lines (> {}); push detail into "
                           "references/".format(n, BODY_SOFT_LIMIT)))

    # rigid directives
    hits = sum(len(re.findall(r"\b%s\b" % w, body)) for w in RIGID)
    if hits > RIGID_LIMIT:
        out.append(Finding("WARN", rel, "{} ALL-CAPS NEVER/ALWAYS/MUST — prefer explaining "
                           "the why".format(hits)))
    return out


def _terms(desc: str) -> set:
    toks = re.findall(r"[a-zA-Z][a-zA-Z0-9-]{3,}", desc.lower())
    return {t for t in toks if t not in STOPWORDS}


def cross_checks(repo: str, items: List[dict]) -> List[Finding]:
    out = []
    # duplicate names
    by_name: Dict[str, List[dict]] = {}
    for it in items:
        if it["name"]:
            by_name.setdefault(it["name"], []).append(it)
    for nm, group in sorted(by_name.items()):
        if len(group) > 1:
            out.append(Finding("ERROR", nm, "duplicate name across: {}".format(
                ", ".join(_rel(repo, g["path"]) for g in group))))

    # description overlap (routing/trigger conflict risk)
    termed = [(it, _terms(it["desc"])) for it in items if it["desc"]]
    pairs = []
    for i in range(len(termed)):
        for j in range(i + 1, len(termed)):
            a, ta = termed[i]
            b, tb = termed[j]
            if not ta or not tb:
                continue
            jac = len(ta & tb) / len(ta | tb)
            if jac >= OVERLAP_THRESHOLD:
                pairs.append((jac, a, b, ta & tb))
    for jac, a, b, shared in sorted(pairs, key=lambda p: p[0], reverse=True)[:12]:
        out.append(Finding("WARN", "overlap", "{} ~ {} (Jaccard {:.2f}; shared: {})".format(
            a["name"] or _rel(repo, a["path"]), b["name"] or _rel(repo, b["path"]), jac,
            ", ".join(sorted(shared)[:6]))))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Static health check for agents + skills.")
    ap.add_argument("--repo", default=".", help="Repo root (default: cwd)")
    ap.add_argument("--warnings-as-errors", action="store_true",
                    help="Exit nonzero on WARN too")
    args = ap.parse_args()
    repo = os.path.abspath(args.repo)

    items = discover(repo)
    if not items:
        print("no agents or skills found under {}".format(repo), file=sys.stderr)
        return 2

    file_index = build_file_index(repo)
    valid_agents = BUILTIN_AGENTS | {it["name"].lower() for it in items
                                     if it["kind"] == "agent" and it["name"]}
    findings: List[Finding] = []
    for it in items:
        findings.extend(check_item(repo, it, file_index, valid_agents))
    findings.extend(cross_checks(repo, items))

    errors = [f for f in findings if f.level == "ERROR"]
    warns = [f for f in findings if f.level == "WARN"]

    for level, bucket in (("ERROR", errors), ("WARN", warns)):
        for f in bucket:
            print("[{}] {}: {}".format(level, f.item, f.msg))

    n_agents = sum(1 for it in items if it["kind"] == "agent")
    n_skills = len(items) - n_agents
    print("\nchecked {} agents + {} skills — {} error(s), {} warning(s)".format(
        n_agents, n_skills, len(errors), len(warns)))
    return 1 if (errors or (args.warnings_as_errors and warns)) else 0


if __name__ == "__main__":
    sys.exit(main())
