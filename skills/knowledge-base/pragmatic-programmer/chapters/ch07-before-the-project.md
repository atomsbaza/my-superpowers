# Chapter 7: Before the Project

## Core Idea
Projects can be doomed before a line of code is written if requirements aren't dug for rather than merely gathered, if impossible-seeming constraints aren't correctly identified, if starting is rushed past a legitimate gut-level "not ready" signal, if specifications are over-engineered into a security blanket, or if a formal methodology is followed as a substitute for thinking rather than a tool for it.

## Frameworks Introduced
- **Digging for Requirements**: requirements are buried under assumptions, misconceptions, and politics — they must be excavated, not passively collected.
  - When to use: at the very start of any project, and continuously as understanding deepens.
  - How: separate the requirement (the general, invariant need) from policy (which changes) and from implementation/UI detail; document policy separately and hyperlink it to the requirement so it can become metadata later; discover the underlying reason users do something, not just their current method; become a user yourself (sit with the help desk, work the warehouse) to build both insight and trust.
- **Cockburn's Use Case Template**: a structured, goal-driven document format for capturing a requirement scenario at an appropriate level of abstraction.
  - When to use: when documenting requirements for a wide, mixed audience (developers, sponsors, end users).
  - How: capture Characteristic Information (goal, scope, level, pre/post-conditions, primary actor, trigger), a Main Success Scenario, Extensions, Variations, Related Information (priority, performance target, frequency, secondary actors), Schedule, and Open Issues; nest use cases hierarchically (e.g., "post debit" and "post credit" elaborate "post transaction").
- **Specification by Example / avoiding the Specification Trap**: recognize that natural language and formal notations can never capture every nuance, and that overly detailed specifications rob implementation of the skill and insight that only emerges during coding.
  - When to use: whenever a team is tempted to treat spec-writing as a substitute for, rather than a facet of, implementation.
  - How: treat requirements gathering, design, and implementation as facets of one continuous process with feedback flowing both ways; use prototyping or tracer bullet development to break out of an over-specified stall; reserve exhaustive detail for contractually or safety-critical needs (life-critical systems, published interfaces/libraries).
- **Solving Impossible Puzzles (finding "the box")**: distinguish absolute constraints (must be honored) from merely preconceived ones (assumed, but not actually binding), and locate your true degrees of freedom.
  - When to use: whenever a problem in requirements, analysis, coding, or testing seems intractable.
  - How: enumerate every possible avenue, however implausible, then prove — don't assume — why each one is or isn't blocked; categorize and prioritize constraints, tackling the most restrictive first; ask "Is there an easier way? Am I solving the right problem? Does it have to be done this way? Does it have to be done at all?"

## Key Concepts
- **Requirement vs. policy vs. implementation**: a requirement states a general need ("only authorized users may access an employee record"); policy is the changeable specific rule underneath it; implementation is how the code satisfies both — conflating them hardwires change into the code.
- **Project glossary**: a single, widely accessible place defining the specific vocabulary used by users and developers, preventing the same word meaning different things to different people (or different words meaning the same thing).
- **Requirements creep / feature bloat**: a special case of the boiled-frog syndrome — scope grows unnoticed unless requirements changes are actively tracked (who requested, who approved, cumulative count).
- **Absolute constraint vs. preconceived notion**: only the former must be honored; much of "impossible" difficulty comes from treating an assumption as if it were a hard rule.
- **Prototyping as a diagnostic for procrastination vs. genuine unease**: if a prototype quickly feels like wasted motion, the original hesitation was probably just reluctance to start; if it reveals a wrong premise, the hesitation was well-founded instinct.
- **Circles and Arrows (formal methods skepticism)**: no notation, diagram, or methodology substitutes for understanding the whole system — specialization by artifact (data modelers vs. architects vs. use-case gatherers) tends to produce poor communication and an "us vs. them" culture.
- **Y2K as a DRY/foresight failure**: the two-digit year bug wasn't a memory-saving trick gone wrong so much as a failure to abstract DATE as its own concept — "seeing further" means writing requirements general enough to anticipate this kind of abstraction, not predicting the future.

## Mental Models
- Use the Gordian Knot as the model for reinterpreting requirements: Alexander didn't solve the puzzle as stated, he changed the frame — "does it have to be done this way?" is often the real question.
- Think of overspecification as a security blanket: the longer a team hides behind a spec instead of building, the harder it becomes to ever start coding — break out via prototyping or tracer bullets.
- Treat "the box" (in "thinking outside the box") as something to be *found*, not assumed — the real constraint boundary is often larger than first believed.
- Treat formal methodologies as tools in a toolbox to be selected and blended, never as masters to which the team defers unquestioningly ("circles and arrows make poor masters").

## Anti-patterns
- **Stating policy as if it were a hard requirement**: "Only personnel can view an employee record" leads a developer to hard-code an explicit test; "Only authorized users may access an employee record" leads them to build an access-control system that survives policy changes.
- **Two-inch-thick, never-read requirements binders**: static, print-bound requirements documents go stale the instant they're printed and are rarely consulted; web-based, hyperlinked, layered documentation serves a mixed audience and stays current.
- **Treating "the class diagram is the application, the rest is mechanical coding"** as a philosophy: a sign of a waterlogged project that has mistaken the notation for the understanding.
- **Letting specifications become infinitely detailed**: a design that leaves the coder no room for interpretation removes the skill and insight that only surfaces during implementation, and risks specifying something that turns out to be unbuildable.
- **Adopting a use-case or diagramming notation just because it's standard**: if stick-figure use case diagrams (or any notation) don't actually communicate with your specific audience, the notation is failing regardless of its popularity.

## Code Examples
No code examples in this chapter.
- **What it demonstrates**: Chapter 7 is entirely about the requirements/pre-project phase — analysis, documentation, and process, not implementation.

## Reference Tables
| Cockburn use case template section | Contents |
|---|---|
| A. Characteristic Information | Goal in context, scope, level, preconditions, success/failed end conditions, primary actor, trigger |
| B. Main Success Scenario | Numbered steps of the ideal path |
| C. Extensions | Alternate branches off specific steps |
| D. Variations | Alternate channels/mechanisms for a step |
| E. Related Information | Priority, performance target, frequency, super/subordinate use cases, actors, channels |
| F. Schedule | Due date / release target |
| G. Open Issues | Unresolved questions |

## Worked Example
The "Buy Goods" use case (Figure 7.2) walks Cockburn's template end-to-end: the goal is that a buyer requests goods directly from the company and expects to be billed; preconditions assume the buyer and address are already known; the main success scenario runs from the buyer calling in a purchase request through the company shipping the invoice and the buyer paying it; extensions cover the company being out of stock (renegotiate the order) or the buyer paying by credit card (a subordinate use case); variations note that the order may come by phone, fax, web form, or EDI, and payment may be cash, check, money order, or credit card; related information records the priority (top), performance target (5 minutes to place the order, 45 days until paid), frequency (200/day), and secondary actors (credit card company, bank, shipping service); and open issues flag unresolved questions like partial orders or stolen cards. The example shows concretely how a template forces you to surface nonfunctional requirements, exceptions, and stakeholders that a narrative paragraph would silently omit — and how subordinate use cases ("Take payment by credit card," "Handle returned goods") let a large requirements set nest cleanly instead of sprawling.

## Key Takeaways
1. Separate requirement from policy from implementation in every requirements statement you write down — policy belongs in metadata, not in the requirement itself.
2. Become a user of the system you're building, even briefly — you'll uncover requirements no interview would surface.
3. Maintain a single project glossary and get everyone — users, developers, support — to use it consistently.
4. Track requirements growth explicitly so "just one more feature" is visible as the fifteenth feature added this month, not an isolated request.
5. When a problem seems impossible, separate absolute constraints from merely assumed ones before concluding it can't be solved.
6. Trust a nagging "not ready" feeling; use a time-boxed prototype to tell whether it's genuine insight or ordinary fear of starting.
7. Treat specification, design, and implementation as one continuous, feedback-driven process — never let specification become a substitute for building.
8. Use formal methodologies selectively and critically; never let "the diagram is the application" become the team's operating philosophy.

## Connects To
- **Ch 3 (Tracer Bullets, Prototypes and Post-it Notes)**: the antidotes recommended here for both the Specification Trap and "Not Until You're Ready" procrastination-vs-instinct problem.
- **Ch 1 (Stone Soup and Boiled Frogs)**: requirements creep is explicitly named as an instance of the boiled-frog syndrome.
- **Ch 8 (Great Expectations)**: requirements-pit rapport-building with users is called out as feeding directly into managing user expectations later in the project.
- **Ch 5 (Metaprogramming)**: the recommendation to keep policy as metadata ties requirements analysis directly to the dynamic-configuration techniques from Chapter 5.
