# Chapter 38: Secure User Experience

## Core Idea
The UI layer is both a source of security risk (information disclosure, enumeration) and an underused opportunity to improve security: error messages and API responses must be deliberately generic and allowlisted rather than raw, and "light patterns" can nudge users toward safer choices at the exact moment a risky action is taken, without forcing secure-by-default friction on everyone.

## Frameworks Introduced
- **Error Message Security Spectrum**: A five-point scale for how much detail to disclose to a user on failure, from most to least risky.
  - When to use: Any time a form, API, or auth flow needs to surface a failure to the end user.
  - How: Choose along the spectrum — (1) reflect the raw server error/code, (2) reflect the server error/code only if it matches a predefined allowlist, (3) show a client-determined generic message plus the server code, (4) show only the server code, (5) show nothing. Prefer option (2): allowlisted generic messages balance usability against information disclosure risk better than either raw reflection or total silence.
- **Enumeration-Resistant Design (three criteria)**: A checklist for preventing an attacker from combining many small, individually-harmless responses into a valuable disclosure.
  - When to use: Any endpoint that responds differently based on the existence/validity of an input (usernames, IDs, auth attempts).
  - How: (1) Use generic errors for all related failure cases (e.g., OWASP's single "authentication failed" message instead of distinguishing bad username vs. bad password). (2) Avoid predictable/sequential identifiers (sequential user IDs, numbered API endpoints) that make brute enumeration trivial. (3) Rate-limit any endpoint where repeated querying could leak information, capped near the upper bound of legitimate usage.
- **Light Patterns**: The inverse of a dark pattern — a UI nudge that gently guides users toward better security/privacy choices, placed at the point of risky action rather than buried in documentation.
  - When to use: When a valuable security feature exists but is opt-in and under-adopted, and true secure-by-default isn't feasible.
  - How: Do not rely on documentation next to a settings toggle (most users won't read it). Instead, surface the reminder repeatedly at the moment the user is about to perform the risky action itself (e.g., every outgoing transaction), where the user has direct, immediate familiarity with the consequence being warned about.

## Key Concepts
- **Information disclosure (UX layer)**: Leaking application/server state through overly detailed error messages, even when done with good UX intentions.
- **Enumeration vulnerability**: A class of vulnerability where many individually low-risk queries, or their combination, reveal information the client was never meant to access.
- **Dark pattern**: A UI design pattern that tricks users into invoking functionality they didn't intend, typically degrading their security or privacy (external/Wikipedia-sourced definition).
- **Light pattern (author-coined)**: The deliberate opposite of a dark pattern — a gentle nudge toward a more secure/private choice, distinguished from mere documentation by being contextual and repeated at risk-relevant moments.
- **Generic error code (e.g., 400, or "418 I'm a teapot")**: Returning a non-specific HTTP status to avoid giving recon information via fine-grained error codes.
- **Secure by default**: The superior alternative to light patterns — forcing the secure setting on rather than nudging the user to opt in — used whenever feasible.
- **Blast-radius limiting**: Capping the maximum damage a compromise can cause (e.g., a daily withdrawal cap) so a stolen credential doesn't grant unlimited abuse.

## Mental Models
- Think of every error message as sitting on a dial between "maximally helpful to the user" and "maximally safe from disclosure" — the correct setting is rarely either extreme; an allowlisted generic message is usually the sweet spot.
- Treat enumeration as "information disclosure by accumulation": no single response leaks much, but a thousand slightly-different responses (wrong password vs. user does not exist) can be aggregated into a working attack, exactly as MegaBank's admin-panel enumeration example shows.
- Use light patterns like a seatbelt reminder chime, not a seatbelt lock: place the security reminder exactly where and when the risky action is about to happen (an outgoing transaction), not in a settings page the user visits once and never again.
- When choosing between documentation and a light pattern, assume most users will never read the documentation in full — design the light pattern to work for the users who don't.

## Anti-patterns
- **Reflecting raw server errors or database messages to the client**: Discloses application/server internals (e.g., a full address in an error string) that aid fingerprinting and further attacks.
- **Distinguishing "wrong password" from "user does not exist"**: Enables the classic username-enumeration attack chain (breach-derived usernames -> enumerate valid accounts -> targeted password attack).
- **Sequential/predictable identifiers** (numbered API endpoints, sign-up-date-derived user IDs): Makes enumeration and total-user-count disclosure trivial.
- **No rate limiting on enumeration-prone endpoints**: Removes the last practical barrier to large-scale automated enumeration even when messages are generic.
- **Placing a security nudge only on the settings page as documentation**: Most users never read it in full; it fails to change behavior compared to a light pattern surfaced at the moment of risk.

## Code Examples
This chapter is UX/behavioral rather than syntax-driven; no headers or config snippets are introduced. The closest artifact is the contrast between raw and generic error messages:

```
Raw:     "the user Jonathan Smith could not be queried because the address
          905 N. Main St. provided does not match the current file."

Generic: "The user could not be queried due to an address mismatch."
```
- **What it demonstrates**: An allowlisted generic error message preserves the useful "reason" category for the user (address mismatch) while stripping the disclosed name and address.

## Reference Tables
| Error disclosure option | Security | Usability |
|---|---|---|
| Reflect raw server error + code | Lowest | Highest |
| Reflect error + code only if allowlisted | Balanced (recommended) | High |
| Client-generic message + server code | Good | Medium |
| Server code only | Better | Low |
| Nothing at all | Highest (technically) | Lowest |

## Worked Example
A hacker targets a MegaBank internal admin interface not meant to be internet-exposed. Unable to breach authentication directly, the hacker notices the login endpoint distinguishes "wrong password" from "user does not exist" — an enumeration bug. The hacker collects breach dumps from unrelated hobby-forum and ecommerce sites containing usernames/emails, filters for `@megabank.com` addresses, and feeds each into the admin login form. Every response of "wrong password" (rather than "user does not exist") confirms a valid MegaBank staff username, producing a spreadsheet of confirmed accounts — all without ever guessing a single correct password. With valid usernames now isolated from the much larger space of possible username:password combinations, the hacker can apply targeted techniques (credential-stuffing from the breach data, social engineering, or a narrowed brute force) far more efficiently and with far less detectable noise than blind brute forcing would require. The chapter's fix applies its own framework: collapse both failure cases into OWASP's generic "authentication failed" message, avoid any endpoint behavior that differs based on username validity, and rate-limit the login endpoint so even a generic-response enumeration attempt is throttled toward the legitimate-usage ceiling.

## Key Takeaways
1. Default to allowlisted generic error messages over both raw reflection and total silence — it is usually the best trade-off point on the disclosure/usability spectrum.
2. Collapse related failure states (e.g., bad username vs. bad password) into a single generic message, per OWASP's "authentication failed" guidance.
3. Never expose sequential or otherwise predictable identifiers in APIs or endpoints.
4. Rate-limit any endpoint whose repeated querying could leak information, at roughly the legitimate-usage ceiling.
5. Use secure-by-default wherever feasible; reserve light patterns for cases where forcing the secure setting isn't practical.
6. Place light-pattern nudges at the point of the risky action itself, not as documentation on a settings page most users won't read.
7. Consider blast-radius-limiting features (like daily transaction caps) as a light-pattern-promotable mitigation that reduces damage even if a compromise occurs.

## Connects To
- **Chapter 37 (Secure Application Configuration)**: Generic error-code practices here pair with CSP `report-uri`/logging to ensure disclosure-safe error handling is consistent from the header layer down to the UI layer.
- **Chapter 39 (Threat Modeling Applications)**: The MegaBank threat-modeling worked example independently flags an "information disclosure - FeatureID" attack vector via non-generic error messages, directly reinforcing this chapter's error-message guidance.
- **OWASP authentication guidance**: External standard cited directly for the generic "authentication failed" message recommendation.
