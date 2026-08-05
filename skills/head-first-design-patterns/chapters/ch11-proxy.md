# Chapter 11: Controlling Object Access — Proxy

## Core Idea

Proxy provides a surrogate or placeholder for another object and controls access to it. The proxy implements the same service interface as the real subject, so clients can use local policy, lazy loading, remoting, caching, or synchronization without changing their code.

## Frameworks Introduced

- **Proxy Pattern**: “Provides a surrogate or placeholder for another object to control access to it.”
  - When to use: access requires a boundary, expensive creation, remote communication, permission check, or concurrency policy.
  - How: define a Subject interface, implement it with the RealSubject and a Proxy, and have the proxy mediate requests.
- **Remote Proxy**:
  - When to use: the real object lives in another address space or process.
  - How: proxy marshals a method call across the boundary and presents a local interface.
- **Virtual Proxy**:
  - When to use: object creation or loading is expensive.
  - How: proxy stands in until the real object is needed, then creates or loads it lazily.
- **Protection Proxy**:
  - When to use: access depends on caller identity or role.
  - How: proxy checks authorization before forwarding.
- **Java dynamic proxy**: the platform can create a proxy at runtime around an interface using an InvocationHandler.

## Key Concepts

- **Subject**: interface shared by proxy and real subject.
- **RealSubject**: object that performs the actual work.
- **Proxy**: intermediary that controls or augments access.
- **Lazy initialization**: delay expensive work until it is observable that the client needs it.
- **Marshalling**: encode a remote method call and its arguments for transport.
- **Protection boundary**: a policy checkpoint before delegation.
- **Invocation handler**: dynamic-proxy callback that receives method calls and decides what to do.

## Mental Models

- A virtual ImageProxy is an empty picture frame until the image is loaded; once loaded, it delegates painting to the real image.
- A remote proxy is a local-looking representative for a remote object. Network failures and latency remain part of the real behavior even if the interface looks ordinary.
- A protection proxy is a bouncer: it applies authorization policy before admitting a call.
- A proxy should preserve the subject contract while making its access behavior visible in documentation and failure handling.

## Anti-patterns

- **Proxy that changes the contract silently**: callers cannot reason about exceptions, latency, or authorization.
- **Synchronous remote calls in latency-sensitive code**: a local-looking method hides network delay.
- **Virtual proxy without thread safety**: concurrent callers may load the same resource repeatedly or observe partial initialization.
- **Protection checks only in the UI**: an alternate client can bypass the policy.
- **Proxy recursion or double mediation**: proxy and real subject accidentally wrap each other.

## Code Examples

~~~java
public interface Image {
    void display();
}

public final class ImageProxy implements Image {
    private final String filename;
    private ImageIcon realImage;

    public ImageProxy(String filename) { this.filename = filename; }

    @Override public void display() {
        if (realImage == null) {
            realImage = new ImageIcon(filename);
        }
        realImage.paintIcon(null, null, 0, 0);
    }
}
~~~

~~~java
public final class ProtectionProxy implements Person {
    private final Person target;
    private final Set<String> allowedRoles;

    public ProtectionProxy(Person target, Set<String> allowedRoles) {
        this.target = target;
        this.allowedRoles = allowedRoles;
    }

    @Override public void setName(String name) {
        if (allowedRoles.contains("owner")) target.setName(name);
        else throw new SecurityException("Not authorized");
    }
}
~~~

- **What it demonstrates**: the client depends on Image or Person, not on loading details or permission mechanics. Production proxies should also specify failure, caching, and thread-safety policy.

## Reference Tables

| Proxy variant | Access concern | Typical technique |
|---|---|---|
| Remote | Different process or machine | Serialize and transport calls |
| Virtual | Expensive creation or loading | Lazy initialization |
| Protection | Permission or role | Authorization check |
| Firewall | Network/resource boundary | Filter requests |
| Smart Reference | Extra behavior on access | Reference counting or locking |
| Caching | Repeated expensive calls | Store and reuse results |
| Synchronization | Concurrent access | Coordinate threads |
| Complexity Hiding | Difficult subsystem | Present a simpler interface |

| Proxy | Adapter | Decorator |
|---|---|---|
| Controls access to an existing subject | Converts one interface to another | Adds responsibilities to an object |
| Usually preserves the subject interface | Changes the client-facing interface | Preserves the component interface |
| Focuses on mediation | Focuses on compatibility | Focuses on flexible extension |

## Worked Example

The image viewer must display a large image without blocking startup. ImageProxy implements the same Image interface as the real image, renders a placeholder while loading, and replaces itself logically with the loaded image for subsequent painting. The application remains coupled to Image, while the proxy owns lazy loading and status behavior. A remote proxy follows the same shape but adds transport and failure concerns.

## Key Takeaways

1. Use the same Subject interface for proxy and real subject.
2. Match the proxy variant to the access problem.
3. Make hidden latency, failure, caching, and authorization semantics explicit.
4. Use virtual proxies to defer expensive work and protection proxies to enforce policy at the boundary.
5. Distinguish Proxy by intent from Adapter and Decorator even when their class diagrams look alike.

## Connects To

- **Chapter 7 — Adapter and Facade**: structural similarity makes intent the deciding factor.
- **Chapter 3 — Decorator**: both wrap objects; Proxy controls access while Decorator adds responsibilities.
- **Chapter 4 — Factory**: a Factory can create and hide the choice between a proxy and a real subject.
- **Chapter 9 — Composite**: a proxy can stand in for a tree or a remote composite.

