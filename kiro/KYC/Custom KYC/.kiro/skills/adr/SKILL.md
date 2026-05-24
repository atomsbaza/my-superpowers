---
name: adr
description: "Capture architectural decisions made during KYC platform work. Use when choosing between significant alternatives (auth scheme, DB pattern, framework, service split), when someone says 'ADR this' or 'why did we choose X?'. Stores decisions in .kiro/steering/decisions/ and offers to publish to Confluence EKYC space."
---

# Architecture Decision Records (KYC)

Architectural decisions made in chat or PR comments are lost. Decisions that live in `.kiro/steering/decisions/` survive team changes, refactors, and onboarding.

## When to activate

- "ADR this", "record this decision", "document why we chose X"
- A significant choice is made during planning or coding (auth pattern, library, service boundary, DB strategy, versioning approach)
- "Why do we use HMAC instead of JWT?", "Why MySQL and not Postgres?" → read existing ADRs
- A decision is revisited — update status to `superseded`

---

## Writing a new ADR

1. **Identify the core decision** — one clear, nameable choice
2. **Gather KYC context** — which services are affected? Compliance implications? .NET version constraint?
3. **List alternatives** — what else was considered and why rejected?
4. **State consequences** — what becomes easier or harder across the KYC monorepo?
5. **Scan existing ADRs** in `.kiro/steering/decisions/` — increment the number
6. **Present draft for review** before writing any file
7. **Write after approval** → `.kiro/steering/decisions/NNNN-decision-title.md`
8. **Offer to publish** to Confluence EKYC space

---

## ADR format

```markdown
# ADR-NNNN: [Decision Title]

**Date:** YYYY-MM-DD
**Status:** accepted
**Services affected:** [e.g. all services / kyc-partner-api, identification]

## Context

What situation or constraint prompted this decision?
What KYC/compliance/operational forces are at play?
(2–4 sentences)

## Decision

What was decided, stated clearly.
(1–2 sentences)

## Alternatives Considered

### [Alternative 1]
- **Pros:** ...
- **Cons:** ...
- **Why rejected:** ...

### [Alternative 2]
- **Pros:** ...
- **Cons:** ...
- **Why rejected:** ...

## Consequences

### Positive
- ...

### Negative / Trade-offs
- ...

### Risks
- [risk] — [mitigation]
```

---

## KYC decision examples (for context when writing)

| Decision area | Example ADR title |
|---|---|
| Auth | "Use HMAC over JWT for internal service-to-service auth" |
| DB | "Primary/Replica split — reads on Replica, writes on Primary" |
| Encryption | "AES via EntitiesExtra partial classes for PII at rest" |
| Versioning | "URL-segment versioning (/api/v{n}/) over header versioning" |
| Messaging | "AWS SQS for async CDD trigger — no direct service call" |
| Framework | "Migrate kyc-partner-api from .NET 6 to .NET 8 in next quarter" |
| Error shape | "Standardise all errors as {code, description} with shared code table" |
| HMAC scheme | "Use ApiKey scheme (.NET 8+) over basic scheme (.NET 6) for new services" |

---

## Publishing to Confluence

After writing the ADR file, offer:

> "Want me to publish this to Confluence?"

If yes:
- **Space:** EKYC
- **Parent page:** Architecture Decisions section
- **Title:** `ADR-NNNN: [Decision Title]`
- **Format:** Markdown → Confluence markup

---

## Reading existing ADRs

When asked "why did we choose X?":
1. List files in `.kiro/steering/decisions/`
2. Read the matching ADR
3. Present **Context** + **Decision** + **Alternatives Considered**
4. If no ADR found: "No ADR recorded for that decision. Would you like to write one now?"

---

## Rules

- Never write the file without user review of the draft first
- One decision per ADR — do not bundle
- Status: `proposed` / `accepted` / `deprecated` / `superseded by ADR-NNNN`
- Use KYC domain vocabulary (StatusCode not status, PrimaryDbContext not write DB)
- Context section under 5 sentences — if it needs more, split into two ADRs
