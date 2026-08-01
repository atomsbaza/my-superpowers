# Chapter 11 — Networking

## Core Idea

Network configuration is part of application behavior. A server may have several interfaces, routes, addresses, and failure paths, and each integration point may have different reachability and trust requirements. Resilience depends on making those choices explicit rather than relying on whichever route or interface the operating system happens to select.

## Frameworks Introduced

- **Explicit interface intent:** bind listeners and outbound connections to the interface or address that matches the design.
- **Route-aware integration:** reason about path, source address, destination, DNS, firewall, and failover together.
- **Virtual address indirection:** separate a service identity from a particular machine when failover requires it.

## Key Concepts

### Multihomed servers

A host with public, private, management, storage, or replication interfaces has multiple possible paths. Binding a listener to all interfaces can expose an administrative or internal service unintentionally. Binding outbound traffic without considering source address can select a route that a firewall or peer does not accept.

For each listener and integration, document:

- intended local address or interface;
- destination and expected route;
- firewall and security-group assumptions;
- DNS or service-discovery identity;
- behavior when the preferred path fails.

### Routing

Routing failures can look like application failures: connection timeouts, asymmetric paths, intermittent resets, or traffic reaching the wrong network zone. Test the actual path from the deployed topology. A successful connection from an operator laptop is not evidence that every application node can reach the dependency.

Use timeouts appropriate to the operation and classify errors. A connect timeout, TLS failure, DNS failure, and application rejection have different remediation paths. Do not let a network timeout occupy an unbounded thread or connection slot.

### Virtual IP addresses

A virtual IP can provide a stable service identity while an active node changes. This simplifies clients when failover moves the address, but it does not automatically solve stale connections, state synchronization, ARP/DNS propagation, health checking, or split-brain. Clients must reconnect safely, and the failover mechanism must define ownership and fencing.

## Review Checklist

- Are management endpoints inaccessible from the public interface?
- Does each listener bind only where required?
- Are outbound source addresses and routes deterministic?
- Are DNS names, virtual IPs, certificates, and health checks aligned?
- What happens to existing connections after failover?
- Is there a test for asymmetric routing, partial reachability, and DNS failure?
- Are connection, read, and overall-operation deadlines distinct?

## Reference Table

| Network concern | Failure mode | Design response |
|---|---|---|
| Any-interface binding | Accidental exposure | Bind explicitly and verify from each zone |
| Ambiguous route | Intermittent or blocked dependency | Document source, path, and route policy |
| Stale connection | Requests use failed node/path | Detect, close, and reconnect safely |
| Virtual IP move | Split-brain or stale ARP | Health checks, fencing, and ownership protocol |
| Long network wait | Thread/pool exhaustion | Layered deadlines and bounded retries |

## Worked Example

An application host has a public interface and a private database interface. A new admin endpoint binds to `0.0.0.0`, making it reachable through the public address. Separately, a database failover moves a virtual IP, but the connection pool keeps dead sockets. The fixes are different: bind the admin listener to the management/private address and validate or discard pooled connections after network failure. Treating both as “the network is flaky” obscures the actual controls.

## Key Takeaways

1. Interface selection, routing, and service identity are application design decisions.
2. Make listener exposure and outbound paths explicit.
3. A virtual IP moves identity, not state or live connections.
4. Test partial network failure, not only total host failure.

## Connects To

- Chapter 5 uses timeouts and handshaking to contain network uncertainty.
- Chapter 12 applies least privilege to network-reachable services.
- Chapter 13 combines network identity with load balancing and clustering.

