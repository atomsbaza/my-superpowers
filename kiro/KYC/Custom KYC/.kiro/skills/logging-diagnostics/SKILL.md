---
name: logging-diagnostics
description: "Add structured logging to HTTP clients and handlers for better observability. Use when a service call lacks sufficient logging, after a debugging session reveals log gaps, or when adding a new downstream client. Pairs with: log-investigator, incident-debugger subagents."
---

# Logging Diagnostics

Ensure downstream HTTP calls log enough information to diagnose failures without code access.

## When to Use

- After debugging reveals "we can't tell what went wrong from logs"
- When adding a new HTTP client to another service
- When a handler swallows errors with generic responses
- When correlation IDs aren't flowing through

## What Good Logging Looks Like

### HTTP Client (outbound calls)

```csharp
// Before the call
_logger.LogInformation("Calling {Url} with {CorrelationId}", url, correlationId);

// After the call — branch on success/failure
if (!response.IsSuccessStatusCode)
    _logger.LogWarning("{Service} {Method} failed with {StatusCode}. Response: {ResponseBody}",
        serviceName, methodName, (int)response.StatusCode, responseBody);
else
    _logger.LogInformation("{Service} {Method} responded with {StatusCode}",
        serviceName, methodName, (int)response.StatusCode);
```

### Handler (response mapping)

```csharp
// When falling through to a generic error response
_logger.LogError("Upstream {Service} returned unexpected {StatusCode}. Response: {ResponseBody}",
    serviceName, (int)statusCode, responseBody);
```

## Rules

- **Non-success = Warning or Error**, never Information. Information-level failures get lost in noise.
- **Always log response body** for non-2xx responses. Without it, you're blind.
- **Log the numeric status code** `(int)statusCode`, not the enum name. Numeric is searchable in OpenSearch.
- **Correlation ID must flow** — pass via `X-Correlation-Id` header to downstream, log it on both sides.
- **Never log raw PII** in response bodies. If the response might contain PII, log only the error/code fields.
- **Log the full URL** being called (not just the relative path) — config mistakes (wrong base URL) are common.
- **Catch blocks must log the exception** — `_logger.LogError(ex, "...")` not just the message.

## Checklist When Reviewing a Client

- [ ] Logs the outbound URL before calling
- [ ] Logs CorrelationId sent to downstream
- [ ] Logs status code for ALL responses (not just success)
- [ ] Logs response body for non-success
- [ ] Handler logs unexpected status codes at Error level with response body
- [ ] Exception catch blocks include the exception object
- [ ] No raw PII in log messages


## Verify OpenSearch Sink is Configured

When a service has logs in Argo/kubectl but NOT in OpenSearch, check:

1. **Serilog WriteTo config** — must have OpenSearch/Elasticsearch sink:
   ```json
   "Serilog": {
     "WriteTo": [{
       "Name": "OpenSearch",
       "Args": { "nodeUris": "https://opensearch-endpoint:443" }
     }]
   }
   ```

2. **Index naming** — must follow `kyc-{service-name}-{yyyy.MM}` pattern

3. **Secrets Manager override** — `Serilog:WriteTo:0:Args:nodeUris` in secrets can override appsettings. If set to empty/invalid, logs won't reach OpenSearch.

4. **Network** — pod must have network access to OpenSearch endpoint (check security groups / VPC)

### Services known to lack OpenSearch index
- `kyc-cdd-business-worker` — verify if Serilog OpenSearch sink is configured in its `Program.cs` or `appsettings.json`
