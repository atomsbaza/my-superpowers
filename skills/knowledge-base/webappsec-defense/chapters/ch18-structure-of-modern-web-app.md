# Chapter 18: The Structure of a Modern Web Application

## Core Idea
Modern web applications are actually multiple separate-but-symbiotic applications (client, API, database, CDN) communicating over well-defined protocols rather than a single monolith, and each of these common technologies carries its own recognizable fingerprints and security implications worth mastering before doing recon.

## Frameworks Introduced
- **REST architectural constraints**: A REST API must (1) be separate from the client, (2) be stateless, (3) be easily cacheable, (4) expose each endpoint as a specific object/resource acted on via HTTP verbs.
  - When to use: Identifying whether an observed API follows REST conventions, which predicts its likely endpoint/verb structure.
  - How: Look for hierarchical resource URLs (`/moderators/joe/logs/12_21_2018`), tokenized auth sent per-request (statelessness), and consistent verb-to-CRUD mapping.
- **Client vs. server responsibility split**: Reason about a web app as (at minimum) a browser client, one or more API servers, and one or more databases, each independently fingerprintable and independently exploitable.
  - When to use: Whenever mapping an application's architecture during recon.
  - How: Identify the client's SPA framework/JS libraries, the server's web-server software and language, and the database technology in use — each has distinct detection techniques (Ch19-21 build on this).
- **Secure-default DOM-write pattern**: Centralize any raw HTML injection into the DOM behind a single utility function with an explicit, off-by-default "unsafe" flag, rather than writing to `innerHTML` ad hoc throughout the codebase.
  - When to use: Any client code that renders user- or server-supplied data into the DOM.
  - How: Default to `element.innerText` (safe); only use `element.innerHTML` via a sanitizer (e.g., DOMPurify) when an explicit `unsafe=true` flag is passed, placed last in the function signature so it's not flipped by accident.

## Key Concepts
- **Statelessness (REST)**: The API must not remember anything about the requester between calls; authorization must instead be tokenized and re-sent on every request.
- **Prototypal inheritance / Prototype Pollution**: JavaScript objects inherit via a mutable `prototype` chain rather than fixed classes; because prototype changes propagate live to all child objects, attackers can exploit unintended prototype mutation to alter app-wide behavior.
- **Same Origin Policy (SOP) enforcement on local storage**: Browser-managed `localStorage`/`sessionStorage` are isolated per-origin, but poorly architected apps may still leak sensitive tokens into them.
- **GraphQL**: A query language that wraps existing REST endpoints, letting a client request specific fields, aliases, and combined operations in a single network round-trip instead of several REST calls.
- **Authentication vs. authorization**: Authentication verifies *who* a user is (e.g., HTTP Basic/Digest, OAuth); authorization determines *what* the verified user may access — conflating the two, or reimplementing authorization per-API instead of centralizing it, is a common source of vulnerabilities.
- **CI/CD and VCS as an attack surface**: Git-based version control and automated deployment pipelines (triggered on push) are now part of an application's security perimeter, not just its code.
- **CDN/cache staleness risk**: Offloading static content to a CDN or various cache layers introduces the risk of stale caches leaking privileged information or serving outdated authorization data.

## Mental Models
- Think of a modern app as three loosely coupled systems (client, API, database) each with its own tech stack and its own fingerprinting technique — recon should treat them as three separate targets, not one.
- Use "one centralized authorization class" as the litmus test for architectural maturity: if authorization checks are reimplemented per-API rather than centralized, expect at least one endpoint to have a human-error gap.
- Treat JavaScript's `var`/`let`/`const` and callback/promise/async evolution as a proxy for a codebase's age and quality — heavy reliance on global/`var`-scoped state and callback pyramids often correlates with legacy, less-reviewed code paths.

## Anti-patterns
- **Reimplementing authorization per-endpoint**: Manual, per-API authorization checks are prone to being forgotten or inconsistently applied on at least one endpoint; centralize authorization logic instead.
- **Unmodified default error pages/headers**: Leaving default framework 404 pages or `X-Powered-By`/`X-AspNet-Version` headers enabled hands fingerprinting data directly to attackers (detailed further in Ch21).
- **Ad hoc `innerHTML` writes scattered through client code**: Without a single, sanitizer-gated write path, every scattered DOM-write call site is a separate opportunity for an XSS gap.
- **Treating SQL/NoSQL query construction as risk-free**: Injection-style attacks apply to *any* database once an attacker learns its query model, not just classic SQL.

## Code Examples
```javascript
// Secure-default DOM injection pattern
import { DOMPurify } from '../utils/DOMPurify';

const appendToDOM = function (data, selector, unsafe = false) {
  const element = document.querySelector(selector);
  if (unsafe) {
    element.innerHTML = DOMPurify.sanitize(data);
  } else {
    element.innerText = data; // safe default
  }
};
```
- **What it demonstrates**: Centralizing DOM writes behind a function with an explicit, last-position, off-by-default `unsafe` flag dramatically reduces the odds of an accidental XSS-causing `innerHTML` write.

```javascript
// Prototype propagation — the mechanism behind Prototype Pollution
const Vehicle = function (make, model) {
  this.make = make;
  this.model = model;
};
const prius = new Vehicle('Toyota', 'Prius');
const charger = new Vehicle('Dodge', 'Charger');

// getMaxSpeed() doesn't exist yet on either instance
Vehicle.prototype.getMaxSpeed = function () { return 100; };

// both existing instances are updated live, because prototypes
// propagate from parent to children at any point at runtime
prius.getMaxSpeed();   // 100
charger.getMaxSpeed(); // 100
```
- **What it demonstrates**: Why JavaScript's live, mutable prototype chain is powerful but also the mechanism attackers exploit in Prototype Pollution — a parent object mutation changes all children's behavior retroactively.

## Reference Tables
Client/server-side databases and their characteristic risk profile:

| Database type | Examples | Query risk |
|---|---|---|
| SQL | PostgreSQL, MySQL, SQL Server, SQLite | Classic SQL injection when queries are not parameterized |
| NoSQL (document) | MongoDB, DocumentDB, CouchDB | Injection-style attacks once query model is learned; less efficient at aggregation |
| Search-specific | Elasticsearch | Must stay synchronized with main DB; sync gaps are a data-consistency/security risk |

Authentication schemes referenced in this chapter (expanded fully with strengths/weaknesses in Ch20's Table 5-2):

| Scheme | Mechanism |
|---|---|
| HTTP Basic Auth | Base64 username:password sent every request |
| HTTP Digest Auth | Hashed username:realm:password sent every request |
| OAuth | Bearer token issued by a trusted third-party identity provider |

## Worked Example
The chapter's REST vs. SOAP/XML comparison is the clearest end-to-end example:

1. **Legacy pattern (SOAP/XML)**: A user object is transmitted as a verbose XML payload:
   ```xml
   <user>
     <username>joe</username>
     <password>correcthorsebatterystaple</password>
     <email>joe@website.com</email>
   </user>
   ```
2. **Modern pattern (REST/JSON)**: The same data, using JSON — lighter, native to JavaScript, and requiring less parsing:
   ```json
   { "username": "joe", "password": "correcthorsebatterystaple", "email": "joe@website.com" }
   ```
3. **Why it matters for recon**: Because REST APIs are stateless, hierarchical, and verb-driven, once you observe `GET /moderators/joe`, you can *predict* that `PUT /moderators/joe` (modify) and `DELETE /moderators/joe/logs/12_21_2018` (delete a specific log) likely also exist — self-documenting API shape is both a developer convenience and a recon accelerant.
4. **The security payoff**: Recognizing REST conventions lets a tester generate a hypothesis-driven list of likely-valid endpoint/verb combinations to probe (formalized as a technique in Ch20's API Analysis chapter), rather than blindly brute-forcing URL space.

## Key Takeaways
1. Decompose any target application into client, API, and database layers — each has distinct, learnable fingerprinting techniques.
2. REST's stateless, hierarchical, verb-driven design makes API shape predictable once a single endpoint is observed — use this to accelerate endpoint discovery.
3. Centralize authorization logic; per-endpoint reimplementation is a reliable source of at least one missed check.
4. Centralize and sanitizer-gate all DOM-injection call sites behind a secure-by-default utility rather than scattering `innerHTML` writes.
5. JavaScript's mutable, live prototype chain is both a productivity feature and the root cause of Prototype Pollution vulnerabilities.
6. CI/CD pipelines and VCS hosting are now part of the application's security perimeter, not just an engineering convenience.
7. CDN/cache layers introduce staleness risk that can leak privileged or outdated data — treat cache invalidation as a security-relevant operation.

## Connects To
- **Ch19-23 (this book's Recon material, global)**: This chapter's technology inventory (REST, SPA frameworks, JS libraries, web servers, databases) is exactly what Ch19 (subdomains), Ch20 (API analysis), and Ch21 (dependency fingerprinting) each teach you to detect and version-fingerprint in practice.
- **Ch24-34 (Offense, global)**: Prototype Pollution, SQL/NoSQL injection, and XSS via unsanitized DOM writes — all introduced conceptually here — become fully worked attack chapters in Offense.
- **Ch35-52 (Defense, global)**: The centralized-authorization and secure-default-DOM-write patterns here are exactly the architectural countermeasures elaborated in Defense.
- **GraphQL security (external concept)**: The query-batching power described here has its own dedicated security literature (query depth/complexity limiting) referenced but not fully covered in this chapter.
