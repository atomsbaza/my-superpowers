---
name: pragmatic-programmer
description: "Knowledge base from \"The Pragmatic Programmer: From Journeyman to Master\" (1st ed., 1999) by Andrew Hunt and David Thomas. Use when applying DRY, Orthogonality, Tracer Bullets, Design by Contract, Law of Demeter, or other foundational software-craftsmanship principles, or when reviewing code/process against pragmatic-engineering practice."
---

<!-- argument-hint: [topic, framework name, or chapter number] -->

# The Pragmatic Programmer: From Journeyman to Master
**Authors**: Andrew Hunt & David Thomas | **Pages**: ~352 | **Chapters**: 8 + 2 appendices | **Generated**: 2026-07-31

## How to Use This Skill

- **Without arguments** — load core frameworks below for reference
- **With a topic** — ask about `DRY`, `orthogonality`, `tracer bullets`, or another indexed topic; I find and read the relevant chapter
- **With a chapter** — ask for `ch02` or `chapter 5`; I load that specific chapter file
- **Browse** — ask "what chapters do you have?" to see the full index

When you ask about a topic not covered below, I will read the relevant chapter file before answering.

---

## Core Frameworks & Mental Models

**DRY (Don't Repeat Yourself)** — every piece of knowledge must have a single, unambiguous, authoritative representation. Diagnose duplication by its cause (imposed, inadvertent, impatient, interdeveloper) before fixing it — not all duplication looks the same or has the same remedy. (Ch2)

**Orthogonality** — design components so a change in one has no effect on unrelated others. Ask "how many other modules does changing this affect?" — the answer should be as close to zero as possible. (Ch2)

**Tracer Bullets vs. Prototypes** — a Tracer Bullet is a thin, real, end-to-end slice meant to survive and be refined into the final system; a Prototype is deliberately throwaway, built purely to reduce uncertainty about one risky area. Pick based on whether you intend to keep what you build. (Ch2)

**Reversibility** — there are no final decisions. Favor architectures where vendor, platform, and format choices can be undone later without a full rewrite. (Ch2)

**Design by Contract** (from Bertrand Meyer/Eiffel) — every routine has preconditions (what the caller must guarantee), postconditions (what the routine guarantees in return), and invariants (what stays true across calls). Document and, ideally, assert them. (Ch4)

**Crash Early / Dead Programs Tell No Lies** — a program that continues after detecting an impossible condition is more dangerous than one that crashes immediately. Use assertions to actively verify "impossible" conditions rather than silently trusting them — and never give assertions side effects. (Ch4)

**Law of Demeter** — a method should only invoke methods on itself, its own fields, its parameters, or objects it creates — never on objects reached transitively through another object (`a.getB().getC()...`). Reduces coupling. (Ch5)

**Programming by Coincidence** — code that "happens to work" without the author understanding why is fragile; you can't predict when it will break because you never understood why it worked. Prefer to understand deliberately over guessing successfully. (Ch6)

**Broken Window Theory** — visible unaddressed small defects (bad design, wrong decisions, poor code left as "we'll fix it later") signal that nobody cares and accelerate further decay. Fix them immediately, or at minimum flag them explicitly. (Ch1)

**Stone Soup / Boiled Frog** — two complementary project-momentum analogies: Stone Soup (show a small compelling result first, then recruit others' investment and resources) for starting change; Boiled Frog (gradual degradation goes unnoticed until severe) as a warning against passive tolerance of slow decline. (Ch1)

**Knowledge Portfolio** — treat professional knowledge like a financial portfolio: invest regularly, diversify across technologies, manage risk, and periodically review/rebalance. (Ch1)

**Requirements Pit** — requirements gathering is investigative digging with concrete use cases, not a one-time document handoff; treat a stated requirement as a starting point, not the literal answer. Avoid the Specification Trap of assuming upfront exhaustiveness. (Ch7)

**Ubiquitous Automation + Ruthless Testing** — script every repeated process (build/test/deploy) so it never depends on human memory; test early and continuously against explicit contracts rather than as a late separate phase. (Ch4, Ch8)

---

## Chapter Index

| # | Title | Key Frameworks |
|---|-------|----------------|
| [ch01](chapters/ch01-a-pragmatic-philosophy.md) | A Pragmatic Philosophy | Broken Windows, Stone Soup/Boiled Frog, Good-Enough Software, Knowledge Portfolio |
| [ch02](chapters/ch02-a-pragmatic-approach.md) | A Pragmatic Approach | DRY, Orthogonality, Reversibility, Tracer Bullets, Prototypes, Domain Languages, Estimating |
| [ch03](chapters/ch03-the-basic-tools.md) | The Basic Tools | Power of Plain Text, Debugging mindset, Rubber Ducking, Source Code Control |
| [ch04](chapters/ch04-pragmatic-paranoia.md) | Pragmatic Paranoia | Design by Contract, Crash Early, Assertive Programming |
| [ch05](chapters/ch05-bend-or-break.md) | Bend, or Break | Law of Demeter, Metaprogramming, Temporal Coupling, Blackboard systems |
| [ch06](chapters/ch06-while-you-are-coding.md) | While You Are Coding | Programming by Coincidence, Algorithm Speed (O()), Refactoring, Evil Wizards |
| [ch07](chapters/ch07-before-the-project.md) | Before the Project | Requirements Pit, Specification Trap, Circles and Arrows |
| [ch08](chapters/ch08-pragmatic-projects.md) | Pragmatic Projects | Pragmatic Teams, Ubiquitous Automation, Ruthless Testing |
| [Appendix A](chapters/appendix-a-resources.md) | Resources | Professional societies, building a library, bibliography |
| [Appendix B](chapters/appendix-b-answers-to-exercises.md) | Answers to Exercises | Illustrative worked answers to the book's exercises |

## Topic Index

- **Algorithm speed / Big-O** → ch6
- **Assertions / Design by Contract** → ch4
- **Automation** → ch8
- **Broken Windows / software entropy** → ch1
- **Coupling / decoupling** → ch2, ch5
- **Debugging** → ch3
- **Domain languages / DSLs** → ch2
- **DRY** → ch2
- **Estimating** → ch2
- **Knowledge portfolio / career growth** → ch1
- **Law of Demeter** → ch5
- **Metaprogramming** → ch5
- **Orthogonality** → ch2
- **Programming by coincidence** → ch6
- **Prototypes vs. tracer bullets** → ch2
- **Refactoring** → ch6
- **Requirements gathering** → ch7
- **Reversibility** → ch2
- **Rubber duck debugging** → ch3
- **Source code control** → ch3
- **Team practices** → ch8
- **Temporal coupling** → ch5
- **Testing** → ch4, ch8

## Supporting Files

- [glossary.md](glossary.md) — all key terms with definitions
- [patterns.md](patterns.md) — all techniques and design patterns
- [cheatsheet.md](cheatsheet.md) — quick reference tables and decision guides

---

## Scope & Limits

This skill covers the 1st edition (1999) content only — some tooling references (specific editors, version control systems, code generators) are dated; the underlying principles (DRY, Orthogonality, Design by Contract, etc.) remain the durable value and are still widely cited in modern engineering practice. For topics beyond this book, check related skills or ask the agent directly.
