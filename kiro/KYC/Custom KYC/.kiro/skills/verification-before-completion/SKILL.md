---
name: verification-before-completion
description: "Before claiming any task is done, fixed, or ready to deploy — run the verification commands and confirm output. KYC-specific gate: tests, build, migrations, secrets, PII masking, health check. Evidence before assertions."
---

# Verification Before Completion

Claiming work is complete without running the checks is not efficiency — it is risk shifted onto the next engineer or onto production.

**Core principle: evidence before claims, always.**

---

## The Iron Law

```
NO COMPLETION CLAIM WITHOUT FRESH VERIFICATION OUTPUT IN THIS MESSAGE
```

If you have not run the command in this response, you cannot claim it passes.

---

## KYC Gate Checklist

Run every applicable item before declaring a task done. State the output of each command inline.

### 1. Build & Tests

```bash
# Run from solution root
dotnet build src/{Solution}.sln
dotnet test src/{Solution}.sln
```

- [ ] Build exits 0 — no compilation errors
- [ ] All tests pass — `X passed, 0 failed`
- [ ] No test skipped that covers the changed path

### 2. DB Migration (if schema changed)

```bash
dotnet ef migrations add <Name> --context PrimaryDbContext \
  --project src/{Project}.Infrastructure \
  --startup-project src/{Project}.API
```

- [ ] Migration file generated and reviewed — no unintended DROP or ALTER
- [ ] Migration applied to SIT DB before deploying app
- [ ] Rollback script written and attached to Jira ticket
- [ ] Stored procedures updated if affected (prefix: `sp`)

### 3. Secrets Manager (if new config keys added)

- [ ] New key added to `APP_SECRET_MANAGER` secret in AWS Secrets Manager (all envs: SIT, UAT, Prod)
- [ ] New key added to `appsettings.json` as placeholder: `"+++ FROM SECRET MANAGER +++"`
- [ ] No hardcoded credentials or connection strings in committed files

### 4. PII & Logging (if new personal data fields added)

- [ ] New PII columns are AES encrypted at rest (`IDatabaseCryptography` used on write)
- [ ] `EntitiesExtra` partial class provides `*Decrypted` properties
- [ ] Log statements use masking (`.MaskName()`, `.ExceptLastFour()`, etc.) — no raw PII in logs
- [ ] EF column length is sufficient for encrypted value (≥ 3× plaintext length, typically 500)

### 5. Service Contract (if request/response shape changed)

- [ ] Breaking change? → new version folder created (`Handler/V{n+1}/`)
- [ ] Non-breaking addition? → existing consumers still compile and behave correctly
- [ ] SQS message contract updated on both producer and consumer sides
- [ ] Consumer deployed before producer for SQS contract changes
- [ ] Provider deployed before consumer for HTTP contract changes

### 6. Health Check

```bash
# After deploying to SIT
curl -s https://{service-sit-host}/hc
curl -s https://{service-sit-host}/diag
```

- [ ] `/hc` returns HTTP 200
- [ ] `/diag` shows expected dependencies (DB, Redis, downstream services)

### 7. Cross-Service Impact (if multiple services changed)

- [ ] Each affected service builds and tests pass independently
- [ ] Deploy order matches dependency graph (upstream first — see `project-map.md`)
- [ ] HMAC auth header set correctly on new HTTP client calls
- [ ] `X-Correlation-Id` propagated through new service call chain

---

## Common Rationalisations (and why they fail)

| Claim | Why it doesn't count |
|---|---|
| "Tests should pass now" | Should ≠ do. Run them. |
| "I only changed one line" | One line broke production before. |
| "Build passed locally" | SIT config differs. Verify on SIT. |
| "Migration will apply automatically" | It won't unless explicitly run. |
| "Secrets are the same as before" | New keys aren't. Check each one. |
| "PII masking is already set up" | Not for the new field you just added. |

---

## What to State When Done

```
✅ dotnet build: 0 errors
✅ dotnet test: 47 passed, 0 failed
✅ Migration: AddCustomerStatusColumn applied to SIT
✅ Secrets: Authentication:NewKey added to SIT/UAT/Prod
✅ /hc: 200 OK
✅ No raw PII in log statements (grep verified)
```

Never: "Looks good" / "Should be fine" / "I'm confident" without running the above.
