#!/usr/bin/env python3
"""Test whether an agent's name+description causes Claude to delegate to it.

The agent analogue of skill-creator's run_eval.py. Where skills trigger via a
`Skill`/`Read` tool call, agents trigger via the `Agent` (a.k.a. `Task`) tool
with `input.subagent_type == <agent-name>`. We inject a candidate definition
with `claude --agents '{...}'` (no temp files in .claude/agents/), run each
query through `claude -p` with streaming JSON, and watch for that delegation —
killing the subprocess as soon as the routing decision is visible so we pay for
the decision, not the agent's full run.

Signature confirmed empirically against claude 2.1.x:
  stream_event -> content_block_delta -> input_json_delta:
    {"partial_json": "..., \"subagent_type\": \"<name>"}
  assistant message tool_use: {"name":"Agent","input":{"subagent_type":"<name>", ...}}
  system: {"subtype":"task_started","subagent_type":"<name>","task_type":"local_agent"}

Python 3.9 compatible. Uses only the stdlib.
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

# Tool names that mean "Claude delegated to a subagent". The available-tools
# list calls it "Task"; the emitted tool_use is named "Agent". Accept both.
DELEGATION_TOOLS = ("Agent", "Task")


def parse_agent_md(path: str) -> Tuple[str, str, str]:
    """Return (name, description, body) from an agent .md file."""
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


def run_single_query(query: str, agent_name: str, description: str,
                     agent_prompt: str, timeout: int,
                     model: Optional[str]) -> bool:
    """Return True if `claude -p query` delegates to the candidate agent."""
    agents_spec = {agent_name: {"description": description, "prompt": agent_prompt}}
    cmd = ["claude", "-p", query, "--agents", json.dumps(agents_spec),
           "--output-format", "stream-json", "--verbose", "--include-partial-messages"]
    if model:
        cmd += ["--model", model]
    # Allow nesting claude -p inside a Claude Code session (the guard is only
    # for interactive terminal conflicts; subprocess usage is safe).
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                            env=env)
    buffer = ""
    pending_tool = None        # name of an in-progress tool_use
    accumulated = ""           # partial_json for the pending tool
    start = time.time()
    try:
        while time.time() - start < timeout:
            if proc.poll() is not None:
                rest = proc.stdout.read()
                if rest:
                    buffer += rest.decode("utf-8", "replace")
                break
            ready, _, _ = select.select([proc.stdout], [], [], 1.0)
            if not ready:
                continue
            chunk = os.read(proc.stdout.fileno(), 8192)
            if not chunk:
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

                # Cleanest structured signal: a subagent task actually started.
                if etype == "system" and event.get("subtype") == "task_started":
                    return event.get("subagent_type") == agent_name

                # Early detection from streaming tool-call construction.
                if etype == "stream_event":
                    se = event.get("event", {})
                    se_type = se.get("type")
                    if se_type == "content_block_start":
                        cb = se.get("content_block", {})
                        if cb.get("type") == "tool_use":
                            tname = cb.get("name", "")
                            if tname in DELEGATION_TOOLS:
                                pending_tool, accumulated = tname, ""
                            else:
                                # First action is a direct tool (Read/Bash/Skill/…)
                                # => Claude is handling it itself, not delegating.
                                return False
                    elif se_type == "content_block_delta" and pending_tool:
                        delta = se.get("delta", {})
                        if delta.get("type") == "input_json_delta":
                            accumulated += delta.get("partial_json", "")
                            if _subagent_is(accumulated, agent_name):
                                return True
                    elif se_type in ("content_block_stop", "message_stop"):
                        if pending_tool:
                            return _subagent_is(accumulated, agent_name)
                        if se_type == "message_stop":
                            return False

                # Fallback: a fully-formed assistant tool_use.
                elif etype == "assistant":
                    for item in event.get("message", {}).get("content", []):
                        if item.get("type") != "tool_use":
                            continue
                        if item.get("name") in DELEGATION_TOOLS:
                            return item.get("input", {}).get("subagent_type") == agent_name
                        return False  # some other tool first

                elif etype == "result":
                    return False
        return False
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait()


def _subagent_is(partial_json: str, name: str) -> bool:
    """Did the streamed tool input set subagent_type to our agent?"""
    m = re.search(r'"subagent_type"\s*:\s*"([^"]*)', partial_json)
    return bool(m) and m.group(1) == name


def run_eval(eval_set: List[dict], agent_name: str, description: str,
             agent_prompt: str, num_workers: int, timeout: int,
             runs_per_query: int, trigger_threshold: float,
             model: Optional[str]) -> dict:
    triggers: Dict[str, List[bool]] = {}
    items: Dict[str, dict] = {}
    with ProcessPoolExecutor(max_workers=num_workers) as ex:
        fut = {}
        for item in eval_set:
            for _ in range(runs_per_query):
                f = ex.submit(run_single_query, item["query"], agent_name,
                              description, agent_prompt, timeout, model)
                fut[f] = item
        for f in as_completed(fut):
            item = fut[f]
            q = item["query"]
            items[q] = item
            try:
                triggers.setdefault(q, []).append(bool(f.result()))
            except Exception as exc:  # noqa: BLE001 - record failures, don't crash the run
                print("warning: query failed: {}".format(exc), file=sys.stderr)
                triggers.setdefault(q, []).append(False)

    results = []
    for q, runs in triggers.items():
        rate = sum(runs) / len(runs)
        should = items[q]["should_trigger"]
        passed = rate >= trigger_threshold if should else rate < trigger_threshold
        results.append({"query": q, "should_trigger": should,
                        "trigger_rate": rate, "triggers": sum(runs),
                        "runs": len(runs), "pass": passed})
    passed = sum(1 for r in results if r["pass"])
    return {"agent_name": agent_name, "description": description,
            "results": results,
            "summary": {"total": len(results), "passed": passed,
                        "failed": len(results) - passed}}


def main() -> int:
    ap = argparse.ArgumentParser(description="Trigger eval for an agent description.")
    ap.add_argument("--agent-path", required=True, help="Path to the agent .md")
    ap.add_argument("--eval-set", required=True, help="JSON: [{query, should_trigger}]")
    ap.add_argument("--description", default=None, help="Override description to test")
    ap.add_argument("--num-workers", type=int, default=6)
    ap.add_argument("--timeout", type=int, default=45)
    ap.add_argument("--runs-per-query", type=int, default=3)
    ap.add_argument("--trigger-threshold", type=float, default=0.5)
    ap.add_argument("--model", default=None)
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    name, desc, body = parse_agent_md(args.agent_path)
    description = args.description or desc
    eval_set = json.loads(open(args.eval_set, encoding="utf-8").read())

    out = run_eval(eval_set, name, description, body, args.num_workers,
                   args.timeout, args.runs_per_query, args.trigger_threshold,
                   args.model)
    if args.verbose:
        s = out["summary"]
        print("{}/{} passed".format(s["passed"], s["total"]), file=sys.stderr)
        for r in out["results"]:
            print("  [{}] {}/{} expect={}: {}".format(
                "PASS" if r["pass"] else "FAIL", r["triggers"], r["runs"],
                r["should_trigger"], r["query"][:70]), file=sys.stderr)
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
