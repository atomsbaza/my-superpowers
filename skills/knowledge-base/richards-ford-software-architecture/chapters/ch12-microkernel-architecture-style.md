# Chapter 12: Microkernel Architecture Style

## Core Idea

Microkernel architecture separates a minimal core system from plug-in components. The core contains the fundamental workflow or rules, while plugins provide extensions, variations, or integrations. The style is valuable when the product needs a stable core and a changing set of capabilities.

## Frameworks Introduced

- **Core system plus plug-ins**:
  - **Core:** owns the primary flow, common state, and extension contract.
  - **Plug-in:** implements a specialized capability behind the contract.
- **Registry**: discovers, names, configures, and selects plug-ins.
- **Contracts**: stable interfaces and data agreements between core and plug-ins.
- **Product-line architecture**: use a shared core with variants assembled from different plug-ins.

## Key Concepts

- **Microkernel** — the minimal central system that coordinates essential behavior.
- **Plug-in component** — an extension that adds or varies capability.
- **Registry** — metadata or mechanism for discovering and loading plug-ins.
- **Contract** — the interface and behavioral assumptions that permit extension.
- **Core workflow** — the invariant process retained in the kernel.
- **Extension point** — an explicit location where behavior can be added.

## Mental Models

Use microkernel when variation is a first-class business concern: products, rules engines, workflow engines, IDEs, and systems with customer-specific extensions.

Keep the core small and stable. Every capability placed in the core increases the cost of changing the foundation and reduces the value of the extension boundary.

Treat plugin contracts as architecture decisions. Versioning, isolation, failure behavior, security, and performance constraints must be explicit.

## Anti-patterns

- **Big kernel**: the core absorbs every feature and the plugin boundary becomes cosmetic.
- **Plugin leakage**: plugins reach into core internals or depend directly on one another.
- **Unversioned contract**: a core change silently breaks all extensions.
- **Registry as bottleneck**: discovery and configuration become a single fragile dependency.

## Code Examples

A minimal extension contract:

```text
interface PricingPlugin {
    Quote calculate(QuoteRequest request)
    Capabilities capabilities()
}

core -> registry.select(request.context)
core -> plugin.calculate(request)
```

The core should not need to know plugin implementation details; the contract must define errors, timeouts, and compatibility.

## Reference Tables

| Concern | Core responsibility | Plugin responsibility |
|---|---|---|
| Workflow | Coordinate invariant steps | Implement variable behavior |
| State | Own shared/core state | Own extension-specific state |
| Compatibility | Version and enforce contract | Declare supported versions |
| Failure | Contain plugin failure | Return explicit failure/degraded result |
| Deployment | Provide extension runtime | Package and release extension |

## Worked Example

An insurance platform has a stable policy workflow but different rating rules by country and product. The core validates a policy request, manages the workflow, and records audit events. Country-specific rating plugins implement the volatile calculation behind a versioned contract. A registry selects a plugin by policy context. If a plugin fails, the core marks the request pending rather than corrupting shared state. New countries can be added without rewriting the core workflow.

## Key Takeaways

1. Microkernel fits stable workflows with variable extensions.
2. The core should remain minimal and own invariant behavior.
3. Registries and contracts are part of the architecture, not implementation trivia.
4. Plugin isolation and versioning determine whether extensibility is real.

## Connects To

- **Chapter 3:** stable contracts reduce cross-boundary connascence.
- **Chapter 13:** service-based styles provide another way to isolate capabilities.
- **Chapter 18:** choose microkernel when variation and extension are dominant drivers.

