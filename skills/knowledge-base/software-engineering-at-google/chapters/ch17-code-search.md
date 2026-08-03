# Chapter 17: Code Search

## Core Idea

At organizational scale, code search is a primary developer tool for understanding a codebase, not merely a faster grep. Trust, completeness, low latency, ranking, history, and integration with documentation and other tools determine whether engineers use it as a question-and-answer system.

## Frameworks Introduced

- **Where, what, how, why, who, and when**: Search should help developers locate code, understand its behavior, navigate relationships, learn rationale, identify owners, and inspect history.
  - When to use: Designing search features or diagnosing why developers cannot understand code.
  - How: Support discovery, browsing, cross-references, ownership, and change history in one low-friction experience.
- **Zero-setup global view**: A developer should be able to inspect the organization’s code without configuring a local workspace first.
  - When to use: Large monorepos, unfamiliar services, onboarding, and cross-team work.
  - How: Index the authoritative repository and make browsing available through a fast web or IDE surface.
- **Trust through completeness and ranking**: Users trust search when it indexes all relevant code, returns the expected results, and ranks useful results first.
  - When to use: Choosing between exactness and relevance.
  - How: Make limitations visible, improve ranking signals, and preserve repository-at-head semantics.
- **Layered search expressiveness**: Token, substring, regular-expression, and semantic or cross-reference search serve different costs and needs.
  - When to use: Selecting index structures and query modes.
  - How: Start with useful low-cost search, then add expressiveness where the scale justifies its indexing and latency cost.

## Key Concepts

- **Search index**: Structures that make code retrieval fast.
- **Query-independent signal**: Ranking information independent of the current query, such as popularity or path.
- **Query-dependent signal**: Ranking information derived from the query/result relationship.
- **Result diversity**: Avoiding a result set dominated by one nearly identical location.
- **Index latency**: Delay between a repository change and search visibility.
- **Query latency**: Time from request to useful results.
- **Code archaeology**: Using history and review records to understand why code evolved.

## Mental Models

- Search is an interactive conversation: users ask progressively refined questions.
- Completeness is a trust property, not merely a backend statistic.
- A search tool becomes more valuable when it is the shared substrate for documentation, ownership, and navigation.
- The right result is often a path to understanding, not a single matching line.

## Anti-patterns

- **Local-only indexing**: It excludes code the developer does not already have.
- **Search that is fast but incomplete**: Users learn that absence of a result means nothing.
- **Ranking without transparency**: Useful results are hidden behind unexplained ordering.
- **History disconnected from code**: Engineers lose the rationale needed to change safely.

## Worked Example

A developer investigating an unfamiliar API first searches for the symbol, follows references to callers and definitions, opens documentation, identifies owners, and inspects recent changes. Each hop should be fast enough to preserve the question-and-answer loop. A tool that returns a perfect match only after a slow index refresh still fails the workflow.

## Reference Table

| Need | Search capability |
|---|---|
| Find exact identifier | Token search |
| Find text inside strings/comments | Substring search |
| Express structural pattern | Regular expression |
| Understand call or type relationships | Cross-reference index |
| Understand intent | History and review integration |

## Key Takeaways

1. Make global code understanding zero-setup.
2. Optimize for trust, latency, and completeness together.
3. Rank useful results without hiding the limits.
4. Integrate search with docs, ownership, and history.
5. Start useful at small scale, then invest in specialized indexing as scale demands.

## Connects To

- **Chapter 3**: Search makes organizational knowledge discoverable.
- **Chapter 16**: The authoritative head determines what search should index.
- **Chapter 19**: Review tooling and code search reinforce each other.

