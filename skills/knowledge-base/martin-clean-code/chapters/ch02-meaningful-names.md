# Chapter 2: Meaningful Names

## Core Idea
Names are the primary interface between a programmer's intent and a reader's understanding, so choosing them well is not cosmetic — it is one of the highest-leverage acts in writing readable code. A name should answer why something exists, what it does, and how it is used, without requiring a comment to fill in the gap.

## Frameworks Introduced
- **Intention-Revealing Names**: "The name of a variable, function, or class, should answer all the big questions... If a name requires a comment, then the name does not reveal its intent."
  - When to use: every declaration — variables, functions, classes, arguments.
  - How: replace implicit context (`d`, `theList`, `list1`) with explicit domain vocabulary (`elapsedTimeInDays`, `gameBoard`, `flaggedCells`) so the code reads without needing the surrounding comments or the original author's memory.
- **Context via Enclosure over Prefixing**: "you need to place names in context for your reader by enclosing them in well-named classes, functions, or namespaces. When all else fails, then prefixing the name may be necessary as a last resort."
  - When to use: when several related variables (e.g., `firstName`, `state`, `zipcode`) only make sense together.
  - How: prefer extracting a class (`Address`, `GuessStatisticsMessage`) that structurally groups the fields; fall back to prefixes (`addrState`) only if extraction isn't feasible yet.

## Key Concepts
- **Implicity**: Martin's coined term for code whose simplicity hides the fact that critical context (what a container holds, what a magic value means) is not explicit in the code itself.
- **Disinformation**: a name that carries an entrenched, false meaning — e.g., naming a non-`List` container `accountList`, or using near-identical names (`XYZControllerForEfficientHandlingOfStrings` vs. `...StorageOfStrings`) that differ almost invisibly.
- **Noise words**: meaningless filler appended to force uniqueness (`ProductInfo`, `ProductData`, `NameString`, `a`, `the`, `variable`, `table`) that satisfies the compiler but adds no distinct meaning.
- **Hungarian Notation (HN)**: prefixing a name with an encoded type/scope tag (e.g., `pszqint`); a historic crutch for weakly-typed languages, now an active liability in strongly-typed, IDE-assisted languages.
- **Mental Mapping**: forcing the reader to translate a placeholder name (`r`, `c`) into the real concept it stands for, rather than naming the concept directly.
- **Pun (naming)**: reusing the same word for two semantically different operations (e.g., calling both "concatenate" and "insert into collection" `add`).
- **Gratuitous Context**: prefixing every class with an app-wide tag (e.g., `GSD` for "Gas Station Deluxe") that adds length without adding precision and actively hurts IDE autocomplete.
- **Searchability**: a property of a name — long, distinctive names (`WORK_DAYS_PER_WEEK`) can be grepped reliably; single letters and bare numeric literals (`5`, `e`) cannot.

## Mental Models
- Think of a name as a stand-in for a comment: if you need a comment to explain a name, rename instead of annotating (`int d; // elapsed time in days` → `int elapsedTimeInDays;`).
- Use CS/pattern/algorithm vocabulary ("solution domain names," e.g., `AccountVisitor`, `JobQueue`) when talking to programmers about programmer concerns; use domain-expert vocabulary ("problem domain names") when there is no clean technical term, so a maintainer can ask a business expert what it means.
- "The length of a name should correspond to the size of its scope" — a loop index in a 3-line loop can be `i`; anything visible across a wider scope needs a fuller, searchable name.
- Treat renaming as routine maintenance, not a risk: "we are actually grateful when names change (for the better)" — don't let fear of disruption block a better name.

## Anti-patterns
- **Number-series names (`a1`, `a2`, ...`aN`)**: noninformative — provide no clue to intent, unlike disinformative names which actively mislead.
- **Encoding type/scope into names (HN, `m_` prefixes)**: adds a decoding burden, breaks when the underlying type changes (`PhoneNumber phoneString;`), and is unnecessary once compilers/IDEs enforce types.
- **`l` (lowercase L) and `O` (uppercase O) as identifiers**: visually indistinguishable from `1` and `0`.
- **Interface prefix `I` (`IShapeFactory`)**: Martin prefers leaving interfaces unadorned and encoding the implementation instead (`ShapeFactoryImp`) if encoding is unavoidable.
- **Cute/slang names (`HolyHandGrenade`, `whack()` for `kill()`, `eatMyShorts()` for `abort()`)**: memorable only to those sharing the joke; sacrifices clarity for entertainment.
- **Multiple words for one concept (`fetch`/`retrieve`/`get` across classes) and puns (`add` meaning both "sum" and "insert")**: forces readers to memorize arbitrary per-class vocabulary instead of relying on a consistent lexicon.
- **Gratuitous context / redundant prefixes (`GSDAccountAddress`)**: "Ten of 17 characters are redundant or irrelevant" — hurts autocomplete and adds no precision.

## Code Examples
```java
public List<int[]> getThem() {
  List<int[]> list1 = new ArrayList<int[]>();
  for (int[] x : theList)
    if (x[0] == 4)
      list1.add(x);
  return list1;
}
```
- **What it demonstrates**: syntactically simple code can still be unreadable ("implicity") because `theList`, `x[0]`, and `4` carry no revealed intent — contrast with the renamed version below.

```java
public List<Cell> getFlaggedCells() {
  List<Cell> flaggedCells = new ArrayList<Cell>();
  for (Cell cell : gameBoard)
    if (cell.isFlagged())
      flaggedCells.add(cell);
  return flaggedCells;
}
```
- **What it demonstrates**: identical logic and nesting, but intention-revealing names plus a small `Cell` class (replacing raw `int[]` and a magic index) make the purpose self-evident without comments.

## Reference Tables
| Rule | Guidance | Example |
|---|---|---|
| Intention-Revealing | Name should answer why/what/how | `elapsedTimeInDays` not `d` |
| Avoid Disinformation | No entrenched-but-wrong words; no near-identical names | avoid `accountList` for a non-List; avoid `hp`/`aix`/`sco` |
| Meaningful Distinctions | Don't differentiate names only to satisfy the compiler | `source`/`destination` not `a1`/`a2` |
| Pronounceable | Names must be sayable in conversation | `generationTimestamp` not `genymdhms` |
| Searchable | Scope size should drive name length/searchability | `WORK_DAYS_PER_WEEK` not bare `5` |
| Avoid Encodings | No Hungarian Notation, no `m_` prefixes | `description` not `m_dsc` |
| Interfaces vs. Impl | Leave interface name unadorned; encode the impl if needed | `ShapeFactory` / `ShapeFactoryImp` |
| Avoid Mental Mapping | No cryptic single-letter stand-ins outside tiny loop scopes | avoid `r` for a stripped URL |
| Class Names | Noun/noun phrase; avoid `Manager`, `Processor`, `Data`, `Info` | `Customer`, `AddressParser` |
| Method Names | Verb/verb phrase; `get`/`set`/`is` for accessors per JavaBean convention | `postPayment`, `isPosted()` |
| Don't Be Cute | Clarity over jokes/slang | `deleteItems()` not `holyHandGrenade()` |
| One Word per Concept | Pick one verb per abstract operation, use consistently | pick `get`, not `get`/`fetch`/`retrieve` mixed |
| Don't Pun | Same word must mean the same operation everywhere | use `insert`/`append`, not overloaded `add` |
| Solution vs. Problem Domain | Use CS terms for programmer concerns; domain terms otherwise | `AccountVisitor`, `JobQueue` |
| Add Meaningful Context | Group related names in a class/function rather than scattering | `Address` class vs. loose `state`, `zipcode` |
| No Gratuitous Context | Don't prefix every name with the app/module name | `Address` not `GSDAccountAddress` |

## Worked Example
Martin walks through `printGuessStatistics`, a method with three loosely related local variables — `number`, `verb`, `pluralModifier` — built up inside conditional branches and then combined into a `guessMessage` string. Read cold, the variables are opaque: nothing states they jointly represent parts of a "guess statistics" sentence; that context has to be inferred by reading the whole method. The fix is not a rename but an extraction: pull the three variables out as fields of a new `GuessStatisticsMessage` class, and split the branching logic into small, well-named private methods (`thereAreNoLetters()`, `thereIsOneLetter()`, `thereAreManyLetters(count)`) called from a `createPluralDependentMessageParts` helper. Once the class exists, the compiler itself enforces that the three fields belong together, the algorithm becomes easier to decompose, and the top-level `make()` method reads as a short, clear composition of intention-revealing calls.

## Key Takeaways
1. If a name needs an explanatory comment, that's a signal to rename it, not to comment it.
2. Never let two names differ only by a noise word, number suffix, or misspelling — differences in name must reflect differences in meaning.
3. Say names out loud before committing to them; unpronounceable names degrade team communication.
4. Match name length/searchability to scope size: tiny-scope loop counters can be one letter, anything broader needs a distinctive, greppable name.
5. Drop Hungarian Notation, `m_` prefixes, and interface `I`-prefixes in modern statically-typed, IDE-assisted languages — they add decoding cost without safety benefit.
6. Use one consistent verb per abstract operation across the codebase (no `fetch`/`get`/`retrieve` sprawl) and never reuse a word for semantically different operations (no puns).
7. Give related variables a real home — a class, function, or namespace — instead of leaning on ad hoc prefixes or hoping the reader infers the connection; but don't over-prefix with app-wide gratuitous context either.

## Connects To
- **Ch 3 (Functions)**: naming discipline directly enables the small-function extraction shown in the `GuessStatisticsMessage` worked example — good names make short functions self-documenting.
- **Ch 4 (Comments)**: the intention-revealing-names rule is this book's primary argument for why most comments are a failure to name well, foreshadowing Ch 4's stance that comments compensate for unclear code.
- **Ch 9 (Classes)**: the noun/verb naming split for classes vs. methods and the "avoid Manager/Processor/Data" guidance set up Ch 9's deeper treatment of class responsibility and cohesion.
- **Refactoring vocabulary (Fowler)**: "rename" as a first-class, low-risk refactoring move underlies Martin's insistence that renaming for clarity should never be feared.
