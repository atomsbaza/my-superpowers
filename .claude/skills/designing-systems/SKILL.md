---
name: designing-systems
description: >
  Designs the technical system architecture from requirements or a feature brief.
  Produces a system design document covering component diagrams, data flow, API
  contracts, entity model, deployment topology, and cross-cutting concerns. Use
  when the user asks for system design, architecture design, component design,
  a design document, C4 diagram, data flow diagram, or deployment topology.
  Reads workflow-state.json for requirements context when available.
---

## Purpose

Translate requirements into a concrete, implementable technical design. The output is a design document that an engineer can execute without further clarification.

## Input

- `workflow-state.json` → `requirements_analysis` if available (preferred)
- Direct user description of the system to design
- Existing partial design to extend or review

If requirements analysis has not been done and the request is complex (>3 bounded contexts implied), recommend running `analyzing-requirements` first.

## Process

### 1. Design Principles Applied

Before designing, state the three most relevant principles for this system:
- Prefer simple, proven patterns unless requirements demand otherwise
- Design for the failure case first
- Make the data model the source of truth — the rest follows from it

### 2. Component Design (C4 Level 1 + 2)

Produce an ASCII C4 context diagram then a container diagram:

**Context Diagram** (System in Environment):
```
[External User] --> [System Name] --> [External Dependency]
```

**Container Diagram** (System internals):
```
[API Service] --> [Application Service] --> [Domain Model]
                                        --> [Repository] --> [OceanBase]
[API Service] --> [Message Broker] --> [Worker Service]
```

Label every arrow with the interaction type (HTTP, gRPC, SQL, event).

### 3. Data Flow

Describe the primary request path step by step:
1. Request enters at [entry point]
2. [Auth/validation happens]
3. [Core logic executes]
4. [Persistence occurs]
5. [Response returns]

For write-heavy flows, include the outbox pattern if cross-service consistency is required.

### 4. API Contracts

For each API surface, produce an OpenAPI-style sketch:

```
POST /api/v1/[resource]
Request:  { field: type, ... }
Response: { field: type, ... }
Errors:   400 (validation), 401 (auth), 409 (conflict), 500 (internal)
```

Note idempotency requirements on every mutation endpoint.

### 5. Entity Model

List the core entities with their key fields and relationships:

```
Entity: OrderHeader
  - Id: Guid (PK)
  - CustomerId: Guid (FK → Customer)
  - Status: OrderStatus (enum)
  - CreatedAt: DateTimeOffset
  - UpdatedAt: DateTimeOffset (rowversion for optimistic concurrency)
  Relationships: has many OrderLine
```

For OceanBase targets, recommend partitioning strategy per entity:
- Event/log tables: RANGE on `CreatedAt` (monthly intervals)
- High-write lookup tables: HASH on `Id`
- Reference/config tables: no partitioning needed

### 6. Deployment Topology

Describe the deployment units:
- Services and their runtime (.NET 8 minimal API, worker service, etc.)
- Infrastructure dependencies (OceanBase cluster, cache, message broker)
- Network boundaries and ingress

### 7. Cross-Cutting Concerns

Address each:
- **Authentication:** mechanism (JWT, API key, mTLS) and where validated
- **Authorization:** RBAC/ABAC, policy enforcement layer
- **Caching:** what is cached, TTL, invalidation strategy
- **Rate limiting:** per-user or per-endpoint limits
- **Observability:** structured logs (Serilog), metrics (Prometheus/OpenTelemetry), distributed tracing
- **Error handling:** global exception middleware, problem details (RFC 7807)
- **Resilience:** retry policy (Polly), circuit breaker for external calls

### 8. OceanBase-Specific Design Notes

When OceanBase is the persistence target:
- Identify which tables need partitioning and state the strategy
- Flag any query pattern that would require `FOR SHARE` and redesign with optimistic concurrency
- Note that EF Core migrations must include `migrationBuilder.Sql(...)` for partition DDL

## Output

Write design to `docs/design/system-design.md` (create `docs/design/` if needed).

Update `workflow-state.json`:
```json
{
  "stage": "system_designed",
  "design": {
    "document_path": "docs/design/system-design.md",
    "entities": ["EntityName"],
    "services": ["ServiceName"],
    "requires_partitioning": true
  }
}
```

Print the full design document to the conversation.
