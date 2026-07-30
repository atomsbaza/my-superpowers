# Chapter 2: Prototype Pattern

## Core Idea
Specify the kinds of objects to create using a prototypical instance, and create new objects by copying this prototype — avoiding the expense of building a new instance from scratch.

## Frameworks Introduced
- **Prototype**: Specify the kinds of objects to create using a prototypical instance, and create new objects by copying this prototype (GoF).
  - When to use: When creating a new instance is expensive or complex, but you already have a similar object available to copy and then adjust.
  - How: Define an abstract prototype with a `Clone()` method; concrete prototypes implement `Clone()` (commonly via `MemberwiseClone()` for a shallow copy) and return a copy of themselves that the client then customizes.

## Key Concepts
- **Prototype**: The abstract base class (`BasicCar` in the example) that declares the `Clone()` contract all concrete prototypes must implement.
- **Concrete Prototype**: A class (`Nano`, `Ford`) that implements `Clone()`, typically by calling `MemberwiseClone()` and casting the result to its own type.
- **`MemberwiseClone()`**: A .NET method that creates a new object and copies the nonstatic fields of the current object into it — performing a bit-by-bit copy for value types but only copying the reference for reference types.
- **Shallow copy**: A copy where reference-type fields still point to the original referenced objects — the new object and the source object share those sub-objects.
- **Deep copy**: A copy where referenced objects are themselves copied recursively, so the new object graph shares nothing with the original.
- **Copy constructor**: A user-defined constructor (e.g., `Student(Student student)`) that builds a new object by explicitly copying fields from an existing instance of the same type — an alternative to `Clone()`/`MemberwiseClone()`.
- **Client**: `Program.cs`, which holds "base" prototype instances and clones them to produce new, individually priced objects rather than constructing each from scratch.

## Mental Models
- The book's real-life analogy: photocopying a master document to experiment with edits, instead of retyping the whole document from scratch — you clone the "prototype" and then modify the copy.
- The computer-world framing: given a stable application, you copy it first, then make and analyze changes on the copy — you don't want to rebuild from zero just to explore a variant.
- Think of shallow copy as "copying the address, not the house": if object X1 references Y1, a shallow copy X2 also references the same Y1 — changes through Y1 are visible from both X1 and X2.
- Think of deep copy as "copying the whole house and everything inside it": copying X1 deeply produces X3 with its own new Y3 (a copy of Y1), which itself has its own new Z3 (a copy of Z1) — nothing is shared.

## Anti-patterns
- **Assuming `MemberwiseClone()` gives full independence**: it only performs a shallow copy, so any reference-type fields on the cloned object still point at the *same* referenced objects as the original — mutating them affects both.
- **Cloning objects with circular references or types that don't support copying**: the chapter notes this can make implementing the cloning mechanism challenging or infeasible without extra design work.
- **Ignoring per-subclass cloning burden**: every concrete prototype must implement its own cloning/copying logic — this is boilerplate that grows with the number of subclasses.

## Code Examples
```csharp
//BasicCar.cs
using System;
namespace PrototypePattern
{
    public abstract class BasicCar
    {
        public string ModelName{get;set;}
        public int Price {get; set;}
        public static int SetPrice()
        {
            int price = 0;
            Random r = new Random();
            int p = r.Next(200000, 500000);
            price = p;
            return price;
        }
        public abstract BasicCar Clone();
    }
}
//Nano.cs
using System;
namespace PrototypePattern
{
    public class Nano:BasicCar
    {
        public Nano(string m)
        {
            ModelName = m;
        }
        public override BasicCar Clone()
        {
            return (Nano) this.MemberwiseClone();//shallow Clone
        }
    }
}
//Ford.cs
using System;
namespace PrototypePattern
{
    public class Ford:BasicCar
    {
        public Ford(string m)
        {
            ModelName = m;
        }
        public override BasicCar Clone()
        {
            return (Ford)this.MemberwiseClone();
        }
    }
}
//Client
using System;
namespace PrototypePattern
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("***Prototype Pattern Demo***\n");
            //Base or Original Copy
            BasicCar nano_base = new Nano("Green Nano") {Price = 100000};
            BasicCar ford_base = new Ford("Ford Yellow") {Price = 500000};
            BasicCar bc1;
            //Nano
            bc1 = nano_base.Clone();
            bc1.Price = nano_base.Price+BasicCar.SetPrice();
            Console.WriteLine("Car is: {0}, and it's price is Rs. {1} ",bc1.ModelName,bc1.Price);
            //Ford
            bc1 = ford_base.Clone();
            bc1.Price = ford_base.Price+BasicCar.SetPrice();
            Console.WriteLine("Car is: {0}, and it's price is Rs. {1}", bc1.ModelName, bc1.Price);
            Console.ReadLine();
        }
    }
}
```
- **What it demonstrates**: An abstract `Clone()` contract with two concrete prototypes that each shallow-clone themselves via `MemberwiseClone()`, letting the client derive new priced instances from held "base" prototypes instead of constructing them anew.

```csharp
using System;
namespace PrototypePatternQAs
{
    class Student
    {
        int rollNo;
        string name;
        //Instance Constructor
        public Student(int rollNo, string name)
        {
            this.rollNo = rollNo;
            this.name = name;
        }
        //Copy Constructor
        public Student(Student student)
        {
            this.name = student.name;
            this.rollNo = student.rollNo;
        }
        public void DisplayDetails()
        {
            Console.WriteLine("Student name :{0}, Roll no: {1}", name,rollNo);
        }
    }
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("***A simple copy constructor demo***\n");
            Student student1 = new Student(1, "John");
            Console.WriteLine("The details of student1 is as follows:");
            student1.DisplayDetails();
            Console.WriteLine("\n Copying student1 to student2 now");
            Student student2 = new Student (student1);
            Console.WriteLine("The details of student2 is as follows:");
            student2.DisplayDetails();
            Console.ReadKey();
        }
    }
}
```
- **What it demonstrates**: A copy constructor as an alternative cloning mechanism to `Clone()`/`MemberwiseClone()` — the new object's fields are explicitly assigned from the source object inside the constructor body.

## Reference Tables
| Copy type | Value-type fields | Reference-type fields | Mechanism used in chapter |
|---|---|---|---|
| Shallow copy | Bit-by-bit copied | Reference copied (shared target) | `MemberwiseClone()` |
| Deep copy | Bit-by-bit copied | New copies created recursively | Not implemented in this chapter's code; discussed conceptually |

## Worked Example
`Program.Main` creates two "base" prototypes: a Nano priced at 100,000 and a Ford priced at 500,000. For each, it calls `Clone()` to get an independent copy (`bc1`), then adds a random price component from `BasicCar.SetPrice()` (a random number between 200,000 and 500,000) to the *original* base price and assigns it to the clone. Output looks like:
```
***Prototype Pattern Demo***
Car is: Green Nano, and it's price is Rs. 486026
Car is: Ford Yellow, and it's price is Rs. 886026
```
The exact numbers vary run to run because of the random price generator, but the chapter notes the Ford price is guaranteed to exceed the Nano price since Ford's base price (500,000) is higher to start with. The separate copy-constructor demo constructs `student1` (roll 1, "John"), then builds `student2` via `new Student(student1)`, and both display identical details — showing the copy constructor produced an independent object with the same field values.

## Key Takeaways
1. Prototype trades "construct from scratch" for "clone an existing instance and adjust," which pays off when construction is expensive or complex.
2. `MemberwiseClone()` in C# only performs a shallow copy — reference fields are shared between original and clone, not duplicated.
3. Deep copying must be implemented manually (e.g., recursively cloning referenced objects) when reference-type state must not be shared between the original and the clone.
4. A copy constructor is a viable alternative to the `Clone()` method for a similar effect, and is sometimes simpler for a single class without a prototype hierarchy.
5. Each concrete prototype subclass bears its own cloning implementation burden — there's no free lunch for a deep object graph or hard-to-copy types (e.g., those with circular references).
6. This code targets pre-modern C# (circa C# 6/7, .NET Framework era, 2018); the Prototype intent and shallow/deep-copy reasoning still apply, but idiomatic C# today might use `with` expressions on records for a built-in shallow-copy-and-modify workflow in simple cases.

## Connects To
- **Ch 1**: Like Singleton, Prototype is a Creational pattern concerned with controlling how instances come into being, but Prototype optimizes *repeated* creation via copying rather than restricting cardinality to one.
- **GoF 1994 catalog**: Prototype is one of the five Creational patterns in the original Gang of Four catalog, positioned as an alternative to factory-style creation when instantiation cost matters more than instantiation flexibility.
