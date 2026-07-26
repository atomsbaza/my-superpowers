# Martin Clean Code / Clean Coder — Reasoning Cheatsheet

## Decision Rules (When X, Do Y, Because Z)

- Name needs a comment to make sense → rename it instead. A name is the interface to intent; comments rot, code doesn't.
- About to write a comment → first ask "would a well-named function/variable make this unneeded?" Comment only if truly nothing else can say it (legal, intent-behind-a-tradeoff, warning, TODO, public API doc).
- Function body mixes high-level and low-level statements → extract until every line is one level below the function's name. Mixed abstraction is why functions feel "hard to follow" even when short.
- Function is doing an `if`/`else`/`while` body of any complexity → keep the block to one line (usually a call). Depth and length compound reading cost.
- You find yourself dividing a function into internal sections (setup/work/cleanup) → split it into 3 functions. Sectionable = already multi-purpose.
- A boolean/flag parameter changes what the function does → split into two named functions. A flag hides "this does two things" behind one signature.
- Argument list creeping past 2 → wrap the related ones into an argument object (e.g., `x,y` → `Point`). Naming the group also names a concept you were missing.
- Choosing exceptions vs return codes → always exceptions. Return codes force an immediate `if` at the call site and mix error-flow with logic; exceptions let happy path and error path separate cleanly.
- Function contains `try` → the function should do nothing else. Extract the try body and catch body into their own named functions.
- About to return or pass `null` → don't. Return an empty collection or a Special Case object; treat passing null as forbidden absent an API that explicitly wants it — there's no universal safe recovery.
- Adopting a third-party library → write learning tests against it before writing production code that uses it; keep them permanently as regression tripwires for upgrades.
- A broad third-party interface (e.g. `Map`) would otherwise cross a public API → wrap it in your own narrow class first. Every consumer of the raw interface is coupled to its entire surface, including the parts you didn't want them to use.
- Class accrues methods that only touch a subset of its instance variables → that's a hidden class; extract it. Loss of cohesion is the signal, not line count.
- Class depends directly on a volatile/external concrete type (DB, vendor API, exchange) → extract an interface and inject it (DIP). Makes the dependency swappable and the class testable with a stub.
- You can't describe a class in ~25 words without "and/or/but/if" → it has more than one responsibility; split by "reason to change," not by method count.
- Same 3-line block (or same algorithm shape) appears in 2+ places → extract it immediately, however small. Small duplications compound risk on every future change; don't defer because it's tiny.
- Multiple methods differ only by one step of an otherwise-identical algorithm → TEMPLATE METHOD (shared base + one abstract hook), not copy-paste-and-edit.
- Repeated `switch`/`instanceof`/type-case chains on the same type → collapse to one switch, buried behind a factory, dispatching to polymorphic objects — never scattered through the codebase.
- Shared mutable state must cross threads → prefer copying data over sharing it; if you must share, minimize and tightly encapsulate the guarded region; keep synchronized blocks as small as possible.
- A test failure is non-reproducible / "flaky" → treat it as a real threading bug first, not a fluke. Concurrency bugs pass casual testing and fail unpredictably under load.
- Code you didn't write "looks fine" and tests "all pass" → check coverage before trusting it. Passing tests only prove what they cover.
- Manager/stakeholder pressures for an unrealistic date → give the honest earliest-certain date, hold it under pushback; never say "I'll try" as a hedge — restate the fact instead.
- Under deadline pressure, tempted to cut tests/refactoring/pairing → don't. Cutting discipline never actually goes faster and violates your standing commitment to quality, which outranks any single deadline.
- You realize you'll miss a commitment → raise the flag immediately, not at the deadline, so the team can replan.
- You catch yourself mid-Zone or exhausted at 3am → stop. Code written impaired looks fine in the moment and is structurally wrong; it's cheaper to stop than to fix later.
- Requirement is described only in prose → don't start building; turn it into an executable acceptance test (given/when/then) with the stakeholder before implementation, so ambiguity surfaces now instead of in production.
- A test as written seems wrong or unachievable → negotiate a better test with its author; don't implement to a known-bad spec.

## Decision Trees

**Objects vs. data structures — which shape to use:**
- Expect to add new *types* over time, behavior is stable → use objects + polymorphism (adding a type touches nothing else).
- Expect to add new *operations/functions* over time, types are stable → use data structures + free functions (adding a function touches nothing else).
- Need both to change often → no free lunch; pick which axis hurts less for this module, don't default to objects everywhere.

**Should this chain of calls worry me? (Law of Demeter / train wrecks)**
1. Are the intermediate things plain data structures (DTOs)? → chaining is fine, data naturally exposes structure.
2. Are they true objects (behavior-hiding)? → a chain (`a.getB().getC().getD()`) is a Demeter violation.
   - Fix: ask "what did the caller actually want to *do*?" and push that behavior into the owning object (tell, don't ask) rather than just splitting the chain into local variables.

**Test Automation Pyramid — where does this test belong:**
1. Is it "is this code unit correct?" → unit test (programmer-written, TDD, majority of volume, run every CI build).
2. Is it "does this component satisfy a business rule?" → component/acceptance test (QA+business, ~half the system, happy path + obvious edges).
3. Is it "do assembled components talk to each other correctly?" (plumbing, not business rules) → integration test (architects, run periodically).
4. Is it "does the whole system construct/interoperate/perform?" → system test (~10% coverage, run infrequently).
5. Is it "what does this do that we didn't think to specify?" → manual exploratory testing (no script, human creativity, goal is discovery not coverage).

**Should I say yes, no, or negotiate to a request?**
1. Is it fully achievable without cutting discipline or working unbounded overtime? → commit: "I will X by Y."
2. Is the outcome partly outside your control? → commit to the controllable actions, not the outcome.
3. Is it not achievable as stated? → say no with the fact (not "I'll try"); let the other side push back with their facts; negotiate scope/date together.
4. Being asked to hit it by cutting tests/refactoring? → refuse regardless of pressure; quality is the non-negotiable prior commitment.

**Refactoring a mess (successive refinement):**
1. Get it working end-to-end, however ugly.
2. Notice the design straining under the next requirement (e.g., a third parallel structure, growing type-case) → stop adding features.
3. Refactor in many tiny test-verified steps until structure is sound again.
4. Resume feature work. (Never big-bang rewrite; never "get it working" and stop there.)

## Trade-off Matrices

| Concern | Procedural (data + functions) | OO (objects + polymorphism) |
|---|---|---|
| Add a new data type | Hard — every function edited | Easy — new class only |
| Add a new operation | Easy — new function only | Hard — every class edited |

| Exception style | Cost |
|---|---|
| Checked exceptions | Cascades signature changes up every call layer; violates OCP |
| Unchecked exceptions | Preferred default; catch site decoupled from throw site |

| Pressure response | Outcome |
|---|---|
| Intensify disciplines (more tests, more refactoring, pair up) | Slower feeling, actually faster, fewer defects |
| Drop disciplines "just this once" | Feels faster, is slower, proves you never trusted the discipline |

| Commitment language | What it signals |
|---|---|
| "I will X by Y" | Real, binding, owned |
| "I need to / I hope / let's" | Outcome treated as out of your hands |
| "I'll try" | Disguised non-commitment unless it means genuine extra effort with a real reserve plan |

## Thresholds & Defaults

- Functions: "small, and then smaller than that" — hardly ever >20 lines; indent depth 1–2.
- Argument count preference order: niladic (0) > monadic (1) > dyadic (2, avoid) > triadic (3, avoid) > polyadic (needs special justification).
- Line length: cap ~120 chars (80 classic).
- File size: ~200 lines typical, ~500 upper bound.
- F.I.R.S.T.: tests must be Fast, Independent, Repeatable, Self-Validating, Timely.
- Kent Beck's 4 Rules of Simple Design, in strict priority order: (1) passes all tests, (2) no duplication, (3) expresses intent, (4) minimizes classes/methods — never satisfy a later rule at a former's expense.
- PERT: µ (expected) = (O + 4N + P) / 6; σ (uncertainty) = (P − O) / 6. For a sequence: sum the µ's, root-sum-square the σ's. O and P should each carry <1% chance of actually happening.
- 60-hour week model: 40 hrs belong to the employer, 20 hrs of practice/learning belong to you.
- Bounded overtime: acceptable only if <2–3 weeks, affordable, and paired with a concrete fallback plan if it fails.
- Team size: ~12 people ideal (3–20 range); ~2:1 programmer-to-tester/analyst ratio; gelling takes 6–12 months.
- Pomodoro: 25-minute protected focus blocks, ~5 min break, longer break every 4th.

## Tells & Smells (fast heuristics, Ch17 tags in brackets)

- Function name is a verb but it also returns a status → command/query violation; split into a command and a query.
- A getter also has a side effect (e.g., lazily creates the value) → the name is lying [N7]; rename to reveal it (`createOrReturnX`).
- You see `if (!x.shouldNotY())` → flip it positive: `if (x.canY())` [G29].
- A closing brace has a comment (`} // while`) → the function is too long; shorten it, don't decorate the brace.
- Constants/lookup tables live on an abstract base class but only one subclass uses them → push them down [G7]; a base class must not depend on or imply knowledge of its derivatives.
- A method spends more time reading another object's data than its own → Feature Envy [G14]; move the method to the object it envies.
- A bug fix requires a scattered set of `+1`/`-1` adjustments around an index → the real representation is wrong (probably 1-based where it should be 0-based); fix the representation, not each site.
- Two functions must be called in a specific undocumented order → hidden temporal coupling [G31]; make the order structural (one calls the other) instead of relying on caller discipline.
- A raw number or string appears inline with no name → magic value [G25]; extract a named constant.
- You're tempted to add a comment explaining *why* a conditional is there → extract and name the conditional instead [G28]; comment only if the "why" still isn't obvious from the name.
- A module needs to change for more than one kind of reason → SRP violation; find each "reason to change" and extract a class per reason.
- Code review or self-review turns up an "I'll clean this up later" → LeBlanc's Law: later never comes; fix it now or accept it as permanent.
- You notice you're avoiding your workstation, doing anything but the actual task → priority inversion / avoidance, not real reprioritization — name it and go back to the real task.
- You're "making progress" in code that keeps getting harder without getting better → you're in a swamp, not a blind alley; the way back is never as expensive as it looks — the Rule of Holes applies (stop digging) even more urgently here.
