---
name: webappsec-defense
description: "Knowledge base from \"Grokking Web Application Security\" by Malcolm McDonald and \"Web Application Security: Exploitation and Countermeasures for Modern Web Applications\" (2nd ed.) by Andrew Hoffman. Use when applying defensive frameworks for XSS, CSRF, injection, authentication/session/authorization design, threat modeling, dependency security, or reviewing code for security issues."
---

<!-- argument-hint: [topic, framework name, or chapter number] -->

# Web Application Security — Defense Playbook
**Authors**: Malcolm McDonald & Andrew Hoffman | **Pages**: ~780 combined | **Chapters**: 52 | **Generated**: 2026-07-31

## How to Use This Skill

- **Without arguments** — load core frameworks below for reference
- **With a topic** — ask about `XSS`, `CSRF`, `threat modeling`, or another indexed topic; I find and read the relevant chapter(s)
- **With a chapter** — ask for `ch25` or `chapter 43`; I load that specific chapter file
- **Browse** — ask "what chapters do you have?" to see the full index

This is a combined skill from two complementary sources: McDonald (chapters 1-15) covers defensive engineering by *layer* (browser, network, server, process); Hoffman (chapters 16-52) covers the full recon → offense → defense pipeline by *attack type*, with each offense chapter paired to a later defense chapter. When you ask about a topic not covered below, I will read the relevant chapter file before answering.

---

## Core Frameworks & Mental Models

**Defense in Depth** — layer independent, redundant protections so no single control's failure is fatal. Never rely on one mechanism (e.g., escaping alone, or SameSite alone) for a high-value control. (Ch4, Ch35)

**Principle of Least Privilege / Least Authority** — grant only the minimum permissions a process, person, or dependency needs. Applies to OS users, API scopes, third-party integrations, and even code-execution contexts. (Ch4, Ch7, Ch21, Ch46)

**Allow list > Block list** — validate against what's explicitly permitted, never what's forbidden. Block lists can't anticipate novel encodings/bypasses; this is the single most-repeated decision rule across both books. (Ch4, Ch25, Ch40)

**Zero Trust Architecture** (NIST SP-800-207) — no implicit trust from network location, session age, or prior authentication. Re-verify continuously; the "Joe Admin" case (48hr token, no re-check of employment status) is the canonical failure mode. (Ch21, Ch36)

**Threat Modeling — five-goal framework** — document knowledge → identify threat actors (internal + external + machine/script) → identify risks/vectors → identify mitigations → identify delta. Do this at design time: fixes here are ~30-60x cheaper than post-production (NIST estimate). (Ch24, Ch39)

**RBAC / ABAC authorization modeling** — model permissions as roles (RBAC) plus resource-attribute policy checks (ABAC), centralized in one layer (MVC Model, not Controller), never re-implemented per endpoint. Choose failure responses deliberately: 404 when existence itself is sensitive, 403 when acknowledgment is fine, 302/401 for unauthenticated. (Ch10, Ch18)

**Context-specific output escaping + parameterized queries** — escape dynamic output at the exact point of interpretation (HTML/DB/shell), and always use parameterized/prepared statements for SQL/NoSQL/LDAP. String concatenation into any of these contexts is the root cause of the majority of injection classes covered. (Ch4, Ch12, Ch28, Ch31, Ch46)

**Field allowlisting before bind/write** — explicitly enumerate which fields a request may set (a DTO or manual copy); never do a generic recursive merge or whole-object bind. This single pattern prevents mass assignment, prototype pollution, and privilege-field injection (`isAdmin: true`). (Ch11, Ch16, Ch33, Ch48)

**CVSS v3.1 scoring** — Base metrics (Attack Vector, Attack Complexity, Privileges Required, User Interaction, Scope, C/I/A impact) give a reproducible severity score (0.1-3.9 Low, 4.0-6.9 Medium, 7.0-8.9 High, 9.0-10 Critical). Always reproduce in staging before scoring, and require a regression test before closing. (Ch27, Ch42)

**Archetypal vs. business-logic vulnerabilities** — archetypal vulnerabilities (XSS, SQLi, CSRF) are generic patterns catchable by tooling; business-logic vulnerabilities are app-specific flaws discovered only by modeling the legitimate use case and mapping its edge cases (self-transfers, race conditions, precision loss). No scanner catches the second category. (Ch18, Ch25, Ch33, Ch40, Ch51)

**Layered session/cookie security** — Secure + HttpOnly + explicit SameSite on every session cookie; cryptographically secure RNG for session IDs; never accept a client-suggested ID (session fixation); never put session IDs in URLs. Signing a JWT proves integrity, not confidentiality — it's still client-readable. (Ch2, Ch9, Ch22)

**Dependency manifest + automated CVE auditing** — pin all dependencies (including transitive) in source control; run automated audits regularly; risk-assess before patching rather than blind-patching or indefinite deferral. Popularity ≠ vulnerability — heavily-scrutinized packages *look* riskier by CVE count precisely because they're well-audited. (Ch5, Ch13, Ch17, Ch32, Ch35)

**Incident response sequence** — stem bleeding → stabilize → assess → forensics (reconstruct a timeline from logs/commits) → blameless postmortem → transparent user communication → `security.txt` disclosure channel to de-escalate future incidents. (Ch15, Ch41)

---

## Chapter Index

### Grokking Web Application Security (McDonald)
| # | Title | Key Frameworks |
|---|-------|----------------|
| [ch01](chapters/ch01-know-your-enemy.md) | Know Your Enemy | Threat actor taxonomy, drive-by scanning, CVE tracking |
| [ch02](chapters/ch02-browser-security.md) | Browser Security | CSP, same-origin policy, CORS, SRI, cookie attributes |
| [ch03](chapters/ch03-encryption.md) | Encryption | TLS/HSTS, bcrypt, salt/pepper, integrity checking |
| [ch04](chapters/ch04-web-server-security.md) | Web Server Security | Allow lists, escaping, parameterization, defense in depth |
| [ch05](chapters/ch05-security-as-a-process.md) | Security as a Process | Four-eyes principle, CI/CD, dependency audits |
| [ch06](chapters/ch06-browser-vulnerabilities.md) | Browser Vulnerabilities | XSS, CSRF, clickjacking, XSSI |
| [ch07](chapters/ch07-network-vulnerabilities.md) | Network Vulnerabilities | MITM, DNS poisoning, cert/key hygiene |
| [ch08](chapters/ch08-authentication-vulnerabilities.md) | Authentication Vulnerabilities | SSO/OAuth/SAML, MFA, timing attacks |
| [ch09](chapters/ch09-session-vulnerabilities.md) | Session Vulnerabilities | Session fixation, JWT signing |
| [ch10](chapters/ch10-authorization-vulnerabilities.md) | Authorization Vulnerabilities | RBAC/ABAC, MVC placement, 403 vs 404 |
| [ch11](chapters/ch11-payload-vulnerabilities.md) | Payload Vulnerabilities | Deserialization, XXE, prototype pollution, uploads |
| [ch12](chapters/ch12-injection-vulnerabilities.md) | Injection Vulnerabilities | SQL/NoSQL/LDAP/command/CRLF/regex injection |
| [ch13](chapters/ch13-third-party-code-vulnerabilities.md) | Vulnerabilities in Third-Party Code | Dependency manifests, CVE audits, header hardening |
| [ch14](chapters/ch14-unwitting-accomplice.md) | Being an Unwitting Accomplice | SSRF, SPF/DKIM/DMARC, open redirects |
| [ch15](chapters/ch15-what-to-do-when-hacked.md) | What to Do When You Get Hacked | Incident response, forensics, security.txt |

### Web Application Security (Hoffman, 2nd ed.) — Part I: Recon
| # | Title | Key Frameworks |
|---|-------|----------------|
| [ch16](chapters/ch16-history-of-software-security.md) | The History of Software Security | Worst-case design, Enigma/phreaking history |
| [ch17](chapters/ch17-intro-to-web-app-recon.md) | Intro to Web Application Recon | RBAC mapping, app "map" model |
| [ch18](chapters/ch18-structure-of-modern-web-app.md) | The Structure of a Modern Web App | REST/GraphQL/SPA fingerprinting |
| [ch19](chapters/ch19-finding-subdomains.md) | Finding Subdomains | dnscan, zone transfer attacks |
| [ch20](chapters/ch20-api-analysis.md) | API Analysis | OPTIONS discovery, auth-scheme fingerprinting |
| [ch21](chapters/ch21-identifying-third-party-dependencies.md) | Identifying Third-Party Dependencies | Version fingerprinting, CVE cross-referencing |
| [ch22](chapters/ch22-identifying-weak-points-in-architecture.md) | Identifying Weak Points in Architecture | Layered-security maturity model |
| [ch23](chapters/ch23-part1-summary-recon.md) | Part I Summary — Recon | Recon technique lifecycle |

### Part II: Offense
| # | Title | Key Frameworks |
|---|-------|----------------|
| [ch24](chapters/ch24-intro-to-hacking-web-apps.md) | Intro to Hacking Web Applications | Hacker mindset, exploit reuse, pivoting |
| [ch25](chapters/ch25-cross-site-scripting.md) | Cross-Site Scripting | Stored/reflected/DOM/mutation XSS, filter bypasses |
| [ch26](chapters/ch26-cross-site-request-forgery.md) | Cross-Site Request Forgery | GET/POST/zero-interaction payloads, bypass table |
| [ch27](chapters/ch27-xml-external-entity.md) | XML External Entity | Direct/indirect/OOB XXE, Linux ATO chain |
| [ch28](chapters/ch28-injection.md) | Injection | SQL/code/command injection, blind SQLi |
| [ch29](chapters/ch29-denial-of-service.md) | Denial of Service | Regex DoS, logical DoS, DDoS |
| [ch30](chapters/ch30-attacking-data-and-objects.md) | Attacking Data and Objects | Mass assignment, IDOR, serialization attacks |
| [ch31](chapters/ch31-client-side-attacks.md) | Client-Side Attacks | Prototype pollution, clickjacking, tabnabbing |
| [ch32](chapters/ch32-exploiting-third-party-dependencies.md) | Exploiting Third-Party Dependencies | Supply-chain incidents, integration risk |
| [ch33](chapters/ch33-business-logic-vulnerabilities.md) | Business Logic Vulnerabilities | Custom math, quasi-cash, IEEE754 precision |
| [ch34](chapters/ch34-part2-summary-offense.md) | Part II Summary — Offense | Mitigations-not-fixes framing |

### Part III: Defense
| # | Title | Key Frameworks |
|---|-------|----------------|
| [ch35](chapters/ch35-securing-modern-web-apps.md) | Securing Modern Web Applications | Defense pipeline, regression-test discipline |
| [ch36](chapters/ch36-secure-application-architecture.md) | Secure Application Architecture | Zero Trust, BCrypt/PBKDF2, MFA |
| [ch37](chapters/ch37-secure-application-configuration.md) | Secure Application Configuration | CSP/CORS/HSTS/COOP/CORP exact syntax |
| [ch38](chapters/ch38-secure-user-experience.md) | Secure User Experience | Dark vs light patterns, enumeration resistance |
| [ch39](chapters/ch39-threat-modeling-applications.md) | Threat Modeling Applications | Five-goal framework, worked example |
| [ch40](chapters/ch40-reviewing-code-for-security.md) | Reviewing Code for Security | Blocklist/boilerplate/trust-by-default anti-patterns |
| [ch41](chapters/ch41-vulnerability-discovery.md) | Vulnerability Discovery | Static/dynamic analysis, bug bounties |
| [ch42](chapters/ch42-vulnerability-management.md) | Vulnerability Management | CVSS v3.1 full scoring tables |
| [ch43](chapters/ch43-defending-against-xss.md) | Defending Against XSS Attacks | innerText, CSP script-src, entity encoding |
| [ch44](chapters/ch44-defending-against-csrf.md) | Defending Against CSRF Attacks | Origin/Referer checks, stateless tokens |
| [ch45](chapters/ch45-defending-against-xxe.md) | Defending Against XXE | Parser DTD-disable, XML vs JSON |
| [ch46](chapters/ch46-defending-against-injection.md) | Defending Against Injection | Prepared statements, PoLA |
| [ch47](chapters/ch47-defending-against-dos.md) | Defending Against DoS | Regex review, DDoS blackholing |
| [ch48](chapters/ch48-defending-data-and-objects.md) | Defending Data and Objects | DTO pattern, IDOR indirection |
| [ch49](chapters/ch49-defense-against-client-side-attacks.md) | Defense Against Client-Side Attacks | Object.freeze, frame-ancestors, COOP |
| [ch50](chapters/ch50-securing-third-party-dependencies.md) | Securing Third-Party Dependencies | Dependency tree modeling, SCA |
| [ch51](chapters/ch51-mitigating-business-logic-vulnerabilities.md) | Mitigating Business Logic Vulnerabilities | Statistical modeling, worst-case design |
| [ch52](chapters/ch52-part3-summary-and-conclusion.md) | Part III Summary and Conclusion | Full book recap, offense↔defense pairing table |

## Topic Index

- **API security / recon** → ch18, ch20
- **Authentication** → ch8, ch21, ch36
- **Authorization** → ch10
- **Business logic vulnerabilities** → ch18, ch33, ch51
- **Clickjacking / tabnabbing** → ch6, ch16, ch31, ch34, ch49
- **Content Security Policy (CSP)** → ch2, ch6, ch22, ch28, ch37, ch43
- **CSRF** → ch6, ch11, ch26, ch29, ch44
- **CVSS / severity scoring** → ch27, ch42
- **Denial of Service** → ch14, ch29, ch32, ch47
- **Dependency / supply-chain security** → ch5, ch13, ch17, ch21, ch32, ch35, ch50
- **Encryption / TLS / HSTS** → ch3, ch7, ch22, ch37
- **Incident response / forensics** → ch15, ch20, ch41
- **Injection (SQL/NoSQL/LDAP/command/regex)** → ch4, ch12, ch28, ch31, ch46
- **Mass assignment / prototype pollution** → ch11, ch16, ch18, ch30, ch31, ch33, ch34, ch48, ch49
- **Network / MITM attacks** → ch7
- **Password / credential storage** → ch3, ch8, ch21, ch36
- **Recon methodology** → ch1, ch17, ch19, ch20, ch21, ch22, ch23, ch24
- **Session management** → ch2, ch9, ch22, ch37
- **SSRF / email spoofing / open redirects** → ch14
- **Third-party dependency exploitation** → ch17, ch32, ch50
- **Threat modeling** → ch1, ch24, ch39
- **XSS (all variants)** → ch6, ch10, ch25, ch28, ch43
- **XXE** → ch11, ch12, ch27, ch30, ch45
- **Zero Trust Architecture** → ch21, ch36, ch52

## Supporting Files

- [glossary.md](glossary.md) — all key terms with definitions
- [patterns.md](patterns.md) — all techniques and design patterns
- [cheatsheet.md](cheatsheet.md) — quick reference tables and decision guides

---

## Scope & Limits

This skill covers the book content only (defensive engineering + attack/defense pairs for web applications). For hands-on implementation in your codebase, combine with project-specific tools and current framework documentation — some specific library APIs (e.g., exact CSP browser support, current CVE databases) may have moved on since these editions (2024). For topics beyond web application security, check related skills or ask the agent directly.
