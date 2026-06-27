---
model: opus
name: pragmatic-review
description: >
  Scores an architecture proposal, ADR, or engineering decision against the Engineering
  Diagnostic Matrix: four dimensions that distinguish dogmatic from pragmatic engineering
  culture. Outputs a verdict and concrete adjustments. Use before committing to a
  technology choice, before writing an ADR, or when a team's architecture decisions
  feel consistently over-engineered. Trigger on /pragmatic-review.
---

# Pragmatic Review

Score a proposal against the Engineering Diagnostic Matrix. Four dimensions, two
columns. The goal is not to always land in the Pragmatic column — it is to make the
trade-off consciously and justify deviations with hard data.

## The Engineering Diagnostic Matrix

| Dimension | Dogmatic | Pragmatic |
|---|---|---|
| **Scale Strategy** | Design for 100x day one | Design for next order of magnitude only |
| **Technology Choice** | Generic frameworks, NoSQL by default | Specific solutions, single VM, Relational DB first |
| **Definition of Quality** | Elegant abstractions | Simple to trace when on fire |
| **Reaction to AI** | Resists AI — resents loss of craft | Embraces AI for orchestration and speed |

A dogmatic score is not automatically wrong — there are contexts where designing for
100x day one is justified (regulated industries, safety-critical systems, known explosive
growth trajectory with hard data). But the justification must be explicit, not assumed.

## When to invoke

- Reviewing a proposed architecture, tech stack choice, or migration plan
- An ADR is about to be written and a second perspective is wanted
- A team's engineering decisions feel consistently over-engineered or status-driven
- Evaluating whether to adopt a new framework, database, or infrastructure layer
- `/pragmatic-review` is typed

## Workflow

### 1. Extract the proposal
Summarize what is being proposed in three bullets:
- What is being built or changed?
- What technology choices are involved?
- What scale or load does the system currently handle?

### 2. Score each dimension

For each of the four dimensions, assign a score:

**P** — Pragmatic: the proposal matches what current and near-term reality requires.
**D** — Dogmatic: the proposal is driven by architectural idealism rather than current need.
**D\*** — Dogmatic with justification: the proposal leans dogmatic but hard data or a
  specific constraint justifies it. State the justification explicitly.

#### Scale Strategy
- What is the current load? What is the next 10x?
- Is the proposal sized for the current-to-next-10x transition, or for a hypothetical
  future state with no load data to support it?
- Dogmatic signal: "we'll need this eventually" without a number or timeline.

#### Technology Choice
- Is the technology choice the simplest thing that solves the current problem?
- Does the proposal reach for a distributed system, NoSQL, or a heavyweight framework
  when a single VM, relational DB, or standard library would suffice?
- Dogmatic signal: "industry best practice" or "everyone uses this now" without a
  specific constraint that requires it.

#### Definition of Quality
- When this system is on fire at 3am, can an on-call engineer trace the problem in
  minutes using logs and a mental model of the code?
- Does the proposal introduce abstractions that require knowing the abstraction model
  to debug, or does it remain flat and readable under pressure?
- Dogmatic signal: abstractions justified by elegance or "separation of concerns"
  rather than operational traceability.

#### Reaction to AI
- Does the proposal account for the current reality that AI agents can generate
  boilerplate, write tests, and benchmark architectural alternatives in minutes?
- Does it free engineers to focus on uptime, architecture, and ripple effects, or
  does it double down on hand-crafted complexity as a form of craft identity?
- Pragmatic signal: AI is used to multiply architectural output, not to avoid thinking.
- Note: This dimension is less applicable for proposals in regulated or security-critical
  contexts where AI-generated code requires human review.

### 3. Identify the primary drift
If two or more dimensions score D, name the root cause:
- **Status-driven:** Technology choice is about prestige, not fitness.
- **Premature scale:** Designed for a future that has no data to support it.
- **Complexity for its own sake:** Elegance is valued over operational simplicity.
- **Craft identity:** Resistance to tools or patterns that reduce manual work.

### 4. Propose concrete adjustments
For each D score, give one concrete, actionable change that moves the proposal toward
Pragmatic without abandoning the underlying goal:

- "Replace Kubernetes with a single VM + systemd to reduce operational surface by 80%
  at current scale. Revisit at 10M req/day."
- "Start with PostgreSQL. The document-store use case can be served with a JSONB column
  and a GIN index at this scale."
- "Flatten the service mesh to a monolith with internal module boundaries. The contracts
  can be extracted to separate services if and when traffic data justifies it."

## Output format

```
## Pragmatic Review

**Proposal summary:**
- [what is being built/changed]
- [technology choices]
- [current scale / load]

**Diagnostic Matrix scores:**

| Dimension | Score | Reasoning |
|---|---|---|
| Scale Strategy | P / D / D* | [one sentence] |
| Technology Choice | P / D / D* | [one sentence] |
| Definition of Quality | P / D / D* | [one sentence] |
| Reaction to AI | P / D / D* | [one sentence] |

**Overall verdict:** [Pragmatic / Pragmatic with concerns / Dogmatic drift]
**Primary drift (if any):** [Status-driven / Premature scale / Complexity / Craft identity]

**Adjustments:**
1. [Dimension]: [concrete change]
2. [Dimension]: [concrete change]

**What would justify the dogmatic choice(s):**
[The specific data, constraint, or external requirement that would make a D score correct.
If no such justification exists, state that.]
```

## Rules

- Score each dimension independently. Do not let a strong P in one dimension
  compensate for a D in another.
- Do not soften verdicts. "Pragmatic with minor concerns" and "Dogmatic drift" mean
  different things — use the right one.
- Every D score must come with a concrete adjustment. A finding without a fix is noise.
- If you cannot determine the current scale or load, flag it as the primary unknown —
  a Scale Strategy score without load data is speculative.
- "Industry best practice" is not a justification. Name the specific constraint.
