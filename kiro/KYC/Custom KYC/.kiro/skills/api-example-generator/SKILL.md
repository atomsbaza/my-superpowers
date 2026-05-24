---
name: api-example-generator
description: Generate Postman-ready JSON request/response examples from C# request DTOs. Use when asked for API examples, sample requests, Postman bodies, or when onboarding partners to an endpoint.
---

# API Example Generator

Generate realistic JSON examples from C# request/response DTOs for use in Postman, documentation, or partner onboarding.

## When to invoke

- "give me a sample request for [endpoint]"
- "create Postman body for [endpoint]"
- "example JSON for [endpoint]"
- "what does the request look like for [endpoint]?"
- When onboarding a partner to a new API

## Process

1. **Find the request DTO** — search for the MediatR request class (implements `IRequest<TResponse>`)
2. **Read all properties** — including nested objects, lists, and validation attributes
3. **Generate realistic values** based on:
   - `[MaxLength(N)]` → generate string within limit
   - `[Required]` → always include
   - `[RegularExpression]` → match the pattern
   - Property name hints (email → valid email, tel → Thai phone, citizenId → 13 digits, etc.)
   - Optional fields → include with comment noting they're optional
4. **Include nested objects** — recursively generate for address, questionnaire, document list, etc.
5. **Output as JSON** — ready to paste into Postman

## Output format

```json
// POST /api/v{version}/{path}
// Headers: X-Refer, X-Client, X-Request-Time, Authorization (HMAC)
{
  "field": "value"
}
```

## Value generation rules

| Field pattern | Generated value |
|---|---|
| `*Id` (numeric) | `1` or realistic ID |
| `*Id` (string, citizen) | Valid 13-digit Thai ID with checksum |
| `*Email*` | `test@example.com` |
| `*Tel*`, `*Phone*`, `*Mobile*` | `0891234567` |
| `*Date*` | `2024-01-15` (yyyy-MM-dd) |
| `*Name*` | Realistic Thai/English name |
| `*Address*` | Realistic Thai address |
| `*Country*` | `THA` (3-char alpha) |
| `*Amount*`, `*Capital*`, `*Size*` | Realistic decimal |
| `*Image*`, `*Document*` | `"<base64-encoded-image>"` with note |
| `*TransactionId*` | UUID or prefixed ID |
| `*Code*` (enum-like) | Use known codes from the system (ATS001, YOR003, etc.) |
| `*Url*`, `*Website*` | `https://www.example.com` |
| `*ZipCode*` | `10110` |

## Also generate

- **Success response** example
- **Error response** example (E03 validation error)
- **Required headers** reminder (HMAC auth)
- **Notes** about encrypted fields (citizenId, passportNo are AES encrypted in transit)

## Rules

- Read the actual DTO class — don't guess field names
- Respect camelCase serialization (our APIs use `CamelCasePropertyNamesContractResolver`)
- Mark optional fields with comments
- Note which fields are AES-encrypted (citizenId, passportNo, laserId)
- Include all nested objects fully expanded
- If a field has known enum values (from Constants or enums), list them in a comment
