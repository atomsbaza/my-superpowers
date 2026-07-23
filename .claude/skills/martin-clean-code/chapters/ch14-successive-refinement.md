# Chapter 14: Successive Refinement

## Core Idea
Clean code is not written in one pass — it is written dirty and then refined, in a long sequence of tiny, test-protected steps, into something elegant. This chapter is a case study of that process applied to an `Args` command-line-argument parser.

## Frameworks Introduced
- **Successive Refinement (write-then-clean)**: "To write clean code, you must first write dirty code and then clean it." Programming is a craft, not a one-shot science — like writing a composition, you draft, then re-draft, until the final version emerges.
  - When to use: Any nontrivial module, especially when requirements/scope are still growing incrementally.
  - How: (1) Get something working end-to-end, however ugly. (2) Once you sense the design straining under new requirements, stop adding features. (3) Refactor in a large number of very small steps, each of which keeps a full automated test suite (unit + acceptance) passing. (4) Only resume adding features once the structure is sound again.
- **Incrementalism via TDD-protected refactoring**: Never make a change that breaks the system; use a fast, comprehensive test suite (JUnit unit tests + FitNesse acceptance tests in the case study) as a safety net so structural changes can be made fearlessly, one tiny step at a time.
  - When to use: Whenever restructuring existing working code (as opposed to greenfield design).
  - How: Add new structure alongside the old without wiring it in yet (e.g., append an empty class); migrate one call site at a time; run tests after every step; if a step breaks tests, fix immediately before proceeding; delete the old structure only once nothing references it.

## Key Concepts
- **Rough draft**: The first "working" version of code — expected to be messy, not a target to leave in production.
- **ArgumentMarshaler**: A polymorphic interface (`set`/`get`) that each argument type (boolean, string, integer, double, string array) implements, replacing type-specific maps and switch/type-case logic.
- **Type-case (anti-pattern being removed)**: A chain of `if (m instanceof XMarshaler) ... else if ...` that the refactoring's central goal is to eliminate by pushing behavior into polymorphic `set`/`get` implementations.
- **Schema string**: The compact DSL Args uses to declare argument types, e.g. `"l,p#,d*"` — `l` boolean, `p#` integer, `d*` string, `##` double, `[*]` string array.
- **Parallel-maps smell**: The rough draft keeps a separate `HashMap` per argument type (`booleanArgs`, `stringArgs`, `intArgs`); refactoring consolidates these into one `marshalers` map keyed by argument character.
- **Deploying to derivatives**: The technique of moving a method from a base/host class down into subclasses one tiny step at a time (add abstract method → implement trivially → redirect caller → delete old method), used repeatedly to push `set`/`get` logic into each `ArgumentMarshaler` subclass.
- **Iterator over array+index**: Converting `args` (array) + `currentArgument` (int index) into `List<String>` + `Iterator<String>` so only one parameter needs to be threaded through the marshaler `set` methods instead of two.
- **ArgsException extraction**: Moving all error-code/error-message logic out of `Args` into its own `ArgsException` class — an SRP-driven separation of concerns.

## Mental Models
- **Refactoring is like a Rubik's Cube**: many small, individually-reversible-feeling moves, each enabling the next, working toward a large goal that isn't reachable in one twist. You sometimes reintroduce code you just removed, temporarily, because a later step needs it in a different shape.
- **Bad code is like fermenting rot**: left alone it "insinuates itself" into other modules, creating tangled dependencies that are expensive to unwind later; cleaning a five-minute-old mess is cheap, cleaning a five-month-old mess is not.
- **The mess grows nonlinearly with types added**: going from boolean-only (Listing 14-9, "not that bad") to boolean+string+int (Listing 14-8, "festering pile") shows that each new case multiplies structural complexity — a signal to stop and refactor before adding the next.

## Anti-patterns
- **"Get it working, then move on"**: Leaving code in whatever state it first "worked" in — the freshman/grade-schooler mistake; professional programmers treat this as "professional suicide."
- **Type-case / instanceof chains**: `if (m instanceof BooleanArgumentMarshaler) ... else if (m instanceof StringArgumentMarshaler) ...` — violates Open/Closed, forces every call site to know every type; the fix is polymorphism (a single `m.set(...)` call).
- **Parallel type-specific collections**: Separate `booleanArgs`/`stringArgs`/`intArgs` maps force every new type to touch three places (parse, set, get) instead of one new derivative class.
- **Passing raw index + array instead of an iterator**: Requires threading two coupled parameters everywhere; consolidating into an `Iterator<String>` is "dirty" [F1] avoidance — pass one cohesive argument instead of two related ones.
- **Big-bang rewrite**: Making massive structural changes all at once "in the name of improvement" risks a program that never gets working the same way again — the antidote is many tiny test-verified steps.

## Code Examples
```java
// BEFORE (rough draft, Listing 14-8): type-specific maps, ad hoc null-guards
private Map<Character, Boolean> booleanArgs = new HashMap<Character, Boolean>();
private Map<Character, String> stringArgs = new HashMap<Character, String>();
private Map<Character, Integer> intArgs = new HashMap<Character, Integer>();
...
public boolean getBoolean(char arg) { return falseIfNull(booleanArgs.get(arg)); }
public int getInt(char arg) { return zeroIfNull(intArgs.get(arg)); }
public String getString(char arg) { return blankIfNull(stringArgs.get(arg)); }

// AFTER (final, Listing 14-2/14-16): one map, polymorphic marshalers
private Map<Character, ArgumentMarshaler> marshalers = new HashMap<Character, ArgumentMarshaler>();

private void parseArgumentCharacter(char argChar) throws ArgsException {
    ArgumentMarshaler m = marshalers.get(argChar);
    if (m == null) {
        throw new ArgsException(UNEXPECTED_ARGUMENT, argChar, null);
    } else {
        argsFound.add(argChar);
        try {
            m.set(currentArgument);
        } catch (ArgsException e) {
            e.setErrorArgumentId(argChar);
            throw e;
        }
    }
}

public boolean getBoolean(char arg) {
    return BooleanArgumentMarshaler.getValue(marshalers.get(arg));
}
```
- **What it demonstrates**: The end state of the refactoring — one generic map plus a polymorphic `ArgumentMarshaler` interface replaces three parallel type-specific maps and their bespoke null-handling, eliminating the type-case entirely.

## Reference Tables
(omit — no tabular data in this chapter)

## Worked Example
The chapter reconstructs the full evolution of the `Args` class:

1. **Boolean-only version** (Listing 14-9): compact, understandable, ~60 lines — a single `booleanArgs` map, simple parse/set/get.
2. **Add String support** (Listing 14-10): a second parallel map (`stringArgs`), duplicated parse/set/get scaffolding, an `ErrorCode` enum appears. Still tolerable but visibly duplicating structure.
3. **Add Integer support** (Listing 14-8, the "rough draft"): a third parallel map, `NumberFormatException` handling, an inner `ArgsException`, growing `errorMessage()` switch. Now a "festering pile" — daunting instance-variable count, try/catch/catch blocks, magic strings like `"TILT"`.
4. **Stop and refactor.** Author recognizes each new argument type touches three places (schema parsing, argument parsing/conversion, getXXX retrieval) — "many different types, all with similar methods... that sounds like a class to me." Birth of `ArgumentMarshaler`.
5. **Incremental introduction of ArgumentMarshaler**, protected by tests at every step:
   - Append an inert `ArgumentMarshaler` class (with `Boolean/String/Integer` derivative stubs) — breaks nothing.
   - Change `booleanArgs` map's value type to `ArgumentMarshaler`; fix the handful of call sites this breaks (`parseBooleanSchemaElement`, `setBooleanArg`, `getBoolean`); restore a null-check that had silently become load-bearing (`falseIfNull` → explicit `am != null` check) — a test caught this regression immediately.
   - Repeat the same map-swap + call-site-fix pattern for String, then Integer arguments — all marshalling logic temporarily lives in one shared `ArgumentMarshaler` base class with fields for all three value types.
   - **Push behavior down**: convert `ArgumentMarshaler` to `abstract`, add `abstract set(String)`/`get()`, implement in each derivative one type at a time, deleting the now-dead base-class fields/methods after each successful migration. Getters become ugly briefly (`Object get()` needs casting) — accepted as a temporary cost of the process.
   - **Unify the three parallel maps** into one `marshalers` map; replace `booleanArgs.containsKey`-style type checks with `instanceof` checks against the unified map; then inline the now-trivial `isXxxArg` helper methods directly into the `instanceof` chain.
   - **Eliminate the type-case entirely**: convert `args[] + int index` into `List<String> + Iterator<String>` so a single argument can be threaded through all marshalers; add an iterator-based `set(Iterator<String>)` to the interface; migrate boolean, then string, then integer `set` logic into their respective derivatives; the `setArgument` method collapses to a single polymorphic call: `m.set(currentArgument)`.
   - Convert `ArgumentMarshaler` from an abstract class to a plain `interface` once all fields have migrated to derivatives.
6. **Prove extensibility**: adding a new `double` argument type (`##` schema syntax) now requires only: one new case in `parseSchemaElement`, one new `DoubleArgumentMarshaler` class, one new `ErrorCode` enum value, one new `getDouble` method — "pretty painless."
7. **Extract `ArgsException`** into its own file/class, carrying the `ErrorCode` enum and `errorMessage()` formatting out of `Args` — an SRP fix (Args should process arguments, not format error text), done as ~30 more tiny test-passing steps.
8. **Final structure** (Listing 14-16 / the chapter's opening Listing 14-2): `Args` holds one `marshalers` map and delegates all type-specific behavior to `ArgumentMarshaler` implementations; `ArgsException` owns all error codes/messages; each `getXxx` method fetches a marshaler and asks it for its value, with a `ClassCastException` guard for wrong-type queries.

## Key Takeaways
1. First make it work, then make it right — but never stop at "working"; treat the second step as mandatory professional practice, not optional polish.
2. Refactor in many tiny steps, each verified by a fast automated test suite (unit + acceptance) — this is what makes large structural change safe.
3. When you notice a new requirement is about to multiply complexity (e.g., a third parallel map, a growing type-case), stop feature work and refactor before continuing.
4. Repeated type-specific logic across parse/set/get is a signal to extract a polymorphic type (here, `ArgumentMarshaler`) rather than adding more parallel data structures.
5. Eliminating a type-case/instanceof chain is a strong sign the design has finished converging on proper polymorphism.
6. Extracting a concern into its own class (here, `ArgsException`) is often mostly deletion from the original class — a healthy sign the split was correct.
7. Never let rot start: cleaning code five minutes after making a mess is cheap; cleaning it after it has "insinuated itself" into the rest of the system is expensive and sometimes never fully happens.

## Connects To
- **Ch 3 (Functions)**: The incremental extraction of `setBooleanArg`/`setIntArg` etc. into small, single-purpose methods before pushing them into derivatives applies the same small-function discipline.
- **Ch 10 (Classes)**: The whole `ArgumentMarshaler` extraction and later `ArgsException` extraction are concrete applications of the Single Responsibility Principle discussed in that chapter.
- **Ch 9 (Unit Tests)**: The entire refactoring is only possible because of the JUnit + FitNesse test suite described there — tests as the enabling safety net for fearless refactoring.
- **Ch 17 (Smells and Heuristics)**: Several named smells surface inline (e.g., [G23] switch statements/type-case, [F1] too many function arguments, [N5] poor names) — this chapter is those heuristics applied in real time.
- **Ch 21 (Coding, The Clean Coder)**: The discipline of keeping the system always in a working, releasable state via TDD mirrors the professionalism theme of always being able to ship.
- **Boy Scout Rule**: This chapter is essentially a book-length demonstration of the Boy Scout Rule ("leave the code cleaner than you found it") applied continuously across dozens of small commits rather than one big cleanup.
- **Refactoring (Fowler)**: The technique catalog implicitly used throughout — Extract Class, Extract Method, Replace Conditional with Polymorphism, Replace Type Code with Class.
