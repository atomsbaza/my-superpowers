# Chapter 7: Being Adaptive — Adapter and Facade

## Core Idea

Adapter changes an existing interface into the interface a client expects. Facade provides a simpler, unified interface to a subsystem while leaving the subsystem available. Both wrap objects, but intent—not the number of wrapped classes—distinguishes them.

## Frameworks Introduced

- **Adapter Pattern**: “Converts the interface of a class into another interface the clients expect. Adapter lets classes work together that couldn’t otherwise because of incompatible interfaces.”
  - When to use: an existing or vendor class cannot be changed, but a client already depends on another interface.
  - How: implement the target interface, hold the adaptee, translate each target operation into one or more adaptee calls; use a two-way adapter when both interfaces must be supported.
- **Facade Pattern**: “Provides a unified interface to a set of interfaces in a subsystem. Facade defines a higher-level interface that makes the subsystem easier to use.”
  - When to use: clients repeatedly coordinate a complex subsystem or should be decoupled from its concrete components.
  - How: compose the subsystem components into a facade, orchestrate their calls, and keep direct subsystem access available for advanced clients.
- **Principle of Least Knowledge**: interact with a small set of close friends—the object itself, method parameters, objects it creates, and its own components.

## Key Concepts

- **Target**: the interface the client expects.
- **Adaptee**: the existing interface or class that needs translation.
- **Object adapter**: uses composition; works with an adaptee and its subclasses.
- **Class adapter**: uses multiple inheritance; unavailable in ordinary Java.
- **Two-way adapter**: implements both interfaces.
- **Facade**: simplified entry point to a subsystem.
- **Subsystem**: cooperating classes behind the facade.
- **Least Knowledge**: limit direct knowledge and chained method calls.
- **Law of Demeter**: another name for the Principle of Least Knowledge.

## Mental Models

- Adapter is a translator: preserve the client’s vocabulary while converting calls behind the boundary.
- Facade is a control panel: expose the common sequence, but do not remove the detailed controls.
- Judge an Adapter and Decorator by intent: Adapter changes the interface; Decorator adds responsibility.
- A long call chain such as station.getThermometer().getTemperature() signals that a collaborator should perform the request.

## Anti-patterns

- **Changing every client for a vendor interface**: spreads compatibility code instead of isolating it.
- **Confusing Adapter with Decorator**: wrapping alone does not tell you the pattern.
- **Facade that hides all lower-level access**: a facade simplifies; it does not have to forbid advanced use.
- **Excessive wrapper methods for Least Knowledge**: fewer dependencies trade for more code, objects, and possible runtime cost.

## Code Examples

~~~java
public final class TurkeyAdapter implements Duck {
    private final Turkey turkey;
    public TurkeyAdapter(Turkey turkey) { this.turkey = turkey; }
    public void quack() { turkey.gobble(); }
    public void fly() {
        for (int i = 0; i < 5; i++) {
            turkey.fly();
        }
    }
}

public final class HomeTheaterFacade {
    private final Amplifier amp;
    private final Projector projector;
    private final StreamingPlayer player;

    public void watchMovie(String movie) {
        amp.on();
        projector.on();
        amp.setStreamingPlayer(player);
        player.play(movie);
    }
}
~~~

- **What it demonstrates**: the adapter translates a Duck call to Turkey operations; the facade sequences subsystem work.

## Reference Tables

| Pattern | Intent | Client sees |
|---|---|---|
| Adapter | Convert an incompatible interface | The target interface |
| Facade | Simplify a subsystem | One higher-level operation |
| Decorator | Add responsibilities | The original component type plus behavior |
| Proxy | Control access to a subject | The subject interface |

## Worked Example

The home-theater client originally turns on the popper, dims lights, lowers the screen, configures the projector and amplifier, starts the player, and later reverses the sequence. HomeTheaterFacade exposes watchMovie(movie) and endMovie(). The facade knows the correct order and delegates to each component. If the components are upgraded, the client remains written against the facade; a client needing a special projector feature can still access the subsystem directly.

## Key Takeaways

1. Use Adapter when the client and existing class disagree about vocabulary.
2. Use Facade when the vocabulary is valid but too complex for common use.
3. Adapter and Facade may wrap multiple classes; count is not the deciding test.
4. Use composition for flexible object adapters.
5. Apply Least Knowledge with awareness of the wrapper and performance trade-off.

## Connects To

- **Chapter 3 — Decorator**: same wrapping shape, different intent.
- **Chapter 11 — Proxy**: same-subject substitution, but Proxy controls access.
- **Chapter 12 — MVC**: HeartAdapter lets a different model satisfy BeatModelInterface.

