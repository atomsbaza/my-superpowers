# Chapter 19: Critique: Google’s Code Review Tool

## Core Idea

Review tooling should make the human review process clearer, faster, and more integrated—not attempt to replace trust and communication. Critique supports the complete lifecycle from creating a change through review, approval, commit, and historical inspection.

## Frameworks Introduced

- **End-to-end review flow**: Tool support should cover authoring, presubmit analysis, requesting review, understanding/commenting, approval, commit, and history.
  - When to use: Evaluating or designing code-review tooling.
  - How: Remove friction at every stage without obscuring state or responsibility.
- **Tight tool integration**: Build, tests, static analysis, code search, ownership, release, and workspace tools should connect at the review boundary.
  - When to use: A review requires context from several systems.
  - How: Surface links and relevant signals in the review while keeping the core experience focused.
- **Attention set**: Make it explicit whose action is currently needed.
  - When to use: Multi-person reviews with comments, replies, or changed patches.
  - How: Track responsibility and notifications so the change does not disappear in an inbox.
- **Review as change archaeology**: Preserve the evolution and rationale of code.
  - When to use: Debugging, auditing, onboarding, and future refactoring.
  - How: Connect files and diffs to authors, comments, approvals, and committed history.

## Key Concepts

- **Critique**: Google’s internal code-review tool described in the chapter.
- **Precommit review**: Review before a change enters the repository.
- **Snapshot**: The submitted view of a change at a point in time.
- **Attention set**: The people whose response is currently required.
- **Change dashboard**: A view for discovering and tracking review work.
- **Change archaeology**: Historical analysis of how and why code changed.

## Mental Models

- A review tool is a state machine; every stage needs visible state and a next action.
- Notifications are a coordination system and must preserve attention rather than create noise.
- Links beat embedding when another system owns the full context.
- The tool should make the right workflow the path of least resistance.

## Anti-patterns

- **Tool as bottleneck**: Slow uploads, analysis, or UI delay commits.
- **Notification flood**: Important review state is buried among low-value alerts.
- **Disconnected checks**: Reviewers must manually search for build, test, ownership, or release context.
- **Opaque approval state**: Authors cannot tell what remains before commit.

## Worked Example

When an author uploads a new snapshot, the tool runs analyzers and shows results with the diff. Reviewers comment on the current version; after the author responds or uploads a revision, the attention set identifies whose turn it is. Once approvals and checks are complete, the same system records the committed change for later archaeology.

## Reference Table

| Review stage | Tool responsibility |
|---|---|
| Create | Upload snapshot and run checks |
| Request | Find reviewers and notify them |
| Understand | Present readable diff and context |
| Comment | Track discussion and response |
| Approve | Show scores and missing approvals |
| Commit | Validate and submit safely |
| After commit | Preserve history and navigation |

## Key Takeaways

1. Optimize the whole review lifecycle.
2. Make the current owner and next action explicit.
3. Integrate checks and context without making the UI a cluttered portal.
4. Reduce notification noise.
5. Preserve review history as an engineering asset.

## Connects To

- **Chapter 9**: The tool operationalizes review principles.
- **Chapter 17**: Search and history provide review context.
- **Chapter 20**: Static analysis is a core review integration point.

