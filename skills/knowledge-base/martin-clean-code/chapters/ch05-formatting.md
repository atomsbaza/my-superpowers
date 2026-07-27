# Chapter 5: Formatting

## Core Idea
Code formatting is a communication discipline, not an aesthetic afterthought: consistent, deliberate vertical and horizontal layout makes a codebase's structure and intent legible, and that legibility outlives the specific functionality the code implements.

## Frameworks Introduced
- **The Newspaper Metaphor**: a source file should read like a well-written newspaper article — name/headline at the top telling you what it's about, a synopsis (high-level concepts) immediately below, and increasing detail as you move downward, ending in the lowest-level functions and details.
  - When to use: whenever structuring a source file or class from top to bottom.
  - How: put a simple, explanatory name on the file; place high-level concepts and algorithms at the top; order functions so callers precede callees; push low-level detail to the bottom so a reader can skim the top and stop before drowning in detail.
- **Vertical Formatting Rules** (openness, density, distance, ordering): a set of four complementary rules governing how lines and blocks relate to each other top-to-bottom within a file.
  - When to use: any time you add, remove, or reorder code within a file.
  - How: separate distinct concepts with blank lines (openness); keep tightly related lines free of interrupting blank lines or comments (density); keep related concepts near each other and order declarations predictably (distance); order functions so high-level/caller code sits above the lower-level/callee code it depends on (ordering).
- **Horizontal Formatting Rules** (line length, openness/density, alignment, indentation): governs how a single line and its immediate context should read left-to-right.
  - When to use: writing any individual line or block of declarations.
  - How: keep lines short (rule of thumb ~120 chars max); use spacing to separate weakly-related tokens and omit it between tightly-related ones; avoid manual alignment of declarations/assignments; indent strictly according to scope depth, even for single-line bodies.

## Key Concepts
- **Vertical openness**: blank lines used as a visual cue to separate distinct concepts (e.g., package declaration, imports, each function) so the eye can identify where one thought ends and another begins.
- **Vertical density**: the absence of unnecessary blank lines or comments between lines that are tightly related, so they read as one visual "eye-full."
- **Vertical distance**: the principle that concepts closely related in meaning should be kept physically close in the file, minimizing the reader's need to scroll and hunt.
- **Vertical ordering**: the convention that a calling function appears above the functions it calls, producing a top-down flow from high-level to low-level code.
- **Conceptual affinity**: a non-dependency-based reason for two pieces of code to be kept close together, such as performing variations of the same operation or sharing a naming scheme.
- **Horizontal openness/density**: use of whitespace within a line to visually separate loosely related elements (e.g., around `=`) while omitting it between tightly bound elements (e.g., function name and its parenthesis) to signal precedence and association.
- **Indentation**: whitespace prefixing a line that encodes its depth in the file's scope hierarchy (file → class → method → block), letting readers visually "hop over" irrelevant scopes.
- **Dummy scope**: an empty loop/conditional body (e.g., a lone semicolon) that is easy to miss visually unless deliberately indented onto its own line and made visible.
- **Team rules**: a single, team-agreed formatting standard, ideally enforced by an automated formatter, that overrides any individual developer's personal preference.

## Mental Models
- **The file as a hierarchy/outline**: a source file mirrors nested scopes (file, class, method, block), and indentation is the visual encoding of that hierarchy — remove it and the structure becomes unreadable even though the code is unchanged semantically.
- **Style survives, code doesn't**: today's functionality will likely be rewritten, but the formatting discipline and readability precedent you set will keep affecting the codebase's maintainability long after the original code is gone.
- **Formatting as skimming support**: good vertical ordering and density let a reader get the gist from the first few functions without immersing in every detail — analogous to reading only the headline and lead paragraph of a newspaper article.
- **The team, not the individual, owns style**: "every programmer has his own favorite formatting rules, but if he works in a team, then the team rules" — personal preference is subordinate to consistency.

## Anti-patterns
- **Removing blank lines between concepts**: collapses visually distinct ideas into a "muddle," destroying the reader's ability to scan for new thoughts (Listing 5-2 vs 5-1).
- **Interrupting closely related lines with comments or blank lines**: breaks the "eye-full" association, as in unnecessary Javadoc comments splitting two instance variable declarations that belong together.
- **Burying instance variables mid-class**: hiding declarations somewhere other than a single well-known location (top of class) forces readers to stumble across them by accident.
- **Placing callee functions before or far from their caller**: forces readers to hop around the file instead of reading top-down; breaks the newspaper flow.
- **Manual horizontal alignment of declarations/assignments**: emphasizes the wrong tokens (e.g., variable names over types), draws the eye away from true intent, and is undone by auto-formatters anyway; if a list needs alignment to be readable, the real problem is that the list is too long (the class should be split).
- **Collapsing short if/while/function bodies onto one line**: breaking the indentation rule "for short" scopes reduces readability; the author reports always reverting this when tempted.
- **Invisible dummy scopes**: a semicolon sitting silently at the end of a `while` line (empty body) is easily missed and causes bugs of misreading; must be indented on its own line and/or braced to be visible.
- **Inconsistent per-developer styles on a team**: produces code that reads as if "written by a bunch of disagreeing individuals," adding cognitive overhead unrelated to the actual logic.

## Code Examples
```java
// Vertical density violation vs. fix (Listing 5-3 -> 5-4)
public class ReporterConfig {
    private String m_className;
    private List<Property> m_properties = new ArrayList<Property>();

    public void addProperty(Property property) {
        m_properties.add(property);
    }
}
```
- **What it demonstrates**: removing interrupting comments between the two instance variables restores vertical density so the class reads as one coherent "eye-full."

```java
// Horizontal spacing signals operator precedence
public static double root1(double a, double b, double c) {
    double determinant = determinant(a, b, c);
    return (-b + Math.sqrt(determinant)) / (2*a);
}
private static double determinant(double a, double b, double c) {
    return b*b - 4*a*c;
}
```
- **What it demonstrates**: no space around high-precedence `*` factors, but space around lower-precedence `+`/`-` terms, making the expression's structure visible at a glance.

## Reference Tables
| Rule | Guideline |
|---|---|
| File size | ~200 lines typical, ~500 lines upper bound (observed across FitNesse, JUnit, etc.) |
| Line length | Avoid scrolling; author personally caps at 120 characters (80 is classic, up to 100–120 acceptable) |
| Variable declaration | As close to first use as possible; loop control variables declared inside the loop statement |
| Instance variables | Declared in one well-known place — top of the class (Java convention) |
| Function ordering | Caller above callee, high-level to low-level, top to bottom |

## Worked Example
The chapter walks through `FitNesseExpediter`'s field declarations and constructor to illustrate horizontal alignment. The author originally aligned types and variable names in columns (`private   Socket          socket; private   InputStream     input; ...`), a habit carried over from assembly-language work. He then shows the same code unaligned (`private Socket socket; private InputStream input; ...`) and explains that manual alignment tempts the reader to scan down just the variable names or just the rvalues, ignoring the types or operators next to them — the wrong emphasis. He concludes he no longer aligns declarations, and that if a list of declarations is long enough to seem to need alignment, the real problem is that the list (and likely the class) is too long and should be split up rather than reformatted.

## Key Takeaways
1. Treat formatting as a communication tool with the same seriousness as naming or function design — it's not optional polish.
2. Structure files like newspaper articles: informative name, high-level summary near the top, increasing detail downward.
3. Use blank lines to separate distinct concepts (vertical openness) and remove interrupting comments/blank lines between tightly related lines (vertical density).
4. Declare variables close to their use; put instance variables in one consistent, well-known location (top of class).
5. Order functions so callers appear above callees, creating a top-down, skimmable flow.
6. Keep lines reasonably short (roughly 80–120 chars) and use whitespace deliberately to show which tokens are tightly vs. loosely related.
7. Never break indentation for short bodies, and always make dummy/empty scopes visually explicit; agree on one team-wide formatting standard, ideally automated.

## Connects To
- **Ch 3 (Functions)**: short, well-named functions are what make vertical ordering and the newspaper metaphor practical — a file of many small functions is easy to arrange top-down.
- **Ch 4 (Comments)**: this chapter shows comments can actively harm vertical density (e.g., Javadoc splitting related instance variables), reinforcing Ch 4's caution against unnecessary comments.
- **Ch 9 (Classes)**: the instance-variable-placement discussion and the "long declaration list means the class should be split" observation both foreshadow class-size and cohesion concerns covered in the Classes chapter.
- **Ch 17 (Smells and Heuristics)**: several rules here (e.g., G10 vertical distance, G35 keeping constants at appropriate levels) are drawn from and cross-referenced with the heuristics catalog.
- **Automated code formatters**: the chapter's practical recommendation is to encode team formatting rules into an IDE/tool formatter rather than relying on manual discipline.
