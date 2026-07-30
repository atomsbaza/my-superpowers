# Chapter 29: Denial of Service

## Core Idea
Denial of service is any attack that consumes server or client resources beyond what is available for legitimate use, and it can be triggered by a single crafted string (regex), a single abusive account (logical DoS), a coordinated botnet (DDoS), or by hijacking someone else's infrastructure to attack a target indirectly (proxy-based DoS).

## Frameworks Introduced
- **Resource-first DoS hunting**: before searching for specific bugs, identify which server resources are most valuable (CPU/RAM, queue slots, DB writes, drive writes), then look for APIs that consume those resources without bound.
  - When to use: any time you're auditing an app for DoS surface with no known bug yet.
  - How: list resource-intensive operation types (synchronous operations, database writes, drive writes, SQL joins, file backups, looping logical operations), map them to specific endpoints, then test how each endpoint's cost scales with attacker-controlled input.
- **Timing-based backend inference**: reconstruct backend data-model shape (and its DoS-relevant costs) purely from network payloads and UI behavior, without server access.
  - When to use: black-box testing where you cannot see server code.
  - How: time requests end-to-end via browser devtools; fire the same request many times concurrently to detect if processing is synchronous (staggered responses); script and average ~100 calls per measurement to cancel out noise from traffic spikes or cron jobs; infer object relationships (e.g., User HAS Album HAS Photos HAVE Metadata) from IDs in payloads, then find aggregate endpoints (e.g., `GET /metadata/:userid`) whose cost scales with account size.

## Key Concepts
- **Regex DoS (ReDoS) / evil regex / malicious regex**: a regular expression crafted (or accidentally written) so that certain inputs cause catastrophic backtracking, making matching time explode.
- **Greedy regex**: a regex using operators like `+` that test for one-or-more matches rather than stopping at the first match, which is the usual precondition for backtracking blowups.
- **Logical DoS**: a DoS vulnerability rooted in application logic rather than a specific parser bug — an illegitimate user drains server resources via a legitimate-looking but unbounded operation.
- **Distributed Denial of Service (DDoS)**: a large network of devices (often a botnet of malware-compromised machines owned by real people) floods a server, usually at the network layer with UDP traffic against the server's IP rather than at any specific API endpoint.
- **YoYo attack**: repeatedly flooding then abruptly stopping traffic against an autoscaling cloud-hosted app to force costly scale-up/scale-down cycles, degrading UX and inflating the victim's hosting bill.
- **Compression attack**: uploading a malformed file (e.g., video, image) that causes a compression/processing library (FFMPEG, ImageMagick) to consume excessive CPU/memory or crash during server-side processing.
- **Proxy-based DoS** (author-coined term): tricking a third-party service with large compute resources — e.g., a search engine crawler — into directing amplified request volume at a target site, so the attacker doesn't have to pay for the attacking compute themselves.
- **DoS sink**: the specific point in a system (a function, query, or resource) where degraded performance actually originates, which can be difficult to pinpoint even after a DoS symptom is observed.

## Mental Models
- Think of regex backtracking as exhaustive combinatorial search: an ambiguous grouping like `(ab)*` forces the engine to try every possible split of the matched prefix before concluding failure, so cost grows with the number of ways the string can be partitioned, not just its length.
- Use the "reupload the same photo into hundreds of albums" pattern as the general template for logical DoS: find any endpoint whose cost is a function of an attacker-controlled quantity (album count, photo count, list length) with no server-side cap, then scale that quantity artificially.
- Treat DDoS as "any DoS attack, but distributed" — a botnet does not require a new attack primitive; it just applies existing DoS techniques (regex payloads, logical abuse, or raw bandwidth floods) at scale from many sources, which is what makes source attribution ("are they real users?") hard.
- Think of proxy-based DoS as laundering compute: instead of paying for your own attack traffic, you get an already-resourced, allowlisted service (a crawler) to generate the traffic against the target on your behalf.

## Anti-patterns
- **Accepting or constructing regular expressions from user input without safeguards**: a regex like `/^((ab)*)+$/` looks harmless but backtracks catastrophically on adversarial input, and the flaw can "lie dormant for years" until someone finds the triggering string.
- **Unbounded resource scaling tied to attacker-controlled input**: an endpoint like `GET /metadata/:userid` whose cost scales linearly (or worse) with how many objects a user has created, with no per-request resource cap, lets any user turn their own account size into a weapon.
- **Running unhardened/outdated media-processing libraries on user-uploaded files**: parsing untrusted video/image files with libraries like FFMPEG (e.g., CVE-2021-38094) exposes integer-overflow and similar bugs that spike CPU/memory or crash the process.
- **Trusting crawler traffic as inherently benign**: allowlisting search-engine crawlers in `robots.txt` for indexing purposes creates an amplification channel if crawlers can be tricked (via proxying domains/subdomains) into hammering a target repeatedly.

## Code Examples
```regex
/^((ab)*)+$/
```
Triggering inputs (from source):
```
abababababababa        // extra trailing 'a' after ababababababab — triggers slow backtracking
abababababababababababa      // 23 chars, 8 ms
ababababababababababababa    // 25 chars, 15 ms
abababababababababababababa  // 27 chars, 31 ms
ababababababababababababababa // 29 chars, 61 ms
```
Non-triggering (safe) inputs of similar length (from source):
```
ababababababababababab       // 22 chars, <1 ms
abababababababababababab     // 24 chars, <1 ms
ababababababababababababab   // 26 chars, <1 ms
abababababababababababababab // 28 chars, >1 ms
```
- **What it demonstrates**: capture group `((ab)*)+` matched against a string ending in an unpaired extra character forces the engine to backtrack through every possible split of the `(ab)` sequence before failing, while strings that match cleanly (even/paired) or fail immediately return fast — the same regex is safe on most inputs and catastrophic on a narrow, easy-to-miss class of inputs.

## Reference Tables

Table 14-1 (malicious input, from source) — time to match `/^((ab)*)+$/`:

| Input | Length | Execution time |
|---|---|---|
| abababababababababababa | 23 chars | 8 ms |
| ababababababababababababa | 25 chars | 15 ms |
| abababababababababababababa | 27 chars | 31 ms |
| ababababababababababababababa | 29 chars | 61 ms |

Table 14-2 (safe input, from source) — same regex, different inputs:

| Input | Length | Execution time |
|---|---|---|
| ababababababababababab | 22 chars | <1 ms |
| abababababababababababab | 24 chars | <1 ms |
| ababababababababababababab | 26 chars | <1 ms |
| abababababababababababababab | 28 chars | >1 ms |

Table 14-3 (logical DoS scaling, from source) — `GET /metadata/:userid` by account archetype:

| Account type | Response time |
|---|---|
| New account (1 album, 1 photo) | 120 ms |
| Average account (6 albums, 60 photos) | 470 ms |
| Power user (28 albums, 490 photos) | 1,870 ms |

DoS attack types compared:

| Attack type | Mechanism (one line) |
|---|---|
| ReDoS | Catastrophic regex backtracking on crafted input strings |
| Logical DoS | Attacker-controlled quantity (e.g., account size) drives unbounded server-side cost |
| DDoS | Many coordinated devices/bots flood a server, usually at the network layer |
| YoYo | Repeated flood/stop cycles abuse cloud autoscaling, inflating cost and degrading UX |
| Compression attack | Malformed uploaded file causes excessive cost/crash in a processing library |
| Proxy-based DoS | Third-party crawler/service tricked into amplifying requests at a target |

## Worked Example
A photo-sharing app exposes `GET /metadata/:userid` to fetch all metadata across a user's albums and photos. From the UI, the tester observes IDs referencing Photo, Album, and Metadata objects (e.g., `{ image: data, metadata: 123abc }`) and infers a User HAS Album HAS Photos HAVE Metadata structure, meaning the endpoint likely performs a join or iterative query that scales with account size. The tester measures response time across account archetypes: 120 ms for a new account (1 album, 1 photo), 470 ms for an average account (6 albums, 60 photos), and 1,870 ms for a power user (28 albums, 490 photos) — confirming near-linear (or worse) scaling with content volume. The tester then scripts client-side reuploads of the same or similar images to build an account with roughly 600 albums and 3,500 photos. Repeated requests against `GET /metadata/:userid` for that inflated account degrade server performance for other users, unless the server enforces per-request resource limits — and even if the request times out client-side, the database may still be consuming resources to complete the query server-side.

## Key Takeaways
1. Regex DoS is often invisible during normal testing because the same evil regex is safe for most inputs and only catastrophic for a narrow class the developer never tried — never assume a regex is safe just because normal traffic doesn't trigger slowness.
2. Greedy operators (`+`, `*`) combined with ambiguous/overlapping groupings are the concrete signature to look for when hunting evil regexes, especially any regex sourced from or built with user input.
3. Logical DoS requires no parser bug at all — just find any endpoint whose cost is a function of an attacker-controllable quantity (list size, account size) with no upper bound or per-request resource cap.
4. Black-box timing plus averaging (~100 requests) is enough to detect synchronous, unbounded-cost operations without server-side access; watch for endpoints that scale with account/data size across archetypes.
5. Third-party media/file-processing libraries (FFMPEG, ImageMagick) are a common, often-overlooked compression-attack surface because they process attacker-supplied file bytes directly — CVE-2021-38094 (FFMPEG integer overflow in `filter_sobel()`, `libavfilter/vf_convolution.c`) is a concrete real-world instance.
6. DDoS is not a distinct attack primitive but a delivery mechanism — nearly any DoS technique (regex, logical) can theoretically be distributed, though most real-world DDoS instead targets the network layer directly (UDP floods against IPs) rather than application-level endpoints.
7. Proxy-based DoS exploits the trust extended to crawlers via `robots.txt` allowlisting — a hacker can proxy a target's content through many subdomains to trick crawlers into amplifying request volume at the target for free.

## Connects To
- **Defending Against DoS chapter**: this attack chapter's countermeasures (regex hardening, rate limiting, per-request resource caps, autoscale safeguards) are covered in the later "Defending Against DoS" chapter — the source text places its own equivalent chapter around chapter 32.
- **Rate limiting**: the primary practical mitigation implied throughout (per-request/per-account resource limits) for logical DoS and repeated-request abuse.
- **Backtracking regex engines**: the underlying mechanism (NFA-style backtracking vs. linear-time engines like RE2) that makes ReDoS possible in JavaScript, PCRE, and most mainstream regex implementations.
- **Chapter 15, "Attacking Data and Objects"**: the next chapter in the source book, following directly after this one.
