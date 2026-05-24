---
name: flow-tracer
description: Trace the full request flow of an API endpoint or feature across KYC services. Use when asked "how does X work?", "trace the flow of X", "what happens when X is called", or when investigating how a request travels through the system. Pairs with: log-investigator, incident-debugger subagents.
---

# Flow Tracer

Systematically trace a request's journey through the KYC platform — from API entry to final response, across service boundaries.

## When to invoke

- "how does [endpoint/feature] work?"
- "trace the flow of [endpoint]"
- "what happens when [action] is called?"
- "walk me through [feature]"
- "explain the [endpoint] flow end-to-end"

## Process

### 1. Identify the entry point

Determine which service receives the initial request:
- External partner call → `kyc-partner-api`
- Admin action → `kyc-admin-portal`
- Internal trigger (SQS) → `kyc-customer-due-diligence`

### 2. Trace the chain

For each hop in the flow, document:

```
[Service] Controller/Endpoint
  → Validation (FluentValidation / manual)
  → Handler (MediatR)
    → Business logic / decisions
    → External calls (other services / third-party APIs)
    → Database operations (read/write, which DbContext)
    → Side effects (SQS publish, email, audit log)
  → Response mapping
```

### 3. Cross-service calls

When the flow crosses service boundaries, document:
- Which client class makes the call (`IKycVerificationClient`, `IZolozClient`, etc.)
- Auth mechanism (HMAC internal, OAuth, anonymous)
- Request/response contract
- Error handling (what happens if the downstream service fails?)

### 4. Decision points

Highlight branching logic:
- What determines the path? (config flags, input values, DB state)
- What are the possible outcomes?
- Which outcomes stop the flow early (validation failure, NotPass, etc.)?

### 5. Output format

```
## Flow: [endpoint/feature name]

### Entry
- Service: [name]
- Endpoint: [method] [path]
- Auth: [HMAC / OAuth / partner token]

### Step 1: [description]
- File: [path]
- Logic: [what happens]
- Outcome: [result / next step]

### Step 2: [description]
...

### Cross-service call: [service → service]
- Client: [class name]
- Endpoint called: [path]
- On success: [next step]
- On failure: [error handling]

### Response
- Success: [shape + code]
- Error cases: [list with codes]

### Sequence diagram
```mermaid
sequenceDiagram
  participant P as Partner
  participant API as kyc-partner-api
  participant V as verification
  ...
```
```

## Rules

- **Read the actual code** — don't guess from naming conventions. Search the knowledge base, then read the handler file.
- **Follow the real path** — trace through MediatR dispatch, not just the controller.
- **Document error paths** — what happens when each step fails? This is often more valuable than the happy path.
- **Note version differences** — if V1/V2/V3 exist, mention which version you're tracing and key differences.
- **Include config dependencies** — if behavior depends on settings (company config, feature flags), note them.
- **Keep it scannable** — use the structured format above. Engineers will reference this, not read it linearly.

## Publish to Confluence

After producing the flow trace, offer to publish:

> "Want me to publish this to Confluence?"

If yes:
- **Space:** EKYC
- **Parent page:** Determine from the feature area (e.g., Individual Person Details page for save individual flow)
- **Title:** `Flow: [feature name]`
- **Format:** Markdown with Mermaid sequence diagram
- **Ask for parent page** if not obvious from context

Common parent pages:
- Individual Person flows → page ID `315252233` (Individual Person Details)
- Business Customer flows → find under Business Customer section
- CDD flows → find under CDD section
- General architecture → create under Architecture section


## Live Trace from OpenSearch

When given a specific RequestId or CorrelationId, trace the actual execution in production/SIT logs.

### Search strategies

| Have | Search with | Index |
|------|-------------|-------|
| RequestId (`0HNLNQ33EEER0:00000001`) | `query_string: "0HNLNQ33EEER0:00000001"` | `kyc-{service}-*` |
| CorrelationId (UUID) | `fields.CorrelationId: "{uuid}"` | `kyc-*` (all services) |
| ApplicationId | `query_string: "{id}"` | `kyc-*` |

### RequestId format
Kestrel generates: `{ConnectionId}:{RequestNumber}` (e.g., `0HNLNQ33EEER0:00000001`)
- Same RequestId = same HTTP request within one service
- To follow across services, use CorrelationId (flows via `X-Correlation-Id` header)

### OpenSearch index naming
```
kyc-identification-api-{yyyy.MM}
kyc-partner-api-{yyyy.MM}
kyc-verification-api-{yyyy.MM}
kyc-cdd-individual-api-{yyyy.MM}
kyc-admin-portal-api-{yyyy.MM}
kyc-risk-rating-individual-api-{yyyy.MM}
```

**Note:** Some services (e.g., `kyc-cdd-business-worker`) may NOT have an OpenSearch index. Check Argo/kubectl logs as fallback.

### Build timeline

Sort results by `@timestamp` ascending to reconstruct the execution order:
```json
{"query": {"query_string": {"default_field": "*", "query": "\"<RequestId>\""}}, "sort": [{"@timestamp": "asc"}]}
```

### Key log patterns to look for

| Pattern | Meaning |
|---------|---------|
| `Start {ActionName}` | Request entered the service |
| `End {ActionName} in {ProcessingTime}s` | Request completed (check StatusCode) |
| `The {Refer} from {Caller} authorized` | HMAC auth passed |
| `Calling {Url}` | Outbound HTTP call starting |
| `Received HTTP response headers after {ms} - {StatusCode}` | Downstream response |
| `Database transaction committed` | DB write succeeded |
| `CDD SQS sent successfully` | SQS message published |
| `Failed to send CDD` | SQS publish failed (check IAM) |

### Common issues found via live trace

| Symptom in logs | Root cause |
|-----------------|-----------|
| No logs in downstream service | Message never arrived (IAM denied, wrong queue URL) |
| Auth log missing, 401 returned | HMAC scheme mismatch (basic vs ApiKey) |
| `StatusCode: 204` from verification | DOPA accepted (fire-and-forget, no response body) |
| Deserialization error in consumer | Contract mismatch between producer and consumer DTOs |
