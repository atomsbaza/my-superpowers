# Attribution

## obra/superpowers

The following skills were adapted from [obra/superpowers](https://github.com/obra/superpowers)
by Jesse Vincent / Prime Radiant, licensed under MIT:

**skills/planning/**
- `brainstorming`
- `writing-plans`
- `spike`
- `prototype`
- `adr`

**skills/execution/**
- `subagent-driven-development`
- `executing-plans`
- `dispatching-parallel-agents`

**skills/quality/**
- `requesting-code-review`
- `receiving-code-review`
- `verification-before-completion`

**skills/git/**
- `using-git-worktrees`
- `finishing-a-development-branch`

**skills/tools/**
- `writing-skills`
- `find-skills`

## thananon/9arm-skills

The following skills were adapted from [thananon/9arm-skills](https://github.com/thananon/9arm-skills)
by Thananon:

**skills/quality/**
- `scrutinize`

**skills/debugging/**
- `post-mortem`

## mattpocock/skills

The following skills were adapted from [mattpocock/skills](https://github.com/mattpocock/skills)
by Matt Pocock:

**skills/planning/**
- `codebase-design`
- `domain-modeling`
- `grill-with-docs`
- `to-issues`

**skills/tools/**
- `writing-great-skills`

## DietrichGebert/ponytail

`skills/quality/ponytail/` was adapted from [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail),
licensed under MIT. Pinned at v4.2.0 (June 2026).

## tt-a1i/archify

`skills/design/archify/` was installed from [tt-a1i/archify](https://github.com/tt-a1i/archify),
licensed under MIT. Based on Cocoon-AI's architecture-diagram-generator (MIT).
Pinned at v2.17.0-dev.1 (September 2026); `test/` and `benchmarks/` stripped.

## Backfilled from local Codex CLI skill installs (2026-08-06)

These skills were already present locally under `~/.agents/skills/` (the Codex CLI skill
directory, populated over time via `npx skills add` and manual installs) but had never been
copied into this repo — creating the exact "born outside the repo" drift this repo's own
convention exists to prevent (see `feedback_agents_skills_in_repo` in the maintainer's memory).
Backfilled into their matching categories here so they're tracked, versioned, and installed
consistently going forward.

Provenance below is what `~/.agents/.skill-lock.json` records for each (verify license terms
against the upstream repo before further redistribution — this is a personal-use backfill, not
a license audit):

- `skills/apple/ce-test-xcode/` — from [everyinc/compound-engineering-plugin](https://github.com/everyinc/compound-engineering-plugin), `plugins/compound-engineering/skills/ce-test-xcode/SKILL.md`
- `skills/tools/changelog-writer/` — from [patricio0312rev/skills](https://github.com/patricio0312rev/skills), `foundation/changelog-writer/SKILL.md`
- `skills/git/git-advanced-workflows/` — from [wshobson/agents](https://github.com/wshobson/agents), `plugins/developer-essentials/skills/git-advanced-workflows/SKILL.md`
- `skills/quality/security-review/` — from [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code), `skills/security-review/SKILL.md`
- `skills/tools/chrome-extension-development/` — from [mindrally/skills](https://github.com/mindrally/skills), `chrome-extension-development/SKILL.md`
- `skills/quality/performance/` — from [addyosmani/web-quality-skills](https://github.com/addyosmani/web-quality-skills), `skills/performance/SKILL.md`, MIT-licensed per the skill's own frontmatter (`author: web-quality-skills`)
- `skills/quality/security-auditor/` — from [charon-fan/agent-playbook](https://github.com/charon-fan/agent-playbook), `skills/security-auditor/SKILL.md`
- `skills/quality/code-review-quality/` — from [proffesor-for-testing/agentic-qe](https://github.com/proffesor-for-testing/agentic-qe), `.claude/skills/code-review-quality/SKILL.md`

**Provenance unknown** — no lockfile entry, no in-file attribution; source could not be determined at backfill time:
- `skills/product-owner/brd-to-prd/`
- `skills/product-owner/prd-to-tdd/`
- `skills/product-owner/to-prd/`
- `skills/planning/grill-me/`
- `skills/execution/tdd/`

## Original skills (2026-09-05)

- `skills/tools/kirocrew-claude-backend/` — original work; procedures verified against KiroCrew upstream `d3e67b7e9` (2026-09-04) on macOS.

## Curated external workflow adaptations (2026-08-21)

These are concise, non-verbatim adaptations of useful workflow ideas read from public skills. No external bundle, dependency, or installer was copied.

- `skills/quality/ci-quality-gates/` — adapted from [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills), specifically `ci-cd-and-automation`; MIT licensed.
- `skills/quality/ai-agent-security/` — adapted from [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills), specifically `ai-security`; MIT licensed.
- `skills/quality/code-review/` — extended with confidence/impact filtering and draft-only safety ideas from [aj-geddes/useful-ai-prompts](https://github.com/aj-geddes/useful-ai-prompts), specifically `code-review-analysis`; MIT licensed.
- `skills/qa/reporting-test-results/` — extended with evidence-manifest and E2E validation ideas from [aws-samples/sample-agent-skills-for-builders](https://github.com/aws-samples/sample-agent-skills-for-builders), specifically `end-to-end-testing`; Apache-2.0 licensed.

The existing `tools/agent-evals/` engine is reused as-is. Evaluation concepts from [Microsoft Waza](https://github.com/microsoft/waza) informed the preference for isolated fixtures, explicit validators, baseline comparison, replayable results, and regression gates; no Waza code was copied.

## Kiro Crew learning-pairing adaptation

`skills/learning-pairing/` is a portable, English-only adaptation of the user's Kiro Crew
learning-pairing behavioral prototype. It contains only AgentSkills-compatible guidance;
no Kiro Crew production code, runtime integration, credentials, or runtime state was copied.

## Adapted from X-scout digest (2026-09-08)

Extensions adapted from the X-scout knowledge-scout digest of 2026-09-08
(Discord thread #xTreand, cron job f933f5a8d591):

- `skills/quality/verification-before-completion/` — self-report failure
  statistics (Frontier Challenge: 75% of failed runs report success) and the
  acceptance-checks-beyond-green-tests requirement (SWE-Gate, arXiv
  2609.04167), plus autonomy-sized-by-verifiability (Andrew Ng).
- `skills/execution/loop/` — bounded-loop requirements section (declared
  budget, persisted state, evidence gate; arXiv 2609.00050 — recovery-loop
  removal drops verified completion 95.0%→12.9%).
- `skills/knowledge-base/agent-memory-design/` — protect-the-prefix
  compaction rule (arXiv 2609.03430) and ACE/MCE incremental context
  evolution evidence.
- `skills/quality/ai-agent-security/` — GitSpawn CVE-2026-7163 and the
  global-config-doesn't-work mitigation detail.
- `docs/research/agentic-ai/2026-09-08-verification-product-bounded-loops.md`
  — full cited analysis.

Sources: clauday.com Frontier Challenge analysis, arXiv 2609.04167 (SWE-Gate),
arXiv 2609.04681 (Verification Tax/PQC), x.com/AndrewYNg/status/2095890279865721217
+ deeplearning.ai The Batch, arXiv 2609.00050 (Tata) +
codex.danielvaughan.com, arXiv 2609.00006 (Wavestone 11-harness autopsy) +
codex.danielvaughan.com, alphaxiv.org/abs/2609.03430 (Random Attention),
miraflow.ai ACE/MCE, martinfowler.com accidental blackboard,
dev.to/jamilxt FLT shared-DAG postmortem, workloft.ai CLAUDE.md demotion,
pipelinemag.ai design-system memory correction, manifold.security GitSpawn
(CVE-2026-7163), x.com/METR_Evals HF postmortem.

## Original work — Loop Engineering

The following skill was created in this repo, derived from concepts in
*Loop Engineering* (NotebookLM, 2025) by Bassem Dghaidi:

- `skills/planning/loop-architect/` — Loop Prompt design: project read → scope verification → task breakdown → four-component Loop Prompt generation

## Original work — The Pragmatic Engineering Playbook

The following six skills were created in this repo, derived from concepts in
*The Pragmatic Engineering Playbook* (NotebookLM, 2024) by Bassem Dghaidi:

- `skills/planning/scale-audit/` — Order of Magnitude Playbook enforcement
- `skills/planning/quarterly-evolution/` — quarterly tech investment framing
- `skills/quality/good-enough/` — Esthetics Trap detection
- `skills/quality/pragmatic-review/` — Engineering Diagnostic Matrix scoring
- `skills/communication/business-impact/` — business consequence translation
- `skills/execution/benchmark-sprint/` — parallel architectural benchmarking harness

## Original work — Clean Code & The Clean Coder

The following skill was created in this repo, derived from concepts in
*Clean Code: A Handbook of Agile Software Craftsmanship* and *The Clean Coder:
A Code of Conduct for Professional Programmers* by Robert C. Martin:

- `skills/knowledge-base/martin-clean-code/` — extracted frameworks, principles, and
  techniques from both books (naming, functions, testing, refactoring, code
  smells, TDD, professionalism, estimation, craftsmanship), generated via the
  `book-to-skill` converter

## Original work — Clean Architecture

The following skill was created in this repo, derived from concepts in
*Clean Architecture: A Craftsman's Guide to Software Structure and Design* by
Robert C. Martin:

- `skills/knowledge-base/martin-clean-architecture/` — extracted frameworks, principles,
  and techniques from the book (SOLID, component cohesion/coupling principles,
  the Dependency Rule, architecture boundaries, use cases and entities, package
  organization strategies), generated via the `book-to-skill` converter

## Original work — Learning Domain-Driven Design

The following skill was created in this repo, derived from concepts in
*Learning Domain-Driven Design* by Vlad Khononov (O'Reilly):

- `skills/knowledge-base/khononov-ddd/` — extracted frameworks, principles, and
  techniques from the book (subdomains, bounded contexts, context mapping,
  tactical business-logic patterns, architectural patterns, communication
  patterns, design heuristics, EventStorming, microservices, event-driven
  architecture, data mesh), generated via the `book-to-skill` converter

## Original work — TDD Knowledge Base

`skills/knowledge-base/tdd-knowledge-base/` was synthesized from a NotebookLM deep
web research pass (89 sources) on Test-Driven Development, not from a single
book. It attributes named techniques and quotes to their original
practitioners (Kent Beck, Martin Fowler, Robert C. Martin, Steve Freeman &
Nat Pryce, David Heinemeier Hansson) where the research identifies them, and
flags the few gaps the research left unverified.

## Original work — EF Core Knowledge Base

`skills/dotnet/efcore-knowledge-base/` was synthesized from a NotebookLM deep
web research pass (98 sources) on EF Core performance and data-access
architecture, not from a single source. It flags an explicit coverage gap
where the research crawler's fetch of OceanBase's official docs (24 pages)
and 2 StackOverflow pages failed, and marks OceanBase-specific claims beyond
basic Pomelo/MySQL-mode compatibility as unverified pending a follow-up pass.

## Original work — Design Patterns in C#

The following skill was created in this repo, synthesized from two books:
*Design Patterns: Elements of Reusable Object-Oriented Software* by Erich
Gamma, Richard Helm, Ralph Johnson, and John Vlissides (Addison-Wesley, 1994)
supplies the canonical pattern definitions (Intent, Applicability,
Consequences, Known Uses, Related Patterns), folded into each pattern chapter
and two dedicated chapters on GoF foundations and case studies. *Design Patterns
in C#: A Hands-on Guide with Real-World Examples* by Vaskaran Sarcar (Apress,
2018) supplies the C# implementations and worked examples.

- `skills/knowledge-base/design-patterns-csharp/` — 23 Gang of Four patterns
  with canonical definitions folded in, C# code examples, plus Simple Factory,
  Null Object, MVC, pattern criticisms, anti-patterns, memory-leak hardening;
  two dedicated chapters on GoF foundations and the Lexi case study; modern C#
  modernization notes (sourced from public Medium articles and web research,
  2025–26) flagging patterns absorbed into dependency injection frameworks or
  language features in modern C#, generated via the `book-to-skill` converter

## Original work — C# Concurrency

The following skill was created in this repo, derived from concepts in
*C# Concurrency: Asynchronous and Multithreaded Programming* by Nir Dobovizki:

- `skills/knowledge-base/dobovizki-csharp-concurrency/` — extracted frameworks
  and patterns for compiler state machine transformation, thread safety
  primitives, SynchronizationContext, async/await execution models, concurrent
  collections, and async streams, generated via the `book-to-skill` converter

## Original work — Refactoring

The following skill was created in this repo, derived from concepts in
*Refactoring: Improving the Design of Existing Code* by Martin Fowler:

- `skills/knowledge-base/fowler-refactoring/` — extracted code smell
  identification, refactoring mechanics, the Two Hats principle, the Rule of
  Three, small-step refactoring discipline, composing methods, organizing data,
  and simplifying conditional expressions, generated via the `book-to-skill`
  converter

## Original work — A Philosophy of Software Design

The following skill was created in this repo, derived from concepts in
*A Philosophy of Software Design* by John Ousterhout:

- `skills/knowledge-base/ousterhout-software-design/` — extracted frameworks for
  deep vs shallow modules, information hiding, complexity analysis, tactical vs
  strategic programming trade-offs, error handling semantics, comment-driven
  design, and cohesion principles, generated via the `book-to-skill` converter

## Original work — The Pragmatic Programmer

The following skill was created in this repo, derived from concepts in
*The Pragmatic Programmer: From Journeyman to Master* by Andrew Hunt and David
Thomas (Addison-Wesley, 1999):

- `skills/knowledge-base/pragmatic-programmer/` — extracted core principles
  including DRY, orthogonality, tracer bullets, reversibility, Design by
  Contract, Law of Demeter, programming by coincidence avoidance, and broken
  windows theory, generated via the `book-to-skill` converter

## Original work — Pro Asynchronous Programming with .NET

The following skill was created in this repo, derived from concepts in
*Pro Asynchronous Programming with .NET* by Richard Blewett and Andrew Clymer:

- `skills/knowledge-base/pro-async-dotnet/` — extracted the asynchrony matrix
  (CPU vs I/O), Task Parallel Library (TPL) fundamentals, SynchronizationContext
  semantics, ConfigureAwait discipline, concurrent collections, PLINQ, and
  synchronization primitives, generated via the `book-to-skill` converter

## Original work — Web Application Security

The following skill was created in this repo, synthesized from concepts in two
books: *Grokking Web Application Security* by Malcolm McDonald (Manning, 2024)
and *Web Application Security: Exploitation and Countermeasures for Modern Web
Applications* by Andrew Hoffman (O'Reilly, 2nd ed., 2024):

- `skills/knowledge-base/webappsec-defense/` — extracted and cross-referenced
  attack vectors (XSS, CSRF, injection, XXE) and defensive patterns
  (authentication/authorization, session design, threat modeling, CVSS,
  Zero Trust, dependency vulnerability scanning), generated via the
  `book-to-skill` converter

## UditAkhourii/neuroarxiv

`skills/tools/neuroarxiv/` was copied from [UditAkhourii/neuroarxiv](https://github.com/UditAkhourii/neuroarxiv), licensed under MIT. The portable copy includes only the Claude/Codex skill definition; the upstream TypeScript CLI and its dependencies are not included.

## warpdotdev/common-skills

`skills/tools/skill-doctor/` was vendored from [warpdotdev/common-skills](https://github.com/warpdotdev/common-skills)
(Warp, `.agents/skills/skill-doctor/`), licensed under MIT. Vendored 2026-08-29;
the copy includes only the skill itself (SKILL.md, scripts/, scorers/, references/, assets/),
not the upstream repo's tests or other skills.

## Adapted from X-scout digest (2026-09-01)

`skills/knowledge-base/agent-memory-design/` was adapted from the X-scout
knowledge-scout digest of 2026-09-01 (Discord thread #xTreand, cron job
f933f5a8d591), consolidating cited 2026 research: arXiv 2602.11988 (ETH
Zurich, context files), arXiv 2608.20202 (MemTrapBench),
hatch.org agent-memory revision benchmark, jatingargiitk "Coding Brain"
(claude-rem rewrite-with-history design), PostHog context-as-code, and Mem0
*State of AI Agent Memory 2026* (patterns only — vendor benchmark numbers
failed independent reproduction and are excluded). Full cited analysis:
`docs/research/agentic-ai/2026-09-01-agent-memory-and-context.md`.

## Adapted from X-scout digest (2026-09-02)

`skills/quality/model-churn-resilience/` and the eval-environment escape
extension to `skills/quality/ai-agent-security/` were adapted from the
X-scout knowledge-scout digest of 2026-09-02 (Discord thread #xTreand, cron
job f933f5a8d591). Sources: Anthropic eval-sandbox-escape review (141,006
runs, via michaelnemtsev.com and Axios/CNET), Ben Rehberger's Claude Code
Auto Mode supply-chain break, GitHub Copilot's overnight removal of 6 models
(byteiota.com), Anthropic Claude Code limit change (explainx.ai, claudefa.st),
2026-09-01/02. Full cited analysis:
`docs/research/agentic-ai/2026-09-02-model-churn-and-agent-sandboxes.md`.

## Adapted from X-scout digest (2026-09-03)

MCP security controls added to `skills/quality/ai-agent-security/` (new attack
path + MCP-specific controls subsection), the harness-engineering corollary in
the same skill, and the write-ownership-per-lane pattern added to
`skills/knowledge-base/agent-memory-design/` were adapted from the X-scout
knowledge-scout digest of 2026-09-03 (Discord thread #xTreand, cron job
f933f5a8d591). Sources: API Evangelist "The MCP Authentication and
Authorization Gap" (apievangelist.com, 2026-09-03), Digital Applied MCP server
audit (2026-09-02, injection path in Context7), @tonbistudio security-dials
masterclass (x.com/tonbistudio/status/2093764090619638228), @0xwhrrari
harness-engineering article (x.com/0xwhrrari/status/2093685107534000560),
@joerg_peetz compile-once memory / write-ownership thread. Full cited analysis:
`docs/research/agentic-ai/2026-09-03-mcp-security-doctrine.md`.

## Adapted from X-scout digest (2026-09-04)

Extensions to `skills/quality/ai-agent-security/` (startup hijack via repo git
config, classifier-passing attack chains as attack paths; sandbox-egress and
structural-gating controls section), the external-itemized-checklist evidence
added to `skills/quality/verification-before-completion/`, and the
forward-only memory typing + source-or-error lint + ConstraintRot additions to
`skills/knowledge-base/agent-memory-design/` were adapted from the X-scout
knowledge-scout digest of 2026-09-04 (Discord thread #xTreand, cron job
f933f5a8d591). Sources: Google Cloud agent sandbox isolation lessons
(explainx.ai), "Out of the Sandbox" X article
(x.com/i/article/2094174866576404913), embracethered.com Claude Code
Auto-Mode attack chain, GitSpawn git-hijack disclosure
(manifold.security), explainx.ai MCP security guide (updated 2026-09-01),
Univ. Calgary memory-poisoning research (via the-14.com), arXiv 2606.22528
(Governance Decay/ConstraintRot), arXiv 2607.17937 (skills failure in long
context), prefactor.tech step-level evaluation gap, devgent.org harness-design
piece (Terminal Bench 2.0 harness-only gains), markhuang.ai append-only
history note, yonk.dev process-as-memory, @joerg_peetz MeMex Zero-RAG thread
(x.com/joerg_peetz/status/2094467733568286777). Full cited analysis:
`docs/research/agentic-ai/2026-09-04-sandbox-context-integrity.md`.

## Adapted from X-scout digest (2026-09-05)

Extensions to `skills/quality/ai-agent-security/` (GitSpawn scope refinement —
clone/fetch/pull are safe, pre-built `.git` directories are the risk;
gitignore-is-not-a-sandbox attack path with trace-based verification;
execution-path enforcement control — fail-closed decision engine, taint floor,
payload-blind checks against the Framing Gap reframed-injection result,
arXiv 2608.27092), the Demotion Ladder + context-file/skill hygiene additions
to `skills/knowledge-base/agent-memory-design/`, and the hook-gotchas section
(exit code 2, Stop-hook distrust, stdin payloads, settings override semantics)
added to `skills/execution/loop/` were adapted from the X-scout knowledge-scout
digest of 2026-09-05 (Discord thread #xTreand, cron job f933f5a8d591). Sources:
scoutapm.com AGENTS.md analysis, PostHog stale-instruction case
(x.com/posthog/status/2094485724171223409), pvncher skill-hygiene article,
@ThePracticalDev skill-trigger evals, dev.to/doberman execution-path
enforcement, arXiv 2608.27092 (Framing Gap), itsecuritynews.info GitSpawn
refinement, dev.to/devio_3007 gitignore-vs-sandbox, mem0 loop-engineering
article, @prukalpa context-governance thread, contextandchaos.substack.com
context portability, @calcsam harness anatomy, @udayan_w multi-harness research
summary (HELIX, DGM, EdgeBench), hackernoon.com Demotion Ladder,
nick-liu.com + dev.to/nishilbhave Claude Code hooks traps,
@akshay_pachaar local-model agent mechanics. Full cited analysis:
`docs/research/agentic-ai/2026-09-05-context-hygiene-execution-enforcement.md`.

## Adapted from X-scout digest (2026-09-10)

Extensions to `skills/quality/ai-agent-security/` (control-plane-outside-the-
sandbox doctrine from CVE-2026-82533 — unauthenticated harness API let the
agent self-escalate to danger-full-access; boundary credential injection from
Cloudflare Dynamic Workers — secrets never model-visible; markdown playbooks
as attacker-side standard per Google Threat Intelligence), to
`skills/knowledge-base/agent-memory-design/` (memory quarantine / HOLDING
until cold review, decision imports with acceptance-check questions,
second-brain sprawl counter-patterns), and to `skills/execution/loop/`
(resume-from-compiled-state with streaming step logs, contract-based
completion, confidence-loop ≠ verification) were adapted from the X-scout
knowledge-scout digest of 2026-09-10 (Discord thread #xTreand, cron job
f933f5a8d591). Full cited analysis:
`docs/research/agentic-ai/2026-09-10-security-boundaries-memory-lifecycle.md`.

## Adapted from X-scout digest (2026-09-12)

Extensions to `skills/knowledge-base/agent-memory-design/` (abstraction-first
embedding + merge-don't-add from Microsoft Research's Memora; write-path
control for agent-writable memory — provenance, write-time validation, audit
trail — from OWASP ASI06 / the MemoryTrap case; context files as
table-of-contents from OpenAI harness-engineering), to
`skills/quality/ai-agent-security/` (skill supply-chain doctrine — no
portable sandbox contract in skill manifests, audit allowed-tools before
install, narrow broad shell grants per grith.ai/packslip; sandbox escapes via
state-changing reads, GET-only proxies, and unauthenticated loopback control
APIs per DSEWiki / the Hugging Face swarm / the Sept-11 CVE round), to
`skills/execution/loop/` (classify-failure-before-rerun — six harness layers
to check before "same prompt, but louder"), and to
`skills/quality/verification-before-completion/` (Verification Tax framing
from arXiv:2609.04681 — measure agents by production-qualified change) were
adapted from the X-scout knowledge-scout digest of 2026-09-12 (Discord thread
#xTreand, cron job f933f5a8d591). Full cited analysis:
`docs/research/agentic-ai/2026-09-12-write-path-control-skills-sandboxes.md`.

## Adapted from X-scout digest (2026-09-15)

Extensions to `skills/execution/loop/` (long-horizon budgeting as r^H from
arXiv:2609.01660 — context compression accelerates agent rot, so reduce
dependent steps instead; fork-vs-isolated subagent context modes from
LangChain Deep Agents), to `skills/execution/dispatching-parallel-agents/`
(fork-vs-isolated context-mode selection per subagent role), to
`skills/knowledge-base/agent-memory-design/` (context-hygiene cutting rules —
block cuts, absolute-rule→principle conversion, examples→parameters for tool
docs — plus the four token-engineering levers incl. tool-output pruning),
to `skills/quality/ai-agent-security/` (per-step constraint validation +
step-indexed traces from Microsoft AgentRx), and to
`skills/debugging/diagnose/` (restate-the-problem-before-coding gate from
Lauren Tan's pstack workflow) were adapted from the X-scout knowledge-scout
digest of 2026-09-15 (Discord thread #xTreand, cron job f933f5a8d591). Full
cited analysis:
`docs/research/agentic-ai/2026-09-15-harness-context-lifecycle-subagent-boundaries.md`.

## Original work

The following were created independently in this repo:

- `skills/tools/research/` — custom web research skill
- `skills/tools/prompt-engineering-patterns/` — original patterns for authoring system prompts, agent definitions, and skill instructions
- `skills/tools/research-verify/` — research + mandatory fact-check-against-live-system pass before publishing, built from a real Herdr+NotebookLM+Codex workflow session
- `skills/tools/session-promoter/` — end-of-session memory promotion
- `skills/quality/improve-codebase-architecture/`
- `skills/quality/circuit-breaker/` — stuck-detection wrapper for the loop hook
- `skills/quality/secrets-guardrail/` — PostToolUse credential redaction hook
- `skills/quality/verify-before-stop/` — always-on regression guard
- `skills/planning/spec-writer/` — spec-first development with PreToolUse gate
- `skills/execution/loop/` — engineering loop with Stop-hook maker-checker
- `skills/execution/tdd-loop/` — TDD with automated loop verification
- `skills/communication/` — session-summary, handoff, management-talk, business-impact
- `skills/planning/scale-audit/` — Order of Magnitude Playbook enforcement
- `skills/planning/quarterly-evolution/` — quarterly tech investment framing
- `skills/quality/good-enough/` — Esthetics Trap detection
- `skills/quality/pragmatic-review/` — Engineering Diagnostic Matrix scoring
- `skills/execution/benchmark-sprint/` — parallel architectural benchmarking harness
- `skills/debugging/diagnose/`
- `agents/` — all agent definitions
- `skills/dotnet/`, `skills/qa/`, `skills/product-owner/`, `skills/apple/` — originally
  built as .NET / QA / Product Owner / Apple skill sets
- `tools/agent-evals/` — agent evaluation engine and improvement loops
- `install.sh` — install script
