# Chapter 3: Storage and Retrieval

## Core Idea

Storage engines are workload-specific data structures. Understand how writes, reads, range scans, compaction, and recovery work before choosing an engine; the difference between an append-oriented LSM tree and an in-place B-tree can dominate latency, write amplification, and operational behavior.

## Frameworks Introduced

- **Hash index over an append-only log**: Keep the latest byte offset for each key in memory while appending writes sequentially.
  - When to use: simple key-value workloads with enough memory for the index and acceptable compaction/recovery requirements.
  - How: append records, update the key→offset map, periodically merge segments, discard obsolete values, and make recovery/WAL behavior explicit.
- **SSTable + LSM-tree**: Buffer writes in memory, flush sorted immutable files, and compact overlapping files in the background.
  - When to use: write-heavy workloads and sequential I/O where high write throughput matters.
  - How: maintain a memtable, flush to an SSTable, merge levels/segments, use sparse indexes and filters, and bound read amplification with compaction.
- **B-tree**: Keep sorted key ranges in fixed-size pages and update pages in place, splitting full pages as needed.
  - When to use: predictable point/range reads, mature transactional behavior, and workloads where read amplification or compaction pauses are costly.
  - How: traverse from root to leaf, update the leaf, split/rebalance pages, and protect partial writes with a WAL or copy-on-write mechanism.
- **OLTP versus OLAP**: Transaction processing needs many small, selective reads/writes; analytics needs scans and aggregates over large volumes.
  - When to use: deciding whether to serve dashboards from the primary application database.
  - How: separate workload contention with a warehouse/derived store when needed; choose row-oriented or column-oriented storage by access pattern.
- **Column-oriented analytics**: Store each column separately, compress it, and sort/encode to scan only the columns and values an aggregate needs.
  - When to use: large analytical scans with a small projection and repeated aggregations.
  - How: select useful sort order, exploit run-length/bitmap/dictionary compression, and account for updates being more expensive than append/batch writes.

## Key Concepts

- **Write-ahead log (WAL)**: A durable record of intended changes written before in-place data is modified.
- **Memtable**: An in-memory ordered structure receiving writes in an LSM engine.
- **SSTable**: An immutable, sorted string table on disk.
- **Compaction**: Merging sorted files and removing overwritten/deleted records.
- **Write amplification**: Extra bytes written because data is rewritten during maintenance.
- **Read amplification**: Multiple structures/files consulted to answer one read.
- **Bloom/filter index**: A cheap probabilistic test used to skip files that cannot contain a key.
- **B-tree page**: A fixed-size block containing sorted keys and child pointers/values.
- **OLTP**: Online transaction processing with small, concurrent operational requests.
- **OLAP**: Online analytical processing with large scans and aggregations.

## Mental Models

- Think of an index as an additional data structure whose maintenance cost must be paid on writes.
- Use sequential append plus compaction when write throughput is more important than stable write amplification.
- Use a B-tree when range locality, in-place updates, and predictable reads matter more than maximizing sequential writes.
- Treat a warehouse as a different workload environment, not merely a larger OLTP database.

## Anti-patterns

- **Choosing an engine from its benchmark headline**: Workload shape, cache size, compaction, and durability settings determine the result.
- **Ignoring compaction**: LSM read latency, space use, and write pauses depend on background maintenance.
- **Putting every query index on the primary store**: Each index increases write cost and can create contention.
- **Running analytics directly on an OLTP workload**: Long scans compete with latency-sensitive transactions.

## Code Examples

```text
put(key, value):
  append_to_log(key, value)
  memtable[key] = value
  if memtable.bytes > flush_threshold:
    enqueue_flush(sorted(memtable))  # immutable SSTable
    memtable = new_memtable()

get(key):
  check memtable, then newest SSTables first
  use sparse indexes/filters to skip impossible files
  return the newest visible value
```

- **What it demonstrates**: An LSM tree separates the fast write path from immutable sorted files; compaction later trades background I/O for bounded read and space amplification.

## Reference Tables

| Structure | Best at | Costs to watch |
|---|---|---|
| Append-only hash index | point reads/writes | range scans, recovery, segment compaction |
| LSM tree | high write throughput, sequential I/O | compaction, read/space amplification |
| B-tree | point and range queries, transactions | random writes, page splits, write amplification |
| Column store | scans/aggregates over selected columns | updates and point lookups |

## Worked Example

Suppose an event service performs 90% point writes, occasional key lookups, and nightly range scans. An LSM engine with a memtable, immutable SSTables, compaction, and tombstones fits the write path; a Bloom filter and sparse index reduce reads. If the service instead performs frequent range reads and updates records in place, a B-tree may be simpler and more predictable. For the nightly scan, copy or derive data into a column-oriented warehouse so compression and vectorized scans do not contend with the operational workload. The right answer is often multiple stores connected by derived data, not one universal engine.

## Key Takeaways

1. Match storage structures to point/range access, write rate, update pattern, and durability needs.
2. LSM trees trade background compaction for high sequential write throughput.
3. B-trees trade random page updates for strong range locality and mature transactional behavior.
4. Indexes, compression, and materialized views are performance structures with maintenance costs.
5. Separate OLTP and OLAP when their access patterns interfere.

## Connects To

- **Chapter 2**: Data model and query shape determine the index structures worth maintaining.
- **Chapter 4**: Stored bytes need an encoding/evolution contract.
- **Chapter 10–11**: Batch and stream processors are common ways to build derived indexes and analytical stores.

