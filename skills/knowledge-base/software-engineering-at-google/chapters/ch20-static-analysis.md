# Chapter 20: Static Analysis

## Core Idea

Static analysis turns organizational knowledge into repeatable feedback before code runs in production. Effective analysis scales, is usable, integrates with the developer workflow, keeps false positives low, offers fixes, and lets domain experts contribute checks.

## Frameworks Introduced

- **Developer happiness first**: An analysis that annoys users will be ignored or disabled, regardless of theoretical correctness.
  - When to use: Selecting signals, thresholds, and rollout strategy.
  - How: Measure false positives, collect feedback, tune aggressively, and explain findings in actionable language.
- **Workflow integration**: Analysis should appear where engineers already work.
  - When to use: Choosing between IDE, compiler, review, presubmit, and browsing integrations.
  - How: Layer fast advisory feedback with blocking checks for high-confidence, high-value rules.
- **Empower users to contribute**: Domain experts can create checks that a central team cannot discover alone.
  - When to use: Large organizations with many languages and specialized APIs.
  - How: Provide a common platform, contribution path, ownership, and feedback channels.
- **Suggested fixes**: Reduce the cost of acting on a finding.
  - When to use: Mechanical or locally resolvable violations.
  - How: Show the problem, rationale, and safe automated edit where possible.

## Key Concepts

- **Static analysis**: Program analysis performed without executing the program.
- **Tricorder**: Google’s platform for integrating analyses and feedback.
- **False positive**: A reported issue that is not a real problem in context.
- **Presubmit**: A check run before a change is committed.
- **Compiler integration**: Analysis emitted as part of compilation.
- **Project customization**: Local configuration that adapts shared analysis to a project.
- **Feedback channel**: A mechanism for users and analysis authors to improve checks.

## Mental Models

- A static check is a product with users, support cost, and a reputation.
- Blocking power must be earned by precision and demonstrated value.
- Analysis is most powerful when it prevents technical debt from entering, not when it reports an unmanageable backlog.
- Suggested fixes convert policy from criticism into assistance.

## Anti-patterns

- **False-positive flood**: Users learn to ignore all findings.
- **Workflow detachment**: Results arrive after the author has forgotten the change.
- **Central-only authorship**: The analysis platform misses domain-specific hazards.
- **Blocking too early**: Low-confidence checks halt work and create resistance.

## Worked Example

Tricorder-style integration can show an analyzer result in code review, offer a suggested fix, and route feedback to the analyzer owner. A high-confidence rule may become a presubmit gate; a developing rule can remain advisory in the IDE or browser. This staged enforcement preserves trust while allowing the organization to codify best practices.

## Code Examples

~~~text
edit -> analyzer finding -> explanation + suggested fix
     -> reviewer context -> presubmit gate when confidence is high
~~~

## Key Takeaways

1. Optimize for developer happiness and signal quality.
2. Put analysis in the core workflow.
3. Offer understandable findings and fixes.
4. Let domain experts contribute while preserving ownership.
5. Earn blocking authority through precision and value.

## Connects To

- **Chapter 8**: Static checks enforce style and safety guidance.
- **Chapter 15**: Analysis prevents deprecated APIs from returning.
- **Chapter 19**: Review is a natural integration point.

