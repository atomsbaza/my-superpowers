# Chapter 3: Knowledge Sharing

## Core Idea

An organization scales knowledge by combining a safe learning culture with mechanisms that make questions, answers, teaching, and canonical documentation easy to find. Start with simple behaviors—ask questions and write things down—then add forums, mentorship, classes, code review, and ownership as scale demands.

## Frameworks Introduced

- **Psychological safety as the foundation**: People must be able to admit ignorance, ask basic questions, and try ideas without humiliation.
  - When to use: Onboarding, incident response, team discussions, and learning programs.
  - How: Avoid feigned surprise, reward useful questions, make mentors explicit, and model uncertainty from senior people.
- **Ask, understand context, share**: Learning is a loop rather than a one-time transfer.
  - When to use: Unfamiliar systems, debugging, and joining a new organization.
  - How: Ask a focused question, learn why the answer is true, then record or teach what you learned.
- **Canonical sources**: Prefer one maintained, discoverable source over a collection of competing documents.
  - When to use: Organization-wide guidance, API usage, style rules, or onboarding.
  - How: Give the source an owner, put it under version control where practical, provide stable links, and retire duplicates.
- **Readability as standardized mentorship**: Code review can teach language idioms, APIs, structure, documentation, and testing—not merely approve correctness.
  - When to use: Growing a large engineering organization without concentrating expertise in a few people.
  - How: Make review feedback educational, certify experienced reviewers, and integrate the process with normal code review.

## Key Concepts

- **Information island**: Knowledge trapped in one person, team, or private conversation.
- **Information fragmentation**: Many partial or conflicting sources that force readers to reconstruct the answer.
- **YAQS**: A scalable question-and-answer system that preserves answers for future seekers.
- **Mentorship**: An explicit relationship that lowers the cost of asking for help.
- **Canonical source**: The maintained authority to which competing guidance can point.
- **Readability**: Google’s language- and practice-oriented mentorship approval process.

## Mental Models

- Treat questions as reusable assets when the answer is recorded and searchable.
- Every teaching mechanism has a scale limit; combine one-to-one help with one-to-many channels.
- Code is knowledge encoded in a form that future maintainers can consume.
- A document without ownership is a future information island.

## Anti-patterns

- **Punishing basic questions**: It teaches people to hide uncertainty and repeat mistakes.
- **Expert-only support**: A few heroes become a bottleneck and a single point of failure.
- **Wiki sprawl**: Unowned, overlapping pages make readers guess which answer is current.
- **Teaching outside workflow**: Optional training disappears when delivery pressure rises.

## Worked Example

The readability process began as a senior engineer reviewing each new hire’s first major change. As hiring grew, volunteers and certification scaled the practice. The useful pattern is not the exact approval gate; it is standardized mentorship embedded in code review, where the learning happens at the moment the engineer is changing real code.

## Key Takeaways

1. Make it safe to say “I don’t know.”
2. Capture answers in searchable, owned sources.
3. Scale human expertise through forums, classes, documentation, and review.
4. Put learning in the developer workflow.
5. Reward people who broaden organizational knowledge, not only their own output.

## Connects To

- **Chapter 2**: Humility, respect, and trust determine whether people participate.
- **Chapter 9**: Review is both quality control and knowledge distribution.
- **Chapter 10**: Documentation turns individual understanding into durable context.

