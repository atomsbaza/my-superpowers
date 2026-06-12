#!/usr/bin/env python3
"""Autonomously optimize an agent's `description` for correct ROUTING.

What "correct" means here: among its sibling agents, this agent should win the
queries it owns (recall) and not steal queries that belong to a sibling or to no
one (precision). That competition is what a description actually controls — see
trigger_eval.py for why measuring single-agent "did it trigger?" is the wrong
signal in headless `claude -p`.

Loop (skill-creator's run_loop, adapted to routing):
  1. Split the routing eval set into train / held-out test, stratified by
     whether this agent should win each query.
  2. Evaluate the current description against the full sibling field.
  3. If every TRAIN query routes correctly -> stop.
  4. Else call `claude -p` to propose a new description, BLIND to the test set,
     told to generalize and stay < 1024 chars.
  5. Repeat up to --max-iterations. Pick the winner by TEST score (then train),
     so we don't overfit.

Eval item: {"query": "...", "expected_agent": "<name>" | "none"}.

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
from trigger_eval import load_agent_pool, parse_agent_md, run_eval  # noqa: E402


def split_eval_set(eval_set: List[dict], target: str, holdout: float,
                   seed: int = 42) -> Tuple[List[dict], List[dict]]:
    import random
    random.seed(seed)
    mine = [e for e in eval_set if e.get("expected_agent") == target]
    others = [e for e in eval_set if e.get("expected_agent") != target]
    random.shuffle(mine)
    random.shuffle(others)
    n_mine = max(1, int(len(mine) * holdout)) if mine else 0
    n_oth = max(1, int(len(others) * holdout)) if others else 0
    test = mine[:n_mine] + others[:n_oth]
    train = mine[n_mine:] + others[n_oth:]
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


def propose_description(target: str, body: str, current: str, siblings: Dict[str, str],
                        train_results: dict, history: List[dict],
                        model: Optional[str]) -> str:
    missed = [r for r in train_results["results"] if r["should_win"] and not r["pass"]]
    stolen = [r for r in train_results["results"] if not r["should_win"] and not r["pass"]]
    sib_block = "\n".join('  - {}: {}'.format(n, d[:140]) for n, d in siblings.items() if n != target)
    prompt = (
        'You are optimizing the `description` of a Claude Code subagent named "{}". '
        "Claude reads every agent's name + description and, when delegating, picks "
        "ONE. Your agent competes with these siblings:\n{}\n\n"
        "Your description must make Claude pick your agent for the work it owns, and "
        "NOT pick it for work that belongs to a sibling or to no specialist.\n\n"
        '<current_description>\n"{}"\n</current_description>\n\n'
    ).format(target, sib_block, current)
    if missed:
        prompt += "LOST queries it SHOULD have won (went elsewhere):\n"
        for r in missed:
            prompt += '  - "{}" (went to: {})\n'.format(r["query"], r["majority_pick"])
        prompt += "\n"
    if stolen:
        prompt += "STOLEN queries it should NOT have won (belong to a sibling/none):\n"
        for r in stolen:
            prompt += '  - "{}" (expected: {})\n'.format(r["query"], r["expected_agent"])
        prompt += "\n"
    if history:
        prompt += "PREVIOUS ATTEMPTS (try something structurally different):\n"
        for h in history:
            prompt += '  train={}/{}: "{}"\n'.format(h.get("train_passed"), h.get("train_total"),
                                                      h["description"][:120])
        prompt += "\n"
    prompt += (
        "Agent body for context:\n<body>\n{}\n</body>\n\n"
        "Write an improved description. GENERALIZE — sharpen the boundary between "
        "this agent and its siblings rather than enumerating specific queries. "
        "Imperative voice, focus on user intent, make the ownership distinctive. "
        "Hard limit 1024 chars (~100-200 words). Respond with ONLY the new "
        "description in <new_description></new_description>.".format(body[:3500])
    )
    text = _call_claude(prompt, model)
    m = re.search(r"<new_description>(.*?)</new_description>", text, re.DOTALL)
    desc = (m.group(1) if m else text).strip().strip('"').strip()
    if len(desc) > 1024:
        desc = desc[:1020].rsplit(" ", 1)[0] + "…"
    return desc


def apply_description(agent_path: str, new_desc: str) -> None:
    text = Path(agent_path).read_text(encoding="utf-8")
    parts = text.split("---", 2)
    if len(parts) != 3:
        raise RuntimeError("no frontmatter in {}".format(agent_path))
    fm = parts[1]
    indented = "\n  ".join(new_desc.split("\n"))
    block = "description: >\n  {}\n".format(indented)
    if re.search(r"(?m)^description:.*(\n[ \t]+.*)*", fm):
        fm = re.sub(r"(?m)^description:.*(\n[ \t]+.*)*\n?", block, fm, count=1)
    else:
        fm = fm.rstrip("\n") + "\n" + block
    Path(agent_path).write_text("---{}---{}".format(fm, parts[2]), encoding="utf-8")


def _summ(results: List[dict]) -> dict:
    passed = sum(1 for r in results if r["pass"])
    return {"passed": passed, "failed": len(results) - passed, "total": len(results)}


def main() -> int:
    ap = argparse.ArgumentParser(description="Optimize an agent description for correct routing.")
    ap.add_argument("--agent-path", required=True)
    ap.add_argument("--agents-dir", default=".claude/agents", help="Competitor agent pool")
    ap.add_argument("--eval-set", required=True, help="JSON: [{query, expected_agent}]")
    ap.add_argument("--max-iterations", type=int, default=5)
    ap.add_argument("--holdout", type=float, default=0.4)
    ap.add_argument("--runs-per-query", type=int, default=3)
    ap.add_argument("--threshold", type=float, default=0.5)
    ap.add_argument("--num-workers", type=int, default=6)
    ap.add_argument("--timeout", type=int, default=60)
    ap.add_argument("--model", default=None)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--output", default=None)
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    name, original_desc, body = parse_agent_md(args.agent_path)
    pool = load_agent_pool(args.agents_dir)
    pool.setdefault(name, {"description": original_desc, "prompt": body[:3000]})
    siblings = {n: pool[n]["description"] for n in pool}
    eval_set = json.loads(Path(args.eval_set).read_text(encoding="utf-8"))
    train, test = split_eval_set(eval_set, name, args.holdout) if args.holdout > 0 else (eval_set, [])
    if args.verbose:
        print("Agent: {} | {} train, {} test | competitors: {}".format(
            name, len(train), len(test), ", ".join(n for n in pool if n != name)), file=sys.stderr)

    current = original_desc
    history: List[dict] = []
    best = {"description": original_desc, "test_passed": -1, "test_total": len(test),
            "train_passed": -1, "train_total": len(train)}

    for it in range(1, args.max_iterations + 1):
        pool[name]["description"] = current
        t0 = time.time()
        all_q = train + test
        res = run_eval(all_q, name, pool, args.num_workers, args.timeout,
                       args.runs_per_query, args.threshold, args.model)
        by_q = {r["query"]: r for r in res["results"]}
        train_res = {"results": [by_q[q["query"]] for q in train if q["query"] in by_q]}
        test_res = {"results": [by_q[q["query"]] for q in test if q["query"] in by_q]}
        train_res["summary"] = _summ(train_res["results"])
        test_res["summary"] = _summ(test_res["results"])
        tp, tt = train_res["summary"]["passed"], train_res["summary"]["total"]
        sp, st = test_res["summary"]["passed"], test_res["summary"]["total"]
        if args.verbose:
            print("iter {}: train {}/{}, test {}/{} ({:.0f}s)".format(it, tp, tt, sp, st, time.time() - t0),
                  file=sys.stderr)
        history.append({"iteration": it, "description": current, "train_passed": tp,
                        "train_total": tt, "test_passed": sp, "test_total": st,
                        "train_detail": [{"q": r["query"][:60], "expected": r["expected_agent"],
                                          "got": r["majority_pick"], "pass": r["pass"]}
                                         for r in train_res["results"]]})
        if (sp, tp) > (best["test_passed"], best["train_passed"]):
            best = {"description": current, "test_passed": sp, "test_total": st,
                    "train_passed": tp, "train_total": tt}
        if tt > 0 and tp == tt:
            if args.verbose:
                print("All train queries route correctly — stopping.", file=sys.stderr)
            break
        if it == args.max_iterations:
            break
        current = propose_description(name, body, current, siblings, train_res, history, args.model)
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


if __name__ == "__main__":
    sys.exit(main())
