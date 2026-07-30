# Chapter 22: Chain of Responsibility Pattern

## Core Idea
Avoid coupling the sender of a request to its receiver by giving more than one object a chance to handle the request, chaining the receiving objects and passing the request along the chain until an object handles it.

## Frameworks Introduced
- **Chain of Responsibility**: Avoid coupling the sender of a request to its receiver by giving more than one object a chance to handle the request. Chain the receiving objects and pass the request along the chain until an object handles it (GoF).
  - When to use: A request may be handled by one of several candidate handlers, but the sender shouldn't need to know which handler is responsible — and the set/order of handlers should be changeable independently of the sender.
  - How: Each handler holds a reference to the next handler in the chain; on receiving a request, it either handles it fully or forwards it to the next handler, continuing until a handler processes it or the chain ends.

## Canonical GoF Reference (1994)
*Source: Gamma, Helm, Johnson & Vlissides, "Design Patterns: Elements of Reusable Object-Oriented Software" (Addison-Wesley, 1994).*

**Intent (verbatim)**: "Avoid coupling the sender of a request to its receiver by giving more than one object a chance to handle the request. Chain the receiving objects and pass the request along the chain until an object handles it."

**Applicability** — GoF says use this pattern when:
- More than one object may handle a request, and the handler isn't known a priori — it should be ascertained automatically.
- You want to issue a request to one of several objects without specifying the receiver explicitly.
- The set of objects that can handle a request should be specified dynamically.

**Participants**:
- **Handler** (`HelpHandler`) — defines an interface for handling requests and, optionally, implements the successor link.
- **ConcreteHandler** (`PrintButton`, `PrintDialog`) — handles requests it's responsible for; if it can't, forwards to its successor.
- **Client** — initiates the request to a ConcreteHandler object somewhere on the chain.

**Consequences**:
1. Reduced coupling — an object only needs to know a request will be handled "appropriately"; neither sender nor receiver needs explicit knowledge of the other, and objects need only a single reference to their successor rather than to every candidate receiver.
2. Added flexibility in assigning responsibilities — responsibilities can be added to or rearranged on the chain at run-time, combinable with static subclassing.
3. Receipt isn't guaranteed — since a request has no explicit receiver, it can fall off the end of the chain unhandled, whether by design or by a misconfigured chain.

**Implementation notes**: (1) Implementing the successor chain — either define new links (usually in Handler) or reuse existing links already present in the object structure (e.g., parent references in a part-whole hierarchy), which saves space but only works if that structure matches the needed chain. (2) Representing requests — a hard-coded operation call (simple, safe, closed set of requests) versus a single handler function keyed by request code (open-ended, but needs conditional dispatch and manual parameter packing) versus explicit Request objects (type-safer, subclassable per request kind). (3) Subclasses extend rather than override dispatch by handling only requests they care about and forwarding the rest to the parent class's handler. (4) Smalltalk can implement forwarding automatically via `doesNotUnderstand`, rather than hand-writing it per class.

**Known Uses (1994-era)**: MacApp and ET++'s `EventHandler`, Symantec TCL's `Bureaucrat`, and NeXT AppKit's `Responder` — all chain-of-responsibility event dispatch under different names; Unidraw's `Command` objects forwarding interpretation up a component/view hierarchy; ET++'s `InvalidateRect` graphical-update forwarding through enclosing Scrollers/Zoomers up to a `Window`.

**Related Patterns (per GoF)**: Chain of Responsibility is often applied together with **Composite**, where a component's parent acts as its successor in the chain.

## Key Concepts
- **Handler**: An object in the chain that can process a particular kind of request (e.g., `IReceiver` with `HandleMessage`).
- **Chain construction**: Handlers are wired together explicitly by passing the "next" handler into each constructor (e.g., `FaxErrorHandler` holds a reference to `EmailErrorHandler`).
- **Request forwarding**: If a handler cannot process the request, it forwards it unchanged to the next handler rather than failing outright.
- **Termination conditions**: The chain ends either when a handler fully processes the request, or when the end of the chain is reached with no handler claiming it.
- **Decoupled sender/receiver**: The object that raises the issue (`IssueRaiser`) knows only the first handler in the chain, not which handler will ultimately process the request.
- **Dynamic reordering**: Handlers can be added, removed, or reordered without changing the sender's code, since the sender only depends on the chain's entry point.

## Mental Models
- Think of a customer-care pipeline: a representative logs the issue and forwards it to the department that seems responsible; that department either fixes it or forwards it onward — no single department needs to know the full org chart in advance.
- Or a hospital referral: a doctor in one department can refer a patient to another department for further diagnosis if the issue is outside their responsibility, without the patient needing to know the diagnosis path up front.
- Use Chain of Responsibility when you have several handlers of the same general kind (e.g., error handlers for different channels) and you want the freedom to reorder them by frequency — e.g., placing `EmailErrorHandler` first if most issues are email issues, to reduce average processing time.
- Unlike Observer's parallel broadcast, model Chain of Responsibility as strictly sequential: one handler is tried, then the next, in order, until the chain resolves or ends.

## Anti-patterns
- **Assuming the request is always handled**: reaching the end of the chain with no handler claiming the request is a real possibility this pattern does not protect against by itself; unhandled requests can silently vanish unless you add explicit end-of-chain handling.
- **Coupling the sender to a specific handler**: defeats the purpose of the pattern — the sender (`IssueRaiser`) should only know the first handler, never which one will ultimately process the request.
- **Ignoring debuggability costs**: because responsibility is distributed across a dynamic chain, tracing which handler processed (or failed to process) a given request is harder than with a single centralized dispatcher.

## Code Examples
```csharp
public interface IReceiver
{
    bool HandleMessage(Message message);
}
public class IssueRaiser
{
    public IReceiver setFirstReceiver;
    public IssueRaiser(IReceiver firstReceiver)
    {
        this.setFirstReceiver = firstReceiver;
    }
    public void RaiseMessage(Message message)
    {
        if (setFirstReceiver != null) setFirstReceiver.HandleMessage(message);
    }
}
public class FaxErrorHandler : IReceiver
{
    private IReceiver nextReceiver;
    public FaxErrorHandler(IReceiver nextReceiver)
    {
        this.nextReceiver = nextReceiver;
    }
    public bool HandleMessage(Message message)
    {
        if (message.Text.Contains("Fax"))
        {
            Console.WriteLine("FaxErrorHandler processed {0} priority issue: {1}", message.Priority, message.Text);
            return true;
        }
        else
        {
            if (nextReceiver != null) nextReceiver.HandleMessage(message);
        }
        return false;
    }
}
```
- **What it demonstrates**: `IssueRaiser` only knows the first handler in the chain; each handler (`FaxErrorHandler`) either processes the message and returns `true`, or forwards it to `nextReceiver` — the chain-building constructor pattern wires `FaxErrorHandler` before `EmailErrorHandler` so fax issues are tried first.

```csharp
// Chain wiring in Main
IReceiver faxHandler, emailHandler;
//End of chain
emailHandler = new EmailErrorHandler(null);
//fax handler is placed before email handler
faxHandler = new FaxErrorHandler(emailHandler);
//Starting point: IssueRaiser will raise issues and set the first handler
IssueRaiser raiser = new IssueRaiser(faxHandler);
```
- **What it demonstrates**: The chain is assembled from the tail backward — `EmailErrorHandler` is the terminal handler (`null` next), and `FaxErrorHandler` is placed before it — showing how easily the order could be swapped without touching `IssueRaiser`.

## Reference Tables
| Aspect | Chain of Responsibility | Observer (Ch 14, for contrast) |
|---|---|---|
| Notification style | Sequential — one handler at a time | Parallel — all observers notified |
| Who decides completion | The chain, when a handler claims the request or the chain ends | N/A — all observers always get notified |
| Sender coupling | Sender knows only the first handler | Subject knows all registered observers |

## Worked Example
An `IssueRaiser` is wired to a two-handler chain: `FaxErrorHandler` → `EmailErrorHandler` (the terminal handler). Four messages are raised, mixing "Fax" and "Email" text with `Normal`/`High` priorities. `raiser.RaiseMessage(m1)` ("Fax is reaching late...") is caught by `FaxErrorHandler` since it contains "Fax". `m2` ("Emails are not reaching...") doesn't match "Fax", so `FaxErrorHandler` forwards it to `EmailErrorHandler`, which matches and processes it. `m3` ("In Email, CC field is disabled...") is likewise forwarded to and handled by `EmailErrorHandler`. `m4` ("Fax is not reaching destination...") is handled directly by `FaxErrorHandler`. The message priorities are printed but not used for routing logic — the Q&A clarifies they exist only to "beautify the code" and could instead drive a priority-based chain.

## Key Takeaways
1. The pattern decouples request senders from receivers by letting any of several handlers in a chain claim the request.
2. Handlers can be added, removed, or reordered dynamically without changing the sender, since the sender only references the chain's entry point.
3. There is no guarantee a request will be handled — reaching the end of the chain unhandled is a real failure mode that needs explicit handling (e.g., try/catch, or Smalltalk-style `doesNotUnderstand` forwarding to logging/queuing).
4. Debugging is trickier than a single dispatcher because responsibility is spread dynamically across the chain.
5. This code targets pre-modern C# (2018, .NET Framework era) — the sequential-handler-chain intent still applies today, but a modern implementation might express the chain as a pipeline of `Func<Message, bool>` delegates or middleware rather than hand-wired constructor chaining.

## Connects To
- **Ch 14 (Observer)**: The book explicitly contrasts the two in this chapter's Q&A — Observer notifies all registered objects in parallel, while Chain of Responsibility notifies objects sequentially until one handles the request or the chain ends.
- **GoF 1994 catalog**: Chain of Responsibility is one of the Behavioral patterns in the original Gang of Four catalog; the GoF also references Smalltalk's automatic message-forwarding mechanism (`doesNotUnderstand`) as a related real-world precedent for handling unclaimed requests.
- **GoF 1994 canonical entry**: The catalog's explicit liability — "receipt isn't guaranteed," since a request can fall off the end of an unhandled or misconfigured chain — is the pattern's key risk the derivative treatment doesn't call out by name, and GoF's cross-pattern discussion positions Chain of Responsibility as good for decoupling sender/receiver specifically when the chain structure already exists in the system (e.g., a part-whole hierarchy).
