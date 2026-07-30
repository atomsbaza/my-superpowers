# Chapter 1: Know Your Enemy

## Core Idea
Before writing a line of defensive code, understand who attacks web applications, why, and with what tools, so you can calibrate your security effort to your actual risk profile rather than to either complacency or paranoia.

## Frameworks Introduced
- **Threat modeling**: Considering who would want to attack your organization and what they might gain by compromising your systems, then sizing your defensive investment accordingly.
  - When to use: At the start of any project, and periodically as the organization grows or changes industry/data profile.
  - How: Assess industry sensitivity (government, energy, finance, healthcare, education = high risk), organization size (bigger = more lucrative to attackers, "big-game hunting"), and what data/access you hold. Higher-risk profiles usually justify a dedicated security team and a formal P0 (priority zero) escalation process.
- **The hacker taxonomy (black/white/gray hat)**: Classifies actors by intent to calibrate what kind of activity you should expect and how to respond to it.
  - When to use: When deciding whether to run a bug bounty program or interpret unsolicited vulnerability reports.
  - How: Black hats exploit for gain; white hats report vulnerabilities (often for bounty money) before black hats find them; gray hats report or exploit depending on which is more profitable to them.
- **Drive-by vulnerability scanning as baseline threat**: Regardless of your threat model tier, assume automated tools are scanning you right now for known vulnerabilities.
  - When to use: Always — it is the universal minimum threat, independent of industry or size.
  - How: Fix obvious/known vulnerabilities and become a "hard target"; opportunistic scanners tend to move on to easier prey rather than persist.

## Key Concepts
- **CVE (Common Vulnerabilities and Exposures)**: MITRE's public database cataloging disclosed, patched security vulnerabilities, referenced by CVE number.
- **Zero-day vulnerability**: A security flaw that has just been publicly disclosed ("zero days since disclosure"), triggering a race between defenders patching and attackers exploiting.
- **Advanced persistent threat (APT)**: A sophisticated, usually state-sponsored hacking group (e.g., Cozy Bear, Charming Kitten) tracked by its signature techniques.
- **Social engineering / spear phishing**: Gaining a target's trust to extract credentials or secrets; spear phishing targets specific named individuals (often in accounting) after background research.
- **Malicious insider**: A rogue employee or contractor who leaks data or IP; mitigated by need-to-know data access restrictions rather than code-level controls.
- **Credential stuffing vs. password spraying**: Credential stuffing retries a whole stolen password database against one target site; password spraying retries stolen credentials across many different sites (exploiting password reuse).
- **Rootkit / botnet**: A rootkit is tooling used to escalate to root/admin access; a botnet is the resulting network of compromised machines used for cryptomining, spam, click fraud, or resale on the dark web.
- **Living off the land**: Attackers avoiding detection by using only pre-existing, locally available tools and processes rather than introducing new malware signatures.
- **Big-game hunting**: Targeting large organizations because compromising their network is more lucrative than targeting small ones.

## Mental Models
- Think of drive-by scanning as background radiation: every internet-facing app receives it regardless of industry, so baseline hygiene is non-negotiable even for "boring" targets.
- Use the P0 framing as a signal, not a threat: if your organization has an in-house security team invoking a threat-modeling matrix and declaring a P0, that is confirmation the org already treats security formally — your job is to support that process, not second-guess it.
- Treat "keeping code/dependencies known" as a prerequisite capability, not an optional nicety: you cannot patch what you cannot enumerate, so dependency visibility (source control + dependency manager, chapter 5) is upstream of all patching decisions.
- Treat legacy code maintenance and deadline pressure as the two conditions under which security review time gets silently cut — build in slack deliberately rather than assuming reviews will "just happen."

## Anti-patterns
- **"We're not a target" complacency**: Ignores that drive-by scanning targets everyone indiscriminately, not just high-profile industries; small size does not confer invisibility.
- **Rushing releases without review time**: Security problems at the code level disproportionately occur when a team is rushing to hit deadlines; skipped reviews compound with legacy code that no original author remains to explain.
- **Treating detection as someone else's job**: Assuming an in-house security team or hosting provider will notice compromise without your own logging, error reporting, and monitoring in place.

## Code Examples
No code examples in this narrative chapter — its content is entirely conceptual (threat actors, motives, and organizational posture).

## Reference Tables
No tables in this chapter (purely narrative).

## Worked Example
Consider a small startup, "Breddit" (a fictional baking-recipe community used throughout this book), just before its public launch, trying to decide how paranoid to be.

1. **Threat model check**: Breddit is not a bank, government contractor, or healthcare provider — but it does store user emails, passwords, and payment details for a "Pro" subscription tier. That alone makes it a target for credential-stuffing resale value and dark-web data sales, even though it is not a big-game-hunting target for APTs.
2. **Baseline assumption**: Regardless of Breddit's low profile, its public IP range will be swept by automated scanners within hours of DNS propagating. The team treats this as certain, not hypothetical.
3. **Immediate actions taken** (mapped to the chapter's "where to start" checklist):
   - Subscribe to security-relevant feeds (X/Reddit security accounts, CVE alerts for their exact stack: e.g., their Ruby web framework and Postgres version).
   - Confirm every dependency is pinned and visible via their dependency manager (Bundler) so a CVE against a gem can be matched to actual exposure in minutes, not days.
   - Turn on request logging and basic uptime/error-rate monitoring before launch, not after an incident — so that if something goes wrong, forensic reconstruction is possible.
   - Run a lightweight internal code review culture: two-person review on anything touching authentication or payments, explicitly building in review time rather than treating it as schedule slack to cut.
   - Accept that they will not achieve zero risk, and instead aim to be a "hard target" — fixing the obvious flaws that drive-by scanners look for (default credentials, outdated framework versions, missing HTTPS) so that opportunistic attackers move on to easier prey.

The outcome: Breddit doesn't need an in-house SOC or a P0 escalation matrix at this size, but it does need the five foundational habits (vulnerability tracking, dependency visibility, logging/monitoring, security-literate reviewers, and unhurried review time) — because these are the controls proportionate to "small company holding payment data," not "nation-state target."

## Key Takeaways
1. Calibrate defensive effort to your actual threat model (industry sensitivity + organization size) rather than assuming either "too small to matter" or maximal paranoia.
2. Assume automated drive-by vulnerability scanning targets you regardless of profile; fixing obvious flaws to become a "hard target" is the universal minimum.
3. Track new vulnerabilities (CVEs, security news) continuously — zero-days create a race condition between disclosure and exploitation.
4. You cannot patch what you cannot see: know precisely which dependencies are deployed (sets up chapter 5's dependency-manager discipline).
5. Logging, error reporting, and monitoring must exist before an incident, because they are the only way to reconstruct what happened during forensics afterward.
6. A whole team trained to spot security issues in code review outperforms any single expert; make this a cultural investment.
7. Deadline pressure is the most common trigger for skipped security review — protect review time deliberately, especially on legacy code.

## Connects To
- **Ch 5**: "Know what code you are deploying" here is the seed of the full dependency-management, code-review, and audit-trail discipline covered in Security as a Process.
- **Ch 6**: The mention of XSS as a way hackers "target your users" after compromising your site is expanded fully into stored/reflected/DOM-based XSS.
- **Ch 13 (external)**: Tracking dependencies and applying patches, only briefly introduced here, is the dedicated subject of the book's later chapter on third-party code vulnerabilities.
- **Threat modeling (external concept)**: A standard security-engineering practice (also formalized elsewhere as STRIDE or DREAD) that this chapter introduces informally.
