# Chapter 8: Authentication Vulnerabilities

## Core Idea
Attackers primarily try to steal or guess credentials via brute force, so defenses must layer SSO delegation, stronger password nudges, automated-guessing blockers, MFA, and correct credential storage — while also closing side-channel leaks (user enumeration, timing attacks) that make brute-forcing easier.

## Frameworks Introduced
- **Brute-force attack via automated tooling (Hydra)**: repeatedly submit username/password combinations against a login form until one succeeds.
  - When to use (as a defender, to test yourself): assess your login, signup, and password-reset endpoints before an attacker does.
  - How: `hydra -l admin -P /usr/share/wordlists/rockyou.txt example.com https-post-form "/login:user=admin&password=^PASS^:Invalid credentials"` — response-text matching reveals success/failure.
- **Defense-in-depth authentication stack**: SSO/OAuth/SAML → password complexity nudges → CAPTCHA → rate limiting → MFA → secure storage.
  - When to use: for any system holding user credentials, layer these rather than relying on one control.
  - How: delegate credential custody to a trusted IdP where possible (SSO); where you must store passwords, nudge complexity via a strength meter (zxcvbn), throttle guessing (CAPTCHA + rate limiting), and require a second factor for high-value accounts.
- **Hash + salt + pepper (inbound credentials) vs. encrypt with separated key (outbound credentials)**: two different storage models for two different threat models.
  - When to use: hash+salt+pepper for passwords you only need to *verify*, never read back; encrypt for credentials your own code needs to *use* at runtime (DB passwords, API keys).
  - How: bcrypt with per-user salt stored alongside the hash, plus a pepper stored outside the database (e.g., in environment/config); AES-256-CBC with the key stored in a separate location (ideally a key management store) from the encrypted value and IV.

## Key Concepts
- **User enumeration**: leaking, via differing error/acknowledgment messages, whether a given username/email exists in the system.
- **Timing attack**: inferring information (e.g., account existence) by measuring how long an operation like password hashing takes to execute.
- **Salt**: a per-user random value mixed into a password before hashing, forcing attackers to precompute hashes separately for every user.
- **Pepper**: a single secret value, stored outside the database (e.g., config/env), mixed into every password hash so a stolen DB alone isn't enough to crack passwords.
- **Rainbow table**: a precomputed table of hash values for common passwords, used to reverse weak/unsalted hashes quickly.
- **Key management store**: a managed service for creating/storing encryption keys separately from the data they protect.
- **WebAuthn / biometrics**: a passwordless authentication flow where a public key is registered with the server and a private key stays on the user's device, unlocked by biometric proof.
- **Lockout attack**: a denial-of-service variant where an attacker deliberately triggers account lockouts (via rate limiting) to lock out legitimate users.
- **MFA (multifactor authentication)**: requiring a second proof of identity (biometric, authenticator app, or SMS) beyond the password.

## Mental Models
- Think of authentication as an onion: each layer (SSO, complexity nudge, CAPTCHA, rate limit, MFA, storage) stops a different class of attacker; strip one layer and only that class gets through.
- Use the same code path whether or not the user exists — treat "does this account exist" as sensitive information leaking through both wording (enumeration) and timing (timing attack).
- Treat inbound passwords as write-only (hash, never decrypt) and outbound credentials as read-write-but-guarded (encrypt with a key held elsewhere) — conflating the two models is the root of most storage mistakes.

## Anti-patterns
- **Plaintext password storage**: catastrophic on breach — the RockYou 2009 leak of 14 million plaintext passwords became the standard wordlist attackers still use today.
- **MD5/SHA-1 for password hashing**: fast, collision-prone algorithms that are cheap for attackers to brute-force; use bcrypt/SHA-2/SHA-3 instead, which are deliberately slow.
- **Differing error messages across login/signup/reset**: "Invalid password" vs. "No such user" (or equivalent) directly enables user enumeration.
- **Rate limiting by username only**: lets an attacker rotate usernames from one IP to route around the throttle; rate limit by IP (or both) instead.
- **Storing an encryption key alongside the data it encrypts**: defeats the purpose of encryption — an attacker who steals the config store gets both pieces at once.
- **Skipping the password-hash computation when the username doesn't exist**: creates a measurable timing difference that lets attackers enumerate valid usernames.

## Code Examples
```ruby
require 'bcrypt'
def hash_password(password)
  salt   = BCrypt::Engine.generate_salt
  pepper = ENV['PEPPER']
  hashed_password = BCrypt::Engine.hash_secret(pepper + password + salt, salt)
  return [hashed_password, salt]
end

def check_password(password, hashed_password, salt)
  pepper = ENV['PEPPER']
  recalculated_hash = BCrypt::Engine.hash_secret(pepper + password + salt, salt)
  return hashed_password == recalculated_hash
end
```
- **What it demonstrates**: bcrypt hashing with a per-user salt and a globally stored pepper, so a stolen DB alone can't be cracked.

```ruby
def login(username, password, users)
  user = User.find_by_username username
  stored_password = user.nil? ? BCrypt::Password.create("") : BCrypt::Password.new(user[:password_hash])
  if stored_password == password and not user.nil?
    sign_in(:user, user)
    render json: { message: 'Welcome back!' }, status: :found
  else
    render json: { error: 'Invalid email or password.' }, status: :unauthorized
  end
end
```
- **What it demonstrates**: timing-attack mitigation — a dummy hash is computed even when the username doesn't exist, so response time doesn't leak account existence.

```ruby
require 'openssl'
password = ARGV[0]
key      = ARGV[1]
iv = OpenSSL::Random.random_bytes(16)
cipher = OpenSSL::Cipher.new('aes-256-cbc')
cipher.encrypt
cipher.key = key
cipher.iv  = iv
encrypted_password = cipher.update(password) + cipher.final
encrypted_data = iv + encrypted_password
```
- **What it demonstrates**: AES-256-CBC encryption of an outbound credential, storing the IV alongside the ciphertext but the key in a separate location.

## Reference Tables
| Storage need | Technique | Reversible? | Where the "secret" lives |
|---|---|---|---|
| Inbound user password | bcrypt + salt + pepper | No (one-way) | Pepper in config/env, separate from DB |
| Outbound DB/API credential | AES-256 (or key-management-store) | Yes (by design) | Encryption key in a separate store from ciphertext |
| Legacy/insecure | MD5, SHA-1, plaintext | N/A | N/A — avoid entirely |

| Defense layer | Stops |
|---|---|
| SSO / OAuth / SAML | Need to store credentials at all |
| Password complexity nudge (zxcvbn) | Weak/guessable passwords |
| CAPTCHA | Automated brute force / mass signup or reset abuse |
| Rate limiting (by IP) | High-volume guessing |
| MFA (biometric > authenticator app > SMS) | Stolen/guessed single-factor credentials |
| Hash+salt+pepper / AES+separate key | Data theft translating directly into credential compromise |

## Worked Example
A login page shows "Incorrect password" only when the username exists, and "Invalid credentials" otherwise for missing users. An attacker runs Hydra against the `/login` endpoint, harvesting every username that returns "Incorrect password" — building a valid-username list without ever needing a working password. They then reuse the same enumeration trick against the signup and password-reset pages, discovering the same information (and incidentally triggering a flood of password-reset emails, effectively spamming those users).

The fix: standardize on identical wording everywhere ("Invalid credentials", "Check your inbox") regardless of whether the account exists, and add a CAPTCHA to signup/reset pages to stop the mass-email abuse. For login specifically, also normalize timing: compute a bcrypt hash unconditionally (against a dummy hash if the user is missing) so the HTTP response time is statistically identical whether or not the username was valid — closing the timing side-channel that the wording fix alone leaves open.

## Key Takeaways
1. Prefer delegating authentication to an SSO/OAuth/SAML identity provider over storing your own credentials.
2. Nudge for password length over complexity (zxcvbn-style scoring) since length costs attackers more compute to brute-force.
3. Put CAPTCHA and rate limiting (by IP) on login, signup, and reset endpoints alike — all three leak enumeration and invite abuse.
4. Require MFA for high-value systems; prefer biometrics/authenticator apps over SMS.
5. Hash+salt+pepper passwords you only verify; encrypt (with a separately stored key) credentials you must read back.
6. Keep error/acknowledgment messages identical regardless of account existence, on every credential-related page.
7. Always perform the password-hash computation, even for nonexistent users, to prevent timing-based enumeration.

## Connects To
- **Ch 9**: once authentication succeeds, session management takes over as the next attack surface (hijacking, fixation).
- **Ch 13**: monitoring for known vulnerabilities in whichever third-party auth libraries (bcrypt, JWT libs, WebAuthn polyfills) you depend on.
- **Ch 15**: password rotation and credential-compromise assumptions after a breach tie back to how credentials were stored here.
