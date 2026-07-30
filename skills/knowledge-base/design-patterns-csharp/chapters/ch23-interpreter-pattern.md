# Chapter 23: Interpreter Pattern

## Core Idea
Given a language, define a representation for its grammar along with an interpreter that uses that representation to interpret sentences in the language.

## Frameworks Introduced
- **Interpreter**: Given a language, define a representation for its grammar along with an interpreter that uses the representation to interpret sentences in the language (GoF).
  - When to use: You have a small, well-defined language or notation whose sentences need repeated evaluation — the book's own Q&A cautions this is rarely needed in everyday programming and should be weighed against its cost.
  - How: Represent each grammar rule as a class deriving from a common abstract expression type; a `Context` carries the input/output state; a "parse tree" of expression objects interprets the context piece by piece.

## Canonical GoF Reference (1994)
*Source: Gamma, Helm, Johnson & Vlissides, "Design Patterns: Elements of Reusable Object-Oriented Software" (Addison-Wesley, 1994).*

**Intent (verbatim)**: "Given a language, define a representation for its grammar along with an interpreter that uses the representation to interpret sentences in the language."

**Applicability** — GoF says use the pattern when there is a language to interpret and its statements can be represented as abstract syntax trees; it works best when:
- The grammar is simple — for complex grammars the class hierarchy becomes large and unmanageable, and a parser generator is the better tool.
- Efficiency is not a critical concern — the most efficient interpreters translate the parse tree into another form first (e.g., regular expressions into state machines) rather than interpreting the tree directly, though that translator can itself be built with Interpreter.

**Participants**:
- **AbstractExpression** (`RegularExpression`) — declares an abstract `Interpret` operation common to all nodes in the abstract syntax tree.
- **TerminalExpression** (`LiteralExpression`) — implements `Interpret` for terminal symbols; one instance is required per terminal symbol in a sentence.
- **NonterminalExpression** (`AlternationExpression`, `RepetitionExpression`, `SequenceExpression`) — one class per grammar rule of the form `R ::= R1 R2 ... Rn`; holds instance variables of type AbstractExpression for each Ri and implements `Interpret` by recursing into them.
- **Context** — holds information global to the interpreter (e.g., the input string and how much has been matched).
- **Client** — builds (or is given) the abstract syntax tree for a particular sentence and invokes `Interpret`.

**Consequences**:
1. It's easy to change and extend the grammar — because rules map to classes, inheritance lets you modify existing expressions incrementally and define new ones as variations.
2. Implementing the grammar is easy too — the classes for each tree node have similar shapes and are straightforward (even automatable) to write.
3. Complex grammars are hard to maintain — one class per rule (sometimes more, for BNF) means many rules produce many classes; beyond a certain complexity, parser/compiler generators are more appropriate.
4. Adding new ways to interpret expressions is easy — new operations (pretty-printing, type-checking) can be added as new methods on the expression classes; if new interpretations keep appearing, consider moving them into a **Visitor** instead of growing the grammar classes.

**Implementation notes**: (1) Creating the abstract syntax tree is out of scope for the pattern itself — it doesn't address parsing; a table-driven parser, a hand-written recursive-descent parser, or the client directly can build it. (2) Defining `Interpret` doesn't have to live on the expression classes — if new interpreters are created often, moving `Interpret` into a separate Visitor object avoids repeatedly modifying every grammar class. (3) Sharing terminal symbols via **Flyweight** — grammars whose sentences repeat the same terminal many times (e.g., a variable name across a program) benefit from sharing one instance per terminal, distinguishing shared intrinsic state from passed-in (extrinsic) context.

**Known Uses (1994-era)**: Smalltalk compilers' widespread use of the pattern; SPECTalk, interpreting descriptions of input file formats; the QOCA constraint-solving toolkit, using it to evaluate constraints.

**Related Patterns (per GoF)**: **Composite** — the abstract syntax tree is itself an instance of Composite. **Flyweight** shows how to share terminal symbols within the tree. **Iterator** can be used to traverse the tree structure. **Visitor** can be used to keep the behavior for each tree node in one class instead of scattering it across the grammar classes.

## Key Concepts
- **Grammar**: A formal definition of the language's structure — here, a three-digit number is defined as `E ::= E1 E2 E3` (hundreds, tens, units).
- **Context**: Holds shared interpretation state — the raw input, a validity flag (`CanProceed`), and the accumulating output string (`SetOutput`).
- **InputExpression (abstract)**: The common abstract base for all grammar-rule classes, exposing an `Interpret(Context context)` method.
- **HundredExpression / TensExpression / UnitExpression**: Concrete expression classes, each responsible for interpreting one grammar rule (hundreds digit, tens digit, units digit) and appending its piece to `Context.SetOutput`.
- **Parse tree**: The ordered list of expression objects (`List<InputExpression>`) that the client builds and then walks, calling `Interpret` on each in turn.
- **Validation gate**: `ValidateUserInputBeforeProceedings` checks the input is parseable and in range (100–999) before any expression is allowed to interpret it, using the `CanProceed` flag as a guard each expression checks.

## Mental Models
- Think of a translator converting a foreign language sentence-by-sentence, or a musician reading music notation — the notation is the grammar, and the musician is the interpreter that turns symbols into sound.
- Think of it as compiler front-ends in miniature: the Java compiler interprets source into bytecode for the JVM, and C# source is converted to MSIL, later JIT-compiled to native code — both are larger-scale analogues of "define a grammar representation, then interpret it."
- Use Interpreter only when you are effectively building a small custom language or notation of your own — the Q&A frames this explicitly as a return-on-investment question, not something needed in "daily programming life."
- Model each grammar production rule as its own class rather than one big parser method — this keeps each rule's interpretation logic isolated and independently extensible, at the cost of proliferating small classes.

## Anti-patterns
- **Reaching for Interpreter without a real grammar need**: the chapter itself warns this pattern is rarely needed in daily programming and should only be used when you truly need to define, change, and extend your own grammar.
- **Skipping the validity check before interpreting**: without a guard like `CanProceed`, expression classes could operate on malformed or out-of-range input (the example restricts input to 100–999) and produce garbage output.
- **Letting grammar complexity grow unchecked**: maintaining a complex grammar requires creating and maintaining a separate class per rule, which the chapter's Q&A calls out as the pattern's biggest practical concern.

## Code Examples
```csharp
public class Context
{
    private int getInput;
    private string getStringInput;
    private string setOutput;
    private bool canProceed = false;
    public bool CanProceed { get {return canProceed;} }
    public int GetInput { get {return getInput;} }
    public string SetOutput { get {return setOutput;} set {setOutput = value;} }
    public Context(string input) { this.getStringInput = input; }
    public int ValidateUserInputBeforeProceedings(string inputString)
    {
        if (int.TryParse(inputString, out getInput))
        {
            Console.WriteLine("You have entered {0}", getInput);
            if ((getInput < 100) || (getInput > 999))
            {
                Console.WriteLine("Please enter a number between 100 and 999 and try again.");
                return -9999;
            }
        }
        canProceed = true;
        return getInput;
    }
}
abstract class InputExpression
{
    public abstract void Interpret(Context context);
}
class HundredExpression : InputExpression
{
    public override void Interpret(Context context)
    {
        if (context.CanProceed)
        {
            int hundreds = context.GetInput / 100;
            switch (hundreds)
            {
                case 1: context.SetOutput += "One Hundred"; break;
                // ... cases 2-9 ...
                default: context.SetOutput += "*"; break;
            }
        }
    }
}
```
- **What it demonstrates**: `Context` centralizes shared state (input, validity, accumulating output) while each `InputExpression` subclass interprets only its own grammar rule, guarded by `context.CanProceed` before doing any work.

```csharp
// Build the 'parse tree'
List<InputExpression> expTree = new List<InputExpression>();
expTree.Add(new HundredExpression());
expTree.Add(new TensExpression());
expTree.Add(new UnitExpression());
// Interpret the valid input
foreach (InputExpression inputExp in expTree)
{
    inputExp.Interpret(context);
}
```
- **What it demonstrates**: The client assembles an ordered list of expression objects (the "parse tree") and interprets the shared `context` by walking that list in sequence — hundreds, then tens, then units — accumulating the output string across all three.

## Reference Tables
| Grammar Symbol | Class | Responsibility |
|---|---|---|
| `E` (whole expression) | `InputExpression` (abstract) | Common interpretation contract |
| `E1` (hundreds) | `HundredExpression` | Interprets the hundreds digit |
| `E2` (tens) | `TensExpression` | Interprets the tens digit |
| `E3` (units) | `UnitExpression` | Interprets the units digit |

## Worked Example
The client prompts for a three-digit number. A `Context` is constructed from the raw string, and `ValidateUserInputBeforeProceedings` checks it parses as an integer and falls within 100–999; on success it sets `CanProceed = true` and returns the parsed integer, otherwise it returns `-9999` and the client skips interpretation entirely. On success, the client builds a "parse tree" — a `List<InputExpression>` containing one `HundredExpression`, one `TensExpression`, and one `UnitExpression`, in that order — and calls `Interpret(context)` on each in turn, each appending its own piece to `context.SetOutput`. For input `375`, this produces "Three Hundred" + "Seventy" + "Five", printed as "Original Input 375 is interpreted as Three Hundred Seventy Five". For invalid input like `-769`, validation fails before any expression runs, and the program prints "Please enter a number between 100 and 999 and try again."

## Key Takeaways
1. Interpreter represents each grammar rule as its own class, letting you evaluate "sentences" in a small custom language by walking a tree of expression objects.
2. A shared `Context` object carries state (input, a validity flag, accumulating output) so each expression class can operate independently without expressions needing to reference each other.
3. Real-world software examples of this same underlying idea include compiler front-ends: Java source to bytecode for the JVM, or C# source to MSIL for the CLR (later JIT-compiled to native code).
4. The chapter is explicit that this pattern is rarely justified in ordinary application code — evaluate the return on investment before introducing a custom grammar and its associated class proliferation.
5. This code targets pre-modern C# (2018, .NET Framework era) — the grammar-as-classes intent still applies, but a modern rewrite might lean on pattern matching (`switch` expressions) or a parser-combinator library instead of one class per grammar rule.

## Connects To
- **Ch 22 (Chain of Responsibility)**: Both patterns process a `List`/chain of objects in sequence, but Interpreter's list (the "parse tree") always runs every element to accumulate output, whereas Chain of Responsibility's chain stops as soon as one handler claims the request.
- **GoF 1994 catalog**: Interpreter is one of the Behavioral patterns in the original Gang of Four catalog, and is generally considered one of its least frequently applied patterns in mainstream application development.
- **GoF 1994 canonical entry**: The original catalog's explicit warning — one class per grammar rule quickly becomes unmanageable, so the pattern suits only *simple* grammars, with complex grammars better served by a parser generator — is the load-bearing caveat missing from a from-scratch three-digit-number example.
