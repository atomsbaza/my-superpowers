# Chapter 16: Independence

## Core Idea
A good architecture supports use cases, operation, development, and deployment simultaneously by decoupling the system along two axes — horizontal layers (UI, application-specific rules, application-independent rules, database) and vertical use-case slices — while deliberately keeping the decoupling *mode* (source, deployment, or service level) an open, reversible option for as long as possible.

## Frameworks Introduced
- **Conway's Law**: "Any organization that designs a system will produce a design whose structure is a copy of the organization's communication structure."
  - When to use: when planning how to partition a system across multiple development teams.
  - How: architect components so they map to independently-workable units, letting teams be allocated to well-isolated components without interfering with each other.
- **Decoupling layers (horizontal)**: separate things that change for different reasons — UI, application-specific business rules, application-independent (domain) business rules, and database/persistence details — into distinct layers.
  - When to use: always, as the baseline SRP/CCP-driven partitioning of any system.
  - How: apply SRP/CCP to identify what changes at different rates for different reasons; UI changes for reasons unrelated to business rules; input-validation rules (application-specific) change at a different rate than domain rules like interest calculation (application-independent); persistence details change independently of both.
- **Decoupling use cases (vertical)**: separate each use case (e.g., add-order vs. delete-order) down through all the horizontal layers it touches, so adding a new use case doesn't risk breaking existing ones.
  - When to use: whenever a system is expected to grow new use cases over time.
  - How: keep each use case's slice of UI, business rules, and database access separate from other use cases' slices, even where they touch the same layers.
- **Decoupling mode**: the mechanism used to realize layer/use-case separation — source level, deployment level, or service level.
  - When to use: chosen based on current operational/development/deployment needs, and expected to change over the project's lifetime.
  - How: prefer starting at source-level decoupling (cheapest), pushing components to deployment-level or service-level only as operational/development/deployment pressures actually demand it — while designing so the option to escalate (or later de-escalate back toward monolith) remains open.

## Key Concepts
- **Source-level decoupling**: controlling dependencies between source modules so a change to one doesn't force recompilation of others (e.g., Ruby Gems); all components run in the same address space via function calls — the "monolithic structure."
- **Deployment-level decoupling**: controlling dependencies between deployable binary units (jar, DLL, shared library) so a source change in one doesn't force rebuild/redeploy of others; components may still share an address space or communicate via IPC/sockets/shared memory.
- **Service-level decoupling**: reducing dependencies to data-structure/network-packet level so every execution unit is fully independent of source and binary changes in others (services/micro-services).
- **True duplication vs. accidental (false) duplication**: true duplication is where every change to one instance requires the identical change to its duplicate; accidental duplication is superficially similar code that evolves along independent paths for independent reasons and should NOT be merged.
- **Immediate deployability**: the deployment goal — a good architecture avoids reliance on manual configuration scripts, ad hoc file/directory setup, etc., so the system is deployable right after build.
- **Independent develop-ability / deployability**: emergent benefits of proper layer+use-case decoupling — teams can work and components can be hot-swapped/added without interfering with unrelated parts of the system.

## Mental Models
- Think of the system as a grid: horizontal layers (UI / app-specific rules / domain rules / DB) crossed by vertical use-case slices — decoupling must happen along both axes simultaneously.
- Use "will these two similar-looking things change at different rates, for different reasons?" as the test before merging apparently duplicated code — if yes, the duplication is accidental and should be left alone (or you'll pay a much higher cost un-merging it later).
- Treat decoupling mode as a dial, not a fixed choice: start cheap (source level), turn the dial up (deployment, then service level) only as real development/deployment/operational pressure demands, and be willing to turn it back down as pressure subsides — a good architecture "protects the majority of the source code" from mode changes.
- Default-to-microservices is a trap: service-level decoupling by default is expensive (dev time + runtime resources) and tends to produce coarse-grained boundaries no matter how "micro" the services claim to be.

## Anti-patterns
- **Knee-jerk elimination of duplication**: merging two use cases' similar screens/algorithms/queries because they look alike, without checking whether the similarity is true or accidental — creates unwanted coupling between use cases that will diverge over time and be painful to re-separate.
- **Passing a database record structure straight up to the UI instead of creating a view model**: treats accidental structural similarity as true duplication, coupling layers that should stay independent.
- **Committing to service-level decoupling by default**: expensive in both development time and runtime resources; wastes effort on boundaries that may not be needed, and doesn't necessarily produce fine-grained enough decoupling anyway.
- **Building an architecture that depends on monolithic structure**: cannot be easily upgraded to multiple processes/threads/services later if operational needs grow — the opposite of "leaving options open."

## Reference Tables
| Decoupling Mode | Mechanism | Example | Communication cost |
|---|---|---|---|
| Source level | control source-module dependencies | Ruby Gems | in-process function calls (cheap) |
| Deployment level | control dependencies between binary/deployable units | .NET DLL, Java jar, shared library | mostly function calls; some IPC/sockets/shared memory |
| Service level | reduce dependencies to data structures over the network | services / micro-services | network calls (most expensive, highest latency) |

## Worked Example
A shopping-cart-style system must support: use cases (buy, add-to-cart, remove-from-cart, etc.), operation (throughput/response-time targets), development (multiple teams), and deployment (ease of shipping). The author's recommended approach: apply SRP/CCP to split UI from application-specific business rules from application-independent (domain) business rules from the database layer (horizontal), and simultaneously keep each use case's slice of those layers separate from other use cases' slices (vertical) — e.g., the add-order use case's UI/rules/DB code stays separate from delete-order's. Initially deploy everything as a single source-level-decoupled monolith. If, over time, the add-order flow needs to scale independently (operational pressure) or a separate team needs to own it (development pressure), that vertical+horizontal separation already in place makes it straightforward to promote just that slice to a deployment-level component, or ultimately a service — without having to restructure the whole system, and with the option to fold it back into the monolith later if that pressure subsides.

## Key Takeaways
1. Decouple both horizontally (UI / app-specific rules / domain rules / DB) and vertically (per use case) — a system needs both axes of separation to support independent use case addition.
2. Treat decoupling mode (source/deployment/service) as a reversible dial tuned by actual operational, development, and deployment pressure — not a permanent up-front architectural bet.
3. Default to source-level decoupling; escalate to deployment- or service-level only when real pressure justifies the cost.
4. Before merging similar-looking code, verify it's true duplication (same reason to change) not accidental duplication (different reasons, will diverge) — accidental merges create false coupling that's expensive to undo.
5. Conway's Law means team structure and system structure will mirror each other whether you intend it or not — design component boundaries deliberately rather than let team communication patterns dictate them by default.
6. Aim for "immediate deployability" — a good architecture should not require manual configuration steps to go from build to running system.

## Connects To
- **Ch 15 (What Is Architecture?)**: this chapter operationalizes the four life-cycle concerns (use cases, operation, development, deployment) introduced there.
- **SRP / CCP**: the mechanism used to decide what belongs in which horizontal layer and vertical use-case slice.
- **Ch 21 "Screaming Architecture"**: referenced regarding making use cases visible in the architecture.
- **Conway's Law**: named and applied directly to explain why team structure drives (or should be deliberately decoupled from) component structure.
