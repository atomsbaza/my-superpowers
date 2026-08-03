# Chapter 12: Unit Testing

## Core Idea

A unit test is valuable when it remains correct and useful while implementation changes. Test public behavior and state, keep tests complete and concise, avoid logic in the test itself, and prefer DAMP clarity over DRY abstraction.

## Frameworks Introduced

- **Strive for unchanging tests**: A refactor that preserves behavior should not require rewriting the test.
  - When to use: Choosing seams, APIs, and assertions.
  - How: Test stable public contracts rather than private structure or call sequences.
- **Test state, not interactions**: Assert the resulting observable state rather than the exact calls made internally.
  - When to use: Most unit tests.
  - How: Set up input, invoke the public API, and inspect returned or persisted state.
- **Test behaviors, not methods**: Organize a test around a meaningful scenario, even when it crosses helper methods.
  - When to use: Naming, grouping, and reviewing tests.
  - How: Name the test after the behavior and structure setup/action/assertion around that behavior.
- **DAMP, not DRY**: Descriptive and meaningful tests may repeat small values or setup to remain readable.
  - When to use: Sharing test code.
  - How: Extract only stable, conceptually meaningful helpers; do not hide the behavior under generic abstractions.

## Key Concepts

- **Public API test**: A test that uses the contract a real caller uses.
- **State testing**: Verifying returned, stored, or externally visible results.
- **Interaction testing**: Verifying calls between collaborators.
- **Brittle test**: A test that fails for harmless implementation changes.
- **Complete test**: A test whose setup contains all information needed to understand the scenario.
- **Concise test**: A test without irrelevant setup or incidental detail.
- **DAMP**: Descriptive And Meaningful Phrases.

## Mental Models

- A test is a second client of the API; it should behave like a legitimate caller.
- Test readability is a maintenance feature, not cosmetic polish.
- A failure message is a debugging interface for the future.
- The test should be simpler than the production code it verifies.

## Anti-patterns

- **Private-method tests**: They lock the implementation and make refactoring expensive.
- **Interaction-heavy unit tests**: They encode call structure rather than behavior.
- **Logic in tests**: Loops and conditionals can reproduce the same bug as production code.
- **Over-DRY tests**: Generic helpers hide the scenario and make failures hard to interpret.
- **Incomplete setup**: Readers must search elsewhere to understand why the assertion matters.

## Worked Example

The transaction API example illustrates a stable test boundary. A test submits a transaction through the public operation, then asserts the resulting account state and error behavior. It does not inspect internal helper calls or the storage implementation. If the transaction algorithm is refactored while the API behavior stays stable, the test remains useful.

## Code Examples

~~~text
test "rejects an overdraft":
    account = Account(balance=10)
    result = account.withdraw(20)
    assert result == insufficient_funds
    assert account.balance == 10
~~~

This reconstructed shape emphasizes behavior, state, complete setup, and a clear failure message.

## Key Takeaways

1. Test through public APIs and stable behavior.
2. Prefer state assertions over implementation interactions.
3. Name tests after behaviors.
4. Keep logic out of tests and failure messages clear.
5. Use DAMP clarity when sharing test code.

## Connects To

- **Chapter 13**: Test doubles often tempt interaction-based tests.
- **Chapter 14**: Unit tests need larger tests to cover system risks.
- **Chapter 23**: Fast unit tests are the first CI feedback layer.

