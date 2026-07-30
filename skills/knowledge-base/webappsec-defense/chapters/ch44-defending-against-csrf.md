# Chapter 44: Defending Against CSRF Attacks

## Core Idea
CSRF is defeated by combining origin/referer header verification, cryptographically strong per-user CSRF tokens, and an architectural rule that HTTP GET requests never alter server-side state — enforced application-wide via middleware rather than per-route.

## Frameworks Introduced
- **Header verification (Origin/Referer allowlisting)**: A first-line, low-cost CSRF defense checking that state-changing requests originate from a known-good set of origins.
  - When to use: As a baseline check on every state-changing request, always combined with stronger defenses since it fails if an attacker gets an XSS on your own allowlisted origin.
  - How: Reject requests where the `Origin` (POST-only) or `Referer` (all requests) header is missing or not in your allowlist of trusted origins.
- **CSRF token**: A cryptographically generated, per-session/per-request token the client must echo back on every state-changing request.
  - When to use: As the primary, most powerful CSRF defense — should be the default for any application handling authenticated state changes.
  - How: Server generates a low-collision token; client attaches it to every form submission and AJAX call; server verifies it's live, authentic, unmanipulated before processing; log and reject on failure.
- **Stateless CSRF token construction**: Building a CSRF token without server-side session storage, compatible with stateless/REST API architectures.
  - When to use: In modern stateless API designs, where reverting to stateful session tracking purely to support CSRF tokens is not worth the trade-off.
  - How: Combine a unique user identifier + timestamp (for expiration) + a cryptographic nonce whose key exists only on the server; encrypt/decrypt this bundle rather than looking it up in a session store.

## Key Concepts
- **Origin header**: Sent only on HTTP POST requests, indicates the request's origin, cannot be programmatically modified by JavaScript in major browsers.
- **Referer header**: Sent on all requests (unless `rel=noreferrer` is set on the originating link), also indicates request origin.
- **Stateless GET requests**: The architectural principle that GET requests must never modify server-side state, since they are the easiest CSRF attack vector (links, images).
- **Anti-CSRF middleware**: Request-processing code that runs before route logic on every (or every relevant) request, centralizing header verification and CSRF token validation application-wide.
- **Nonce**: A cryptographic value, unique per token, whose validating key exists only server-side — prevents token forgery even if the user ID and timestamp are guessable.
- **Split GET/update endpoints**: Refactoring a single endpoint that both retrieves and optionally updates state (via a GET param) into two separate endpoints — a safe GET and a POST-only update.

## Mental Models
- Think of header verification as a necessary but insufficient perimeter check — it fails the moment an attacker can execute script from your own origin (e.g., via a stored XSS), so it must never be your only defense.
- Treat CSRF tokens the way you'd treat authentication itself: unique per session/user, expiring, and cryptographically hard to forge — the token turns a scalable "attack anyone" exploit into "attack one specific, currently-valid user," which is far less practical.
- Use the "GET should never mutate state" rule as an architectural constraint, not a suggestion — any GET-triggerable state change (links, `<img>` tags) is inherently CSRF-exposed by the nature of how browsers issue GET requests.
- Think of application-wide CSRF middleware as "the weakest link breaks the chain" made operational — a defense implemented on some routes but not others leaves the unprotected routes as the actual attack surface.

## Anti-patterns
- **Combining retrieval and state-mutation in a single GET endpoint**: `GET /user?id=123&updates=email:hacker` lets any link, image tag, or hyperlink silently mutate state — split into GET (read) and POST (write) endpoints instead.
- **Relying on header verification alone**: Breaks down entirely if the attacker achieves XSS on an allowlisted origin, or if the site accepts user-generated content that could host a payload.
- **Per-route, inconsistent CSRF protection**: Any application without middleware-level, application-wide enforcement has only as much protection as its weakest unprotected route.
- **Rejecting only when both headers are absent, without allowlist matching**: The chapter's own middleware treats "no header at all" as suspicious, but a real allowlist check is still required — a present-but-unmatched origin/referer must also fail.

## Code Examples
```javascript
const validLocations = [
  'https://www.mega-bank.com',
  'https://api.mega-bank.com',
  'https://portal.mega-bank.com'
];

const validateHeadersAgainstCSRF = function (headers) {
  const origin = headers.origin;
  const referer = headers.referer;
  if (!origin || referer) {
    return false;
  }
  if (!validLocations.includes(origin) || !validLocations.includes(referer)) {
    return false;
  }
  return true;
};

const transfer = function (req, res) {
  if (!session.isAuthenticated) {
    return res.sendStatus(401);
  }
  if (!validateHeadersAgainstCSRF(req.headers)) {
    return res.sendStatus(401);
  }
  return transferFunds(session.currentUser, req.query.to_user, req.query.amount);
};
module.exports = transfer;
```
- **What it demonstrates**: Origin/referer allowlist verification gating a sensitive fund-transfer endpoint before any business logic runs.

```javascript
// GET (read-only, safe)
const getUser = function (req, res) {
  getUserById(req.query.id).then((user) => {
    return res.json(user);
  });
};

// POST (state-changing, separated out)
const updateUser = function (req, res) {
  getUserById(req.query.id).then((user) => {
    user.update(req.updates).then((updated) => {
      if (!updated) {
        return res.sendStatus(400);
      }
      return res.sendStatus(200);
    });
  });
};
```
- **What it demonstrates**: Splitting a combined read+update GET endpoint into a safe read-only GET and a state-changing POST, eliminating GET-based CSRF exposure for the update path.

```javascript
const CSRFShield = function (req, res, next) {
  if (!validateHeaders(req.headers, req.method) ||
      !validateCSRFToken(req.csrf, session.currentUser)) {
    logger.log(req);
    return res.sendStatus(401);
  }
  return next();
};
```
- **What it demonstrates**: Application-wide anti-CSRF middleware combining header verification and CSRF token validation as a single gate before any route logic executes.

## Reference Tables
### CSRF Defense Layers and Failure Modes

| Defense | Strength | Known failure mode |
|---|---|---|
| Origin/Referer header verification | First line of defense, near-zero cost | Fails if attacker achieves XSS on an allowlisted origin, or site hosts user-generated content |
| CSRF tokens (stateful or stateless) | Most powerful; turns "attack anyone" into "attack one specific user with a live token" | Requires consistent client-side propagation on every request (forms + AJAX) |
| Stateless GET requests | Eliminates the most distributable attack vector (links, images) | Only protects GET-based CSRF; POST-based CSRF still needs tokens |

## Worked Example
MegaBank's fund transfer endpoint, `POST https://www.mega-bank.com/transfer`, accepts `amount` and `to_user` params. The team builds a layered defense. First, `validateHeadersAgainstCSRF` checks that both `Origin` and `Referer` headers are present and match the `validLocations` allowlist (`www.mega-bank.com`, `api.mega-bank.com`, `portal.mega-bank.com`); a request missing either header, or coming from an unlisted origin, is rejected with 401 before `transferFunds` is ever called.

Recognizing header checks alone are insufficient, the team adds a stateless CSRF token: each token encodes the user's ID, an issuance timestamp, and a server-only-key nonce, all encrypted into a single string. The `CSRFShield` middleware runs on every request: `validateHeaders` re-checks origin/referer (using POST-specific logic requiring both origin and referer to match, versus GET-only logic requiring just referer), and `validateCSRFToken` decrypts the token, extracts `user_id`/`date`/`nonce`, and confirms the user ID matches the session's current user, the date is within one week (expiration), and the nonce validates cryptographically. If any check fails, the request is logged and rejected with 401 before any business logic runs — since this is middleware, it applies to every route uniformly rather than needing to be replicated per-endpoint.

Finally, the client side is updated to guarantee the token is always attached: rather than trusting every developer to remember it, the team wraps `XMLHttpRequest` (via the proxy pattern or a thin request-generation library) so the token is injected automatically depending on the HTTP verb, removing the risk of a forgotten client-side token call.

## Key Takeaways
1. Never let an HTTP GET request mutate server-side state — split combined read/update endpoints into GET and POST.
2. Use Origin/Referer header verification as a first-line, low-cost check, but never as your only defense.
3. Implement CSRF tokens (unique per user/session, expiring, cryptographically verified) as the primary defense mechanism.
4. In stateless/REST architectures, build stateless CSRF tokens from user ID + timestamp + server-only nonce rather than reverting to session storage.
5. Enforce CSRF defenses via application-wide middleware, not per-route, since inconsistent coverage is equivalent to no coverage on the gaps.
6. Automate client-side token attachment (proxy pattern or wrapper library) so it can't be forgotten on any individual request.

## Connects To
- **Chapter 26 (offense): Cross-Site Request Forgery**: This chapter directly defends against the link-based, image-based, and form-based CSRF attacks constructed there.
- **Chapter 41: Vulnerability Discovery**: The chapter 41 worked example (Steve/Jed's `changeSubscriptionTier` bug) is precisely the GET-based state mutation vulnerability this chapter's "stateless GET requests" rule prevents.
- **Chapter 43: Defending Against XSS Attacks**: Explicitly called out as a prerequisite risk — an XSS on an allowlisted origin defeats header-based CSRF verification, so XSS defenses and CSRF defenses are mutually reinforcing.
