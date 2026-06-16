# Research: UditAkhourii/adhd — Repository Evaluation

## Summary

ADHD (`adhd-agent` on npm) is a TypeScript library and CLI that implements parallel divergent ideation for coding agents. It solves premature convergence in LLM reasoning by fanning out problem analysis across N isolated "cognitive frames," scoring and clustering resulting ideas, then deepening the top survivors. The codebase is compact (~7 source files), well-structured, and leans on the Anthropic Claude Agent SDK as its single heavyweight dependency. It was released recently (v0.1.4, May 30, 2026) with a focused 10-day burst of commit activity and a sole maintainer. Evals show strong gains over single-shot baselines but are limited in scope and methodology rigor.

---

## Key Findings

### 1. Purpose and Target Audience

ADHD addresses anchoring bias in autoregressive reasoning — the tendency of LLMs to converge on the first plausible answer. It is explicitly designed as a **skill plugin for coding agents** (Claude Code, Cursor, Cline, Gemini CLI, Windsurf, and ~50 others), not as a standalone reasoning model. The target audience is developers using agent IDEs who face architecture decisions, fuzzy debugging, API design, and naming problems. It is not intended for deterministic tasks or simple lookups. [README](https://github.com/UditAkhourii/adhd/blob/main/README.md)

### 2. Features

- **Two-phase diverge/converge loop**: Phase 1 spawns N isolated parallel LLM calls, one per cognitive frame; Phase 2 scores, clusters, and deepens survivors. Generator and critic are separate API calls with opposing system prompts — this is a code-enforced invariant, not a prompt-level promise. [how-it-works.md](https://github.com/UditAkhourii/adhd/blob/main/documentation/how-it-works.md)
- **15 built-in frames**: Hardware engineer, regulator/auditor, 10-year-old, competitor/adversary, biology, logistics, game design, markets, inversion, budget extremes ($0 and unlimited), remove-load-bearing-assumption, speedrunner, ant colony/swarm, and 3am on-call. Each is a vantage-point prompt, not a persona. Frame selection biases toward `code`/`design` tags in engineering mode and guarantees at least one `wild` frame. [frames.ts](https://github.com/UditAkhourii/adhd/blob/main/src/frames.ts)
- **Configurable CLI flags**: `--frames N`, `--ideas N`, `--top N`, `--concurrency N`, `--context PATH`, `--model NAME`, `--no-code-mode`, `--json`, `--quiet`. [cli.ts](https://github.com/UditAkhourii/adhd/blob/main/src/cli.ts)
- **Library API**: Exports `run()`, `renderText()`, `selectFrames()`, `FRAMES`, and all core TypeScript types for programmatic use. [index.ts](https://github.com/UditAkhourii/adhd/blob/main/src/index.ts)
- **Streaming event emission**: Progress events (frame start/end, scoring, clustering, deepening, warnings) are emitted to stderr during a run. [cli.ts](https://github.com/UditAkhourii/adhd/blob/main/src/cli.ts)
- **Trap detection**: The critic pass explicitly identifies "seductive-but-broken" ideas and flags them with mechanistic explanations — the biggest delta over baseline in evals. [EVALS.md](https://github.com/UditAkhourii/adhd/blob/main/EVALS.md)
- **npx install path**: `npx skills add UditAkhourii/adhd` auto-detects agent type and installs the SKILL.md for the active agent runtime. [README](https://github.com/UditAkhourii/adhd/blob/main/README.md)

### 3. Tech Stack and Architecture

| Layer | Technology |
|---|---|
| Language | TypeScript (strict mode), compiled to `dist/` |
| Runtime | Node.js >=18 |
| LLM integration | `@anthropic-ai/claude-agent-sdk ^0.1.0` |
| Concurrency | `p-limit ^5.0.0` (semaphore over parallel API calls) |
| Schema validation | `zod ^3.23.0` |
| Build | `tsc` + `tsx` for dev hot-reload |
| Test/eval runner | Custom bench suite (`bench/run-evals.ts`, `bench/judge.ts`) |

Source is 7 files: `engine.ts` (orchestration), `frames.ts` (frame data + selection), `llm.ts` (SDK wrapper + JSON parser), `types.ts` (all interfaces), `render.ts` (ANSI terminal output), `cli.ts` (arg parsing + entry), `index.ts` (public API re-exports). [src/](https://github.com/UditAkhourii/adhd/tree/main/src)

The architecture is deliberately stateless: each branch is a fresh `query()` call against the Claude Agent SDK with `allowedTools: []` and `permissionMode: "bypassPermissions"`. Token costs scale linearly (not quadratically) because branches never share KV-cache. [how-it-works.md](https://github.com/UditAkhourii/adhd/blob/main/documentation/how-it-works.md)

### 4. Code Quality Indicators

- **TypeScript strict mode** enforced; `any` requires justification per CONTRIBUTING.md. [CONTRIBUTING.md](https://github.com/UditAkhourii/adhd/blob/main/CONTRIBUTING.md)
- **Minimal dependencies**: Only 3 runtime deps (`claude-agent-sdk`, `p-limit`, `zod`). This is a deliberate design constraint called out in contributing guidelines.
- **No unit or integration tests**: The `bench/` directory contains an eval harness against live LLM calls, not unit tests. There is no `__tests__/` directory, no Jest/Vitest configuration, and no test script in `package.json`. [package.json](https://github.com/UditAkhourii/adhd/blob/main/package.json)
- **No retry logic in `llm.ts`**: The `callLLM()` function is a single-shot wrapper. If the SDK call fails or returns a non-success subtype, it throws immediately with no backoff or retry.
- **`render.ts` is fully readable**: The ANSI rendering function is clean, well-commented, and easy to extend. It follows the `// brief → wide set → converge → deepened → provocation` output contract documented in source comments.
- **Error handling is minimal but explicit**: CLI wraps `main()` in a try-catch with `process.exit(1)`. `llm.ts` checks `message.subtype !== "success"` and throws. No silent failures in the visible paths, but the eval harness has no observable error path testing.
- **Documentation is thorough**: 7 dedicated docs files covering install, architecture, frames reference, API reference, eval methodology, use-case guidance, and comparison with CoT/ToT.

### 5. Maintenance Activity

- **Sole maintainer**: `UditAkhourii` (Udit Raj), with GitHub Actions bot for automated commits.
- **Commit window**: All commits fall between May 26 and June 4, 2026 — a 10-day intensive launch burst with no activity before or since (as of research date). [commits/main](https://github.com/UditAkhourii/adhd/commits/main)
- **13 open issues, 0 closed, 0 open PRs**: All 13 issues were opened on May 27, 2026 — the same day — and appear to be the maintainer's own roadmap tracking, not community bug reports. No issues have been closed.
- **41 forks, 819 stars**: Healthy star count for a 3-week-old project, suggesting viral distribution. No evidence of a deep contributor community yet.
- **v0.1.4** is the latest release (May 30, 2026). 4 patch releases in ~4 days during the launch window.

### 6. Gaps and Weaknesses

**No unit or integration tests**: The only automated testing is the eval harness, which requires live Anthropic API calls (~10 LLM calls per problem). There is no way to run a fast offline test suite, no mocks at the LLM boundary, and no regression coverage for engine logic changes.

**Hard Claude dependency**: `llm.ts` calls the `@anthropic-ai/claude-agent-sdk` exclusively. The `--model` CLI flag can override model name, but the SDK call structure (`preset: "claude_code"`) is Claude-specific. Adding OpenAI, Gemini, or local model support would require a significant refactor of `llm.ts`.

**No retry/resilience in `callLLM()`**: A single transient API failure aborts the entire branch run. With 5 frames × 6 ideas, a flaky network call loses the whole job.

**Cost accounting undocumented**: Issue #8 explicitly flags that "cost accounting is undercounted in README and paper." Users have no cost estimation tool.

**Eval methodology is thin**: Only 6 benchmark problems, all engineering-focused, judged by a single LLM with a fixed system prompt. No inter-rater reliability, no comparison against MoA or other tree-of-thought implementations (issue #14). The 1-in-6 loss case ("llm-hang-cli") shows ADHD scores 4 vs baseline 9 on builder usefulness — the breadth-over-pragmatism tradeoff has a real failure mode.

**Single maintainer, short track record**: All commit activity is within 10 days of launch. No evidence of sustained maintenance, no second committer, no response to issues.

**`@anthropic-ai/claude-agent-sdk ^0.1.0` is pre-1.0**: API surface could break across minor versions. The `permissionMode: "bypassPermissions"` setting raises a security concern for teams running this in multi-tenant or production contexts.

**No streaming to stdout**: Progress events go to stderr; `--json` output is a single JSON blob after the full run. No incremental result streaming for long-running jobs.

---

## Trade-offs / Caveats

- **Eval self-assessment risk**: The benchmark was designed and run by the maintainer. Issue #14 (head-to-head vs MoA and competitors) is open and unresolved — independent validation does not yet exist.
- **"Community integrations" unverifiable**: The README cites repowire PR #313, mstack, and zk-flow-oss as adopters, but no links to these external repos are provided.
- **Star count vs. depth**: 819 stars in under 3 weeks is high relative to 41 forks and 0 closed issues — viral-but-shallow adoption pattern.
- **`permissionMode: "bypassPermissions"`**: Bypasses all tool permission checks in the Claude Agent SDK. Needs to be addressed before production use.

---

## Build vs. Improve Verdict

**Lean toward fork-and-improve, but only if the team's use case closely matches the current constraints.**

The core architecture is sound and the code is clean enough to build on. The diverge/converge two-phase loop, the frame data structure, `types.ts`, and `render.ts` are all well-reasoned starting points. The codebase is small enough (~500-700 lines of TypeScript across 7 files) that a team could read it completely in a morning.

However, three gaps push against a clean fork:

1. **No tests whatsoever** — any meaningful extension requires building a test harness from scratch before making changes safely.
2. **Hard Claude SDK dependency** — if the team needs model-agnostic operation, the `llm.ts` layer needs a full replacement.
3. **Single burst of activity with no follow-up** — 13 self-assigned issues, all open, none commented on. The project may be in a post-launch stall.

**Build from scratch if**: the team needs model-agnostic LLM support, requires a tested and resilient production foundation, or has a substantially different orchestration model (stateful branches, human-in-the-loop, streaming results).

**Fork and improve if**: the team is Claude SDK-native, wants exactly this diverge-converge pattern with frames, and is prepared to add tests, retry logic, cost estimation, and model abstraction as first tasks before any feature work.

---

## Sources

- [UditAkhourii/adhd — GitHub](https://github.com/UditAkhourii/adhd)
- [README.md](https://github.com/UditAkhourii/adhd/blob/main/README.md)
- [src/engine.ts](https://github.com/UditAkhourii/adhd/blob/main/src/engine.ts)
- [src/frames.ts](https://github.com/UditAkhourii/adhd/blob/main/src/frames.ts)
- [src/types.ts](https://github.com/UditAkhourii/adhd/blob/main/src/types.ts)
- [src/llm.ts](https://github.com/UditAkhourii/adhd/blob/main/src/llm.ts)
- [src/cli.ts](https://github.com/UditAkhourii/adhd/blob/main/src/cli.ts)
- [src/render.ts](https://github.com/UditAkhourii/adhd/blob/main/src/render.ts)
- [package.json](https://github.com/UditAkhourii/adhd/blob/main/package.json)
- [EVALS.md](https://github.com/UditAkhourii/adhd/blob/main/EVALS.md)
- [CONTRIBUTING.md](https://github.com/UditAkhourii/adhd/blob/main/CONTRIBUTING.md)
- [documentation/how-it-works.md](https://github.com/UditAkhourii/adhd/blob/main/documentation/how-it-works.md)
- [documentation/frames.md](https://github.com/UditAkhourii/adhd/blob/main/documentation/frames.md)
- [GitHub Issues](https://github.com/UditAkhourii/adhd/issues)
- [commits/main](https://github.com/UditAkhourii/adhd/commits/main)
