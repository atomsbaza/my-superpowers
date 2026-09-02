# AGENTS.md

Context files only help with non-inferable constraints (arXiv 2602.11988).
Everything else: infer from repo structure, or run tools/agent-evals/scripts/doctor.py.

## Non-inferable constraints

- Run `python3 tools/agent-evals/scripts/doctor.py --repo .` before committing
  any skill/agent edit — ERROR findings are blocking.
- When the skill/agent set changes, keep three files in sync:
  the file itself, README.md table, ATTRIBUTION.md.
- Coding may be delegated to Claude Code (GLM plan) per orchestrator's rules —
  but agents never commit; the orchestrator verifies on disk and commits.
