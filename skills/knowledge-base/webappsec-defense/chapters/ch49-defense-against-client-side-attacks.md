# Chapter 49: Defense Against Client-Side Attacks

## Core Idea
Client-side attacks (prototype pollution, clickjacking, tabnabbing) are hard to detect but comparatively cheap to mitigate: a small set of configuration changes and language-level features — CSP `frame-ancestors`, `Object.freeze()`/`Object.create(null)`, `noopener`/`noreferrer`, COOP, and fetch metadata headers — close most of the attack surface with minimal ongoing effort.

## Frameworks Introduced
- **Key Sanitization (prototype pollution)**: Allowlist object keys before merging user-controlled data into an object.
  - When to use: Any code path that merges or assigns user-supplied keys into an object, where the set of legitimate keys is known and static.
  - How: Maintain an `allowedKeys` array; iterate incoming data's keys and reject the whole update if any key isn't on the list. Not usable when the application must accept flexible, non-static user input.
- **Prototype Freezing**: Make an object immutable for the rest of the browsing session using `Object.freeze()`.
  - When to use: On specific, well-understood objects (e.g., `userData`) that don't need further mutation — not as a bulk/looped freeze across many objects.
  - How: Call `Object.freeze(userData)`; the object becomes immutable until the page reloads. Avoid bulk-freezing built-in DOM/JS APIs, since many depend on mutability of other objects and will break.
- **Null Prototypes**: Cut off an object's prototype chain entirely at creation time.
  - When to use: When an object is expected to handle untrusted keys later in its lifecycle and pollution risk via inherited prototype lookup must be eliminated at the source.
  - How: Create the object via `Object.create(null)` instead of an object literal; it has no prototype (`Object.getPrototypeOf()` returns `null`), so there is no chain to walk or pollute.
- **Frame Ancestors CSP Directive**: The primary, browser-native clickjacking defense, replacing the obsolete `X-Frame-Options` header.
  - When to use: Any site that does not need to be embedded elsewhere (default: `'none'`), or needs to allow only specific, trusted embedding origins.
  - How: Set `Content-Security-Policy: frame-ancestors 'none';` to block all framing (stops ~95%+ of clickjacking attempts, per current browser support); loosen to specific origins (e.g., `subdomain.my-website.com`) or `self` only if a legitimate framing use case exists.
- **Framebusting (fallback)**: A JavaScript+CSS technique for browsers/use-cases where CSP `frame-ancestors` isn't viable.
  - When to use: Legacy browser support gaps, or rare cases where CSP framing rules can't be applied.
  - How: Set `html { display: none; }` in a `<head>`-loaded stylesheet so content is invisible/non-interactive by default; in the body, run a script comparing `self == top` — if true (not framed), flip `display` to `block`. Avoid legacy framebuster variants that let content render before the check runs, since that leaves a clickjackable window.
- **Cross-Origin-Opener Policy (COOP) + Link Blockers**: Combined defense against tabnabbing.
  - When to use: Any application generating dynamic outbound links or opening new tabs/windows.
  - How: Set `Cross-Origin-Opener-Policy: same-origin` by default (relax only for legitimate multi-domain setups); add `rel="noopener noreferrer"` to dynamically generated `<a>` links so `window.opener` is nulled out and referrer data is withheld.
- **Isolation Policies / Fetch Metadata**: Use browser-sent request-context headers to build server-side, defense-in-depth mitigations.
  - When to use: As an additional layer alongside CSP/COOP — currently only supported on recent Chrome/Firefox, not Safari or most international browsers, so treat as supplementary, not primary.
  - How: Inspect `Sec-Fetch-Site` (same-origin/same-site/cross-site/none), `Sec-Fetch-Mode` (same-origin/no-cors/cors/navigate), `Sec-Fetch-Dest` (frame, script, style, etc.), and `Sec-Fetch-User` (1/null) on the server; reject requests whose context doesn't match the expected use (e.g., reject `Sec-Fetch-Dest: frame` to block framing attempts server-side).

## Key Concepts
- **Key sanitization**: Validating/allowlisting object keys prior to merge/assignment to prevent prototype-chain keys like `__proto__` from propagating.
- **Object.freeze()**: A built-in JS function that makes an object immutable for the remainder of the browsing session (reset on page reload).
- **Object.create(null)**: Constructs an object with no prototype at all, immune to prototype-chain pollution because there is no chain.
- **frame-ancestors**: A CSP directive controlling which origins (if any) may embed the page in a frame/iframe; the modern replacement for `X-Frame-Options`.
- **Framebuster / framekiller script**: JS+CSS that hides page content by default and only reveals it once confirmed the page is not being framed (`self == top`).
- **COOP (Cross-Origin-Opener-Policy)**: A header controlling whether a window opened via a link retains a reference back to its opener's origin.
- **noopener / noreferrer**: Link `rel` attributes that null out `window.opener` (`noopener`) and suppress referrer data (`noreferrer`) on links a page generates.
- **Fetch metadata / isolation policies**: A set of `Sec-Fetch-*` request headers browsers send, giving the server context about where/how/why a request was made, usable to build custom request-context-based mitigations.

## Mental Models
- Use CSP `frame-ancestors` as your default lock on the front door; treat framebusting scripts as the spare key you only need for the rare visitor whose browser doesn't recognize the lock.
- Think of `noopener`/`noreferrer` links as cutting the phone line between two rooms before a stranger walks into one of them — without it, either room can call the other and redirect its occupants.
- Treat `Object.freeze()` like sealing a single labeled box, not shrink-wrapping the whole warehouse — freeze specific known-safe objects; bulk/looped freezing across the prototype chain breaks APIs that depend on mutability elsewhere.
- Treat fetch metadata / isolation policies as a defense-in-depth layer, not a primary control, given its current browser support gap (missing on Safari and most international browsers) — always pair it with CSP/COOP, never rely on it alone.

## Anti-patterns
- **Relying on `X-Frame-Options` for clickjacking defense**: Considered obsolete by most major browsers; CSP `frame-ancestors` is the effective modern replacement.
- **Bulk or looped `Object.freeze()` calls down a prototype chain**: Freezing built-in DOM/JS APIs (even accidentally) breaks large swaths of application functionality that depends on their mutability.
- **Using legacy framebuster scripts that let the page render before the top-check runs**: Leaves a window of clickjackable interaction, and can be delayed/halted by a determined attacker to defeat the defense entirely.
- **Generating dynamic links without `rel="noopener noreferrer"`**: Leaves a live `window.opener` reference the target page can use to redirect the original tab (reverse tabnabbing), plus leaks referrer data.
- **Treating isolation policies / fetch metadata as a standalone defense**: Given current support is limited to recent Chrome/Firefox, using it alone leaves users on Safari or many international browsers unprotected.

## Code Examples
```javascript
// submitted via address collection form
const obj = { "__proto__": { "role": "admin" } }
```
- **What it demonstrates**: The malicious key (`__proto__`) that key sanitization must catch before merging user input into an object.

```javascript
const allowedKeys = ["street", "city", "state", "firstName", "lastName"];
const isKeyValid = function (key) {
  if (!allowedKeys.includes(key)) {
    return false;
  } else {
    return true;
  }
};
const updateUserData(data) {
  let isValid = true;
  for (const [key, value] of Object.entries(data)) {
    if (!isKeyValid(key)) {
      isValid = false;
    }
  }
  if (!isValid) {
    console.error("an invalid key was found!");
  } else {
    updateUserData(data);
  }
};
```
- **What it demonstrates**: Full key-sanitization implementation — iterate every incoming key, reject the entire update if any key fails the allowlist check.

```javascript
// manual object constructor invocation inheriting from null
const myObj2 = Object.create(null);
myObj2["username"] = "testUser2";
Object.getPrototypeOf(myObj2); // null
```
- **What it demonstrates**: Creating a prototype-less object immune to prototype-chain pollution because there is no parent to walk up to.

```text
Content-Security-Policy: frame-ancestors 'none';
```
- **What it demonstrates**: The single-line CSP directive that blocks all framing of the page, stopping the majority of clickjacking attempts.

```javascript
html { display: none; }
if (self == top) {
  document.documentElement.style.display = 'block';
}
```
- **What it demonstrates**: A framebuster fallback — content hidden by default, revealed only when the page confirms it is the top-most window (not framed).

```text
<a href="malicious-website.com" rel="noopener noreferrer">click me</a>
```
- **What it demonstrates**: Nulling `window.opener` and suppressing referrer leakage on a dynamically generated link, the core tabnabbing defense.

```javascript
app.get('/index.html', function (req, res, next) {
  if (req.headers["Sec-Fetch-Dest"]) {
    const dest = req.headers["Sec-Fetch-Dest"];
    if (dest === "frame") {
      return res.sendStatus(400);
    } else {
      return res.sendFile("/index.html");
    }
  }
});
```
- **What it demonstrates**: A server-side isolation-policy mitigation that rejects requests whose `Sec-Fetch-Dest` indicates the page is being loaded into a frame, blocking clickjacking attempts at the server.

## Reference Tables
| Attack | Primary defense | Fallback / supplementary defense |
|---|---|---|
| Prototype pollution | Key Sanitization (allowlist keys) | `Object.freeze()` on specific objects; `Object.create(null)` at instantiation |
| Clickjacking | CSP `frame-ancestors` | Framebusting script (`self == top` check) |
| Tabnabbing | COOP `same-origin` | `rel="noopener noreferrer"` on dynamic links |
| All three (defense-in-depth) | — | Fetch metadata / isolation policies (`Sec-Fetch-*` headers), Chrome/Firefox only |

| Sec-Fetch-Site value | Meaning |
|---|---|
| same-origin | Request from the site's own origin |
| same-site | Request from a subdomain of the application |
| cross-site | Request from a different site |
| none | Not from a website (e.g., bookmark, plug-in) |

## Worked Example
The chapter's clickjacking-defense walkthrough, combined with the fetch-metadata mitigation:

1. **Baseline risk**: An application has no framing controls, so an attacker can iframe it, set the iframe's opacity to 0, and overlay a decoy button to hijack clicks (as detailed in the Offense chapter).
2. **Primary fix — CSP frame-ancestors**: The team adds `Content-Security-Policy: frame-ancestors 'none';` to the response headers. Because over 95% of modern browsers honor this directive, the page can no longer be loaded inside any iframe anywhere, closing off the clickjacking vector for the vast majority of users immediately.
3. **Handling a legitimate framing need**: If the application actually needs to be embeddable (e.g., a widget), the policy is loosened to an explicit allowlist: `Content-Security-Policy: frame-ancestors subdomain.my-website.com`, or `self` if the app needs to embed a copy of itself.
4. **Fallback for unsupported browsers**: For the small remaining population on browsers without `frame-ancestors` support, a framebuster script is added: CSS hides all content by default (`display: none`), and a JS check (`self == top`) reveals it only once confirmed the page is not framed — deliberately avoiding legacy variants that let content render before the check completes.
5. **Defense-in-depth layer**: On top of both, the server inspects the `Sec-Fetch-Dest` header on requests for `/index.html` and returns HTTP 400 if the value is `frame`, adding a server-side backstop for the subset of browsers (Chrome/Firefox) that send fetch metadata — acknowledged as supplementary, not a replacement for CSP.

## Key Takeaways
1. Sanitize object keys against an allowlist before merging user data into JS objects — this is the first-line defense against prototype pollution, though it doesn't work when input must stay flexible.
2. Use `Object.freeze()` and `Object.create(null)` surgically on specific objects, never in bulk or looped across a prototype chain, since many built-in APIs depend on mutability elsewhere.
3. CSP `frame-ancestors 'none'` (or an origin allowlist) is the primary, modern clickjacking defense — `X-Frame-Options` is obsolete; reserve framebuster scripts for browsers without CSP support.
4. Set COOP to `same-origin` by default and add `rel="noopener noreferrer"` to every dynamically generated link to close both traditional and reverse tabnabbing paths.
5. Fetch metadata / isolation policies (`Sec-Fetch-*` headers) are a defense-in-depth layer only — current support is limited to recent Chrome/Firefox, so never rely on them as a sole mitigation.
6. Most client-side attack mitigations are simple configuration changes with high leverage — a small time investment here yields a disproportionately large improvement in security posture.

## Connects To
- **Client-Side Attacks — Offense chapter (ch31)**: This chapter directly mitigates the prototype pollution, clickjacking, and tabnabbing techniques described there.
- **Secure Application Configuration (Chapter 22, referenced)**: CSP and COOP directive implementation details are covered there in full.
