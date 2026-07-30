# Chapter 3: Builder Pattern

## Core Idea
Separate the construction of a complex object from its representation so that the same construction process can create different representations.

## Frameworks Introduced
- **Builder**: Separate the construction of a complex object from its representation so that the same construction processes can create different representations (GoF).
  - When to use: When an object has multiple parts and a complex, multi-step assembly process that should be decoupled from what the final assembled object looks like — e.g., assembling different vehicle types, or converting between text formats.
  - How: Define a `Builder` interface with step methods; each `ConcreteBuilder` implements those steps to assemble its own parts into a `Product`; a `Director` drives the builder through the same fixed sequence of steps regardless of which concrete builder is used.

## Key Concepts
- **Product**: The complex object under construction (`Product`, backed by a `LinkedList<string>` of parts in the example).
- **Builder**: The abstract interface (`IBuilder`) declaring the construction steps (`StartUpOperations`, `BuildBody`, `InsertWheels`, `AddHeadlights`, `EndOperations`) and a way to retrieve the finished product (`GetVehicle`).
- **ConcreteBuilder**: A class (`Car`, `MotorCycle`) that implements `IBuilder`, assembling its own parts into its own `Product` instance.
- **Director**: The class (`Director`) responsible for invoking the builder's steps in a fixed sequence via `Construct(IBuilder builder)`, without knowing which concrete builder or product it's working with.
- **Construction step**: One method in the `IBuilder` interface representing one stage of assembly (e.g., inserting wheels); concrete builders give each step a body appropriate to their product.
- **Same process, different representations**: The chapter's central mechanic — `Director.Construct()` calls the identical sequence of steps for both `Car` and `MotorCycle`, yet produces different final products because each concrete builder implements the steps differently.

## Mental Models
- The book's real-life analogy: ordering a custom computer — the same ordering/assembly *process* (choose parts, assemble) produces different final machines depending on customer preferences (e.g., 500GB disk + Intel vs. 250GB disk + AMD).
- The computer-world framing: converting one text format to another (e.g., RTF to ASCII) — the conversion process is the same shape regardless of target format, only the concrete "builder" for that format differs.
- Think of the Director as a recipe card that never changes ("start up, build body, add wheels, add headlights, finish") while the ConcreteBuilder is the chef who interprets each instruction differently depending on what's being made.
- Use Builder when you want fine-grained, step-by-step control over construction of a complex object while still exposing only one high-level "make the whole thing" operation to the caller.

## Anti-patterns
- **Using Builder for mutable objects that need post-construction modification**: the chapter's Q&A notes the pattern "is not suitable if you want to deal with mutable objects" in the sense the pattern is intended.
- **Expecting to avoid code duplication across concrete builders**: some duplication across builders is expected and can matter in some contexts — Builder doesn't eliminate all repetition, it isolates the *process* from the *representation*.
- **Adding a new product type without adding a new concrete builder**: the pattern requires a new `ConcreteBuilder` for every new product family; there's no shortcut around this per the chapter's stated drawback.

## Code Examples
```csharp
using System;
using System.Collections.Generic;//For LinkedList
namespace BuilderPattern
{
    // Builders common interface
    interface IBuilder
    {
        void StartUpOperations();
        void BuildBody();
        void InsertWheels();
        void AddHeadlights();
        void  EndOperations();
        Product GetVehicle();
    }
    // ConcreteBuilder: Car
    class Car : IBuilder
    {
        private string brandName;
        private Product;
        public Car(string brand)
        {
            product = new Product();
            this.brandName = brand;
        }
        public void StartUpOperations()
        {
            //Starting with brandname
            product.Add(string.Format("Car Model name :{0}",this.brandName));
        }
        public void BuildBody()
        {
            product.Add("This is a body of a Car");
        }
        public void InsertWheels()
        {
            product.Add("4 wheels are added");
        }
        public void AddHeadlights()
        {
            product.Add("2 Headlights are added");
        }
        public void EndOperations()
        {
            //Nothing in this case
        }
        public Product GetVehicle()
        {
            return product;
        }
    }
    // ConcreteBuilder:Motorcycle
    class MotorCycle : IBuilder
    {
        private string brandName;
        private Product product;
        public MotorCycle(string brand)
        {
            product = new Product();
            this.brandName = brand;
        }
        public void StartUpOperations()
        {
            //Nothing in this case
        }
        public  void BuildBody()
        {
            product.Add("This is a body of a Motorcycle");
        }
        public void InsertWheels()
        {
            product.Add("2 wheels are added");
        }
        public void AddHeadlights()
        {
            product.Add("1 Headlights are added");
        }
        public void EndOperations()
        {
            //Finishing up with brandname
            product.Add(string.Format("Motorcycle Model name :{0}", this.brandName));
        }
        public Product GetVehicle()
        {
            return product;
        }
    }
    // "Product"
    class Product
    {
        // We can use any data structure that you prefer e.g.List<string> etc.
        private LinkedList<string> parts;
        public Product()
        {
            parts = new LinkedList<string>();
        }
        public void Add(string part)
        {
            //Adding parts
            parts.AddLast(part);
        }
        public void Show()
        {
            Console.WriteLine("\nProduct completed as below :");
            foreach (string part in parts)
                Console.WriteLine(part);
        }
    }
    // "Director"
    class Director
    {
        IBuilder builder;
        // A series of steps-in real life, steps are complex.
        public void Construct(IBuilder builder)
        {
            this.builder = builder;
            builder.StartUpOperations();
            builder.BuildBody();
            builder.InsertWheels();
            builder.AddHeadlights();
            builder.EndOperations();
        }
    }
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("***Builder Pattern Demo***");
            Director director = new Director();
            IBuilder b1 = new Car("Ford");
            IBuilder b2 = new MotorCycle("Honda");
            // Making Car
            director.Construct(b1);
            Product p1 = b1.GetVehicle();
            p1.Show();
            //Making MotorCycle
            director.Construct(b2);
            Product p2 = b2.GetVehicle();
            p2.Show();
            Console.ReadLine();
        }
    }
}
```
- **What it demonstrates**: `Director.Construct()` calls the same five-step sequence on any `IBuilder`, but `Car` and `MotorCycle` each interpret those steps differently, producing distinct `Product` results from one shared process. (Note: the source text's `Car` class shows `private Product;` without a field name — apparently an OCR/text-extraction artifact from the original PDF; reproduced here exactly as it appears in the source, consistent with the `MotorCycle` class's correctly named `private Product product;` field for comparison.)

## Reference Tables
| Aspect | Abstract class | Interface (used in this chapter) |
|---|---|---|
| Default/shared implementation | Yes — can provide default method bodies | No — no implementation for any member |
| Adding a new method later | Existing subclasses keep working via inherited default | All implementers must be updated |
| Versioning multiple components | Easier — update base class, derived classes update automatically | Harder — a new interface version is needed |
| Best suited for | Closely related objects, large functional units | Unrelated classes, small/concise functionality, multiple-inheritance-like needs |

## Worked Example
`Program.Main` creates one `Director` and two builders: `Car("Ford")` and `MotorCycle("Honda")`. For each, it calls `director.Construct(builder)`, which runs `StartUpOperations → BuildBody → InsertWheels → AddHeadlights → EndOperations` in that fixed order, then retrieves the product via `GetVehicle()` and calls `Show()`. Output:
```
***Builder Pattern Demo***
Product completed as below :
Car Model name :Ford
This is a body of a Car
4 wheels are added
2 Headlights are added
Product completed as below :
This is a body of a Motorcycle
2 wheels are added
1 Headlights are added
Motorcycle Model name :Honda
```
Notably, `Car` adds its model name during `StartUpOperations` (first step) while `MotorCycle` adds its model name during `EndOperations` (last step) — the chapter confirms this is intentional, to show each concrete builder has freedom in exactly how it produces its final representation, even while both follow the same `Construct()` call sequence.

## Key Takeaways
1. Builder decouples the fixed, multi-step *construction process* (owned by the Director) from the *representation* of the final product (owned by each ConcreteBuilder).
2. The same `Construct()` call sequence can yield entirely different products depending on which concrete builder is passed in.
3. Concrete builders have full freedom in how they interpret each step — as shown by `Car` and `MotorCycle` placing the "add model name" logic at opposite ends of the sequence.
4. Prefer an abstract class over an interface when you want shared default behavior across builders or expect to version the contract; prefer an interface for small, unrelated-class contracts.
5. Builder isn't free of cost: expect some duplicated code across concrete builders, added concrete-builder classes for each new product, and reduced fit for objects that need later mutation.
6. This code targets pre-modern C# (circa C# 6/7, .NET Framework era, 2018); the Builder intent and Director/ConcreteBuilder separation still apply, but idiomatic C# today might use fluent method-chaining builders or object initializers/records for simpler cases.

## Connects To
- **Ch 1**: Both Singleton and Builder are Creational patterns, but Builder decomposes construction into explicit steps for complex multi-part objects, whereas Singleton restricts an object's cardinality to exactly one instance.
- **Ch 5**: The chapter's abstract-class-vs-interface discussion (MSDN recommendations on versioning, shared default behavior) recurs directly in Chapter 5's Q&A when discussing the Abstract Factory pattern's interface design.
- **GoF 1994 catalog**: Builder is one of the five Creational patterns in the original Gang of Four catalog, distinguished from Factory Method and Abstract Factory by its focus on *step-by-step* assembly of one complex product rather than one-shot creation of a product (or family of products).
