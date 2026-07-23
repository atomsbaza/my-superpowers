# Chapter 16: Refactoring SerialDate

## Core Idea
A full case study: Martin takes David Gilbert's real, already-"good" `SerialDate` class from the JCommon open-source library and walks through raising its test coverage, fixing bugs, and refactoring it toward clean code — demonstrating that professional critique and continuous improvement apply even to competent, working code.

## Frameworks Introduced
- **Make It Work, Then Make It Right**: separate the correctness pass from the design pass.
  - When to use: any time you inherit or must modify code you didn't originally write and don't yet trust.
  - How: first raise test coverage until you understand and trust the code's actual behavior (write new independent tests, use a coverage tool like Clover to find untested paths), fix bugs the tests expose; only then start restructuring names, classes, and methods, re-running the full suite after every change.
- **The Boy Scout Rule (applied)**: leave the code cleaner than you found it, incrementally, without waiting for permission to do a "big rewrite."
  - When to use: any pass over legacy code, even code that already looks professional.
  - How: many small, test-verified refactorings in sequence rather than one large rewrite.
- **Professional Code Review as Craft Discipline**: critiquing another programmer's code in public is a normal, respectful professional act, not an attack.
  - When to use: reviewing any codebase, especially one that is already "good."
  - How: separate the person from the code; assume competence; explain the *why* behind each critique.

## Key Concepts
- **Test coverage as a trust metric**: Clover reported the original suite exercised only ~50% of statements; low coverage on "passing" tests hides latent bugs and unreachable/dead branches.
- **Abstract Factory pattern**: used to remove a base class's (`DayDate`) hidden dependency on knowledge of its own concrete subclass (`SpreadsheetDate`) when creating new instances.
- **Feature Envy**: a method (`monthCodeToQuarter`) that operates mostly on another class's data and rightly belongs on that other class (moved into the `Month` enum as `quarter()`).
- **Explaining Temporary Variables**: intermediate named variables introduced purely to make a non-obvious algorithm step self-documenting (used repeatedly in `addMonths`, `getNearestDayOfWeek`, etc.).
- **Logical vs. physical dependency**: a method can have no *compile-time* dependency on a subclass yet still implicitly depend on subclass-specific facts (e.g., `getDayOfWeek`'s algorithm depends on which day ordinal-zero falls on) — such hidden coupling should be made explicit via an abstract method.
- **Command/query naming ambiguity**: `date.addDays(7)` reads as mutating `date` even though it returns a new instance; renaming to `plusDays` removes the ambiguity.
- **Flag arguments as a smell**: two near-duplicate methods differing only by a boolean/format flag should be split or replaced by structure (e.g., `toString`/`toShortString`).
- **Redundant/stale comments**: comments that restate the code or that go out of sync with it (like a hand-maintained change history) are worse than no comment — delete them and rely on source control and expressive code instead.

## Mental Models
- Even "good code" from a competent, disciplined author (Gilbert) still has systemic issues once you actually measure test coverage and trace usages — professionalism is a spectrum, not a pass/fail badge.
- An abstract base class should imply nothing about its implementation; if a name, constant, or field only makes sense for one concrete subclass, it belongs in that subclass, not the base.
- Naming should track the level of abstraction: `SerialDate` names the implementation detail (a day-serial-number); the abstract concept is better named `DayDate`.
- Refactoring can be done as a chain of small, IDE-assisted, test-verified steps — each step alone looks trivial, but the sequence can eliminate entire methods (e.g., moving `weekInMonthToString` into an enum's `toString()`, then discovering it's fully redundant and deleting it).
- Decreased raw coverage percentage after refactoring can be a *good* sign — it can mean the class got smaller and only trivial statements remain untested, not that testing got worse.

## Anti-patterns
- **Inheriting from a class of constants** (`DayDate implements MonthConstants`) instead of using a proper enum — an old Java trick to avoid qualifying constant names, at the cost of a meaningless "is-a" relationship.
- **Base class instantiating/knowing its own subclass** — `DayDate.createInstance` hard-coded creation of `SpreadsheetDate`, so an "abstract" class silently depended on one specific implementation. Fixed with `DayDateFactory` (Abstract Factory).
- **Magic numbers and unclear constants**: `EARLIEST_DATE_ORDINAL = 2` with no obvious reason for 2 instead of 0; a bare `1` used instead of `Month.JANUARY.toInt()`.
- **Boundary condition bugs from careless comparison operators**: `getFollowingDayOfWeek` used `>` instead of `>=`, so December 25 (a Saturday) matched itself as "the following Saturday."
- **Dead/unreachable code hidden by poor test coverage**: an `if` branch in `getNearestDayOfWeek` could never execute because the guarding variable was structurally always negative — only visible via coverage tooling.
- **Duplicate near-identical methods differing by a flag or one line** — two `getMonths` methods, two `monthCodeToString` methods; collapse into one, parameterized properly (often by enum) rather than by flag.
- **Data belonging to the wrong class**: constants/tables (`MINIMUM_YEAR_SUPPORTED`, `AGGREGATE_DAYS_TO_END_OF_PRECEDING_MONTH`) defined on the abstract base but used only by one concrete subclass, or unused everywhere.
- **Redundant Javadoc/comments and a hand-maintained change-history block** at the top of the file — noise that source control already handles, and a place where lies/misinformation accumulate.
- **Ambiguous naming that implies mutation** (`addDays`) on an immutable value class — should read fluently as a query (`plusDays`) so callers don't wrongly assume in-place mutation.
- **Sparse, unverified test suite treated as "passing" proof of correctness** — passing tests only prove what they cover; ~50% coverage meant half the class was unverified despite "all tests pass."

## Code Examples
```java
// Before: static method, boundary bug (`>` instead of `>=`), buried logic
if (baseDOW > targetWeekday) { ... }  // wrong: Dec 25 (Sat) "follows" itself

// After: corrected boundary condition
685  if (baseDOW >= targetWeekday) {
```
- **What it demonstrates**: a one-character boundary condition error, invisible without a targeted regression test, silently broke `getFollowingDayOfWeek`.

```java
public abstract class DayDateFactory {
    private static DayDateFactory factory = new SpreadsheetDateFactory();
    public static void setInstance(DayDateFactory factory) {
        DayDateFactory.factory = factory;
    }
    protected abstract DayDate _makeDate(int ordinal);
    protected abstract DayDate _makeDate(int day, DayDate.Month month, int year);
    protected abstract int _getMinimumYear();
    protected abstract int _getMaximumYear();
    public static DayDate makeDate(int ordinal) { return factory._makeDate(ordinal); }
    public static int getMinimumYear() { return factory._getMinimumYear(); }
}
```
- **What it demonstrates**: Abstract Factory removes the base class's hidden knowledge of its concrete subclass, while still letting client code ask implementation-level questions (min/max year) through the abstract interface.

```java
// Before (implied mutation, ambiguous):
date.addDays(7); // bump date by one week — does this mutate `date`?

// After (renamed to read as a pure query):
DayDate date = oldDate.plusDays(5);
```
- **What it demonstrates**: renaming to remove command/query ambiguity on an immutable value object.

## Reference Tables
(omit — no tabular reference material in this chapter)

## Worked Example
Martin picks the real, MIT/BSD-licensed `SerialDate` class (and its `SerialDateTests`) from JCommon. **Phase 1 — Make It Work**: existing tests all "passed" but Clover showed only 91/185 statements (~50%) covered. He wrote an independent test suite, driving coverage to 92%, which surfaced: a case-sensitivity bug in `stringToMonthCode`/weekday parsing (fixed with `equalsIgnoreCase`), a boundary bug in `getFollowingDayOfWeek` (`>` vs `>=`), and a genuinely dead/wrong branch in `getNearestDayOfWeek` (rewritten with a clean modulo-based algorithm), plus two methods changed to throw `IllegalArgumentException` instead of returning sentinel error strings. **Phase 2 — Make It Right**, top to bottom: deleted the manual change-history comment block (source control's job now); replaced `MonthConstants` and other int-constant groups with proper `Month`, `Day`, `WeekInMonth`, `DateInterval`, `WeekdayRange` enums; renamed the class conceptually from `SerialDate` to `DayDate` (implementation-neutral name); introduced `DayDateFactory` (Abstract Factory) to stop the base class from hard-coding `SpreadsheetDate` creation; pushed subclass-specific constants (`MINIMUM_YEAR_SUPPORTED`, lookup tables) down into `SpreadsheetDate`; pulled genuinely generic abstract methods (`toDate`, `getDayOfWeek`, `compareTo`/`daysSince`, `isInRange`) up into `DayDate`, isolating the one true implementation-dependent fact (`getDayOfWeekForOrdinalZero`) behind a new abstract method; converted static methods that touched instance state to instance methods (`addDays`→`plusDays`, `addMonths`→`plusMonths`); eliminated duplicate methods, flag arguments, redundant comments, and magic numbers; extracted `correctLastDayOfMonth` to remove duplication between `plusYears`/`plusMonths`; moved enums and static date utilities into their own files/classes (`DateUtil`). End state: `DayDate` shrank to 53 executable statements with 45 covered (84.9%) — a lower percentage than before but a much smaller, better-understood, fully-intentional surface area.

## Key Takeaways
1. "All tests pass" is not the same as "well tested" — always check *coverage*, not just pass/fail, before trusting legacy code.
2. Even code written by a skilled, disciplined author benefits from critique; professional review is a normal craft practice, not an insult.
3. Separate correctness work from design work: get trustworthy tests and fix real bugs first, then refactor structure — verify with the full suite after every single change.
4. Replace flag arguments, int/String pseudo-enums, and duplicate near-identical methods with real enums and single well-named methods.
5. An abstract class must not encode knowledge of its concrete subclasses; when it needs implementation-level answers (like value ranges or instance creation), route them through a Factory instead.
6. Delete comments and code that no longer earn their keep (stale change history, redundant Javadoc, unused fields/tables) rather than dragging them forward.
7. Name query methods on immutable types so they can't be misread as mutators (`plusDays`, not `addDays`).

## Connects To
- **Ch 9 (Unit Tests)**: this chapter is the applied version of Ch 9's coverage and F.I.R.T.S. principles — Clover-measured gaps directly drove the refactoring order here.
- **Ch 3 (Functions)**: flag arguments, duplicate twin methods, and Feature Envy fixes here are direct applications of Ch 3's function-design rules.
- **Ch 2 (Meaningful Names)**: the `SerialDate`→`DayDate`, `addDays`→`plusDays`, `toSerial`→`getOrdinalDay` renames are case-study instances of Ch 2's naming guidance.
- **Ch 17 (Smells and Heuristics)**: nearly every bracketed tag in this chapter ([G1]-[G25], [N1]-[N4], [C1]-[C3], [J1]-[J3], [T1]-[T8], [F4]) refers directly to the numbered heuristics catalogued in Ch 17.
- **Ch 14 (Successive Refinement)**: the other extended refactoring case study in the book (`Args` class), showing the same incremental, test-guarded method applied to a different codebase.
- **JCommon / `org.jfree.date`**: the real open-source library this chapter refactors; David Gilbert is credited as original author and praised for open-sourcing the code for public review.
