# Chapter 1: Reliable, Scalable, and Maintainable Applications

## Core Idea

Treat databases, caches, indexes, queues, and batch/stream processors as components of one data system. Judge the resulting system against three independent goals: it must continue to do the right thing under faults (reliability), have an explicit response to growth (scalability), and remain workable as people and requirements change (maintainability).

## Frameworks Introduced

- **Reliability as fault tolerance**: A fault is one component deviating from its specification; a failure is the system no longer providing its required service. Design boundaries that prevent expected faults from becoming failures.
  - When to use: whenever you define an SLO, failure mode, backup, failover, or recovery plan.
  - How: enumerate hardware, software, dependency, and human faults; decide which are prevented, detected, contained, recovered from, and verified.
- **Scalability as a load-and-response question**: “Scalable” is not a system property in the abstract. State the load parameters, then describe how performance changes as each parameter grows.
  - When to use: capacity planning or comparing architectures.
  - How: measure requests/second, read/write mix, active users, data volume, or fan-out; model throughput, response-time distribution, and bottlenecks; add resources where the model says they help.
- **Maintainability = operability + simplicity + evolvability**: Make routine operation easy, keep accidental complexity low, and make future changes safe.
  - When to use: reviewing an architecture that works today but is expensive to operate or modify.
  - How: expose observability and automation to operators, choose abstractions that reduce surprises, and isolate change behind stable interfaces.
- **Percentiles over averages**: The median describes a typical request; p95/p99 describe the tail that users and upstream services experience. Tail latency compounds when one request fans out to many services.
  - When to use: latency SLOs, capacity tests, and fan-out architectures.
  - How: record a latency histogram, report p50/p95/p99 over a stated window, and investigate long-tail causes instead of optimizing only the mean.

## Key Concepts

- **Data-intensive application**: An application whose hard limits are data volume, data complexity, or change rate rather than raw CPU.
- **Fault**: A component-level deviation from its specification.
- **Failure**: A system-level loss of required service.
- **Resilience**: The ability to tolerate selected faults without failing.
- **Load parameter**: A number that characterizes demand, such as QPS, active users, or read/write ratio.
- **Throughput**: The amount of work completed per unit time.
- **Response time**: The elapsed time observed by a client, including queueing and network delay.
- **Percentile**: A point in a latency distribution below which a given fraction of observations fall.
- **Operability**: Making routine operations, diagnosis, and recovery straightforward.
- **Evolvability**: Making change possible without destabilizing the system.

## Mental Models

- Think of a composite service as a new data system: its API must state the guarantees created by combining the underlying tools.
- Use independent, ideally uncorrelated failure domains when redundancy is meant to protect against common-cause failure.
- Use deliberate fault injection to exercise recovery paths; untested error handling is not a reliability mechanism.
- Use “what grows?” as the first scalability question. Data volume, traffic, fan-out, and complexity may need different solutions.

## Anti-patterns

- **Calling a system scalable without naming the load**: It hides the growth model and makes architecture claims unfalsifiable.
- **Optimizing average latency**: A low mean can conceal a disastrous tail, especially when requests fan out.
- **Relying only on hardware redundancy**: Software bugs, configuration errors, and correlated dependency failures can take every replica down.
- **Making operations depend on heroics**: Manual recovery and opaque behavior turn routine faults into outages.

## Code Examples

```sql
-- A read-heavy, fan-out-on-read timeline query.
SELECT tweets.*
FROM tweets
JOIN follows ON follows.followee_id = tweets.author_id
WHERE follows.follower_id = :viewer_id
ORDER BY tweets.created_at DESC
LIMIT 30;
```

- **What it demonstrates**: The query is simple, but its cost grows with the number of followed accounts and their recent tweets; the access pattern, not the SQL syntax, determines scalability.

## Reference Tables

| Concern | Ask | Useful evidence |
|---|---|---|
| Reliability | What happens when a component is wrong or absent? | fault injection, recovery drills, error budgets |
| Scalability | What happens when a named load parameter grows? | throughput curves, queue depth, p99 latency |
| Maintainability | Can operators and future developers change it safely? | runbooks, observability, deployment and rollback time |

## Worked Example

For a social timeline, **fan-out on read** stores each tweet once and joins recent tweets from followed accounts when a reader opens the timeline. It is efficient for a user who follows few people, but a celebrity’s large follower base creates expensive reads for every follower. **Fan-out on write** precomputes a per-user home timeline when a tweet is posted; reads become cheap, but one celebrity post creates a huge write burst. A practical design uses write fan-out for ordinary accounts, a special path for high-fan-out accounts, and explicit measurements for read/write load, cache hit rate, and tail latency. The lesson is to choose a load model, not a slogan.

## Key Takeaways

1. Separate faults from failures and design containment/recovery around the faults you actually intend to tolerate.
2. Describe load and performance with distributions and growth curves, not adjectives.
3. Reliability, scalability, and maintainability are related but distinct design objectives.
4. Treat operability, simplicity, and evolvability as first-class system features.
5. When combining specialized tools, the application must provide the missing consistency and correctness guarantees.

## Connects To

- **Chapter 3**: Storage structures make different workload/performance trade-offs.
- **Chapter 5**: Replication turns component faults into recoverable node failures.
- **Chapter 10–11**: Batch and stream systems provide different ways to handle growing derived data.

