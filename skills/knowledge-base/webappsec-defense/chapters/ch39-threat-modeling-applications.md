# Chapter 39: Threat Modeling Applications

## Core Idea
A properly implemented threat model is a living knowledge repository built from five sequential goals — document knowledge, identify threat actors, identify risks/attack vectors, identify mitigations, identify the delta between risk and mitigation — and it only produces actionable value once all five are completed together; skipping any one (especially mitigations or delta) leaves the exercise a box-checking ritual.

## Frameworks Introduced
- **The Five-Goal Threat Modeling Framework**: Document knowledge -> Identify threat actors -> Identify risks (attack vectors) -> Identify mitigations -> Identify delta.
  - When to use: For any new feature or product with meaningful public-facing or privileged surface area, before or during development — not after launch.
  - How: Collect logic design and technical design documentation first (goal 1); enumerate every threat actor including internal, external, and machine/script users, split by authenticated/unauthenticated where relevant (goal 2); cross-reference logic design, technical design, and threat actors to brainstorm attack vectors with a severity ranking (goal 3); document all *existing* mitigations per attack vector (goal 4); subtract mitigated vectors from the full list to find the unmitigated delta, then brainstorm new mitigations for each remaining item before the feature is allowed to launch (goal 5).
- **Logic Design vs. Technical Design (as dual inputs)**: Two complementary description levels that together expose both business-logic vulnerabilities and traditional technical vulnerabilities.
  - When to use: Both are required inputs before attack-vector brainstorming; neither alone is sufficient.
  - How: Logic design is a functionality-level description (UX-designer level of detail) capturing what the feature is supposed to do and why — used to spot logic vulnerabilities (application not following its own intended business rules). Technical design is implementation-level (languages, DBs, third-party services, data flow diagrams, network config, auth/authz mechanisms, schema) — used to spot conventional vulnerabilities and connect them to specific components.

## Key Concepts
- **Threat actor**: An archetypal category of potential attacker (human or machine), each with a distinct attack surface and permission level; must include internal, external, and machine/script users, not just external humans.
- **Attack vector**: A potential (not yet confirmed) pathway by which a threat actor could attack the system, identified before the system is even fully built.
- **Existing mitigation**: A security control already in place that addresses a specific attack vector; must be documented before deciding a new mitigation is needed.
- **Delta**: The gap between identified attack vectors and existing mitigations — the set of attack vectors with no adequate defense yet, and the threat model's actionable output.
- **Logic vulnerability**: A vulnerability arising from the application failing to enforce its own intended business rules (e.g., accepting a review score outside its valid 0-5 range), as distinct from a generic technical vulnerability class.
- **Worst-case vs. best-case modeling**: Threat modeling must assume the worst-case scenario (internal actors get compromised, scripts malfunction) rather than the best-case assumption that only intended functionality will ever be invoked.
- **Data flow diagram (DFD)**: A technical-design artifact showing how data moves between modules, including format and encryption in transit — a key input to attack-vector brainstorming.

## Mental Models
- Treat a threat model as a living document, not a one-time exercise: it should be revisited and updated whenever a feature's scope changes, re-running the threat-actor, attack-vector, and delta steps.
- Use "risks are not actionable until existing mitigations are known" as a hard rule: never propose a new mitigation for an attack vector before confirming whether one already exists — duplicated mitigations add technical debt and can introduce new bugs.
- Always model worst-case, not best-case: assume internal users get hacked or go rogue, and machine users malfunction or have bugs — this is why the review-aggregator script and the admin user both appear as first-class threat actors alongside external hackers.
- Think of logic design and technical design as two lenses on the same feature: technical design alone tells you *how* it's built (useful for classic vulnerabilities); logic design tells you *what it's supposed to do* (necessary for spotting business-logic violations that no automated scanner would flag).

## Anti-patterns
- **Threat modeling as a rushed compliance checkbox**: A hasty or improper implementation "does nothing but check boxes and waste valuable time" — the framework only pays off with disciplined execution.
- **Skipping mitigation documentation and jumping straight to "fixes needed"**: Risk is not actionable until you know what's already mitigated; skipping this step risks duplicate or conflicting fixes.
- **Only considering external human attackers**: Ignoring internal users (admins, support staff) and machine/script users (scheduled jobs, aggregators) misses a major category of real-world attack vectors, as the MegaBank example's admin and review-aggregator-script rows show.
- **Modeling best-case usage only**: Assuming users will only invoke intended functionality ignores compromised accounts, rogue insiders, and malfunctioning automation.
- **Skipping logic design collection**: Technical design alone finds classic vulnerabilities but misses logic vulnerabilities unique to the specific business rules of the feature.

## Code Examples
This is a process/methodology chapter; no header or config syntax is introduced. The closest artifacts are the worked-example tables reproduced under Reference Tables and Worked Example below.

## Reference Tables
**Table 24-1 (abridged). Potential threat actors — MegaBank user reviews feature**

| Threat actor | Powers/permissions, risk |
|---|---|
| User admin | Read/update DB via admin UI; could steal PII or modify ratings; usage not logged — no accountability |
| Customer support user | Read-only DB access; could steal PII |
| Review aggregator script | Runs periodically to average scores; has DB-admin access; if compromised, could run any query |
| Authenticated user | Can post reviews/scores; could bypass the web form to POST malicious payloads (e.g., SQLi, out-of-range score) |
| Unauthenticated (guest) user | Read-only; low risk barring DoS or circular graph queries |

**Table 24-2/24-4 (abridged). Attack vectors and post-mitigation delta**

| Threat name | Severity | Threat actor | Mitigated? |
|---|---|---|---|
| Improper validation - score | P1 | All except guest | Yes (validation logic) |
| SQL injection | P0 | All except guest | Yes (DSL forces prepared statements) |
| Information disclosure - FeatureID | P3 | All users | No -> delta |
| GraphQL circular/large queries | P1 | All users | No -> delta |
| GraphQL introspection/errors | P1 | All users | No -> delta |
| High privilege user attacks | P0 | Admin, aggregator script | No -> delta |

## Worked Example
MegaBank is launching a "user review" feature letting authenticated users post a 0-5 score and text review against existing features. Security engineer Holly Hacker runs the full five-goal process. **Logic design**: a plain-language description of the feature's intended behavior — reviews stored server-side, queryable via "show reviews" on feature pages — which immediately surfaces a logic vulnerability (a user bypassing the web form to POST a score outside 0-5, skewing aggregates and damaging trust). **Technical design**: React components `getReviews`/`createReview`, an AWS EC2 Express REST server, PostgreSQL storage, session-cookie auth check on write, TLS 1.3 via Let's Encrypt, and an optional GraphQL query layer — this surfaces classic vulnerability candidates: unclear XSS-safe rendering of review text, unclear SQL-query construction for user-submitted strings, and information disclosure via a "no reviews found for chosen feature" error on unreleased features. **Threat actors**: five archetypes are tabled (admin, support user, review-aggregator script, authenticated user, guest user), explicitly including the non-human aggregator script because it holds direct database-admin access. **Attack vectors**: cross-referencing logic + technical design + threat actors produces six ranked vectors (P0-P3), including SQL injection, improper score validation, FeatureID information disclosure, GraphQL circular/large queries, GraphQL introspection/error leakage, and high-privilege-user attacks. **Existing mitigations**: only two of the six already have coverage — validation logic (rejects non-integer or out-of-range scores) and a SQL-injection-safe DSL forcing prepared statements. **Delta**: subtracting mitigated vectors leaves four open items — FeatureID disclosure, GraphQL circular/large queries, GraphQL introspection/errors, and high-privilege-user attacks — each of which is then assigned a new mitigation (generic error messages; GraphQL compute-time limits; disabling introspection and suppressing internal GraphQL errors; and reworking privileged tokens to be scoped, off-platform-logged, and column-restricted for the aggregator script) before the feature is cleared to launch.

## Key Takeaways
1. Run all five goals (document, threat actors, attack vectors, mitigations, delta) together — a partial threat model is far less valuable than a complete one.
2. Collect both logic design and technical design; logic design alone catches business-rule violations no scanner will find.
3. Enumerate threat actors broadly: internal, external, and machine/script users, split by auth state where relevant.
4. Never propose a new mitigation before confirming whether one already exists for that attack vector.
5. Always model worst-case scenarios — assume internal actors and automation can be compromised or malfunction.
6. Treat the delta (unmitigated attack vectors) as the actionable launch-blocking output of the exercise.
7. Revisit and re-run the threat model whenever feature scope changes — it's a living document, not a one-time artifact.

## Connects To
- **Chapter 36 (Secure Application Architecture)**: The "analyze feature requirements for risk" step there is the seed of this chapter's logic-design/technical-design collection process.
- **Chapter 38 (Secure User Experience)**: The MegaBank example's "information disclosure - FeatureID" attack vector is the same class of error-message risk covered in depth there.
- **Chapter 40 (Reviewing Code for Security)**: Threat modeling happens before code is written; code review is the corresponding verification step once code exists, checking that the delta's mitigations were actually implemented.
- **NIST cost-of-fix estimate**: The chapter closes by citing the same architecture-phase cost advantage as Chapter 36 (10 hours of architecture-phase fixes vs. 100 hours post-launch).
