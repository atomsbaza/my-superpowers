# Chapter 12: The Future of Data Systems

## Core Idea

Modern applications are dataflows: one system of record feeds caches, indexes, warehouses, recommendations, clients, and other derived views. The most robust architecture makes derivations explicit, supports replay and verification, uses coordination only where correctness requires it, and treats privacy, accountability, and integrity as system properties rather than afterthoughts.

## Frameworks Introduced

- **Derived data and dataflow**: Specialized stores can coexist when each is a materialized view of durable input and the flow between them is observable.
  - When to use: no single database efficiently serves operational, search, analytical, and client/offline workloads.
  - How: identify systems of record, derivation functions, dependencies, freshness, rebuild paths, and publication boundaries.
- **Batch/stream unification**: A batch computation over all history and a stream computation over incremental changes should produce compatible state.
  - When to use: support both initial construction/reprocessing and low-latency updates.
  - How: define event schemas and deterministic derivations; use snapshots/checkpoints and replay rather than permanently separate business logic.
- **Unbundled databases**: Separate storage, indexing, stream, and query components can be composed behind a dataflow API.
  - When to use: specialized workloads need different technologies.
  - How: make writes/events the integration boundary, keep derived views replaceable, and observe freshness/integrity instead of hiding distributed complexity.
- **Application code as a derivation function**: Current state is a function of inputs plus code/version.
  - When to use: evolve business logic or rebuild a view after a bug.
  - How: retain enough source history, version the derivation, replay into a new output, compare/validate, and switch publication atomically.
- **End-to-end argument for correctness**: A lower-level guarantee does not remove the need for validation at the boundary where the user-visible invariant is known.
  - When to use: exactly-once claims, duplicate suppression, checksums, authorization, and cross-system workflows.
  - How: carry operation IDs, verify final effects, make retries safe, and audit the result rather than trusting every intermediate promise.
- **Correctness dimensions: integrity and timeliness**: Data can be complete/correct but late, or timely but incomplete/wrong.
  - When to use: define SLOs for data products and derived views.
  - How: measure freshness, completeness, correctness, provenance, and correction behavior separately.
- **Trust, but verify**: Systems need auditability, monitoring, independent checks, and the ability to explain how a result was produced.
  - When to use: high-impact decisions, regulatory data, analytics, and automated actions.
  - How: preserve provenance, sample/reconcile outputs, expose assumptions, and design feedback loops that do not amplify bias or surveillance harm.

## Key Concepts

- **System of record**: Authoritative source from which other data can be derived.
- **Derived data**: Replaceable output computed from other data.
- **Dataflow**: Movement and transformation of data between components.
- **Materialized view**: Persisted result maintained from source changes.
- **Unbundled database**: Composition of storage/query/index components via dataflow.
- **Freshness**: How current a derived view is relative to its source.
- **Integrity**: Whether data satisfies its constraints and is complete/correct.
- **End-to-end argument**: Put guarantees at the layer that can observe the final property.
- **Idempotency key**: Identifier that collapses retries into one logical operation.
- **Provenance**: Evidence of source, transformations, versions, and timing behind a result.
- **Feedback loop**: A prediction/action changes future data and therefore future predictions.

## Mental Models

- Treat every cache, index, and client replica as a materialized view with a rebuild story.
- Separate “source of truth” from “source of convenience”; a derived store may be disposable even when it is operationally critical.
- Use coordination only for constraints that truly require a shared decision; use asynchronous derivation for everything else.
- If a system cannot explain, verify, or correct a high-impact output, it is not maintainable enough for that use.

## Anti-patterns

- **Dual writes with no durable ordering/idempotence**: The database and index can diverge after a crash between writes.
- **Treating a cache/index as authoritative**: Rebuilds become impossible and corruption propagates.
- **Claiming exactly-once from at-least-once components**: Physical duplicate delivery is normal; only the final effect can be made idempotent.
- **Optimizing freshness while ignoring integrity/privacy**: Fast, wrong, or harmful data is still a system failure.
- **Hiding all coordination behind a “unified” interface**: The cost and failure semantics remain; observability gets worse.

## Code Examples

```text
derive(source_event, current_view):
  return apply_business_rules(current_view, source_event)

rebuild(source_log, code_version="v2"):
  view = empty_view()
  for event in source_log:
    view = derive(event, view)
  publish_atomically(view, version=code_version)
```

- **What it demonstrates**: Versioned deterministic derivation enables reprocessing after code changes or repair without mutating the system of record.

```text
operation_id = client_id + sequence
if seen(operation_id): return recorded_result(operation_id)
result = perform_effect(operation_id)
record_result(operation_id, result)
return result
```

- **What it demonstrates**: End-to-end duplicate suppression must surround the user-visible effect, not merely rely on transport delivery.

## Reference Tables

| Property | Question | Example signal |
|---|---|---|
| Correctness/integrity | Is the result valid and complete? | invariant checks, reconciliation, audit |
| Freshness/timeliness | How late is it? | source-to-view lag, watermark age |
| Availability | Can the consumer obtain a result? | success rate, fallback rate |
| Provenance | Can we explain how it was made? | source IDs, code/schema version |
| Privacy/impact | Is collection/use justified and safe? | retention, consent, access audit |

## Worked Example

An order system writes an authoritative event stream, then derives a search index, customer timeline, warehouse table, and offline client state. Each consumer tracks offsets and reports freshness. A bug in the indexing code is fixed by replaying the event stream into a new index version, comparing counts/checksums and sample queries, then switching the alias. The order stream remains authoritative; the index is replaceable. A duplicate client request is collapsed with an operation ID at the order boundary, while downstream consumers remain at-least-once and idempotent. This architecture makes repair, verification, and evolution normal operations.

## Key Takeaways

1. Make systems of record, derivations, dependencies, freshness, and rebuild paths explicit.
2. Unbundle specialized data systems through durable dataflow rather than unsafe ad hoc dual writes.
3. Design every derived view for replay, verification, and atomic publication.
4. Put duplicate suppression and final invariant checks at the end-to-end boundary.
5. Measure integrity, timeliness, provenance, privacy, and predictive feedback effects—not just throughput.

## Connects To

- **All chapters**: The future-of-data-systems view composes their models into explicit dataflows and correctness boundaries.
- **Chapter 10–11**: Batch rebuilds and stream updates are complementary derivation paths.
- **Chapter 9**: Uniqueness and cross-partition constraints are where consensus/coordination remain necessary.

