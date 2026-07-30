# Chapter 20: API Analysis

## Core Idea
After finding subdomains, the next recon step is mapping each subdomain's API endpoints — the HTTP verbs they accept, their authentication scheme, and their expected payload shape — since this determines both an endpoint's purpose and how it can be exploited.

## Frameworks Introduced
- **REST verb discovery via hypothesis testing**: Once you observe one verb working against a resource URL, systematically test the other CRUD-mapped verbs against the same URL to discover undocumented functionality.
  - When to use: Any time a single HTTP request (e.g., `GET /users/1234`) is observed and the API appears RESTful.
  - How: Try `OPTIONS` first (cheap, sometimes discloses `Allow:` header directly); if unavailable, fire `POST`/`GET`/`PUT`/`PATCH`/`DELETE` against the same URL asynchronously and record which return a real status code vs. timeout, always with explicit permission since verb brute-forcing can mutate or delete data.
- **Payload shape discovery**: Determine the exact fields/types an endpoint expects by combining known public specs (OAuth), observed working requests, and error-message analysis.
  - When to use: After an endpoint's existence and verb are confirmed, before attempting exploitation.
  - How: Check if the endpoint matches a public spec (OAuth 2.0, standard auth flows) first; otherwise send a plausible payload and read error messages for hints (e.g., "auth_token not supplied"); narrow the "solutions space" using any known constraints (field length, charset) before brute-forcing values.

## Key Concepts
- **Solutions space**: The full set of possible values for a given field; the goal of payload-shape recon is to shrink this space to the smallest viable search space before attempting brute force.
- **OPTIONS method**: An HTTP verb whose sole purpose is to report which verbs an endpoint supports (via the `Allow:` response header) — rarely exposed on non-public enterprise APIs, but a free first check.
- **HTTP Basic Authentication fingerprint**: An `Authorization: Basic <base64>` header, decodable in-browser via `atob()`, revealing a plaintext `username:password` pair sent on every request.
- **Application-specific vs. common shapes**: Common shapes (OAuth 2.0 authorization requests) can be inferred from public specs; application-specific shapes require trial, error, and error-message analysis.
- **Error-message leakage**: Verbose validation errors (e.g., "publicProfile only accepts 'auth' and 'noAuth' as params") can hand an attacker the exact schema of a field without any brute forcing.
- **Stateless token propagation**: A REST API sending a bearer/auth token on every request (rather than server-side session state) is itself a signal of RESTful, stateless design.

## Mental Models
- Think of an unknown endpoint the way you'd think of a locked door with a visible hinge: if `GET /users/1234` works, the "hinge" (resource pattern) suggests `PUT`, `PATCH`, and `DELETE` variants exist on the same URL — test the hypothesis rather than assuming.
- Use error verbosity as a maturity signal: an API that returns a generic 400/401 for every bad request is more mature/secure than one that names the missing field or invalid value.
- Treat public-spec compliance (OAuth 2.0) as a recon shortcut: if an endpoint looks like a standard flow, don't reverse-engineer from scratch — check the spec (Discord, Facebook docs) for the expected shape first.

## Anti-patterns
- **Brute-forcing verbs without permission**: `PUT`/`DELETE` attempts can mutate or destroy real application data; never attempt verb discovery against an API without explicit authorization.
- **Verbose validation errors in production**: Returning field-specific error messages ("X only accepts Y") hands attackers the schema for free — return generic errors instead.
- **Assuming `OPTIONS` will be available**: Very few enterprise APIs expose it; treat it as a quick free check, not a reliable discovery method.
- **Ignoring authentication headers when an endpoint "does nothing"**: An endpoint returning empty/generic results with no auth attached may simply require an `Authorization` header to reveal real behavior.

## Code Examples
```javascript
// Given a URL known to accept at least one HTTP verb, discover
// which other verbs are also mapped to the same endpoint.
const discoverHTTPVerbs = function (url) {
  const verbs = ['POST', 'GET', 'PUT', 'PATCH', 'DELETE'];
  const promises = [];

  verbs.forEach((verb) => {
    const promise = new Promise((resolve, reject) => {
      const http = new XMLHttpRequest();
      http.open(verb, url, true);
      http.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');

      http.onreadystatechange = function () {
        if (http.readyState === 4) {
          return resolve({ verb: verb, status: http.status });
        }
      };
      // Treat non-response within 1s as "verb not mapped"
      setTimeout(() => {
        return resolve({ verb: verb, status: -1 });
      }, 1000);

      http.send({});
    });
    promises.push(promise);
  });

  Promise.all(promises).then(function (values) {
    console.log(values);
  });
};
```
- **What it demonstrates**: Async, timeout-bounded verb discovery — each verb is fired in parallel via `XMLHttpRequest`, with a 1-second timeout treated as "no valid endpoint mapping," and results collected once every promise resolves.

```javascript
// Decoding an HTTP Basic Auth header observed in the browser console
// Authorization: Basic am9lOjEyMzQ=
atob('am9lOjEyMzQ='); // "joe:1234"
```
- **What it demonstrates**: A one-line fingerprint check — the `Basic` scheme plus a decodable base64 string confirms HTTP Basic Authentication, and reveals the actual credential format in transit.

## Reference Tables
HTTP verbs mapped to REST/CRUD semantics (Table 5-1):

| REST HTTP Verb | Usage |
|---|---|
| POST | Create |
| GET | Read |
| PUT | Update/replace |
| PATCH | Update/modify |
| DELETE | Delete |

Major authentication schemes and their trade-offs (Table 5-2):

| Authentication scheme | Implementation details | Strengths | Weaknesses |
|---|---|---|---|
| HTTP Basic Auth | Username and password sent on each request | Natively supported by all major browsers | Session does not expire; easy to intercept |
| HTTP Digest Auth | Hashed username:realm:password sent each request | Harder to intercept; server can reject expired tokens | Encryption strength depends on the hashing algorithm used |
| OAuth | Bearer token-based; allows sign-in via other sites | Tokenized permissions shareable across integrations | Phishing risk; one compromised central site compromises all connected apps |

## Worked Example
The chapter walks through analyzing `api.mega-bank.com/users/1234`:

1. **Confirm REST shape**: Observed traffic shows `GET /users/1234` and `GET/POST /users/1234/payments`, hierarchical and resource-targeted — a RESTful signature. A `Bearer` token on every request confirms statelessness.
2. **Try `OPTIONS` first**: `curl -i -X OPTIONS https://api.mega-bank.com/users/1234` — if it returns `200 OK` with `Allow: HEAD, GET, PUT, DELETE, OPTIONS`, verb discovery is solved instantly. (Rare on non-public APIs.)
3. **Fall back to verb brute force** (with permission): Run `discoverHTTPVerbs()` against `/users/1234`, discovering, say, that `PUT` and `DELETE` are also mapped even though the UI only ever issues `GET`.
4. **Determine auth scheme**: After logging in via the UI, the tester observes `Authorization: Basic am9lOjEyMzQ=` on the follow-up `/homepage` request; `atob()` reveals `joe:1234`, confirming HTTP Basic Auth over what must be a TLS-protected connection (otherwise credentials would be trivially interceptable).
5. **Determine payload shape**: For a non-standard endpoint like `POST /users/config`, the tester sends a guessed payload `{ "user_id": 12345, "privacy": { "publicProfile": true } }`; a `400` error message "auth_token not supplied" reveals a missing required field. Adding a valid token yields a further error: "publicProfile only accepts 'auth' and 'noAuth' as params" — now the tester knows the exact enum accepted by that field.
6. **Outcome**: The tester has now fully documented an endpoint's verb set, auth scheme, and payload schema — ready to add to the recon map and prioritize for exploitation.

## Key Takeaways
1. Once one verb is confirmed on a resource URL, systematically test the other CRUD-mapped verbs — but only with explicit permission, since brute forcing can mutate or delete real data.
2. Try `OPTIONS` first as a free, if unreliable, verb-discovery shortcut.
3. Recognize and decode common auth schemes (Basic/Digest/OAuth) directly from headers using browser built-ins like `atob()`.
4. Verbose error messages are a schema-discovery goldmine for attackers — treat generic error responses as a security requirement, not a UX nicety.
5. Narrow the "solutions space" using any learnable constraint (length, charset, enum) before attempting to brute force a field's value.
6. Check public specs (OAuth 2.0) before reverse-engineering a payload shape from scratch — many "custom" auth flows are actually standard.

## Connects To
- **Ch19 (global)**: API Analysis is the direct next step after subdomain discovery — each subdomain found there is analyzed here for its endpoint/verb/shape structure.
- **Ch21 (global)**: Once endpoints and their auth are known, Identifying Third-Party Dependencies uses similar fingerprinting logic (headers, error messages) to determine underlying frameworks and databases.
- **Ch24-34 (Offense, global)**: Discovered payload shapes and verbs are the direct target list for injection, business-logic, and auth-bypass attacks covered later.
- **Ch35-52 (Defense, global)**: Generic error messages and centralized authorization (rather than per-endpoint reimplementation) are defensive countermeasures directly implied by this chapter's findings.
