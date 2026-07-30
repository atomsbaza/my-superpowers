---
name: ousterhout-software-design
description: "Knowledge base from 'A Philosophy of Software Design' by John Ousterhout. Use when making architectural decisions, designing deep modules, or reviewing code for complexity."
---

# A Philosophy of Software Design
**Author**: John Ousterhout | **Pages**: ~188 | **Chapters**: 21 | **Generated**: 2026-07-31

## How to Use This Skill
- **Without arguments** — load core frameworks for reference
- **With a topic** — ask about `Information Hiding`, `Deep Modules`, or `Comments`; I find and read the relevant chapter
- **With chapter** — ask for `ch04` to dive into Deep Modules

---

## Core Frameworks & Mental Models

### Tactical vs Strategic Programming
- **Tactical**: Focused entirely on getting the next feature to work as quickly as possible. Leads to hacks, technical debt, and eventual system stagnation.
- **Strategic**: Focused on producing a great design. Writing working code is secondary to ensuring the system's design makes future modifications easy. (Requires ~10-20% upfront investment).

### Deep vs Shallow Modules
- **Deep Modules**: Provide powerful, complex functionality but expose a very simple, small interface to the caller (e.g., Unix file I/O). These are the building blocks of a healthy system.
- **Shallow Modules**: Expose an interface that is almost as complex as the implementation itself (e.g., pass-through methods). They fail to hide complexity.

### Information Hiding
Modules should encapsulate specific design decisions (like a data format, a network protocol, or an algorithm). If a design decision changes, only that single module should need to change. If the knowledge leaks into other modules, you suffer from **Change Amplification**.

### Define Errors Out of Existence
Exception handling is a major source of complexity. Instead of throwing exceptions for edge cases, change the semantics of the operation so the edge case becomes normal behavior (e.g., deleting a key that isn't there should just return successfully, not throw).

### Comment-Driven Design
Write the interface comments for a module *before* writing the implementation. If the comment is hard to write, it means the interface is too complex.

---

## Chapter Index

| # | Title | Key Frameworks |
|---|-------|----------------|
| [ch01](chapters/ch01-ousterhout.md) | Introduction | Complexity |
| [ch02](chapters/ch02-ousterhout.md) | The Nature of Complexity | Change Amplification, Cognitive Load |
| [ch03](chapters/ch03-ousterhout.md) | Working Code Isn't Enough | Tactical vs Strategic Programming |
| [ch04](chapters/ch04-ousterhout.md) | Modules Should Be Deep | Deep vs Shallow Modules |
| [ch05](chapters/ch05-ousterhout.md) | Information Hiding (and Leakage) | Information Hiding, Temporal Decomposition |
| [ch06](chapters/ch06-ousterhout.md) | General-Purpose Modules are Deeper | Somewhat General-Purpose |
| [ch07](chapters/ch07-ousterhout.md) | Different Layer, Different Abstraction | Pass-through Methods |
| [ch08](chapters/ch08-ousterhout.md) | Pull Complexity Downwards | Pulling Complexity Down |
| [ch09](chapters/ch09-ousterhout.md) | Better Together Or Better Apart? | Cohesion |
| [ch10](chapters/ch10-ousterhout.md) | Define Errors Out Of Existence | Error Masking |
| [ch11](chapters/ch11-ousterhout.md) | Design it Twice | Design Iteration |
| [ch12](chapters/ch12-ousterhout.md) | Why Write Comments? | The Four Excuses |
| [ch13](chapters/ch13-ousterhout.md) | Comments Should Describe Things that Aren't Obvious | Interface vs Implementation Comments |
| [ch14](chapters/ch14-ousterhout.md) | Choosing Names | Precision |
| [ch15](chapters/ch15-ousterhout.md) | Write The Comments First | Comment-Driven Design |
| [ch16](chapters/ch16-ousterhout.md) | Modifying Existing Code | Strategic Modification |
| [ch17](chapters/ch17-ousterhout.md) | Consistency | Conventions |
| [ch18](chapters/ch18-ousterhout.md) | Code Should be Obvious | Obscurity |
| [ch19](chapters/ch19-ousterhout.md) | Software Trends | Agile, TDD critique |
| [ch20](chapters/ch20-ousterhout.md) | Designing for Performance | Measurement |
| [ch21](chapters/ch21-ousterhout.md) | Conclusion | |

## Topic Index
- **Agile** → ch19
- **Change Amplification** → ch02
- **Cognitive Load** → ch02
- **Comments** → ch12, ch13, ch15
- **Deep Modules** → ch04
- **Errors/Exceptions** → ch10
- **Information Hiding** → ch05
- **Names** → ch14
- **Strategic Programming** → ch03
- **TDD** → ch19

## Supporting Files
- [glossary.md](glossary.md) — all key terms with definitions
- [patterns.md](patterns.md) — all techniques and design patterns
- [cheatsheet.md](cheatsheet.md) — quick reference tables and decision guides\n