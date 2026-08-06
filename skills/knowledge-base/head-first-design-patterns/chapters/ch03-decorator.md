# Chapter 3: Decorating Objects — Decorator

## Core Idea

Decorator wraps an object with another object that has the same supertype, adding responsibilities dynamically while preserving substitutability. It is a flexible alternative to building every combination as a subclass.

## Frameworks Introduced

- **Open-Closed Principle**: “Classes should be open for extension, but closed for modification.”
  - When to use: focus it on likely change points rather than applying it everywhere.
  - How: provide extension seams such as composition and polymorphic wrappers; accept that flexibility adds abstraction and complexity.
- **Decorator Pattern**: “Attaches additional responsibilities to an object dynamically. Decorators provide a flexible alternative to subclassing for extending functionality.”
  - When to use: optional, combinable responsibilities must be selected at runtime.
  - How: share the component supertype, store the wrapped component, add behavior before/after delegation, and allow nested wrappers.

## Key Concepts

- **Component**: the common supertype of concrete objects and decorators.
- **Concrete component**: the base object being extended, such as DarkRoast.
- **Decorator**: a wrapper with the same component type.
- **Concrete decorator**: one responsibility, such as Mocha or Whip.
- **Transparent composition**: decorated objects can be passed where the component type is expected.
- **Delegation chain**: the outer decorator delegates inward until the concrete component handles the base operation.
- **Open for extension**: new behavior can be added through new decorators.
- **Closed for modification**: existing components need not change for each new responsibility.

## Mental Models

- Think of decorators as an onion: the outermost layer gets the call first and can add its contribution before delegating inward.
- Use inheritance to obtain the component type when necessary; obtain behavior through composition.
- Keep decorators focused on one responsibility so chains remain understandable.
- OCP is a targeted design choice, not a demand that every class be infinitely extensible.

## Anti-patterns

- **Subclass for every condiment combination**: produces a class explosion and fixes choices at compile time.
- **Boolean flags in the base component**: every new option changes the base class and creates conditional logic.
- **Client code that checks concrete component types**: wrapping makes the original concrete type invisible.
- **Unmanaged deep chains**: many small wrappers can overwhelm users and complicate construction.

## Code Examples

~~~java
public abstract class Beverage {
    protected String description = "Unknown Beverage";
    public String getDescription() { return description; }
    public abstract double cost();
}

public abstract class CondimentDecorator extends Beverage {
    protected final Beverage beverage;
    protected CondimentDecorator(Beverage beverage) {
        this.beverage = beverage;
    }
}

public final class Mocha extends CondimentDecorator {
    public Mocha(Beverage beverage) { super(beverage); }
    public String getDescription() {
        return beverage.getDescription() + ", Mocha";
    }
    public double cost() { return beverage.cost() + .20; }
}
~~~

- **What it demonstrates**: Mocha is itself a Beverage, so it can wrap another beverage and delegate the base cost.

## Reference Tables

| Decorator | Inheritance-only extension |
|---|---|
| Runtime composition | Compile-time subclass choice |
| Many responsibilities can be mixed | Combinations require subclasses |
| Preserves component interface | May expose a different or broader API |
| Can create many small objects | Can create a large class hierarchy |

## Worked Example

A Starbuzz order starts as new DarkRoast(). Wrapping it with new Mocha(...), then another Mocha, then new Whip(...) creates a chain. Calling getDescription() walks inward and accumulates labels; calling cost() adds the base drink and each decorator’s price. The client uses only Beverage, so it does not care how many layers exist. Factory or Builder can later encapsulate this potentially error-prone construction.

## Key Takeaways

1. Make decorators and components share the same supertype.
2. Add one responsibility per decorator and delegate the rest.
3. Use Decorator when combinations are runtime choices.
4. Apply OCP where change is probable; do not abstract everything.
5. Keep clients at the component type and avoid concrete-type tests.

## Connects To

- **Chapter 2 — Observer**: registration can extend a subject without modifying it.
- **Chapter 4 — Factory**: factories can hide nested decorator construction.
- **Java I/O**: FilterInputStream and related streams use decorator-like wrapping.
- **Chapter 7 — Adapter and Facade**: all wrap objects, but their intents differ.

