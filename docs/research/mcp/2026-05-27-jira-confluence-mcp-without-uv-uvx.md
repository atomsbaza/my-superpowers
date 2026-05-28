# Research: Using Jira and Confluence MCP Servers Without uv/uvx

## Summary

There are four practical, `uv`/`uvx`-free paths for running Jira and Confluence MCP servers with Claude: (1) run `sooperset/mcp-atlassian` via its official **Docker image**; (2) install it directly with **`pip`/`pipx`** and run the console-script entry point; (3) use the Node-based **`@aashari/mcp-server-atlassian-*`** packages with `npx`; and (4) connect to **Atlassian's official hosted Remote MCP Server** via the lightweight `mcp-remote` npm bridge, which requires no local Python or Docker at all. The Docker and `npx` routes avoid `uv` entirely; the Atlassian Remote MCP Server is the lightest option because it requires only Node and an OAuth browser flow, but it is Cloud-only.

---

## Key Findings

### 1. The uv/uvx antivirus problem is documented and real

`uv` is a statically-linked Rust binary distributed via an installer script from `astral.sh`. Multiple corporate AV products (Windows Defender SmartScreen, Cylance, CrowdStrike, McAfee) repeatedly flag the installer or the `uv`/`uvx` binaries as suspicious, generating false-positive detections. This is tracked across multiple issues in the `astral-sh/uv` repository. The recommended community workaround is to switch runtime entirely — Docker, Node, or plain `pip` — rather than attempt AV whitelisting. [astral-sh/uv issues (GitHub)](https://github.com/astral-sh/uv/issues)

---

### 2. Path A — Docker (supported uv-free path for `sooperset/mcp-atlassian`)

The maintainer publishes prebuilt images at **`ghcr.io/sooperset/mcp-atlassian:latest`** and documents Docker as a first-class alternative. This also supports Jira/Confluence **Server and Data Center**, unlike the Atlassian hosted server. [sooperset/mcp-atlassian (GitHub)](https://github.com/sooperset/mcp-atlassian)

**Step 1 — Pull the image (once):**
```bash
docker pull ghcr.io/sooperset/mcp-atlassian:latest
```

**Step 2 — `claude_desktop_config.json` entry (Cloud):**
```json
{
  "mcpServers": {
    "mcp-atlassian": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "-e", "CONFLUENCE_URL",
        "-e", "CONFLUENCE_USERNAME",
        "-e", "CONFLUENCE_API_TOKEN",
        "-e", "JIRA_URL",
        "-e", "JIRA_USERNAME",
        "-e", "JIRA_API_TOKEN",
        "ghcr.io/sooperset/mcp-atlassian:latest"
      ],
      "env": {
        "CONFLUENCE_URL": "https://your-company.atlassian.net/wiki",
        "CONFLUENCE_USERNAME": "you@example.com",
        "CONFLUENCE_API_TOKEN": "<your-api-token>",
        "JIRA_URL": "https://your-company.atlassian.net",
        "JIRA_USERNAME": "you@example.com",
        "JIRA_API_TOKEN": "<your-api-token>"
      }
    }
  }
}
```

**For Jira/Confluence Server or Data Center**, swap the username/token variables for Personal Access Tokens and optionally disable SSL verification:
```json
"env": {
  "CONFLUENCE_URL": "https://confluence.your-company.com",
  "CONFLUENCE_PERSONAL_TOKEN": "<PAT>",
  "CONFLUENCE_SSL_VERIFY": "false",
  "JIRA_URL": "https://jira.your-company.com",
  "JIRA_PERSONAL_TOKEN": "<PAT>",
  "JIRA_SSL_VERIFY": "false"
}
```

---

### 3. Path B — Direct Python with pip/pipx (no uv, no Docker)

`mcp-atlassian` is a standard Python package published to PyPI and exposes a `mcp-atlassian` console-script entry point on installation. Python 3.10+ is required. [mcp-atlassian on PyPI](https://pypi.org/project/mcp-atlassian/)

**Install with pipx (recommended — isolates dependencies, puts entry point on `PATH`):**
```bash
pipx install mcp-atlassian
```

**Or with plain pip (use a virtual environment to avoid polluting the system interpreter):**
```bash
pip install mcp-atlassian
```

**`claude_desktop_config.json` entry:**
```json
{
  "mcpServers": {
    "mcp-atlassian": {
      "command": "mcp-atlassian",
      "env": {
        "CONFLUENCE_URL": "https://your-company.atlassian.net/wiki",
        "CONFLUENCE_USERNAME": "you@example.com",
        "CONFLUENCE_API_TOKEN": "<your-api-token>",
        "JIRA_URL": "https://your-company.atlassian.net",
        "JIRA_USERNAME": "you@example.com",
        "JIRA_API_TOKEN": "<your-api-token>"
      }
    }
  }
}
```

If `mcp-atlassian` is not on your `PATH` (e.g., if installed into a virtual environment at `/path/to/venv`), set `"command": "/path/to/venv/bin/mcp-atlassian"` with an absolute path.

---

### 4. Path C — Pure Node/npx (`@aashari/mcp-server-atlassian-*`)

Two community npm packages — one for Jira, one for Confluence — run entirely on Node 18+ with no Python, Docker, or `uv` required. They can be invoked directly via `npx` without a global install. [npm: @aashari/mcp-server-atlassian-jira](https://www.npmjs.com/package/@aashari/mcp-server-atlassian-jira), [npm: @aashari/mcp-server-atlassian-confluence](https://www.npmjs.com/package/@aashari/mcp-server-atlassian-confluence)

**`claude_desktop_config.json` entry (both servers together):**
```json
{
  "mcpServers": {
    "atlassian-jira": {
      "command": "npx",
      "args": ["-y", "@aashari/mcp-server-atlassian-jira"],
      "env": {
        "ATLASSIAN_SITE_NAME": "your-company",
        "ATLASSIAN_USER_EMAIL": "you@example.com",
        "ATLASSIAN_API_TOKEN": "<your-api-token>"
      }
    },
    "atlassian-confluence": {
      "command": "npx",
      "args": ["-y", "@aashari/mcp-server-atlassian-confluence"],
      "env": {
        "ATLASSIAN_SITE_NAME": "your-company",
        "ATLASSIAN_USER_EMAIL": "you@example.com",
        "ATLASSIAN_API_TOKEN": "<your-api-token>"
      }
    }
  }
}
```

Note: `ATLASSIAN_SITE_NAME` is the subdomain only (e.g., `your-company`, not the full URL). These packages are Cloud-only; they do not support Server/DC.

---

### 5. Path D — Atlassian's Official Remote MCP Server (hosted, OAuth, no local runtime)

Atlassian launched a hosted Remote MCP Server in 2025, generally available for Cloud Standard/Premium/Enterprise plans. It is accessed at `https://mcp.atlassian.com/v1/sse` and authenticates via OAuth — no API token stored in config. [Atlassian Remote MCP Server](https://www.atlassian.com/platform/remote-mcp-server), [Atlassian Support docs](https://support.atlassian.com/atlassian-rovo-mcp-server/docs/getting-started-with-the-atlassian-remote-mcp-server/)

**Claude Desktop** (stdio-only) needs the `mcp-remote` npm bridge. Config:
```json
{
  "mcpServers": {
    "atlassian": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://mcp.atlassian.com/v1/sse"]
    }
  }
}
```
On first launch, a browser window opens for the Atlassian OAuth flow. The token is cached by `mcp-remote` for subsequent runs. [mcp-remote on npm](https://www.npmjs.com/package/mcp-remote)

**Claude Code (CLI)** supports remote MCP natively — no bridge needed:
```bash
claude mcp add --transport sse atlassian https://mcp.atlassian.com/v1/sse
```
[Claude Code MCP docs](https://docs.anthropic.com/en/docs/claude-code/mcp)

---

### 6. Comparison: Which path to choose

| Criterion | Docker | pip/pipx | npx (@aashari) | Atlassian Remote |
|---|---|---|---|---|
| Requires `uv`/`uvx` | No | No | No | No |
| Requires Python | No | Yes (3.10+) | No | No |
| Requires Docker | Yes | No | No | No |
| Jira Server/DC support | Yes | Yes | No | No |
| Confluence Server/DC | Yes | Yes | No | No |
| Credentials in config | Yes | Yes | Yes | No (OAuth) |
| Community vs. official | Community | Community | Community | Official Atlassian |

---

## Trade-offs / Caveats

- **Docker daemon required for Path A.** On locked-down corporate machines Docker Desktop may itself be blocked or require admin rights. In that case fall back to `pipx` (Path B) or `npx` (Path C).
- **`npx` contacts `registry.npmjs.org` on first run.** Corporate firewalls may block the npm registry. Both `mcp-remote` and `@aashari/...` cache after the first download; subsequent runs work offline. A private npm mirror or pre-caching with `npm install -g` can help.
- **`@aashari/...` packages (Path C) are community-maintained**, not from Atlassian. Tool coverage and update cadence differ from `sooperset/mcp-atlassian`. They do not support Jira/Confluence Server or Data Center.
- **Atlassian Remote MCP (Path D) is Cloud-only.** It does not work with self-hosted Jira/Confluence. Also, it is scoped to a Rovo-licensed workspace — check your plan.
- **PyPI `mcp-atlassian` version may lag the GitHub `main` branch.** The maintainer's primary distribution channels are Docker and `uvx`; the `pip` path works but you may not get the newest tools on the same day as a release. Run `pip show mcp-atlassian` to verify the installed version against the GitHub release tag.
- **API tokens are plaintext in `claude_desktop_config.json`**, which sits under your home directory. Do not commit this file to version control. The OAuth path (Atlassian Remote MCP) is preferable from a secrets hygiene standpoint.
- **`uv` AV flags are intermittent and version-dependent.** Vendors typically update their definitions within weeks of a new `uv` release. If you want to re-evaluate using `uv` in the future, test it again on the current version rather than assuming it is permanently blocked.

---

## Sources

- [sooperset/mcp-atlassian (GitHub)](https://github.com/sooperset/mcp-atlassian) — Primary Python MCP server for Jira + Confluence; Docker run instructions, environment variables, and Claude Desktop JSON config examples.
- [mcp-atlassian on PyPI](https://pypi.org/project/mcp-atlassian/) — Confirms the package is pip/pipx-installable and exposes a `mcp-atlassian` console-script entry point.
- [@aashari/mcp-server-atlassian-jira (npm)](https://www.npmjs.com/package/@aashari/mcp-server-atlassian-jira) — Node/npx-based Jira MCP server with `ATLASSIAN_SITE_NAME`-style config.
- [@aashari/mcp-server-atlassian-confluence (npm)](https://www.npmjs.com/package/@aashari/mcp-server-atlassian-confluence) — Node/npx-based Confluence MCP server.
- [Atlassian Remote MCP Server (product page)](https://www.atlassian.com/platform/remote-mcp-server) — Atlassian's hosted, OAuth-based MCP server for Cloud customers.
- [Getting started with the Atlassian Remote MCP Server (Atlassian Support)](https://support.atlassian.com/atlassian-rovo-mcp-server/docs/getting-started-with-the-atlassian-remote-mcp-server/) — Configuration steps, supported plans, and the SSE endpoint URL.
- [mcp-remote (npm)](https://www.npmjs.com/package/mcp-remote) — Stdio-to-SSE bridge allowing Claude Desktop to connect to any remote MCP server; only requires `npx`.
- [Claude Code MCP documentation](https://docs.anthropic.com/en/docs/claude-code/mcp) — Native `--transport sse` support for remote MCP servers, no bridge needed.
- [astral-sh/uv issues (GitHub)](https://github.com/astral-sh/uv/issues) — Background on recurring antivirus false-positive reports against `uv`/`uvx` binaries.
- [pipx documentation](https://pipx.pypa.io/) — Recommended method for installing Python CLI tools like `mcp-atlassian` in isolation.
