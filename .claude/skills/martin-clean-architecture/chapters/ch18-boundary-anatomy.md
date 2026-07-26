# Chapter 18: Boundary Anatomy

## Core Idea
Architectural boundaries come in a spectrum of physical strengths — monolith (source-level), deployment components, local processes, and services — each trading cheaper/faster communication for weaker isolation, but all following the same rule: source-code dependencies must point from lower-level details toward higher-level components, regardless of which physical form the boundary takes.

## Frameworks Introduced
- **Boundary strength spectrum**: monolith < deployment component < local process < service, ordered by increasing isolation strength and increasing communication cost/latency.
  - When to use: when deciding the physical/runtime form a given architectural boundary should take.
  - How: pick the weakest (cheapest, fastest) form that satisfies current isolation needs; a boundary's *existence* (discipline in source-code dependency management) matters even when its physical form is invisible, as in a monolith.
- **Boundary crossing discipline**: at runtime a boundary crossing is just a function call passing data across it; the real discipline is managing the *source code dependency direction* across that call, not the runtime call itself.
  - When to use: at every point where control flow crosses a boundary.
  - How: for a low-level-client-calls-higher-level-service crossing, both runtime and compile-time dependencies point the same way (toward the higher-level component) — the simple case. For a high-level-client-calls-lower-level-service crossing, use dynamic polymorphism (an interface owned by the high-level side) so the compile-time dependency is inverted against the runtime flow of control — runtime control still crosses low→high in the interface sense, but source dependency points from the low-level implementation back up to the interface.

## Key Concepts
- **Boundary crossing**: at runtime, nothing more than a function call on one side invoking a function on the other side, optionally passing a data structure (`<DS>`).
- **Monolith**: the weakest/simplest boundary — no physical deployment representation, just disciplined segregation of functions/data within a single process/address space (statically linked executable, single jar, single .EXE); relies on dynamic polymorphism (OO) to manage internal dependencies, since raw function pointers are too risky for most teams to use safely.
- **Deployment component**: the simplest *physical* boundary — a dynamically linked library (DLL, jar, Gem, shared library); deployment is gathering these binaries together (e.g., into a WAR or directory), no compilation step; otherwise behaves like a monolith (same address space, function-call communication).
- **Threads**: not an architectural boundary or deployment unit — just a way to organize execution order/scheduling; can live wholly within one component or span many.
- **Local process**: a stronger physical boundary — separate address space (via OS process/command-line creation), typically same machine/processor set; communicates via sockets, mailboxes, or message queues; may be a monolith or composed of deployment components internally. "A kind of uber-component."
- **Service**: the strongest boundary — a process assumed to communicate purely over the network, with no assumption of shared physical location; highest latency (tens of ms to seconds), requires care to avoid excessive "chattiness."
- **Chattiness**: how much high-frequency, low-value back-and-forth communication crosses a boundary; tolerable and cheap across monolith/deployment boundaries (plain function calls), must be carefully limited across local-process and especially service boundaries due to marshaling/context-switch/network cost.

## Mental Models
- Think of boundary strength and communication cost as directly correlated: the stronger the isolation (monolith → deployment → process → service), the more expensive and higher-latency each crossing becomes — choose the weakest boundary that still gives you the isolation you actually need right now.
- Use "which side owns the interface?" to determine dependency inversion at a crossing: whichever side is higher-level (more policy, less detail) should own the interface that the lower-level side implements, regardless of which side initiates the runtime call.
- Treat a local process as an "uber-component" — internally it's still built from monolith or deployment-component-style pieces obeying the same source-dependency direction rules; the process boundary is just one more (stronger) layer wrapped around that same discipline.
- Most real systems are NOT purely one boundary type — expect a mixture (e.g., a service that internally is a facade over several local processes, each of which is a monolith or set of deployment components).

## Anti-patterns
- **Assuming a monolith has "no boundaries"**: because there's no physical deployment separation, teams may skip the discipline of separating components — but the value of independent development/testing of logically separate components exists even without physical separation; skipping it loses that value for no benefit.
- **Excessive chattiness across process or service boundaries**: OS calls, data marshaling/decoding, and network round-trips are moderately-to-very expensive; treating a service boundary like an in-process function call (fine-grained, high-frequency calls) causes severe latency/performance problems.
- **Higher-level process/service source code containing physical knowledge of lower-level ones**: e.g., a higher-level process embedding the URI, registry key, or physical address of a lower-level process/service inverts the intended dependency direction — lower-level components should "plug in" to higher-level ones, not be hard-referenced by them.
- **Relying on raw function pointers instead of OO/dynamic polymorphism to manage monolith-internal dependencies**: the author calls this "dangerous" and notes most architects avoid it, effectively abandoning component partitioning if they don't have polymorphism available.

## Code Examples
No language-specific code samples in this chapter (diagram/pattern-driven: Figures 18.1 and 18.2 depict `Client → f() → Service` with a `<DS>` Data marker, both with and without dependency inversion via a `Service` interface).
- **What it demonstrates**: the two canonical shapes of a boundary crossing — (1) low-level client calling high-level service, where runtime and compile-time dependency both point toward the higher-level component; (2) high-level client calling a lower-level `ServiceImpl` through a `Service` interface it owns, where compile-time dependency is inverted to still point toward the higher-level component even though runtime control flows the other way.

## Reference Tables
| Boundary Type | Physical Representation | Address Space | Communication Mechanism | Relative Cost/Latency |
|---|---|---|---|---|
| Monolith | none (single executable) | shared | function calls | cheapest, can be very chatty |
| Deployment component | DLL / jar / Gem / shared library | usually shared | function calls (+ one-time link/load cost) | cheap, can be very chatty |
| Local process | OS process | separate | sockets, mailboxes, message queues | moderate — limit chattiness |
| Service | independent process, network-based | separate, possibly different machines | network calls | high (tens of ms–seconds) — must minimize chattiness |

## Worked Example
Two boundary-crossing shapes, per Figures 18.1/18.2: (1) A `Client` calls `Service.f()` directly, passing a `Data` structure defined on the *called* (Service) side — both the compile-time dependency and the runtime flow of control point the same direction, from Client toward Service (the higher-level component). (2) A high-level `Client` needs to call a *lower-level* `ServiceImpl`; instead of depending on `ServiceImpl` directly, `Client` calls through a `Service` interface that `Client`'s side (the higher-level component) owns, and `ServiceImpl` implements that interface. Now the runtime flow of control still crosses left-to-right (Client → ServiceImpl), but the *compile-time* source dependency of `ServiceImpl` points back left, up to the `Service` interface — meaning the higher-level component's source is never polluted by knowledge of the lower-level implementation. This dynamic-polymorphism inversion is what allows lower-level details (databases, UIs, frameworks — see Ch 17) to depend on business rules instead of the reverse, no matter which physical boundary type (monolith, deployment component, process, or service) is used to realize the crossing.

## Key Takeaways
1. A boundary crossing at runtime is always just a function call plus data; the architectural discipline is entirely about managing the *source-code* dependency direction across it.
2. Choose the weakest/cheapest boundary type (monolith → deployment → local process → service) that satisfies your actual current isolation needs — stronger boundaries cost more in latency and complexity.
3. When a high-level component must call a lower-level one, invert the compile-time dependency via an interface owned by the high-level side (dynamic polymorphism), regardless of which physical boundary type is in play.
4. Minimize chattiness as boundary strength increases — cheap across monoliths/deployment components, must be carefully controlled across processes and especially services.
5. Higher-level components (processes or services) must never embed physical knowledge (names, addresses, URIs, registry keys) of lower-level ones — lower-level components should "plug in" to higher-level ones.
6. Most real systems mix boundary types — a service may be a facade over multiple local processes, each built from monolithic or deployment-component pieces — apply the same dependency-direction discipline uniformly across all of them.

## Connects To
- **Ch 17 (Boundaries: Drawing Lines)**: this chapter is the direct physical/runtime follow-up — Ch 17 establishes *where* and *why* to draw boundaries (plugin architecture, axis of change); Ch 18 covers *what form* those boundaries take at runtime.
- **Ch 16 (Independence)**: the decoupling-mode spectrum (source/deployment/service level) introduced there maps directly onto this chapter's monolith/deployment-component/service boundary types.
- **Dynamic polymorphism / OO**: the mechanism enabling dependency inversion across any boundary crossing where runtime control flow and desired source dependency direction differ.
