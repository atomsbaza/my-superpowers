# Chapter 29: Sealing the Leaks in Your Applications

## Core Idea
Even a well-designed application built with correct patterns can degrade or crash from memory leaks; understanding .NET's generational garbage collector, `IDisposable`, and finalizers — and applying Microsoft's dispose pattern — is what prevents allocated resources from silently accumulating.

## Frameworks Introduced
- **Microsoft's basic Dispose pattern**: Implement `IDisposable.Dispose()` to call a protected `Dispose(bool disposing)` and then `GC.SuppressFinalize(this)`; also provide a destructor that calls `Dispose(false)` as a safety net.
  - When to use: Any class holding unmanaged resources, event subscriptions, file/connection handles, or anything else that needs deterministic cleanup beyond what the GC does automatically.
  - How: `Dispose()` calls `Dispose(true)` then `GC.SuppressFinalize(this)`; `Dispose(bool disposing)` checks the flag — only touch other managed objects when `disposing == true`, since during finalization those objects may already be finalized in unpredictable order; the destructor (`~ClassName(){ Dispose(false); }`) exists purely as a backstop for when `Dispose()` is skipped (e.g., due to an exception).
- **Generational garbage collection**: Objects are grouped into generation 0 (short-lived), 1, and 2 (long-lived); the GC collects lower generations far more frequently than higher ones, promoting survivors upward each pass.
  - When to use: Understanding this model is a prerequisite for reasoning about `GC.Collect(Int32)`, `GC.GetGeneration()`, and when forcing a collection is (rarely) worthwhile.
  - How: The GC runs three phases — marking (identify live objects by tracing the object graph from roots), relocating (update references for objects that will be compacted), and compacting (move live objects together to reclaim contiguous free space and avoid fragmentation).

## Key Concepts
- **Memory leak**: Continuously allocating resources without deallocating them; the impact (slowdown, crash, `OutOfMemoryException`) appears only once the leak accumulates enough — the chapter's worked math shows even 512 bytes/click becomes 4.76 GB at 10 million clicks.
- **Dirty/unreferenced objects**: Objects with no remaining references, which the low-priority background GC thread identifies and reclaims.
- **Finalization queue / freachable queue**: Objects with a destructor (`Finalize()`) go into a finalization queue after the marking phase; the GC then moves them to the "freachable" queue, where a separate thread executes their finalizers before the object's memory can finally be reclaimed on a later GC pass.
- **Managed heap**: The memory segment the CLR allocates to store and manage objects — distinct from an old-style unmanaged heap because compaction means new allocations just use a heap pointer instead of scanning a free list.
- **False leak**: Apparent memory growth (e.g., in a singleton or static class) that is not actually a leak because it will not continue growing indefinitely.
- **Finalizable type**: Any type that overrides `Object.Finalize()` (i.e., defines a C# destructor `~ClassName()`), which the GC invokes prior to reclaiming memory.
- **`using` statement**: Syntactic sugar for a `try`/`finally` block that guarantees `Dispose()` runs even if an exception occurs mid-block — visible in compiled IL as an explicit try/finally.

## Mental Models
- Think of GC generations as triage by expected lifetime: generation 0 is checked constantly (cheap, frequent), generation 2 is checked rarely (expensive, because it also re-checks 0 and 1) — this is why `GC.Collect(2)` is costly and generally discouraged except in specific diagnostic scenarios.
- Use the dual-implementation mental model for cleanup: `Dispose()` gives you a known, deterministic moment to release resources; the destructor is an unreliable but guaranteed-eventually backstop for when `Dispose()` is skipped — pattern experts recommend implementing both, not choosing one.
- Treat leak-rate math as the way to judge urgency: a tiny per-operation leak (bytes) is invisible at low volume but catastrophic at scale (thousands to millions of operations) — always reason about leaks multiplied by expected traffic, not in isolation.
- Use the Visual Studio Diagnostic Tools' snapshot-diffing workflow as the standard leak-hunting loop: take a snapshot, run the suspect operation repeatedly, take another snapshot, and look at the "Objects (Diff)" / "Heap Size (Diff)" columns for classes that keep growing.

## Anti-patterns
- **Registering an event and never unregistering it**: The chapter's core demonstration — `SimpleEvent += new MyDelegate(PrintText);` with no matching `-=` — keeps `SimpleEventClass` instances rooted by the delegate's invocation list, so they're never eligible for garbage collection even after they go out of scope in the caller.
- **Relying solely on the finalizer for cleanup**: You never know exactly when `Finalize()` will run, and while an object is queued for finalization, both it and everything it references are held alive for an extra GC cycle — unacceptable when resources must be freed promptly.
- **Skipping `GC.SuppressFinalize(this)` after a successful `Dispose()`**: Without it, the CLR still queues the object for finalization even though cleanup already happened, wasting a GC cycle and delaying final reclamation.
- **Treating `-1`, `999`, or a sentinel date as null** (cross-referenced from Chapter 28) is not repeated here, but the chapter's implicit anti-pattern is symmetric: treating "the GC will handle it" as sufficient for resources the GC does not manage (unmanaged handles, event subscriptions, open files).

## Code Examples
```csharp
// Demonstration 1: forcing GC across generations
using System;
namespace GarbageCollectionEx1
{
    class MyClass
    {
        private int myInt;
        private double myDouble;
        public MyClass()
        {
            myInt = 25;
            myDouble = 100.5;
        }
        public void Dispose()
        {
            GC.SuppressFinalize(this);
            Console.WriteLine("Dispose() is called");
        }
        ~MyClass()
        {
            Console.WriteLine("Destructor is Called..");
        }
    }
    class Program
    {
        public static void Main(string[] args)
        {
            MyClass myOb = new MyClass();
            Console.WriteLine("myOb is in Generation : {0}", GC.GetGeneration(myOb));
            GC.Collect(0);  //will call generation 0
            Console.WriteLine("myOb is in Generation : {0}", GC.GetGeneration(myOb));
            GC.Collect(1);  //will call generation 1 with 0
            GC.Collect(2);  //will call generation 2 with 1 and 0
        }
    }
}
```
- **What it demonstrates**: `myOb` starts in generation 0; each successive `GC.Collect(N)` promotes surviving objects up a generation and also re-triggers collection of every lower generation, which is why `GC.Collect(2)` is the most expensive call.

```csharp
// Microsoft's basic Dispose pattern, applied to fix an event leak
class SimpleEventClass : IDisposable
{
    public int Id { get; set; }
    public event MyDelegate SimpleEvent;
    public bool disposed = false;
    public SimpleEventClass()
    {
        SimpleEvent += new MyDelegate(PrintText);
    }
    public string PrintText(string text) { return text; }
    public void Dispose()
    {
        Dispose(true);
        GC.SuppressFinalize(this);
    }
    protected virtual void Dispose(bool disposing)
    {
        if (disposing)
        {
            if (this.SimpleEvent != null)
            {
                this.SimpleEvent -= new MyDelegate(PrintText);
            }
            disposed = true;
        }
    }
    ~SimpleEventClass()
    {
        Dispose(false);
    }
}
```
- **What it demonstrates**: Unsubscribing the event handler inside `Dispose(true)` removes the reference chain that was keeping `SimpleEventClass` instances rooted; calling `col[currentObjectNo].Dispose()` immediately after use (or wrapping the object in a `using` block) eliminates the incremental heap growth seen in the Diagnostic Tools' snapshots.

## Reference Tables
| Approach | When it runs | Guarantee | Cost |
|---|---|---|---|
| Destructor only | GC-determined, eventually | Will run eventually, but timing is unpredictable and holds the object an extra GC cycle | Delays reclamation, unpredictable timing |
| `IDisposable.Dispose()` only | Deterministic — whenever caller invokes it | Not guaranteed if caller skips it or an exception intervenes | Cheap, precise, but fragile without discipline |
| Dual implementation (`Dispose()` + destructor calling `Dispose(false)`) | Deterministic when called; guaranteed fallback otherwise | Guaranteed in all scenarios per the chapter | Recommended default despite the extra boilerplate |
| `using` statement | Compiler-generated try/finally around `Dispose()` | Guarantees `Dispose()` runs even on exception | Best practice — least code, strongest guarantee |

## Worked Example
The chapter's central case study: an online form leaks 512 bytes per Submit click because the developers never implemented a dispose pattern. At low volume this is invisible; at 100,000 clicks it's 48.8 MB lost, and at 10 million clicks it's 4.76 GB — illustrating that leak severity is a function of rate times volume, not the per-operation size alone. The concrete demonstration mirrors this: a loop creates 500,000 `SimpleEventClass` objects, each subscribing its own `PrintText` method to `SimpleEvent` but never unsubscribing. Visual Studio's Diagnostic Tools, snapshotted seven times during the run, show `SimpleEventClass` and its delegate `MyDelegate` growing without bound in the heap view — the "Objects (Diff)" column keeps climbing. Applying Microsoft's Dispose pattern (unsubscribing the event in `Dispose(true)`, then calling `col[currentObjectNo].Dispose(); col[currentObjectNo] = null;` after each use) eliminates the growth in a re-run: the follow-up snapshots show no incremental heap growth, and the same fix, wrapped in a `using` block, compiles down to a visible try/finally in IL — proof the compiler is doing exactly what manual `try`/`finally` cleanup would do by hand.

## Key Takeaways
1. The GC automatically reclaims managed memory, but it cannot help with unmanaged resources, open handles, or forgotten event subscriptions — those require explicit `Dispose()` discipline.
2. Implement the dual pattern (`Dispose()` + a destructor that calls `Dispose(false)`) rather than relying on either alone: `Dispose()` gives you deterministic timing, the destructor guarantees eventual cleanup if `Dispose()` is skipped.
3. Always call `GC.SuppressFinalize(this)` at the end of a successful `Dispose()` to avoid wasting a GC cycle on an object that's already been cleaned up.
4. Prefer the `using` statement over manual `Dispose()` calls wherever possible — it compiles to a guaranteed try/finally and eliminates the most common cause of skipped cleanup (an exception between allocation and disposal).
5. Use tools (Visual Studio Diagnostic Tools, Windbg, CLR Profiler, ANTS Memory Profiler) and repeated-snapshot diffing to actually locate leaks rather than guessing — the growing-class-in-heap-view signal is concrete and specific.
6. Even a small per-operation leak becomes catastrophic at scale; always reason about leak rate multiplied by realistic operation volume, not the per-operation footprint in isolation.
7. This chapter's code targets .NET Framework and Visual Studio 2017-era tooling (C# 6/7, 2018); the GC generational model, `IDisposable`, and the dispose-pattern guidance remain directly applicable to modern C#/.NET, though today's guidance also emphasizes `SafeHandle`, `IAsyncDisposable`, and `using` declarations (`using var x = ...;`) not covered here.

## Connects To
- **Ch 28 (Anti-patterns)**: A memory leak from a skipped Dispose pattern is itself a concrete, mechanical instance of the "attractive shortcut now, costly later" shape the anti-patterns chapter describes in the abstract.
- **Ch 21 (Observer)**: The event-subscription leak demonstrated here is the same underlying mechanism as the Observer pattern's subject-observer relationship — failing to unsubscribe an observer is precisely what roots the leaked object.
- **.NET resource-management guidance**: Directly mirrors Microsoft's official dispose-pattern documentation (`docs.microsoft.com/.../dispose-pattern`), making this chapter a practical companion to that reference material.
