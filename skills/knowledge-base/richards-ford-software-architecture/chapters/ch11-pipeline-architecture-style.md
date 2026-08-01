# Chapter 11: Pipeline Architecture Style

## Core Idea

Pipeline architecture processes data through a sequence of filters connected by pipes. Each filter performs a focused transformation, and the style is particularly effective for batch or streaming data transformations where stages can be composed and reasoned about independently.

## Frameworks Introduced

- **Pipes and filters**:
  - **Pipe:** transports data between stages and can provide buffering or protocol behavior.
  - **Filter:** transforms, validates, enriches, or consumes data.
- **Four filter categories**:
  - **Producer:** creates the initial data.
  - **Transformer:** changes or enriches data while continuing the flow.
  - **Tester:** evaluates data and routes or rejects it based on a condition.
  - **Consumer:** terminates or persists the flow.
- **Pipeline composition**: build a processing path by connecting focused filters rather than embedding all transformations in one unit.

## Key Concepts

- **Pipeline** — an ordered path through filters.
- **Pipe** — the communication channel between filters.
- **Filter** — a stateless or stateful transformation stage.
- **Producer** — source of data entering the pipeline.
- **Transformer** — modifies data in flight.
- **Tester** — makes a decision about data.
- **Consumer** — final destination or side-effecting stage.
- **Technical partitioning** — the style commonly partitions by processing function rather than domain capability.

## Mental Models

Use pipeline architecture when the system’s core problem is transforming data through a sequence of relatively independent steps. It works best when each filter has a clear contract and the data shape between stages is stable.

Treat pipes as first-class capacity and failure boundaries. Buffer size, backpressure, ordering, retry, and poison-message behavior affect the whole pipeline.

Prefer stateless filters when possible. State increases coordination, recovery, and scaling complexity.

## Anti-patterns

- **Fat filter**: one stage contains unrelated transformations and becomes a hidden monolith.
- **Unbounded pipe**: buffering hides overload until memory or latency fails.
- **Shared mutable state**: filters coordinate through hidden state instead of explicit data.
- **Pipeline for business transactions**: using a linear transformation style when branching invariants and long-lived state dominate.

## Code Examples

A functional pipeline sketch:

```text
input
  |> parse
  |> validate
  |> enrich
  |> route
  |> persist
```

Each function should define input, output, error, ordering, and backpressure behavior.

## Reference Tables

| Element | Responsibility | Design question |
|---|---|---|
| Pipe | Transport and buffering | How is backpressure handled? |
| Producer | Introduce data | Can input be replayed? |
| Transformer | Change data | Is it deterministic and idempotent? |
| Tester | Route/accept/reject | What happens to failed data? |
| Consumer | Persist or terminate | How are commits and retries handled? |

## Worked Example

An image-processing system receives files, decodes them, resizes them, applies a watermark, and stores variants. Each stage is a filter with a versioned image contract. A bounded pipe between resize and watermark prevents the producer from overwhelming the slowest stage. Failed images are routed to a quarantine consumer with a correlation ID. The pipeline is easier to extend than a single processing method, but operational characteristics depend on queue limits and replay behavior.

## Key Takeaways

1. Pipes and filters make sequential data transformation explicit.
2. Filter contracts, backpressure, and failure handling define the real architecture.
3. Keep filters focused and preferably stateless.
4. Choose another style when complex business state or branching coordination dominates.

## Connects To

- **Chapter 14:** event-driven systems often use pipeline-like processing stages.
- **Chapter 15:** data pumps and readers/writers apply similar processing ideas at scale.
- **Chapter 17:** microservices can accidentally become distributed pipelines.

