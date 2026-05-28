# Research: Configuring the OpenSearch MCP Server in AWS Kiro Without uv/uvx

## Summary

AWS has an official open-source OpenSearch MCP server (`opensearch-mcp-server-py`) maintained under the `opensearch-project` GitHub organization, with first-class documentation for Kiro. All official examples default to `uvx`, but the package installs cleanly via `pip` or `pipx` and can be invoked as either `opensearch-mcp-server-py` (the installed script entry point) or `python -m mcp_server_opensearch`. Kiro's MCP config format is nearly identical to Claude Desktop's but lives at a different path (`.kiro/settings/mcp.json`), uses `url` (not `"type": "sse"`) for remote servers, and has a known bug where the Kiro CLI does not interpolate `${VAR}` syntax — the IDE does. The biggest practical risk is PATH resolution: Kiro spawns MCP subprocesses from its own install directory, so using absolute paths for `command` is essential.

---

## Key Findings

### 1. Available OpenSearch MCP Packages

**The official package** is [`opensearch-mcp-server-py`](https://pypi.org/project/opensearch-mcp-server-py/), maintained by the `opensearch-project` organization. Current version: **0.9.0** (March 24, 2026). Requires Python 3.10+. The AWS OpenSearch Service Developer Guide has a dedicated page confirming it is the intended bridge between both AWS products. [OpenSearch MCP server — Amazon OpenSearch Service docs](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/opensearch-mcp-server.html)

**Nine default tools:** `ListIndexTool`, `IndexMappingTool`, `SearchIndexTool`, `GetShardsTool`, `ClusterHealthTool`, `CountTool`, `ExplainTool`, `MsearchTool`, `GenericOpenSearchApiTool`. [GitHub — opensearch-project/opensearch-mcp-server-py](https://github.com/opensearch-project/opensearch-mcp-server-py)

**Other packages (non-official):**
- [`opensearch-mcp`](https://pypi.org/project/opensearch-mcp/) — community package, separate project
- [`@mseep/mcp-opensearch-js`](https://www.npmjs.com/package/@mseep/mcp-opensearch-js) — npm, scoped to Wazuh security logs, not general OpenSearch
- [`elasticsearch-mcp-server`](https://pypi.org/project/elasticsearch-mcp-server/) — Elasticsearch-compatible, works with OpenSearch, third-party

---

### 2. Kiro MCP Configuration: File Locations and JSON Format

**Config file paths** ([Kiro MCP Configuration docs](https://kiro.dev/docs/mcp/configuration/)):

| Scope | Path |
|---|---|
| Project (workspace) | `.kiro/settings/mcp.json` |
| User (global) | `~/.kiro/settings/mcp.json` |

Workspace settings take precedence over user-level settings.

**Local (stdio) server schema:**
```json
{
  "mcpServers": {
    "server-name": {
      "command": "command-to-run-server",
      "args": ["arg1", "arg2"],
      "env": { "KEY": "value" },
      "disabled": false,
      "autoApprove": ["tool_name"],
      "disabledTools": ["tool_name"]
    }
  }
}
```

**Remote (HTTP/SSE) server schema — no `"type"` field needed, auto-detected:**
```json
{
  "mcpServers": {
    "server-name": {
      "url": "https://your-mcp-endpoint",
      "headers": { "Authorization": "${API_TOKEN}" },
      "disabled": false,
      "autoApprove": ["tool_name"]
    }
  }
}
```

**Differences from Claude Desktop:**
- Config path: `.kiro/settings/mcp.json` vs. Claude Desktop's app data folder
- Kiro adds `disabledTools` (per-server tool blocklist) — not in Claude Desktop
- Kiro supports `autoApprove` arrays to skip confirmation dialogs
- Kiro supports first-class `url`-based remote servers; Claude Desktop does not natively

---

### 3. Concrete Kiro Config JSON for OpenSearch — Without uv/uvx

**Method A: pip install + script entry point (recommended for simplicity)**

Install once:
```bash
pip install opensearch-mcp-server-py
```

The `[project.scripts]` in `pyproject.toml` maps `opensearch-mcp-server-py` → `mcp_server_opensearch:main`.

**Kiro mcp.json (OpenSearch Service domain, IAM/AWS profile):**
```json
{
  "mcpServers": {
    "opensearch": {
      "command": "/absolute/path/to/opensearch-mcp-server-py",
      "args": [],
      "env": {
        "OPENSEARCH_URL": "https://your-domain.us-east-1.es.amazonaws.com",
        "AWS_REGION": "us-east-1",
        "AWS_PROFILE": "your-aws-profile"
      }
    }
  }
}
```

**Kiro mcp.json (basic auth):**
```json
{
  "mcpServers": {
    "opensearch": {
      "command": "/absolute/path/to/opensearch-mcp-server-py",
      "args": [],
      "env": {
        "OPENSEARCH_URL": "https://your-domain-endpoint",
        "OPENSEARCH_USERNAME": "admin",
        "OPENSEARCH_PASSWORD": "${OPENSEARCH_PASSWORD}"
      }
    }
  }
}
```

**Kiro mcp.json (OpenSearch Serverless):**
```json
{
  "mcpServers": {
    "opensearch": {
      "command": "/absolute/path/to/opensearch-mcp-server-py",
      "args": [],
      "env": {
        "OPENSEARCH_URL": "https://collection-id.us-east-1.aoss.amazonaws.com",
        "AWS_OPENSEARCH_SERVERLESS": "true",
        "AWS_REGION": "us-east-1",
        "AWS_PROFILE": "your-aws-profile"
      }
    }
  }
}
```

**Method B: pipx install (isolated env, cleanly resolves PATH problem)**
```bash
pipx install opensearch-mcp-server-py
# Binary at: ~/.local/bin/opensearch-mcp-server-py
```

```json
{
  "mcpServers": {
    "opensearch": {
      "command": "/Users/yourname/.local/bin/opensearch-mcp-server-py",
      "args": [],
      "env": { "OPENSEARCH_URL": "...", "OPENSEARCH_USERNAME": "admin", "OPENSEARCH_PASSWORD": "${OPENSEARCH_PASSWORD}" }
    }
  }
}
```

**Method C: python -m (most explicit, works with any pip-installed Python env)**
```json
{
  "mcpServers": {
    "opensearch": {
      "command": "/usr/bin/python3",
      "args": ["-m", "mcp_server_opensearch"],
      "env": {
        "OPENSEARCH_URL": "https://your-domain-endpoint",
        "OPENSEARCH_USERNAME": "admin",
        "OPENSEARCH_PASSWORD": "${OPENSEARCH_PASSWORD}"
      }
    }
  }
}
```

Use `which python3` (macOS/Linux) or `where python` (Windows) to find the absolute path.

**Method D: SSE/Streaming remote transport (run server separately, connect via URL)**

Start the server first:
```bash
python -m mcp_server_opensearch --transport stream --host 0.0.0.0 --port 9900
```

Kiro config (no `command` needed):
```json
{
  "mcpServers": {
    "opensearch": {
      "url": "http://localhost:9900/sse",
      "headers": {}
    }
  }
}
```

**Method E: Multi-cluster mode with YAML config**

`clusters.yml`:
```yaml
version: "1.0"
clusters:
  dev:
    opensearch_url: "http://localhost:9200"
    opensearch_username: "admin"
    opensearch_password: "admin123"
  prod:
    opensearch_url: "https://prod.us-east-1.es.amazonaws.com"
    iam_arn: "arn:aws:iam::123456789012:role/OpenSearchRole"
    aws_region: "us-east-1"
    profile: "prod-profile"
```

Kiro mcp.json:
```json
{
  "mcpServers": {
    "opensearch": {
      "command": "/usr/bin/python3",
      "args": ["-m", "mcp_server_opensearch", "--mode", "multi", "--config", "/absolute/path/to/clusters.yml"],
      "env": {}
    }
  }
}
```

---

### 4. Kiro-Specific Quirks Around PATH and Environment Variables

**PATH is not inherited from your shell.** Kiro spawns MCP subprocesses from its own install directory, not from a login shell. Commands like `python3` or `opensearch-mcp-server-py` will only resolve in the minimal system PATH. ([Kiro GitHub issue — absolute paths required](https://github.com/kirodotdev/Kiro/issues/5659))

Find absolute paths with:
- macOS/Linux: `which opensearch-mcp-server-py` or `which python3`
- Windows: `where.exe python` or `where.exe opensearch-mcp-server-py`

**`${VAR}` interpolation works in Kiro IDE but NOT in Kiro CLI.** The Kiro IDE expands `${OPENSEARCH_PASSWORD}` in `env` blocks. The `kiro-cli` passes the literal string unchanged — open bug. ([GitHub issue #5988](https://github.com/kirodotdev/Kiro/issues/5988))

Workaround for Kiro CLI: export credentials as actual shell environment variables before launching `kiro-cli`.

**Kiro auto-reconnects** after saving `mcp.json` — no restart required.

---

### 5. Remote/SSE MCP Transport Native Support in Kiro

- **Streamable HTTP** is the primary supported transport (current MCP spec)
- **HTTP+SSE** (deprecated MCP transport) is also supported for backward compatibility
- Remote servers are configured with a `url` field — Kiro infers transport from the URL; no `"type"` field needed
- Authentication via `headers` object (static values or `${VAR}` references)
- Dynamic client registration (OAuth browser sign-in) also supported for remote servers ([Kiro blog: Introducing remote MCP servers](https://kiro.dev/blog/introducing-remote-mcp/))

For OpenSearch, `python -m mcp_server_opensearch --transport stream --port 9900` starts an SSE-compatible endpoint at `http://localhost:9900/sse`. Run it in Docker for full isolation.

**Note: No official Docker image exists** for `opensearch-mcp-server-py`. A custom Dockerfile with `pip install opensearch-mcp-server-py` works, exposing port 9900 with `--transport stream`.

---

## Trade-offs / Caveats

- **All official Kiro config examples use `uvx`.** The pip-based configs above are derived from confirmed `[project.scripts]` entry point and `python -m mcp_server_opensearch` in USER_GUIDE — valid but not shown in official quick-start guides. [AWS OpenSearch Service IDE config page](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/mcp-server-configure-ide.html)
- **No official Docker image** for `opensearch-mcp-server-py` as of May 2026.
- **Kiro CLI `${VAR}` interpolation is broken** (open bug). Use actual shell environment variables when using the CLI. ([Issue #5988](https://github.com/kirodotdev/Kiro/issues/5988))
- **PATH resolution failure is the most common silent failure mode.** If the MCP server doesn't appear in Kiro's tool list, use absolute paths in `command`.
- **`--transport stream` requires a separately started server process** — unlike stdio mode, Kiro does not auto-launch the process for remote transports.
- **`opensearch-mcp` on PyPI** is a separate community package — prefer `opensearch-mcp-server-py` for AWS-supported use.

---

## Sources

- [OpenSearch MCP server — Amazon OpenSearch Service Developer Guide](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/opensearch-mcp-server.html) — official AWS docs confirming the server, auth modes, and Kiro usage
- [Configure in a coding IDE — Amazon OpenSearch Service](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/mcp-server-configure-ide.html) — official Kiro and Claude Code config JSON examples (uvx-based, authoritative structure)
- [opensearch-project/opensearch-mcp-server-py — GitHub](https://github.com/opensearch-project/opensearch-mcp-server-py) — source repo; USER_GUIDE.md confirms `python -m mcp_server_opensearch`, transport flags
- [opensearch-mcp-server-py — PyPI](https://pypi.org/project/opensearch-mcp-server-py/) — version 0.9.0, pip install, Python 3.10+
- [pyproject.toml — opensearch-mcp-server-py](https://raw.githubusercontent.com/opensearch-project/opensearch-mcp-server-py/main/pyproject.toml) — confirmed `opensearch-mcp-server-py` entry point → `mcp_server_opensearch:main`
- [MCP Configuration — Kiro IDE docs](https://kiro.dev/docs/mcp/configuration/) — file paths, JSON schema, `url`-based remote config, `autoApprove`, `disabledTools`
- [Model Context Protocol (MCP) — Kiro IDE docs](https://kiro.dev/docs/mcp/) — overview of Kiro MCP support
- [Introducing remote MCP servers — Kiro blog](https://kiro.dev/blog/introducing-remote-mcp/) — Streamable HTTP and deprecated HTTP+SSE support
- [GitHub issue #5988 — kiro-cli does not interpolate env vars in mcp.json](https://github.com/kirodotdev/Kiro/issues/5988)
- [GitHub issue #5659 — variable substitution in mcp.json](https://github.com/kirodotdev/Kiro/issues/5659) — absolute path context
- [Getting Started with Kiro and MCP Servers — AWS re:Post](https://repost.aws/articles/ARuX8rkojgSx-TYCc65JyAOw/getting-started-with-kiro-and-mcp-servers-connect-your-ai-ide-to-real-world-tools)
