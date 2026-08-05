# Chapter 8: Encapsulating Algorithms — Template Method

## Core Idea

Template Method defines an algorithm’s skeleton in a method and defers selected steps to subclasses. The superclass controls the invariant sequence; abstract operations supply required variation and hooks provide optional extension points.

## Frameworks Introduced

- **Template Method Pattern**: “Defines the skeleton of an algorithm in a method, deferring some steps to subclasses. Template Method lets subclasses redefine certain steps without changing the algorithm’s structure.”
  - When to use: several implementations share an algorithmic sequence but vary in a few steps.
  - How: put the template method in an abstract superclass, keep invariant operations there, make required steps abstract, and make optional steps hooks.
- **Hook**:
  - When to use: a subclass may optionally affect the algorithm.
  - How: supply a default implementation, often empty or returning a safe default, and call it from the template method.
- **Hollywood Principle**: “Don’t call us, we’ll call you.”
  - When to use: building a framework that lets lower-level components plug in without creating dependency rot.

## Key Concepts

- **Template method**: the method that fixes the algorithm order.
- **Primitive operation**: a step implemented by subclasses.
- **Concrete operation**: shared implementation in the superclass.
- **Hook**: optional method with a default behavior.
- **Algorithm skeleton**: stable sequence with controlled variation points.
- **Dependency rot**: tangled high-level/low-level dependencies that make system structure hard to understand.
- **Hollywood Principle**: high-level code controls when extension points are invoked.
- **Framework**: reusable control flow with application-specific steps supplied by clients or subclasses.

## Mental Models

- Use Template Method when the algorithm is mostly fixed and the variation belongs at named steps.
- Make a method abstract when every subclass must supply it; make it a hook when omission is valid.
- Keep the template method protected from accidental override when its sequence is an invariant.
- Fewer, coarser primitive operations reduce subclass burden but also reduce flexibility.

## Anti-patterns

- **Duplicated prepareRecipe() algorithms**: changes to the sequence must be repeated and can drift.
- **Too many granular abstract steps**: every new subclass becomes a large implementation task.
- **Hook used for mandatory behavior**: a silent default can create incomplete algorithms.
- **Confusing Strategy with Template Method**: Strategy supplies a whole algorithm by composition; Template Method shares a skeleton and defers pieces.

## Code Examples

~~~java
public abstract class CaffeineBeverage {
    public final void prepareRecipe() {
        boilWater();
        brew();
        pourInCup();
        if (customerWantsCondiments()) {
            addCondiments();
        }
    }

    protected abstract void brew();
    protected abstract void addCondiments();
    protected void boilWater() { System.out.println("Boiling water"); }
    protected void pourInCup() { System.out.println("Pouring into cup"); }
    protected boolean customerWantsCondiments() { return true; }
}
~~~

- **What it demonstrates**: invariant steps stay in one place; brew, condiments, and optional choice are extension points.

## Reference Tables

| Extension point | Default? | Subclass obligation |
|---|---|---|
| Abstract primitive operation | No | Must implement |
| Concrete operation | Yes, shared | Usually should not override |
| Hook | Yes, optional | May override |

| Template Method | Strategy |
|---|---|
| Inheritance and a shared algorithm skeleton | Composition and a complete interchangeable algorithm |
| Superclass controls the sequence | Client/context chooses the strategy |
| Efficient reuse of common steps | Greater runtime flexibility |

## Worked Example

Coffee and tea both boil water, extract the beverage, pour it into a cup, and add condiments. CaffeineBeverage owns prepareRecipe(). Coffee implements brew() as dripping grounds and addCondiments() as sugar and milk; Tea steeps a tea bag and adds lemon. A hook such as customerWantsCondiments() lets a subclass ask the user and skip the optional step. The sequence cannot drift between beverages.

## Key Takeaways

1. Centralize an algorithm’s invariant order.
2. Name variation points explicitly as abstract operations or hooks.
3. Use hooks for optional decisions and reactions.
4. Let high-level framework code call extension code.
5. Recognize non-textbook variants, such as Arrays.sort() using Comparable to fill one algorithm step.

## Connects To

- **Chapter 4 — Factory**: Factory Method is described as a specialization of Template Method.
- **Chapter 1 — Strategy**: both encapsulate algorithms, but use different control and composition mechanisms.
- **Java APIs**: InputStream, JFrame, AbstractList, and Arrays show template-like designs.

