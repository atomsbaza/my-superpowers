# Chapter 10: Batch Processing

## Core Idea

Batch processing reads a bounded historical input, transforms it, and writes derived output. Its strengths are repeatability, high throughput, and the ability to rebuild state from the source of truth. Good batch pipelines make dataflow explicit, use joins suited to partitioning, tolerate task failures, and treat output as derived data rather than mutable shared state.

## Frameworks Introduced

- **Unix philosophy**: Small programs with one purpose compose through a uniform stream interface.
  - When to use: exploratory analysis, simple transformations, and pipelines whose data fits the tools’ operational limits.
  - How: make each stage composable, keep wiring separate from logic, and preserve transparent intermediate output.
- **MapReduce dataflow**: Mappers emit key/value pairs; the framework partitions and sorts by key; reducers process each key’s grouped values.
  - When to use: large immutable inputs and transformations that can be expressed as parallel map, shuffle, and reduce stages.
  - How: choose the key to bring related records together, design for skew, and make tasks re-runnable after failure.
- **Reduce-side joins and grouping**: Partition both inputs by join key, sort/group them, then combine records at the reducer.
  - When to use: both datasets are large or neither fits in memory on every worker.
  - How: use the same partitioning key, control key skew, and stream grouped records rather than building an unbounded in-memory map.
- **Map-side joins**: Join before the shuffle when one input is broadcastable, both inputs share partitioning, or both are sorted compatibly.
  - When to use: reduce network/sort cost and latency.
  - How: broadcast a small table, co-partition inputs, or merge sorted streams.
- **Derived-data output**: Write indexes, materialized views, or key-value datasets as replaceable results of a deterministic computation.
  - When to use: search indexes, recommendations, analytics tables, or any view that can be rebuilt from the system of record.
  - How: version/atomically publish output, retain provenance, and keep destructive side effects out of the middle of a retryable job.
- **Materialized intermediate state**: Persist boundaries between stages for fault tolerance and reuse; dataflow engines may fuse stages when safe.

## Key Concepts

- **Batch process**: Offline computation over a bounded input.
- **Mapper**: Function that turns input records into key/value pairs.
- **Reducer**: Function that consumes all values for a key.
- **Shuffle**: Partitioning, sorting, and transferring mapper output to reducers.
- **Data skew**: Uneven key distribution that overloads one task.
- **Reduce-side join**: Join after repartitioning both inputs by key.
- **Map-side join**: Join before shuffle using broadcast/partition/order assumptions.
- **Materialized view**: Stored result of a query/transformation.
- **Derived data**: Data computed from other data and replaceable by recomputation.
- **Fault tolerance**: Re-running failed tasks/stages without corrupting final output.

## Mental Models

- Treat batch output as a cache/index of the input, not as a second authoritative copy.
- The shuffle is the price of grouping related records; choose keys and join strategy to minimize it.
- Deterministic, side-effect-free stages are easy to retry; external writes require idempotence or an atomic publication boundary.
- A pipeline’s intermediate files are both a performance optimization and a recovery checkpoint.

## Anti-patterns

- **Using a single custom program for every transformation**: It hides reusable stages and makes recovery/parallelism harder.
- **Joining everything with a reduce-side shuffle**: It creates unnecessary network and sort work when a broadcast or co-partitioned join is possible.
- **Ignoring skew**: One popular key can serialize the job even when average partitions look balanced.
- **Mutating the source database from retryable tasks**: Task retries can duplicate side effects or leave partial output.

## Code Examples

```sh
# Count requests by URL with composable Unix stages.
cat access.log \
  | awk '{print $7}' \
  | sort \
  | uniq -c \
  | sort -nr
```

- **What it demonstrates**: Each stage has a narrow contract; sorting brings equal keys together so `uniq -c` needs little state.

```text
map(record): emit(record.join_key, record.payload)
shuffle: partition_and_sort_by_key()
reduce(key, values): emit(key, combine(values))
```

- **What it demonstrates**: MapReduce’s grouping boundary makes parallel aggregation possible and makes the partition key a central design choice.

## Reference Tables

| Join | Preconditions | Network/sort cost | Use when |
|---|---|---|---|
| Reduce-side | neither input is local/broadcastable | high shuffle | both inputs are large/unmatched |
| Broadcast hash | one input fits in worker memory | low for small side | small dimension + large fact |
| Partitioned hash | both can be co-partitioned | moderate | repeated joins with stable keys |
| Map-side merge | both inputs sorted/partitioned | low | ordered, compatible inputs |

## Worked Example

To build a search index from web crawl records, map each document to `(term, document_id)` pairs, shuffle by term, reduce each term to a postings list, and publish a new index generation. A failed reducer can be rerun because it reads immutable input and writes an isolated output file. The final index is swapped into service only after all partitions succeed. If a small document-metadata table is needed, broadcast it to mappers rather than shuffling the entire table through reducers.

## Key Takeaways

1. Choose map/reduce keys to express the data that must meet at one task.
2. Prefer map-side joins when size/partition/order make them safe.
3. Design for skew, retries, and partial task failure from the beginning.
4. Make derived outputs versioned and replaceable so recomputation is safe.
5. Keep the system of record separate from derived indexes and analytical views.

## Connects To

- **Chapter 3**: Batch jobs build indexes, column stores, and materialized views.
- **Chapter 6**: Partitioning and locality determine shuffle and join cost.
- **Chapter 11–12**: Stream processing provides incremental versions of derived-data pipelines.

