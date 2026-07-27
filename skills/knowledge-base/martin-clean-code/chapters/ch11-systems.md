# Chapter 11: Systems

## Core Idea
Cleanliness must extend beyond code into system-level architecture: separate the concern of *constructing* a system (wiring objects together) from the concern of *using* it, and let architecture grow incrementally from POJOs rather than committing to a Big Design Up Front.

## Frameworks Introduced
- **Separation of Construction from Use**: construction is a fundamentally different process from runtime use, and the two should never be mixed in the same method or class.
  - When to use: always — any time an object graph is being assembled, whether at application startup or on demand during execution.
  - How: move all object creation into `main` (or modules `main` calls) or into dedicated Factories/DI containers, so the rest of the application only consumes fully-constructed objects and has zero knowledge of how they were built.
- **Dependency Injection (DI) / Inversion of Control (IoC)**: an object should never instantiate its own dependencies; instead an authoritative external mechanism (a "main" routine or a DI container) constructs and injects them via constructor arguments or setters.
  - When to use: whenever a class needs collaborators whose concrete type may vary by context (test vs. production, different environments) or whose construction is nontrivial.
  - How: define wiring declaratively (XML config, annotations, or a construction module); the container resolves and injects dependencies, often lazily on demand.
- **Cross-Cutting Concerns / Aspect-Oriented Programming (AOP)**: concerns like persistence, transactions, security, and caching cut across normal object/class boundaries and can't be modularized with ordinary OO decomposition alone; AOP-like mechanisms declare these behaviors separately and weave them in non-invasively.
  - When to use: when the same infrastructural behavior (logging, transactions, persistence) must apply uniformly across many otherwise-unrelated domain classes.
  - How: use proxies, byte-code manipulation, or a dedicated aspect language (AspectJ) to intercept method calls and apply the cross-cutting behavior without editing the target source.

## Key Concepts
- **Lazy Initialization/Evaluation**: the `if (x == null) x = new X()` idiom; avoids unneeded construction cost but silently couples the caller to a concrete class and mixes two responsibilities in one method.
- **Factory pattern / Abstract Factory**: gives application code control over *when* an object is created while keeping the details of *how* it's built (and its dependencies) out of application code.
- **IoC container**: a special-purpose framework (e.g., Spring) that reads configuration and constructs/wires the object graph on the application's behalf.
- **POJO (Plain Old Java Object)**: a domain object with no dependencies on any framework or infrastructure API, making it simple, testable, and free to evolve.
- **Java Proxies**: JDK dynamic proxies (interface-only) or byte-code libraries (CGLIB, ASM, Javassist for classes) used to wrap objects and intercept calls — the low-level mechanism many AOP tools build on.
- **DECORATOR ("Russian doll")**: a chain of nested proxy/wrapper objects (e.g., domain object → DAO → JDBC data source) where each layer adds one concern transparently.
- **Domain-Specific Language (DSL)**: a small scripting language or fluent API that lets code read like domain prose, minimizing the translation gap between domain experts and implementation.
- **Big Design Up Front (BDUF)**: designing the entire system architecture before writing any code; contrasted with incremental architecture and called out as harmful for software.
- **"An optimal system architecture consists of modularized domains of concern"**: each implemented with POJOs, integrated by minimally invasive Aspects or aspect-like tools — the chapter's central formulation of good system design.

## Mental Models
- **The city analogy**: a city works not because one person designs it all up front, but because it grows incrementally with clear separation of concerns (water, power, traffic) and levels of abstraction that let people work on their part without understanding the whole — software systems should scale the same way.
- **Construction crane vs. finished building**: construction (cranes, hard hats) and use (finished glass tower) are different processes with different actors; conflating them in code creates the same kind of mess as leaving scaffolding attached to a finished building.
- **Software has different physics than buildings**: buildings require BDUF because structural changes are infeasible mid-construction; software, if properly decoupled, can change radically and cheaply even late — so incremental, test-driven architecture is not just possible but preferable.
- **Postpone decisions to the last responsible moment**: modularity and separation of concerns let teams defer architectural commitments until they have maximum information, reducing the cost of premature decisions.

## Anti-patterns
- **Mixing construction with use**: e.g., lazy-init inside a getter — hard-codes a dependency, breaks compilation without unrelated classes, complicates testing (need to inject test doubles before the method runs), and violates the Single Responsibility Principle by giving one method two jobs.
- **Scattered, duplicated setup logic**: many small ad hoc construction idioms spread across the app instead of one global, consistent wiring strategy — erodes modularity even if each instance looks harmless.
- **Heavyweight invasive frameworks (EJB1/EJB2 as the cautionary case)**: business logic subclassed container types and implemented empty lifecycle methods, coupling domain logic so tightly to the container that isolated unit testing was nearly impossible and reuse outside the framework was infeasible.
- **Adopting standards for their own sake**: teams used EJB2 "because it was a standard" even when lighter designs would have sufficed — losing focus on delivering customer value.
- **Over-engineered APIs / BDUF**: architecture decided entirely before implementation, discouraging later change due to sunk-cost psychology and prematurely constraining subsequent design thinking.

## Code Examples
```java
public Service getService() {
    if (service == null)
        service = new MyServiceImpl(...); // Good enough default for most cases?
    return service;
}
```
- **What it demonstrates**: the LAZY-INITIALIZATION anti-pattern — construction and use mixed in one method, hard-coding a concrete dependency and complicating testing.

```java
// Bank.java
public interface Bank {
    Collection<Account> getAccounts();
    void setAccounts(Collection<Account> accounts);
}

// BankImpl.java — the POJO implementing the abstraction
public class BankImpl implements Bank {
    private List<Account> accounts;
    public Collection<Account> getAccounts() { return accounts; }
    public void setAccounts(Collection<Account> accounts) {
        this.accounts = new ArrayList<Account>();
        for (Account account : accounts) this.accounts.add(account);
    }
}

// BankProxyHandler.java — InvocationHandler required by the Proxy API
public class BankProxyHandler implements InvocationHandler {
    private Bank bank;
    public BankProxyHandler(Bank bank) { this.bank = bank; }
    public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
        String methodName = method.getName();
        if (methodName.equals("getAccounts")) {
            bank.setAccounts(getAccountsFromDatabase());
            return bank.getAccounts();
        } else if (methodName.equals("setAccounts")) {
            bank.setAccounts((Collection<Account>) args[0]);
            setAccountsToDatabase(bank.getAccounts());
            return null;
        } else { ... }
    }
    protected Collection<Account> getAccountsFromDatabase() { ... }
    protected void setAccountsToDatabase(Collection<Account> accounts) { ... }
}

// wiring
Bank bank = (Bank) Proxy.newProxyInstance(
    Bank.class.getClassLoader(),
    new Class[] { Bank.class },
    new BankProxyHandler(new BankImpl()));
```
- **What it demonstrates**: a hand-rolled JDK dynamic proxy adding persistence behavior to a POJO non-invasively — and how much boilerplate that requires compared to a framework-managed aspect.

## Reference Tables
| Approach | Coupling to framework | Testability | Boilerplate |
|---|---|---|---|
| EJB2 Entity Beans | Very high — subclass container types, implement empty lifecycle methods | Poor — must mock/deploy heavyweight container | High |
| Hand-written Java Proxy | Low — POJO + InvocationHandler | Good | High (proxy plumbing) |
| Spring AOP / JBoss AOP (pure Java) | Very low — POJOs + declarative config | Very good | Low |
| EJB3 (annotations) | Low-moderate — annotations only | Good | Low-moderate |
| AspectJ | Low, but requires new tools/language | Good | Low, steeper learning curve |

## Worked Example
Martin traces one domain object — a `Bank` with persisted accounts — through three architectural eras to show cross-cutting concerns handled with decreasing invasiveness.

1. **EJB2**: `Bank` extends `javax.ejb.EntityBean`, implements a local interface (`BankLocal`) full of `EJBException`-throwing getters/setters, plus empty lifecycle methods (`ejbActivate`, `ejbPassivate`, `ejbLoad`, `ejbStore`, etc.) forced on it by the container, plus separate XML deployment descriptors for persistence/transactions/security. Business logic and container plumbing are inseparably tangled; unit testing requires mocking or deploying to a real server.
2. **JDK Proxy (Listing 11-3)**: `Bank` becomes a plain interface, `BankImpl` a true POJO with no framework awareness, and a separate `BankProxyHandler` implements persistence by intercepting `getAccounts`/`setAccounts` calls via `InvocationHandler` and reflection. This decouples the domain object but the proxy/reflection code is verbose and doesn't scale to declaring "system-wide points of interest" the way real AOP does.
3. **Spring AOP config (Listing 11-4)**: an XML file wires `appDataSource` → `bankDataAccessObject` → `bank` as nested "Russian doll" decorators; application code fetches the fully wired `bank` in two lines (`XmlBeanFactory` + `getBean("bank")`). The framework generates the proxy machinery automatically, so almost no Spring-specific code appears in the application.
4. **EJB3 (Listing 11-5)**: the same `Bank` becomes a POJO annotated with `@Entity`, `@Table`, `@Id`, `@Embedded`, `@OneToMany` — persistence metadata lives in annotations rather than invasive base classes, yielding code that is clean, testable, and (if desired) can push the mapping details out to XML entirely for a pure POJO.

The arc shows the same problem — persist a `Bank`'s accounts — solved with steadily less invasive, more test-drivable architecture, illustrating that "an optimal system architecture consists of modularized domains of concern" implemented as POJOs and integrated via minimally invasive aspects.

## Key Takeaways
1. Separate the code that constructs your object graph (main, factories, DI containers) from the code that uses it — dependency arrows should point away from `main`, never toward it.
2. Prefer true Dependency Injection over ad hoc lazy-initialization or JNDI-style active lookups; let a container or main routine own the "authoritative" construction responsibility.
3. Treat persistence, transactions, security, and similar concerns as cross-cutting; solve them with proxies, AOP frameworks, or annotations rather than invasive base classes and boilerplate lifecycle methods.
4. Keep domain logic in POJOs with zero framework dependencies — this is what makes both code and architecture test-drivable.
5. Don't do Big Design Up Front; software's economics allow architecture to grow incrementally from a simple, decoupled starting point, adding infrastructure only as scale demands it.
6. Postpone architectural and technology decisions until the last responsible moment to maximize the information available when the decision is made.
7. Adopt standards only when they add demonstrable value — a standard chosen for its own sake (as many teams chose EJB2) can cost more than it saves.

## Connects To
- **Ch 6 (Objects and Data Structures)**: POJOs as objects that expose behavior, not data structures manipulated externally — the domain objects wired together here are the same kind of well-formed objects Ch 6 argues for.
- **Ch 9 (Unit Tests)**: separating construction from use is what makes classes testable in isolation without mocking heavyweight containers, echoing Ch 9's emphasis on fast, isolated tests.
- **Ch 10 (Classes)**: the Single Responsibility Principle invoked against lazy-initialization here is the same SRP that Ch 10 applies at the class-design level.
- **Ch 12 (Emergence)**: "simplest thing that can possibly work," incremental design, and eliminating duplication are Kent Beck's four rules of simple design, which this chapter applies at the system/architecture level.
- **Ch 13 (Concurrency)**: cross-cutting concerns and separation of construction from use recur when reasoning about thread-safety boundaries and where synchronization logic should live.
- **DI, AOP, IoC**: the chapter's central external concepts — Dependency Injection and Inversion of Control for construction, Aspect-Oriented Programming for cross-cutting concerns — both aimed at keeping domain code as plain, framework-free POJOs.
