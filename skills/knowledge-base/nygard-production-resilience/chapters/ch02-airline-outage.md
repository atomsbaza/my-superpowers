# Chapter 2: Case Study — The Exception That Grounded an Airline

## Core Idea

A routine database failover exposed a small resource-cleanup bug that exhausted a connection pool and blocked every caller. The lesson is not “never use failover”; it is that failures at one boundary must not propagate unchecked through shared resources.

## Frameworks Introduced

- **Restore service before investigation**: During an incident, collect automated evidence only when it does not prolong recovery.
  - When to use: Any active outage.
  - How: Restore service, capture thread dumps/logs/DB snapshots with prepared scripts, then investigate the preserved evidence.
- **Post-mortem as evidence analysis**: Separate observations from hypotheses and reconstruct the causal chain from logs, dumps, and source.
  - When to use: After service is restored.
  - How: Establish symptoms, common dependencies, resource states, and the smallest mechanism that explains the outage.

## Key Concepts

- **Virtual-IP failover**: A database address moved to another host while existing TCP connections remained unusable.
- **Connection pool exhaustion**: Leaked connections consumed the finite pool until new callers blocked.
- **Cleanup-path failure**: A secondary exception during statement cleanup prevented connection cleanup.
- **Common dependency**: A service shared by otherwise separate applications can become a shared failure domain.

## Mental Models

- A resource pool is a fuse: when it is exhausted, every caller may stop even if the caller’s own code is healthy.
- “The failover caused it” is a hypothesis; the causal mechanism must be proved.
- Every exceptional cleanup path deserves the same design attention as the success path.

## Anti-patterns

- **Trusting normal driver behavior**: Assuming a rarely thrown cleanup exception cannot happen in production.
- **Monitoring a shallow health endpoint**: A status page can remain healthy while all business threads are blocked.
- **Investigating before stabilizing**: Improvised diagnostics can extend the outage.

## Code Examples

```java
try {
    connection = pool.getConnection();
    statement = connection.createStatement();
    return execute(statement);
} finally {
    closeQuietly(statement);
    closeQuietly(connection); // cleanup must survive a failed close above
}
```

The exact language is incidental; the invariant is that every acquired resource is released even when another cleanup operation fails.

## Reference Table

| Evidence | What it can establish |
|---|---|
| Thread dump | Which pools/threads are blocked and where |
| Application log | Timing and error sequence |
| Dependency health check | Only the behavior actually exercised by that check |
| Source/decompiled code | Whether cleanup and error paths leak resources |

## Worked Example

After the failover, stale connections were allowed to create statements, but network I/O failed. Statement cleanup then threw, the connection was not returned, and repeated requests consumed the pool. The fix is defensive cleanup plus a pool policy that detects stale connections and bounds checkout waits; the broader fix is to contain dependency failure with timeouts and circuit breaking.

## Key Takeaways

1. A one-line exception can become a system-wide outage through a shared pool.
2. Capture operational evidence automatically, but prioritize recovery.
3. Treat dependency failover and cleanup behavior as production paths, not rare anomalies.

## Connects To

- **Ch 4**: Blocked Threads and Cascading Failures generalize the incident.
- **Ch 5**: Timeouts, Circuit Breaker, and Bulkheads contain the same class of failure.
- **Ch 17**: Real health checks need business and resource visibility.
