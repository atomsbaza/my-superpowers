# Chapter 37: Secure Application Configuration

## Core Idea
Browsers ship a large set of built-in security mechanisms — CSP, CORS/SOP, HSTS, COOP, CORP, cookie attributes, and multiple sandboxing techniques — that only protect an application if they are explicitly and correctly configured; running with none of them (or with legacy/weak settings) leaves the browser's default protections effectively disabled.

## Frameworks Introduced
- **Strict CSP (nonce-based or hash-based)**: A method of allowing inline scripts securely without opening the door to arbitrary inline-script XSS.
  - When to use: Nonce-based when every page is server-rendered (a fresh nonce per load); hash-based when pages are cached/CDN-served (nonces can't rotate reliably behind a cache).
  - How: Set `script-src 'nonce-{RANDOM}' 'strict-dynamic'` and stamp matching `nonce="..."` attributes on legitimate inline `<script>` tags; or precompute SHA-256 hashes of each legitimate inline script and list them in `script-src`. The browser refuses to execute any script whose nonce/hash doesn't match.
- **CORS Simple vs. Preflight decision**: WHATWG's two-tier check for cross-origin requests.
  - When to use: Simple-request rules apply automatically to GET/HEAD/POST requests meeting strict header/content-type constraints; anything else (state-changing, custom headers, non-form content types) triggers a preflight `OPTIONS` check automatically — this isn't a manual choice, but understanding which tier a request falls into explains observed CORS errors.
  - How: For simple requests, the browser sends `Origin: <source-origin>` and expects `Access-Control-Allow-Origin: <source-origin>` back with 200; anything not qualifying as simple gets an `OPTIONS` preflight carrying `origin`, `access-control-request-method`, and `access-control-request-headers`, all of which the server must echo/approve before the real request is sent.
- **Four-Tier Sandboxing Ranking**: A prioritized list of options for running third-party code safely inside your page.
  - When to use: Whenever your application must embed or execute code you did not write (partner integrations, user-generated widgets, ad content).
  - How: Prefer, in order: (1) `<iframe>` (browser-vendor-funded isolation, but heavy/awkward UI integration), (2) Web Workers (isolated JS thread, no DOM access, but can still make cross-origin HTTP requests), (3) Subresource Integrity (verifies third-party code hasn't been tampered with, not an isolation mechanism per se), (4) Shadow Realms (emerging TC39 stage 3/4 proposal, synchronous execution, lighter weight than iframes but not yet universally supported).

## Key Concepts
- **CSP (Content Security Policy, W3C)**: A header/meta-tag-driven allowlist mechanism that mitigates XSS, data injection, phishing, framing, and redirect attacks by restricting which sources scripts/styles/images/etc. may load from.
- **CORS / SOP (WHATWG)**: Same Origin Policy is the browser default restricting cross-origin `fetch`/`XMLHttpRequest` calls; CORS is the opt-in mechanism for relaxing SOP for specific origins.
- **HSTS (HTTP Strict Transport Security)**: A header forcing all future requests to a domain (and optionally its subdomains) to upgrade to HTTPS, avoiding the vulnerable initial-HTTP-then-301-redirect pattern.
- **COOP (Cross-Origin-Opener-Policy)**: Controls whether a page shares its "browsing context" (tab/window/iframe relationships) with the page that opened it, preventing cross-context navigation-based information leakage.
- **CORP (Cross-Origin-Resource-Policy)**: A 2018-era mitigation for Spectre-style side-channel timing attacks, restricting which origins may read a given resource at the browser's lower memory-sharing level.
- **SRI (Subresource Integrity)**: A base64 SHA-256/384/512 hash attached to a `<script>`/`<link>` tag that lets the browser refuse to load third-party code that has been modified since the hash was generated.
- **Shadow Realms (TC39)**: An upcoming JavaScript language feature creating an isolated execution context (own globals/intrinsics) without the overhead and asynchrony of an iframe.
- **SameSite cookie attribute**: Controls whether a cookie is sent with cross-site requests (`Strict`, `Lax`, or `None`); `Strict` is the primary CSRF mitigation at the cookie level.

## Mental Models
- Think of CSP as an allowlist for *what the page is permitted to load and execute*, and CORS/SOP as an allowlist for *what the page is permitted to call out to* — they solve adjacent but distinct problems and are commonly confused.
- Use the sandboxing ranking as a cost/isolation trade-off ladder: iframe buys the most isolation (funded by browser vendors) at the highest UI/dev cost; Shadow Realms buys convenience and synchronous execution at the cost of being a not-yet-universal proposal.
- Treat every legacy security header (X-Frame-Options, X-XSS-Protection, Expect-CT) as a signal to check whether a modern CSP directive or default browser behavior has already superseded it — don't configure both redundantly or, worse, only the legacy one.
- Treat the cookie `domain` attribute as a footgun: adding it (even to scope things down) silently widens the effective cookie scope from `my-domain.com` to `*.my-domain.com`, the opposite of the intended tightening in most cases.

## Anti-patterns
- **Shipping with no CSP at all**: A fully functioning site can run with zero CSP policy, which means zero browser-enforced mitigation against XSS, injection, phishing, framing, or redirect attacks.
- **Wildcard CORS (`*`) instead of an explicit allowlist**: Violates least privilege by granting cross-origin access to every origin rather than the specific ones the application needs.
- **Adding the cookie `domain` attribute "just in case"**: Unexpectedly extends cookie transmission to all subdomains, enabling account-takeover risk if any subdomain runs user-controlled script.
- **Using deprecated CSP headers** (`X-Content-Security-Policy`, `X-Webkit-CSP`): No longer implement CSP in modern browsers; only the `Content-Security-Policy` header/meta tag should be used.
- **Relying on `X-XSS-Protection` or `Expect-CT`**: Both are effectively dead — modern browsers no longer scan for reflected XSS this way, and CT is enforced by default on all TLS certs issued after May 2018.

## Code Examples
```
Content-Security-Policy default-src: 'self'; script-src: 'self' 'nonce-jgoj23j2o3j2oij26jk2nkn26kjh23' 'strict-dynamic'; frame-ancestors: 'none'; img-src: data: https:; report-uri: https://reporting.megabank.com
```
- **What it demonstrates**: A secure-by-default starter CSP combining nonce-based strict CSP for scripts, clickjacking prevention (`frame-ancestors: 'none'`), HTTPS-only images with base64 allowed, and a violation-reporting endpoint.

```
Strict-Transport-Security: max-age=<expire-time>; includeSubDomains; preload
```
- **What it demonstrates**: HSTS syntax forcing HTTPS upgrade for the origin and (optionally) all subdomains, with an optional preload-list opt-in.

```
Set-Cookie: auth_token=abc123; Secure; HttpOnly; SameSite=Strict
```
- **What it demonstrates**: A cookie hardened against MITM theft (`Secure`), JavaScript/XSS exfiltration (`HttpOnly`), and cross-site request forgery (`SameSite=Strict`).

```
Cross-Origin-Opener-Policy: same-origin
Cross-Origin-Resource-Policy: same-origin
X-Content-Type-Options: nosniff
```
- **What it demonstrates**: Three independent header-level hardenings — browsing-context isolation (COOP), Spectre-style cross-origin memory-read restriction (CORP), and MIME-sniffing prevention.

```js
const express = require('express');
const app = express();
const cors = require('cors');
const corsOptions = { origin: 'https://mega-bank.com' };
app.get('/users/:id', cors(corsOptions), function (req, res, next) {
  res.sendStatus(200);
});
app.listen(443, function () { console.log('listening on port 443') });
```
- **What it demonstrates**: Server-side CORS configuration allowlisting a single origin via Express's `cors` middleware, rather than wildcarding.

```html
<iframe src="https://other-website.com" sandbox></iframe>
```
- **What it demonstrates**: A hardened iframe using the `sandbox` attribute to force separate-origin treatment, block form submission/script execution/plugin use/autoplay, and prevent parent-context access.

```js
if (window.Worker) {
  const myWorker = new Worker('code.js');
  myWorker.terminate();
}
```
- **What it demonstrates**: Creating and tearing down a Web Worker as a lighter-weight (but less isolated than an iframe) sandboxing mechanism.

```html
<script src="other-website.com/stuff.js" integrity="sha384-NmJhYmViMzNiMmU1NzllMDMyODdl" crossorigin="anonymous"></script>
```
- **What it demonstrates**: Subresource Integrity verifying third-party script content hasn't changed since the hash was generated.

## Reference Tables
| Legacy header | Modern equivalent |
|---|---|
| X-Frame-Options | CSP `frame-ancestors` |
| X-XSS-Protection | Removed — CSP blocks common XSS sinks by default |
| Expect-CT | Removed — CT enforced by default on all certs issued after May 2018 |
| Referrer-Policy | Still relevant for legacy browsers: `Referrer-Policy: strict-origin-when-cross-origin` |
| X-Powered-By | Disable — enables server fingerprinting |
| X-Download-Options | IE-only; generally unneeded (deprecated browser) |

| Sandboxing method | Isolation level | Key limitation |
|---|---|---|
| Traditional iframe | Highest (browser-vendor-funded) | Heavy UI/CSS duplication; async-only `postMessage` communication |
| Web Workers | Medium (separate thread, no DOM) | Can still make cross-origin HTTP requests |
| Subresource Integrity | N/A (integrity, not isolation) | Only verifies unmodified content, doesn't sandbox execution |
| Shadow Realms | Medium-high (own globals/intrinsics) | Stage 3/4 TC39 proposal, not yet universally shipped |

## Worked Example
The chapter's running example is hardening mega-bank.com end to end. Content-Security-Policy is set with `default-src 'self'`, a nonce-based `script-src` plus `strict-dynamic` so legitimate inline scripts (tagged with the matching `nonce` attribute) execute while any injected script without the correct nonce is blocked; `frame-ancestors 'none'` prevents any other site from framing mega-bank.com for clickjacking; `img-src data: https:` allows base64 images and HTTPS-loaded images only; and `report-uri` sends CSP violation reports to a monitoring endpoint. Separately, CORS is configured server-side with the Express `cors` middleware scoped to the single legitimate partner origin (`https://mega-bank.com`) rather than a wildcard, so a `fetch` from an unrelated origin fails the preflight/simple-request check and the browser refuses to hand the response to the calling script. On the cookie layer, the session cookie is issued as `Set-Cookie: auth_token=abc123; Secure; HttpOnly; SameSite=Strict` so it is never sent over plain HTTP, never readable by injected JavaScript even under a successful XSS, and never attached to a cross-site request. Finally, if mega-bank.com needs to embed a partner's JavaScript widget, the chapter walks through the sandboxing ladder: first try an `<iframe sandbox>` for maximum isolation; if UI constraints make iframes impractical, fall back to a Web Worker for isolated (but DOM-less) execution; and regardless of embedding method, attach a Subresource Integrity hash to any third-party `<script src>` tag so a tampered file is refused at load time.

## Key Takeaways
1. Always ship an explicit CSP — running with none disables an entire category of browser-side attack mitigation.
2. Use nonce-based strict CSP for server-rendered pages and hash-based strict CSP for CDN-cached pages, to allow inline scripts securely.
3. Configure CORS with an explicit origin allowlist, never a wildcard, following least privilege.
4. Force HTTPS everywhere with HSTS (`max-age`, `includeSubDomains`, `preload`) rather than relying on HTTP-to-HTTPS redirects.
5. Harden every cookie with `Secure`, `HttpOnly`, and `SameSite=Strict`, and avoid the `domain` attribute unless subdomain sharing is truly required.
6. Add COOP and CORP headers to mitigate cross-context leakage and Spectre-style side-channel reads.
7. Rank third-party code isolation options by need: iframe first, Web Workers next, SRI for integrity verification, Shadow Realms as an emerging lightweight option.
8. Retire legacy headers (X-XSS-Protection, Expect-CT) and replace X-Frame-Options with CSP's `frame-ancestors`.

## Connects To
- **Chapter 36 (Secure Application Architecture)**: This chapter operationalizes the TLS/data-in-transit requirement established there into concrete HSTS and cookie `Secure` syntax.
- **Chapter 38 (Secure User Experience)**: Both chapters address browser-facing risk; CSP/CORS/cookie hardening here prevents the technical exploitation paths that Chapter 38's UX-layer mitigations (generic errors, rate limiting) address at the information-disclosure layer.
- **XSS/CSRF chapters (offense, earlier in the book)**: The CSP, SOP/CORS, and SameSite mechanisms here are the direct defensive countermeasures to the XSS and CSRF attack techniques covered in the book's offense section.
