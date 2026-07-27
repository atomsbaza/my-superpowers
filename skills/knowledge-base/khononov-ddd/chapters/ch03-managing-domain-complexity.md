# Chapter 3: Managing Domain Complexity

## Core Idea
A ubiquitous language cannot be consistent across an entire organization because domain experts in different departments hold genuinely conflicting mental models of the same terms; DDD resolves this by splitting the language into multiple smaller, explicitly scoped languages, each valid only within its bounded context.

## Frameworks Introduced
- **Bounded Context**: the explicit boundary within which a particular model and its ubiquitous language are defined and consistent; outside that boundary, the same term can carry a different meaning.
  - When to use: whenever domain experts from different parts of the business use the same word to mean different things (e.g., "lead" in marketing vs. sales), or whenever a model is growing large enough that filtering, finding, and maintaining consistency in it becomes its own source of complexity.
  - How: divide the ubiquitous language into multiple smaller languages and assign each one to an explicit context of applicability; do not try to build one model that serves everyone, and do not just prefix conflicting terms (e.g., "marketing lead"/"sales lead") since that adds cognitive load without matching how people actually talk.

## Key Concepts
- **Inconsistent models**: different domain experts (e.g., marketing vs. sales) can hold genuinely conflicting mental models of the same business entity, and forcing them into one shared model over- or under-engineers the solution for one side.
- **Model boundaries**: a model has no inherent size limit and will expand toward becoming a copy of the real world unless an explicit boundary — its bounded context — constrains its purpose.
- **Scope of a bounded context**: the widest a bounded context can be is set by where the ubiquitous language stays consistent; from there it can be narrowed further, but narrower boundaries trade internal simplicity for more integration overhead between contexts.
- **Bounded contexts vs. subdomains**: subdomains are discovered through business-domain analysis (they reflect how the business already works); bounded contexts are designed as a strategic software decision (they reflect how the team chooses to model the solution).
- **Physical boundaries**: each bounded context should be implemented as its own service/project, evolved and versioned independently, and free to use whatever technology stack fits it best.
- **Ownership boundaries**: a bounded context is implemented and maintained by exactly one team, though a single team may own multiple bounded contexts; this removes implicit cross-team assumptions and forces explicit integration contracts.
- **Semantic domains**: a lexicographic concept — an area of meaning and the words used within it — that bounded contexts are grounded in; the same word (e.g., "tomato") can correctly mean different things in different semantic domains (botany, culinary arts, taxation law).

## Mental Models
- A ubiquitous language is not truly "ubiquitous" across an organization — it is ubiquitous only within the boundary of its bounded context; outside that boundary it may not apply or may mean something else entirely.
- Maps as models, extended: a subway map is useless for nautical navigation not because one map is wrong, but because each is scoped to a specific purpose — the same holds for models of a business domain across different bounded contexts.
- "All models are wrong, but some are useful" — a model's fidelity to reality is irrelevant; what matters is whether it solves the specific problem it was built for, and using multiple narrow models can beat one broad, more "accurate" one.
- Subdomains are discovered, bounded contexts are designed: this single distinction reframes bounded-context decisions as strategic engineering choices, not facts to be uncovered from the business.

## Anti-patterns
- **One giant enterprise-wide model (mega-ERD)**: attempting a single model to serve every department's needs becomes "effective for nothing" — it forces constant complexity in filtering irrelevant details, finding what's needed, and keeping a sprawling structure internally consistent.
- **Prefixing conflicting terms instead of separating contexts (e.g., "marketing lead" / "sales lead")**: technically distinguishes the models but induces cognitive load about which to use when, and doesn't match how people actually speak — no one uses the prefixes in real conversation, so the code drifts from the ubiquitous language.
- **Splitting one coherent functionality across multiple bounded contexts**: prevents each piece from evolving independently, since the same business change now has to be coordinated and deployed simultaneously across contexts — apply the Chapter 1 rule of thumb (coherent use cases operating on the same data) to avoid this.
- **Forcing a strict one-to-one mapping between bounded contexts and subdomains as a rule**: sometimes appropriate, but treating it as mandatory removes the flexibility to use multiple models of the same subdomain for different problems, or to combine several subdomains into one bounded context.

## Code Examples
(omit — not code-heavy)

## Reference Tables
| Dimension | Subdomain | Bounded Context |
|---|---|---|
| Origin | Discovered — reflects how the business already operates | Designed — a strategic software engineering decision |
| Defined by | Business strategy and use cases | Engineering team, based on project context and constraints |
| Nature | A set of interrelated use cases operating on the same data | A boundary of model consistency, physical deployment, and team ownership |
| Who controls it | The business (marketing, sales, etc.) | The software engineering team |
| Relationship to the other | One or more bounded contexts can map to a subdomain | A bounded context can span multiple subdomains, or align 1:1 with one |
| Can it change independently? | Changes with business strategy | Changes with technical/organizational needs (team splits, scaling, tech stack) |
| Boundary type | Conceptual/business boundary | Physical (service/deployment) and ownership (team) boundary |

## Worked Example
A telemarketing company's marketing department treats a "lead" as a single event — a notification that someone showed interest. Its sales department treats "lead" as an entire long-running sales process with many states. Forcing one shared model either drags sales' complexity into marketing (overengineering) or flattens sales' process into marketing's simplistic event (underengineering). The DDD fix: split the ubiquitous language into a marketing bounded context and a sales bounded context, each with its own consistent meaning of "lead." Neither model is "more correct" — each is scoped to solve its own department's problem.

The "buying a refrigerator" example reinforces the same point outside software: to check whether a refrigerator would fit through a kitchen doorway, a piece of cardboard cut to the fridge's width and depth (not its color, doors, or shape) served as a perfectly sufficient model for the width/depth problem, and a tape measure served as a separate, equally sufficient model for the height problem. Building a full 3D replica would have been gross overengineering — neither model needed to resemble the real fridge; each only needed to solve its one bounded problem.

## Key Takeaways
1. When domain experts genuinely disagree on a term's meaning, don't force consensus — split the ubiquitous language into separate bounded contexts, one per meaning.
2. A model without an explicit boundary will keep expanding toward an unusable copy of reality; always define what problem the model exists to solve.
3. Never conflate subdomains (discovered from the business) with bounded contexts (designed by engineering) — they answer different questions and don't have to map 1:1.
4. Size a bounded context by usefulness, not by a rule: too wide risks inconsistency, too narrow multiplies integration overhead.
5. Keep coherent use cases operating on the same data inside a single bounded context; splitting them apart forces coordinated, simultaneous deployments across contexts.
6. Treat bounded contexts as both physical boundaries (independently deployable services) and ownership boundaries (exactly one team per context, though a team may own several contexts).
7. Look for bounded contexts everywhere, not just in software — semantic domains (botany vs. culinary vs. tax law definitions of "tomato") show the same pattern of context-dependent meaning in everyday life.

## Connects To
- **Ch 1**: Analyzing Business Domains — establishes subdomains (core/supporting/generic) and the "coherent use cases on the same data" rule of thumb this chapter reuses to avoid splitting functionality across bounded contexts.
- **Ch 4**: Integrating Bounded Contexts — the natural next step once contexts are decomposed: how independently evolving bounded contexts communicate without cascading changes.
- **Ch 8**: Architectural Patterns — revisits continuously optimizing bounded context boundaries.
- **Ch 10**: Design Heuristics — also revisits bounded context boundary optimization over time.
- **Ch 14**: Microservices — physical and ownership boundaries of bounded contexts map closely onto microservice boundaries and team-per-service ownership models.
- **Ubiquitous language (Ch 2)**: this chapter completes its definition — a ubiquitous language is only "ubiquitous" within its bounded context, not across the whole organization.
- **Semantic domains (lexicography)**: external concept underpinning bounded contexts — an area of meaning and the words used to talk about it.
