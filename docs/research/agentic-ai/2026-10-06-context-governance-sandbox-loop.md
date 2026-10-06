# Context-file governance, sandbox scoping, loop design (2026-10-06 digest)

> Adapted from the X-scout knowledge-scout digest of 2026-10-06 (Discord
> thread #xTreand, cron job f933f5a8d591). Six batches, two provider
> failures; 11 raw items → 9 kept. Full daily note (Thai):
> `~/.hermes/profiles/architect/memories/knowledge/x-scout-2026-10-06.md`.

Theme: the context file is a liability that needs governance — rules
accumulate faster than their justifications, config files shadow each other
silently, and caches break on hidden state. Plus a production sandbox
doctrine and a loop-design checklist.

## 1. "Catastrophic remembering" — context rules are a ratchet

Source: https://x.com/rohanpaul_ai/status/2096977144111132908

A scan of 1,867 GitHub repos found that agents "remember" rules longer than
maintainers remember why the rules exist. A rule whose origin is forgotten
cannot be safely deleted — so rules only accumulate, and stale rules consume
context on every session while actively steering the agent.

Operational rule: **every rule added to a context file carries provenance**
(date + the bug/commit/event that motivated it). A rule without provenance
is a deletion candidate, not an authority. This complements the existing
"non-inferable constraints only" rule (arXiv 2602.11988): provenance is what
makes eventual removal possible.

## 2. Nested agent-memory directories silently destroy the prompt cache

Source: https://x.com/areshawns/status/2095422606174490807

Claude Code rebuilds the system prompt from the shell's cwd. Subagent
`.claude/agent-memory` directories scattered through a repo (~25 root
resolution candidates observed) make the cache breakpoint move on every
invocation → chronic cache misses, paid in tokens, with no error anywhere.

Check: `find . -path '*/.claude/agent-memory' -not -path './.claude/*'` —
merge any finds into the repo root and gitignore. Generalizes to: keep
agent state/memory at one fixed path; never scatter it per-cwd.

## 3. "Agents don't need memory, they need documentation"

Sources: https://liao.gg/blog/agents-dont-need-memory ·
https://news.ycombinator.com/item?id=49945933

RAG-style memory (embed transcripts, retrieve 5 snippets) has five failure
modes: similarity ranking misses context; old memories are treated as truth;
the agent can't find what it doesn't know exists; it isn't auditable; and
it's expensive (full-history retrieval: p95 latency +91%). The working
alternative is a "Markdown brain": a structured workspace
(instructions/specs/decisions/research/indexes) with the loop
consult → build → update-while-knowledge-is-freshest — git-native, PR-reviewable.

HN caveat (280+ comments): agents authoring their own specs invent
nice-to-haves nobody asked for. **Specs and decisions are human-approved;
agents may update only low-risk layers** (indexes, research notes).
Retrieval remains necessary for three cases: personal conversational memory,
multi-year archives, cross-project relations.

## 4. Sandbox doctrine from two years of financial-services agents (Fintool)

Source: https://x.com/nicbstme/status/2015174818497437834 (long-form, ~11 sections)

- Sandboxing per user is not optional — the author caught an LLM running
  `rm -rf` on the server while "cleaning up temp files."
- Fix: isolated env per user + **three mount points** (private read-write /
  shared read-only / public read-only) + AWS ABAC **short-lived credentials
  scoped per S3 prefix** per user — never trust the model, scope the blast
  radius.
- "Context is the product": the real work is normalizing many schemas into
  one context the model can reason over — not model tuning.
- Skills (markdown) became the product more than the model itself.

## 5. AGENTS.md shadowing — silent, not merged

Sources: https://x.com/simonw (review) ·
https://ayautomate.com/blog/claude-md-vs-agents-md

Claude Code 2.1.277 mechanics: if CLAUDE.md / `.claude/CLAUDE.md` /
CLAUDE.local.md exists in the current directory **or any parent**, AGENTS.md
is shadowed entirely (no merge, no error). `~/.claude/CLAUDE.md` and
`.claude/rules/` do not block. Recommended pattern: canonical AGENTS.md +
a one-line CLAUDE.md stub containing `@AGENTS.md` (avoids double-reading).
Symptom when missed: "I edited AGENTS.md and behavior didn't change" — with
no warning.

Doctrine: overlapping config files must be checked with commands, never
assumed to merge.

## 6. Procedural sediment — agents that never push back

Source: https://x.com/KirkMarple/status/2106268824265957796

Coding agents break from process shape more than model capability: an agent
that obeys every instruction progressively encodes wrong directions into the
system until they sediment. Fix: build an escalation path and the *right to
challenge direction* into the agent's operating rules, not just a list of
commands.

## 7. Five filters for adopting an agent launch (X Article)

Source: https://x.com/rohit4verse/article/2049548305408131349

1. Survives 2 years? (primitives survive, wrappers die)
2. Real postmortem, or marketing?
3. Does adopting it force discarding existing tracing/retry/auth?
   (frameworks trying to become platforms: ~90% death rate, vendor-claimed)
4. Costly to cross in 6 months?
5. Measurable against your own agent?

Closing doctrine: write down "what must be true in 6 months for me to keep
believing this" and check back.

## 8. State of Memory in Agent Harnesses (mem0 teardown — mechanism only,
vendor numbers unverified)

Source: https://x.com/mem0ai/status/2061822612398014782

Across 9 harnesses (Claude Code, Codex, Hermes, Copilot, Devin, …) the same
shape breaks the same way: small local storage (Claude Code ~25KB, Hermes
~800 durable tokens), keyword-only retrieval (filename selection / grep /
FTS5), and — the universal failure — **silent truncation**: a file that
isn't selected produces no warning at all. Design consequence: fail visibly
(log what was dropped), and never expect a keyword index to find a fact
paraphrased differently from its filename.

## 9. Loop engineering (Addy Osmani)

Source: https://x.com/addyosmani/status/2064127981161959567

Stop prompting agents; design loops that prompt agents. A loop needs five
pieces plus a state file: automations (time-triggered), worktrees (parallel
agents without collisions), skills (stop re-explaining the project),
connectors (the loop touches real systems), sub-agents (writer separated
from reviewer). The state file outside the conversation is the spine.
Three traps: verification, comprehension debt, cognitive surrender. Sharpest
point: **the stop condition must be judged by a fresh/other model, not the
one doing the work.**

## Smaller items

- **OpenRouter server-side code execution** (`openrouter:shell`/`bash`) with
  a build-vs-buy benchmark against OpenAI/Anthropic/Google native sandboxes
  (cold-start, isolation, $/second — vendor-reported):
  https://openrouter.ai/blog/insights/server-side-code-execution-tools-for-ai-agents-compared/

## Where this went in the repo

- `skills/knowledge-base/agent-memory-design/SKILL.md` — sections 1, 2, 3,
  8 as four dated patterns (rule provenance / nested-memory cache damage /
  Markdown-brain write-lane split / silent-truncation visibility).
- `skills/quality/ai-agent-security/SKILL.md` — section 4 as the
  per-user-sandbox + scoped-credentials doctrine.
- `skills/execution/loop/SKILL.md` — section 9 as the fresh-judge stop
  condition note.
