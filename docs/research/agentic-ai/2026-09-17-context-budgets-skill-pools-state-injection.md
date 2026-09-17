# Context Budgets, Skill-Pool Collapse, and State-Borne Injection (2026-09-17)

Three themes from the 2026-09-17 X-scout digest (Discord thread #xTreand,
cron job f933f5a8d591). Numbers are as reported by the cited sources and
are **unverified** per this repo's vendor-numbers rule; mechanisms were
confirmed across independent sources or published papers.

## A. Context budgets — how much you may cut before agents fail

**Core evidence: [arXiv:2609.16461](https://arxiv.org/abs/2609.16461)** (15
Sep 2026) compares five context-trimming strategies in agentic workflows:

- Naive recency/summarization trimming: ~60% token savings, but task success
  drops to 67–77%.
- Protocol-aware trimming + adaptive budget guardrails: 96% success at 56%
  savings.
- Key number: a retained-context budget ≤25% increases failure odds ~11×
  vs ≥50%.

**Companion evidence** (same digest): the Long-Horizon Agents primer
([x.com/agihouse_org/status/2090823305481822470](https://x.com/agihouse_org/status/2090823305481822470))
reports per-step accuracy of 99% yields ~0.004% end-to-end success at 1,000
steps, and identifies **scratchpad persistence as the strongest predictor**
of long-horizon success (YC-Bench).

And a caution for anyone monitoring agents: **"Corrupt Plans, Clean Traces"**
(arXiv, listed 15 Sep 2026 — no abs ID at collection time) shows attackers
can inject a corrupted plan while the chain-of-thought trace remains clean —
traces are not ground truth for agent intent; check trace against
action/environment state.

**Takeaway:** trimming is safe only above a floor. Keep protocol-critical
state (tool state, unresolved dependencies) first; token savings second.
Never decide an agent did its job from a clean transcript alone — verify
against on-disk state.

Merged into: `skills/execution/loop/` (trim-floor rule), and referenced by
`skills/quality/ai-agent-security/` (trace ≠ ground truth).

## B. Skill-pool collapse — library size has a measurable cliff

**Core evidence: [arXiv:2608.14036](https://arxiv.org/abs/2608.14036)** (via
mindpattern.ai):

- 65.7% of the benefit of agent skills comes from *procedural anchoring*
  (the check-this-first / run-tests-after-edit sequence), not knowledge
  injection.
- Growing the skill pool from 5 to 100 collapses correct-skill selection
  from ~29.6% to ~3.3% (paper numbers, unverified at replication).

This quantifies the 2026-09-05 digest's qualitative finding (description
truncation causes wrong-skill selection) and lands directly on this repo's
own ~150-file backlog: the correct policy is **prune before add** — audit
which skills actually fired last month, prune or demote the rest
(`disable-model-invocation` for keep-but-don't-load), before adding more.

Merged into: `skills/tools/writing-great-skills/` (library-level hygiene:
procedural anchoring, pool-size cliff, prune-before-add) and reflected in
`skills/knowledge-base/agent-memory-design/` (memory/notes pools obey the
same shape — promote proven entries down a layer instead of accumulating).

## C. State-borne injection — the persistent store is the attack surface

**Core evidence: XSPI, [arXiv:2606.04425](https://arxiv.org/html/2606.04425v2)**:
injection payloads planted in persistent state (memory, filesystem, notes)
activate in the *next* session; four tested guardrails caught only 0–15% at
planting time and 0.4–36% at activation time.

**Re-confirmed from primary source:** Framing Gap
([arXiv:2608.27092](https://arxiv.org/abs/2608.27092)) — models can refuse
explicit injections, yet leak the same payload at near-100% when it is
reframed as a "config field / integrity signature". The working defense is
payload-blind: infra-level destination allow-lists and planner/reader
capability separation (already in `ai-agent-security` since 2026-09-05;
now cited from the primary paper).

**Takeaway for knowledge stores:** anything arriving from outside (web,
tool output) must pass a review gate *before* it crosses into persistent
state, and must carry provenance. "It's in the vault already" is not
evidence it was vetted.

Merged into: `skills/quality/ai-agent-security/` (state-borne injection
window; review gate before the persistent-store boundary).

## Skill-pool hygiene for this repo (application note)

Applying theme B to this repository itself: the 2026-09-17 additions below
are *extensions to existing skills*, not new skills. New skills proposed
from this digest: none — all four candidates (scratchpad/trim rules,
skill-pool hygiene, state-borne injection, cron self-improvement rules)
merge into existing skills, matching the prune-before-add policy this
digest teaches.

## Sources

- https://arxiv.org/abs/2609.16461 (context trimming strategies)
- https://x.com/dair_ai/status/2100250366495625320 (paper review)
- https://x.com/agihouse_org/status/2090823305481822470 (long-horizon primer)
- arXiv cs.AI listing, 15 Sep 2026 — "Corrupt Plans, Clean Traces" (no abs ID at collection)
- https://arxiv.org/abs/2608.14036 (skill retrieval collapse / procedural anchoring)
- https://mindpattern.ai/blog/2026-08-17 (secondary summary of 2608.14036)
- https://arxiv.org/html/2606.04425v2 (XSPI state-borne injection)
- https://arxiv.org/abs/2608.27092 (Framing Gap, primary source)
- https://mielony.com/blog/self-improvement-by-cron (cron-driven self-improvement rules)
- https://x.com/adiix_official/status/2099883923543130281 (Anthropic 5-layer memory playbook summary)
- https://x.com/ericzakariasson/status/2094818067905941886 (fleet ops — confirmation only)
- https://x.com/davidondrej1/status/2094424967345496191 (self-host sessions — confirmation only)
- https://x.com/0xCodio/status/2096982132644106507 (memory quarantine — duplicate of 2026-09-10)
- https://x.com/mem0ai/status/2061822612398014782 (mem0 staleness — duplicate, vendor numbers banned)
- https://x.com/iHarnoorSingh/article/2072878522633458009 (Obsidian-vs-RAG — skipped: disclosure of interest, confirms 2026-09-15 corpus-size doctrine)
