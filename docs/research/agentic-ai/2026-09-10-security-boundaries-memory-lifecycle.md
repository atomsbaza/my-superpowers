# Security Boundaries and Memory Lifecycle (2026-09-10)

Consolidated analysis of the 2026-09-10 X-scout digest (6 batches, cron job
f933f5a8d591; batch 04:01 malformed, 12:01 silent; 12 raw → 10 curated items
after dedupe against the 2026-09-06 and 2026-09-08 files). Two themes; all
findings strengthen existing skills rather than creating new surface.

## Theme A — The control plane belongs outside the sandbox

Evidence:
- **CVE-2026-82533** (DeepSeek Harness, VulnCheck 2026-09-08, CVSS 9.4): an
  unauthenticated internal API let the agent — from *inside* its own sandbox —
  escalate its session to `danger-full-access` with approval `never`. Doctrine:
  the control plane (harness/approval state) must live outside the sandbox, and
  permission state must never be mutable from within. "A fence that opens on
  any request is not a fence." (devops.com DeepSeek coverage; HN thread
  47990675 "The agent harness belongs outside the sandbox")
- **Cloudflare Dynamic Workers**: the constructive counterpart. The agent writes
  code that calls APIs, executed in an isolate; an RPC bridge makes tools feel
  like a local library while HTTP filter + **credential injection sit at the
  boundary** — the agent never sees the secret, so it cannot leak one.
  (blog.cloudflare.com/dynamic-workers/)
- **Google Threat Intelligence (2026-09-08)**: a solo attacker assembled a
  credential-theft agent from commodity parts (AI chatbot + prompt + **markdown
  playbooks**) harvesting 23,800 credentials in 6 hours (Google-reported figure,
  independently unverified). Takeaway: agent-readable markdown playbooks are now
  the attacker-side standard — any agent ingesting external content must be
  assumed drivable the same way.

Merged into: `skills/quality/ai-agent-security/` — new attack path
(control-plane API exposure → self-escalation), new control (credential
injection at the boundary, secrets never model-visible), and the
markdown-playbook-as-attack-surface note extending indirect prompt injection.

## Theme B — Memory has a lifecycle: quarantine, decision provenance, sprawl control

Evidence:
- **Memory quarantine** (@0xCodio): new memories enter a HOLDING state (stored
  but barred from decision-making) until a cooldown + cold review; ~40% (case-
  reported, unverified) evaporate during quarantine because they were startled
  reactions, not lessons. Never let an agent write a rule from a single event.
  This is independent confirmation of the "recurring-twice before promote"
  wiki-loop rule already in use.
- **Decision provenance** (Brandon Waselnuk at AI Engineer, Sep 2026; X Article
  "Agent Memory Stack" ~3.8k words): agents repeat corrected mistakes because
  every session starts with zero organizational knowledge. Pattern: import
  decisions — especially rejections of options that looked good because of
  constraints invisible in the final code — into a queryable knowledge graph,
  force the next agent to check before acting. New idea: **the acceptance check
  at import time is a question you want answered** — it measures whether the
  memory actually gets used. (Related speaker-claimed token figure 21M → 10.8M:
  unverified, vendor-adjacent.)
- **Memory sprawl** (@tomcrawshaw01): letting an agent free-build a second
  brain from full conversation history fails the same way every time — notes
  land in files nobody chose, structures nobody approved. What worked: (1) the
  vault holds durable knowledge, agent memory holds identity + pointers only;
  (2) the first-round prompt makes the agent *write its own instructions*
  (direct instruction round one yields a single report = an audit, not a second
  brain); (3) start with a small source set (cost is hard to predict); (4) an
  approval gate between every stage.

Merged into: `skills/knowledge-base/agent-memory-design/` — quarantine/HOLDING
lifecycle pattern, decision-import with acceptance-check questions, and the
sprawl counter-patterns (vault-vs-pointer split, self-authored instructions,
staged approval gates).

## Theme C — Harness mechanics (lighter evidence, practitioner threads)

- **Prompt-as-scar-tissue** (@spectnfa long thread + Harness Engineering
  article): agents that run 2h without finishing usually fail on what the agent
  can *see/touch/remember/define-as-done*, not reasoning. Mechanisms: context as
  a map (agent pulls detail on demand), event log → compiled state with
  execute/resume from state not raw transcript (how to make resumable agents),
  same-agent-same-context double-checks are confidence loops not verification;
  contract-based completion ("which action leads to an outcome the contract
  accepts") + tool gateways that separate propose from execute.
- **Anthropic 1st-party agent guide** (@cyrilXBT): run agents server-side and
  stream-log every step (a run failing at hour 6 resumes from logs); separate
  tool-execution failures from reasoning failures; "make failure cheap" — design
  the harness so failure is a normal handled event (same pattern as
  kanban-worker `--result` reporting contracts).
- **Context Collapse in graph engineering** (X Article): dumping 50 raw worker
  outputs into one synthesis node is the anti-pattern — fan-in through layers
  (batch into intermediate summaries first), and nodes may read in parallel but
  only one node writes to state/codebase.
- **Six-layer agent stack** (@AnnatarXBT): generation → evaluation → memory →
  scheduling → optimization → recursion; a missing layer presents as "the model
  is dumb" but the chain is broken — use as a triage checklist.
- **Harness > model** (YC Paper Club on arXiv:2608.23552): same weights lifted
  ~30% → 95.5% (paper-reported, unverified) under a better harness (persistent
  REPL, cross-trajectory memory/skills, direct subagent communication). Not
  merged as doctrine — it repeats the 2026-09-08 harness-anatomy theme; link
  kept for reference.

Merged into: `skills/execution/loop/` (resumable agents = execute from compiled
state + streaming step logs; contract-based completion) and noted in
`skills/knowledge-base/agent-memory-design/` where memory-adjacent.

## References

- https://devops.com/flaw-in-deepseek-harness-ai-coding-tool-let-agents-disable-their-sandbox/ (CVE-2026-82533)
- https://news.ycombinator.com/item?id=47990675 (HN: harness outside the sandbox)
- https://blog.cloudflare.com/dynamic-workers/ (credential injection at boundary)
- https://michaelnemtsev.com/digest/2026-09-10 (Google TI credential-theft case)
- https://x.com/0xCodio/status/2096982132644106507 (memory quarantine)
- https://x.com/i/article/2097362674078331148 (Agent Memory Stack article)
- https://finance.biggo.com/news/dac47635824b4720 (Waselnuk "you're absolutely right" loop)
- https://x.com/tomcrawshaw01/status/2097308735639265725 (memory sprawl)
- https://x.com/spectnfa/status/2097298431383417150 + https://x.com/i/article/2096570562625655088 (harness scar tissue)
- https://x.com/cyrilXBT/status/2096253035563426134 (Anthropic 1st-party guide)
- https://x.com/i/article/2083419832381489588 (Context Collapse)
- https://x.com/AnnatarXBT/status/2096490078537138268 (six-layer stack)
- https://arxiv.org/abs/2608.23552 (harness > model, reference only)

All figures (~40% memory evaporation, 23,800 credentials, 21M→10.8M tokens,
30%→95.5%) are as reported by the cited sources and were not independently
verified — mechanisms are corroborated across multiple independent sources;
numbers follow the no-vendor-numbers rule and are labeled unverified.
