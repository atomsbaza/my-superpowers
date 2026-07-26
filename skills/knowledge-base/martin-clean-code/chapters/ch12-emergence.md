# Chapter 12: Emergence

## Core Idea
Good design does not need to be planned upfront in full — it can emerge from following four simple, ordered rules (Kent Beck's Four Rules of Simple Design), which push a codebase toward low coupling, high cohesion, and clarity through disciplined, test-backed refactoring.

## Frameworks Introduced
- **Kent Beck's Four Rules of Simple Design**: A design is "simple" if, in priority order, it (1) runs all the tests, (2) contains no duplication, (3) expresses the intent of the programmer, (4) minimizes the number of classes and methods.
  - When to use: Continuously, as a checklist applied during every refactoring pass after code is written and passing tests — not as an upfront design phase.
  - How: Write a test, make it pass, then refactor against rules 2-4 in order; run tests after each change to confirm nothing broke; repeat in small increments.

## Key Concepts
- **Emergent design**: Good architecture that arises from repeatedly and disciplined applying simple rules over time, rather than from big upfront design.
- **Runs all the tests**: A system fully covered by passing tests is verifiable; unverifiable systems should never be deployed, and pursuing testability naturally drives SRP-conformant, loosely coupled classes.
- **No duplication**: Repeated code, or repeated *implementation logic*, is the primary enemy of good design — it adds work, risk, and complexity.
- **Expresses intent**: Code should communicate the author's purpose clearly through names, small units, standard nomenclature, and expressive tests, since most cost is in long-term maintenance.
- **Minimizes classes/methods**: Keep the overall count of classes and methods low; taken to excess, decomposition and duplication-elimination create needless small classes — this rule is the lowest priority and exists to check dogmatic over-splitting.
- **Reuse in the small**: Extracting small, well-named private methods to remove local duplication surfaces reusable abstractions that can later be promoted/reused more broadly.
- **TEMPLATE METHOD pattern**: A technique (from GoF) for eliminating higher-level duplication by moving a shared algorithm skeleton into a base class and deferring the varying steps to subclasses.
- **Pointless dogmatism**: Rigid rules applied without judgment (e.g., "every class needs an interface") that inflate class/method counts without benefit.

## Mental Models
- Design quality is not a binary planning artifact but a continuously maintained property, re-earned with every small change via the "add code → pause → reflect → refactor → re-run tests" loop.
- Tests are the safety net that removes fear of cleanup — without fear, developers actually refactor; without refactoring, small duplications calcify into large design problems.
- The four rules are strictly ordered: testability and correctness come before duplication removal, which comes before expressiveness, which comes before minimalism — later rules should never be pursued at the expense of earlier ones.
- "Reuse in the small" compounds into "reuse in the large" — abstraction discipline at the line/method level is what makes system-level reuse possible.

## Anti-patterns
- **Skipping tests or letting the suite go stale**: An unverifiable system cannot be safely refactored, so duplication and unclear intent accumulate unchecked.
- **Leaving small duplications "because they're tiny"**: Small duplicated logic (e.g., separate size/isEmpty tracking, or repeated dispose/gc/reassign sequences) multiplies risk and makes future changes error-prone — it should be extracted immediately, however small.
- **Writing code only you understand**: Code written deep in the problem context but never revisited for clarity imposes a comprehension tax on every future maintainer, including your future self.
- **Dogmatic decomposition**: Mandating an interface per class, or always splitting data and behavior into separate classes regardless of need, inflates class/method counts without improving design — violates rule 4's intent.

## Code Examples
```java
public class VacationPolicy {
    public void accrueUSDivisionVacation() {
        // code to calculate vacation based on hours worked to date
        // code to ensure vacation meets US minimums
        // code to apply vacation to payroll record
    }
    public void accrueEUDivisionVacation() {
        // code to calculate vacation based on hours worked to date
        // code to ensure vacation meets EU minimums
        // code to apply vacation to payroll record
    }
}

// After applying TEMPLATE METHOD to remove duplication:
abstract public class VacationPolicy {
    public void accrueVacation() {
        calculateBaseVacationHours();
        alterForLegalMinimums();
        applyToPayroll();
    }
    private void calculateBaseVacationHours() { /* ... */ }
    abstract protected void alterForLegalMinimums();
    private void applyToPayroll() { /* ... */ }
}
public class USVacationPolicy extends VacationPolicy {
    @Override protected void alterForLegalMinimums() { /* US specific logic */ }
}
public class EUVacationPolicy extends VacationPolicy {
    @Override protected void alterForLegalMinimums() { /* EU specific logic */ }
}
```
- **What it demonstrates**: TEMPLATE METHOD eliminates duplicated algorithm structure by hoisting the common steps into a base class and isolating only the varying step (legal-minimums logic) in subclasses.

## Reference Tables
| Rule (priority order) | What it means |
|---|---|
| 1. Runs all the tests | The system must be fully testable and pass all tests; unverifiable systems should never ship. Pursuing this drives SRP and low coupling. |
| 2. Contains no duplication | Eliminate duplicated code and duplicated implementation logic, even at the scale of a few lines; use techniques like extracted methods and TEMPLATE METHOD. |
| 3. Expresses the intent of the programmer | Communicate clearly via good names, small functions/classes, standard pattern nomenclature, and expressive tests. |
| 4. Minimizes the number of classes and methods | Keep overall class/method counts low; resist dogmatic over-decomposition — this is the lowest-priority rule, never pursued at the cost of the other three. |

## Worked Example
The chapter walks through an image-processing class with `scaleToOneDimension` and `rotate` methods that both independently call `image.dispose(); System.gc(); image = newImage;` after computing a new `RenderedOp`. This is duplication of implementation, not just of literal text. The fix: extract the shared three lines into a private `replaceImage(RenderedOp newImage)` method, and have both original methods call it with their respective computed image. The result: each method keeps only its unique logic (scaling factor computation, or rotation), while the common "swap in the new image" behavior lives in one place. This small-scale duplication removal is then generalized to a larger case — two `VacationPolicy` methods (US and EU) that are identical except for the legal-minimums check — resolved with the TEMPLATE METHOD pattern (shown above), converting duplicated algorithm structure into a shared base-class method with an abstract hook for the varying part.

## Key Takeaways
1. Follow Kent Beck's four rules of Simple Design in strict order — tests first, then duplication, then expressiveness, then minimalism — since later rules should never override earlier ones.
2. A fully tested system is a prerequisite for safe refactoring; without tests, fear prevents the cleanup that keeps design good over time.
3. Eliminate duplication relentlessly, even at the scale of a few repeated lines — small "reuse in the small" extractions compound into system-wide reuse and cleaner abstractions.
4. Use TEMPLATE METHOD (and similar patterns) to remove higher-level duplication when multiple methods share an algorithm skeleton but differ in one step.
5. Prioritize expressive names, small units, standard pattern names, and expressive tests — code is read far more than it is written, and most project cost is long-term maintenance.
6. Keep class and method counts low as a final check, resisting dogmatic rules (mandatory interfaces, forced data/behavior separation) that inflate counts without adding value.
7. Treat design as emergent and continuous: pause after every small addition to ask whether the design just degraded, then clean up immediately while tests still pass.

## Connects To
- **Ch 3 (Functions)**: Small, single-purpose functions are both a cause and effect of rule 3 (expressiveness) and rule 1 (testability) — this chapter explains *why* that discipline matters for design.
- **Ch 9 (Unit Tests)**: Rule 1 depends directly on the F.I.R.S.T. testing principles and comprehensive coverage discussed there — testability is the gateway to safe refactoring.
- **Ch 10 (Classes)**: SRP and cohesion, covered there in depth, are the natural outcome of pursuing rules 1 and 2 (testable, duplication-free) here.
- **Ch 17 (Smells and Heuristics)**: Many heuristics listed there (duplication, unclear naming, needless complexity) are concrete instances of violating the four rules.
- **Kent Beck, Extreme Programming**: The Four Rules of Simple Design originate from Beck's XP practice and are cited directly (private correspondence, and *Extreme Programming Explained*) as the chapter's foundational framework.
- **GoF, TEMPLATE METHOD pattern**: Cited (*Design Patterns*, Gamma et al.) as the concrete mechanism used to eliminate higher-level duplication in the worked example.
