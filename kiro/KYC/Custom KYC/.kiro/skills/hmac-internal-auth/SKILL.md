---
name: hmac-internal-auth
description: HMAC internal service-to-service authentication pattern. Use when adding a new HTTP client that calls another KYC service internally, or when setting up auth headers for cross-service communication. Pairs with: cross-project subagent.
---

# HMAC Internal Authentication

## Overview
All KYC service-to-service calls use HMAC authentication with these headers:
- `X-Refer` — Caller identifier (e.g., company ID or service name)
- `X-Client` — Application name constant
- `X-Request-Time` — ISO 8601 timestamp (`DateTime.Now.ToString("O")`)
- `X-Correlation-Id` — GUID for distributed tracing
- `Authorization` — HMAC signature generated from `Authentication.Key`

## HTTP Client Pattern

```csharp
private HttpRequestMessage GenerateHttpRequestMessage(HttpMethod method, string url, object request = null)
{
    var message = new HttpRequestMessage(method, url);

    var refer = _clientContext.Client.Id.ToString();
    var client = Constants.ApplicationName;
    var requestTime = DateTime.Now.ToString("O");
    var correlationId = Guid.NewGuid().ToString();

    message.Headers.Authorization = refer.GenerateInternalAuthorization(client, requestTime, _authentication.Key);
    message.Headers.Add(HeaderName.Refer, refer);
    message.Headers.Add(HeaderName.Client, client);
    message.Headers.Add(HeaderName.RequestTime, requestTime);
    message.Headers.Add(HeaderName.CorrelationId, correlationId);

    if (method != HttpMethod.Get && request != null)
    {
        var payload = JsonConvert.SerializeObject(request, new JsonSerializerSettings
        {
            ContractResolver = new CamelCasePropertyNamesContractResolver()
        });
        message.Content = new StringContent(payload, null, MediaTypeNames.Application.Json);
    }

    return message;
}
```

## Header Constants

```csharp
public static class HeaderName
{
    public const string CorrelationId = "X-Correlation-Id";
    public const string Refer = "X-Refer";
    public const string Client = "X-Client";
    public const string RequestTime = "X-Request-Time";
}
```

## Required Dependencies
- `DevII.Authentication` (.NET 8+) or `Issuing.Authentication` (.NET 6) — provides `GenerateInternalAuthorization` extension
- `Authentication.Key` from appsettings or Secrets Manager

## Receiving Side (Validation)
Controllers requiring HMAC auth use:
```csharp
[Authorize] // JWT validation
[RequiredHeadersFilter] // Validates X-Refer, X-Client, X-Request-Time presence
```

## Checklist
- [ ] Add `Authentication.Key` to appsettings/secrets
- [ ] Inject `IClientContext` for caller identity
- [ ] Set `X-Correlation-Id` for tracing
- [ ] Use `CamelCasePropertyNamesContractResolver` for JSON serialization
- [ ] Log the correlation ID with each outbound call
