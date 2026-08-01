# Chapter 4: Encoding and Evolution

## Core Idea

Encoding is a contract between processes and over time. A format must be efficient enough for its workload, but its most important property is that old and new code can coexist during rolling deployments, long-lived data, replication, and message replay.

## Frameworks Introduced

- **Backward and forward compatibility**: New readers should understand old data (backward compatibility); old readers should safely handle data written by new code (forward compatibility).
  - When to use: every schema or wire-format change.
  - How: add optional fields, preserve field identifiers, define defaults, avoid destructive type changes, and test mixed-version paths.
- **Schema evolution with stable field tags**: Protocol Buffers and Thrift identify fields by numeric tags rather than position or field name.
  - When to use: compact RPC/message formats with generated code and long-lived schemas.
  - How: never reuse a removed tag, add new optional fields, and treat renames as cosmetic if the tag remains stable.
- **Avro writer/reader schema resolution**: The writer records data using one schema; the reader resolves it against its own schema at read time.
  - When to use: files or messages whose writer and reader versions are controlled independently.
  - How: evolve schemas within compatible rules and make the writer schema available through the file header, registry, or negotiated protocol.
- **Modes of dataflow**: Data moves through databases, services (REST/RPC), and asynchronous message passing; each boundary has different compatibility and failure semantics.
  - When to use: choosing an integration boundary or migration strategy.
  - How: specify ownership, retry/idempotence behavior, versioning, and whether data is stored for later replay.

## Key Concepts

- **Encoding/serialization**: Converting in-memory structures into bytes and back.
- **Schema**: The expected structure, types, and constraints of encoded data.
- **Backward compatibility**: New code reads old encoded data.
- **Forward compatibility**: Old code reads data written by new code.
- **Field tag**: Stable numeric identifier used by a schema-based binary format.
- **Writer schema**: The schema used to encode a particular record.
- **Reader schema**: The schema the consumer wants to see.
- **RPC**: A request/response abstraction over a network boundary.
- **Message broker**: A component that accepts messages and delivers them asynchronously.
- **Rolling upgrade**: Replacing instances incrementally while old and new versions coexist.

## Mental Models

- Treat a schema change as a distributed deployment problem, not a local refactor.
- Prefer additive changes that preserve old meanings; removing or reusing identifiers is dangerous because old data and old code persist.
- Separate “can be decoded” from “has the business meaning I want”; defaults can preserve wire compatibility while hiding semantic problems.
- Think of a message as durable API data: retries, delayed delivery, and replay make it outlive the producer process.

## Anti-patterns

- **Using language-native serialization across service boundaries**: It couples consumers to a language/runtime and may create security risks.
- **Changing a field’s meaning while keeping its name/tag**: Bytes remain readable but the business contract silently breaks.
- **Reusing removed field numbers**: Old data can be misinterpreted by a new reader.
- **Assuming RPC behaves like a local function**: Timeouts, retries, partial failure, and version skew make remote calls fundamentally different.

## Code Examples

```protobuf
message User {
  required string user_name = 1;
  optional string favorite_color = 2;
  optional string bio = 3;
}
```

- **What it demonstrates**: Field tags, rather than source order, identify fields; adding an optional field can remain compatible with older readers.

```text
writer schema: {name: string, favorite_color: string}
reader schema: {name: string, favorite_color: string, bio: string = ""}
```

- **What it demonstrates**: A reader can project an evolved schema and supply a default for data written before `bio` existed.

## Reference Tables

| Format/family | Strength | Evolution concern |
|---|---|---|
| JSON/XML | human-readable, broad tooling | larger, ambiguous types, weak schema discipline |
| Protocol Buffers/Thrift | compact, typed, generated APIs | stable tags and compatible type changes required |
| Avro | writer/reader resolution, schema-driven files | schema distribution/registry and compatibility rules |
| Language-specific | convenient inside one codebase | tight coupling and unsafe/opaque cross-language use |

## Worked Example

During a rolling deployment, version 1 writes `{name, favorite_color}` while version 2 introduces an optional `bio`. Version 2 readers must handle old records by using a default. Version 1 readers must ignore the new field when they receive version 2 data. Only after all readers understand both forms should a required semantic change be introduced, usually as a new field or a staged migration. For an asynchronous event, also make the consumer idempotent: a retry may deliver the same event after the producer has moved on.

## Key Takeaways

1. Compatibility is two-directional and must be tested with mixed versions.
2. Stable identifiers and additive changes are the safest default for long-lived data.
3. Databases, RPC, and messages are separate dataflow modes with distinct failure semantics.
4. A durable message outlives the code that produced it; design for replay and delayed consumers.
5. Keep encoding concerns separate from application-level meaning and migration policy.

## Connects To

- **Chapter 5**: Replication logs are dataflow streams whose encoding must evolve safely.
- **Chapter 11**: Event streams, CDC, and replay make schema compatibility operationally critical.
- **Chapter 12**: Reprocessing derived data depends on stable, auditable encodings.

