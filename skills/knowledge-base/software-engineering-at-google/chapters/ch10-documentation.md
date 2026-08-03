# Chapter 10: Documentation

## Core Idea

Documentation is executable organizational memory: it reduces the cost of understanding systems over time and scale. Good documentation has one primary purpose, names its audience, lives where it can be maintained, and receives technical, audience, and writing feedback.

## Frameworks Introduced

- **Write for the audience**: The reader’s task and context determine what belongs in the document.
  - When to use: API references, tutorials, design documents, landing pages, and team guides.
  - How: Identify who the reader is, what they need to do, and what prior knowledge can be assumed.
- **WHO, WHAT, WHEN, WHERE, WHY**: Frame a document before explaining HOW.
  - When to use: Any technical document whose scope or status could be ambiguous.
  - How: State audience, purpose, freshness, location/ownership, and intended takeaway early.
- **One document, one job**: Separate conceptual explanation, reference detail, tutorial steps, and design rationale.
  - When to use: Documents becoming long, confusing, or difficult to update.
  - How: Give each document a clear contract and link related documents rather than combining them.
- **Completeness, accuracy, and clarity**: These qualities compete; optimize for the document’s intended job.
  - When to use: Choosing depth and deciding what to omit.
  - How: Sacrifice rare edge cases in conceptual material, but preserve them in reference documentation.

## Key Concepts

- **Reference documentation**: Complete, precise information about an API or system.
- **Tutorial**: A guided path that helps a reader accomplish a task.
- **Conceptual documentation**: Explanation of the ideas and relationships behind a system.
- **Design document**: A record of intent, trade-offs, and decisions.
- **Landing page**: A focused traffic director, not a second encyclopedia.
- **Freshness date**: Ownership and review metadata that makes staleness visible.
- **Audience review**: Evaluation by someone who does not share the author’s assumptions.

## Mental Models

- Documentation quality is measured by the reader’s success, not the writer’s effort.
- A document is like code: it needs ownership, review, versioning, and deprecation.
- The landing page should be a traffic cop; detail belongs behind links.
- Technical writers add the most value at API boundaries where the team’s assumptions are least visible.

## Anti-patterns

- **Wiki as permanent source of truth**: Unowned pages drift and compete.
- **One document serving two audiences**: User and team information become confusing.
- **The bad tutorial**: It starts with unexplained commands, omits purpose, or assumes hidden setup.
- **Stale authority**: A document looks official but no longer works.
- **Implementation leakage**: API documentation forces readers to learn internal decisions they do not need.

## Worked Example

The book contrasts a bad tutorial with a better one. The repair starts by naming the audience and desired outcome, introducing the necessary concepts, showing a minimal successful path, and ending with next steps. The same discipline fixes landing pages: state the page’s purpose and link to focused setup, reference, and conceptual documents.

## Reference Table

| Document type | Optimize for |
|---|---|
| Reference | Completeness and precision |
| Tutorial | A successful first path |
| Conceptual guide | Clarity and mental model |
| Design document | Rationale and trade-offs |
| Landing page | Navigation and scope |

## Key Takeaways

1. Give every document one job and an owner.
2. Name WHO, WHAT, WHEN, WHERE, and WHY before HOW.
3. Review documentation for accuracy, audience clarity, and writing quality.
4. Keep canonical documentation versioned and discoverable.
5. Mark, repair, or retire stale documents.

## Connects To

- **Chapter 3**: Canonical documentation scales knowledge sharing.
- **Chapter 8**: Style guidance benefits from the same ownership and change process.
- **Chapter 15**: Documentation itself needs deprecation.

