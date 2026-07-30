# Cheatsheet

## Decision Rules

- **When validating input**: use an allow list. If you catch yourself writing a block list, stop — block lists can't anticipate novel bypass encodings (case variation, Unicode, double-encoding, protocol-relative URLs). (Ch4, Ch25)
- **When rendering dynamic data**: escape at the point of interpretation, using the escaper for that exact context (HTML/DB/shell/regex). Never trust one generic "sanitize" call to cover multiple contexts. (Ch4, Ch43)
- **When a template engine's auto-escape is explicitly disabled** (`| safe`, `dangerouslySetInnerHTML`, `innerHTML =`): treat it as a mandatory manual security review point, not a stylistic choice.
- **When a request changes state**: it must not be a GET. If it is, that's an automatic CSRF finding regardless of other defenses present. (Ch6, Ch26)
- **When choosing a failure response for unauthorized access**: use 404 if the resource's existence itself is sensitive (e.g., `/admin`), 403 if existence may be acknowledged, 302/401 if merely unauthenticated. (Ch10)
- **When a password needs to be recoverable** (e.g., to relay to a third-party API): encrypt it (AES), don't hash it. **When a password only needs to be verified** (user login): hash it (bcrypt/PBKDF2/Argon2-class), don't encrypt it. Confusing these two is a recurring real-world bug. (Ch3, Ch8, Ch21)
- **When storing a secret used for decryption**: never co-locate the key with the encrypted data — encryption at rest is meaningless if an attacker who steals the disk also gets the key. (Ch3, Ch7)
- **When you need to know if a dependency is exploitable**: don't patch reflexively and don't ignore CVEs reflexively — check actual usage context and exploitability, then patch based on risk, not alphabetical CVE severity. (Ch5, Ch13, Ch35)
- **When XML parsing untrusted input**: disable external entity resolution by default, every time, in every language — never assume the library ships safe defaults (Java parsers especially don't). (Ch11, Ch27, Ch45)
- **When binding request data to an object or DB row**: allowlist fields explicitly. A generic recursive merge or whole-object bind is a mass-assignment / prototype-pollution vulnerability waiting to happen. (Ch11, Ch30, Ch31, Ch48, Ch49)
- **When deciding whether client-side JS can enforce a security rule**: it can't. Any check must be re-verified server-side, no exceptions — client checks are UX only. (Ch10, Ch23)
- **When fixing a vulnerability at design/architecture time vs. after shipping**: architecture-time fixes are cited (NIST) as roughly 30-60x cheaper than production fixes — bias review effort toward the design phase. (Ch21, Ch35, Ch52)

## Decision Tree: "Something looks like an XSS sink"

1. Is the value ever inserted into the DOM (via `innerHTML`, `document.write`, a templating engine, or a URL/hash read)?
   - No → not a client-side XSS concern (check server-side reflection instead).
   - Yes → continue.
2. Is the insertion point using `innerText`/`textContent` (safe) or `innerHTML`/`document.write` (dangerous)?
   - Safe sink → low risk, but still check for CSS-based exfiltration and mutation-based (mXSS) edge cases if a sanitizer library is layered on top.
   - Dangerous sink → continue.
3. Is the value sanitized before insertion (e.g., DOMPurify)?
   - No → confirmed XSS risk; fix via escaping/`innerText` or CSP hardening.
   - Yes → check whether the sanitizer's parsing context matches the DOM's actual render context — mismatches are exactly how mutation-based XSS (mXSS) bypasses sanitizers. (Ch10, Ch25, Ch28, Ch43)

## Trade-off Matrix: Session Storage Approach

| Approach | Revocation | Scales across microservices? | Payload readable client-side? | Notes |
|---|---|---|---|---|
| Server-side session (Redis-backed) | Immediate | Needs shared store | No | Requires sticky LB or shared store; simplest to revoke |
| Client-side session cookie (unsigned) | N/A — never do this | N/A | Yes, and forgeable | Never use without signing/encryption |
| Signed JWT | Hard (needs blocklist/short expiry) | Yes, independent verification per service | Yes (readable, not necessarily writable) | Signing proves integrity only, not confidentiality |
| Encrypted JWT | Hard (same as above) | Yes | No | Best of both, more complexity | 
(Ch9)

## Trade-off Matrix: CSRF Defense Layer

| Defense | Blocks basic CSRF? | Blocks token-pool bypass? | Blocks header-stripping bypass? | Notes |
|---|---|---|---|---|
| SameSite cookie alone | Mostly | N/A | N/A | Insufficient alone — some browsers/proxies don't enforce it |
| Origin/Referer check alone | Yes | Yes | No, if header can be stripped/omitted | Combine with tokens |
| Anti-CSRF token (session-bound) | Yes | No, if token pool is shared across resources | Yes | Strongest single control |
| Anti-CSRF token + SameSite + Origin check (layered) | Yes | Yes | Yes | Recommended: defense in depth |
(Ch6, Ch11, Ch26, Ch29, Ch44)

## Thresholds & Defaults

- **CVSS severity bands**: 0.1–3.9 Low · 4.0–6.9 Medium · 7.0–8.9 High · 9.0–10.0 Critical. (Ch27, Ch42)
- **Cost multiplier, design-time vs. production fix**: ~30-60x cheaper to fix at architecture/design phase (NIST estimate cited by Hoffman). (Ch21, Ch36, Ch52)
- **Password defense priority**: length/entropy > complexity rules. Nudge with a strength estimator (zxcvbn) rather than rigid character-class requirements. (Ch8)
- **Rate limiting brute-force attempts**: key by IP, not by username — rate-limiting by username enables a lockout-attack DoS against a known user. (Ch8)
- **Regression rate for shipped vulnerabilities**: ~25% of vulnerabilities at a 10k+ employee company were regressions of previously fixed bugs (Hoffman) — always add a regression test when closing a security bug. (Ch35, Ch41, Ch42)
- **Redirect safety rule**: only allow relative paths starting with a single `/` (not `//`, which is protocol-relative and can point off-site). (Ch14)

## Tells & Smells

- **Differing error messages between "wrong password" and "no such user"** → user enumeration vulnerability. (Ch8, Ch23, Ch38)
- **Session ID or auth token appears in a URL (query string)** → leaks via browser history, server logs, and the `Referer` header; also enables session fixation. (Ch9)
- **A JSON merge/extend utility recursively copies `__proto__` or `constructor.prototype`** → prototype pollution risk. (Ch11, Ch16, Ch31)
- **An XML parser is used with default settings and no explicit DTD-disable call** → XXE risk, assume vulnerable until proven otherwise. (Ch11, Ch12, Ch27)
- **A regex contains nested quantifiers like `(a+)+` or `(a*)*`** → classic catastrophic-backtracking ReDoS pattern. (Ch12, Ch29, Ch47)
- **A file upload is validated only by extension or `Content-Type` header** → trivially bypassed; must check magic bytes. (Ch11)
- **A dependency's version/framework is disclosed via response headers (`X-Powered-By`, `Server`) or unmodified default error pages** → free recon for attackers to match CVEs to your exact stack. (Ch13, Ch21)
- **An endpoint accepts an arbitrary user-supplied URL to fetch server-side** → potential SSRF if the destination isn't validated against a domain allow-list. (Ch11, Ch14)
- **A CSP header is either absent or includes `unsafe-inline`/`unsafe-eval`** → XSS mitigation layer is effectively disabled. (Ch2, Ch22, Ch37, Ch43)
- **Business logic feature works correctly for the "happy path" but was never modeled against automatable edge cases** (self-transfers, negative amounts, race conditions on shared balances) → likely business-logic vulnerability, won't be caught by any scanner. (Ch18, Ch33, Ch51)
