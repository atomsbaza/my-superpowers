---
name: fowler-refactoring
description: "Knowledge base from 'Refactoring: Improving the Design of Existing Code' by Martin Fowler. Use when evaluating code smells, applying refactoring mechanics, reducing technical debt, or referencing object-oriented design principles."
---

# Refactoring: Improving the Design of Existing Code
**Author**: Martin Fowler | **Pages**: ~337 | **Chapters**: 15 | **Generated**: 2026-07-31

## How to Use This Skill
- **Without arguments** — load core frameworks for reference
- **With a topic** — ask about `Duplicated Code`, `Extract Method`, or another indexed topic
- **With chapter** — ask for `ch03` to see Bad Smells in Code
- **Browse** — ask "what chapters do you have?" to see the full index

---

## Core Frameworks & Mental Models

### The Two Hats
Software development is divided into two mutually exclusive activities: adding function and refactoring.
- **Adding Function**: Add new tests and code. Do not change existing structure.
- **Refactoring**: Change structure without changing observable behavior. Do not add functionality or new tests (unless tests were missing).
**Rule**: Never wear both hats at the same time. Swap frequently, but know which one you are wearing.

### The Rule of Three
- The first time you do something, you just do it.
- The second time you do something similar, you wince at the duplication, but you do the duplicate thing anyway.
- The third time you do something similar, you **refactor**.

### Code Smells
Code smells are surface indicators that usually point to a deeper problem in the system. They are heuristics, not hard rules. When you identify a smell, consult the catalog to find the corresponding refactoring to eliminate it.

### Small Steps
Refactoring is not a rewrite. It is a series of tiny, behavior-preserving transformations. After each transformation, the system is fully functional, and tests pass. If you make a mistake, it's easy to undo because the step was so small.

---

## Chapter Index

| # | Title | Key Frameworks |
|---|-------|----------------|
| [ch01](chapters/ch01-fowler.md) | Refactoring, a First Example | The Refactoring Rhythm |
| [ch02](chapters/ch02-fowler.md) | Principles in Refactoring | The Two Hats, The Rule of Three |
| [ch03](chapters/ch03-fowler.md) | Bad Smells in Code | Smell Identification |
| [ch04](chapters/ch04-fowler.md) | Building Tests | The Testing Rhythm, Self-Testing Code |
| [ch05](chapters/ch05-fowler.md) | Toward a Catalog of Refactorings | Catalog Format |
| [ch06](chapters/ch06-fowler.md) | Composing Methods | Extract Method, Replace Temp with Query |
| [ch07](chapters/ch07-fowler.md) | Moving Features Between Objects | Move Method, Extract Class |
| [ch08](chapters/ch08-fowler.md) | Organizing Data | Replace Data Value with Object, Encapsulate Field |
| [ch09](chapters/ch09-fowler.md) | Simplifying Conditional Expressions | Decompose Conditional, Replace Conditional with Polymorphism |
| [ch10](chapters/ch10-fowler.md) | Making Method Calls Simpler | Rename Method, Preserve Whole Object |
| [ch11](chapters/ch11-fowler.md) | Dealing with Generalization | Pull Up Method, Replace Inheritance with Delegation |
| [ch12](chapters/ch12-fowler.md) | Big Refactorings | Tease Apart Inheritance, Extract Hierarchy |
| [ch13](chapters/ch13-fowler.md) | Refactoring, Reuse, and Reality | Reality of Refactoring |
| [ch14](chapters/ch14-fowler.md) | Refactoring Tools | Automated Refactoring |
| [ch15](chapters/ch15-fowler.md) | Putting It All Together | Continuous Refactoring |

## Topic Index
- **Code Smells** → ch03
- **Duplicated Code** → ch03, ch06, ch11
- **Encapsulate Field** → ch08
- **Extract Class** → ch07
- **Extract Method** → ch06
- **Feature Envy** → ch03, ch07
- **Move Method** → ch07
- **Polymorphism** → ch09
- **Refactoring (Definition)** → ch02
- **Rule of Three** → ch02
- **Testing** → ch04
- **The Two Hats** → ch02

## Supporting Files
- [glossary.md](glossary.md) — all key terms with definitions
- [patterns.md](patterns.md) — all techniques and design patterns
- [cheatsheet.md](cheatsheet.md) — quick reference tables and decision guides\n