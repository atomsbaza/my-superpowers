# Chapter 10: ISP: The Interface Segregation Principle

## Core Idea
Depending on a module that offers more than you use is harmful — it forces unnecessary recompilation/redeployment in statically typed languages and, more generally at the architecture level, couples you to failures and changes in features you never needed.

## Frameworks Introduced
- **Interface Segregation Principle (ISP)**: Don't force clients to depend on interfaces (operations) they don't use. Named for the diagram showing a fat interface (`OPS`) split into per-client interfaces (`U1Ops`, `U2Ops`, `U3Ops`).
  - When to use: When a class/interface exposes multiple operations used by disjoint sets of clients, especially in statically typed languages where unused-but-imported declarations create real compile/deploy dependencies.
  - How: Segregate the fat interface into smaller, client-specific interfaces so each client's source code depends only on the interface(s) it actually calls.

## Key Concepts
- **Fat interface**: A single interface/class (e.g., `OPS`) bundling operations (`op1`, `op2`, `op3`) used by different, non-overlapping clients (`User1`, `User2`, `User3`).
- **Source code dependency (static languages)**: In languages like Java, `import`/`use`/`include` declarations create real dependencies — a client that imports `OPS` depends on all of `OPS`, even operations it never calls, forcing recompilation/redeployment on unrelated changes.
- **Inferred dependency (dynamic languages)**: In Ruby/Python, dependencies are resolved at runtime rather than declared in source, so ISP's recompilation-forcing mechanism doesn't literally apply — but the deeper architectural concern still does.
- **Architectural-level ISP**: Depending on a framework F that itself depends on a database D (with features S doesn't use) means changes or failures in unused D features can force redeployment or cause failures in F and S, even though S never used those features.

## Mental Models
- Think of a fat interface like a shared apartment lease where one roommate's rent dispute (change to `op2`) forces every roommate (including `User1`, who never uses `op2`) to re-sign the lease (recompile/redeploy).
- Ask "does my source code even mention things I don't call?" — if yes in a statically typed language, that's a live ISP violation with real recompilation cost, not just aesthetics.
- Extend the same question up the stack to third-party dependencies: "does my dependency (F) drag in a dependency (D) with capabilities I don't use?" — unused transitive capability is unused transitive risk.

## Anti-patterns
- **Single fat class/interface serving multiple unrelated clients**: Forces clients depending on unrelated operations to be recompiled/redeployed when those unrelated operations change, even though nothing they use has changed.
- **Depending on a framework that bundles an unnecessary dependency (e.g., a specific database)**: Failures or changes in the unused parts of that transitive dependency can cause failures or forced redeployment of your own system, purely from "carrying baggage you don't need."

## Code Examples
<!-- omit — chapter is diagram-based (Figures 10.1–10.3), no source code -->

## Reference Tables
<!-- no comparison/decision table in this chapter -->

## Worked Example
`OPS` is a class with three operations (`op1`, `op2`, `op3`) used respectively and exclusively by `User1`, `User2`, `User3`. In a statically typed language, `User1`'s source imports `OPS` wholesale, so it inadvertently depends on `op2` and `op3` too — a change to `op2`'s implementation forces `User1` to be recompiled and redeployed even though `User1` never calls `op2`. The fix: segregate `OPS` into three interfaces `U1Ops`, `U2Ops`, `U3Ops`, each exposing only the relevant operation; `User1` now depends only on `U1Ops`, so changes to `op2`/`op3` no longer touch `User1`'s build.

At the architecture scale: system S includes framework F, and F is bound to database D. Even though S (via F) never uses certain features of D, changes to those unused D features can force redeployment of F and, transitively, S — and a failure in an unused D feature can cause F and S to fail too.

## Key Takeaways
1. Apply ISP most rigorously in statically typed languages, where unused imports create real, mechanical build/deploy coupling.
2. In dynamically typed languages, the compile-time forcing mechanism disappears, but the deeper "don't depend on baggage you don't need" concern still applies architecturally.
3. Segregate fat interfaces along client usage lines — one interface per distinct consumer need, not one interface per implementing class.
4. Extend ISP thinking to transitive/third-party dependencies: evaluate not just what a dependency does for you, but what unused capability (and unused risk) it drags in.
5. ISP is a special case of the broader rule: software entities should not depend on things they don't directly use — the same rule underlies OCP's information-hiding boundaries (Ch 8) and will resurface as the Common Reuse Principle (Ch 13).

## Connects To
- **Ch 8 (OCP)**: The `FinancialReportRequester` information-hiding interface in Ch 8 is a direct application of "don't depend on things you don't use."
- **Ch 13 (Common Reuse Principle)**: Explicitly foreshadowed in this chapter's conclusion as the component-level generalization of ISP's "don't carry unneeded baggage" concern.
- **Ch 11 (DIP)**: Segregated interfaces are also typically abstract, so ISP and DIP reinforce each other when designing boundary interfaces.
