# Chapter 12: Patterns of Patterns — Compound Patterns

## Core Idea

A compound pattern combines two or more patterns to solve a recurring problem in a general way. The value comes from the collaboration among patterns, not from collecting pattern names. The simulator and MVC examples show how separate abstractions can cooperate without collapsing into one giant class.

## Frameworks Introduced

- **Compound Pattern**: a solution in which multiple patterns work together to solve a recurring or general problem.
  - When to use: several independent design pressures appear together and a known collaboration handles them cleanly.
  - How: assign each responsibility to a fitting pattern, then define the contracts between the participants.
- **Duck Simulator compound design**:
  - Adapter converts Goose into Quackable.
  - Decorator adds counting to Quackable objects.
  - Abstract Factory creates a family of counting or non-counting ducks.
  - Composite represents a flock of Quackables.
  - Iterator traverses the flock.
  - Observer reports quack events to the simulator.
- **Model-View-Controller**:
  - Model encapsulates data and domain behavior.
  - View renders the model and can be composed from GUI components.
  - Controller interprets input and selects behavior, often through Strategy-like variation.
  - Observer keeps views synchronized with model changes.

## Key Concepts

- **Collaboration**: the runtime relationship through which patterns hand work to one another.
- **Quackable**: the common subject interface used by ducks, an adapted goose, decorators, and composites.
- **QuackCounter**: a Decorator that delegates quack behavior and increments a shared counter.
- **CountingDuckFactory**: an Abstract Factory that produces decorated duck variants consistently.
- **Flock**: a Composite whose children may be individual ducks or nested flocks.
- **Observable model**: a model that notifies views when its state changes.
- **Controller**: translates user actions into model operations and chooses view behavior.
- **Pattern language**: a vocabulary of related patterns and their collaborations for a problem domain.

## Mental Models

- A compound pattern is an orchestra: each pattern has a part, and the arrangement defines the result.
- Follow one event through the system to understand the design: a duck quacks, the decorator counts, the observer is notified, and a flock composite may propagate the operation.
- MVC is a separation of change rates: data/domain rules, presentation, and input handling can evolve independently.
- Use factories to make composition consistent; otherwise callers can accidentally construct objects that do not participate in the intended compound design.

## Anti-patterns

- **Pattern soup**: adding patterns because they are available rather than because a design pressure requires them.
- **Leaky compound boundaries**: clients reach into concrete decorators, factories, or model internals and defeat the collaboration.
- **Circular MVC dependencies**: views mutate model internals directly or models start rendering themselves.
- **Inconsistent assembly**: some ducks are counted and others are not because object construction is scattered.
- **Observable everything**: notifying every object for every detail creates noise and hidden coupling.

## Code Examples

~~~java
public interface Quackable extends QuackObservable {
    void quack();
}

public final class QuackCounter implements Quackable {
    private final Quackable duck;
    private static int numberOfQuacks;

    public QuackCounter(Quackable duck) { this.duck = duck; }
    @Override public void quack() {
        duck.quack();
        numberOfQuacks++;
    }
    public static int getQuacks() { return numberOfQuacks; }
}
~~~

~~~java
public final class Flock implements Quackable {
    private final List<Quackable> quackers = new ArrayList<>();

    public void add(Quackable quacker) { quackers.add(quacker); }
    @Override public void quack() {
        for (Quackable quacker : quackers) quacker.quack();
    }
}
~~~

~~~java
public final class BeatController implements ControllerInterface, Observer {
    private final BeatModelInterface model;
    private final BeatBar view;

    public void update(Observable source, Object arg) {
        view.updateBPM(model.getBPM());
    }

    public void start() { model.on(); model.setBPM(90); }
    public void stop() { model.off(); }
}
~~~

- **What it demonstrates**: the first two snippets combine interface, decorator, and composite collaborations; the MVC sketch separates model notifications from controller actions and view rendering.

## Reference Tables

| Simulator responsibility | Pattern |
|---|---|
| Make incompatible Goose look like Quackable | Adapter |
| Count every quack without editing duck classes | Decorator |
| Create a consistent family of counting ducks | Abstract Factory |
| Treat duck groups as one quacker | Composite |
| Traverse groups uniformly | Iterator |
| Report quacks to an inspector | Observer |

| MVC part | Main responsibility | Common pattern contribution |
|---|---|---|
| Model | State and domain behavior | Observer subject |
| View | Display and user-facing presentation | Composite; Observer observer |
| Controller | Interpret input and coordinate actions | Strategy-like behavioral variation |

## Worked Example

The simulator begins with Quackable ducks. A GooseAdapter lets a goose join the same ecosystem, while QuackCounter decorates each object to count quacks. A CountingDuckFactory centralizes construction so the simulator cannot forget a decorator. Flock uses Composite to group quackers and Iterator to traverse them. Quackologist observes individual quack events. Each pattern handles one pressure, and the interfaces between them make the compound solution testable.

## Key Takeaways

1. Combine patterns only where their collaborations answer recurring design pressures.
2. Design the interfaces between patterns as carefully as the patterns themselves.
3. Use factories to preserve consistent assembly of a compound design.
4. Trace runtime events to understand compound behavior.
5. Treat MVC as a family of collaborating responsibilities rather than a single class diagram.

## Connects To

- **Chapters 2–11**: the compound examples deliberately reuse the earlier patterns.
- **Chapter 13 — Real World**: patterns become most useful when named as part of a shared vocabulary.
- **Chapter 14 — Leftover Patterns**: additional patterns can extend a compound design, but every addition needs a concrete pressure.

