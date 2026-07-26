# Chapter 9: LSP: The Liskov Substitution Principle

## Core Idea
The Liskov Substitution Principle, originally a guide for inheritance, generalizes into an architectural principle: any set of interchangeable interface implementations (classes, services, or REST APIs) must be truly substitutable, or the architecture is forced to accumulate special-case mechanisms to compensate.

## Frameworks Introduced
- **Liskov Substitution Principle (LSP)**: Barbara Liskov, 1988 (SIGPLAN Notices 23(5)): "What is wanted here is something like the following substitution property: If for each object o1 of type S there is an object o2 of type T such that for all programs P defined in terms of T, the behavior of P is unchanged when o1 is substituted for o2, then S is a subtype of T."
  - When to use: Whenever designing subtypes/inheritance, interface implementations, polymorphic classes with shared method signatures, or a set of services conforming to the same REST contract.
  - How: Verify that any consumer of the supertype/interface can use any substitutable implementation with zero behavioral change or special-casing; if the consumer needs an `if` to distinguish implementations, LSP is violated.

## Key Concepts
- **Subtype (Liskov sense)**: A type S is a true subtype of T only if objects of S can replace objects of T in any program without altering that program's observable behavior.
- **Substitutability**: The property that any implementation of an interface/contract can be swapped for another without the consumer needing to know or care.
- **Square/Rectangle problem**: The canonical LSP violation — `Square` is not a proper subtype of `Rectangle` because `Rectangle`'s width and height vary independently while `Square`'s must vary together, breaking a `User`'s assumptions.
- **LSP at the architecture level**: Extends beyond class inheritance to any interchangeable interface implementations — Java-style interfaces, duck-typed Ruby classes with shared method signatures, or REST services sharing a contract.
- **Special-case mechanism**: Extra code (if-statements, configuration lookups) an architect is forced to add when substitutability breaks, polluting the architecture with mechanism that wouldn't otherwise be needed.

## Mental Models
- Use "does the consumer need an `if` to tell implementations apart?" as the direct test for LSP violation — any such branch is evidence the types aren't truly substitutable.
- Think of LSP violations as a tax that compounds architecturally: one non-conforming implementation (Acme's `dest` instead of `destination`) forces a permanent detection-and-compensation mechanism (a configuration-driven dispatch-format table) rather than a one-time fix.
- Treat REST/service contracts the same way you'd treat a Java interface — LSP is about behavioral substitutability of any interface, not just OO inheritance hierarchies.

## Anti-patterns
- **Overriding a method in a way that violates the base type's implied contract**: E.g., `Square.setW()` also changing height — breaks calling code (like `Billing` or `User`) that assumes independent mutation, because the subtype isn't behaviorally substitutable even though it type-checks.
- **Adding type-detection `if` statements in consumer code**: A direct symptom that the "polymorphic" types aren't actually substitutable, defeating the purpose of the shared interface.
- **Letting one implementation deviate from a shared contract "just this once" (e.g., a partner's API using `dest` instead of `destination`)**: Forces the whole system to carry a permanent special-case/config mechanism rather than a clean interface, and each future deviation compounds the mechanism's complexity.

## Code Examples
```
Rectangle r = … 
r.setW(5); 
r.setH(2);
assert(r.area() == 10);
```
- **What it demonstrates**: If `…` actually constructs a `Square`, the assertion fails — proving `Square` cannot be silently substituted for `Rectangle` despite being a subclass, i.e., the canonical LSP violation.

```
if (driver.getDispatchUri().startsWith("acme.com")) …
```
- **What it demonstrates**: The "quick fix" special-case an architect is tempted to add when one REST service implementation (Acme) deviates from the shared dispatch contract — exactly the kind of mechanism LSP violations force into an architecture.

## Reference Tables
| URI | Dispatch Format |
|---|---|
| Acme.com | `/pickupAddress/%s/pickupTime/%s/dest/%s` |
| `*.*` (default) | `/pickupAddress/%s/pickupTime/%s/destination/%s` |

(The proper architectural fix for the Acme LSP violation: replace the hardcoded `if` with a configuration-driven dispatch-format lookup keyed by URI, isolating the deviation instead of hardcoding vendor names into business logic.)

## Worked Example
A taxi aggregator dispatches drivers via a shared REST contract: `PUT /driver/{name}/pickupAddress/{addr}/pickupTime/{time}/destination/{dest}`. All taxi companies' dispatch services are expected to be substitutable implementations of this contract. Acme Taxi's engineers implement `dest` instead of `destination`, breaking substitutability. The naive fix — hardcoding `if (uri.startsWith("acme.com")) …` — embeds a vendor name in business logic, inviting bugs when Acme later merges with Purple Taxi (requiring yet another hardcoded branch). The architecturally sound fix externalizes the deviation into a configuration table mapping URI → dispatch format string, so the dispatch-command-construction module stays generic and new non-conforming vendors are handled by data, not code changes.

## Key Takeaways
1. LSP is not just an OOP inheritance rule — apply it to any set of interchangeable implementations: interfaces, duck-typed classes, or REST services.
2. If consumer code needs a conditional to special-case one implementation, that's a live LSP violation, not just a code smell.
3. Don't "fix" an LSP violation with a hardcoded special case (e.g., a vendor name in an `if`) — isolate the deviation in configuration/data to prevent architectural pollution from compounding.
4. When designing shared contracts (REST APIs, interfaces), the contract itself is the substitutability guarantee — deviations by any implementer force system-wide compensating mechanisms.
5. The Square/Rectangle example generalizes: a subtype must preserve behavioral invariants the supertype's consumers rely on, not just type-check as compatible.

## Connects To
- **Ch 8 (OCP)**: Substitutable implementations are what make OCP's "add new implementations without modifying consumers" possible; LSP violations directly undermine OCP.
- **Ch 11 (DIP)**: Both principles rely on stable, well-defined abstractions/interfaces that implementations must faithfully honor.
- **REST API contract design**: LSP's architectural extension is directly relevant to designing/versioning service contracts across independently-deployed teams or vendors.
