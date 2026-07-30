# Chapter 11: Payload Vulnerabilities

## Core Idea
Server-targeted attacks exploit how crafted payloads — serialized objects, JSON, XML, uploaded files, or bound object data — are parsed, deserialized, or bound on the server, potentially achieving remote code execution or unauthorized data manipulation.

## Frameworks Introduced
- **Safe deserialization**: never auto-invoke deserializers that can call arbitrary code on untrusted binary data; prefer text formats with a safe loader.
  - When to use: any time a server accepts serialized data from a client (e.g., a document editor's "save state" feature).
  - How: use `yaml.SafeLoader` instead of the default YAML loader; never deserialize raw pickled Python objects from an untrusted source; if you must round-trip serialized state to a client, HMAC-sign it and verify the signature (via `hmac.compare_digest`) before deserializing.
- **Allow-list field binding (anti mass-assignment / anti prototype-pollution)**: explicitly enumerate which fields may be written from an incoming payload rather than merging/binding the whole object.
  - When to use: any data-binding step from HTTP request body to an in-memory or DB-backed object (user profile updates, JSON merges).
  - How: manually unpack only expected fields (`user.setName(json.get("name"))`) instead of generic recursive merge or full-object data binding.
- **DTD-disabling per XML parser**: block inline Document Type Definitions to prevent XML bombs and XXE.
  - When to use: any XML parsing of untrusted input, in any language.
  - How: language-specific settings (see Reference Tables) — e.g., `defusedxml` in Python, `disallow-doctype-decl` feature in Java, `ProhibitDtd` in .NET.

## Key Concepts
- **Serialization/deserialization**: converting an in-memory structure to a binary/text format for storage or transfer, and reversing that process — called pickling (Python) or marshaling (Ruby).
- **Prototype pollution**: an attacker-controlled JSON merge modifies an object's `__proto__` chain, altering behavior of every object sharing that prototype.
- **XML bomb ("billion laughs")**: nested DTD entity substitutions that expand exponentially, exhausting server memory with a single small request.
- **XXE (XML external entity attack)**: an inline DTD entity referencing an external `file://` or network URL, letting an attacker read local files or trigger SSRF via the XML parser.
- **Web shell**: an uploaded executable script (e.g., PHP) that lets an attacker run arbitrary OS commands via HTTP once it lands in an executable location.
- **Indirection (for uploads)**: saving a file to disk under a machine-generated name while recording the user-facing name in a database, avoiding both path-traversal and overwrite risks.
- **Path/directory traversal**: manipulating a filename parameter (e.g., `../../etc/passwd`) to read or overwrite files outside the intended directory.
- **Mass assignment**: automatically binding all fields of an incoming request onto a data object, letting an attacker set fields (like `isAdmin`) that were never meant to be user-controlled.
- **Zip bomb**: an archive that expands to a much larger size when unzipped, exhausting disk space if unarchiving isn't bounded.

## Mental Models
- Treat every uploaded file as hostile until proven otherwise: validate filename charset, size, and true type (magic bytes, not extension) — client-side JS validation is UX only.
- Think of DTDs as "self-modifying documents" — because entities can reference other entities (exponential blowup) or external URLs (SSRF/file read), any parser that honors inline DTDs is trusting the attacker's own document to tell it what to do.
- Use indirection as the default answer to "can an attacker control a filename/path": store real names in a database, not in the filesystem path itself.

## Anti-patterns
- **Auto-invoking deserializers on untrusted binary data**: Python's `pickle` will call `__setstate__()` during deserialization — an attacker-crafted object can execute arbitrary code (e.g., `os.system("rm -rf /")`) the instant it's loaded.
- **Non-safe YAML loading**: the default YAML loader in many languages allows arbitrary object construction; always use the safe/restricted loader variant.
- **`eval()` on untrusted JSON in Node.js**: because JSON is a JavaScript subset, `eval(data)` on a request body lets an attacker submit raw executable JavaScript instead of data — use `JSON.parse()` exclusively.
- **Recursive/generic object merge**: merging attacker-supplied JSON into a live object without an allow list enables prototype pollution via `__proto__` keys.
- **Inline DTDs left enabled**: nearly every mainstream XML parser defaults to allowing them; explicitly disable per the language-specific setting.
- **Trusting file extensions or client-declared MIME types**: attackers can craft files valid in multiple formats (e.g., simultaneously a GIF and a JAR); verify with magic-byte inspection server-side.
- **Executable permissions on uploaded files**: writing uploads with `0o755` (execute for all) instead of `0o644` (read-write only) turns a file-upload feature into a web-shell deployment vector.
- **Whole-object data binding without an allow list**: frameworks like Java Play's Jackson-based binding will happily set an `isAdmin` field if the attacker includes it in the request body.

## Code Examples
```python
import yaml
data = {"name": "Rammellzee", "address": "Far Rockaway, Queens"}
serialized_data   = yaml.dump(data)
deserialized_data = yaml.load(serialized_data, Loader=yaml.SafeLoader)
```
- **What it demonstrates**: safe YAML deserialization using `SafeLoader` to prevent arbitrary object creation.

```python
import hmac, pickle, hashlib
def save_state(document):
    data      = pickle.dumps(document)
    signature = hmac.new(secret_key, data, hashlib.sha256).digest()
    return data, signature

def load_state(data, signature):
    computed_signature = hmac.new(secret_key, data, hashlib.sha256).digest()
    if not hmac.compare_digest(signature, computed_signature):
        raise ValueError("HMAC signature verification failed. The data may have been tampered with.")
    return pickle.loads(data)
```
- **What it demonstrates**: HMAC-signing round-tripped serialized state so tampering is detected before deserialization is even attempted.

```javascript
// Vulnerable prototype-pollution merge
function merge(target, source) {
  Object.entries(source).forEach(([key, value]) => {
    if (value instanceof Object) {
      if (!target[key]) { target[key] = {}; }
      merge(target[key], value);
    } else {
      target[key] = value;
    }
  });
}
// Attack payload: { name: "sneaky_pete", __proto__: { access_code: "brainworms" } }

// Fix: explicit allow-listed assignment
function saveProfileChanges(edits) {
  let user = db.user.load(currentUserId());
  user.name    = edits.name;
  user.address = edits.address;
  user.phone   = edits.phone;
  db.user.save(user);
}
```
- **What it demonstrates**: generic recursive merge enabling prototype pollution, fixed by enumerating exactly which fields may be written.

```xml
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE sneaky [
  <!ENTITY passwords SYSTEM "file://etc/shadow">
]>
<sneaky>&passwords;</sneaky>
```
- **What it demonstrates**: an XXE payload that, if the parser resolves external entities, inserts the contents of a sensitive local file into the parsed document (often leaked via an error message).

```php
<?php
if(isset($_REQUEST['cmd'])) {
    $cmd = ($_REQUEST['cmd']);
    system($cmd);
} else {
    echo "What is your bidding?";
}
?>
```
- **What it demonstrates**: a PHP web shell — if an attacker can upload this and have it served with execute permission, they gain arbitrary command execution via HTTP.

## Reference Tables
| Language | Disable inline DTDs by |
|---|---|
| Python | Use `defusedxml` instead of the standard `xml` module |
| Ruby | Set the `noent` flag to `true` in Nokogiri |
| Node.js | Set `{noent: true}` when using `libxmljs` |
| Java | `dbf.setFeature("https://apache.org/xml/features/disallow-doctype-decl", true)` |
| .NET | `XmlReaderSettings.ProhibitDtd = true` (or `XmlTextReader.ProhibitDtd` pre-3.5) |
| PHP | Use libxml ≥ 2.9.0, or call `libxml_disable_entity_loader(true)` |

| Upload validation layer | Checks |
|---|---|
| Client-side (JS) | Filename pattern, MIME type, size — UX only, bypassable |
| Server-side (mandatory) | Max file size, filename charset/length/no path chars, true file type via magic bytes |
| Storage | Rename or use indirection; write with `0o644` never `0o755`; prefer S3/cloud storage |

## Worked Example
A restaurant-menu site stores PDF menus and references the filename directly in the URL, e.g. `/menu?filename=companyA.pdf`. An attacker manipulates the `filename` parameter to `../../etc/passwd` or similar, attempting to read files outside the menu directory (path traversal).

The robust fix avoids direct file references altogether: store each company's menu path in a database indexed by company ID, so the URL parameter never maps directly to a filesystem path. Where a filename parameter can't be avoided, restrict it to a strict allow-listed character set and reject anything else:
```python
@app.route('/menu', methods=['GET'])
def get_file():
    filename = request.args.get('filename')
    if not filename:
        return jsonify({'message': 'File name not provided'}), 400
    validation_pattern = r'^[a-zA-Z0-9_-]+$'
    if not re.match(validation_pattern, filename):
        return jsonify({'message': 'Invalid file name.'}), 400
    path = os.path.join(app.config['MENU_FOLDER'], filename)
    if not os.path.exists(path):
        return abort(404)
    return send_file(path, as_attachment=True)
```
This regex rejects any `/`, `..`, or other path-traversal characters outright, closing the vulnerability even without full indirection.

## Key Takeaways
1. Avoid deserializing untrusted binary/executable content; prefer JSON/YAML with a safe loader, or sign serialized round-trip data with HMAC.
2. In Node.js, always use `JSON.parse()` — never `eval()` — on untrusted JSON, and merge objects via an allow list to prevent prototype pollution.
3. Disable inline DTD processing in every XML parser you use, regardless of language.
4. Validate uploaded files server-side (size, filename charset, true type via magic bytes) — client-side checks are bypassable.
5. Rename uploaded files or use indirection (DB-tracked real name) rather than trusting user-supplied filenames.
6. Never write uploaded files with execute permission; restrict the web server process's own execute rights in upload directories.
7. Enumerate an explicit allow list of bindable fields for any data-binding step — never bind a whole object from a request body.

## Connects To
- **Ch 10**: mass assignment is fundamentally an authorization failure (an attacker sets `isAdmin` through a data-binding gap) — the same discipline of explicit, reviewed field lists applies.
- **Ch 12**: injection attacks are the sibling category — payload vulnerabilities target parsing/deserialization, injection targets command/query construction.
- **Ch 14**: XXE's external-entity capability is itself a form of SSRF, covered in depth in Chapter 14.
