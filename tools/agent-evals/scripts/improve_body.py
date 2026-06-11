#!/usr/bin/env python3
"""Autonomously improve an agent's BODY against objective task evals, gated on
a held-out set so it can't overfit.

This is the heavier, higher-risk loop. It is only trustworthy when the eval
`expectations` are objectively checkable (code compiles, test passes, value is
present and correct) — i.e. the .NET engineering agents, NOT subjective agents
like po-agent (see docs/improving-agents.md for why). Run it in a throwaway
worktree/sandbox: it both edits the agent .md and lets the agent execute tasks.

Loop:
  1. Split task evals into train / held-out test.
  2. For the current body, run the agent on each task and grade its outputs.
  3. Propose a body edit from the FAILING train assertions + transcripts.
  4. GATE: accept the edit only if it improves train pass-rate AND does not
     regress the held-out test pass-rate. Otherwise discard and try again.
  5. Repeat up to --max-iterations; keep the best-gated body.

Mechanism (confirmed against claude 2.1.x):
  - `claude -p "<task>" --agents '{name:{description,prompt:<body>}}' --agent name`
    runs the *whole session as that agent*, so the candidate body is what
    actually does the work. The agent writes outputs into the run's cwd.
  - Grading and body proposals are separate `claude -p` text calls.

GRADING HONESTY: grading here is an LLM grader call. For genuine objectivity,
write expectations that a script can check (and/or have the grader run
`dotnet build`/`dotnet test` in the run dir). An LLM grader marking its own
family's work is the weakest link — keep assertions concrete and verifiable.

Python 3.9 compatible; stdlib only (shells out to `claude`).
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from trigger_eval import parse_agent_md  # noqa: E402


def _call_claude_text(prompt: str, model: Optional[str], timeout: int = 600) -> str:
    cmd = ["claude", "-p", "--output-format", "text"]
    if model:
        cmd += ["--model", model]
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    res = subprocess.run(cmd, input=prompt, capture_output=True, text=True,
                         env=env, timeout=timeout)
    if res.returncode != 0:
        raise RuntimeError("claude -p exited {}: {}".format(res.returncode, res.stderr[:500]))
    return res.stdout


def run_agent_task(agent_name: str, description: str, body: str, task: str,
                   workdir: Path, model: Optional[str], timeout: int) -> str:
    """Run the candidate agent on a task inside workdir; return the transcript."""
    workdir.mkdir(parents=True, exist_ok=True)
    agents_spec = {agent_name: {"description": description, "prompt": body}}
    cmd = ["claude", "-p", task, "--agents", json.dumps(agents_spec),
           "--agent", agent_name, "--output-format", "text"]
    if model:
        cmd += ["--model", model]
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    res = subprocess.run(cmd, input="", capture_output=True, text=True, env=env,
                         cwd=str(workdir), timeout=timeout)
    transcript = res.stdout + ("\n[stderr]\n" + res.stderr if res.stderr else "")
    (workdir / "transcript.txt").write_text(transcript, encoding="utf-8")
    return transcript


def grade_run(task: str, expectations: List[str], transcript: str,
              workdir: Path, model: Optional[str]) -> dict:
    """LLM-grade expectations against the transcript + files produced in workdir."""
    listing = []
    for p in sorted(workdir.rglob("*")):
        if p.is_file() and p.name != "transcript.txt":
            try:
                content = p.read_text(encoding="utf-8")[:4000]
            except (OSError, UnicodeDecodeError):
                content = "[binary or unreadable]"
            listing.append("### {}\n{}".format(p.relative_to(workdir), content))
    files_block = "\n\n".join(listing) or "(no output files)"
    exp_block = "\n".join("- {}".format(e) for e in expectations)
    prompt = (
        "You are a strict grader. For each expectation, decide PASS or FAIL based "
        "ONLY on evidence in the transcript and the produced files. PASS only when "
        "the evidence shows the work was genuinely done right (right filename + "
        "wrong/empty content = FAIL). When uncertain, FAIL.\n\n"
        "TASK:\n{}\n\nEXPECTATIONS:\n{}\n\nTRANSCRIPT:\n{}\n\nPRODUCED FILES:\n{}\n\n"
        "Respond with ONLY JSON in this exact shape:\n"
        '{{"expectations":[{{"text":"...","passed":true,"evidence":"..."}}],'
        '"summary":{{"passed":0,"failed":0,"total":0,"pass_rate":0.0}}}}'
    ).format(task, exp_block, transcript[:8000], files_block[:8000])
    text = _call_claude_text(prompt, model)
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        raise RuntimeError("grader did not return JSON: {}".format(text[:300]))
    return json.loads(m.group(0))


def propose_body(agent_name: str, current_body: str, failures: List[dict],
                 model: Optional[str]) -> str:
    fail_block = ""
    for f in failures:
        fail_block += "\n## Task: {}\n".format(f["task"][:200])
        for e in f["failed"]:
            fail_block += "  - FAILED: {} ({})\n".format(e.get("text"), e.get("evidence", "")[:160])
    prompt = (
        'You maintain the system prompt (the "body") of a Claude Code subagent '
        'named "{}". Below is the current body and the assertions it FAILED on '
        "real tasks. Improve the body so it would pass them — but GENERALIZE: fix "
        "the underlying gap, do not bolt on task-specific rules. Explain the WHY of "
        "any instruction rather than adding rigid MUSTs; keep it lean (remove lines "
        "that aren't pulling their weight). Preserve the agent's identity and "
        "scope.\n\n<current_body>\n{}\n</current_body>\n\nFAILURES:\n{}\n\n"
        "Respond with ONLY the full new body inside <new_body></new_body>."
    ).format(agent_name, current_body, fail_block)
    text = _call_claude_text(prompt, model)
    m = re.search(r"<new_body>(.*?)</new_body>", text, re.DOTALL)
    return (m.group(1) if m else text).strip()


def eval_body(agent_name, description, body, evals, base_workdir, model, timeout, label, verbose):
    """Run + grade every eval for a body; return (pass_rate, per_eval failures)."""
    total_passed = total = 0
    failures = []
    for ev in evals:
        wd = base_workdir / label / "eval-{}".format(ev["id"])
        if wd.exists():
            shutil.rmtree(wd)
        transcript = run_agent_task(agent_name, description, body, ev["prompt"],
                                    wd, model, timeout)
        grading = grade_run(ev["prompt"], ev.get("expectations", []), transcript, wd, model)
        (wd / "grading.json").write_text(json.dumps(grading, indent=2), encoding="utf-8")
        s = grading["summary"]
        total_passed += s["passed"]
        total += s["total"]
        failed = [e for e in grading["expectations"] if not e.get("passed")]
        if failed:
            failures.append({"task": ev["prompt"], "failed": failed})
        if verbose:
            print("    [{}] eval {}: {}/{}".format(label, ev["id"], s["passed"], s["total"]),
                  file=sys.stderr)
    rate = total_passed / total if total else 0.0
    return rate, failures


def main() -> int:
    ap = argparse.ArgumentParser(description="Autonomously improve an agent body, gated on held-out evals.")
    ap.add_argument("--agent-path", required=True)
    ap.add_argument("--eval-set", required=True,
                    help="JSON: {evals:[{id,prompt,expectations:[...]}]} (objective expectations!)")
    ap.add_argument("--workspace", required=True, help="Scratch dir for runs (gitignored)")
    ap.add_argument("--max-iterations", type=int, default=3)
    ap.add_argument("--holdout", type=float, default=0.4)
    ap.add_argument("--model", default=None)
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("--apply", action="store_true", help="Write the best-gated body back to the agent .md")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    name, description, body = parse_agent_md(args.agent_path)
    data = json.loads(Path(args.eval_set).read_text(encoding="utf-8"))
    evals = data["evals"] if isinstance(data, dict) else data
    if any(not ev.get("expectations") for ev in evals):
        print("error: every eval needs objective `expectations`. This loop is not "
              "for subjective agents — use qualitative review instead.", file=sys.stderr)
        return 2

    import random
    random.seed(42)
    shuffled = list(evals)
    random.shuffle(shuffled)
    n_test = max(1, int(len(shuffled) * args.holdout))
    test, train = shuffled[:n_test], shuffled[n_test:] or shuffled
    ws = Path(args.workspace)
    if args.verbose:
        print("Agent {}: {} train, {} held-out test".format(name, len(train), len(test)), file=sys.stderr)

    # Baseline
    base_train, _ = eval_body(name, description, body, train, ws / "iter-0", args.model,
                              args.timeout, "train", args.verbose)
    base_test, _ = eval_body(name, description, body, test, ws / "iter-0", args.model,
                             args.timeout, "test", args.verbose)
    if args.verbose:
        print("baseline: train {:.0%}, test {:.0%}".format(base_train, base_test), file=sys.stderr)

    best = {"body": body, "train": base_train, "test": base_test, "iteration": 0}
    current_body = body
    history = [{"iteration": 0, "train": base_train, "test": base_test, "accepted": True}]

    for it in range(1, args.max_iterations + 1):
        _, failures = eval_body(name, description, current_body, train, ws / "iter-{}-cur".format(it),
                                args.model, args.timeout, "train", False)
        if not failures:
            if args.verbose:
                print("No train failures — stopping.", file=sys.stderr)
            break
        candidate = propose_body(name, current_body, failures, args.model)
        cand_train, _ = eval_body(name, description, candidate, train, ws / "iter-{}".format(it),
                                  args.model, args.timeout, "train", args.verbose)
        cand_test, _ = eval_body(name, description, candidate, test, ws / "iter-{}".format(it),
                                 args.model, args.timeout, "test", args.verbose)
        # GATE: must improve train and not regress held-out test.
        accepted = cand_train > best["train"] and cand_test >= best["test"]
        if args.verbose:
            print("iter {}: candidate train {:.0%}, test {:.0%} -> {}".format(
                it, cand_train, cand_test, "ACCEPT" if accepted else "reject"), file=sys.stderr)
        history.append({"iteration": it, "train": cand_train, "test": cand_test, "accepted": accepted})
        if accepted:
            current_body = candidate
            best = {"body": candidate, "train": cand_train, "test": cand_test, "iteration": it}

    report = {"agent_name": name, "baseline_train": base_train, "baseline_test": base_test,
              "best_train": best["train"], "best_test": best["test"],
              "best_iteration": best["iteration"], "history": history}
    (ws / "improve_body_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    if args.apply and best["iteration"] > 0:
        text = Path(args.agent_path).read_text(encoding="utf-8")
        parts = text.split("---", 2)
        if len(parts) == 3:
            Path(args.agent_path).write_text("---{}---\n\n{}".format(parts[1], best["body"].lstrip()),
                                             encoding="utf-8")
            print("Applied best-gated body (iter {}) to {}".format(best["iteration"], args.agent_path),
                  file=sys.stderr)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
