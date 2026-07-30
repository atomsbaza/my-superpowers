# Chapter 11: Composite Pattern

## Core Idea
Compose objects into tree structures to represent part-whole hierarchies. Composite lets clients treat individual objects (leaves) and compositions of objects (branches) uniformly.

## Frameworks Introduced
- **Composite**: Compose objects into tree structures to represent part-whole hierarchies. Composite lets clients treat individual objects and compositions of objects uniformly.
  - When to use: You have tree-structured data and want client code to stop discriminating between a single leaf node and a branch that contains many nodes.
  - How: Define a common interface (`IEmployee`) implemented both by leaf objects (`Employee`) and by a container object (`CompositeEmployee`) that holds a list of children of that same interface type and delegates operations to them recursively.

## Key Concepts
- **Part-whole hierarchy**: A structure where whole objects are built from parts, and parts can themselves be wholes containing further parts (a tree).
- **Component interface**: The shared contract (`IEmployee.PrintStructures()`) that both leaves and composites implement, enabling uniform treatment.
- **Leaf**: A node with no children (`Employee`) — implements the component interface but has no `Add`/`Remove`.
- **Composite**: A node that holds children (`CompositeEmployee`) and implements the component interface by iterating over and delegating to its children.
- **Safety vs. transparency trade-off**: Putting `Add`/`Remove` on the shared interface is "transparent" (uniform) but "unsafe" (leaves must implement meaningless operations); keeping them only on the composite class is safer but less transparent. The GoF explicitly frame this as a trade-off, not a rule.
- **Recursive delegation**: A composite's method implementation just loops over children and calls the same method on each — this is what makes the tree traversal implicit rather than something the client codes by hand.

## Mental Models
- Think of a college organization: a Principal sits above two Heads of Department (HOD-Maths, HOD-CSE), each of whom supervises several teachers. Every one of these people is fundamentally an "employee" — the org chart is a tree, and printing "who works here" should work the same way whether you start from the Principal, an HOD, or a single teacher.
- Use Composite when you catch yourself writing `if (node is Leaf) ... else if (node is Branch) ...` throughout client code — that branching is exactly what the shared interface should absorb.
- Traversal note from the book: when you need to visit every node of the composite tree, you'll often reach for an Iterator pattern (Chapter 18) alongside Composite.

## Anti-patterns
- **Special-casing branches vs. leaves in client code**: Defeats the entire purpose of the pattern; if client code needs `is`/type checks to decide how to call an object, the abstraction has leaked.
- **Putting Add/Remove on the leaf via the shared interface without a plan for it**: Forces leaves to implement operations that make no sense for them (a teacher can't "add a subordinate"), silently breaking the safety guarantee unless you throw or no-op deliberately.

## Code Examples
```csharp
interface IEmployee
{
    void PrintStructures();
}

class CompositeEmployee : IEmployee
{
    private string name;
    private string dept;
    //The container for child objects
    private List<IEmployee> controls;

    public CompositeEmployee(string name, string dept)
    {
        this.name = name;
        this.dept = dept;
        controls = new List<IEmployee>();
    }

    public void Add(IEmployee e) { controls.Add(e); }
    public void Remove(IEmployee e) { controls.Remove(e); }

    public void PrintStructures()
    {
        Console.WriteLine("\t" + this.name + "works in" + this.dept);
        foreach (IEmployee e in controls)
        {
            e.PrintStructures();
        }
    }
}

class Employee : IEmployee
{
    private string name;
    private string dept;

    public Employee(string name, string dept)
    {
        this.name = name;
        this.dept = dept;
    }

    public void PrintStructures()
    {
        Console.WriteLine("\t\t"+this.name + "works in" + this.dept);
    }
}
```
- **What it demonstrates**: One interface (`IEmployee`) implemented by both a leaf (`Employee`) and a composite (`CompositeEmployee`) so that `PrintStructures()` works identically at any level of the tree, including after runtime `Add`/`Remove` mutations.

## Reference Tables
None in this chapter.

## Worked Example
The demo builds a college org chart: a `CompositeEmployee` Principal contains two `CompositeEmployee` HODs (Maths, CSE); the Maths HOD contains 2 `Employee` teachers, the CSE HOD contains 3. Calling `Principal.PrintStructures()` recursively prints the entire org chart. Calling `hodCompSc.PrintStructures()` prints only the CSE subtree, and calling a single teacher's `PrintStructures()` prints just that leaf — all through the exact same method call. The demo then removes one CSE teacher via `hodCompSc.Remove(cseTeacher2)` and reprints the full structure from the Principal to show the tree updates uniformly, without any client-side branching logic to handle "is this a leaf or a branch."

## Key Takeaways
1. A single component interface implemented by both leaves and composites is what lets client code stay uniform regardless of tree depth or position.
2. Deciding whether `Add`/`Remove` belong on the shared interface or only on the composite class is a deliberate safety-vs-transparency trade-off, not a bug to fix.
3. There's no requirement to use a particular collection type for children — a `List<T>` is a convenience, not part of the pattern's contract.
4. Composite and Iterator (Chapter 18) are natural partners: once you have a tree, you often need a standard way to walk it.
5. This example predates modern C# (2018-era, targeting C# 6/7): it uses classic getters, manual `foreach` loops, and no records, expression-bodied members, or pattern matching — the Composite intent still applies, but idiomatic 2020s C# would express parts of this more tersely (see modern-csharp-notes.md).

## Connects To
- **Ch 13 (Visitor)**: The book's modified Visitor example directly reuses this chapter's college composite structure, adding an `Accept(IVisitor)` method to both `Employee` and `CompositeEmployee` to demonstrate Visitor-over-Composite.
- **Ch 18 (Iterator)**: Traversing a composite tree commonly needs an Iterator to standardize "visit every node" without exposing the internal list structure.
- **GoF 1994 catalog**: Composite is one of the seven original Structural patterns, alongside Adapter, Bridge, Decorator, Facade, Flyweight, and Proxy.
