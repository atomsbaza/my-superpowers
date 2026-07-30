# Chapter 6: While You Are Coding

## Core Idea
Coding is not mechanical transcription of a design — it is a continuous stream of judgment calls, and Pragmatic Programmers stay deliberately, consciously in control of those calls: understanding why code works (not just that it seems to), estimating algorithmic cost before it bites, refactoring relentlessly, designing for testability, and never trusting generated code they don't understand.

## Frameworks Introduced
- **Programming by Coincidence vs. Programming Deliberately**: code that "seems to work" for reasons you don't understand is a minefield; only rely on things you can prove.
  - When to use: always — but especially whenever you're tempted to leave working code alone "because it works."
  - How: be aware of what you're doing; don't code blindfolded in unfamiliar technology; proceed from a plan; rely only on documented behavior; document your assumptions (Design by Contract); test assumptions with assertions, not guesses; prioritize effort on the hard, foundational parts; don't be a slave to existing code — refactor when it's no longer appropriate.
- **O() Notation / Algorithm Speed estimation**: a mathematical shorthand for the upper-bound growth rate of an algorithm's time or memory as input size increases.
  - When to use: whenever you write a loop or recursive call, and especially before choosing between competing implementations that must scale.
  - How: recognize the shape from the code structure (simple loop → O(n), nested loop → O(n²), halving each iteration → O(log n), divide-and-conquer → O(n log n), permutations → factorial); confirm empirically by timing with varying input sizes and plotting the curve; profile in the real production environment with real data as the final word.
- **Refactoring**: rewriting, reworking, and re-architecting code as understanding deepens, treated as gardening rather than one-shot construction.
  - When to use: on discovering duplication (DRY violation), nonorthogonal design, outdated knowledge, or a performance need to relocate functionality.
  - How (Fowler's rules, as relayed by the authors): don't refactor and add functionality at the same time; have good tests before you begin and run them constantly; take short, deliberate steps (move one field, fuse two methods) and test after each step; make incompatible interface changes break the build so old callers surface immediately.
- **Code That's Easy to Test / Testing Against Contract**: design testability in from the start, and derive test cases directly from a routine's Design by Contract preconditions/postconditions.
  - When to use: as you write each module, before assembling it with others.
  - How: test subcomponents' contracts in dependency order (leaves first) so a failure at the top can be isolated to the new code, not the foundations; keep unit tests conveniently colocated with the code; build a standard test harness (or use xUnit) with setup/cleanup, selectable tests, output analysis, and standardized failure reporting; formalize ad hoc/debugger-session tests into permanent regression tests.

## Key Concepts
- **Accidents of implementation**: relying on undocumented behavior or boundary conditions of a routine that happen to work today but were never designed to.
- **Accidents of context**: silently depending on an environment detail (a GUI being present, English-speaking users) that isn't actually guaranteed.
- **Big-O growth classes**: constant, logarithmic, linear, O(n log n), quadratic, cubic, exponential — each with characteristic real-world examples (binary search, bubble sort, quicksort average case, traveling salesman).
- **Premature optimization**: optimizing an algorithm before confirming it's actually a bottleneck; the fastest algorithm is not always the best choice, especially for small inputs with high setup cost.
- **Software as gardening, not construction**: code is organic and needs continual pruning, splitting, and rebalancing, unlike a building poured once from blueprints.
- **Class browser / refactoring browser**: Smalltalk-originated IDE tooling that semi-automates common refactoring operations (renaming, extracting methods, propagating changes).
- **Software IC (Integrated Circuit)**: the metaphor that software components should be as reliably pluggable as hardware chips, which requires the same discipline of built-in, thorough per-unit testing.
- **Evil wizards**: code-generation tools that produce large amounts of code that becomes woven inextricably into your own — dangerous specifically because the generated code isn't cleanly factored behind an interface you can ignore.

## Mental Models
- Think of the soldier probing a minefield with a bayonet: early "successes" without incident don't prove safety — they may just mean you haven't hit the mine yet. Apply this skepticism to any code that "seems to work."
- Think of refactoring as a "growth" requiring surgery: remove it while it's small; every delay makes removal more expensive and more dangerous, up to and including losing the patient (the project).
- Think of algorithmic estimation the way you think of driving on autopilot but still constantly scanning for hazards: most loops don't need formal analysis, but a quick subconscious O() check should run every time you write one.
- Use a wizard's generated code only if you're willing to treat it as your own from that moment forward — if you wouldn't want to own and debug every line, don't ship it.

## Anti-patterns
- **Fred's coincidence-driven coding**: adding code incrementally, testing loosely, and never understanding *why* it works — guarantees an eventual failure with no diagnostic foothold.
- **Calling routines in undocumented sequences to force a visual result** (the `paint()`/`invalidate()`/`repaint()` example): looks like it works, but the ordering is an accident, not a contract, and will break under a different platform, resolution, or library version.
- **Leaving "spurious calls" in place because "it works now"**: undocumented behavior may change on the next release; extra calls also cost performance and add bug surface.
- **Skipping regression tests to save time on refactoring**: time pressure is used as an excuse not to refactor, but the later fix always costs more, not less.
- **Using a GUI/code wizard without reading every line it generates**: you cannot maintain, extend, or debug what you don't understand, and wizard code is interwoven with your own, not hidden behind a boundary.

## Code Examples
```java
public void testValue(double num, double expected) {
    double result = 0.0;
    try {
        result = mySqrt(num); // may throw a precondition exception
    } catch (Throwable e) {
        if (num < 0.0) return;      // exception expected for negative input
        else assert(false);         // otherwise force a test failure
    }
    assert(Math.abs(expected - result) < epsilon * expected);
}
```
- **What it demonstrates**: deriving a unit test directly from a routine's Design by Contract precondition (`argument >= 0`) and postcondition (result squared within epsilon of argument).

## Reference Tables
| O() notation | Class | Example |
|---|---|---|
| O(1) | Constant | Array element access, simple statements |
| O(log n) | Logarithmic | Binary search |
| O(n) | Linear | Sequential search |
| O(n log n) | Slightly worse than linear | Average-case quicksort, heapsort |
| O(n²) | Square law | Selection sort, insertion sort |
| O(n³) | Cubic | Multiplying two matrices |
| O(2ⁿ) | Exponential | Traveling salesman, set partitioning |

## Worked Example
The book's O() illustration: a routine takes 1 second to process 100 records. Extrapolating for 1,000 records — an O(log n) routine still takes about 1 second; O(n) takes about 10 seconds (linear scale-up); O(n log n) takes about 33 seconds; O(n²) takes about 100 seconds; and an exponential O(2ⁿ) routine would take "years," with the deadpan aside "let us know how the universe ends." This single walk-through demonstrates why recognizing an algorithm's shape *before* it runs at scale matters — the same code that felt instantaneous at 100 records can become computationally unusable at 1,000, and the gap only widens from there. The chapter pairs this with practical advice: if you're unsure of an algorithm's true growth curve, vary the input size, time it, and plot three or four points — the shape of the curve (flattening, straight, or curving upward) tells you what you're actually dealing with, independent of theory.

## Key Takeaways
1. If you don't know *why* your code works, you don't actually know it works — treat that as a bug waiting to happen, not a success.
2. Rely only on documented behavior; if you must depend on undocumented behavior, write down that assumption explicitly.
3. Do a mental O() check on every loop and recursive call — nested loops are O(n²) until proven otherwise.
4. Refactor as soon as you notice duplication, nonorthogonality, or outdated assumptions — the cost only grows with delay, and good regression tests are what make refactoring safe rather than reckless.
5. Derive unit tests from a routine's contract (preconditions, postconditions, boundary values) rather than throwing random data at it.
6. Test subcomponents' contracts before testing the module that depends on them, so failures localize to the newest code.
7. Never ship wizard-generated code you haven't read and understood line by line — it becomes yours the moment it ships.

## Connects To
- **Ch 5**: Design for Concurrency's emphasis on always-valid object state is the same discipline "How to Program Deliberately" demands generally.
- **Ch 8 (Ruthless Testing)**: unit testing here is the foundation that project-wide integration, validation, and regression testing (Ch 8) builds on.
- **Design by Contract (Ch 4)**: both "Testing Against Contract" and "How to Program Deliberately" lean directly on preconditions/postconditions/invariants introduced earlier in the book.
- **Code Generators (Ch 4)**: Evil Wizards contrasts with the book's endorsement of *writing your own* code generators, where the generated code's role and boundary are fully understood by the author.
