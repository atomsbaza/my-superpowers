# Chapter 45: Defending Against XXE

## Core Idea
XXE is trivial to prevent — disable external entity processing in your XML parser's configuration — yet remains widespread because many parsers (particularly Java-based ones) have it enabled by default, and defenders should never assume otherwise without checking documentation.

## Frameworks Introduced
- **Disable-external-entities parser configuration**: A single configuration line that closes the vulnerability at its root.
  - When to use: For every XML parser in your stack, verified individually — never assumed safe by default.
  - How: Set the parser's disallow-doctype-declaration feature to true (e.g., `factory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);` for Java/Apache XML parsers); consult the specific parser's API documentation since the setting and default vary by language/library.
- **Data format re-architecture (XML → JSON/YAML/BSON/EDN)**: Eliminating XXE risk entirely by moving away from XML where the use case allows it.
  - When to use: When the application is sending hierarchical payloads that merely happen to be XML-shaped, rather than genuine XML/SVG/XML-derived content.
  - How: Compare payload requirements (schema validation need, mixed content, rendering requirements) against Table 30-1 before committing to a replacement format.

## Key Concepts
- **XXE (XML External Entity) attack**: An attack exploiting XML parsers configured to resolve external entities, allowing access to local files or internal network resources via crafted XML.
- **DOCTYPE declaration**: The XML construct that can declare external entities; disabling DOCTYPE processing (`disallow-doctype-decl`) is the standard mitigation.
- **XXE as a gateway attack**: XXE often starts as read-only data access but can escalate into full remote code execution and server takeover once internal data aids further compromise.
- **Schema validation**: An XML capability (absent in JSON) allowing rigid, enforced document structure — a legitimate reason to keep XML despite its higher inherent risk.
- **Mixed content**: XML's ability to interleave text and child elements within a single element, unsupported in JSON — relevant when content will be rendered rather than just parsed as data.

## Mental Models
- Treat "disabled by default" as a claim to verify, not assume — Java XML parsers in particular are noted as commonly XXE-enabled out of the box.
- Think of the XML-vs-JSON decision as "rendering and validation rigidity" vs "lightweight and safer by default" — pick XML when you actually need schema validation or eventual HTML-like rendering; pick JSON/YAML/BSON/EDN for lightweight structured data consumed by JavaScript.
- Treat every XXE finding as potentially more than read-only: because it can be a stepping stone to broader compromise, triage it with the assumption of escalation potential, not just the immediate data exposure.

## Anti-patterns
- **Assuming XML parsers disable external entities by default**: Directly contradicted for Java-based parsers per OWASP guidance — always check parser-specific documentation.
- **Keeping XML "because that's what we've always used" without re-evaluating format fit**: Misses an opportunity to eliminate an entire vulnerability class when the payload doesn't actually require XML's rendering/schema features.
- **Treating a discovered XXE as low-severity because it "only" reads files**: Ignores that XXE frequently serves as a recon platform enabling escalation to remote code execution.

## Code Examples
```java
factory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
```
- **What it demonstrates**: The single-line parser configuration change (Java/Apache XML API) that disables DOCTYPE declarations and closes the XXE vulnerability at its source.

## Reference Tables
### Table 30-1. XML versus JSON

| Category | XML | JSON |
|---|---|---|
| Payload size | Large | Compact |
| Specification complexity | High | Low |
| Ease of use | Requires complex parsing | Simple parsing for JavaScript compatibility |
| Metadata support | Yes | No |
| Rendering (via HTML-like structuring) | Easy | Difficult |
| Mixed content | Supported | Unsupported |
| Schema validation | Supported | Unsupported |
| Object mapping | None | JavaScript |
| Readability | Low | High |
| Comment support | Yes | No |
| Security | Lower | Higher |

## Worked Example
A team maintaining a document-processing API discovers, during a routine third-party penetration test, that their Java-based XML parser accepts a crafted document declaring an external entity pointing at `file:///etc/passwd`, and the parser resolves it — leaking the contents of that file into the parsed output. Following the reproduce-score-fix-regress pipeline from Chapter 42, they first reproduce the exploit in staging using the same crafted payload, confirming the parser indeed resolves external entities by default (consistent with the chapter's note that Java parsers are commonly XXE-enabled out of the box, contrary to assumption).

The immediate fix is the single-line configuration change: `factory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);`, applied to every instantiation of that parser across the codebase — not just the one endpoint where it was found, since the same library is likely reused elsewhere. Because the vulnerability could plausibly have been used as a stepping stone toward the internal network or further file access (the "gateway attack" pattern), the team also scores it conservatively high rather than as a simple read-only issue, and reviews whether any other internal systems were reachable through the resolved entity during the reproduction window.

Separately, product reviews why the API accepts XML at all: the actual payloads are simple hierarchical key/value structures with no rendering or schema-validation requirement. Per Table 30-1's comparison, they decide to offer a JSON-based alternative endpoint for new integrations going forward, eliminating an entire class of future XML-parser misconfiguration risk for that surface area, while leaving true XML/SVG-consuming endpoints on a hardened, explicitly-configured parser.

## Key Takeaways
1. Disable external entity/DOCTYPE processing in every XML parser you use — check documentation per parser/language rather than assuming a safe default.
2. Treat Java-based XML parsers as a known-risk case: OWASP flags them as commonly XXE-enabled by default.
3. Where your payload is just hierarchical data (not true XML/SVG needing rendering or schema validation), consider migrating to JSON or another lighter format to eliminate the risk class entirely.
4. Score XXE findings assuming escalation potential — it's frequently a gateway to broader compromise, not just a read-only leak.
5. Re-verify parser configuration across every place the library is instantiated, not just the one endpoint where an issue was found.

## Connects To
- **Chapter 27 (offense): XML External Entity**: This chapter is the direct defense pairing for the XXE attack techniques constructed there.
- **Chapter 42: Vulnerability Management**: The escalation-prone nature of XXE argues for scoring it conservatively (higher Confidentiality/Integrity impact) within the CVSS framework covered there.
- **Chapter 46: Defending Against Injection**: Both chapters share the theme of "attacker-controlled input reaching an interpreter" — XXE is effectively injection into an XML parser's entity-resolution machinery.
