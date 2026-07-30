# Chapter 26: Cross-Site Request Forgery

## Core Idea
CSRF exploits the browser's trust that any request originating from a logged-in user's browser is authorized by that user, letting an attacker craft a link, image, form, or auto-submitting script that makes a privileged, authenticated request (e.g., a bank transfer) on the victim's behalf without their knowledge.

## Frameworks Introduced
- **The two defining traits of a CSRF attack**: privilege escalation, and the user account that initiates the request typically does not know it occurred (it is a stealthy attack).
  - When to use: as a triage checklist — if a vulnerability doesn't escalate privilege or requires the victim to knowingly cooperate, it isn't really CSRF.
  - How: confirm the target endpoint performs a state change under the victim's authenticated session, and confirm the victim has no visible indication the request was sent.
- **CSRF GET param-tampering attack flow**: hacker finds a GET endpoint that changes state via query params, crafts a URL embedding malicious params, then distributes it.
  - When to use: whenever a CRUD/state-changing operation (e.g., `/transfer`) is reachable via HTTP GET.
  - How: (1) find the GET endpoint and its param names; (2) craft `<a href="https://www.megabank.com/transfer?to_user=<hacker's account>&amount=10000">click me</a>`; (3) pick a distribution strategy — targeted (highest chance of being logged in with sufficient funds) or bulk (hit as many victims as possible before detection), often via email, social media, or even paid web-ad campaigns.

## Key Concepts
- **Token Pools**: a legacy CSRF defense that validates tokens against a shared pool rather than tying a token to the specific user/session/action, so a token generated from the attacker's own account is accepted when replayed in an attack against another user.
- **Weak Tokens**: CSRF tokens generated predictably (dates, times, usernames, sequential integers, or raw Unix epoch timestamps) that an attacker can forge without ever stealing a real one.
- **Header Validation bypass**: defenses that check Referer/Origin headers can be defeated by causing the browser to omit those headers entirely, e.g., via `rel="noreferrer"` on `<a>`/`<form>` tags.
- **Content Type bypass**: if the server only validates CSRF tokens for one content type (e.g., `application/json`), submitting the payload as `application/x-www-form-urlencoded` or `multipart/form-data` may skip validation entirely.
- **Regex Filter Bypass**: alternate but equivalent URL syntax (`;` instead of `?` for query params, `\` instead of `/` for path separators, `../` relative-path tricks) can slip past a naive regex-based CSRF/URL validator.
- **Iframe Payload**: an `<iframe src="...">` loads and fires its request with zero user interaction, but only works against GET endpoints.
- **AJAX Payload**: a CSRF request fired via `XMLHttpRequest` from injected JavaScript — normally requires an XSS vulnerability or a customization feature that allows script execution.
- **Zero Interaction Form**: a hidden `<form>` whose fields are populated and submitted entirely via JavaScript DOM APIs (`el.submit()`), removing the need for the victim to click anything, typically delivered via XSS.

## Mental Models
- Think of every HTTP GET-triggering HTML tag (`<a>`, `<img>`, `<video>`, `<iframe>`) as a potential zero-click CSRF delivery vector — anything with a `src`/`href` fires a GET the instant it loads into the DOM.
- Use POST-based CSRF (a submitted `<form>`) when the target endpoint requires POST/PUT/DELETE — it costs the attacker some user interaction but is still automatable via a disguised fake-login form or JavaScript auto-submit.
- Treat header-based, token-pool, and regex-based CSRF defenses as forgeable-by-default: any request from the browser can be forged with Burp, ZAP, or curl, so bypass testing should try header removal, content-type swaps, and regex evasion in turn rather than assuming one validator style covers all cases.

## Anti-patterns
- **State-changing operations on GET requests**: GET is the easiest HTTP verb to weaponize via `<a>`, `<img>`, or `<video>` tags because it requires no scripting and often no user awareness at all.
- **Header-only validation (Referer/Origin only)**: trivially defeated by `rel="noreferrer"`, which causes the browser to omit the header the server relies on.
- **Token-pool validation (accepting any valid token, not tying it to the specific user/session/action)**: lets an attacker generate a legitimate token from their own account and reuse it inside an attack against a different victim.
- **Predictable/weak CSRF tokens (timestamps, sequential IDs, usernames)**: an attacker who identifies the generation scheme (e.g., Unix epoch seconds) can forge a currently-valid token without ever observing a real one.

## Code Examples
```html
<!-- GET CSRF via image tag: fires on page load, zero interaction, invisible (0x0 px) -->
<img src="https://www.mega-bank.com/transfer?to_user=<hacker's account>&amount=10000" width="0" height="0" border="0">

<!-- GET CSRF via plain hyperlink -->
<a href="https://www.megabank.com/transfer?to_user=<hacker's account>&amount=10000">click me</a>

<!-- POST CSRF via hidden form -->
<form action="https://www.mega-bank.com/transfer" method="POST">
  <input type="hidden" name="to_user" value="hacker">
  <input type="hidden" name="amount" value="10000">
  <input type="submit" value="Submit">
</form>

<!-- POST CSRF disguised as a legitimate login form -->
<form action="https://www.mega-bank.com/transfer" method="POST">
  <input type="hidden" name="to_user" value="hacker">
  <input type="hidden" name="amount" value="10000">
  <input type="text" name="username" value="username">
  <input type="password" name="password" value="password">
  <input type="submit" value="Submit">
</form>

<!-- Iframe payload: GET-only, zero interaction -->
<iframe src="https://example.com/change_password?password=123"></iframe>

<!-- Zero-interaction auto-submitting form via JavaScript DOM API -->
<form id="pw_form" method="GET" action="https://example.com/change_password">
  <input id="pw" type="hidden" name="password" value="" />
  <input type="submit" value="submit"/>
</form>
<script>
  const el = document.querySelector("#el")
  const pw = document.querySelector("#pw")
  pw.val = "new_password_123"
  el.submit()
</script>
```
- **What it demonstrates**: the escalating stealth ladder of CSRF delivery — visible link, invisible image tag, disguised POST form, GET-only iframe, and a fully scripted zero-click form submission.

## Reference Tables
| Bypass Category | Description / Example |
|---|---|
| Header Validation | Strip Referer/Origin via `rel="noreferrer"` on `<a>`/`<form>` so the server reads null/undefined during validation. |
| Token Pools | Steal a valid token from your own account (e.g., via curl: `curl https://website.com/auth -H "anti-csrf-token": "12345abc"`) and replay it — pool-based validators don't tie tokens to a specific user/session/action. |
| Weak Tokens | Tokens like `1691434927`, `1691434928` are Unix epoch timestamps; forge a token matching the current time (e.g., `1691438676` for 08/07/2023 8:04:36 PM). |
| Content Types | Switch from the validated content type (e.g., `application/json`) to one the server doesn't check — candidates include `application/x-7z-compressed`, `application/zip`, `application/xml`, `application/xhtml+xml`, `application/rtf`, `application/pdf`, `application/ld+json`, `application/gzip`, `text/csv`, `text/css`; for forms, edit the `enctype` attribute (e.g. `multipart/form-data`) via dev tools. |
| Regex Filter Bypasses | `;` instead of `?` (`https://example.com;test=123`); `\` instead of `/` in paths; relative-path tricks like `https://example.com/../test`. |
| Iframe Payloads | `<iframe src="...">` auto-fires a GET with zero interaction; GET endpoints only. |
| AJAX Payloads | `XMLHttpRequest` fired from injected JS; needs script execution (customization feature or XSS). |
| Zero Interaction Forms | JS DOM API (`el.submit()`) populates and submits a hidden form with no click required; typically delivered via XSS. |

## Worked Example
MegaBank exposes `/transfer` as a GET route: it checks `session.isAuthenticated`, requires `req.query.to_user` and `req.query.amount`, then calls `transferFunds(session.currentUser, req.query.to_user, req.query.amount, ...)`. Because authentication is verified but the *source* of the request is not, the route implicitly trusts that an authenticated request is intentional. The attacker crafts `<a href="https://www.megabank.com/transfer?to_user=<hacker's account>&amount=10000">click me</a>` and distributes it by email or social media (targeted at users likely logged in with sufficient funds, or bulk-blasted before detection). Any authenticated MegaBank user who clicks the link has their browser fire the GET with their session cookie attached, and `transferFunds` executes as if the victim initiated it — silently, since the response is just a JSON reflection the victim likely never sees.

## Key Takeaways
1. Any state-changing operation reachable by HTTP GET is CSRF-vulnerable by default — GET requests carry session cookies automatically and can be triggered by an `<a>`, `<img>`, `<video>`, or `<iframe>` tag with zero scripting.
2. POST/PUT/DELETE endpoints aren't safe by default either — a hidden or disguised `<form>` (fake login page) still forces a one-click or auto-submitted state change.
3. Don't trust Referer/Origin headers as a primary defense — `rel="noreferrer"` strips them trivially, and any header can be forged with Burp/ZAP/curl.
4. CSRF tokens must be unique per user/session/action and unpredictable — pool-validated tokens and timestamp-derived tokens are both forgeable.
5. Validate content type strictly and don't assume regex-based URL/param filters cover encoding variants (`;` vs `?`, `\` vs `/`, `../`).
6. When script execution or XSS is present, CSRF stops needing any user interaction at all (AJAX payloads, auto-submitting DOM forms) — XSS and CSRF compound each other.

## Connects To
- **Defending Against CSRF chapter**: this attack chapter's countermeasures (proper per-action anti-CSRF tokens, SameSite cookies, double-submit patterns) are covered in the later "Defending Against CSRF" chapter.
- **Same-Origin Policy**: the browser security boundary CSRF sidesteps — SOP restricts script-level cross-origin *reads*, but does not by itself prevent cross-origin *writes* triggered by tags/forms.
- **SameSite cookies**: a cookie attribute (`Strict`/`Lax`/`None`) that constrains when cookies are sent on cross-site requests, directly mitigating the GET/POST delivery vectors shown here.
- **XSS (Cross-Site Scripting)**: AJAX and zero-interaction form payloads both assume script execution is already possible, usually via an XSS vulnerability on the target site.
