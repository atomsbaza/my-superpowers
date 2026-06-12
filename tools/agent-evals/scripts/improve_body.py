#!/usr/bin/env python3
"""Autonomously improve an agent's BODY against objective task evals, gated on
a held-out set so it can't overfit.

The heavier, higher-risk loop — only trustworthy when grading is objective.
Two grading modes:
  * --verify-cmd "<shell>"  : run a command in the eval's workdir; exit 0 = pass.
    For .NET that's `dotnet build && dotnet test ...` — fully deterministic, no
    LLM grader involved. This is the trustworthy mode.
  * otherwise               : fall back to an LLM grader over the transcript +
    produced files (weaker; the model marks its own family's work).

For tasks that modify an existing project, pass --project-template <dir>; each
eval run gets a fresh copy of it as its workdir (ignoring .git/bin/obj), so the
agent edits a real, isolated checkout and the verify command builds/tests it.

Loop: split into train/held-out test -> run+grade each -> propose a body edit
from failures -> ACCEPT only if train improves AND held-out test doesn't
regress -> repeat. Keep the best-gated body. Run it in a throwaway worktree:
it edits the agent .md and lets the agent execute tasks.

Mechanism (confirmed against claude 2.1.x): `claude -p "<task>" --agents
'{name:{description,prompt:<body>}}' --agent name` runs the whole session as
that agent inside the workdir.

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

# Extra PATH entries so the agent subprocess and verify command can find tools
# installed outside the default PATH (e.g. a user-local .NET SDK in ~/.dotnet).
EXTRA_PATH = [str(Path.home() / ".dotnet")]
SEED_IGNORE = shutil.ignore_patterns(".git", "bin", "obj", "TestResults",
                                     "node_modules", "*.user")


def _subprocess_env() -> dict:
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    extra = ":".join(p for p in EXTRA_PATH if os.path.isdir(p))
    if extra:
        env["PATH"] = extra + ":" + env.get("PATH", "")
    env.setdefault("DOTNET_CLI_TELEMETRY_OPTOUT", "1")
    env.setdefault("DOTNET_NOLOGO", "1")
    return env


def _call_claude_text(prompt: str, model: Optional[str], timeout: int = 600) -> str:
    cmd = ["claude", "-p", "--output-format", "text"]
    if model:
        cmd += ["--model", model]
    res = subprocess.run(cmd, input=prompt, capture_output=True, text=True,
                         env=_subprocess_env(), timeout=timeout)
    if res.returncode != 0:
        raise RuntimeError("claude -p exited {}: {}".format(res.returncode, res.stderr[:500]))
    return res.stdout


def seed_workdir(workdir: Path, template: Optional[str]) -> None:
    if workdir.exists():
        shutil.rmtree(workdir)
    if template:
        shutil.copytree(template, workdir, ignore=SEED_IGNORE)
    else:
        workdir.mkdir(parents=True, exist_ok=True)


def run_agent_task(agent_name: str, description: str, body: str, task: str,
                   workdir: Path, model: Optional[str], timeout: int) -> str:
    """Run the candidate agent on a task inside workdir; return the transcript."""
    agents_spec = {agent_name: {"description": description, "prompt": body}}
    cmd = ["claude", "-p", task, "--agents", json.dumps(agents_spec),
           "--agent", agent_name, "--output-format", "text",
           "--permission-mode", "bypassPermissions"]
    if model:
        cmd += ["--model", model]
    try:
        res = subprocess.run(cmd, input="", capture_output=True, text=True,
                             env=_subprocess_env(), cwd=str(workdir), timeout=timeout)
        transcript = res.stdout + ("\n[stderr]\n" + res.stderr if res.stderr else "")
    except subprocess.TimeoutExpired:
        transcript = "[agent run timed out after {}s]".format(timeout)
    (workdir / "_transcript.txt").write_text(transcript, encoding="utf-8")
    return transcript


def verify_grade(verify_cmd: str, workdir: Path, timeout: int) -> dict:
    """Run verify_cmd in workdir; exit 0 == pass. Deterministic, no LLM."""
    try:
        res = subprocess.run(verify_cmd, shell=True, cwd=str(workdir),
                             capture_output=True, text=True, env=_subprocess_env(),
                             timeout=timeout)
        passed = res.returncode == 0
        tail = (res.stdout + res.stderr)[-1500:]
    except subprocess.TimeoutExpired:
        passed, tail = False, "[verify timed out after {}s]".format(timeout)
    return {
        "expectations": [{"text": "verify: `{}` exits 0".format(verify_cmd),
                          "passed": passed, "evidence": tail}],
        "summary": {"passed": int(passed), "failed": int(not passed),
                    "total": 1, "pass_rate": 1.0 if passed else 0.0},
    }


def grade_run(task: str, expectations: List[str], transcript: str,
              workdir: Path, model: Optional[str]) -> dict:
    """LLM-grade expectations (fallback when no verify_cmd)."""
    listing = []
    for p in sorted(workdir.rglob("*")):
        if p.is_file() and p.name != "_transcript.txt":
            try:
                content = p.read_text(encoding="utf-8")[:3000]
            except (OSError, UnicodeDecodeError):
                continue
            listing.append("### {}\n{}".format(p.relative_to(workdir), content))
    files_block = "\n\n".join(listing[:30]) or "(no output files)"
    exp_block = "\n".join("- {}".format(e) for e in expectations)
    prompt = (
        "You are a strict grader. For each expectation decide PASS or FAIL from "
        "evidence in the transcript and files only. When uncertain, FAIL.\n\n"
        "TASK:\n{}\n\nEXPECTATIONS:\n{}\n\nTRANSCRIPT:\n{}\n\nFILES:\n{}\n\n"
        "Respond with ONLY JSON: "
        '{{"expectations":[{{"text":"...","passed":true,"evidence":"..."}}],'
        '"summary":{{"passed":0,"failed":0,"total":0,"pass_rate":0.0}}}}'
    ).format(task, exp_block, transcript[:6000], files_block[:6000])
    text = _call_claude_text(prompt, model)
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        raise RuntimeError("grader did not return JSON: {}".format(text[:300]))
    return json.loads(m.group(0))


def propose_body(agent_name: str, current_body: str, failures: List[dict],
                 model: Optional[str]) -> str:
    fail_block = ""
    for f in failures:
        fail_block += "\n## Task: {}\n".format(f["task"][:300])
        for e in f["failed"]:
            fail_block += "  - FAILED: {} ({})\n".format(e.get("text"), (e.get("evidence") or "")[:300])
    prompt = (
        'You maintain the system prompt ("body") of a Claude Code subagent named '
        '"{}". Below is the current body and what it FAILED on real tasks. Improve '
        "the body so it would pass — but GENERALIZE: fix the underlying gap, do not "
        "bolt on task-specific rules. Explain the WHY rather than adding rigid MUSTs; "
        "keep it lean. Preserve the agent's identity and scope.\n\n"
        "<current_body>\n{}\n</current_body>\n\nFAILURES:\n{}\n\n"
        "Respond with ONLY the full new body inside <new_body></new_body>."
    ).format(agent_name, current_body, fail_block)
    text = _call_claude_text(prompt, model)
    m = re.search(r"<new_body>(.*?)</new_body>", text, re.DOTALL)
    return (m.group(1) if m else text).strip()


def eval_body(agent_name, description, body, evals, base_workdir, model, timeout,
              verify_timeout, label, default_template, default_verify, verbose):
    """Run + grade every eval for a body; return (pass_rate, failures)."""
    total_passed = total = 0
    failures = []
    for ev in evals:
        wd = base_workdir / label / "eval-{}".format(ev["id"])
        template = ev.get("project_template", default_template)
        verify = ev.get("verify_cmd", default_verify)
        seed_workdir(wd, template)
        transcript = run_agent_task(agent_name, description, body, ev["prompt"],
                                    wd, model, timeout)
        if verify:
            grading = verify_grade(verify, wd, verify_timeout)
        else:
            grading = grade_run(ev["prompt"], ev.get("expectations", []), transcript, wd, model)
        (wd / "_grading.json").write_text(json.dumps(grading, indent=2), encoding="utf-8")
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
                    help="JSON: {evals:[{id,prompt,expectations|verify_cmd,project_template?}]}")
    ap.add_argument("--workspace", required=True, help="Scratch dir for runs (gitignored)")
    ap.add_argument("--project-template", default=None, help="Dir copied into each eval workdir")
    ap.add_argument("--verify-cmd", default=None, help="Shell cmd run in workdir; exit 0 = pass")
    ap.add_argument("--max-iterations", type=int, default=3)
    ap.add_argument("--holdout", type=float, default=0.4)
    ap.add_argument("--model", default=None)
    ap.add_argument("--timeout", type=int, default=900, help="Per agent-run timeout (s)")
    ap.add_argument("--verify-timeout", type=int, default=600, help="Per verify-cmd timeout (s)")
    ap.add_argument("--apply", action="store_true", help="Write best-gated body back to the agent .md")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    name, description, body = parse_agent_md(args.agent_path)
    data = json.loads(Path(args.eval_set).read_text(encoding="utf-8"))
    evals = data["evals"] if isinstance(data, dict) else data
    # Objective grading required: every eval must have a verify_cmd (per-eval or
    # global) or explicit expectations. No silent subjective grading.
    for ev in evals:
        if not (ev.get("verify_cmd") or args.verify_cmd or ev.get("expectations")):
            print("error: eval {} has no verify_cmd and no expectations — this loop "
                  "needs objective grading.".format(ev.get("id")), file=sys.stderr)
            return 2

    import random
    random.seed(42)
    shuffled = list(evals)
    random.shuffle(shuffled)
    n_test = max(1, int(len(shuffled) * args.holdout)) if len(shuffled) > 1 else 0
    test, train = shuffled[:n_test], shuffled[n_test:] or shuffled
    ws = Path(args.workspace)
    tmpl, vcmd, vt = args.project_template, args.verify_cmd, args.verify_timeout
    if args.verbose:
        print("Agent {}: {} train, {} held-out test | verify={}".format(
            name, len(train), len(test), bool(vcmd)), file=sys.stderr)

    def run(b, evs, sub, lbl):
        return eval_body(name, description, b, evs, ws / sub, args.model, args.timeout,
                         vt, lbl, tmpl, vcmd, args.verbose)

    base_train, _ = run(body, train, "iter-0", "train")
    base_test, _ = run(body, test, "iter-0", "test") if test else (1.0, [])
    if args.verbose:
        print("baseline: train {:.0%}, test {:.0%}".format(base_train, base_test), file=sys.stderr)

    best = {"body": body, "train": base_train, "test": base_test, "iteration": 0}
    current_body = body
    history = [{"iteration": 0, "train": base_train, "test": base_test, "accepted": True}]

    for it in range(1, args.max_iterations + 1):
        _, failures = run(current_body, train, "iter-{}-cur".format(it), "train")
        if not failures:
            if args.verbose:
                print("No train failures — stopping.", file=sys.stderr)
            break
        candidate = propose_body(name, current_body, failures, args.model)
        cand_train, _ = run(candidate, train, "iter-{}".format(it), "train")
        cand_test, _ = run(candidate, test, "iter-{}".format(it), "test") if test else (cand_train, [])
        accepted = cand_train > best["train"] and cand_test >= best["test"]
        if args.verbose:
            print("iter {}: candidate train {:.0%}, test {:.0%} -> {}".format(
                it, cand_train, cand_test, "ACCEPT" if accepted else "reject"), file=sys.stderr)
        history.append({"iteration": it, "train": cand_train, "test": cand_test, "accepted": accepted})
        if accepted:
            current_body, best = candidate, {"body": candidate, "train": cand_train,
                                             "test": cand_test, "iteration": it}

    ws.mkdir(parents=True, exist_ok=True)
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
            print("Applied best-gated body (iter {})".format(best["iteration"]), file=sys.stderr)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
