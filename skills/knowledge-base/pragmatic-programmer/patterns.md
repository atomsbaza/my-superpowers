# Patterns

## DRY (Don't Repeat Yourself)
**When to use**: Any time the same piece of knowledge (business rule, format, algorithm, data schema) exists in more than one place.
**How**: Identify which of the four "I"s caused the duplication (imposed by environment, inadvertent, impatient, or interdeveloper) and address it structurally — extract a single authoritative source, generate derived copies rather than hand-maintaining them.
**Trade-offs**: Over-applying DRY to superficially-similar-but-conceptually-different code creates false coupling; DRY is about knowledge, not literal text similarity. (Ch2)

## Orthogonal Design
**When to use**: When designing module/component boundaries.
**How**: Ask "if I change this component, how many others does it affect?" Aim for zero — decouple via clean interfaces so components can be developed, tested, and reasoned about independently.
**Trade-offs**: Requires upfront design discipline; poorly-chosen abstractions can look orthogonal but leak implementation details later. (Ch2)

## Tracer Bullets
**When to use**: Starting a new system or major feature where the end-to-end path is unclear.
**How**: Build a thin, working slice through every layer (UI → logic → data) early, then iteratively thicken it — unlike a prototype, a tracer bullet is meant to survive into the final system.
**Trade-offs**: Requires resisting the urge to make the first pass "production-quality" in every layer at once; the win is fast, real feedback on architecture. (Ch2)

## Reversibility
**When to use**: Any decision involving vendor lock-in, data formats, or architectural commitments.
**How**: Favor abstractions (interfaces, adapters, config-driven choices) that let a decision be undone later without a full rewrite; treat no decision as final.
**Trade-offs**: Excessive abstraction "just in case" has its own cost; reserve for genuinely high-uncertainty or high-switching-cost decisions. (Ch2)

## Design by Contract
**When to use**: Any routine with meaningful preconditions, postconditions, or invariants — especially library/API boundaries.
**How**: Document (and ideally enforce via assertions) what a caller must guarantee before calling, what the routine guarantees after, and what must remain true across calls (class invariants).
**Trade-offs**: Adds verbosity; the payoff is that bugs surface at the actual violation point instead of propagating silently downstream. (Ch4)

## Crash Early / Assertive Programming
**When to use**: Whenever a condition is assumed impossible.
**How**: Use assertions to actively verify "impossible" conditions rather than silently trusting them; let the program crash immediately and loudly rather than continue in a corrupted state.
**Trade-offs**: Requires deciding what's truly a programmer error (crash) vs. a recoverable runtime condition (handle gracefully) — conflating the two is itself an anti-pattern. (Ch4)

## Law of Demeter (Decoupling)
**When to use**: Reviewing method calls that chain through multiple objects (`a.getB().getC().doSomething()`).
**How**: A method should only invoke methods on itself, its parameters, objects it creates, or its direct component objects — not on objects obtained transitively.
**Trade-offs**: Strict adherence can lead to "middle-man" wrapper methods that just forward calls; apply where it genuinely reduces coupling, not mechanically everywhere. (Ch5)

## Metaprogramming / Configuration-Driven Behavior
**When to use**: When business rules or behavior are likely to change independent of code releases.
**How**: Externalize the varying logic into metadata/config (rules tables, DSLs) that the code interprets, instead of hardcoding branches.
**Trade-offs**: Over-engineering simple, stable logic into a metadata-driven system adds indirection cost without a matching payoff. (Ch5)

## Making Temporal Coupling Explicit
**When to use**: Whenever correctness depends on the order or timing of operations.
**How**: Model the sequencing explicitly (finite state machines, explicit workflow steps) rather than relying on implicit "this always happens after that" assumptions in code.
**Trade-offs**: Adds structural overhead for genuinely simple sequences; valuable specifically where hidden ordering bugs are likely. (Ch5)

## Rubber Duck Debugging
**When to use**: Stuck on a bug, especially one that "shouldn't be possible."
**How**: Explain the code and the problem out loud, line by line, to a listener (or an inanimate object) — the act of precise articulation frequently surfaces the flawed assumption.
**Trade-offs**: None significant; cheap and often effective before reaching for heavier debugging tools. (Ch3)

## Algorithm Speed Estimation (O())
**When to use**: Before an implementation is chosen, or when performance problems appear only at scale.
**How**: Estimate how resource usage scales with input size using O() notation; verify empirically once implemented rather than assuming.
**Trade-offs**: Premature optimization for Big-O without profiling real bottlenecks wastes effort; use it to avoid choosing an algorithm that will provably not scale. (Ch6)

## Continuous Refactoring
**When to use**: Whenever working code's internal structure has become awkward, duplicated, or hard to extend.
**How**: Restructure in small, behavior-preserving steps backed by tests, rather than deferring cleanup to a rare "rewrite" project.
**Trade-offs**: Needs a solid test safety net first; without it, refactoring risk becomes indistinguishable from a rewrite's risk. (Ch6)

## Requirements as Investigative Digging (Requirements Pit)
**When to use**: Gathering requirements for a new feature or system.
**How**: Treat stated requirements as a starting point, not the answer — dig with concrete use cases (e.g., Cockburn-style use case templates) to surface the real underlying need, iterating with stakeholders.
**Trade-offs**: More upfront investigative time than accepting a spec at face value; avoids building the wrong thing precisely per a wrong spec (the "Specification Trap"). (Ch7)

## Ubiquitous Automation
**When to use**: Any repeated manual process (build, test, deploy, environment setup).
**How**: Script it fully and run it the same way every time — no manual steps that depend on human memory or discipline.
**Trade-offs**: Upfront scripting investment; pays back immediately in eliminated human error and repeatability. (Ch8)

## Ruthless, Early, Automated Testing
**When to use**: From the start of a project, not as a late-phase gate.
**How**: Write tests against the contracts established via Design by Contract; automate them to run continuously; treat a passing test suite as a necessary (not sufficient) condition for confidence.
**Trade-offs**: Requires code designed to be testable from the outset (small, decoupled units); retrofitting tests onto untestable code is far more expensive. (Ch4, Ch8)
