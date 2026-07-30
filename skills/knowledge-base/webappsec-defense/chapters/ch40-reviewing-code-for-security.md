# Chapter 40: Reviewing Code for Security

## Core Idea
Security code review must happen after architecture review (never before), should be performed by an ideally unrelated reviewer at merge-request time, needs a deliberate starting point (client -> API -> dependencies -> unexposed APIs -> remainder) to avoid wasted effort on low-risk code, and must watch for four recurring anti-patterns — blocklists, boilerplate code, trust-by-default, and client/server coupling — that look like solutions but aren't.

## Frameworks Introduced
- **Client-First Review Ordering**: A prioritized path through an unfamiliar codebase for security review.
  - When to use: Whenever reviewing an application you didn't design (consulting, existing products, or just an unfamiliar internal codebase) and don't yet know which components are highest risk.
  - How: (1) Review client-side code first to learn business logic and user-facing functionality. (2) Follow the client's API calls back to the server, evaluating those specific endpoints. (3) Trace the dependencies those APIs rely on — databases, helper libraries, logging, uploaded files, conversion libraries. (4) Look for public-facing APIs not directly called by the client — accidentally exposed or future-feature endpoints. (5) Cover the remainder of the codebase, now with organic familiarity, prioritized by risk.
- **Archetypal vs. Business Logic Vulnerability Distinction**: A framework for recognizing that generic vulnerability classes (XSS, CSRF, injection) are necessary but not sufficient to find in review.
  - When to use: Any security code review, especially on features with nontrivial custom business rules.
  - How: Gain context on the feature's users, functionality, and business impact before reviewing; use that context to look specifically for logic bugs that violate the feature's own intended rules (e.g., an API accepting a client-supplied `isMember: true` flag) — these will not be caught by scanners tuned only for archetypal vulnerability patterns.
- **Local Review Flow**: The mechanical git-based starting sequence for any code review, functional or security.
  - When to use: At the start of any merge-request review.
  - How: `git checkout main`; `git pull origin main`; `git checkout <username>/feature`; `git diff origin/main...` to get the file list and line-level diff that the rest of the review builds on.

## Key Concepts
- **Blocklist anti-pattern**: A denylist-based filter (e.g., blocking known-bad domains) that only protects against known-bad inputs and fails against anything not yet catalogued — inherently incomplete and temporary.
- **Allowlist**: The preferred alternative to a blocklist — permits only explicitly approved inputs, at the cost of ongoing (partially automatable) maintenance.
- **Boilerplate code anti-pattern**: Shipping default framework/library configuration to production without hardening it, because many frameworks ship permissive-by-default rather than secure-by-default.
- **Trust-by-default anti-pattern**: Running all application functionality (logging, disk I/O, database access) under one shared, broadly-privileged OS user, so a single vulnerability compromises every resource that user can touch.
- **Client/Server Separation (violation)**: Tight coupling between client and server code (e.g., server-rendered templates carrying authentication logic) that removes the predefined-data-format boundary a distributed design would otherwise enforce.
- **Logic vulnerability (recap)**: A vulnerability specific to a feature's own business rules, requiring context beyond generic vulnerability-pattern knowledge to find.
- **Merge-request-time review**: The point at which the full scope of a feature can be reviewed in one sitting, as opposed to per-commit or pair-programming review styles that only ever see a partial slice.

## Mental Models
- Treat the client-first review order as building a map before exploring the territory: reviewing client code first tells you what functionality *exists* and what data flows *where*, so the API and dependency review that follows is targeted rather than exhaustive-and-blind.
- Think of a blocklist as "protecting against yesterday's attackers" — it only works under perfect (and impossible) knowledge of every current and future bad input; an allowlist inverts the default to "protect against everyone except today's approved list."
- Use the MongoDB internet-accessible-by-default incident as the canonical boilerplate-code warning: a framework/database's out-of-the-box configuration is not a security decision someone made for you — it's frequently the opposite, and shipping it unreviewed is a choice, not a neutral default.
- Model OS-level permissions the way the chapter models modules: one compromised module (SQL access) should never cascade into compromise of unrelated modules (logging, disk) — achieved by giving each module its own least-privilege OS user rather than one shared account.

## Anti-patterns
- **Blocklists as a permanent solution**: `const blocklist = ['http://www.evil.com', ...]` only blocks known-bad domains; a hacker simply registers a new one. Acceptable only as a stopgap with a pre-planned timeline toward a complete (allowlist) solution.
- **Trusting default framework/library configuration in production**: The MongoDB internet-accessible-by-default misconfiguration led to mass Bitcoin-ransom hijackings of tens of thousands of databases; Ruby on Rails boilerplate 404 pages and EmberJS default landing pages leak framework/version information similarly.
- **Running all application functionality under one shared OS user**: A vulnerability in any one module (e.g., SQL access) cascades into compromise of every resource (logs, disk, DB) that shared user can reach.
- **Coupling client and server code tightly** (e.g., server-rendered HTML carrying auth logic): Forces the server to parse and secure arbitrary HTML/script content instead of a predefined, restricted data format, multiplying the surface area that must be defended.
- **Reviewing security before architecture is reviewed**: The chapter states architecture review must always precede code review in a security-conscious organization — reviewing code first wastes effort fixing implementations of a still-flawed design.

## Code Examples
```js
const blocklist = ['http://www.evil.com', 'http://www.badguys.net'];
/*
 * Determine if the domain is allowed for integration.
 */
const isDomainAccepted = function (domain) {
  return !blocklist.includes(domain);
};
```
- **What it demonstrates**: The blocklist anti-pattern — looks like a solution but only excludes known-bad domains, leaving all undiscovered or future-registered malicious domains implicitly trusted.

```js
const allowlist = ['https://happy-site.com', 'https://www.my-friends.com'];
/*
 * Determine if the domain is allowed for integration.
 */
const isDomainAccepted = function (domain) {
  return allowlist.includes(domain);
};
```
- **What it demonstrates**: The corrected allowlist approach — inverts the default to deny-unless-explicitly-approved, requiring a new domain *and* business license for a malicious actor to get back in even after removal.

## Reference Tables
| Anti-pattern | Why it looks like a solution | Why it fails |
|---|---|---|
| Blocklist | Actively excludes known-bad inputs | Requires perfect knowledge of all current and future bad inputs; trivially bypassed (buy a new domain) |
| Boilerplate code | Framework/library "just works" out of the box | Frameworks often ship permissive, not secure, by default (MongoDB, Rails, EmberJS examples) |
| Trust-by-default | Simpler to run everything under one service account | One compromised module cascades to every resource that account can reach |
| Client/Server coupling | Faster to build with shared templating/logic | Multiplies the data formats/languages the server must defend against; removes a clean trust boundary |

**Review ordering (summary)**
| Step | Focus |
|---|---|
| 1 | Client-side code — business logic and user-facing functionality |
| 2 | API layer — endpoints the client actually calls |
| 3 | Dependencies — databases, helper libraries, logging, file uploads |
| 4 | Unexposed/future-facing public APIs |
| 5 | Remainder of the codebase, by descending risk |

## Worked Example
MegaBank is building MegaChat, a social-media feature with three roles: default user (text posts only), member (text + video/games/artwork, gated because hosting is expensive and to deter freeloaders/bots), and moderator (member functionality plus moderation, including upgrading users to members). A reviewer applies the archetypal-vs-business-logic framework: an archetypal vulnerability would be a plain XSS bug in a user's post — findable by generic scanning knowledge. A business logic vulnerability would be an API endpoint that trusts a client-supplied `isMember: true` field on a post request, letting any default user upload video/games/artwork without ever being approved by a moderator — a bug invisible to any generic vulnerability scanner because it only makes sense in light of MegaChat's specific role/permission business rules (derived from the requirements: three roles, role-gated functionality, and the explicit business reason — hosting cost and anti-freeloader/anti-bot policy — for gating membership in the first place). The reviewer starts, per the client-first ordering, by reading the client code for the post-creation flow to understand what fields it's supposed to send, then follows that call to the server-side API endpoint to check whether the server independently re-verifies membership status server-side rather than trusting whatever the client claims — exactly the kind of trust-by-default-adjacent gap the ordering and the archetypal/logic distinction are designed to surface together.

## Key Takeaways
1. Never review code for security before the underlying architecture has been reviewed — architecture review always comes first.
2. Start an unfamiliar codebase review at the client, then follow calls to the API, then dependencies, then unexposed APIs, then the remainder by risk.
3. Look specifically for business-logic vulnerabilities (context-dependent) in addition to archetypal vulnerability classes (XSS, CSRF, injection) — the former require understanding the feature's own rules.
4. Replace blocklists with allowlists; treat any blocklist in review as, at best, a temporary stopgap needing a completion plan.
5. Never trust framework/library default configuration in production without explicit review — defaults are often permissive, not secure.
6. Give each application module its own least-privilege OS user so a single compromised module doesn't cascade into others.
7. Keep client and server code and data formats strictly separated; treat tight coupling (e.g., server-rendered auth-bearing templates) as a red flag during review.

## Connects To
- **Chapter 35 (Securing Modern Web Applications)**: This chapter is the direct expansion of that chapter's four-question code-review checklist and "unrelated team" review principle.
- **Chapter 39 (Threat Modeling Applications)**: Threat modeling identifies attack vectors and mitigations before code exists; this chapter's review process is the verification step confirming those mitigations were actually implemented, plus catching anything threat modeling missed.
- **Chapter 36 (Secure Application Architecture)**: The chapter explicitly states architecture review (Chapter 36-adjacent) must precede code review — this is the mandatory ordering between the two chapters.
- **OWASP Top 10 / generic vulnerability taxonomies**: External reference point for what counts as an "archetypal vulnerability" as opposed to a business-logic vulnerability unique to one application.
