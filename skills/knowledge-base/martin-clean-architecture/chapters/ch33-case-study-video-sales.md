# Chapter 33: Case Study: Video Sales

## Core Idea
This chapter walks end-to-end through applying Clean Architecture to a real product (a video-tutorial sales website), showing the concrete process: identify actors/use cases via the Single Responsibility Principle, partition components along both actor boundaries and the Dependency Rule, then defer final deployment grouping until later.

## Frameworks Introduced
- **Actor-Driven Use-Case Analysis**: identify the actors (sources of change) first, then derive use cases per actor.
  - When to use: at the start of architecting any new system, before drawing component diagrams.
  - How: list all human/system actors; for each, list the use cases they drive; look for use cases so similar across actors that they warrant an abstract use case they can inherit from.
- **Two-Dimensional Component Separation**: separate components along two independent axes simultaneously.
  - When to use: designing the component architecture once use cases are known.
  - How: (1) separate by actor per the Single Responsibility Principle — a change for one actor must not affect another; (2) separate by Dependency Rule level — views/presenters/interactors/controllers/utilities, with dependencies pointing toward higher-level policy.

## Key Concepts
- **Abstract use case**: a use case that establishes a general policy which concrete use cases flesh out (e.g., `View Catalog` as parent of `View Catalog as Viewer` and `View Catalog as Purchaser`) — Martin's own notation, not standard UML `<<abstract>>` stereotype.
- **Actors as sources of change**: per SRP, the four actors (e.g., viewers, purchasers, video authors, administrators) are the four reasons the system will change; partitioning must isolate them from each other.
- **Deployable component**: each box in the component diagram is a candidate `.jar`/`.dll`, but the actual deployment grouping is a separate, later decision from the source-level partitioning.
- **Flow of control vs. dependency direction**: control flows right-to-left (controller → interactor → presenter → view) but *using* dependencies (open arrows) point with the flow of control while *inheritance* dependencies (closed arrows) point against it — an application of the Open-Closed Principle to keep dependencies flowing toward policy.

## Mental Models
- Think of the component diagram as **provisional, not final**: partition the *build* this finely, but keep the right to combine components into fewer deliverables (e.g., one jar for all views, one for all presenters) as real-world needs dictate.
- Use **"which actor does this change serve?"** as the litmus test when deciding where new code belongs.

## Reference Tables
| Deployment grouping option | Structure |
|---|---|
| Maximal (per Fig 33.2) | One component per actor × per layer (views, presenters, interactors, controllers each split by actor) |
| Moderate | 5 jars: views, presenters, interactors, controllers, utilities |
| Coarser | 2 jars: (views + presenters) vs. (interactors + controllers + utilities) |
| Coarsest | 2 jars: views+presenters vs. everything else |

## Worked Example
Product: a video-tutorial sales site (modeled on cleancoders.com). Four actors: **Viewers** (watch videos), **Purchasers** (individuals buying streaming or download licenses, or businesses buying batch/discounted streaming licenses), **Video Authors** (supply video files, descriptions, ancillary materials), **Administrators** (manage series, videos, pricing). Use-case analysis produces per-actor use cases plus one abstract use case, `View Catalog`, inherited by both `View Catalog as Viewer` and `View Catalog as Purchaser` because their behavior is nearly identical. The component architecture then splits Views, Presenters, Interactors, and Controllers, further subdivided per actor (e.g., separate Viewer-Presenter and Purchaser-Presenter components), with a shared `Catalog View` / `Catalog Presenter` component holding the abstract classes that actor-specific components inherit from. Dependencies all flow toward higher-level policy (Dependency Rule); inheritance arrows point the opposite direction of the using arrows, an Open-Closed Principle application ensuring low-level detail changes don't ripple upward. Final deployment packaging (how many actual jar/dll files) is left flexible and decided later based on observed real-world change patterns.

## Key Takeaways
1. Start architecture work by identifying actors, not screens or tables — actors are the true sources of change (SRP).
2. Recognize and factor out abstract use cases when concrete use cases are nearly identical, but don't force abstraction where it isn't warranted.
3. Partition along two independent axes at once: by actor (SRP) and by Dependency Rule level (policy vs. detail) — this is a two-dimensional separation, not a single hierarchy.
4. Keep source-level component partitioning separate from deployment-unit decisions — build fine-grained, deploy however is currently convenient, and change deployment grouping freely as the system evolves.
5. Use inheritance arrows (against flow of control) deliberately to keep dependencies pointing toward policy even when control must flow the other way (Open-Closed Principle in action).

## Connects To
- **Ch 7 (SRP)**: directly drives the actor identification step.
- **Ch 11 (OCP)**: explains why inheritance arrows point opposite the flow of control.
- **Ch 22 (Clean Architecture)**: the views/presenters/interactors/controllers layering is the direct concrete instance of the Clean Architecture's four-ring model.
- **Ch 34 (The Missing Chapter)**: picks up immediately where this case study leaves off, addressing how to actually implement these component boundaries in code (packages, access modifiers).
