# Chapter 47: Defending Against DoS

## Core Idea
DoS defense splits into three distinct problems requiring different tooling — regex DoS is stopped at code review, logical DoS requires risk-tiering exposed functionality instead of a binary secure/vulnerable judgment, and DDoS can only be mitigated (never fully prevented) through bandwidth management services and blackholing.

## Frameworks Introduced
- **DoS Risk Categorization (high/medium/low)**: Evaluate exposed functionality on a resource-consumption scale rather than a binary vulnerable/secure label.
  - When to use: Auditing an application's endpoints and functions for logical DoS exposure, where "vulnerable" isn't a yes/no question the way XSS is.
  - How: For each function that touches system resources, estimate how much attacker effort is required to exhaust them (device power, request volume, data size). Extremely-difficult-to-exploit code is "safe"; anything easier is "vulnerable" — err toward the vulnerable classification when uncertain.
- **Evil Regex Code Review**: Catch regex DoS (ReDoS) sinks before they enter the codebase via static review.
  - When to use: Any code review touching regular expressions, especially ones built from user-influenced patterns.
  - How: Look for regex with significant backtracking against a repeated group (pattern shape like `(a[ab]*)+`), where `+` forces greedy matching and `*` forces maximal subexpression repetition. Use an OSS regex-scanning tool or a performance tester to check suspect patterns; also ensure no endpoint accepts a user-supplied regex at all.
- **DDoS Mitigation Stack**: Layered defenses since DDoS cannot be prevented, only mitigated.
  - When to use: Any internet-facing application, proportional to how much traffic-volume risk it can absorb.
  - How: (1) Contract a bandwidth management service to scan and drop malicious-pattern packets before they reach your server; (2) implement blackholing — route suspicious/repeated traffic to a decoy server that performs no real operations while legitimate traffic reaches the real application server; (3) gather deep usage metrics on legitimate traffic first, since oversensitive filters block real users too.

## Key Concepts
- **DoS (Denial of Service)**: An attack aiming to exhaust server resources, exhaust client resources, request unavailable resources, or deny access to resources.
- **DDoS (Distributed Denial of Service)**: A DoS attack launched from many sources under centralized control, usually overwhelming by sheer traffic volume rather than exploiting a logic bug.
- **Botnet**: A network of compromised devices (PCs, mobile, IoT) running attacker-controlled malware, used en masse to conduct a DDoS attack.
- **Regex DoS (ReDoS)**: A DoS caused by a regular expression with catastrophic backtracking against attacker-supplied input.
- **Logical DoS**: A DoS caused by an application logic path that consumes disproportionate system resources, without needing a regex bug.
- **Blackholing**: Routing suspicious or repeated traffic to a decoy server that mimics the application but performs no real work, while legitimate traffic reaches the real server.
- **Bandwidth management service**: A third-party vendor that inspects packets in transit and filters out malicious-pattern traffic before it reaches your infrastructure.

## Mental Models
- Think of DoS risk as a dial, not a switch: unlike XSS (binary — exploit exists or it doesn't), the same function can be "safe" on a powerful desktop and "vulnerable" on an old mobile device — classify by resource cost, not presence/absence of a flaw.
- Treat comprehensive request/response-time logging as your DoS smoke detector: without it, a DoS attack that came through a legitimate-looking API channel is nearly undetectable after the fact.
- Treat DDoS mitigation like triage in an ER, not like a lock on a door — you're not preventing all attackers from arriving, you're routing the worst cases away from resources that matter while accepting some misclassification risk on both sides.

## Anti-patterns
- **Allowing user-supplied regular expressions anywhere in the application**: Even a well-reviewed regex engine can't protect you if the pattern itself is attacker-authored — "like walking through a minefield and hoping you memorized the safe-route map."
- **Judging DoS exposure as simply vulnerable/secure**: Treating DoS like a binary (the way you'd treat XSS) causes you to under-prioritize functions that are only exploitable under specific resource conditions.
- **Deploying DDoS filters without baseline traffic metrics**: Aggressive blackholing or bandwidth filtering with no prior model of legitimate usage patterns will block real users along with attackers.
- **Relying on blackholing alone against large-scale DDoS**: Blackholes work reasonably against small-scale attacks but perform poorly once attack volume scales up — they need to be paired with a bandwidth management service.

## Code Examples
```text
(a[ab]*)+
```
- **What it demonstrates**: The canonical "evil regex" shape — a repeated group under both `*` (match subexpression as many times as possible) and `+` (greedy, exhaustive matching) — that a static reviewer or scanner should flag as a ReDoS sink.

## Reference Tables
| DoS attack goal | Description |
|---|---|
| Exhaust server resources | Consume CPU/memory/connections on the backend |
| Exhaust client resources | Force excessive work in the victim's browser/device |
| Request unavailable resources | Force lookups/allocations for resources that don't exist, wasting cycles |
| Deny access to resources | Lock out legitimate users from resources they need |

| DoS type | Attacker profile | Primary defense |
|---|---|---|
| Regex DoS | Single attacker, exploits a coding bug | Static code review for evil regex patterns; ban user-supplied regex |
| Logical DoS | Single attacker, exploits resource-heavy logic | Risk-tier functionality by resource cost (high/med/low) |
| DDoS | Distributed botnet, overwhelms by volume | Bandwidth management service + blackholing, backed by usage metrics |

## Worked Example
A team ships an API endpoint that accepts a user-provided search pattern and matches it against a large text field using a regex built with string concatenation.

1. **Detection prerequisite**: Because the endpoint responds synchronously and looks like ordinary traffic, the team can only catch an in-the-wild exploit attempt if they've already instrumented comprehensive request logging with response times — without it, a slow regex match blends into background noise.
2. **Code review catches the sink**: During review, a reviewer recognizes the pattern-construction logic could produce a shape like `(a[ab]*)+` if the user input is inserted into a subexpression with both `*` and `+` quantifiers — a backtracking bomb.
3. **First fix — eliminate user-supplied regex entirely**: Rather than trying to sanitize arbitrary user regex (fragile, hard to audit), the endpoint is redesigned to only accept a fixed enum of predefined search modes, removing the sink altogether.
4. **Second fix — static scanning**: The team adds an OSS regex linter to CI to catch any future evil-regex patterns introduced elsewhere in the codebase, since manual review alone doesn't scale.
5. **DDoS layer, separately**: For the application as a whole, the team contracts a bandwidth management service to filter malicious-pattern packets, and stands up a blackhole server for suspicious repeat traffic — but only after building usage-pattern metrics so the filters don't reject legitimate spikes (e.g., a marketing launch).

## Key Takeaways
1. Build comprehensive request/response-time logging first — it's the only way to detect a DoS attempt that arrived through a legitimate-looking channel after the fact.
2. Catch regex DoS at code review time by pattern-matching for backtracking-prone shapes like `(a[ab]*)+`, and never allow user-supplied regex into production matching logic.
3. Classify exposed functionality by DoS risk on a high/medium/low scale, not a binary vulnerable/secure judgment — resource-consumption attacks don't behave like all-or-nothing exploits.
4. DDoS cannot be prevented, only mitigated — combine a bandwidth management service with blackholing, and always baseline legitimate traffic patterns first to avoid blocking real users.
5. Blackholing scales down (effective against small DDoS) but not up (weak against large-scale DDoS) — don't rely on it as your sole DDoS defense.

## Connects To
- **Denial of Service (DoS) — Offense chapter**: This chapter directly mitigates the four DoS goals (exhaust server/client resources, request unavailable resources, deny access) and the regex-backtracking and botnet mechanics described there.
- **Chapter 14 (referenced)**: The four DoS attack outcomes this chapter's defenses are structured around originate from that earlier discussion.
