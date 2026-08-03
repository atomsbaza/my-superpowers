# Chapter 8: Style Guides and Rules

## Core Idea

Style guides are organizational infrastructure: they reduce cognitive load, prevent dangerous constructs, and make large-scale change possible. A rule must justify its maintenance and enforcement cost, optimize for readers, remain consistent, and be automated when practical.

## Frameworks Introduced

- **Rules must pull their weight**: A rule is justified when its benefits exceed the cost of learning, enforcing, and changing it.
  - When to use: Creating or revising style guidance.
  - How: State the problem, gather evidence, estimate enforcement cost, and remove rules that no longer provide value.
- **Optimize for the reader**: Code conventions should make unfamiliar code predictable to the next engineer.
  - When to use: Naming, formatting, API usage, and review disagreements.
  - How: Prefer consistency and low surprise over an author’s local preference.
- **Three rule categories**: Rules to avoid danger, rules to enforce best practices, and rules to build consistency.
  - When to use: Classifying the purpose and strictness of a proposed rule.
  - How: Use the strongest enforcement for safety-critical guidance; allow more flexibility where judgment matters.
- **Automated enforcement**: Formatters and error checkers turn guidance into reliable, low-friction feedback.
  - When to use: Repeated, objective, machine-detectable conventions.
  - How: Put checks in the developer workflow and provide fixes when possible.

## Key Concepts

- **Style arbiter**: A responsible expert or group that maintains language guidance.
- **Error checker**: A tool that detects violations or risky constructs.
- **Formatter**: A tool that applies deterministic layout rules.
- **Consistency**: Similar code looks and behaves similarly across teams and time.
- **Practicality**: The constraint that guidance must work with real tools, code, and migration cost.

## Mental Models

- A style guide is a shared interface for human readers and automated tooling.
- Consistency is a force multiplier for code search, reviews, onboarding, and LSCs.
- Guidance is appropriate when judgment is required; rules are appropriate when repetition and risk justify enforcement.
- Changing a rule is a migration project, not merely an edit to prose.

## Anti-patterns

- **Personal-preference rules**: They impose organization-wide cost without a material benefit.
- **Unenforced rules**: They create arguments and inconsistent application.
- **Surprising constructs**: Clever or error-prone language features shift cost to every future reader.
- **Permanent exceptions**: Accumulated exceptions destroy the predictability the rule was meant to create.

## Worked Example

The std::unique_ptr case shows how a new best practice needs more than a recommendation. Guidance must explain the safer construct, identify dangerous old patterns, provide migration support, and use automated checks to prevent backsliding. The gofmt case goes further: deterministic formatting removes an entire class of review debate and makes code look consistent by construction.

## Reference Table

| Guidance type | Best mechanism |
|---|---|
| Avoid a dangerous construct | Static check, possibly blocking |
| Encourage a best practice | Linter, suggested fix, review guidance |
| Normalize formatting | Deterministic formatter |
| Context-dependent judgment | Documentation and human review |

## Key Takeaways

1. Write rules for readers and long-term scale.
2. Classify the rule before choosing enforcement.
3. Automate objective guidance and make fixes easy.
4. Revisit rules as tools, languages, and evidence change.
5. Preserve consistency because it compounds across the organization.

## Connects To

- **Chapter 9**: Code review handles judgment that automation cannot.
- **Chapter 17**: Consistent code improves search and navigation.
- **Chapter 22**: Style consistency makes large-scale changes safer.

