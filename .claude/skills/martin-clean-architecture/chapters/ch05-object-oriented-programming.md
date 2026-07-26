# Chapter 5: Object-Oriented Programming

## Core Idea
OO's real architectural value is not encapsulation, inheritance, or polymorphism as buzzwords — it's that safe, convenient polymorphism gives the architect absolute control to invert any source code dependency, enabling plugin architectures where high-level policy no longer depends on low-level detail.

## Frameworks Introduced
- **Dependency Inversion via Polymorphism**: Source code dependencies can be pointed opposite to the flow of control by inserting an interface between caller and callee.
  - When to use: Whenever you want a high-level module (business rules) to be independent of a low-level module (UI, database, IO) that it calls.
  - How: Have the low-level module implement an interface owned/called by the high-level module; the high-level module depends only on the interface, and the low-level implementation depends on (inherits/implements) that interface — flipping the source-code dependency arrow relative to runtime call flow.
- **OO Definition for Architects**: "OO is the ability, through the use of polymorphism, to gain absolute control over every source code dependency in the system."
  - When to use: As the working definition of OO's value when designing component boundaries, rather than debating encapsulation/inheritance/polymorphism as OO's essence.
  - How: Identify every source-code dependency in the calling tree; for any dependency you want independently deployable/developable, insert an interface to invert it.

## Key Concepts
- **Encapsulation (debunked as OO-exclusive)**: Perfect encapsulation existed in plain C via header/implementation file splits; C++ actually *weakened* it by requiring member variables in the header.
- **Inheritance (debunked as OO-exclusive)**: C programmers achieved a manual form of inheritance by ordering struct fields identically and casting pointers (e.g., `NamedPoint` masquerading as `Point`); OO made this convenient, not new.
- **Polymorphism (debunked as OO-exclusive)**: Achievable pre-OO via explicit function pointers (e.g., UNIX's `FILE` struct with `open/close/read/write/seek` pointers powering `getchar()`/`putchar()`); OO made this *safe and convenient* by eliminating manual pointer-management conventions.
- **Plugin architecture**: A module (e.g., an IO device driver) can be swapped without recompiling or changing the caller, because the caller depends only on an interface/contract, not on the plugin's source.
- **Independent deployability**: Components with inverted dependencies (e.g., business rules not depending on UI/DB) can be compiled and deployed as separate units (jars, DLLs, Gems) without redeploying the whole system.
- **Independent developability**: A direct consequence of independent deployability — separately deployable modules can be developed by separate teams without coordination overhead.

## Mental Models
- Use the **"award points" audit**: when evaluating what OO actually contributes, check whether a claimed OO feature (encapsulation, inheritance, polymorphism) was truly unavailable before OO, or just made safer/more convenient — this discipline prevents cargo-culting OO buzzwords into architecture decisions.
- Think of the **calling tree vs. dependency graph** as two separate diagrams that, pre-polymorphism, were forced to align; OO's power is decoupling them so the architect chooses the dependency direction independently of the call direction.
- Treat **business rules as the architectural center**, with UI and database as plugins to it — not the reverse — as the default arrangement to aim for.

## Anti-patterns
- **Defining OO by encapsulation/inheritance/polymorphism buzzwords**: Each of these existed (in weaker or manual form) pre-OO; this definition misses OO's actual architectural payload (dependency inversion) and can justify sloppy component boundaries under the guise of "using OO features."
- **Letting source-code dependencies default to following flow of control**: Without deliberately inverting dependencies via interfaces, high-level policy ends up depending on low-level detail (e.g., business rules depending on the database), making the policy layer un-independently-deployable and fragile to detail changes.
- **Treating C++'s header-required member variables as encapsulation**: Clients still see (and are compiled against) member names even though access is `private` — a compiler-enforced illusion, not true encapsulation; renaming a member forces recompilation of clients.

## Code Examples
```c
/* point.h — perfect encapsulation in plain C */
struct Point;
struct Point* makePoint(double x, double y);
double distance(struct Point *p1, struct Point *p2);
```
- **What it demonstrates**: C's header/implementation split gives clients zero visibility into `struct Point`'s internals — stronger encapsulation than C++ provides, despite C having no OO features.

```c
/* UNIX-style polymorphism via a function-pointer table, pre-dating OO languages */
struct FILE {
  void (*open)(char* name, int mode);
  void (*close)();
  int  (*read)();
  void (*write)(char);
  void (*seek)(long index, int mode);
};

extern struct FILE* STDIN;
int getchar() { return STDIN->read(); }
```
- **What it demonstrates**: `getchar()` is polymorphic — its behavior depends on which device's `read` function pointer `STDIN` points to — the same mechanism OO vtables use, just manual and dangerous instead of compiler-enforced.

## Worked Example
The UNIX `copy` program (`while ((c=getchar()) != EOF) putchar(c);`) reads from `STDIN` and writes to `STDOUT` without knowing which physical device is on either end. This works because every UNIX IO driver implements the same five-function contract (`open, close, read, write, seek`), and `getchar()`/`putchar()` simply call through function pointers stored in a `FILE` struct. Consequence: adding a brand-new IO device (e.g., a handwriting-recognition input, a speech-synthesizer output) requires zero changes and zero recompilation of `copy` — the new devices just need to implement the standard `FILE` function set, making them plugins. Martin then generalizes this: in a typical calling tree, `main` → high-level → mid-level → low-level functions, and pre-polymorphism, source dependencies (`#include`/`import`/`using`) were forced to follow that same call direction. With OO's safe polymorphism, an interface can sit between any caller and callee, and the *implementing* module (`ML1`) depends on the interface `I` (owned conceptually by the caller's layer) rather than the caller depending on the concrete implementation — the dependency arrow now points opposite to the flow of control. Applied to architecture: put business rules at the center, and make the UI and database plugins that depend on (not depended-upon-by) the business rules, so each can be deployed and developed independently.

## Key Takeaways
1. When justifying an OO design choice, cite dependency inversion / plugin architecture — not encapsulation, inheritance, or polymorphism as isolated features, since none of those alone is unique to OO.
2. Use interfaces deliberately to invert dependencies wherever you want a high-level module to be independent of a low-level one (classic case: business rules independent of UI and database).
3. Independent deployability and independent developability are the payoff of dependency inversion — use them as concrete success criteria when evaluating a proposed component boundary.
4. Don't mistake compiler-enforced access modifiers (`private` in C++/Java) for true encapsulation — clients may still be source-coupled to internal details.
5. A plugin architecture generalizes beyond IO devices — any module boundary in your system can be turned into a plugin relationship by inserting an interface at the right point.

## Connects To
- **Ch 3**: This chapter is the deep dive on "OO imposes discipline on indirect transfer of control," one of the three foundational paradigms.
- **Ch 4**: Contrasts with structured programming's *direct* control-flow discipline — OO's discipline is specifically about the safety of *indirect* (polymorphic) calls.
- **DIP (Dependency Inversion Principle, Part III / SOLID)**: This chapter is the conceptual foundation for DIP — "details should depend on policies," which SOLID formalizes as a class-level principle.
- **Ch 6**: Functional programming's immutability discipline complements OO's dependency-inversion discipline — together they address architecture's "component separation" and "data management" concerns (per Ch 3's mapping).
