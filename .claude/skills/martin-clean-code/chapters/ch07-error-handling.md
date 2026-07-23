# Chapter 7: Error Handling

## Core Idea
Error handling is a necessary concern, but it must be separated from program logic so both can be understood independently — clean code is readable *and* robust, and those goals do not conflict.

## Frameworks Introduced
- **Use Exceptions Rather Than Return Codes**: replace error flags/return codes with thrown exceptions.
  - When to use: any time a method can fail and the old-style approach would force the caller to check a status immediately after the call.
  - How: let the method throw; separate the algorithm (e.g., device shutdown) into its own method and keep the try/catch wrapper thin, so error handling and logic are visually and structurally distinct.
- **Write Your Try-Catch-Finally Statement First**: start writing code that can throw exceptions by writing the try-catch-finally block before the logic inside it.
  - When to use: whenever a method's body will contain code capable of throwing.
  - How: write a test that forces an exception (e.g., accessing a nonexistent file), get it to throw, catch and translate it, narrow the caught type to what's actually thrown, then use TDD to build the logic inside the try, treating the try block like a transaction scope that the catch must leave in a consistent state.
- **Define the Normal Flow / Special Case Pattern [Fowler]**: eliminate special-case handling from the caller by encapsulating the special case inside an object.
  - When to use: when an exception is being used to handle a routine, expected business case (e.g., "no meal expenses recorded") rather than a true error, and it clutters caller logic.
  - How: create or configure a class that returns sensible default behavior for the special case (e.g., a `PerDiemMealExpenses` that returns the per-diem as its total), so the client code no longer branches on the exceptional condition.

## Key Concepts
- **Unchecked exceptions**: exceptions not declared in a method's signature (as in C#, Python, Ruby); Martin/Feathers recommend them over Java's checked exceptions because checked exceptions force signature (`throws`) changes up every calling layer, violating the Open/Closed Principle.
- **Open/Closed Principle violation (checked exceptions)**: a low-level method change that adds a checked exception forces edits to every intermediate method's signature up the call stack, breaking encapsulation.
- **Context in exceptions**: informative error messages — including the operation that failed and the type of failure — attached to each thrown exception, since a stack trace alone doesn't convey intent.
- **Exception classes defined by caller's needs**: exceptions should be classified by how calling code needs to catch and handle them, not by source or failure type; a single exception class is often sufficient for a whole area of code unless different catch behavior is genuinely required.
- **Special Case Pattern**: a Fowler pattern where an object is created/configured to transparently absorb an exceptional case so client code needs no special-case branch.
- **Wrapping third-party APIs**: writing an adapter class that catches a vendor's assorted exceptions and translates them into one application-defined exception type.
- **Don't Return Null**: methods should avoid returning `null`, since it forces null checks everywhere and one missed check risks a `NullPointerException`.
- **Don't Pass Null**: arguments should never be `null` unless an API explicitly expects it; passing null accidentally has no good universal handling strategy, so it should be forbidden by convention.

## Mental Models
- Error handling is a **separate concern** from business logic — if it obscures the logic, it is wrong, no matter how "necessary" it is.
- A `try` block is like a **transaction**: execution can abort at any point inside it, and the `catch`/`finally` must always restore the program to a consistent state.
- Exceptions let you **handle errors at a distance** — the whole value of exceptions over return codes is that the catch site doesn't need to sit right next to the failure site; checked exceptions defeat this by forcing every intermediate layer to know about low-level failure details.
- Returning or passing `null` is not a neutral default — it is **actively creating work** and risk for callers; treat `null` as itself a bug signal, not a valid value to shuttle around.

## Anti-patterns
- **Returning error codes/flags instead of exceptions**: clutters the caller with mandatory, easily-forgotten immediate checks, and mixes error-handling flow with business logic (Listing 7-1).
- **Checked exceptions across multiple call layers**: cascades signature changes from the lowest level of the software to the highest, forcing rebuilds/redeploys of modules that don't actually care about the change; breaks encapsulation.
- **Catching many vendor-specific exception types with duplicated handling**: each catch block does roughly the same recovery work (log + report), so enumerating every third-party exception type is needless duplication — wrap the API instead.
- **Returning null**: forces defensive null checks throughout the codebase; a single missed check produces an uncaught `NullPointerException` with no clear owner for handling it.
- **Passing null into methods**: worse than returning it — there is no good general recovery for an accidentally-passed null; assertions document intent but don't prevent the runtime error.
- **Mixing error handling with normal-case logic**: e.g. catching `MealExpensesNotFound` inline to compute a per-diem — the exception path is really a business rule, not an error, and should be modeled as the Special Case Pattern instead of a try/catch.

## Code Examples
```java
// Before: wrapping a flaky third-party API directly — duplicated, tangled catches
ACMEPort port = new ACMEPort(12);
try {
    port.open();
} catch (DeviceResponseException e) {
    reportPortError(e);
    logger.log("Device response exception", e);
} catch (ATM1212UnlockedException e) {
    reportPortError(e);
    logger.log("Unlock exception", e);
} catch (GMXError e) {
    reportPortError(e);
    logger.log("Device response exception");
} finally {
    …
}

// After: wrapped, single exception type — caller logic simplified
LocalPort port = new LocalPort(12);
try {
    port.open();
} catch (PortDeviceFailure e) {
    reportError(e);
    logger.log(e.getMessage(), e);
} finally {
    …
}
```
- **What it demonstrates**: wrapping a third-party API to translate multiple vendor exception types into one application-defined exception eliminates duplicated catch logic and decouples the caller from the vendor's API design.

## Reference Tables
(omit — none in this chapter)

## Worked Example
The chapter's central worked example is the **ACMEPort wrapping** case. A call site using the raw third-party `ACMEPort` class must catch three distinct exception types (`DeviceResponseException`, `ATM1212UnlockedException`, `GMXError`), each handled almost identically (report the error, log it). This duplication exists because the classification of exceptions was driven by the vendor's internals rather than by how the caller actually needs to respond.

The fix: introduce a `LocalPort` wrapper class around `ACMEPort`. Internally, `LocalPort.open()` catches all three vendor exception types and rethrows a single custom exception, `PortDeviceFailure`. The calling code now only needs one catch clause. Benefits beyond the immediate simplification: the application depends on a self-defined API instead of the vendor's, making it easy to swap libraries later, easy to mock in tests, and free from being tied to the vendor's exception design decisions. Martin generalizes this: define exception classes by how the caller needs to catch them, and use one exception class per area of code unless there's a genuine reason to let one exception type pass through while catching another.

## Key Takeaways
1. Throw exceptions instead of returning error codes/flags — it separates the failure-handling concern from the algorithm and removes the risk of a forgotten check.
2. Write the try-catch-finally block first when writing code that can throw; it defines the transaction scope and consistent-state guarantee before you fill in the logic, and pairs naturally with TDD (write a test that forces the exception first).
3. Prefer unchecked exceptions in application code; checked exceptions couple every layer of the call stack to low-level implementation details and violate the Open/Closed Principle.
4. Always attach context (operation attempted, failure type) to thrown exceptions — a stack trace alone doesn't explain intent.
5. Design exception classes around how callers need to catch them, not around the failure's source; wrap third-party APIs to collapse multiple vendor exceptions into one type you control.
6. Use the Special Case Pattern to eliminate exception handling for cases that are really normal business flow, not errors.
7. Never return or pass `null`: return empty collections or Special Case objects instead, and treat passing `null` as forbidden by default — there is no universally correct way to recover from it.

## Connects To
- **Ch 3 (Functions)**: functions should do one thing — error handling logic mixed into a function violates that; extracting try/catch into its own method (as in `sendShutDown`/`tryToShutDown`) is a direct application of Ch 3's extraction guidance.
- **Ch 6 (Objects and Data Structures)**: the Special Case Pattern and null-object substitution rely on polymorphism over conditionals, echoing Ch 6's preference for objects that hide implementation behind behavior.
- **Ch 8 (Boundaries)**: wrapping third-party APIs (ACMEPort → LocalPort) is the same technique Ch 8 recommends for isolating your codebase from external library changes.
- **Ch 9 (Unit Tests)**: the try-catch-first workflow is explicitly TDD-driven — write a test expecting the exception, watch it fail, then implement.
- **External concept — Open/Closed Principle**: cited directly to explain why checked exceptions are costly; a change at a low level forces modification of unrelated higher-level signatures.
- **External concept — Special Case Pattern [Fowler]**: attributed to Martin Fowler's *Refactoring*/pattern catalog; used verbatim as the mechanism for eliminating null/exception-driven special-casing.
