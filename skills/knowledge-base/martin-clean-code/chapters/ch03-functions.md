# Chapter 3: Functions

## Core Idea
Functions are the first unit of organization in a program; they should be small, do exactly one thing at one level of abstraction, and be named so descriptively that reading them top-to-bottom tells a coherent story.

## Frameworks Introduced
- **Small!**: "The first rule of functions is that they should be small. The second rule of functions is that they should be smaller than that."
  - When to use: always — as the default constraint on every function you write.
  - How: keep blocks inside `if`/`else`/`while` to one line (usually a function call); keep indent level to one or two; functions should "hardly ever be 20 lines long."
- **Do One Thing**: "FUNCTIONS SHOULD DO ONE THING. THEY SHOULD DO IT WELL. THEY SHOULD DO IT ONLY."
  - When to use: as a test for whether a function needs further extraction.
  - How: a function does one thing if all its steps are one level of abstraction below the function's stated name (expressible as a single "TO" paragraph). If you can extract another function with a name that isn't a restatement of the implementation, the original was doing more than one thing.
- **One Level of Abstraction per Function**: statements within a function must all sit at the same level of abstraction (don't mix `getHtml()` with `.append("\n")`).
  - When to use: whenever a function mixes high-level intent with low-level detail.
  - How: extract the low-level operations into well-named sub-functions until every line in the caller reads at the same conceptual altitude.
- **The Stepdown Rule**: "We want every function to be followed by those at the next level of abstraction so that we can read the program, descending one level of abstraction at a time."
  - When to use: to organize the order of functions within a file/class.
  - How: write the program as a set of nested "TO" paragraphs — each function introduces and is immediately followed by the functions it calls, one level down.
- **Command Query Separation**: "Functions should either do something or answer something, but not both."
  - When to use: whenever naming a function forces a verb/adjective ambiguity (e.g., `set()`).
  - How: split into a query (`attributeExists()`) and a command (`setAttribute()`) instead of one function that both mutates and returns a status.
- **Prefer Exceptions to Returning Error Codes**: replacing error-code returns with exceptions is itself a form of command/query cleanup.
  - When to use: any command function currently returns a status/error code checked in an `if`.
  - How: throw on failure; move error handling out of the happy path via extracted try/catch functions.

## Key Concepts
- **Niladic/Monadic/Dyadic/Triadic/Polyadic**: functions of zero, one, two, three, and more-than-three arguments, respectively — Martin's preference ordering, most-to-least desirable.
- **Flag argument**: a boolean parameter that signals a function does two different things depending on its value; considered a smell.
- **Output argument**: an argument used to carry information back out of a function rather than in; harder to understand than input arguments and largely obsoleted by OO (`this`).
- **Common monadic forms**: single-argument functions are either a question (`fileExists(name)`), a transformation (`fileOpen(name)` returning a new type), or an event (`passwordAttemptFailedNtimes(n)`, no return value).
- **Argument object**: when 2-3 related arguments recur together (e.g., `x, y`), wrap them into a class of their own (`Point`) — reduces arity and names a concept.
- **Verb/keyword form**: encoding argument meaning into the function name itself, e.g., `assertExpectedEqualsActual(expected, actual)`, to remove ambiguity about argument order.
- **Side effect**: an undocumented, hidden action a function performs beyond what its name promises (e.g., `checkPassword()` silently calling `Session.initialize()`), creating temporal coupling.
- **Temporal coupling**: a hidden requirement that functions be called in a particular order/time window because of side effects.
- **Extract Try/Catch Blocks**: pulling the bodies of `try` and `catch` into their own well-named functions so the function containing `try` does error handling and nothing else.
- **Error.java dependency magnet**: a shared error-code enum that many classes must import, so every new error code forces a system-wide recompile/redeploy — avoided by using exception subclasses instead.

## Mental Models
- Think of functions as the **verbs** of a system's domain-specific language, and classes as its **nouns** — programming is language design, and systems are stories to be told.
- Use the **Stepdown Rule / TO-paragraph** framing when ordering functions: read the file top to bottom like nested "TO do X, we do A, then B" narration descending one abstraction level per hop.
- Treat a **switch statement** as tolerable only when it appears exactly once, builds polymorphic objects, and is buried behind an inheritance boundary (an ABSTRACT FACTORY) — never scattered through the codebase.
- Writing functions is like drafting prose: **write it messy first, then refine** — clean functions are the product of iterative refactoring under test coverage, not first-draft output.

## Anti-patterns
- **Long functions with mixed abstraction levels**: readers can't tell if a line is an essential concept or an incidental detail; details accrete "like broken windows" once mixed in.
- **Functions divided into internal sections** (declarations/initializations/etc.): a symptom the function is doing more than one thing — a true single-purpose function can't be meaningfully sectioned.
- **Repeated switch/if-else chains keyed on type**: violates SRP and OCP, grows unbounded as new cases/functions are added; fix by hiding the switch in a factory and dispatching polymorphically.
- **Flag arguments**: `render(true)` forces the reader to look up the signature to know what "true" means; should be split into two differently named functions.
- **Output arguments in OO code**: `appendFooter(s)` is ambiguous about direction; prefer `report.appendFooter()` so the object being mutated is the receiver, not a parameter.
- **Triadic+ argument lists**: ordering, pausing, and "parts we ignore" (where bugs hide) compound with each added argument; `assertEquals(message, expected, actual)` causes recurring double-takes.
- **Error codes checked via nested `if`**: forces the caller to handle errors immediately and produces deep nesting; exceptions let happy-path and error-path code separate cleanly.
- **Duplicated algorithms** (the four near-identical setup/teardown blocks in the original example): bloats code and creates a four-fold risk of an error of omission when the logic changes.

## Code Examples
```java
// Before: HtmlUtil.testableHtml — long, multi-level-abstraction, duplicated logic
public static String testableHtml(PageData pageData, boolean includeSuiteSetup)
    throws Exception {
  WikiPage wikiPage = pageData.getWikiPage();
  StringBuffer buffer = new StringBuffer();
  if (pageData.hasAttribute("Test")) {
    if (includeSuiteSetup) {
      WikiPage suiteSetup = PageCrawlerImpl.getInheritedPage(
          SuiteResponder.SUITE_SETUP_NAME, wikiPage);
      // ... nested path rendering, string appends, repeated 4x for
      // SetUp / SuiteSetUp / TearDown / SuiteTearDown
    }
  }
  // ...
}
```
- **What it demonstrates**: doubly-nested conditionals, mixed abstraction levels, and duplicated logic — the "before" state that the chapter's extraction techniques dismantle.

```java
// After: same behavior, three well-named steps at one abstraction level
public static String renderPageWithSetupsAndTeardowns(
    PageData pageData, boolean isSuite) throws Exception {
  if (isTestPage(pageData))
    includeSetupAndTeardownPages(pageData, isSuite);
  return pageData.getHtml();
}
```
- **What it demonstrates**: the Stepdown Rule and "Do One Thing" applied — the caller reads as a single TO-paragraph, delegating detail to named sub-functions.

```java
// Extract Try/Catch: error handling isolated from the happy path
public void delete(Page page) {
  try {
    deletePageAndAllReferences(page);
  } catch (Exception e) {
    logError(e);
  }
}
private void deletePageAndAllReferences(Page page) throws Exception {
  deletePage(page);
  registry.deleteReference(page.name);
  configKeys.deleteKey(page.name.makeKey());
}
private void logError(Exception e) {
  logger.log(e.getMessage());
}
```
- **What it demonstrates**: "Error handling is one thing" — `delete` does only error handling, `deletePageAndAllReferences` does only deletion, `try` is the first word in its function.

## Reference Tables
| Argument count | Name | Martin's guidance |
|---|---|---|
| 0 | Niladic | Ideal |
| 1 | Monadic | Next best; use for a question, a transformation, or an event |
| 2 | Dyadic | Avoid where possible; convert to monad via member function, member variable, or extracted class |
| 3 | Triadic | Avoid; think very carefully before creating one |
| 3+ | Polyadic | Requires special justification; generally don't use |

## Worked Example
The chapter reconstructs `HtmlUtil.testableHtml` (FitNesse) as `SetupTeardownIncluder`. Starting point: one long static method that builds an HTML test page by (1) checking if the page is a test page, (2) conditionally including suite setup then regular setup, (3) appending page content, (4) including teardown then suite teardown, all via manually rendered wiki paths and raw `StringBuffer` appends — four near-duplicate blocks for SetUp/SuiteSetUp/TearDown/SuiteTearDown. Martin refactors in stages: first extracting `includeSetupPages`/`includeTeardownPages` (Listing 3-2, 9 lines), then collapsing further to a 3-line function calling `isTestPage` and `includeSetupAndTeardownPages` (Listing 3-3). The final form, `SetupTeardownIncluder` (Listing 3-7), is a small class: a public static `render` entry point, a private constructor capturing `pageData`/`testPage`/`pageCrawler`, and a cascade of tiny private methods (`includeSetupAndTeardownPages` → `includeSetupPages`/`includePageContent`/`includeTeardownPages`/`updatePageContent`, each calling further down to `include(pageName, arg)` → `findInheritedPage`/`getPathNameForPage`/`buildIncludeDirective`). Every method is a few lines, every name is a verb/noun pair matching its sibling names (`includeSetupPage`, `includeSuiteSetupPage`, `includeTeardownPage`, `includeSuiteTeardownPage`), and reading top to bottom follows the Stepdown Rule exactly — each function is immediately followed by the functions it calls at the next level down. The four-fold duplication collapses into the single shared `include` helper.

## Key Takeaways
1. Default every function toward "smaller than you think it should be" — extract until each function does one thing at one level of abstraction.
2. Order functions using the Stepdown Rule so the file reads top-down as a narrative descending through abstraction levels.
3. Bury unavoidable `switch`/type-check logic in exactly one place — a low-level factory — and dispatch the rest polymorphically.
4. Minimize argument count; prefer 0-1 arguments, convert dyads to monads via member state or extracted classes, and never use flag or output arguments.
5. Separate commands from queries, and prefer exceptions over error-code returns so error handling can be extracted away from the happy path.
6. A function containing `try` should do nothing but error handling — extract the try body and catch body into their own named functions.
7. Eliminate duplication aggressively (DRY) — it's a four-fold (or N-fold) risk multiplier whenever logic changes; clean functions are reached by iterative refactoring, not written clean on the first pass.

## Connects To
- **Ch 2 (Meaningful Names)**: descriptive function naming here directly builds on the naming discipline from Chapter 2 — "the smaller and more focused a function is, the easier it is to choose a descriptive name."
- **Ch 5 (Formatting)**: the Stepdown Rule dictates vertical ordering of functions, which Formatting's newspaper-metaphor and vertical-distance rules elaborate further.
- **Ch 6 (Objects and Data Structures)**: output-argument avoidance ("have it change the state of its owning object") assumes OO encapsulation — ties directly into the objects-vs-data-structures distinction.
- **Ch 7 (Error Handling)**: "Prefer Exceptions to Returning Error Codes" and "Extract Try/Catch Blocks" here are previewed/expanded fully in Chapter 7's dedicated treatment of exceptions.
- **Ch 9 (Unit Tests)**: the "How Do You Write Functions Like This?" section depends on having a full suite of unit tests to safely refactor messy first drafts into clean functions.
- **Ch 17 (Smells and Heuristics)**: several named rules here (G23 hidden switch/polymorphism, G34 function does more than one thing) are cross-referenced directly to the smells catalog in Chapter 17.
- **External concept — Single Responsibility Principle / Open Closed Principle**: cited explicitly as the design principles violated by type-switching functions, motivating the polymorphic-factory solution.
