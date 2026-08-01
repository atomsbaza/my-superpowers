# Architecture Decision Cheatsheet

## Start Here

| If you see… | Ask… | Likely action |
|---|---|---|
| “Use microservices” | Which characteristic requires independent deployment? | Compare with modular monolith |
| “High performance” | Under what workload and percentile? | Define an architecture scenario |
| “Zero downtime” | Which capability, window, and cost? | Qualify the target |
| Many tiny services | Are they cohesive and operable? | Consolidate or define ownership |
| Shared database everywhere | Who owns each invariant and schema? | Make coupling explicit |
| Architecture review repeats | Where is the rationale? | Write/supersede an ADR |

## Style Selection

1. Identify the top 3–5 characteristics.
2. Identify domain boundaries, team boundaries, and operational capability.
3. Ask whether each boundary needs different scale, deployment, or failure behavior.
4. Choose the least-worst style; record why.
5. Add a fitness function or risk test for the most important claim.

| Dominant need | Candidate |
|---|---|
| Simple local transactions and small team | Modular monolith/layered |
| Sequential transformation | Pipeline |
| Stable workflow with variants | Microkernel |
| Coarse capability separation | Service-based |
| Async fan-out and temporal decoupling | Event-driven |
| Centralized persistence bottleneck | Space-based |
| Independent team/service autonomy | Microservices |

## Boundary Rules

- Minimize connascence overall by encapsulating.
- Minimize cross-boundary connascence.
- Prefer static and weaker connascence across deployment boundaries.
- A quantum is independently deployable, functionally cohesive, and synchronously coupled inside.
- Domain boundaries are candidates; data ownership and operations decide whether they are viable.

## Risk Storming

```text
choose one dimension -> individual risk marking -> consensus -> mitigation
       -> owner + evidence -> repeat after meaningful change
```

Risk score is a prioritization aid: `impact × likelihood`. Do not confuse a precise-looking number with certainty.

## Negotiation Rules

- Translate vague words into measurable scenarios.
- Demonstration defeats discussion.
- State the reason before the constraint.
- Qualify extreme requirements to the smallest necessary scope.
- Prefer communication, collaboration, clarity, and conciseness over accidental complexity.

