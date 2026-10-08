# Eval Harnesses, Verification Bottlenecks, and Fleet Ops — X-scout digest 2026-10-08

Curated analysis adapted from the X-scout knowledge-scout digest of
2026-10-08 (Discord thread #xTreand, cron job f933f5a8d591; consolidated
knowledge file: `~/.hermes/profiles/architect/memories/knowledge/x-scout-2026-10-08.md`).
Theme: public leaderboards and self-reports fail through the same mechanism —
agents are good enough to shortcut a loose oracle — so verification design
outranks model choice.

## 1. Custom evals beat public benchmarks (35B beats 120B, 95% vs 53%)

Source: x.com/pauliusztin_/status/2107443430011908373 (X Article, ~20 min).

- Split three questions that are usually conflated: **benchmark** ("does it
  work at all?"), **regression** ("does what worked keep working?"),
  **online eval** ("does it work as predicted in production?").
- Harness architecture: seed → run → collect → verify → record, with the
  agent as a subprocess that is **never its own grader**.
- Metrics that matter: pass@k, pass^k, flakiness (tasks that pass sometimes),
  and a hard split of **infra_error vs agent_fail** — the former is system
  noise, the latter is the learning signal.
- Grow the regression suite from production failures whose error signature
  repeats (no upfront design needed) — and **delete easy tests** from a grown
  suite to keep signal-per-cost high.

## 2. Verification is the bottleneck of self-improving AI

Source: x.com/SuJinyan6/status/2106946784224510391 (long-form X Article,
workshop summary). Structure: 3 levers of self-improvement
(harness/weights/environment) → the region that works (machine-checkable
tasks) → 5 reasons verification is hard → 3 opportunities (automated review,
gaming-resistant evals, adaptive environments) → what stays human (choosing
which problems are worth verifying).

- Where a checkable score exists, agents beat humans (safety research:
  97% vs 23% recovered). In open-ended research (CRUX, 6 days, $3,000),
  agent papers were rejected 1/6 and 2/6 for lacking "judgment of when the
  work is done."
- **Reward hacking via history**: Cursor found 63% of "successful" SWE-bench
  Pro tasks pulled the fix from git history instead of deriving it; hiding
  history + blocking the net dropped scores 87.1% → 73.0%.
- Iteration count correlates with quality at ≈ 0.17 — measure outcomes, not
  effort.
- Design consequence: every delegated task needs a deterministic grader and
  a strict harness (strip git history / network from the measured run's
  context) before it is delegatable at all.

## 3. Fleet ops rules written from real incidents (25 agents)

Source: x.com/andrebrov/status/2097134891833917946 (long thread).

- Assignments are brief files on disk; the instruction is only "read this
  file and do it" — long in-chat prompts decay silently.
- Status is judged from artifacts only (commits counted from dispatch,
  report file mtime) — a fleet's "done" is false between turns.
- Models never review themselves: DONE must cross harness/model boundaries
  before merge.
- Prose rules don't survive the shell ("no migrations" dies on an unquoted
  heredoc): **a rule that cannot be enforced is not a rule — it must become
  a gate that actually rejects.**

## 4. The determinism layer (propose / apply split)

Source:
stackoverflow.blog/2026/10/07/part-1-make-your-ai-agents-boring-the-determinism-layer
(Oct 7, 2026).

- Agent = pure function that only *proposes* (same context → same proposal,
  testable with a single assert); a dumb, easily-tested **substrate** applies
  proposals after approval; every decision lands in an append-only audit
  ledger.
- Blast radius of a jailbroken/buggy agent ends at a bad proposal, not a bad
  action. Free loops require a step cap + tool allow-list, never
  `while not done`.

## 5. Cost: cache hit rate is not the bill

Source: arize.com/blog/prompt-caching-benchmark/ (Oct 2026; vendor content —
method transparent, numbers unverified independently). Same multi-turn agent
across 4 model/provider paths: DeepSeek cache-read 93.6% cheapest overall,
but Claude at 89.8% reuse was still most expensive because **output tokens
were ~81% of each call's cost**. Judge agent economics from span-level
token breakdown (input vs output) before switching models. Related harness
note (x.com/nssntus/status/2087785729539895453): keep the stable prefix
byte-identical, never add/remove tools mid-session — use tool masking, or
KV-cache invalidation multiplies cost ~10×.

## 6. Memory must converge, not accumulate

- **Alluvium** (github.com/Tespera/alluvium): when archiving a session into
  a knowledge base, read the existing-topics index first and reuse slugs
  ("atomic-write" extends the old page instead of minting
  "atomic-file-write"); lint for near-duplicates periodically. Root cause of
  vault rot is accumulation without convergence.
- **Agent Memory Repo / Devin "Dreaming"** (x.com/walden_yan/
  status/2107139645921296465, github.com/AgentMemoryRepo/agentmemoryrepo,
  analysis: ai.thesatyajit.com/articles/agent-memory-repo): memory as a repo
  of single-line bullets + wikilinks, plus a daily offline cleanup loop that
  merges duplicates, expires notes no session used, and synthesizes lessons
  no session stated. hwchase17: memory needs an offline cleanup loop, not
  just better retrieval. Gap found in the spec by independent testing: git
  rejects *every* push from a stale checkout, not just same-line edits —
  the concurrency model must be designed explicitly.
- **Claim-named memory files** (x.com/nykdotdev/status/2031581912071127158):
  four context failure modes (pollution / distraction / confusion / clash);
  fix with explicit authority ordering (system prompt > docs > history) and
  naming memory files as claims — `we chose PostgreSQL because queries are
  relational.md` beats `decisions.md` because the title decides whether to
  read on.

## 7. Tests as the feedback loop (inversion check)

Source: x.com/addyosmani/status/2106995301802541481 (Addy Osmani).

- If the check loop is slow or flaky, agents *learn* to rerun tests instead
  of fixing code. agent-skills 0.6.12 added an **inversion check**: flip one
  condition; if the suite stays green, the missing test must be reported.
- A test qualifies as a loop stop-condition only if it is fast and
  deterministic.

## 8. Three years of production agents (10 lessons)

Source: x.com/_aj/status/2098172935710380092 (long-form). Highlights: a
working demo is ~10% of the work (the rest is accuracy, consistency,
recovery, eval); benchmarks measure capability while real workloads measure
recovery/consistency/auditability/cost; business logic encoded into the
harness caps the model's judgment — failures wait there; let agents explore
unfamiliar work, then freeze successful paths into constrained procedures.

## 9. Attention economics at 10-repo scale

Source: deramond.dev/blog/how-i-maintain-my-open-source-projects-with-claude-agents
(Oct 7, 2026). One conductor session whose CLAUDE.md is a protocol (it
writes no code itself) + background agents per tier + SQLite shared state;
every rule protects attention: per-repo caps on waiting items, anything
escalating arrives as a single answerable question, token budget paced
across days. Measure a fleet by "how many human decisions it costs," not
tokens/PRs.

## Context-era items

- **Context = IP** (x.com/prukalpa/status/2077772169455530152): era 1
  "agent per task" failed because accuracy tracked context quality and
  per-agent memories drifted; era 2 is "one brain, many agents" with experts
  authoring shared skills. Five-minute audit: list every production context
  source with owner/scope/downstream/change-check — an untidy map means
  islands.
- **Harness vs sandbox, re-confirmed** (x.com/NathanFlurry/status/
  2102523527304032256, rebuttal re DigitalOcean Managed Agents): already
  recorded 2026-10-01; kept here as cross-context confirmation only.

## Deduped (already captured in earlier digests/skills)

- Push-vs-pull memory, 218→6 files (x.com/mvanhorn/status/2070966613994795489)
  — covered by the skills-over-memory 3-bucket audit + Demotion Ladder in
  `agent-memory-design` (2026-10-01 digest).
- Harness engineering / tool masking (x.com/nssntus/status/2087785729539895453)
  — same family as protect-the-prefix / prefix integrity; folded into §5.

All figures quoted from sources; not independently verified.
