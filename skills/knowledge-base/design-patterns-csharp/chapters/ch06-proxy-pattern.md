# Chapter 6: Proxy Pattern

## Core Idea
Provide a surrogate or placeholder for another object to control access to it. Clients believe they are dealing with the real object, but a proxy sits in front of it and decides how (or whether) the request reaches the real object.

## Frameworks Introduced
- **Proxy**: Provide a surrogate or placeholder for another object to control access to it.
  - When to use: You cannot or should not let clients hold a direct reference to the real object — because it is expensive to create, lives on a remote machine, or requires access control.
  - How: Define a shared abstract type (`Subject`) implemented both by the real object (`ConcreteSubject`) and by a `Proxy` that holds a reference to it, forwards calls, and can add logic (lazy creation, access checks) before forwarding.

## Canonical GoF Reference (1994)
*Source: Gamma, Helm, Johnson & Vlissides, "Design Patterns: Elements of Reusable Object-Oriented Software" (Addison-Wesley, 1994).*

**Intent (verbatim)**: "Provide a surrogate or placeholder for another object to control access to it."

**Also Known As**: Surrogate

**Applicability** — GoF says use this pattern when:
- You need a remote proxy: a local representative for an object in a different address space (e.g. NEXTSTEP's `NXProxy`, Coplien's "Ambassador").
- You need a virtual proxy: creates expensive objects on demand (the Motivation's `ImageProxy` for large raster images).
- You need a protection proxy: controls access to the original object for callers with different access rights (e.g. Choices OS `KernelProxies`).
- You need a smart reference: a bare-pointer replacement that performs extra actions on access — reference counting for auto-free ("smart pointers"), loading a persistent object into memory on first reference, or locking checks before access.

**Participants**:
- **Proxy** (`ImageProxy`) — maintains a reference to the real subject, provides an identical interface, controls creation/deletion/access; its extra responsibilities vary by kind (remote proxies encode/send requests; virtual proxies cache info like extent to postpone loading; protection proxies check permissions).
- **Subject** (`Graphic`) — defines the common interface for RealSubject and Proxy so a Proxy can substitute for a RealSubject anywhere.
- **RealSubject** (`Image`) — the real object the proxy represents.

**Consequences**:
1. A remote proxy can hide that an object resides in a different address space.
2. A virtual proxy can perform optimizations such as creating an object on demand.
3. Protection proxies and smart references allow additional housekeeping (access checks, bookkeeping) on each access.
4. Copy-on-write: a proxy can postpone copying a large object until it's actually modified, using reference counting — reducing the cost of copying heavyweight subjects significantly.

**Implementation notes**: In C++, overloading `operator->` lets a proxy behave like a pointer, but this only works when clients don't need to know exactly which operation was called (it fails for the Motivation's virtual proxy, where loading must happen precisely on `Draw`). Smalltalk's `doesNotUnderstand:` hook enables generic forwarding proxies, but it's slow and complicates object identity (`==`) semantics. A proxy doesn't always need to know its RealSubject's concrete type — unless it must instantiate it (virtual proxy), in which case it does. Proxies referring to a not-yet-instantiated subject need an address-space-independent identifier (GoF used a file name).

**Known Uses (1994-era)**: ET++ text building-block classes (the Motivation's virtual `ImageProxy`); NEXTSTEP's `NXProxy` for distributed/remote objects; Choices operating system `KernelProxies` for protected OS-object access.

**Related Patterns (per GoF)**: Adapter — provides a *different* interface to the object it adapts, whereas Proxy provides the *same* interface as its subject (though a protection proxy's interface may be an effective subset). Decorator — can be implemented similarly to Proxy but has a different purpose: Decorator adds responsibilities, Proxy controls access. Proxies vary in how decorator-like their implementation is: a protection proxy may look exactly like a decorator, while a remote proxy holds only an indirect reference (e.g. host ID) and a virtual proxy starts indirect (a file name) but eventually obtains a direct reference.

## Key Concepts
- **Subject**: The abstract type both the real object and the proxy implement, so clients can't tell them apart.
- **ConcreteSubject**: The real object that does the actual work the client wants.
- **Proxy**: The surrogate that controls access to the ConcreteSubject, forwarding calls to it (possibly after checks or lazy instantiation).
- **Lazy initialization**: The proxy delays creating the ConcreteSubject until `DoSomeWork()` is actually invoked, rather than in its constructor — avoiding unnecessary heavy-object creation.
- **Remote proxy**: Hides an object living in a different address space (different machine/process); realized in .NET via WCF or older remoting/web services mechanisms.
- **Virtual proxy**: Performs optimization such as creating a heavy object (e.g., a large image) only on demand.
- **Protection proxy**: Enforces different access rights for different callers.
- **Smart reference**: Does extra housekeeping on access, such as counting references to an object.

## Mental Models
- Think of a classroom roll call: when a student is absent, a friend mimics his voice so the teacher believes the student answered — the teacher (client) is fooled into thinking it's dealing with the real thing.
- Use a proxy when creating the real object is costly (a "heavy object") — an ATM holds proxy objects for bank data that really lives on a remote server, rather than materializing that data locally in full.
- The book's own maxim for the whole family of Proxy variants: pick the proxy type by the *reason* you need indirection — distance (remote), cost (virtual), or authorization (protection) — not by a single generic "proxy" recipe.

## Anti-patterns
- **Instantiating the ConcreteSubject inside the proxy's constructor**: This defeats the purpose of lazy initialization — every time you construct a proxy, you also construct the (possibly expensive) real object, even if you never call a method on it (Q2).
- **Unguarded lazy initialization in a multithreaded context**: The book's `if (cs == null) { cs = new ConcreteSubject(); }` check is not thread-safe; under concurrent access it can create more than one ConcreteSubject instance. The fix is the same class of remedy discussed for Singleton (Chapter 1) — e.g., a smart proxy that locks before granting access (Q3).
- **Conflating Proxy with Decorator**: A protection proxy can look structurally like a decorator, but the intent differs — decorators add responsibilities, proxies control access. Losing sight of intent leads to using the wrong pattern name and the wrong design conversation (Q7).

## Code Examples
```csharp
using System;
namespace ProxyPattern
{
    /// <summary>
    /// Abstract class Subject
    /// </summary>
    public abstract class Subject
    {
        public abstract void DoSomeWork();
    }

    /// <summary>
    /// ConcreteSubject class
    /// </summary>
    public class ConcreteSubject : Subject
    {
        public override void DoSomeWork()
        {
            Console.WriteLine("ConcreteSubject.DoSomeWork()");
        }
    }

    /// <summary>
    /// Proxy class
    /// </summary>
    public class Proxy : Subject
    {
        Subject cs;
        public override void DoSomeWork()
        {
            Console.WriteLine("Proxy call happening now...");
            //Lazy initialization:We'll not instantiate until the method is
            //called
            if (cs == null)
            {
                cs = new ConcreteSubject();
            }
            cs.DoSomeWork();
        }
    }

    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("***Proxy Pattern Demo***\n");
            Proxy px = new Proxy();
            px.DoSomeWork();
            Console.ReadKey();
        }
    }
}
```
- **What it demonstrates**: A client calling `DoSomeWork()` on a `Proxy` cannot tell it isn't calling `ConcreteSubject` directly; the proxy lazily creates the real object only when work is actually requested.

## Reference Tables
Proxy types, from the Q&A session (the book does not print this as a table, but the four are consistently distinguished by purpose):

| Proxy Type | Purpose |
|---|---|
| Remote proxy | Hides an object in a different address space (e.g., another machine); realized via WCF or .NET remoting/web services |
| Virtual proxy | Defers creation of a heavy/expensive object until needed (e.g., a large image) |
| Protection proxy | Enforces access rights per caller |
| Smart reference | Adds bookkeeping on access, e.g., counting references |

## Worked Example
The base demo prints `Proxy call happening now...` then `ConcreteSubject.DoSomeWork()` — a single unconditional forward.

The book then builds a protection-proxy variant to answer "when would you use a protection proxy?" It hardcodes three `registeredUsers` (`"Admin"`, `"Rohit"`, `"Sam"`) and a `currentUser` passed into the `Proxy` constructor. Critically, the constructor no longer creates `ConcreteSubject` at all (not even lazily) — because if the user turns out to be unauthorized, there'd be no point ever creating it. `DoSomeWork()` checks `registeredUsers.Contains(currentUser)`: if authorized, it lazily creates `ConcreteSubject` and forwards the call; if not, it prints `"Sorry {0}, you do not have access."` and never touches `ConcreteSubject`. Running it with `"Admin"` prints the proxy message, the authorization message, and `ConcreteSubject.DoSomeWork()`; running it with `"Robin"` prints the proxy message, the authorization message, and the rejection — with no `ConcreteSubject` ever instantiated. This demonstrates why avoiding eager/eager-lazy instantiation in the constructor matters once you add real access control.

## Key Takeaways
1. Proxy and its real subject share one abstract type so the client's code never has to know which one it's calling.
2. Lazy initialization inside the proxy method (not the constructor) avoids creating expensive real objects that may never be used — but only if you also avoid creating them when access will be denied anyway.
3. Pick the proxy variant (remote, virtual, protection, smart reference) based on *why* you need indirection, not as an undifferentiated "proxy pattern."
4. Naive lazy-init null checks are not thread-safe; treat this the same way you'd treat Singleton's classic double-checked-locking problem.
5. This example predates modern C# (2018-era, targeting C# 6/7): it uses classic null checks and no thread-safety primitives, records, or pattern matching — the Proxy intent still applies, but idiomatic modern C# would express the guarded lazy-init differently (see modern-csharp-notes.md).

## Connects To
- **Ch 7 (Decorator)**: Both Proxy and Decorator wrap an object behind the same interface, which is why they're easy to confuse. The distinguishing question is intent: Proxy controls *access* to an unchanged interface; Decorator adds *responsibilities* to an unchanged interface. Adapter (Ch 8), by contrast, changes the interface itself to make two incompatible types cooperate. Same shape (wrap + delegate), three different jobs: control access (Proxy), add behavior (Decorator), convert interface (Adapter).
- **Ch 1 (Singleton)**: The thread-safety concerns around lazy instantiation in Proxy mirror the same concerns explored for lazy Singleton creation — the same remedies (locking, smart proxies) apply.
- **GoF 1994 catalog**: Proxy is one of the seven original Structural patterns.
- **GoF 1994 canonical entry**: GoF's own "Composite versus Decorator versus Proxy" discussion sharpens the distinction beyond intent alone — Proxy's proxy-subject relationship is inherently static and expressible at compile time (one fixed relationship), while Decorator is deliberately open-ended and recursive because a component's total functionality can't be known in advance; that structural difference, not just "access vs. responsibility," is why the two patterns aren't interchangeable even when their code looks alike.
