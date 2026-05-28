# Research: Configuring Jira & Confluence MCP Servers in AWS Kiro (Without uv/uvx)

## Summary

AWS Kiro reads MCP server definitions from JSON files at `~/.kiro/settings/mcp.json` (global) or `.kiro/settings/mcp.json` (workspace). The schema uses an `mcpServers` object whose entries describe either a local stdio process (`command`/`args`/`env`) or a remote HTTP/SSE endpoint (`url` only). Because `uv`/`uvx` are blocked, Jira and Confluence access can be wired up via four alternatives: Docker (`ghcr.io/sooperset/mcp-atlassian:latest`), `pipx install mcp-atlassian`, `npx`-based `@aashari/mcp-server-atlassian-*` packages, or the hosted Atlassian Remote MCP at `https://mcp.atlassian.com/v1/sse`. Two confirmed Kiro bugs require defensive config: `${VAR}` interpolation is broken in `kiro-cli` (issue #5988), and relative `args` paths resolve from the Kiro install directory instead of the workspace (issue #6525). Absolute paths for every binary are always required because the GUI process does not inherit the shell's `PATH`.

---

## Key Findings

### 1. Configuration File Format and Locations

Kiro follows the standard MCP host schema. Both files are read simultaneously; workspace entries take precedence over global ones for the same key.

```
Global (user-wide):    ~/.kiro/settings/mcp.json
Workspace (per-repo):  <workspace>/.kiro/settings/mcp.json
```

The root JSON shape is:

```json
{
  "mcpServers": {
    "<server-name>": {
      "command": "...",
      "args": [],
      "env": {},
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

For **remote** servers, replace `command`/`args`/`env` with just `url`. No `type` field is needed; Kiro auto-negotiates Streamable HTTP first and falls back to SSE. [Kiro MCP configuration docs](https://kiro.dev/docs/mcp/configuration)

---

### 2. uv-free MCP Configurations

#### (a) Docker — `sooperset/mcp-atlassian` (covers Jira + Confluence in one server)

The Docker image is the most isolation-friendly option and requires no Python environment on the host. [sooperset/mcp-atlassian](https://github.com/sooperset/mcp-atlassian)

```json
{
  "mcpServers": {
    "atlassian": {
      "command": "/usr/local/bin/docker",
      "args": [
        "run", "--rm", "-i",
        "-e", "JIRA_URL",
        "-e", "JIRA_USERNAME",
        "-e", "JIRA_API_TOKEN",
        "-e", "CONFLUENCE_URL",
        "-e", "CONFLUENCE_USERNAME",
        "-e", "CONFLUENCE_API_TOKEN",
        "ghcr.io/sooperset/mcp-atlassian:latest"
      ],
      "env": {
        "JIRA_URL": "https://your-domain.atlassian.net",
        "JIRA_USERNAME": "you@example.com",
        "JIRA_API_TOKEN": "your_atlassian_api_token",
        "CONFLUENCE_URL": "https://your-domain.atlassian.net/wiki",
        "CONFLUENCE_USERNAME": "you@example.com",
        "CONFLUENCE_API_TOKEN": "your_atlassian_api_token"
      }
    }
  }
}
```

- Verify Docker binary path: `which docker` — common values are `/usr/local/bin/docker` (Intel Mac) or `/opt/homebrew/bin/docker` (Apple Silicon)
- For Atlassian Server/Data Center: use `JIRA_PERSONAL_TOKEN`/`CONFLUENCE_PERSONAL_TOKEN` instead of `*_USERNAME`/`*_API_TOKEN`

#### (b) pipx — `mcp-atlassian` console script

`pipx install mcp-atlassian` installs an `mcp-atlassian` entrypoint (typically at `~/.local/bin/mcp-atlassian`) in an isolated virtualenv. [mcp-atlassian on PyPI](https://pypi.org/project/mcp-atlassian/)

```json
{
  "mcpServers": {
    "atlassian": {
      "command": "/Users/YOUR_USERNAME/.local/bin/mcp-atlassian",
      "args": [],
      "env": {
        "JIRA_URL": "https://your-domain.atlassian.net",
        "JIRA_USERNAME": "you@example.com",
        "JIRA_API_TOKEN": "your_atlassian_api_token",
        "CONFLUENCE_URL": "https://your-domain.atlassian.net/wiki",
        "CONFLUENCE_USERNAME": "you@example.com",
        "CONFLUENCE_API_TOKEN": "your_atlassian_api_token"
      }
    }
  }
}
```

Replace `YOUR_USERNAME` with `whoami`. Confirm the path with `which mcp-atlassian`.

#### (c) npx — `@aashari` per-product Node servers (Cloud only)

Two separate Node packages, one for Jira and one for Confluence, fetched on demand by `npx`. [npm: @aashari/mcp-server-atlassian-jira](https://www.npmjs.com/package/@aashari/mcp-server-atlassian-jira) | [npm: @aashari/mcp-server-atlassian-confluence](https://www.npmjs.com/package/@aashari/mcp-server-atlassian-confluence)

```json
{
  "mcpServers": {
    "jira": {
      "command": "/usr/local/bin/npx",
      "args": ["-y", "@aashari/mcp-server-atlassian-jira"],
      "env": {
        "ATLASSIAN_SITE_NAME": "your-domain",
        "ATLASSIAN_USER_EMAIL": "you@example.com",
        "ATLASSIAN_API_TOKEN": "your_atlassian_api_token"
      }
    },
    "confluence": {
      "command": "/usr/local/bin/npx",
      "args": ["-y", "@aashari/mcp-server-atlassian-confluence"],
      "env": {
        "ATLASSIAN_SITE_NAME": "your-domain",
        "ATLASSIAN_USER_EMAIL": "you@example.com",
        "ATLASSIAN_API_TOKEN": "your_atlassian_api_token"
      }
    }
  }
}
```

- `ATLASSIAN_SITE_NAME` is the subdomain only — for `acme.atlassian.net`, put `acme`
- Locate npx with `which npx`; if you use nvm the path changes per Node version
- Note env variable naming differs from `sooperset`: `ATLASSIAN_SITE_NAME`/`ATLASSIAN_USER_EMAIL` vs `JIRA_URL`/`JIRA_USERNAME` — do not mix them

#### (d) Atlassian Remote MCP (hosted, OAuth — zero local install)

Atlassian provides a hosted MCP server requiring no local process at all. [Atlassian Remote MCP Server](https://www.atlassian.com/blog/announcements/remote-mcp-server) | [Setup docs](https://support.atlassian.com/atlassian-rovo-mcp-server/docs/getting-started-with-the-atlassian-remote-mcp-server/)

```json
{
  "mcpServers": {
    "atlassian-cloud": {
      "url": "https://mcp.atlassian.com/v1/sse"
    }
  }
}
```

When Kiro first starts this server it opens the system browser for OAuth consent. Refresh tokens are cached. No API token in the config file needed. Requires Rovo entitlements on your Atlassian plan.

---

### 3. Kiro-Specific Quirks

**GUI app does not inherit shell PATH.**
Kiro launched from the macOS Finder or Dock is a non-login, non-interactive process. Homebrew paths (`/opt/homebrew/bin`), nvm-managed Node, `~/.local/bin`, and Docker Desktop helpers are all invisible. Every `command` value must be an absolute path. Confirm paths with: `which docker`, `which npx`, `which mcp-atlassian`.

**`${VAR}` interpolation broken in `kiro-cli` (issue #5988).**
The Kiro GUI IDE expands `${ATLASSIAN_API_TOKEN}` etc. from the host environment before launching the MCP process. The `kiro-cli` binary passes these tokens through literally, causing auth failures. [kirodotdev/Kiro#5988](https://github.com/kirodotdev/Kiro/issues/5988)

Workarounds:
- Hard-code credentials directly in the `env` block and restrict file permissions (`chmod 600 ~/.kiro/settings/mcp.json`)
- Wrap the command in a small shell script that sources a `.env` file
- Use the remote MCP option (d) to avoid credentials in the file entirely

**Relative `args` paths resolve from the Kiro install directory (issue #6525).**
Any relative path in `args` resolves against the IDE's own install directory, not the workspace root. Always use absolute paths in `args`. [kirodotdev/Kiro#6525](https://github.com/kirodotdev/Kiro/issues/6525)

---

### 4. Native SSE and Remote MCP Support

Kiro supports remote MCP servers natively using just the `url` field — no additional packages like `mcp-remote` are required. On connection, Kiro first attempts Streamable HTTP (MCP spec 2025-03-26) and falls back to SSE if the server returns a non-2xx or SSE-specific response. Both legacy SSE servers (like the Atlassian beta endpoint at `/v1/sse`) and newer Streamable HTTP servers work transparently. [Kiro MCP docs](https://kiro.dev/docs/mcp/configuration)

---

## Trade-offs / Caveats

- **`sooperset` vs `aashari` feature scope.** `sooperset/mcp-atlassian` covers Jira and Confluence on both Cloud and Server/Data Center in one server. `aashari`'s packages are two separate Cloud-only servers. `sooperset` is more complete; `aashari`'s Node packages have faster cold-start via `npx`.
- **Atlassian Remote MCP is beta (mid-2025).** Rate limits, available tools, and the `/v1/sse` URL may change. Requires a Rovo-entitled Atlassian plan.
- **Docker socket note.** Tokens in `env` are forwarded as process environment variables. `chmod 600 ~/.kiro/settings/mcp.json` limits exposure.
- **`kiro-cli` vs GUI IDE for `${VAR}`.** In CI/CD pipelines using `kiro-cli`, interpolated env vars will not work (issue #5988). Pin literal values or use a shell wrapper.
- **Stale tutorials.** Kiro released in 2025; older blog posts may reference different config paths. Trust only `kiro.dev/docs/mcp/` and the `kirodotdev/Kiro` repository.

---

## Sources

- [kiro.dev/docs/mcp/configuration](https://kiro.dev/docs/mcp/configuration) — Kiro's canonical MCP configuration reference: file paths, JSON schema, local vs remote fields
- [github.com/sooperset/mcp-atlassian](https://github.com/sooperset/mcp-atlassian) — Docker/pipx Atlassian MCP server covering Jira and Confluence (Cloud and Server/DC)
- [pypi.org/project/mcp-atlassian](https://pypi.org/project/mcp-atlassian/) — PyPI listing confirming `pipx install mcp-atlassian`
- [github.com/aashari/mcp-server-atlassian-jira](https://github.com/aashari/mcp-server-atlassian-jira) — Jira-only npx server; env var names
- [npmjs.com/package/@aashari/mcp-server-atlassian-jira](https://www.npmjs.com/package/@aashari/mcp-server-atlassian-jira)
- [github.com/aashari/mcp-server-atlassian-confluence](https://github.com/aashari/mcp-server-atlassian-confluence) — Confluence-only npx server
- [npmjs.com/package/@aashari/mcp-server-atlassian-confluence](https://www.npmjs.com/package/@aashari/mcp-server-atlassian-confluence)
- [atlassian.com/blog/announcements/remote-mcp-server](https://www.atlassian.com/blog/announcements/remote-mcp-server) — Atlassian hosted Remote MCP announcement; SSE endpoint URL
- [support.atlassian.com — Getting started with the Atlassian Remote MCP Server](https://support.atlassian.com/atlassian-rovo-mcp-server/docs/getting-started-with-the-atlassian-remote-mcp-server/)
- [github.com/kirodotdev/Kiro/issues/5988](https://github.com/kirodotdev/Kiro/issues/5988) — `${VAR}` interpolation works in Kiro IDE but not `kiro-cli`
- [github.com/kirodotdev/Kiro/issues/6525](https://github.com/kirodotdev/Kiro/issues/6525) — Relative paths in MCP `args` resolve against Kiro's install directory
