# Chapter 9: Facade Pattern

## Core Idea
Provide a unified interface to a set of interfaces in a subsystem. Facade defines a higher-level interface that makes a complex subsystem easier to use, supporting loose coupling between clients and the subsystems they depend on.

## Frameworks Introduced
- **Facade**: Provide a unified interface to a set of interfaces in a subsystem, making the subsystem easier to use.
  - When to use: A system has multiple subsystems that clients would otherwise need to coordinate directly, creating tight coupling and complex client code.
  - How: Build a facade class (`RobotFacade`) that holds references to each subsystem (`RobotColor`, `RobotHands`, `RobotBody`) and exposes simple, high-level operations (`ConstructMilanoRobot`, `DestroyMilanoRobot`) that internally call the subsystems in the correct sequence.

## Canonical GoF Reference (1994)
*Source: Gamma, Helm, Johnson & Vlissides, "Design Patterns: Elements of Reusable Object-Oriented Software" (Addison-Wesley, 1994).*

**Intent (verbatim)**: "Provide a unified interface to a set of interfaces in a subsystem. Facade defines a higher-level interface that makes the subsystem easier to use."

**Applicability** — GoF says use this pattern when:
- You want to provide a simple interface to a complex subsystem, since subsystems tend to grow more complex (more, smaller classes) as they evolve and patterns are applied.
- There are many dependencies between clients and the implementation classes of an abstraction — a facade decouples the subsystem from clients and other subsystems.
- You want to layer your subsystems, using a facade as the entry point to each layer so dependent subsystems communicate only through their facades.

**Participants**:
- **Facade** (`Compiler`) — knows which subsystem classes handle a request and delegates client requests to them.
- **Subsystem classes** (`Scanner`, `Parser`, `ProgramNode`, etc.) — implement subsystem functionality, handle work assigned by the Facade, and have no knowledge of the facade (they keep no reference to it).

**Consequences**:
1. Shields clients from subsystem components, reducing the number of objects clients must deal with and easing the subsystem's use.
2. Promotes weak coupling between subsystem and clients — lets subsystem components vary without affecting clients, can eliminate complex/circular dependencies, and reduces compilation dependencies (important in large systems, and it eases porting since building one subsystem is less likely to force building all others).
3. Doesn't prevent applications from using subsystem classes directly if needed — clients choose between ease-of-use (via the facade) and generality (via direct access).

**Implementation notes**: Client-subsystem coupling can be reduced further by making Facade abstract with concrete subclasses per subsystem implementation, or by configuring a Facade instance with swappable subsystem objects instead of subclassing. GoF also draws a public/private-interface analogy for subsystems: the Facade is part of the public interface, but usually isn't the only public class (e.g. `Parser` and `Scanner` are public too) — few OO languages of the era (barring C++'s then-new namespaces) could enforce a private subsystem interface.

**Known Uses (1994-era)**: A compiler subsystem facade (`Compiler`) inspired by the ObjectWorks\Smalltalk compiler system; ET++'s `ProgrammingEnvironment` facade for built-in object-browsing tools (with a null-object subclass, `ETProgrammingEnvironment`, providing the real browsing behavior); the Choices operating system's `FileSystemInterface` and `Domain` facades over its storage and address-space frameworks.

**Related Patterns (per GoF)**: Abstract Factory — can pair with Facade to create subsystem objects in a subsystem-independent way, or serve as an alternative to Facade for hiding platform-specific classes. Mediator — similarly abstracts functionality of existing classes, but Mediator centralizes arbitrary communication *between* colleague objects that are aware of and talk to the mediator, whereas Facade merely simplifies the interface *to* subsystem objects that remain unaware of it and gain no new functionality. GoF notes Facade objects are usually Singletons, since only one is typically required.

## Key Concepts
- **Subsystem**: An independent piece of a larger system (`RobotColor`, `RobotHands`, `RobotBody`), each with its own focused responsibility and API.
- **Facade**: The single class (`RobotFacade`) that clients talk to; it composes and coordinates the subsystems on the client's behalf.
- **Loose coupling**: Clients depend only on the facade's simple methods, not on the number, order, or internal APIs of the subsystems.
- **Composition in the facade**: `RobotFacade` holds instances of each subsystem class and calls their methods internally — the facade doesn't replace the subsystems, it orchestrates them.
- **Non-restrictive facade**: The pattern does not prevent clients from bypassing the facade and calling subsystems directly; it simply doesn't encourage it.
- **Multiple facades**: A single subsystem can have more than one facade if different clients need different simplified views.

## Mental Models
- Think of hiring a party organizer for a 300-guest birthday party: you give them the party type, date, and guest count, and they handle decorating, catering style, and all the coordination — you never need to know how those subsystems (caterer, decorator) actually work together.
- Use Facade when calling a library method: you don't care how the method is implemented internally, only that a simple call gets the job done.
- Facade is about *simplifying* an interface to a subsystem, whereas Adapter (Ch 8) is about *converting* one interface into another that clients already expect — different problems that are easy to conflate (Q4).

## Anti-patterns
- **Bypassing the facade to call subsystems directly, routinely**: The pattern doesn't forbid this, but doing it regularly makes the code "look dirty" and forfeits the coupling benefits the facade exists to provide (Q3, Q8).
- **Letting the facade drift out of sync with subsystem changes**: When a subsystem's internal structure changes, the facade layer must be updated to match — the facade adds a layer of coding that has to be maintained alongside the subsystems, not once and forgotten (Q7).
- **Introducing a facade layer without stakeholder buy-in**: Developers already fluent in the subsystems/APIs may see the extra facade layer as unnecessary overhead they now have to learn — a real cost worth weighing before adding a facade (Q7).

## Code Examples
```csharp
// RobotFacade.cs
using System;
using FacadePattern.RobotParts;
namespace FacadePattern
{
    public class RobotFacade
    {
        RobotColor rc;
        RobotHands rh;
        RobotBody rb;

        public RobotFacade()
        {
            rc = new RobotColor();
            rh = new RobotHands();
            rb = new RobotBody();
        }

        public void ConstructMilanoRobot()
        {
            Console.WriteLine("Creation of a Milano Robot Start");
            rc.SetDefaultColor();
            rh.SetMilanoHands();
            rb.CreateHands();
            rb.CreateRemainingParts();
            Console.WriteLine("Milano Robot Creation End");
            Console.WriteLine();
        }

        public void ConstructRobonautRobot()
        {
            Console.WriteLine("Initiating the creational process of a Robonaut Robot");
            rc.SetGreenColor();
            rh.SetRobonautHands();
            rb.CreateHands();
            rb.CreateRemainingParts();
            Console.WriteLine("A Robonaut Robot is created");
            Console.WriteLine();
        }

        public void DestroyMilanoRobot()
        {
            Console.WriteLine("Milano Robot's destruction process is started");
            rh.ResetMilanoHands();
            rb.DestroyHands();
            rb.DestroyRemainingParts();
            Console.WriteLine("Milano Robot's destruction process is over");
            Console.WriteLine();
        }

        public void DestroyRobonautRobot()
        {
            Console.WriteLine("Initiating a Robonaut Robot's destruction process.");
            rh.ResetRobonautHands();
            rb.DestroyHands();
            rb.DestroyRemainingParts();
            Console.WriteLine("A Robonaut Robot is destroyed");
            Console.WriteLine();
        }
    }
}

// RobotBody.cs (one representative subsystem; RobotColor and RobotHands
// follow the same shape with SetDefaultColor/SetGreenColor and
// SetMilanoHands/SetRobonautHands/ResetMilanoHands/ResetRobonautHands)
using System;
namespace FacadePattern.RobotParts
{
    public class RobotBody
    {
        public void CreateHands()
        {
            Console.WriteLine("Hands manufactured");
        }
        public void CreateRemainingParts()
        {
            Console.WriteLine("Remaining parts (other than hands) are created");
        }
        public void DestroyHands()
        {
            Console.WriteLine("The robot's hands are destroyed");
        }
        public void DestroyRemainingParts()
        {
            Console.WriteLine("The robot's remaining parts are destroyed");
        }
    }
}
```
- **What it demonstrates**: `RobotFacade` composes three subsystem instances and exposes four simple, high-level methods; clients calling `ConstructMilanoRobot()` never need to know the correct call order across `RobotColor`, `RobotHands`, and `RobotBody`.

## Reference Tables
Facade vs. Adapter, from Q4 (the book states this distinction directly, not as a printed table):

| Aspect | Adapter | Facade |
|---|---|---|
| Goal | Convert an interface into one the client already expects | Simplify a complex subsystem's interface |
| Client's perception | Sees no difference between interfaces | Sees one simple interface instead of many complex ones |
| Number of things behind it | Typically one adaptee | Typically several subsystems |
| Restricts direct access? | N/A | No — clients can still call subsystems directly if they choose |

## Worked Example
`Program.cs` creates two `RobotFacade` instances (`rf1`, `rf2`) and calls `rf1.ConstructMilanoRobot()`, then `rf2.ConstructRobonautRobot()`, then `rf1.DestroyMilanoRobot()`, then `rf2.DestroyRobonautRobot()`. Each facade call internally sequences three subsystem calls in the correct order (e.g., set color, then set hands, then create hands, then create remaining parts) and the client never expresses that sequence itself. The output traces each step: `"Creation of a Milano Robot Start"` → `"This is steel color robot."` → `"The robot will have EH1 Milano hands"` → `"Hands manufactured"` → `"Remaining parts (other than hands) are created"` → `"Milano Robot Creation End"`, and analogously for the green Robonaut robot and for both destruction sequences. The point demonstrated: two different robot "recipes" (Milano vs. Robonaut) are expressed as two simple facade method calls, each hiding a distinct multi-step subsystem coordination.

## Key Takeaways
1. A facade exists to hide subsystem coordination complexity behind a small set of high-level operations, reducing the number of things a client must directly manage.
2. Facade does not forbid direct subsystem access — it just makes bypassing it a deliberate trade-off, not a limitation of the pattern.
3. A subsystem can have more than one facade if different client groups need different simplified views over it.
4. Facade adds a maintenance obligation: subsystem changes must be reflected in the facade layer, or the two drift out of sync.
5. Facade and Adapter are often confused because both "sit in front of" something, but Facade simplifies while Adapter converts.
6. This example predates modern C# (2018-era, targeting C# 6/7): it uses classic field-based composition and no records, primary constructors, or pattern matching — the Facade intent still applies, but idiomatic modern C# would express some of this more tersely (see modern-csharp-notes.md).

## Connects To
- **Ch 8 (Adapter)**: The book draws this line explicitly (Q4) — Adapter alters an interface so a client sees no difference between two interfaces; Facade simplifies a complex subsystem's interface rather than converting one type into another.
- **Ch 6 (Proxy) / Ch 7 (Decorator)**: Unlike Proxy (controls access) and Decorator (adds responsibility), Facade's purpose is purely to reduce the surface area a client must interact with — it doesn't restrict access or add new behavior to individual objects, it aggregates and simplifies calls across several of them.
- **GoF 1994 catalog**: Facade is one of the seven original Structural patterns.
- **GoF 1994 canonical entry**: GoF's own "Discussion of Structural Patterns" section directly warns against conflating Facade with Adapter at the conceptual level: a facade might look like "an adapter to a set of other objects," but that overlooks that a facade *defines a new interface*, while an adapter *reuses an old one* to make two existing interfaces work together — Facade never has to match a pre-existing interface the way Adapter does.
