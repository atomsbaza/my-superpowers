# Chapter 5: Implementing Simple Business Logic

## Core Idea
For subdomains where business logic is genuinely simple, two lightweight patterns — Transaction Script and Active Record — implement it directly and honestly, without paying for abstractions the complexity doesn't warrant; the hard part isn't the logic itself but guaranteeing each operation behaves as an atomic, all-or-nothing transaction.

## Frameworks Introduced
- **Transaction Script**: "Organizes business logic by procedures where each procedure handles a single request from the presentation." (Martin Fowler)
  - When to use: supporting subdomains where business logic resembles simple procedural operations, e.g. ETL (extract-transform-load) pipelines; also as an adapter/anticorruption-layer glue for integrating external or generic subdomains.
  - How: implement each public operation as one straightforward procedural script, optionally with a thin storage-access abstraction (or direct database access). The system's public interface is a collection of business transactions; each transaction is one script acting as its own encapsulation boundary. The only hard requirement is transactional behavior — succeed completely, fail completely, never leave an invalid in-between state.
- **Active Record**: "An object that wraps a row in a database table or view, encapsulates the database access, and adds domain logic on that data." (Martin Fowler)
  - When to use: same class of problems as Transaction Script (simple business logic, at most input validation) but where the data is structured as complex object trees/hierarchies (one-to-many, many-to-many) rather than flat records.
  - How: model each data structure as an "active record" object that bundles the data fields with CRUD data-access methods (create, read, update, delete), typically coupled to an ORM. Business logic (a transaction script) then manipulates these active-record objects instead of touching the database directly, still wrapped in a transaction that must commit or roll back atomically.

## Key Concepts
- **Transactional behavior**: an operation must either fully succeed or fully fail — never leave the system in a partially-applied, inconsistent state.
- **Distributed transaction**: any operation that must atomically coordinate more than one independent party (two databases, a database and a message bus, or even a database and the calling process itself) — inherently hard to make safe.
- **Idempotency**: an operation produces the same end result no matter how many times it is executed; used to make retries after ambiguous failures safe.
- **Optimistic concurrency control**: an update is conditioned on the value read earlier still matching the current stored value, so a stale or duplicate retry becomes a no-op.
- **CRUD**: the four basic data-access operations (create, read, update, delete) that an active record exposes alongside its data.
- **Anemic domain model**: the pejorative name sometimes given to Active Record because it separates data structure from behavior; the author explicitly rejects the "antipattern" framing when the domain is genuinely simple.
- **Encapsulation boundary (per operation)**: in Transaction Script, each public operation/procedure is its own unit of encapsulation, rather than encapsulation living inside domain objects.
- **Be Pragmatic**: named mental model — data consistency guarantees can be deliberately relaxed at scale when the business impact of rare corruption is negligible.

## Mental Models
- **Simplicity is proportional to the subdomain, not a universal virtue** — Transaction Script and Active Record are correct precisely because the underlying business logic is simple; using a heavier pattern (Domain Model) for simple logic introduces "accidental complexity," which is its own kind of harm.
- **Transaction Script is the substrate, not just a beginner pattern** — every business-logic pattern discussed later in the book (including Domain Model) is, underneath, still built on procedures with transactional guarantees; it deserves respect rather than dismissal.
- **"It's Not That Easy!"** (named section) — despite looking trivial, Transaction Script is the pattern most often implemented incorrectly in production; a large share of real debugging work traces back to broken transactional behavior, not to the business logic itself.
- **Be Pragmatic** (named section) — protecting data integrity matters, but at high scale you should explicitly ask whether corrupting one record out of a million is actually a showstopper, weighing that against performance/profitability cost; there are no universal laws, only domain-specific risk tradeoffs, and cutting corners is fine once the risk is evaluated.

## Anti-patterns
- **Multiple sequential DB writes without a wrapping transaction**: if a failure lands between two related writes (e.g., updating `Users` then inserting into `VisitsLog`), the system is left permanently inconsistent — fixed trivially by wrapping both writes in one relational transaction with rollback on error.
- **Implicit distributed transactions across storage mechanisms**: writing to a database and then publishing to a message bus (or any two independent systems) cannot be made atomic with a simple wrapping transaction; a failure between the two steps corrupts state with no easy fix (addressed later via CQRS in Ch. 8 and the outbox pattern in Ch. 9).
- **Ignoring the caller as a third party in the transaction**: even a single-table, single-database update is a distributed transaction if the caller can fail to receive the success/failure result — the caller may retry an already-successful non-idempotent operation (e.g., an increment), silently double-applying it.
- **Using Transaction Script/Active Record for a core subdomain**: both patterns tolerate at most simple validation logic; applying them where business logic is genuinely complex leads to duplicated logic across procedures and, eventually, an unmaintainable "big ball of mud."

## Code Examples
```csharp
public class LogVisit
{
    ...
    public void Execute(Guid userId, long expectedVisits)
    {
        _db.Execute(@"UPDATE Users SET visits=visits+1
                       WHERE user_id=@p1 and visits = @p2",
                       userId, expectedVisits);
    }
}
```
- **What it demonstrates**: fixing an implicit distributed transaction (a caller-retry-safe visit counter) via optimistic concurrency control — the update only applies if the counter still matches the value the caller originally read, so a retried call after an ambiguous failure becomes a safe no-op instead of double-incrementing.

## Reference Tables
| Pattern | When to Use | Limitations |
|---|---|---|
| Transaction Script | Supporting/generic subdomains with simple, procedural logic (e.g. ETL); adapters/anticorruption layers for external integration | Business logic duplicated across procedures as complexity grows, risking inconsistent behavior when copies drift; never suitable for core subdomains |
| Active Record | Same simple-logic subdomains as Transaction Script, but with complex/relational data structures (object trees, one-to-many, many-to-many) | Only tolerates simple logic such as CRUD plus basic validation; separates data from behavior (the "anemic" critique); coupled to an ORM/data-access framework; not suitable for core subdomains |

## Worked Example
The chapter builds its case through the recurring `LogVisit` operation, in three escalating failure modes:
1. **Lack of transactional behavior** — updating `Users.last_visit` and inserting into `VisitsLog` as two unwrapped statements; a crash between them corrupts state. Fixed by wrapping both in `StartTransaction()`/`Commit()`/`Rollback()`.
2. **Distributed transactions** — replacing the `VisitsLog` insert with a message-bus publish after the `Users` update; no simple transaction can span a relational database and a message bus, so this failure mode has no easy fix within this chapter (pointer to CQRS/outbox in later chapters).
3. **Implicit distributed transactions** — a seemingly single-statement counter increment (`visits = visits + 1`) is still a distributed transaction because the *caller* is a third party who must learn of success/failure; if that notification is lost, the caller's retry double-increments. Two remedies are given: (a) make the operation idempotent by having the caller compute and pass the final counter value directly, or (b) use optimistic concurrency control, conditioning the update on the previously-read counter value so a duplicate retry is a no-op.

A second worked example presents `CreateUser` as Active Record: business logic builds a `User` active-record object, sets its fields, and calls `user.Save()`, with the whole operation wrapped in a transaction — showing how Active Record still rides on the Transaction Script pattern underneath, just manipulating richer in-memory objects instead of raw SQL.

The chapter's end-of-chapter exercises revisit a flawed `CreateTicket` procedure (assign least-busy agent, increment their ticket counter, save a new ticket, send an alert) with no overarching transaction, asking readers to spot the same three classes of corruption: agent counter drift, orphaned ticket assignment, and missed notification.

## Key Takeaways
1. Business logic's value depends on being useful, not sophisticated — reach for the simplest pattern that fits the subdomain's actual complexity.
2. Transaction Script organizes logic as one procedure per public operation; its only hard requirement is that each operation is atomic (fully succeeds or fully fails).
3. Active Record is Transaction Script plus CRUD-capable data objects, used when the data model (not the logic) is complex.
4. Any operation visible to a caller — even a single-table update — is implicitly a distributed transaction, because the caller must also learn the outcome; design for retries with idempotency or optimistic concurrency.
5. True distributed transactions across storage mechanisms (DB + message bus) can't be solved with a simple wrapping transaction — they need dedicated patterns (CQRS, outbox) covered later.
6. Never use Transaction Script or Active Record for a core subdomain; their simplicity becomes a liability once logic is genuinely complex, producing duplicated and inconsistent business rules.
7. Be pragmatic about consistency: at scale, explicitly weigh the business cost of rare data corruption against the performance and complexity cost of preventing it — perfect consistency isn't always worth its price.

## Connects To
- **Ch 6**: Tackling Complex Business Logic — introduces the Domain Model pattern as the counterpart for subdomains where logic outgrows Transaction Script/Active Record.
- **Ch 8**: Architectural Patterns — CQRS, referenced here as the way to populate multiple storage mechanisms without a true distributed transaction.
- **Ch 9**: Communication Patterns — the outbox pattern, referenced here as the reliable-publishing fix for the distributed-transaction problem left unresolved in this chapter; also anticorruption layers, mentioned as a use case for Transaction Script.
- **Ch 10**: Design Heuristics — further guidance on matching implementation pattern to subdomain complexity.
- **Ch 11**: Evolving Design Decisions — the migration path from Transaction Script to Active Record to Domain Model as a subdomain's complexity grows over time.
- **Martin Fowler's Patterns of Enterprise Application Architecture**: source of both pattern definitions (Transaction Script, Active Record) quoted verbatim in this chapter.
