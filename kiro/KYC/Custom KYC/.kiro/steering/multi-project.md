# Multi-Project Convention

## Before Editing Any Sub-Project

1. Read that project's `.kiro/steering/` files (tech.md, structure.md, guardrails.md)
2. Check the project's `.kiro/hooks/` for active automation
3. Match the project's existing patterns — do NOT introduce patterns from other projects

## Project Ownership

| Domain | Owner Project | Consumers |
|--------|--------------|-----------|
| Partner onboarding API | kyc-partner-api | External partners |
| Individual customer identity | identification | kyc-partner-api |
| DOPA/DBD verification | verification | identification, kyc-partner-api, kyc-e-kyc-api |
| CDD individual screening | kyc-customer-due-diligence | identification (via SQS), kyc-admin-portal |
| CDD business screening | cdd-business | kyc-admin-portal |
| eKYC (face/DOPA/DipChip) | kyc-e-kyc-api | kyc-partner-api, kyc-admin-portal |
| Admin operations | kyc-admin-portal | Internal staff |

## Internal Package Conventions

| .NET Version | Auth Package | Caching Package | Secrets Package | Logging |
|---|---|---|---|---|
| .NET 8+ | DevII.Authentication | DevII.Caching (`IRedisCaching`) | DevII.SecretsManager | DevII.Logging |
| .NET 6 | Issuing.Authentication | Issuing.Caching (`IRedisCaching`) | Issuing.SecretsManager | Issuing.Logging |

Both expose the same `IRedisCaching` interface. The package name differs by .NET version.

**Exception:** `verification` (.NET 10) uses `DevII.Caching` for Redis + `IMemoryCache` for short-lived token caching (DBD OAuth tokens). It does NOT use `AddCaching()` from the package — it registers `IMemoryCache` and `IConnectionMultiplexer` separately.

## Secret Manager Names

| Project | APP_SECRET_MANAGER | COMMON_SECRET_MANAGER |
|---------|---|---|
| kyc-partner-api | (in appsettings) | — |
| identification | (in appsettings) | — |
| verification | `verification/` (prefix-based) | — |
| kyc-customer-due-diligence | `kyc-cdd-individual-api-configuration` | `kyc-common-configuration` |
| cdd-business | `kyc-cdd-configuration` | `kyc-common-configuration` |
| kyc-e-kyc-api | (env-based) | — |
| kyc-admin-portal | (in appsettings) | — |
| verification | `verification/` (prefix-based) | `kyc-common-configuration` |
| identification | (in appsettings) | `kyc-common-configuration` |

## Cross-Project Changes

When a change spans multiple projects (e.g., adding a new API that another service calls):
1. Start with the **provider** (the project exposing the new endpoint)
2. Then update the **consumer** (the project calling it)
3. Ensure both sides agree on request/response contracts
4. Use the same error code conventions (see shared-conventions.md)

## Build Commands Quick Reference

| Project | Build | Test |
|---------|-------|------|
| verification | `dotnet build src/Verification.sln` | `dotnet test src/Verification.sln` |
| identification | `dotnet build src/Identification.sln` | `dotnet test src/Identification.sln` |
| kyc-customer-due-diligence | `dotnet build src/CustomerDueDiligence.sln` | `dotnet test src/CustomerDueDiligence.sln` |
| cdd-business | `dotnet build src/KYC.CDD.sln` | `dotnet test src/KYC.CDD.sln` |
| kyc-e-kyc-api | `dotnet build src/2C2P.eKYC.sln` | `dotnet test tests/` |
| kyc-partner-api | `dotnet build DipChip.sln` | `dotnet test DipChip.Test/` |
| kyc-admin-portal | `dotnet build eKycApp/eKycApp.sln` | `dotnet test eKycApp/eKycApp.Test/` |
