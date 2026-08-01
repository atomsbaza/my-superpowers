# Chapter 18 — Adaptation

## Core Idea

Production systems live in changing environments: traffic, data, dependencies, regulations, teams, hardware, runtimes, and business expectations all move. The design goal is not to predict every change. It is to make likely changes cheap, observable, reversible, and compatible with the running system.

## Frameworks Introduced

- **Adaptable software design:** isolate change behind interfaces, configuration, dependency injection, and replaceable components.
- **Adaptable enterprise architecture:** use explicit service boundaries, versioned contracts, and ownership that can evolve.
- **Releases should not hurt:** plan configuration, documentation, marketing, deployment, support, timing, expansion, rollout, and cleanup as one change system.
- **Zero-downtime sequence:** expand compatibility first, roll out gradually, then remove old behavior after evidence.

## Key Concepts

### Adaptation over time

Every workaround becomes part of the system unless it is removed. Track assumptions such as maximum record size, protocol version, node count, dependency behavior, and operator procedure. Review them when load, data, or ownership changes.

### Adaptable software design

Use stable interfaces around volatile details. Dependency injection and configuration can make integrations replaceable and testable, but indirection is not automatically good: the boundary must represent a real change axis. Keep compatibility behavior explicit, instrumented, and removable. Avoid spreading vendor-specific assumptions through the whole codebase.

### Adaptable enterprise architecture

Architecture evolves through contracts. Define ownership, data authority, protocol versions, backward/forward compatibility, migration strategy, and failure behavior. A distributed boundary without an operational contract merely relocates coupling.

### Releases should not hurt

A release includes more than binaries. Coordinate:

- configuration and secret changes;
- database/schema compatibility;
- documentation and runbooks;
- customer and support communication;
- deployment and rollback automation;
- timing, staffing, and dependency readiness;
- monitoring and success criteria.

The safest release sequence is usually:

```text
expand -> migrate/dual-read or dual-write -> roll out gradually
       -> verify -> switch behavior -> clean up old path
```

The expand step makes old and new versions coexist. Cleanup waits until rollback is no longer needed. This is slower than an in-place breaking change, but it reduces the blast radius and keeps recovery possible.

### Zero-downtime expansion, rollout, and cleanup

For a schema change, add the new nullable field or table first, deploy code that understands both forms, backfill in bounded batches, switch reads/writes, and remove the old path only after all nodes and consumers have migrated. For a service behavior change, use feature flags or traffic shaping with an owner and expiration. For a node replacement, drain traffic, preserve or reconcile state, and verify health before increasing exposure.

Zero downtime is not merely “the process stayed running.” It requires continuity of useful service, controlled state transition, and a rollback path.

## Reference Table

| Release concern | Failure if omitted | Safer practice |
|---|---|---|
| Compatibility | Old/new versions disagree | Expand before switch |
| Configuration | Wrong value or secret | Validate, version, and stage |
| Database change | Rollback impossible | Backward-compatible migration |
| Rollout | Full blast radius | Canary, gradual traffic, metrics |
| Cleanup | Recovery path removed | Delay until evidence supports removal |
| Support/docs | Operators and users surprised | Update runbooks and communication |

## Worked Example

A new order schema replaces `customer_name` with a customer reference. A direct migration would break old workers and make rollback difficult. Instead, add the reference field, deploy code that reads the reference when present and falls back to the old value, dual-write for a bounded period, backfill, monitor mismatches, then switch all reads and remove the old field in a later release. Each phase has a rollback and an observable completion condition.

## Key Takeaways

1. Design for change axes that are likely and expensive to ignore.
2. Make contracts, compatibility, ownership, and migration state explicit.
3. Expand before switching; roll out with evidence; clean up after rollback risk passes.
4. A release includes people, operations, communication, and documentation.

## Connects To

- Chapter 14 provides configuration, startup, shutdown, and administration controls.
- Chapter 17 supplies the evidence needed for gradual rollout and cleanup.
- The master skill’s review workflow turns these principles into practical design and release checks.

