# Appendix B: Answers to Exercises

## Core Idea
This appendix is the book's answer key: worked solutions to the numbered exercises scattered throughout every chapter, each one keyed back to the section and page it came from. Its value isn't the transcription of every answer, but the reasoning style it models — apply the chapter's named principle (Orthogonality, Law of Demeter, Domain Languages, Refactoring, requirements analysis) concretely to a small, specific problem.

## Key Concepts
- **Answer-by-principle format**: each answer restates which principle from the main text resolves the exercise, then applies it — the appendix is a worked demonstration, not new content.
- **Orthogonality exercises (1-3)**: judge two Java class signatures, modal vs. modeless dialogs, and procedural vs. object-oriented design for which is more orthogonal.
- **Domain Languages exercises (4-8)**: prototyping a UI with markers and Post-its; designing and implementing a mini-language and its BNF grammar with `yacc`/`bison`.
- **Design by Contract exercises (14-21)**: expressing pre/postconditions and invariants for stacks, queues, and similar structures.
- **Decoupling and the Law of Demeter exercises (24-27)**: line-by-line judgment of whether specific method calls violate the Law of Demeter, and how to fix violations via delegation.
- **Metaprogramming exercise (28)**: judging which of several things (port assignments, syntax highlighting rules, parser state machines, unit test data) belong in code versus in metadata.
- **Programming by Coincidence exercises (31-33)**: spotting hidden assumptions in C and Java snippets that "happen to work" for the wrong reasons.
- **Algorithm Speed exercises (34-37)**: empirically measuring sort routine performance, computing stack usage for a recursive tree-printing routine, and proving that binary chop is O(log n).
- **Refactoring exercises (38-40)**: refactoring a tangled conditional, converting an enumerated-type `Shape` class to subclassing, and abstracting shape out of a `Window` class via delegation.
- **Code That's Easy to Test exercise (41)**: designing a test jig and shell-script regression test for a blender interface, driven by a tiny embedded test language.
- **The Requirements Pit exercise (42)**: distinguishing genuine requirements from disguised architecture or UI decisions, and restating the latter as true requirements.

## Mental Models
- Treat every answer as a demonstration of "which principle applies here," not as a standalone trick — the value transfers only if you can re-derive the reasoning on a new problem, not just memorize the specific fix.
- When judging Law-of-Demeter compliance, use the ownership test: you may call methods on yourself, on parameters passed to you, on objects you create, and on your own component objects — anything else is a violation, however convenient it looks.

## Anti-patterns
- **Treating this appendix as a standalone reference**: every answer is meaningless detached from its originating exercise and section; it is designed to be read alongside the main chapter, not in isolation.

## Code Examples
```java
// Exercise 27 (Law of Demeter, C++/Java mix) — violation and fix
// Violation: processTransaction does not own `who`
who = acct.getOwner();
markWorkflow(who->name(), SET_BALANCE);

// Fix: ask acct directly, since acct IS owned (passed in)
markWorkflow(acct.name(), SET_BALANCE);
```
- **What it demonstrates**: the Law of Demeter fix pattern — replace "reach through an owned object to a third object" with "ask the owned object to do it on your behalf," so `BankAccount` (not the caller) knows where the name is actually stored.

```java
// Exercise 39 (Refactoring) — enumerated type replaced by subclassing
public abstract class Shape {
    private double size;
    public Shape(double size) { this.size = size; }
    public double getSize() { return size; }
}
public class Circle extends Shape {
    public Circle(double size) { super(size); }
    public double area() { return Math.PI * getSize() * getSize() / 4.0; }
}
```
- **What it demonstrates**: the standard refactoring move for a type-tag `switch` statement — replace the enumerated type with subclasses, one per variant, each implementing its own behavior.

## Worked Example
Exercise 42 ("The Requirements Pit") is a compact illustration of the whole appendix's method. Given five candidate requirements, the answer sorts them by genuineness: "The response time must be less than 500 ms" is judged a real requirement (an environmental constraint). "Dialog boxes will have a gray background" is judged *not* a requirement but a disguised default — restated as "the dialog background must be configurable by the end user; as shipped, the color will be gray," and generalized further to "all visual elements must be configurable." "The application will be organized as front-end processes and a back-end server" is judged pure architecture masquerading as a requirement, prompting the need to dig deeper into what the user actually wants. "If a user enters non-numeric characters in a numeric field, the system will beep and reject them" is restated more abstractly as "the system will prevent invalid entries and warn the user." "The application code and data must fit within 256kB" is accepted as a hard requirement. This one exercise demonstrates the appendix's recurring move: don't just answer the question, restate the flawed premise the way the corresponding chapter (here, The Requirements Pit) would.

## Key Takeaways
1. Use the appendix as a self-check: attempt each exercise from its originating chapter first, then compare your reasoning (not just your answer) against the book's.
2. The Law of Demeter test in practice is an ownership question: parameters, self, created objects, and direct components are fair game; anything reached through them is not.
3. Restating a suspect "requirement" as a more abstract, policy-free statement is the single most repeated move across the requirements-related answers.
4. Refactoring answers consistently favor subclassing or delegation over conditional/type-tag logic once more than one variant needs to be supported.

## Connects To
- **Ch 5 (Decoupling and the Law of Demeter)**: Exercises 24-29 are directly worked here.
- **Ch 6 (Refactoring, Code That's Easy to Test, Algorithm Speed)**: Exercises 34-41 are directly worked here.
- **Ch 7 (The Requirements Pit)**: Exercise 42 is directly worked here.
- **Metaprogramming (Ch 5)**: Exercise 28's code-vs-metadata judgment call is the direct application of that chapter's central technique.
