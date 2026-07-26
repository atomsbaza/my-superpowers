# Chapter 13: Component Cohesion

## Core Idea
Deciding which classes belong in which component is governed by three competing principles of cohesion — REP and CCP pull components larger (inclusive), CRP pulls them smaller (exclusive) — and a good architect deliberately balances that tension rather than resolving it once and for all.

## Frameworks Introduced
- **REP (Reuse/Release Equivalence Principle)**: "The granule of reuse is the granule of release."
  - When to use: whenever you group classes/modules into a component intended for reuse by others.
  - How: only group classes that share a cohesive theme and that can be tracked, versioned, and released together with shared release documentation. Components without a shared theme "don't make sense" to users and signal poor architecture.
- **CCP (Common Closure Principle)**: "Gather into components those classes that change for the same reasons and at the same times. Separate into different components those classes that change at different times and for different reasons."
  - When to use: for most applications, where maintainability outweighs reusability.
  - How: group classes that are tightly bound (physically or conceptually) so a single requirement change is confined to as few components as possible, minimizing revalidation/redeployment of unrelated components. This is the SRP applied at the component level, and it is "closure" in the OCP sense — components should be closed to the most common types of change.
- **CRP (Common Reuse Principle)**: "Don't force users of a component to depend on things they don't need."
  - When to use: when deciding what NOT to keep together in a component.
  - How: only put classes together that are actually reused together (tightly coupled, e.g. a container and its iterators). If a using component depends on even one class of a used component, it depends on the whole component — so components must be composed so classes are effectively inseparable in use.

## Key Concepts
- **Component**: a unit of release, deployment, and reuse — the granule the REP, CCP, CRP govern.
- **Granule of release**: the level at which software is versioned and given release notes; must equal the granule of reuse per REP.
- **Closure (OCP sense)**: since 100% closure to change is unattainable, closure must be strategic — design classes/components to be closed against the most likely kinds of change.
- **Tension diagram**: a triangle showing the trade-offs between REP, CCP, and CRP; the edges represent the cost of ignoring the principle at the opposite vertex.
- **Develop-ability vs. reusability**: the core forces in tension — CCP/REP favor ease of development, CRP favors minimal, precise reuse dependencies.

## Mental Models
- Think of REP as the packaging discipline that makes reuse *possible* (via versioning), CCP as the packaging discipline that makes development *efficient* (via minimizing change scope), and CRP as the packaging discipline that makes dependency *safe* (via avoiding unnecessary coupling).
- Use the tension triangle when a component "feels wrong": if too many unrelated components must redeploy on a small change, you're over-weighting REP/CRP at the expense of CCP; if you're generating too many needless releases, you're over-weighting CCP/REP at the expense of CRP.
- Early in a project's life, favor CCP over REP — develop-ability matters more than reuse. As a project matures and other projects/teams start consuming it, slide toward REP/CRP.

## Anti-patterns
- **Hodgepodge components**: grouping unrelated classes into one component with no shared theme — violates REP; users notice immediately because the grouping "doesn't make sense."
- **Spreading a single reason-to-change across many components**: violates CCP; forces unnecessary multi-component redeployment and revalidation for one logical change.
- **Depending on a component for one class you need while dragging in classes you don't**: violates CRP; forces recompilation/redeployment on changes you don't care about, wasting effort.
- **Treating cohesion as "does one thing"**: the old, oversimplified view of cohesion (one function per module) is inadequate for components — real component cohesion is a balance of three competing forces, not a single attribute.

## Worked Example
A container class and its associated iterator classes are a canonical CRP example: they are always used together and tightly coupled, so they belong in the same component. If you split them into separate components, any user of the container is forced to also depend on (and redeploy for) whatever else lives in the iterator's component and vice versa — exactly the coupling CRP warns against. Conversely, per CCP, if that container's serialization logic changes for a completely unrelated reason (e.g., a persistence-format change unrelated to iteration behavior), that logic likely belongs in a separate component so a change to serialization doesn't force redeployment of everything depending on iteration.

## Key Takeaways
1. Component boundaries are not fixed forever — they should jitter and evolve as a project matures from prioritizing develop-ability (CCP) toward prioritizing reuse (REP/CRP).
2. Use CCP as your primary grouping heuristic during active development: co-locate classes that change together for the same reasons.
3. Use CRP to *split* components: never let users of a component be forced to depend on classes they don't actually use.
4. REP is necessary but "weak" advice on its own — it only becomes actionable when combined with CCP and CRP.
5. Violations of REP are easy to detect (components stop "making sense" to users); violations of CCP/CRP show up as excessive redeployment or over-broad dependencies.

## Connects To
- **Ch 14**: Component Coupling builds directly on cohesion — once you know what goes inside a component, ADP/SDP/SAP govern how components depend on each other.
- **SRP (Single Responsibility Principle)**: CCP is explicitly the SRP restated at the component level.
- **OCP (Open Closed Principle)**: CCP is the OCP's notion of "closure" applied to component grouping.
- **ISP (Interface Segregation Principle)**: CRP is explicitly the generic, component-level version of ISP ("don't depend on things you don't need").
