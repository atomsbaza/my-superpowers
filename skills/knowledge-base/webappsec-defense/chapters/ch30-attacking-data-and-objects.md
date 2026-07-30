# Chapter 30: Attacking Data and Objects

## Core Idea
Modern languages split program logic into data (objects, first-class citizens) and actions (functions); this chapter shows how attackers exploit that split by injecting unvalidated keys into objects (mass assignment), tampering with client-supplied object references (IDOR), or breaking a serializer's escaping to achieve code execution.

## Frameworks Introduced
- **Serialization Attack Methodology**: a 5-step process for finding and exploiting weak serializers.
  - When to use: any time an application serializes/deserializes data (JSON, XML, YAML, base64) for transport or storage.
  - How:
    1. Find a function that performs serialization.
    2. Read the function carefully or test it with common payloads.
    3. After finding a failure to properly serialize data, create a payload capable of script execution.
    4. Call the function with a payload capable of script execution.
    5. Obtain remote code execution (server) or XSS (client).

## Key Concepts
- **Mass Assignment (autobinding / object injection)**: a function that upserts/updates an object from client-supplied data without validating which keys are permitted, letting an attacker add unauthorized fields.
- **First-class citizen**: a language entity (typically data/objects) that can be assigned, reassigned, passed as an argument, and returned from a function.
- **Insecure Direct Object Reference (IDOR)**: a vulnerability where server-side objects (files, records) are directly and predictably addressable via user-supplied parameters (URL query, POST body, `:id` path segments) with no ownership/authorization check.
- **Serialization**: converting an in-memory object into a transportable/storable format (JSON, XML, YAML, base64) that can later be deserialized back into memory.
- **Deserialization**: reverting a serialized blob back into raw in-memory data, creating new memory addresses/pointers.
- **Key/allowlist validation**: restricting which object keys a write operation will accept, as opposed to accepting or blindly denylisting.
- **eval()-based RCE via serialization**: when a serializer fails to escape attacker-controlled characters, the resulting string can break out of its data context and execute as code if later passed to `eval()`.

## Mental Models
- Think of mass assignment as "the client fills out the whole form, and the server photocopies every line onto the record" — if the client can add a line, the server writes it verbatim unless it checks which lines are allowed.
- Think of IDOR as a hotel that hands out room numbers instead of keys — if you can guess or observe another room number, nothing stops you from walking in.
- Use the serialization methodology whenever an app moves objects across a trust boundary (browser↔server, service↔service, disk) — the boundary is exactly where a broken serializer turns into code execution.

## Anti-patterns
- **No key allowlisting on object writes**: a function like `update()` that loops over `Object.entries(data)` and upserts every key/value pair blindly lets an attacker add fields (e.g. `isAdmin`) never intended to be client-writable.
- **Trusting client-supplied identifiers for authorization**: deriving "which object to serve" purely from a URL/param (`:id`) instead of checking it against the authenticated session's ownership lets any user request any other user's object.
- **Rolling or trusting a serializer without testing its escaping**: using a serialization library (or custom code) without verifying it properly escapes quotes/control characters can turn a data blob into an `eval()`-triggered RCE.

## Code Examples
```javascript
// Vulnerable API endpoint (MegaGame) - no key validation before update
app.post("updatePlayerData", function (req, res, next) {
  // if client sent back player state data, update in the database
  if (!!req.body.data) {
    db.update(session.currentUser, req.body.data);
    return res.sendStatus(200); // success
  } else {
    return res.sendStatus(400); // error
  }
});

// db.update() - upserts every key with no validation
const update = function (data) {
  for (const [key, value] of Object.entries(data)) {
    database.upsert({ `${key}`: `${value}` })
  }
}
```
```json
// Expected client payload
{ "playerId": 123, "playerPosition": { "x": 125, "y": 346 }, "playerHP": 90 }

// Attacker-modified mass assignment payload
{
  "playerId": 123,
  "playerPosition": { "x": 125, "y": 346 },
  "playerHP": 90,
  "isAdmin": true // this is the "attack" portion of the payload
}
```
```javascript
// IDOR endpoint
app.get('/files/:id', function (req, res, next) => {
  return res.sendFile(`/filesystem/files/${req.params.id}`);
});
```
```
Intended request:
HTTP GET https://mywebsite.com/files/my-report-card.txt

Tampered request (change :id to access another user's file):
HTTP GET https://mywebsite.com/files/other-report-card.txt
```
```javascript
// serialize-javascript <=3.0.9 escaping bypass -> eval() RCE
// Input payload:
{"foo": /1"/, "bar": "a\"@__R-<UID>-0__@"}

// Resulting (improperly escaped) serialized output:
{"foo": /1"/, "bar": "a\/1"/}

// Proof-of-concept achieving code execution when passed through eval():
eval('(' + serialize({"foo": /1" + console.log(1) /i, "bar": '"@__R-<UID>-0__@'}) + ')');
```
- **What it demonstrates**: (1) an unvalidated key upsert lets a client escalate privilege by adding `isAdmin: true`; (2) a `:id` path parameter served with no ownership check lets a client swap filenames to read another user's file; (3) a serializer's failure to escape quotes lets attacker input break out of its string context and execute as code via `eval()`.

## Reference Tables
| Attack | Mechanism | Attacker Controls | Typical Impact |
|---|---|---|---|
| Mass Assignment | Function upserts/binds all object keys from client input with no allowlist | Extra/unexpected keys in a request body (e.g. `isAdmin`) | Privilege escalation, unauthorized field modification |
| IDOR | Server resolves objects directly from user-supplied identifiers with no ownership check | The identifier itself (URL param, `:id`, POST body field) | Unauthorized access to other users' data/files, privilege escalation |
| Serialization Attack | Serializer fails to properly escape/format attacker-controlled data | The raw input fed into the serialization function | Remote code execution (server, via `eval()`) or XSS (client) |

## Worked Example
MegaGame exposes `POST /updatePlayerData`, which forwards the client's `req.body.data` straight into `db.update()`. That helper iterates every key in the object and upserts it with no validation. The developer expects only `playerId`, `playerPosition`, and `playerHP`, but because no allowlist exists, a hacker intercepts the request and appends `"isAdmin": true`. The upsert loop writes that key exactly like any other, and the attacker's database row now has `isAdmin` set — granting an in-game admin role. Had `update()` validated/sanitized incoming keys against an allowlist, the injected `isAdmin` field would have been dropped and no privilege escalation would occur.

## Key Takeaways
1. Never let an update/upsert function iterate and write arbitrary client-supplied keys — validate against an explicit allowlist of permitted fields.
2. Never resolve server-side objects (files, records) directly from a user-supplied identifier without checking that the authenticated session actually owns/may access that object.
3. Before trusting any serialization library, test it with adversarial payloads (unescaped quotes, control characters) rather than assuming correct escaping.
4. Treat any code path that pipes serialized/deserialized data into `eval()` (or an equivalent) as a high-value RCE target requiring extra scrutiny.
5. Mass assignment, IDOR, and serialization attacks all stem from the same root cause: trusting client-provided structure (keys, identifiers, or escaped strings) without server-side validation.

## Connects To
- **Defending Against Mass Assignment/IDOR/Insecure Deserialization chapter(s)**: this attack chapter's countermeasures are covered in later defense chapters (exact global chapter numbers not yet finalized, so reference by title only)
- **Allowlist/denylist validation**: the general input-validation principle that prevents mass assignment and weak serialization from being exploitable.
- **Object-relational mapping (ORM) / database upsert semantics**: understanding how `upsert()` writes arbitrary keys is necessary to see why unvalidated mass assignment is dangerous.
- **OWASP Top 10 (2007 IDOR entry)**: IDOR's origin as a named, catalogued web vulnerability class.
