---
model: sonnet
name: scale-audit
description: >
  Assess the current scale tier of a system and determine what the next 10x requires
  before committing to any architecture change. Prevents premature over-engineering
  by grounding decisions in the Order of Magnitude Playbook: 10x = Single VM + Relational
  DB, 100x = Vertical scale + caching, 1,000x = NoSQL + sharding. Trigger on /scale-audit
  or whenever someone proposes a distributed/microservice/NoSQL change without stating
  current load numbers.
---

# Scale Audit

Before touching the architecture, establish where you actually are and what the next
10x genuinely requires. Most systems are proposed at the wrong tier.

## When to invoke

- User proposes introducing microservices, Kubernetes, NoSQL, or horizontal sharding
- Architecture decision is framed around "future scale" without citing current numbers
- A Kubernetes / distributed-system migration is being planned for a product still in early growth
- User asks "should we shard / rewrite / migrate?"
- `/scale-audit` is typed

## The Order of Magnitude Playbook

| Current scale | Right architecture | Wrong to introduce yet |
|---|---|---|
| **10x** (thousands of req/day) | Single VM + Relational DB | Kubernetes, microservices, NoSQL, sharding |
| **100x** (millions of req/day) | Vertical scale (more RAM/CPU) + caching layer | NoSQL, event sourcing, distributed consensus |
| **1,000x** (hundreds of millions of req/day) | NoSQL + read replicas + horizontal sharding | (this is earned, not chosen day one) |

A single modern VM can handle 120 cores and terabytes of RAM. GitHub runs millions of
requests per second on 5–6 containers. Complexity has a cost: every distributed system
component is a new failure mode, a new latency source, and a new on-call page.

## Audit workflow

### 1. Establish current numbers
Ask for (or look up) these three metrics. Do not proceed without at least one of them:
- **Daily active requests** (or transactions/day)
- **Peak concurrent users**
- **Current p99 latency under normal load**

If none are available, state that explicitly — a scale decision without load data is
guesswork and should be deferred until numbers exist.

### 2. Map to tier
Using the table above, state which tier the system is currently in and which tier the
next 10x lands in. Be explicit:
> "At ~500k req/day you are solidly in the 10x tier. The next order of magnitude
> (5M req/day) still lands in the 100x tier — vertical scaling and a caching layer,
> not a distributed rewrite."

### 3. Evaluate the proposal
Score the proposed change against the current tier:

- **Right-sized:** The proposal matches what the current-to-next-tier transition actually needs.
- **Premature:** The proposal jumps ahead by one or more tiers. State the earliest point
  at which the proposed change becomes justified (what load number triggers the need).
- **Insufficient:** The current bottleneck is real but the proposed solution is the
  wrong tool for this tier (e.g. adding a cache when the DB needs an index).

### 4. State the immediate alternative
For premature proposals, always name the simpler thing that solves today's problem:
- Vertical scale the existing VM before sharding
- Add a read replica before adding a cache cluster
- Add a DB index before adding a caching layer
- Profile and fix the hot query before changing the data model

### 5. Define the trigger condition
State the concrete metric that would make the proposed architecture appropriate:
> "Revisit this when sustained p99 > 500ms under 2M req/day on the largest available
> single VM, with DB indexes and a caching layer already in place."

## Output format

```
## Scale Audit

**Current tier:** [10x / 100x / 1,000x]
**Current load:** [numbers or "unknown — cannot audit without data"]
**Next 10x lands at:** [number]

**Proposal verdict:** [Right-sized / Premature / Insufficient]
**Reason:** [one paragraph]

**Recommended path now:** [concrete, tier-appropriate alternative]
**Trigger to revisit:** [specific metric + condition]
```

## Rules

- Never validate a distributed-system proposal without load numbers. Request them first.
- Vertical scaling is almost always the right next step before horizontal. Say so.
- Do not balance the verdict — if it is premature, say premature, not "it depends."
- Cite the specific failure mode the premature architecture would introduce (operational
  complexity, latency from network hops, distributed transaction overhead, etc.).
- A scale audit is not a veto — it is a forcing function to justify the complexity cost.
