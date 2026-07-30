# Chapter 24: Introduction to Hacking Web Applications

## Core Idea
This chapter is the bridge between recon (Part I) and offense (Part II): it reframes hacking as an investigative, analytical discipline rather than a constructive one, and shows how the recon skills already gathered (API type, endpoint discovery, auth scheme, third-party dependencies, application architecture) directly determine what exploits are possible and where to aim them.

## Frameworks Introduced
- **The Hacker's Mindset (vs. the Engineer's Mindset)**: Software engineers measure productivity by features added or performance improved — visible, constructive output. Hackers measure productivity through data gathering and analysis, most of which produces false positives and looks like "wasted time" to an outside observer.
  - When to use: Reframe expectations before starting any offensive engagement — success is not linear or guaranteed on a schedule.
  - How: Treat exploration and dead ends as the actual work product, not overhead; keep detailed records of prior attempts and lessons learned so effort compounds instead of repeating.
- **Applied Recon → Exploit Selection**: Each recon finding from Part I maps to a specific offensive decision.
  - When to use: At the start of any engagement, before choosing a payload or exploit type.
  - How: (1) Confirm API type (mostly REST) since most upcoming payloads are delivered over REST. (2) Check for structurally similar endpoints (e.g., `/users/1234/friends` vs `/users/1234/settings`) — a payload that fails against one may succeed against a sibling endpoint. (3) Determine the authentication scheme, since authenticated functionality is a superset of guest functionality and carries greater privileges. (4) Identify third-party/OSS dependencies to find and adapt publicly documented exploits, including holes created specifically by the custom-code/third-party integration seam.

## Key Concepts
- **Hacker as detective**: A good hacker is an organized detective; a great hacker adds strong technical skill; a master hacker continuously learns and adapts as defenders improve.
- **Data gathering and analysis**: The bulk of hacking work — most hackers analyze existing codebases seeking entrypoints rather than modifying or deconstructing software.
- **False positives as normal cost**: Long stretches (weeks to months) without a successful exploit are expected, not a sign of failure.
- **Exploit reuse across an owner's properties**: Due to code reuse, an exploit found on one application can often be replicated against other internal/related applications discovered via recon (same owner).
- **Authenticated attack surface**: Most web apps expose a superset of functionality to authenticated users, meaning more attackable APIs and higher-privilege outcomes once authenticated.
- **Pivoting through application architecture**: If application A can't be exploited directly but is known to communicate with vulnerable application B, deliver the payload to A so it later relays it to B.
- **Third-party integration seams**: Security holes can arise specifically from how custom code integrates with third-party/OSS code, not from either component alone.

## Mental Models
- Think of recon and hacking as two halves of one skill: recon without exploitation finds nothing exploitable delivered; exploitation without recon has no map of where to strike.
- Use the "detective" model when frustrated by slow progress: detectives don't close cases daily, they accumulate clues until one pays off — apply the same patience and record-keeping discipline.
- When an exploit fails on a target endpoint, try it on structurally similar endpoints first before abandoning it (endpoint-family reuse) — think of it as testing a lock-picking technique against every door of the same brand, not just one.
- When a hardened application is integrated with a weaker one, think of the weaker one as the delivery vector: find not "can I break the strong app" but "what does the weak app send to the strong app, and can I corrupt that."

## Anti-patterns
- **Measuring hacking progress like feature output**: Expecting steady, visible daily progress (as in software engineering) leads to premature abandonment of promising leads — most of the work is invisible analysis.
- **Discarding a failed exploit outright**: Failing against one endpoint (e.g., `/users/1234/friends`) without testing structurally similar endpoints (e.g., `/users/1234/settings`) wastes a potentially working payload.
- **Ignoring authentication scheme analysis**: Attacking only as a guest when authenticated sessions expose a strictly larger, higher-privilege API surface.
- **Treating each target application in isolation**: Missing pivot opportunities by not mapping how a vulnerable-but-uninteresting app communicates with a hardened-but-valuable app.
- **Not logging prior attempts**: Losing lessons learned as engagements scale from small applications to large ones with key functionality/data as the target.

## Reference Tables
None in this chapter.

## Worked Example
The book frames this using its running example, mega-bank.com, and one endpoint-family scenario: suppose recon from Part I revealed the endpoint `/users/1234/friends`. An attack against it returns no sensitive nonpublic data — a dead end on its own. But recon also uncovered a sibling endpoint, `/users/1234/settings`, following the same URL structure and presumably backed by similar code. Because endpoints sharing a structure often share an implementation (and therefore a vulnerability), the same attack technique is retried against `/users/1234/settings` — and this time it could expose sensitive data. The chapter generalizes this into the broader architecture-pivot case: if mega-bank.com's public-facing application (A) resists direct exploitation but is known (from Part I's architecture analysis) to relay data to an internal application (B), the hacker delivers the payload to A with the expectation that A's normal communication with B carries the payload onward — achieving compromise of B without ever attacking B directly.

## Key Takeaways
1. Expect long unproductive-looking stretches; measure success by disciplined analysis and record-keeping, not daily visible output.
2. Before choosing an exploit, re-confirm the API type (mostly REST) established during recon — it determines how payloads will be delivered.
3. When an exploit fails on one endpoint, retest it against structurally similar sibling endpoints discovered during recon.
4. Determine the authentication scheme early — authenticated sessions expose more APIs and higher privileges than guest access.
5. Mine identified third-party/OSS dependencies for public exploits, and specifically inspect the custom-code/third-party integration seam for holes neither component has alone.
6. When a hardened target resists direct attack, map its architecture for a weaker integrated application to pivot through.
7. Reuse successful exploits across other applications owned by the same organization, since code reuse is common.

## Connects To
- **Part I recon chapters**: Every technique here (API typing, endpoint discovery, auth scheme identification, dependency fingerprinting, architecture mapping) is a direct prerequisite input to the decisions made in this chapter.
- **Chapter 25 (Cross-Site Scripting) and subsequent attack-type chapters (CSRF, XXE, Injection, DoS, Attacking Data and Objects, ch25-30)**: This chapter is the conceptual bridge; the specific payload mechanics and exploit walkthroughs for each vulnerability class begin immediately after it.
- **Threat modeling / attack surface analysis**: The authenticated-vs-guest attack surface distinction and the architecture-pivot concept map to standard attack-surface-reduction and trust-boundary analysis in broader security practice.
