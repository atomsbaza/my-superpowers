# Chapter 23: Presenters and Humble Objects

## Core Idea
The Humble Object pattern splits hard-to-test behavior (kept deliberately "humble"/trivial) from easy-to-test behavior, and this split recurs at nearly every architectural boundary in Clean Architecture — Presenter/View, gateway/database, and service listener/external service.

## Frameworks Introduced
- **The Humble Object pattern** (originated by Gerard Meszaros, *xUnit Patterns*): split behaviors into two modules — a humble one holding only the hard-to-test essentials, and a testable one holding everything that was stripped out.
  - When to use: any boundary where one side is inherently hard to unit test (GUI rendering, raw DB access, raw service I/O) and the other side contains logic worth testing.
  - How: move all decision-making/formatting/business logic into the testable module; leave the humble module with nothing but mechanical data transfer (e.g., "move data from ViewModel onto the screen").
- **Presenter/View split**: the GUI-specific instantiation of Humble Object.
  - When to use: whenever building any UI (web, thick client, console).
  - How: Presenter (testable) receives application data (Date, Currency objects, etc.) and formats it into a plain **ViewModel** of strings/booleans/enums; View (humble) does nothing but copy ViewModel fields onto the screen with zero processing.
- **Database Gateways**: polymorphic interfaces between use-case interactors and the database, one method per CRUD operation the application needs (e.g., `getLastNamesOfUsersWhoLoggedInAfter(Date)`).
  - When to use: to keep SQL out of the use-case layer entirely.
  - How: define the gateway interface in/near the use-case layer; implement it (the humble half, using actual SQL) in the database layer; interactors depend only on the interface, so they stay testable via stubs/test doubles even though they're not humble themselves.
- **Data Mappers** (correct name for what's commonly called an "ORM"): load data into data structures from relational tables.
  - When to use: whenever using Hibernate-style persistence tooling.
  - How: keep data mappers confined to the database layer, forming another Humble Object boundary between gateway interfaces and the actual database.
- **Service Listeners**: Humble Object boundary for inbound/outbound service communication.
  - When to use: whenever the application talks to or is called by external services.
  - How: application loads data into simple data structures and passes them across the boundary; listeners on the input side receive service data and reformat it into simple structures for the application.

## Key Concepts
- **Humble object**: the half of a split that is hard to test, stripped to its barest mechanical essence (e.g., the View).
- **Testable object**: the half of a split holding all logic that can be exercised without the hard-to-test medium (e.g., the Presenter).
- **ViewModel**: a plain data structure of strings, booleans, and enums that the Presenter populates and the View blindly renders.
- **"There is no such thing as an ORM"**: Martin's framing — objects expose only behavior (public methods), while a data structure is public data with no behavior; "ORM" is a misnomer for what should be called a **data mapper**.
- **Testability as an architectural-boundary signal**: wherever a testable/non-testable split occurs, an architectural boundary is likely present nearby.

## Mental Models
- Whenever you find code that's hard to unit test, ask: "what's the minimum mechanical residue I can leave here, and can I move everything else to a sibling class I *can* test?" — that residue is the humble object.
- Treat "is this hard to test?" as a detection heuristic for architectural boundaries, not just a testing concern — Presenter/View, gateway/DB, and listener/service all fell out of this same question.
- Distinguish "testable" from "humble": use-case interactors are not humble (they carry real logic) but they ARE testable, because their dependencies (gateways) are interfaces that can be swapped for stubs.

## Anti-patterns
- **Letting the View contain any decision logic or data formatting** (date formatting, currency formatting, red/black flags, grayed-out buttons): defeats the purpose of the split — that logic becomes untestable again because it's now embedded in the hard-to-test GUI layer.
- **Allowing SQL into the use-case/interactor layer**: removes the gateway boundary and makes interactors dependent on database specifics, destroying their testability.
- **Believing "ORM" objects are true objects with encapsulated behavior**: leads to conflating data structures with objects and misplacing data-mapper code outside the database layer.

## Worked Example
Displaying a monetary value and some UI chrome on screen, via the Presenter/View split:
- The application wants to show a `Currency` object on screen. It hands the `Currency` object to the **Presenter**.
- The Presenter formats it with correct decimal places and currency markers into a string, and — if the value is negative — sets a boolean "show in red" flag. Both go into the **ViewModel**.
- Similarly, every button name, menu item name, radio button/checkbox/text-field label, and every "grayed out" state is precomputed by the Presenter into strings/booleans on the ViewModel. Tables of numbers become tables of pre-formatted strings.
- The **View** then does nothing more than copy each ViewModel field onto its corresponding screen element — no formatting, no decisions. This makes the View humble (hard to test, but with nothing worth testing left in it) and the Presenter fully testable (all formatting/decision logic, no screen dependency).
- The same pattern repeats one layer deeper: a `UserGateway` interface might declare `getLastNamesOfUsersWhoLoggedInAfter(Date)`; the interactor calls this interface (testable via stubs), while the concrete database-layer implementation (humble, using raw SQL or a data mapper/"ORM") does the actual query.

## Key Takeaways
1. Split any hard-to-test behavior into a humble module (mechanical only) and a testable module (all the logic) — this is the general Humble Object pattern.
2. Presenters format everything the View needs (strings, booleans, enums) into a ViewModel so the View has literally nothing to decide.
3. Keep SQL and persistence-framework specifics (including "ORMs"/data mappers) entirely inside the database layer, behind gateway interfaces the use-case layer depends on abstractly.
4. Use the presence of a testable/non-testable split as a signal that an architectural boundary belongs there — Presenter/View, gateway/database, and listener/service are all instances of the same underlying pattern.
5. "ORM" is a misleading name — think of these tools as data mappers confined to the outermost database layer, not as first-class objects living anywhere near business logic.

## Connects To
- **Ch 22 (The Clean Architecture)**: this chapter elaborates the Presenter/View and database-gateway mechanics that Chapter 22's typical scenario (Fig 22.2) already sketched — Presenter, ViewModel, and DataAccessInterface reappear here in depth.
- **Ch 24 (Partial Boundaries)**: Humble Object boundaries are full-fledged boundaries; the next chapter covers cheaper, partial variants when the full cost isn't justified yet.
- **Gerard Meszaros, *xUnit Patterns* (2007)**: original source of the Humble Object pattern.
- **Martin Fowler, *Patterns of Enterprise Application Architecture* (2003)**: cited for gateway pattern terminology.
