# Production Resilience Cheatsheet

## Review questions

| If you see… | Ask… | Prefer… |
|---|---|---|
| A remote call with no deadline | “What happens when it never returns?” | Timeout + bounded cleanup |
| Retries around a failing dependency | “Will retries amplify the failure?” | Circuit Breaker, backoff, retry budget |
| One shared pool for unrelated features | “Can one workload consume all capacity?” | Bulkheads and per-workload limits |
| A queue with no bound or lag alert | “What happens when consumers stop?” | Bounded queue, backpressure, dead-letter path |
| An SLA for “the system” | “Which feature, dependency, and time window?” | Feature-level availability and exclusions |
| A large result set or session object | “What is the worst-case size?” | Limits, pagination, compact state |
| A load test with only client metrics | “What happened inside the system?” | Resource and business telemetry during load |
| A deployment requiring all nodes offline | “Can old and new versions coexist?” | Expand → rollout → contract |
| A dashboard that is always green | “Are its thresholds and signals truthful?” | Actionable steady-state indicators |

## Failure-containment sequence

1. Identify the boundary: dependency, resource pool, queue, node, or feature.
2. Bound waiting and resource consumption.
3. Isolate the workload from unrelated work.
4. Detect failure and stop sending harmful traffic.
5. Preserve a useful degraded function or fail clearly.
6. Expose the state to operators and business owners.
7. Test the failure and recovery path under realistic load.

## Availability decision

`cost of prevention` < `expected cost of downtime` → invest in more availability.

Define: feature scope, dependency exclusions, measurement window, recovery objective, tolerated data loss, and the cost of missed transactions. “Five nines” is not a requirement until these are explicit.

## Capacity rules

- Measure useful throughput and latency, not only CPU percentage.
- Find the current constraint before adding hardware.
- Size pools against the downstream system, not just the caller’s thread count.
- Bound memory, result sets, sessions, queues, and cache growth.
- Test launch-day impulses, repeated reloads, and failure-induced redistribution.

## Release sequence

**Expand**: make the system accept both versions/configurations.  
**Roll out**: shift traffic gradually while watching health and business signals.  
**Contract**: remove compatibility only after rollback is no longer required.
