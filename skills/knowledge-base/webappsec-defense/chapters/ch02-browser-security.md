# Chapter 2: Browser Security

## Core Idea
The browser sandbox and same-origin model are the client-side security layer that constrains what untrusted JavaScript can do; Content Security Policy (CSP), CORS, Subresource Integrity (SRI), and cookie attributes only provide real protection when explicitly and correctly configured — the safe defaults are not automatic.

## Frameworks Introduced
- **Content Security Policy (CSP)**: A header (preferred) or `<meta>` tag that tells the browser which origins are permitted to supply each resource type (scripts, images, styles).
  - When to use: On every web application, always — it directly limits the blast radius of any XSS that slips through escaping.
  - How: Set via `Content-Security-Policy` HTTP header (not just `<meta>`, which can't cover all response types); default to `default-src 'self'`; explicitly whitelist any third-party script origins; never include `unsafe-inline` or `unsafe-eval` unless you have no other choice and understand you're disabling the primary XSS mitigation.
- **Same-origin policy**: The browser's rule that JavaScript can only read data from, or freely interact with, another browsing context if protocol, domain, AND port all match exactly.
  - When to use: This is default, unconfigurable browser behavior — the framework matters when you're deciding whether a cross-origin interaction needs an explicit exception (CORS).
  - How: Compare the full origin tuple (protocol + domain + port) of the two resources; any mismatch (including subdomain) means no origin.
- **CORS (Cross-Origin Resource Sharing)**: Server-side opt-in headers (`Access-Control-Allow-*`) that permit specific cross-origin JavaScript reads that the same-origin policy would otherwise block.
  - When to use: Only when a legitimate cross-origin JavaScript read is required (e.g., calling a separate API domain from client-side code).
  - How: Prefer omitting CORS headers entirely (the most secure default). If needed, scope `Access-Control-Allow-Origin` to a specific trusted domain (never `*` for anything sensitive) and restrict `Access-Control-Allow-Methods` to the minimum verbs required.
- **Subresource Integrity (SRI)**: A hash of expected script content embedded in the `<script>` tag's `integrity` attribute, letting the browser refuse to execute a script whose fetched content doesn't match.
  - When to use: Whenever importing scripts from a separate domain or CDN, or any location where a MITM or compromised host could substitute malicious code.
  - How: Generate a SHA-384 hash of the script at build/deploy time, embed it as `integrity="sha384-..."`; the browser recomputes and compares the hash before execution.
- **Cookie attribute discipline (Secure + HttpOnly + SameSite + Expires/Max-Age)**: A bundle of Set-Cookie flags that together restrict where, how, and for how long a cookie can be read or transmitted.
  - When to use: On every cookie that carries session or otherwise sensitive state.
  - How: Always pair `Secure` (HTTPS-only transmission) with `HttpOnly` (no JavaScript access); set `SameSite` explicitly (don't rely on browser defaults); set `Expires` or `Max-Age` so sessions don't persist indefinitely.

## Key Concepts
- **Rendering pipeline / rendering engine**: The browser subsystem that converts HTML/CSS/media into pixels, constructing the DOM as an internal page representation.
- **JavaScript sandbox**: The isolation model preventing JS from accessing arbitrary files, other OS processes, arbitrary memory, or arbitrary network calls — implemented via per-page process isolation.
- **Origin**: The combination of protocol, domain, and port; the unit the browser uses to decide whether two resources may interact.
- **Cross-origin writes / embeds / reads**: Writes (navigating via link) are always permitted; embeds (e.g., `<img>`) are permitted subject to CSP; reads (via `fetch`/`XMLHttpRequest`) are blocked by default and require CORS.
- **WebStorage (localStorage/sessionStorage)**: Browser key-value disk storage (up to 5MB), segregated by origin, storing only inert (non-executable) text.
- **IndexedDB**: A structured, transactional client-side database API, also subject to same-origin isolation.
- **Stateful browsing via cookies**: Small (≤4KB) server-supplied text values automatically resent on every subsequent same-domain request, used to implement sessions atop stateless HTTP.
- **History isolation / fingerprinting / side-channel attacks**: Browser defenses against cross-site tracking, and the countermeasures (fingerprinting, visited-link styling leaks) advertisers use to circumvent them.

## Mental Models
- Think of the same-origin policy as a locked door between browser tabs: JavaScript in one origin simply cannot see into another, by design — CORS is a deliberate, narrow keyhole you cut into that door, not a general unlock.
- Use CSP as a second line of defense, not a substitute for escaping output: even correctly escaped HTML benefits from CSP because it constrains what an attacker can do if some other injection vector is ever missed.
- Treat "no CORS headers set" as the secure default, not an oversight to fix — only add CORS headers when a genuine cross-origin JavaScript read is required, and scope them as narrowly as the use case allows.
- Think of SRI as a tamper-evident seal on third-party or CDN-hosted script content: it doesn't stop a MITM from intercepting the request, but it stops the browser from executing what comes back if it's been altered.

## Anti-patterns
- **`unsafe-inline` in CSP**: Defeats the primary purpose of CSP, which is to prevent execution of JavaScript injected directly into HTML (the classic XSS vector); its name is a deliberate warning.
- **`Access-Control-Allow-Origin: *`**: Grants any website on the internet the ability to read the response via JavaScript; acceptable only for fully public, non-sensitive resources.
- **Missing `Secure`/`HttpOnly`/`SameSite` on session cookies**: Without `Secure`, an initial insecure HTTP request can leak the cookie to a network attacker; without `HttpOnly`, any XSS can steal it via JavaScript; without `SameSite`, cross-site requests carry the cookie, enabling CSRF.
- **Relying on link-visited styling or other side channels for history privacy**: Browsers have closed some of these leaks, but new side-channel techniques continue to emerge — don't assume history isolation is airtight by default.

## Code Examples
```javascript
// Setting a CSP as a response header (Node.js/Express) — preferred over <meta>
res.set("Content-Security-Policy", "default-src 'self'")
```
- **What it demonstrates**: The header form applies uniformly across all URLs on the app, unlike a per-page `<meta>` tag.

```javascript
// Cross-origin read requires CORS headers set on the SERVER receiving the request
fetch("http://example.com/movies.json")
  .then((response) => response.json())
  .then((data) => console.log(data))
```
```
Access-Control-Allow-Origin: https://trusted.com
Access-Control-Allow-Methods: POST, GET, OPTIONS
```
- **What it demonstrates**: A scoped CORS configuration that permits a specific trusted origin and limits which verbs are exposed cross-origin, instead of `*`.

```html
<script src="/js/application.js"
        integrity="sha384-5O3lno38vOKjoSa8HT863w10M7hKzvj+HjknFmPkOJz50htAHuPtPLj6J6lfziE">
```
- **What it demonstrates**: An SRI hash generated at build time; the browser refuses to execute the script if its fetched content doesn't hash to this value.

```
Set-Cookie: session_id=abc123; Secure; HttpOnly; SameSite=Lax; Max-Age=3600
```
- **What it demonstrates**: A cookie configured with the full recommended attribute bundle: HTTPS-only, no JS access, cross-site-request-stripped (except top-level GET navigation), and a 1-hour expiry.

## Reference Tables

| Content security policy | Interpretation |
|---|---|
| `default-src 'self'; script-src ajax.googleapis.com` | JavaScript can load from `ajax.googleapis.com`; all other resources must come from the host domain. |
| `script-src 'self' *.googleapis.com; img-src *` | JavaScript can load from `googleapis.com` or its subdomains; images from anywhere. |
| `default-src https: 'unsafe-inline'` | All resources must load over HTTPS; inline JavaScript is permitted. |
| `default-src https: 'unsafe-eval' 'unsafe-inline'` | All resources over HTTPS; inline JS permitted; JS may also `eval()` strings as code. |

| URL (relative to `https://www.example.com`) | Same origin? |
|---|---|
| `https://www.example.com/profile` | Yes — protocol, domain, port match; path differs, which is irrelevant. |
| `http://www.example.com` | No — protocol differs. |
| `https://www.example.org` | No — domain differs. |
| `https://www.example.com:8080` | No — port differs. |
| `https://blog.example.com` | No — subdomain differs. |

## Worked Example
A web app at `example.com/login` wants to (1) load its own JS, (2) embed images from a trusted CDN, (3) call a third-party chat API from client-side JS, and (4) protect a session cookie.

1. **CSP for own JS**: The team sets `Content-Security-Policy: default-src 'self'` as a response header on every page. This means only scripts served from `example.com` itself will execute; any JavaScript injected via a hypothetical XSS bug (e.g., from a comment field rendered without escaping) that tries to load `evil.com/hack.js` is blocked outright by the browser, independent of whether the escaping bug is ever fixed.
2. **CDN images**: Because the app also loads images from `cdn.example-assets.com`, the team refines the policy to `default-src 'self'; img-src 'self' cdn.example-assets.com`, keeping the script restriction untouched.
3. **Third-party chat widget**: The chat vendor's docs say to call `https://chatapi.vendor.com/token` from client-side JS via `fetch()`. Because this is a cross-origin *read* (not just an embed), the browser blocks it under the same-origin policy unless the vendor's server sends back `Access-Control-Allow-Origin: https://example.com`. The team confirms the vendor scopes this to their domain rather than returning `*`, since the response carries a session-specific access token.
4. **SRI on the chat widget's script**: The vendor also asks the app to embed `<script src="https://cdn.vendor.com/widget.js">`. Because this script is hosted on infrastructure the app doesn't control, the team adds `integrity="sha384-<hash>"` computed against the version they vetted, so that if the vendor's CDN is ever compromised or MITM'd, the browser refuses to run a modified script rather than silently executing it.
5. **Session cookie**: The login endpoint's `Set-Cookie` header is configured as `Set-Cookie: session_id=...; Secure; HttpOnly; SameSite=Lax; Max-Age=3600` — HTTPS-only, inaccessible to JavaScript (mitigating any residual XSS-based cookie theft), stripped from cross-site POST/PUT/DELETE (mitigating CSRF), and expiring in an hour.

Result: even if one layer fails (say, an escaping bug allows a script tag through), the CSP blocks execution of externally-hosted attacker scripts, SRI blocks tampered legitimate scripts, and the cookie attributes limit what a successful XSS could still steal — a concrete instance of defense in depth applied entirely within the browser layer.

## Key Takeaways
1. Set CSP as an HTTP header (not just a `<meta>` tag) and never include `unsafe-inline`/`unsafe-eval` unless truly unavoidable.
2. Default to sending no CORS headers at all; when cross-origin reads are genuinely needed, scope `Access-Control-Allow-Origin` to a specific trusted domain, never `*`, for anything sensitive.
3. Use SRI (`integrity` attribute) on any `<script>` tag pointing at a separate domain or CDN.
4. Always pair `Secure` and `HttpOnly` on cookies carrying session state; add `SameSite` explicitly rather than relying on browser defaults.
5. Set `Expires`/`Max-Age` on sensitive cookies deliberately — omitting them can leave a cookie active indefinitely.
6. WebStorage and IndexedDB are already same-origin-isolated by the browser, but they store plaintext, inert data — don't put anything there you wouldn't put in an unencrypted cookie.
7. Cross-site tracking countermeasures (history isolation) are incomplete; fingerprinting and side-channel attacks are an ongoing arms race, not a solved problem.

## Connects To
- **Ch 3**: `Secure` cookies depend on HTTPS being correctly configured, which is the subject of the Encryption chapter (redirects, HSTS).
- **Ch 6**: This chapter's brief mention of XSS and CSRF is expanded into full attack walkthroughs (stored/reflected/DOM XSS, CSRF, anti-CSRF tokens, clickjacking, XSSI) using these same CSP/cookie/CORS primitives as defenses.
- **Ch 7**: Cookie `domain` attribute and subdomain cookie-sharing concerns, only flagged here, are covered in depth alongside subdomain squatting.
