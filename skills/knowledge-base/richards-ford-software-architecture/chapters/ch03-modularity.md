# Chapter 3: Modularity

## Core Idea

Modularity is the foundation for controlling change. A modular system groups related responsibilities and limits the relationships between groups. Cohesion, coupling, abstractness, instability, and connascence provide vocabulary and measurements for identifying where change will be easy or expensive.

## Frameworks Introduced

- **Cohesion and coupling**: maximize related responsibilities within a module and minimize dependencies between modules.
  - **When to use:** when partitioning code, services, components, or teams.
  - **How:** move elements that change together closer; reduce the number, strength, and scope of cross-module knowledge.
- **Abstractness–instability main sequence**: use abstractness and instability as signals for whether a package is too concrete, too depended upon, or poorly balanced.
- **Connascence**: two elements are connascent when changing one requires changing or coordinating the other.
  - **When to use:** when ordinary coupling metrics miss temporal, value, or runtime relationships.
  - **How:** identify the kind of connascence, its strength, its locality, and whether it crosses an encapsulation boundary.
- **Three connascence rules**: minimize overall connascence by encapsulating; minimize remaining cross-boundary connascence; maximize connascence inside boundaries.

## Key Concepts

- **Cohesion** — how strongly responsibilities inside a module belong together.
- **Coupling** — the degree to which modules depend on each other.
- **Static connascence** — a relationship visible in source or structure, such as name, type, or algorithm agreement.
- **Dynamic connascence** — a runtime relationship, such as execution order, timing, or identity.
- **Connascence of name (CoN)** — elements must agree on a name.
- **Connascence of type (CoT)** — elements must agree on a type.
- **Connascence of meaning (CoM)** — values have shared interpretation.
- **Connascence of position (CoP)** — argument or data positions must match.
- **Connascence of algorithm (CoA)** — elements must use the same algorithm.
- **Connascence of execution (CoE)** — execution order matters.
- **Connascence of timing (CoT)** — actions must occur within a timing relationship.
- **Connascence of identity (CoI)** — elements must reference the same identity.

## Mental Models

Think of connascence as a change map. Two modules can have few syntactic references yet still be tightly coupled if they must coordinate order, timing, or a shared interpretation.

Prefer weaker connascence, more local connascence, and static over dynamic connascence when the boundary is unavoidable. Dynamic connascence is harder to discover, test, and govern across a distributed boundary.

Use metrics as signals, not verdicts. High coupling may be justified inside a cohesive component; low line-count complexity does not guarantee a healthy boundary.

## Anti-patterns

- **Entity trap**: creating one component per database entity, producing scattered business behavior and excessive coupling.
- **Metric worship**: treating a threshold for cohesion, coupling, or complexity as a universal design rule.
- **Hidden dynamic coupling**: relying on ordering, timing, or shared identity without documenting the protocol.

## Code Examples

The difference between explicit and hidden connascence:

```text
// Explicit: the type and interface expose the dependency.
sendPayment(PaymentRequest request)

// Hidden: caller must know that validate() must run first and that
// calculateTotal() mutates shared state before submit().
validate(); calculateTotal(); submit();
```

Move the protocol behind a deeper interface so callers do not coordinate internal steps.

## Reference Tables

| Connascence | Typical strength | Boundary risk |
|---|---:|---|
| Name/type | Lower | Usually visible and statically checkable |
| Meaning/position | Medium | Contract drift and parameter mistakes |
| Algorithm | Higher | Duplicated knowledge must stay synchronized |
| Execution/timing | High | Runtime ordering and performance assumptions |
| Identity | High | Shared state and lifecycle coordination |

## Worked Example

An order flow has `Pricing`, `Tax`, and `Checkout` modules. Initially, `Checkout` knows that pricing must run before tax, tax must mutate a shared total, and a later call reads a flag set by tax. This is dynamic connascence of execution and meaning across a boundary. Introduce a `Quote` value returned by a pricing policy and pass it to checkout. The internal order remains, but the public interface carries the result explicitly, reducing hidden coordination.

## Key Takeaways

1. Modularity reduces the cost and blast radius of change.
2. Strong or dynamic connascence is especially dangerous across boundaries.
3. Encapsulate related change and expose protocols explicitly.
4. Use metrics to find questions, then validate them with design reasoning.

## Connects To

- **Chapter 7:** applies connascence to architectural quanta and deployment boundaries.
- **Chapter 8:** uses modularity to identify components and partitions.
- **Chapter 17:** uses bounded contexts and data isolation to manage distributed coupling.

