# Chapter 3: Encryption

## Core Idea
Encryption in transit (TLS/HTTPS), encryption at rest, and one-way hashing for passwords and integrity checks are the foundational cryptographic controls every web application must apply correctly — not because you need to understand the underlying math, but because you need to know when and how to invoke each one.

## Frameworks Introduced
- **Encryption in transit via HTTPS/TLS**: Wrapping HTTP traffic in a TLS session so it cannot be read or manipulated en route.
  - When to use: For all traffic to and from your web server, without exception — not just login/checkout pages.
  - How: Obtain a certificate from a certificate authority, host it (with its private key) on your server, redirect all HTTP to HTTPS, and set an HSTS header so browsers stop attempting insecure connections at all.
- **Password hashing with salting/peppering**: Storing a one-way hash of a password (never the password itself), randomized so identical passwords don't produce identical hashes.
  - When to use: Every time you store user credentials.
  - How: Hash with a strong, slow algorithm (bcrypt); add a per-password random salt stored alongside the hash; optionally add a pepper (a secret value held in configuration, not the database) for defense in depth against a database-only breach.
- **Integrity checking via hashing**: Using a hash value transmitted alongside (or via a separate channel from) data to let a recipient detect unexpected tampering.
  - When to use: Whenever data crosses a trust boundary and you need to detect — without needing to store the original — whether it has been altered (TLS packets, dependency downloads, deployment artifacts, session cookies, intrusion detection on sensitive files).
  - How: Compute a hash of the data at the trusted source; pass the hash via a separate channel or protected mechanism; recompute and compare at the recipient.

## Key Concepts
- **Symmetric encryption**: The same key encrypts and decrypts; fast but requires securely sharing the key beforehand.
- **Asymmetric (public key) encryption**: Different keys for encryption (public, shareable) and decryption (private, secret); enables secure communication (as in HTTPS) without a pre-shared secret.
- **Hash / hash collision**: A one-way function whose output cannot be reversed to recover the input; a collision is the near-zero-probability event of two different inputs producing the same output.
- **Cipher suite**: The negotiated combination of key-exchange algorithm, authentication algorithm, bulk encryption algorithm, and message authentication code (MAC) algorithm used in a TLS handshake.
- **Digital certificate / certificate authority**: A certificate binds a public key to a domain and is signed by a certificate authority the browser trusts; a self-signed certificate triggers a browser warning because no trusted authority vouches for it.
- **Confidentiality / Integrity / Nonrepudiation**: The three guarantees HTTPS provides — traffic can't be read, can't be manipulated, and can't be spoofed.
- **HSTS (HTTP Strict Transport Security)**: A response header instructing the browser to always use HTTPS for a domain for a specified period, closing the window where an initial HTTP request could leak data.
- **Encryption at rest**: Encrypting data stored on disk (databases, backups, logs) so it's unreadable to anyone who obtains the raw disk/storage without the decryption key — but provides no protection if the key itself is stolen.
- **Lookup table attack**: A precomputed table of hash values for common passwords, defeated by salting (which makes every stored hash unique even for identical passwords).

## Mental Models
- Think of a hash algorithm as an "ultrareliable sausage machine": always the same output for the same input, and (almost) always a different output for a different input — but there's no way to run it backward to recover the original ingredients.
- Think of public key encryption as a padlock you can hand out freely: anyone can lock the box (encrypt with the public key), but only the holder of the private key can unlock it.
- Use encryption at rest as a defense against disk/media theft, not key theft — it does nothing if the attacker also gets the decryption key, so key management is the real control.
- Treat integrity checking as a generalizable pattern, not a one-off browser feature: the same "hash it, transmit the hash separately, recompute and compare" logic recurs in TLS, SRI (chapter 2), dependency managers, deployment pipelines, and intrusion detection.

## Anti-patterns
- **Storing plaintext passwords**: Turns any database breach into an instant full credential compromise, both for your site and (via reuse) every other site the user has an account on.
- **Weak hash algorithms (e.g., MD5)**: Considered broken for password storage because modern computing power makes brute-forcing or precomputed-table attacks feasible; use bcrypt instead.
- **Missing salt/pepper**: Without a salt, identical passwords hash identically, making the database vulnerable to lookup-table attacks across all users at once.
- **Trusting self-signed certificates in production**: No browser-trusted certificate authority vouches for them, so users see security warnings — self-signed certs are only appropriate for local dev/testing.
- **Encryption at rest without securing the key**: Gives a false sense of security; an attacker who steals the key alongside (or instead of) the disk defeats the control entirely.

## Code Examples
```
server {
    listen 80 default_server;
    server_name _;
    return 301 https://$host$request_uri;
}
```
- **What it demonstrates**: NGINX configuration redirecting all HTTP (port 80) traffic to HTTPS.

```
Strict-Transport-Security: max-age=604800
```
- **What it demonstrates**: HSTS header telling the browser to always use HTTPS for this domain for the next week (seconds).

```ruby
# bcrypt-based password hashing with salting (conceptual)
require 'bcrypt'
password_hash = BCrypt::Password.create("user_password")
# ... later, on login:
BCrypt::Password.new(password_hash) == "user_password_attempt"  # => true/false
```
- **What it demonstrates**: bcrypt automatically incorporates a random salt into the hash, so verifying a login means recomputing and comparing rather than decrypting.

```
Integrity checking use cases:
1. Detecting manipulated data packets during TLS transmission
2. Detecting manipulated software modules downloaded by a dependency manager
3. Ensuring code is deployed cleanly, without errors or unexpected modification
4. Detecting suspicious changes in sensitive files during intrusion detection
5. Detecting manipulated session data passed via a browser cookie
```
- **What it demonstrates**: The breadth of contexts where "hash it, compare it later" recurs as a security pattern.

## Reference Tables
| Property | Symmetric encryption | Asymmetric (public key) encryption |
|---|---|---|
| Keys used | Same key encrypts and decrypts | Separate public (encrypt) and private (decrypt) keys |
| Speed | Fast — used for bulk data | Slower — used mainly for key exchange/authentication |
| Key distribution problem | Must securely share the key beforehand | Public key can be shared openly; only private key must stay secret |
| Typical use | Bulk encryption within a TLS session | Initial TLS handshake / key exchange, digital certificates |

## Worked Example
A team is launching a web app that stores user passwords and payment metadata, and wants full encryption coverage end to end.

1. **In transit**: They obtain a certificate via their cloud provider's certificate manager, host it (with the private key) on their load balancer, and configure NGINX to `return 301 https://...` for any request hitting port 80. They add `Strict-Transport-Security: max-age=604800` to every HTTPS response so that after a user's first visit, their browser refuses to even attempt an HTTP connection for a week — closing the classic "user typed http:// once" leak window.
2. **At rest**: Their hosting provider (AWS RDS) offers encryption at rest as a checkbox at database-creation time. They enable it for the primary database, its backups, and its snapshots, and separately confirm application log files (which might incidentally capture request bodies) are also written to an encrypted volume. They note internally that encryption at rest does *not* protect them if an attacker steals the AWS IAM credentials that can also decrypt the volume — so IAM key hygiene is a separate, necessary control.
3. **Password storage**: On signup, instead of storing the submitted password, the backend runs it through bcrypt, which generates a random salt per password and folds it into the returned hash string. Only this hash is stored. On login, the same bcrypt verification function recomputes the hash from the submitted password plus the stored salt and compares it to the stored hash — the plaintext password is never persisted or comparable directly.
4. **Pepper as defense in depth**: Recognizing that a full database dump would still let an attacker brute-force weak individual passwords against their bcrypt hashes, they add a pepper — a secret string held only in application configuration (not the database) that is combined with the password before hashing. Now a database-only breach (without also compromising the app's config/secrets store) is insufficient to attack any password.
5. **Integrity check on deployment artifacts**: Their CI pipeline computes a SHA-384 hash of each build artifact before deployment and compares it against the hash recomputed after the artifact reaches production servers, catching any corruption or tampering introduced during the deploy step itself — the same hash-then-compare pattern used for SRI in chapter 2.

## Key Takeaways
1. Use HTTPS for all traffic, not just sensitive pages — redirect HTTP to HTTPS and set HSTS so browsers stop trying insecure connections altogether.
2. Enable encryption at rest wherever your hosting provider supports it, but manage the decryption key's access separately — encryption at rest is defeated by key theft.
3. Never store plaintext passwords; hash with bcrypt (not MD5), and always salt (ideally per-password) — pepper adds defense in depth against database-only breaches.
4. Distinguish symmetric encryption (fast, shared key) from asymmetric encryption (public/private key pair, powers HTTPS's initial handshake).
5. Use hashing for integrity checking anywhere you need to detect tampering without storing the original data — this pattern recurs across TLS, dependency managers, deployments, and session cookies.
6. A certificate's trust depends on the issuing certificate authority; self-signed certificates will always trigger browser warnings.

## Connects To
- **Ch 2**: Subresource Integrity (SRI) is this chapter's integrity-checking concept applied specifically to `<script>` tags.
- **Ch 7**: Certificate compromise, revocation, and key theft — only flagged here as "chapter 7 will cover this" — are the dedicated subject of the Network Vulnerabilities chapter.
- **Ch 8 (external)**: The book's later Authentication Vulnerabilities chapter revisits password hashing risk when hashes themselves leak, building on the salting/peppering foundation laid here.
