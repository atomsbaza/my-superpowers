# Chapter 6: Partitioning

## Core Idea

Partitioning (sharding) splits a dataset across nodes so storage and query load can scale horizontally. A good scheme balances load, preserves useful locality, handles hot keys, supports secondary indexes, and can be rebalanced without making the whole system unavailable.

## Frameworks Introduced

- **Range partitioning**: Assign contiguous key ranges to partitions.
  - When to use: range scans and ordered locality matter.
  - How: choose boundaries, split hot/large ranges, and account for skewed or time-ordered keys.
- **Hash partitioning**: Hash a key and assign hash ranges/buckets to partitions.
  - When to use: point lookups and even distribution matter more than range scans.
  - How: hash the partition key, use a stable partition map, and add salting or subpartitions for hot keys.
- **Secondary indexes by document versus by term**: Local indexes live with the primary record; global/term-partitioned indexes route each indexed value to the nodes that contain matches.
  - When to use: choose between write fan-out and query fan-out.
  - How: local index queries many partitions but updates one; global index makes reads targeted but must coordinate index updates and rebalancing.
- **Rebalancing with fixed partitions**: Create more logical partitions than nodes, move whole partitions between nodes, and update routing metadata.
  - When to use: node membership changes are expected.
  - How: transfer ownership in controlled steps, throttle movement, and preserve availability/ordering during handoff.
- **Request routing**: Any node, a routing tier, or an aware client can map a key to its partition.
  - When to use: define where partition-map knowledge lives and how it changes.
  - How: use a stable source of truth/coordination service, version routing metadata, and handle stale maps safely.

## Key Concepts

- **Partition/shard**: A subset of records owned by one node or replica group.
- **Partition key**: Field used to assign a record to a partition.
- **Range partitioning**: Assignment based on ordered key intervals.
- **Hash partitioning**: Assignment based on a key hash.
- **Hot spot**: A partition receiving disproportionate traffic or data.
- **Consistent hashing**: Hash-space ownership scheme that limits movement when nodes change.
- **Secondary index**: An index on a field other than the primary partition key.
- **Local index**: Secondary index stored with each primary partition.
- **Global index**: Secondary index partitioned independently, often by indexed term.
- **Rebalancing**: Moving partition ownership as nodes or load change.

## Mental Models

- Partitioning is a routing problem plus a load-distribution problem; solving only one is insufficient.
- Pick the partition key by the dominant access path, then test worst-case skew rather than average distribution.
- Keep many logical partitions so ownership can move incrementally; do not bind data permanently to physical nodes.
- Every global query has a fan-out/fan-in cost; every global index has a write and coordination cost.

## Anti-patterns

- **`hash(key) mod N` as a rebalancing strategy**: Changing `N` remaps almost every key and creates a massive migration.
- **Time-only range keys**: New writes concentrate on the newest partition and create a hot spot.
- **Ignoring secondary-index semantics**: A query that looks local may become a scatter/gather operation.
- **Automatic rebalancing without limits**: Moving data too aggressively can consume the resources needed to serve traffic.

## Code Examples

```text
partition_for(key, partition_count):
  bucket = hash(key) % partition_count
  return routing_table[bucket]

# For a hot time-ordered key, spread writes deliberately:
physical_key = (account_id, hash(event_id) % 16, event_time)
```

- **What it demonstrates**: Hashing spreads point traffic, while an explicit bucket/salt can prevent one logical key from becoming one hot partition; reads must then merge buckets.

```sql
-- Global/term index query: route to partitions containing the term.
SELECT document_id FROM term_index
WHERE term = :term;
```

- **What it demonstrates**: A term-partitioned index can avoid querying every document partition, at the cost of maintaining a separately partitioned structure.

## Reference Tables

| Choice | Good locality | Main query cost | Typical risk |
|---|---|---|---|
| Key range | ordered/range scans | hot ranges, boundary management | sequential keys hotspot |
| Key hash | point lookups | range scans fan out | related data loses locality |
| Local secondary index | primary-key writes | query many partitions | scatter/gather latency |
| Global secondary index | targeted term reads | index update fan-out | consistency/rebalancing complexity |

## Worked Example

A metrics service keys data by `(tenant_id, timestamp)`. Range partitioning makes time-window queries efficient but overloads the newest range for a large tenant. Pure hashing balances writes but makes a time-window query touch many partitions. A hybrid design hashes a bounded bucket within each tenant and retains timestamp order inside each bucket. Queries fan out to the tenant’s buckets and merge results, while writes distribute across them. The trade-off is explicit: more read fan-out buys protection from hot spots.

## Key Takeaways

1. Choose partition keys from measured access patterns and worst-case skew.
2. Range partitioning preserves locality; hash partitioning usually balances point load.
3. Secondary-index design determines whether reads or writes fan out.
4. Fixed logical partitions make rebalancing incremental and predictable.
5. Routing metadata, handoff, throttling, and failure behavior are part of the partitioning design.

## Connects To

- **Chapter 3**: Per-partition storage engines and indexes determine local performance.
- **Chapter 5**: Each partition is commonly replicated as a group.
- **Chapter 7–9**: Cross-partition transactions, ordering, and consensus are expensive coordination boundaries.

