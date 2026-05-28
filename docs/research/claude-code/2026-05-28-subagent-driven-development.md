# Research: `subagent-driven-development` Skill (obra/superpowers)

**Date:** 2026-05-28
**Topic:** https://github.com/obra/superpowers/tree/main/skills/subagent-driven-development
**Decision:** Whether to adopt, adapt, or skip for existing skill+agent workflow

---

## Summary

The `subagent-driven-development` skill is an execution-orchestration pattern: a protocol for how Claude runs a multi-task implementation plan by dispatching a fresh subagent per task and applying a mandatory two-stage review (spec compliance first, then code quality) before marking each task complete. It is not a phase in a development pipeline itself — it is a coordination layer that sits inside the implementation phase, between receiving a finalized plan and producing a reviewed, committed implementation. For an already-structured pipeline, the skill's two-stage review separation is the most actionable novel piece. The skill conflicts at one point with the `clarify-before-acting` global rule and depends on several sibling superpowers skills that are not installed.

---

## What It Does

The skill consists of four files:

- **SKILL.md** — Behavioral instructions loaded into the controller session. Changes how Claude runs a plan: instead of implementing tasks itself in one continuous session, it dispatches each task to a fresh subagent with only the context that task needs, then runs two more subagents in sequence as reviewers.
- **implementer-prompt.md** — A fill-in template for the implementer subagent. It standardizes pre-work clarification, implementation steps (code, test, verify, commit, self-review), and a structured status report with four states: `DONE`, `DONE_WITH_CONCERNS`, `BLOCKED`, `NEEDS_CONTEXT`.
- **spec-reviewer-prompt.md** — A template for a first-pass reviewer whose sole job is verifying "did they build what was asked, nothing more, nothing less?" The prompt explicitly instructs the reviewer not to trust the implementer's own report and to verify against actual code.
- **code-quality-reviewer-prompt.md** — A template for a second-pass reviewer who only runs after spec compliance passes. This one delegates to the existing `requesting-code-review/code-reviewer.md` sibling skill and adds additional checks for file responsibility, decomposition, and whether the change contributed new size problems.

**Behavioral changes the skill enforces on the controller:**

- Context isolation: each subagent gets only what it needs, never the controller's full session history.
- Continuous execution: "Do not pause to check in with your human partner between tasks." Stopping is only justified for a blocking issue, genuine ambiguity that prevents progress, or task completion.
- Model tier selection: use the cheapest model that can handle the role. Isolated function tasks go to fast cheap models; integration tasks to standard models; architecture and review tasks to the most capable model.
- Sequential two-stage gate: code quality review only starts after spec compliance passes. Re-review is mandatory if fixes are made after a review.

---

## Problem It Solves

The skill targets a specific failure mode of long in-session implementation: **context window pollution**. When a single session implements 10+ tasks sequentially, the session accumulates all prior code, all prior decisions, and all prior errors. Later tasks get a degraded, distracted model. The fresh-subagent-per-task pattern prevents this by giving each implementer a clean context constructed precisely for its task.

The two-stage review addresses a second failure mode: a single review conflates two distinct questions ("is this the right thing?" and "is it built well?") and reviewers drift toward the second because it is easier to evaluate. Separating spec compliance from code quality makes each check more reliable.

Model-tier selection addresses cost: running the most capable model for a mechanical one-file implementation is wasteful; the skill makes explicit that roles should be matched to model capability.

---

## Comparison to Existing Workflow

The existing pipeline phases are:

```
/brainstorming → /to-prd → /tdd → /prototype → code-reviewer → /session-summary
```

With purpose-specific domain agents: swift-reviewer, ui-reviewer, xcode-build, simulator-qa, ios-test-runner, privacy-reviewer.

**Where this skill would slot in:** Between `/prototype` (or wherever a finalized implementation plan is produced) and `code-reviewer`. It is an execution protocol for the plan, not a phase-producing skill.

| Dimension | Existing setup | subagent-driven-development |
|---|---|---|
| Review stages | Single-stage `code-reviewer` | Two-stage: spec compliance first, then code quality |
| Review scope | Domain-specific (swift, ui, privacy) | Role-specific (compliance vs quality); domain is additive |
| Context isolation | Not explicit in named skills | Core behavioral rule |
| Continuous execution | Not specified | Mandated — no check-ins between tasks |
| Model tier selection | Not specified | Explicit hierarchy by task complexity |
| Plan execution | Not a named skill | Named, structured, with status protocol |

**What it would complement:** The existing domain reviewers (swift-reviewer, ui-reviewer, privacy-reviewer) can plug directly into the code-quality review stage. The two-stage pattern does not replace them — it provides the orchestration layer that sequences them correctly after spec compliance passes first.

**What it would not replace:** None of the existing pipeline phases. It is purely an execution protocol layer.

---

## Gaps / Conflicts

**Conflict 1 — Continuous execution vs. `clarify-before-acting` global rule.**
The skill mandates: "Do not pause to check in with your human partner between tasks." The `clarify-before-acting.md` global rule mandates: "Before building, state your interpretation of the request explicitly if it could mean more than one thing." These are in direct tension. The implementer-prompt.md does include a pre-work clarification step per subagent, which partially mitigates this, but the controller-level "no check-ins" instruction could suppress clarification the global rule requires. The skill's own exception language ("stop for genuine ambiguity") should be made explicit before adoption.

**Conflict 2 — Dependency on missing sibling skills.**
The `code-quality-reviewer-prompt.md` delegates to `requesting-code-review/code-reviewer.md`, a sibling skill from the superpowers marketplace. This needs to be substituted with the existing `code-reviewer` agent invocation — a one-line fix.

**Gap — Issue #601: accumulated learnings not propagated.**
Discoveries made by one subagent (e.g., "this ORM wraps errors in a custom type") are invisible to subsequent subagents because each starts fresh. Existing domain skills (swiftdata-pro, swift-concurrency) partially compensate, but runtime discoveries during a plan are still lost. The fix: maintain a running "Project Discoveries" block in the controller and inject it into each subsequent subagent prompt.

**Gap — No iOS/Xcode-specific hooks.**
The skill's implementer and reviewer templates are language-agnostic. The iOS workflow (xcode-build, simulator-qa, ios-test-runner, SwiftData testing constraints) would need to be injected into the implementer template or delegated to existing specialist agents.

**Gap — Model tier selection requires manual mapping.**
The "use the cheapest model that can handle the task" guidance is correct but leaves the user to maintain their own model-ID-to-tier mapping. Not a blocker, but worth documenting.

---

## Recommendation

**Adapt — extract the two-stage review pattern and the implementer status protocol; do not install as-is.**

### What to keep

- **Two-stage review separation**: Run a spec compliance pass *before* domain quality reviewers. This is the single biggest behavioral improvement over the current single-stage `code-reviewer`.
- **Implementer status protocol**: `DONE`, `DONE_WITH_CONCERNS`, `BLOCKED`, `NEEDS_CONTEXT` — low-cost, high-value addition to any subagent dispatch template.
- **Model-tier selection heuristic**: Worth documenting explicitly in workflow preferences.

### What to rewrite before adopting

- `code-quality-reviewer-prompt.md` reference to `requesting-code-review/code-reviewer.md` → substitute with existing `code-reviewer` agent call.
- "No check-ins" continuous execution rule → scope to "no unnecessary progress summaries" to stay consistent with `clarify-before-acting.md`.
- Implementer template → inject SwiftData, Xcode build, and simulator-lifecycle guidance (or reference existing swiftdata-pro/swift-concurrency skills in the subagent context block).

### What to watch

- **Issue #601** — implement a running "Project Discoveries" block in the controller and inject it per-task if context isolation is adopted.

---

## Sources

- [SKILL.md](https://github.com/obra/superpowers/blob/main/skills/subagent-driven-development/SKILL.md)
- [implementer-prompt.md](https://github.com/obra/superpowers/blob/main/skills/subagent-driven-development/implementer-prompt.md)
- [spec-reviewer-prompt.md](https://github.com/obra/superpowers/blob/main/skills/subagent-driven-development/spec-reviewer-prompt.md)
- [code-quality-reviewer-prompt.md](https://github.com/obra/superpowers/blob/main/skills/subagent-driven-development/code-quality-reviewer-prompt.md)
- [GitHub Issue #601: accumulate learnings across subagents](https://github.com/obra/superpowers/issues/601)
- [obra/superpowers repository](https://github.com/obra/superpowers/)
