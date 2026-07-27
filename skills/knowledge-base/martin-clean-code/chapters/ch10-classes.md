# Chapter 10: Classes

## Core Idea
Clean code isn't finished at the function level — classes must also be small, single-purposed, and organized to minimize the risk and cost of future change. Size is measured in responsibilities, not lines, and classes should depend on abstractions so that concrete details can change without rippling outward.

## Frameworks Introduced
- **Single Responsibility Principle (SRP)**: A class or module should have one, and only one, reason to change.
  - When to use: Any time a class accumulates methods or private helpers that serve unrelated concerns (e.g., version tracking mixed with GUI management).
  - How: Identify each distinct "reason to change" the class has; extract each into its own class named for that responsibility. A class doing too much can often be spotted because you can't describe it in ~25 words without "and," "or," "but," "if."
- **Open-Closed Principle (OCP)**: Classes should be open for extension but closed for modification.
  - When to use: When a class is expected to grow new variants of behavior over time (e.g., new SQL statement types).
  - How: Define an abstract base with a single abstract operation; put each variant behavior in its own subclass. Adding a new variant means adding a new subclass, not editing existing ones.
- **Dependency Inversion Principle (DIP)**: Classes should depend upon abstractions, not on concrete details.
  - When to use: When a class depends on a volatile, external, or hard-to-test concrete implementation (an API, a database, an external service).
  - How: Extract an interface representing the abstract capability needed; have the concrete class implement it; inject the interface into the dependent class's constructor rather than instantiating the concrete class directly.

## Key Concepts
- **Class size by responsibility**: Unlike functions (measured in lines), classes are measured by how many responsibilities/reasons-to-change they hold, not method or line count.
- **God class**: A class (like `SuperDashboard` with ~70 public methods) that has accreted far too many unrelated responsibilities.
- **Class organization order**: Public static constants first, then private static variables, then private instance variables, then public functions, with private utility functions placed immediately after the public function that calls them (the stepdown rule) so the class reads top-to-bottom like a newspaper article.
- **Encapsulation as default, not dogma**: Keep variables and utilities private by default; loosen to protected/package-scope only as a last resort, typically to let a test in the same package access something.
- **Cohesion**: A measure of how many of a class's methods use how many of its instance variables; a maximally cohesive class has every method touching every variable.
- **Loss of cohesion as a splitting signal**: When only a subset of methods use a subset of instance variables, a class is trying to hide another class inside it — split it out.
- **Isolating from change**: Depending on interfaces/abstract classes instead of concrete implementations shields client code from the volatility of those implementation details, and makes the code testable via stand-in implementations.
- **Organizing for change**: SRP and OCP work together — SRP gives many small, focused classes; OCP structures them (via abstraction/subclassing) so that adding a new capability means adding new code, not editing tested code.

## Mental Models
- **Toolbox with many small labeled drawers vs. a few drawers you toss everything into**: many small, well-named classes carry no more total complexity than a few large ones, but they let you find and load only what's relevant right now.
- **"How small?" for classes = "how few reasons to change?"**, not "how few lines/methods?" — a five-method class can still be too big if those methods serve two unrelated purposes.
- **A class name test**: if you cannot give the class a concise, unambiguous name (and words like "Processor," "Manager," "Super" are red flags), it's probably absorbing more than one responsibility.
- **Opening a class = risk**: every time you must modify an existing, working, tested class to add a feature, you risk breaking it and must re-test it fully; the goal of good class design is to need to do this as rarely as possible.

## Anti-patterns
- **God classes**: Classes exposing dozens of unrelated public methods (e.g., `SuperDashboard`) — they violate SRP so thoroughly that no concise description is possible; every change to any part of the class risks affecting all the others.
- **Weasel-word class names**: Names containing "Manager," "Processor," "Super," etc. usually signal an unfortunate aggregation of responsibilities rather than a genuine, cohesive concept.
- **Low cohesion from variable proliferation**: Promoting local variables to instance variables just to avoid passing arguments during function extraction quietly destroys cohesion — the class accumulates state that only a few methods actually use.
- **Depending directly on concrete/volatile classes**: A class like `Portfolio` depending directly on `TokyoStockExchange` couples business logic to an external, non-deterministic system and makes deterministic testing (and future substitution) hard.

## Code Examples
```java
// Isolating from change via DIP: an interface breaks the dependency
// on a concrete, volatile external system.
public interface StockExchange {
    Money currentPrice(String symbol);
}

public class Portfolio {
    private StockExchange exchange;
    public Portfolio(StockExchange exchange) {
        this.exchange = exchange;
    }
    // ...
}

// Test uses a fixed stub instead of the real TokyoStockExchange
public class PortfolioTest {
    private FixedStockExchangeStub exchange;
    private Portfolio portfolio;

    @Before
    protected void setUp() throws Exception {
        exchange = new FixedStockExchangeStub();
        exchange.fix("MSFT", 100);
        portfolio = new Portfolio(exchange);
    }

    @Test
    public void GivenFiveMSFTTotalShouldBe500() throws Exception {
        portfolio.add(5, "MSFT");
        Assert.assertEquals(500, portfolio.value());
    }
}
```
- **What it demonstrates**: DIP applied via constructor injection of an interface, which simultaneously isolates the class from external volatility and makes it deterministically testable.

## Reference Tables
(omit)

## Worked Example
The `Sql` class generates SQL strings and currently supports `create`, `insert`, `selectAll`, `findByKey`, `select` (two overloads), and `preparedInsert`, with several private helpers (`columnList`, `valuesList`, `selectWithCriteria`, `placeholderList`). It violates SRP for two independent reasons to change: (1) adding a new statement type (e.g., `update`), and (2) altering details of an existing statement type (e.g., adding subselect support to `select`). A clue is visible in the method outline itself: private methods like `selectWithCriteria` clearly relate only to `select`, not to the class as a whole.

The refactor (Listing 10-10) makes `Sql` an abstract base class with a constructor and a single abstract `generate()` method. Each former public method becomes its own subclass: `CreateSql`, `SelectSql`, `InsertSql`, `SelectWithCriteriaSql`, `SelectWithMatchSql`, `FindByKeySql`, `PreparedInsertSql` — each implementing `generate()` and owning only the private helpers it actually needs (e.g., `valuesList` moves into `InsertSql`). Shared private behavior common across statement types is factored into two small utility classes, `Where` and `ColumnList`.

Result: each class becomes small and "excruciatingly simple," comprehension time per class drops to nearly nothing, one function can no longer break an unrelated one, and each class is trivially testable in isolation. Critically, adding update-statement support later requires only a new `UpdateSql` subclass — none of the existing, already-tested classes need to change. This simultaneously satisfies SRP (each class has one reason to change) and OCP (the family is open to new statement types via subclassing, closed to modification of existing ones).

## Key Takeaways
1. Measure class size by counting responsibilities (reasons to change), not lines or method count — a small class can still violate SRP.
2. If you can't name a class concisely, or can't describe it in ~25 words without "and/or/but/if," it likely has too many responsibilities.
3. Favor many small, cohesive classes over a few large ones — total system complexity doesn't shrink, but comprehension load per task does.
4. When instance variables are used by only a subset of methods, that's a signal a hidden class wants to split out — do it to restore cohesion.
5. Apply SRP and OCP together: separate responsibilities into classes, then structure variant behavior (e.g., via an abstract base + subclasses) so new features are added by extension, not modification.
6. Use DIP — depend on interfaces/abstractions, not concrete implementations — especially for external, volatile, or slow dependencies, so client code stays testable and change-resistant.
7. Loosening encapsulation (protected/package-scope) is acceptable only as a last resort, typically to support testing, and only after other options are exhausted.

## Connects To
- **Ch 3 (Functions)**: The same "small is the primary rule" philosophy applied to functions carries directly into class design; extracting small functions is often what triggers the discovery of hidden classes.
- **Ch 9 (Unit Tests)**: DIP-based isolation (the `StockExchange`/`Portfolio` example) exists specifically to make classes testable without depending on volatile, real external systems.
- **Ch 11 (Systems)**: Organizing classes for change and isolating them via abstractions scales up into the system-level concern of separating construction from use and managing cross-cutting complexity.
- **Ch 17 (Smells and Heuristics)**: Several heuristics there (e.g., "Base classes depending on derivatives," excessive class coupling) directly formalize the SRP/OCP/DIP violations discussed in this chapter.
- **SOLID**: This chapter is effectively a hands-on tour of three of the five SOLID principles (SRP, OCP, DIP), grounding them in concrete refactoring examples (`SuperDashboard`, `Sql`, `Portfolio`).
