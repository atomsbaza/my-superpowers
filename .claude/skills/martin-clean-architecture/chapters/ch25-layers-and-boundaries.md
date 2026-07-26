# Chapter 25: Layers and Boundaries

## Core Idea
Architectural boundaries exist everywhere a system has an axis of change (not just at the classic UI/business-rules/database split), but each boundary is expensive to build and expensive to retrofit — the architect's job is to watch the system and add boundaries right at the inflection point where implementing costs less than ignoring.

## Frameworks Introduced
- **Streams of data divided by boundaries**: A system's data flow naturally splits into multiple streams (e.g., a UI stream and a persistence stream) that reconverge at the highest-level policy component.
  - When to use: When mapping how many architectural boundaries a system actually needs beyond the obvious three-tier split.
  - How: Trace each axis of change (language, communication mechanism, persistence mechanism, network topology) as its own potential stream; draw an API at each point where a stream's implementation could vary independently.
- **Watch-and-wait boundary strategy**: Don't decide all boundaries up front; observe the system as it evolves, and add a boundary at the first real friction, weighing cost-to-implement vs. cost-to-ignore, reviewed frequently.
  - When to use: Continuously, throughout a system's life — not as a one-time upfront decision.
  - How: Note candidate boundaries as they appear; wait for the first inkling of friction from not having them; then compare implementation cost against continued-ignorance cost before committing.

## Key Concepts
- **Axis of change**: A dimension along which a system component might independently vary (e.g., human language, communication mechanism, data storage technology) — each axis is a candidate architectural boundary.
- **Abstract component / dashed outline**: A component that defines an API implemented by components above or below it in the dependency diagram; the API is owned by the upstream (using) component, not the implementer.
- **Boundary interface**: A polymorphic interface used by one component and implemented by another, crossing an architectural boundary; ownership belongs to the user of the interface, not its implementer.
- **Central Transform**: The historical (structured-design) term for the component where multiple data streams converge and are processed — here, `GameRules`, the highest-level policy.
- **Full-fledged architectural boundary**: A boundary that is completely realized (e.g., via a micro-service API), as opposed to a partial or ignored one.
- **YAGNI ("You aren't going to need it")**: The counter-pressure against pre-building boundaries; overengineering is often worse than under-engineering, but the tension with retrofit cost is the chapter's central dilemma.

## Mental Models
- Think of a system's dependency diagram as always oriented so all arrows point up toward the highest-level policy — this makes the true "top" of the architecture visually obvious regardless of how many streams feed into it.
- Use "does this axis of change actually appear in this system?" as the test for whether a boundary is architecturally significant, not "could this theoretically vary?"
- Think of boundaries as a cost-crossover problem: cost-to-implement (upfront abstraction work) trades off against cost-to-ignore (later retrofit pain), and the correct time to add a boundary is the crossover point, not the start or the point of crisis.
- Streams that meet at the top can also split again deeper in the hierarchy (e.g., `MoveManagement` vs. `PlayerManagement`) — boundary-finding is recursive/fractal, not a single top-level exercise.

## Anti-patterns
- **Assuming only three components (UI/business rules/database) exist**: Most real systems have more axes of change than this simple model admits, and treating it as sufficient hides needed boundaries (e.g., communication mechanism separate from language).
- **Deciding all architectural boundaries once at project start**: Boundary needs emerge as the system evolves; a one-time decision either overbuilds (YAGNI violation) or underbuilds (expensive retrofit) since the future can't be fully predicted upfront.
- **Ignoring friction signals**: Failing to watch for the first signs that a missing boundary is causing pain means the cost of retrofitting only grows — even comprehensive tests and refactoring discipline don't make late boundary-adding cheap.

## Reference Tables
<!-- no comparison/decision table in this chapter -->

## Worked Example
Hunt the Wumpus (a simple text adventure) starts with three components: UI, GameRules, DataStorage. Decoupling human language from GameRules via an API reveals a second axis: the *communication mechanism* (shell window vs. SMS vs. chat) is independent of *language* (English vs. Spanish), so `Language` and `TextDelivery` become separate abstract components, each owned upstream by its user (`GameRules` owns the Language API; `Language` owns the TextDelivery API). This creates two data streams — a UI stream and a persistence stream — meeting at `GameRules`, the Central Transform. Adding networked multiplayer introduces a third stream (`Network`). Going deeper, `GameRules` itself splits into low-level `MoveManagement` (cavern mechanics) and higher-level `PlayerManagement` (health, win/lose state); when `PlayerManagement` is moved to a server as a micro-service consumed by many `MoveManagement` clients, a full-fledged architectural boundary now exists between them — proving boundaries recur fractally, not just at the top level.

## Key Takeaways
1. Don't assume the UI/business-rules/database split is complete — enumerate every axis of change (language, transport, persistence, network) before concluding a boundary isn't needed.
2. Boundary interfaces are owned by the upstream (using) component, not the implementer — this determines which side defines the API.
3. Treat boundary decisions as ongoing, not one-time: watch the system, note friction, and add boundaries at the cost-crossover point.
4. Weigh YAGNI against retrofit cost explicitly — both overengineering and under-engineering are real failure modes, and the right answer depends on the specific system's evolution.
5. Boundaries are fractal — a component that looks monolithic today (like `GameRules`) may itself split into further boundary-separated pieces as requirements grow (e.g., into a micro-service).

## Connects To
- **Ch 26 (The Main Component)**: Main is the component that wires together the boundary-crossing dependencies established here.
- **Ch 27 (Services: Great and Small)**: The micro-service boundary example here (`MoveManagement`/`PlayerManagement`) is the seed for Ch 27's deeper critique of services-as-architecture.
- **Dependency Rule**: All boundary interfaces in this chapter are directed strictly according to the Dependency Rule established earlier in the book.
