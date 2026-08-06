# Chapter 1: Welcome to Design Patterns — Strategy

## Core Idea

The Strategy Pattern separates a family of interchangeable algorithms from the object that uses them. The context owns a behavior interface and delegates to a selected strategy, so behavior can vary independently of the context and can be changed at runtime.

## Frameworks Introduced

- **Strategy Pattern**: “Defines a family of algorithms, encapsulates each one, and makes them interchangeable. Strategy lets the algorithm vary independently from clients that use it.”
  - When to use: when several variants of an algorithm or behavior exist, especially when clients need different variants or runtime switching.
  - How: define a strategy interface, implement each algorithm in a concrete strategy, compose the strategy into the context, and delegate through the interface.
- **Program to an interface, not an implementation**:
  - When to use: whenever the client should not know which concrete strategy it has.
  - How: hold FlyBehavior, QuackBehavior, or another supertype; select the concrete object at a construction or configuration boundary.
- **Runtime behavior setters**: expose a focused setter when a context must change its strategy during its lifetime.

## Key Concepts

- **Context**: the object whose behavior is supplied by a strategy; Duck is the context.
- **Strategy**: the common supertype for interchangeable algorithms.
- **Concrete strategy**: one implementation of the algorithm family, such as FlyWithWings.
- **Delegation**: the context forwards an operation to its current strategy.
- **HAS-A**: composition of a context with a strategy.
- **IS-A**: inheritance; useful for stable type relationships but less flexible for changing behavior.
- **Behavior family**: related implementations that share an operation but differ in algorithm.

## Mental Models

- Use Strategy when the question is “which algorithm should this object use?” rather than “which state is it in?”
- Think of the context as owning the decision point and the strategy as owning the algorithm.
- Treat a strategy interface as a seam for testing: a fake strategy can replace a production implementation.
- Runtime replacement is a consequence of composition, not a special feature of inheritance.

## Anti-patterns

- **Subclass-per-behavior**: creates class proliferation and makes runtime changes difficult.
- **Superclass with optional behavior methods**: subclasses inherit meaningless operations or must override them with no-op code.
- **Duplicated interface implementations**: solves type selection but scatters fixes across many classes.
- **Concrete strategy references in clients**: defeats the point of polymorphism and makes extensions require client edits.

## Code Examples

~~~java
public interface FlyBehavior {
    void fly();
}

public final class FlyRocketPowered implements FlyBehavior {
    public void fly() {
        System.out.println("I'm flying with a rocket!");
    }
}

public abstract class Duck {
    private FlyBehavior flyBehavior;
    public void performFly() { flyBehavior.fly(); }
    public void setFlyBehavior(FlyBehavior behavior) {
        this.flyBehavior = behavior;
    }
}
~~~

- **What it demonstrates**: the same Duck can delegate to any FlyBehavior, including a new implementation added later.

## Reference Tables

| Strategy | Inheritance |
|---|---|
| Behavior is composed into the context | Behavior is inherited by the subclass |
| Algorithms can be selected per instance | Behavior is mostly fixed by class |
| New strategies do not require context changes | New variants often require new subclasses |
| More objects and indirection | Fewer objects, but tighter coupling |

## Worked Example

ModelDuck begins with FlyNoWay because it is a model, not a flying duck. Later, the simulator calls modelDuck.setFlyBehavior(new FlyRocketPowered()). No ModelDuck subclass is added and no Duck code changes. The next call to performFly() delegates to the new strategy. The context’s identity stays stable while its algorithm changes.

## Key Takeaways

1. Isolate algorithms that vary from the object that uses them.
2. Give each strategy one coherent behavior and a common supertype.
3. Compose strategies into contexts and delegate through the supertype.
4. Use setters only when runtime switching is a real requirement.
5. Strategy and composition usually improve reuse more than inheritance hierarchies do.

## Connects To

- **Introduction**: the SimUDuck refactoring motivates the pattern.
- **Chapter 10 — State**: similar structure, different intent; State changes as the context transitions.
- **Chapter 12 — MVC**: the controller is a strategy plugged into the view.

