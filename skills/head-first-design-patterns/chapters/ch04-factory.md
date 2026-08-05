# Chapter 4: Baking with OO Goodness — Factory Method and Abstract Factory

## Core Idea

Factory patterns encapsulate object creation so clients depend on abstractions rather than a growing list of concrete classes. Simple Factory centralizes creation; Factory Method defers one product decision to subclasses; Abstract Factory creates related product families through composition.

## Frameworks Introduced

- **Simple Factory**: an idiom that moves new and type selection into one creator object.
  - When to use: one application needs a small, centralized creation policy.
  - Trade-off: it is not a formal GoF pattern and a static factory cannot be subclassed.
- **Factory Method Pattern**: “Defines an interface for creating an object, but lets subclasses decide which class to instantiate.”
  - When to use: a framework owns a stable process but regional or product-specific subclasses choose the concrete product.
  - How: put the factory method in an abstract creator; keep the algorithm in the creator; let concrete creators return concrete products.
- **Abstract Factory Pattern**: “Provides an interface for creating families of related or dependent objects without specifying their concrete classes.”
  - When to use: products must be created as a compatible family, such as regional pizza ingredients or platform-specific widgets.
  - How: define one creation method per product; compose clients with a concrete factory selected for the context.
- **Dependency Inversion Principle**: high-level and low-level components should both depend on abstractions, not high-level code on low-level concrete classes.

## Key Concepts

- **Creator**: the class that owns the product workflow in Factory Method.
- **Concrete creator**: a subclass that implements the factory method.
- **Product**: the abstract type returned to clients.
- **Simple Factory**: centralized creation without subclass-based variation.
- **Factory Method**: creation through inheritance.
- **Abstract Factory**: creation of a product family through composition.
- **Product family**: related products that must be mutually compatible.
- **Dependency Inversion Principle**: a direction-of-dependencies guideline.
- **Concrete dependency**: a direct reference or instantiation of a specific implementation.

## Mental Models

- When you see a long if (type) chain of new expressions, ask whether creation is the changing part.
- Factory Method varies “which class makes this one product?”; Abstract Factory varies “which compatible family makes all these products?”
- Use inheritance for Factory Method and object composition for Abstract Factory.
- DIP is a guideline, not a ban on every new; stable classes such as String may be safe concrete dependencies.

## Anti-patterns

- **Dependent Pizza Store**: one client instantiates every regional/product class and changes for every menu addition.
- **Creation mixed with workflow**: orderPizza() becomes a concrete-class decision tree instead of a stable process.
- **Static factory when subclass variation is needed**: static creation is convenient but cannot be overridden.
- **Inconsistent product families**: individually selecting ingredients can mix incompatible regional implementations.

## Code Examples

~~~java
public abstract class PizzaStore {
    public final Pizza orderPizza(String type) {
        Pizza pizza = createPizza(type);
        pizza.prepare();
        pizza.bake();
        pizza.cut();
        pizza.box();
        return pizza;
    }
    protected abstract Pizza createPizza(String type);
}

public final class NYPizzaStore extends PizzaStore {
    protected Pizza createPizza(String type) {
        if (type.equals("cheese")) return new NYStyleCheesePizza();
        if (type.equals("clam")) return new NYStyleClamPizza();
        return null;
    }
}
~~~

- **What it demonstrates**: the creator owns the invariant preparation sequence; the subclass owns concrete product selection.

## Reference Tables

| Technique | Varies | Mechanism | Main trade-off |
|---|---|---|---|
| Simple Factory | Product selection | One factory object/method | Central point, but not a formal extensible pattern |
| Factory Method | One product implementation | Creator subclass | Adds creator subclasses |
| Abstract Factory | Product family | Composed factory object | Adding a new product kind changes every factory |

## Worked Example

The pizza store’s preparation steps are stable, but the pizza classes differ by region. Factory Method keeps orderPizza() in PizzaStore and lets NYPizzaStore or ChicagoPizzaStore implement createPizza(). When ingredient compatibility also matters, each pizza receives a regional PizzaIngredientFactory; createDough(), createSauce(), and createCheese() all come from that one family. Switching the factory changes the regional family without changing pizza preparation logic.

## Key Takeaways

1. Encapsulate creation when concrete types are a likely source of change.
2. Use Simple Factory for centralization, Factory Method for subclass-controlled products.
3. Use Abstract Factory for compatible families of products.
4. Keep high-level workflows written against product abstractions.
5. Treat DIP guidelines as design pressure, not mechanically absolute rules.

## Connects To

- **Chapter 3 — Decorator**: factories and builders can hide wrapper-chain construction.
- **Chapter 8 — Template Method**: Factory Method is a specialization using subclass-supplied operations.
- **Chapter 12 — Compound Patterns**: Abstract Factory ensures decorated duck families are created consistently.

