# Chapter 25: Compute as a Service

## Core Idea

Compute as a Service (CaaS) provides a standardized, managed environment for running software at organizational scale. The abstraction removes infrastructure toil but requires software to be designed for distributed failure, explicit state, workload type, resource sizing, and the trade-off between centralization and customization.

## Frameworks Introduced

- **Tame the compute environment**: Standardize scheduling, isolation, resource allocation, and lifecycle management.
  - When to use: Running many services or batch workloads.
  - How: Automate placement, rightsizing, autoscaling, and recovery instead of hand-managing machines.
- **Architect for failure**: Managed distributed environments will reschedule, restart, partition, and lose individual resources.
  - When to use: Any service running on shared or elastic infrastructure.
  - How: Make retries safe, manage state explicitly, design for partial failure, and observe dependencies.
- **Batch versus serving**:
  - **Batch**: Work completed asynchronously, often optimized for throughput.
  - **Serving**: Long-running request handling, optimized for latency and availability.
  - When to use: Choosing runtime assumptions and scheduling policy.
  - How: Match the workload model to its user-facing contract.
- **Centralization versus customization**: Shared infrastructure creates leverage, while custom paths may be necessary for special constraints.
  - When to use: Choosing a compute platform or abstraction level.
  - How: Standardize common needs and permit controlled escape hatches with explicit ownership and cost.
- **Serverless trade-off**: Higher abstraction reduces operational work but can limit control, portability, and predictability.
  - When to use: Evaluating managed/serverless platforms.
  - How: Compare the platform’s abstraction to workload requirements rather than treating “serverless” as universally simpler.

## Key Concepts

- **CaaS**: A managed service that runs workloads on shared compute infrastructure.
- **Containerization**: Packaging software and its declared environment into an isolated unit.
- **Multitenancy**: Multiple workloads sharing infrastructure with isolation.
- **Rightsizing**: Allocating resources close to actual workload needs.
- **Autoscaling**: Adjusting capacity in response to demand.
- **Serving workload**: A request-driven, usually long-running service.
- **Batch workload**: A job-driven workload that can run asynchronously.
- **Implicit dependency**: An unrecorded assumption about the runtime environment.
- **Serverless**: A high-level compute abstraction that hides server management.

## Mental Models

- CaaS is an organizational API: its stability and defaults shape every workload.
- Containers isolate packaging, not all behavior; network, time, identity, and resource assumptions remain.
- Compute is a shared pool: unbounded resource requests impose costs on neighbors.
- The highest useful abstraction is the one that removes toil without hiding a required control.

## Anti-patterns

- **Pets on shared infrastructure**: Hand-tuned instances that cannot be recreated or rescheduled.
- **Unbounded retries**: Cascading failures caused by retry storms and absent backoff.
- **Hidden state**: Assuming local disk or process memory survives rescheduling.
- **One platform for every workload**: Forcing batch, serving, and specialized jobs into an unsuitable abstraction.
- **Custom infrastructure by default**: Recreating platform capabilities without the scale or ownership to maintain them.

## Worked Example

A service moved to managed compute should externalize durable state, declare resource needs, handle restart and rescheduling, expose health signals, and distinguish request-serving from background work. A standardized configuration can then let the platform schedule and autoscale it. If the service needs a specialized accelerator or latency guarantee, the exception should be explicit rather than hidden in an ad hoc deployment script.

## Reference Table

| Decision | Prefer standardization when | Prefer customization when |
|---|---|---|
| Runtime abstraction | Workload matches common platform assumptions | Required control is absent |
| Resource policy | Demand is variable and measurable | Workload has unusual guarantees |
| State placement | Durable shared storage is available | Local ephemeral state is intentional |
| Serverless | Operational simplicity dominates | Control, portability, or predictable cost dominates |

## Key Takeaways

1. Standardize compute operations to remove toil.
2. Design for restart, rescheduling, partial failure, and shared resources.
3. Separate batch and serving assumptions.
4. Make state and runtime dependencies explicit.
5. Choose the abstraction level that fits the workload and preserves necessary control.

## Connects To

- **Chapter 18**: Build systems provide reproducible artifacts for deployment.
- **Chapter 23**: CI validates deployment and runtime assumptions.
- **Chapter 24**: Continuous delivery depends on a stable compute platform.

