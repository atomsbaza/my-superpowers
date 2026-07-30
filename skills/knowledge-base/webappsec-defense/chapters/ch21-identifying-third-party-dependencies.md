# Chapter 21: Identifying Third-Party Dependencies

## Core Idea
Fingerprinting the client-side frameworks, server software, and databases behind an application — and pinning down their exact versions — lets a tester cross-reference known CVEs and skip straight to reusing a documented exploit instead of hunting for a novel one.

## Frameworks Introduced
- **Global-object fingerprinting for SPA/JS frameworks**: Most major client-side frameworks expose a detectable global object with a version constant.
  - When to use: Any time you need to identify and version-pin a client-side framework during recon.
  - How: Check for `Ember.VERSION`, `angular.version`/`ng-version` attribute, `React.version`, or `Vue.version` in the browser console; for frameworks without a global (Angular 4.0+), inspect root-element attributes instead.
- **Version-range fingerprinting via default error pages / Git history**: For open-source frameworks without an explicit version endpoint, diff the framework's own Git history of its default error/404 page against the target's current default page to bracket a version range.
  - When to use: When a framework hides its version number but is open source with public commit history (e.g., Ruby on Rails).
  - How: Clone the framework's repo, `git log | grep <feature-file>` to find dated changes to the default error page, check which of those changes are present/absent in the target's page, and cross-reference the resulting date range against the framework's official release schedule to bracket a version range — then check that range against CVE databases.

## Key Concepts
- **X-Powered-By / X-AspNet-Version headers**: Default, often-forgotten HTTP response headers that directly disclose server software and version.
- **Primary key structure fingerprinting**: Database-generated IDs (e.g., MongoDB's 12-byte `ObjectId`, encoding a Unix timestamp + random bytes + counter) have detectable structural signatures visible in API responses, even without direct error-message leakage.
- **`document.querySelectorAll('script'/'link')` enumeration**: A DOM-traversal technique to enumerate every third-party JS/CSS dependency loaded into a page, independent of whether that library exposes a recognizable global.
- **CVE cross-referencing**: Once a dependency and its version (or version range) are known, checking public CVE databases can hand over a ready-made, documented exploit rather than requiring original vulnerability research.
- **Client vs. server fingerprinting asymmetry**: Client-side dependencies are trivially enumerable (all code ships to the browser); server-side dependencies must be inferred indirectly via headers, error pages, or behavioral fingerprints since the code itself is never sent to the client.

## Mental Models
- Think of version fingerprinting as detective work with two evidence classes: direct evidence (a version header or global constant handed to you) and circumstantial evidence (dated changes to a default page, bracketed against a public release timeline).
- Use "the client ships all its code" as the core asymmetry driving this chapter: anything running in the browser is fully enumerable; anything running server-side must be reconstructed from indirect signals.
- Treat a discovered CVE as a shortcut, not a certainty: version-range fingerprinting narrows a *range*, and confirming actual exploitability against a specific target still requires a follow-up validation step.

## Anti-patterns
- **Leaving default version-disclosing headers enabled**: `X-Powered-By: ASP.NET` or `X-AspNet-Version` headers hand fingerprinting data to any attacker who runs a single `curl` request.
- **Leaving default 404/error pages unmodified**: Stock error pages from open-source frameworks (Rails, etc.) are versioned artifacts in the framework's own public Git history, making them a reliable version oracle.
- **Outdated client-side libraries with known CVEs**: Once a library's version is fingerprinted (trivial for open-source JS libraries), any known ReDoS, prototype pollution, or XSS CVE against that exact version becomes directly actionable.
- **Assuming server-side fingerprinting is impossible**: Even without explicit version headers, primary key structure, error message quirks, and default page diffing frequently reconstruct enough information to narrow a version range.

## Code Examples
```javascript
// Detect SPA framework versions via exposed globals
console.log(Ember.VERSION);  // e.g. "3.1.0"
console.log(React.version);  // e.g. "0.13.3"
console.log(Vue.version);    // e.g. "2.6.10"

// Angular 4.0+ has no global; check root element attributes instead
const elements = getAllAngularRootElements();
const version = elements[0].attributes['ng-version']; // e.g. "6.1.2"

// Force-enable VueJS devtools inspection if disabled
Vue.config.devtools = true;
```
- **What it demonstrates**: The direct-evidence fingerprinting approach — most SPA frameworks expose their version through a discoverable global or DOM attribute, requiring only a console command to read.

```javascript
// Enumerate every third-party <script> tag loaded into the page
const getScripts = function () {
  const scripts = document.querySelectorAll('script');
  scripts.forEach((script) => {
    if (script.src) { console.log(`i: ${script.src}`); }
  });
};
// Example output:
// i: https://www.google-analytics.com/analytics.js
// i: https://js.stripe.com/v3/
// i: https://code.jquery.com/jquery-3.4.1.min.js
```
- **What it demonstrates**: A generic DOM-traversal enumeration technique that works regardless of whether a library exposes a recognizable global — useful as a fallback for less common dependencies.

## Reference Tables
Client-side framework fingerprinting cheatsheet:

| Framework | Detection | Version constant |
|---|---|---|
| EmberJS | Global `Ember` object; `ember-id` DOM tags | `Ember.VERSION` |
| Angular (pre-4.0) | Global `angular` object | `angular.version` |
| Angular (4.0+) | `ng` global exists; check root element attrs | `ng-version` attribute |
| React | Global `React` object; `.jsx` script tags | `React.version` |
| VueJS | Global `Vue` object | `Vue.version` |

MongoDB `ObjectId` structure (12 bytes total) used for database fingerprinting:

| Bytes | Meaning |
|---|---|
| First 4 bytes | Seconds since Unix epoch |
| Next 5 bytes | Random |
| Final 3 bytes | Counter, starting at a random value |

## Worked Example
The chapter's Ruby on Rails 404-page fingerprinting case is the central end-to-end example:

1. **The target**: A web application running an unknown version of Ruby on Rails, with no version header exposed.
2. **The evidence source**: Rails' default 404 page HTML is a public file in its GitHub repo (`rails/railties/lib/rails/generators/rails/app/templates/public/404.html`), whose history can be inspected via `git log | grep 404`.
3. **Known dated changes**:
   - April 5, 2012 — HTML5 `type="text/css"` attribute removed.
   - November 21, 2013 — `U+00A0` character replaced with whitespace.
   - April 20, 2017 — namespaced CSS selectors (`.rails-default-error-page`) added.
4. **Applying it to the target**: The tester's captured 404 page is missing the `type="text/css"` attribute (post-April 2012) and has the whitespace fix (post-Nov 2013), but lacks the namespaced CSS selectors (pre-April 2017).
5. **Bracketing the version**: Cross-referencing these three date boundaries against Rails' official release schedule narrows the version to somewhere between 3.2.16 and 4.2.8.
6. **The payoff**: Rails 3.2.x through 4.2.7 is documented as vulnerable to an XSS issue (CVE-2016-6316) allowing injection of quote-padded HTML into any database field read by an Action View Tag helper — the tester now has a directly actionable, pre-documented exploit instead of needing to discover a new vulnerability.

## Key Takeaways
1. Client-side dependencies are always fully enumerable (the browser has the code); use global-object and DOM-enumeration techniques to fingerprint them and their exact versions.
2. Server-side dependencies require indirect fingerprinting: headers, default error pages, and primary-key structure.
3. Default 404/error pages from open-source frameworks are versioned artifacts — diff them against the framework's own Git history to bracket a version range.
4. Once a version (or version range) is known, cross-reference CVE databases before attempting original vulnerability research — a documented exploit may already exist.
5. Disable default version-disclosing headers (`X-Powered-By`, `X-AspNet-Version`) and replace default error pages as baseline defensive hygiene.

## Connects To
- **Ch20 (global)**: API Analysis findings (headers, error messages) feed directly into this chapter's server-side fingerprinting techniques.
- **Ch22 (global)**: Dependency fingerprinting results are one of the key inputs to judging whether an application's architecture reinvents vs. properly adopts vetted third-party tools.
- **Ch24-34 (Offense, global), especially Ch33 (Exploiting Third-Party Dependencies, global)**: This chapter's fingerprinting techniques are the direct prerequisite for the dedicated dependency-exploitation offense chapter.
- **CVE databases (external concept)**: The Common Vulnerabilities and Exposures system this chapter repeatedly references as the payoff for successful version fingerprinting.
