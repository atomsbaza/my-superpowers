# Glossary

**Availability** — The proportion of time a defined feature or function can successfully serve users; define its scope and exclusions before choosing a target. (Ch 13)

**Bulkhead** — An isolation boundary that limits the resources, traffic, or failure impact of one workload so it cannot sink the whole system. (Ch 5)

**Capacity** — The useful work a system can perform under stated conditions and constraints, not merely the size of its hardware. (Ch 8)

**Cascading failure** — A failure that propagates across a dependency or layer boundary, often through exhausted pools, retries, or blocked threads. (Ch 4)

**Circuit Breaker** — A stateful guard that stops calls to a failing dependency, returns a controlled failure or fallback, and periodically tests recovery. (Ch 5)

**Crack** — A local defect or stress point that can remain contained or propagate into a larger outage. (Ch 3–5)

**Decoupling middleware** — A queue or broker that separates producers and consumers in time, rate, and availability. (Ch 5)

**Fail fast** — Reject work immediately when it cannot complete within a useful time or resource budget. (Ch 5)

**Handshaking** — Explicitly agreeing on readiness, identity, protocol, or capabilities before starting expensive interaction. (Ch 5, 11)

**Horizontal scaling** — Increasing capacity by adding similar servers or workers. (Ch 4, 8, 13)

**SLA inversion** — Promising a service level that is mathematically impossible because dependencies have weaker guarantees. (Ch 4)

**Steady state** — The expected operating condition and measurable baseline used to detect abnormal behavior. (Ch 5, 17)

**Timeout** — A bound on how long an operation may wait before returning control and allowing recovery or fallback. (Ch 5)

**Transparency** — The ability to understand historical trends, forecasts, present status, and instantaneous behavior of a running system. (Ch 17)

**Virtual IP** — A service address that can move between nodes or front multiple physical services, hiding failover details from clients. (Ch 11, 13)
