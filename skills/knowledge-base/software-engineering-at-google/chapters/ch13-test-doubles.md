# Chapter 13: Test Doubles

## Core Idea

Test doubles trade realism for control, speed, or determinism. Prefer real implementations when practical, use fakes when a credible lightweight implementation is needed, use stubs narrowly, and reserve interaction testing for state-changing boundaries where behavior cannot otherwise be observed.

## Frameworks Introduced

- **Prefer realism over isolation**: A test that exercises a real dependency often catches more and is less coupled to implementation.
  - When to use: Deciding whether to replace a dependency.
  - How: Compare execution time, determinism, and construction cost; keep the real implementation when the trade-off is acceptable.
- **Fake versus stub versus interaction test**:
  - **Fake**: A working but simplified implementation that preserves meaningful behavior.
  - **Stub**: A controlled answer used to drive a scenario.
  - **Interaction test**: An assertion about calls made to a collaborator.
  - When to use: Choose the least artificial technique that gives reliable, maintainable coverage.
- **Fidelity of fakes**: A fake must be tested against the real implementation or contract.
  - When to use: Databases, services, or complex dependencies replaced in many tests.
  - How: Verify that the fake’s externally visible behavior matches the real system for the supported surface.
- **Avoid overspecification**: Assert only interactions that are meaningful to the contract.
  - When to use: Interaction testing is unavoidable.
  - How: Focus on state-changing calls, avoid call order/count assertions unless they matter, and keep expectations minimal.

## Key Concepts

- **Test double**: Any substitute for a real dependency in a test.
- **Seam**: A place where behavior can be varied without changing the code under test.
- **Fake**: A simplified but functioning implementation.
- **Stub**: A controlled response or behavior.
- **Mock**: A double used to verify expected interactions.
- **Fidelity**: How closely a fake or test represents the real behavior.
- **@DoNotMock**: A signal that an interface should not be mocked casually because realism or a fake is preferred.

## Mental Models

- Isolation is a means, not the goal; confidence in real behavior is the goal.
- Every double creates a second implementation that can drift.
- Interaction tests are tests of the caller’s current implementation, not necessarily its contract.
- A fake is infrastructure and deserves its own tests and owner.

## Anti-patterns

- **Mock everything**: It creates brittle tests and hides integration failures.
- **Unverified fakes**: A fast fake provides false confidence when its behavior diverges.
- **Stubbed implementation detail**: Tests become unclear because readers must reconstruct hidden call sequences.
- **Overspecified interactions**: Harmless refactors fail tests without changing behavior.

## Worked Example

An over-stubbed test can configure several collaborators, prescribe call order, and assert every interaction before checking a small result. The test is difficult to read and fails whenever implementation structure changes. Refactoring toward a real or fake dependency lets the test exercise state and reduces the number of assumptions the test makes.

## Reference Table

| Technique | Best use | Main risk |
|---|---|---|
| Real implementation | High-fidelity behavior | Slow or nondeterministic setup |
| Fake | Reusable lightweight behavior | Fidelity drift |
| Stub | Narrow input/error control | Unclear or brittle scenarios |
| Interaction test | Meaningful state-changing boundary | Implementation coupling |

## Key Takeaways

1. Start with the real implementation.
2. Prefer a tested fake when realism is too costly.
3. Use stubbing narrowly and intentionally.
4. Prefer state tests to interaction tests.
5. Test and own every widely used fake.

## Connects To

- **Chapter 12**: Public state assertions make tests resilient.
- **Chapter 14**: Larger tests recover fidelity lost to doubles.
- **Chapter 20**: Static analysis can enforce restrictions such as no-mock annotations.

