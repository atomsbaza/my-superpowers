# Crypto Test Gateway — Specification

| | |
|---|---|
| **Status** | Draft |
| **Date** | 2026-07-09 |
| **Owner** | QA / Platform |
| **Scope** | Refactor of the existing internal "test page" project into a headless HTTP API for integration testing and AI-agent access to the 8 internal API services |

---

## 1. Problem & Goals

### 1.1 Problem

Our 8 internal API services (plus the admin portal) require request payloads encrypted per an internal spec: a hybrid scheme where the request body is encrypted with an AES session key, the session key is protected with PGP/RSA, and the payload is signed. No plain-JSON client can talk to these APIs directly.

Today the only working, trusted implementation of that crypto spec lives inside a manually operated internal "test page" web project. QA opens the page in a browser, pastes a payload, clicks a button, and the page encrypts, signs, sends, and decrypts. This has three consequences:

1. **The crypto knowledge is trapped in a UI.** Automated integration tests and AI agents (Claude Code and similar) cannot reuse it. Every automated test against a real API today either doesn't exist or requires a human clicking through the test page.
2. **Reimplementation is risky and expensive.** Any consumer that wants automated access must reimplement the PGP/AES/signing spec. Each reimplementation is a new source of subtle bugs (padding, key wrapping, signature ordering, encoding), and each one must be kept in sync when the spec changes.
3. **Diagnostic ambiguity.** When a home-grown crypto client gets a rejection from a real API, nobody knows whether the test's crypto is wrong or the API is wrong. Debugging burns hours comparing byte-level payloads.

The fix is not to write documentation, and not to build a new crypto client. It is to promote the one implementation everyone already trusts — the test page's — into a callable service.

### 1.2 Goals

| ID | Goal |
|----|------|
| G1 | Plain-JSON integration testing against all 8 services: any test framework can call a real API in dev/SIT/UAT by sending ordinary JSON to the gateway, with encryption handled transparently. |
| G2 | AI-agent-callable: an agent can discover the API (OpenAPI), call it, and **self-diagnose failures** from structured error responses without human help. |
| G3 | A single audited implementation of the crypto spec, extracted from the test page, covered by tests, and reused by every consumer (including the test page UI itself). |
| G4 | Zero key exposure to callers: no consumer of the gateway ever holds crypto keys or implements any part of the crypto spec. |

### 1.3 Non-goals

- **Not a production gateway.** It must never carry production traffic and must actively refuse production hosts (see §6).
- **Not a general-purpose API proxy.** Only the configured internal services, only in test environments.
- **No UI rewrite required.** The existing test page UI may remain; the target end-state is that it becomes a thin client of the new API, but retiring or restyling it is out of scope.
- **Not a key-management system.** Keys are consumed from existing secret storage; provisioning/rotation processes are unchanged.

---

## 2. Adoption Strategy

**This is a refactor of the existing test page, not a green-field build.** The test page's crypto code is the asset we are extracting; a from-scratch implementation would recreate exactly the reimplementation risk described in §1.1. We follow a strangler-style migration: extract, wrap, redirect, then extend — with a behavioral safety net at every step.

### Phase 0 — Inventory

Locate and document what exists before touching anything.

- Find the crypto code in the test page: the encrypt/decrypt/sign/verify functions (in a Blazor Web App these typically live in `@code` blocks, `.razor.cs` code-behind partial classes, or injected services registered in `Program.cs`). Also check for JS interop calls doing crypto in the browser (e.g. openpgp.js) — any such code must be ported to server-side C# during extraction.
- Find the per-service configuration: which keys, endpoints, environments, and signing identities are used for each of the 8 services; where key material currently lives (files on the host? config? a vault?).
- Find the request-sending code: how the page builds headers, wraps the encrypted body, and calls upstream.
- **Document the current crypto spec as executable knowledge**: capture round-trip fixtures — real (non-sensitive or sanitized) plain payloads plus the exact ciphertext, wrapped key, and signature the current test page produces for them, and the upstream responses. These fixtures are the ground truth for everything that follows.

### Phase 1 — Extract the core crypto library

Pull the crypto functions out of the UI code-behind into a standalone library/module with no UI or HTTP dependencies.

- Public surface: `Encrypt(plainBytes, serviceKeyRef)`, `Decrypt(cipherEnvelope, serviceKeyRef)`, `Sign(...)`, `Verify(...)` plus whatever envelope-building helpers the spec needs.
- Unit tests, plus **golden test vectors** built from the Phase 0 fixtures: the extracted library must produce byte-identical output (or, where randomness is involved — e.g. AES session keys/IVs — output that the original code path can decrypt and verify) for every captured fixture.
- The golden vectors are the safety net proving behavior did not change during extraction. No refactor lands without them passing.
- Review the extracted AES code against the companion [AES-GCM review checklist](aes-gcm-review-checklist.md). Two items are near-certain findings in .NET 6-era code: the obsolete `new AesGcm(key)` constructor (SYSLIB0053 — permits silent tag truncation; switch to `new AesGcm(key, tagSizeInBytes)`), and unverified assumptions about session-key freshness vs nonce uniqueness.
- The test page is modified to call the library instead of its inline code. QA keeps using the page as before; if anything broke, they find it immediately.

### Phase 2 — Wrap the core in a headless HTTP API

Build the gateway host (endpoints defined in §3) around the Phase 1 library.

- Implement the proxy layer (`/proxy/...`, `/services`) and the primitive layer (`/crypto/...`).
- **Forwarding is hand-rolled `IHttpClientFactory`, not YARP** (decided 2026-07). YARP has no built-in body transforms — full-body encrypt/decrypt would need custom buffering middleware anyway — and its strengths (load balancing, health checks, high-throughput streaming) don't apply to a QA tool with ~8 one-to-one routes. A typed-client forwarder is simpler to reason about, test, and modify.
- Move per-service config from wherever the test page kept it into the gateway's configuration model (§5), with keys referenced from secret storage.
- Convert the existing test page UI into an **optional thin client** that calls the gateway API instead of doing crypto locally. QA keeps their familiar tool, and — because the UI and the automated consumers now go through the same code path — the two are guaranteed identical. "Works in the test page" now means "works via the API".

### Phase 3 — Agent enablement

- Publish OpenAPI (`/openapi.json`) with full schemas and error taxonomy documented.
- Implement the diagnostics contract (§3.3) so error responses are self-explanatory to an agent.
- Write example integration tests (one per service) as living documentation in the repo.
- Optional, later: a thin MCP server wrapper exposing `call_api` / `encrypt` / `decrypt` tools that delegate to the gateway (§7.3).

### Phase 4 — Value-add features (post-launch)

Explicitly deferred until Phases 0–3 have shipped: the core value is the crypto extraction and proxy, and the migration must not stall on feature growth. These four earn their place because the gateway uniquely sees both the plain payload and the encrypted exchange:

- **Capture & replay.** Persist every proxied call (plain request, encrypted form, response, correlation ID) and expose `POST /replay/{capture_id}`. Gives one-command bug reproduction, and lets any successful capture be promoted to a golden test vector — the regression suite grows from real traffic instead of hand-written cases. Retention and payload-sensitivity policy per §6 (no captures retained from endpoints flagged sensitive). **Storage (decided 2026-07): SQLite via EF Core with WAL mode** — embedded, zero ops, ample for a single-instance gateway; composite index on `(CorrelationId, TimestampUtc)`, retention cleanup by expiry column. Escalation path if sustained writes ever exceed ~1k/sec: swap the EF provider to Pomelo + the team's existing OceanBase — same DbContext, no redesign. LiteDB and DuckDB were evaluated and ruled out (maintenance uncertainty; OLAP mismatch).
- **Key health monitoring.** `GET /health/keys` checks every configured PGP key: resolvable from secret storage, not expired, and **expiring within N days** (configurable warning window). `GET /health/services` runs a scheduled contract smoke check per service. Together they catch key expiry and unannounced upstream key rotation before they burn a test day.
- **Fault injection.** An `X-Chaos` request header (`upstream-timeout`, `tamper-signature`, `wrong-key-version`, ...) makes the gateway deliberately misbehave so QA can test the *callers'* error handling — e.g. how the admin portal reacts when a response fails signature verification. Only honored when a server-side chaos switch is enabled; never in shared UAT without agreement.
- **Async callback catcher** *(conditional — only if Phase 0 confirms any of the 8 services send asynchronous callbacks/webhooks)*. The gateway exposes a callback URL, decrypts and verifies incoming callbacks, and stores them for tests to poll via `GET /callbacks?correlation_id=...`, covering the asynchronous half of flows the proxy alone cannot test. **Build, don't buy (decided 2026-07):** self-hostable catchers exist (webhook-tester, webhook.site OSS, Request Baskets), but they only store and content-search raw requests — with encrypted callback bodies the correlation ID lives inside the ciphertext, so their search is useless and a decrypt shim would be needed anyway. A one-endpoint catcher inside the gateway decrypts inline, indexes the correlation ID, and keeps decrypted payment data within the trusted boundary. (Revisit only if the callback spec puts the correlation ID in the URL or a plaintext header — then webhook-tester, MIT-licensed and actively maintained, becomes viable.)

Backlog beyond Phase 4 (unscheduled): environment diff (same payload to SIT and UAT, structural response diff), "copy as curl/C#/test case" snippet export in the test page UI, and a browsable call-history page over the audit log linked to OpenSearch by correlation ID. Deliberately out of scope: test-data generation, a built-in assertion/test-runner DSL (test frameworks do this better — the gateway stays dumb), and performance testing through the gateway (encryption overhead would distort numbers; load tests should hit services directly).

### Executing phases with engineered loops

Each phase is a good candidate for autonomous loop execution (per the Loop Engineering paradigm: design the loop before running it — context, structure, then execute), because each has a real, runnable verify command and a machine-checkable exit condition:

| Phase | Verify command | Loop exit condition |
|-------|----------------|---------------------|
| 1 | `dotnet test` (golden-vector suite) | all vectors pass; AES-GCM checklist findings resolved |
| 2 | `dotnet test` (WireMock integration suite) | proxy + primitive endpoints + failure-path matrix green |
| 3 | Schemathesis run + one headless agent E2E | fuzz clean; agent completes a documented test unaided |
| 4 | per-feature test suite | feature's acceptance row in the milestone table |

Workflow: at the start of each phase, run the loop design step (`/loop-architect`) against the test page repo to read the project, verify scope, and generate the four-component Loop Prompt (system_protocol / guardrails / autonomy_trigger / safety_net) — then execute via `/loop`. For Phase 1 the guardrails matter most (no edits outside the crypto extraction scope; on the same test failure twice, change approach rather than tweak) — crypto bugs invite endless small tweaks. Phase 0 (inventory) is deliberately *not* a loop: it is the context-gathering that makes the later loops well-designed.

### Milestones & acceptance

| Phase | Milestone | Acceptance criteria |
|-------|-----------|---------------------|
| 0 | Inventory complete | Written map of crypto code, configs, key locations; ≥1 round-trip fixture captured per service (8 total minimum) |
| 1 | Core library extracted | All golden vectors pass; test page runs on the library with no behavior change observed by QA over one normal week of use |
| 2 | Gateway live in test env | All 8 services callable via `/proxy` with plain JSON in SIT; test page UI running as thin client; primitive endpoints pass round-trip tests |
| 3 | Agent-ready | OpenAPI published; an AI agent, given only the gateway URL and an API key, completes a documented end-to-end test against one service without human intervention; example tests merged |
| 4 | Value-add features | Capture/replay in use for ≥1 real bug reproduction; key health checks alerting before expiry; fault injection used in ≥1 caller error-handling test; callback catcher live if applicable |

---

## 3. API Design

Two layers: a **proxy layer** for calling real APIs with plain JSON, and a **primitive layer** exposing the crypto operations directly for spec round-trip and negative testing.

### 3.1 Proxy layer

#### `GET /services`

Lists configured services, their endpoints, and available environments. This is the discovery entry point for agents.

```json
{
  "services": [
    {
      "name": "payments",
      "environments": ["dev", "sit", "uat"],
      "endpoints": [
        { "name": "create-order", "method": "POST", "path": "/api/v1/orders" },
        { "name": "query-order",  "method": "POST", "path": "/api/v1/orders/query" }
      ]
    },
    { "name": "customer-profile", "environments": ["sit", "uat"], "endpoints": [ "..." ] }
  ]
}
```

#### `POST /proxy/{service}/{endpoint}?env=sit`

Body is the **plain JSON** business payload. The gateway encrypts it per the crypto spec, signs it, forwards it to the configured upstream URL for `{service}` in `{env}`, decrypts and verifies the response, and returns plain JSON.

Request:

```
POST /proxy/payments/create-order?env=sit
X-Api-Key: <gateway api key>
Content-Type: application/json

{
  "orderId": "TEST-20260709-001",
  "amount": 1500.00,
  "currency": "THB"
}
```

Successful response:

```json
{
  "ok": true,
  "data": {
    "orderId": "TEST-20260709-001",
    "status": "CREATED",
    "reference": "PAY-88213"
  },
  "diagnostics": {
    "correlation_id": "gw-9f3a1c7e-0001",
    "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
    "stage": "upstream",
    "service": "payments",
    "endpoint": "create-order",
    "env": "sit",
    "upstream_url": "https://payments.sit.internal.example/api/v1/orders",
    "upstream_status": 200,
    "timing_ms": { "encrypt": 12, "upstream": 341, "decrypt": 9, "total": 365 },
    "headers_sent": { "Content-Type": "application/json", "X-Signature": "<redacted>", "X-Key-Id": "payments-sit-2026" }
  }
}
```

With `?debug=true` (gated; see §6), `diagnostics` additionally includes `raw_encrypted_request` and `raw_encrypted_response` (base64) so byte-level disputes with a service team can be settled from one response.

Error response — the envelope is identical in shape whether the failure was in the gateway or upstream, and `error.stage` + the code prefix say which:

```json
{
  "ok": false,
  "error": {
    "code": "UP_DECRYPT_FAILED",
    "stage": "upstream",
    "message": "Upstream returned HTTP 200 but the response payload failed AES decryption with key 'payments-sit-2026'.",
    "hint": "The upstream may be encrypting with a different key version. Check key rotation on the payments SIT environment, or retry with debug=true and compare raw_encrypted_response against a known-good fixture.",
    "retryable": false
  },
  "diagnostics": {
    "correlation_id": "gw-9f3a1c7e-0002",
    "stage": "upstream",
    "upstream_status": 200,
    "timing_ms": { "encrypt": 11, "upstream": 402, "total": 460 },
    "headers_sent": { "Content-Type": "application/json", "X-Key-Id": "payments-sit-2026" }
  }
}
```

### 3.2 Primitive layer

Direct access to the crypto operations, for spec round-trip tests and negative/tamper tests. These never call upstream.

- `POST /crypto/encrypt` — `{ "service": "payments", "env": "sit", "payload": { ... } }` → `{ "ciphertext": "<base64>", "wrapped_key": "<base64>", "iv": "<base64>", "key_id": "payments-sit-2026" }` (exact envelope fields follow the internal spec).
- `POST /crypto/decrypt` — the inverse: takes the encrypted envelope, returns the plain JSON payload, or a `*_DECRYPT_FAILED` error.
- `POST /crypto/sign` — `{ "service": "payments", "env": "sit", "payload_b64": "<base64>" }` → `{ "signature": "<base64>", "signing_identity": "qa-gateway-sit" }`.
- `POST /crypto/verify` — takes payload + signature (+ optional signer identity), returns `{ "valid": true }` or `{ "valid": false, "reason": "..." }`.

Typical uses: prove a round trip (`encrypt` → `decrypt` returns the original), and tamper tests (flip a byte in the ciphertext, expect `decrypt` to fail with a clean error rather than garbage).

### 3.3 Diagnostics contract & error taxonomy

Every response carries a `diagnostics` object with at minimum: `correlation_id`, `stage` (`"gateway"` or `"upstream"`), timings, `upstream_status` (when upstream was reached), and `headers_sent`.

**Correlation ID.** The gateway generates a unique `correlation_id` per request, sends it upstream as `X-Correlation-Id`, and returns it in `diagnostics` on every response (success or error). Provided the upstream services log this header (standard ASP.NET logging middleware does), a consumer holding an `UP_*` error can look up the exact upstream log entries for that request in centralized logging (OpenSearch) — for an AI agent with an OpenSearch MCP connection, this closes the loop: call → failure → query logs by correlation ID → diagnose. Adoption note: verify during Phase 0 whether the 8 services already propagate/log a correlation header and under what field name; if they use a different header (e.g. `X-Request-Id`), the gateway sends that instead — the config model allows a per-service header name override.

**W3C Trace Context (free, use it too).** Because the whole estate is .NET, `HttpClient` propagates the W3C `traceparent` header automatically (default since .NET Core 3.1; .NET 10 defaults to the W3C propagator), and the upstream services very likely already log `TraceId`. The gateway therefore returns `trace_id` in `diagnostics` alongside `correlation_id`: `correlation_id` is the human-readable business join key the gateway controls; `trace_id` is the technical distributed-tracing key the platform provides for free. Agents can query OpenSearch by either field. Phase 0 should confirm which of the two the 8 services actually index today — if `TraceId` is already searchable in OpenSearch, the log-lookup loop works before any service-side change ships. Every error carries a `code`, a human/agent-readable `message`, and a `hint` suggesting the next diagnostic step. The design rule: **an AI agent reading only the error response should be able to tell whether to fix its own request, report a gateway config problem, or file a bug against the upstream API.**

Codes are prefixed by where the fault lies:

| Code | Stage | Meaning |
|------|-------|---------|
| `GW_UNKNOWN_SERVICE` | gateway | `{service}` or `{endpoint}` not in configuration; caller should check `/services` |
| `GW_ENV_NOT_ALLOWED` | gateway | Requested environment not configured (or is production — hard refusal, see §6) |
| `GW_CONFIG_MISSING_KEY` | gateway | Service is configured but its key reference could not be resolved from secret storage |
| `GW_INVALID_REQUEST` | gateway | Request body is not valid JSON / fails the endpoint's basic shape checks |
| `GW_ENCRYPT_FAILED` | gateway | Encryption or key-wrapping threw; gateway-side crypto bug or bad key material |
| `GW_SIGN_FAILED` | gateway | Signing failed (bad signing identity, unusable private key) |
| `GW_AUTH_FAILED` | gateway | Missing/invalid gateway API key |
| `UP_UNREACHABLE` | upstream | Connection refused / DNS failure to the configured upstream host |
| `UP_TIMEOUT` | upstream | Upstream did not respond within the configured timeout |
| `UP_HTTP_4XX` | upstream | Upstream rejected the request (status + any decryptable error body included in diagnostics) |
| `UP_HTTP_5XX` | upstream | Upstream server error |
| `UP_DECRYPT_FAILED` | upstream | Upstream responded but its payload failed decryption — likely key mismatch or upstream not following the spec |
| `UP_VERIFY_FAILED` | upstream | Upstream response decrypted but its signature did not verify |

`GW_*` means: the real API was never validly reached, or was reached with a payload we can't vouch for — fix the gateway/config/request. `UP_*` means: our crypto worked, the payload was well-formed per the audited spec, and the problem is on the service side. This is the direct answer to the "is the test wrong or the API wrong?" ambiguity.

---

## 4. Configuration Model

Configuration is per service, per environment, defined server-side. Callers can never supply URLs or key material — they select by name only.

Each service entry defines:

- `name` — the identifier used in `/proxy/{service}/...`.
- `environments` — allowed upstream base URLs, keyed by environment. **Only dev/sit/uat may appear.** A production URL in config is a startup error, not a warning.
- `keys` — references (not values) to key material: PGP/RSA keypair refs for key wrapping and verification, AES parameters (mode, key size, IV handling) per the internal spec.
- `signing` — the signing identity (private key ref) used for outbound requests, and the upstream's public key ref for response verification.
- `endpoints` — named upstream paths exposed via `/proxy`.
- `timeout_ms` — upstream timeout.

Key material is resolved at runtime from secret storage or environment variables. **No real key, passphrase, or secret is ever committed to the repository or accepted in a request body.**

**Secret-storage guidance (verified 2026-07).** Armored PGP private keys are multiline ASCII (~2–4 KB) and **environment variables mangle the newlines** — avoid bare env-var injection for key blocks (base64-wrapping works but is fragile). Pragmatic ladder for a test-only internal gateway: (1) *minimum:* Kubernetes/Docker secrets **mounted as files** — multiline-safe, zero new infrastructure (`File.ReadAllText("/secrets/payments-priv.asc")`); (2) *better:* Azure Key Vault or AWS Secrets Manager — versioning + audit logs, both return multiline strings verbatim, size limits (25/64 KB) are non-issues; (3) HashiCorp Vault only if the org already runs it — note the official .NET client is still experimental, use community VaultSharp. ASP.NET `user-secrets` is acceptable for local development only (unencrypted, dev-gated). Example shape (placeholder values only):

```yaml
gateway:
  auth:
    api_keys_ref: "env:GATEWAY_API_KEYS"        # comma-separated hashed keys
  debug_flag_allowed: true                       # master switch for ?debug=true

services:
  payments:
    environments:
      dev: "https://payments.dev.internal.example"
      sit: "https://payments.sit.internal.example"
      uat: "https://payments.uat.internal.example"
    keys:
      pgp_public_key_ref:  "vault:qa/payments/sit/upstream-pub"   # encrypts the AES session key
      pgp_private_key_ref: "vault:qa/payments/sit/gateway-priv"   # decrypts responses
      aes:
        mode: "GCM"          # per internal spec
        key_bits: 256
    signing:
      identity: "qa-gateway-sit"
      private_key_ref: "vault:qa/signing/qa-gateway-sit"
      upstream_verify_key_ref: "vault:qa/payments/sit/upstream-signing-pub"
    endpoints:
      create-order: { method: POST, path: "/api/v1/orders" }
      query-order:  { method: POST, path: "/api/v1/orders/query" }
    timeout_ms: 15000

  customer-profile:
    # ... same shape; repeat for all 8 services
```

Open item: whether all 8 services share identical AES/PGP parameters or vary per service (see §9); the config shape above assumes per-service parameters so either answer fits.

---

## 5. Security — the decryption-oracle risk

The gateway is, by design, a machine that produces **valid encrypted payloads for real APIs** and **decrypts their responses**. Anyone who can call it effectively holds the keys, functionally if not literally. It must be treated as sensitive infrastructure, not as a test utility. Controls:

1. **Server-side host allowlist.** Upstream URLs come exclusively from server config. There is no parameter anywhere in the API through which a caller can supply, override, or redirect a URL. This eliminates SSRF-style use of the gateway as a general encryption oracle against arbitrary targets.
2. **Hard refusal of production.** Only dev/sit/uat environments are configurable. As defense in depth, the gateway also maintains a deny-pattern for known production hostnames/domains and refuses to start if any configured URL matches, and refuses at request time if resolution ever lands there.
3. **API-key authentication** on every endpoint (including `/services` and `/openapi.json` if the deployment demands it). Keys are issued per consumer (CI, named agents, individual QA) so the audit log is attributable. Implementation (verified 2026-07): .NET has no built-in API-key scheme — use a custom `AuthenticationHandler` (not bare middleware, so it composes with the authorization pipeline); store keys as SHA-256 hashes and compare with `CryptographicOperations.FixedTimeEquals`; give keys an identifying prefix (e.g. `qagw_`) so leaked keys are recognizable in logs without exposing the secret.
3a. **Rate limiting per consumer** — because the gateway is a crypto oracle, cap request rates using the built-in `Microsoft.AspNetCore.RateLimiting` middleware, partitioned per API key (token bucket suits bursty test runs). Order matters: **authenticate the key before using it as a partition key** — partitioning on unauthenticated caller-supplied values lets an attacker explode partitions into a memory DoS. In-memory limiter state is fine for a single-instance deployment.
4. **Network restriction.** Deployed on the internal network/VPN only; never internet-exposed. Egress limited to the configured upstream hosts where the platform supports it.
5. **No secrets in logs.** Default logging records metadata only: caller, service, endpoint, env, status, error code, timings. Never keys, never decrypted request/response bodies, never raw ciphertext by default.
6. **Debug flag gated.** `?debug=true` (which returns raw encrypted payloads) works only when enabled in server config, intended for dev/SIT troubleshooting; consider restricting it to specific API keys.
7. **Audit log.** Every call is recorded (who, what service/endpoint/env, when, outcome). Retained per internal audit policy; reviewable when a key rotation or incident demands it.

---

## 6. Agent & Integration-Test Consumption

### 6.1 How an agent uses the gateway

1. `GET /openapi.json` — full machine-readable contract, including the error taxonomy.
2. `GET /services` — discover configured services, endpoints, environments.
3. `POST /proxy/{service}/{endpoint}?env=sit` with plain JSON — call the real API.
4. On error, read `error.stage`, `error.code`, and `error.hint` to decide: fix the request (`GW_INVALID_REQUEST`), report gateway config (`GW_CONFIG_MISSING_KEY`), or investigate/report the upstream (`UP_*`).
5. For `UP_*` failures, if the agent has an OpenSearch MCP connection to centralized logging (e.g. the official `opensearch-project/opensearch-mcp-server-py`, or the built-in experimental MCP endpoint in OpenSearch 3.0+), it queries the upstream service's logs by the `correlation_id` or `trace_id` from `diagnostics` — giving the agent an autonomous call → fail → read-logs → diagnose → retry loop. Note the MCP server has no dedicated "search by correlation ID" tool; the agent constructs the index query itself via `SearchIndexTool`/DSL, which Claude handles fine given the field name — document the log index names and field names in the gateway's README so agents don't have to guess.

The agent never sees a key, never implements crypto, and never needs the internal spec document.

### 6.2 Worked example — positive integration test

Pseudocode; any test framework and language works because it's plain HTTP + JSON.

```
# Arrange: plain JSON, no crypto anywhere in the test
payload = { "orderId": "IT-{run_id}-01", "amount": 100.00, "currency": "THB" }

# Act: call the real payments API through the gateway
resp = POST {gateway}/proxy/payments/create-order?env=sit
       headers: { X-Api-Key: $GATEWAY_KEY }
       body: payload

# Assert: on the decrypted, plain-JSON response
assert resp.ok == true
assert resp.data.status == "CREATED"
assert resp.data.orderId == payload.orderId
assert resp.diagnostics.upstream_status == 200
```

### 6.3 Worked example — negative/tamper test via primitives

```
# Round-trip baseline
enc = POST {gateway}/crypto/encrypt  body: { service: "payments", env: "sit", payload: {...} }

# Tamper: flip one byte of the ciphertext
enc.ciphertext = flip_byte(enc.ciphertext, at: 10)

# Decryption must fail cleanly, not return garbage
dec = POST {gateway}/crypto/decrypt  body: enc
assert dec.ok == false
assert dec.error.code in ["GW_DECRYPT_FAILED", "UP_DECRYPT_FAILED"]   # per taxonomy for primitive-layer decrypt

# Similarly: verify must reject a signature over altered bytes
ver = POST {gateway}/crypto/verify  body: { payload_b64: tampered, signature: original_sig }
assert ver.valid == false
```

### 6.4 Optional future: MCP wrapper

Once the HTTP API is stable, a thin MCP server can expose `call_api(service, endpoint, env, payload)`, `encrypt(...)`, `decrypt(...)` tools that simply delegate to the gateway. This gives Claude Code/desktop agents first-class tool access without any new logic — the gateway remains the single implementation. Deliberately deferred to after Phase 3.

Effort check (verified 2026-07): the official MCP C# SDK (`ModelContextProtocol` / `ModelContextProtocol.AspNetCore` NuGet) is GA at v1.4.x with first-class ASP.NET Core hosting — attribute-based tool registration (`[McpServerToolType]`/`[McpServerTool]`) means a minimal tool server is ~30 lines, hostable inside the gateway process itself. Realistic estimate: 2–4 days including auth and testing. Stay on the stable 1.4.x line; a v2.0 protocol revision is in preview.

### 6.5 Running agents headless in CI

Recommended setup for unattended Claude-driven test runs against the gateway (verified 2026-07):

- **Invocation:** `claude -p "<task>" --output-format json` — non-interactive, one task in, structured result out. The JSON result includes `total_cost_usd`, so per-run cost lands in the CI log for free.
- **Permissions:** run inside a Docker container (not directly on the runner); `--permission-mode dontAsk` with an explicit `--allowedTools` allow-list scoped to what the task needs — e.g. `Bash(dotnet test *)`, `Read`, the gateway's HTTP calls, and the OpenSearch MCP tools. Never allow `git push` or destructive shell commands; agent-produced changes flow through normal MRs with branch protection.
- **Cost caps:** `--max-turns N` (stops runaway loops) and `--max-budget-usd X` (financial circuit breaker) on every CI invocation.
- **Pipelines:** GitHub has the official `anthropics/claude-code-action`; GitLab has a beta CI/CD integration; Jenkins is community-MCP only. The "agent runs integration tests, diagnoses via logs, files defects with diagnostic context" workflow this spec targets is an established 2026 pattern, not an experiment.
- **Prompt structure:** author the CI agent's task prompt as a four-component Loop Prompt (Loop Engineering paradigm): *system_protocol* — read `/services`, run the test plan, on `UP_*` errors query OpenSearch by the `correlation_id` from diagnostics; *guardrails* — test environments only, no scope beyond the listed tests, allowed-tools list is the ceiling; *autonomy_trigger* — diagnose → fix → re-run per failure, and on the same failure twice, change approach instead of retrying; *safety_net* — file a defect with diagnostics and stop rather than hammer a failing upstream, and surface anything unexpected in the completion summary. `--max-turns` is the loop's iteration cap.

---

## 7. Testing & Verification of the Gateway Itself

The gateway is now the trust anchor, so it needs its own rigorous suite:

- **Golden-vector regression suite** (from Phase 1): every fixture captured from the original test page must round-trip through the extracted library and the HTTP primitive endpoints. Runs on every commit; this is the guarantee that "the gateway's crypto == the crypto everyone already trusted". The suite is deliberately **bimodal**: decrypt tests are fixed-output known-answer tests (fixed ciphertext → expected plaintext), while encrypt tests are round-trips — byte-exact encrypt KATs are impossible because PGP hybrid encryption randomizes the session key and IV per message. Supplement self-captured vectors with the published test vectors in **RFC 9580 Appendix A** (AEAD sequences, v6 certificates, Argon2+AES) as standards-conformance decrypt KATs, and run a **one-off GnuPG cross-check** (encrypt with the library → decrypt with GnuPG, and vice versa) as an external sanity anchor. The Sequoia OpenPGP interoperability suite was evaluated and skipped (2026-07): it requires a SOP CLI wrapper that doesn't exist for .NET, and its value is interop with diverse external tools — not our closed loop of 8 known counterparts. Revisit only if an external partner's OpenPGP implementation joins the estate.
- **Contract tests per service against SIT**: one smoke test per service/endpoint, run on a schedule and before releases of the gateway, proving each configured upstream still accepts gateway-produced payloads. Failures here with `UP_*` codes flag upstream drift (e.g., unannounced key rotation) early.
- **Round-trip property tests**: for randomly generated payloads (varied sizes, unicode, nesting, empty bodies), `decrypt(encrypt(p)) == p` and `verify(p, sign(p)) == true`.
- **Upstream stubbing with WireMock.NET** so the gateway's own suite runs in CI without network access to SIT: run WireMock in-process alongside `WebApplicationFactory` (point the gateway's configured upstream URLs at the stub server). Its fault simulation (`Fault` enum: connection reset, malformed chunks, empty response; fixed/random delays; probabilistic faults) covers the failure-path matrix below without network flakiness, and its request recording verifies exactly what the gateway sent upstream. Stub responses that must be validly encrypted are pre-generated in test setup using the Phase 1 core library and golden-vector keys — reusing the trust anchor rather than inventing test crypto. Caveat: WireMock.NET's .NET 10 support is computed, not explicitly certified — verify in CI during Phase 2 setup.
- **Failure-path tests** (per §Error Handling baseline — no silent failures): wrong key configured → `GW_CONFIG_MISSING_KEY` / `GW_ENCRYPT_FAILED`; expired/rotated key → clean error, not garbage output; tampered payload → `*_DECRYPT_FAILED` / `verify=false`; upstream down → `UP_UNREACHABLE`; slow upstream → `UP_TIMEOUT` at the configured limit. Each asserts the exact error code and that `stage` is attributed correctly.
- **Property-based fuzzing with Schemathesis**: point `schemathesis run` at the gateway's `/openapi/v1.json` in CI. It generates schema-violating inputs by default (wrong types, missing fields, invalid enums) and asserts the gateway's core error-contract promise: structured errors always, never a bare 500 or crash (`not_a_server_error` + `response_schema_conformance` checks). Prerequisite: every endpoint must document its error response schemas (`.Produces<...>(400)` etc.) in the OpenAPI output, or the schema-conformance check has nothing to validate against. Chosen over alternatives (2026-07): RESTler still lacks OpenAPI 3.1 support; Dredd is archived; StepCI/Hurl are not fuzzers.
- **Security tests**: production-host refusal at startup and request time; requests without API keys rejected; `debug=true` refused when the master switch is off; logs verified to contain no payloads or key material.

---

## 8. In-House Assets to Reuse

Existing agents, skills, and research in this repo (`my-superpowers`) that plug directly into this plan — don't rebuild these:

| Asset | Where it plugs in |
|-------|-------------------|
| `docs/research/mcp/...opensearch-mcp-claude-code-cli-without-uv-uvx.md` (+ Kiro variant) | §6.5 — the exact `claude mcp add opensearch` setup, pipx/venv install, env-var auth for the CI agent's log-debugging loop |
| `docs/research/mcp/...jira-confluence-mcp-*.md` | §6.5 — the defect-filing leg: agent creates Jira tickets with diagnostics after triage |
| `docs/research/mcp/...oceanbase-mcp-*.md` | New capability: after a proxied call, the agent asserts on **database state** via the OceanBase MCP (e.g. the order row actually exists) — end-to-end verification beyond the API response |
| `principal-dotnet-engineer` agent | Implements Phases 1–2; its stack (minimal APIs, xUnit, Testcontainers, Pomelo, Serilog) matches this spec's choices |
| `qa-dotnet-engineer` agent + QA skills (`analyzing-requirements-for-qa`, `generating-automation-scripts`, `generating-bdd-scenarios`, `generating-performance-tests`, `reporting-test-results`) | Generates the integration tests that consume the gateway (Phase 3); `reporting-test-results` is the CI loop's defect-report step |
| `loop-architect` + `loop` skills | Phase execution discipline (see "Executing phases with engineered loops") |
| `docs/research/dotnet/2026-06-22-ef-core-no-repository.md` | Phase 4 capture store: use `DbContext` directly, no repository layer |

Standing constraint from team practice: all .NET code produced by agents — including this gateway — must pass the SonarQube quality gate; verify, don't assume.

## 9. Open Questions

| # | Question | Why it matters |
|---|----------|----------------|
| 1 | ~~What is the actual stack of the test page?~~ **Resolved: .NET 10 Blazor Web App.** Which interactive render modes does it use — Server, WebAssembly, or Auto? | If any component doing crypto runs in a WebAssembly render mode, the crypto and possibly key material execute client-side in the browser — that is itself a security finding, and it changes the Phase 0/1 extraction target (the code to extract is whatever the WASM client holds, and keys must move server-side as part of Phase 2). If everything is Interactive Server, crypto already runs server-side and extraction is straightforward |
| 2 | Where does key material currently live (files on the host, web.config, a vault)? | Drives the secret-storage integration in §4 and how much key-handling remediation Phase 2 includes |
| 3 | Do all 8 services share one crypto spec, or do parameters (AES mode, envelope format, signing scheme) vary per service? | Config model supports either, but the core library's surface and the golden-vector count depend on it |
| 4 | What auth do the upstream APIs require beyond payload encryption (mTLS, tokens, IP allowlists)? | Must be added to per-service config and diagnostics if present |
| 5 | Does the CI environment have network access to SIT? | Determines whether contract tests run in CI or only from an internal runner |
| 6 | Do any of the 8 services send asynchronous callbacks/webhooks? | Determines whether the Phase 4 callback catcher is in scope; without it, integration tests only cover the synchronous half of those flows |

---

## 10. Appendix: .NET 10 Blazor Web App Migration Notes

The test page is confirmed as a **.NET 10 Blazor Web App**. .NET 10 is a current LTS release, so no framework upgrade is needed — the extracted library, the new gateway host, and the existing UI can all target `net10.0`, and the gateway host can live as a new project in the same solution.

- **Inventory (Phase 0):** in a Blazor Web App, crypto logic typically lives in component `@code` blocks, `.razor.cs` code-behind partial classes, or services registered in `Program.cs` DI. Map which of these hold the encrypt/decrypt/sign/verify code. Also check the render mode of the pages doing crypto (`@rendermode InteractiveServer` / `InteractiveWebAssembly` / `InteractiveAuto`, or the app-wide default in `App.razor`): WASM-rendered components execute in the browser, which affects where the code and keys actually run today (see Open Question 1). Finally, grep for `IJSRuntime` interop calls — any browser-side crypto (openpgp.js, WebCrypto) must be ported to server-side C# in Phase 1.
- **Extraction (Phase 1):** move crypto code into a plain class library (`Company.Qa.CryptoCore`) targeting `net10.0`, with no Blazor/ASP.NET dependencies (no `Microsoft.AspNetCore.Components.*` references). The Blazor app references the library and its pages call it via their existing injected services.
- **Host (Phase 2):** ASP.NET Core minimal API on `net10.0` — one file of route mappings over the core library is sufficient. Record DTOs for request/response envelopes. The Blazor pages' submit handlers then become `HttpClient` calls to the new API (registered via `IHttpClientFactory`), completing the thin-client conversion.
- **Config:** `IOptions<ServiceConfig>` bound from `appsettings.{env}.json` + environment variables/secret store for key refs; validate on startup (`ValidateOnStart`) so a bad config — including any production URL — fails deployment, not the first request.
- **PGP:** match whichever library the test page already uses to keep golden vectors byte-compatible. Current state (verified 2026-07): PgpCore 7.x targets `net10.0` and wraps `BouncyCastle.Cryptography` ≥ 2.4.0 — a floor above all three 2024 BouncyCastle .NET CVEs (Ed25519 DoS, EC F2m CPU exhaustion, RSA timing side-channel), so both options are clean. **Interop caveat:** PgpCore's `DecryptAndVerify()` only handles messages produced by its own `EncryptAndSign()`; since our upstream services are independent implementations of the spec, use separate `Decrypt()` + `Verify()` calls (or BouncyCastle directly) rather than the combined convenience method.
- **AES:** built-in `System.Security.Cryptography` (`AesGcm` for GCM mode); no third-party dependency needed.
- **OpenAPI:** the built-in `Microsoft.AspNetCore.OpenApi` in .NET 10 publishes OpenAPI 3.1 at `/openapi/v1.json` natively, including XML doc comments pulled in at compile time (set `GenerateDocumentationFile=true`) — so writing good `<summary>`/`<response>` comments on the gateway endpoints directly improves what agents see. Add Scalar (`Scalar.AspNetCore`) as the human-facing docs UI — it is Microsoft's current recommendation over Swagger UI for new projects.
- **Observability:** enrich Serilog with both the custom correlation ID (via `LogContext` middleware) and the automatic trace/span IDs (`Serilog.Enrichers.Span`), so gateway logs in OpenSearch join with upstream logs on either key.
- **Tests:** xUnit; golden vectors as embedded resources with a data-driven `[MemberData]` theory per service; `WebApplicationFactory` for in-process API tests of the proxy and primitive layers.
