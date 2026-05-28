# Research: Using OceanBase MCP Server Without uv or uvx

## Summary

The OceanBase MCP server is a Python package (`oceanbase-mcp`, v0.0.4 Alpha) published on PyPI. Its official README documents only `uv`/`uvx`-based installation, but the package ships a standard console script entry point (`oceanbase_mcp_server`) and is fully installable via plain `pip`, `pipx`, or a manual virtual environment — none of which require `uv` or `uvx`. Python 3.10–3.12 is required. The key practical consideration for Claude Desktop users on macOS/Windows is that the GUI application does not inherit the shell PATH, so MCP config files must reference the **absolute path** to the installed binary or the Python executable inside the virtual environment.

---

## Key Findings

### 1. Runtime: Python 3.10–3.12

The package requires Python ≥3.10 and <3.13. This constraint comes from a transitive dependency (`pyobvector`) on a specific numpy version. [pyproject.toml (awesome-oceanbase-mcp)](https://github.com/oceanbase/awesome-oceanbase-mcp/blob/main/src/oceanbase_mcp_server/pyproject.toml)

### 2. Core Dependencies (installed automatically by pip)

- `mcp` ≥1.13.1
- `fastmcp` ≥2.12.0
- `mysql-connector-python` ≥9.1.0
- `SQLAlchemy` ≥2.0.32
- `python-dotenv` ≥1.1.1
- `pyobvector` ≥0.2.15
- `pydantic`, `beautifulsoup4`, `certifi`

[PyPI: oceanbase-mcp](https://pypi.org/project/oceanbase-mcp/)

### 3. Required Environment Variables

All five of these must be provided for any transport mode:

| Variable | Description | Example |
|---|---|---|
| `OB_HOST` | Database hostname | `localhost` |
| `OB_PORT` | Database port | `2881` |
| `OB_USER` | Database username | `root` |
| `OB_PASSWORD` | Database password | `your_password` |
| `OB_DATABASE` | Target database name | `your_db` |

Optional: `ALLOWED_TOKENS` (comma-separated auth tokens), `ENABLE_MEMORY` (`1`/`0`).

[Official README](https://github.com/oceanbase/awesome-oceanbase-mcp/blob/main/src/oceanbase_mcp_server/README.md)

### 4. Installation Method A — pipx (Closest Drop-in for uvx Semantics)

`pipx` installs the package into an isolated virtual environment and exposes the console script globally. This is the cleanest replacement for `uvx`.

```bash
pipx install oceanbase-mcp
# Installed binary is available at: ~/.local/bin/oceanbase_mcp_server (macOS/Linux)
# or: %USERPROFILE%\.local\bin\oceanbase_mcp_server.exe (Windows)
```

Find the exact path after install:

```bash
which oceanbase_mcp_server        # macOS/Linux
where oceanbase_mcp_server        # Windows
```

### 5. Installation Method B — Standard pip into a Virtual Environment

```bash
python3 -m venv ~/.venvs/oceanbase-mcp
source ~/.venvs/oceanbase-mcp/bin/activate          # macOS/Linux
# .venvs\oceanbase-mcp\Scripts\activate.bat         # Windows

pip install oceanbase-mcp

# Optional: with memory/AI features (needs ~0.5–4 GiB for model download)
pip install "oceanbase-mcp[memory]" --extra-index-url https://download.pytorch.org/whl/cpu
```

The console script is then at: `~/.venvs/oceanbase-mcp/bin/oceanbase_mcp_server`

[Official README](https://github.com/oceanbase/awesome-oceanbase-mcp/blob/main/src/oceanbase_mcp_server/README.md)

### 6. Claude Desktop / Claude Code MCP Configuration — stdio Mode (No uv/uvx)

**Important:** Claude Desktop on macOS and Windows launches as a GUI app and does not inherit your shell PATH. You must use the **absolute path** to the binary, not just `oceanbase_mcp_server`.

**Using pipx-installed binary (macOS/Linux):**

```json
{
  "mcpServers": {
    "oceanbase": {
      "command": "/Users/YOUR_NAME/.local/bin/oceanbase_mcp_server",
      "args": [],
      "env": {
        "OB_HOST": "localhost",
        "OB_PORT": "2881",
        "OB_USER": "root",
        "OB_PASSWORD": "your_password",
        "OB_DATABASE": "your_database"
      }
    }
  }
}
```

**Using a virtual environment's Python with `-m` (works on all platforms, most explicit):**

```json
{
  "mcpServers": {
    "oceanbase": {
      "command": "/Users/YOUR_NAME/.venvs/oceanbase-mcp/bin/python",
      "args": ["-m", "oceanbase_mcp_server"],
      "env": {
        "OB_HOST": "localhost",
        "OB_PORT": "2881",
        "OB_USER": "root",
        "OB_PASSWORD": "your_password",
        "OB_DATABASE": "your_database"
      }
    }
  }
}
```

**Windows equivalent (venv):**

```json
{
  "mcpServers": {
    "oceanbase": {
      "command": "C:\\Users\\YOUR_NAME\\.venvs\\oceanbase-mcp\\Scripts\\python.exe",
      "args": ["-m", "oceanbase_mcp_server"],
      "env": {
        "OB_HOST": "localhost",
        "OB_PORT": "2881",
        "OB_USER": "root",
        "OB_PASSWORD": "your_password",
        "OB_DATABASE": "your_database"
      }
    }
  }
}
```

### 7. SSE / Streamable-HTTP Mode (Avoids stdio PATH Issues Entirely)

If stdio is causing issues, start the server as a process first, then point Claude at its URL instead. This completely sidesteps the binary PATH problem.

**Start the server (from activated venv or after pipx install):**

```bash
# SSE transport
oceanbase_mcp_server --transport sse --port 8000

# OR: Streamable HTTP
oceanbase_mcp_server --transport streamable-http --port 8000
```

**Claude Desktop config for SSE:**

```json
{
  "mcpServers": {
    "oceanbase": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

**Claude Desktop config for Streamable HTTP:**

```json
{
  "mcpServers": {
    "oceanbase": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

[Official README](https://github.com/oceanbase/awesome-oceanbase-mcp/blob/main/src/oceanbase_mcp_server/README.md)

### 8. Docker (Testing / OceanBase Database Only)

The README provides a Docker command for spinning up a test OceanBase database instance, not the MCP server itself:

```bash
docker run -p 2881:2881 --name obvector -e MODE=mini -d oceanbase/oceanbase-ce:4.3.5.3-103000092025080818
```

[Official README](https://github.com/oceanbase/awesome-oceanbase-mcp/blob/main/src/oceanbase_mcp_server/README.md)

---

## Trade-offs / Caveats

- **The official README documents only `uv`/`uvx`.** The non-uv configurations in this report are derived from the PyPI package metadata (entry-point name, Python version constraints, dependencies), not from officially documented examples. They follow standard Python packaging conventions and should work, but are not explicitly blessed by OceanBase documentation.

- **Absolute paths are mandatory for Claude Desktop.** GUI applications on macOS and Windows do not source your shell profile, so relative commands like `oceanbase_mcp_server` without a full path will fail silently or with a "command not found" error at startup.

- **Package is Alpha (v0.0.4).** The README and PyPI listing both indicate this is alpha-quality software. Expect potential breaking changes between versions. [PyPI: oceanbase-mcp](https://pypi.org/project/oceanbase-mcp/)

- **Python version ceiling is strict.** Python 3.13+ is explicitly excluded due to a numpy compatibility constraint from `pyobvector`. Installing on Python 3.13 will fail with a dependency resolver error.

- **Memory features are heavy.** The `[memory]` extra pulls in PyTorch and sentence-transformers (~500 MB to 4 GB). These work with plain `pip install "oceanbase-mcp[memory]" --extra-index-url https://download.pytorch.org/whl/cpu` but the download is large and slow.

- **Alternative fork:** A community fork at [yuanoOo/oceanbase_mcp_server](https://github.com/yuanoOo/oceanbase_mcp_server) installs as `pip install oceanbase-mcp-server` (different package name, hyphen-server suffix). It uses a similar environment variable pattern but is not the official OceanBase release. Do not mix it with the official `oceanbase-mcp` package.

---

## Sources

- [Official OceanBase MCP Server README](https://github.com/oceanbase/awesome-oceanbase-mcp/blob/main/src/oceanbase_mcp_server/README.md) — Primary source for environment variables, transport modes, and uv-based installation instructions
- [awesome-oceanbase-mcp GitHub Repository](https://github.com/oceanbase/awesome-oceanbase-mcp) — Repository root; confirms requirements.txt, pyproject.toml, and Python 3.8+ badge
- [pyproject.toml (fetched)](https://github.com/oceanbase/awesome-oceanbase-mcp/blob/main/src/oceanbase_mcp_server/pyproject.toml) — Source for Python version bounds (3.10–<3.13), all core and optional dependencies, and console script entry point
- [PyPI: oceanbase-mcp](https://pypi.org/project/oceanbase-mcp/) — Confirms package name, version (0.0.4), Python constraints, and console script `oceanbase_mcp_server`
- [yuanoOo/oceanbase_mcp_server (community fork)](https://github.com/yuanoOo/oceanbase_mcp_server) — Alternative community fork; different PyPI package name (`oceanbase-mcp-server`)
