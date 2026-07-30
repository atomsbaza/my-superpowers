# Chapter 25: Null Object Pattern

## Core Idea
There is no universally accepted formal definition; the book adopts Wikipedia's: a null object is an object with no referenced value or with defined neutral ("null") behavior, used to avoid scattering "is this null?" checks throughout code by providing a safe do-nothing substitute instead.

## Frameworks Introduced
- **Null Object**: Provide an object with neutral ("do-nothing") behavior to substitute for a missing real object, avoiding explicit null checks throughout the codebase.
  - When to use: A client repeatedly needs to guard against a reference being null before invoking a method on it, and those guards are multiplying across the codebase.
  - How: Implement a class (e.g., `NullVehicle`) that satisfies the same interface as real objects but whose methods are no-ops; substitute an instance of it wherever a real object would otherwise be missing, so calling code never needs a null check.

## Key Concepts
- **Faulty program (baseline)**: The chapter opens with a program where an invalid user choice leaves `vehicle` as `null`, and calling `vehicle.Travel()` throws `System.NullReferenceException` at runtime.
- **Immediate remedy (null check)**: Wrapping the call in `if (vehicle != null) { vehicle.Travel(); }` fixes the crash but doesn't scale — an enterprise application accumulating this check at every call site becomes "dirty" and hard to maintain.
- **NullVehicle**: A concrete `IVehicle` implementation whose `Travel()` method does nothing, standing in for a missing/invalid choice instead of leaving the reference `null`.
- **Singleton-backed Null Object**: `NullVehicle` is implemented as a Singleton (`private static readonly` instance behind a `public static Instance` property) so repeated invalid inputs don't create a new, wasted `NullVehicle` object each time.
- **Do-nothing behavior**: The defining trait of a Null Object — it conforms to the expected interface but performs no observable action, letting calling code proceed unconditionally.
- **Object count tracking**: The example tracks `busCount`, `trainCount`, and `nullVehicleCount` to make visible (in the output) that invalid inputs do not inflate the count of "real" objects created.

## Mental Models
- Think of a washing machine that, if the door is left open or the water supply fails, doesn't damage itself — it simply beeps or alarms instead of proceeding, i.e., it exhibits defined neutral behavior rather than crashing or behaving unpredictably.
- Use Null Object when the alternative is "n number of if conditions" scattered through client code just to guard against a possibly-missing reference — the pattern moves that guard into the type system instead of scattering conditionals.
- Model the trade explicitly: a raw `null` communicates "no value, and you must check before use"; a Null Object communicates "here is a value, and it is safe to use, but it does nothing" — the calling code's shape stays identical either way.
- Treat the Singleton wrapping as a memory-safety concern specific to Null Object: because invalid input can recur arbitrarily often, a fresh `NullVehicle` per invalid input would accumulate useless objects and degrade performance over time — reuse one shared instance instead.

## Anti-patterns
- **Scattering `if (x != null)` checks throughout client code**: works but doesn't scale — the chapter is explicit that in an enterprise application with many such scenarios, this makes code "dirty" and harder to maintain.
- **Creating a new Null Object instance per invalid case**: without the Singleton guard, a high volume of invalid inputs over time creates a large number of useless `NullVehicle` objects, consuming memory and potentially slowing the system down.
- **Using Null Object to mask root-cause failures you actually need to diagnose**: the Q&A cautions that sometimes you want the `NullReferenceException` to surface (and be handled via try/catch/finally with logging) so the root cause of a real bug isn't silently hidden behind neutral behavior.

## Code Examples
```csharp
interface IVehicle
{
    void Travel();
}
class Bus : IVehicle
{
    public static int busCount = 0;
    public Bus() { busCount++; }
    public void Travel() { Console.WriteLine("Let us travel with Bus"); }
}
class Train : IVehicle
{
    public static int trainCount = 0;
    public Train() { trainCount++; }
    public void Travel() { Console.WriteLine("Let us travel with Train"); }
}
```
- **What it demonstrates**: `Bus` and `Train` are the "real" `IVehicle` implementations, each tracking its own instantiation count — this is the baseline the faulty program crashes against when neither is chosen.

```csharp
class NullVehicle : IVehicle
{
    private static readonly NullVehicle instance = new NullVehicle();
    public static int nullVehicleCount = 0;
    public static NullVehicle Instance
    {
        get
        {
            return instance;
        }
    }
    public void Travel()
    {
        //Do Nothing
    }
}
```
- **What it demonstrates**: `NullVehicle` implements `IVehicle` just like `Bus` and `Train`, but its `Travel()` is a deliberate no-op; it is exposed as a Singleton (`Instance`) so repeated invalid inputs reuse the same object instead of allocating a new one each time.

## Reference Tables
| Scenario | Faulty Program | With Null Check | With Null Object |
|---|---|---|---|
| Invalid input behavior | `NullReferenceException` at `vehicle.Travel()` | Guarded by `if (vehicle != null)`, no crash | `vehicle = NullVehicle.Instance`, `Travel()` safely does nothing |
| Code cleanliness at scale | N/A (crashes) | Degrades as null checks multiply across the app | Stays clean — no checks needed at any call site |
| Memory behavior on repeated invalid input | N/A | N/A | Reuses one Singleton instance instead of allocating repeatedly |

## Worked Example
The baseline faulty program lets a user repeatedly choose `'a'` (Bus) or `'b'` (Train); any other input leaves `vehicle` as `null`, and the very next `vehicle.Travel()` throws `NullReferenceException` (shown in Figure 25-1). The "immediate remedy" of wrapping the call in a null check avoids the crash but is flagged as not scaling to many such checks across a real application. The pattern's fix redefines the loop: valid inputs (`'a'`/`'b'`) still create `Bus`/`Train` instances as before, but any other input (or `'exit'`) sets `vehicle = NullVehicle.Instance` instead of leaving it `null`. The loop then calls `vehicle.Travel()` unconditionally, with no null check anywhere — for invalid inputs, `Travel()` silently does nothing, and the running total (`Bus.busCount + Train.trainCount + NullVehicle.nullVehicleCount`) stays flat across invalid inputs (demonstrated with inputs `c`, `d`, `e` all leaving the count at 2), proving the Singleton-backed `NullVehicle` isn't being newly allocated each time.

## Key Takeaways
1. Null Object replaces scattered `if (x != null)` guards with a neutral, do-nothing implementation of the same interface, so calling code can invoke methods unconditionally.
2. Implementing the Null Object as a Singleton avoids the side effect of allocating a fresh useless instance for every invalid case, which matters when invalid input volume grows over time.
3. The pattern trades "explicit failure" for "silent no-op" — appropriate for expected/benign gaps (an invalid menu choice), but the Q&A warns it is not appropriate everywhere, since sometimes you specifically want the exception to surface so you can diagnose the root cause.
4. A Null Object must conform to the same interface as the real objects it substitutes for (`IVehicle` here), which is what lets client code stay branch-free.
5. This code targets pre-modern C# (2018, .NET Framework era) — the substitute-a-safe-default intent still applies today, but idiomatic modern C# might reach for nullable reference types plus pattern matching, or `Option`/`Maybe`-style wrapper types, alongside or instead of a hand-rolled Null Object class.

## Connects To
- **Ch 1 (Singleton)**: `NullVehicle` is explicitly built using the Singleton mechanism (`private static readonly` instance behind a static `Instance` accessor) specifically to avoid creating repeated useless objects for repeated invalid input — a direct reuse of Chapter 1's pattern in service of a different intent.
- **State pattern (not covered in these chapters)**: A Null Object that "does nothing" is conceptually adjacent to a State pattern's inactive/disabled state — both let an object safely respond to a condition (missing value, or current state) without conditional branching at every call site, though State manages transitions between behaviors while Null Object simply substitutes a permanent no-op.
