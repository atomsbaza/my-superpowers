# Chapter 15: What Is Architecture?

## Core Idea
The purpose of software architecture is to leave as many options open as possible for as long as possible, by shaping a system so that policy (business rules, where the true value lives) is decoupled from details (frameworks, databases, UI, servers — decisions that don't affect the policy's behavior).

## Frameworks Introduced
- **Policy vs. Details decomposition**: every software system decomposes into policy (business rules/procedures — the true value) and details (IO devices, databases, web frameworks, servers, protocols — necessary for communication but irrelevant to policy behavior).
  - When to use: continuously, as a lens for every architectural decision.
  - How: architect the system so the policy has zero knowledge of and zero dependency on the details, which allows detail decisions (database choice, web framework, REST vs. RPC, DI framework) to be delayed until you have maximum information, or avoided/reversed entirely.
- **"A good architect maximizes the number of decisions not made"**: an explicit operating principle — even when a decision (e.g., a mandated database) has already been made by someone else, architect as if it hadn't been, keeping the system able to defer or change that decision later.

## Key Concepts
- **Architecture**: "the shape given to a system by those who build it" — the division into components, their arrangement, and how they communicate.
- **Software architect**: remains a programmer; guides the team toward a design maximizing productivity but must keep experiencing the problems programmers face, not retreat to pure diagramming.
- **Two types of software value**: behavior (what it does now) and structure (how easy it is to change) — structure is the greater value because it's what makes software "soft."
- **Four life-cycle concerns architecture must support**: development, deployment, operation, maintenance.
- **Spelunking**: the cost of digging through existing code to find where/how to add a feature or fix a defect — the dominant cost driver in maintenance, mitigated by clear component separation and stable interfaces.
- **Device independence**: a historical example (1960s IO abstraction) of decoupling policy from a specific detail (which physical device is attached) via an OS-level abstraction layer — an early, unnamed instance of the Open-Closed Principle.
- **"Architecture should reveal operation"**: use cases, features, and required behaviors should be first-class, visible landmarks in the architecture, not buried — this aids both understanding and maintenance even though architecture's direct influence on runtime behavior is limited.

## Mental Models
- Think of architecture's role in *operation* as largely solvable by throwing hardware at the problem (cheap), whereas architecture's role in *development/deployment/maintenance* is solved only by good structure (expensive to fix later, since people are expensive) — so weight architectural effort accordingly.
- Use "would a small team vs. a five-team org produce this same structure?" as a check on whether your component boundaries are driven by Conway's-law team dynamics rather than genuine architectural need — component-per-team is a common but not necessarily optimal outcome.
- When evaluating any early technical commitment (database engine, web framework, DI container, REST vs. SOA), ask "does the high-level policy need to know this yet?" — if not, defer it structurally, even if organizationally the decision seems already locked in.

## Anti-patterns
- **Choosing frameworks/databases/web servers early "because you'll need them eventually"**: prematurely couples policy to details, closing off options and increasing cost of change later (illustrated by the microservice-deployment story where easy development led to unmanageable deployment).
- **Believing architecture's job is to make the system "work"**: many badly-architected systems work fine operationally — their pain shows up in deployment, maintenance, and ongoing development instead, not runtime correctness.
- **Binding code directly to a specific IO device or physical storage layout**: the PDP-8 teleprinter and truckers-union disk-cylinder/head/sector examples show how hard-wiring physical/device details throughout business logic makes even simple upgrades (new disk drive, new output medium) require rewriting large amounts of code.
- **Assuming architects should stop programming**: "never fall for the lie" — architects who don't code lose contact with the problems they're creating for the team.

## Code Examples
No executable code samples (one PDP-8 assembly snippet referenced but not reproduced in extracted text — described conceptually: a `PRTCHR` subroutine polling a teleprinter-ready flag via `TSF`/`JMP .-1` before writing a character via `TLS`).
- **What it demonstrates**: device-dependent code — the routine is hard-wired to teleprinter-specific IO instructions, illustrating the "device dependence" anti-pattern the chapter uses to motivate device independence.

## Reference Tables
No comparison/decision tables in this chapter.

## Worked Example
**Junk mail (late 1960s):** the author's employer printed personalized form letters from client-supplied magnetic tapes. Programs were written against OS-level unit-record IO abstractions rather than a specific physical device. Initially all printing went to a single expensive IBM 360 line printer (slow, tied up costly hardware). Because the programs only knew about the abstract IO interface, the same code could later be redirected to write to magnetic tape instead — those tapes were then run on five independent offline printers 24/7, multiplying throughput without touching a single line of the printing logic. The architecture's shape (policy = record formatting, detail = output device) meant the device decision was deferred and later changed with zero impact on business logic — a concrete precursor to the Open-Closed Principle.

**Physical addressing (early 1970s):** an accounting system hard-wired disk cylinder/head/sector numbers throughout the business logic and its indices (for Agents, Employers, Members). Upgrading to a new disk drive geometry would have required rewriting a special data-migration program AND finding/changing every hard-coded physical address reference scattered through the code. A more experienced colleague recommended relative (linear) addressing with a single translation routine mapping relative address → physical cylinder/head/sector, isolating the physical disk geometry as a "detail" the business logic no longer needed to know.

## Key Takeaways
1. Architecture's central purpose is to defer and minimize irreversible decisions about details — not to guarantee correct behavior, which it influences only marginally.
2. Separate policy (business rules, the actual value) from details (frameworks, DBs, UI, IO, protocols) so decisions about the latter can be delayed until maximum information is available.
3. Treat "the decision has already been made" as a trap — architect as if it hadn't been, so the system stays changeable even under externally imposed constraints.
4. Weight your architectural investment toward development, deployment, and maintenance — operational problems are comparatively cheap to fix with more hardware.
5. Make the system's use cases and behaviors visible landmarks in its structure ("architecture should reveal operation") to reduce spelunking cost during maintenance.
6. Component-per-team structures often emerge from Conway's-law pressure, not genuine architectural necessity — recognize the difference.

## Connects To
- **Ch 16 (Independence)**: directly continues this chapter's four concerns (use cases/operation, development, deployment, maintenance) into concrete decoupling strategies.
- **OCP (Open-Closed Principle)**: the device-independence story is presented as OCP "born, but not yet named."
- **Ch 21 "Screaming Architecture"**: referenced as the chapter that elaborates on making use cases visible at the architectural level.
- **Conway's Law**: implicitly invoked when discussing how team structure drives component decomposition.
