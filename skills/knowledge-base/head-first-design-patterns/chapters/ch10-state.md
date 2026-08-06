# Chapter 10: The State of Things — State

## Core Idea

State lets an object change its behavior when its internal state changes. The context delegates state-specific behavior to a current State object, so the context appears to change class without a large conditional state machine.

## Frameworks Introduced

- **State Pattern**: “Allows an object to alter its behavior when its internal state changes. The object will appear to change its class.”
  - When to use: behavior depends on a bounded set of states and transitions make conditional code unstable or difficult to extend.
  - How: define a State interface, create one class per state, and let the context delegate requests to its current state.
- **State transition**:
  - Fixed transition: the context controls the next state when the graph is stable.
  - Distributed transition: state objects choose the next state when behavior or workflow rules evolve frequently.
- **State versus Strategy**: the class shape is similar, but State’s objects usually represent phases and transitions; Strategy represents an algorithm selected by a client or context.

## Key Concepts

- **Context**: owns the current state and the public API clients use.
- **State**: common interface for state-specific behavior.
- **Concrete State**: implements behavior and may trigger a transition.
- **Transition**: movement from one state to another after an event.
- **State machine**: states, events, guards, actions, and transitions that define lifecycle behavior.
- **Guard**: a condition that permits or prevents a transition.
- **Delegation**: forwarding the request to the current state instead of branching in the context.

## Mental Models

- A gumball machine has no single correct response to insertQuarter(); the answer depends on whether it is NoQuarter, HasQuarter, Sold, or SoldOut.
- Start with a state/event table. It exposes missing transitions before code hides them.
- The context owns long-lived resources and identity; a State owns the behavior rules for one phase.
- A state object should not quietly mutate unrelated context data without an explicit collaboration contract.

## Anti-patterns

- **Giant conditional state machine**: one method accumulates if/else branches for every event and state.
- **Duplicated transition rules**: different handlers disagree about which state follows an event.
- **State classes that become mini-contexts**: too much data and orchestration make ownership unclear.
- **Implicit invalid events**: silently ignoring an event can hide a bad caller or lost transition.
- **State explosion**: creating a class for every incidental variation instead of modeling meaningful lifecycle states.

## Code Examples

~~~java
public interface State {
    void insertQuarter();
    void ejectQuarter();
    void turnCrank();
    void dispense();
}

public final class GumballMachine {
    private State state;
    private int count;

    public void insertQuarter() { state.insertQuarter(); }
    public void turnCrank() { state.turnCrank(); }
    void setState(State state) { this.state = state; }
    int getCount() { return count; }
}

public final class HasQuarterState implements State {
    private final GumballMachine machine;

    public HasQuarterState(GumballMachine machine) { this.machine = machine; }
    public void insertQuarter() { System.out.println("You can't insert another quarter"); }
    public void ejectQuarter() { machine.setState(new NoQuarterState(machine)); }
    public void turnCrank() { machine.setState(new SoldState(machine)); }
    public void dispense() { }
}
~~~

- **What it demonstrates**: GumballMachine remains the context; the current state decides what an event means and can request a transition.

## Reference Tables

| Role | Responsibility |
|---|---|
| Context | Stores current State, owns public operations and shared data |
| State | Declares events understood by each state |
| Concrete State | Implements event behavior and transition policy |
| Client | Uses the Context rather than selecting state internals directly |

| State | Strategy |
|---|---|
| Represents a lifecycle phase | Represents a replaceable algorithm |
| Often changes as events occur | Usually selected/configured by a client or context |
| Encodes transitions and valid events | Focuses on one algorithm contract |

## Worked Example

The original gumball machine mixes inventory checks, quarter handling, crank handling, and dispensing transitions in one class. Extracting NoQuarterState, HasQuarterState, SoldState, and SoldOutState makes each rule local. When the machine has one gumball left, it can transition through a WinnerState that dispenses two gumballs with a one-in-ten chance. The state graph is easier to test because each event has a named owner.

## Key Takeaways

1. Extract state-dependent behavior when conditionals keep expanding.
2. Keep the context’s public surface stable while state implementations vary.
3. Make invalid events explicit and test every transition.
4. Put transitions in the context for stable graphs or in state objects for more dynamic rules.
5. Use State for lifecycle behavior; use Strategy for interchangeable algorithms.

## Connects To

- **Chapter 1 — Strategy**: same delegation shape, different intent.
- **Chapter 6 — Command**: events can be represented as commands before a State handles them.
- **Chapter 8 — Template Method**: both centralize behavior structure, but State changes behavior at runtime while Template Method varies subclass steps.
- **Chapter 12 — Compound Patterns**: stateful model behavior can participate in MVC-style designs.

