# Chapter 20: State Pattern

## Core Idea
Allow an object to alter its behavior when its internal state changes. The object will appear to change its class.

## Frameworks Introduced
- **State**: Allow an object to alter its behavior when its internal state changes. The object will appear to change its class.
  - When to use: When an object's behavior must vary depending on which of a fixed set of internal states it currently occupies, and you want to avoid large conditional (`if`/`switch`) blocks scattered through the object's methods.
  - How: A `context` class (e.g., `TV`) holds a reference to a `state` object implementing a common state interface (e.g., `IPossibleStates`). Each concrete state class implements the interface's methods and, where a transition applies, reassigns `context.CurrentState` to a new concrete state instance. The context delegates every relevant method call to its current state object.

## Canonical GoF Reference (1994)
*Source: Gamma, Helm, Johnson & Vlissides, "Design Patterns: Elements of Reusable Object-Oriented Software" (Addison-Wesley, 1994).*

**Intent (verbatim)**: "Allow an object to alter its behavior when its internal state changes. The object will appear to change its class."

**Also Known As**: Objects for States

**Applicability** — GoF says use this pattern when:
- An object's behavior depends on its state and must change at run-time depending on that state.
- Operations have large, multipart conditional statements that depend on the object's state, often duplicated across several operations; the State pattern puts each branch of the conditional into a separate class so the state can vary independently of other objects.

**Participants**:
- **Context** (`TCPConnection`) — defines the interface clients use and maintains an instance of a ConcreteState subclass representing the current state.
- **State** (`TCPState`) — defines an interface for encapsulating the behavior associated with a particular state of the Context.
- **ConcreteState subclasses** (`TCPEstablished`, `TCPListen`, `TCPClosed`) — each implements behavior associated with one state of the Context.

**Consequences**:
1. It localizes state-specific behavior and partitions behavior for different states — all code for one state lives in one State subclass, so new states/transitions are added by defining new subclasses rather than editing scattered conditionals; trades off against a larger number of (smaller) classes.
2. It makes state transitions explicit — rebinding the Context's single state-object variable is atomic, versus implicit transitions buried in data-value assignments.
3. State objects can be shared — if a State subclass carries no instance variables, its instances are effectively Flyweights and can be reused across contexts.

**Implementation notes**: (1) Who defines the state transitions — GoF says this isn't specified by the pattern; letting the State subclasses themselves decide their successor (rather than hard-coding it in Context) is more flexible, at the cost of coupling one State subclass to knowledge of another. (2) A table-based alternative (Cargill) maps inputs to successor states in a lookup table — more regular and data-driven, but less efficient than a virtual call, less explicit about intent, and awkward for attaching side-effecting actions to a transition. (3) Creating and destroying State objects — create-on-demand suits states that are rare/expensive and rarely revisited; create-all-up-front suits rapidly-changing state where destruction/recreation churn should be avoided. (4) Dynamic inheritance (e.g., Self's delegation) is the "true" mechanism this pattern is emulating in languages that lack it.

**Known Uses (1994-era)**: Johnson and Zweig's characterization of State applied to TCP connection protocols; the HotDraw and Unidraw drawing-editor frameworks, where a `Tool`/`DrawingController` pair changes editor behavior as the current tool changes; Coplien's Envelope-Letter idiom is a related but more general technique for changing an object's class at run-time.

**Related Patterns (per GoF)**: **Flyweight** explains when and how State objects with no instance variables can be shared. State objects are frequently implemented as **Singletons**.

## Key Concepts
- **Context**: The object whose behavior changes based on state (e.g., `TV`), holding a `CurrentState` property and delegating all state-dependent calls to it.
- **State interface**: The common contract (e.g., `IPossibleStates`) all concrete states implement, so the context can treat them interchangeably.
- **Concrete state**: A class representing one specific state (e.g., `Off`, `On`, `Mute`), implementing the state interface's methods with behavior specific to that state, including triggering transitions.
- **State transition**: Implemented by a concrete state's method setting `context.CurrentState` to a new state instance (e.g., `Off.PressOnButton()` sets `tvContext.CurrentState = new On(context)`).
- **Delegation**: The context's public methods (e.g., `TV.PressOnButton()`) simply forward the call to the current state object (`currentState.PressOnButton(this)`), never containing the state-specific logic itself.
- **State-as-singleton tendency**: State objects often behave like singletons in practice (per the book's Q&A), though the example instantiates a fresh state object on each transition.
- **Open/closed principle applied to states**: Each state class is closed for modification but the system is open for extension — new states can be added without editing existing state classes.

## Mental Models
- Real-life analogy from the book: a TCP network connection that can be established, closed, or listening, responding differently to requests depending on its current state.
- Computer-world analogy: a job-processing system that either processes a new job or signals "busy" depending on whether it has reached its maximum concurrent job capacity.
- The book's worked illustration: a TV and its remote — the TV can be Off, On, or Mute; pressing a button produces different results depending on current state (e.g., pressing Mute while Off does nothing but log a message; pressing On while Off transitions to On).
- Think of State as replacing a wall of `if (currentState == X)` conditionals with polymorphism: "delegate to whichever object represents where you currently are, and let that object decide what happens next and where you go."

## Anti-patterns
- **Encoding state transitions with nested if/else chains inside the context**: The book explicitly shows this as the alternative to avoid — it becomes unreadable and hard to extend as states multiply (illustrated with a snippet checking `currentState==OFF` repeatedly).
- **Letting state count grow unchecked without a plan**: More states means more scattered code across more classes, which the book flags as the pattern's key long-term maintenance challenge.
- **Dropping the `context` parameter from state methods to "simplify" the interface**: The book's Q&A rejects this — the context parameter is what lets a state method evaluate and perform the actual transition (e.g., assign `tvContext.CurrentState`).

## Code Examples
```csharp
using System;
namespace StatePattern
{
    interface IPossibleStates
    {
        void PressOnButton(TV context);
        void PressOffButton(TV context);
        void PressMuteButton(TV context);
    }

    class Off : IPossibleStates
    {
        TV tvContext;
        public Off(TV context)
        {
            Console.WriteLine(" TV is Off now.");
            this.tvContext = context;
        }
        public void PressOnButton(TV context)
        {
            Console.WriteLine("You pressed On button. Going from Off to On state");
            tvContext.CurrentState = new On(context);
        }
        public void PressOffButton(TV context)
        {
            Console.WriteLine("You pressed Off button. TV is already in Off state");
        }
        public void PressMuteButton(TV context)
        {
            Console.WriteLine("You pressed Mute button. TV is already in Off state, so Mute operation will not work.");
        }
    }

    class TV
    {
        private IPossibleStates currentState;
        public IPossibleStates CurrentState
        {
            get { return currentState; }
            set { currentState = value; }
        }
        public TV() { this.currentState = new Off(this); }
        public void PressOffButton() { currentState.PressOffButton(this); }
        public void PressOnButton() { currentState.PressOnButton(this); }
        public void PressMuteButton() { currentState.PressMuteButton(this); }
    }
}
```
- **What it demonstrates**: `TV` (context) delegates every button-press method to `currentState`; `Off` (a concrete state) both handles the Off-state behavior and performs the transition to `On` by reassigning `tvContext.CurrentState`.

## Reference Tables
| Aspect | State Pattern | Strategy Pattern |
|---|---|---|
| Structural shape (per GoF) | Similar to Strategy | Similar to State |
| Intent | Behavior changes as internal state changes; context delegates to current state | Provides an interchangeable alternative to subclassing for an algorithm |
| Shared characteristic | Both promote composition and delegation | Both promote composition and delegation |

## Worked Example
`TV` starts in the `Off` state (constructor sets `CurrentState = new Off(this)`). The demo presses buttons in the sequence Off→Mute→On→On→Mute→Mute→Off. Each `TV.PressXButton()` call delegates to `currentState.PressXButton(this)`. Off ignores a redundant Off press ("already in Off state") and ignores Mute ("Off state, so Mute operation will not work"), but transitions to `On` on an On press. Once `On`, a redundant On press is a no-op message, but a Mute press transitions to `Mute`. From `Mute`, a redundant Mute press is a no-op message, but an Off press transitions back to `Off`. Every transition prints both the button-press message and a constructor message from the new state (e.g., "TV is On now.").

The Q&A section shows the anti-pattern alternative: implementing the same logic with nested `if`/`else` checks against `currentState` inside `TV.PressOnButton()` directly, which the book presents to highlight how State's polymorphic delegation avoids this conditional sprawl.

## Key Takeaways
1. State pattern replaces conditional branching on an internal status flag with polymorphic delegation to state objects, each responsible for its own transitions and behavior.
2. The context (e.g., `TV`) never contains state-specific logic itself — it purely forwards calls to `currentState`, keeping the context class stable as new states are added.
3. State satisfies the open/closed principle: each state class is closed for modification, but new states can be added to extend the system without touching existing state classes.
4. Though State and Strategy share a nearly identical structural diagram in the GoF catalog, their intents differ — Strategy provides an interchangeable algorithm; State captures behavior that changes as an object's internal condition changes.
5. State objects often behave like singletons in practice even though this example instantiates a new state object on every transition — worth noting as a possible optimization for high-transition-frequency contexts.
6. The obvious cost of this pattern is that a large number of possible states leads to more classes and more scattered code, directly trading off maintainability for eliminating conditional complexity.
7. This 2018-era C# code predates modern idioms (records, pattern matching, primary constructors); the State pattern's intent — delegate behavior to interchangeable state objects — still applies, though a modern rewrite might use switch expressions with pattern matching or readonly structs for lighter-weight state representations.

## Connects To
- **Ch 16 (Template Method)**: Both are behavioral patterns that structure control flow around subclass/object specialization, though Template Method fixes an algorithm's step order while State lets the entire behavior set change per state.
- **GoF 1994 catalog**: State is one of the original 23 GoF behavioral patterns, notable for sharing a near-identical UML structure with Strategy despite differing intents — a frequent source of confusion the book explicitly addresses.
- **GoF 1994 canonical entry**: The original catalog frames the open design question of *who* decides state transitions — Context or the ConcreteState subclasses themselves — and contrasts the class-per-state approach with a table-driven transition scheme, a trade-off the derivative book's TV example does not surface.
