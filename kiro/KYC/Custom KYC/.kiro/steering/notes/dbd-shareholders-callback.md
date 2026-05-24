# Future: DBD Shareholders & Callback Exposure

## Status: NEEDS DECISION

## Problem

Verification API has these DBD endpoints:
- `POST /api/v1/dbd/shareholders/job` — creates async shareholder inquiry (requires a `CallbackURL`)
- `POST /api/v1/dbd/shareholders` — query shareholder result by Job ID
- `POST /api/v1/dbd/shareholders/callback` — receives callback FROM DBD when job completes

The **callback endpoint** is `[AllowAnonymous]` because DBD (external) calls it.
However, Verification is an **internal service** — not exposed to the internet.

## Options

1. **Expose only the callback via API Gateway** — route `/verification-api/api/v1/dbd/shareholders/callback` through the public gateway with IP whitelisting for DBD's IPs. Rest of Verification stays internal.

2. **Proxy callback through kyc-partner-api** — add a callback endpoint in kyc-partner-api (which IS public-facing) that forwards to Verification internally. Pass kyc-partner-api's public URL as the `CallbackURL` when creating jobs.

3. **Polling instead of callback** — don't use callbacks. Have a background job poll `InquiryShareholderByJobId` until the job completes. Simpler but adds latency.

## Current State

- Only `/api/v1/dbd/corporate` is proxied through kyc-partner-api (just added).
- Shareholders endpoints are NOT yet exposed through kyc-partner-api.
- The callback issue must be resolved before shareholders can be used in production.

## Decision Needed

Which approach for the callback? This affects:
- Infrastructure (gateway routing rules, IP whitelisting)
- Security (anonymous endpoint exposure surface)
- Latency (polling adds delay vs instant callback)
