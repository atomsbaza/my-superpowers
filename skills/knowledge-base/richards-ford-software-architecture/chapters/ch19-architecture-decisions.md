# Chapter 19: Architecture Decisions

## Core Idea

Architectural decisions are significant choices that shape structure, characteristics, constraints, or future change. They should preserve context and rationale so future teams can understand why a choice was made, what alternatives were rejected, and which consequences were accepted.

## Frameworks Introduced

- **Architecture decision anti-patterns**:
  - **Covering Your Assets:** selecting a choice mainly to protect the architect from blame rather than serve the system.
  - **Groundhog Day:** repeatedly revisiting the same decision because no durable record or decision process exists.
  - **Email-Driven Architecture:** making decisions in scattered conversations that are difficult to find, review, or understand.
- **Architecturally significant decision**: a choice that affects structure, architecture characteristics, dependencies, or future options.
- **Architecture Decision Record (ADR)**:
  - **When to use:** for significant choices and the trade-offs behind them.
  - **How:** record title, status, context, decision, consequences, compliance, and notes; store it where the team can find and evolve it.
- **Request for Comments (RFC)**: invite review before finalizing a decision when the choice affects multiple people or teams.

## Key Concepts

- **Decision context** — forces, constraints, and problem motivating a choice.
- **Alternative** — another viable option considered.
- **Consequence** — benefit, cost, risk, and future constraint caused by the decision.
- **Compliance** — how the decision is verified in implementation.
- **Variance** — an approved exception to a decision or standard.
- **ADR** — durable record of an architecture decision.
- **Decision status** — proposed, accepted, deprecated, or superseded.

## Mental Models

Record why, not merely what. A diagram can show how the system works; an ADR preserves the reasoning and trade-offs that cannot be inferred from structure.

Use the lightest decision process that makes the choice visible. Not every coding choice needs an ADR; every significant architecture choice needs discoverable rationale.

Treat decisions as living constraints. Add compliance checks, review consequences as context changes, and supersede rather than silently rewrite history.

## Anti-patterns

- **Covering Your Assets**: choosing defensively for personal safety rather than business value.
- **Groundhog Day**: revisiting settled decisions because rationale is absent.
- **Email-Driven Architecture**: relying on inbox history as the architecture repository.
- **ADR as bureaucracy**: recording every trivial implementation detail and making the process too heavy to use.

## Code Examples

Minimal ADR shape:

```markdown
# ADR-0042: Use event publication for fulfillment handoff
Status: accepted

## Context
Fulfillment may be unavailable and must not block order confirmation.

## Decision
Publish OrderConfirmed through the outbox after local commit.

## Consequences
Consumers are eventually consistent and must be idempotent.
```

## Reference Tables

| ADR section | Purpose |
|---|---|
| Title/status | Identify and classify the decision |
| Context | Explain forces and constraints |
| Decision | State the chosen option clearly |
| Consequences | Capture benefits, costs, and risks |
| Compliance | Explain how the rule is verified |
| Notes | Preserve follow-up and related references |

## Worked Example

Two architects disagree about REST versus asynchronous messaging. Instead of recording a preference, the RFC states the drivers: peak throughput, user response needs, retry behavior, and team skill. A production-like comparison measures both options. The ADR selects synchronous REST for immediate queries and events for long-running work, documents the trade-off, and adds a fitness check for forbidden synchronous chains.

## Key Takeaways

1. Record decisions that shape structure, qualities, and future options.
2. Preserve context and consequences so the decision can be evaluated later.
3. Use RFCs for collaboration and ADRs for durable memory.
4. Verify important decisions with automation or explicit review.

## Connects To

- **Chapter 1:** “why” completes the architecture definition.
- **Chapter 6:** fitness functions can enforce ADRs.
- **Chapter 20:** risk analysis supplies evidence for architecture decisions.

