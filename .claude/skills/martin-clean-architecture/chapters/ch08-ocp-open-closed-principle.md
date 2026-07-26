# Chapter 8: OCP: The Open-Closed Principle

## Core Idea
A well-architected system lets you extend behavior by adding new code rather than modifying existing code, achieved by separating things that change for different reasons (SRP) and directing dependencies (DIP) so higher-level policy is protected from changes in lower-level detail.

## Frameworks Introduced
- **Open-Closed Principle (OCP)**: Coined by Bertrand Meyer (1988): "A software artifact should be open for extension but closed for modification." I.e., behavior should be extendable without modifying the artifact itself.
  - When to use: Any time new requirements are anticipated to extend (not replace) existing behavior — new output formats, new business rules variants, new delivery channels.
  - How: Apply SRP to separate what changes for different reasons; then arrange dependencies (via interfaces) so that lower-level, volatile components depend on higher-level, stable components — never the reverse.
- **Directional Control / Dependency Hierarchy**: "If component A should be protected from changes in component B, then component B should depend on component A." Components are arranged into a hierarchy of protection based on level; the highest-level policy component (e.g., business rules) is the most protected.

## Key Concepts
- **Level**: A measure of a component's distance from system inputs/outputs; higher-level components encapsulate broader business policy and should be protected from lower-level (peripheral) components.
- **Interactor**: In the worked example, the component holding the central business rules/highest-level policy — the most protected component because nothing else should force it to change.
- **Unidirectional component relationships**: Dependencies between components must all point one way — toward the components being protected — forming a directed (non-cyclic) hierarchy.
- **Information hiding (at the architecture level)**: Using an interface (e.g., a "Requester" interface) so a peripheral component doesn't gain transitive dependencies on the internals of a component it calls.
- **Transitive dependency**: An indirect dependency incurred by depending on something that itself depends on internals you don't use — a violation of "don't depend on things you don't directly use."

## Mental Models
- Think of OCP at the architecture level as a castle with concentric walls: business rules (Interactor) sit in the innermost keep, protected by walls (interfaces) from Controllers, Presenters, and Views, which are progressively more peripheral and more exposed to change.
- Use "arrow direction = protection direction" as the test when drawing a component diagram: an arrow from B to A means A is protected from B, not the reverse.
- Ask "how much old code changes when I add this new feature?" as the OCP health check — ideally the answer is zero for high-level policy components.

## Anti-patterns
- **Modifying existing components to add a variant (e.g., adding a printer report by editing the web-report code)**: Forces re-testing and re-deployment of code unrelated to the new feature and risks regressions in stable, high-level logic.
- **Bidirectional or cyclic component dependencies**: If a "protected" component ends up depending back on the thing it should be shielded from, changes in the peripheral component ripple into the core — defeating OCP.
- **Skipping the boundary interface for convenience**: Letting a Controller call the Interactor's concrete internals directly creates transitive dependencies on business-entity internals, coupling peripheral and central concerns.

## Code Examples
<!-- omit — chapter is diagram-based (Figures 8.1–8.3), no source code -->

## Reference Tables
<!-- no comparison/decision table in this chapter -->

## Worked Example
**Scenario**: A system displays a scrollable financial summary on a web page (negatives in red). Stakeholders then request a paginated, black-and-white printer report with headers/footers/column labels and negatives in parentheses.

**Design response**:
1. Apply SRP: separate the *calculation* of reportable data (an analysis procedure) from its *presentation* (two separate reporter processes — web and print).
2. Partition into components along the double-line boundaries in Figure 8.2: **Controller** (upper left), **Interactor** (upper right, holds business rules), **Database** (lower right), and **Presenters/Views** (lower left, one pair per output format).
3. Direct all source-code dependencies inward and unidirectionally: `FinancialDataMapper` implements `FinancialDataGateway`, so the Interactor's gateway interface is known to the Database layer, not vice versa (dependency inversion applied to protect the Interactor from Database changes).
4. Add a `FinancialReportRequester` interface between Controller and Interactor purely for information hiding — so the Controller doesn't transitively depend on `FinancialEntities` internals.

**Result**: Adding the printer report requires writing new Presenter/View components; the Interactor (business rules) and Controller need zero modification — the system is open for extension, closed for modification.

## Key Takeaways
1. OCP is the reason software architecture matters: a good architecture makes extension cheap without touching stable code.
2. Achieve OCP by combining SRP (separate what changes for different reasons) with DIP (point dependencies at abstractions, toward what you want to protect).
3. Draw component dependency arrows deliberately — the direction encodes what is protected from what.
4. Business-rule-holding components (Interactors) should sit at the top of the protection hierarchy; UI/delivery-mechanism components (Views) sit at the bottom, least protected.
5. Use boundary interfaces even between "physically adjacent" components (e.g., Controller→Interactor) to prevent transitive/information-hiding leaks, not just to invert obviously "risky" dependencies like the Database.

## Connects To
- **Ch 7 (SRP)**: OCP's component partitioning starts from an SRP-driven separation of responsibilities (calculation vs. presentation).
- **Ch 11 (DIP)**: The interface-based dependency inversion used to protect the Interactor from the Database is DIP applied at the architecture level.
- **Ch 10 (ISP)**: The "don't depend on things you don't directly use" principle behind the `FinancialReportRequester` interface is explicitly the same idea the ISP chapter develops further.
