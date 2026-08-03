# Chapter 9: Code Review

## Core Idea

Code review is a scalable engineering control: it improves correctness, comprehension, consistency, knowledge sharing, and the historical record of a codebase. The process works best when authors optimize for readers, changes stay small, and automation removes mechanical work.

## Frameworks Introduced

- **Review for the reader**: The author knows the local context; reviewers and future maintainers do not.
  - When to use: Every change, especially public APIs and unfamiliar code.
  - How: Explain intent, keep the diff focused, and ask whether a new reader can understand the change.
- **Small changes**: A reviewable change has a narrow purpose and a manageable cognitive surface.
  - When to use: Feature work, refactoring, bug fixes, and migrations.
  - How: Separate unrelated cleanup, state behavioral impact, and submit incremental changes.
- **Automation before human review**: Machines should handle formatting, builds, tests, and obvious static checks.
  - When to use: Any repeatable review condition.
  - How: Run checks before or during review so human attention is reserved for design and judgment.
- **Review as organizational memory**: The review record preserves why a change happened and how alternatives were considered.
  - When to use: Future debugging, archaeology, audits, and onboarding.
  - How: Write durable change descriptions and keep comments tied to decisions.

## Key Concepts

- **Change list (CL)**: A reviewable unit of code change.
- **Code owner**: A person or group authorized to approve changes in a repository area.
- **Readability**: A standardized approval and mentorship process for language and code-quality practices.
- **Correctness review**: Checking behavior against requirements and failure modes.
- **Comprehension review**: Checking whether the code is understandable and maintainable.
- **LGTM**: An approval signal, not a substitute for knowing what was reviewed.

## Mental Models

- Code is a liability until it proves its value; every added line creates future reading and maintenance cost.
- A review is a design conversation with an artifact attached.
- Minimize reviewer count while ensuring the right expertise and ownership.
- Politeness is throughput infrastructure: defensive authors slow the feedback loop.

## Anti-patterns

- **Rubber-stamp review**: It creates the appearance of safety without checking assumptions.
- **Huge mixed-purpose diffs**: Reviewers miss defects and authors cannot respond to focused feedback.
- **Reviewer crowding**: Too many reviewers increase latency and contradictory feedback.
- **Mechanical nitpicking by humans**: It spends scarce attention on checks a tool could perform.
- **Unclear change descriptions**: Future readers cannot reconstruct intent or risk.

## Worked Example

A strong CL describes the problem, the chosen approach, important alternatives, and validation performed. Automated checks report build, test, formatting, and analyzer results before reviewers spend time on design. The primary reviewer then evaluates behavior and maintainability, while an owner confirms the change fits the area’s contracts. The result is a small, auditable artifact rather than a meeting transcript.

## Reference Table

| Review concern | Preferred mechanism |
|---|---|
| Formatting and simple style | Formatter or linter |
| Build and regression risk | Automated tests and CI |
| Design and maintainability | Human reviewer |
| Ownership and local conventions | Code owner/readability approval |
| Historical rationale | Change description and review record |

## Key Takeaways

1. Review every meaningful change, but keep each change small.
2. Optimize for the reader and future maintainer.
3. Automate mechanical checks.
4. Be polite, specific, and professional.
5. Preserve intent in the review record.

## Connects To

- **Chapter 3**: Reviews distribute expertise.
- **Chapter 8**: Automation enforces objective style rules.
- **Chapter 19**: Tooling should make the review flow clear and low-friction.

