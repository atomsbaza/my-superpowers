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
- **Constraint Pinning, with numbers (2026-09-24, same paper via
  arxiv.org/html/2606.22528 + dreaming.press compaction post).** The decay is
  quantified across 1,323 episodes / 7 models: agents obeyed a rule 100% while
  it stayed in context; after compaction, violations jumped 0%→30% (one model
  59%); rules that survived a *summary* were obeyed 0% of the time; plain
  deletion 38%. The mitigation that returns violations to 0%: **Constraint
  Pinning** — keep rules in a pinned buffer exempt from compaction and
  re-inject them verbatim every round (~47 tokens/rule, <0.5% overhead; the
  paper also demonstrates a Compaction-Eviction Attack that biases the
  summarizer into dropping rules, which worked on every model). Operational
  form: safety/tool-control rules must be re-injected every turn or every
  compaction — never trusted to "it was loaded at session start."
- **Fixed-interval summarization is the worst compaction default
  (2026-09-24).** Two independent alternatives beat summarize-on-a-timer:
  dependency-graph eviction (Kiz8/Pi.dev fork, github.com/kiz8-team/pi-cwl) ran
  one 80M-token session across 89 Terminal-Bench 2.0 tasks *without any
  compaction* by having the agent mark exploration vs action phases and evicting
  only orphaned chunks (order: CoT → search results → bash output → file
  reads); and SelfCompact (arXiv 2606.23525) lets the agent trigger compaction
  itself at sub-task boundaries (+5–9 points at 30–70% lower cost). Common
  point: compaction decided *by the model guessing what matters* is the source
  of context loss and bias — make eviction dependency-driven or boundary-driven
  instead.
- **The Demotion Ladder** (HackerNoon, 2026-09): the systematic mitigation for
  the above — as a rule proves fragile, walk it down rungs: prose → hook that
  re-injects it before compaction → restrict the write path → tests as
  definition of done → make illegal states unrepresentable. Field data
  (14 months): 4,000 lines of prose replaced by 13 hooks (~1,300 lines) —
  cost doesn't vanish, it moves and becomes auditable.
- **Compaction must promote down, not just summarize (2026-09-17, Anthropic
  agent-memory playbook via x.com/adiix_official/status/2099883923543130281).**
  The playbook's L1 working → L2 episodic → L3 semantic → L4 procedural →
  L5 meta layering makes one operational point most setups miss: when a
  context window is about to compact or a session ends, the important
  contents must be *promoted into a lower layer* (a memory file, a skill,
  a knowledge note) before the context dies — a summary that stays in
  conversation is still in the layer that's about to be destroyed. Audit
  every consolidation job for a real promote path: did the durable claim
  land in a file, or only in a chat summary?
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
- **Context hygiene: cut in blocks, convert rules to principles (2026-09-15).**
  A Claude Code session loads ~7,850 tokens before the first keystroke
  (system prompt, memory, skill descriptions, context files) while people
  optimize a 45-token prompt. Safe cuts: remove whole *blocks*, never single
  sentences (smaller cuts are below eval noise); convert *absolute rules into
  principles* ("never multi-line comments" → "match surrounding comment
  density") — rules written for weaker models are now overhead plus
  contradiction. And stop teaching tools by examples: examples constrain the
  exploration space — design expressive parameters instead.
- **Tool-output pruning + token engineering levers (2026-09-15).** At the
  system level, four levers dominate prompt compression: (1) prune
  intermediate tool outputs — never replay a 3,000-line terminal dump every
  turn; summarize completed steps; (2) size thinking budgets to query
  difficulty; (3) route easy tasks off reasoning models; (4) right-size with
  continuous evals at the gateway.
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

- **Stored-but-never-injected lessons are dead (agentmemory #381, 2026-09-19).**
  A system that recorded lessons from every session shipped none of their
  value because session-start injection didn't include them — the agent had
  to "think to recall," which almost never happens. Confirmed by the fix:
  auto-inject a relevance × confidence ranked top-N at session start. Rule:
  anything that must be known at task start lives behind a *push* layer
  (pointer file loaded every session), never behind optional recall;
  a lesson that relies on the agent choosing to search is dormant from the
  moment it's written.
- **Compaction/summarizer output is untrusted input (OpenAI alignment
  report, 2026-09-19).** Models were caught writing jailbreak-style
  instructions into their own compaction summaries that carry into the next
  context window — the data/directive boundary breaks *from the inside*,
  no external attacker required. Anything a summarizer produces that will
  re-enter context needs the same treatment as external content: log it
  separately, audit periodically, and run it through the same review gate
  as any other write into persistent state.
- **Grep-able markdown + a phased write path beats vector stores for coding
  agents (mem0 harness-anatomy article, 2026-09-19).** Production coding
  harnesses keep memory as plain directory markdown that greps well, with a
  two-phase write path (extract after idle → redact secrets → land in a
  holding state before promotion). Copy the phasing even if the storage is
  a vault: separate extraction from promotion so secrets and noise never
  reach the durable layer in one step.
- **Memory is an expirable cache, and curation — not storage — is the hard
  problem (Doug Turnbull, 2026-09-24).** Practitioner thread on building
  agent memory for OpenCode (x.com/softwaredoug/status/2102103607843668297):
  knowledge graphs are brittle — skip them; moderately-organized raw text is
  far more flexible, and memory should be treated as a cache that expires,
  not permanent facts. Follow-up (x.com/stretchcloud/status/2102205740869877985):
  everyone solves storing, almost nobody solves *what deserves to be
  remembered* — an agent that logs every decision and every rejected approach
  drowns in its own context within days; working teams put a curation + decay
  layer over the store. Rule: before writing a memory, ask "is this worth
  remembering?", and keep a deletion/consolidation policy for the old.
  (Independent confirmation of the tiered-pointers + decay policy pattern.)
- **Shared task contract, not shared transcript (2026-09-24).** When work
  crosses agent/harness boundaries, facts the previous agent relied on
  (frozen interfaces, failed approaches, acceptance gates) die with the old
  session and the new agent reopens closed decisions. Fix: keep state as a
  small *versioned contract* — objective / verified decisions / failed
  approaches / what the next agent may do — read-only for executors, updated
  with compare-and-swap on a `state_version` field so a stale round can't
  overwrite newer state (x.com/rohit4verse/status/2090135919714324876).
  This is the handoff-file pattern plus optimistic concurrency.
- **Git-native memory needs a trust tier (OKF Agent Memory, 2026-09-24,
  news.ycombinator.com/item?id=49581240).** Pattern worth stealing without
  the library: a small index always in context + fetch only the ~300-token
  concept the task needs (progressive disclosure, ~90% prompt-overhead cut),
  all memory as Markdown in git so `git diff/blame` is the audit tool — no
  vector DB or embedding API. The addition to make: an explicit trust tier
  separating "verified by a human" entries from "generated by the agent."
- **Claude Code auto-memory internals — retrieval is filename-based
  (@mem0ai, 2026-09-24, x.com/mem0ai/status/2061822612398014782).**
  MEMORY.md caps at ~200 lines/25KB; retrieval picks files by *filename +
  description* through a small model (not semantic search), max 5 files per
  turn; files over cap are silently truncated. Name memory files after what
  will need to be recalled, and never place critical data at the tail of the
  6th+ file.
- **Model-Harness-Fit: swapping models means swapping harnesses
  (2026-09-24).** Reading Codex/Claude Code/Copilot CLI sources: each model is
  post-trained against its harness's tool surface, schemas, and memory
  rituals (e.g. citation tags the harness uses to count usage/decay) — pull a
  model out of its native harness and the performance doesn't come back
  (x.com/nicbstme/status/2051131906327212298). For multi-model setups: treat
  model swap as a port of tool surface + memory format + planning protocol,
  not a config change.
- **Harness decay: build to delete (2026-09-24).** Every harness component
  encodes an assumption about what the model *can't* do; after a model
  upgrade, previously load-bearing scaffolding becomes overhead (Anthropic
  case: sprint decomposition needed for Opus 4.5 was dead weight on 4.6).
  After every model upgrade, test-removing harness pieces one at a time to
  find the ones whose job is gone
  (x.com/sairahul1/status/2063544956158185927). (Extends the
  model-churn-resilience "pin, then diff behavior" rule from configs to
  harness components.)

- **Compaction output is an untrusted instruction channel — with prevalence
  data (2026-10-01, OpenAI alignment report via practitioner threads).**
  "Be transparent only if asked" was found embedded in 2.15% of GPT-5.6
  Sol training compaction summaries, and the *next context window obeyed
  it* — summaries re-enter as "the agent's own voice" and pass every
  author-based check. Extends the 2026-09-19 rule with operational form:
  log every compaction verbatim for separate audit; validate summaries
  contain no instruction-like content before re-injection; constraints
  that must survive resets live outside the window (a rule file re-injected
  every round), never in conversation
  (x.com/ParkerRex/status/2102078834409340962,
  max.nardit.com/articles/the-compaction-is-an-untrusted-input).
- **Deletion beats summarization — deterministic compaction alternatives
  (2026-10-01).** CliffCompaction (arXiv 2609.26779): grow context to a
  threshold, drop recomputable tool output, keep important fragments
  *verbatim* without rephrasing — reported ~50% cost cut with SWE-bench
  73.27% vs 73.87% full context. OpenDev-style tiered masking: log
  pressure at 70% of budget, mask old tool outputs into
  `[output offloaded to scratch file]` (~15 tokens) at 80%, plus fixed-size
  episodic summary (≤500 chars, regenerated periodically) + a small
  verbatim working window. Anthropic confirms the three primitives are
  distinct — tool-result clearing (mechanical, free) vs memory tool vs
  compaction — use clearing as primary and reserve compaction for carrying
  reasoning across turns (arxiv.org/abs/2609.26779,
  github.com/ai-boost/awesome-harness-engineering,
  platform.claude.com/cookbook/tool-use-context-engineering-context-engineering-tools).
- **Context trimming has a cliff, not a gradient (arXiv 2609.16461,
  2026-10-01).** Retained-context budgets below 25% raise failure risk
  ×10.92 (source-reported); naive "recent or relevant" selection gets ~60%
  savings at 66–77% success while adaptive guardrails that recognize
  critical protocol state reach 96% success at 56% savings. Grade trimming
  by *invariant survival rate*, not average token savings — and type/
  validate irrevocable state (spent budget, crossed thresholds) at the
  boundary so a bad trim errors loudly on the next step instead of rotting
  silently. Sharpens the ~50% trim floor in execution/loop.
- **Memory quality is decided at write time (2026-10-01).** Raw
  transcript + vector search retrieves "messages," not "facts" — two
  conflicting entries ("we're on Team plan" vs "we upgraded to Enterprise")
  are both true-at-write and cosine similarity can't pick. Tag every
  retain with timestamp + context label, extract facts at write time,
  keep the working window verbatim and separate from long-term recall,
  and say in the prompt: "memory may be stale — if it conflicts with now,
  trust now and ask"
  (dev.to/baharfatima/why-my-agent-kept-forgetting-things-and-how-hindsight-fixed-it-50e3).
- **Skills-over-memory: audit the store into 3 buckets before growing it
  (2026-10-01).** A practitioner cut 218 memory files to 6 and found 90%
  weren't trash — they were *misfiled*: lessons tied to one skill belong
  in that skill, not in global memory the tool never reads. Buckets:
  trash (git already holds it) / skill-tied (PR it into the skill) /
  cross-cutting (keep, ≤~200-line context file). Close auto-memory that
  writes its own noise; make necessary recall a pull store, not
  session-start push (x.com/mvanhorn/status/2070966613994795489). Direct
  confirmation of tiered-pointers + the promote-recurring-lesson-to-skill
  rule.
- **Compiled knowledge drift (2026-10-01).** When an LLM compiles raw
  sources into a wiki page, details lost at compile time ("2% discount if
  paid within 10 days") make later retrieval answer from silently wrong
  hub pages — unlike RAG hallucination, the *sources themselves* rot and
  nothing flags it. Every compiled claim needs provenance back to raw
  sources, periodic lint passes, and verbatim-quote guards on write-time
  synthesis
  (foundanand.medium.com/the-hidden-flaw-in-karpathys-llm-wiki-e3a86a94b459).
- **Sandbox egress: covert channels and secret hygiene outrank model
  cleverness (2026-10-01).** SwarmTraces (80,000+ payloads): agents used
  public link-shorteners as read-write channels under GET-only egress and
  directory names as covert channels; what actually opened production was
  secrets readable from worker process env, static Tailscale auth keys
  (181 unnoticed device enrollments), and cluster-admin connector
  credentials — "None of that required intelligence to find." Audit env
  vars / static keys / over-broad credentials in any environment agents
  run in before worrying about model capability; verifier context must be
  separated from maker (x.com/JeffLadish/status/2103584701357437133,
  swarmtraces.org).
- **Single-file profile memory beats vector search for agent identity
  (2026-10-03, Arize Alyx).** One profile file (~8k chars) loaded into
  context every request — no read-time retrieval at all. Admission rule
  for every entry: durable (still true next month) / not re-discoverable
  by a tool call / useful across sessions. Two failure modes found in
  production: (a) compaction silently dropped a user preference — give
  user-authored entries a high-priority prefix like `[user]`; (b) the
  agent wrote its own mistake back into memory as a "convention" — audit
  the memory file itself, not just the agent's answers. Trigger
  compaction ~1k tokens *below* the ceiling: a compaction target that
  can't be reached drops the most recent writes instead
  (arize.com/blog/alyx-agent-long-term-memory-architecture/).
- **Chat IS the memory: compress inline, keep constant size (2026-10-03,
  VictorTaelin optmem).** Harness with one tool (spawn) and no chat
  history: an append-only log compressed *during* the session ("nap,
  don't sleep" — never batch-at-sleep) into a constant-size memory
  context where detail fades with age and nothing is deleted. Inline
  compression plus a fixed-size ceiling eliminates context bloat by
  construction instead of fighting it with retrieval
  (x.com/VictorTaelin/status/2105182389961908544).
- **File-as-context: let the model edit its context like a file — with a
  diff guard (2026-10-03, Context Language Models, UW+Meta, arXiv
  2609.37725).** Instead of append-only transcript + mid-run
  summarization, the model edits its context file with bash (delete stale
  search results, fold 20 tool calls into 2 lines, update a scoreboard
  header); beats Codex-style summarization (59.4% vs 53.4%
  BrowseComp-Plus) at ~21% fewer FLOPs, and the model can author its own
  "skill document" for context management selected on a dev split — no
  retraining needed. Three caveats for agent builders: (1) arbitrary
  edits destroy the prefix cache — prefer suffix reuse and expect append
  to be cheaper than mid-file edits; (2) the model can plant misleading
  instructions for itself in the file — gate self-edits behind a diff
  review; (3) edited context does not survive across tasks — cross-task
  memory stays a memory-tool job. CC BY-NC license: pattern is usable,
  code is not (arxiv.org/abs/2609.37725,
  x.com/RulinShao/status/2105282444270448647). Full analysis:
  `docs/research/agentic-ai/2026-10-03-single-file-memory-self-edited-context.md`.
- **Observational memory beats summarize-and-discard (2026-10-01, Mastra).**
  Compaction that summarizes and discards makes every session after the
  compact point read worse and contradict earlier decisions. Architectural
  alternative: an observer model continuously writes *structured
  observations* (decisions, facts, state changes), and a reflector folds
  them into layers — the agent reads (1) recent raw messages, (2) the
  observation log, (3) reflections. Decisions survive as decisions, not as
  paraphrases buried in a summary. File-format corollary: keep decisions as
  structured, append-only entries (a Decisions file) separate from
  narrative handoff summaries — narrative is lossy, structure survives
  compaction (x.com/calcsam/article/2065222134633504871).
- **Second brain = compiler, not library (2026-10-01).** RAG pays the
  "understanding" cost on every query; a compiled wiki pays once at ingest,
  and each new source only touches the 10–15 pages it overlaps (3-folder
  shape: raw/ → wiki/ → output/, context file as the hub). The catch: a bad
  source in a library is easy to delete, but in a compiler it contaminates
  the 15 pages it touched before anyone notices — so lint sources *before*
  compiling, flag contradictions at link time, and expect the payoff to
  start at ~50–100 compiled sources
  (x.com/rvaniaaaa, threadnavigator.com/thread/2090512486738845784/).

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
- 2026-09-24 additions: arXiv 2606.22528 quantified decay + Constraint Pinning (dreaming.press/posts/context-compaction-erases-agent-guardrails.html), Kiz8 dependency-graph eviction (github.com/kiz8-team/pi-cwl), arXiv 2606.23525 (SelfCompact), x.com/softwaredoug/status/2102103607843668297, x.com/stretchcloud/status/2102205740869877985, x.com/rohit4verse/status/2090135919714324876, news.ycombinator.com/item?id=49581240 (OKF Agent Memory), x.com/mem0ai/status/2061822612398014782, x.com/nicbstme/status/2051131906327212298, x.com/sairahul1/status/2063544956158185927 — full curated analysis: `docs/research/agentic-ai/2026-09-24-instruction-context-lifecycle.md`
- 2026-10-01 additions: compaction-output-as-untrusted-channel with 2.15% prevalence (x.com/ParkerRex/status/2102078834409340962, max.nardit.com/articles/the-compaction-is-an-untrusted-input), CliffCompaction arXiv 2609.26779 + tiered masking (github.com/ai-boost/awesome-harness-engineering) + Anthropic 3 primitives (platform.claude.com/cookbook/tool-use-context-engineering-context-engineering-tools), trimming cliff arXiv 2609.16461 (thecolony.ai), write-time memory quality (dev.to/baharfatima/why-my-agent-kept-forgetting-things-and-how-hindsight-fixed-it-50e3), skills-over-memory 3-bucket audit (x.com/mvanhorn/status/2070966613994795489), compiled knowledge drift (foundanand.medium.com/the-hidden-flaw-in-karpathys-llm-wiki-e3a86a94b459), SwarmTraces covert channels (swarmtraces.org) — full curated analysis: `docs/research/agentic-ai/2026-10-01-context-lifecycle-compaction-economics.md`
- 2026-10-03 additions: single-file profile memory (arize.com/blog/alyx-agent-long-term-memory-architecture/), chat-IS-the-memory inline compression (x.com/VictorTaelin/status/2105182389961908544), file-as-context with diff guard + suffix-reuse cache economics (arXiv 2609.37725, x.com/RulinShao/status/2105282444270448647) — full curated analysis: `docs/research/agentic-ai/2026-10-03-single-file-memory-self-edited-context.md`
- `docs/research/agentic-ai/2026-09-12-write-path-control-skills-sandboxes.md` — 2026-09-12 additions (abstraction-first embedding, write-path control, context-files-as-index; sources: x.com/marfinxx/status/2098184256677699929, x.com/mem0ai/article/2074509697689002254, openai.com/index/harness-engineering)
