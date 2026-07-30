# Chapter 48: Defending Data and Objects

## Core Idea
Data and object attacks (mass assignment, IDOR, serialization) are among the simplest vulnerability classes to defend against once you commit to explicit allowlisting, non-guessable references with authorization checks, and audited serialization libraries — the defenses are cheap relative to the offense.

## Frameworks Introduced
- **Field Allowlisting**: Restrict which client-supplied fields are ever passed into a database write.
  - When to use: Any endpoint that accepts an object from the client and forwards fields of it into `db.update()` or equivalent.
  - How: Define an explicit array of permitted field names (e.g., `["hp", "location"]`); validate the incoming payload against it before the write call, rejecting or stripping any field not on the list (such as `admin`).
- **Data Transfer Object (DTO) Pattern**: Use an intermediary constructor to enforce a strict object shape between services or function calls.
  - When to use: When allowlisting alone feels insufficient, or when the same shape needs enforcing across multiple call sites — a more intensive but more systematic mitigation than ad hoc validation.
  - How: Define a constructor function that only assigns known properties (e.g., `hp`, `location`) onto `this`; route all incoming client data through the DTO constructor before it reaches persistence code, so any extra attacker-supplied parameters are silently dropped rather than propagated.
- **IDOR Defense (indirection + authorization)**: Prevent direct or guessable references to objects/files, and gate every access with an authorization check.
  - When to use: Any endpoint returning or referencing files/objects by ID, filename, or other client-visible identifier.
  - How: Never expose the raw filename/reference in the API; mask it, and perform an authorization check prior to every file/object return. Where direct exposure can't be avoided, use randomly generated references with enough entropy that guessing requires millions of attempts, combined with rate limiting — treated as a short-term mitigation pending a real architecture fix.
- **Strong Serialization Practice**: Eliminate weak serialization, the root cause of every serialization attack.
  - When to use: Any place the application serializes or deserializes data (session state, API payloads, cache entries).
  - How: Choose a popular, well-audited open source library and a common, well-scrutinized format (JSON, YAML) over obscure/unaudited formats. Sanitize or allowlist characters and object types being serialized, especially data that could be interpreted as script or contains escape characters, if the serializer doesn't already handle this.

## Key Concepts
- **Mass assignment**: A vulnerability where a server trusts an entire client-supplied object and writes its fields directly to the database, letting an attacker set fields (e.g., `admin`) they shouldn't control.
- **Allowlist**: An explicit, exhaustive list of permitted values (here, field names) used to reject anything not on the list.
- **Data Transfer Object (DTO)**: An intermediary object with a fixed constructor shape used to pass data between services or calls, filtering out unexpected properties by construction.
- **IDOR (Insecure Direct Object Reference)**: Referencing an object or file via a directly guessable identifier without an accompanying authorization check.
- **Weak serialization**: A serialization/deserialization implementation lacking security auditing or robust handling of unsafe characters/object types, the underlying cause of serialization attacks.
- **Ephemeral vs. persistent data**: In-memory (ephemeral) versus filesystem/database (persistent) storage; most persisted data passes through memory during operations, so ephemeral-data defenses often apply to filesystem data too.

## Mental Models
- Treat every client-supplied object as an attacker's editable form, not as trusted server state — mass assignment exists purely because a developer chose to trust it wholesale.
- Use a DTO like a bouncer with a strict guest list at a constructor's door: anything not named on entry never gets in, regardless of what's smuggled in the request body.
- Think of IDOR defense as "don't hand out the map, and check ID at the door anyway" — masking the reference and performing authorization are complementary, not substitutes for each other.
- Treat serialization format choice like picking a vendor for a safe: popularity and audit history (JSON/YAML with a maintained library) matter more than a format's theoretical elegance.

## Anti-patterns
- **Directly writing an entire client-supplied object to the database**: Without allowlisting or a DTO, any field the client includes (e.g., `admin: true`) gets persisted, regardless of developer intent.
- **Using guessable or sequential object/file references without authorization checks**: Even non-guessable random references are not a substitute for per-request authorization — they're a stopgap, not a fix.
- **Rolling your own serialization format or using an unaudited one**: Weak serialization is the single root cause of serialization attacks; homegrown or rarely-audited formats carry disproportionate risk.
- **Accepting serializable data without sanitizing script-like or escape characters**: Even a strong library can be undermined if the data fed into it isn't screened for characters the server or browser could later interpret as executable.

## Code Examples
```javascript
/*
 * This is a server-side API endpoint for updating player data
 * for the web-based video game "MegaGame".
 */
app.post("updatePlayerData", function (req, res, next) {
  // if client sent back player state data, update in the database
  if (!!req.body.data) {
    db.update(session.currentUser, req.body.data);
    return res.sendStatus(200); // success
  } else {
    return res.sendStatus(400); // error
  }
});
```
- **What it demonstrates**: The vulnerable mass assignment pattern — trusting `req.body.data` wholesale and writing it directly to the database with no field restriction.

```javascript
const allowlist = ["hp", "location"]; // only allow these two fields to be updated
```
- **What it demonstrates**: The minimal allowlist-based mitigation — validate incoming fields against this list before calling `db.update()`.

```javascript
const DTO = function (hp, location) {
  this.hp = hp;
  this.location = location;
};
```
- **What it demonstrates**: A Data Transfer Object constructor — any property not explicitly assigned here (like `admin`) never makes it onto the resulting object, regardless of what the client sent.

## Reference Tables
| Attack | Root cause | Primary defense |
|---|---|---|
| Mass assignment | Server trusts full client object | Allowlisting or DTO before `db.update()` |
| IDOR | Direct/guessable object reference, no auth check | Mask references + authorization check per request; random high-entropy refs as stopgap |
| Serialization attack | Weak serialization/deserialization library or format | Audited OSS library, popular format (JSON/YAML), sanitize risky characters |

## Worked Example
The chapter walks through the "MegaGame" player-data update endpoint as its running example.

1. **Vulnerable state**: The endpoint blindly checks `!!req.body.data` and calls `db.update(session.currentUser, req.body.data)` — any field the client includes gets written, including one like `admin` that was never meant to be client-writable.
2. **First defense — allowlist**: Before the `db.update()` call, the fields present in `req.body.data` are validated against `const allowlist = ["hp", "location"]`. Any request containing an unlisted field (e.g., `admin`) is rejected or stripped, closing the mass assignment path with minimal code change.
3. **Second, more robust defense — DTO**: Instead of (or in addition to) allowlist validation, incoming data is passed through `const DTO = function (hp, location) { this.hp = hp; this.location = location; }`. Because the DTO constructor only ever assigns `hp` and `location` onto the resulting object, any extra client-supplied properties are structurally impossible to smuggle through — the mitigation is enforced by the object's shape itself, not by a validation step someone could forget to call.
4. **Result**: Both defenses independently prevent the `admin` field (or any other sensitive field) from reaching persistence, with the DTO offering stronger guarantees at the cost of slightly more implementation effort.

## Key Takeaways
1. Never write a full client-supplied object into the database — allowlist the specific fields you expect, or route the data through a DTO constructor that only assigns known properties.
2. A DTO is a stronger mass-assignment defense than a validation-step allowlist because the object's shape itself enforces the restriction, rather than relying on a check someone could forget to call.
3. IDOR defense requires two layers together: mask/avoid guessable references AND perform an authorization check before every object/file return — neither alone is sufficient.
4. High-entropy random references are a short-term IDOR mitigation, not a substitute for a proper architecture with authorization checks and rate limiting.
5. Serialization attacks trace back to weak serialization — pick popular, audited libraries and formats (JSON/YAML) over obscure ones, and sanitize script-like or escape characters before serializing.
6. Because most persistent (filesystem) data passes through memory during operations, defenses built for ephemeral in-memory data usually apply to filesystem-stored data as well.

## Connects To
- **Attacking Data and Objects — Offense chapter**: This chapter directly mitigates the mass assignment, IDOR, and serialization exploitation techniques described there.
- **Defending Against Injection (Chapter 46 / Hoffman ch31)**: Shares the allowlisting philosophy — restrict acceptable input shape rather than trying to blocklist malicious variants.
