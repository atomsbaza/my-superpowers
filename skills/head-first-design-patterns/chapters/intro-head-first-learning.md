# Introduction: Your Brain on Design Patterns

## Core Idea

Design patterns are reusable design experience, not paste-in code. Start with the change pressure in a design, identify what varies, and use object-oriented principles to isolate that variation so the rest of the system can remain stable.

## Frameworks Introduced

- **Encapsulate What Varies**: Identify the behavior or decision that changes most often and separate it from the stable parts.
  - When to use: whenever new requirements force edits across unrelated subclasses or clients.
  - How: isolate the varying behavior behind a supertype, compose it into the context, and delegate.
- **Program to a Supertype**: Declare collaborators using an interface or abstract type so the concrete implementation can vary.
  - When to use: whenever a client should work with several interchangeable implementations.
  - How: keep the variable typed as the supertype and inject or create the concrete implementation at a boundary.
- **Favor Composition over Inheritance**: Acquire behavior by composing objects instead of inheriting every possible behavior.
  - When to use: when behavior needs to differ between instances or change at runtime.
  - Why it works: composition supports reuse without forcing every subclass to inherit the same behavior.
- **Strategy Pattern**: A family of algorithms is encapsulated and made interchangeable; the algorithm varies independently from the context.

## Key Concepts

- **Change**: the constant pressure that makes rigid designs expensive.
- **Behavior class**: a class whose primary responsibility is one reusable behavior.
- **Delegation**: forwarding work to a composed collaborator.
- **Composition**: a HAS-A relationship used to assemble behavior at runtime.
- **Polymorphism**: substituting any concrete implementation of a common supertype.
- **Design pattern**: experience reuse at the design level.
- **Shared vocabulary**: a pattern name communicates structure, intent, trade-offs, and constraints.

## Mental Models

- Think “what changes?” before thinking “what class should I add?”
- Treat a behavior as a first-class design element; it can have state, methods, and multiple implementations.
- Use inheritance for stable identity and shared structure; use composition for variable behavior.
- Patterns go into the designer’s brain first, then into code.

## Anti-patterns

- **Behavior in a superclass**: subclasses inherit behavior they may not support, and a fix can affect every subclass.
- **One interface per behavior with duplicated implementations**: avoids inappropriate inheritance but loses reuse.
- **Concrete-type decision trees**: every new implementation requires edits to the client.
- **Pattern fever**: applying a pattern to trivial code adds indirection without solving a real change problem.

## Code Examples

~~~java
public abstract class Duck {
    FlyBehavior flyBehavior;
    QuackBehavior quackBehavior;

    public void performFly() { flyBehavior.fly(); }
    public void performQuack() { quackBehavior.quack(); }
    public void setFlyBehavior(FlyBehavior behavior) {
        flyBehavior = behavior;
    }
}
~~~

- **What it demonstrates**: the stable Duck delegates variable behavior to objects typed by interfaces.

## Reference Tables

| Design choice | Main consequence |
|---|---|
| Inheritance for changing behavior | Reuse is static and changes spread through subclasses |
| Interfaces with duplicated behavior | Behavior is selectable but not reused |
| Composition + delegation | Behavior is reusable, replaceable, and can change at runtime |

## Worked Example

The SimUDuck application first puts fly() and quack() in Duck, which makes rubber ducks fly and forces every subclass to understand every behavior. The refactoring pulls those methods into FlyBehavior and QuackBehavior families. MallardDuck composes FlyWithWings and Quack; ModelDuck starts with FlyNoWay, then switches to FlyRocketPowered through setFlyBehavior(). The duck hierarchy remains focused on duck identity while behavior becomes independently reusable.

## Key Takeaways

1. Start design work by locating likely change points.
2. Encapsulate variation behind a stable supertype.
3. Composition is the mechanism that makes behavior reusable and replaceable.
4. Use pattern names as a precise design vocabulary, not as decoration.
5. Prefer the simplest design that handles a real change.

## Connects To

- **Chapter 1 — Strategy**: the complete encapsulated-behavior example.
- **Chapter 3 — Decorator**: runtime composition extends responsibilities.
- **Chapter 13 — Patterns in the Real World**: when to introduce or remove patterns.

