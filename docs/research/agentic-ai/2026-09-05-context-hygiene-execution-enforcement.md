# Context-File Hygiene, Execution-Path Enforcement, and Loop/Harness Engineering (2026-09-05)

Consolidated analysis of the 2026-09-05 X-scout digest (6 batches, cron job
f933f5a8d591). Three converging themes, each with direct application to this
repo's skills.

## Theme A — Context files and skills are paid context: audit or they rot

Evidence:
- Scout (Jack Rothrock) reading Claude Code's compaction prompt via MITM proxy:
  prompt = per-task context, skill = conditional context, AGENTS.md = paid every
  run → must be the most ruthless file. ETH Zurich (arXiv 2602.11988, already in
  agent-memory-design) measured >20% average inference cost from context files.
- PostHog case study: the line "never run gh pr merge" in AGENTS.md became the
  *wrong* instruction 21 hours after their merge queue changed — the agent
  followed it unquestioningly. Boris Cherny (Claude Code creator): delete
  CLAUDE.md every 6 months.
- Skill descriptions: harnesses truncate long descriptions to fit context →
  wrong-skill selection. Descriptions must be short routing rules ("when X"),
  not "pick me" ads; multi-workflow skills should be thin routers to child files
  (progressive disclosure). Old instructions written to constrain older models
  (read-file-first, run-tests-yourself) now burn context for nothing.
- Trigger verification: many skills *never fire* because their description
  doesn't trigger at the right moments — measure with trajectory evals
  (Inspect AI in Docker sandbox, an older model as grader), not vibes.
  Relevant to this repo's large skill backlog: verify a skill triggers before
  accumulating more.

Practices adopted:
1. "Every line names the failure it prevents, or delete" — apply to AGENTS.md /
   CLAUDE.md on a schedule (6 months per Cherny), not just when it feels stale.
2. ~150-line ceiling for context files (Scout/PostHog heuristic).
3. Description = routing rule; verify firing with trajectory evals before
   promotion.

## Theme B — Enforcement belongs on the execution path

Evidence:
- dev.to/doberman (Sep 3): prompt/output filters that "warn" are advisory — the
  model can ignore them. Fix: normalize every tool call into one object through
  a single fail-closed decision engine (timeout = deny) + a **taint floor**: a
  session that read a secret is blocked from any outbound value matching that
  secret — no intent inference required. Sandbox ≠ authorization: sandbox
  limits blast radius, authorization decides whether the action happens.
- The Framing Gap (arXiv 2608.27092, lab conditions): direct injection ~0%
  success; the same leak reframed as an "integrity signature" or config field
  → up to 100%. Defense that survives reframing is **payload-blind**:
  destination allow-lists, planner/reader capability separation.
- GitSpawn refinement (2026-09-05): the git-config startup hijack is narrower
  than first reported — `clone/fetch/pull` do not load the target's config;
  only pre-built `.git` directories (zip, shared drive, USB) carry it.
  Companion piece: gitignore filters git's index, not other readers —
  "the agent never touched .env" must be proven from JSONL traces of what was
  actually opened, not the agent's summary. `npm test` exit 0 is a receipt that
  the process started, not that tests passed.

Merged into: `skills/quality/ai-agent-security/` (attack path refinement +
execution-path enforcement control).

## Theme C — Loops and harnesses: memory and compaction are the failure points

Evidence:
- mem0 X Article: loops fail from memory, not intelligence —
  self-reinforcement (the loop eats its own output; the first error becomes
  ground truth) and repeated work (forgetting completed steps, premature
  "complete"). LongMemEval: commercial assistants drop ~30% on long-term
  memory tasks. Ralph Loop (Geoffrey Huntley) as reference: context reset
  every iteration, surviving state stored *outside* context.
- @calcsam harness anatomy: compaction is where coding agents die — the model
  truncates its own decision nodes mid-summary. A real harness manages its own
  context, survives restarts, preserves decisions: thread persistence, live
  task list the agent checks before declaring done, mid-run steering,
  human-gated tools that run headless in CI.
- Multi-harness research (udayan_w summary of 4 papers): HELIX — the best
  single harness adds only ~4%; a collection of 65 harnesses solves far more
  (different tasks fit different harnesses); Darwin Gödel Machine keeps
  multiple harness versions and measures which wins; EdgeBench measures how
  fast a setup *learns to solve* a task type, not first-attempt score.
- The Demotion Ladder (HackerNoon): preprint — policy violations 0% when rules
  fully in context → 30–59% after compaction. Ladder: prose → hook that
  re-injects the rule before compaction → restrict the write path → tests as
  definition of done → make illegal states unrepresentable. 14 months of
  practice: 4,000 lines of prose → 13 hooks (~1,300 lines); cost moves and
  becomes auditable.
- Claude Code hooks traps (nick-liu.com + dev.to/nishilbhave): blocking
  requires **exit code 2** (JSON decision:block + exit 0 is silently ignored);
  Stop-hook messages arrive in tool-result format and get distrusted — use
  PostToolUse flag + PreToolUse gate for hard enforcement; payloads via stdin;
  `settings.local.json` overrides user settings; `claude --debug hooks` to
  debug.
- Local-model agents (akshay_pachaar): token rate = memory bandwidth; MoE
  35B-A3B loads all 35B params; long agent trajectories can exceed weights in
  RAM; quantization risks tool-call structural precision — prefer higher
  bit-depth for tool-calling agents.

Merged into: `skills/execution/loop/` (hook gotchas),
`skills/knowledge-base/agent-memory-design/` (Demotion Ladder + context-file
hygiene).

## Sources

- https://www.scoutapm.com/blog/prompts-skills-and-the-agents-md-nobody-wants-to-write
- https://x.com/posthog/status/2094485724171223409
- https://x.com/pvncher/status/2095991462416490862
- https://x.com/ThePracticalDev/status/2095488985636172057
- https://dev.to/doberman/prompt-filters-are-advisory-enforce-on-the-execution-path-kd4
- https://arxiv.org/abs/2608.27092 (The Framing Gap)
- https://www.itsecuritynews.info/1-folder-was-all-it-took-security-researchers-find-ai-coding-agents-can-be-hijacked-before-a-single-prompt-is-typed/
- https://dev.to/devio_3007/the-agent-could-still-open-env-46am
- https://x.com/mem0ai/article/2067305118891163833
- https://x.com/0xCarnagee/status/2093477307637801344
- https://x.com/prukalpa/status/2077772169455530152
- https://contextandchaos.substack.com/p/the-github-for-context-doesnt-exist
- https://x.com/calcsam/article/2065222134633504871
- https://x.com/udayan_w/status/2095414953717186837
- https://hackernoon.com/the-demotion-ladder-a-year-of-governing-claude-code
- https://nick-liu.com/posts/claude-code-hooks-reality/
- https://dev.to/nishilbhave/claude-code-hooks-12-production-patterns-and-the-stop-hook-trap-3kib
- https://x.com/akshay_pachaar/status/2094765529231929361
- https://x.com/grok/status/2095869090065772920 (minor — memory "dreaming" talk summary)
