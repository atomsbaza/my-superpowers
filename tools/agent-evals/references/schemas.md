# JSON Schemas (agent-evals)

The contracts the agent-eval harness reads and writes. Adapted from
skill-creator's schemas; the key difference is the `configuration` strings are
`with_agent` / `without_agent` instead of `with_skill` / `without_skill`.

`aggregate_benchmark.py` depends on these exact field names. Reference this
file when writing any of them by hand.

---

## evals.json

Defines the test set for one agent. Keep it in `tools/agent-evals/<agent-name>/evals.json`.

```json
{
  "agent_name": "principal-dotnet-engineer",
  "evals": [
    {
      "id": 1,
      "prompt": "Add a POST /orders endpoint that upserts by idempotency key against OceanBase via EF Core. Existing project is in ./src.",
      "expected_output": "An idempotent minimal-API endpoint + EF config that compiles and is safe on duplicate keys.",
      "files": [],
      "expectations": [
        "Solution compiles (dotnet build succeeds)",
        "Duplicate idempotency key does not throw and does not double-insert",
        "CancellationToken is threaded to the EF Core call"
      ]
    }
  ]
}
```

- `prompt` — the realistic task a user would actually give the agent.
- `expectations` — objectively verifiable statements (the discriminating ones).
  Write the prompts first; draft the expectations later, while runs are in flight.
- For subjective agents (e.g. `po-agent`), `expectations` may be empty — those
  are judged qualitatively. See `docs/improving-agents.md`.

---

## grading.json

Written by the grader (see `agents/grader.md`) into each run directory
(`with_agent/` and `without_agent/`). `aggregate_benchmark.py` reads
`expectations[].{text,passed}` and `summary.pass_rate`.

```json
{
  "expectations": [
    {
      "text": "Duplicate idempotency key does not throw and does not double-insert",
      "passed": true,
      "evidence": "Transcript step 4: upsert via INSERT ... ON DUPLICATE KEY UPDATE; integration test asserts single row."
    }
  ],
  "summary": { "passed": 2, "failed": 1, "total": 3, "pass_rate": 0.67 }
}
```

Field names are load-bearing: use `text`/`passed`/`evidence` (not
`name`/`met`/`details`).

---

## timing.json (optional)

Captured from the Agent tool's `<usage>` block (`subagent_tokens`, `tool_uses`,
`duration_ms`) and saved immediately into the run directory — it is not
persisted anywhere else. **Optional:** a missing file or field is reported as
`n/a` and excluded from stats; it never breaks the benchmark.

```json
{ "subagent_tokens": 8617, "tool_uses": 1, "duration_ms": 58375, "total_duration_seconds": 58.4 }
```

`aggregate_benchmark.py` reads `total_duration_seconds` (or falls back to
`executor_duration_seconds`, then `duration_ms / 1000`) and tokens from
`subagent_tokens` (or `total_tokens`, skill-creator's name — both accepted).

---

## benchmark.json + benchmark.md

Produced by `aggregate_benchmark.py <iteration-dir> --agent-name <name>`.

```json
{
  "metadata": { "agent_name": "principal-dotnet-engineer", "iteration_dir": "/abs/iteration-1" },
  "runs": [
    {
      "eval_name": "idempotent-upsert-endpoint",
      "configuration": "with_agent",
      "result": { "pass_rate": 1.0, "passed": 3, "failed": 0, "total": 3,
                  "time_seconds": 210.0, "tokens": 91000 },
      "expectations": [ { "text": "...", "passed": true, "evidence": "..." } ]
    }
  ],
  "run_summary": {
    "with_agent":    { "pass_rate": {"mean": 1.0, "stddev": 0.0, "min": 1.0, "max": 1.0}, "n_evals": 2 },
    "without_agent": { "pass_rate": {"mean": 0.58, "stddev": 0.12, "min": 0.5, "max": 0.67}, "n_evals": 2 },
    "delta": { "pass_rate": "+0.42", "time_seconds": "+60.0", "tokens": "+37000" }
  },
  "notes": [ "Non-discriminating assertion ... — it doesn't measure what the agent adds." ]
}
```

- `configuration` must be exactly `with_agent` or `without_agent`.
- `result.pass_rate` is nested under `result`, not top-level.
- `notes` are auto-generated (non-discriminating assertions, high-variance evals)
  — extend them with your own analyst observations before reviewing with a human.

The Markdown twin (`benchmark.md`) is the human-readable report; it is what you
show instead of a browser viewer.
