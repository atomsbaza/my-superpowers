# Chapter 13: Concurrency

## Core Idea
Concurrency decouples *what* gets done from *when* it gets done, improving throughput and structure, but this decoupling makes reasoning about correctness much harder — clean concurrent code demands deliberate discipline, not intuition.

## Frameworks Introduced
- **Single Responsibility Principle applied to concurrency**: concurrency logic is a reason to change in its own right and must be separated from business logic.
  - When to use: any time thread-management code (locks, thread pools, synchronization) would otherwise be mixed into domain/POJO code.
  - How: extract concurrency-aware wrapper classes around thread-ignorant POJOs so concurrency has its own life cycle of design, testing, and tuning.
- **Limit the Scope of Data** (corollary of SRP): restrict how many places shared data can be touched.
  - When to use: whenever a field or object is shared across threads.
  - How: encapsulate the shared data tightly, guard it with as few critical sections (`synchronized` blocks) as possible, so nothing is missed and duplication of guarding logic is avoided.
- **Use Copies of Data** (corollary of SRP): avoid sharing altogether by giving each thread its own copy.
  - When to use: when the cost of extra object creation is smaller than the cost/risk of synchronization.
  - How: copy objects, treat copies as read-only or thread-local, then merge results back in a single thread afterward.
- **Threads Should Be as Independent as Possible** (corollary of SRP): design each thread to live in its own world.
  - When to use: partitioning work across threads/processors, e.g., request-handling code like servlets.
  - How: pass all needed data in as parameters/local variables so a thread never touches another thread's state; only unshared resources (like a DB connection pool) break the isolation.

## Key Concepts
- **Race condition**: a bug where the outcome of concurrent operations depends on unpredictable thread interleaving, e.g., two threads incrementing `lastIdUsed` and getting the same value.
- **Bound resource**: a fixed-size or fixed-count resource (DB connection pool, fixed buffer) shared under concurrency.
- **Mutual exclusion**: guarantee that only one thread accesses a shared resource at a time.
- **Starvation**: a thread is perpetually denied the resources/turns it needs to proceed.
- **Deadlock**: two or more threads each hold a resource the other needs and none can proceed.
- **Livelock**: threads keep actively retrying but continually block each other, making no real progress.
- **Synchronized methods**: Java's `synchronized` keyword creates a lock around a critical section; dependencies between multiple synchronized methods on the same shared object are a common source of subtle bugs.
- **Producer-Consumer**: producers place work on a bound queue, consumers take it off; both signal each other about queue full/empty state.
- **Readers-Writers**: many readers and occasional writers share a resource; balancing throughput against staleness and starvation is the core challenge.
- **Dining Philosophers**: a classic resource-contention model (competing for shared "forks") illustrating deadlock/livelock risk in systems where processes compete for multiple shared resources.
- **Thread-safe collections**: library-provided classes (e.g., `ConcurrentHashMap`) engineered to be safe and performant under concurrent access, generally preferable to hand-rolled locking.

## Mental Models
- Concurrency turns a single "big main loop" program into "many little collaborating computers" — a structural shift, not just a performance tweak.
- A trivial one-line increment (`++lastIdUsed`) can have thousands to millions of possible execution interleavings at the byte-code level; correctness is a probabilistic minefield, not something eyeballed.
- Treat any inexplicable, non-reproducible test failure as a suspected threading bug first, not a "cosmic ray" — the "one-off" almost never really is.
- Concurrency bugs hide: only a tiny fraction of possible execution paths actually fail, so bugs surface rarely and unpredictably until the system is under stress or on an unfamiliar platform.

## Anti-patterns
- **Assuming concurrency always improves performance**: it only helps when there's real wait time to overlap across threads/processors; otherwise it just adds overhead and complexity.
- **Believing containers (Web/EJB) fully manage concurrency for you**: shared state still needs explicit guarding; ignorance of what the container does leads to concurrent-update and deadlock bugs.
- **Embedding concurrency code directly in business logic**: violates SRP, multiplies the places that can fail, and makes both concurrency bugs and business bugs harder to isolate and test.
- **Wide/large synchronized (critical) sections**: naively synchronizing large blocks "to be safe" increases contention and kills performance instead of fixing correctness.
- **Multiple synchronized methods on one shared object without coordinating their locking**: each method may be individually safe, but call sequences across methods can still race — needs client-based, server-based, or adapted-server locking.
- **Trusting single-threaded test passes as proof of correctness**: threaded code that "works fine" under light, single-configuration testing can still harbor race conditions that manifest only under load, different thread counts, or different platforms.
- **Ignoring spurious/rare failures**: writing off an unreproducible failure as a fluke lets faulty concurrent code become a foundation other code is built on.

## Code Examples
```java
public class X {
    private int lastIdUsed;
    public int getNextId() {
        return ++lastIdUsed;
    }
}
```
- **What it demonstrates**: an apparently trivial one-line increment is not atomic; when shared across two threads it can yield a repeated value (both threads get 43) instead of two distinct increments — illustrating how many hidden execution paths exist even in tiny methods.

```java
public synchronized String nextUrlOrNull() {
    if (hasNext()) {
        String url = urlGenerator.next();
        Thread.yield(); // inserted for testing.
        updateHasNext();
        return url;
    }
    return null;
}
```
- **What it demonstrates**: hand-instrumenting code with `Thread.yield()` deliberately perturbs execution ordering during testing to surface latent concurrency bugs without changing production behavior (the yield call itself doesn't cause the bug — it exposes one that already exists).

## Reference Tables
| Principle | Statement |
|---|---|
| Single Responsibility Principle | Keep concurrency-related code separate from other code — it has its own life cycle, its own harder-than-usual failure modes. |
| Limit the Scope of Data | Severely restrict access to any data that may be shared; fewer guarded locations means fewer places to forget a guard. |
| Use Copies of Data | Where feasible, copy data instead of sharing it — avoids synchronization cost and its risks entirely. |
| Threads Should Be as Independent as Possible | Partition data into independent subsets so threads never need to coordinate over shared state. |

## Worked Example
The chapter's clearest illustration of "how hard concurrency really is" is the `X.getNextId()` example. `X` has a single `int lastIdUsed` field, initialized to 42, shared between two threads that both call `getNextId()` (`return ++lastIdUsed;`). Naively one expects the two threads to get 43 and 44 in some order, ending with `lastIdUsed == 44`. But there is a third, "surprising" outcome: both threads read the same stale value and both return 43, leaving `lastIdUsed` at 43 — a lost update. The reason is that `++lastIdUsed` is not one atomic operation at the byte-code level; the JIT-compiled instructions interleave in thousands of possible orders (12,870 paths for `int`, ballooning to 2,704,156 for `long`). Most interleavings produce a correct result, but the ones that don't are exactly the silent, load-dependent failures that make concurrency bugs so elusive — they pass in casual testing and fail unpredictably in production.

## Key Takeaways
1. Apply the Single Responsibility Principle to concurrency: isolate thread-management code from thread-ignorant POJOs so each can be developed, reasoned about, and tested independently.
2. Minimize and tightly encapsulate shared mutable state; prefer copying data over sharing it, and design threads to be as independent as possible.
3. Know your concurrency library (e.g., `java.util.concurrent`'s thread-safe collections, `ReentrantLock`, `Semaphore`, `CountDownLatch`) before hand-rolling synchronization.
4. Study the canonical execution models — Producer-Consumer, Readers-Writers, Dining Philosophers — because most real concurrency problems are variations of these.
5. Keep synchronized/critical sections as small as possible, and be wary of dependencies between multiple synchronized methods on the same shared object.
6. Treat any spurious, non-reproducible failure as a candidate threading bug rather than dismissing it; get non-threaded code fully correct first, then make threaded code pluggable and tunable for varied testing.
7. Actively try to force failures: run with more threads than processors, test on every target platform, and instrument code (by hand or via automated jiggling) to expose rare interleavings before production does.

## Connects To
- **Ch 9 (Unit Tests)**: threaded code testing builds on the same discipline of writing focused, repeatable tests, but concurrency demands additional configurations (thread counts, platforms, jiggling) beyond standard TDD.
- **Ch 10 (Classes)**: the SRP-driven separation of concurrency code from business logic is a direct application of small, single-purpose classes.
- **Ch 3 (Functions)**: keeping synchronized sections small mirrors the general principle of keeping units of code small and focused.
- **Producer-Consumer, Readers-Writers, Dining Philosophers**: the three canonical concurrency execution models the chapter recommends studying as templates for real-world problems.
