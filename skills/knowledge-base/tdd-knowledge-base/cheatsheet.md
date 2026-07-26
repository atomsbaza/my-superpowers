# TDD Cheatsheet — Practitioner Judgment

## Decision Rules

| When... | Do... | Because... |
|---|---|---|
| Unsure of the right abstraction | Triangulate: wait for 2 tests to demand it, don't generalize from 1 | one example is weak evidence; guessing wrong costs a rewrite |
| Logic is simple & you already know it | Use Obvious Implementation, skip Fake It | faking adds no value when correctness is already certain |
| You want a fast green bar, unsure of real logic | Fake It (hardcode), then evolve as tests force it | defers design commitment; must be redeemed, never left permanent |
| Multiple ways exist to go green | Pick the lowest-priority (simplest) TPP transformation, not the general one | premature generality = "getting stuck," forcing a bigger rewrite later |
| A dependency is "awkward" to mock | Treat it as a design smell — fix the design, don't just work around it (London) | "if hard to test, hard to use" — friction is real architectural feedback |
| Testing legacy code with zero tests | Write Characterization Tests / Golden Master BEFORE touching anything | there is no safety net otherwise — "refactoring" without one is just risky rewriting |
| A characterization test locks in a bug | Leave it; fix the bug as a separate, deliberate decision later | conflating "describe reality" with "fix reality" corrupts the safety net |
| New feature, requirements still fuzzy | Go Outside-In (UI → down), stub inner layers, replace as you go | forces business alignment; avoids YAGNI violations by construction |
| Legacy modernization / domain already understood | Go Inside-Out (logic → up) | fast unit feedback on a foundation that's already believed correct |
| Choosing test type for the whole suite | Shape it like a pyramid: many unit, fewer integration/contract, minimal acceptance/E2E | cost/speed/fragility rise at each higher layer |
| London-school (heavy mocking) codebase | Keep a real E2E layer regardless | mocks can't prove real integration works |
| Refactoring | Do it only while Green, never while Red | Green is your only proof the change didn't break behavior |
| Writing/reviewing test code | Apply the same style/refactor discipline as production code (Builders, DRY setup) | "Respect" — sloppy tests decay into a maintenance burden, killing Courage |
| Deciding what's "done" for a feature | Don't trust a green acceptance test alone if inner layers are stubbed | passing outer test can mask quick-and-dirty, undertested internals |

## Decision Trees

**Detroit vs. London — which style for this test?**
- Is this new-feature design being discovered through object collaboration? → London (interaction verification, mock all collaborators)
- Is this well-understood domain logic / legacy modernization? → Detroit (state verification, real collaborators, mock only awkward externals)
- Is the dependency external (network, filesystem, 3rd-party API, clock)? → mock it either way, but wrap it in an adapter you own first ("don't mock what you don't own")
- Is refactor-safety more valuable than pinpoint bug localization here? → Detroit. Reverse priority? → London.

**Inside-Out vs. Outside-In — where to start?**
- Requirements clear, logic-first, no UI yet needed? → Inside-Out
- Requirements fuzzy, need product/QA buy-in, user-facing? → Outside-In, drive from a failing acceptance test, stub inward
- Either way: pair with a Three Amigos session first to prevent the "Business Gap"

**Legacy code entry point**
- Codebase has clear seams / identifiable units? → Characterization tests per unit
- Tangled/opaque, no seams, hard to isolate? → Golden Master (bulk input/output diff) first, narrow to characterization tests as it's decomposed

## Trade-off Matrices

| Dimension | Detroit (Classicist) | London (Mockist) |
|---|---|---|
| Verifies | Final state | Interactions/calls |
| Refactoring ease | High — tests don't know internals | Lower — mocks pin internal calls ("Vulnerable Tests") |
| Bug localization | Weaker — failures cascade across dependents | Strong — failure isolates to one class |
| Design pressure | Indirect, via setup pain | Immediate — awkward mock = fix design now |
| Failure mode if overdone | The Inspector (brittle on internals) | The Mockery (no real integration confidence) |

| Dimension | Inside-Out | Outside-In |
|---|---|---|
| Business alignment | Risk of "Business Gap" | Strong — driven by user scenario |
| Feedback speed early | Fast (unit tests immediately) | Slow (outer test stays red a long time) |
| Risk if overdone | Technically polished, wrong thing built | Quick-and-dirty stubs become the shipped internals |
| Best fit | Legacy, API-first, tech-debt work | New features, unclear requirements |

## Thresholds & Defaults

- Defect reduction: 40–90% industrial (MSFT/IBM), 35–45% academic — cite the range, never a bare number.
- Same-day fix rate: 97% (TDD) vs 73% (non-TDD).
- Technical debt ratio: 0.45 → 0.29 with sustained TDD+BDD — a long-term effect, not immediate.
- Short-term productivity may *drop* initially — sell TDD as an investment with a payback period, not a free win.
- TPP ordering (simplest→most complex): null→constant, const→const, const→variable, statement→statements, unconditional→if, scalar→array, if→while, statement→recursion. Only escalate a rung when the current test genuinely can't pass otherwise.
- DHH's flagged smell: 4 lines of test per 1 line of production code — a sign of over-testing ratio, not a target.

## Tells & Smells (fast diagnosis)

| Symptom | Name | Fix |
|---|---|---|
| Test passes, but proves nothing | The Liar | Rewrite so it actually asserts the requirement |
| Suite too slow to run often | The Slow Poke | Push slow tests out of unit tier; isolate I/O |
| Only verifies mocks were called | The Mockery | Swap some mocks for real collaborators; prefer state verification |
| Asserts on private/internal state | The Inspector | Assert only on public API/observable output |
| Huge arrange blocks | Excessive Setup | Extract Builders/Factories; question collaborator count in the design |
| Prod code reshaped only for testability | Test-Induced Design Damage | Test through natural seams; don't add indirection whose only job is enabling a double |
| Breaks on refactor, output unchanged | Vulnerable Tests | Test outcomes, not call sequences |
| Mocking a 3rd-party type directly | Mocking What You Don't Own | Wrap in an owned adapter; mock that |
| "It's hard to write a test for this" | Design smell (Detroit maxim: hard to test = hard to use) | Fix the design, don't add test scaffolding to route around it |
| Green unit suite, no E2E | False confidence gap | Add a minimal E2E/acceptance layer, especially if London-style |
| Gherkin scenario mentions button IDs/clicks | BDD scenario coupled to UI mechanics | Rewrite around business outcome, not implementation |

## Root-Cause Note
Excessive Setup, Test-Induced Damage, The Inspector, and Vulnerable Tests are almost always **the same underlying disease**: coupling to *how* something is done rather than *what* it produces. When you see any of these, look first at the production design's responsibility split, not just the test.
