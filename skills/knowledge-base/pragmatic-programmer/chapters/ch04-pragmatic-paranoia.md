# Chapter 4: Pragmatic Paranoia

## Core Idea
Assume your own code is fallible and the world hostile: make every module's obligations explicit through contracts, crash loudly and immediately on impossible states rather than limping on corrupted, use exceptions only for truly exceptional events, and always balance every resource you allocate.

## Frameworks Introduced
- **Design by Contract (DBC)**: Every routine has preconditions (what the caller must guarantee), postconditions (what the routine guarantees on completion), and class invariants (what must hold true from the caller's perspective) — Bertrand Meyer's formalism for Eiffel.
  - When to use: Designing any module or class interface, especially base classes in an inheritance hierarchy.
  - How: State the precondition (caller's responsibility to satisfy), postcondition (routine's guarantee, implying the routine must terminate), and invariant explicitly — in code comments if the language lacks native support (iContract for Java, Nana for C/C++), or as first-class syntax in Eiffel (`require` / `ensure`).
- **Crash Early / Dead Programs Tell No Lies**: When something impossible happens, terminate immediately rather than continuing with corrupted state.
  - When to use: Any detected violation of an assumption that "can never happen" — a bad case-statement selector, a failed resource check, an out-of-range value.
  - How: Let runtime exceptions propagate and halt the program (Java's `RuntimeException` model), or build your own abort macro in languages without exceptions; a dead program does far less damage than a crippled one that keeps writing corrupted data.
- **Assertive Programming / TIP 33 — "If It Can't Happen, Use Assertions to Ensure That It Won't"**: Whenever you think "but of course that could never happen," add an assertion to check it.
  - When to use: Any assumption baked into your code's logic (non-null pointers, sorted arrays, valid enum ranges) that you believe is always true.
  - How: Use `assert`/`_assert` macros on Boolean conditions with no side effects; leave assertions turned on in production (only disable the specific ones that provably hurt performance); never use assertions as a substitute for real input validation or error handling.
- **Finish What You Start**: The routine or object that allocates a resource should be the one responsible for deallocating it.
  - When to use: Managing memory, files, transactions, threads, locks, or any resource with an allocate/use/deallocate lifecycle.
  - How: Keep allocation and deallocation symmetric and local to the same routine/scope; when nesting multiple resources, deallocate in the reverse order of allocation, and always allocate shared resources in the same order everywhere to avoid deadlock; use language facilities (destructors, `finally`, garbage-collected wrapper objects) to guarantee cleanup even when exceptions are thrown.

## Key Concepts
- **Liskov Substitution Principle**: Subclasses must be usable through the base class interface without callers needing to know the difference — DBC enforces this by requiring subclasses to accept at least as much and guarantee at least as much as their parent.
- **Loop Invariant**: A condition that holds before a loop starts, on every iteration, and after it terminates — used to reason about correctness of nontrivial loops (e.g., finding a max value in an array).
- **Semantic Invariant**: A "philosophical contract" — an inviolate business rule (distinct from a changeable policy) stated once, clearly, and applied throughout a system's design (example given: "ERR IN FAVOR OF THE CONSUMER" for a debit-card switch, ensuring duplicate transactions are never processed even under failure).
- **"This Can Never Happen" mantra**: The chapter's name for the dangerous self-deception programmers practice when dismissing edge cases as impossible.
- **Exceptional vs. Non-exceptional errors**: An exception should be reserved for events that break the normal flow assumption of the code (a missing `/etc/passwd` file); a merely uncertain outcome (a user-specified filename that may or may not exist) should be a normal return value, not an exception.
- **Error Handlers as an alternative to exceptions**: A registered routine invoked automatically for a category of error (e.g., wrapping RMI's `RemoteException` handling) — useful when exceptions everywhere would be too tedious or when the language lacks exception support.
- **Nest Allocations rules**: (1) deallocate in the reverse order of allocation; (2) always allocate a given set of resources in the same order across the codebase to prevent deadlock.

## Mental Models
- Think of a contract like an employment agreement: each party (caller and routine) has explicit rights, responsibilities, and an agreed remedy if either side fails to hold up their end.
- Think of preconditions/postconditions as "lazy code": accept as little as you can get away with, promise as little as possible in return — the narrower the contract, the less code you owe the world.
- Think of crashing early as choosing the "dead program" over the "crippled one" — a halted process does no more damage, while a corrupted process may keep writing bad data or commanding physical hardware (the chapter's washing-machine-on-endless-spin-cycle image) indefinitely.
- Think of resource management like nested parentheses: whichever routine opens a resource must be the one to close it, and nested resources must close in strict reverse order of opening — mirroring a class's constructor/destructor symmetry.

## Anti-patterns
- **"This can never happen" self-deception**: Dismissing edge cases (two-digit dates, non-negative counts, printf never failing) as impossible is exactly the mentality that produces catastrophic bugs like Y2K-class failures.
- **Turning off assertions in production**: A common but "patently wrong" assumption that testing finds all bugs and that assertions are only a debugging aid — the book calls disabling them "crossing a high wire without a net because you once made it across in practice."
- **Assertions with side effects**: E.g., `assert(iter.nextElement() != null)` inside a loop that also calls `iter.nextElement()` for real use — the assertion itself silently consumes an element, corrupting the very logic it was meant to verify (a "Heisenbug").
- **Using exceptions for normal control flow**: Turns exceptions into "a kind of cascading goto," coupling routines and callers tightly and reintroducing the same readability problems as unstructured spaghetti code.
- **Globally coupled resource lifecycle code**: The `readCustomer`/`writeCustomer` example shares a global `cFile` variable across routines — a later "fix" that skips `writeCustomer` under some conditions leaves the file handle open, eventually exhausting file descriptors in production.
- **Assuming precondition-checking is the callee's job**: In DBC, if the caller fails to satisfy a precondition, that's a bug in the caller, not something the routine should defensively re-validate as if it were user input.

## Code Examples
```java
// Design by Contract via iContract-style comments (Java)
/**
 * @invariant forall Node n in elements() |
 *   n.prev() != null
 *   implies
 *   n.value().compareTo(n.prev().value()) > 0
 */
public class dbc_list {
    /**
     * @pre  contains(aNode) == false
     * @post contains(aNode) == true
     */
    public void insertNode(final Node aNode) {
        // ...
    }
}
```
```c
/* Finish What You Start: symmetric resource allocation, fixed version */
void readCustomer(FILE *cFile, Customer *cRec) {
    fread(cRec, sizeof(*cRec), 1, cFile);
}
void writeCustomer(FILE *cFile, Customer *cRec) {
    rewind(cFile);
    fwrite(cRec, sizeof(*cRec), 1, cFile);
}
void updateCustomer(const char *fName, double newBalance) {
    FILE *cFile;
    Customer cRec;
    cFile = fopen(fName, "r+");     // >--- open
    readCustomer(cFile, &cRec);     //  |
    if (newBalance >= 0.0) {        //  |
        cRec.balance = newBalance;  //  |
        writeCustomer(cFile, &cRec);//  |
    }                                //  |
    fclose(cFile);                  // <--- close, same routine
}
```
- **What it demonstrates**: The DBC snippet shows preconditions/postconditions/invariants expressed as structured comments processed by a preprocessor; the resource-balancing snippet shows the "finish what you start" fix — moving the file handle out of a shared global and making the single routine that opens the file responsible for closing it, regardless of which branch executes.

## Reference Tables
| Concept | Eiffel keyword | Applies to |
|---|---|---|
| Precondition | `require` | Caller's obligation before calling |
| Postcondition | `ensure` | Routine's guarantee on exit |
| Class invariant | (implicit, class-level) | Must hold whenever control returns to caller |

| Situation | Exception warranted? |
|---|---|
| Expected file (`/etc/passwd`) missing | Yes — genuinely exceptional |
| User-specified filename that may not exist | No — plain `boolean`/error return |

## Worked Example
The chapter's square-root example crystallizes DBC's division of responsibility. An Eiffel `sqrt` routine on `DOUBLE` declares a precondition (`require sqrt_arg_must_be_positive: Current >= 0`) and a postcondition (`ensure` that the result squared is within `epsilon` of the original value). The key question the authors pose is: who is responsible for checking the precondition, the caller or the routine? The answer is neither, directly — in a language with native DBC support, the precondition is checked automatically behind the scenes between the call and the routine's actual body, so the routine itself will never see an out-of-range argument. This means if a user types a negative number at the console, it is entirely the calling code's job to prevent that number from ever reaching `sqrt` — through validation, warning, or coercion — because that is "definitely not sqrt's problem." The payoff is contrasted directly with C, C++, and Java's typical behavior: passing a negative number to their sqrt implementations silently returns `NaN`, and the program may not notice anything wrong until much later, when arithmetic on that `NaN` produces bizarre, hard-to-trace results far from the actual fault. Eiffel's contract violation, by contrast, prints the precondition's name and a stack trace immediately at the call site — "it's much easier to find and diagnose the problem by crashing early, at the site of the problem."

## Key Takeaways
1. Write contracts (preconditions, postconditions, invariants) for your interfaces even without language support — as comments, they still tell future readers (including you) what a routine actually promises.
2. Push validation responsibility to the caller via preconditions; a routine violated by bad input from a caller has a bug in the caller, not in itself.
3. Treat "this can never happen" as a trigger to add an assertion, not a reason to skip a check.
4. Leave assertions on in production; disable only the specific ones proven to cause unacceptable overhead.
5. Reserve exceptions for genuinely exceptional, unexpected conditions — use ordinary return values for expected, "may or may not exist" outcomes.
6. Make the routine that allocates a resource responsible for freeing it, and deallocate nested resources in the reverse order they were acquired.
7. When a bug's failure mode is silent corruption (like NaN propagation), prefer crashing loudly and immediately over continuing with data you can no longer trust.

## Connects To
- **Ch 2**: DBC is orthogonality applied at the interface boundary — contracts let modules stay decoupled while still guaranteeing correctness across that boundary.
- **Ch 3**: "Crash early" and assertive programming build directly on Chapter 3's debugging discipline of never dismissing a bug as impossible.
- **Meyer's Eiffel language**: DBC originates in Bertrand Meyer's design of Eiffel, building in part on earlier formal-methods work by Dijkstra, Floyd, Hoare, and Wirth; the chapter treats Eiffel's native `require`/`ensure`/`old` support as the gold standard against which preprocessor-based emulation (iContract for Java, Nana for C/C++) is compared.
- **Modern software engineering**: DBC's ideas persist in modern type systems and contract libraries (e.g., Python's `contracts`, .NET Code Contracts, Rust's `debug_assert!`); "fail fast" is now standard distributed-systems doctrine; RAII in C++/Rust and `try-with-resources`/`using` blocks in Java/C# are direct descendants of "finish what you start."
