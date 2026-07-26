# Chapter 6: Functional Programming

## Core Idea
Variables in functional languages do not vary — and because all race conditions, deadlocks, and concurrent-update problems stem from mutable variables, architects should push as much logic as possible into immutable components and segregate the rest behind disciplined mutation boundaries.

## Frameworks Introduced
- **Functional Programming**: "Functional programming imposes discipline upon assignment," rooted in Alonzo Church's λ-calculus (1936); functional languages have no assignment statement, or only heavily disciplined mutation.
  - When to use: Whenever designing for concurrency/multi-threaded, multi-processor robustness.
  - How: Eliminate or minimize mutable state; where mutation is unavoidable, isolate it behind a disciplined boundary (see Segregation of Mutability).
- **Segregation of Mutability**: Split the application into immutable components (purely functional) and a smaller set of components that allow mutation, protected by transactional memory.
  - When to use: When full immutability isn't practicable due to real storage/processing constraints.
  - How: Push as much processing as possible into the immutable components; drive as much code as possible out of the mutable ones; protect mutable variables with a transaction-/retry-based scheme (e.g., compare-and-swap) analogous to how databases protect records.
- **Event Sourcing**: Store transactions, not state; derive state on demand by replaying transactions (optionally from a periodic snapshot).
  - When to use: When you have enough storage and processing power to avoid mutation entirely for the reasonable lifetime of the application.
  - How: Persist only append-only transaction records (CR, not CRUD); compute current state by summing/applying transactions since the last snapshot; take periodic snapshots (e.g., nightly) as a practical shortcut.

## Key Concepts
- **Immutability**: The λ-calculus's foundational notion — the value of a symbol does not change once set.
- **Mutable variable**: A variable that changes state during execution (e.g., a loop counter); the direct and sole source of race conditions, deadlocks, and concurrent-update bugs per this chapter's argument.
- **Transactional memory**: Treating in-memory variables the way a database treats records on disk, using transaction- or retry-based protection (e.g., Clojure's `atom` + `swap!` using compare-and-swap).
- **Event sourcing**: Storing the full transaction history instead of current state, and deriving state by replay; makes the data store append-only (CR, never U or D), eliminating concurrent-update issues by construction.
- **CRUD vs. CR**: Event-sourced systems only Create and Read — no Update or Delete — because nothing is ever mutated in place.

## Mental Models
- Treat **mutability as the root cause of concurrency bugs** — before reaching for locks, semaphores, or complex synchronization, ask whether the shared state could simply not vary.
- Use the **immutable-core / mutable-shell** model: architects should maximize the immutable core and minimize the necessary mutable shell, since only the shell needs concurrency protection.
- Think of an **event-sourced datastore as your source control system** — nothing is ever deleted or overwritten; the current "state" (working tree) is just a materialized view of the full commit history.

## Anti-patterns
- **Defaulting to mutable shared state for convenience**: Directly creates exposure to race conditions, deadlocks, and concurrent-update bugs that would be structurally impossible with immutability.
- **Ad hoc mutation without a protection scheme**: Mutable variables accessed by multiple threads without transactional memory (locking/retry discipline) are the concrete mechanism by which concurrency bugs occur.
- **Assuming immutability requires infinite resources therefore isn't practicable**: The chapter explicitly rejects this — segregation of mutability and event sourcing make near-full immutability practicable within realistic (not infinite) storage/processing budgets.

## Code Examples
```clojure
;; Prints the squares of the first 25 integers, no mutable variables
(println (take 25 (map (fn [x] (* x x)) (range))))
```
- **What it demonstrates**: Contrast with the equivalent Java `for (int i=0; i<25; i++)` loop — the Clojure version has no mutable loop-control variable at all; `range` lazily produces an infinite list, `map` applies squaring, `take` truncates to 25 elements, and no element is evaluated until accessed.

```clojure
;; Clojure's atom facility: disciplined, safe mutation via compare-and-swap
(def counter (atom 0))   ; initialize counter to 0
(swap! counter inc)      ; safely increment counter
```
- **What it demonstrates**: `swap!` reads the atom's value, computes the new value via the given function (`inc`), then locks, compares, and stores only if unchanged, retrying otherwise — this is the concrete mechanism behind "segregation of mutability" / transactional memory.

## Worked Example
Banking account balances: the naive approach mutates a stored balance on every deposit/withdrawal. The event-sourcing alternative stores only the transactions and computes a balance on demand by summing all transactions for that account "from the beginning of time." This sounds absurd at unbounded scale (unbounded transaction growth, unbounded compute to replay), but is made practicable by (a) modern storage being effectively cheap and abundant, and (b) shortcuts like snapshotting the computed state every midnight, so only same-day transactions need replay at query time. The resulting datastore is append-only (CR, not CRUD) — nothing is ever updated or deleted — which by construction eliminates concurrent-update issues, since there is nothing to concurrently update. Martin notes this is precisely how a source control system already works: full immutable history, with the "current state" just a derived, replayable view.

## Key Takeaways
1. When designing for concurrency, first ask whether shared state needs to be mutable at all — eliminating mutability eliminates the bug class, not just mitigates it.
2. Apply segregation of mutability as the practical compromise: maximize the immutable/functional core, minimize and specially protect the mutable shell.
3. Use transactional-memory-style protection (compare-and-swap, retry) for any mutable state that must be shared across threads — don't rely on ad hoc locking conventions.
4. Consider event sourcing when storage/compute budgets allow — it converts a CRUD data model into an append-only CR model, removing concurrent-update problems structurally.
5. The three paradigms (Ch 3–6) are cumulative disciplines: structured programming disciplines control flow, OO disciplines indirect control transfer (component boundaries), and functional programming disciplines data/assignment — a complete architecture applies all three where relevant.

## Connects To
- **Ch 3**: This chapter is the deep dive on "functional programming imposes discipline upon assignment," and closes the loop on the three-paradigm-to-three-architecture-concerns mapping (function/structured, components/OO, data management/functional).
- **Ch 5**: OO's dependency inversion (structural/component concern) pairs with this chapter's immutability (data concern) — a well-architected system applies both simultaneously.
- **Part III (SOLID / Design Principles)**: Segregation of mutability foreshadows the broader architectural theme of separating volatile/mutable concerns from stable/policy concerns.
