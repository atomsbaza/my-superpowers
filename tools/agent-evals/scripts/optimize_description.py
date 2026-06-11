#!/usr/bin/env python3
"""Autonomously optimize an agent's `description` for correct triggering.

The agent analogue of skill-creator's run_loop.py + improve_description.py.
The description is the ONLY thing that decides whether Claude delegates to an
agent, so it is worth optimizing independently of the body — and it is the one
loop that can run fully unattended, because "did it delegate?" is objective.

Loop:
  1. Split the eval set into train / held-out test (stratified by should_trigger).
  2. Evaluate the current description on all queries (trigger_eval, N runs each).
  3. If every TRAIN query passes -> stop.
  4. Otherwise call `claude -p` to propose a new description, BLIND to the test
     results, told to generalize (not enumerate cases) and stay < 1024 chars.
  5. Repeat up to --max-iterations.
Select the winner by TEST score, not train score, to avoid overfitting.

Important: in `claude -p`, the main model handles many tasks itself instead of
delegating. So trigger queries must be substantive, specialist-warranting tasks
(multi-step, domain-heavy) where delegation is genuinely warranted — trivial
queries won't delegate regardless of the description, and will just add noise.

Python 3.9 compatible; stdlib only (shells out to `claude`).
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from trigger_eval import parse_agent_md, run_eval  # noqa: E402


def split_eval_set(eval_set: List[dict], holdout: float,
                   seed: int = 42) -> Tuple[List[dict], List[dict]]:
    import random
    random.seed(seed)
    pos = [e for e in eval_set if e["should_trigger"]]
    neg = [e for e in eval_set if not e["should_trigger"]]
    random.shuffle(pos)
    random.shuffle(neg)
    n_pos = max(1, int(len(pos) * holdout)) if pos else 0
    n_neg = max(1, int(len(neg) * holdout)) if neg else 0
    test = pos[:n_pos] + neg[:n_neg]
    train = pos[n_pos:] + neg[n_neg:]
    return train, test


def _call_claude(prompt: str, model: Optional[str], timeout: int = 300) -> str:
    cmd = ["claude", "-p", "--output-format", "text"]
    if model:
        cmd += ["--model", model]
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    res = subprocess.run(cmd, input=prompt, capture_output=True, text=True,
                         env=env, timeout=timeout)
    if res.returncode != 0:
        raise RuntimeError("claude -p exited {}: {}".format(res.returncode, res.stderr))
    return res.stdout


def propose_description(agent_name: str, body: str, current: str,
                        train_results: dict, history: List[dict],
                        model: Optional[str]) -> str:
    failed_trigger = [r for r in train_results["results"]
                      if r["should_trigger"] and not r["pass"]]
    false_trigger = [r for r in train_results["results"]
                     if not r["should_trigger"] and not r["pass"]]
    prompt = (
        "You are optimizing the `description` of a Claude Code subagent named "
        '"{}". Claude sees each agent\'s name + description in its available-agents '
        "list and decides, per user query, whether to delegate to that agent. The "
        "description is the ONLY thing driving that decision. Write a description "
        "that makes Claude delegate for relevant queries and NOT delegate for "
        "irrelevant ones.\n\n".format(agent_name)
    )
    prompt += '<current_description>\n"{}"\n</current_description>\n\n'.format(current)
    if failed_trigger:
        prompt += "FAILED TO TRIGGER (should have delegated, didn't):\n"
        for r in failed_trigger:
            prompt += '  - "{}" ({}/{})\n'.format(r["query"], r["triggers"], r["runs"])
        prompt += "\n"
    if false_trigger:
        prompt += "FALSE TRIGGERS (delegated but shouldn't):\n"
        for r in false_trigger:
            prompt += '  - "{}" ({}/{})\n'.format(r["query"], r["triggers"], r["runs"])
        prompt += "\n"
    if history:
        prompt += ("PREVIOUS ATTEMPTS (do NOT repeat — try something structurally "
                   "different):\n")
        for h in history:
            prompt += '  train={}/{}: "{}"\n'.format(
                h.get("train_passed"), h.get("train_total"), h["description"])
        prompt += "\n"
    prompt += (
        "Agent body for context on what it actually does:\n<body>\n{}\n</body>\n\n"
        "Write an improved description. GENERALIZE from the failures to broader "
        "categories of user intent — do NOT enumerate specific queries (that "
        "overfits and bloats the prompt). Tips that work well:\n"
        "- imperative voice (\"Use this agent to…\"/\"Delegate here when…\")\n"
        "- focus on the user's intent, not implementation\n"
        "- be distinctive so it competes well with other agents for attention\n"
        "- be a little pushy about WHEN to use it (agents tend to under-trigger), "
        "but keep the should-NOT-trigger boundary sharp\n"
        "Hard limit 1024 characters; aim for ~100-200 words. Respond with ONLY the "
        "new description inside <new_description></new_description>.".format(body[:4000])
    )
    text = _call_claude(prompt, model)
    m = re.search(r"<new_description>(.*?)</new_description>", text, re.DOTALL)
    desc = (m.group(1) if m else text).strip().strip('"').strip()
    if len(desc) > 1024:
        desc = desc[:1020].rsplit(" ", 1)[0] + "…"
    return desc


def _score(results: dict) -> Tuple[int, int]:
    s = results["summary"]
    return s["passed"], s["total"]


def apply_description(agent_path: str, new_desc: str) -> None:
    """Replace the frontmatter description with a YAML block scalar."""
    text = Path(agent_path).read_text(encoding="utf-8")
    parts = text.split("---", 2)
    if len(parts) != 3:
        raise RuntimeError("no frontmatter to update in {}".format(agent_path))
    fm = parts[1]
    indented = "\n  ".join(new_desc.split("\n"))
    block = "description: >\n  {}\n".format(indented)
    if re.search(r"(?m)^description:.*(\n[ \t]+.*)*", fm):
        fm = re.sub(r"(?m)^description:.*(\n[ \t]+.*)*\n?", block, fm, count=1)
    else:
        fm = fm.rstrip("\n") + "\n" + block
    Path(agent_path).write_text("---{}---{}".format(fm, parts[2]), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Autonomously optimize an agent description for triggering.")
    ap.add_argument("--agent-path", required=True)
    ap.add_argument("--eval-set", required=True, help="JSON: [{query, should_trigger}]")
    ap.add_argument("--max-iterations", type=int, default=5)
    ap.add_argument("--holdout", type=float, default=0.4)
    ap.add_argument("--runs-per-query", type=int, default=3)
    ap.add_argument("--trigger-threshold", type=float, default=0.5)
    ap.add_argument("--num-workers", type=int, default=6)
    ap.add_argument("--timeout", type=int, default=45)
    ap.add_argument("--model", default=None, help="Model id (match the session you ship to)")
    ap.add_argument("--apply", action="store_true", help="Write the winning description back into the agent .md")
    ap.add_argument("--output", default=None, help="Write the full JSON report here")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    name, original_desc, body = parse_agent_md(args.agent_path)
    eval_set = json.loads(Path(args.eval_set).read_text(encoding="utf-8"))
    train, test = split_eval_set(eval_set, args.holdout) if args.holdout > 0 else (eval_set, [])
    if args.verbose:
        print("Agent: {} | {} train, {} test".format(name, len(train), len(test)), file=sys.stderr)

    current = original_desc
    history: List[dict] = []
    best = {"description": original_desc, "test_passed": -1, "test_total": len(test),
            "train_passed": -1, "train_total": len(train)}

    for it in range(1, args.max_iterations + 1):
        t0 = time.time()
        all_q = train + test
        res = run_eval(all_q, name, current, body, args.num_workers, args.timeout,
                       args.runs_per_query, args.trigger_threshold, args.model)
        train_qs = {q["query"] for q in train}
        train_res = {"results": [r for r in res["results"] if r["query"] in train_qs]}
        test_res = {"results": [r for r in res["results"] if r["query"] not in train_qs]}
        train_res["summary"] = _summ(train_res["results"])
        test_res["summary"] = _summ(test_res["results"])
        tp, tt = _score(train_res)
        sp, st = _score(test_res)
        if args.verbose:
            print("iter {}: train {}/{}, test {}/{} ({:.0f}s)".format(
                it, tp, tt, sp, st, time.time() - t0), file=sys.stderr)

        history.append({"iteration": it, "description": current,
                        "train_passed": tp, "train_total": tt,
                        "test_passed": sp, "test_total": st})

        # Track best by test score (then train as tiebreak).
        if (sp, tp) > (best["test_passed"], best["train_passed"]):
            best = {"description": current, "test_passed": sp, "test_total": st,
                    "train_passed": tp, "train_total": tt}

        if tt > 0 and tp == tt:
            if args.verbose:
                print("All train queries pass — stopping.", file=sys.stderr)
            break
        if it == args.max_iterations:
            break
        current = propose_description(name, body, current, train_res, history, args.model)
        if args.verbose:
            print("  proposed: {}".format(current[:100]), file=sys.stderr)

    report = {"agent_name": name, "original_description": original_desc,
              "best_description": best["description"],
              "best_test_score": "{}/{}".format(best["test_passed"], best["test_total"]),
              "best_train_score": "{}/{}".format(best["train_passed"], best["train_total"]),
              "iterations_run": len(history), "holdout": args.holdout,
              "train_size": len(train), "test_size": len(test), "history": history}

    if args.output:
        Path(args.output).write_text(json.dumps(report, indent=2), encoding="utf-8")
    if args.apply and best["description"] != original_desc:
        apply_description(args.agent_path, best["description"])
        print("Applied winning description to {}".format(args.agent_path), file=sys.stderr)

    print(json.dumps(report, indent=2))
    return 0


def _summ(results: List[dict]) -> dict:
    passed = sum(1 for r in results if r["pass"])
    return {"passed": passed, "failed": len(results) - passed, "total": len(results)}


if __name__ == "__main__":
    sys.exit(main())
