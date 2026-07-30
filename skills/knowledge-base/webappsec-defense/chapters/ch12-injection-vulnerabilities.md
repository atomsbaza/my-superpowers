# Chapter 12: Injection Vulnerabilities

## Core Idea
Injection attacks subvert the intended meaning of a command — code, SQL, NoSQL, LDAP, OS shell, log line, or regex — by letting attacker-supplied data be interpreted as command syntax rather than as pure data; the fix is always structured parameterization, never string concatenation.

## Frameworks Introduced
- **Parameterized/prepared statements**: pass the command template and the values to the database driver separately so the driver — not string concatenation — inserts values safely.
  - When to use: every database query (SQL or NoSQL) that incorporates any value from an untrusted source.
  - How: use placeholders (`%s`, `?`, named params) and pass values as a separate argument tuple/array to `execute()`/`prepareStatement()`, never interpolate values into the query string.
- **Structured process-invocation APIs (anti command-injection)**: pass command arguments as a list/array to the OS process API instead of building a shell command string.
  - When to use: any time application code must invoke an OS-level command (e.g., `nslookup`).
  - How: `subprocess.run(["nslookup", domain])` (Python), `child_process.spawn('nslookup', [domain])` (Node), `Runtime.getRuntime().exec(new String[]{"nslookup", domain})` (Java) — each avoids a shell interpreting attacker-controlled metacharacters like `&&`.
- **Sandboxed/formally-parsed DSLs (anti RCE)**: never use raw dynamic evaluation (`eval()`) to run a domain-specific language; either embed a purpose-built sandboxed language, or parse the DSL grammar explicitly.
  - When to use: any feature offering users an expression language (search filters, spreadsheet-like formulas).
  - How: embed Lua via `lupa` with explicit control over what context is exposed to the runtime, or use a grammar/AST-based evaluator (Python's `ast` module) that explicitly enumerates permitted operations.

## Key Concepts
- **RCE (remote code execution)**: an attacker causes arbitrary code to run on the server, typically via dynamic evaluation of untrusted input (`eval()`) or unsafe server-side includes.
- **DSL (domain-specific language)**: a small, tailored expression language (e.g., search operators, spreadsheet formulas) that needs its own safe evaluation strategy rather than generic dynamic evaluation.
- **SQL injection**: constructing a SQL command via string concatenation/interpolation of untrusted input, letting an attacker change the command's meaning (e.g., appending `' --` to bypass a password check).
- **ORM (leaky abstraction)**: object-relational mappers auto-parameterize most queries, but still allow raw/interpolated SQL fragments where developers "color outside the lines" — those fragments remain injectable.
- **NoSQL injection**: the SQL-injection pattern applied to non-relational stores (MongoDB, Couchbase, Cassandra) via their own low-level/string-based query APIs.
- **LDAP injection**: unescaped user input incorporated into an LDAP filter string, letting an attacker supply wildcard characters (`*`) to bypass authentication checks.
- **CRLF injection / log injection / HTTP response splitting**: injecting carriage-return/line-feed characters to forge fake log lines or to terminate an HTTP header section early and smuggle attacker content into the response body.
- **ReDoS (regular expression denial of service)**: a maliciously crafted "evil regex" or input string that forces catastrophic backtracking in a regex engine, exhausting server CPU.

## Mental Models
- Think of every database/OS/directory command as having two channels — the command's *structure* and the *data* flowing through it — and injection is what happens when those channels get merged into one string.
- Treat any place your code builds a command string by concatenation as suspect by default; the presence of `+`, string interpolation, or f-strings feeding into a query/command is the smell to search for in review.
- Use Elasticsearch (or similar) instead of ever exposing raw user-supplied regex — "rich search syntax" is a solved problem that doesn't require accepting attacker-authored patterns.

## Anti-patterns
- **`eval()` on untrusted input**: whether raw JS request bodies or DSL expressions, dynamic evaluation of attacker-controlled strings is the direct path to RCE.
- **Server-side includes from a remote/attacker-controlled URL**: PHP's `include` (and similar) supporting remote protocols lets an attacker inject arbitrary remote code if the include target comes from the request.
- **String-concatenated SQL/NoSQL/LDAP/OS commands**: the root cause of essentially every injection variant in this chapter — always parameterize instead.
- **Manual ORM string interpolation**: Rails' `Book.where("isbn = '#{isbn}'")` reintroduces SQL injection despite using an ORM; use `Book.where(["isbn = ?", isbn])` instead.
- **Unsanitized newlines in logs or HTTP headers**: lets attackers forge fake log entries (hiding brute-force attempts) or split HTTP responses to inject malicious content.
- **Accepting user-defined regex patterns**: opens the door to ReDoS; static analysis tools (e.g., SonarSource rule RSPEC-2631) can flag this pattern in CI.

## Code Examples
```python
# Vulnerable: string concatenation
sql  = "SELECT * FROM users WHERE username = '" + username + "' and password_hash = '" + hash + "'"
user = cursor.execute(sql).fetchone()
# Attack: username = "admin' --" bypasses the password check entirely

# Fixed: parameterized statement
sql = "SELECT * FROM users WHERE username = %s and password_hash = %s"
user = cursor.execute(sql, (username, hash)).fetchone()
```
- **What it demonstrates**: classic SQL injection via string concatenation, and the parameterized-statement fix that prevents the attacker from altering query structure.

```java
Connection connection = DriverManager.getConnection(URL, USER, PASS);
String sql = "SELECT * FROM users WHERE username = ?";
PreparedStatement stmt = connection.prepareStatement(sql);
stmt.setString(1, email);
ResultSet results = stmt.executeQuery(sql);
```
- **What it demonstrates**: Java's prepared-statement equivalent of parameterized queries.

```ruby
# Vulnerable ORM usage (string interpolation)
def find_book
  isbn         = params[:isbn]
  where_clause = "isbn = '#{isbn}'"
  @book        = Book.where(where_clause)
end

# Fixed
Book.where(["isbn = ?", isbn])
Book.where(["isbn = :isbn", { isbn: isbn }])
```
- **What it demonstrates**: an ORM (Rails) is only as safe as its usage — manual string interpolation reintroduces SQL injection even through an ORM.

```python
import escape_filter_chars from ldap.filter
def validate_credentials(username, password):
    esc_user   = escape_filter_chars(username)
    esc_pass   = escape_filter_chars(password)
    ldap_query = f"(&(uid={esc_user})(userPassword={esc_pass}))"
    connection = ldap.initialize("ldap://127.0.0.1:389")
    user       = connection.search_s("dc=example,dc=com", ldap.SCOPE_SUBTREE, ldap_query)
    return user.length == 1
```
- **What it demonstrates**: escaping LDAP filter special characters to prevent wildcard-based authentication bypass.

```python
from subprocess import run
run(["ns_lookup", domain])
```
- **What it demonstrates**: passing command arguments as a list to `subprocess.run()`, avoiding shell interpretation of attacker-controlled metacharacters like `&&`.

## Reference Tables
| Language | Command-injection-safe invocation |
|---|---|
| Python | `subprocess.run(["nslookup", domain])` |
| Ruby | `Shellwords.escape(domain)` before shell invocation |
| Node.js | `child_process.spawn('nslookup', [domain])` |
| Java | `Runtime.getRuntime().exec(new String[]{"nslookup", domain})` |
| .NET | `ProcessStartInfo` with structured `FileName`/`Arguments` |
| PHP | `escapeshellcmd($domain)` before `system()` |

| NoSQL store | Safe query pattern |
|---|---|
| MongoDB | `books.find_one({"isbn": isbn})` — avoid the low-level command-string API |
| Couchbase | `cluster.query("select * from books where isbn = $1", isbn)` (parameterized) |
| Cassandra | `session.prepare("update books set ... where isbn = ?")` (prepared statement) |
| HBase | Row-key based access; ensure attacker can't manipulate row keys directly |

## Worked Example
A DNS-lookup web page runs `nslookup <domain>` on the server and prints the result, building the command via string concatenation with the `domain` query parameter. An attacker supplies `example.com && cat /etc/passwd` as the domain value. Because `&&` is a shell chaining operator on Linux and the input was never sanitized, the server executes both `nslookup example.com` and `cat /etc/passwd`, returning the contents of a sensitive system file in the HTTP response — with a persistent attacker, this same gap could be leveraged to install ransomware.

The fix follows the chapter's two-option framework: prefer avoiding the OS invocation entirely (e.g., use a DNS library instead of shelling out to `nslookup`); if invocation is unavoidable, use the structured array-based process API for the language in use — e.g., Python's `subprocess.run(["nslookup", domain])` — which passes `domain` as a single, non-interpreted argument, so `&&` and other metacharacters lose all special meaning and are treated as literal (and invalid) hostname characters.

## Key Takeaways
1. Never dynamically execute untrusted input as code; sandbox any DSL with an embedded language or explicit grammar parser instead of `eval()`.
2. Disable remote-URL server-side includes in any template language that supports them.
3. Always use parameterized/prepared statements for SQL and NoSQL queries — including inside ORMs, where manual string interpolation reintroduces the same risk.
4. When dynamic query construction is unavoidable (e.g., `ORDER BY` clauses), validate the input against a strict allow list rather than parameterizing.
5. Avoid shelling out to OS commands where possible; when unavoidable, use structured argument-list APIs, never string-concatenated shell commands.
6. Strip CR/LF characters from untrusted input before it reaches logs or HTTP response headers to prevent log forgery and response splitting.
7. Never accept user-supplied regex patterns; route rich search needs through a dedicated search index like Elasticsearch instead.

## Connects To
- **Ch 11**: payload vulnerabilities (deserialization, mass assignment) and injection vulnerabilities both stem from trusting attacker-controlled data to define structure, not just content.
- **Ch 13**: injection-prone libraries/ORMs are exactly the kind of third-party dependency that needs CVE-tracking and prompt patching.
- **Ch 8**: the SQL-injection login-bypass example directly parallels the timing/enumeration issues in authentication — both stem from insufficiently defensive login-handling code.
