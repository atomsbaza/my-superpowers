# Research: Configuring OceanBase MCP Server in AWS Kiro Without uv/uvx

## Summary

AWS Kiro (Amazon's AI-powered IDE) uses a JSON config file at `~/.kiro/settings/mcp.json` (global) or `.kiro/settings/mcp.json` (per-workspace) to define MCP servers. It supports both local stdio-based servers (launched as a subprocess via `command` + `args`) and remote HTTP-based servers (connected via `url`). Because Kiro is a GUI application, it does not inherit the user's shell `$PATH`, making absolute executable paths essential when not using `uv`/`uvx`. For the OceanBase MCP server (`oceanbase-mcp` on PyPI), the recommended no-uv approach is `pipx install oceanbase-mcp` (which places the console script at a fixed, known path) or a dedicated virtual environment. For remote transport, the **streamable-http** approach (not SSE) is the reliable path in Kiro due to a known bug where Kiro's transport client tries Streamable HTTP first and fails to fall back to SSE when the server returns 405.

---

## Key Findings

### 1. Kiro MCP Configuration — File Location and Format

Kiro uses a three-level hierarchy for MCP server configuration ([Kiro IDE MCP Configuration docs](https://kiro.dev/docs/mcp/configuration/)):

| Priority | File |
|---|---|
| Highest | `mcpServers` field inside an agent's `.kiro/agents/<name>.json` |
| Middle | `.kiro/settings/mcp.json` (workspace-level) |
| Lowest | `~/.kiro/settings/mcp.json` (user-global) |

When the same server name appears in two levels, the higher-priority entry completely overrides the lower one.

The top-level key is always `"mcpServers"`. Under it, **local servers** use `command`/`args`, and **remote servers** use `url`. Kiro's schema for remote servers has no `type` field — transport is auto-negotiated by the client ([Kiro Configuration docs](https://kiro.dev/docs/mcp/configuration/)). The `type: "sse"` / `type: "streamableHttp"` fields seen in OceanBase's README examples are **Cursor conventions**, not Kiro fields, and should be omitted in Kiro configs.

**Differences from Claude Desktop:** Claude Desktop also uses `mcpServers` with `command`/`args`/`env` but does not natively support remote URL-based servers. Kiro adds first-class `url` + `headers` remote server support and a per-agent override layer.

---

### 2. PATH / Environment Quirks in Kiro (GUI App)

Kiro is a GUI application and **does not inherit the user's shell `$PATH`** ([Kiro MCP PATH issue discussion](https://github.com/kirodotdev/Kiro/issues/6525)). This means:

- `"command": "python"` or `"command": "oceanbase_mcp_server"` **will fail** unless those names are resolvable in the minimal system `PATH`
- Always use **absolute paths** in `command` for both the executable and any file arguments
- Relative paths in `args` are resolved from Kiro's own install directory — a confirmed bug in Kiro v0.11.34+ ([Kiro issue #6525](https://github.com/kirodotdev/Kiro/issues/6525))
- The `env` block accepts `${VAR_NAME}` references to OS environment variables — use this for secrets

---

### 3. Installing OceanBase MCP Without uv/uvx

The package on PyPI is `oceanbase-mcp` and installs a console script named `oceanbase_mcp_server` (entry point: `oceanbase_mcp.server:main`). Python 3.10–3.12 is required (3.13+ excluded due to numpy/pyobvector constraint).

**Option A — pipx (recommended):**
```bash
pipx install oceanbase-mcp
# macOS/Linux: ~/.local/bin/oceanbase_mcp_server
# Windows:     %USERPROFILE%\.local\bin\oceanbase_mcp_server.exe
which oceanbase_mcp_server   # confirms the path
```

**Option B — dedicated venv:**
```bash
python3.11 -m venv ~/.venvs/oceanbase-mcp
~/.venvs/oceanbase-mcp/bin/pip install oceanbase-mcp
# Console script: ~/.venvs/oceanbase-mcp/bin/oceanbase_mcp_server
```

**Option C — python -m:** Use the full dotted module path `oceanbase_mcp.server` (not the README's `server` shortform, which requires a specific working directory):
```bash
/usr/bin/python3.11 -m oceanbase_mcp.server --help  # verify it works
```

---

### 4. Concrete Kiro mcp.json Examples (No uv/uvx)

**Method A — stdio via pipx (simplest, preferred):**
```json
{
  "mcpServers": {
    "oceanbase": {
      "command": "/Users/yourname/.local/bin/oceanbase_mcp_server",
      "args": [],
      "env": {
        "OB_HOST": "127.0.0.1",
        "OB_PORT": "2881",
        "OB_USER": "${OB_USER}",
        "OB_PASSWORD": "${OB_PASSWORD}",
        "OB_DATABASE": "your_database"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

Windows path variant — replace `command` with:
`"C:\\Users\\yourname\\.local\\bin\\oceanbase_mcp_server.exe"`

**Method B — stdio via venv Python binary:**
```json
{
  "mcpServers": {
    "oceanbase": {
      "command": "/Users/yourname/.venvs/oceanbase-mcp/bin/python",
      "args": ["-m", "oceanbase_mcp.server"],
      "env": {
        "OB_HOST": "127.0.0.1",
        "OB_PORT": "2881",
        "OB_USER": "${OB_USER}",
        "OB_PASSWORD": "${OB_PASSWORD}",
        "OB_DATABASE": "your_database"
      },
      "disabled": false
    }
  }
}
```

**Method C — stdio via system Python:**
```json
{
  "mcpServers": {
    "oceanbase": {
      "command": "/usr/bin/python3.11",
      "args": ["-m", "oceanbase_mcp.server"],
      "env": {
        "OB_HOST": "127.0.0.1",
        "OB_PORT": "2881",
        "OB_USER": "${OB_USER}",
        "OB_PASSWORD": "${OB_PASSWORD}",
        "OB_DATABASE": "your_database"
      },
      "disabled": false
    }
  }
}
```

---

### 5. SSE / Streamable-HTTP Approach (Run Server Separately, Connect via URL)

This decouples the server process from Kiro's lifecycle. Start the server once, then Kiro connects via HTTP.

**Start the server (terminal, separate from Kiro):**
```bash
# Streamable HTTP (RECOMMENDED for Kiro — avoid SSE due to known bug)
OB_HOST=127.0.0.1 OB_PORT=2881 OB_USER=root OB_PASSWORD=secret OB_DATABASE=mydb \
  /Users/yourname/.local/bin/oceanbase_mcp_server \
  --transport streamable-http --port 8000
# Server listens at http://localhost:8000/mcp
```

**Kiro mcp.json for Streamable HTTP:**
```json
{
  "mcpServers": {
    "oceanbase-http": {
      "url": "http://localhost:8000/mcp",
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

**SSE workaround (if you must use SSE):** Kiro's `rmcp` client tries Streamable HTTP first. When an SSE-only server returns 405, it fails rather than falling back. Route via `mcp-remote` as a bridge:
```json
{
  "mcpServers": {
    "oceanbase-sse": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "http://localhost:8000/sse"],
      "disabled": false
    }
  }
}
```
([Kiro issue #6663](https://github.com/kirodotdev/Kiro/issues/6663))

---

### 6. Remote/SSE Transport Native Support in Kiro

Kiro v0.5 (October 2025) added native remote MCP support for both **Streamable HTTP** (primary) and **HTTP+SSE** (deprecated but supported). The `url`-based remote config auto-negotiates — no `"type"` field needed. HTTP (non-HTTPS) is permitted for localhost. ([Kiro changelog v0.5](https://kiro.dev/changelog/ide/0-5/))

---

## Trade-offs / Caveats

- **SSE fallback is unreliable.** Prefer `--transport streamable-http` over `--transport sse` when running the server in remote mode. ([Kiro issue #6663](https://github.com/kirodotdev/Kiro/issues/6663))
- **`type` field is Cursor-specific.** The OceanBase README's `"type": "sse"` examples are Cursor conventions — omit them in Kiro configs.
- **`python -m server` is a footgun.** Use `python -m oceanbase_mcp.server` (full dotted path), not the README's `python3 -m server`.
- **Python version constraint is strict.** Python 3.10–3.12 only; 3.13+ fails at install.
- **Relative paths in args break on Kiro** (bug v0.11.34+). Always use absolute paths. ([Kiro issue #6525](https://github.com/kirodotdev/Kiro/issues/6525))
- **All first-party README examples use `uv`.** These pip/venv configs are derived from `pyproject.toml` entry-point metadata, not official Kiro+OceanBase examples.
- **Workspace config vs. global config:** Use `env` with `${VAR_NAME}` and never commit raw passwords.

---

## Sources

- [Kiro IDE MCP Configuration](https://kiro.dev/docs/mcp/configuration/) — schema, file locations, `env` expansion syntax
- [Kiro CLI MCP Configuration](https://kiro.dev/docs/cli/mcp/configuration/) — CLI-side config hierarchy
- [Kiro Troubleshooting](https://kiro.dev/docs/troubleshooting/) — PATH/shell integration issues
- [Kiro Changelog v0.5 — Remote MCP](https://kiro.dev/changelog/ide/0-5/) — Streamable HTTP + HTTP+SSE support
- [Kiro Blog: Introducing Remote MCP Servers](https://kiro.dev/blog/introducing-remote-mcp/) — transport protocol details
- [Kiro issue #6663: SSE-only servers fail to connect](https://github.com/kirodotdev/Kiro/issues/6663) — rmcp Streamable-HTTP-first bug, mcp-remote workaround
- [Kiro issue #6525: Relative paths resolve from Kiro install directory](https://github.com/kirodotdev/Kiro/issues/6525) — absolute paths required in args
- [OceanBase MCP Server README](https://github.com/oceanbase/awesome-oceanbase-mcp/blob/main/src/oceanbase_mcp_server/README.md) — transport modes, CLI flags, env vars
- [OceanBase MCP pyproject.toml](https://raw.githubusercontent.com/oceanbase/awesome-oceanbase-mcp/main/src/oceanbase_mcp_server/pyproject.toml) — console script name, entry point, Python version bounds
- [AWS Builder Center: MCP Server Integration with Kiro IDE](https://builder.aws.com/content/39Dijw7QtT42XRmMkbex9Kz2AZu/mcp-server-integration-with-kiro-ide-local-python-setup-guide) — absolute paths and venv Python in Kiro MCP configs
