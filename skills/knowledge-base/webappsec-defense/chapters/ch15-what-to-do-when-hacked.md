# Chapter 15: What to Do When You Get Hacked

## Core Idea
Breaches are inevitable given enough time and attackers; what determines the organizational outcome is the quality of the response — detecting the incident, containing it, investigating root cause, fixing it, communicating transparently with users, and de-escalating future attacks.

## Frameworks Introduced
- **Centralized logging + metric-based alerting**: aggregate every log source and alert on anomalous patterns, so incidents are detectable in progress or reconstructable after the fact.
  - When to use: continuously, as baseline infrastructure — not something you build after a breach.
  - How: centralize HTTP access, network, server, database, application, and error logs into one logging system; define alert thresholds for suspicious signals (unrecognized IPs, traffic/error spikes, heavy resource use, large data egress).
- **Contain-then-fix response sequence**: judge whether to take systems offline (or fail over to a status page) before fixing the root cause, rather than trying to fix live under attack.
  - When to use: any confirmed active incident.
  - How: a senior decision-maker weighs the cost of downtime (e.g., halting a trading system mid-market vs. a noncritical service) against the risk of continued compromise; fail over to a status page to buy time while the underlying issue (rollback, credential rotation, firewall rule, emergency patch) is fixed.
- **Digital forensics via timeline reconstruction**: piece together exactly when the vulnerability was introduced, first exploited, what the attacker did, and how it was mitigated.
  - When to use: after any suspected or confirmed breach, whether caught live or discovered after the fact.
  - How: cross-reference log files, release/deployment logs, and source-control commit history to build a chronological account, typically with input from in-house or hired cybersecurity professionals.
- **Transparent post-incident user communication**: disclose breach details even absent legal disclosure requirements, framed around what happened, what data was at risk, what you're doing about it, and what users should do.
  - When to use: after any breach involving user data or access.
  - How: senior management and legal typically draft the announcement; include a technical timeline, an assessment of what was accessed/at risk, concrete prevention steps taken, and any required user action (e.g., forced password rotation).

## Key Concepts
- **SOC (security operations center)**: a dedicated team monitoring real-time logs/graphs to detect attacks in progress, typical of larger organizations.
- **IDS (intrusion detection system)**: automated tooling (increasingly ML-based) that detects suspicious activity and raises alerts without requiring a human to be watching continuously.
- **Status page**: a subdomain (e.g., `status.example.com`) that communicates real-time operational status, used both to fail over traffic during an incident and to build a historical reliability record.
- **Digital forensics**: the process of reconstructing exactly how a breach occurred from logs, commits, and other artifacts — framed as process-improvement investigation, not blame assignment.
- **security.txt**: a standardized file (`/security.txt` or `/.well-known/security.txt`) publishing a contact channel and public key for responsible vulnerability disclosure, before an attacker resorts to exploitation or ransom.
- **Code freeze**: an organizational policy restricting releases during sensitive windows, which can complicate — but shouldn't indefinitely block — emergency patching.

## Mental Models
- Treat a breach response like triage in an emergency room: first stop the bleeding (contain/take offline/fail over), then diagnose (forensics), then treat the underlying condition (root-cause fix) — not the other way around.
- Frame forensics interviews as "looking for failures in processes, not scapegoats" — a healthy organization's post-mortem culture directly determines whether people surface problems early next time or hide them.
- Publish a `security.txt` file as a pre-negotiated, dignified off-ramp for a would-be attacker who might otherwise default to ransom or public exploitation simply because they had no legitimate channel to report what they found.

## Anti-patterns
- **Hiding after a breach**: erodes user trust further than the breach itself; transparency (technical detail, timeline, remediation, required user action) is the only path to rebuilding it.
- **Gloating or "I told you so" during root-cause review**: even if you flagged the exact risk beforehand, publicly embarrassing a manager or team "gains you a manager who resents you" — document the prior warning factually and move on to solutions.
- **Treating forensics as blame-seeking**: a healthy organization looks for process failures, not individuals to scapegoat — this is what makes people willing to surface near-misses in the future.

## Code Examples
```json
{
  "version": "2018-03-01",
  "logGroup": "/var/log/secure",
  "filterPattern": "{ ($.message like '%Failed password%') || ($.message like '%Failed publickey%') }"
}
```
- **What it demonstrates**: an AWS CloudWatch filter pattern that raises an alert on failed SSH login attempts (password or public-key auth) in `/var/log/secure`, the common Linux SSH log location.

## Reference Tables
| Response phase | Key activity | Owner/decision-maker |
|---|---|---|
| Detect | Centralized logging + alerting; IDS | SOC / automated tooling |
| Contain | Take systems offline or fail over to status page | Senior leadership (judgment call) |
| Fix | Rollback, credential rotation, firewall change, emergency patch | Engineering |
| Investigate | Digital forensics — timeline from logs/commits | In-house or hired cybersecurity professionals |
| Prevent recurrence | Process changes (patch cadence, refactor, audits, review rigor, testing, bug bounty) | Team + management |
| Communicate | Transparent user-facing disclosure | Senior management + legal |
| De-escalate future attacks | Publish `security.txt` for responsible disclosure | Engineering / security team |

## Worked Example
The 2022 Optus breach (Australian telecom) is used as the chapter's central real-world case: an attacker exploited an unsecured, unauthenticated API to enumerate personal data — names, emails, passport and driver's license numbers — for about 9.7 million current and former customers, roughly 40% of Australia's population. This is framed explicitly as a catastrophic authorization failure (tying directly back to Chapter 10's access-control lessons), not a sophisticated exploit.

The attacker initially posted a ransom demand of AU$1 million on a hacking forum, a steep discount against the roughly AU$140 million Optus ultimately spent reissuing passports for affected customers. Notably, the attacker (posting under a pseudonymous avatar) stated they would have preferred to responsibly disclose the vulnerability if Optus had provided any way to contact them. This detail is the chapter's argument for publishing a `security.txt` file: had Optus published one, pointing to a contact channel and public key, this particular attacker's own stated preference suggests the incident might have been resolved through responsible disclosure rather than a mass ransom-driven breach — illustrating that "deescalating future attacks" is sometimes as simple as making it possible for good-faith(-ish) discoverers to reach you before they decide exploitation is the only option.

## Key Takeaways
1. Build centralized logging and metric-based alerting before you need it — detection depends entirely on this being in place beforehand.
2. Have a senior-level protocol for the contain-vs-continue-operating decision; don't leave it ad hoc in the middle of an incident.
3. Use a status page to fail over gracefully while you diagnose and fix, buying time without leaving users in the dark.
4. Reconstruct a forensic timeline from logs, deploy history, and commits — treat it as process diagnosis, not blame assignment.
5. Convert root-cause findings into concrete process changes (patch cadence, review rigor, testing, bug bounties) rather than one-off fixes.
6. Communicate breach details to users transparently: what happened, what was at risk, what you're doing, and what they need to do.
7. Publish a `security.txt` file so good-faith vulnerability finders have a legitimate channel to reach you before resorting to exploitation or ransom.

## Connects To
- **Ch 10**: the Optus breach is explicitly framed as an authorization/access-control failure — this chapter's forensic response assumes lessons from Ch 10 as prevention.
- **Ch 8/9**: forced credential rotation and session invalidation are standard post-breach remediation steps directly tied to how credentials and sessions were designed earlier.
- **Ch 14**: the Optus case also appears in Chapter 14 as an example of unauthenticated API abuse — both chapters use it to anchor different lessons (access control vs. incident response).
