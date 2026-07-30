# Chapter 9: Session Vulnerabilities

## Core Idea
Once authentication succeeds, the session identifier and its associated state become the target — attackers hijack sessions over the network or via XSS, forge weak or client-suggested IDs, or tamper with client-held state — so sessions need proven frameworks, strong random IDs, correct cookie flags, and tamper-evidence (signing/encryption) rather than blind trust in the client.

## Frameworks Introduced
- **Server-side sessions with shared store**: session ID issued via `Set-Cookie`, session state kept server-side (in-memory, DB, or Redis) so it survives across a load-balanced fleet.
  - When to use: multi-server deployments behind a load balancer, where sticky sessions alone are unreliable.
  - How: configure `express-session` (or equivalent) with a shared backing store (`connect-redis`) instead of the default in-memory store, so any server instance can look up any session.
- **Client-side sessions / JWTs**: entire session state (and often user identity) travels in the cookie or Authorization header, avoiding a shared store lookup.
  - When to use: microservice architectures where independent services need to verify a caller without hitting a central auth service; or when a shared session store would bottleneck at scale.
  - How: sign (HMAC) or encrypt session payloads (`cookie-parser` signed cookies, `jsonwebtoken` for JWTs); each consuming service validates the signature before trusting the payload.
- **Cookie hardening (Secure + HttpOnly + SameSite)**: cookie attributes that block network sniffing and JS-based theft.
  - When to use: any cookie carrying a session ID or JWT.
  - How: set `Secure` (HTTPS-only transmission), `HttpOnly` (inaccessible to JavaScript), and appropriate `SameSite` value at session-store configuration time.

## Key Concepts
- **Session hijacking**: stealing a valid session identifier to impersonate its owner, via network sniffing (MITM) or XSS.
- **Session fixation**: an attacker pre-chooses a session ID (often via a crafted URL), tricks the victim into authenticating under it, then reuses that same ID to hijack the now-authenticated session.
- **Session tampering**: modifying client-held session state (in a client-side session or JWT) to escalate privilege or impersonate another user, unless the payload is signed or encrypted.
- **PRNG vs. cryptographically secure RNG**: a plain pseudorandom number generator (fast but predictable) is unsafe for generating session IDs; use a CSPRNG (e.g., `java.security.SecureRandom`) instead.
- **HMAC (Hash-Based Message Authentication Code)**: a signature scheme used to detect tampering in client-side session cookies and JWT payloads.
- **Sticky load balancing**: routing all requests from one client to the same backend server — helps but isn't a complete substitute for a shared session store, since users can change IP mid-session.
- **JWT (JSON Web Token)**: a digitally signed, JSON-encoded token that lets services validate a caller's identity without querying the issuing service — but signed is not the same as encrypted.

## Mental Models
- Use a proven session framework, never roll your own — Tomcat's own history of weak session-ID generation (patched by moving to `SecureRandom`) shows even mature platforms get this wrong.
- Think of a JWT/client-side session as a sealed but transparent envelope: the signature proves nobody tampered with the contents, but anyone (including the user, via devtools) can still read what's inside unless you also encrypt it.
- Treat session IDs like passwords in transit: never put them in URLs (bookmarks, logs, browser history, and Referer headers can all leak them), and always require Secure + HttpOnly.

## Anti-patterns
- **Session IDs in URLs**: leaks via server logs, browser history, and the Referer header, and directly enables session fixation — disable URL-based session tracking (`tracking-mode: COOKIE` in Tomcat, `session.use_trans_sid = 0` in PHP).
- **Weak/predictable session ID generation**: a PRNG-based session ID generator (old Tomcat using `java.util.Random`) lets attackers narrow down and eventually guess valid IDs via high-volume requests.
- **Trusting a signed-but-unencrypted JWT/cookie as private**: digital signatures prove integrity, not confidentiality — sensitive data in the payload is still readable via the browser's debugger.
- **Accepting a client-suggested session ID**: enables session fixation — the server must always generate its own session ID at login, never adopt one supplied by the request.

## Code Examples
```javascript
const express          = require('express');
const sessions         = require('express-session');
const RedisStore       = require("connect-redis")(session);
const { createClient } = require("redis");
const app              = express();
const redis = createClient();
redis.connect().catch(console.error);

app.use(sessions({
  secret: "8b1b8c46-480b-4ee7-be12-a83953fe79ee",
  store: new RedisStore({ client: redis }),
  cookie: {
    maxAge:   1000 * 60 * 60 * 24,
    secure:   true,
    httpOnly: true,
    sameSite: 'lax'
  }
}))
```
- **What it demonstrates**: server-side session config with a shared Redis store (for load-balanced deployments) plus hardened cookie flags.

```javascript
/**
 * Unsign and decode the given `input` with `secret`,
 * returning `false` if the signature is invalid.
 */
exports.unsign = function(input, secret){
  var tentativeValue = input.slice(0, input.lastIndexOf('.')),
      expectedInput  = exports.sign(tentativeValue, secret),
      expectedBuffer = Buffer.from(expectedInput),
      inputBuffer    = Buffer.from(input);
  return (
    expectedBuffer.length === inputBuffer.length &&
    crypto.timingSafeEqual(expectedBuffer, inputBuffer)
  ) ? tentativeValue : false;
};
```
- **What it demonstrates**: tamper detection for a client-side session cookie, using a timing-safe comparison to avoid introducing a new timing side-channel while validating the signature.

```java
protected void getRandomBytes(byte bytes[]) {
    SecureRandom random = randoms.poll();
    if (random == null) {
        random = createSecureRandom();
    }
    random.nextBytes(bytes);
    randoms.add(random);
}
```
- **What it demonstrates**: Tomcat's fix for weak session-ID generation — switching to `java.security.SecureRandom`, a cryptographically secure RNG.

## Reference Tables
| Session model | State location | Scales via | Key risk | Mitigation |
|---|---|---|---|---|
| Server-side | Server/session store | Shared store (Redis/DB) behind LB | Store becomes bottleneck | Redis/in-memory data store |
| Client-side (signed cookie) | Cookie | No shared store needed | Tampering, readability | HMAC signature; encrypt if sensitive |
| JWT | Cookie or Authorization header | Independent verification per microservice | Same as above, plus XSS exposure if in JS-readable storage | HttpOnly cookie delivery; signature validation per service |

## Worked Example
An older Java web application passes session IDs in the URL as `?JSESSIONID=83730bh3ufg2` for browsers that don't support cookies. An attacker crafts a link containing a fictional session ID and sends it to a victim. The victim clicks it, lands on the login page under that attacker-chosen ID, and logs in — the vulnerable server creates the new authenticated session under the ID the attacker already knows. The attacker now simply revisits the same URL and inherits the victim's authenticated session (session fixation), no credential theft required.

The fix has two parts: disable URL-based session tracking entirely (`<tracking-mode>COOKIE</tracking-mode>` in Tomcat's `web.xml`, or `session.use_trans_sid = 0` in `php.ini`), and ensure the session framework never accepts a client-suggested session ID — it must always mint a fresh, cryptographically random ID at the point of authentication, discarding whatever ID (if any) was active before login.

## Key Takeaways
1. Use a proven, actively maintained session framework rather than building session management from scratch.
2. Always set `Secure` and `HttpOnly` on session cookies; add appropriate `SameSite` handling.
3. Ensure session IDs come from a cryptographically secure RNG, never a general-purpose PRNG.
4. Never accept a client-suggested session ID — always mint a new one server-side after authentication, to prevent fixation.
5. Disable any configuration that allows session IDs to travel in URLs.
6. Sign or encrypt client-side sessions and JWTs — signing alone proves integrity, not confidentiality.
7. Assume client-side session/JWT payloads are readable by the user; never store data there you don't want them to see.

## Connects To
- **Ch 8**: sessions begin where authentication ends — weak login flows compound with weak session handling.
- **Ch 13**: session-ID generation weaknesses are exactly the kind of third-party framework vulnerability worth tracking via CVE audits.
- **Cross-site scripting (Ch 6, referenced)**: XSS is the other major vector for session hijacking, alongside network MITM.
