# Chapter 15 — Design Summary

## Core Idea

Production resilience is a system property assembled from many design decisions. Networking, security, availability, capacity, administration, and operations must agree on failure boundaries and recovery behavior. A strong design makes dangerous waiting, hidden coupling, ambiguous ownership, and unbounded growth visible before production exposes them.

## Cross-Cutting Review Framework

### Stability

- What are the integration points?
- Which failures can trigger a chain reaction or cascading failure?
- Where are timeouts, circuit breakers, bulkheads, fail-fast checks, and handshakes applied?
- Are cleanup and cancellation paths as defensive as success paths?
- Can a slow or hostile dependency consume all local resources?

### Capacity

- What is the representative workload and burst shape?
- What resource becomes constrained first?
- Are pools, queues, sessions, payloads, and data growth bounded?
- Is work being repeated unnecessarily?
- Does a scale-out change remove the bottleneck or move it?

### Networking and security

- Are interfaces, routes, service identities, and failover paths explicit?
- Are listeners exposed only to intended networks?
- Does every component have the minimum required privilege?
- Can secrets be rotated without unsafe emergency changes?

### Availability

- What feature-level availability is actually required?
- What is the failure domain: process, node, zone, region, dependency, or operator?
- What state is lost or replayed on failover?
- How are ownership, fencing, reconnection, and split-brain handled?
- What degraded mode preserves the most valuable work?

### Administration and operations

- Does QA exercise production-like operational behavior?
- Are configuration, startup, shutdown, and admin actions testable?
- Can operators see saturation, queueing, dependency health, and recovery progress?
- Is the incident procedure itself designed, rehearsed, and observable?

## Design Heuristics

1. **Prefer bounds over hopes.** A timeout, queue limit, session lifetime, and cache maximum turn an unbounded failure into a controlled decision.
2. **Recover before diagnosing.** Restore service safely, preserve evidence automatically, then investigate the deeper cause.
3. **Contain at the dependency boundary.** Do not let a failed integration point occupy every local worker.
4. **Make bad states legible.** A fast, explicit failure is easier to operate than a silent fallback or indefinite wait.
5. **Test the transitions.** Steady state matters, but startup, overload, failover, cache coldness, partial reachability, and deployment are where assumptions are exposed.
6. **Design for the next change.** Every system will evolve; make configuration, protocols, topology, and operations adaptable.

## Compact Review Table

| Question | Evidence to request |
|---|---|
| What fails first? | Saturation and dependency test data |
| What happens next? | Sequence diagram or failure injection result |
| What is bounded? | Limits, deadlines, and rejection metrics |
| How is service restored? | Runbook, automation, and recovery test |
| How do we know? | Logs, metrics, alerts, and operator views |
| What changes safely? | Rollout, rollback, compatibility, and migration plan |

## Worked Example

During a provider outage, the application uses a 60-second default network timeout, unlimited retries, and one shared worker pool. The review identifies three changes: a provider-specific deadline and circuit breaker, a separate bulkhead for provider calls, and an explicit degraded state that queues only idempotent work. Monitoring exposes open-circuit state, queue depth, and recovery. The design is improved across stability, capacity, availability, and operations at once.

## Key Takeaways

1. Review the entire failure path, not isolated components.
2. Require evidence for capacity, failover, and recovery claims.
3. Bounds, containment, observability, and adaptation are the recurring design themes.

## Connects To

- Chapter 16 applies these ideas to an operational incident.
- Chapter 17 explains transparency and operating feedback loops.
- Chapter 18 covers adaptation and releases that do not hurt.

