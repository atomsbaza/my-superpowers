# Chapter 1: Analyzing Business Domains

## Core Idea
Before designing software you must understand the business it serves: DDD gives you a vocabulary — business domain, subdomain, and three subdomain types (core, generic, supporting) — for analyzing where a company's competitive advantage lives and where it doesn't, so engineering effort and rigor can be allocated accordingly.

## Frameworks Introduced
- **The Three Subdomain Types**: Every business domain decomposes into subdomains, and every subdomain is one of three strategic types — core, generic, or supporting.
  - When to use: Whenever starting analysis of a new project or business area, before making any architecture or design-effort decisions.
  - How: For each candidate subdomain, ask (1) does it provide competitive advantage? (2) how complex is its business logic? (3) how often does it change? The answers classify it as core, generic, or supporting and dictate implementation strategy.
- **Distilling Subdomains**: Coarse-grained organizational units (departments) are a starting point, but must be decomposed into finer-grained subdomains to reveal their true strategic mix.
  - When to use: When a department or business function looks like a single subdomain but actually bundles multiple types (e.g., a "customer service department" hiding a generic help-desk tool, a supporting shift-scheduling function, and a core incident-routing algorithm).
  - How: Drill into a business function's inner workings until you reach "coherent use cases" — sets of use cases sharing the same actor and closely related data. Distill core subdomains aggressively (they are the most important); relax distillation for generic/supporting subdomains once further drilling reveals no new design-relevant insight.
- **The Complexity/Differentiation Test**: A practical heuristic to disambiguate subdomain types when the classification is unclear.
  - When to use: When it's hard to tell core from supporting, or supporting from generic.
  - How: Core vs. supporting — "Could this be spun off as a side business? Would someone pay for it alone?" If yes, it's core. Supporting vs. generic — "Would it be simpler/cheaper to build your own vs. integrate an existing solution?" If cheaper to build, it's supporting; if an off-the-shelf solution is more cost-effective, it's generic.

## Key Concepts
- **Business domain**: A company's main area of activity — the service it provides to its clients (e.g., FedEx = courier delivery). A company can operate across multiple business domains (Amazon: retail + cloud computing).
- **Subdomain**: A fine-grained area of business activity; all of a company's subdomains together form its business domain. No single subdomain alone makes a company succeed.
- **Core subdomain**: What a company does differently from competitors — its source of competitive advantage; complex, in-house, and constantly evolving.
- **Generic subdomain**: A business activity all companies perform the same way, using widely available battle-tested solutions (e.g., authentication, encryption); complex but not differentiating.
- **Supporting subdomain**: A necessary but non-differentiating activity with simple, CRUD/ETL-like business logic and low entry barriers.
- **Competitive advantage**: The strategic edge a company gains over rivals; only core subdomains provide it.
- **Domain expert**: A subject-matter authority who understands the intricacies of the business being modeled — the source, not the transcriber, of business knowledge (distinct from analysts and engineers).
- **Coherent use cases**: The technical signature of a subdomain — a tightly related set of use cases sharing the same actor and manipulating closely related data; the natural stopping point for distillation.
- **Core domain (synonym caution)**: Eric Evans's original term, used interchangeably with "core subdomain"; the author prefers "core subdomain" to avoid confusion with "business domain" and because subdomains can change type over time (see Chapter 11).

## Mental Models
- Think of subdomains as **building blocks of a structure**: remove any one (core, generic, or supporting) and the whole business can fail, even though only core subdomains carry competitive weight.
- Use the **known-unknowns framing** for generic subdomains: you know you don't know how to solve them optimally, but the knowledge to solve them is readily available externally (buy or adopt).
- Think of core subdomain complexity as a **deliberate moat**: if a problem is easy to solve, competitors solve it too, so genuine competitive advantage is inherently hard to build and never "done."
- Use the **side-business test** as a lightweight classifier during any domain conversation: "would someone pay for just this piece?" is a fast proxy for "is this core?"

## Anti-patterns
- **Treating department boundaries as subdomain boundaries**: Organizational units are coarse-grained and often mix subdomain types; stopping analysis there hides core subdomains inside seemingly generic departments (e.g., an ingenious incident-routing algorithm buried inside "customer service").
- **Over-investing engineering rigor in supporting/generic subdomains**: Applying elaborate design patterns or your most skilled engineers to CRUD screens or authentication wastes the scarce resource (deep technical talent and design effort) that core subdomains need.
- **Building core subdomains with off-the-shelf or outsourced solutions**: Buying or outsourcing a core subdomain hands your competitive advantage to anyone else who buys the same product — it undermines the entire point of a core subdomain.
- **Assuming non-technical competitive advantages don't matter for software design**: A core subdomain (e.g., jewelry design) may have nothing to do with code; the mistake is polishing the surrounding generic software (the online shop) while treating the true differentiator as out of scope.
- **Infinite drill-down**: Distilling supporting/generic subdomains indefinitely wastes analysis effort once further granularity stops revealing design-relevant information.

## Code Examples
(omit — this chapter is business-strategy content, not code)

## Reference Tables
| Subdomain Type | Competitive Advantage | Complexity | Volatility | Implementation Strategy | Problem Nature | Examples |
|---|---|---|---|---|---|---|
| Core | Yes | High | High — constantly evolving | In-house, best engineers, advanced techniques | Interesting | Uber's ride-matching optimization, Google Search ranking algorithm, jewelry design, incident-routing algorithm |
| Generic | No | High | Low (changes via patches/new solutions, not business need) | Buy / adopt off-the-shelf or open source | Solved | Authentication, encryption, accounting, traffic-condition data feeds |
| Supporting | No | Low (CRUD/ETL, data entry) | Low | In-house (no ready-made option) or outsource | Obvious | Content/creative cataloging, promotions & discount management, attended-gigs logging module |

Gray area: when a generic solution exists for what looks like a supporting subdomain, the classification depends on whether integrating it is simpler/cheaper than building it in-house.

## Worked Example
**Gigmaster** (ticket sales & distribution, mobile app recommending nearby shows from users' music/streaming/social data):
- Business domain: ticket sales.
- Core: recommendation engine, data anonymization (privacy is a differentiator here), mobile app UX.
- Generic: encryption, accounting, clearing, authentication/authorization.
- Supporting: streaming-service integration, social-network integration, attended-gigs module.
- Design decisions: build core in-house with top engineers; buy/adopt generic pieces; outsource the supporting integrations.

**BusVNext** (public transportation / on-demand bus rides):
- Business domain: public transportation.
- Core: routing algorithm (a "travelling salesman"-style problem, continuously re-tuned — e.g., prioritizing fast pickups over shorter total ride length after data showed wait time drove cancellations), ride/behavior analysis, mobile app UX, fleet management.
- Generic: third-party traffic-condition data, accounting, billing, authorization.
- Supporting: promotions/discount management (simple CRUD over coupon codes).
- Design decisions: build routing, analysis, fleet management, and app usability in-house with the most advanced tools; outsource promotions management; offload traffic data, authorization, and financial processing to external providers.

Both examples show the same pattern: identify the business domain, list plausible subdomains from both explicit and implicit requirements, classify each by competitive advantage / complexity / volatility, then let the classification directly drive build-vs-buy-vs-outsource decisions.

## Key Takeaways
1. Understanding the business (its domain and subdomains) is a prerequisite for sound software design, not a detour from it.
2. Classify every subdomain you touch as core, generic, or supporting — the classification directly determines implementation strategy: build in-house with top talent (core), buy/adopt (generic), or build cheaply/outsource (supporting).
3. Core subdomains are inherently complex and volatile by design — simple, static competitive advantages get copied fast, so treat "it's easy" as a warning sign, not a relief.
4. Don't stop at department-level analysis; distill down to coherent use cases to uncover hidden core subdomains buried inside apparently generic or supporting business functions.
5. A core subdomain need not be technical (e.g., jewelry design) — identify the true source of competitive advantage even when it lives outside the software you're building.
6. Use the side-business test (core vs. supporting) and the build-vs-integrate cost test (supporting vs. generic) as fast, practical disambiguators when classification is unclear.
7. Domain experts are the business's knowledge source, not the analysts or engineers who translate that knowledge into software — identify and engage them directly.

## Connects To
- **Ch 2 (Discovering Domain Knowledge)**: how to actually extract domain expert knowledge once subdomains and experts are identified here.
- **Ch 3 (Managing Domain Complexity)**: builds directly on core-subdomain complexity to introduce bounded contexts as the tool for managing it.
- **Ch 11 (Evolving Design Decisions)**: revisits subdomain classification as a moving target — core subdomains can decay into generic/supporting and vice versa over a company's lifecycle.
- **Ch 13 (Domain-Driven Design in the Real World) / Ch 17 (Appendix A case study)**: applies this chapter's classification framework to a full real-world scenario.
- **Eric Evans's "Blue Book"**: origin of the "core domain" term that this chapter deliberately renames "core subdomain" for terminological clarity.
- **Competitive strategy (business literature)**: the core/generic/supporting split is DDD's software-facing translation of classic build-vs-buy and competitive-moat strategic thinking.
