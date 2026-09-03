# MCP Security Doctrine & Harness Engineering (2026-09-03)

Adapted from the X-scout knowledge-scout digest of 2026-09-03 (Discord thread
#xTreand, cron job f933f5a8d591). Three sources, one converging theme: **the
agentic middleman is probabilistic, so classic auth and logging assumptions
break**. Plus one adjacent piece on harness engineering.

## 1. The MCP authentication gap (API Evangelist)

Source: apievangelist.com/2026/09/03/the-mcp-authentication-and-authorization-gap/

- Production MCP servers mostly use **long-lived god-mode API keys in env
  vars** — i.e. no auth layer at all once the agent is compromised or injected.
- When the middleman is an injectable probabilistic model, the human-judgment
  backstop disappears; a leaked god-mode key is total compromise.
- The standard already exists: **OAuth 2.1 + Dynamic Client Registration +
  token exchange** → the agent holds **narrowly-scoped short-lived tokens per
  task**, not a standing credential.

## 2. Tool output is an untrusted instruction surface nobody logs (Digital Applied)

Source: Digital Applied MCP server audit, 2026-09-02 (19 popular MCP servers
audited; injection path found in Context7, widely wired into coding agents).

- Tool responses are treated as trusted data by most agent stacks, but they are
  attacker-controlled input (indirect prompt injection via tool results).
- **Log tool returns OUTSIDE the agent's trust boundary** — otherwise the
  audit trail is editable by the very attack you are auditing for.
- Doctrine: treat every tool response as untrusted input, same tier as a web
  page fetched from a hostile site.

## 3. Security posture = 7 dials scoped per trust level (@tonbistudio)

Source: https://x.com/tonbistudio/status/2093764090619638228 (masterclass;
real attacks shown, 3 of 4 stopped).

- Capability ↔ security is a trade-off: **no agent is fully safe AND fully
  capable**. Each layer is a dial: trust, approvals, containers, filters,
  hardening (plus scoping of the dial set per profile).
- External/webhook/scraped input paths → default-deny approvals + sandboxed
  backend + blocklist.
- Maps directly to profile-based agent tiering: each worker profile gets its
  own dial settings, not a global policy.

## 4. Adjacent: harness engineering (@0xwhrrari)

Source: https://x.com/0xwhrrari/status/2093685107534000560 (X Article, ~12 min)

- "Failure should upgrade the system": patching one run fixes one run; patching
  the harness fixes every future run.
- Convert the request to a **CONTRACT before the agent works** — prevents
  silent task redefinition mid-run.
- Separate **brain / hands / history** (reasoning model, executing tools,
  persistent state) so each can be hardened and versioned independently.

## Durability assessment

- MCP auth doctrine and untrusted-tool-output logging: durable (standard-based,
  principle-level, valid in 6 months). → merged into `skills/quality/ai-agent-security/`.
- 7-dials vocabulary: durable as a decision aid. → merged into the same skill.
- Harness engineering contract/harness principles: durable. → cross-referenced
  from the same skill's verification section; matches repo AGENTS.md doctrine.
- Excluded as transient: Uber session-cost decomposition (vendor-specific
  economics), six-bot media company writeup (unverified skim).
