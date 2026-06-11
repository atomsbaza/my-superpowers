#!/usr/bin/env python3
"""Lint an agent definition against the improvement-philosophy guidelines.

This is a fast, deterministic pre-check — it does NOT replace running evals.
It flags the cheap-to-detect smells the philosophy warns about so you fix them
before spending tokens on an A/B run:

- missing/!weak frontmatter (name, description)
- description that lists no trigger context (under-triggering risk)
- body longer than the progressive-disclosure budget
- over-reliance on rigid ALL-CAPS MUST/NEVER/ALWAYS instead of explaining why

Exit code is always 0 (advisory). Python 3.9 compatible.
"""

import argparse
import re
import sys
from typing import List, Tuple

BODY_SOFT_LIMIT = 500          # lines; skill-creator's progressive-disclosure budget
DESCRIPTION_MIN_CHARS = 80
RIGID_WORDS = ("NEVER", "ALWAYS", "MUST")


def _split_frontmatter(text: str) -> Tuple[str, str]:
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            return parts[1], parts[2]
    return "", text


def _frontmatter_value(fm: str, key: str) -> str:
    # handles "key: value" and YAML block scalars "key: >" / "key: |"
    m = re.search(r"(?m)^" + re.escape(key) + r":\s*(.*)$", fm)
    if not m:
        return ""
    first = m.group(1).strip()
    if first in (">", "|", ">-", "|-"):
        block = []
        capture = False
        for line in fm.splitlines():
            if re.match(r"^" + re.escape(key) + r":\s*[>|]", line):
                capture = True
                continue
            if capture:
                if re.match(r"^\S", line):  # next top-level key
                    break
                block.append(line.strip())
        return " ".join(b for b in block if b)
    return first


def lint(path: str) -> List[Tuple[str, str]]:
    """Return list of (level, message). level in {INFO, WARN}."""
    findings = []
    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read()
    fm, body = _split_frontmatter(text)

    if not fm:
        findings.append(("WARN", "No YAML frontmatter found — name/description required."))
        return findings

    name = _frontmatter_value(fm, "name")
    desc = _frontmatter_value(fm, "description")

    if not name:
        findings.append(("WARN", "Frontmatter missing `name`."))
    if not desc:
        findings.append(("WARN", "Frontmatter missing `description` — this is the primary "
                                 "triggering mechanism."))
    else:
        if len(desc) < DESCRIPTION_MIN_CHARS:
            findings.append(("WARN", "Description is short ({} chars). Include both WHAT it "
                                     "does and WHEN to use it.".format(len(desc))))
        has_trigger = bool(re.search(r"(?i)use (this|when)|trigger|keywords?:", desc))
        if not has_trigger:
            findings.append(("WARN", "Description lists no trigger context (no 'use when…', "
                                     "'trigger', or 'keywords:'). Risks under-triggering."))

    body_lines = [l for l in body.splitlines()]
    n_lines = len([l for l in body_lines if l.strip()])
    if n_lines > BODY_SOFT_LIMIT:
        findings.append(("WARN", "Body is {} non-blank lines (> {} soft limit). Move detail "
                                 "into references/ and point to it.".format(n_lines, BODY_SOFT_LIMIT)))

    rigid_hits = []
    for i, line in enumerate(body_lines, 1):
        for w in RIGID_WORDS:
            # whole-word, all-caps occurrences
            for _ in re.finditer(r"\b" + w + r"\b", line):
                rigid_hits.append((i, w, line.strip()))
    if len(rigid_hits) > 6:
        sample = "; ".join('L{}:{}'.format(h[0], h[1]) for h in rigid_hits[:5])
        findings.append(("WARN", "{} rigid directives (NEVER/ALWAYS/MUST). Prefer explaining "
                                 "*why* over absolute rules. e.g. {} …".format(len(rigid_hits), sample)))
    elif rigid_hits:
        findings.append(("INFO", "{} rigid directive(s) — fine in moderation; make sure each "
                                 "carries its reasoning.".format(len(rigid_hits))))

    if not findings:
        findings.append(("INFO", "No issues flagged. (Lint is advisory — still run evals.)"))
    return findings


def main() -> int:
    ap = argparse.ArgumentParser(description="Lint agent definition(s).")
    ap.add_argument("paths", nargs="+", help="Agent .md file(s)")
    args = ap.parse_args()
    for path in args.paths:
        print("\n== {} ==".format(path))
        try:
            for level, msg in lint(path):
                print("  [{}] {}".format(level, msg))
        except OSError as exc:
            print("  [WARN] could not read: {}".format(exc))
    return 0


if __name__ == "__main__":
    sys.exit(main())
