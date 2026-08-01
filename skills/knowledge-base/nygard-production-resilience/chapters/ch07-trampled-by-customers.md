# Chapter 7 — Case Study: Trampled by Your Own Customers

## Core Idea

A system can pass functional testing and still fail catastrophically when real customers arrive. Production capacity is shaped by traffic shape, data volume, concurrency, session behavior, dependency latency, and operational conditions—not by whether a small test suite produces correct answers.

The case study follows a retail launch that looked successful in QA but collapsed under a major public event. The important lesson is not a particular product failure. It is the testing gap between a controlled environment and the coupled, stateful, impatient system that exists in production.

## Frameworks Introduced

- **Target matching:** load tests must aim at the same behavior, traffic mix, data shape, and operational limits that matter in production.
- **Load as a system property:** throughput is limited by every resource and dependency in the request path, not just the web tier.
- **Temporary-fix debt:** emergency capacity changes can conceal design flaws and become permanent without a follow-up.
- **Failure under popularity:** success can create the load that causes failure; the system is most vulnerable precisely when demand is highest.

## Key Concepts

### Testing the right target

Functional tests answer whether a feature behaves correctly for selected examples. Load tests answer whether the complete system maintains useful service under a specified workload. They need realistic:

- request mix and arrival pattern;
- user concurrency and session behavior;
- record counts, index sizes, cache warmth, and object sizes;
- third-party and internal dependency latency;
- deployment topology, configuration, and resource limits;
- success criteria such as latency percentiles, error rates, and recovery time.

A test that sends one simple request repeatedly may measure a fast path that few real users take. A test that generates only average traffic misses burst behavior. A test with an empty database misses query plans and memory pressure caused by historical data.

### The launch amplification loop

When response time increases, users tend to retry, reload, open additional pages, or abandon and return. Applications may also create more work when a request is slow: threads remain occupied, sessions remain resident, and queued work consumes memory. The resulting loop is:

```text
traffic spike -> queue growth -> slower responses -> retries and timeouts
      ^                                               |
      +--------------- more effective demand --------+
```

Protective measures must break this loop by bounding work, failing fast, and communicating overload to callers.

### Temporary capacity is not a design

Adding servers, increasing pool sizes, or disabling an expensive feature can restore service. These are valid incident actions, but they do not prove that the architecture is sound. A temporary change should have an owner, an expiration or review date, and a measured hypothesis: what bottleneck was relieved, and what new bottleneck may now be exposed?

## Anti-patterns

- **QA optimism:** treating a green functional suite as evidence of production readiness.
- **Synthetic simplicity:** using unrealistic data, request mixes, or user behavior.
- **Average-load thinking:** planning for the mean while ignoring bursts and tail latency.
- **Single-tier tuning:** tuning web servers while ignoring databases, queues, networks, or external services.
- **Permanent emergency settings:** retaining oversized pools or disabled safeguards without understanding their cost.

## Code and Test Examples

A useful load-test result is multidimensional:

```text
scenario: browse -> search -> add-to-cart -> checkout
arrival: 600 users/s, 3x burst over 90 seconds
data: production-shaped catalog and historical orders
pass: p95 < 800 ms, p99 < 2 s, errors < 0.1%, no queue unbounded
observe: CPU, GC, memory, pool wait, DB locks, cache hit rate, dependency latency
```

The pass criteria should include recovery: after the burst ends, queues drain, error rates return to baseline, and no leaked sessions or exhausted pools remain.

## Reference Table

| Question | Weak answer | Production-grade answer |
|---|---|---|
| What is tested? | A page or endpoint | A realistic business flow |
| What data is used? | Small fixtures | Production-shaped volume and distribution |
| What is measured? | Average response time | Percentiles, errors, saturation, and recovery |
| What happens at overload? | More threads and retries | Bounded queues, timeouts, and controlled rejection |
| What follows a temporary fix? | Nothing | A recorded hypothesis and follow-up test |

## Worked Example

Suppose checkout normally uses 20 database connections and QA tests with 10 concurrent users. Production receives 500 users, each holding a session while a payment provider takes 1.5 seconds. Increasing the pool from 20 to 200 may move the queue from the application to the database, where locks and CPU now saturate. A better test models the payment latency, measures pool wait and database saturation, and verifies that checkout times out and releases resources when the provider is unhealthy.

## Key Takeaways

1. Production readiness is a workload-and-recovery claim, not a feature-completeness claim.
2. Test the traffic shape, data shape, dependency behavior, and topology that matter.
3. Include overload and recovery in the acceptance criteria.
4. Record every emergency capacity change as a design signal.

## Connects To

- Chapter 8 defines capacity and its constraints.
- Chapter 9 catalogs capacity antipatterns that often hide in otherwise correct applications.
- Chapter 5 provides timeouts, circuit breakers, bulkheads, and fail-fast behavior for overload containment.

