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

- `.claude/skills/martin-clean-code/` — extracted frameworks, principles, and
  techniques from both books (naming, functions, testing, refactoring, code
  smells, TDD, professionalism, estimation, craftsmanship), generated via the
  `book-to-skill` converter

## Original work — Learning Domain-Driven Design

The following skill was created in this repo, derived from concepts in
*Learning Domain-Driven Design* by Vlad Khononov (O'Reilly):

- `.claude/skills/khononov-ddd/` — extracted frameworks, principles, and
  techniques from the book (subdomains, bounded contexts, context mapping,
  tactical business-logic patterns, architectural patterns, communication
  patterns, design heuristics, EventStorming, microservices, event-driven
  architecture, data mesh), generated via the `book-to-skill` converter

## Original work — TDD Knowledge Base

`.claude/skills/tdd-knowledge-base/` was synthesized from a NotebookLM deep
web research pass (89 sources) on Test-Driven Development, not from a single
book. It attributes named techniques and quotes to their original
practitioners (Kent Beck, Martin Fowler, Robert C. Martin, Steve Freeman &
Nat Pryce, David Heinemeier Hansson) where the research identifies them, and
flags the few gaps the research left unverified.

## Original work

The following were created independently in this repo:

- `skills/tools/research/` — custom web research skill
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
- `.claude/agents/` — all agent definitions
- `.claude/skills/` — .NET / QA / Product Owner skills
- `tools/agent-evals/` — agent evaluation engine and improvement loops
- `install.sh` — install script
