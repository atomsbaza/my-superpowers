# Chapter 16: Version Control and Branch Management

## Core Idea

Version control is the shared source of truth for change, but branching and version choices create coordination cost. Google’s practices emphasize one current version, development at head, few long-lived branches, and repository structures that preserve a coherent virtual trunk.

## Frameworks Introduced

- **Source of truth**: A team must know where the authoritative current state lives and how changes enter it.
  - When to use: Repository design, release management, and dependency questions.
  - How: Establish ownership, a canonical path, review rules, and a way to reconstruct history.
- **One-Version Rule**: Reducing choices about which version to use simplifies builds, support, upgrades, and large-scale change.
  - When to use: Shared libraries, monorepos, and organization-wide dependencies.
  - How: Prefer a single supported version at a common head; remove parallel choices unless a real compatibility boundary requires them.
- **Trunk-based development**: Integrate small changes continuously instead of maintaining long-lived development branches.
  - When to use: Collaborative products with continuous integration.
  - How: Keep changes small, use feature flags where isolation is needed, and rely on CI/rollback rather than branch divergence.
- **Work in progress is a branch**: Unmerged local or remote work already creates divergence and integration cost.
  - When to use: Deciding whether a branch is justified.
  - How: Minimize the lifetime of divergence and make partial work safe to integrate.

## Key Concepts

- **Version control system (VCS)**: Records and coordinates changes to source.
- **Source of truth**: The authoritative current representation of a project.
- **Trunk/head**: The main integrated line of development.
- **Long-lived branch**: A branch whose divergence creates substantial future merge or testing cost.
- **Release branch**: A controlled line used to stabilize or support a release.
- **Monorepo**: A repository containing many projects or most of an organization’s source.
- **Virtual monorepo**: Multiple repositories presented with a coherent head/trunk model.

## Mental Models

- Every available version is a choice tax paid by every consumer and tool.
- Branches defer integration; they do not remove it.
- A repository is a collaboration protocol, not merely a file container.
- Separate repositories can still share a virtual trunk if dependency and review tooling preserve one coherent head.

## Anti-patterns

- **No clear source of truth**: Teams do not know which state is authoritative.
- **Branch-per-feature by default**: Divergence and merge costs grow with organization size.
- **Multiple supported versions without need**: Every version multiplies testing, support, and migration paths.
- **Technical workarounds for dependency choice**: Shading or linker tricks may hide organizational debt while consuming engineering time.

## Worked Example

When a shared library has several available versions, each consumer must choose, test, and support a dependency edge. An organization-wide One-Version Rule removes that decision and makes upgrades and large-scale changes tractable. If release support requires a branch, keep it narrow and time-bounded while mainline development continues at head.

## Reference Table

| Choice | Scaling benefit | Cost/risk |
|---|---|---|
| Single head version | Simple dependency and tooling model | Requires coordinated migration |
| Long-lived dev branches | Local isolation | Merge conflicts and late integration |
| Trunk-based development | Fast feedback and shared state | Requires strong CI and rollback |
| Monorepo | Broad visibility and atomic change | Requires scalable tools and policies |
| Fine-grained repositories with virtual head | Local ownership plus coherent version | More infrastructure complexity |

## Key Takeaways

1. Establish one authoritative source of truth.
2. Prefer one supported version and development at head.
3. Keep branches short-lived and purposeful.
4. Invest in CI and rollback before relying on branch isolation.
5. Treat repository boundaries and version choices as organizational design.

## Connects To

- **Chapter 18**: Build systems expose the cost of dependency choices.
- **Chapter 21**: Dependency management is version-control design extended across boundaries.
- **Chapter 23**: CI makes trunk-based development safe.

