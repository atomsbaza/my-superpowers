# Chapter 23: Interpreter Pattern

## Core Idea
Given a language, define a representation for its grammar along with an interpreter that uses that representation to interpret sentences in the language.

## Frameworks Introduced
- **Interpreter**: Given a language, define a representation for its grammar along with an interpreter that uses the representation to interpret sentences in the language (GoF).
  - When to use: You have a small, well-defined language or notation whose sentences need repeated evaluation — the book's own Q&A cautions this is rarely needed in everyday programming and should be weighed against its cost.
  - How: Represent each grammar rule as a class deriving from a common abstract expression type; a `Context` carries the input/output state; a "parse tree" of expression objects interprets the context piece by piece.

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
