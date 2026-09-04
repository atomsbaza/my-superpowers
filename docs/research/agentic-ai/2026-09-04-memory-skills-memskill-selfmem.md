# Memory as Skills: MemSkill, SelfMem, and the 2026 Memory-Skills Landscape

Research note compiling three complementary 2026 works on self-evolving agent
memory, read from primary sources (arXiv HTML). Companion to
[2026-09-01-agent-memory-and-context.md](./2026-09-01-agent-memory-and-context.md)
(memory policy findings) and
[2026-09-04-wikiskill-persistent-knowledge.md](./2026-09-04-wikiskill-persistent-knowledge.md)
(WikiSkill). All numbers quoted from the papers.

## The landscape in one table

| | WikiSkill (Google) | MemSkill (NTU/UIUC) | SelfMem |
|---|---|---|---|
| arXiv | [2608.27454](https://arxiv.org/abs/2608.27454) | [2602.02474](https://arxiv.org/abs/2602.02474) v2 | [2607.03726](https://arxiv.org/abs/2607.03726) |
| Core question | What knowledge should skill evolution build on? | Which memory operation applies to this context? | What memory *strategy* fits this task? |
| Mechanism | Persistent wiki + skill proposer + validation gating | RL-trained skill selector + LLM designer evolving the skill bank | Agent explores memory tools with feedback, refines its own strategy |
| Skills evolve? | Yes (proposer + gate) | Yes (designer, two-stage) | Strategy-level (agent-driven) |
| Who picks skills? | Force-injected (retrieval out of scope) | Learned controller (Top-K, RL) | The agent itself |
| Rollback | Skills only; **wiki never rolled back** | Skill-bank snapshot + rollback if worse | None described |

The three answer *different* layers of the same problem: WikiSkill = what to
accumulate, MemSkill = what to apply per moment, SelfMem = how to meta-optimize
the approach. They compose conceptually rather than compete.

## MemSkill (arXiv:2602.02474, ICML-format, Feb 2026)

**Thesis:** hand-designed memory operations (add/update/delete/skip) bake in
human priors and go rigid. Instead, treat memory operations as *learnable,
evolvable skills*.

**Architecture — three components:**

1. **Controller** (trainable, RL): per text *span* (not turn), selects a Top-K
   subset of memory skills from a shared skill bank, conditioned on the current
   span + retrieved existing memories. Scores skills via semantic distance
   (embedding of skill *description* — compact and stable, not full content).
   Ordered Top-K without replacement via Gumbel-Top-K; trained with PPO using
   downstream task performance as reward.
2. **Executor** (frozen LLM): applies the selected skills in **one pass** per
   span to produce structured memory updates — span-level one-pass processing
   is what cuts cost vs turn-by-turn pipelines.
3. **Designer** (frozen LLM, periodic): reviews a sliding **hard-case buffer**
   (query-centric failures, two expiration rules: max step-age or capacity),
   clusters them (KMeans), picks representatives by difficulty score (low task
   performance × repeated failure), then in two stages: analyze what memory
   behaviors are missing → propose edits to existing skills and brand-new
   skills. Keeps a **snapshot of the best skill bank and rolls back** if an
   update degrades performance; early-stops when updates stop helping;
   briefly boosts exploration toward newly added skills after each evolution.

**Skill anatomy** (matches AgentSkills conventions): short description (for
selection) + detailed content spec: *purpose / when to use / how to apply /
constraints / action type*. Bank initialized with just 4 primitives (Insert,
Update, Delete, Skip); the designer grows the rest (e.g. CAPTURE_ACTIVITY_
DETAILS, CAPTURE_TEMPORAL_CONTEXT — domain-specialized, data-driven).

**Results:**
- Beats MemoryBank, A-MEM, Mem0, MemoryOS, LangMem, ReadAgent, CoN on LoCoMo,
  LongMemEval, HotpotQA, ALFWorld with both LLaMA3.3-70B and Qwen3-Next-80B.
- LoCoMo L-J: 53.82/54.14 (LLaMA/Qwen) — A-MEM 49.71/50.30, MemoryOS 48.64/47.37.
- ALFWorld success rate 80.36/81.29 with *fewer* steps than baselines.
- **Ablation (LoCoMo L-J):** full 53.82 → w/o designer 46.50, w/o controller
  (random selection) 48.43, refine-only 47.45 (LLaMA). **Evolving the skill
  bank matters more than selecting from a fixed one**; adding new skills beats
  refine-only. Under Qwen the designer matters even more (54.14 → 36.15).
- **Cost (LoCoMo, span=512):** L-J 53.82 with 249K input / 18K output tokens /
  215 LLM calls — vs A-MEM 2850K/362K/1548 calls at 49.71. Span size is the
  cost/quality knob (SS=1024 degrades: 48.11).
- Transfers under distribution shift and to smaller models (appendix).

## SelfMem (arXiv:2607.03726, Jul 2026)

**Thesis:** don't put the agent inside a fixed retrieval/compression/update
pipeline — give it **memory tools + feedback signals** and let it explore,
evaluate, and refine its own memory strategy ("teach an agent to fish").

**Results:** on BEAM (100K–1M token conversations) vs the strongest baseline:
+48.7% (100K), +40.8% (500K), +41.9% (1M) on the official score; broad
robustness across question types; model-guided strategy refinement adds
further gains.

**Positioning:** the most radical of the three — no skill bank, no designer,
no gating; the strategy lives in the agent's own exploration. Costly to run
but assumption-free. Note the missing rollback story — unbounded
self-modification is exactly what WikiSkill's gating and MemSkill's snapshots
protect against.

## Survey: Memory for Autonomous LLM Agents (arXiv:2603.07670, Mar 2026)

Single-author survey (2022 → early 2026) formalizing memory as a
**write–manage–read loop** coupled to perception/action, with a 3-axis
taxonomy: **temporal scope × representational substrate × control policy**.

- **Five mechanism families:** context-resident compression,
  retrieval-augmented stores, reflective self-improvement, hierarchical
  virtual context, policy-learned management.
- **Evaluation shift:** from static recall benchmarks → multi-session agentic
  tests interleaving memory with decisions (4 recent benchmarks analyzed).
- **Engineering realities it names:** write-path filtering, contradiction
  handling, latency budgets, privacy governance.
- **Open challenges:** continual consolidation, causally grounded retrieval,
  trustworthy reflection, learned forgetting, multimodal embodied memory.

Use as the map: every memory system (including ours) is a point in the
taxonomy — e.g. our Wiki loop = long temporal scope, markdown substrate,
human-gated control policy.

## Audit: the Hermes Wiki loop against this literature

Our implementation (see the WikiSkill note's adaptation section) scored
against the three papers:

| Literature mechanism | Wiki loop status | Verdict |
|---|---|---|
| Persistent, never-rolled-back knowledge | `patterns/` + never delete on reject; housekeeping only after 1 month unused + skill coverage | ✅ aligned |
| Rejected-proposal audit trail | `impact-log.md` Accepted/Rejected rows | ✅ aligned |
| Designer reviews hard cases periodically | Daily consolidate cron reads yesterday's failures (≤5 fail + ≤3 pass) | ✅ aligned |
| Snapshot + rollback on degradation | None — a promoted rule is fixed by editing, not reverted | ⚠️ gap: add "capture rule state before edit" (tree/commit) so a bad promotion can be rolled back |
| Selection control (only relevant knowledge per task) | Manual: orchestrator reads index at triage, workers never see the catalog | ✅ equivalent at our scale (10–30 patterns; no retrieval needed yet) |
| Strategy self-optimization (SelfMem) | None | ⚠️ out of scope by design — human-gated policy |
| Cost lever (span-level one-pass) | N/A (no per-turn extraction pipeline) | n/a |

**Actionable takeaways:**
1. **Snapshot before promoting/editing rules** (from MemSkill's rollback):
   promoted rules should live in git or with a dated copy so a Rejected
   promotion has a restore point.
2. **Difficulty scoring for consolidation** (from MemSkill's designer): the
   daily cron already picks failures, but ranking them by
   "low performance × repeated occurrence" would pick better representatives
   — this is effectively what the ≥2-recurrence promote gate encodes, so the
   design transfers without RL.
3. **Skill description = selection key** (from MemSkill): keep the first line
   of each pattern file and the index table crisp — it is what the
   orchestrator actually selects on.
4. **Beware unbounded self-modification** (SelfMem's missing rollback): our
   human-approval gate for promotions is the safeguard; keep it.

## Reproduce / verify

- MemSkill full text: <https://arxiv.org/html/2602.02474v2> (ablation table 2,
  cost table 3, evolved-skill case studies appendix C), code:
  <https://github.com/ViktorAxelsen/MemSkill>
- SelfMem: <https://arxiv.org/abs/2607.03726>
- Survey: <https://arxiv.org/abs/2603.07670>
