# Chapter 17: Microservices Architecture

## Core Idea

Microservices architecture is a distributed style built around independently deployable services, usually aligned with bounded contexts and owned data. Its value is autonomy, change isolation, and targeted scaling—not simply small codebases. The style also demands mature operations, observability, communication contracts, and distributed transaction strategies.

## Frameworks Introduced

- **Microservice topology**: independently deployable services with APIs, isolated data, and operational ownership.
- **Bounded Context alignment**: use domain language and model boundaries to identify candidate services.
- **Granularity**: judge service size by functional cohesion, data ownership, change rate, and operational cost.
- **Data isolation**: services own their data and expose behavior rather than allowing direct database access.
- **Operational reuse versus code reuse**: share platforms and automation where helpful, but avoid shared runtime behavior that couples releases.
- **Choreography and orchestration**: choose whether services react to events independently or coordinate through an explicit workflow.
- **Sagas**: manage long-running distributed transactions through local transactions and compensating actions.

## Key Concepts

- **Bounded Context** — boundary around a consistent domain model and language.
- **Service granularity** — how much capability belongs in one service.
- **Data isolation** — each service owns and controls its persistence.
- **API layer** — stable contract through which clients interact with a service.
- **Operational reuse** — shared deployment, monitoring, security, and platform capabilities.
- **Enforced heterogeneity** — allowing each service to choose appropriate technology while preserving operational standards.
- **Choreography** — event-driven collaboration without a central coordinator.
- **Orchestration** — explicit coordinator for a multi-service process.
- **Saga** — sequence of local transactions with compensation for failure.

## Mental Models

Use microservices when independent deployability, team autonomy, fault isolation, or differentiated scaling is more valuable than local transaction simplicity.

Treat each service as a product with code, data, runtime, on-call ownership, and a contract. A service is not independent if its schema, release, or operational behavior is controlled by another team.

Prefer data ownership over shared database convenience. Cross-service queries become APIs, events, projections, or explicit reporting pipelines.

## Anti-patterns

- **Distributed monolith**: services require synchronized deployments or long synchronous chains.
- **Nano-services**: units are too small to own meaningful capability or justify operational cost.
- **Shared database coupling**: services bypass APIs and write each other’s tables.
- **Operational reuse as runtime coupling**: shared libraries force every service to release together.
- **Saga without business compensation**: technical rollback is assumed where real-world actions cannot be undone.

## Code Examples

A saga makes local state and compensation explicit:

```text
Order: create PENDING
Payment: authorize
Inventory: reserve
Order: confirm

on InventoryFailed:
  Payment: void authorization
  Order: mark REJECTED
```

Each step must be idempotent, observable, and durable enough to resume after a crash.

## Reference Tables

| Concern | Microservices decision |
|---|---|
| Boundary | Bounded context plus operational ownership |
| Data | Service-owned persistence and published contracts |
| Communication | Sync for immediate answers; async for temporal decoupling |
| Reuse | Prefer platform/operational reuse over shared domain code |
| Transactions | Local atomicity plus saga/compensation |
| Frontends | Backend-for-frontend or tailored API where client needs differ |

## Worked Example

An order platform separates Ordering, Payment, Inventory, and Fulfillment because these capabilities have different teams, change rates, and failure behavior. Each service owns its data. Checkout uses synchronous calls only for immediate authorization, then publishes an event for fulfillment. A saga records progress and compensates a payment authorization if inventory cannot be reserved. A shared observability platform is reused, but domain libraries are not shared in a way that forces synchronized release.

## Key Takeaways

1. Microservices are an organizational and operational style as much as a code structure.
2. Independence requires deployment, data, contract, and ownership autonomy.
3. Bounded contexts are strong candidates, not automatic service boundaries.
4. Distributed transactions need explicit business compensation and recovery.

## Connects To

- **Chapter 7:** defines the quantum and synchronous connascence behind service independence.
- **Chapter 14:** supplies events and delivery patterns.
- **Chapter 18:** compares microservices against simpler styles using actual drivers.

