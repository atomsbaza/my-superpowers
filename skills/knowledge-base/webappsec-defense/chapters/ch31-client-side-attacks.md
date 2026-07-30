# Chapter 31: Client-Side Attacks

## Core Idea
As application logic moved from server to browser, the client became a first-class attack surface: entire exploit classes — prototype pollution, clickjacking, and tabnabbing — can be developed and deployed against a browser without ever touching, or being logged by, a web server.

## Frameworks Introduced
- **Client-targeted vs. client-specific attacks**: A two-way split for categorizing browser attacks.
  - When to use: Scoping whether a vulnerability class belongs in "client-side attacks" analysis at all.
  - How: Client-targeted attacks (e.g., ReDoS) can occur on either client or server depending on where the vulnerable code runs; client-specific attacks (e.g., DOM XSS) exist solely in the browser and require no server-side counterpart.
- **Prototype pollution exploitation**: Compromise an object you cannot reach by polluting a prototype it inherits from.
  - When to use: Against JavaScript/Node.js applications using prototypal inheritance, especially where merge/extend-style utilities combine attacker-controlled input into objects.
  - How: Find a merge/assign function that writes into an object's prototype chain (`__proto__` or `constructor.prototype`) using attacker-supplied keys; inject a property or function name that a downstream object will resolve via prototype-chain lookup.
- **Prototype Pollution Archetypes**: Classifies what an attacker does once pollution is achieved.
  - When to use: After confirming a pollution primitive, to decide the exploitation goal.
  - How: Escalate toward (1) denial of service — corrupt a value's type to break downstream logic, (2) property injection — override a value a function call depends on, or (3) remote code execution — reach a sink like `eval()` or `DOMParser.parseFromString()` to upgrade to script execution (client) or server code execution (Node.js).
- **Clickjacking construction**: Overlay a transparent, legitimate iframe underneath a decoy UI so user clicks are silently redirected.
  - When to use: Against any site that lacks framing controls (no X-Frame-Options/CSP frame-ancestors).
  - How: iframe the target site, set its opacity to 0, position a decoy button exactly over a privileged control in the iframe, and set `pointer-events: none` on the decoy so clicks pass through to the invisible iframe underneath.
- **Tabnabbing / reverse tabnabbing**: Abuse the DOM's cross-tab `window` reference to swap or redirect a trusted tab after the user has already verified it.
  - When to use: Against sites that open new tabs via `window.open()` without `noopener`, or that can be tricked into linking to attacker content with `target="_blank"` or in an iframe.
  - How (traditional): opener tab holds a reference from `window.open()` and later calls `windowObj.location.replace(...)` on the now-trusted tab. How (reverse): the newly opened/linked/iframed page reaches back via `window.opener` or `window.parent` to redirect the original tab.

## Key Concepts
- **Client-side attack**: Any exploitable vulnerability that requires no vulnerable web server or network call to succeed.
- **Prototype chain**: The lookup path (`obj.__proto__` → ... → `Object.prototype`) a JavaScript interpreter walks when a property/function isn't found directly on an object.
- **Constructor pollution**: Polluting `constructor.prototype` instead of `__proto__` directly, achieving the same downstream effect since all instances call `constructor`.
- **Clickjacking**: Merging malicious and legitimate UI so a user's click registers against an unintended, often privileged, target — effectively a UI-level keylogger for clicks.
- **Traditional tabnabbing**: The site that opened a new tab later hijacks that tab's location using its retained `window` reference.
- **Reverse tabnabbing**: The site opened in the new tab hijacks the tab that opened it, via `window.opener` or `window.parent`.
- **Sink for pollution escalation**: A function like `eval()` or `DOMParser.parseFromString()` that turns injected data into executed code.

## Mental Models
- Think of client-side attacks as "offline-capable" exploitation: once the HTML/CSS/JS is downloaded, an attacker can turn off the network and iterate millions of payload attempts with zero server-side detection risk.
- Use the prototype chain like an org chart lookup: a call that fails to resolve on the direct report (`Bob`) escalates up to the manager (`Technician`), then the CEO (`Object`) — pollute any level above the target and the resolution is silently redirected.
- Treat `window.open()` and `target="_blank"` as handing out a live remote control to your tab by default; the absence of `noopener`/`noreferrer` is what leaves that control in the wrong hands.
- Treat clickjacking as a transparency problem, not an input-validation problem: the "vulnerability" is architectural (missing framing headers), not a bug in any one endpoint.

## Anti-patterns
- **Merging attacker-controlled objects directly into shared state**: Libraries like `merge()` that don't block `__proto__`/`constructor` keys let an attacker pollute every consumer of that prototype, not just the object they touched.
- **Opening new tabs without `rel="noopener"`**: Leaves a live `window` reference in the new tab that either party can weaponize to redirect the other.
- **Framing third-party content without `sandbox` or CSP `frame-ancestors`**: Allows an attacker to invisibly overlay your privileged UI and steal clicks.
- **Assuming client-side code is unreachable to attackers**: Because it ships in the browser, all client-side logic (including “security” checks) is fully readable and offline-testable by a hacker.

## Code Examples
```javascript
// adds functionality to technician class
const addTechnicianFunctionality = function (obj) {
  Technician.prototype[obj.name] = obj.data
}
// user input payload
{ name: "toString", data: `function() { console.log("polluted!"); }` }
Bob.toString(); // prints "polluted!"
```
- **What it demonstrates**: Polluting a prototype one level up (`Technician`) silently changes behavior on an instance (`Bob`) the attacker never directly touched.

```javascript
merge(Object, { "__proto__.isAdmin": true });
console.log(Bob.isAdmin); // true

merge(Object, { "constructor.prototype.isAdmin": true });
console.log(Bob.isAdmin); // true
```
- **What it demonstrates**: The real-world npm `merge` v2.0 payloads that pollute `Object.prototype` directly or via `constructor.prototype`, both propagating `isAdmin: true` to every object instance.

```html
<div id="clickjacker">
  <span id="fake_button">click me</span>
</div>
<iframe id="target_website" src="target-website.com"></iframe>
```
```css
#target_website { opacity: 0; }
#fake_button { position: relative; right: 25px; top: 25px; pointer-events: none; background-color: blue; }
```
- **What it demonstrates**: A minimal clickjacking rig — invisible iframe of the real target, decoy button positioned exactly over a privileged control, `pointer-events: none` letting clicks fall through to the hidden iframe.

```javascript
// traditional tabnabbing
const goToLegitWebsite = function () {
  const windowObj = window.open("https://website-b.com");
  setTimeout(() => {
    windowObj.location.replace("https://website-c.com");
  }, 1000 * 60 * 5);
};

// reverse tabnabbing (DOM API attack, opened tab targets the opener)
window.opener.location.replace("https://get-hacked.com")

// reverse tabnabbing (iframe attack)
window.parent.location.replace("https://get-hacked.com");
```
- **What it demonstrates**: The three tabnabbing directions — attacker-opened tab later hijacking a trusted tab it spawned, and the reverse where the opened/framed malicious page reaches back to hijack its opener/parent.

## Reference Tables
Table 16-1. Prototype chain resolution for `Bob.toString()`

| Step | Function called | Class evaluated | Found? |
|------|------------------|------------------|--------|
| 1    | toString()       | Bob              | False  |
| 2    | toString()       | Technician       | False  |
| 3    | toString()       | Object           | True   |

## Worked Example
The chapter walks through polluting the `Bob` object (an instance of `Technician`, which inherits from `Object`) without ever touching `Bob` directly.

1. Establish the inheritance chain: `Object → Technician → Bob`, verified via `Bob.__proto__ == Technician.prototype` and `Bob instanceof Object`.
2. Observe that calling an undefined method on `Bob` (e.g., `toString()`) walks the prototype chain until it resolves on `Object`.
3. Find an attack surface: the npm `merge` v2.0 library's `merge()` function, which naively merges attacker-supplied keys into a target object.
4. First attempt fails: `merge(Object, { isAdmin: true })` sets a property directly on `Object` itself, not its prototype — `Bob.isAdmin` stays `undefined`.
5. Successful payload: `merge(Object, { "__proto__.isAdmin": true })` writes into `Object.prototype`, so `Bob.isAdmin` now resolves to `true` via prototype-chain lookup, despite the attacker never having access to `Bob`.
6. Equivalent variant: targeting `constructor.prototype` instead of `__proto__` achieves the identical result, since every object created via `Object`'s constructor inherits from the same polluted prototype.
7. Escalation: this pollution primitive can then be pushed toward DoS (corrupt a type), property injection (override a value a function depends on), or RCE (reach `eval()` or `DOMParser.parseFromString()`).

## Key Takeaways
1. Client-side attacks can be fully developed offline once the application's HTML/CSS/JS is downloaded, making them nearly undetectable by server-side logging.
2. Prototype pollution lets you compromise objects you don't have access to by polluting a shared ancestor (`__proto__` or `constructor.prototype`) that a merge/extend function writes into.
3. Escalate a pollution primitive along the DoS → property injection → RCE ladder; RCE typically requires a sink like `eval()` or `DOMParser.parseFromString()`.
4. Clickjacking exploits missing framing controls: an invisible iframe plus `pointer-events: none` on a decoy silently redirects clicks to a privileged, hidden target.
5. `window.open()` and `target="_blank"` leave a live cross-tab `window` reference by default, which either the opener or the opened page can weaponize (traditional vs. reverse tabnabbing) absent `noopener`.
6. All three attack families let a hacker compromise state or steal input without a server-side workflow, so they are cheap to iterate and hard to trace.

## Connects To
- **Defense Against Client-Side Attacks**: Directly mitigates prototype pollution (input sanitization, `Object.freeze`, blocking `__proto__`/`constructor` keys), clickjacking (X-Frame-Options, CSP `frame-ancestors`), and tabnabbing (`rel="noopener noreferrer"`, `sandbox`, CSP).
- **DOM XSS (external, Chapter 10)**: Named in this chapter as the poster-child client-specific attack, sharing the property that both sink and source live entirely in the browser.
