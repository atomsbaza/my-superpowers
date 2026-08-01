# Chapter 13 — Availability

## Core Idea

Availability is a business requirement expressed through technical behavior. It cannot be designed responsibly until the required service, time window, user population, dependencies, and acceptable degraded modes are explicit. Once the requirement is clear, topology choices such as load balancing and clustering can be evaluated against failure modes and economics.

## Frameworks Introduced

- **Availability requirement gathering:** ask what must be available, for whom, when, and at what quality.
- **Availability budgeting:** express target downtime and recovery expectations in a measurable budget.
- **Load-balancing choices:** DNS, reverse proxy, and hardware/software load balancers have different failure and state implications.
- **Clustering semantics:** redundancy must define state, ownership, failover, and split-brain behavior.

## Key Concepts

### Gather the requirement

“The system must be highly available” is not testable. Gather requirements by feature and business period:

- Which functions are critical, and which can be read-only or deferred?
- Which users or regions are covered?
- Is availability measured continuously, during business hours, or during a seasonal peak?
- What latency and error thresholds count as available?
- How quickly must service recover, and how much data loss is acceptable?
- Which third-party or internal dependencies are included in the commitment?

Different features can have different budgets. A product catalog may remain available while checkout is unavailable or placed into a durable pending state. Designing all features for the strictest target can cost more and create unnecessary complexity.

### Document the requirement

Record target, measurement window, exclusions, dependencies, maintenance policy, incident clock, and ownership. Include the difference between service availability and data correctness. A response that returns quickly with wrong or stale data is not necessarily a successful degraded mode.

Use an availability budget as a design constraint. It should influence timeout values, failover time, deployment strategy, test coverage, and staffing. It is also a tradeoff tool: investments should be evaluated against the business value of reducing expected loss.

### Load balancing

DNS round robin is simple and widely distributed, but has coarse health awareness, caching, and uneven client behavior. Reverse proxies can perform health checks, routing, TLS termination, and connection management, but become a critical layer. Hardware or software load balancers can provide richer policies and high throughput, while adding cost, configuration, and another failure domain.

Ask what happens when a node is slow rather than fully down. A health check that tests only process liveness may keep routing traffic to a node whose database or downstream dependency is unusable. Health checks should be specific enough to remove unhealthy capacity without causing a synchronized storm.

### Clustering

Active-active clusters spread work but require shared or replicated state, consistent routing, and conflict handling. Active-passive clusters simplify ownership but leave standby capacity and failover timing concerns. Neither model eliminates data, network, software, or operator failures.

Define:

- who owns the service identity;
- how ownership is acquired and fenced;
- what state is replicated and at what point;
- how clients reconnect;
- how queued or in-flight work is recovered;
- how split-brain is prevented and detected.

## Reference Table

| Choice | Strength | Main concern |
|---|---|---|
| DNS round robin | Simple distribution | Caching and weak failure reaction |
| Reverse proxy | Health checks and routing policy | Proxy capacity and failure domain |
| Hardware/software LB | Rich policy and throughput | Cost, configuration, and dependency |
| Active-active | Uses multiple nodes | State consistency and coordination |
| Active-passive | Clear ownership | Standby capacity and failover time |

## Worked Example

An application promises 99.9% monthly availability for checkout. It uses two active nodes, but both share one database and one payment provider. Adding a second node does not remove the database or provider failure modes. The design should document those dependencies, define a pending-payment mode, measure failover and reconnection, and determine whether the target requires a second database path or a business-level degraded mode.

## Key Takeaways

1. Availability starts with a business-defined service requirement.
2. Redundancy only helps the failure modes it actually removes.
3. Health checks must reflect useful service, not just process existence.
4. State, ownership, reconnection, and split-brain behavior are part of clustering.

## Connects To

- Chapter 11 supplies network identity and route considerations.
- Chapter 14 covers operational configuration, startup, and shutdown.
- Chapter 18 connects availability design to safe releases and long-term adaptation.

