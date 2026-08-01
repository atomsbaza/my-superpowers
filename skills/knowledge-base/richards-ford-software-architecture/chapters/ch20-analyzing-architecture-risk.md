# Chapter 20: Analyzing Architecture Risk

## Core Idea

Every architecture contains risk. The architect’s responsibility is to identify and qualify risk early, then mitigate the highest-impact and most-likely problems before production reveals them. Risk storming makes this activity collaborative, evidence-based, and repeatable.

## Frameworks Introduced

- **Risk matrix**: classify risk using impact and likelihood, commonly producing a 1–9 score.
  - **When to use:** when prioritizing architecture risks or explaining why one concern deserves investment.
  - **How:** score impact and likelihood separately, discuss assumptions, and focus mitigation on high combined risk.
- **Risk assessment**: evaluate architecture areas against selected dimensions such as availability, performance, scalability, data loss, or security.
- **Risk storming**:
  1. **Identification:** participants independently mark risks on an architecture diagram.
  2. **Consensus:** the group compares scores, exposes assumptions, and agrees on risk areas.
  3. **Mitigation:** the team chooses changes, owners, and follow-up measurements.
- **Agile story risk analysis**: apply the same matrix to stories when a risky feature can threaten iteration or architecture outcomes.

## Key Concepts

- **Impact** — consequence if a risk occurs.
- **Likelihood** — probability that the risk occurs.
- **Risk score** — combination of impact and likelihood.
- **Risk dimension** — a focused area such as availability, elasticity, or security.
- **Risk storming** — collaborative architecture-risk discovery.
- **Identification** — individual risk discovery before group influence.
- **Consensus** — collaborative qualification and shared understanding.
- **Mitigation** — design, process, or operational response that reduces risk.

## Mental Models

Separate risk discovery from solution advocacy. Participants should identify risk independently before the group discusses mitigations; otherwise the loudest expert determines what everyone sees.

Focus each storming session on one dimension where possible. Narrow focus produces better analysis and makes disagreements interpretable.

Use diagrams as a shared risk surface. The value is not the colored notes; it is the conversation about why a boundary, dependency, or data store is risky.

## Anti-patterns

- **Architect-only risk review**: missing implementation and operational knowledge.
- **Consensus-first identification**: group influence hides risks that one participant would have found alone.
- **Risk score without mitigation**: producing a heat map that does not change the architecture.
- **One-time storming**: assuming risk does not change after features, teams, or dependencies change.

## Code Examples

A simple risk score:

```text
impact  = 3   # service unavailable to all users
likelihood = 2  # possible under expected dependency failure
risk = impact * likelihood = 6   # high-priority mitigation
```

The numbers are prompts for comparison, not precision probabilities.

## Reference Tables

| Phase | Rule | Output |
|---|---|---|
| Identification | Work individually first | Marked architecture areas |
| Consensus | Ask why scores differ | Shared risk qualification |
| Mitigation | Choose owner and evidence | Architecture/process change |
| Revisit | Repeat after meaningful change | Updated risk picture |

## Worked Example

In the nurse diagnostics example, participants storm availability, elasticity, and security separately. They identify the diagnostics engine as a throughput risk, the database as an availability risk, and a shared API gateway as a security risk. The mitigations add caching and queue channels for outbreak traffic, improve database failover, and separate access paths. Developers participate, uncovering implementation risks the architect had missed.

## Key Takeaways

1. Risk analysis is continuous architecture work, not a launch checklist.
2. Separate individual discovery from group consensus.
3. Use risk dimensions and a simple matrix to focus discussion.
4. Every high risk needs a mitigation, owner, and evidence of improvement.

## Connects To

- **Chapter 6:** measures and fitness functions provide mitigation evidence.
- **Chapter 19:** risk and alternatives belong in ADRs.
- **Chapter 21:** diagrams make architecture risk discussable.

