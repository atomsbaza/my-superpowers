# Patterns Reference — Clean Code / The Clean Coder

Concrete, reusable techniques extracted from all 32 chapters. Code-level patterns first, then professional-practice patterns.

## Extract Till You Drop
**When to use**: A function mixes levels of abstraction, has internal "sections," or is hard to name in one phrase.
**How**: Keep pulling out well-named sub-functions until every remaining line sits at one level of abstraction below the function's name (the "TO paragraph" test). Order functions top-down by the Stepdown Rule so callers precede callees.
**Trade-offs**: Produces many tiny methods — navigation cost is real but is offset by names carrying meaning; don't stop extracting just because a function "looks small enough."

## Extract Try/Catch Blocks
**When to use**: A function mixes error handling with business logic.
**How**: Pull the `try` body into its own well-named method and the `catch` body into another; the outer function does nothing but delegate. `try` should be the first word of its containing function.
**Trade-offs**: Adds one extra method per error path, but cleanly separates the "happy path" story from failure handling.

## Special Case Pattern (Fowler)
**When to use**: An exception or null check is really encoding a routine business case (e.g., "no expenses recorded"), not a true error.
**How**: Create/configure an object that returns sensible default behavior for the special case, so calling code has no branch at all.
**Trade-offs**: Adds a class per special case; only worth it when the branch recurs at multiple call sites.

## Adapter Pattern for Boundaries
**When to use**: Integrating a third-party library, or a not-yet-defined subsystem/API from another team.
**How**: Define the interface you wish you had, in your domain vocabulary. Code and test against it with a fake. Once the real API exists (or is understood via learning tests), write an Adapter class that translates calls to it. Wrap broad interfaces (e.g. `Map`) inside a narrow application-specific class so only one place knows the vendor's shape.
**Trade-offs**: Extra indirection layer, but isolates the whole codebase from vendor churn and makes the dependency swappable/mockable.

## Learning Tests
**When to use**: Adopting any new third-party library or framework.
**How**: Write small tests that call the library exactly as production code will, iterating until you understand its actual behavior. Keep them permanently in the suite as regression checks against future version upgrades.
**Trade-offs**: Upfront time cost, but it's time you'd spend learning anyway, and it converts tribal knowledge into an executable, upgrade-safe document.

## Dependency Injection / Inversion of Control
**When to use**: A class depends on a volatile, external, or hard-to-test concrete implementation.
**How**: Extract an interface for the needed capability, have the concrete class implement it, and inject the interface via constructor (or a DI container/`main`) rather than instantiating it internally. Never mix object construction with object use in the same method (no lazy-init getters).
**Trade-offs**: Requires a composition root (`main`, factory, or IoC container); pays off in testability and the ability to swap implementations per environment.

## SRP / OCP / DIP for Class Design
**When to use**: A class has grown multiple unrelated reasons to change, or is expected to grow new behavioral variants over time.
**How**: SRP — split by "reason to change" until each class is describable in ~25 words without and/or/but. OCP — put an abstract operation on a base type and add new variants as new subclasses (never edit existing, tested ones). DIP — depend on abstractions, inject concretions.
**Trade-offs**: More, smaller classes to navigate; in exchange, each change touches less untested code and comprehension load per task drops.

## Kent Beck's Four Rules of Simple Design
**When to use**: Continuously, as the refactor checklist after any test goes green.
**How**: In strict priority order — (1) passes all tests, (2) no duplication, (3) expresses programmer intent, (4) minimizes classes/methods. Use TEMPLATE METHOD to remove duplicated algorithm skeletons across near-identical methods.
**Trade-offs**: Rule 4 must stay last — chasing "fewer entities" before duplication/expressiveness produces artificially collapsed, unclear code.

## Law of Demeter / Avoid Train Wrecks
**When to use**: Code chains multiple method calls through an object graph (`a.getB().getC().doX()`).
**How**: A method should only call methods on itself, its arguments, objects it creates, or its own instance fields — not on objects returned by those calls. Replace the chain with a single "tell, don't ask" delegating method on the object that owns the data.
**Trade-offs**: Only a true violation when the chained things are objects (not plain data structures); over-applying it to DTOs is pointless.

## The Args-Class Incremental Refactoring Approach
**When to use**: A rough draft has accumulated parallel type-specific collections and repeated instanceof/type-case logic.
**How**: (1) Get it working messily first. (2) When a new requirement would multiply an existing pattern (a third parallel map, a growing switch), stop and refactor. (3) Introduce a polymorphic type one tiny, test-verified step at a time — add an inert class, migrate one call site, push behavior down field-by-field, delete dead code. (4) Only resume features once structure is sound again.
**Trade-offs**: Feels slow in the moment (dozens of micro-steps); each step is individually safe, and the alternative (a big-bang rewrite) risks never reaching a working state again.

## Successive Refinement ("Make It Work, Then Make It Right")
**When to use**: Any nontrivial module, especially with growing/unclear requirements, or inherited legacy code you don't yet trust.
**How**: For new code — get an end-to-end version working however ugly, then refactor in small test-protected steps. For legacy code — first raise test coverage (use a coverage tool) and fix bugs it exposes to build trust, only then restructure names/classes.
**Trade-offs**: Resist the urge to "clean as you go" during the first pass — mixing correctness work and design work in one step makes both harder to verify.

## Smells & Heuristics Catalog (selected)
**When to use**: As a standing code-review checklist (own file/PR pass), or to look up a specific suspected smell by ID.
**How**: Key entries to check every review — G5 Duplication (highest priority), G23 Prefer Polymorphism to Switch/If-Else, G28 Encapsulate Conditionals, G34 Functions Descend Only One Level of Abstraction, G36 Avoid Transitive Navigation, F1/F3 Too Many Arguments / Flag Arguments, N1/N7 Descriptive Names / Names Describe Side-Effects, T2 Use a Coverage Tool.
**Trade-offs**: Not a mechanical checklist to apply blindly — it externalizes a trained "code-sense"; judgment still decides which entries actually apply.

## Boy Scout Rule
**When to use**: Every time you touch a file, on any codebase (even ones written by experts, even framework code).
**How**: Make one small opportunistic improvement per check-in — rename, extract a method, remove a duplication, encapsulate a conditional — trusting the test suite to catch regressions.
**Trade-offs**: Small diffs mixed with feature work can complicate review; keep cleanup commits separable where the team's review norms require it.

## Test Automation Pyramid (Mike Cohn)
**When to use**: Designing a team's overall test strategy, not just one suite.
**How**: Layer coverage bottom-up — unit tests (largest volume, fastest, ~90%+ coverage, run every build, written by programmers) → component tests (business rules per component, mocked collaborators, QA/business-authored) → integration tests (plumbing/wiring between components, run periodically) → system tests (whole-system construction/throughput, infrequent) → manual exploratory tests (unscripted, smallest volume, aimed at discovery not coverage).
**Trade-offs**: An inverted pyramid (heavy manual/GUI testing, thin unit base) is slow and expensive; each layer answers a different question and none substitutes for another.

## Acceptance Tests as the Definition of "Done"
**When to use**: Before implementation starts on any requirement/story.
**How**: Business (happy path) and QA (unhappy path, boundaries) jointly write executable given/when/then scenarios against a stable API layer (not the GUI). "Done" means all such tests pass — nothing else counts. Negotiate a test with its author if it turns out wrong or unachievable rather than implementing to a known-bad spec.
**Trade-offs**: Requires upfront collaboration time between business/QA/dev; the payoff is that ambiguity in prose requirements surfaces before code is written, not after production incidents.

## PERT Estimation (Trivariate Analysis)
**When to use**: Any estimate you need to communicate honestly, especially ones that will be combined into a project-level forecast.
**How**: For each task gather Optimistic (O, <1% likely), Nominal (N, most likely), Pessimistic (P, <1% likely) durations. Compute µ = (O + 4N + P)/6 and σ = (P − O)/6. For a sequence, sum the µ's and combine σ's via root-sum-of-squares: σ_total = √(Σσ²).
**Trade-offs**: More overhead than a single guess; in return it prevents business from mistaking a nominal number for a promise, and reveals that sequences of uncertain tasks compound to longer, less certain totals than naive summation suggests.

## Wideband Delphi (Planning Poker / Flying Fingers / Affinity Estimation)
**When to use**: Generating team-consensus estimates instead of one person's solo guess.
**How**: Discuss the task; everyone simultaneously reveals an estimate (fingers or numbered cards); repeat discussion/reveal until convergence. Affinity variant: silently sort task cards by relative size, then draw bucket lines.
**Trade-offs**: Takes longer than asking one person, but surfaces risks a solo estimator misses and converges faster than Boehm's original heavyweight Delphi process.

## Time Boxing / Pomodoro
**When to use**: Whenever deep, uninterrupted focus is needed, or you want to measure how much of a day is genuinely productive.
**How**: Set a 25-minute timer; defer all interruptions to after it rings ("can I get back to you in 25 minutes?"); take a short break; every fourth interval take a longer break.
**Trade-offs**: Requires the discretion/authority to defer requests; some roles (support, on-call) can't fully protect the window.

## Commitment Language ("I will X by Y")
**When to use**: Any time you're asked for a status, estimate, or promise.
**How**: Replace hedging ("need to," "hope," "let's," "I'll try") with a concrete, self-owned, time-bound statement said to a real person. If the outcome depends on someone else, commit to the controllable actions that advance it, not the outcome itself. Raise a flag the moment you suspect you'll miss it.
**Trade-offs**: Exposes you socially when you fail — that exposure is the point; it's what makes the promise mean something.

## Saying No / Adversarial Negotiation
**When to use**: A deadline or scope request conflicts with what you know to be technically achievable.
**How**: State the fact plainly ("that's a two-week job"), let the other side push back with their own facts, negotiate toward a reduced-scope or renegotiated deliverable. Never answer "I'll try" as a cop-out for "maybe."
**Trade-offs**: Feels confrontational in the moment; the alternative (silent compliance or passive-aggressive documentation) produces worse outcomes and erodes trust further downstream.

## Kata / Coding Dojo Practice
**When to use**: Ongoing, on your own time, to keep TDD rhythm, hotkeys, and standard problem/solution pairs reflexive.
**How**: Pick a known exercise (Bowling Game, Prime Factors, Word Wrap); repeat it solo (kata), in pairs alternating test/implementation (wasa/ping-pong), or as a rotating group (randori) until execution is automatic.
**Trade-offs**: Unpaid, discipline-dependent time investment; the payoff is that real production work under pressure draws on trained reflexes instead of first-time problem solving.

## Focus-Manna / Meeting Discipline
**When to use**: Daily planning of when to do deep work versus administrative/low-focus work.
**How**: Treat focus as a decaying, rechargeable resource — spend it on coding when high, decline or exit meetings without a clear agenda/necessity, recharge via sleep and de-focusing breaks (not more caffeine than moderate amounts).
**Trade-offs**: Declining meetings can read as uncooperative in meeting-heavy cultures; the professional case is that unfocused attendance costs more than the awkwardness of opting out.

## Rule of Holes / Recognizing Messes
**When to use**: Mid-implementation, when a design choice starts feeling like it's fighting you.
**How**: When you realize you're in a blind alley, stop digging and back out immediately (Rule of Holes). For slower-building messes (marshes/swamps), watch for the inflection point where reversing is still cheap — the way forward always looks shorter than it is.
**Trade-offs**: Backing out has a real, visible cost (sunk work); the alternative — pushing forward through a recognized mess — is a slower, hidden, and ultimately larger cost.
