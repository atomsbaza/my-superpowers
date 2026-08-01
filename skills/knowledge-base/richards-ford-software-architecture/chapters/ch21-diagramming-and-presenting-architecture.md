# Chapter 21: Diagramming and Presenting Architecture

## Core Idea

Architecture diagrams are communication tools, not decoration. Good diagrams reveal the structure and decisions relevant to an audience, while good presentations build understanding incrementally. Choose a notation and level of detail that answers a question; avoid artifact worship and diagrams that create complexity without insight.

## Frameworks Introduced

- **Diagramming standards**:
  - **UML:** broad modeling notation with formal elements.
  - **C4:** context, container, component, and code levels for progressive architecture communication.
  - **ArchiMate:** enterprise architecture modeling across business, application, and technology concerns.
- **Diagram guidelines**: meaningful titles, directional lines, understandable shapes, precise labels, restrained color, and keys where needed.
- **Manipulating time**: present architecture through incremental builds, zooms, and staged detail rather than one overloaded image.
- **Infodeck versus presentation**: an infodeck is a self-contained reference; a presentation supports a live narrative.

## Key Concepts

- **Context diagram** — system in its environment and external relationships.
- **Container diagram** — deployable/runtime units inside a system.
- **Component diagram** — major building blocks within a container.
- **Code diagram** — implementation-level detail where useful.
- **Irrational Artifact Attachment** — defending a diagram, notation, or artifact because of emotional investment rather than communication value.
- **Incremental build** — revealing a diagram in stages.
- **Invisibility** — the audience cannot infer the key point because the presentation or diagram lacks focus.

## Mental Models

Choose the audience before the notation. An operations team needs deployment, dependencies, failure, and ownership; a product stakeholder needs business capability and trade-off; a developer needs boundaries and contracts.

Use a diagram to answer one question. If it must show every detail, create several views and connect them.

Use time as a fourth dimension. Reveal the current state, the change, and the reason in a sequence that lets the audience build a mental model.

## Anti-patterns

- **Big-picture spaghetti**: one diagram tries to contain every system and implementation detail.
- **Decorative arrows**: lines have no direction, protocol, ownership, or meaning.
- **Tool/notation attachment**: protecting a format even when the audience cannot understand it.
- **Slide invisibility**: important text is too small, colors are ambiguous, or the story is missing.

## Code Examples

A compact C4-style context sketch:

```text
[Customer] --places order--> [Ordering System]
[Ordering System] --authorizes--> [Payment Provider]
[Ordering System] --publishes--> [Fulfillment System]
```

Add detail only after the audience understands this level.

## Reference Tables

| View | Primary question | Audience |
|---|---|---|
| Context | What surrounds the system? | Business, architecture, operations |
| Container | What runs and communicates? | Developers, operators |
| Component | How is a container partitioned? | Developers, architects |
| Code | How is a component implemented? | Developers |

## Worked Example

To present a proposed service extraction, start with the current context and business capability. Add the current container boundary, then highlight the change seam, data ownership, and deployment flow. Next show one request and one failure path. Finish with the ADR trade-off and migration sequence. The audience sees why the change exists before being asked to judge implementation details.

## Key Takeaways

1. Diagram for a question and an audience.
2. Use C4-style progressive detail when communicating software structure.
3. Make lines, labels, colors, and keys carry meaning.
4. Build presentations incrementally; do not hide the architecture inside one artifact.

## Connects To

- **Chapter 7:** diagrams can expose quanta and synchronous coupling.
- **Chapter 19:** diagrams communicate ADR context and consequences.
- **Chapter 20:** diagrams are the shared surface for risk storming.

