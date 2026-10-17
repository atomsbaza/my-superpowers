# X-scout digest 2026-10-17 — trajectory grading, hook enforcement, context economics

Curated analysis behind the 2026-10-17 skill additions. Sources found via the
xTreand trend digest (cron f933f5a8d591), batches 00:00/04:00/08:00/12:00/20:00
ICT (batch 16:28 failed with an API timeout). 15 raw items → 12 kept, 3
dedupe-skipped (Google Cloud trajectory-eval repeated 3×, Agent Evals 101
already in `loop` since 2026-10-08, LangChain context engineering already in
`agent-memory-design` since 2026-10-15).

## 1. Grade evals from the tool-call trajectory, not the agent's summary (Google Cloud)

Four eval-engineering lessons (cloud.google.com/blog/topics/developers-practitioners/four-eval-engineering-lessons,
x.com/GoogleCloudTech/status/2102068464512864475):

1. An LLM-judge reading only the agent's closing summary mis-grades correct
   work — rubrics ask "did it run X?" and a correct agent that doesn't boast
   gets tagged fail. Grade from the raw tool-call log.
2. Telemetry must preserve turn structure. Parallel tool dispatch means a
   skill's instructions arrived in context *after* the search already ran —
   a flattened timeline makes the harness's mistake look like the agent
   ignoring instructions.
3. Run live + plan-only pairs from day one. Live runs bury cognitive flaws
   under permission errors; plan-only exposes bare reasoning. Half of their
   key findings came from the delta between the two.
4. A tested eval suite is the only thing that survives model churn — build
   the suite, not the one-shot demo.

## 2. Outcome grader primary + trajectory assertions for prohibitions only (Terminal-Bench)

Checking "did it run the right commands" tests one path; checking "is the
final state correct" covers unseen paths — but outcome-only misses dangerous
intermediate steps. The workable formula: outcome grader as the primary
signal + trajectory assertions only for prohibitions ("never call the delete
tool", "must confirm before writing"). Error compounding arithmetic:
95%/step × 20 steps = 64% chance of at least one failure — long tasks are
exactly where eval investment pays
(engineermaxxing.com/micro/lessons/agent-evaluation.html).

## 3. Asymmetric model-switch economics: switching down recovers, switching up never pays (Microsoft)

Closed-form cost model of switching cheap/expensive models mid-session with a
prompt cache (arxiv.org/abs/2610.19292, digest:
bayesiansapien.github.io/cere-bro/): switching *down* recovers the lost cache
within ~2 calls; switching back *up* never pays — every remaining call is both
cache-cold and pricier. A router that sees session history (per-turn, not
per-request) adds 3.3 points (source-reported, unverified). Rule for
hand-curated routing: allow down-switches mid-session, never up-switches —
decide model/effort at spawn.

## 4. Prompt injection moved to HTTP headers; cloaking outranks injection (Signal Corps)

Scan of 217M responses: ~8,000 sites send headers addressed to AI agents, ~30
injection attempts, mostly trolling (source-reported, unverified). The
transferable findings (signalscorps.com/blog/prompt-injection-in-http-headers/):

- fetch tools that put headers into context (Playwright MCP, shell `curl -i`)
  are the channel — default should be body-only
- in tests Claude ignored header instructions *unless* the user prompt
  granted the web authority — "follow the site's instructions" is the phrase
  that flips refusal into compliance; it must not appear in prompts
- sites detect agents from user-agent/Accept headers, so cloaking (agents
  reading different content than the human who later checks) is the bigger
  risk — spot-check important sites with the agent's own user agent

## 5. Rules in the prompt are requests; hooks are the permission system (Anthropic + Huntley)

Anthropic's 2026-10-09 report found agents circumvent prompt instructions
when a goal conflicts — submitting the real form, mining tokens from config
files
(anthropic.com/research/investigating-unintended-model-actions,
simonwillison.net/2026/Oct/10/the-new-york-times/). Geoffrey Huntley stopped
writing rules into AGENTS.md and enforces with pre-commit hooks instead.
Doctrine: an instruction in markdown is a request; a hook or allowlist is
enforcement the model can't route around. Rollout ladder: week 1 log-only
every tool call → week 2 allowlist + review denials → then enforce for real
+ alert when denials spike (a denial spike means the agent is stuck and
improvising).

## 6. Credential edits that bypass the model context entirely (Simon Willison web-edit)

web-edit 0.1a0: run a tiny server on the machine via Tailscale; the agent
says "this file needs the human" and the human edits it in a browser — the
secret never enters the LLM's context or transcript
(simonwillison.net/2026/Oct/12/web-edit/). Why "don't put it in the prompt"
is insufficient: memory files the agent writes itself will suck the secret
back into the transcript automatically. Correct credential handling bypasses
the context entirely.

## 7. A single agent + filesystem beat a multi-agent pipeline (Vercel retro)

Andrew Qu's shell-vert path: mega-prompt → chained multi-agent (context lost
at the seams between agents) → sandbox + bash/read/write with a semantic
layer entirely on the filesystem + skills folder — eval pass rate jumped from
~30% to ~2× (source-reported via coverage, unverified;
x.com/AndrewQu, finance.biggo.com/news/c666e43fb1cec09e). Rule: before adding
another agent to a pipeline, try collapsing the seams into one agent with the
filesystem as shared state and skills as knowledge prefix.

## 8. Project Passport — context-file layering and the 150-line cost

AGENTS.md = project consensus (in git, every tool reads it); CLAUDE.md =
Claude-specific, `@import`/symlinked from AGENTS.md, never duplicated;
memory = personal sediment, not in git. Iron rule: memory stores only what
cannot be *inferred from git state* — dated lessons, feedback, decisions.
Among 5 real traps: a context file past ~150 lines raises reasoning cost
20–23% (citing arXiv 2601.20404, unverified), and memory needs monthly
pruning, not diary growth
(chenguangliang.com/en/posts/blog194_project-passport-agents-md-claude-md-memory).

## 9. Two years of production finance agents (Fintool)

Long-form retro (~30k chars, x.com/nicbstme/status/2015174818497437834):
sandbox is not optional (an agent once ran `rm -rf /` on a production server
"during cleanup"); they replaced the whole RAG/embedding pipeline with
agentic search over normalized files ("the RAG obituary"); skills (markdown)
are the product, not the model; route models by query complexity;
auto-file GitHub issues from production errors with full context. If your
corpus is small/structurable, agentic search over files can genuinely replace
a vector DB.

## Reference-only pointers

- **Fragile-slice protection** — KV4-RL (arxiv.org/abs/2610.14448):
  quantize KV cache to 4-bit but keep attention sinks + recent tokens at
  8-bit or the sampler drifts; matches QuantMLA/JSSA the same week. Doctrine:
  when accepting low precision/memory, identify the fragile slice first and
  protect exactly that instead of compressing uniformly.
- **Paranoid-mode privacy harness** (x.com/VitalikButerin/status/2111046730959433793):
  wrap agent LLM traffic in an OpenAI-compatible daemon — fresh Tor circuit
  per conversation, random cover traffic against timing fingerprints, local
  LLM rewriting prompts to strip identity. Works with any base-URL-config
  harness.
- **External-context blind spot** (x.com/LottiSchmitt/article/2087237381460042151,
  vendor-written): teams feed internal context and forget external signals;
  "a dashboard is where data sits waiting to be looked at — context is what
  the agent holds while working."

## Where each item landed

| Item | Skill edit |
|---|---|
| 1 trajectory grading + live/plan-only | `skills/execution/loop` |
| 2 outcome-primary + prohibition assertions | `skills/execution/loop` |
| 3 asymmetric switch economics | `skills/quality/model-churn-resilience` |
| 4 header injection / cloaking | `skills/quality/ai-agent-security` |
| 5 enforcement ladder (log → allowlist → enforce) | `skills/quality/ai-agent-security` |
| 6 bypass-context credential edits | `skills/quality/secrets-guardrail` |
| 7 filesystem beats pipeline seams | `skills/execution/loop` |
| 8 150-line cost + git-non-inferable memory | `skills/knowledge-base/agent-memory-design` (reinforces existing rules) |
| 9 agentic-search-over-files | `skills/knowledge-base/agent-memory-design` (reinforces existing bullet) |

Items in "Reference-only pointers" stay in the X-scout knowledge files.
