# Project Map

| Folder | Service | Tech | DB | .kiro/ |
|--------|---------|------|-----|--------|
| kyc-partner-api | External partner gateway | .NET 6, EF Core | MySQL 5.7 | ✅ |
| identification | Business customer onboarding | .NET 8, EF Core | MySQL | ✅ |
| kyc-customer-due-diligence | AML/CDD screening | .NET 8, EF Core | MySQL | ✅ |
| verification | DOPA/DBD verification | .NET 10, EF Core | MySQL | ✅ |
| cdd-business | Business CDD screening | .NET 8, EF Core | MySQL | ✅ |
| kyc-e-kyc-api | eKYC internal API | .NET 6, EF Core | MySQL | ✅ |
| kyc-admin-portal | Admin web portal | .NET 6, Razor/MVC | MySQL | ✅ |
| approval | Application approval workflow | .NET 10, EF Core | MySQL | — |
| risk-assessment | Risk scoring & assessment | .NET 8, EF Core | MySQL | — |
| kyc-database | Database scripts & stored procedures | SQL (MySQL) | MySQL | ✅ |

## Service Communication

```
Partner (external)
    │
    ▼
kyc-partner-api ──► identification ──► verification
       │                    │
       │                    └──► SQS ──► kyc-customer-due-diligence
       │
       ├──► kyc-customer-due-diligence (CDD status)
       ├──► verification (DOPA check)
       └──► kyc-e-kyc-api (eKYC/face/DOPA via OAuth)

kyc-admin-portal ──► kyc-customer-due-diligence (override CDD)
                 ──► kyc-e-kyc-api

cdd-business ──► external CDD providers (Refinitiv, etc.)
```
