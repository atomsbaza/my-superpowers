# Chapter 8: Boundaries

## Core Idea
Third-party and not-yet-defined code brings power but also risk; clean systems isolate these boundaries behind a small number of controlled points instead of letting foreign APIs leak throughout the codebase.

## Frameworks Introduced
- **Learning Tests**: tests written purely to explore and verify understanding of a third-party API, using it exactly as production code will.
  - When to use: whenever adopting a new third-party library or framework, before or during integration.
  - How: write small `@Test` methods that call the third-party API the way you intend to use it in production; run them, read errors, adjust, and iterate until the API behaves as expected and understood. Keep the passing tests in the suite permanently.
- **Boundary Wrapping / Encapsulation**: hide a third-party interface (e.g. `java.util.Map`) inside a single class or small family of classes rather than passing it around the system.
  - When to use: any time a broad, general-purpose third-party interface (collections, frameworks) would otherwise be passed across public APIs.
  - How: create an application-specific class that owns the third-party object as a private field, exposes only the narrow operations the application needs, and performs casting/type conversion internally.
- **Adapter Pattern for Undefined APIs**: define the interface you wish you had, code against it, and write an Adapter later once the real third-party/subsystem API exists.
  - When to use: when a dependency's interface is unknown, unowned, or not yet designed (e.g. a subsystem another team hasn't finished).
  - How: define your own interface expressing intent in your domain's vocabulary; build and test your code against that interface using a fake/stub implementation; once the real API arrives, write an Adapter class that implements your interface and translates calls to the real API.

## Key Concepts
- **Boundary**: the point of contact between code you control and code/interfaces you do not (third-party libraries, undefined subsystems, other teams' components).
- **Third-party code**: packages or frameworks (open source or vendor) providing broad, general-purpose interfaces not tailored to your specific application needs.
- **Learning tests**: tests that encode what you've learned about a third-party API's behavior and double as regression checks when the library is upgraded.
- **Boundary/outbound tests**: tests exercising the third-party interface the same way production code does, giving early warning if a new release changes behavior incompatibly.
- **Adapter pattern**: a structural pattern used to convert between the interface you wish you had and the interface a third party actually provides.
- **Seam**: a place in the code where behavior can be substituted (e.g. a `FakeTransmitter`) without editing the class itself, enabling testing at a boundary.
- **Not-yet-defined interface**: an interface you author yourself to represent a dependency that doesn't exist yet or whose design is outside your control, so you aren't blocked waiting on it.
- **Clean boundary**: a boundary with very few code locations that know about the third-party specifics, backed by tests that define expectations.

## Mental Models
- Providers of general-purpose interfaces optimize for broad applicability; consumers want narrow, focused interfaces — that tension is the source of boundary problems, and it is resolved by wrapping, not by fighting the provider.
- "It's better to depend on something you control than on something you don't control, lest it end up controlling you" — minimize the surface area where foreign code touches your code.
- Learning a third-party API and integrating it are each hard; doing both simultaneously in production code is doubly hard — separate the two by learning first, in isolated tests.
- An undefined boundary is like fog: you can't see past it, but you can still know exactly what shape you want the edge to have, and build confidently up to that edge.

## Anti-patterns
- **Passing third-party interfaces (e.g. `Map`, `Map<Sensor>`) freely around the system**: every consumer becomes coupled to that interface's full surface (including dangerous methods like `clear()`), so any change to the third-party interface (e.g. Java 5 generics) forces changes at every call site.
- **Casting objects pulled from a generic container repeatedly throughout the codebase**: duplicates responsibility for type-safety everywhere instead of centralizing it, hurting readability and increasing error surface.
- **Learning a new API by experimenting directly inside production code**: conflates the hard problem of understanding the API with the hard problem of integrating it correctly, leading to long, ambiguous debugging sessions.
- **Blocking on an undefined or unowned interface**: waiting for another team to finish their API before starting your own work stalls progress unnecessarily when you could define the interface you need and adapt later.
- **Staying on an outdated third-party version to avoid discovering incompatibilities**: without boundary/learning tests giving early warning of behavior changes, teams avoid upgrades longer than they should.

## Code Examples
```java
public class Sensors {
  private Map sensors = new HashMap();

  public Sensor getById(String id) {
    return (Sensor) sensors.get(id);
  }
  //snip
}
```
- **What it demonstrates**: hiding the boundary interface (`Map`) inside a single class so the rest of the application only sees the narrow, tailored `Sensors` API — generics or other `Map` changes are absorbed in one place.

## Reference Tables
(omit if none)

## Worked Example
The chapter walks through learning the Apache `log4j` logging library from scratch via learning tests. First attempt just logs "hello":
```java
@Test
public void testLogCreate() {
  Logger logger = Logger.getLogger("MyLogger");
  logger.info("hello");
}
```
This fails, revealing the need for an `Appender`. Adding a bare `ConsoleAppender` still fails — no output stream configured. After research, the author supplies a `PatternLayout` and `ConsoleAppender.SYSTEM_OUT` explicitly, and logging finally works — revealing an odd, undocumented default-constructor behavior in `log4j` (arguably a library inconsistency). Each experiment is captured as a permanent unit test rather than thrown away, converging on `LogTest.java`, a small suite (`basicLogger`, `addAppenderWithStream`, `addAppenderWithoutStream`) that fully documents correct `log4j` initialization. That accumulated knowledge is then encapsulated into the team's own logger class, isolating the rest of the application from the `log4j` boundary. A second worked example describes a radio communications project where the "Transmitter" subsystem's API wasn't yet defined; the team wrote their own `Transmitter` interface (`transmit(frequency, dataStream)`) expressing intent, built `CommunicationsController` against it, and later added a `TransmitterAdapter` once the real API existed — using a `FakeTransmitter` as a test seam throughout.

## Key Takeaways
1. Never pass a broad third-party interface (like `Map`) across public APIs — wrap it in an application-specific class that exposes only what you need.
2. Write learning tests before or while integrating any new third-party library; they cost nothing beyond the learning you'd do anyway and double as regression tests against future upgrades.
3. Keep learning/boundary tests in the permanent suite and rerun them on every third-party version bump to catch incompatible behavior changes immediately.
4. When a dependency's interface is unknown or undefined, define the interface you wish you had, code against it, and test with a fake — don't let an unfinished dependency block your progress.
5. Once the real third-party or subsystem API is available, bridge it with an Adapter, keeping the translation logic in one place.
6. Concentrate all boundary knowledge into a small number of classes/locations so future changes to the third-party code require touching minimal code.
7. Prefer depending on interfaces you control over interfaces you don't — it preserves your ability to change and test your own code independently.

## Connects To
- **Ch 9 (Unit Tests)**: learning tests and boundary tests are a specialized application of the general unit-testing discipline — same FIRST principles apply.
- **Ch 6 (Objects and Data Structures)**: wrapping `Map` behind `Sensors` is an instance of choosing a clean, minimal object interface over exposing a raw data structure's full capability.
- **Ch 11 (Systems)**: boundary management is a system-level concern about separating construction/dependency concerns from use, keeping architecture decoupled from external frameworks.
- **Ch 24 (Acceptance Testing, The Clean Coder)**: both chapters treat tests as executable specifications/contracts — learning tests specify third-party behavior the way acceptance tests specify system behavior.
- **Adapter pattern [GOF]**: the structural pattern explicitly cited for bridging your own interface to a third-party or subsystem API once it becomes known.
- **Seams [WELC — Working Effectively with Legacy Code]**: the concept used to justify how boundary wrapping enables substituting fakes for testing.
