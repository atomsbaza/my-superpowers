# Research: Using opensearch-mcp-server-py with Claude Code CLI (No uv/uvx)

## Summary

The `opensearch-mcp-server-py` package from the `opensearch-project` GitHub org is a standard PyPI wheel that installs via `pip`, `pipx`, or a plain Python venv — uv/uvx are only a convenience default in the vendor docs and are not required. Once installed, it exposes two console scripts (`opensearch-mcp-server` for stdio and `opensearch-mcp-server-streaming` for SSE/HTTP) and is also runnable as a Python module via `python -m mcp_server_opensearch`. Claude Code's `claude mcp add` CLI supports stdio subprocess launch and native remote SSE/HTTP transports, and project-scoped configuration lives in a `.mcp.json` file at the repo root. Authentication is entirely driven by environment variables covering basic auth, IAM SigV4, and OpenSearch Serverless.

---

## Key Findings

### 1. Installation Without uv/uvx

The package is a regular wheel on PyPI. Three safe alternatives to uvx:

**pipx (recommended replacement for uvx):**
```bash
pipx install opensearch-mcp-server-py
```
Creates an isolated venv automatically and places `opensearch-mcp-server` and `opensearch-mcp-server-streaming` on PATH.

**Plain Python venv (most robust for GUI-launched Claude Code):**
```bash
python3 -m venv ~/.venvs/opensearch-mcp
~/.venvs/opensearch-mcp/bin/pip install opensearch-mcp-server-py
```
Use the absolute venv path in Claude Code config so that shell PATH issues never interfere.

**System pip (quick but less isolated):**
```bash
pip install --user opensearch-mcp-server-py
```
On macOS with PEP 668 enforcement you may need `--break-system-packages`; prefer pipx or a venv.

After any of the above, three equivalent launch forms exist:
- `opensearch-mcp-server` (stdio console script)
- `opensearch-mcp-server-streaming` (SSE/HTTP console script)
- `python -m mcp_server_opensearch` (module form, useful when scripts are not on PATH)

Sources: [PyPI: opensearch-mcp-server-py](https://pypi.org/project/opensearch-mcp-server-py/), [GitHub README](https://github.com/opensearch-project/opensearch-mcp-server-py#readme)

---

### 2. `claude mcp add` CLI Commands

The general shape:
```bash
claude mcp add <name> [--scope local|user|project] \
  [-e KEY=VALUE ...] \
  [--transport stdio|sse|http] \
  -- <command> [args...]
```

The `--` separator is required when passing flags to the underlying command.

**Stdio via pipx-installed script (simplest):**
```bash
claude mcp add opensearch \
  -e OPENSEARCH_URL=https://localhost:9200 \
  -e OPENSEARCH_USERNAME=admin \
  -e OPENSEARCH_PASSWORD=admin \
  -- opensearch-mcp-server
```

**Stdio via absolute venv path (most reliable when PATH is restricted):**
```bash
claude mcp add opensearch \
  -e OPENSEARCH_URL=https://localhost:9200 \
  -e OPENSEARCH_USERNAME=admin \
  -e OPENSEARCH_PASSWORD=admin \
  -- /Users/yourname/.venvs/opensearch-mcp/bin/opensearch-mcp-server
```

**Stdio via `python -m` (fallback when console script is missing):**
```bash
claude mcp add opensearch \
  -e OPENSEARCH_URL=https://localhost:9200 \
  -e OPENSEARCH_USERNAME=admin \
  -e OPENSEARCH_PASSWORD=admin \
  -- /Users/yourname/.venvs/opensearch-mcp/bin/python3 -m mcp_server_opensearch
```

**IAM / AWS profile auth (managed OpenSearch Service):**
```bash
claude mcp add opensearch-aws \
  -e OPENSEARCH_URL=https://search-mydomain.us-east-1.es.amazonaws.com \
  -e AWS_REGION=us-east-1 \
  -e AWS_PROFILE=my-profile \
  -- /Users/yourname/.venvs/opensearch-mcp/bin/opensearch-mcp-server
```

**OpenSearch Serverless:**
```bash
claude mcp add opensearch-aoss \
  -e OPENSEARCH_URL=https://abcd1234.us-east-1.aoss.amazonaws.com \
  -e AWS_REGION=us-east-1 \
  -e AWS_PROFILE=my-profile \
  -e AWS_OPENSEARCH_SERVERLESS=true \
  -- /Users/yourname/.venvs/opensearch-mcp/bin/opensearch-mcp-server
```

Add `--scope project` to any of the above to write to `.mcp.json` so teammates share the config.

Sources: [Anthropic docs — Claude Code MCP](https://docs.claude.com/en/docs/claude-code/mcp), [AWS docs — OpenSearch MCP server](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/opensearch-mcp-server.html)

---

### 3. `.mcp.json` Project-Config Format

Claude Code uses a `.mcp.json` file at the project root for project-scoped servers. Top-level `mcpServers` object; stdio entries use `command`, `args`, `env`; remote entries use `type` and `url`.

**Basic auth, pipx-installed script:**
```json
{
  "mcpServers": {
    "opensearch": {
      "command": "opensearch-mcp-server",
      "args": [],
      "env": {
        "OPENSEARCH_URL": "https://localhost:9200",
        "OPENSEARCH_USERNAME": "admin",
        "OPENSEARCH_PASSWORD": "admin"
      }
    }
  }
}
```

**Basic auth, absolute venv path (avoids PATH issues):**
```json
{
  "mcpServers": {
    "opensearch": {
      "command": "/Users/yourname/.venvs/opensearch-mcp/bin/opensearch-mcp-server",
      "args": [],
      "env": {
        "OPENSEARCH_URL": "https://localhost:9200",
        "OPENSEARCH_USERNAME": "admin",
        "OPENSEARCH_PASSWORD": "admin"
      }
    }
  }
}
```

**IAM / AWS profile auth (managed OpenSearch Service):**
```json
{
  "mcpServers": {
    "opensearch-aws": {
      "command": "/Users/yourname/.venvs/opensearch-mcp/bin/python3",
      "args": ["-m", "mcp_server_opensearch"],
      "env": {
        "OPENSEARCH_URL": "https://search-mydomain.us-east-1.es.amazonaws.com",
        "AWS_REGION": "us-east-1",
        "AWS_PROFILE": "my-profile"
      }
    }
  }
}
```

**OpenSearch Serverless:**
```json
{
  "mcpServers": {
    "opensearch-aoss": {
      "command": "/Users/yourname/.venvs/opensearch-mcp/bin/opensearch-mcp-server",
      "args": [],
      "env": {
        "OPENSEARCH_URL": "https://abcd1234.us-east-1.aoss.amazonaws.com",
        "AWS_REGION": "us-east-1",
        "AWS_PROFILE": "my-profile",
        "AWS_OPENSEARCH_SERVERLESS": "true"
      }
    }
  }
}
```

Sources: [Anthropic docs — Claude Code MCP](https://docs.claude.com/en/docs/claude-code/mcp), [AWS docs — OpenSearch MCP server](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/opensearch-mcp-server.html), [GitHub USER_GUIDE.md](https://github.com/opensearch-project/opensearch-mcp-server-py/blob/main/USER_GUIDE.md)

---

### 4. Remote SSE / HTTP Transport (No uv/uvx, No Child Process)

Claude Code can connect to a separately running MCP server over SSE or streamable HTTP.

**Step 1 — Start the server (done once, out-of-band):**
```bash
OPENSEARCH_URL=https://localhost:9200 \
OPENSEARCH_USERNAME=admin \
OPENSEARCH_PASSWORD=admin \
opensearch-mcp-server-streaming --transport sse --host 127.0.0.1 --port 9900
```
Or via module form:
```bash
python -m mcp_server_opensearch --transport sse --host 127.0.0.1 --port 9900
```

**Step 2 — Register with Claude Code:**
```bash
# SSE
claude mcp add --transport sse opensearch http://localhost:9900/sse

# Streamable HTTP
claude mcp add --transport http opensearch http://localhost:9900/mcp
```

**Equivalent `.mcp.json` entries:**
```json
{
  "mcpServers": {
    "opensearch": {
      "type": "sse",
      "url": "http://localhost:9900/sse"
    }
  }
}
```
```json
{
  "mcpServers": {
    "opensearch": {
      "type": "http",
      "url": "http://localhost:9900/mcp"
    }
  }
}
```

Sources: [Anthropic docs — Claude Code MCP](https://docs.claude.com/en/docs/claude-code/mcp), [GitHub README — Transports](https://github.com/opensearch-project/opensearch-mcp-server-py#transports)

---

### 5. Required Environment Variables

| Variable | Auth type | Purpose |
|---|---|---|
| `OPENSEARCH_URL` | All | Full cluster endpoint, e.g. `https://localhost:9200` |
| `OPENSEARCH_USERNAME` | Basic auth | Username for HTTP basic auth |
| `OPENSEARCH_PASSWORD` | Basic auth | Password for HTTP basic auth |
| `AWS_REGION` | IAM / Serverless | AWS region for SigV4 request signing |
| `AWS_PROFILE` | IAM / Serverless | Named profile in `~/.aws/credentials`; omit to use default credential chain |
| `AWS_OPENSEARCH_SERVERLESS` | Serverless only | Set to `"true"` to sign with service `aoss` instead of `es` |
| `OPENSEARCH_NO_AUTH` | Dev/local only | `"true"` to skip authentication (insecure) |
| `OPENSEARCH_SSL_VERIFY` | Dev/local only | `"false"` to skip TLS cert verification (insecure) |

When both basic-auth and AWS variables are present, the server prefers SigV4 when `AWS_REGION` is set. AWS credentials resolve in standard chain order (explicit profile → environment key/secret → instance role → SSO) when `AWS_PROFILE` is omitted.

Sources: [AWS docs — OpenSearch MCP server](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/opensearch-mcp-server.html), [GitHub README — Environment variables](https://github.com/opensearch-project/opensearch-mcp-server-py#environment-variables)

---

## Trade-offs / Caveats

- **Absolute paths vs PATH.** Claude Code launched from a macOS GUI does not inherit your interactive `~/.zshrc` PATH. If `opensearch-mcp-server` is not found, use the absolute path from `which opensearch-mcp-server` or the venv's `bin/` directory.
- **Secrets in `.mcp.json`.** Committing `OPENSEARCH_PASSWORD` or AWS secret keys in a project `.mcp.json` exposes them in version control. Prefer `AWS_PROFILE` for AWS auth and `--scope user` for basic-auth secrets (written to `~/.claude.json` instead of the repo file).
- **Transport naming.** If `claude mcp add --transport http` returns an error in your Claude Code version, fall back to `--transport sse`. The SSE endpoint is `/sse` and the HTTP endpoint is `/mcp` by convention on `opensearch-mcp-server-streaming`.
- **`AWS_OPENSEARCH_SERVERLESS` must be the string `"true"`.** The server checks this exact value; `1`, `yes`, or `True` will not work.
- **Active development.** New transports, tool-allow-listing, and profile support were added through 2024–2025. Re-check the [README](https://github.com/opensearch-project/opensearch-mcp-server-py#readme) before pinning a production config.
- **pipx absolute path.** pipx scripts live in `~/.local/pipx/venvs/opensearch-mcp-server-py/bin/`. Find the real path via `which opensearch-mcp-server` after `pipx install`.

---

## Sources

- [AWS docs — OpenSearch MCP server](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/opensearch-mcp-server.html) — canonical env-var reference, managed service and Serverless config examples, transport options
- [GitHub: opensearch-project/opensearch-mcp-server-py](https://github.com/opensearch-project/opensearch-mcp-server-py) — installation, console-script entrypoints, `python -m` launch, transport flags, full env-var list
- [PyPI: opensearch-mcp-server-py](https://pypi.org/project/opensearch-mcp-server-py/) — confirms the package is a standard wheel installable via pip/pipx without uv
- [Anthropic docs — Claude Code MCP](https://docs.claude.com/en/docs/claude-code/mcp) — exact `claude mcp add` syntax, `-e KEY=VALUE`, `--transport sse|http`, `--scope local|user|project`, and `.mcp.json` schema
- [GitHub: opensearch-project/opensearch-mcp-server-py — USER_GUIDE.md](https://github.com/opensearch-project/opensearch-mcp-server-py/blob/main/USER_GUIDE.md) — Claude Desktop config examples (same JSON shape as Claude Code's `.mcp.json`) for basic auth, IAM, and Serverless
