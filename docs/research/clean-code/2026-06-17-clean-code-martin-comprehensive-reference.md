# Research: Clean Code — A Handbook of Agile Software Craftsmanship by Robert C. Martin

## Summary

*Clean Code: A Handbook of Agile Software Craftsmanship* (Robert C. Martin, Prentice Hall, 2008) is the definitive practitioner reference for writing readable, maintainable, professional software. The book covers naming, function design, comments, formatting, object design, error handling, boundaries, testing, class design, system architecture, emergence, concurrency, and a comprehensive appendix of code smells and heuristics. The central thesis is that code is read far more often than it is written, and every decision — from a variable name to the shape of a class — should optimize for the next reader. This document synthesizes all major chapters and the complete heuristics appendix at sufficient depth for an AI agent to apply the principles directly to code review, refactoring, and implementation tasks.

---

## Chapter 2 — Meaningful Names

### Core Principle

Names are the primary communication mechanism in code. Every name — variable, function, class, package, argument, file — should reveal intent without requiring a comment to explain it.

### Use Intention-Revealing Names

A name should tell you why something exists, what it does, and how it is used. If a name requires a comment, the name is wrong.

**Bad:**
```java
int d; // elapsed time in days
```

**Clean:**
```java
int elapsedTimeInDays;
int daysSinceCreation;
int fileAgeInDays;
```

### Avoid Disinformation

- Do not use names that carry false connotations. Do not call a collection `accountList` unless it is actually a `List`. Prefer `accountGroup` or `accounts`.
- Do not use names that differ only in small ways: `XYZControllerForEfficientHandlingOfStrings` vs `XYZControllerForEfficientStorageOfStrings` are nearly indistinguishable.
- Avoid using lowercase `l` or uppercase `O` as variable names — they are visually identical to `1` and `0`.

### Make Meaningful Distinctions

Noise words create no distinction. If names must differ, the difference must mean something to the reader.

**Bad:**
```java
getActiveAccount();
getActiveAccounts();
getActiveAccountInfo();
```
The reader cannot know which to call.

**Bad noise words:**
```java
ProductInfo   // vs
ProductData   // "Info" and "Data" are indistinguishable noise
```

**Bad:** Never use `a1`, `a2`, `aN` as positional series names. They communicate nothing.

### Use Pronounceable Names

**Bad:**
```java
private Date genymdhms; // generation year month day hour minute second
```

**Clean:**
```java
private Date generationTimestamp;
```

If you cannot pronounce a name, you cannot discuss it intelligently with a colleague.

### Use Searchable Names

Single-letter names and numeric constants are not searchable. The length of a name should correspond to the size of its scope. Single-letter variables are acceptable only as loop counters in tiny, local scopes (`for (int i = 0; i < 5; i++)`).

**Bad:**
```java
for (int j = 0; j < 34; j++) {
    s += (t[j] * 4) / 5;
}
```

**Clean:**
```java
int realDaysPerIdealDay = 4;
final int WORK_DAYS_PER_WEEK = 5;
int sum = 0;
for (int j = 0; j < NUMBER_OF_TASKS; j++) {
    int realTaskDays = taskEstimate[j] * realDaysPerIdealDay;
    int realTaskWeeks = (realTaskDays / WORK_DAYS_PER_WEEK);
    sum += realTaskWeeks;
}
```

### Avoid Encodings

**Hungarian Notation** was necessary when compilers didn't check types. Modern IDEs and compilers make it redundant and noise-generating.

**Bad:**
```java
PhoneNumber phoneString; // type is not a string, the name encodes wrong type
String strName;
int iCount;
```

**Member prefixes** are similarly obsolete:
```java
// Bad
private String m_dsc;

// Clean
private String description;
```

**Interface prefixes:** The `I` prefix (e.g., `IShapeFactory`) is noise. Prefer the clean name for the interface (`ShapeFactory`) and encode the implementation if necessary (`ShapeFactoryImpl` or `CShapeFactory`). Martin's preference is to keep the interface name clean and encode the implementation.

### Avoid Mental Mapping

Readers should not have to mentally translate names to something meaningful. Single-letter names require mental mapping. A professional programmer uses clarity over cleverness.

**Common violation:** Using `r` for a filtered `url` string when `r` forces the reader to remember what `r` means.

### Class Names: Nouns

Class names should be nouns or noun phrases: `Customer`, `WikiPage`, `Account`, `AddressParser`.

**Avoid:** verbs, and noise words such as `Manager`, `Processor`, `Data`, `Info` — these indicate the class does too much.

### Method Names: Verbs

Method names should be verbs or verb phrases: `postPayment`, `deletePage`, `save`.

Accessors, mutators, and predicates should follow the JavaBean convention: `getName`, `setName`, `isPosted`.

When constructors are overloaded, use static factory methods with names describing the argument:
```java
// Prefer this
Complex fulcrumPoint = Complex.fromRealNumber(23.0);

// Over this
Complex fulcrumPoint = new Complex(23.0);
```

### Don't Be Cute

Prefer clarity over entertainment value. `deleteItems` is better than `holyHandGrenade`. `abort` is better than `eatMyShorts`. Say what you mean; mean what you say.

### Pick One Word per Concept

Pick one word for one abstract concept and stick with it throughout the codebase. Having `fetch`, `retrieve`, and `get` as equivalent methods in different classes is confusing. Similarly, a `controller`, a `manager`, and a `driver` in the same codebase: what is the difference?

### Don't Pun

Do not use the same word for two purposes. If you use `add` for building a concatenated value in one class, don't use `add` in another class to mean inserting into a collection — prefer `insert` or `append`.

### Use Solution Domain Names

Readers are programmers. Use computer science terms, algorithm names, pattern names, math terms where appropriate: `AccountVisitor` (Visitor pattern), `JobQueue`, `nameMap`.

### Use Problem Domain Names

When there is no programmer term, use the problem domain name. Code that relates more to problem domain concepts should have problem domain names.

### Add Meaningful Context

Names rarely are self-explanatory in isolation — context comes from enclosing classes, functions, and namespaces. When context is not provided by the enclosing structure, prefixes may be added as a last resort.

**Bad:** `state` alone is ambiguous; `addrState` as part of an address structure provides context — but better still is an `Address` class with a `state` field.

### Don't Add Gratuitous Context

For a mail app called `Gas Station Deluxe`, prefixing every class with `GSD` is noise. Shorter names are better than longer names, when they are equally clear.

---

## Chapter 3 — Functions

### Functions Should Be Small

The first rule of functions is that they should be small. The second rule is that they should be smaller than that. In Martin's view, functions should be no more than 20 lines, and ideally 4–5 lines. Every function should tell a story at exactly one level of abstraction.

**Bad:** A 100-line function that sets up the environment, iterates a list, checks conditions, formats output, and handles errors — all mixed together.

**Clean:** Multiple small functions, each named for exactly what it does.

### Blocks and Indenting

Blocks within `if`, `else`, `while` statements should be one line long — almost always a function call. This means functions should not be large enough to hold nested structures. The indent level should not be greater than one or two.

### Do One Thing

**Functions should do one thing. They should do it well. They should do it only.**

A function does one thing if you cannot meaningfully extract another function from it with a name that is not a restatement of its implementation. If a function has sections labeled with comments — setup, processing, cleanup — it is doing more than one thing.

**Common violation:** Functions named `saveAndValidate()`, `fetchAndProcess()` — the "and" reveals two responsibilities.

### One Level of Abstraction per Function

Mixing levels of abstraction within a function is confusing. Reading `getHtml()` (high abstraction), `.append("\n")` (low abstraction), and `PathParser.render(pagePath)` (intermediate) in the same function mixes levels that belong in different places.

### The Step-Down Rule (Newspaper Metaphor)

Code should read like a top-down narrative. Every function is followed by those at the next level of abstraction, so that the code reads like a set of TO paragraphs:

- TO render the page, we check the page and render the setup sections.
- TO check the page, we determine whether it is a test page.
- TO render the setup sections, we include the suite setup if the page is a suite.

This "step-down rule" means the most abstract operations are at the top, and the most detailed implementations are progressively further down the file.

### Function Arguments

The ideal number of arguments is zero (niladic). One argument (monadic) is next best. Two arguments (dyadic) should be used only with strong justification. Three arguments (triadic) should be avoided wherever possible. More than three (polyadic) requires very special justification and is almost always wrong.

**Why arguments are hard:**
- Arguments require readers to understand the conceptual relationship between function and argument.
- Testing effort multiplies: all meaningful combinations must be exercised.
- Output arguments are particularly confusing (more below).

**Monadic forms (legitimate):**
1. Asking a question about the argument: `boolean isFileExists(File file)`
2. Transforming the argument and returning it: `InputStream fileOpen(String name)`
3. Events — using the argument to alter the system with no return value: `void passwordAttemptFailedNtimes(int attempts)`

**Bad monadic:** Functions that transform but return nothing; functions that use one argument as both input and output.

**Flag Arguments** are ugly. Passing a boolean into a function proclaims that it does two things. Split the function:
```java
// Bad
render(boolean isSuite)

// Clean
renderForSuite()
renderForSingleTest()
```

**Dyadic functions** are harder to understand than monadic. `writeField(name)` is easier than `writeField(outputStream, name)`. Dyadic functions are appropriate when the two arguments are ordered components of a single value: `new Point(0, 0)`. The problems arise when the arguments have no natural ordering.

**Argument objects:** When a function needs more than two or three arguments, wrap some of them into a class:
```java
// Bad
Circle makeCircle(double x, double y, double radius);

// Clean
Circle makeCircle(Point center, double radius);
```

**Argument lists:** Variadic functions like `String.format(String format, Object... args)` — when the variable arguments are treated identically, the function is effectively dyadic (or triadic with the format string).

**Verbs and keywords:** For monadic functions, the function and argument should form a verb/noun pair: `writeField(name)`. For dyadic, encode argument names in the function name: `assertExpectedEqualsActual(expected, actual)`.

### Have No Side Effects

Side effects are lies. A function promises to do one thing but secretly does something else. The `checkPassword` function that also calls `Session.initialize()` as a side effect is deceptive — the caller who uses `checkPassword` to verify credentials does not expect the session to be initialized.

**Common violation:** Output arguments. If a function must change the state of something, have it change the state of its owning object.

```java
// Bad — output argument
appendFooter(StringBuffer report);

// Clean — change state of owning object
report.appendFooter();
```

### Command-Query Separation

Functions should either do something (command) or answer something (query), but never both. A function that changes state and also returns a boolean about that state causes confusion:

```java
// Bad — command and query mixed
if (set("username", "bob")) { ... }
// Is this asking "was 'username' set to 'bob'?" or "did setting 'username' to 'bob' succeed?"

// Clean
if (attributeExists("username")) {
    setAttribute("username", "bob");
}
```

### Prefer Exceptions to Returning Error Codes

Returning error codes from command functions violates command-query separation. They also lead to deeply nested structures as the caller must check the error code immediately:

```java
// Bad
if (deletePage(page) == E_OK) {
    if (registry.deleteReference(page.name) == E_OK) {
        if (configKeys.deleteKey(page.name.makeKey()) == E_OK) {
            logger.log("page deleted");
        } else {
            logger.log("configKey not deleted");
        }
    } else {
        logger.log("deleteReference from registry failed");
    }
} else {
    logger.log("delete failed");
    return E_ERROR;
}

// Clean
try {
    deletePage(page);
    registry.deleteReference(page.name);
    configKeys.deleteKey(page.name.makeKey());
} catch (Exception e) {
    logger.log(e.getMessage());
}
```

**Error handling is one thing.** A function that handles errors should do nothing else. Extract the try-catch body into their own functions.

### Don't Repeat Yourself (DRY)

Duplication is the root of all evil in software. Every time you repeat a block of logic, you multiply the places where a future change must be made and multiply the risk of inconsistency. Structured programming, object-oriented programming, aspect-oriented programming, and component-oriented programming are all in some sense strategies for eliminating duplication.

### Structured Programming

Dijkstra's structured programming rule: every function and every block within a function should have one entry and one exit. That means only one `return` per function, no `break` or `continue` in loops, never `goto`. For small functions these rules add little benefit — multiple `return` statements are acceptable and often clarifying in small functions.

---

## Chapter 4 — Comments

### Comments Are Always Failures

Martin's controversial position: every comment is a failure to express something in code. The correct medium for intent is code itself. Comments cannot be kept in sync with code as code changes, and they lie. Strive to express yourself in code; use comments only where code cannot suffice.

### Good Comments

**Legal comments:** Copyright and authorship statements at the top of source files are necessary and appropriate.

**Informative comments:** Sometimes useful to explain a return value when the function name alone cannot fully convey it:
```java
// format matched kk:mm:ss EEE, MMM dd, yyyy
Pattern timeMatcher = Pattern.compile("\\d*:\\d*:\\d* \\w*, \\w* \\d*, \\d*");
```

**Explanation of intent:** Sometimes a comment is useful to explain the reasoning behind a decision, not merely what the code does. This communicates the programmer's intent:
```java
// We tried to use the Java API but discovered
// that it was more performant to sort the list
// ourselves when dealing with large datasets
```

**Clarification comments:** Sometimes a comment is useful to translate an obscure argument or return value into something readable, when the argument is from a library you cannot alter:
```java
assertTrue(a.compareTo(b) != 0); // a != b
assertTrue(a.compareTo(b) ==  1); // a > b
```
These are risky — they must be verified for accuracy.

**Warning comments:** Warning other programmers about consequences:
```java
// Don't run unless you have some time to kill.
public void _testWithReallyBigFile() { ... }
```

**TODO comments:** Jobs the programmer thinks should be done but cannot do for some reason. Not an excuse to leave bad code; they should be reviewed and cleaned periodically.

**Amplification:** A comment can amplify the importance of something that might otherwise seem trivial:
```java
String listItemContent = match.group(3).trim();
// the trim is real important.  It removes the starting
// spaces that could cause the item to be recognized
// as another list.
```

**Javadoc in public APIs:** Well-maintained Javadoc for a public API is invaluable.

### Bad Comments

**Mumbling:** A comment written carelessly, just to have a comment, or to satisfy a process. If you write a comment, invest the time to write a good one.

**Redundant comments:** A comment that describes what the code already says clearly. It takes longer to read than the code itself and is less precise:
```java
// Utility method that returns when this.closed is true.
// Throws an exception if the timeout is reached.
public synchronized void waitForClose(final long timeoutMillis) throws Exception { ... }
```
The function signature already says this.

**Mandated comments:** It is foolish to require that every function must have a Javadoc or every variable must have a comment. This leads to noise and clutters the code:
```java
/**
 * @param title The title of the CD
 * @param author The author of the CD
 */
public void addCD(String title, String author) { ... }
```

**Journal comments:** Source control handles history. Remove changelogs from source files:
```java
// Changes (from 11-Oct-2001)
// --------------------------
// 11-Oct-2001 : Re-organized the class...
// 05-Nov-2001 : Added a getDescription() method...
```

**Noise comments:** Comments that restate the obvious and provide no new information:
```java
/** The day of the month. */
private int dayOfMonth;

/** Default constructor. */
protected AnnualDateRule() { }
```

**Scary noise:** Javadoc copied-and-pasted carelessly from one function to another, resulting in comments that describe the wrong thing entirely.

**Don't use a comment when you can use a function or variable:**
```java
// Bad — comment instead of meaningful code
// does the module from the global list <mod> depend on the
// subsystem we are part of?
if (smodule.getDependSubsystems().contains(subSysMod.getSubSystem()))

// Clean
ArrayList moduleDependees = smodule.getDependSubsystems();
String ourSubSystem = subSysMod.getSubSystem();
if (moduleDependees.contains(ourSubSystem))
```

**Position markers:** These are usually noise and should be used very sparingly:
```java
// Actions //////////////////////////
```

**Closing brace comments:** Put in by people who work in very long functions. The solution is to shorten the functions, not to comment the closing braces.

**Attributions and bylines:** `/* Added by Rick */` — source control handles this.

**Commented-out code:** Others see commented-out code and are afraid to delete it, thinking it is important. Source control remembers it. Delete it.

**HTML comments:** It is the responsibility of the tool to render Javadoc, not the programmer to decorate it with HTML in the source file.

**Nonlocal information:** If you must write a comment, make sure it describes the code it appears near, not somewhere else in the system.

**Too much information:** Don't put historical discussions or irrelevant descriptions of detail into comments.

**Inobvious connection:** The connection between a comment and the code it describes should be obvious. If the comment explains a non-obvious relationship, the underlying code may need to be restructured.

**Function headers:** Short, well-named functions need no Javadoc comment header.

---

## Chapter 5 — Formatting

### The Purpose of Formatting

Formatting is about communication. Communication is the professional developer's first order of business.

### Vertical Formatting

**File size:** Most source files should be between 200 and 500 lines. Files of 200 lines communicate their purpose more clearly than files of thousands.

**Vertical openness between concepts:** Blank lines separate concepts. Each blank line is a visual cue that a new and separate concept is beginning. Without blank lines, code becomes a dense wall of text:
```java
// Bad — no separation
package fitnesse.wikitext.widgets;
import java.util.regex.*;
public class BoldWidget extends ParentWidget {
public static final String REGEXP = "'''.+?'''";
private static final Pattern pattern = Pattern.compile("'''(.+?)'''");
public BoldWidget(ParentWidget parent, String text) throws Exception {
super(parent);
```

**Vertical density:** Lines of code that are tightly related should appear vertically dense — no blank lines between:
```java
public class ReporterConfig {
    private String className;
    private List<Property> properties = new ArrayList<Property>();

    public void addProperty(Property property) {
        properties.add(property);
    }
}
```

**Vertical distance:** Concepts that are closely related should be kept vertically close. Variables should be declared as close to their usage as possible. Instance variables should be declared at the top of the class (Java convention). Dependent functions (caller and callee) should be vertically close — the caller should be above the callee when possible.

**Vertical ordering:** Function call dependencies should point in the downward direction. A function that is called should be below a function that does the calling. The most important concepts come first; the details come last.

### Horizontal Formatting

**Line length:** The old 80-character limit is well-justified. Martin suggests 120 as an absolute upper limit, preferring shorter lines. Readers should not have to scroll horizontally.

**Horizontal openness and density:** Use horizontal white space to associate things that are strongly related and disassociate things that are weakly related:
```java
private void measureLine(String line) {
    lineCount++;
    int lineSize = line.length();
    totalChars += lineSize;
    lineWidthHistogram.addLine(lineSize, lineCount);
    recordWidestLine(lineSize);
}
```
Spaces around assignment operators reinforce the separation between left and right side. Spaces after commas in argument lists separate the arguments. No space between function name and opening parenthesis — function and its arguments are closely related.

**Horizontal alignment:** Aligning variable declarations or assignments in columns is counterproductive:
```java
// Bad — alignment hides real structure
private   Socket         socket;
private   inputStream    input;
protected long           requestDeadline;
```
The alignment shifts attention away from the true intent and toward the alignment itself. Automated formatters will destroy this anyway.

**Indentation:** Indentation reveals hierarchical structure. Never collapse scope to a single line:
```java
// Bad
public class Foo { public int bar; }

// Clean
public class Foo {
    public int bar;
}
```

**Dummy scopes:** Sometimes the body of a `while` or `for` loop is a dummy. Ensure the semicolon is visible on its own line with indentation:
```java
while (dis.read(buf, 0, readBufferSize) != -1)
    ;
```

### Team Rules

A team of developers should agree on a single formatting style. That style must be consistently enforced. Every developer should follow it regardless of personal preference. A source file should look like it was written by a single person, not a committee.

---

## Chapter 6 — Objects and Data Structures

### Data Abstraction

There is a fundamental tension between objects and data structures. Objects hide their data behind abstractions and expose functions that operate on that data. Data structures expose their data and have no meaningful functions.

**Bad (concrete point):**
```java
public class Point {
    public double x;
    public double y;
}
```

**Good (abstract point):**
```java
public interface Point {
    double getX();
    double getY();
    void setCartesian(double x, double y);
    double getR();
    double getTheta();
    void setPolar(double r, double theta);
}
```

The abstract interface hides implementation. You cannot tell whether it is implemented in rectangular or polar coordinates. Hiding implementation is not merely a matter of putting a function between your variables — it is about abstractions. A class does not simply push its variables out through getters and setters. It exposes abstract interfaces that allow users to manipulate the essence of the data without knowing its implementation.

**Bad (concrete vehicle — leaks implementation):**
```java
public interface Vehicle {
    double getFuelTankCapacityInGallons();
    double getGallonsOfGasoline();
}
```

**Good (abstract vehicle):**
```java
public interface Vehicle {
    double getPercentFuelRemaining();
}
```

### Data/Object Anti-Symmetry

Objects and data structures are opposites. This leads to a fundamental dichotomy:

- **Procedural code** (code using data structures) makes it easy to add new functions without changing the existing data structures. Hard to add new data structures because all functions must change.
- **OO code** makes it easy to add new classes without changing existing functions. Hard to add new functions because all classes must change.

**Procedural shape (easy to add functions, hard to add shapes):**
```java
public class Square { public Point topLeft; public double side; }
public class Circle { public Point center; public double radius; }

public class Geometry {
    public double area(Object shape) throws NoSuchShapeException {
        if (shape instanceof Square) {
            Square s = (Square)shape;
            return s.side * s.side;
        } else if (shape instanceof Circle) {
            Circle c = (Circle)shape;
            return Math.PI * c.radius * c.radius;
        }
        throw new NoSuchShapeException();
    }
}
```

**OO shape (easy to add shapes, hard to add functions):**
```java
public class Square implements Shape {
    private Point topLeft;
    private double side;
    public double area() { return side * side; }
}
public class Circle implements Shape {
    private Point center;
    private double radius;
    public double area() { return Math.PI * radius * radius; }
}
```

The appropriate choice depends on the problem. Sometimes you want to add new data types (OO); sometimes you want to add new functions (procedural).

### The Law of Demeter

A module should not know about the innards of the objects it manipulates. More formally: a method `f` of class `C` should only call methods of:
1. `C` itself
2. An object created by `f`
3. An object passed as an argument to `f`
4. An object held in an instance variable of `C`

The method should not invoke methods on objects returned by any of the allowed functions — talk to friends, not to strangers.

### Train Wrecks

The following code violates the Law of Demeter and is called a "train wreck" — a chain of function calls:

```java
// Bad
final String outputDir = ctxt.getOptions().getScratchDir().getAbsolutePath();
```

This is best split apart:
```java
Options opts = ctxt.getOptions();
File scratchDir = opts.getScratchDir();
final String outputDir = scratchDir.getAbsolutePath();
```

Whether this violates Demeter depends on whether `ctxt`, `Options`, and `ScratchDir` are objects or data structures. If they are data structures with no behavior, then Demeter does not apply. But if they are objects, then this code calls into the internal structure and violates the law.

### Hybrids

Hybrids are half-object, half-data-structure. They have functions that do significant things and public variables or public accessors that make private variables public. These hybrids make it hard to add new functions and hard to add new data structures. They are the worst of both worlds. Avoid creating them.

### Data Transfer Objects

The quintessential form of a data structure is a class with public variables and no functions. This is called a Data Transfer Object (DTO). They are useful for communicating with databases or parsing messages from sockets. They often serve as the first stage in the translation process that converts raw data from the persistence layer into objects in the application code.

**Active Records** are a special form of DTOs. They are data structures with public variables but with navigational methods like `find` and `save`. Active Records are direct translations of database tables. Unfortunately developers often put business rule methods in these classes, creating a hybrid. Treat Active Records as data structures and create separate objects to contain the business rules.

---

## Chapter 7 — Error Handling

### Use Exceptions Rather Than Return Codes

Before exceptions existed, techniques for error handling were limited. Callers must check for errors immediately after calling. Error handling code obscures the logic of the algorithm.

```java
// Bad — return codes cluttering logic
if (handle != DeviceHandle.INVALID) {
    // Save the device status to the record field
    retrieveDeviceRecord(handle);
    if (record.getStatus() != DEVICE_SUSPENDED) {
        pauseDevice(handle);
        clearDeviceWorkQueue(handle);
        closeDevice(handle);
    } else {
        logger.log("Device suspended. Unable to shut down");
    }
} else {
    logger.log("Invalid handle for: " + DEV1.toString());
}

// Clean — exceptions separate logic from error handling
try {
    tryToShutDown();
} catch (DeviceShutDownError e) {
    logger.log(e);
}

private void tryToShutDown() throws DeviceShutDownError { ... }
```

### Write Your Try-Catch-Finally Statement First

`try-catch-finally` establishes a scope. When you execute code in the `try` portion, you are stating that execution can abort at any point and then resume at the `catch`. In a sense, `try` blocks are like transactions. Start with a try-catch-finally when writing code that could throw exceptions. This helps define what the user of that code should expect.

### Use Unchecked Exceptions

The debate over checked exceptions is settled in Martin's view: **unchecked exceptions are almost always correct**. Checked exceptions violate the Open/Closed Principle — if you throw a checked exception from a method in your code and the catch is three levels above, you must declare that exception in each method in the call chain between you and the catch. This means a change at a low level of the software can force signature changes on many higher levels.

### Provide Context with Exceptions

Each exception you throw should provide enough context to determine the source and location of an error. Create informative error messages and pass them along with your exceptions. Mention the operation that failed and the type of failure.

### Define Exception Classes in Terms of Caller's Needs

When defining exception classes, the most important concern is how they are caught. Wrapping third-party APIs is best practice:

```java
// Bad — multiple catch clauses for the same action
ACMEPort port = new ACMEPort(12);
try {
    port.open();
} catch (DeviceResponseException e) {
    reportPortError(e);
    logger.log("Device response exception", e);
} catch (ATM1212UnlockedException e) {
    reportPortError(e);
    logger.log("Unlock exception", e);
} catch (GMXError e) {
    reportPortError(e);
    logger.log("Device response exception");
}

// Clean — wrapper class
LocalPort port = new LocalPort(12);
try {
    port.open();
} catch (PortDeviceFailure e) {
    reportError(e);
    logger.log(e.getMessage(), e);
}
```

Wrappers around third-party APIs minimize dependencies and ease transitions to different libraries.

### Define the Normal Flow — Special Case Pattern

The Special Case Pattern (from Martin Fowler) can eliminate the need for exception handling in some cases. You create a class or configure an object so that it handles a special case for you — the client code doesn't have to deal with exceptional behavior:

```java
// Bad — caller has to handle the exceptional case
try {
    MealExpenses expenses = expenseReportDAO.getMeals(employee.getID());
    m_total += expenses.getTotal();
} catch (MealExpensesNotFound e) {
    m_total += getMealPerDiem();
}

// Clean — DAO returns a MealExpenses object that returns per diem when no meals found
MealExpenses expenses = expenseReportDAO.getMeals(employee.getID());
m_total += expenses.getTotal();
```

### Don't Return Null

Returning null from a method creates an obligation on every caller to check for null. One missing null check can send an application spinning out of control. If you are tempted to return null from a method, consider throwing an exception or returning a Special Case object instead.

### Don't Pass Null

Passing null into methods is even worse than returning null. Unless you are working with an API that expects null, you should avoid passing null whenever possible. In most programming languages there is no good way to deal with a null that is passed by a caller accidentally. Because this is the case, the rational approach is to forbid passing null by default.

---

## Chapter 8 — Boundaries

### Using Third-Party Code

There is a natural tension between the provider of an interface and the user of an interface. Providers of third-party packages and frameworks strive for broad applicability. Users want an interface focused on their particular needs. This tension can cause problems at the boundaries of our systems.

**Encapsulate boundary types:** If you use a boundary interface such as `Map`, keep it inside the class or close family of classes that uses it. Avoid returning it from or accepting it as an argument to public APIs.

```java
// Bad — Map boundary type exposed
public Map getSensors();

// Clean — encapsulated
public class Sensors {
    private Map sensors = new HashMap();
    public Sensor getById(String id) {
        return (Sensor) sensors.get(id);
    }
}
```

### Exploring and Learning Boundaries

Third-party code is hard to learn and hard to integrate. Learning tests are useful — writing tests against the third-party API not to test it, but to learn it. These tests focus on what we want out of the API and clarify our understanding of it. If the third-party package changes in ways incompatible with our tests, we find out immediately.

### Using Code That Does Not Yet Exist

Sometimes boundaries separate known from unknown. You may have a part of the system you know nothing about yet. Rather than waiting, define the own interface representing the behavior you wish you had, then write code in terms of your interface. When the real API is available, write an adapter.

### Clean Boundaries

Code at boundaries needs clear separation and tests that define expectations. When using code that is not under your control, special care must be taken to prevent too much of our code from knowing about third-party particulars. It is better to depend on something you control than something you don't. Wrap third-party APIs in adapter/wrapper classes.

---

## Chapter 9 — Unit Tests

### The Three Laws of TDD

1. You may not write production code until you have written a failing unit test.
2. You may not write more of a unit test than is sufficient to fail, and not compiling is failing.
3. You may not write more production code than is sufficient to pass the currently failing test.

These three laws lock you into a cycle that is perhaps 30 seconds long. Tests and production code are written together, with the tests just a few seconds ahead of the production code.

### Keeping Tests Clean

Test code is just as important as production code. It is not a second-class citizen. It requires thought, design, and care. If you have dirty tests, you might as well have no tests. The dirtier the tests, the harder they are to change. As production code changes, old tests start to fail, and the mess in the test code makes it hard to get those tests to pass again. Eventually tests are discarded, and without tests, the production code begins to rot.

**Tests enable the -ilities.** Unit tests keep the code flexible, maintainable, and reusable. Without tests, every change is a possible bug. The only way to make sure a change works as expected is to test it.

### Clean Tests

Readability is paramount in clean tests. What makes tests readable? Clarity, simplicity, and density of expression. The BUILD-OPERATE-CHECK pattern is useful:

```java
public void testGetPageHierarchyAsXml() throws Exception {
    makePages("PageOne", "PageOne.ChildOne", "PageTwo"); // BUILD
    submitRequest("root", "type:pages");                  // OPERATE
    assertResponseIsXML();                                // CHECK
    assertResponseContains(
        "<name>PageOne</name>", "<name>PageTwo</name>",
        "<name>ChildOne</name>"
    );
}
```

### Domain-Specific Testing Language

Build a set of functions and utilities that make the tests more convenient to write and easier to read. These create a testing API layered over the tested system.

### A Dual Standard

Test code has a different set of engineering standards than production code. It must be simple, succinct, and expressive, but it need not be as efficient as production code. Things you might never do in a production environment are perfectly fine in a test environment.

### One Assert per Test

Tests are easiest to read when they have a single `assert` statement. This is a valuable discipline, though sometimes more than one assert is acceptable. The better rule is: **one concept per test**. Test a single concept in each test function. Do not test everything in the kitchen sink.

### FIRST Properties

**Fast:** Tests should be fast. They should run quickly. When tests run slow, you won't run them frequently. When you don't run them frequently, you won't find problems early enough to fix them easily.

**Independent:** Tests should not depend on each other. One test should not set up the conditions for the next test. You should be able to run each test independently and run the tests in any order you like.

**Repeatable:** Tests should be repeatable in any environment. You should be able to run the tests in the production environment, in the QA environment, and on your laptop while riding home on the train without a network. If tests aren't repeatable in any environment, you'll always have an excuse for why they fail.

**Self-Validating:** The tests should have a boolean output. Either they pass or they fail. You should not have to read through a log file to tell whether the tests pass. If tests aren't self-validating, then failure can become subjective and running the tests can require a long manual evaluation.

**Timely:** Tests need to be written in a timely fashion. Unit tests should be written just before the production code that makes them pass. If you write tests after the production code, then you may find the production code to be hard to test. You may decide that some production code is too hard to test. You may not design the production code to be testable.

---

## Chapter 10 — Classes

### Class Organization

Following the Java convention, a class begins with a list of variables: public static constants first, then private static variables, then private instance variables. Public functions follow the variable list. Private utilities called by a public function come right after that public function — this follows the step-down rule and gives the program the structure of a newspaper article.

### Encapsulation

Classes and functions should be as private as possible. Relax encapsulation only as a last resort. Tests drive design — if a test needs access to a method or variable, make it protected or package-scope rather than public, but do this grudgingly.

### Classes Should Be Small

The first rule of classes is that they should be small. The second rule is that they should be smaller than that. But for classes, size is measured in **responsibilities**, not lines of code.

**Naming is a quality measure:** If you cannot derive a concise name for a class, it is too large. The more ambiguous the class name, the more likely it has too many responsibilities. Class names including words like `Processor`, `Manager`, or `Super` hint at unfortunate aggregation of responsibilities.

**The Single Responsibility Principle (SRP):** A class or module should have one, and only one, reason to change. The SRP is one of the more important concepts in OO design and one of the simpler concepts to understand and adhere to. Yet curiously, SRP is often the most abused class design principle. We regularly encounter classes that do far too many things.

```java
// Bad — manages versions AND has too many methods
public class SuperDashboard extends JFrame implements MetaDataUser {
    public Component getLastFocusedComponent() { ... }
    public void setLastFocused(Component lastFocused) { ... }
    public int getMajorVersionNumber() { ... }
    public int getMinorVersionNumber() { ... }
    public int getBuildNumber() { ... }
}

// Clean — version info extracted
public class Version {
    public int getMajorVersionNumber() { ... }
    public int getMinorVersionNumber() { ... }
    public int getBuildNumber() { ... }
}
```

**The concern:** Many developers fear many small classes make it harder to understand the bigger picture. However, a system with many small, well-named classes has no more moving parts than a system with few large classes. There is just as much to learn either way. The question is whether we want our tools organized into toolboxes with many small drawers, each containing well-defined and well-labeled components, or a few drawers where we dump everything.

### Cohesion

Classes should have a small number of instance variables. Each method in the class should manipulate one or more of those variables. A class in which each variable is used by each method is maximally cohesive. Cohesion is high when instance variables and methods are co-dependent and hang together as a logical whole. Maintaining cohesion results in many small classes.

### Organizing for Change

In a clean system, classes are organized to reduce the risk of change. An Open/Closed Principle (OCP) class is open for extension but closed for modification.

```java
// Bad — adding new SQL operations requires modifying the class
public class Sql {
    public Sql(String table, Column[] columns) { ... }
    public String create() { ... }
    public String insert(Object[] fields) { ... }
    public String selectAll() { ... }
    public String findByKey(String keyColumn, String keyValue) { ... }
    // Adding UPDATE requires modifying this class
}

// Clean — each SQL type is a separate class
abstract public class Sql {
    abstract public String generate();
}
public class CreateSql extends Sql { ... }
public class SelectSql extends Sql { ... }
public class InsertSql extends Sql { ... }
// Adding UpdateSql only requires a new class
```

### Isolating from Change — Dependency Inversion Principle

Needs will change, so code will change. A client class depending upon concrete details is at risk when those details change. Interfaces and abstract classes help isolate the impact. The Dependency Inversion Principle (DIP) says classes should depend upon abstractions, not on concrete details.

```java
// Bad — depends on concrete class
public class Portfolio {
    private TokyoStockExchange exchange;
    public Portfolio(TokyoStockExchange exchange) { ... }
}

// Clean — depends on abstraction
public interface StockExchange {
    Money currentPrice(String symbol);
}
public class Portfolio {
    private StockExchange exchange;
    public Portfolio(StockExchange exchange) { ... }
}
```

---

## Chapter 11 — Systems

### Separate Constructing a System from Using It

**Construction is a very different process from use.** Software systems should separate the startup process, when application objects are constructed and dependencies are wired together, from the runtime logic that takes over after startup.

**Don't do both in one place:**
```java
// Bad — lazy initialization mixed into usage
public Service getService() {
    if (service == null)
        service = new MyServiceImpl(...); // construction dependency
    return service;
}
```

This has a CONSTRUCTION DEPENDENCY directly in the usage code. Testing is hard because `MyServiceImpl` is hardcoded. The `service == null` path is never tested in production.

### Separation Mechanisms

**Main:** Move all construction to `main` or modules called by `main`. Pass the constructed objects to the application. The application has no knowledge of `main` or the construction process.

**Factories:** Use the Abstract Factory pattern to give the application control of when an object gets created but keep the details of construction separate from the application code.

**Dependency Injection (DI):** The most powerful mechanism for separating construction from use. DI applies Inversion of Control (IoC) to dependency management. An object should not take responsibility for instantiating dependencies. Instead, it should pass this responsibility to another "authoritative" mechanism, thereby inverting the control. Setup is done in `main` or a special-purpose container.

### Scaling Up

Cities work because they have teams of people who manage particular parts of the city. Some are responsible for power, water, sewers, streets, law enforcement, building codes, etc. Software systems and cities both grow by following patterns of organic growth rather than fully-planned systems. You cannot get it right the first time. Implement today's stories, then refactor and expand to implement tomorrow's stories.

### Cross-Cutting Concerns

Modularizing concerns like persistence, security, and transaction management is difficult because these concerns naturally "cross-cut" the primary decomposition of the system. Aspect-Oriented Programming (AOP) was developed to address this. In AOP, modular constructs called "aspects" specify which points in the system should have their behavior modified in some consistent way.

**Java Proxies** allow you to wrap individual objects or classes, intercepting method calls. They work well for simple situations but are verbose. **AOP frameworks** (like Spring AOP and AspectJ) provide a declarative approach to specify cross-cutting behavior.

### Test Drive the System Architecture

An optimal system architecture consists of modularized domains of concern, each implemented with Plain Old Java (or other) Objects. Different domains are integrated together with minimally invasive aspects or aspect-like tools. This architecture can be test-driven, just like the code.

### Use Standards Wisely, When They Add Demonstrable Value

Standards make it easier to reuse ideas and components, recruit people with relevant experience, encapsulate good ideas, and wire components together. However, the process of creating standards can sometimes take too long for the industry to wait, and some standards lose touch with the real needs of the adopters they are intended to serve.

---

## Chapter 12 — Emergence

### Kent Beck's Four Rules of Simple Design

Kent Beck's four rules of Simple Design are, in order of importance:

1. **Runs all the tests.** A design must be verifiable. Systems that cannot be verified should not be deployed. Writing tests leads to better designs — to write tests you must think about how to make classes smaller, more focused. Tight coupling makes it difficult to write tests. The more tests we write, the more we develop toward things that are easier to test. Thus pushing toward low coupling and high cohesion.

2. **Contains no duplication.** Duplication is the primary enemy of a well-designed system. It represents additional work, additional risk, and additional unnecessary complexity. Even a few lines of duplication can be pulled into a separate method; reuse in the small (the TEMPLATE METHOD pattern is a common technique for removing higher-level duplication).

3. **Expresses the intent of the programmer.** Most of the cost of a software project is in long-term maintenance. It is easy to write code that we understand because at the time we write it we are deeply familiar with it. Other maintainers of the code are not going to have so deep an understanding. The software should clearly express the intent of its author. Choose good names. Keep functions and classes small. Use standard nomenclature. Write well-crafted unit tests (tests as documentation).

4. **Minimizes the number of classes and methods.** In an effort to make our classes and methods small, we might create too many. This rule suggests that we also keep our function and class counts low. High class and method counts are sometimes the result of pointless dogmatism — every class must have an interface, or data and behavior must always be separated. Fight dogmatism; be pragmatic. This rule is the lowest priority of the four.

---

## Chapter 13 — Concurrency

### Why Concurrency?

Concurrency is a decoupling strategy. It helps us decouple what gets done from when it gets done. In single-threaded systems, what and when are so strongly coupled that the state of the entire application can often be determined by looking at the stack trace. In a concurrent system, what and when are decoupled.

**Motivations:**
- Web applications: one thread per connection improves throughput
- Batch processing: run multiple computations in parallel
- Responsive UI: background processing while the UI remains responsive

### Myths and Misconceptions

- **Concurrency always improves performance.** Sometimes. Concurrency can improve performance only when there is wait time that can be shared between multiple threads or processors.
- **Design does not change when writing concurrent programs.** In fact, the design of a concurrent algorithm can be very different from the design of a single-threaded system.
- **It is not important to understand concurrency issues when working with a container such as a Web or EJB container.** You need to know what your container is doing and how to guard against the issues of concurrent update and deadlock.

**True statements:**
- Concurrency incurs some overhead in performance and writing additional code.
- Correct concurrency is complex, even for simple problems.
- Concurrency bugs aren't usually repeatable, so they are often ignored as one-offs instead of the true defects they are.
- Concurrency often requires a fundamental change in design strategy.

### Concurrency Defense Principles

**Single Responsibility Principle:** The SRP says a given method/class/component should have a single reason to change. Concurrency design is complex enough to be a reason all by itself to separate from the rest of the code. Keep concurrency-related code separate from other code.

**Limit the Scope of Data:** Use the `synchronized` keyword to protect a critical section in the code that uses the shared object. Limit the number of such critical sections. The more places shared data can get updated, the more likely you are to have forgotten to protect one or more of those places — introducing bugs that cause failure in concurrent code.

**Use Copies of Data:** Avoid sharing data where possible. Copy objects and treat them as read-only. Copy objects, collect results from multiple threads in these copies and merge the results in a single thread.

**Threads Should Be as Independent as Possible:** Write threaded code such that each thread exists in its own world, sharing no data with any other thread. Each thread processes one client request, with all of its required data coming from an unshared source and stored as local variables. This makes each thread behave as if it were the only thread in the world and there was no synchronization requirements.

### Know Your Library

Java 5 and onwards offer many concurrency improvements. Know and use the following:
- Use the provided thread-safe collections: `ConcurrentHashMap`, etc.
- Use the executor framework for executing unrelated tasks.
- Use nonblocking solutions where possible.
- Several library classes are not thread-safe.

### Know Your Execution Models

- **Bound Resources:** Resources of a fixed size or number used in a concurrent environment (connections, read/write buffers).
- **Mutual Exclusion:** Only one thread can access shared data at a time.
- **Starvation:** One thread or group of threads is prohibited from proceeding for an excessively long time or forever.
- **Deadlock:** Two or more threads waiting for each other to finish. Each thread has a resource the other needs.
- **Livelock:** Threads in lockstep, each trying to do work but finding another "in the way." Both continually repeat the same result.

**Producer-Consumer:** One or more producer threads create work and place it in a buffer or queue. One or more consumer threads acquire that work from the queue and complete it. The queue between them is a bound resource.

**Readers-Writers:** When you have a shared resource that primarily serves as a source of information for readers, but which is occasionally updated by writers, the challenge is balancing the needs of both. Starving readers or allowing stale information are difficult problems in concurrent design.

**Dining Philosophers:** Several processes compete for a finite number of resources in a cycle of possible deadlock.

### Beware Dependencies Between Synchronized Methods

Dependencies between synchronized methods cause subtle bugs in concurrent code. The Java language has the word `synchronized`, which protects an individual method. If there is more than one synchronized method on the same shared class, the system may be written incorrectly. **Recommendation:** Avoid using more than one method on a shared object.

### Keep Synchronized Sections Small

The `synchronized` keyword introduces a lock. All sections of code guarded by the same lock are guaranteed to have only one thread executing through them at any given time. Locks are expensive because they create delays and add overhead. So we want to design our code with as few critical sections as possible. Some naive programmers try to achieve this by making their critical sections very large. Extend synchronization sections only as far as necessary.

### Testing Threaded Code

Write tests that have the potential to expose problems and then run them frequently, with different programmatic configurations and system configurations and load. If tests ever fail, track down the failure. Don't ignore a failure just because the tests pass on a subsequent run.

- Treat spurious failures as candidate threading issues. Do not ignore system failures as one-offs.
- Get your nonthreaded code working first.
- Make your threaded code pluggable so that you can run it in various configurations.
- Run with more threads than processors.
- Run on different platforms.
- Instrument your code to try and force failures.

---

## Chapter 14, 15, 16 — Successive Refinement

### The Process

Martin illustrates through a lengthy case study (a command-line argument parser) that clean code is not written all at once. The process is:

1. **Write dirty code first.** Get it working. Don't spend time making it beautiful before you know it works.
2. **Refactor continuously.** Once it works, immediately begin cleaning: extract functions, rename variables, remove duplication.
3. **Incremental improvement.** Make one small, focused improvement at a time, keeping all tests passing throughout.
4. **Never let rot accumulate.** Stopping the refactoring because "it mostly works" leads to a downward spiral. A mess builds quickly; cleaning it later costs exponentially more than cleaning it continuously.

**Key insight:** It is not enough to write code that works. Code that works but is unreadable is a liability. The discipline of continuous refinement — writing, testing, cleaning — is what separates professionals from hobbyists.

---

## Chapter 17 — Code Smells and Heuristics

This appendix provides a reference catalog of smells (symptoms of poor design) and heuristics (rules of thumb for good design). Each is identified with a prefix indicating its category.

---

### Comments (C1–C5)

**C1 — Inappropriate Information**
Comments should not hold information better suited for other systems: version control, issue trackers, change logs. Comments should describe technical matters relating to code and design only.

**C2 — Obsolete Comment**
A comment that has drifted away from the code it describes is worse than no comment. Old comments become irrelevant and misleading. Update or delete obsolete comments promptly.

**C3 — Redundant Comment**
A comment is redundant if it describes something that adequately describes itself. Redundant comments take more time to read than the code and provide no additional information:
```java
i++; // increment i
```

**C4 — Poorly Written Comment**
A comment worth writing is worth writing well. Do not ramble. Do not state the obvious. Be brief, correct, and clear.

**C5 — Commented-Out Code**
Commented-out code is an abomination. Source control systems remember deleted code. Delete commented-out code immediately. Others who see it will not have the courage to delete it because they assume it is important.

---

### Environment (E1–E2)

**E1 — Build Requires More Than One Step**
Building a project should be a single trivial operation. You should not have to check out several sub-trees from source control, search through wikis, or follow long sequences of instructions. One command should check out the system and one command should build it.

**E2 — Tests Require More Than One Step**
You should be able to run all unit tests with just one command. This command should be obvious, fast, and always available. Nothing is more demoralizing than requiring a multi-step process to run tests.

---

### Functions (F1–F4)

**F1 — Too Many Arguments**
Functions should have few arguments. No argument is best. One, two, and three arguments are acceptable. More than three is very questionable and should be avoided. (See Chapter 3 discussion above.)

**F2 — Output Arguments**
Output arguments are counterintuitive. Readers expect arguments to be inputs, not outputs. If your function must change the state of something, change the state of its owning object. Avoid output arguments.

**F3 — Flag Arguments**
Boolean arguments loudly declare that a function does more than one thing. They are confusing and should be eliminated. Split the function into separate functions for each true/false case.

**F4 — Dead Function**
Methods that are never called should be discarded. Keeping dead code around wastes mental energy. Source control remembers deleted functions.

---

### General (G1–G36)

**G1 — Multiple Languages in One Source File**
Today's modern programming environments allow mixing multiple languages in a single source file. For example, a Java file might contain HTML, XML, YAML, JavaDoc, English, JavaScript. This confusion is best minimized. Ideally, a source file should contain only one language.

**G2 — Obvious Behavior Is Unimplemented**
Following the Principle of Least Surprise, any function or class should implement the behaviors that another programmer could reasonably expect. When obvious behavior is not implemented, readers and users of the code lose their ability to trust their intuitions about the function.

**G3 — Incorrect Behavior at the Boundaries**
Developers often write functions that they think work correctly and then don't bother testing the boundary cases. Every boundary condition, every corner case, every quirk and exception needs to be tested. Do not rely on intuition at the boundaries.

**G4 — Overridden Safeties**
It is risky to override safeties. Turning off failing tests and telling yourself you'll get them to pass later is as bad as pretending your credit cards are free money. Do not silence compiler warnings. Do not disable tests. Fix the underlying problem.

**G5 — Duplication**
This is one of the most important rules in this book and is worth repeating. Every time you see duplication in the code, it represents a missed opportunity for abstraction. That duplication could probably become a subroutine or perhaps another class outright. By folding the duplication into such an abstraction, you increase the vocabulary of the language of your design. Other programmers can use the abstract facilities you create. Coding becomes faster and less error-prone because you have raised the abstraction level.

- Simple code clones → extract method
- Switch/case or if/else chains that appear over and over again in various modules → polymorphism
- Similar algorithms but different code → TEMPLATE METHOD or STRATEGY pattern

**G6 — Code at Wrong Level of Abstraction**
It is important to create abstractions that separate higher level general concepts from lower level detailed concepts. Sometimes we do this by creating abstract classes to hold the higher level concepts and derivatives to hold the lower level concepts. When we do this, we need to make sure that the separation is complete. All lower level concepts should be in the derivative classes, and all higher level concepts should be in the base class. For example, constants, variables, or utility functions that pertain only to the detailed implementation should not be present in the base class.

**G7 — Base Classes Depending on Their Derivatives**
The most common reason for partitioning concepts into base and derivative classes is so that the higher level base class concepts can be independent of the lower level derivative class concepts. Therefore, when we see base classes mentioning the names of their derivatives, we suspect a problem.

**G8 — Too Much Information**
Well-defined modules have very small interfaces that allow you to do a lot with a little. Poorly defined modules have wide and deep interfaces that force you to use many different gestures to get simple things done. The fewer methods a class has, the better. The fewer variables a function knows about, the better. The fewer instance variables a class has, the better. Hide your data. Hide your utility functions. Hide your constants and your temporaries. Don't create classes with lots of methods or lots of instance variables. Don't create lots of protected variables and functions for your subclasses. Concentrate on keeping interfaces very tight and very small. Help keep coupling low by limiting information.

**G9 — Dead Code**
Dead code is code that isn't executed. You find it in the body of an `if` statement that checks for a condition that can't happen. You find it in the `catch` block of a `try` that never `throws`. You find it in little utility methods that are never called or `switch/case` conditions that never occur. Delete dead code from the system. Don't worry, the source code control system still remembers it.

**G10 — Vertical Separation**
Variables and functions should be defined close to where they are used. Local variables should be declared just above their first usage and should have a small vertical scope. Private functions should be defined just below their first usage. Finding a private function should be a matter of scanning downward from the first usage.

**G11 — Inconsistency**
If you do something a certain way, do all similar things in the same way. This is the principle of least surprise. Be careful with the conventions you choose, and once chosen, be careful to continue to follow them. If within a particular function you use a variable named `response` to hold an `HttpServletResponse`, then use the same variable name consistently in the other functions that use `HttpServletResponse` objects. If you name a method `processVerificationRequest`, then use a similar name, such as `processDeletionRequest`, for a method that processes deletion requests.

**G12 — Clutter**
Of what use is a default constructor with no implementation? All it serves to do is clutter up the code with meaningless artifacts. Variables that aren't used, functions that are never called, comments that add no information — all this is clutter and should be removed. Keep your source files clean, well organized, and free of clutter.

**G13 — Artificial Coupling**
Things that don't depend upon each other should not be artificially coupled. For example, general `enums` should not be contained within more specific classes because this forces the whole application to know about these more specific classes. The same goes for general purpose `static` functions being declared in specific classes. Take the time to figure out where functions, constants, and variables ought to be declared. Don't just toss them in the most convenient place at hand and then leave them there.

**G14 — Feature Envy**
The methods of a class should be interested in the variables and functions of the class they belong to, and not the variables and functions of other classes. When a method uses accessors and mutators of some other object to manipulate the data within that object, then it envies the scope of the class of that other object. It wishes that it were inside that other class so that it could have direct access to the variables it is manipulating.

**G15 — Selector Arguments**
There is hardly anything more abominable than a dangling `false` argument at the end of a function call. What does it mean? What would it change if it were `true`? Not only is the purpose of a selector argument difficult to remember, each selector argument combines many functions into one. Selector arguments are just a lazy way to avoid splitting a large function into several smaller functions.

**G16 — Obscured Intent**
We want code to be as expressive as possible. Run-on expressions, Hungarian notation, and magic numbers all obscure the author's intent. It is worth taking the time to make the intent of our code visible to our readers.

**G17 — Misplaced Responsibility**
One of the most important decisions a software developer can make is where to put code. The principle of least surprise applies here too: code should be placed where a reader would naturally expect it to be. Sometimes we get "clever" about where we put certain functionality. We'll put it in a function that's convenient for us but that the reader would not have expected to find it there.

**G18 — Inappropriate Static**
`Math.max(double a, double b)` is a good static method. It does not operate on a single instance; indeed it would be silly to have to say `new Math().max(a, b)` or even `a.max(b)`. However, `HourlyPayCalculator.calculatePay(employee, overtimeRate)` is a questionable static function. It seems plausible that we might want this function to be polymorphic. In general you should prefer nonstatic methods to static methods. When in doubt about whether to make a function static or not, make it nonstatic. If you really want a function to be static, make sure that there is no chance that you'll want it to behave polymorphically.

**G19 — Use Explanatory Variables**
One of the most powerful ways to make a program readable is to break up the calculations into intermediate values that are held in variables with meaningful names:
```java
// Bad
if (line.split(",")[0].trim().equals("valid")) { ... }

// Clean
String status = line.split(",")[0].trim();
if (status.equals("valid")) { ... }
```

**G20 — Function Names Should Say What They Do**
Look at this code:
```java
Date newDate = date.add(5);
```
Would you expect this to add five days to the date? Or five weeks? Or five hours? If you can't tell what the function does from the name, then either the function is doing too much, or it needs a better name. If the function adds five days to the date and changes the date, then it should be called `addDaysTo` or `increaseByDays`. If, on the other hand, the function returns a new date that is five days later but does not change the date instance, it should be called `daysLater` or `daysSince`.

**G21 — Understand the Algorithm**
Lots of interesting bugs hide in functions where programmers implement something that "works" without really understanding how it works. You think you know the right implementation for a function and make it work by adding in special cases and extra flags. Before you consider yourself done with a function, make sure you understand how it works — not just "I think the tests pass." Often the best way to gain this knowledge is to refactor the function into something that is so clean and expressive that it is obvious how it works.

**G22 — Make Logical Dependencies Physical**
If one module depends upon another, that dependency should be physical, not just logical. The dependent module should not make assumptions (logical dependencies) about the module it depends upon. Rather it should explicitly ask that module for all the information it depends upon.

**G23 — Prefer Polymorphism to If/Else or Switch/Case**
Before using a switch consider: "Is there an existing `switch` statement for this type of selection? The obvious place to look is where the object in question is created. Use polymorphism to make the software more maintainable and extensible. The "ONE SWITCH" rule: There may be no more than one switch statement for a given type of selection. The cases in that switch statement must create polymorphic objects that take the place of other switch statements in the rest of the system.

**G24 — Follow Standard Conventions**
Every team should follow a coding standard based on common industry norms. This standard should specify things like where to declare instance variables; how to name classes, methods, and variables; where to put braces; and so on. The team should not need a document to describe these conventions because their code provides the examples. Everyone on the team should follow these conventions. This means that each team member must be mature enough to realize that it doesn't matter a bit where you put your braces so long as you all agree on where to put them.

**G25 — Replace Magic Numbers with Named Constants**
This is probably one of the oldest rules in software development. In general it is a bad idea to have raw numbers in your code. You should hide them behind well-named constants. For example, the number 86,400 should be hidden behind the constant `SECONDS_PER_DAY`. If you are printing 55 lines per page, then the constant 55 should be hidden behind the constant `LINES_PER_PAGE`.

**G26 — Be Precise**
When you make a decision in your code, make sure you make it precisely. Know why you have made it and how you will deal with any exceptions. Don't be lazy about the precision of your decisions. If you decide to call a function that might return null, check for null. If you query for what you think is the only record in the database, make sure your query returns only one record. If you need to deal with currency, use integers and deal with rounding appropriately. If there is the possibility of concurrent update, make sure you implement some kind of locking mechanism. Ambiguities and imprecision in code are either a result of disagreements or laziness. In either case they should be eliminated.

**G27 — Structure Over Convention**
Enforce design decisions with structure over convention. Naming conventions are good, but they are inferior to structures that force compliance. For example, switch/cases with nicely named enumerations are inferior to base classes with abstract methods. No one is forced to implement the switch/case statement the same way each time; but the base classes do enforce that concrete classes implement all abstract methods.

**G28 — Encapsulate Conditionals**
Boolean logic is hard enough to understand without having to see it in the context of an `if` or `while` statement. Extract functions that explain the intent of the conditional:
```java
// Bad
if (shouldBeDeleted(timer))

// Good — already clean, but further example:
if (timer.hasExpired() && !timer.isRecurrent())

// Encapsulated version:
if (shouldBeDeleted(timer))
```

**G29 — Avoid Negative Conditionals**
Negatives are just a bit harder to understand than positives. So, when possible, conditionals should be expressed as positives:
```java
// Bad
if (!buffer.shouldNotCompact())

// Clean
if (buffer.shouldCompact())
```

**G30 — Functions Should Do One Thing**
It is often tempting to create functions that have multiple sections that perform a series of operations. Functions of this kind do more than one thing and should be converted into many smaller functions, each of which does one thing. (See Chapter 3.)

**G31 — Hidden Temporal Couplings**
Temporal couplings are often necessary, but you should not hide the coupling. Structure the arguments of your functions such that the order in which they should be called is obvious:
```java
// Bad — order of calls is implicit
void dive(String reason) {
    saturateGradient();
    reticulateSplines();
    diveForMoog(reason);
}

// Clean — chain forces order
void dive(String reason) {
    Gradient gradient = saturateGradient();
    List<Spline> splines = reticulateSplines(gradient);
    diveForMoog(splines, reason);
}
```

**G32 — Don't Be Arbitrary**
Have a reason for the way you structure your code, and make sure that reason is communicated by the structure of the code. If a structure appears arbitrary, others will feel empowered to change it. If a structure appears consistent and deliberate, others are much more likely to leave it alone.

**G33 — Encapsulate Boundary Conditions**
Boundary conditions are hard to keep track of. Put the processing for them in one place. Don't let them leak all over the code. We don't want swarms of `+1`s and `-1`s scattered hither and yon:
```java
// Bad — boundary condition scattered
if (level + 1 < tags.length) {
    parts = new Parse(body, tags, level + 1, offset + endTag);
    body = null;
}

// Clean — boundary encapsulated
int nextLevel = level + 1;
if (nextLevel < tags.length) {
    parts = new Parse(body, tags, nextLevel, offset + endTag);
    body = null;
}
```

**G34 — Functions Should Descend Only One Level of Abstraction**
The statements within a function should all be written at the same level of abstraction, which should be one level below the operation described by the name of the function. This may be the hardest of these heuristics to interpret and follow. Though the idea is simple enough, getting the practice right can be elusive.

**G35 — Keep Configurable Data at High Levels**
If you have a constant such as a default or configuration value that is known and expected at a high level of abstraction, do not bury it in a low-level function. Expose it as an argument to that low-level function called from the high-level function:
```java
// Bad — default buried in low-level code
public class Server {
    private static final int DEFAULT_PORT = 8080;
    // ... used deep inside the code
}

// Clean — exposed at high level for easy configuration
public static void main(String[] args) {
    Arguments arguments = parseCommandLine(args);
    // arguments.port defaults to 8080, easily changed
}
```

**G36 — Avoid Transitive Navigation**
In general we don't want a single module to know much about its collaborators. More specifically, if A collaborates with B, and B collaborates with C, we don't want modules that use A to know about C. (The Law of Demeter revisited.) We want our immediate collaborators to offer all the services we need. We should not have to roam through the object graph of the system, hunting for the method we want to call. Rather: `myCollaborator.doSomething()` rather than `a.getB().getC().doSomething()`.

---

### Java Smells (J1–J3)

**J1 — Avoid Long Import Lists by Using Wildcards**
If you use two or more classes from a package, import the whole package with a wildcard import statement: `import package.*;`. Long lists of imports are daunting to the reader. Specific imports create hard dependencies whereas wildcard imports do not. If a class does not exist in the package, a wildcard import does not create a dependency on it.

**J2 — Don't Inherit Constants**
There is a practice of putting constants in an interface and gaining access to those constants by inheriting that interface. Do not do this. Use a static import instead. Constants belong in the class where they are most meaningful, not in an inheritance hierarchy.

**J3 — Constants versus Enums**
Now that enums have been added to the language (Java 5+), use them. Don't keep using the old trick of `public static final int`. The meaning of `ints` can get lost. The meaning of `enums` cannot, because they belong to an enumeration that is named. Also, study the syntax for enums carefully. They can have methods and fields, making them very powerful tools that allow much more expression and flexibility than `int`s ever did.

---

### Names (N1–N7)

**N1 — Choose Descriptive Names**
Don't be too quick to choose a name. Make sure the name is descriptive. Remember that meanings tend to drift as software evolves, so frequently evaluate whether the name still makes sense. Software is a social activity, and names should be clear to the team, not just to the author.

**N2 — Choose Names at the Appropriate Level of Abstraction**
Don't pick names that communicate implementation; choose names that reflect the level of abstraction of the class or function you are working in. This is hard to do. Again, people are good at mixing levels of abstractions. Each time you make a pass over your code, look for variables that communicate implementation. Name them at the abstraction level of the function.

**N3 — Use Standard Nomenclature Where Possible**
Names are easier to understand if they are based on existing convention or usage. For example, if you are using the DECORATOR pattern, you should use the word `Decorator` in the names of the decorating classes. Patterns are examples of standard nomenclature. Design patterns are a rich source of standard names. Use them freely.

**N4 — Unambiguous Names**
Choose names that make the workings of a function or variable unambiguous:
```java
// Ambiguous
private String doRename() throws Exception

// Better
private String renamePage() throws Exception
```
The name `doRename` says nothing other than "does a rename." But `renamePage` makes clearer what is being renamed.

**N5 — Use Long Names for Long Scopes**
The length of a name should be related to the length of the scope. You can use very short variable names for tiny scopes, but for large scopes you should use longer names. Variable names like `i` and `j` are just fine if their scope is five lines long. But for the scope of a 100-line function, they are extremely poor choices.

**N6 — Avoid Encodings**
Names should not be encoded with type or scope information. Prefixes such as `m_` or `f` are useless in today's environments. Also, encoding project or subsystem information into a name rarely helps, and usually creates an extra burden on those who read the code.

**N7 — Names Should Describe Side-Effects**
Names should describe everything that a function, variable, or class is or does. Don't hide side effects with a name. Don't use a simple verb to describe a function that does more than just that simple action:
```java
// Bad — name hides side effect of creating
public ObjectOutputStream getOos() throws IOException {
    if (m_oos == null) {
        m_oos = new ObjectOutputStream(m_socket.getOutputStream());
    }
    return m_oos;
}

// Better
public ObjectOutputStream createOrReturnOos() throws IOException { ... }
```

---

### Tests (T1–T9)

**T1 — Insufficient Tests**
A test suite should test everything that could possibly break. The tests are insufficient so long as there are conditions that have not been explored by the tests or calculations that have not been validated.

**T2 — Use a Coverage Tool**
Coverage tools report gaps in your testing strategy. They make it easy to find modules, classes, and functions that are insufficiently tested. Most IDEs give you a visual indication of which lines are covered and which aren't. Use these tools and make sure that the coverage is high.

**T3 — Don't Skip Trivial Tests**
They are easy to write and their documentary value is higher than the cost to produce them.

**T4 — An Ignored Test Is a Question about an Ambiguity**
Sometimes we are uncertain about a behavioral detail because the requirements are unclear. We can express our question about the requirements as a test that is commented out, or a test that annotated with `@Ignore`. Which you choose depends upon whether the ambiguity is about something that would compile or not.

**T5 — Test Boundary Conditions**
Take special care to test boundary conditions. We often get the middle of an algorithm right but misjudge the boundaries.

**T6 — Exhaustively Test Near Bugs**
Bugs tend to congregate. When you find a bug in a function, it is wise to do an exhaustive test of that function. You'll probably find that the bug was not alone.

**T7 — Patterns of Failure Are Revealing**
Sometimes you can diagnose a problem by finding patterns in the way the test cases fail. This is another argument for making the test cases as complete as possible. Complete test cases, ordered in a reasonable way, expose patterns. As a simple example, if every test with a date later than a certain date fails, or if every test with a negative number for the second argument fails, then you probably know where the bug lives.

**T8 — Test Coverage Patterns Can Be Revealing**
Looking at the code that is or is not executed by the passing tests gives clues to why the failing tests fail.

**T9 — Tests Should Be Fast**
A slow test is a test that won't be run. When things get tight, it's the slow tests that will be dropped from the suite. Do what you must to keep your tests fast.

---

## Trade-offs and Caveats

**The small-function dogma.** Martin's prescription of 4–5 line functions is widely criticized as going too far. Excessive extraction into tiny functions can make code harder to follow by scattering a single coherent operation across dozens of named fragments. Context matters: a complex domain calculation may legitimately be 30 well-organized lines. The underlying principle — "do one thing" and "one level of abstraction" — is more important than the line-count prescription.

**Comments as failures.** Martin's position that comments represent failures is the most contested claim in the book. Many experienced developers and style guides (Google, Microsoft) disagree: well-written comments on public APIs, complex algorithms, and non-obvious architectural decisions are considered essential professional practice. The defensible position is that comments should explain *why*, not *what* — and *what* should always be expressible in code.

**Checked exceptions.** Martin's advice to prefer unchecked exceptions reflects Java-circa-2008 design frustrations with verbose checked exception propagation. Modern Java (and Kotlin) design practices are more nuanced; checked exceptions have legitimate uses in APIs where callers must handle recoverable failures. The principle of providing context with exceptions remains sound.

**Clean Code is Java-centric.** The book's examples are in Java. Some advice (Hungarian notation avoidance, constructor factory methods, class organization conventions) is partly language-specific. The underlying principles translate to other languages, but the specific forms differ.

**The heuristics appendix is a catalog, not a checklist.** The 72 heuristics in Chapter 17 are a distillation of the book's principles into a reference form. They are meant to be internalized, not mechanically applied one by one. Many overlap and reinforce each other. When two heuristics appear to conflict (e.g., G27 Structure over Convention vs. G24 Follow Standard Conventions), apply judgment: enforce important design decisions structurally; let style conventions be conventional.

**Publication date.** The book was published in 2008. The core principles (DRY, SRP, naming, small functions, TDD) are timeless. Some specific Java idioms are outdated (Java 5 concurrency utilities, the `J1–J3` Java-specific smells). Modern language features (records, sealed classes, pattern matching, functional constructs) provide additional ways to satisfy Clean Code principles that the book could not address.

---

## Sources

- [Robert C. Martin - Clean Code Heuristics (GitHub Gist, eujoy)](https://gist.github.com/eujoy/5d62a0d398571cb51bf6217cc3dfda2e) — Complete verified enumeration of all heuristic categories and numbers (C1–C5, E1–E2, F1–F4, G1–G36, N1–N7, T1–T9)
- [Chapter 17 – Smells & Heuristics (Vivek Khatri)](https://vivekkhatri.com/chapter-17-smells-heuristics-clean-code-robert-c-martin/) — Confirmed G1–G36 and J1–J3 categories with full descriptions; cross-referenced against gist
- [GitHub - janaipakos/Clean-Code-Smells-and-Heuristics](https://github.com/janaipakos/Clean-Code-Smells-and-Heuristics) — Community reference of all heuristics cross-referencing Martin and Fowler
- [GitHub - DanWareing/clean_code_heuristics](https://github.com/DanWareing/clean_code_heuristics) — Additional community reference for heuristic numbering and descriptions
- [Clean Code Smells And Heuristics (Diego Balduini, Medium)](https://medium.com/@mut_e/clean-code-smells-and-heuristics-9080d9ab67c1) — Language-agnostic rendering of all heuristics used to verify category completeness
