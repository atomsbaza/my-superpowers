# Chapter 20: State Pattern

## Core Idea
Allow an object to alter its behavior when its internal state changes. The object will appear to change its class.

## Frameworks Introduced
- **State**: Allow an object to alter its behavior when its internal state changes. The object will appear to change its class.
  - When to use: When an object's behavior must vary depending on which of a fixed set of internal states it currently occupies, and you want to avoid large conditional (`if`/`switch`) blocks scattered through the object's methods.
  - How: A `context` class (e.g., `TV`) holds a reference to a `state` object implementing a common state interface (e.g., `IPossibleStates`). Each concrete state class implements the interface's methods and, where a transition applies, reassigns `context.CurrentState` to a new concrete state instance. The context delegates every relevant method call to its current state object.

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
