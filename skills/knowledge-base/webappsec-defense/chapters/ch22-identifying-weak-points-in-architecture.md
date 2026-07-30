# Chapter 22: Identifying Weak Points in Application Architecture

## Core Idea
Most real-world vulnerabilities stem from systemic architecture weaknesses — inconsistent security layering and organizational reinvention of mature technology — rather than isolated coding mistakes, so recon should prioritize functionality with a low ratio of security mechanisms to layers, and defenders should prioritize architectural consistency over one-off fixes.

## Frameworks Introduced
- **Security maturity model (three tiers)**: Applications fall into secure-by-design (mechanisms built in before/during feature development), bolted-on (mechanisms added only during feature development), or none (no mechanisms) tiers.
  - When to use: When judging how much effort to invest hunting for vulnerabilities in a given application or feature area.
  - How: Look for evidence of centralized, reusable security utilities (e.g., a shared sanitizing DOM-write function) versus per-feature, ad hoc reimplementation; the fewer centralized mechanisms observed, the higher tier of risk.
- **Multiple layers of security**: For any given vulnerability class (XSS, XXE, CSRF), defenses should exist redundantly at more than one layer (API write, database write, database read, API read, client read) so that a gap opening at one layer doesn't expose the whole system.
  - When to use: Designing or auditing defenses against any specific vulnerability class.
  - How: Enumerate every layer data passes through for a given feature; confirm at least one independent defensive mechanism exists at more than one of those layers, since different layers can support different mechanism types (e.g., a headless-browser script-execution check is only feasible at the API layer, not the database layer).
- **Adopt-vs-reinvent decision rule**: Reinvent only purely functional features (comment schemas, notification systems); never reinvent features requiring deep math/OS/hardware expertise (cryptography, databases, process isolation, memory management).
  - When to use: Evaluating whether a custom-built subsystem is a red flag during recon, or deciding whether to build vs. adopt during development.
  - How: Ask whether matching an established open, heavily-tested implementation (e.g., NIST-vetted SHA-3) would cost the organization more in engineering/testing effort than simply adopting it for free — for math/OS/hardware-heavy domains, the answer is almost always yes.

## Key Concepts
- **Weak point in architecture**: A functional area where security mechanisms are inconsistently applied across the layers data flows through, making it more exploitable than functionally similar areas with consistent layering.
- **DOMPurify**: A widely used sanitization library referenced as the correct implementation detail behind a secure-default DOM-write utility (see Ch18).
- **Solutions-space reduction via architecture, not code**: A single well-designed centralized function (e.g., `appendToDOM`) can eliminate an entire vulnerability class app-wide, versus fixing bugs one call site at a time.
- **Rolling your own cryptography (anti-pattern)**: Building custom hashing/crypto algorithms instead of adopting vetted, heavily-tested standards (SHA-3/NIST) — near-guaranteed to underperform against real attacks (combinator, Markov, etc.) given the engineering cost gap.
- **Organizational drivers of reinvention**: Licensing avoidance, desire for extra functionality, and marketing/publicity value are legitimate business reasons developers cite for reinventing existing tools — but they are organizational, not architectural, in origin.
- **Recon documentation checklist**: Technology used, API endpoints by verb, endpoint shapes, functionality inventory, domains, configuration (e.g., CSP), and auth/session systems — the complete "map" contents this chapter assumes are already gathered from Ch18-21.

## Mental Models
- Think of an application's defenses like a building's fire-suppression system: a single working sprinkler head (one security mechanism at one layer) is not sufficient if every other floor (layer) has none — redundancy across layers is what actually contains a breach.
- Use "ratio of security mechanisms to layers" as your recon prioritization score: functionality with many data-flow layers but few enforced mechanisms is the highest-value target, since features with good architecture stay consistently defended everywhere, while weak ones have exploitable gaps somewhere.
- Treat "reinvented mission-critical infrastructure" (custom crypto, custom DB, custom process isolation) as a structural red flag during recon — it reliably correlates with exploitable weaknesses because achieving parity with vetted implementations is prohibitively expensive.

## Anti-patterns
- **Single-layer defense**: Implementing a security mechanism (e.g., input sanitization) only at the original entry point (single-message API) and not at every subsequent path that reaches the same sink (e.g., a newly added bulk-message API) — new code paths bypass the original protection entirely.
- **Reinventing math/OS/hardware-heavy infrastructure**: Custom cryptography, custom databases, or custom memory management, which cannot realistically match the testing rigor of vetted, community-reviewed alternatives (e.g., SHA-3 vetted by NIST for ~20 years).
- **Treating architecture as a purely high-level, non-actionable discussion**: Dismissing architectural analysis as "too abstract" for hands-on security work misses that architecture-level gaps predict where code-level bugs will cluster.

## Code Examples
```javascript
// client/send.js — collects message + target from the DOM, sends via API
const send = function () {
  const message = document.querySelector('#send').value;
  const target = document.querySelector('#target').value;
  messageUtils.sendMessageToServer(session.token, target, message);
};

// server/postMessage.js — the single layer where this app validates/sanitizes
const postMessage = function (req, res) {
  if (!req.body.token || !req.body.target || !req.body.message) {
    return res.sendStatus(400);
  }
  saveMessage(req.body.token, req.body.target, req.body.message)
    .then(() => res.sendStatus(200))
    .catch((err) => res.sendStatus(400));
};

// client/displayMessage.js — the read-side layer, where an unsanitized
// message would be rendered back into the DOM if appendToDOM lacked
// the secure-default pattern from Ch18
const displayMessage = function (msgId) {
  messageUtils.getMessageById(session.token, msgId)
    .then((msg) => {
      messageUtils.appendToDOM('#message', msg);
      messageUtils.appendToDOM('#message-author', msg.author);
    })
    .catch(() => console.log('an error occured'));
};
```
- **What it demonstrates**: A minimal instant-messaging feature's full data path (client write → API POST → DB write → API GET → client read) — the exact five "layers" the chapter uses to illustrate where redundant XSS defenses should each independently exist.

## Reference Tables
Layers where a single vulnerability class (e.g., XSS) can be independently defended, per the chapter's messaging example:

| Layer | Defense example |
|---|---|
| API POST | Reject/sanitize payloads containing script before writing to DB |
| Database write | Reject or escape script-like content at the storage layer |
| Database read | Re-validate/sanitize on read, independent of what was stored |
| API GET | Headless-browser rendering check to detect script execution before returning data |
| Client read | Secure-default DOM-write utility (`appendToDOM`, Ch18) as the last line of defense |

## Worked Example
The chapter's messaging-app case study, extended to a specific failure scenario:

1. **Baseline**: A messaging feature sanitizes user input at the original single-message `API POST` endpoint, eliminating XSS via that path.
2. **New feature added later**: A separate team ships a new bulk-messaging `API POST` endpoint (`/messages/bulk`) to support sending several messages at once, but its sanitization is weaker or missing entirely.
3. **The gap**: Because the original defense existed only at the single-message API layer — not also at the database-write layer — the new bulk endpoint can insert script payloads directly into the same database table the single-message endpoint writes to, bypassing the original protection entirely.
4. **Why layering would have prevented it**: Had the team also enforced sanitization at the database-write layer (independent of which API endpoint produced the write), the new bulk endpoint's gap would have been caught before persistence, regardless of which upstream code path introduced it.
5. **The generalized lesson**: An application is only as secure as its weakest layer for a given vulnerability class; redundant, layer-independent mechanisms (not just one well-defended entry point) are what make new code additions safe by default.

## Key Takeaways
1. Prioritize recon effort on functionality with many data-flow layers but few observed security mechanisms — that ratio predicts exploitability better than any single code review.
2. Defend each vulnerability class redundantly across multiple layers (API write, DB write, DB read, API read, client read), not just at the original entry point.
3. New code paths (a bulk API added later) can silently bypass defenses that were only ever implemented at one original layer — audit for this specifically after any new endpoint ships.
4. Never reinvent cryptography, databases, or other math/OS/hardware-heavy infrastructure — the engineering cost to match vetted, community-tested implementations is prohibitive.
5. It is fine, and often preferable, to reinvent purely functional features (custom comment schemas, notification systems) where no deep specialized expertise is required.
6. Document a full recon "map" (tech, endpoints, shapes, functionality, domains, config, auth) before attempting architectural weak-point analysis — this chapter assumes that data already exists.

## Connects To
- **Ch18 (global)**: The centralized, secure-default `appendToDOM` pattern introduced there is the concrete "good architecture" example this chapter builds its multi-layer defense argument around.
- **Ch17 (global)**: The recon documentation checklist referenced here is a direct expansion of the "map" concept introduced in the Introduction to Recon chapter.
- **Ch23 (global)**: This chapter's architectural weak-point analysis is the final individual recon skill before Ch23 synthesizes all of Part I (Recon) into a bridge toward Offense.
- **Ch24-34 (Offense, global) / Ch35-52 (Defense, global)**: The adopt-vs-reinvent rule and multi-layer defense framework here are the conceptual seeds for specific offensive techniques (exploiting single-layer gaps) and defensive architecture guidance later.
