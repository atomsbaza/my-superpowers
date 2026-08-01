---
name: designing-data-intensive-apps
description: "Knowledge base from \"Designing Data-Intensive Applications\" by Martin Kleppmann. Use when designing reliable, scalable, and maintainable data systems involving storage engines, data models, replication, partitioning, transactions, consistency, batch/stream processing, or derived data."
---

<!-- argument-hint: [topic, framework name, or chapter number] -->

# Designing Data-Intensive Applications
**Author**: Martin Kleppmann | **Pages**: ~613 | **Chapters**: 12 | **Generated**: 2026-08-01

## How to Use This Skill

- **Without arguments** — load the core design rules below.
- **With a topic** — ask about `replication`, `LSM-trees`, `write skew`, `event time`, or another indexed term; read the relevant chapter.
- **With a chapter** — ask for `ch05` or `Chapter 11` to load that chapter’s frameworks, examples, and tables.
- **Browse** — ask “what chapters do you have?” to see the full index.

When a question reaches beyond the core rules, load the linked chapter file instead of treating this compact file as the whole book.

---

## Core Frameworks & Mental Models

### 1. Design the data system, not just the database

Compose databases, caches, search indexes, queues, batch jobs, and stream processors behind an API. The composition is itself a data system, so state its consistency, freshness, recovery, and security guarantees explicitly.

### 2. Separate reliability, scalability, and maintainability

- **Reliability**: Use fault tolerance so selected faults do not become user-visible failures. Distinguish a component fault from a system failure; include hardware, software, dependency, and human error.
- **Scalability**: Name the load parameters first. Measure how throughput, queueing, and latency distributions change as QPS, data volume, fan-out, active users, or skew grows. “Scalable” without a growth model is not a useful claim.
- **Maintainability**: Improve **operability** with automation/observability, **simplicity** by reducing accidental complexity, and **evolvability** through stable boundaries and safe change.

### 3. Match data model and storage to access paths

- Use a **document aggregate** for bounded data that is read/written together; use references for shared, independently evolving, or unbounded data.
- Use **relational models** when arbitrary joins, integrity constraints, and flexible queries dominate; use **graphs** when variable-length traversal is the central operation.
- Choose **LSM trees** for write-heavy sequential workloads when compaction is acceptable; choose **B-trees** for predictable point/range access and mature in-place transactions.
- Separate **OLTP** and **OLAP** when scans/aggregations would compete with latency-sensitive operational traffic. Column stores and compression are designed for the analytical path.

### 4. Treat bytes and messages as long-lived contracts

Backward compatibility means new readers understand old data; forward compatibility means old readers handle new data. Prefer additive schema changes, stable field tags, optional/defaulted fields, and explicit mixed-version tests. A remote call is not a local function: timeouts, retries, version skew, and partial failure are part of the API.

### 5. Make replication semantics visible

Leader/follower replication gives one write order but introduces lag and failover choices. Multi-leader replication supports multi-datacenter/offline writes but requires conflict handling. Leaderless quorum replication needs `W`, `R`, and `N` analysis plus versioning, repair, and stale-read monitoring. Use read-your-writes, monotonic reads, or consistent-prefix reads when user sessions need stronger behavior than eventual consistency without global linearizability.

### 6. Partition for both balance and locality

Range partitions preserve ordered/range locality but can hotspot sequential keys. Hash partitions balance point load but fan out range queries. Secondary indexes force a choice between local indexes (query fan-out) and global/term indexes (write/coordination fan-out). Prefer many logical partitions, controlled rebalancing, versioned routing, and throttled movement.

### 7. Choose transaction guarantees by anomaly

Read committed prevents dirty reads/writes, but not all read skew or write conflicts. Snapshot isolation provides a stable view but can allow write skew. Serializable execution uses serial execution, 2PL, or SSI to protect cross-row/predicate invariants. Protect read-modify-write with atomic operations, compare-and-set, locks, predicate/index-range locks, or materialized conflict rows. Make retries idempotent.

### 8. Design around partial failure and uncertain time

A timeout says that evidence did not arrive, not that the remote operation did not happen. Use operation IDs, reconciliation, and idempotence. Use monotonic clocks for durations; do not use wall-clock time as proof of ordering or ownership. Leases require fencing tokens checked by the protected resource. Document the timing/fault model and separate safety from liveness.

### 9. Separate consistency, ordering, commit, and consensus

Linearizability gives a single real-time order for individual operations; serializability orders transaction histories. Causal consistency preserves dependencies without a total order. Total-order broadcast creates a common sequence. 2PC provides atomic commit but can block on coordinator failure; consensus chooses a value/order with agreement, integrity, validity, and termination under its model. Use consensus-backed coordination for uniqueness, leadership, and membership.

### 10. Use batch and stream processing as complementary derivation paths

Batch processes bounded history and is excellent for rebuilds; streams process unbounded input with low latency. A queue distributes work; a partitioned log retains replayable history. Choose join strategy by size/partition/order. For streams, define event time, processing time, windows, lateness, watermarks, offsets, state recovery, and correction behavior. Assume at-least-once processing and make effects idempotent.

### 11. Treat derived data as replaceable, observable state

Caches, indexes, warehouses, recommendations, and client replicas are materialized views. Identify the system of record, derivation function, freshness target, provenance, and rebuild path. For a code or schema change, replay into a new generation, validate, and publish atomically. Put duplicate suppression and final invariant checks at the end-to-end boundary. Measure integrity, timeliness, availability, provenance, privacy, and feedback effects separately.

---

## Chapter Index

| # | Title | Key frameworks |
|---|---|---|
| [ch01](chapters/ch01-reliable-scalable-maintainable.md) | Reliable, Scalable, and Maintainable Applications | fault tolerance, load parameters, percentiles, operability |
| [ch02](chapters/ch02-data-models-and-query-languages.md) | Data Models and Query Languages | documents, relational model, graphs, declarative queries |
| [ch03](chapters/ch03-storage-and-retrieval.md) | Storage and Retrieval | hash indexes, LSM trees, B-trees, OLTP/OLAP, column stores |
| [ch04](chapters/ch04-encoding-and-evolution.md) | Encoding and Evolution | compatibility, schemas, Avro, RPC, message dataflow |
| [ch05](chapters/ch05-replication.md) | Replication | leaders, lag, session guarantees, quorums, version vectors |
| [ch06](chapters/ch06-partitioning.md) | Partitioning | range/hash, hot spots, secondary indexes, rebalancing |
| [ch07](chapters/ch07-transactions.md) | Transactions | ACID, isolation anomalies, MVCC, 2PL, SSI |
| [ch08](chapters/ch08-trouble-with-distributed-systems.md) | The Trouble with Distributed Systems | partial failure, time, leases, fencing, fault models |
| [ch09](chapters/ch09-consistency-and-consensus.md) | Consistency and Consensus | linearizability, causality, total order, 2PC, consensus |
| [ch10](chapters/ch10-batch-processing.md) | Batch Processing | Unix pipelines, MapReduce, joins, derived output |
| [ch11](chapters/ch11-stream-processing.md) | Stream Processing | logs, CDC, event sourcing, time, windows, replay |
| [ch12](chapters/ch12-future-of-data-systems.md) | The Future of Data Systems | dataflow, unbundling, end-to-end correctness, auditability |

## Topic Index

- **ACID / isolation / transactions** → [ch07](chapters/ch07-transactions.md)
- **batch processing / MapReduce / joins** → [ch10](chapters/ch10-batch-processing.md)
- **causality / ordering / consensus** → [ch05](chapters/ch05-replication.md), [ch09](chapters/ch09-consistency-and-consensus.md)
- **change data capture / event sourcing / windows** → [ch11](chapters/ch11-stream-processing.md)
- **column stores / OLAP / LSM trees / B-trees** → [ch03](chapters/ch03-storage-and-retrieval.md)
- **data models / documents / graphs / SQL** → [ch02](chapters/ch02-data-models-and-query-languages.md)
- **dataflow / derived data / unbundling / privacy** → [ch12](chapters/ch12-future-of-data-systems.md)
- **encoding / schema evolution / RPC** → [ch04](chapters/ch04-encoding-and-evolution.md)
- **fencing / leases / clocks / partial failure** → [ch08](chapters/ch08-trouble-with-distributed-systems.md)
- **fault tolerance / scalability / percentiles** → [ch01](chapters/ch01-reliable-scalable-maintainable.md)
- **partitioning / hot spots / rebalancing** → [ch06](chapters/ch06-partitioning.md)
- **quorums / replication lag / version vectors** → [ch05](chapters/ch05-replication.md)
- **serializability / write skew / MVCC** → [ch07](chapters/ch07-transactions.md)
- **stream logs / offsets / event time / replay** → [ch11](chapters/ch11-stream-processing.md)
- **total order / linearizability / 2PC** → [ch09](chapters/ch09-consistency-and-consensus.md)

## Supporting Files

- [glossary.md](glossary.md) — key terms and definitions
- [patterns.md](patterns.md) — concrete techniques and trade-offs
- [cheatsheet.md](cheatsheet.md) — decision rules, tables, thresholds, and smells

## Scope & Limits

This skill captures the frameworks and design reasoning from *Designing Data-Intensive Applications*. It is not a substitute for current product documentation, operational runbooks, security review, or project-specific load testing.

