# Patterns

## Allow-list Input Validation
**When to use**: Any point where untrusted input determines behavior (form fields, file uploads, query parameters, regex against user data).
**How**: Define the explicit set of permitted values/patterns/formats and reject everything else, rather than trying to enumerate forbidden values. For files, validate by magic bytes, not extension.
**Trade-offs**: Requires knowing the legitimate input space upfront; can reject valid-but-unanticipated input if the allow list is too narrow. Still strictly safer than a block list, which can never anticipate novel bypass techniques. (Ch4, Ch11, Ch12, Ch25, Ch31, Ch40, Ch46)

## Context-Specific Output Escaping
**When to use**: Any point where dynamic data is rendered into HTML, injected into a DB query, or interpolated into a shell/OS command.
**How**: Escape at the point of interpretation using the correct escaper for that context (HTML entity encoding, DB parameterization, shell-safe array APIs) — never a single generic "sanitize" function for all contexts.
**Trade-offs**: Requires discipline to escape at every sink, not just once at the boundary; auto-escaping template engines reduce risk but any explicit disable (`| safe`, `dangerouslySetInnerHTML`) becomes a high-priority review flag. (Ch4, Ch6, Ch25, Ch43)

## Parameterized/Prepared Statements
**When to use**: Every SQL, NoSQL, or LDAP query built with any untrusted input.
**How**: Use placeholders (`?`, `%s`, named params) bound separately from the query template; never concatenate untrusted strings into query syntax, including in ORM raw-query escape hatches.
**Trade-offs**: Slightly more verbose than string interpolation; some dynamic clauses (e.g. `ORDER BY column`) can't be parameterized and need allow-list validation instead. (Ch4, Ch12, Ch28, Ch31, Ch46)

## Anti-CSRF Token + SameSite Cookie (layered)
**When to use**: Any state-changing (POST/PUT/DELETE) endpoint reachable by an authenticated browser session.
**How**: Issue an unpredictable, session-bound token embedded in forms/headers and verified server-side; additionally set `SameSite=Lax` or `Strict` on session cookies. Never rely on SameSite alone — older browsers and edge cases don't enforce it.
**Trade-offs**: Requires token plumbing through every form/AJAX call; stateless token variants (user ID + timestamp + server-key HMAC) avoid session-store lookups but need clock-skew tolerance. (Ch6, Ch11, Ch26, Ch29, Ch44)

## Defense in Depth (layered independent controls)
**When to use**: Any high-value asset or action (auth, payments, admin functions) where a single control's failure would be catastrophic.
**How**: Stack multiple independent protections (e.g., input validation + parameterization + least-privilege DB user + WAF) so that bypassing one still leaves others intact.
**Trade-offs**: More engineering and operational overhead per protected asset; reserve for genuinely high-value targets rather than applying uniformly everywhere. (Ch4, Ch5, Ch35)

## Field Allowlisting Before Bind/Write (anti mass-assignment)
**When to use**: Any endpoint that accepts a JSON/form payload and writes it to a database record or in-memory object.
**How**: Explicitly enumerate which fields may be set from the request (a Data Transfer Object or manual field-by-field copy); never do a generic recursive merge or whole-object bind.
**Trade-offs**: More boilerplate per endpoint than `Object.assign`-style binding; the alternative (prototype pollution, privilege-field injection like `isAdmin`) is a serious vulnerability class. (Ch11, Ch15, Ch16, Ch30, Ch31, Ch33, Ch48, Ch49)

## Disable External Entity Resolution in XML Parsers
**When to use**: Any XML parsing of untrusted input, in any language/library.
**How**: Explicitly disable DOCTYPE/external-entity processing (e.g., `disallow-doctype-decl`); never assume it's off by default — Java parsers in particular default to enabled.
**Trade-offs**: None significant — legitimate use cases for external entities in user-facing XML are rare; prefer JSON over XML entirely where the format choice is still open. (Ch11, Ch12, Ch27, Ch30, Ch45)

## Timing-Safe / Enumeration-Resistant Responses
**When to use**: Login, signup, and password-reset flows.
**How**: Return identical response messages and near-identical response times regardless of whether the account/resource exists (e.g., always compute a dummy password hash even for a nonexistent user).
**Trade-offs**: Slightly worse UX (can't tell users "that email isn't registered"); necessary to prevent enumeration and timing side-channel attacks. (Ch8, Ch10, Ch23, Ch38)

## Secure Session Cookie Configuration
**When to use**: Any session-identifying cookie.
**How**: Set `Secure` + `HttpOnly` + explicit `SameSite`; generate IDs with a cryptographically secure RNG; never accept a client-suggested session ID (prevents fixation); never pass session IDs in URLs.
**Trade-offs**: None — this is a baseline, not an optional hardening step. (Ch2, Ch9, Ch22, Ch37)

## CSP with No `unsafe-inline`/`unsafe-eval`
**When to use**: Every HTML-serving application, as a second XSS defense layer behind output escaping.
**How**: Set CSP as an HTTP header (not a `<meta>` tag); use `script-src 'self'` plus nonces/hashes for any inline scripts that are unavoidable; omit `unsafe-inline` and `unsafe-eval`.
**Trade-offs**: Can require refactoring inline event handlers/scripts; the payoff is that even a successful injection often can't execute. (Ch2, Ch6, Ch22, Ch28, Ch37, Ch43)

## Frame-Ancestors CSP Directive (Clickjacking Defense)
**When to use**: Any page that shouldn't be embeddable in a third-party iframe.
**How**: Set `Content-Security-Policy: frame-ancestors 'none'` (or a specific allow-list); use `X-Frame-Options: DENY` only as a legacy fallback for very old browsers.
**Trade-offs**: None if the page genuinely shouldn't be framed; if legitimate embedding is needed, allow-list specific origins rather than disabling the control entirely. (Ch6, Ch34, Ch49)

## Dependency Manifest + Automated CVE Auditing
**When to use**: Every project with third-party dependencies (i.e., virtually all of them).
**How**: Keep manifest/lock files in source control (pinning transitive dependencies too); run an automated per-language audit tool (npm audit, Snyk, Bandit, bundler-audit, etc.) regularly; risk-assess before patching rather than patching blindly or deferring indefinitely.
**Trade-offs**: Requires ongoing maintenance investment; the alternative (unpatched/unpinned dependencies) is one of the most common real-world breach vectors. (Ch5, Ch13, Ch17, Ch21, Ch32, Ch35, Ch50)

## Threat Modeling — Five-Goal Framework
**When to use**: Before building a new feature/system, and periodically for existing high-value systems.
**How**: (1) Document existing knowledge of the system's logic and technical design, (2) identify threat actors (internal, external, and machine/script users), (3) identify attack vectors and score severity, (4) identify existing + needed mitigations, (5) identify the delta between current and needed state.
**Trade-offs**: Time-intensive for large systems; most valuable when done at the architecture phase, where fixes are cited as 30-60x cheaper than post-production fixes. (Ch24, Ch39)

## CVSS-Based Vulnerability Scoring
**When to use**: Triaging any discovered or reported vulnerability.
**How**: Score Base metrics (Attack Vector, Attack Complexity, Privileges Required, User Interaction, Scope, Confidentiality/Integrity/Availability impact); adjust with Temporal/Environmental metrics; reproduce in staging before finalizing the score; require a regression test before closing.
**Trade-offs**: Adds process overhead per bug; without it, severity judgments become inconsistent and low-severity-looking-but-actually-critical bugs get deprioritized. (Ch27, Ch42)

## Blameless Postmortem / Incident Response Sequence
**When to use**: After any security incident, regardless of severity.
**How**: Stem the bleeding → stabilize → assess damage → run digital forensics reconstructing a timeline from logs/commits → hold a no-fingerpointing postmortem focused on process fixes → communicate transparently to affected users → optionally publish a `security.txt` disclosure channel to de-escalate future incidents.
**Trade-offs**: Requires cultural buy-in (no blame) to get honest information during forensics; skipping steps (esp. transparent communication) erodes user trust more than the breach itself. (Ch15, Ch20, Ch41)
