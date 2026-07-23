# Topic 11: TDD Katas and Deliberate Practice

## Core Idea
TDD is a skill, not just a rule set, and skills are built through repeated, deliberate practice outside of production pressure. Coding katas — small, repeatable programming exercises like Uncle Bob's "Bowling Game Kata" — give practitioners a low-stakes, constrained environment to rehearse TDD technique, small-stepping discipline, and refactoring until it becomes second nature.

## Frameworks Introduced
- **Coding Kata**: a repeatable programming exercise used for deliberate practice of TDD
  - When to use: outside of feature/deadline work, as standalone practice sessions (solo or in a group/dojo setting), when a developer or team wants to sharpen red-green-refactor discipline without the risk of production code
  - How: pick a small, well-known problem (e.g., Bowling Game, FizzBuzz, String Calculator), solve it from scratch using strict TDD, and repeat the same kata multiple times — each repetition focusing on tightening a specific skill (smaller steps, faster cycles, cleaner refactors, trying a different implementation strategy such as Fake It vs. Obvious Implementation)

## Key Concepts
- **Deliberate practice**: focused, repetitive rehearsal of a specific skill with the explicit goal of improving performance, rather than just "getting work done"
- **Bowling Game Kata (Uncle Bob)**: a named, widely-used kata example cited in the research as a concrete instance of a coding kata for TDD practice
- **Small stepping**: taking the smallest possible increments between red and green so each step is easy to verify and reason about — the specific discipline katas are used to train
- **Low-stakes, constrained environment**: practicing on a bounded, well-understood toy problem so mistakes and experimentation carry no real cost, unlike production code

## Mental Models
- **Musicians practicing scales / athletes drilling fundamentals**: katas are to TDD what scales are to a musician or drills are to an athlete — repeated practice of the fundamentals, performed away from the "gig" (production code, deadlines), so the skill is already fluent when it matters. (This framing is a reconstruction consistent with the research's "deliberate practice" language, not an explicit analogy present in the source material.)
- **Practice court vs. game day**: a kata is a practice court — you can fail safely, rewind, and retry the same exercise repeatedly to isolate and improve one aspect of the discipline (e.g., step size or refactor timing) without any feature-delivery consequence.
- **Muscle memory for the cycle**: repeating the same kata many times is meant to make the red-green-refactor rhythm automatic, so during real work the mechanics don't compete for attention with the actual design problem.

## Anti-patterns
- **Only ever practicing TDD live on production code under deadline pressure**: never rehearsing the cycle in a low-stakes setting means every attempt to get small steps or clean refactors right happens under time and correctness pressure, which discourages experimentation and slows skill growth.
- **Treating a kata as a one-and-done exercise**: doing a kata once and moving on forfeits the repetition that makes it "deliberate practice" — the value compounds from doing the same exercise multiple times with a specific improvement focus each time.

## Code Examples
(omit — not code-heavy)

## Reference Tables
(omit if none)

## Worked Example
Practicing the Bowling Game Kata: the exercise is to compute a bowling score for a game, given a sequence of rolls, including the scoring quirks for spares and strikes. The constraint of the kata is that you solve it using strict TDD — write one small failing test, make it pass with the least code necessary, refactor, and repeat — rather than designing the scoring algorithm up front.

A practitioner might run this kata repeatedly:
1. First pass: focus purely on getting through red-green-refactor without worrying about elegance — just build the habit of tiny steps and running tests constantly.
2. Second pass: repeat the same problem, this time deliberately using Fake It ('Til You Make It) for early tests and only generalizing once triangulation demands it, to feel out how far a hardcoded shortcut can carry you before it breaks down.
3. Third pass: repeat again, this time timing how quickly you can reach a clean, fully-refactored solution, using the familiarity from prior runs to take smaller, faster, more confident steps.

Because the problem (bowling scoring) is small, well-known, and has no real stakes, the practitioner can afford to "waste" an attempt exploring a bad design, then immediately retry — something that isn't practical against unfamiliar production code with real deadlines.

## Key Takeaways
1. Treat TDD as a trained skill: schedule kata practice the way you'd schedule any deliberate-practice drill, separate from feature work.
2. Reuse the same kata multiple times rather than treating it as solved after one pass — repetition with a changing focus (step size, green-bar pattern, refactor timing) is what builds fluency.
3. Use katas to rehearse specific named techniques (TPP, Fake It, Triangulation, Test List) in isolation before relying on them under real deadline pressure.
4. Keep kata problems small and well-known (e.g., Bowling Game) so the exercise stays low-stakes and repeatable, with the learning goal on process, not on solving a novel problem.
5. Don't let deadline-pressure production coding be the only place TDD discipline gets exercised — it will erode under pressure if it was never practiced without pressure.

## Connects To
- **Topic 2 (Red-Green-Refactor & Canon TDD)**: katas are the practice vehicle for internalizing the red-green-refactor cycle and the small-stepping discipline it depends on.
- **Topic 9 (Transformation Priority Premise)**: TPP and the other named green-bar techniques (Fake It, Obvious Implementation, Triangulation) are exactly the kind of technique-specific skills katas are used to drill.
- **External concept**: Uncle Bob's Bowling Game Kata, the named example cited in the research as a canonical practice kata.
