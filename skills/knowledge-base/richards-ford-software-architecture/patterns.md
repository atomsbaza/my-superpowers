# Patterns and Techniques

## Architecture Characteristics Extraction
**When to use**: Before selecting a style or topology.
**How**: derive qualities from domain concerns, explicit requirements, constraints, operations, and failure scenarios; convert them into measurable scenarios.
**Trade-offs**: more discovery time up front, less fashion-driven complexity later.

## Architecture Katas
**When to use**: To practice or compare architecture reasoning.
**How**: give a bounded scenario, identify drivers and characteristics, propose alternatives, and defend trade-offs.
**Trade-offs**: improves breadth and communication but cannot replace production evidence.

## Fitness Functions
**When to use**: When a structural, operational, or process quality must survive continuous change.
**How**: encode the rule as a test, metric, monitor, or experiment at an appropriate feedback frequency.
**Trade-offs**: automation creates maintenance cost; weak or noisy checks lose trust.

## Domain Component Discovery
**When to use**: When defining components or service candidates.
**How**: use Actor/Actions, Event Storming, and Workflow views; assign requirements, responsibilities, characteristics, and data ownership; restructure.
**Trade-offs**: domain alignment improves change locality but requires domain collaboration.

## Closed Layers
**When to use**: When technical separation and controlled change matter.
**How**: require calls to pass through the next layer; record and govern justified variances.
**Trade-offs**: improves isolation but can create sinkholes and cross-layer change cost.

## Pipes and Filters
**When to use**: For sequential data transformation.
**How**: compose focused filters over bounded pipes with explicit contracts, backpressure, retries, and poison-message handling.
**Trade-offs**: composability versus state, ordering, and operational pipeline complexity.

## Microkernel Plugins
**When to use**: When a stable workflow has many variants or extensions.
**How**: keep invariant behavior in a small core; expose versioned contracts; discover plugins through a registry.
**Trade-offs**: extensibility versus contract, registry, security, and compatibility cost.

## Event Publication with Outbox
**When to use**: When local state change and event publication must not be lost.
**How**: commit business state and an outbox record in one transaction; relay and retry records; make consumers idempotent.
**Trade-offs**: reliable at-least-once delivery requires deduplication and operational cleanup.

## Service/Data Partitioning
**When to use**: When a capability has distinct ownership, change, scale, or availability needs.
**How**: choose coarse-grained boundaries; define data ownership and contracts; migrate shared data gradually.
**Trade-offs**: independence versus distributed consistency, integration, and reporting complexity.

## Saga
**When to use**: For long-running business transactions spanning service-owned data.
**How**: execute local transactions, record progress, and issue business compensations on failure.
**Trade-offs**: availability and autonomy versus eventual consistency and more complex recovery.

## Risk Storming
**When to use**: Before major releases, after meaningful architecture change, or when a characteristic is critical.
**How**: identify independently, reach collaborative consensus, mitigate, assign owners, and repeat.
**Trade-offs**: consumes group time but exposes risks a single architect will miss.

## Architecture Decision Record
**When to use**: For a significant architecture choice.
**How**: record context, alternatives, decision, consequences, status, compliance, and notes; supersede rather than erase.
**Trade-offs**: small documentation cost prevents repeated debate and lost rationale.

## C4-Style Communication
**When to use**: When explaining architecture to mixed audiences.
**How**: progressively show context, containers, components, and code; title and label every view.
**Trade-offs**: multiple views require maintenance but are clearer than one overloaded diagram.

