# Vault-as-production: 6 ways to let AI read an Obsidian vault (2026-10-01 digest)

Source: <https://datameerkat.com/six-ways-to-let-ai-read-my-obsidian-vault>
(long-form postmortem from the "VIKI" setup — 3,137 notes, scheduled jobs
running at 02:00). Consolidated from the X-scout digest of 2026-10-01
(cron job f933f5a8d591, Discord thread #xTreand). All numbers as reported
by the source — unverified.

## Why this matters

It is one of the few write-ups of an agent-managed Obsidian vault that has
run long enough to accumulate *production failures*, and the failures map
one-to-one onto cron/heartbeat/reporting-contract problems in any agent
setup (Hermes included).

## The three failures that teach mechanism

1. **Silent empty-toolbox spawn.** Sub-agents locked to MCP-only tools
   still spawned when the MCP server was down — with an empty tool list —
   and refused their tasks one by one without ever erroring. 132 refusals
   were found only by auditing 44 job logs. "Green" job runs meant nothing
   because no job declared its expected output. Fix: every automated job
   states its expected output up front; tool availability is verified at
   agent startup; refusals are surfaced as failures, not swallowed.
2. **Unannounced truncation.** Retrieval rankings that hit a token/size
   ceiling returned silently truncated results that looked like complete
   result sets. Fix: ranking happens on the backend; the model reads only
   candidates; truncated sets carry an explicit partial marker. Reported
   effect of the restructure (auto-generated ~400-token vault map +
   candidate-only reads): 12 turns/202k tokens → 6 turns/69k tokens on
   their benchmark task.
3. **Basename link resolution.** Resolving wiki links by file basename
   breaks on duplicates and symlinks. Fix: stable IDs (GUID-style) for
   link targets. Directly relevant to symlinked vault roots (e.g. a
   `Work` symlink pointing into the real vault): resolve by real path or
   ID, never by display name.

## Merge targets

- `skills/quality/ai-agent-security/SKILL.md` — silent empty-toolbox
  failure + declare-expected-output corollary (merged 2026-10-01).
- Hermes-side analogues: kanban reporting contract (workers must report
  results), monitor-gated heartbeats (output must change to matter).

## Related in-repo notes

- `docs/research/agentic-ai/2026-10-01-context-lifecycle-compaction-economics.md`
  — same-week compaction/cache findings.
- `skills/knowledge-base/agent-memory-design/SKILL.md` — "second brain =
  compiler, not library" + observational memory (merged 2026-10-01).
