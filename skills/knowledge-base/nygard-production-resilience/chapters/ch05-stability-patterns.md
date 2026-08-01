# Chapter 5: Stability Patterns

## Core Idea

Stability patterns do not prevent every failure; they prevent a crack from propagating. Apply them based on credible threats, not by counting how many patterns appear in an architecture.

## Frameworks Introduced

- **Use Timeouts**: Bound every operation that can wait, including pool checkout, locks, network calls, and database calls.
- **Circuit Breaker**: Stop calling a failing dependency, return a controlled result, and probe recovery later.
- **Bulkheads**: Partition pools, queues, threads, or traffic so one workload cannot consume all capacity.
- **Steady State**: Define normal behavior and use it as the baseline for detecting trouble.
- **Fail Fast**: Reject work that cannot complete usefully before it consumes more resources.
- **Handshaking**: Establish readiness, identity, version, and capabilities before normal traffic.
- **Test Harness**: Exercise real interactions, load, failure, and recovery behavior.
- **Decoupling Middleware**: Use queues or brokers to separate rate, time, and availability.

## Key Concepts

- **Timeout budget**: The remaining caller deadline passed through nested calls.
- **Open circuit**: A breaker state that prevents normal calls to a dependency.
- **Recovery probe**: Limited test traffic used to determine whether a dependency is healthy again.
- **Bulkhead partition**: A capacity boundary reserved for a workload or dependency.

## Mental Models

- A timeout returns control; a Circuit Breaker prevents repeated damage; a Bulkhead limits the blast radius.
- Fail fast is kinder to the system than slow failure after consuming every resource.
- Recovery is a design path, not an operator improvisation.

## Anti-patterns

- Applying patterns mechanically, hiding failures indefinitely, retrying without limits, or using one global pool for unrelated work.

## Code Examples

```text
call dependency with deadline
if timeout/error rate crosses threshold:
    open breaker
    return fallback or controlled failure
after cool-down:
    permit a small probe
    close only after healthy response
```

## Reference Table

| Pattern | Contains | Does not solve |
|---|---|---|
| Timeout | Indefinite wait | Work already running downstream |
| Circuit Breaker | Repeated calls to a troubled dependency | The dependency’s root bug |
| Bulkhead | Resource and traffic blast radius | Incorrect capacity sizing by itself |
| Fail Fast | Useless work and queue growth | A missing fallback requirement |
| Decoupling Middleware | Synchronous coupling | Eventual-consistency complexity |

## Worked Example

For a payment provider, use a caller deadline, a small payment-client pool, a breaker for repeated timeouts, idempotency keys, and a clear “payment status pending” result when the outcome is unknown. Do not blindly retry a request that may already have charged the customer.

## Key Takeaways

1. Choose patterns from failure modes, not fashion.
2. Pair waiting bounds with resource isolation and observable state.
3. Test failure and recovery paths as first-class behavior.

## Connects To

- **Ch 4**: Each pattern counters one or more stability antipatterns.
- **Ch 17**: Pattern state must be visible to operators.
- **Ch 18**: Decoupling and handshaking make releases safer.
