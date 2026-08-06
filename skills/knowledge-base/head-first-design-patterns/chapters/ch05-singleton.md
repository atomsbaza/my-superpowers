# Chapter 5: One-of-a-Kind Objects — Singleton

## Core Idea

Singleton controls instantiation so a class has one instance and offers a global access point to it. The pattern is simple in structure but easy to get wrong around lazy creation, threads, class loaders, reflection, serialization, and coupling.

## Frameworks Introduced

- **Singleton Pattern**: “Ensures a class has only one instance, and provides a global point of access to it.”
  - When to use: when multiple instances would create inconsistent state, waste scarce resources, or conflict with a unique resource.
  - How: make the constructor inaccessible, store the unique instance in the class, and expose an access method or enum constant.
- **Lazy instantiation**: create the instance only when getInstance() is first called.
  - When to use: the object is expensive and may never be needed.
  - Trade-off: lazy initialization must be safe under concurrent access.
- **Eager instantiation**: initialize the unique instance when the class is loaded.
  - When to use: creation is cheap or guaranteed to be needed.
- **Double-checked locking**: check before and inside synchronization, with volatile publication.

## Key Concepts

- **Unique instance**: the one object managed by the Singleton class.
- **Global access point**: the class-level API used to retrieve that object.
- **Private constructor**: prevents outside code from calling new.
- **Lazy creation**: defers allocation until first use.
- **Eager creation**: allocates during class initialization.
- **Synchronization**: coordinates concurrent first access.
- **Volatile**: prevents unsafe publication in the double-checked implementation.
- **Enum Singleton**: Java enum-based approach that handles many construction and serialization concerns.
- **Class-loader boundary**: separate class loaders can create separate Singleton instances.

## Mental Models

- Singleton is an ownership policy, not merely a convenient global variable.
- Ask whether “one per process,” “one per class loader,” or “one per application scope” is actually required.
- The pattern’s global access can be useful while also becoming a hidden dependency.
- Use it sparingly; a large population of Singletons is a design smell.

## Anti-patterns

- **Unsynchronized lazy initialization**: two threads can observe null and create two instances.
- **Global variable disguised as Singleton**: offers access but may not enforce uniqueness or lazy creation.
- **Singleton for every shared service**: spreads hidden coupling and makes tests or replacement harder.
- **Assuming private construction solves every loophole**: reflection, serialization, and multiple class loaders need separate consideration.

## Code Examples

~~~java
public enum Singleton {
    UNIQUE_INSTANCE;

    public void doSomething() {
        // shared service state and behavior
    }
}

public final class SingletonClient {
    public void run() {
        Singleton.UNIQUE_INSTANCE.doSomething();
    }
}
~~~

- **What it demonstrates**: enum construction gives one named instance with JVM-managed initialization and serialization behavior.

~~~java
public final class LazySingleton {
    private volatile static LazySingleton uniqueInstance;
    private LazySingleton() {}

    public static LazySingleton getInstance() {
        if (uniqueInstance == null) {
            synchronized (LazySingleton.class) {
                if (uniqueInstance == null) {
                    uniqueInstance = new LazySingleton();
                }
            }
        }
        return uniqueInstance;
    }
}
~~~

- **What it demonstrates**: the book’s double-checked approach avoids synchronizing every access; volatile is required for safe publication.

## Reference Tables

| Implementation | Use when | Main concern |
|---|---|---|
| Synchronized getInstance() | Access is not performance-critical | Synchronization overhead |
| Eager static instance | Creation is cheap or always needed | No lazy resource saving |
| Double-checked locking | Lazy creation and hot access both matter | More complex; requires volatile |
| Enum | Java implementation can use an enum | API shape differs from getInstance() |

## Worked Example

The ChocolateBoiler must never have two controllers filling or draining separate copies of the same physical boiler. Its constructor is private, and callers retrieve the shared object through getInstance(). The boiler still owns ordinary state such as empty and boiled; Singleton controls only instance ownership. If initialization is expensive and access is concurrent, choose synchronized access, eager initialization, or double-checked locking based on the actual performance and lifecycle requirements.

## Key Takeaways

1. Define the required scope of “one” before choosing Singleton.
2. Prevent outside construction and provide one controlled access path.
3. Pick lazy, eager, synchronized, double-checked, or enum implementation deliberately.
4. Expect hidden coupling and testability costs from global access.
5. Prefer enum in modern Java when its API and scope fit the need.

## Connects To

- **Chapter 4 — Factory**: factories encapsulate creation without imposing one instance.
- **Chapter 6 — Command**: commands can use shared receivers, but do not make every receiver global.
- **Chapter 10 — State**: state objects may be shared when they hold no context-specific state.

