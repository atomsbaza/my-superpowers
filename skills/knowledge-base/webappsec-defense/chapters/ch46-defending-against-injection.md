# Chapter 46: Defending Against Injection

## Core Idea
Injection — most commonly SQL injection, but extending to any CLI or interpreter fed user input — is best mitigated with prepared statements as the first line of defense, database-specific sanitizers as a secondary layer, and the Principle of Least Authority plus command allowlisting for any non-SQL interpreter surface.

## Frameworks Introduced
- **Prepared statements**: A two-step query execution model that compiles query intent before user data is ever considered, structurally preventing user data from changing the query's meaning.
  - When to use: As the first-line, default defense for any SQL query incorporating user-supplied data.
  - How: Compile the query with placeholder/bind variables first; then supply the actual values, which are substituted post-compilation and cannot alter the query structure — supported by virtually every major SQL database (MySQL, Oracle, PostgreSQL, MS SQL Server).
- **Principle of Least Authority (a.k.a. least privilege)**: Each module/component in a system should only have access to the data and functionality required for it to operate correctly.
  - When to use: When designing any component (especially CLIs or subprocesses) that interacts with user input, so a compromise stays contained.
  - How: Scope credentials, keys, and OS-level permissions narrowly per component rather than granting broad/admin access for convenience; accept the operational overhead (multiple accounts/keys) as the cost of containment.
- **Allowlisting commands (not blocklisting)**: When user input must translate into server-side command execution, restrict it to an explicitly vetted allowlist rather than trying to block known-bad commands.
  - When to use: Any time user-chosen commands must be executed on a server (CLI wrappers, task automation).
  - How: Maintain an array of allowed command names; reject any user-submitted command not in that array before invoking the underlying CLI; treat order/frequency constraints as a further refinement beyond simple name allowlisting.

## Key Concepts
- **SQL injection**: The most common and best-understood injection attack, occurring when user-supplied data alters the structure/intent of a SQL query sent as a raw string.
- **Bind variable / placeholder variable**: A stand-in (`?` or named parameter) in a prepared statement, filled with user data only after the query has already been compiled.
- **Command injection**: Injection that reaches the OS level rather than an application-level interpreter — distinguished from generic injection by its blast radius.
- **Database-specific sanitizer**: A vendor-provided escaping function (e.g., Oracle's `ESAPI.encoder().encodeForSQL()`, MySQL's `QUOTE()` or `mysql_real_escape_string()`) that escapes risky characters when a query cannot be parameterized.
- **High-risk injection targets**: Categories of components most likely to harbor injection vulnerabilities — task schedulers, compression/optimization libraries, remote backup scripts, databases, loggers, any call to the host OS, any interpreter or compiler.
- **Allowlist vs. blocklist**: An allowlist only accepts explicitly vetted commands/values; a blocklist rejects known-bad ones and is considered a security risk because new functionality can be added without updating the blocklist.

## Mental Models
- Think of prepared statements as "intent locked in before data arrives" — because the query is compiled prior to substitution, no amount of malicious user input can turn a SELECT into a DELETE or append a second statement.
- Treat database-specific sanitizers (ESAPI, `mysql_real_escape_string`) as a mitigation layer, not a comprehensive defense — use them only when a query genuinely cannot be parameterized.
- Use the Principle of Least Authority as blast-radius control: assume any component *will* eventually be compromised, and design so that compromise doesn't cascade — a CLI running as admin turns one rogue injection into a full server takeover, while a narrowly scoped CLI limits the damage to its own sandbox.
- Prefer allowlists over blocklists structurally, not just as a style preference: applications evolve, and a blocklist silently becomes unsafe the moment a new command is added that the blocklist author never anticipated.

## Anti-patterns
- **String-concatenated SQL queries**: `'SELECT name, barcode from products WHERE price <= ' + price + ';'` allows user input to change query structure entirely — always prefer a prepared statement instead.
- **Relying solely on database-specific escaping instead of prepared statements**: Escaping functions are a mitigation for cases where parameterization isn't possible, not a substitute for it.
- **Running CLI integrations with elevated/admin privileges**: A compromised low-privilege backup CLI stays contained; a compromised admin-level CLI can expose the entire application server.
- **Building a blocklist of disallowed commands for a user-facing CLI passthrough**: Silently becomes unsafe as new commands are added to the underlying CLI without corresponding blocklist updates.
- **Allowing literal client-to-server command execution at all**: The chapter calls this "a bad architectural practice" that "should be avoided at all costs" regardless of what filtering is layered on top.

## Code Examples
```sql
PREPARE q FROM 'SELECT name, barCode from products WHERE price <= ?';
SET @price = 12;
EXECUTE q USING @price;
DEALLOCATE PREPARE q;
```
- **What it demonstrates**: A MySQL prepared statement — the query is compiled with a `?` placeholder before `@price` is ever set, so no user-supplied value can alter the query's structure (e.g., appending `5; UPDATE users ...` has no effect since it isn't compiled).

```javascript
const commands = ['print', 'cut', 'copy', 'paste', 'refresh'];

/*
 * Accepts commands from the client, runs them against the CLI ONLY if
 * they appear in the allowlist array.
 */
const postCommands = function (req, res) {
  const userCommands = req.body.commands;
  userCommands.forEach((c) => {
    if (!commands.includes(c)) {
      return res.sendStatus(400);
    }
  });
  cli.run(req.body.commands);
};
```
- **What it demonstrates**: Allowlist-based command filtering before invoking a CLI wrapper — rejects any command not explicitly vetted, though it does not yet address order/frequency-based misuse of allowed commands.

```
ESAPI.encoder().encodeForSQL(new OracleCodec(), str);
```
- **What it demonstrates**: Oracle/Java's ESAPI-based database-specific SQL encoder, used as a secondary mitigation when a query cannot be parameterized.

## Reference Tables
### Injection Defense Layers

| Layer | Applies to | Coverage |
|---|---|---|
| Prepared statements | SQL specifically | First-line, most effective; near-complete against classic SQL injection |
| Database-specific sanitizers (ESAPI, `mysql_real_escape_string`, `QUOTE()`) | SQL specifically | Secondary mitigation when parameterization isn't possible |
| Principle of Least Authority | Any component/module, especially CLIs | Limits blast radius after a compromise, doesn't prevent the injection itself |
| Command allowlisting | Any user-input-to-CLI/interpreter path | Prevents unvetted command execution; blocklists rejected as unsafe long-term |

### High-Risk Injection Targets

| Category |
|---|
| Task schedulers |
| Compression/optimization libraries |
| Remote backup scripts |
| Databases |
| Loggers |
| Any call to the host OS |
| Any interpreter or compiler |

## Worked Example
A team builds a CLI-backed feature that automatically backs up user profile photos, invocable either manually from a terminal or via an adapter called from the main web application. Following the Principle of Least Authority, they scope this CLI's credentials narrowly: it can read/write only the profile-photo storage bucket and has no access to the broader database, user-credential store, or admin APIs — even though it would be more "convenient" to reuse an existing broad-access service account.

Later, a request-handling endpoint is added so support staff can trigger a small set of maintenance operations (`print`, `cut`, `copy`, `paste`, `refresh`) against this CLI from a web UI button. Rather than passing arbitrary user-submitted command strings straight to `cli.run()` — which would let any caller invoke any function the underlying `cli` library supports, including ones never intended for external use — the team allowlists the exact five command names in an array and rejects (400) any command not present in it, per the `postCommands` pattern shown above. They explicitly reject a blocklist approach because the underlying CLI library gets new commands added over time as it's upgraded, and a blocklist would need to be remembered and updated for every such change; the allowlist instead defaults new/unrecognized commands to rejected.

Some months later, a dependency update to the backup CLI introduces a bug that, if this had been designed with elevated privileges, could have been chained into broader filesystem access. Because the CLI was scoped under least authority from the start, the resulting incident is contained to the photo-storage bucket rather than cascading into the wider application server — the architectural decision made months earlier is what limited the blast radius, not any code fixed at incident time.

## Key Takeaways
1. Use prepared statements as the default, first-line defense for any SQL query touching user-supplied data.
2. Treat database-specific sanitizers as a secondary mitigation, only when true parameterization isn't achievable.
3. Search your codebase systematically for all SQL/DSL entry points (per-adapter imports), since multiple database libraries may coexist.
4. Apply the Principle of Least Authority to every component that touches user input, especially CLIs and subprocesses — scope credentials and OS permissions narrowly so a compromise stays contained.
5. Never allow literal client-supplied commands to reach a server-side interpreter; when user input must drive server-side operations, allowlist the exact vetted set of commands rather than blocklisting known-bad ones.
6. Extend injection defenses beyond SQL to any high-risk target: task schedulers, compression libraries, backup scripts, loggers, and any OS-level or interpreter call.

## Connects To
- **Chapter 28 (offense): Injection**: This chapter is the direct defense pairing for the SQL/command injection attacks (including the FFMPEG CLI example) constructed there.
- **Chapter 45: Defending Against XXE**: Both chapters address "attacker-controlled input reaching an interpreter" — XXE is injection into XML entity resolution, generalized here to SQL and CLI interpreters.
- **Chapter 42: Vulnerability Management**: Injection findings should be scored (SQL injection with database write access typically scores High/Critical on CVSS Integrity/Confidentiality) and regression-tested per that chapter's pipeline.
