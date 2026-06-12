#!/usr/bin/env python3
"""Routing/discrimination eval: when Claude delegates, does the RIGHT agent win?

What this measures (and why the earlier version was wrong)
----------------------------------------------------------
An agent's `description` competes with its sibling agents for Claude's
attention. The thing it controls is *which* agent gets picked once delegation
happens — not whether delegation happens at all. Spontaneous delegation in
headless `claude -p` is ~0 (a capable main model just does the task itself, and
this harness is reluctant to spawn agents), so measuring "did it trigger?" for a
single injected agent measures harness policy, not description quality.

So instead we:
  1. Inject ALL sibling agents as competitors via `claude --agents '{...}'`.
  2. Prefix the query with explicit delegation intent ("Delegate this to the
     most appropriate specialist: ..."), conditioning on delegation-sought.
  3. Capture which `subagent_type` Claude selects, and compare it to the
     query's `expected_agent`.

Eval item: {"query": "...", "expected_agent": "<agent-name>" | "none"}
"none" means no sibling should own it (out of scope) — correct iff nothing here
is chosen.

Detection signature confirmed against claude 2.1.x (Agent/Task tool_use with
input.subagent_type; system task_started; streamed input_json_delta).

Python 3.9 compatible; stdlib only (shells out to `claude`).
"""

import argparse
import json
import os
import re
import select
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Dict, List, Optional, Tuple

DELEGATION_TOOLS = ("Agent", "Task")
DELEGATE_PREFIX = "Delegate this to the most appropriate specialist: "


def parse_agent_md(path: str) -> Tuple[str, str, str]:
    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read()
    name, desc, body = "", "", text
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            fm, body = parts[1], parts[2]
            name = _fm_value(fm, "name")
            desc = _fm_value(fm, "description")
    return name, desc, body


def _fm_value(fm: str, key: str) -> str:
    m = re.search(r"(?m)^" + re.escape(key) + r":\s*(.*)$", fm)
    if not m:
        return ""
    first = m.group(1).strip()
    if first in (">", "|", ">-", "|-", ">+", "|+"):
        block, capture = [], False
        for line in fm.splitlines():
            if re.match(r"^" + re.escape(key) + r":\s*[>|]", line):
                capture = True
                continue
            if capture:
                if line and not line[0].isspace():
                    break
                block.append(line.strip())
        return " ".join(b for b in block if b)
    return first


def load_agent_pool(agents_dir: str, body_chars: int = 3000) -> Dict[str, dict]:
    """Build a {name: {description, prompt}} spec from every .md in a dir."""
    pool = {}
    for fn in sorted(os.listdir(agents_dir)):
        if not fn.endswith(".md"):
            continue
        name, desc, body = parse_agent_md(os.path.join(agents_dir, fn))
        if name:
            pool[name] = {"description": desc, "prompt": body[:body_chars]}
    return pool


def select_agent(query: str, agents_spec: Dict[str, dict], timeout: int,
                 model: Optional[str]) -> Optional[str]:
    """Return the subagent_type Claude delegates to (or None)."""
    cmd = ["claude", "-p", DELEGATE_PREFIX + query, "--agents", json.dumps(agents_spec),
           "--output-format", "stream-json", "--verbose", "--include-partial-messages"]
    if model:
        cmd += ["--model", model]
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, env=env)
    buffer = ""
    pending = False
    accumulated = ""
    start = time.time()
    try:
        while time.time() - start < timeout:
            if proc.poll() is not None:
                rest = proc.stdout.read()
                if rest:
                    buffer += rest.decode("utf-8", "replace")
            ready, _, _ = select.select([proc.stdout], [], [], 1.0)
            if not ready:
                if proc.poll() is not None and "\n" not in buffer:
                    break
                continue
            chunk = os.read(proc.stdout.fileno(), 8192)
            if not chunk and proc.poll() is not None:
                break
            buffer += chunk.decode("utf-8", "replace")
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                etype = event.get("type")
                if etype == "system" and event.get("subtype") == "task_started":
                    return event.get("subagent_type")
                if etype == "stream_event":
                    se = event.get("event", {})
                    st = se.get("type")
                    if st == "content_block_start":
                        cb = se.get("content_block", {})
                        if cb.get("type") == "tool_use" and cb.get("name") in DELEGATION_TOOLS:
                            pending, accumulated = True, ""
                    elif st == "content_block_delta" and pending:
                        d = se.get("delta", {})
                        if d.get("type") == "input_json_delta":
                            accumulated += d.get("partial_json", "")
                            m = re.search(r'"subagent_type"\s*:\s*"([^"]+)"', accumulated)
                            if m:
                                return m.group(1)
                    elif st in ("content_block_stop", "message_stop") and pending:
                        m = re.search(r'"subagent_type"\s*:\s*"([^"]+)"', accumulated)
                        return m.group(1) if m else None
                elif etype == "assistant":
                    for it in event.get("message", {}).get("content", []):
                        if it.get("type") == "tool_use" and it.get("name") in DELEGATION_TOOLS:
                            return it.get("input", {}).get("subagent_type")
                elif etype == "result":
                    return None
        return None
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait()


def _is_none(expected: str) -> bool:
    return expected in (None, "", "none", "None")


def run_eval(eval_set: List[dict], target_name: str, agents_spec: Dict[str, dict],
             num_workers: int, timeout: int, runs_per_query: int,
             threshold: float, model: Optional[str]) -> dict:
    """Evaluate the target agent's recall+precision over a routing eval set.

    For each query, should = (expected_agent == target). pass = target won the
    query (rate>=threshold) iff it should have. Also records what *was* chosen.
    """
    picks: Dict[str, List[Optional[str]]] = {}
    items: Dict[str, dict] = {}
    with ProcessPoolExecutor(max_workers=num_workers) as ex:
        fut = {}
        for item in eval_set:
            for _ in range(runs_per_query):
                f = ex.submit(select_agent, item["query"], agents_spec, timeout, model)
                fut[f] = item
        for f in as_completed(fut):
            item = fut[f]
            q = item["query"]
            items[q] = item
            try:
                picks.setdefault(q, []).append(f.result())
            except Exception as exc:  # noqa: BLE001 - log, don't crash the batch
                print("warning: query failed: {}".format(exc), file=sys.stderr)
                picks.setdefault(q, []).append(None)

    results = []
    for q, chosen in picks.items():
        expected = items[q].get("expected_agent")
        should = (expected == target_name)
        target_rate = sum(1 for c in chosen if c == target_name) / len(chosen)
        won = target_rate >= threshold
        passed = (won == should)
        # majority pick for diagnostics
        from collections import Counter
        maj = Counter(c or "none" for c in chosen).most_common(1)[0][0]
        results.append({"query": q, "expected_agent": expected, "should_win": should,
                        "target_rate": target_rate, "majority_pick": maj,
                        "runs": len(chosen), "pass": passed})
    passed = sum(1 for r in results if r["pass"])
    return {"agent_name": target_name, "results": results,
            "summary": {"total": len(results), "passed": passed,
                        "failed": len(results) - passed}}


def main() -> int:
    ap = argparse.ArgumentParser(description="Routing/discrimination eval for an agent.")
    ap.add_argument("--agent-path", required=True, help="Target agent .md")
    ap.add_argument("--agents-dir", default=".claude/agents", help="Dir of competitor agents")
    ap.add_argument("--eval-set", required=True, help="JSON: [{query, expected_agent}]")
    ap.add_argument("--description", default=None, help="Override target description to test")
    ap.add_argument("--num-workers", type=int, default=6)
    ap.add_argument("--timeout", type=int, default=60)
    ap.add_argument("--runs-per-query", type=int, default=3)
    ap.add_argument("--threshold", type=float, default=0.5)
    ap.add_argument("--model", default=None)
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    name, desc, _ = parse_agent_md(args.agent_path)
    pool = load_agent_pool(args.agents_dir)
    pool.setdefault(name, {"description": desc, "prompt": ""})
    if args.description:
        pool[name]["description"] = args.description
    eval_set = json.loads(open(args.eval_set, encoding="utf-8").read())

    out = run_eval(eval_set, name, pool, args.num_workers, args.timeout,
                   args.runs_per_query, args.threshold, args.model)
    if args.verbose:
        s = out["summary"]
        print("{} routing: {}/{} correct".format(name, s["passed"], s["total"]), file=sys.stderr)
        for r in out["results"]:
            print("  [{}] expect={} got={} (target_rate {:.2f}): {}".format(
                "PASS" if r["pass"] else "FAIL", r["expected_agent"], r["majority_pick"],
                r["target_rate"], r["query"][:55]), file=sys.stderr)
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
