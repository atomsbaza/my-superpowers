# Chapter 2: Keeping Your Objects in the Know — Observer

## Core Idea

Observer creates a one-to-many dependency between a subject that owns state and a changing set of observers that depend on it. When the subject changes, it notifies registered observers without knowing their concrete classes.

## Frameworks Introduced

- **Observer Pattern**: “Defines a one-to-many dependency between objects so that when one object changes state, all of its dependents are notified and updated automatically.”
  - When to use: when many independent consumers need updates from one changing source and consumers may be added or removed.
  - How: define Subject registration/removal/notification operations and an Observer update operation; compose observers with the subject at runtime.
- **Loose coupling**:
  - When to use: whenever a publisher should not depend on the details of its consumers.
  - How: make the subject depend only on the observer interface; allow new observers without modifying the subject.
- **Push vs. pull notification**:
  - Push passes changed values in update(...).
  - Pull sends a notification and lets each observer call subject getters for only the state it needs.

## Key Concepts

- **Subject**: the object that owns and changes the authoritative state.
- **Observer**: a dependent that receives a notification.
- **One-to-many relationship**: one subject coordinates many observers.
- **Registration**: adding an observer to the subject’s collection.
- **Notification**: invoking the common observer callback.
- **Loose coupling**: limited knowledge of collaborators’ concrete details.
- **Publish-subscribe**: related but more decoupled messaging where subscribers can express message interests.
- **Display element**: a Weather Station client that renders a view of the subject’s measurements.

## Mental Models

- Think newspaper publisher/subscribers: subscriptions are dynamic, and the publisher does not tailor itself to each subscriber.
- Use push when a stable, small state payload is convenient; use pull when the subject’s state may grow or observers need different slices.
- Treat registration and removal as a lifecycle contract, not just a list operation.
- A subject owns data; observers consume notifications and should not become competing owners of that data.

## Anti-patterns

- **Hard-coded display calls in measurementsChanged()**: every new display requires editing the subject.
- **Concrete observer fields**: the subject becomes coupled to each display implementation.
- **Leaking the collection representation**: clients should not need to know how observers or measurements are stored.
- **Assuming notification order**: Observer users should not depend on a particular order unless the contract explicitly guarantees it.

## Code Examples

~~~java
public interface Subject {
    void registerObserver(Observer observer);
    void removeObserver(Observer observer);
    void notifyObservers();
}

public class WeatherData implements Subject {
    private final List<Observer> observers = new ArrayList<>();
    private float temperature;

    public void registerObserver(Observer observer) {
        observers.add(observer);
    }
    public void removeObserver(Observer observer) {
        observers.remove(observer);
    }
    public void notifyObservers() {
        for (Observer observer : observers) {
            observer.update();
        }
    }
    public float getTemperature() { return temperature; }
}
~~~

- **What it demonstrates**: a pull-oriented subject can notify without exposing a fixed payload shape.

## Reference Tables

| Choice | Strength | Cost |
|---|---|---|
| Push update(temp, humidity, pressure) | Simple observer implementation | Adding subject state can change every observer |
| Pull update() + subject getters | Observers choose what they need; state can grow | Observers retain a subject reference and make more calls |
| Direct callbacks to concrete displays | Easy first implementation | No extension seam; high coupling |

## Worked Example

WeatherData stores temperature, humidity, and pressure. CurrentConditionsDisplay, StatisticsDisplay, and ForecastDisplay register themselves in their constructors. Each new measurement calls notifyObservers(), which invokes the common update() contract. A future heat-index display only implements Observer and registers; WeatherData remains unchanged. In the book’s first version, measurements are pushed. The more extensible revision sends a no-argument update and lets each display pull the values it needs.

## Key Takeaways

1. Keep the subject’s state in one authoritative place.
2. Depend on the Observer interface, not concrete displays.
3. Make observer membership dynamic through register/remove operations.
4. Choose push or pull based on how likely the subject’s state contract is to change.
5. Loose coupling is the reason new observers do not require subject changes.

## Connects To

- **Chapter 7 — Facade**: both reduce client knowledge, but Facade simplifies calls rather than broadcasting changes.
- **Chapter 12 — MVC**: the model uses Observer to notify views and sometimes controllers.
- **Java Swing**: listeners such as ActionListener are a familiar Observer-shaped API.

