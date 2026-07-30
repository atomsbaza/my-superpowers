# Chapter 5: Bend, or Break

## Core Idea
Code that survives change is code built with minimal coupling: modules should hide their internals, defer details to metadata, avoid depending on the order or timing of events, separate models from views, and — where possible — exchange data anonymously through a shared space rather than through direct calls.

## Frameworks Introduced
- **Law of Demeter for Functions**: A method of an object should only call methods belonging to: itself, its parameters, any objects it creates, and its direct component objects — never an object obtained by calling another method (no "reaching through" a chain of getters).
  - When to use: whenever a method would otherwise traverse `a.getB().getC().getD()` to reach a needed value or service.
  - How: ask a directly-owned object to perform the work on your behalf (delegate) rather than pulling out a subordinate object and operating on it yourself; write small wrapper/forwarding methods so the "general contractor" (your object) deals with its "subcontractors" and shields the caller from them.
- **Metaprogramming (dynamic configuration via metadata)**: Program for the general case and put the specifics — algorithms, business rules, UI style, database choice — outside the compiled code, as metadata.
  - When to use: for anything likely to change more often than the code itself (business policy, tuning parameters, install directories, workflow rules).
  - How: express configuration as plain-text metadata (key/value files, embedded mini-languages, rule engines); decide whether it must be re-readable at runtime (long-running servers) or only at startup (short-lived clients).
- **Temporal Coupling / decoupling in time**: Design explicitly for concurrency and for the absence of a required ordering between operations, rather than assuming things happen one after another.
  - When to use: during workflow analysis, architecture, interface design, and deployment planning — any place a "tick before tock" assumption might sneak in.
  - How: model workflow with UML activity diagrams to expose what can run in parallel; architect independent, concurrent services communicating via work queues (the "hungry consumer" model); design interfaces (and class invariants) so objects are always in a valid state, since they may be called at any time.
- **Model-View-Controller / It's Just a View**: Separate the data model from the view(s) that display it and the controller(s) that manipulate it, connected via a publish/subscribe event mechanism.
  - When to use: any time more than one presentation, or more than one way of driving updates, is needed for the same underlying data — not just GUIs.
  - How: the model has no knowledge of its views; views subscribe to model change events; controllers publish events to the model and view; chain models/viewers into networks so one view can be another view's model.
- **Blackboard systems**: A shared space where producers and consumers of information post and read data anonymously and asynchronously, with no knowledge of each other's existence.
  - When to use: workflows or distributed data-gathering processes where data arrives in unpredictable order, from many uncoordinated sources, and where rules should trigger off whatever facts happen to be present.
  - How: post partial facts to a shared, possibly partitioned space; combine with a rules engine so posting a new fact can trigger further rules and further postings; use tuple-space style systems (JavaSpaces, T Spaces) with `read`/`write`/`take`/`notify` operations for programmatic implementations.

## Key Concepts
- **Coupling**: the dependencies among modules of code; the central enemy this chapter fights across every technique.
- **Response set**: the number of functions directly invoked by methods of a class; studies show classes with larger response sets are more error-prone.
- **Metadata**: data about data — configuration describing how an application should run, deferred out of the compiled code.
- **Cooperative configuration**: software that configures itself, or configures other software, dynamically at runtime without human intervention.
- **Activity diagram / synchronization bar**: a UML notation for capturing which actions in a workflow can run in parallel versus which must wait for others to complete.
- **Hungry consumer model**: a load-balancing pattern where independent consumer tasks pull work from a shared queue instead of a central scheduler pushing work to them.
- **Event**: a message meaning "something interesting just happened," used to decouple a sender from any particular receiver.
- **Publish/subscribe**: objects register interest in specific events so they receive only what they need, instead of being routed through one giant dispatch routine.
- **Tuple space**: a blackboard-style storage model (popularized by Linda) where active objects, not just data, can be stored and retrieved by pattern-matching templates.

## Mental Models
- Think of your modules as spy cells: each cell knows only its own members; if one is compromised, the others carry on — apply that isolation to code modules.
- Use the "general contractor" model for object collaboration: you hire your direct object for a service, and it deals with its own subcontractors on your behalf — you never talk to the subcontractors directly.
- Think of concurrency-first design as a discipline, not a feature: even if you never deploy concurrently, designing as if you might forces cleaner, coincidence-free interfaces.
- Think of a blackboard as a police incident board: detectives (modules) post evidence and observations without knowing who else is working the case, and the board itself is the only shared contract.

## Anti-patterns
- **Reaching through chained getters** (`aSelection.getRecorder().getLocation().getTimeZone()`): couples your code to three classes at once instead of one; an unrelated change anywhere in that chain forces a change in your code.
- **Hard-wiring business policy into code**: policies (payment terms, supplier categories) change far more often than the general shape of the requirement; wiring the policy directly into logic guarantees future rewrites for what should be metadata edits.
- **Routing all events through one dispatch routine**: violates encapsulation (one routine now needs intimate knowledge of every interaction), violates DRY and orthogonality, and typically shows up as a giant `case`/`if-then` chain.
- **Time-dependent APIs like `strtok`**: relying on hidden static state between calls (must call first with a buffer, then `NULL`) creates a temporal coupling that silently breaks as soon as two independent parses are attempted concurrently.
- **Wizard-generated code you don't understand** (spillover from ch5's Related sections into ch6, but rooted in the same coupling concerns): interweaving unexamined generated code with your own removes your ability to maintain or debug it.

## Code Examples
```java
// Violates the Law of Demeter: three classes of coupling
public void plotDate(Date aDate, Selection aSelection) {
    TimeZone tz = aSelection.getRecorder().getLocation().getTimeZone();
    ...
}

// Honors the Law of Demeter: ask for what you need directly
public void plotDate(Date aDate, TimeZone aTz) { ... }
plotDate(someDate, someSelection.getTimeZone());
```
- **What it demonstrates**: delegation removes the caller's dependency on `Recorder` and `Location`; `Selection` (or `Recorder` beneath it) absorbs the responsibility for locating the `TimeZone`.

```c
char buf1[BUFSIZ], buf2[BUFSIZ];
char *p, *q;
strcpy(buf1, "this is a test");
strcpy(buf2, "this ain't gonna work");
p = strtok(buf1, " ");
q = strtok(buf2, " ");   // clobbers strtok's implicit state from buf1
```
- **What it demonstrates**: temporal coupling via hidden static state; contrast with Java's `StringTokenizer`, whose instances hold their own position and are safe to interleave.

## Reference Tables
| JavaSpaces operation | Function |
|---|---|
| `read` | Search for and retrieve data from the space (non-destructive) |
| `write` | Put an item into the space |
| `take` | Like `read`, but removes the item from the space |
| `notify` | Register for notification whenever a matching object is written |

## Worked Example
The OLTP (On-Line Transaction Processing) system example: the authors describe a system that reads incoming transaction requests off many data communication lines and posts them against a back-end database. The constraints were that database operations are slow, communication lines must not block while a transaction is processed, the database performs worse with too many concurrent sessions, and each line has multiple transactions in flight at once. Rather than write a single monolithic dispatcher, they built the system as independent processes communicating through work queues: each input process only watches its own comm line and fires off asynchronous requests to an application server, which in turn queues work to a database process and is notified on completion. This is the "hungry consumer" model — a pool of independent consumer processes pull from a shared work queue instead of a central scheduler pushing to them, so a slow consumer never blocks the others. The result: temporally decoupled, independent "services" behind well-defined interfaces, which turned out to be *less* work than a synchronous design, not more, and which left the door open to deploy stand-alone, client-server, or n-tier without redesigning.

## Key Takeaways
1. Before writing a chain of getters, ask whether you can delegate the work to the object you already have instead of pulling out its internals.
2. Push anything that changes faster than your code (business policy, algorithm choice, UI style) out into metadata rather than hard-coding it.
3. Design for concurrency even for systems that will initially run stand-alone — retrofitting concurrency later is much harder than removing it from an already-concurrent design.
4. Separate model from view/controller from the start; it buys multiple simultaneous presentations of the same data almost for free.
5. When data arrives from many uncoordinated sources in unpredictable order, reach for a blackboard-plus-rules-engine architecture instead of a hand-coded workflow state machine.
6. The Law of Demeter has a real runtime/space cost (wrapper methods); apply it deliberately, and knowingly break it (like denormalizing a database) only when the coupling is well understood and accepted.

## Connects To
- **Ch 6**: Temporal coupling and concurrency discipline directly motivate "Design for Concurrency" as a way to fight Programming by Coincidence.
- **Ch 3 (Orthogonality, Reversibility)**: this chapter's techniques (Demeter, metadata, MVC, blackboards) are the concrete mechanisms for achieving the orthogonality and reversibility promised earlier in the book.
- **Design by Contract**: class invariants from Design by Contract are the tool recommended for keeping concurrently-accessed objects always in a valid state.
- **Observer pattern [GHJV95]**: publish/subscribe as described here is the general form of the Gang-of-Four Observer pattern.
