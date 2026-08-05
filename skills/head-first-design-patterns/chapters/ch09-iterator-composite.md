# Chapter 9: Well-Managed Collections — Iterator and Composite

## Core Idea

Iterator and Composite solve two different collection problems. Iterator separates sequential traversal from an aggregate’s representation; Composite lets clients treat individual objects and compositions uniformly in a tree.

## Frameworks Introduced

- **Iterator Pattern**: “Provides a way to access the elements of an aggregate object sequentially without exposing its underlying representation.”
  - When to use: clients need to traverse different collection implementations through one protocol.
  - How: give the aggregate a method that returns an iterator with operations such as hasNext() and next().
- **Composite Pattern**: “Allows you to compose objects into tree structures to represent part-whole hierarchies. Composite lets clients treat individual objects and compositions of objects uniformly.”
  - When to use: the domain is recursive and a node can contain more nodes or leaves.
  - How: define a common component abstraction, implement leaves directly, and let composites hold children.
- **Single Responsibility Principle**: a class should have one reason to change. An iterator keeps traversal responsibility out of the menu or aggregate.
- **Transparency versus safety**: a transparent Composite interface exposes child operations on every component; a safer interface separates leaf and composite capabilities but requires more type checks.

## Key Concepts

- **Aggregate**: a collection that exposes an iterator rather than its storage details.
- **Iterator**: the traversal object that tracks current position.
- **External iterator**: traversal state lives outside the aggregate and the client advances it.
- **Internal iterator**: the aggregate controls traversal and applies an operation to each element.
- **Leaf**: a terminal Composite object such as MenuItem.
- **Composite**: a node that contains child components, such as Menu.
- **Uniform treatment**: client code can call a common operation on a leaf or an entire subtree.
- **Recursive structure**: a tree whose nodes can contain trees of the same component type.

## Mental Models

- The client should ask an iterator for the next element, not ask a menu whether it uses an array or an ArrayList.
- A Composite is a file-system-like tree: a file is a leaf, a directory is a composite, and both can be displayed.
- Tree operations naturally become recursive: a composite performs work for itself and delegates the same operation to each child.
- Adding child-management methods to leaves makes an interface transparent but can produce meaningless operations and runtime failures.

## Anti-patterns

- **Representation-aware client**: branching on ArrayList versus array versus HashMap leaks collection decisions into every caller.
- **Traversal in the aggregate’s public API**: callers become coupled to indexes and storage layout.
- **Composite as a universal bag of operations**: leaf methods that throw UnsupportedOperationException weaken the abstraction.
- **Recursive Composite without a termination case**: forgetting the leaf behavior causes infinite recursion or null handling bugs.
- **Overlooking mutation semantics**: an iterator must define what happens when the aggregate changes during traversal.

## Code Examples

~~~java
public interface Iterator<T> {
    boolean hasNext();
    T next();
}

public interface Menu {
    Iterator<MenuItem> createIterator();
}

public final class PancakeHouseMenu implements Menu {
    private final List<MenuItem> items = new ArrayList<>();

    public Iterator<MenuItem> createIterator() {
        return items.iterator();
    }
}
~~~

~~~java
public abstract class MenuComponent {
    public void print() { throw new UnsupportedOperationException(); }
    public void add(MenuComponent component) { throw new UnsupportedOperationException(); }
    public Iterator<MenuComponent> createIterator() { throw new UnsupportedOperationException(); }
}

public final class MenuItem extends MenuComponent {
    private final String name;

    public MenuItem(String name) { this.name = name; }
    @Override public void print() { System.out.println(name); }
}

public final class Menu extends MenuComponent {
    private final List<MenuComponent> children = new ArrayList<>();

    @Override public void add(MenuComponent component) { children.add(component); }
    @Override public void print() {
        for (MenuComponent child : children) child.print();
    }
    @Override public Iterator<MenuComponent> createIterator() {
        return children.iterator();
    }
}
~~~

- **What it demonstrates**: Iterator hides storage representation; Composite makes print() work across a menu tree. Production code should choose an explicit policy for unsupported leaf operations or use a safer split interface.

## Reference Tables

| Concern | Iterator | Composite |
|---|---|---|
| Primary problem | Traverse collections uniformly | Represent part-whole trees uniformly |
| Main abstraction | Iterator | Component |
| Hides | Collection representation | Leaf/composite distinction from clients |
| Typical operation | hasNext()/next() | print(), display(), calculate() |

| Composite design choice | Benefit | Cost |
|---|---|---|
| Transparent interface | Simple client code; uniform treatment | Invalid methods may exist on leaves |
| Safe interface | Capability rules are explicit | Clients may need type distinctions |

## Worked Example

The diner menu application combines a PancakeHouseMenu backed by an ArrayList, a DinerMenu backed by an array, and a cafe menu backed by another collection. Waitress code should print all menus without knowing any representation. Each menu supplies an iterator, and the waitress loops through the common protocol. Later, a dessert submenu is nested under a parent menu. Modeling MenuItem as a leaf and Menu as a composite lets the same print operation recurse through the entire hierarchy.

## Key Takeaways

1. Encapsulate traversal as an object.
2. Program against Iterator rather than a concrete collection.
3. Use Composite for recursive part-whole structures.
4. Decide deliberately between transparent and safe Composite interfaces.
5. Pair Composite with Iterator when clients must traverse trees without exposing their representation.

## Connects To

- **Chapter 1 — Strategy**: both move a variable responsibility behind an interface.
- **Chapter 6 — Command**: commands can be queued and iterated over for execution or logging.
- **Chapter 12 — Compound Patterns**: the duck simulator uses Composite and Iterator together for flocks.
- **Chapter 14 — Leftover Patterns**: Visitor can add operations across a Composite structure.

