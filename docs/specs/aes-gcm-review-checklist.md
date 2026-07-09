# AES-GCM Review Checklist — Crypto Test Gateway, Phase 1 Extraction

Companion to [crypto-test-gateway-spec.md](crypto-test-gateway-spec.md). Run this checklist when reviewing the crypto code extracted from the test page. Sources verified 2026-07 (Microsoft Learn AesGcm docs, NIST SP 800-38D commentary, dotnet/runtime #71366).

Background: nonce reuse under the same AES-GCM key is the catastrophic failure mode — it breaks both confidentiality and authentication. PGP hybrid schemes usually generate a fresh AES session key per message, which makes nonce handling forgiving, but the review must *confirm* the extracted code actually does that rather than assume it.

## A. Key lifecycle & nonce binding

- [ ] Confirm the key reuse model: fresh symmetric session key per message (typical PGP hybrid) or a reused key. If per-message, a static nonce may have been "safe" in the original code; if the key is ever reused, every message MUST have a unique nonce.
- [ ] Document how the nonce is generated: CSPRNG (`RandomNumberGenerator.GetBytes`) or counter-based. Random nonces carry a NIST limit of ~2^32 invocations per key.
- [ ] Red flags: hardcoded/fixed nonce with a reused key; nonce derived from plaintext or a bare timestamp; nonce from a non-crypto PRNG (`System.Random`).

## B. API & constructor compliance (.NET 8+)

- [ ] All `AesGcm` instantiations use `new AesGcm(key, tagSizeInBytes)`. The old `new AesGcm(key)` constructor is obsolete (SYSLIB0053) because it allowed silent tag-truncation attacks — .NET 6-era code (our test page) likely uses it and must be updated during extraction.
- [ ] Tag size is fixed at instantiation, not inferred from input; `Decrypt()` must reject tags of any other length.

## C. Tag handling & authentication

- [ ] Tags are always full size per the internal spec (16 bytes unless the spec says otherwise) and never truncated in storage or transport.
- [ ] The tag travels with the ciphertext and nonce; nothing discards or shortens it before decryption.
- [ ] If AAD (associated data) is used, the exact same bytes are passed to `Encrypt()` and `Decrypt()` — header changes must fail authentication.

## D. Platform & limits

- [ ] Cross-platform note: on macOS (.NET 8+/CryptoKit) only 16-byte tags are supported; hardcoded 12-byte tags throw at runtime. Relevant if devs run the gateway locally on Macs.
- [ ] Plaintext per (key, nonce) pair is limited to ~64 GiB (2^39 − 256 bits); .NET does not enforce this. Irrelevant for JSON payloads, but document it if the spec ever covers file transfer.

## E. Golden-vector interaction

- [ ] Where nonces/session keys are random, golden-vector tests cannot demand byte-identical ciphertext — instead assert that the original code path can decrypt and verify output from the extracted library, and vice versa (cross-decryption both directions).

## F. Anti-patterns to reject outright

- [ ] No AES-ECB anywhere.
- [ ] No hand-rolled AES-CBC + HMAC unless the upstream spec mandates it — and then only Encrypt-then-MAC with constant-time comparison.
- [ ] No `#pragma warning disable SYSLIB0053` without a documented reason.
