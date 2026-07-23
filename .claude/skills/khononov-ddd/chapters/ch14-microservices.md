# Chapter 14: Microservices

## Core Idea
A microservice is simply a service with a micro-public interface, and its design quality should be judged by John Ousterhout's "deep module" heuristic; DDD's Bounded Contexts, Aggregates, and Subdomains define, respectively, the widest, narrowest, and safest/most-balanced boundaries for placing microservices.

## Frameworks Introduced
- **Microservices as Deep Modules**: A module (physical, in the case of a microservice) is defined by its function (public interface complexity) and logic (implementation complexity). Visualized as a rectangle — width is the interface, area is the implementation — an effective module is "deep": a narrow, simple interface hiding a large, complex implementation. A "shallow" module has an interface whose complexity approaches that of its implementation, adding accidental complexity instead of encapsulating it. This is a direct application of Ousterhout's model from *The Philosophy of Software Design*, adapted from logical modules to physical microservice boundaries.
  - When to use: As the evaluation lens for any proposed microservice boundary — before committing to a decomposition, check whether the resulting service will be deep or shallow.
  - How: Draw the service as a rectangle; ask whether its public interface stays narrow relative to the business logic it encapsulates. If splitting a component forces the interface to grow (extra integration methods), the split made the module shallower, not better.
- **DDD boundary alignment for microservices** (Bounded Contexts, Aggregates, Subdomains as service boundaries): Bounded contexts mark the *widest* valid boundary (the largest defensible monolith protecting one ubiquitous language); aggregates mark the *narrowest* valid boundary (the smallest indivisible transactional/business-rule unit); subdomains sit between the two and are the safest default because their "what, not how" framing naturally produces deep modules.
  - When to use: When deciding where to cut a system into microservices — instead of guessing at line counts or team size, use these existing DDD boundaries as candidate seams.
  - How: Default to aligning services with subdomain boundaries. Only widen to a full bounded context when nonfunctional or organizational constraints favor a broader monolith; only narrow to a single aggregate when that aggregate's business logic is strongly self-contained and rarely interacts with sibling aggregates.

## Key Concepts
- **Service**: A mechanism providing access to capabilities through a prescribed public interface (synchronous or asynchronous) — the service's "front door."
- **Microservice**: A service with a micro-public interface — a small front door, not necessarily small implementation.
- **"Method as a Service" anti-pattern**: Decomposing a system so finely that each service exposes essentially one method, forcing services to grow "staff only" integration interfaces to compensate.
- **Design goal (of microservices architecture)**: To produce a flexible *system*, not merely simple individual services — a system cannot be built from independent components; integration and communication between services are inherent.
- **System complexity (local vs. global)**: Local complexity is the complexity within a single microservice's implementation; global complexity is the complexity of interactions/dependencies among services. Both extremes are bad — all-local (monolith/big ball of mud) or all-global-ignored (distributed big ball of mud) — the goal is balancing both.
- **Deep vs. shallow services**: A deep service has a simple interface over complex logic (reduces global complexity); a shallow service's interface approaches the complexity of its logic (adds global complexity via forced integration surface).
- **Compressing Microservices' Public Interfaces**: Using Open-Host Service (published language) and Anticorruption Layer to shrink a service's effective public interface without shrinking its implementation, making it deeper.
- **Microservices threshold**: The point of decomposition beyond which further splitting increases rather than decreases the cost of change, because services turn shallow and interfaces balloon back up.

## Mental Models
- A good microservice boundary is a deep module: small interface, large implementation — judge boundaries by interface-to-logic ratio, not line count or team-size rules of thumb.
- Granularity is a U-shaped cost curve: cost of change decreases as a monolith is decomposed toward the microservices threshold, then increases again past it as services become shallow and integration costs dominate.
- Safe boundaries live in the band between bounded contexts (widest) and microservices/aggregates (narrowest) — outside that band you get either a big ball of mud (too wide, conflicting models) or a distributed big ball of mud (too narrow, chatty integration).
- All microservices are bounded contexts, but not all bounded contexts are microservices — the relationship is asymmetric, so the two terms should not be used interchangeably.

## Anti-patterns
- **"Method as a Service"**: Applying a naive "one method per service" decomposition rule. Each resulting service looks simple in isolation, but because services must still cooperate, their interfaces balloon with integration-only methods, and the overall system becomes a distributed big ball of mud — local complexity minimized, global complexity maximized.
- **Defining microservices by superficial metrics**: Lines-of-code limits or "easier to rewrite than modify" heuristics focus on the individual service and ignore the system-level interactions that actually determine whether a boundary is sound.
- **Decomposing aggregates into multiple services/bounded contexts**: Splitting a single aggregate's invariant boundary across services is not just suboptimal but produces real consistency problems (elaborated in the book's case-study appendix).

## Code Examples
(omit — not code-heavy)

## Reference Tables
| DDD Concept | Microservice Boundary Role |
|---|---|
| Bounded Context | Widest valid boundary; protects consistency of one ubiquitous language/model. All microservices are bounded contexts, but a bounded context may be wider than any single microservice (may contain multiple subdomains). |
| Aggregate | Narrowest valid boundary; an indivisible transactional/business-rule unit. Can work as a microservice when its logic is largely self-contained, but strong relationships to sibling aggregates make it shallow as a standalone service. |
| Subdomain | Balanced, generally safest boundary; a coherent set of use cases sharing a model and strong functional relationship. Naturally deep (function/"what" stays simple while implementation/"how" absorbs complexity), making it the default heuristic for microservice boundaries. |

## Worked Example
The chapter walks through a backlog management service with eight public methods and applies a naive "one method per service" split. Each resulting microservice still encapsulates its own database (per microservice convention), so no service may query another's database directly — all cross-service coordination must go through public interfaces. But splitting created no interface for that coordination, so each service's interface had to be expanded with integration-specific methods just to keep the system working. Visualized, the resulting web of integrations resembles a textbook distributed big ball of mud: minimal "front doors" but enormous "staff only" entrances. The lesson: optimizing a single service's local complexity while ignoring the system's global complexity (the interactions between services) produces a worse overall system even though each piece looks simpler. The chapter then reframes the earlier bounded-context example (a Lead entity modeled differently in Promotions vs. Sales) to show several valid decompositions into bounded contexts — some wide enough to contain multiple subdomains — none of which are automatically valid microservices, illustrating that bounded contexts bound the *widest* safe monolith, not the microservice itself.

## Key Takeaways
1. A microservice is defined by its public interface being "micro" — not by team size, line count, or rewrite-ability.
2. Judge candidate service boundaries with the deep-module heuristic: small interface, large implementation; a service whose interface must grow to cover integration concerns is a design smell.
3. Optimize both local complexity (within a service) and global complexity (between services) — optimizing only one produces either a monolithic big ball of mud or a distributed big ball of mud.
4. Use subdomains as the default microservice boundary heuristic; reserve bounded contexts for wider, linguistically-consistent monoliths and aggregates for narrower, tightly self-contained services, chosen based on business/organizational/nonfunctional constraints.
5. All microservices are bounded contexts, but not all bounded contexts are microservices — don't use the terms interchangeably.
6. Use Open-Host Service (published language) and Anticorruption Layer to compress a service's effective public interface, making it deeper without changing its underlying implementation.
7. Decomposing past the microservices threshold increases the cost of change again, because shallow services force interfaces to widen for integration — decomposition has diminishing and then negative returns.

## Connects To
- **Ch3**: Bounded Contexts — the widest valid boundary discussed here builds directly on Chapter 3's definition of bounded contexts as protectors of ubiquitous language consistency.
- **Ch4**: Open-Host Service and Anticorruption Layer — the integration patterns used here to compress microservices' public interfaces and make services deeper.
- **Ch6**: Aggregates — the narrowest valid boundary discussed here, including why splitting an aggregate across services causes consistency problems.
- **Ch1**: Analyzing Business Domains — subdomains, the recommended default microservice boundary, are introduced there as fine-grained business capabilities.
- **Ch9**: Communication Patterns — referenced regarding the anticorruption layer's traditional placement within a bounded context versus as a standalone service.
- **Ch11**: Evolving Design Decisions — referenced on the need to continuously adapt architecture as business/organizational context changes.
- **Ch15**: Event-Driven Architecture — the next chapter, continuing the system-architecture discussion via asynchronous integration and event types that further refine microservice boundaries.
- **External**: John Ousterhout's *A Philosophy of Software Design* (deep modules heuristic); Glenford J. Myers's *Composite/Structured Design* (local vs. global complexity); Randy Shoup's "front door" metaphor for service interfaces; Conway's Law (implicit, via team-ownership alignment of microservices and bounded contexts).
