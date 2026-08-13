# Research: `/show-me` and visual context engineering for coding agents

## Summary

Dex Horthy's August 12, 2026 article proposes that coding agents should explain themselves with compact visual representations instead of defaulting to long prose. The accompanying `show-me` skill uses the smallest useful view for the problem: component trees, call stacks, diagrams, shallow file trees, pseudocode, type signatures, diffs, and focused HTML artifacts. The approach is especially valuable before implementation, when humans need to review program shape, and after implementation, when reviewers need to understand a large diff. For `my-superpowers`, this is a strong candidate for a reusable communication skill that makes research, design, planning, and review artifacts easier to inspect without replacing human technical judgment.

## Key Findings

- **The problem is communication quality, not only model intelligence.** Horthy argues that agents have become more capable on paper while the user experience has become harder to read: jargon, walls of prose, and less useful conversational voice. The article's remedy is to optimize the interface for how people understand information, not just for how models generate it. [Dex Horthy — `/show-me: compact visual representations for coding agents`](https://x.com/dexhorthy/status/2087569590268391897)

- **Use the smallest representation that preserves the important shape.** The official skill instructs the agent to keep prose brief and choose a focused representation: pseudocode for logic, call trees for runtime flow, component trees for UI structure, file trees for ownership and refactor scope, Mermaid for interactions, and diffs when the surrounding structure is already known. [HumanLayer `show-me` skill](https://github.com/humanlayer/skills/blob/main/plugins/show-me/skills/show-me/SKILL.md)

- **Program design is the highest-leverage use case.** The article recommends discussing types, signatures, and call stacks before an agent writes code. These artifacts expose the intended shape of a design while changes are still cheap to correct. The same technique can be used after the fact to navigate a large diff and decide where detailed review is needed. [Dex Horthy — `/show-me`](https://x.com/dexhorthy/status/2087569590268391897)

- **The visual vocabulary maps naturally to common engineering questions.**

  | Question | Useful representation |
  | --- | --- |
  | “What owns this UI state?” | Component tree |
  | “What happens after this command?” | Call stack or sequence diagram |
  | “Where should this change live?” | Shallow file tree |
  | “What is the algorithm?” | Pseudocode |
  | “What is the contract before implementation?” | Types and signatures |
  | “What changed?” | Diff-shaped sketch |
  | “How should this interaction feel?” | HTML mockup or explainer |

- **The skill is intentionally lightweight and portable.** The public repository distributes it as a normal Agent Skill and documents installation with `npx skills add humanlayer/skills --skill show-me`. The skill body is mostly presentation guidance, so it can be adapted to agents that support Markdown, Mermaid, or generated HTML without requiring a new orchestration runtime. [HumanLayer skills repository](https://github.com/humanlayer/skills)

- **HumanLayer treats artifacts as durable collaboration objects.** Its product documentation describes research, designs, mockups, and plans as versioned artifacts tied to a task, with comments and decisions feeding back into agent work. This supports the article's broader point: visual explanations are most useful when they remain reviewable artifacts, not transient chat output. [HumanLayer](https://www.humanlayer.dev/)

## Trade-offs / Caveats

- **Visuals can still be wrong.** A concise diagram that omits an important boundary can be more misleading than verbose prose. The skill itself says to include omitted context when it would hide ownership or order; humans still need to validate the representation against the code.

- **This is a communication layer, not a correctness guarantee.** `show-me` can make an agent's assumptions easier to inspect, but it does not replace tests, code review, architecture decisions, or runtime evidence.

- **HTML artifacts add operational friction.** They can be clearer than text for UI and dense concepts, but they introduce a file-opening step and may not render consistently in every agent client. Use them when a diagram or short text sketch is insufficient.

- **The source article is recent and experience-based.** It is a practitioner proposal published August 12, 2026, not an independent usability study. Treat claims about readability and visual cognition as design rationale rather than experimentally established performance results.

- **Scope should stay narrow.** The skill recommends choosing one or a few representations rather than producing every possible visual. Overproducing diagrams would recreate the same cognitive load the approach is meant to remove.

## Implications for `my-superpowers`

- Add a reusable `show-me`-style communication skill under `skills/communication/` or `skills/tools/`.
- Make the skill available during research, design, planning, implementation, and review, with a default instruction to choose the smallest useful visual.
- Standardize a small set of outputs: component tree, call stack, file tree, Mermaid sequence/state diagram, pseudocode, type/signature sketch, diff sketch, and optional HTML explainer.
- Teach existing research and planning skills to include a visual when it materially clarifies ownership, data flow, control flow, or change scope.
- Keep the skill advisory: it should improve explanations and reviewability, not silently make design decisions or treat diagrams as source of truth.

## Suggested adoption sequence

1. Prototype the guidance as a small communication skill using the official `show-me` skill as the reference.
2. Try it on one existing `my-superpowers` workflow, preferably code review or architecture planning.
3. Compare the resulting artifacts for clarity, omitted context, and review time.
4. Add narrowly scoped templates only after repeated use shows that a representation is worth standardizing.

## Sources

- [Dex Horthy — `/show-me: compact visual representations for coding agents`](https://x.com/dexhorthy/status/2087569590268391897) — Primary article and proposal summarized in this report.
- [HumanLayer `show-me` skill](https://github.com/humanlayer/skills/blob/main/plugins/show-me/skills/show-me/SKILL.md) — Official skill instructions and representation examples.
- [HumanLayer skills repository](https://github.com/humanlayer/skills) — Installation command and available skill listing.
- [HumanLayer](https://www.humanlayer.dev/) — Product context for artifact-based research, design, planning, and implementation workflows.
