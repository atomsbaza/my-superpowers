# Topic 2: The Red-Green-Refactor Cycle and Canon TDD

## Core Idea
TDD is a fine-grained, iterative discipline — write a failing test, write the minimum code to pass it, then clean up — and Kent Beck's "Canon TDD" adds two supporting techniques (a running Test List and the "Green Bar Patterns") that tell you *which* test to write next and *how* to make it pass without over-committing to a design too early.

## Frameworks Introduced
- **Red-Green-Refactor Cycle**: The six steps, per the research's Study Guide: (1) Create a Test — based on a specific requirement, write a test before any production code exists; (2) Run Tests (Red) — execute the suite; the new test must fail, confirming it is valid and not already satisfied; (3) Write Code — implement the minimum amount of code necessary to make the test pass; (4) Run Tests (Green) — execute the suite again; if it passes, the requirement is met; (5) Refactor — clean the code for efficiency and style without changing behavior, so that "as the tests get more specific, the code becomes more generic"; (6) Repeat — move to the next requirement or refinement.
  - When to use: For every unit of behavior you add, not just once per feature — the research describes the original Beck style as "line-by-line," sometimes one line of failing test paired with one line of production code.
  - How: Never skip the Red step — a test that passes immediately is either testing nothing new or already satisfied, and either way it hasn't proven anything. Write only enough code to flip it to Green, then use the Refactor step (not the Green step) as the place to improve design, since the passing suite is your safety net for that change.

- **Canon TDD / Test List Technique**: Kent Beck's discipline of starting development by writing out a list of the test scenarios and variants you want to cover, then picking exactly one item you're confident you can implement quickly and turning it into a failing test. New scenarios, edge cases, or refactoring ideas that occur to you mid-cycle get appended to the list rather than chased immediately.
  - When to use: At the start of any TDD session, before writing the first test, and continuously throughout as new cases surface.
  - How: Brainstorm test names/scenarios as plain-language bullets (not code) covering the happy path, edge cases, and error conditions. Pick the simplest or most informative item first. Resist the urge to jump to a newly-discovered case mid-cycle — write it down and finish the current red-green-refactor loop first. This keeps each cycle short and keeps you from losing your place.

- **Green Bar Patterns** (Fake It, Obvious Implementation, Triangulation): Kent Beck's three strategies for the "Write Code" step — three different ways to get from Red to Green depending on how confident you are in the correct implementation.
  - When to use: Choose per-test based on your certainty: Obvious Implementation when you know the real logic and it's simple; Fake It when you want a fast green bar and aren't ready to commit to real logic; Triangulation when you don't yet trust what the general abstraction should be.
  - How: **Fake It** — return a hardcoded constant that satisfies the current test, then gradually replace constants with real variables and logic as more tests arrive. **Obvious Implementation** — skip faking it and type the real code directly when the solution is simple and known. **Triangulation** — hold off on generalizing until at least two specific tests both demand the same generalized solution; let the second test force the abstraction rather than guessing it from one example.

## Key Concepts
- **Red**: The state where the newly written test fails, proving it actually exercises new, unmet behavior.
- **Green**: The state where all tests pass, including the newly added one, confirming the requirement is satisfied.
- **Refactor**: Restructuring code to improve its internal quality without changing observable behavior, done only while the suite is Green.
- **Test List / To-Do List**: A running backlog of test scenarios and variants, maintained alongside the code so ideas aren't lost or chased prematurely.
- **Fake It ('Til You Make It)**: Returning a hardcoded/constant value to pass a test quickly, deferring real logic to later iterations.
- **Obvious Implementation**: Writing the real, correct implementation directly because it's simple and already known.
- **Triangulation**: Generalizing code into a real algorithm only once two or more specific tests jointly demand it.
- **Transformation Priority Premise (TPP)**: A related discipline (Uncle Bob) for choosing the *simplest* code transformation (e.g., constant → variable) before reaching for more complex ones (e.g., conditionals, loops, recursion) when moving from Red to Green — introduced here because it shares the "tests get more specific, code gets more generic" mantra with this cycle, and is developed fully in Topic 9.

## Mental Models
- "As the tests get more specific, the code gets more generic" — each new test should push the implementation toward greater generality, not toward a pile of special cases.
- The Test List is a pressure valve: it lets you stay laser-focused on one red-green-refactor cycle at a time by writing down (not acting on) every new idea that surfaces mid-flow.
- Fake It is a safety net, not a shortcut you keep forever — the hardcoded constant exists to get you to Green fast, with the explicit expectation that later tests will force it toward real logic.
- Triangulation treats a single passing test as weak evidence for a general rule; two independent tests that both require the same generalization are treated as much stronger evidence.

## Anti-patterns
- **Writing more production code than the current failing test demands**: This front-loads speculative design before a test has justified it, working against TPP's preference for the smallest transformation and defeating the incremental safety of the cycle.
- **Skipping the Red step / not confirming the test fails first**: A test that was never watched to fail can't be trusted — it may be testing nothing, be miswired, or be trivially satisfied by pre-existing code, silently voiding the whole cycle's value.
- **Generalizing from a single test (skipping Triangulation when uncertain)**: Committing to an abstraction based on one example risks guessing wrong and having to unwind it; Triangulation's two-test rule exists specifically to guard against this.
- **Refactoring while Red**: Changing code structure before the suite is Green removes your only safety net for that change — refactor only has meaning as a distinct, protected step after Green.
- **Never redeeming a "Fake It" constant**: Leaving a hardcoded return value in place instead of evolving it once more tests arrive turns a deliberate stepping-stone into a hidden bug.

## Code Examples
```python
# Test List (kept as comments/notes, not executed):
# - sum of empty list is 0
# - sum of single-item list is that item
# - sum of multi-item list adds correctly

# Cycle 1: "sum of empty list is 0"
def test_sum_of_empty_list_is_zero():
    assert total([]) == 0

# Fake It: minimum code to go Green
def total(numbers):
    return 0

# Cycle 2: "sum of single-item list is that item"
def test_sum_of_single_item_list():
    assert total([5]) == 5

# Fake It no longer works alone; still resist generalizing from one case.
def total(numbers):
    if not numbers:
        return 0
    return numbers[0]

# Cycle 3: "sum of multi-item list adds correctly"
def test_sum_of_multi_item_list():
    assert total([2, 3, 4]) == 9

# Triangulation: two non-trivial tests now demand real generalization.
def total(numbers):
    result = 0
    for n in numbers:
        result += n
    return result
```
- **What it demonstrates**: A Test List driving cycle order, Fake It supplying quick green bars for early cases, and Triangulation forcing the jump to a genuinely general `total()` only once two multi-value tests require it.

## Reference Tables
| Green Bar Pattern | When to use | Risk if misused |
| :--- | :--- | :--- |
| Fake It | You want a fast green bar and aren't yet sure of the real logic | Left un-evolved, the hardcoded constant becomes a silent, permanent bug |
| Obvious Implementation | The correct logic is simple and already known with confidence | Overconfidence on non-trivial logic skips useful test-driven feedback and can introduce untested bugs |
| Triangulation | You're unsure of the correct abstraction and want tests to force it | Used unnecessarily on truly obvious cases, it slows progress with redundant tests |

## Worked Example
Start a session on a `total()` function by writing a Test List: "empty list → 0", "single item → that item", "multiple items → sum". Pick the first item: write `test_sum_of_empty_list_is_zero`, run it (Red — `total` doesn't exist yet), then implement the minimum via Fake It (`return 0`), run again (Green), and refactor if needed (nothing to clean up yet). Repeat: pick "single item → that item" from the list, write the test, watch it fail (Red), and since the real logic (`numbers[0]`) is just as simple as faking it, use Obvious Implementation directly, reaching Green. For "multiple items → sum," write the test, watch it fail, and now — with two tests (single-item and multi-item) both implying summation — apply Triangulation: replace the special-cased logic with a genuine loop that generalizes to any list length. After each Green, pause for Refactor (e.g., renaming variables, removing duplication) before returning to the Test List for the next item.

## Key Takeaways
1. The six-step cycle (Create Test, Red, Write Code, Green, Refactor, Repeat) is the mechanical backbone of TDD — skipping the Red confirmation or the dedicated Refactor step undermines its guarantees.
2. Maintain a Test List so you always know the next small step and never lose a new idea mid-cycle — append, don't chase.
3. Choose the Green Bar Pattern by your confidence level: Obvious Implementation when certain, Fake It when you want speed, Triangulation when you're unsure of the abstraction.
4. Fake It is intentionally temporary — plan to redeem the hardcoded value as soon as a subsequent test makes it insufficient.
5. Triangulation's two-test threshold exists to prevent premature generalization from a single example.
6. "As the tests get more specific, the code gets more generic" is the shared mantra linking this cycle to the Transformation Priority Premise (Topic 9).
7. The research notes this technique comes from Kent Beck's "Canon TDD" framing specifically — treat it as one authoritative articulation of practice, not the sole possible interpretation of TDD.

## Connects To
- **Topic 9 (Transformation Priority Premise)**: TPP extends this cycle's "Write Code" step with a prioritized ladder of transformations (e.g., constant → variable before introducing conditionals or loops), sharing the same "tests get more specific, code gets more generic" mantra.
- **Topic 11 (TDD Katas & Practice)**: Katas such as the Bowling Game Kata are the deliberate-practice vehicle for internalizing the Red-Green-Refactor cycle, Test List discipline, and Green Bar Patterns in a low-stakes setting.
- **Topic 3 (Classicist vs Mockist Schools)**: Both schools run the same red-green-refactor mechanics; they differ in what counts as a "unit" and how isolated the SUT is, not in the cycle itself.
- **Topic 12 (The "Is TDD Dead?" Debate)**: Critiques of TDD dogmatism (e.g., over-testing, four lines of test per line of code) target rigid application of this exact cycle, not its existence.
- **External concept — YAGNI**: Fake It and Triangulation both operationalize YAGNI at the code level — don't build general logic until a test actually demands it.
