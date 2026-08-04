# Control & Safety Patterns

These three patterns are the non-negotiable layer the moment an agent can take a consequential action: pause for a human when the stakes require it (Human-in-the-Loop), never trust the model to police itself (Guardrail), and assume things will fail transiently and plan for it (Retry and Recovery).

## 1. Human-in-the-Loop (HITL)

**Definition.** Some actions require human approval before execution — a large expense, a trade, an irreversible write. The agent pauses, persists its state, and waits for a human to approve or reject via a dashboard or approval event before resuming.

**When to use it.** Any action whose cost of being wrong exceeds the cost of a short delay for approval: financial transactions above a threshold, irreversible deletions, anything with legal or safety consequences. Never allow autonomous execution of critical business operations without this gate.

```csharp
if (!approvalService.IsApproved(request))
{
    return "Waiting for manager approval.";
}
await paymentService.ProcessAsync(request);
```

**Production note.** HITL only works if the pause is *durable* — the agent's state must survive the wait (which could be minutes or days), not just live in an in-memory conversation. This is one of the concrete reasons persistent, checkpointed state (see [Chapter 3](chapter03-memory-pattern.md) and [Chapter 10](chapter10-anti-patterns-failure-modes.md)) is a production requirement, not a nice-to-have.

## 2. Guardrail Pattern

**Definition.** A runtime policy-enforcement layer that operates as **deterministic software checks outside the model's own reasoning loop** — not prompt instructions, not a "constitution" baked into the system prompt. This distinction matters: because an LLM processes instructions and untrusted data in the same token attention space, prompt-only safety is fundamentally bypassable via jailbreaks and semantic manipulation. A guardrail that itself runs as another LLM call inside the same trust boundary is not a guardrail in this sense.

**The three-stage control plane.** Production architectures apply guardrails at three points:

```
User Prompt → [ INPUT GUARDS ] → Orchestration/Tools → LLM Invocation → [ OUTPUT GUARDS ] → Response
```

* **Input guardrails** — inspect and sanitize raw input before it reaches the model (prompt injection detection, PII masking).
* **Orchestration/tool guardrails** — verify credentials and inspect proposed tool parameters before execution (authorization checks).
* **Output guardrails** — sanitize the model's completion before it reaches the user or a downstream system (content safety, schema validation, groundedness checks).

### Prompt Injection: Direct and Indirect

**Direct injection (jailbreaking)** — a user directly instructs the agent to ignore its guidelines ("ignore all previous instructions…"). Input guardrails intercept this inline, typically using a fast classifier model to detect adversarial patterns before the main model ever sees the request.

**Indirect injection** — the more dangerous class in deployed systems. Malicious instructions are embedded in *external data* the agent retrieves or processes (a web page, an email, a PDF, a database record) during RAG or tool execution. When the agent ingests that data, the embedded instructions can hijack its attention and coerce destructive tool calls — data exfiltration, unauthorized writes — without the user ever typing anything malicious. Mitigations: tag all retrieved/tool-observed content as explicitly *untrusted data* so the model doesn't interpret it as instructions; separate untrusted-data-processing agents from high-privilege execution agents at design time (a trust-boundary decomposition, not just a prompt caveat); and gate raw system-level actions (shell commands, raw SQL, direct writes) behind pre-tool validation hooks rather than letting the model invoke them freely.

### PII Detection, Content Safety, and Output Validation

* **PII masking** at the input gateway — configurable, reversible for authorized recovery, and toggleable per workflow — prevents sensitive data (SSNs, card numbers, health records) from reaching model-provider logs, which matters for GDPR/HIPAA/PCI-DSS compliance.
* **Content safety filtering** on both input and output blocks toxic, harmful, or off-policy content and deflects gracefully with a fallback response on violation.
* **Output validation** converts probabilistic generation into a deterministic contract: force the model to populate a strict schema (Pydantic models are the common Python implementation), parse and type-check the result, and trigger a retry or a HITL exception on mismatch rather than passing malformed data downstream.

### Authorization and Least Privilege

An agent must never run under ambient, unconstrained credentials. Treat every agent as a distinct non-human identity with its own credentials so every downstream call is attributed and auditable. Implement per-call validation callbacks (e.g. a `before_tool_callback`) that check proposed parameters against the authenticated caller's context before execution — for example, rejecting a tool call whose `user_id` parameter doesn't match the authenticated session's user.

### Reported Platform Capabilities

| Platform | Enforcement stage | Capabilities | Reported figures (vendor-reported, treat as such) |
|---|---|---|---|
| AWS Bedrock Guardrails | Pre- and post-processing | Content moderation, PII redaction, topic denial, RAG grounding checks | Blocks up to 88% of harmful content; up to 99% accuracy on automated hallucination/groundedness checks |
| Google Model Armor | Inline security proxy (Agent Gateway) | Real-time traffic sanitation against injection, PII leakage, tool poisoning | Integrated into the ADK Agent Runtime and mTLS-secured Agent Gateway |
| Azure Content Safety / Prompt Shields | Input/output gateway | Injection protection, toxicity filtering, RAG groundedness | Reported ~11 microsecond overhead at 5,000 RPS on loopback (via a third-party gateway benchmark) |

### MCP-Specific Security Concerns

The Model Context Protocol standardizes how agents discover and call external tools — which introduces two vulnerability classes generic prompt-injection guardrails don't cover:

* **Tool poisoning.** Tool selection in MCP relies on natural-language tool descriptions and schemas exposed by the server. If an attacker compromises an MCP server or manipulates a tool's metadata (renaming parameters, altering descriptions to bias the model's tool choice), the client LLM can be tricked into chaining inappropriate tools or exfiltrating data — without tripping traditional structural validation. Mitigation: cryptographically signed tool definitions, immutable versioning on server capabilities, and fine-grained capability negotiation scoped to explicitly granted permissions.
* **Confused deputy.** Arises when an MCP proxy/gateway manages third-party OAuth on behalf of multiple users using a single shared client ID without per-user validation. Stale consent cookies or session hijacking can let an attacker abuse the proxy's broad backend credentials to act as another user. Mitigation: explicit audience validation on incoming tokens (reject tokens not issued for this specific service) and scoped, short-lived, user-bound access tokens rather than a shared static credential.

## 3. Retry and Recovery Pattern

**Definition.** LLM calls fail — rate limits, transient latency, model outages. Production systems must recover automatically rather than surfacing every transient failure to the user: retry, fall back to an alternative model/region, serve a cached response, or escalate to human review, in that order of preference.

```csharp
try
{
    return await openAi.InvokeAsync(prompt);
}
catch
{
    return await azureOpenAi.InvokeAsync(prompt);
}
```

**Production tradeoff.** A single-model, no-fallback design is itself an anti-pattern (see [Chapter 10](chapter10-anti-patterns-failure-modes.md)) — it converts a transient provider issue into a hard outage. But retries are not free: naïve retries that dump the raw error into conversation history pollute the context for subsequent steps (a specific instance of the context-rot failure mode from [Chapter 3](chapter03-memory-pattern.md)), and unbounded retry loops on a persistently failing call burn cost without ever succeeding. Bound every autonomous retry/recovery loop with an explicit step budget and escalate to Human-in-the-Loop on exhaustion rather than looping indefinitely.
