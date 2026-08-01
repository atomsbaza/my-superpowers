# Chapter 8: Component-Based Thinking

## Core Idea

Components are the building blocks of an architecture. Good component boundaries group meaningful capabilities, align responsibilities with architecture characteristics, and make change local. The architect and development team should discover components collaboratively, then revisit their granularity as understanding improves.

## Frameworks Introduced

- **Domain partitioning**: organize components around business capabilities, workflows, or domain responsibilities.
  - **When to use:** when business boundaries, ownership, or change patterns dominate.
- **Technical partitioning**: organize components around technical concerns such as presentation, business logic, and persistence.
  - **When to use:** when a small system or technical constraint makes domain boundaries unclear or premature.
- **Component identification flow**:
  1. Identify initial components.
  2. Assign requirements.
  3. Analyze roles and responsibilities.
  4. Analyze architecture characteristics.
  5. Restructure components.
- **Actor/Actions, Event Storming, and Workflow approaches**: alternative discovery techniques for finding cohesive components.
- **Conway’s Law**: system structure tends to mirror the communication structure of the organization.

## Key Concepts

- **Component** — a building block of an application, usually a group of classes or source files.
- **Domain partitioning** — partitioning by business capability or domain responsibility.
- **Technical partitioning** — partitioning by technical layer or concern.
- **Component granularity** — the size and responsibility scope of a component.
- **Entity trap** — creating components around data entities rather than behavior and capability.
- **Actor/Actions approach** — derive components from actors and the actions they perform.
- **Workflow approach** — follow a business process through steps and responsibilities.
- **Event Storming** — collaborative exploration of domain events, commands, policies, and boundaries.

## Mental Models

Use the architect role to establish partitioning and characteristics; use the developer role to validate implementation seams and revise granularity. The boundary must work in code, not only in a diagram.

Treat component discovery as an iterative flow. An initial partition is a hypothesis; requirements and quality pressures are evidence that may require restructuring.

Use Conway’s Law intentionally. If teams cannot communicate effectively across a boundary, the architecture may need clearer ownership, a different partition, or a deliberate platform relationship.

## Anti-patterns

- **Entity trap**: one component per table/entity, scattering workflows across the system.
- **Layer-only partitioning**: forcing every domain change through broad technical layers when independent capabilities are needed.
- **Premature granularity**: splitting components before responsibilities and characteristics are understood.
- **Diagram-only components**: naming boundaries that do not exist in code, deployment, or team ownership.

## Code Examples

A component identification worksheet:

```text
Requirement: place an order
Actors: customer, shop, payment provider
Actions: price, reserve, authorize, confirm, notify
Characteristics: auditability, availability, deployability
Candidate components: Ordering, Payment, Inventory, Notification
Restructure question: which component owns each invariant and data store?
```

## Reference Tables

| Approach | Best input | Risk |
|---|---|---|
| Actor/Actions | Clear user roles and capabilities | Misses internal workflows |
| Event Storming | Domain experts and complex process | Needs facilitation and shared language |
| Workflow | Explicit end-to-end business process | Can create process-centric coupling |
| Entity-based | Existing data model | Scattered behavior and anemic boundaries |

## Worked Example

For the auction system, the team first creates `Bidder`, `Auctioneer`, and `System` components from actors and actions. Event Storming then reveals streaming and bid-ordering responsibilities that do not belong to the original components. The team adds `VideoStreamer` and `BidStreamer`, assigns data and quality characteristics, and evaluates whether the resulting units form one quantum or multiple independently deployable quanta.

## Key Takeaways

1. Components should own coherent responsibilities and the invariants around them.
2. Domain partitioning usually preserves business change better; technical partitioning can still be appropriate.
3. Discover boundaries collaboratively and revise them with evidence.
4. Component design and deployment quantum decisions are related but distinct.

## Connects To

- **Chapter 7:** evaluates component boundaries as possible quanta.
- **Chapter 9:** components become the structural elements of architecture styles.
- **Chapter 22:** team boundaries and guidance influence component health.

