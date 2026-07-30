# Chapter 16: Template Method Pattern

## Core Idea
Define the skeleton of an algorithm in an operation, deferring some steps to subclasses. Subclasses can redefine certain steps of the algorithm without changing its overall structure.

## Frameworks Introduced
- **Template Method**: Define the skeleton of an algorithm in an operation, deferring some steps to subclasses. The Template Method pattern lets subclasses redefine certain steps of an algorithm without changing the algorithm's structure.
  - When to use: You have a multistep algorithm that is mostly identical across variants, and you want to allow subclasses to customize specific steps without letting them touch the overall flow.
  - How: An abstract base class exposes one non-overridable (or non-virtual) "template" method that calls a fixed sequence of private/concrete helper methods and one or more abstract (or virtual "hook") methods. Subclasses override only the abstract/hook methods; the base class retains control of the sequence.

## Key Concepts
- **Template method**: The method in the base class that defines the fixed sequence of steps (e.g., `Papers()` calling `Math()`, `SoftSkills()`, `SpecialPaper()`).
- **Abstract step**: A step subclasses must implement (e.g., `SpecialPaper()`), representing the varying part of the algorithm.
- **Concrete step**: A step shared by all subclasses and not overridable (e.g., `Math()`, `SoftSkills()`), representing the fixed part of the algorithm.
- **Hook method**: A virtual method with a default implementation that subclasses may optionally override to opt in/out of an optional step (e.g., `IsAdditionalPapersNeeded()`).
- **Inversion of control**: The base class calls into the subclass (not the other way around) — "Hollywood principle: don't call us, we'll call you."
- **Boss of the flow**: In Template Method, the base class controls execution order; the client cannot reorder steps (contrast with Builder, where the client dictates order).

## Mental Models
- Think of it as designing an online engineering degree: every course shares the same first-semester structure (Math, Soft Skills), but later semesters add a track-specific special paper (Computer Science vs Electronics) without altering the shared skeleton.
- Real-life analogy from the book: making a pizza always follows the same basic mechanism, but the final toppings/ingredients vary by customer choice (vegetarian vs meat, extra cheese, etc.) — the process skeleton is fixed, the details vary.
- Use Template Method when you want to avoid duplicated boilerplate across near-identical algorithms but still allow bounded, well-defined customization points.
- Distinguish from plain polymorphism: Template Method deliberately restricts subclasses to redefining only specific steps, not overriding the entire workflow.

## Anti-patterns
- **Letting subclasses override the template method itself**: This defeats the pattern's purpose — the shared algorithm structure must stay fixed and non-overridable (or at least not intended for override) in the base class.
- **Overriding a step with an empty method body to skip it**: The book notes this works but is inferior to using an explicit hook method (e.g., `IsAdditionalPapersNeeded()`) that clearly signals optionality.
- **Adding too many subclasses for minor variations**: More subclasses means more scattered code, which becomes difficult to maintain.

## Code Examples
```csharp
// BasicEngineering.cs
using System;
namespace TemplateMethodPattern
{
    public abstract class BasicEngineering
    {
        public void Papers()
        {
            //Common Papers:
            Math();
            SoftSkills();
            //Specialized Paper:
            SpecialPaper();
        }
        private void Math() { Console.WriteLine("Mathematics"); }
        private void SoftSkills() { Console.WriteLine("SoftSkills"); }
        public abstract void SpecialPaper();
    }
}
//ComputerScience.cs
using System;
namespace TemplateMethodPattern
{
    public class ComputerScience:BasicEngineering
    {
        public override void SpecialPaper() { Console.WriteLine("Object-Oriented Programming"); }
    }
}
//Electronics.cs
using System;
namespace TemplateMethodPattern
{
    public class Electronics:BasicEngineering
    {
        public override void SpecialPaper() { Console.WriteLine("Digital Logic and Circuit Theory"); }
    }
}
```
- **What it demonstrates**: `Papers()` is the template method — it always runs `Math()` and `SoftSkills()` in order, then delegates the varying `SpecialPaper()` step to whichever subclass (`ComputerScience` or `Electronics`) is instantiated.

## Reference Tables
| Pattern | Type | Who controls step order | Key distinction |
|---|---|---|---|
| Template Method | Behavioral | Base class (boss) | Subclasses redefine steps but never the sequence |
| Builder | Creational | Client/customer (boss) | Client controls order of construction steps |

## Worked Example
`BasicEngineering` is an abstract class with a public `Papers()` template method that calls private `Math()` and `SoftSkills()` steps followed by the abstract `SpecialPaper()` step. `ComputerScience` overrides `SpecialPaper()` to print "Object-Oriented Programming"; `Electronics` overrides it to print "Digital Logic and Circuit Theory". `Program.Main` creates a `BasicEngineering` reference pointing to `ComputerScience`, calls `Papers()`, then reassigns it to `Electronics` and calls `Papers()` again — producing "Mathematics / SoftSkills / Object-Oriented Programming" and "Mathematics / SoftSkills / Digital Logic and Circuit Theory" respectively.

The Q&A extension adds a hook method `IsAdditionalPapersNeeded()` (returns `true` by default) checked inside `Papers()` before calling a new `AdditionalPapers()` step. `Electronics` overrides the hook to return `false` (opting out), while `ComputerScience` leaves the default `true` (opting in), so only the Computer Science output includes "AdditionalPapers are needed in this stream."

## Key Takeaways
1. The template method itself must remain fixed — customization happens only through designated abstract or hook methods, never by letting subclasses reorder or bypass the algorithm.
2. Use hook methods (virtual methods with default behavior) to make optional steps explicit and controllable, rather than having subclasses override a step with an empty body.
3. Template Method centralizes common code in the base class, eliminating duplication across subclasses that share most of an algorithm.
4. Watch for Liskov Substitution Principle risk: subclasses overriding base-defined steps can subtly change behavior in ways that break substitutability if not carefully scoped.
5. This is a behavioral pattern (controls *how* an algorithm's steps are distributed), distinct from the creational Builder pattern (controls *what* gets constructed and in what client-chosen order) — the two are easy to confuse because both involve step-by-step processes.
6. The book's C# (2018, pre-C# 8) code uses classic abstract classes and `override`; the pattern's intent — fixed skeleton, deferred steps — still applies in modern C#, though idioms like default interface methods could reshape the implementation.

## Connects To
- **Ch 3 (Builder, if present in this catalog)**: Both are step-by-step processes, but Template Method fixes the sequence in the base class while Builder lets the client direct it.
- **GoF 1994 catalog**: Template Method is one of the original 23 GoF patterns, classified as behavioral, and is frequently taught alongside Strategy since both defer behavior but via different mechanisms (inheritance vs composition).
