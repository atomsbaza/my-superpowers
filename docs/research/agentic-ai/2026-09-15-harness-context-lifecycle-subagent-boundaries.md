# Harness, Context Lifecycle, and Subagent Boundaries (2026-09-15)

Consolidated analysis of the 2026-09-15 X-scout digest (6 batches, cron job
f933f5a8d591, all with content; 19 raw items → 10 curated after dedupe
against the 2026-09-08 / 09-10 / 09-12 files). Theme: outcomes are set by the
*harness* — agent failure is geometric in step count, pre-loaded context is
the dominant cost nobody optimizes, and untrusted-code boundaries must be
deny-by-default — not by the model.

## Theme A — Long-horizon failure is geometric, and squeezing context makes it worse

Evidence:
- **"How Fast Do Agents Rot?"** (arXiv:2609.01660; 9 models, 10,664
  trajectories): long-horizon task success follows a geometric law r^H —
  every model, including deployed ones, collapses from ~100% to near 0%
  within ~16 dependent steps. Counterintuitive headline: *shortening the
  context window makes rot faster* (logit slope −0.69 vs −0.44), refuting
  the "lost-in-the-middle" justification for aggressive context compression.
  (arxiv.org/abs/2609.01660)

Merged into: `skills/execution/loop/` — budget workflow reliability as
r^(number of dependent steps); the fix is fewer dependent steps
(checkpoint/resume, split the task), never "compress context harder".

## Theme B — Pre-loaded context and the hygiene rules that survive

Evidence:
- **7,850 unexamined tokens** (Claude Code): system prompt + memory + skill
  descriptions + CLAUDE.md load ~7,850 tokens before the first keystroke,
  while people optimize a 45-token prompt. Safe-cutting rules: cut in
  *blocks*, not sentences (below eval noise); convert *absolute rules into
  principles* ("never multi-line comments" → "match surrounding comment
  density") — rules written for weaker models are now pure overhead +
  contradiction. Don't teach tools by examples anymore (examples constrain
  the exploration space); design expressive parameters instead.
  (x.com/i/web/status/2089393338977829278)
- **AGENTS.md is written for the person who joins on Monday, not for the
  model** (@undefinedKi): build/test commands, conventions, prohibitions;
  name it AGENTS.md (nearly every tool reads it) and make CLAUDE.md a
  2-line pointer — one source of truth, no split-brain across teams using
  different agents. (x.com/undefinedKi/status/2098760642526085164)
- **ICM filesystem-as-memory** (tomcrawshaw01): every work folder carries a
  CONTEXT.md contract (input/process/output/human-check) the agent reads
  before acting; separate "factory" (skills/templates/rules) from "product"
  (artifacts); when work drifts, *fix the contract, not the output*.
  (x.com/tomcrawshaw01/status/2087886985705009421)
- **558 real AGENTS.md files surveyed** (dev.to/janzong): 85.7% are
  prohibitions, 82.8% list build/test commands, but only 13.6% record
  gotchas — the most valuable content — and a third of recorded "gotchas"
  aren't real. Confirms the non-inferable-only + failures.md convention.
  (dev.to/janzong/i-labeled-558-agentsmd-files-heres-what-they-say-and-what-almost-nobody-writes-down-34gb)

Merged into: `skills/knowledge-base/agent-memory-design/` (context hygiene:
block-cuts + absolute-rule→principle conversion + examples→parameters for
tool docs) and `skills/quality/ai-agent-security/` (per-step constraint
validation below). The AGENTS.md/pointer pattern was already in place in
this repo — independent confirmation.

## Theme C — Subagent context modes and capability isolation

Evidence:
- **Fork vs isolated subagents** (LangChain Deep Agents, Sept 2026): `fork`
  passes the supervisor's whole state to the subagent (for work that
  continues an existing task — implementing an already-diagnosed fix — no
  re-reading files); `isolated` starts empty (for verifiers/reviewers —
  "inheriting the supervisor's reasoning can be counterproductive"). The
  decision axis: does the role need *history* or *neutrality*?
  (langchain.com/blog/organizing-context-multi-agent-harness)
- **Running untrusted agent code without a full sandbox** (LangChain):
  QuickJS→WASM interpreter separates the *execution boundary* (protect the
  host) from *capability isolation* (define what the agent may do); the
  runtime starts with nothing — file reads, network, package installs must
  each be bridged in with a narrow contract (call a subagent function
  instead of process/network). Doctrine: deny-by-default + open
  capabilities one by one, not "sandbox it then block the dangerous bits".
  (langchain.com/blog/running-untrusted-agent-code-without-a-sandbox)

Merged into: `skills/execution/dispatching-parallel-agents/` (fork-vs-
isolated decision rule) and `skills/quality/ai-agent-security/`
(deny-by-default capability isolation as the design posture for running
generated code).

## Theme D — Model/token-level pitfalls and lighter harness evidence

- **Tokenization is where the bugs hide** (@mdancho84): the model sees token
  IDs, not your prompt; BPE is not automatically byte-level, SentencePiece
  is a framework not an algorithm; never swap a trained model's tokenizer
  like a preprocessing function. Thai/code/multilingual inputs have
  specific failure modes — suspect the tokenizer before the reasoning when
  a model "doesn't see" data as expected.
  (x.com/mdancho84/status/2098435177076625754)
- **Harness is a 6× lever, and it co-adapts to the model** (@rohanpaul_ai,
  Stanford+MIT work): different harnesses on the same model span up to 6×
  on one benchmark; the Meta-Harness technique lets an agent optimize its
  own harness given code, logs, and execution traces via the filesystem
  (+4.7 pts on IMO-level math, beats hand-engineered baseline on
  TerminalBench-2). HarnessDev: a harness co-adapted with Opus scores 69.3
  on SWE-Pro but 33.0 when the same harness code runs on Gemini 3.1 Pro —
  harnesses are not automatically portable across executors; re-verify
  with your own eval before reuse.
  (x.com/rohanpaul_ai/status/2098986025397977287;
  x.com/rohanpaul_ai/status/2095784429142880415)
- **MCP is becoming a context layer — SEP-2640 Skills Extension**
  (@stretchcloud): the "Skills Over MCP" WG proposes shipping skills
  (SKILL.md + scripts + references) through resource templates
  (`skill://my-skill/...`) on the existing MCP — an atomic "tool + how to
  use it" unit that fixes the burn-context-at-startup pain of loading all
  skill metadata into the system prompt. Server-side instructions become
  first-class payload. (x.com/i/status/2099415857537466836; PR
  modelcontextprotocol#2640)
- **RAG vs 1M-token context** (controlled test, 12 questions, blind
  grading): decide by corpus size before choosing; prompt cache only hits
  ~1/3 of calls with no predictive pattern (unverified); an explicit
  "admit there's no data" instruction converts confident guesses into
  honest refusals when retrieval misses.
  (x.com/0xMortyx/status/2094413825780928800)
- **pstack workflow** (Lauren Tan): force the agent to restate the problem
  in its own words before touching code — surfaces misunderstanding before
  code exists and keeps your biases out of its context. The root skill is
  verification: an agent that can't verify its own work makes you the
  bottleneck forever. (x.com/i/web/status/2097732320606507506)
- **Token engineering, four levers** (system level): prune intermediate tool
  outputs (don't replay 3,000-line terminal dumps; summarize completed
  steps), size thinking budgets to query difficulty, route easy tasks off
  reasoning models, right-size + continuous evals at the gateway.
  (x.com/i/web/status/2090892404509601819)
- **AgentRx (Microsoft)** — debug agent that crashes *after* the real one:
  validate per-step constraints (schema/state consistency, e.g. claimed
  item count vs actual array) + step-indexed traceability; observability
  that doesn't evaluate constraints per step is debugging theater.
  (x.com/marfinxx/status/2098909060204831036)
- **Second brain, one writer per layer**: /0-raw (human only), /1-wiki
  (nightly agent), /2-digest (scheduled jobs), identity.md (human, read
  before every run); context rule: "if the vault has the answer, don't
  answer from training data" + cite the note used.
  (x.com/i/web/status/2083276253550043271)
- **Graph engineering**: do entity/relationship extraction by hand first to
  learn what "correct" looks like, or you can't tell when automated
  extraction is broken. (x.com/cyrilXBT/status/2088088373642539490)

Merged into: `skills/knowledge-base/agent-memory-design/` (token-engineering
levers + tool-output pruning), `skills/quality/ai-agent-security/`
(per-step constraint validation from AgentRx), and
`skills/debugging/diagnose/` (restate-the-problem-before-coding gate).
Tokenization pitfalls and SEP-2640 remain in this research file (tokenizer
swaps are rare operational events; SEP-2640 is a proposal to track, not a
stable pattern to install).

## Skipped (with reasons)

- **LLM foundations Part 1/6** (batch 08) — good syllabus, but a taxonomy;
  no mechanism beyond what's already captured (bounded loops #38,
  Verification Tax #57).
- **Memory quarantine** (batch 04) — duplicate of #48/2026-09-10
  (HOLDING-until-cold-review already merged); kept as confirmation.
- **RAG vs long-context as a main entry** — doctrines folded into Theme D;
  the cache-hit figure is unverified.
- **Graph engineering course as a main entry** — duplicates the existing
  `graph-engineering-knowledge-base`; kept the hand-extraction principle
  only.
- All release/deal/MAU news — ban list (scout filtered most of it already).

All figures are as reported by the cited sources and were not independently
verified (mechanisms corroborated across multiple independent sources or
published research).

## References

- https://arxiv.org/abs/2609.01660 (How Fast Do Agents Rot?)
- https://x.com/i/web/status/2089393338977829278 (7,850-token context hygiene)
- https://x.com/undefinedKi/status/2098760642526085164 (AGENTS.md + pointer)
- https://dev.to/janzong/i-labeled-558-agentsmd-files-heres-what-they-say-and-what-almost-nobody-writes-down-34gb (558-file survey)
- https://x.com/tomcrawshaw01/status/2087886985705009421 (ICM CONTEXT.md)
- https://www.langchain.com/blog/organizing-context-multi-agent-harness (fork vs isolated)
- https://www.langchain.com/blog/running-untrusted-agent-code-without-a-sandbox (QuickJS→WASM capabilities)
- https://x.com/mdancho84/status/2098435177076625754 (tokenization)
- https://x.com/rohanpaul_ai/status/2098986025397977287 (Meta-Harness)
- https://x.com/rohanpaul_ai/status/2095784429142880415 (HarnessDev)
- https://x.com/i/status/2099415857537466836 (SEP-2640)
- https://x.com/0xMortyx/status/2094413825780928800 (RAG vs long context)
- https://x.com/i/web/status/2097732320606507506 (pstack)
- https://x.com/i/web/status/2090892404509601819 (token engineering)
- https://x.com/marfinxx/status/2098909060204831036 (AgentRx)
- https://x.com/i/web/status/2083276253550043271 (one writer per layer)
- https://x.com/cyrilXBT/status/2088088373642539490 (graph extraction by hand)
