# Topic 9: The Transformation Priority Premise

## Core Idea
Robert C. Martin's Transformation Priority Premise (TPP) orders the possible code changes you can make to turn a failing test green, so that you always reach for the simplest, lowest-risk transformation first and only escalate to complexity when the tests genuinely force it.

## Frameworks Introduced
- **Transformation Priority Premise (TPP)**: a prioritized list of code "transformations" — small, mechanical edits that change one piece of code into another (e.g. `null` into a constant) — applied to make the current failing test pass with the least-complex change available.
  - When to use: during the "make it green" step of red-green-refactor, whenever more than one transformation could satisfy the failing test.
  - How: scan the priority list from simplest to most complex; pick the highest-priority (simplest) transformation that actually makes the test pass; only drop to a lower-priority (more complex) transformation when the simpler ones are insufficient for the new test case.

## Key Concepts
- **Transformation**: a small, well-defined edit that changes code from one state to a slightly more capable state (e.g. constant → variable), as opposed to an arbitrary rewrite.
- **Priority ordering**: transformations are ranked from lowest-risk/simplest to highest-risk/most complex; TDD should climb this ladder one rung at a time rather than jumping ahead.
- **Getting "stuck"**: the failure mode TPP is designed to prevent — writing code that is over-fit to the current test (via a transformation more complex than necessary), which then requires a painful rewrite when a new test demands different behavior.

## Mental Models
- "As the tests get more specific, the code gets more generic" — the guiding mantra of TPP: each new, more specific test should pull the implementation toward more general logic, but only as far as that specific test demands.
- Climbing a ladder of complexity one rung at a time, rather than leaping to the top rung (recursion, complex conditionals) before it's earned by the tests.
- TPP as a discipline for *how* to satisfy a test, complementary to (not a replacement for) the outer red-green-refactor cycle covered in Topic 2 — it operates inside the "green" step.

## Anti-patterns
- **Jumping straight to a complex transformation**: reaching for recursion, nested conditionals, or loops when a simpler transformation (e.g. hardcoding a constant, or introducing a variable) would satisfy the current test — leads to code that is prematurely general and to getting "stuck," ultimately forcing a larger rewrite than incremental transformation would have required.
- **Ignoring transformation order entirely**: treating "make the test pass" as license for any implementation, rather than as a search for the minimal viable transformation — undermines the small-steps discipline TDD relies on.

## Code Examples
```python
# Test 1: sum of empty list is 0
def test_empty():
    assert sum_list([]) == 0

# Transformation: null -> constant
def sum_list(items):
    return 0

# Test 2: sum of [5] is 5
def test_single():
    assert sum_list([5]) == 5

# Transformation: constant -> variable (still no branching needed yet)
def sum_list(items):
    return items[0] if items else 0

# Test 3: sum of [1, 2, 3] is 6
def test_multiple():
    assert sum_list([1, 2, 3]) == 6

# Only now, when a single variable can no longer satisfy the test,
# escalate to a loop (a higher-priority-number, more complex transformation)
def sum_list(items):
    total = 0
    for x in items:
        total += x
    return total
```
- **What it demonstrates**: each test only forces the next-simplest transformation — constant, then variable, then loop — instead of writing the general loop-based solution up front.

## Reference Tables
| Priority | Transformation | Example |
|---|---|---|
| 1 (simplest) | `null` → constant | `return None` → `return 0` |
| 2 | constant → constant | `return 0` → `return 1` |
| 3 | constant → variable | `return 0` → `return items[0]` |
| 4 | statement → statements | adding a second line of code |
| 5 | unconditional → `if` | adding a guard/branch when a test demands one path vs another |
| 6 | scalar → array | `x` → `xs[]` |
| 7 | `if` → `while` (loop) | a single conditional check becomes iteration |
| 8 (most complex) | statement → recursion | iterative structure replaced by a recursive call |

*(The research notes this is Robert C. Martin's ordering; treat exact step count/labels as approximate — the core claim the research supports firmly is the simplest-to-most-complex direction, e.g. null→constant and constant→variable before if/loop/recursion.)*

## Worked Example
Implementing a simple "FizzBuzz"-style kata under TPP discipline:
1. Test: `fizzbuzz(1) == "1"` → transformation *null → constant*: `return "1"`.
2. Test: `fizzbuzz(2) == "2"` → transformation *constant → variable*: `return str(n)`.
3. Test: `fizzbuzz(3) == "Fizz"` → forces the first conditional: transformation *unconditional → if*: `if n % 3 == 0: return "Fizz"` else `return str(n)`.
4. Test: `fizzbuzz(5) == "Buzz"` → extends the `if` with another branch (`elif n % 5 == 0`), still no loop needed since each test targets one call.
5. Only if a test required processing a *range* of numbers (e.g. `fizzbuzz_range(1, 15)`) would TPP justify escalating to a loop — introduced no earlier than the tests demand it.

## Key Takeaways
1. When multiple ways exist to make a test pass, choose the transformation lowest on Martin's priority list (simplest/lowest-risk) rather than the most general one.
2. Let the tests, not intuition, force each escalation in complexity — write the loop or recursion only once a test cannot be satisfied without it.
3. Premature complexity is a specific TDD failure mode ("getting stuck") that TPP directly targets by naming and ordering the escalation path.
4. TPP is a micro-level discipline that operates inside the green step of red-green-refactor — it refines *how* you go green, not whether you go red first.
5. The guiding check is the mantra "tests more specific → code more generic": if your code just got more generic than the current test requires, you've skipped priority levels.

## Connects To
- **Topic 2 (Red-Green-Refactor & Canon TDD)**: TPP is a refinement of the "make it pass" step within the canonical red-green-refactor loop, giving concrete guidance on *which* code to write to go green.
- **Topic 11 (TDD Katas & Practice)**: TPP is most often practiced and internalized through katas (e.g. Bowling Game, FizzBuzz), where small, repeatable exercises let developers drill the transformation ordering.
- **Robert C. Martin / Uncle Bob**: originator of TPP, also associated with the Bowling Game Kata and broader craftsmanship practices referenced elsewhere in this research.
