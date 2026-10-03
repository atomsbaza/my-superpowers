# Single-file memory, self-edited context, and proving agent permissions

> Adapted from X-scout digests of 2026-10-03 (Discord thread #xTreand, cron
> job f933f5a8d591). Consolidated from 6 batches; 13 raw items → 8 kept.
> All figures are as reported by the cited sources — unverified by us.

## 1. Single-file profile memory (Arize Alyx)

Source: https://arize.com/blog/alyx-agent-long-term-memory-architecture/

Alyx dropped vector search entirely: one profile file (~8k chars) is loaded
into context on every request; there is no read-time retrieval. Admission
rules for every entry:

1. **Durable** — still true next month.
2. **Not re-discoverable** by a tool call (if a search can find it, don't
   memorize it).
3. **Cross-session** — useful in more than one session.

Production failure modes and fixes:

- **Compaction dropped a user preference.** User-authored entries now get
  a high-priority prefix (`[user]`) so compaction preserves them.
- **The agent wrote its own mistake back into memory as a "convention."**
  The fix is procedural: audit the memory file itself, not just the
  agent's answers. (Mirrors the repo's write-path-control pattern —
  provenance + audit trail for agent-writable memory.)
- **Trigger compaction ~1k tokens below the ceiling.** A compaction whose
  target size can't actually be reached drops the most recent writes
  instead of the oldest.

## 2. "Chat IS the memory" (VictorTaelin optmem)

Source: https://x.com/VictorTaelin/status/2105182389961908544

A harness with a single tool (spawn) and no chat history: an append-only
log is compressed *during* the session ("nap, don't sleep" — compression
is inline, never a batch job at sleep time) into a constant-size memory
context. Detail fades with age; nothing is deleted. Two transferable
points: compression must happen mid-session, and a constant-size memory
eliminates context bloat by construction rather than fighting it with
retrieval.

## 3. Context Language Models (UW + Meta, arXiv 2609.37725)

Sources: https://arxiv.org/abs/2609.37725 ·
https://x.com/RulinShao/status/2105282444270448647 ·
https://dev.to/gaurav_dadhich/context-language-models-what-the-uw-and-meta-paper-changes-for-agent-builders-and-what-it-leaves-40a7

Replace append-only transcript + threshold summarization with a context
file the model edits itself via bash (delete stale search results, fold 20
tool calls into 2 lines, update a scoreboard header). Reported results:
59.4% vs 53.4% on BrowseComp-Plus (vs Codex-style summarization) at ~21%
fewer FLOPs; the model authors its own "skill document" for context
management, selected on a dev split — no retraining.

Caveats the authors acknowledge:

1. **Arbitrary edits destroy the prefix cache.** They propose Prefix-Reuse
   FLOPs and Suffix Cache Reuse as metrics/techniques. Practical
   corollary: appending to a planning file is cheaper than editing its
   middle.
2. **The model can plant misleading instructions for itself** in the
   context file — self-edits need a diff-review guard.
3. **Edited context does not survive across tasks** — cross-task memory
   remains a memory-tool job. License CC BY-NC: adopt the pattern, not
   the code.

## 4. Proving agent permissions (security doctrine)

Sources:
https://dev.to/ianwieds/stop-eyeballing-your-agents-permissions-prove-them-57kd ·
https://wpnews.pro/news/a-coding-agent-s-permissions-need-a-negative-test

- **Counterexample proving (NVIDIA OpenShell `openshell-prover`, SMT/Z3):**
  feed child policy + parent boundary to the solver; it searches for a
  concrete request the child allows but the parent forbids. Real finds:
  a `git-remote-https` policy that permits clone but also permits push,
  and one interpreter entry in a rule extending reach to everything the
  interpreter can invoke. Doctrine: whenever an agent spawns sub-agents,
  run the prover on child-policy-vs-parent-boundary every time (exit 0 =
  allow; anything else = human review). Tools that answer "unsupported"
  beat tools that silently pass.
- **Negative-test taxonomy (4 states):** attempt each forbidden action
  against a throwaway repo with fixture paths holding dummy tokens;
  record each result as unexposed / runner-rejected / agent-declined /
  executed. Only the first two are enforcement — *agent-declined proves
  nothing* because it changes with the next prompt. Also test the
  patch-apply and stop/reconnect paths separately: an agent blocked from
  writing files directly can still propose patches another component
  applies.
- **MCP behavioral grading:** install servers in gVisor, call every tool
  with schema-generated args (no LLM in the loop — reproducibility),
  plant canary credentials in every secret-looking env var, watch DNS and
  egress. Across 20 popular servers: 4 contacted undeclared hosts (mostly
  third-party telemetry), 0 leaked canaries. Static scans and
  self-declared annotations miss "phones home to a company you've never
  heard of." Canary pitfall: never canary `AWS_REGION`-style variables —
  SDKs construct hostnames from them (false positives)
  (https://dev.to/agentavow/we-started-running-every-mcp-server-we-grade-heres-what-20-popular-ones-actually-did-53ik).

## 5. Smaller items

- **Claude Code deletes session transcripts after 30 days by default**
  (background sweep). Fix: `"cleanupPeriodDays": 3650` in
  `~/.claude/settings.json` (0 is rejected). Transcripts are free evals —
  engineer-corrected sessions are more accurate test cases than synthetic
  ones (Anthropic analyzed 200k sessions) — but the files are plaintext
  and contain .env/token material: scrub before sharing
  (https://ccassist.dev/blog/where-claude-code-stores-conversations/ ·
  https://quesma.com/blog/agent-session-transcripts-are-precious/).
- **State of AI Agent Memory 2026 (Mem0 — methodology only, vendor
  numbers unverified):** standard benchmarks (LoCoMo, LongMemEval, BEAM)
  measure accuracy *and* token/query *and* latency together — a system
  that is accurate but spends 26K tokens/query is not production-viable.
  Patterns: multi-signal retrieval (semantic + keyword + entity, fused)
  beats any single signal; multi-scope tagging (user/agent/session/app)
  with scope composition at retrieval
  (https://mem0.ai/blog/state-of-ai-agent-memory-2026).
- **Harness engineering (X Article):** when an agent fails repeatedly,
  fix the failure *class* (the harness), not the run; keep a change
  receipt per run (how the output was produced) to compare model upgrades
  and trace regressions
  (https://x.com/i/article/2093685107534000560).
- **Knowledge work engineering (X Article):** knowledge should persist as
  links (decision ↔ evidence ↔ derived work) in typed markdown + skills +
  tools + views inside one agent repo; when a decision depends on an
  assumption, model that relationship so it can be revisited
  (https://x.com/arscontexta/status/2105397004226494487).

## Where this went in the repo

- `skills/knowledge-base/agent-memory-design/SKILL.md` — sections 1–3 as
  three dated patterns (single-file profile, chat-IS-memory, file-as-
  context with diff guard).
- `skills/quality/ai-agent-security/SKILL.md` — section 4 as negative-test
  doctrine in "Build safe evaluation cases" + MCP behavioral grading in
  the attack-path list.
