# Chapter 6: Objects and Data Structures

## Core Idea
Objects hide their data behind abstractions and expose behavior; data structures expose their data and have no meaningful behavior. This is a deliberate asymmetry, not an oversight — each shape trades off which kind of change (new data types vs. new behaviors) is easy and which is hard.

## Frameworks Introduced
- **Data/Object Anti-Symmetry**: Objects hide data behind abstractions and expose functions that operate on that data; data structures expose data and have no meaningful functions. They are virtual opposites.
  - When to use: choose objects when the system needs the flexibility to add new data types (new classes) without disturbing existing behavior; choose data structures + procedures when the system needs the flexibility to add new behaviors (new functions) without disturbing existing data types.
  - How: for objects, add a new class implementing a shared interface and existing functions are untouched; for data structures, add a new function operating on the structures and existing structures are untouched. Adding the "wrong" kind of new thing forces changes everywhere (new shape in the OO design touches nothing; new shape in the procedural design touches every function; conversely a new function in OO touches every class).
- **Law of Demeter**: A method `f` of a class `C` should only call methods on: `C` itself, an object created by `f`, an object passed as an argument to `f`, or an object held in an instance variable of `C`. It should not call methods on objects returned by any of those calls. "Talk to friends, not to strangers."
  - When to use: whenever a module manipulates objects (not plain data structures) — the rule exists specifically to keep an object's internal structure hidden.
  - How: replace chained navigation (`a.getB().getC().getD()`) with a single delegating method the outer object provides (e.g., `ctxt.createScratchFileStream(name)`) so the object is told what to do rather than asked to reveal its internals.

## Key Concepts
- **Data abstraction**: exposing the essence/meaning of data through an interface, without exposing its underlying representation (e.g., `getPercentFuelRemaining()` vs. `getGallonsOfGasoline()`).
- **Access policy**: an object's interface can enforce rules about how data may be read or written (e.g., polar coordinates must be set atomically as a pair, not one field at a time).
- **Law of Demeter**: heuristic that a module should not know about the innards of the objects it manipulates.
- **Train wreck**: a chain of method calls (`ctxt.getOptions().getScratchDir().getAbsolutePath()`) that looks like coupled train cars and is generally sloppy style, though it's a real Demeter violation only if the intermediate objects are objects (not data structures).
- **Hybrid structure**: a class that is half object, half data structure — has significant behavior functions plus public variables/accessors that expose its internals — combining the worst of both worlds.
- **Data Transfer Object (DTO)**: a class with public variables and no functions, the quintessential data structure, often used as a translation stage between raw data (database rows, socket messages) and application objects.
- **Bean**: a DTO variant with private variables and public getters/setters; gives an illusion of encapsulation without the actual benefits objects provide.
- **Active Record**: a special DTO with public/bean-accessed variables plus navigational methods like `save` and `find`, typically a direct translation of a database table.
- **Feature Envy**: (referenced from Fowler's Refactoring) the smell where a hybrid's business logic reaches into another object's data rather than that object exposing behavior.

## Mental Models
- Objects and data structures are complementary opposites: what is easy in one paradigm is hard in the other, and vice versa — there is no free lunch, only a choice of which axis of change you're optimizing for.
- "The idea that everything is an object is a myth" — mature engineers deliberately pick data structures + procedures for parts of the system where new functions (not new types) are the expected axis of change.
- Whether a chain of calls violates Demeter depends entirely on whether the things in the chain are objects (hide structure, violation) or plain data structures (naturally expose structure, no violation) — the same-looking code can be fine or bad depending on this distinction.
- When an object is asked for data just so the caller can act on it, the better design is to tell the object what to do (push behavior in) rather than ask it for internals (pull data out) — this is the "tell, don't ask" instinct underlying Demeter.

## Anti-patterns
- **Blithely adding getters/setters**: exposes private variables as if public and defeats the purpose of hiding implementation; serious thought should instead go into what abstraction the data represents.
- **Train wrecks**: long navigation chains like `ctxt.getOptions().getScratchDir().getAbsolutePath()` are sloppy and, when the traversed objects are true objects, a Law of Demeter violation because the caller ends up knowing the internal object graph.
- **Hybrid structures**: classes with both meaningful behavior and exposed public data — they make it hard to add new functions (behavior must stay consistent) *and* hard to add new data structures (data is entangled with logic), the worst of both worlds; usually a sign the author didn't decide whether the type needs protection from functions or from types.
- **Putting business rules in Active Records**: turns a data structure into a hybrid; the fix is to keep the Active Record as a pure data structure and put business rules in a separate object that wraps/hides it.
- **Admixture of different levels of detail**: mixing low-level string/path manipulation (dots, slashes, extensions) with higher-level object calls in the same block of code, obscuring intent.

## Code Examples
```java
// Listing 6-2 Abstract Point (interface hides representation & enforces atomic set)
public interface Point {
    double getX();
    double getY();
    void setCartesian(double x, double y);
    double getR();
    double getTheta();
    void setPolar(double r, double theta);
}
```
- **What it demonstrates**: a well-designed object interface expresses the essence of the data (a point) and an access policy (atomic polar set) without revealing whether the underlying storage is rectangular, polar, or something else.

```java
// Train wreck vs. Demeter-respecting delegation
final String outputDir = ctxt.getOptions().getScratchDir().getAbsolutePath(); // train wreck

// split up (still arguably knows too much if these are objects)
Options opts = ctxt.getOptions();
File scratchDir = opts.getScratchDir();
final String outputDir = scratchDir.getAbsolutePath();

// tell, don't ask — respects Demeter if ctxt is a true object
BufferedOutputStream bos = ctxt.createScratchFileStream(classFileName);
```
- **What it demonstrates**: fixing a train wreck isn't just about splitting lines — the real fix is asking why the caller needed that value and pushing the behavior (creating the scratch file stream) into the object that owns the data.

## Reference Tables
| | Add new data type (class) | Add new function |
|---|---|---|
| **Procedural code (data structures + functions)** | Hard — every function must change | Easy — existing data structures untouched |
| **OO code (objects + polymorphism)** | Easy — existing functions untouched | Hard — every class must change |

## Worked Example
The chapter walks through the Square/Rectangle/Circle example twice.

**Procedural version (Listing 6-5)**: `Square`, `Rectangle`, `Circle` are plain data structures (public fields, no behavior). A separate `Geometry` class has an `area(Object shape)` method that does `instanceof` checks and casts to compute area for each shape type. Adding a new function, e.g. `perimeter()`, is trivial — add one more method to `Geometry`; none of the shape classes or their dependents change. But adding a new shape (e.g., `Triangle`) requires editing every method in `Geometry` (`area`, `perimeter`, etc.) to add a new branch.

**OO version (Listing 6-6)**: Each shape class (`Square`, `Rectangle`, `Circle`) implements a `Shape` interface with its own polymorphic `area()` method; no `Geometry` class is needed. Adding a new shape (e.g., `Triangle implements Shape`) requires no changes to existing classes — just a new class. But adding a new function (e.g., `perimeter()`) requires editing every existing shape class to add the new method (a footnote notes VISITOR/dual-dispatch can work around this but reintroduces procedural-style costs).

This pair demonstrates the anti-symmetry concretely: the OO design and the procedural design have exactly inverted strengths and weaknesses, and neither is universally "more correct" — the right choice depends on which axis of change (new types vs. new operations) the system is expected to undergo more often.

## Key Takeaways
1. Decide deliberately whether a given part of your system needs to be easy to extend with new types (favor objects/polymorphism) or easy to extend with new operations (favor data structures + procedures) — don't default to objects everywhere.
2. Don't reflexively add getters/setters; design interfaces around the abstraction the data represents (e.g., percent fuel remaining, not gallons and tank capacity).
3. Apply the Law of Demeter to true objects: a method should only talk to itself, its arguments, objects it creates, and its own instance variables — not to objects returned by those.
4. Long navigation chains ("train wrecks") are a design smell; fix them by asking what the caller actually wanted to *do*, and push that behavior into the object instead of pulling data out.
5. Never build hybrids — a class that is both a heavily-behaviored object and a publicly-exposed data bag combines the worst of both worlds and signals unclear design intent.
6. DTOs and beans are legitimate and useful, especially at translation boundaries (database rows, socket messages) — but keep them pure data, with no embedded business rules.
7. Active Records should stay pure data structures with navigational methods (`save`, `find`); put business logic in separate objects that wrap and hide them.

## Connects To
- **Ch 9: Unit Tests**: DTOs and simple data structures used in tests should stay free of hidden behavior, mirroring the "don't build hybrids" guidance here.
- **Ch 10: Classes**: this chapter's data/object distinction underlies class design decisions about cohesion, encapsulation, and what belongs behind an interface versus what is legitimately exposed data.
- **Ch 17: Smells and Heuristics**: G36 (Law of Demeter violations / train wrecks) and G34/G6 (mixed levels of abstraction) are the heuristics catalog entries this chapter's examples are drawn from.
- **Refactoring (Fowler)**: Feature Envy, cited directly as the smell underlying hybrid structures where external functions reach into an object's data instead of the object exposing behavior.
- **GoF Design Patterns**: VISITOR and double-dispatch are mentioned as ways to work around the "OO makes new functions hard" limitation, at the cost of reintroducing procedural structure.
