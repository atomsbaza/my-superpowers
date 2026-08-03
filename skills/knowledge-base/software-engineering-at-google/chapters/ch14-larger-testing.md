# Chapter 14: Larger Testing

## Core Idea

Larger tests cover risks that unit tests cannot: integration behavior, configuration, load, deployment, side effects, and emergent interactions. They should be explicit about their system under test, data, action, and verification, while remaining fast and understandable enough to participate in the developer workflow.

## Frameworks Introduced

- **Fidelity**: The test environment must resemble the behavior that matters in production.
  - When to use: Evaluating whether unit coverage leaves a risk gap.
  - How: Identify unfaithful doubles, configuration differences, load effects, and unexpected side effects; add the smallest larger test that addresses the gap.
- **SUT/Data/Action/Verification**:
  - **SUT**: The system under test and its boundary.
  - **Data**: Inputs and state.
  - **Action**: The event or operation being exercised.
  - **Verification**: The observable result and invariant.
  - When to use: Designing any larger test.
  - How: Make each part explicit so the test is reproducible and failures are diagnosable.
- **Hermetic larger tests**: Control dependencies and inputs while retaining meaningful system behavior.
  - When to use: Integration or multi-process tests in CI.
  - How: Use isolated environments, seeded data, controlled dependencies, and deterministic cleanup.
- **Test diversity**: Use functional, browser/device, performance, deployment, exploratory, canary, chaos, and user-evaluation tests according to risk.
  - When to use: Systems with different failure modes.
  - How: Match each test type to a risk rather than treating end-to-end testing as one category.

## Key Concepts

- **Large test**: A test involving multiple components, processes, services, or realistic environments.
- **System Under Test (SUT)**: The bounded system whose behavior is being evaluated.
- **Hermeticity**: Reproducibility through controlled dependencies and inputs.
- **Record/replay**: Capturing real responses and replaying them in a controlled test.
- **Emergent behavior**: Behavior that appears only when components interact.
- **Canary analysis**: Evaluating a change on a limited population before broad rollout.
- **Chaos engineering**: Deliberately testing resilience to failure.

## Mental Models

- Larger tests are risk insurance; choose coverage based on failure cost.
- A test that is too realistic to run cannot provide continuous feedback.
- Reduce the SUT at problem boundaries, but never remove the behavior that creates the risk.
- Test ownership and runtime are part of the test’s design.

## Anti-patterns

- **Hourglass suite**: Many unit and end-to-end tests with little useful middle coverage.
- **Unfaithful environment**: A test passes because it omits the dependency or configuration that fails in production.
- **Unowned large test**: Nobody repairs flakes, data, or infrastructure, so the test becomes ignored.
- **Opaque verification**: A failure says only that “the system failed,” not which invariant broke.

## Worked Example

The Webdriver Torso case illustrates why production-like behavior can expose problems that isolated tests miss. A larger test can run the real boundary, use controlled data, and verify an observable outcome without reproducing the entire production fleet. When a full SUT is too large, record/replay or a reduced boundary can preserve the relevant behavior.

## Reference Table

| Risk | Useful larger test |
|---|---|
| Component interaction | Functional test of interacting binaries |
| Device or browser variation | Browser/device testing |
| Capacity and latency | Performance, load, or stress testing |
| Deployment mistakes | Deployment configuration testing |
| Unknown behavior | Exploratory testing or bug bash |
| Release regression | A/B diff or canary analysis |
| Resilience | Disaster recovery or chaos engineering |

## Key Takeaways

1. Use larger tests for risks units cannot observe.
2. Make SUT, data, action, and verification explicit.
3. Preserve fidelity while controlling nondeterminism.
4. Keep large tests understandable, owned, and integrated with workflow.
5. Match test type to the failure mode.

## Connects To

- **Chapter 11**: Test size is a deliberate fidelity/latency trade-off.
- **Chapter 13**: Larger tests compensate for unfaithful doubles.
- **Chapter 23**: CI schedules presubmit and post-submit larger tests.

