# Chapter 4: Web Server Security

## Core Idea
The server boundary must validate every input as strictly as possible (allow list > pattern matching > block list) and escape every output before it reaches an HTML, database, or shell context, layered with defense in depth and least privilege so no single control failure is catastrophic.

## Frameworks Introduced
- **Input validation hierarchy (allow list > pattern matching > block list)**: A ranked set of strategies for accepting only safe input at the server boundary.
  - When to use: On every HTTP parameter, file upload, and header your server processes.
  - How: Use an allow list wherever the full set of valid values is enumerable (currency codes, IP allow-lists); fall back to pattern matching/regex (length bounds + expected character set) when values can't be enumerated; use a block list only as a last resort for known-bad values, since it can never anticipate every malicious input.
- **Output escaping by context (HTML, database, shell)**: Replacing metacharacters with escape sequences appropriate to the specific downstream interpreter before untrusted content reaches it.
  - When to use: Any time untrusted/dynamic content is written into an HTML response, a database command, or an OS command string.
  - How: Rely on your templating engine's default auto-escaping for HTML; use parameterized statements (never string concatenation) for SQL; use structured OS-call APIs with `shell=False`-equivalent semantics instead of building shell command strings.
- **Defense in depth**: Layering multiple independent, overlapping protections so that failure of any single layer doesn't lead to compromise.
  - When to use: For every vulnerability class covered in the book, especially injection.
  - How (for injection specifically): parameterize database statements; validate all inputs (allow/pattern/block list); connect to the database as a limited-permission account; validate the shape of every database response; log and monitor database calls.
- **Principle of least privilege (for systems)**: Grant each software component only the minimum permissions required for its task.
  - When to use: Whenever configuring database accounts, server processes, or file-system permissions.
  - How: Run the web server as a non-root user with access only to required directories; connect to the database under an account without schema-altering privileges even if it needs read-write data access.

## Key Concepts
- **Allow list**: An enumerated list of valid input values; the gold standard for validation when feasible.
- **Block list**: An enumerated list of explicitly banned values; weaker because it can't anticipate unknown malicious inputs, useful mainly as a last resort or for quickly patching known bad values via configuration.
- **Metacharacter**: A character with special meaning to a downstream parser (`<` in HTML, `'`/`;` in SQL, `&&` in shell) — the root cause of injection when left unescaped.
- **Luhn algorithm**: A checksum formula used to reject obviously invalid credit card numbers before further processing.
- **Client-side validation**: Validation performed in the browser (HTML5 input types, JavaScript); improves UX but provides zero security since attackers bypass the browser entirely.
- **Parameterized statement**: A database query where user input is passed as a bound parameter rather than concatenated into the SQL string, letting the driver handle safe escaping.
- **REST (Representational State Transfer)**: An architectural style mapping each resource to a clean URL and each action to the semantically correct HTTP verb.
- **GET side-effect freedom**: The REST/HTTP principle that GET requests must never mutate server state, because GET requests can be triggered merely by a link click (the root cause of CSRF via GET).

## Mental Models
- Think of allow lists, pattern matching, and block lists as a strength ladder: always try to climb to the strongest control the situation allows, and treat block lists as the "we had no other choice" option, not a default strategy.
- Treat escaping as context-specific, never universal: an HTML-safe escape does nothing to protect a SQL query, and a SQL-safe escape does nothing to protect a shell command — each output boundary needs its own correct escaping mechanism.
- Use the medieval-castle model for defense in depth: multiple overlapping walls (parameterization + validation + limited DB permissions + response validation + logging) mean a single breached wall doesn't equal a fallen castle.
- Think of the principle of least privilege like airport security tiers: every actor (process, account, or person) gets exactly the access their specific role requires — not more, regardless of how trusted they otherwise seem.

## Anti-patterns
- **Trusting file extensions for upload validation**: An attacker can name a malicious file anything they want; validate by magic bytes/file header (e.g., via `libmagic`) and cap file size instead.
- **Disabling auto-escape without manual re-escaping**: Frameworks like Jinja2 escape by default; explicitly disabling it (`| safe`, `autoescape false`) without re-implementing escaping yourself reopens XSS.
- **String-concatenated SQL or shell commands**: Directly embeds untrusted input into a command string, enabling SQL injection or command injection.
- **GET-based mutation**: Using a GET request to change server state (e.g., account deletion) makes the action trivially triggerable via a malicious link — a CSRF vulnerability by construction.
- **Leaking implementation details in URLs**: Paths like `/login.php` hint at your technology stack, giving attackers a head start (see chapter 13 on further information leakage).

## Code Examples
```ruby
# Allow list validation
input_value = 'GBP'
raise StandardError, "Invalid currency!" unless %w[USD EUR JPY].include?(input_value)
```
- **What it demonstrates**: Rejecting any value not explicitly enumerated as valid — the strongest validation strategy.

```python
# Luhn algorithm for credit card number validation
def is_valid_credit_card_number(card_number):
    def digits_of(n):
        return [int(d) for d in str(n)]
    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d * 2))
    return bool(checksum % 10)
```
- **What it demonstrates**: Domain-specific structural validation beyond simple regex, rejecting malformed credit card numbers immediately.

```sql
-- Vulnerable: string-concatenated query with attacker-supplied email = "'; DROP TABLE USERS --"
SELECT * FROM users WHERE email = ''; DROP TABLE USERS --'
```
```java
// Fixed: parameterized statement lets the driver escape safely
PreparedStatement stmt = connection.prepareStatement(
    "SELECT * FROM users WHERE email = ?");
stmt.setString(1, email);
```
- **What it demonstrates**: The classic SQL injection root cause (string concatenation) versus the fix (parameterized/prepared statements).

```python
# Vulnerable: shell=True with concatenated input allows command chaining
from subprocess import run
response = run("cat " + input_value, shell=True)
# attacker supplies: file.txt && rm -rf /

# Fixed: shell=False with argument list avoids shell metacharacter interpretation
from subprocess import run
response = run(["cat", input_value], shell=False)
```
- **What it demonstrates**: Command injection via shell string concatenation versus the fix using an argument-list API that bypasses shell interpretation entirely.

## Reference Tables
| Data type | Regex pattern (illustrative) |
|---|---|
| ISO date (`2032-08-17T00:00:00`) | `\d{4}-[01]\d-[0-3]\dT[0-2]\d:[0-5]\d:[0-5]\d([+-][0-2]\d:[0-5]\d|Z)` |
| IPv4 address (`125.0.0.3`) | `((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}` |
| IPv6 address (`2001:0db8:...`) | `([0-9A-Fa-f]{0,4}:){2,7}([0-9A-Fa-f]{1,4}$|...)` |

| Request | Action |
|---|---|
| `GET /books` | Retrieves a list of books |
| `GET /books/9780393972832` | Retrieves a specific book |
| `PUT /books` | Creates a book |
| `POST /books/38429` | Edits a particular book |
| `DELETE /books/9780393972832` | Deletes a specific book |

**Defense-in-depth checklist for injection attacks:**
1. Use parameterized statements when connecting to the database.
2. Validate all HTTP inputs against an allow list, pattern match, or block list.
3. Connect to the database as an account with limited permissions.
4. Validate that each database response has the expected form.
5. Log database calls and monitor for unusual activity.

## Worked Example
A team is building the account-deletion feature for the Breddit baking forum and needs to secure both the input path (the confirmation form) and the output paths (rendering the confirmation page, writing to the database).

1. **Input validation**: The delete-confirmation form takes a "type DELETE to confirm" text field. Rather than pattern-matching loosely, the team uses an allow list of exactly one valid value (`"DELETE"`), rejecting anything else outright — the strongest possible validation for a single expected value.
2. **HTTP verb correction**: The original implementation (mistakenly) mapped account deletion to a GET request:
   ```python
   @app.route('/profile/delete', methods=['GET'])
   def delete_account():
       ...
   ```
   A reviewer flags this immediately: because GET requests are triggerable by a bare hyperlink, an attacker could embed `<img src="https://breddit.com/profile/delete">` or a shortened link in a forum comment, and any logged-in user who merely *views* that comment would have their account deleted — a CSRF-by-GET vulnerability. The team changes the route to `methods=['POST']` and updates the client-side form's `method="post"` accordingly.
3. **Database escaping**: The delete operation itself,
   ```python
   db.execute('delete from users where id = ?', user['id'])
   ```
   already uses a parameterized placeholder (`?`) rather than string-interpolating `user['id']` directly into the SQL string, so even if `id` were ever attacker-influenced, it can't be used to inject additional SQL.
4. **Least-privilege database account**: The application's database connection uses an account that has DELETE and UPDATE privileges on the `users` table but no privilege to alter table structure (no `DROP`/`ALTER`), so even a hypothetical injection that slipped past parameterization would be unable to drop the table entirely.
5. **REST cleanup**: While fixing the verb, the team also renames the route from the legacy `/profile/delete` naming to a RESTful `DELETE /users/{id}` endpoint pattern, removing the implementation-revealing `/profile/` prefix and aligning verb and action.
6. **Defense in depth applied together**: Even if one layer were bypassed — say a future refactor reintroduces string concatenation in a different query — the limited-privilege database account, the input allow list, and the correct HTTP verb each independently reduce the blast radius, rather than the whole feature depending on any single control being perfect.

## Key Takeaways
1. Prefer allow lists over pattern matching over block lists, in that order of strength, for every input.
2. Validate file uploads by magic bytes/type, not filename extension, and always cap upload size.
3. Client-side validation is a UX feature only — never treat it as a security control.
4. Escape output per-context: HTML escaping, SQL parameterization, and shell argument-list APIs are three different mechanisms for three different injection classes.
5. Never build SQL or shell commands via string concatenation with untrusted input — always use parameterized statements or structured argument-list APIs.
6. Map every action to its semantically correct HTTP verb; GET must never mutate state, or it becomes trivially CSRF-able.
7. Combine defense in depth (multiple independent layers) with least privilege (minimal permissions per component) so no single failure is catastrophic.

## Connects To
- **Ch 6**: This chapter's brief walkthrough of GET-based CSRF and HTML escaping is expanded into the full cross-site scripting and cross-site request forgery treatments (anti-CSRF tokens, SameSite cookies).
- **Ch 12 (external)**: The book's dedicated Injection Vulnerabilities chapter goes deeper into SQL and command injection variants beyond this chapter's introduction.
- **Ch 13 (external)**: The URL-cleanliness principle ("don't leak implementation details") connects to that chapter's broader treatment of information leakage about your technology stack.
