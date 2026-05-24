---
name: pii-encryption
description: 'AES encryption/decryption setup for PII fields with EntitiesExtra partial classes. Use when adding new PII columns or setting up encryption in a project. Pairs with: compliance-reviewer subagent.'
---

# PII Encryption (AES at Rest)

## When to Use
- Adding a new entity with PII fields (name, email, ID card, passport, phone, DOB)
- Setting up encryption in a new project
- Adding decrypted property access to an existing entity

## Prerequisites
- `IDatabaseCryptography` interface exists in Domain
- `DatabaseCryptography` implementation exists in Infrastructure
- AES key configured in Secrets Manager

## Steps

1. **Entity** — Store encrypted value in main entity (`Domain/Entities/`):
```csharp
public partial class {{Entity}} : BaseEntity
{
    public string? FirstName { get; set; }  // Encrypted AES value
    public string? Email { get; set; }       // Encrypted AES value
    public string? IdCardNo { get; set; }    // Encrypted AES value
}
```

2. **EntitiesExtra** — Add decrypted properties (`EntitiesExtra/` or `Domain/EntitiesExtra/`):
```csharp
public partial class {{Entity}}
{
    private readonly IDatabaseCryptography? _crypto;

    public {{Entity}}(IDatabaseCryptography crypto) => _crypto = crypto;
    public {{Entity}}() { }

    public string? FirstNameDecrypted => _crypto?.Decrypt(FirstName);
    public string? EmailDecrypted => _crypto?.Decrypt(Email);
    public string? IdCardNoDecrypted => _crypto?.Decrypt(IdCardNo);
}
```

3. **Encrypt on save** — In repository or handler before persisting:
```csharp
entity.FirstName = _crypto.Encrypt(request.FirstName);
entity.Email = _crypto.Encrypt(request.Email);
entity.IdCardNo = _crypto.Encrypt(request.IdCardNo);
```

4. **Read decrypted** — Always use `*Decrypted` properties:
```csharp
var name = entity.FirstNameDecrypted; // Never entity.FirstName directly
```

5. **Log masking** — Never log decrypted values raw:
```csharp
logger.LogInformation("Processing {Name}", name.MaskName());
```

## EF Core Configuration
```csharp
entity.Property(e => e.FirstName).HasColumnName("FirstName").HasMaxLength(500); // Encrypted is longer
entity.Property(e => e.Email).HasColumnName("Email").HasMaxLength(500);
```

## Validation
- [ ] PII columns use sufficient varchar length for encrypted values (typically 3-4x plain text)
- [ ] EntitiesExtra partial class created with decrypted properties
- [ ] No raw PII in log statements
- [ ] Repository reads use decrypted properties
- [ ] Repository writes encrypt before save
- [ ] Unit tests mock IDatabaseCryptography

## Variations
| .NET Version | Crypto Package |
|---|---|
| .NET 8+ | DevII.Cryptography or project-local |
| .NET 6 | Issuing.Cryptography or project-local |
