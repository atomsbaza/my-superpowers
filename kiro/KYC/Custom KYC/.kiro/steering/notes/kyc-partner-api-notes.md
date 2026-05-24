# kyc-partner-api Notes

## HMAC Auth Scheme Compatibility (Issuing vs DevII)

**Critical:** `Issuing.Cryptography.GenerateInternalAuthorization` hardcodes scheme `"basic"`. `DevII.Authentication` validates scheme `"ApiKey"`. These are incompatible.

### Rule: Match the scheme to the downstream service's auth library

| Downstream service | Auth lib | Required scheme |
|---|---|---|
| identification (.NET 8) | `DevII.Authentication` | `ApiKey` |
| verification (.NET 10) | `DevII.Authentication` | `ApiKey` |
| kyc-customer-due-diligence (.NET 8) | `Issuing.Authentication` | `basic` |
| risk-assessment (.NET 8) | `Issuing.Authentication` | `basic` |
| cdd-business (.NET 8) | `Issuing.Authentication` | `basic` |

### Pattern for DevII consumers (ApiKey scheme)
Do NOT use `GenerateInternalAuthorization` — use directly:
```csharp
message.Headers.Authorization = new AuthenticationHeaderValue("ApiKey", (refer + client + requestTime).ComputeHmacSha512(_authentication.Key));
```

### Pattern for Issuing consumers (basic scheme)
Use the existing extension:
```csharp
message.Headers.Authorization = refer.GenerateInternalAuthorization(client, requestTime, _authentication.Key);
```

### General rule
- .NET 6 services use `Issuing.*` libs → `basic` scheme
- .NET 8+ services use `DevII.*` libs → `ApiKey` scheme

## Authentication Config Structure (as of 6.9.0)

```json
"Authentication": {
  "Issuer": "...",
  "Audience": "...",
  "Internal": {
    "SigningKey": "..."
  },
  "Key": "..."
}
```

- `Internal.SigningKey` — JWT signing key for partner tokens (same value as `Key`)
- `Key` — HMAC key for outgoing calls to internal services
- `SecurityKey` was removed — replaced by `Internal.SigningKey`
- `OAuthHandler` generates JWT using `Internal.SigningKey`
- `Startup.Jwt.cs` validates JWT using `Internal.SigningKey` (throws `InvalidOperationException` if missing)

## UsePathBase

`app.UsePathBase("/partner")` — no trailing slash. With trailing slash the prefix match fails.

## Version

Current version: **6.9.0** (`AssemblyVersion` + `FileVersion` in `DipChip.API.csproj`)