# Future: Migrate DOPA from kyc-e-kyc-api to Verification API

## Status: NOT YET — will impact existing customers

## Context

Currently `kyc-partner-api` calls DOPA via two paths:
- **Active (legacy):** `IKycEkycClient.CheckStatusByLaserAsync()` → kyc-e-kyc-api → DOPA SOAP directly
- **Ready but unused:** `IKycVerificationClient.CheckStatusByLaser()` → Verification API → DOPA

## When to Migrate

- When kyc-e-kyc-api DOPA SOAP dependency needs to be retired
- When Verification API is stable in production with DOPA endpoints proven
- Requires coordination with existing partners using the eKYC flow

## Migration Steps (when ready)

1. Switch `kyc-partner-api` V1/V3 handlers from `IKycEkycClient.CheckStatusByLaserAsync()` to `IKycVerificationClient.CheckStatusByLaser()`
2. Verify Verification API handles the same request/response contract
3. Run in parallel (feature flag) before full cutover
4. Deprecate kyc-e-kyc-api DOPA SOAP calls

## Impact Assessment

- All existing DipChip/eKYC partners use the current flow
- Changing the DOPA path could affect response times (extra hop: partner → verification → DOPA vs partner → ekyc → DOPA)
- Need regression testing with all partner integrations

## Decision

Do NOT create new V3 APIs in kyc-partner-api for DOPA via Verification. The `IKycVerificationClient` is already wired — just switch handlers when ready.
