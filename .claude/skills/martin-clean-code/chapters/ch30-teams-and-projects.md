# Chapter 30: Teams and Projects

## Core Idea
Teams take far longer to build than projects take to complete, so organizations should form persistent, "gelled" teams and feed them a rotating stream of projects — not assemble ad-hoc teams around each project and disband them when it ends.

## Frameworks Introduced
- **Does It Blend?**: the test for whether a group of people staffed onto a project is actually a team. If individuals are split 25-50% across multiple projects, with different project managers, analysts, programmers, and testers per project, the result is not a team — it's "something that came out of a Waring blender."
  - When to use: whenever evaluating how an organization staffs a project, especially in enterprises (banks, insurance companies) that habitually fractionalize people across many concurrent small projects.
  - How: ask whether each member is dedicated full-time to this one group of people with a shared manager/analysts/testers. If not — if there is "half a person" on the team — it will never gel into a real team.
- **Velocity-based reallocation**: manage a gelled team's output across multiple concurrent projects by measuring velocity (points of work completed per week) and letting management allocate percentages of that velocity to each project.
  - When to use: once a team has gelled and is taking on more than one project simultaneously.
  - How: measure velocity as a statistical average over several weeks; management sets a target split (e.g., 15/15/20 points across three projects) and can shift the whole team's effort to one project in an emergency.

## Key Concepts
- **Gelled team**: a team that has worked together long enough (six months to a year) to anticipate, cover for, support, and demand the best from each other — producing near-magical results.
- **Team size**: roughly a dozen people is ideal (range three to twenty).
- **Team composition**: programmers, testers, analysts, and a project manager, with a programmer:tester/analyst ratio around 2:1 (e.g., 7 programmers, 2 testers, 2 analysts, 1 project manager).
- **Analyst vs. tester perspective**: both write automated acceptance tests/requirements, but analysts focus on business value and write happy-path cases; testers focus on correctness and write failure/boundary cases.
- **Coach/master role**: an optional part-time role held by a team member who defends the team's process and discipline, acting as the team's conscience under schedule pressure.
- **Fermentation**: the multi-month process by which a newly formed group works out interpersonal differences and becomes a gelled team.
- **Velocity**: the amount of work (measured in points of complexity) a team completes per fixed period; it fluctuates week to week but averages out over time.
- **Team vs. project longevity**: teams should outlive any single project — projects should be allocated to existing gelled teams rather than teams formed around projects.

## Mental Models
- Teams are an expensive, slow-to-build asset; projects are transient. Optimize for preserving the asset, not the transient unit.
- A gelled team is a reusable "engine" for getting many projects done, not a resource pool to be reshuffled.
- Reallocating priorities is only cheap and fast when the team itself doesn't need to be re-formed — velocity can shift between projects on a dime, but people cannot be reassembled that quickly into a working team.
- There is an inherent tension between project-owner security (a dedicated team they control) and business agility (a shared gelled team that can be reprioritized); the author explicitly favors business agility, placing the burden on project owners to make the case for priority.

## Anti-patterns
- **The blender team**: staffing a project with people who are each only 25-50% allocated, under different managers/analysts/testers than their other projects. This structure can never gel because no one has enough time or continuity with the group to build working relationships.
- **Forming teams around projects**: banks and insurance companies routinely assemble a team for a project and disband it when the project ends. This destroys the investment made in gelling and forces every new project to start the team-building process from zero.
- **Treating people as fungible resource units**: "half a person" doesn't exist; splitting individuals' time thinly across unrelated project groups is treated as normal management practice but actually guarantees the group never becomes a real team.
- **Breaking apart a gelled team when a project ends**: once a team has gelled, disbanding it just because the current project finished discards the hard-won magic instead of simply feeding the team its next project.

## Worked Example
Martin describes his recurring experience consulting for banks and insurance companies: a small project needing one or two programmers for a few weeks gets staffed with a project manager, business analyst, programmers, and testers — all of whom are simultaneously split across several other unrelated projects with different managers and colleagues. No one is ever fully "on" this project. He contrasts this with the ideal: a stable ~12-person gelled team (7 programmers, 2 testers, 2 analysts, 1 PM) that stays together across many projects, taking 6-12 months to fully gel but then able to plan, solve problems, and deliver together — and to have its effort reallocated by percentage (e.g., splitting a velocity of 50 into 15/15/20 across three concurrent projects) rather than being physically reassembled each time priorities shift.

## Key Takeaways
1. Build teams, not projects — form persistent teams and feed them a continuous stream of projects rather than assembling new teams per project.
2. Never split people across multiple project groups with different managers/analysts/testers at 25-50% each; there is no such thing as half a person on a team.
3. Target roughly a dozen people per team, with a ~2:1 ratio of programmers to testers/analysts, plus a project manager and optionally a part-time coach.
4. Expect gelling to take six months to a year — protect that investment by not disbanding a team once it has formed.
5. Use team velocity (points/week, averaged) to allocate a gelled team's capacity across multiple concurrent projects, rather than physically reallocating people.
6. When priorities shift, move work to the team via velocity reallocation, not people via reorganization — this is what lets a business "turn on a dime."
7. Expect project owners to lose some sense of dedicated control under this model; treat that as the price of organizational agility, and require project owners to make the case for priority.

## Connects To
- **Ch29 Collaboration**: the collaborative practices (pairing, stand-ups, shared ownership) described there are what make gelling possible within a stable team — Ch30 explains why that team needs to persist for those practices to compound in value.
- **Ch25 Time Management / Ch27 Pressure**: velocity-based capacity allocation gives management a disciplined way to absorb schedule pressure and emergencies without breaking team structure.
- **Ch26 Estimation**: velocity as used here is the same estimation currency (points per iteration) discussed for estimating and tracking work.
- **Ch3 Functions / Ch1 Clean Code (Clean Code book)**: not directly connected — Ch30 is organizational, not code-craft, though both books share the underlying premise that professionalism requires disciplined, sustainable structures (technical and organizational).
- **"Jelled teams"**: the concept and term are drawn directly from Peopleware (DeMarco & Lister), which Martin's "gelled team" discussion closely echoes.
