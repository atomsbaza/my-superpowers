# Chapter 27: Criticisms of Design Patterns

## Core Idea
Design patterns capture reusable experience, but applied uncritically they can confuse teams, ossify into maintenance burdens, and be superseded by language features — so understanding a pattern's criticisms is part of judging its real return on investment.

## Frameworks Introduced
- **"Experience reuse" as the value of patterns**: A pattern's benefit isn't the code, it's the accumulated wisdom of how a class of problem was solved before.
  - When to use: Frame any pattern decision by asking whether it's transferring real prior experience to your context, not just following a name/checklist.
  - How: Before applying a pattern, weigh both its best practices and its known problems — the chapter argues this critical assessment, done up front, predicts whether the pattern will pay off.
- **Force (as used in pattern literature)**: The criterion developers use to justify a design decision, made up of the target you're aiming for and the current constraints you're working under.
  - When to use: When justifying why a pattern (or any design decision) is the right call for this specific situation.
  - How: Articulate both halves explicitly — what you're trying to achieve, and what limits you — rather than citing the pattern's name alone as justification.

## Key Concepts
- **Pattern confusion**: Many GoF patterns are closely related (similar UML, overlapping intent), which can confuse developers about which one actually applies, and each carries its own pros/cons.
- **Maintenance burden**: A pattern applied today can become a burden tomorrow, because the software industry — and the requirements a pattern was chosen for — keeps changing.
- **Finite patterns vs. infinite requirements**: The chapter argues it is unlikely that a finite catalog of patterns can cleanly cover an unbounded space of real-world requirements.
- **Design as art**: Because software design is treated as an art rather than a science with objective criteria, "correct" pattern usage is inherently judgment-based, not provably optimal.
- **Ideas, not implementations**: Patterns (unlike libraries or frameworks) give you a concept, not code — every engineer may implement the same pattern differently, which can create inconsistency across a team.
- **Over-application in simple/demo code**: Patterns encourage coding to a supertype (abstract class/interface); for a small application with no expected future change, this indirection may not be worth its cost.
- **Composition vs. inheritance shift**: The chapter frames the industry's move from favoring inheritance to favoring composition as a hard mental adjustment — a specific example of erasing old habits being difficult even when the new approach is better.
- **Language subsumption of patterns**: Some GoF patterns are already built into modern languages (e.g., C#'s native Iterator support via `IEnumerable`/`yield`), making a from-scratch implementation of the pattern redundant; the chapter cites Peter Norvig's claim that Lisp/Dylan's language features simplify or eliminate 16 of the 23 GoF patterns.
- **Pattern-to-anti-pattern drift**: Inappropriate use of a pattern can itself become an anti-pattern — the chapter's example is a misused Mediator degenerating into a God Class (covered in Chapter 28).

## Mental Models
- Use the boarding-pass analogy to understand why "a pattern is a proven solution to a problem in a context" is an incomplete definition: rushing home for a forgotten boarding pass is a "solution," but it's not a repeatable, intelligent one — a real pattern must generalize beyond one-off luck, accounting for context (traffic, time available) the way a pattern must account for its applicability conditions.
- Treat "problem / context / solution" as a starting decomposition for evaluating any claimed pattern, but recognize it's necessary, not sufficient — you must also understand intent behind the design to distinguish superficially similar patterns.
- When two patterns look alike in UML, resist picking based on diagram shape alone; the distinguishing factor is almost always intent, not structure.

## Anti-patterns
- **Blind pattern application**: Using a pattern because it's "the way it's done" rather than because the specific problem and context justify it — this is the root cause the chapter ties to patterns curdling into anti-patterns.
- **Over-engineering small/demo applications**: Enforcing supertype abstraction and other pattern discipline on code that will never need to vary increases code size and maintenance cost for no benefit.
- **Reimplementing language-native patterns from scratch**: Manually hand-rolling a GoF pattern (e.g., Iterator) that the language already provides as a built-in feature adds needless ceremony.

## Code Examples
No significant code examples in this chapter.

## Reference Tables
None in this chapter.

## Worked Example
The chapter's central argument is that criticism is a tool for predicting ROI, not a reason to abandon patterns. It walks through roughly ten distinct criticisms — pattern confusion, future maintenance burden, the finite-patterns-vs-infinite-requirements mismatch, design as art without objective criteria, "ideas not implementations" causing team inconsistency, over-application to trivial code, code-size/maintenance-cost inflation in small apps, the difficulty of retiring old habits (inheritance to composition), the fallibility of a developer's judgment about "what varies," and language features subsuming patterns outright (Norvig's Lisp/Dylan observation). It closes its Q&A by contextualizing the book's own scope: it covers the GoF's 23 patterns plus 3 others because fundamentals must come first — you cannot evaluate the need for a newer pattern like Model-View-Presenter without first understanding the MVC it evolved from.

## Key Takeaways
1. A pattern's real cost is only visible when you weigh it against your specific requirements' likely rate of change, not against a generic "best practice" checklist.
2. Coding to a supertype and other GoF discipline are investments that only pay off when variation is actually expected — applying them to fixed, small, or demo-only code is often pure overhead.
3. When a language absorbs a pattern as a first-class feature (e.g., iterators in C#), prefer the native construct over a hand-rolled GoF implementation.
4. Misapplying a pattern outside its intended context is the direct mechanism by which a design pattern becomes an anti-pattern — this is the explicit bridge to Chapter 28.
5. This is a discussion chapter with essentially no code; its arguments (composition-over-inheritance shift, language features displacing patterns) predate C# 7-era tooling but the critical-thinking framework still applies directly to modern C#.

## Connects To
- **Ch 28 (Anti-patterns)**: This chapter's closing point — that misapplied patterns become anti-patterns (e.g., Mediator to God Class) — is the direct setup for the next chapter's dedicated treatment.
- **Ch 26 (MVC)**: Used as the concrete example for why understanding a fundamental pattern first (MVC) is a prerequisite for evaluating derived/newer ones (MVP).
- **Modern software engineering discourse on pattern overuse**: The chapter's Peter Norvig citation and "patterns as evidence of missing language features" argument anticipates later industry debate (post-2018) about whether design patterns are workarounds for weak type systems rather than universal wisdom — still actively discussed regarding functional-language features displacing OOP pattern boilerplate.
