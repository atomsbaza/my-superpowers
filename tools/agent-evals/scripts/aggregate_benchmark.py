#!/usr/bin/env python3
"""Aggregate per-run grading into a benchmark for an agent A/B evaluation.

Reads an iteration directory laid out like:

    <agent>-workspace/iteration-N/
      <eval-name>/
        with_agent/    grading.json   [timing.json]
        without_agent/ grading.json   [timing.json]

and writes benchmark.json + benchmark.md next to it.

The `configuration` strings are "with_agent" / "without_agent" (the agent
analogue of skill-creator's with_skill/without_skill). The baseline
("without_agent") is the same prompt run with NO agent definition adopted,
so the delta isolates what the agent definition is actually buying you.

Design notes:
- timing.json is optional. A missing file or field never breaks the run; the
  affected metric is reported as null and excluded from stats (explicit
  fallback, not a silent zero).
- Python 3.9 compatible (no match, no PEP 604 unions at runtime).
"""

import argparse
import json
import math
import os
import sys
from typing import Dict, List, Optional

CONFIGS = ("with_agent", "without_agent")


def _read_json(path: str) -> Optional[dict]:
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (json.JSONDecodeError, OSError) as exc:
        print("  warning: could not read {}: {}".format(path, exc), file=sys.stderr)
        return None


def _timing_seconds(timing: Optional[dict]) -> Optional[float]:
    if not timing:
        return None
    for key in ("total_duration_seconds", "executor_duration_seconds"):
        if isinstance(timing.get(key), (int, float)):
            return float(timing[key])
    if isinstance(timing.get("duration_ms"), (int, float)):
        return round(timing["duration_ms"] / 1000.0, 1)
    return None


def _timing_tokens(timing: Optional[dict]) -> Optional[int]:
    # Claude Code's Agent tool reports `subagent_tokens` in its <usage> block;
    # accept that and `total_tokens` (skill-creator's name) interchangeably.
    if not timing:
        return None
    for key in ("total_tokens", "subagent_tokens"):
        if isinstance(timing.get(key), (int, float)):
            return int(timing[key])
    return None


def _stats(values: List[float]) -> Optional[Dict[str, float]]:
    """mean/stddev/min/max over present values; None if nothing to report."""
    present = [v for v in values if v is not None]
    if not present:
        return None
    mean = sum(present) / len(present)
    if len(present) > 1:
        var = sum((v - mean) ** 2 for v in present) / (len(present) - 1)
        stddev = math.sqrt(var)
    else:
        stddev = 0.0
    return {
        "mean": round(mean, 3),
        "stddev": round(stddev, 3),
        "min": round(min(present), 3),
        "max": round(max(present), 3),
    }


def _collect(iteration_dir: str) -> List[dict]:
    runs = []
    for entry in sorted(os.listdir(iteration_dir)):
        eval_dir = os.path.join(iteration_dir, entry)
        if not os.path.isdir(eval_dir):
            continue
        for config in CONFIGS:
            run_dir = os.path.join(eval_dir, config)
            grading = _read_json(os.path.join(run_dir, "grading.json"))
            if grading is None:
                continue
            timing = _read_json(os.path.join(run_dir, "timing.json"))
            summary = grading.get("summary", {})
            expectations = grading.get("expectations", [])
            runs.append({
                "eval_name": entry,
                "configuration": config,
                "result": {
                    "pass_rate": summary.get("pass_rate"),
                    "passed": summary.get("passed"),
                    "failed": summary.get("failed"),
                    "total": summary.get("total"),
                    "time_seconds": _timing_seconds(timing),
                    "tokens": _timing_tokens(timing),
                },
                "expectations": [
                    {"text": e.get("text"), "passed": e.get("passed"),
                     "evidence": e.get("evidence")}
                    for e in expectations
                ],
            })
    return runs


def _summarize(runs: List[dict]) -> Dict[str, dict]:
    out = {}
    for config in CONFIGS:
        rows = [r for r in runs if r["configuration"] == config]
        if not rows:
            continue
        out[config] = {
            "pass_rate": _stats([r["result"].get("pass_rate") for r in rows]),
            "time_seconds": _stats([r["result"].get("time_seconds") for r in rows]),
            "tokens": _stats([r["result"].get("tokens") for r in rows]),
            "n_evals": len(rows),
        }
    return out


def _delta(summary: Dict[str, dict]) -> Dict[str, Optional[str]]:
    w, b = summary.get("with_agent"), summary.get("without_agent")
    if not w or not b:
        return {}
    out = {}
    for metric, fmt in (("pass_rate", "{:+.2f}"), ("time_seconds", "{:+.1f}"),
                        ("tokens", "{:+.0f}")):
        ws, bs = w.get(metric), b.get(metric)
        if ws and bs:
            out[metric] = fmt.format(ws["mean"] - bs["mean"])
        else:
            out[metric] = None
    return out


def _non_discriminating(runs: List[dict]) -> List[str]:
    """Assertions that pass in BOTH configs -> they don't measure agent value."""
    by_text = {}
    for r in runs:
        for e in r["expectations"]:
            text = e.get("text")
            if text is None:
                continue
            by_text.setdefault(text, {}).setdefault(r["configuration"], []).append(
                bool(e.get("passed")))
        # noqa
    flagged = []
    for text, per_config in by_text.items():
        w = per_config.get("with_agent", [])
        b = per_config.get("without_agent", [])
        if w and b and all(w) and all(b):
            flagged.append(text)
    return flagged


def _fmt_stat(stat: Optional[Dict[str, float]], suffix: str = "") -> str:
    if not stat:
        return "n/a"
    return "{:.2f} ± {:.2f}{}".format(stat["mean"], stat["stddev"], suffix)


def _write_markdown(path: str, agent_name: str, runs: List[dict],
                    summary: Dict[str, dict], delta: Dict[str, Optional[str]],
                    notes: List[str]) -> None:
    lines = ["# Benchmark: {}".format(agent_name), ""]
    lines.append("Baseline `without_agent` = same prompts, no agent definition adopted.")
    lines.append("")
    lines.append("## Summary (mean ± stddev across evals)")
    lines.append("")
    lines.append("| Configuration | Pass rate | Time (s) | Tokens |")
    lines.append("|---|---|---|---|")
    for config in CONFIGS:
        s = summary.get(config)
        if not s:
            continue
        lines.append("| `{}` | {} | {} | {} |".format(
            config,
            _fmt_stat(s["pass_rate"]),
            _fmt_stat(s["time_seconds"]),
            _fmt_stat(s["tokens"])))
    if delta:
        lines.append("| **delta** | {} | {} | {} |".format(
            delta.get("pass_rate") or "n/a",
            delta.get("time_seconds") or "n/a",
            delta.get("tokens") or "n/a"))
    lines.append("")
    lines.append("## Per-eval breakdown")
    lines.append("")
    lines.append("| Eval | Config | Pass rate | Passed/Total | Time (s) | Tokens |")
    lines.append("|---|---|---|---|---|---|")
    for r in runs:
        res = r["result"]
        pr = res.get("pass_rate")
        lines.append("| {} | `{}` | {} | {}/{} | {} | {} |".format(
            r["eval_name"], r["configuration"],
            "{:.2f}".format(pr) if pr is not None else "n/a",
            res.get("passed", "?"), res.get("total", "?"),
            res.get("time_seconds") if res.get("time_seconds") is not None else "n/a",
            res.get("tokens") if res.get("tokens") is not None else "n/a"))
    lines.append("")
    if notes:
        lines.append("## Analyst notes")
        lines.append("")
        for n in notes:
            lines.append("- {}".format(n))
        lines.append("")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def main() -> int:
    ap = argparse.ArgumentParser(description="Aggregate agent A/B eval runs into a benchmark.")
    ap.add_argument("iteration_dir", help="Path to iteration-N directory")
    ap.add_argument("--agent-name", required=True, help="Agent name for the report header")
    args = ap.parse_args()

    iteration_dir = os.path.abspath(args.iteration_dir)
    if not os.path.isdir(iteration_dir):
        print("error: not a directory: {}".format(iteration_dir), file=sys.stderr)
        return 2

    runs = _collect(iteration_dir)
    if not runs:
        print("error: no grading.json files found under {}".format(iteration_dir),
              file=sys.stderr)
        return 1

    summary = _summarize(runs)
    delta = _delta(summary)

    notes = []
    nd = _non_discriminating(runs)
    for text in nd:
        notes.append("Non-discriminating assertion (passes with AND without the agent): "
                     "“{}” — it doesn't measure what the agent adds.".format(text))
    # flag wide spread ACROSS evals (this is cross-task spread, NOT within-eval
    # flakiness — each eval is a single run in v1, so "run it more times" would
    # not change this number. See the single-run limitation in
    # docs/improving-agents.md.)
    for config in CONFIGS:
        s = summary.get(config, {}).get("pass_rate")
        if s and s["stddev"] >= 0.25:
            notes.append("Wide pass-rate spread across evals in `{}` (stddev {:.2f}) — "
                         "the agent is uneven across tasks (strong on some, weak on "
                         "others), not necessarily flaky.".format(config, s["stddev"]))

    benchmark = {
        "metadata": {
            "agent_name": args.agent_name,
            "iteration_dir": iteration_dir,
        },
        "runs": runs,
        "run_summary": dict(summary, delta=delta),
        "notes": notes,
    }

    json_path = os.path.join(iteration_dir, "benchmark.json")
    md_path = os.path.join(iteration_dir, "benchmark.md")
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(benchmark, fh, indent=2)
    _write_markdown(md_path, args.agent_name, runs, summary, delta, notes)

    print("wrote {}".format(json_path))
    print("wrote {}".format(md_path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
