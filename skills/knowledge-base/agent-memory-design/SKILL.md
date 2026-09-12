---
name: agent-memory-design
description: "Use when designing or auditing an agent's persistent memory (memory stores, session summaries, knowledge files, or a vector/graph memory layer) — covers rewrite-with-history vs append-only, multi-scope tagging, staleness/revision policy, and the research showing why naive memory degrades agent performance."
---

# Agent Memory Design

Research-backed patterns for agent memory systems. Sources are 2026 research
([docs/research/agentic-ai/2026-09-01-agent-memory-and-context.md](../../docs/research/agentic-ai/2026-09-01-agent-memory-and-context.md)
holds the full cited analysis). The headline finding: **memory is not a store, it
is a policy** — naive append-only memory measurably *hurts* agent performance.

## Why append-only memory fails

Two independent studies (2026):

- **ETH Zurich (arXiv 2602.11988)**: context/memory files add +20% average
  inference cost and help only when they carry *non-inferable* facts.
- **MemTrapBench (arXiv 2608.20202)**: *every* tested memory strategy reduced
  performance vs no memory — degradation came from what the memories said, not
  context length.

Named failure modes (use this vocabulary when diagnosing):

- **Reasoning fixation** — the agent reads a prior approach from memory and
  locks onto it even when the problem needs a different one.
- **Belief distortion** — the agent inherits a fact recorded as true, treats it
  as settled, and reasons on top of it. Same phenomenon as the hatch.org
  revision benchmark: memory systems confidently answer with stale versions of
  revised facts, beating a recency baseline by only ~1.5–20%.

> "A system that cannot expire a stale fact will hand the next agent a decision
> that was true in July and poison in September."

## The core pattern: rewrite-with-history

From the claude-rem design (jatingargiitk):
1. **Append never happens.** After each session, *rewrite* a short (~100-line)
   briefing of "what is true right now".
2. **Supersession check.** The harvester receives the previous briefing's open
   threads under an explicit "Prior STATE (for supersession check)" heading —
   every claim must survive contact with new evidence or it disappears.
3. **Rewrite-with-history.** Session digests are immutable; the briefing is
   rewritten, and every rewrite is a single commit — the audit trail lives in
   the diff. Expiry keeps the receipt.
4. **Context-file authoring rule** (from the ETH preprint + PostHog practice):
   keep only what the agent *cannot infer* from the repo (ports, PII rules,
   hard-won gotchas); cut derivable content; failed prompts become regression
   tests for the context itself; rewrite the file on a schedule (Boris Cherny:
   every 6 months) or it becomes a landfill.

## Patterns for a larger memory layer

From Mem0's *State of AI Agent Memory 2026* — **adopt the patterns, never the
vendor benchmark numbers** (independent reproduction failed by 26–37 points;
see the research note):

- **Multi-scope writes**: tag every entry with its scope — user / agent /
  run(session) / org — and compose scopes at retrieval time.
- **Multi-signal retrieval**: semantic + keyword (BM25) + entity matching,
  fused into one score, beats any single signal.
- **Standard benchmarks to know by name**: LoCoMo (multi-hop + temporal),
  LongMemEval (includes knowledge updates), BEAM (1M/10M-token scale).
- **Staleness is an open problem** — you need the revision policy above
  regardless of storage backend.

## Applying it to agent setups

- A memory store without a consolidation/supersession operation is a liability,
  not an asset. If the tooling offers batch "replace/consolidate" semantics,
  use them instead of adds.
- Schedule a periodic supersession audit: re-check each durable claim against
  current state; entries that fail get rewritten (not silently deleted — keep
  the receipt in session history).
- If the stack uses git: "git log your own memory and watch a belief change"
  is the cheapest audit tool that exists.
- **Write-ownership per lane** (@joerg_peetz, 2026-09): in multi-agent setups
  with shared lanes/stores, each lane gets an explicit write owner — one agent
  (or one consolidation job) may rewrite a lane's memory; others append
  session digests only. Concurrent writers to the same briefing race and
  silently drop each other's supersessions; single-writer-per-lane makes the
  rewrite-with-history audit trail unambiguous.
- **Forward-only memory typing + source-or-error lint** (@joerg_peetz MeMex
  Zero-RAG, 2026-09): tag every entry with a memory type (episodic / semantic
  / procedural) that only moves *up* — consolidation never downgrades old
  types; and enforce "every claim must have a source, otherwise it is an
  error" mechanically (lint on every change), not by instruction. Both keep
  the supersession audit trail trustworthy at scale.
- **Constraints do not survive compaction** (arXiv 2606.22528, 2026-09): rules
  living in conversation/context (policies from context files, old turns) are
  silently cut during compaction/summarization as "not the current sub-goal" —
  reproduced across 7 model families × 4 compaction strategies. Must-not-fail
  rules must be re-injected after every compaction or pinned system-level;
  never trust the summary to keep them.
- **The Demotion Ladder** (HackerNoon, 2026-09): the systematic mitigation for
  the above — as a rule proves fragile, walk it down rungs: prose → hook that
  re-injects it before compaction → restrict the write path → tests as
  definition of done → make illegal states unrepresentable. Field data
  (14 months): 4,000 lines of prose replaced by 13 hooks (~1,300 lines) —
  cost doesn't vanish, it moves and becomes auditable.
- **Context-file and skill hygiene** (2026-09-05): a context file is paid on
  every run — every line must name the failure it prevents or be deleted
  (~150-line ceiling; a fake command is worse than silence); stale
  instructions become active sabotage (an agent obeyed a superseded
  "never run gh pr merge" unquestioningly). Skill descriptions are short
  routing rules, not ads — harnesses truncate long descriptions, causing
  wrong-skill selection; and many skills never fire at all — verify with
  trajectory evals that a skill triggers before accumulating more.
- **Protect the prefix during compaction** (Random Attention, arXiv:2609.03430,
  2026-09-08): uniform random KV eviction *with the prompt pinned* matches
  sophisticated scoring methods while gaining 32–43% throughput — reasoning
  traces protect themselves through redundancy, so system prompt + task
  definition is the only fragile region when trimming context. Exception:
  non-redundant facts stated once (needle-type) must never be randomly cut.
- **Evolve context incrementally, never regenerate** (ACE/MCE, ICLR/ICML
  2026): maintain context as a playbook updated per-entry (add/merge/prune)
  from execution feedback; wholesale regeneration introduces brevity bias and
  context collapse. This is the research backing for per-entry edits and
  rewrite-with-history over file rewrites from scratch.

- **Memory quarantine: new memories must cool down before use (2026-09-10).**
  Independent practitioner confirmation of the recurring-twice promote rule:
  new memories enter a HOLDING state (stored but barred from
  decision-making) until a cooldown + cold review; ~40% (case-reported,
  unverified) evaporate during quarantine because they were startled
  reactions, not lessons. Never write a rule from a single event.
- **Import rejected decisions with an acceptance-check question (2026-09-10).**
  Agents repeat corrected mistakes because every session starts with zero
  organizational knowledge. When importing a decision — especially a rejection
  of an option that looked good due to constraints invisible in the final
  code — record *why* it was rejected, and attach an acceptance check phrased
  as a question you want answered; it measures whether the memory actually
  gets used by the next agent.
- **Second-brain sprawl counter-patterns (2026-09-10).** Letting an agent
  free-build a knowledge base from full conversation history fails the same
  way every time: notes land in files nobody chose, structures nobody
  approved. What works: the vault holds durable knowledge, agent memory holds
  identity + pointers only; the first-round prompt makes the agent write its
  own instructions (a direct instruction yields a single report — an audit,
  not a second brain); start with a small source set (cost is hard to
  predict); put an approval gate between every stage.

- **Embed abstractions, not raw content — and merge, don't add (Memora,
  Microsoft Research + Cambridge, 2026-09-12).** Memory collapse comes from
  embedding raw content into the vector store (fragmentation + wrong
  retrieval), not from small context windows. Embed only a short (~6–8-word)
  primary abstraction plus cue-anchor tags; keep the full content stored but
  un-embedded; new data on an existing topic *merges* into the original
  entry instead of spawning duplicates; retrieval is iterative navigation,
  not one-shot top-k.
- **Write-path control for agent-writable memory (OWASP ASI06 / MemoryTrap,
  2026-09-12).** A memory the agent "believes because it was written" is a
  persistence vulnerability: an ordinary workflow (clone repo → install a
  suggested dependency) planted a payload into persistent memory + global
  hooks + the system prompt, surviving across sessions, projects, and
  reboots. Anything the agent writes into memory/vault needs provenance
  (who wrote what, when), validation at *write* time (not read time), and an
  audit trail for every memory file. (Independent confirmation of the
  impact-log audit-trail pattern.)
- **AGENTS.md/context files are a table of contents, not an encyclopedia
  (OpenAI harness-engineering, 2026-09-12).** One giant context file fails
  because context is the scarce resource — the file squeezes out the actual
  task/code/docs and the agent misses constraints or optimizes the wrong
  thing. Keep context files as index + pointers into knowledge stored in the
  repo; knowledge that lives only in a person's head is invisible to the
  agent. (Reinforces the non-inferable-only authoring rule above.)

## References

- `docs/research/agentic-ai/2026-09-01-agent-memory-and-context.md` — full cited analysis with all sources
- arXiv 2602.11988 (ETH Zurich context files), arXiv 2608.20202 (MemTrapBench)
- https://hatch.org/2026/08/24/agent-memory-state-revision
- https://x.com/jatingargiitk/article/2091901298060952005
- https://mem0.ai/blog/state-of-ai-agent-memory-2026
- @joerg_peetz MeMex Zero-RAG: https://x.com/joerg_peetz/status/2094467733568286777 (repo: github.com/JPeetz/MeMex-Zero-RAG)
- arXiv 2606.22528 (Governance Decay / ConstraintRot — compaction deletes in-conversation constraints)
- arXiv 2609.03430 (Random Attention eviction — protect the prefix)
- https://miraflow.ai/blog/context-engineering-explained-mce-ace-2026 (ACE/MCE incremental context evolution)
- `docs/research/agentic-ai/2026-09-04-sandbox-context-integrity.md` — 2026-09-04 additions (§B1, §C)
- `docs/research/agentic-ai/2026-09-10-security-boundaries-memory-lifecycle.md` — 2026-09-10 additions (quarantine, decision acceptance checks, sprawl counter-patterns; sources: x.com/0xCodio/status/2096982132644106507, x.com/i/article/2097362674078331148, x.com/tomcrawshaw01/status/2097308735639265725)
- `docs/research/agentic-ai/2026-09-12-write-path-control-skills-sandboxes.md` — 2026-09-12 additions (abstraction-first embedding, write-path control, context-files-as-index; sources: x.com/marfinxx/status/2098184256677699929, x.com/mem0ai/article/2074509697689002254, openai.com/index/harness-engineering)
