# Chapter 36: Secure Application Architecture

## Core Idea
Secure architecture starts by analyzing business requirements for risk (credentials? PII? financial data? search?) before writing code, then applies concrete controls — TLS for data in transit, slow adaptive hashing for credentials at rest, MFA, and Zero Trust's continuous explicit verification — because fixing a design-level security flaw after launch costs an estimated 30-60x more than fixing it at the architecture phase.

## Frameworks Introduced
- **Analyzing Feature Requirements for Risk**: A first-pass method for deriving security risk areas directly from a plain-language feature/business requirements list.
  - When to use: Before any code is written for a new product or feature, especially when engineering and security are separate teams.
  - How: Read the requirements and tag anything that implies (1) storing credentials, (2) storing PII, (3) elevated vs. guest privilege tiers, (4) search/query functionality, (5) storing financial data. Each tag opens a specific risk question (e.g., "how do we handle sessions, logins, cookies?" for credentials; "does law affect how we handle this data?" for PII; "primary DB or separate cached DB?" for search).
- **Zero Trust Architecture (NIST SP-800-207)**: A design pattern replacing implicit trust (granted by proximity/role, e.g., "already past the firewall") with explicit trust ("trust but verify" at every privileged action).
  - When to use: Anywhere authorization state can become stale relative to real-world state — e.g., long-lived tokens, employee role changes, privileged internal tooling.
  - How: Require a verification step in front of every action that could lead to compromise, rather than relying on a one-time boundary check (firewall pass, initial login) to imply ongoing trust. Combine with the Principle of Least Privilege so actors can only reach resources intended for them.
- **Credential Hashing Selection**: A criterion for choosing a password-hashing algorithm based on irreversibility and adaptive slowness rather than raw speed.
  - When to use: Any time user credentials must be stored.
  - How: Reject plaintext and fast/reversible schemes. Prefer BCrypt (Blowfish + Crypt, deliberately slower on faster hardware) or PBKDF2 (key stretching, configurable iteration count set to your hardware's practical maximum) so that brute-forcing scales unfavorably for the attacker as hardware improves.

## Key Concepts
- **Entropy (password security)**: The amount of randomness/unpredictability in a password; the true driver of password strength, not length or character-set size alone.
- **Hashing vs. encryption**: Hashing is one-way (non-reversible) and used for credential storage so not even staff can recover a password; encryption is reversible and used for data that must later be read back.
- **BCrypt**: A password hashing function combining the Blowfish cipher (1993, Bruce Schneier) with the Unix Crypt function, engineered to get slower as hardware gets faster.
- **PBKDF2 / key stretching**: A hashing approach where each additional hash attempt becomes progressively more expensive, configured via a minimum-iteration count set to the defender's own hardware ceiling.
- **MFA (multifactor authentication)**: Requiring a second factor (mobile app, SMS, or physical USB token) in addition to a password; eliminates most unauthorized remote logins absent a compromise of both factors.
- **Zero Trust / ZTNA / Zero Trust Design**: Interchangeable names for the same design philosophy requiring continuous, per-action verification instead of one-time boundary trust.
- **Implicit trust**: Trust granted by proximity or role alone (e.g., "inside the firewall" or "holds an unexpired token") without re-verification.
- **Explicit trust ("trust but verify")**: Trust that is re-checked at the moment of every privileged action.
- **Principle of Least Privilege**: Actors should only be able to access the resources intended specifically for them — the permissions backbone that Zero Trust builds on.

## Mental Models
- Treat a new feature's requirements list the way the chapter treats MegaMerch's ecommerce spec: read each plain-English requirement and translate it into a risk category (credentials, PII, privilege tiers, search, financial data) before any architecture diagram exists.
- Use the "castle with a moat" analogy for implicit trust: once someone is past the moat, an implicit-trust system assumes they belong there — it has no answer for the attacker who "swims across."
- For credential hashing, think "slow is a feature, not a bug": an algorithm that gets slower per-guess on modern hardware (BCrypt) or per-attempt over time (PBKDF2) directly reduces a hacker's guesses-per-second, unlike fast general-purpose hash functions.
- Use the "Joe Admin" scenario as the canonical test case for any authorization design: ask "if this actor's real-world status changed right now, would our system notice before the current token expires?" If the answer is no, the design is implicit-trust and violates Zero Trust.

## Anti-patterns
- **Storing passwords in plaintext**: Total compromise the moment the database is breached (Case #1 in the chapter's own comparison).
- **Hashing with a fast, non-adaptive algorithm like MD5**: Vulnerable to rainbow-table attacks; a meaningful fraction of passwords can be cracked even though they're "hashed" (Case #2).
- **Implicit trust based on token expiry alone**: A 48-hour unexpired token was treated as sufficient proof of continued employment in the "Joe Admin" case, letting a fired employee tamper with company books.
- **Skipping TLS/SSL on any data in transit**: Leaves data (especially credentials and financial data) exposed to man-in-the-middle interception.
- **Building a custom search engine without planning for database sync**: Search indexes drawing from a separate database can drift from the primary source of truth (stale permissions, deleted-but-still-searchable objects).

## Code Examples
This chapter does not include header/config syntax (that begins in Chapter 37); its only "code-like" artifact is the qualitative hashing comparison below.

- **What it demonstrates**: Why algorithm choice, not just "hashing vs. not," determines real-world credential safety.

## Reference Tables
| Case | Storage method | Result if database is breached |
|---|---|---|
| #1 | Plain text | All passwords compromised |
| #2 | MD5 hash | Hacker can crack some passwords via rainbow tables |
| #3 | BCrypt hash | Unlikely any passwords will be cracked |

## Worked Example
MegaBank launches a new ecommerce brand, MegaMerch, selling T-shirts, sweatpants, and swimwear. Requirements: users create accounts and sign in; accounts store full name, address, and date of birth; users browse a front page and search items; users save credit cards and bank accounts. A security architecture review derives the risk areas directly from this list: credential storage (auth/authz risk), PII storage (legal/regulatory risk), elevated vs. guest privilege (authorization risk), a search feature (primary-vs-cache database sync risk), and financial data storage (PII-adjacent legal risk). From there the review walks each risk to a concrete decision: all network traffic must use TLS (RFC 2246) to prevent man-in-the-middle credential/financial-data theft; passwords must be rejected if found in a top-1000 common-password list or if they contain the user's own name/birthdate/address (entropy-based password policy); passwords must be hashed with BCrypt and compared only as hashes, never stored or logged in plaintext; MFA should be offered (though not mandated) to users wanting stronger account protection; PII/financial data storage must be legal in every operating jurisdiction, with outsourcing to a compliant specialist considered for smaller companies; and the search feature, if implemented with a separate database (e.g., Elasticsearch), must have an explicit sync plan so that permission changes and deletions in the primary database propagate correctly. Separately, the "Joe Admin" case illustrates the Zero Trust gap: an admin employee is fired for money laundering, but the internal software only checks for an unexpired 48-hour auth token and never re-verifies employment status, letting Joe keep using privileged tooling to tamper with company books after termination — a failure that continuous, explicit-trust authorization checks would have prevented.

## Key Takeaways
1. Derive architecture-phase risk areas directly from plain-language feature requirements before any design document exists.
2. Encrypt all data in transit with TLS; treat this as a first-step, non-negotiable architecture decision.
3. Judge password strength by entropy, not length — reject common, patterned, or personally-derived passwords.
4. Hash credentials with an adaptively slow algorithm (BCrypt or PBKDF2 with hardware-maxed iterations); never store plaintext or use fast general-purpose hashes.
5. Offer MFA for any application where account takeover has real consequences.
6. Design authorization around explicit, continuous verification (Zero Trust) rather than implicit trust from a one-time check or unexpired token — the "Joe Admin" failure mode.
7. Plan explicitly for search-index/primary-database sync risk any time a separate search engine is introduced.
8. Remember the NIST estimate: architecture-phase fixes cost roughly 30-60x less than fixes made after production launch.

## Connects To
- **Chapter 37 (Secure Application Configuration)**: Takes the TLS/data-in-transit requirement established here and shows the exact HSTS/CSP/cookie header syntax used to enforce it in the browser.
- **Chapter 39 (Threat Modeling Applications)**: Formalizes the "analyze requirements for risk" step into a repeatable five-goal threat-modeling process.
- **Chapter 35 (Securing Modern Web Applications)**: This chapter is the concrete expansion of that chapter's "architecture phase is cheapest to fix" claim, with the 30-60x NIST figure.
- **Principle of Least Privilege / RBAC**: External concept underlying both Zero Trust's explicit-trust model and general authorization design.
