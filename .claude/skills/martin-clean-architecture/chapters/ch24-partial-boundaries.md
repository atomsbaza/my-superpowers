# Chapter 24: Partial Boundaries

## Core Idea
Full architectural boundaries are expensive to build and maintain, so architects can hold a place for a future boundary with cheaper partial implementations — but every partial boundary degrades over time without the discipline a full boundary enforces.

## Frameworks Introduced
- **Skip the Last Step**: build the full boundary (reciprocal interfaces, input/output data structures, all the dependency-management design work) but deploy everything as one component instead of separate independently deployable components.
  - When to use: when you anticipate needing a real boundary later but want to avoid the ongoing cost of multi-component version/release management now.
  - How: do all the architectural design work of a full boundary, just skip splitting into separate compiled/deployed artifacts; accept the risk that, without separate deployability forcing discipline, dependencies can start crossing the line in the wrong direction over time.
- **One-Dimensional Boundaries (Strategy pattern)**: a single interface (`ServiceBoundary`) used by clients and implemented by `ServiceImpl` classes, using dependency inversion in one direction only.
  - When to use: as a lighter-weight placeholder than a full reciprocal boundary, when you want the DIP benefit without full bidirectional isolation.
  - How: define the interface, have the client depend on it, have the implementation depend on/implement it — but recognize there's no reciprocal interface protecting the *other* direction, so backchannel dependencies can form without any structural resistance.
- **Facades**: a boundary defined purely by a `Facade` class listing all services as methods, delegating to classes the client isn't "supposed" to access directly.
  - When to use: the cheapest possible placeholder, when even one-directional dependency inversion isn't justified yet.
  - How: create a Facade class exposing service methods; client calls through it — but note even the dependency inversion is sacrificed, so the client has a transitive compile-time dependency on every service class behind the facade.

## Key Concepts
- **Full-fledged architectural boundary**: reciprocal polymorphic Boundary interfaces + Input/Output data structures + independent compilability/deployability of both sides.
- **Anticipatory design**: deliberately preparing for a boundary that might be needed later, even though YAGNI would argue against it.
- **YAGNI ("You Aren't Going to Need It")**: the Agile-community objection to anticipatory boundary design — Martin acknowledges the tension but argues architects sometimes reasonably judge "I might need it."
- **Backchannel dependency**: an undisciplined dependency that crosses a partial boundary in the wrong direction because no reciprocal interface prevents it.
- **Transitive dependency**: in the Facade approach, the client's compile-time dependency on every class behind the facade, even though it only calls through the Facade's methods.

## Mental Models
- Think of partial boundaries as a spectrum of cost vs. protection: Skip-the-Last-Step (high cost, high protection, just skips deployment separation) → One-Dimensional/Strategy (medium cost, one-directional protection) → Facade (lowest cost, essentially no structural protection).
- Treat a partial boundary as a bet: you're trading the ongoing cost of full component separation for the risk that, without deployability forcing discipline, the boundary silently erodes over time.
- Use FitNesse's own history as a cautionary tale: intentions to keep options open don't prevent erosion — only continued vigilance (or the actual cost of separate deployment) does.

## Anti-patterns
- **Assuming a partial boundary is "free" long-term insurance**: without either full deployability separation or reciprocal interfaces, nothing but developer/architect diligence prevents dependencies from crossing back the wrong way — and that diligence typically erodes.
- **Using a Facade and assuming isolation**: the client still has a compile-time transitive dependency on every service class behind the facade; a change to any service class forces client recompilation in static languages, and backchannels are easy to create since there's no interface at all protecting the boundary.
- **Never revisiting the "will we need this boundary" decision**: FitNesse's web component and wiki/testing component were meant to stay separable, but as it became clear a separate web component would never be needed, the boundary was allowed to decay to the point where re-separating it later would be "something of a chore."

## Reference Tables
| Approach | Reciprocal interfaces? | Independently deployable? | Protects against backchannel? | Relative cost |
|---|---|---|---|---|
| Full architectural boundary | Yes | Yes | Strongly (both directions) | Highest |
| Skip the Last Step | Yes | No (single deployed component) | Fairly well, but erodes without deployment pressure | High (same design cost, lower ops cost) |
| One-Dimensional / Strategy | No (one interface only) | No | Only in one direction | Medium |
| Facade | No | No | Essentially none (transitive dependency remains) | Lowest |

## Worked Example
**FitNesse's web component vs. wiki/testing component**, used as the running example for "Skip the Last Step":
- FitNesse's web server component was architected to be separable from the wiki/testing component, anticipating that the web component might someday power other web-based applications.
- To honor the "download and go" design goal (one jar file, no hunting for compatible versions of multiple jars), the team deployed both components together as a single artifact rather than as two independently versioned/released components — this is exactly the Skip-the-Last-Step pattern: full design-time separation, but shared deployment.
- Over time, since no second application ever emerged that needed the standalone web component, the incentive to maintain the separation weakened. Dependencies began crossing the boundary in the wrong direction.
- Consequence: by the time of writing, re-establishing that separation would require significant rework — illustrating that a partial boundary's protection depends on continued discipline, and that discipline tends to fade once the anticipated need doesn't materialize.

## Key Takeaways
1. Full architectural boundaries (reciprocal interfaces + independent deployability) are expensive — reserve them for boundaries you're confident you need now.
2. When you suspect a boundary might be needed later but aren't sure, consider a partial boundary rather than either paying full cost upfront or building nothing.
3. "Skip the Last Step" gives full design protection at lower operational cost, but only remains effective as long as developers stay disciplined — deployability pressure, which normally enforces the boundary, is absent.
4. One-Dimensional (Strategy) boundaries and Facades trade decreasing cost for decreasing structural protection; a Facade in particular leaves a full transitive compile-time dependency intact.
5. Revisit anticipatory boundaries periodically — if the anticipated need never materializes, either commit to removing the boundary deliberately or accept that it will erode and become costly to reinstate later.
6. Deciding whether/how much to partially implement a boundary is explicitly called out as one of the architect's core judgment calls.

## Connects To
- **Ch 22 (The Clean Architecture)**: partial boundaries are cheaper variants of the same reciprocal-interface/Dependency-Rule-crossing mechanism defined in the full Clean Architecture model.
- **Ch 23 (Presenters and Humble Objects)**: the Humble Object boundaries described there are examples of *full* boundaries; this chapter offers cheaper alternatives when that full cost isn't yet justified.
- **YAGNI (Agile principle)**: explicitly named as the countervailing pressure against anticipatory boundary design that architects must weigh.
- **Strategy and Facade design patterns (Gang of Four)**: reused here as concrete partial-boundary implementation techniques.
