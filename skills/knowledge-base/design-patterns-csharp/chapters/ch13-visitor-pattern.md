# Chapter 13: Visitor Pattern

## Core Idea
Represent an operation to be performed on the elements of an object structure so that a new operation can be defined without changing the classes of the elements it operates on.

## Frameworks Introduced
- **Visitor**: Represent an operation to be performed on the elements of an object structure. Visitor lets you define a new operation without changing the classes of the elements on which it operates.
  - When to use: Public APIs or existing class hierarchies need to support plug-in operations added later, without modifying the original (often frozen or shared) source — an application of the open/closed principle.
  - How: Elements of the existing hierarchy implement an `Accept(IVisitor visitor)` method that calls back into the visitor (`visitor.Visit(this)` or a type-specific `VisitX` method), letting the visitor perform new operations on the element's data without the element's own code changing.

## Canonical GoF Reference (1994)
*Source: Gamma, Helm, Johnson & Vlissides, "Design Patterns: Elements of Reusable Object-Oriented Software" (Addison-Wesley, 1994).*

**Intent (verbatim)**: "Represent an operation to be performed on the elements of an object structure. Visitor lets you define a new operation without changing the classes of the elements on which it operates."

**Applicability** — GoF says use this pattern when:
- An object structure contains many classes of objects with differing interfaces, and you want to perform operations on them that depend on their concrete classes.
- Many distinct and unrelated operations need to be performed on objects in a structure, and you want to avoid "polluting" their classes with these operations — Visitor keeps related operations together in one class, and lets you put operations only in the applications that need them.
- The classes defining the object structure rarely change, but you often want to define new operations over the structure — changing those classes would require redefining the interface to all visitors, which is potentially costly; if the structure's classes change often, define the operations directly on them instead.

**Participants**:
- **Visitor** (`NodeVisitor`) — declares a `Visit` operation for each class of ConcreteElement; the operation's name/signature identifies the element's class, letting the visitor access it directly through its particular interface.
- **ConcreteVisitor** (`TypeCheckingVisitor`) — implements each operation declared by Visitor; each implements one fragment of the algorithm for the corresponding element class and provides/stores the algorithm's context, often accumulating results across the traversal.
- **Element** (`Node`) — defines an `Accept` operation taking a visitor as argument.
- **ConcreteElement** (`AssignmentNode`, `VariableRefNode`) — implements `Accept` to call back the visitor operation matching its own class.
- **ObjectStructure** (`Program`) — can enumerate its elements; may provide a high-level interface for the visitor to visit them; may be a Composite or a plain collection.

**Consequences**:
1. Visitor makes adding new operations easy — define one new visitor rather than editing every element class.
2. A visitor gathers related operations and separates unrelated ones — related behavior is localized in one visitor rather than spread across element classes; algorithm-specific data structures can be hidden in the visitor.
3. Adding new ConcreteElement classes is hard — each new element requires a new abstract operation on Visitor plus a corresponding implementation in every ConcreteVisitor; this is the pattern's central liability, and the deciding factor for whether Visitor is a good fit is whether the object structure's classes or the operations over them are more likely to change.
4. Visiting across class hierarchies — unlike an Iterator (bound to one common item type), a Visitor can operate over elements with no common parent class at all.
5. Accumulating state — visitors can accumulate results across a traversal instead of passing extra arguments or relying on globals.
6. Breaking encapsulation — Visitor assumes ConcreteElement exposes enough public state for the visitor to do its job, which can compromise the element's encapsulation.

**Implementation notes (double dispatch)**: In single-dispatch languages (C++, Smalltalk), which operation runs depends on the request's name and the receiver's type alone. Visitor's `Accept` is a *double-dispatch* operation — the operation actually executed depends on both the Visitor's type and the Element's type — achieved by having `Accept` call back a type-specific `VisitX` on the visitor rather than binding the operation statically into the Element interface. Traversal responsibility can live in the object structure (most common — a composite has each `Accept` recurse into children before/after visiting itself), in a separate Iterator, or in the Visitor itself (useful for irregular traversals, e.g., a `RepeatExpression` that must revisit its component repeatedly).

**Known Uses (1994-era)**: The Smalltalk-80 compiler's `ProgramNodeEnumerator`, used for source-analysis algorithms. IRIS Inventor's "actions" — visitors for rendering, event handling, searching, filing, and bounding-box computation over a 3-D scene graph, using a two-dimensional dispatch table (visitors × node classes) for double dispatch. Mark Linton coined the term "Visitor" in the X Consortium's Fresco toolkit spec.

**Related Patterns (per GoF)**: Composite — Visitor is commonly applied to operate over an object structure built with Composite. Interpreter — Visitor may be used to implement the interpretation step. GoF's discussion of behavioral patterns adds that Visitor is one of several patterns where an object is passed purely as an argument (here, to the polymorphic `Accept`) rather than being treated as part of the visited objects themselves.

## Key Concepts
- **Object structure**: The existing class hierarchy being visited (`IOriginalInterface` / `MyClass`), which the Visitor pattern is explicitly designed to leave unmodified.
- **Visitor hierarchy**: The new, separate hierarchy (`IVisitor` / `Visitor`) that contains the operations, decoupled from the object structure it acts on.
- **Double dispatch**: `element.Accept(visitor)` calls back to `visitor.Visit(element)` — the operation actually executed depends on both the element's type and the visitor's type, which single virtual-method dispatch alone can't express.
- **Open/closed principle**: Extension (new visitors/new operations) is allowed; modification of the existing element classes is disallowed — Visitor is a concrete mechanism for achieving this.
- **Encapsulation trade-off**: Visitor deliberately opens up an object's internals to an external visitor class, so by design it weakens encapsulation in exchange for extensibility.
- **Visitor + Composite combination**: When the object structure is itself a Composite tree, the visitor typically needs `VisitCompositeElement` and `VisitLeafNode` methods to handle branch vs. leaf nodes differently while still traversing uniformly.

## Mental Models
- Think of a taxi-booking scenario: once you (the "element") get in the taxi (the "visitor" takes control), the taxi can alter your route or even destination — control temporarily shifts to the visiting party without you needing to change who you are.
- Use Visitor when you need to bolt a new operation onto an existing, hard-to-touch class hierarchy — the new operation lives entirely in the visitor, not scattered across edits to every element class.
- The book's own escalation: a simple Visitor changing one integer field is the toy case; the "true power" shows up once Visitor is combined with Composite (Chapter 11) to gather and act on data across an entire tree without mutating the tree's own classes.

## Anti-patterns
- **Adding a new concrete element class frequently**: Every new element type requires updating the visitor interface and every existing concrete visitor to handle it — the visitor hierarchy becomes the maintenance bottleneck exactly where Composite/Iterator-style trees would otherwise be cheap to extend.
- **Using Visitor purely for convenience when encapsulation matters**: Because Visitor pulls internal state out to be processed externally, using it on classes whose invariants depend on hidden state risks violating those invariants without the compiler catching it.

## Code Examples
```csharp
interface IOriginalInterface
{
    void Accept(IVisitor visitor);
}

class MyClass : IOriginalInterface
{
    private int myInt = 5;//Initial or default value
    public int MyInt
    {
        get { return myInt; }
        set { myInt = value; }
    }

    public void Accept(IVisitor visitor)
    {
        Console.WriteLine("Initial value of the integer:{0}", myInt);
        visitor.Visit(this);
        Console.WriteLine("\nValue of the integer now:{0}", myInt);
    }
}

interface IVisitor
{
    void Visit(MyClass myClassElement);
}

class Visitor : IVisitor
{
    public void Visit(MyClass myClassElement)
    {
        Console.WriteLine("Visitor is trying to change the integer value.");
        myClassElement.MyInt = 100;
        Console.WriteLine("Exiting from Visitor.");
    }
}
```
- **What it demonstrates**: `MyClass` (the existing hierarchy) never contains the "set to 100" operation itself — it only exposes `Accept`, which hands control to `Visitor`, so a brand-new operation was added without touching `MyClass`'s own logic beyond the one generic `Accept` hook.

## Reference Tables
None in this chapter.

## Worked Example
The simple illustration: `MyClass` starts with `myInt = 5`. `myClass.Accept(visitor)` prints the initial value, calls `visitor.Visit(this)` which sets `MyInt = 100`, then prints the new value — output confirms `5` before and `100` after, entirely via the visitor.

The modified (combined) illustration reuses Chapter 11's college composite: `CompositeEmployee` and `Employee` both gain a `yearsOfExperience` field and an `Accept(IVisitor)` method that calls `VisitCompositeElement` or `VisitLeafNode` respectively. A single `Visitor` class implements promotion-eligibility rules that differ by node type: composites (HODs, experience > 15 years) vs. leaves (teachers, experience > 12 years). The demo iterates each manager's `Controls` list, calling `Accept` on each subordinate, and the visitor prints a promotion-eligible true/false per employee — for example, Math Teacher-1 (14 years, leaf, threshold 12) is eligible, while HOD-Maths (14 years, composite, threshold 15) is not. This shows Composite, Visitor, and (via `foreach`) Iterator working together.

## Key Takeaways
1. Visitor's core value is adding operations to a hierarchy you can't or shouldn't modify — if you can freely edit the element classes, a plain virtual method may be simpler.
2. `Accept`/`Visit` implements double dispatch: the actual code path depends on both the element's concrete type and the visitor's concrete type.
3. Visitor knowingly trades away encapsulation — an external class reaches into and mutates or reads an element's state, so it should be a deliberate choice, not a default.
4. Combining Visitor with Composite requires per-node-type visit methods (`VisitCompositeElement` vs. `VisitLeafNode`) so the visitor can apply different rules to branches vs. leaves while still traversing uniformly.
5. Adding a new element type to the object structure is expensive under Visitor (every visitor must be updated) — the pattern optimizes for "new operations, stable types," not the reverse.
6. This example predates modern C# (2018-era): the code uses classic getter/setter properties, no pattern matching on element type, and no records — the double-dispatch structure is unchanged in modern idiom, though switch expressions could simplify the visitor body (see modern-csharp-notes.md).

## Connects To
- **Ch 11 (Composite)**: The modified illustration in this chapter directly reuses Chapter 11's college org-chart Composite structure to demonstrate Visitor's real power over tree data.
- **Ch 18 (Iterator)**: The combined example's `foreach` loops over composite children are functioning as an implicit Iterator, making the three-pattern combination (Visitor + Composite + Iterator) explicit.
- **GoF 1994 catalog**: Visitor is one of the original eleven Behavioral patterns and is often cited as the most structurally complex of the GoF patterns due to double dispatch.
- **GoF 1994 canonical entry**: The original catalog names the pattern's central liability explicitly as a design trade-off, not just a caveat — Visitor is the right choice only when the element hierarchy is stable and operations churn, and the wrong choice when new element types are added frequently, since each one forces a new abstract method onto Visitor and an override in every ConcreteVisitor.
