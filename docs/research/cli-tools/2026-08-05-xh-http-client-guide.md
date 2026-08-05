# xh: a lightweight CLI HTTP client (Postman alternative)

**Repo:** https://github.com/ducaale/xh
**Why:** Postman's Electron app consumes significant hardware resources for simple API testing. `xh` is a Rust reimplementation of HTTPie — a single static binary, fast startup, no GUI overhead.

## Install

```bash
brew install xh
```

Use the Homebrew bottle, not the `curl … install.sh | sh` script in the README — the bottle is a signed, reviewable build from the tagged release.

## Security notes (from dependency audit, 2026-08-05)

- No known CVEs/advisories (OSV, GitHub security advisories both clean as of `v0.26.2`).
- TLS verification is on by default; delegated to rustls, not hand-rolled crypto.
- Reads `~/.netrc` by default (same as curl) — matters only if you keep credentials there. Suppress with `--ignore-netrc`.
- `--session <name>` writes **plaintext** JSON to `~/.config/xh/sessions/`, including raw auth credentials and cookies, at default umask permissions (world-readable). This is opt-in — nothing is persisted unless you pass `--session`. If you save an authenticated session, point it at a file inside a `chmod 700` directory instead of the default location.
- Trust surface: `curl` (preinstalled) < `xh` (single Rust binary) < httpie (Python + pip tree) < Bruno (Electron + npm tree).
- No request-collections feature — `--session` only persists cookies/auth, not saved/named requests. If you need Postman-style collections, `xh` doesn't replace that (Bruno would, at much higher trust cost).

## Basic usage

```bash
# GET
xh httpbin.org/get

# GET with query params
xh httpbin.org/get name==bob age==30

# POST with JSON body (default content-type is JSON)
xh POST httpbin.org/post name=bob age:=30

# note: `=` sends a string field, `:=` sends raw JSON (numbers, bools, arrays, objects)
xh POST httpbin.org/post active:=true tags:='["a","b"]'
```

## Headers, auth, query

```bash
# custom headers
xh httpbin.org/get X-Api-Key:secret123

# basic auth
xh -a user:pass httpbin.org/get

# bearer token
xh httpbin.org/get "Authorization:Bearer $TOKEN"

# form-encoded instead of JSON
xh --form POST httpbin.org/post name=bob
```

## Sessions (persist cookies/auth across requests)

```bash
# create/update a named session
xh --session=/path/to/safe-dir/my-session.json -a user:pass httpbin.org/get

# reuse it without re-auth
xh --session=/path/to/safe-dir/my-session.json httpbin.org/get

# read-only: use a session's state but don't overwrite it
xh --session-read-only=/path/to/safe-dir/my-session.json httpbin.org/get
```

Keep the session file's parent directory at `chmod 700` — see security notes above.

## Downloads

```bash
xh --download https://example.com/file.zip
# resumes automatically if the partial file already exists
```

## Interop with curl

```bash
# see the equivalent curl command instead of sending the request
xh --curl POST httpbin.org/post name=bob
```

Useful for sharing a request with someone who doesn't have `xh`, or pasting into a script that must not depend on it.

## Output control

```bash
xh -q httpbin.org/get        # quiet: suppress progress/headers noise
xh -v httpbin.org/get        # verbose: show the request as sent
xh -p=hb httpbin.org/get     # print only headers + body (no status/meta line)
```

## When to reach for something else

- Need saved, named, shareable request collections → Bruno (file-based, git-friendly), not xh.
- Scripting where you can't assume `xh` is installed → plain curl.
- Mocking a server or team-shared environments → xh has neither; use a dedicated tool.
